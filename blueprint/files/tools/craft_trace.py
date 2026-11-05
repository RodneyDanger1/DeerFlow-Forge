#!/usr/bin/env python3
"""CraftTrace: ArtCraft VectorCraft Image Trace + retyped text → print master.

The professional workflow, not a generic tracer:

  1. strict white cutout (tools.prep_print_art; owner rule: every white transparent)
  2. erase the AI-rendered text bands (white) so the trace carries illustration only —
     AI text has diffusion erosion/shadow that no tracer can repair
  3. VectorCraft `imageTrace.make` (Illustrator-compatible options) + `imageTrace.expand`
  4. export SVG, render at exact print pixels with rsvg-convert
  5. retype the wordmark + tagline with a real font at the mapped boxes
  6. saturation/sharpen restore, compose on the provider canvas, run the 10 checks

Coordinate spaces: prep crops to the subject bbox and re-centres, so every box
measured on the original image MUST be transformed through `mapping` before it is
used for erasing or retyping. That bug produced ghost text and misplaced labels.

Usage (inside /opt/pod-pipeline):

    .venv/bin/python -m tools.craft_trace \
      --input data/ai-uploads/rb_logo.jpg \
      --template pro_e4677535402b4eeb81 --area front_large --dpi 300 --print-width-in 8 \
      --retype-json config/retype-ridgeboundia.json \
      --output data/ai-uploads/rb_tee_craft.png --svg data/ai-uploads/rb_tee_craft.svg \
      --report-json data/ai-uploads/rb_tee_craft.json \
      --preview-dir data/ai-uploads/previews_rb_tee_craft
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from skimage import filters, measure

from tools.prep_print_art import drop_small_components

DEFAULT_VECTORCRAFT = "/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli"
FONT_CANDIDATES = ("FreeSansBold.ttf", "NimbusSans-Bold.otf")


class CraftTraceError(RuntimeError):
    def __init__(self, code: str, message: str, how_to_fix: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code, self.message, self.how_to_fix = code, message, how_to_fix


def find_font(preferred: str | None = None) -> str:
    if preferred and Path(preferred).is_file():
        return preferred
    for name in FONT_CANDIDATES:
        hits = list(Path("/usr/share/fonts").rglob(name))
        if hits:
            return str(hits[0])
    raise CraftTraceError("E_FONT_MISSING", "No bold sans font found for retyping.", "Install fonts-freefont/dejavu or pass a font path.")


def vectorcraft_bin(explicit: str | None) -> str:
    for candidate in (explicit, DEFAULT_VECTORCRAFT):
        if candidate and Path(candidate).is_file():
            return candidate
    hits = list(Path("/opt/craft").rglob("vectorcraft-cli"))
    if hits:
        return str(hits[0])
    raise CraftTraceError("E_VECTORCRAFT_MISSING", "vectorcraft-cli is not installed.", "Install ArtCraft VectorCraft under /opt/craft.")


def cutout_and_erase_text(args: argparse.Namespace, temp: Path) -> tuple[Path, Image.Image, dict]:
    """Strict-white cutout at the source aspect, with AI text bands painted white."""
    probe = Image.open(args.input)
    width, height = probe.size
    cutout = temp / "cutout.png"
    report_path = temp / "prep.json"
    command = [
        sys.executable, "-m", "tools.prep_print_art",
        "--input", str(Path(args.input).resolve()), "--output", str(cutout),
        "--width-px", str(width), "--height-px", str(height), "--dpi", "300",
        "--mode", "white", "--clean-rim", "--min-component", "60",
        "--edge-clean-px", "26", "--edge-clean-lum", "140",
        "--margin-px", "0", "--print-width-in", f"{width / 300:.6f}",
        "--report-json", str(report_path),
    ]
    result = subprocess.run(command, cwd=Path.cwd(), capture_output=True, text=True)
    if result.returncode != 0 or not cutout.is_file():
        raise CraftTraceError("E_CUTOUT_FAILED", "White cutout failed.", result.stderr[-500:])
    stats = json.loads(report_path.read_text(encoding="utf-8"))
    bbox = [int(value) for value in stats["subject_bbox"]]
    crop_w, crop_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    scale = width / crop_w
    scaled = (round(crop_w * scale), round(crop_h * scale))
    mapping = {
        "bbox": bbox,
        "crop": [crop_w, crop_h],
        "canvas": [width, height],
        "scale": scale,
        "offset": ((width - scaled[0]) // 2, (height - scaled[1]) // 2),
    }
    canvas = Image.open(cutout).convert("RGBA")
    if args.retype_json:
        spec = json.loads(Path(args.retype_json).read_text(encoding="utf-8"))
        draw = ImageDraw.Draw(canvas)
        ox, oy = mapping["offset"]
        for item in spec:
            x0, y0, x1, y1 = [int(value) for value in item["box"]]
            box = [
                round(ox + (x0 - bbox[0]) * scale),
                round(oy + (y0 - bbox[1]) * scale),
                round(ox + (x1 - bbox[0]) * scale),
                round(oy + (y1 - bbox[1]) * scale),
            ]
            draw.rectangle(box, fill=(255, 255, 255, 255))
    trace_input = temp / "trace_input.png"
    canvas.save(trace_input)
    return trace_input, canvas, mapping


def run_trace(vectorcraft: str, trace_input: Path, svg_path: Path, params: dict, temp: Path) -> None:
    steps = [
        {"command": "select.all"},
        {"command": "imageTrace.make", "params": {"params": params}},
        {"command": "imageTrace.expand"},
    ]
    steps_file = temp / "steps.json"
    steps_file.write_text(json.dumps(steps), encoding="utf-8")
    result = subprocess.run(
        [vectorcraft, "run", "--in", str(trace_input), "--commands", str(steps_file), "--export", str(svg_path)],
        capture_output=True, text=True, timeout=600,
    )
    if result.returncode != 0 or not svg_path.is_file():
        raise CraftTraceError("E_TRACE_FAILED", "vectorcraft-cli imageTrace failed.", (result.stderr or result.stdout)[-700:])


def retype_overlay(spec: list[dict], mapping: dict, print_width_px: int) -> Image.Image:
    """Render the wordmark/tagline at the mapped boxes, in rendered-art space.

    The traced SVG keeps the full canvas (art centred, not cropped), so a box is
    mapped: original bbox coords -> prep canvas coords -> rendered-art pixels.
    """
    bbox = mapping["bbox"]
    canvas_w, canvas_h = mapping["canvas"]
    offset_x, offset_y = mapping["offset"]
    prep_scale = mapping["scale"]
    art_scale = print_width_px / canvas_w
    art_w = print_width_px
    art_h = round(canvas_h * art_scale)
    overlay = Image.new("RGBA", (art_w, art_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for item in spec:
        x0, y0, x1, y1 = [int(value) for value in item["box"]]
        box = [
            round((offset_x + (x0 - bbox[0]) * prep_scale) * art_scale),
            round((offset_y + (y0 - bbox[1]) * prep_scale) * art_scale),
            round((offset_x + (x1 - bbox[0]) * prep_scale) * art_scale),
            round((offset_y + (y1 - bbox[1]) * prep_scale) * art_scale),
        ]
        box_w, box_h = box[2] - box[0], box[3] - box[1]
        text = item["text"]
        font_path = find_font(item.get("font"))
        stroke_px = max(1, round(int(item.get("stroke_px", 0)) * art_scale * prep_scale / 2))
        best = None
        probe = ImageDraw.Draw(Image.new("L", (1, 1)))
        for font_size in range(8, 1200):
            font = ImageFont.truetype(font_path, font_size)
            text_bbox = probe.textbbox((0, 0), text, font=font, stroke_width=stroke_px)
            width, height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
            if width <= box_w * 0.98 and height <= box_h * 0.96:
                best = (font, text_bbox, width, height)
            else:
                break
        if best is None:
            continue
        font, text_bbox, width, height = best
        tx = box[0] + (box_w - width) // 2 - text_bbox[0]
        ty = box[1] + (box_h - height) // 2 - text_bbox[1]
        draw.text((tx, ty), text, font=font, fill=item.get("fill", "#efe6cf"),
                  stroke_width=stroke_px, stroke_fill=item.get("stroke") or item.get("fill", "#efe6cf"))
    return overlay


def compose_canvas(art: Image.Image, canvas_w: int, canvas_h: int) -> Image.Image:
    master = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    master.alpha_composite(art, ((canvas_w - art.width) // 2, (canvas_h - art.height) // 2))
    return master


def verify(source: Image.Image, final_art: Image.Image, canvas: tuple[int, int], dpi: int,
           svg_path: Path, spec: list[dict] | None, mapping: dict | None) -> dict:
    src = source.convert("RGBA").resize(final_art.size, Image.LANCZOS)
    final_rgb = final_art.convert("RGB")
    final = np.asarray(final_rgb, dtype=np.uint8)
    alpha = np.asarray(final_art.getchannel("A"), dtype=np.uint8) > 127
    height, width = alpha.shape
    near_white = np.all(final >= 245, axis=-1) & alpha
    labels = measure.label(alpha)
    specks = int(sum(1 for region in measure.regionprops(labels) if region.area < 150))
    coverage = float(alpha.sum()) / float(alpha.size)
    svg_text = svg_path.read_text(encoding="utf-8")
    fills = set(re.findall(r'fill="#([0-9a-fA-F]{6})"', svg_text))
    grey_final = np.asarray(final_rgb.convert("L"), dtype=float) / 255.0
    strong_edges = int((np.abs(filters.laplace(grey_final)) > 0.35).sum())
    edge_density = strong_edges / float(alpha.sum() or 1)
    corner_ok = bool(not any(bool(alpha[y, x]) for y, x in ((2, 2), (2, width - 3), (height - 3, 2), (height - 3, width - 3))))
    text_ok = True
    if spec and mapping:
        bbox = mapping["bbox"]
        canvas_w, canvas_h = mapping["canvas"]
        offset_x, offset_y = mapping["offset"]
        prep_scale = mapping["scale"]
        art_scale = final_art.width / canvas_w
        for item in spec:
            if not item.get("text"):
                continue
            x0, y0, x1, y1 = [int(value) for value in item["box"]]
            box = [
                round((offset_x + (x0 - bbox[0]) * prep_scale) * art_scale),
                round((offset_y + (y0 - bbox[1]) * prep_scale) * art_scale),
                round((offset_x + (x1 - bbox[0]) * prep_scale) * art_scale),
                round((offset_y + (y1 - bbox[1]) * prep_scale) * art_scale),
            ]
            bx0, bx1 = max(0, box[0]), min(width, box[2])
            by0, by1 = max(0, box[1]), min(height, box[3])
            if bx1 <= bx0 or by1 <= by0 or int(alpha[by0:by1, bx0:bx1].sum()) < 2000:
                text_ok = False
    checks = {
        "white_residual_ratio": {"value": float(round(float(near_white.sum()) / max(1, int(alpha.sum())), 5)),
                                 "pass": bool(float(near_white.sum()) / max(1, int(alpha.sum())) <= 0.002)},
        "edge_specks": {"value": specks, "pass": bool(specks <= 10)},
        "coverage": {"value": float(round(coverage, 4)), "pass": bool(0.05 <= coverage <= 0.95)},
        "dpi": {"value": int(dpi), "pass": bool(dpi >= 300)},
        "canvas_geometry": {"value": [int(canvas[0]), int(canvas[1])], "pass": bool(canvas[0] >= 1500 and canvas[1] >= 1500)},
        "vector_fill_colours": {"value": len(fills), "pass": bool(2 <= len(fills) <= 40)},
        "edge_definition": {"value": float(round(edge_density, 4)), "pass": bool(edge_density >= 0.002)},
        "alpha_hard_edges": {"value": float(round(float(((np.asarray(final_art.getchannel("A")) == 0) | (np.asarray(final_art.getchannel("A")) == 255)).mean()), 4)),
                             "pass": bool(float(((np.asarray(final_art.getchannel("A")) == 0) | (np.asarray(final_art.getchannel("A")) == 255)).mean()) >= 0.85)},
        "transparent_corners": {"value": corner_ok, "pass": corner_ok},
        "retyped_text_present": {"value": text_ok, "pass": text_ok},
    }
    return {"passed": all(bool(check["pass"]) for check in checks.values()), "checks": checks,
            "svg_paths": int(svg_text.count("<path")), "svg_bytes": int(svg_path.stat().st_size),
            "src_size": list(src.size)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="VectorCraft Image Trace + retyped text → print master.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--svg", required=True)
    parser.add_argument("--template")
    parser.add_argument("--area", default="front_large")
    parser.add_argument("--details", default="config/fourthwall-template-details.json")
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--print-width-in", type=float, default=8.0)
    parser.add_argument("--canvas-width", type=int)
    parser.add_argument("--canvas-height", type=int)
    parser.add_argument("--retype-json")
    parser.add_argument("--vectorcraft")
    parser.add_argument("--colors", type=int, default=12)
    parser.add_argument("--paths", type=float, default=65)
    parser.add_argument("--corners", type=float, default=45)
    parser.add_argument("--noise", type=float, default=16)
    parser.add_argument("--palette", default="limited")
    parser.add_argument("--mode", default="color")
    parser.add_argument("--saturation", type=float, default=1.12)
    parser.add_argument("--brightness", type=float, default=1.03)
    parser.add_argument("--sharpen", type=float, default=30)
    parser.add_argument("--report-json")
    parser.add_argument("--preview-dir")
    args = parser.parse_args(argv)

    canvas_w, canvas_h = args.canvas_width, args.canvas_height
    if args.template:
        rows = json.loads(Path(args.details).read_text(encoding="utf-8"))
        row = next((r for r in rows if r.get("productId") == args.template), None)
        if row is None:
            print(f"REFUSED E_TEMPLATE_UNKNOWN {args.template}", file=sys.stderr)
            return 2
        if not row.get("supportsBackendRendering") or row.get("productionMethod") == "KNITTING":
            print("REFUSED E_TEMPLATE_UNRENDERABLE", file=sys.stderr)
            return 2
        dims = (row.get("areaGeometry") or {}).get(args.area)
        if not dims:
            print(f"REFUSED E_AREA_UNKNOWN {args.area}", file=sys.stderr)
            return 2
        canvas_w = round(float(dims["inchesWidth"]) * args.dpi)
        canvas_h = round(float(dims["inchesHeight"]) * args.dpi)
    if not canvas_w or not canvas_h:
        print("REFUSED E_GEOMETRY_MISSING", file=sys.stderr)
        return 2

    try:
        vectorcraft = vectorcraft_bin(args.vectorcraft)
        with tempfile.TemporaryDirectory() as temp_name:
            temp = Path(temp_name)
            trace_input, original, mapping = cutout_and_erase_text(args, temp)
            svg_path = Path(args.svg)
            svg_path.parent.mkdir(parents=True, exist_ok=True)
            params = {
                "mode": args.mode, "palette": args.palette, "colors": args.colors,
                "paths": args.paths, "corners": args.corners, "noise": args.noise,
                "ignoreWhite": True, "method": "abutting", "fills": True, "strokes": False,
                "shapes": False, "autoGrouping": False, "gradients": False,
            }
            run_trace(vectorcraft, trace_input, svg_path, params, temp)
            print_width_px = round(args.print_width_in * args.dpi)
            rendered = temp / "traced.png"
            render = subprocess.run(["rsvg-convert", "-w", str(print_width_px), "-o", str(rendered), str(svg_path)], capture_output=True, text=True)
            if render.returncode != 0:
                raise CraftTraceError("E_RENDER_FAILED", "rsvg-convert failed.", render.stderr[-400:])
            art = Image.open(rendered).convert("RGBA")
            cleaned_alpha = drop_small_components(art.getchannel("A").copy(), 800).point(lambda v: 255 if v >= 128 else 0)
            art.putalpha(cleaned_alpha)
            spec = json.loads(Path(args.retype_json).read_text(encoding="utf-8")) if args.retype_json else None
            if spec:
                overlay = retype_overlay(spec, mapping, print_width_px)
                art = Image.alpha_composite(art, overlay)
            colour = art.convert("RGB")
            colour = ImageEnhance.Color(colour).enhance(args.saturation)
            colour = ImageEnhance.Brightness(colour).enhance(args.brightness)
            colour = colour.filter(ImageFilter.UnsharpMask(radius=2, percent=int(args.sharpen), threshold=2))
            transparency = art.getchannel("A")
            art = colour.convert("RGBA")
            art.putalpha(transparency)
            master = compose_canvas(art, canvas_w, canvas_h)
            master.save(args.output, dpi=(args.dpi, args.dpi))

            previews: list[str] = []
            if args.preview_dir:
                preview_dir = Path(args.preview_dir)
                preview_dir.mkdir(parents=True, exist_ok=True)
                for name, background in (("black", (20, 19, 19, 255)), ("white", (255, 255, 255, 255))):
                    flat = Image.new("RGBA", master.size, background)
                    flat.alpha_composite(master)
                    path = preview_dir / f"{Path(args.output).stem}_{name}.jpg"
                    flat.convert("RGB").save(path, quality=94)
                    previews.append(str(path))
                crop = master.crop((canvas_w // 2 - 800, canvas_h // 2 - 600, canvas_w // 2 + 800, canvas_h // 2 + 600))
                crop_path = preview_dir / f"{Path(args.output).stem}_100pct.png"
                crop.save(crop_path)
                previews.append(str(crop_path))

            report = verify(original, art, (canvas_w, canvas_h), args.dpi, svg_path, spec, mapping)
            result = {
                "ok": bool(report["passed"]),
                "pipeline": "craft_trace",
                "vectorcraft": vectorcraft,
                "svg": str(svg_path),
                "output": str(args.output),
                "canvas_px": [int(canvas_w), int(canvas_h)],
                "dpi": int(args.dpi),
                "art_px": [int(art.width), int(art.height)],
                "trace_params": params,
                "retyped": bool(args.retype_json),
                "svg_paths": report["svg_paths"],
                "svg_bytes": report["svg_bytes"],
                "previews": previews,
                "checks": report["checks"],
            }
            if args.report_json:
                Path(args.report_json).write_text(json.dumps(result, indent=2), encoding="utf-8")
            print(json.dumps({"ok": result["ok"], "checks": result["checks"]}, indent=2))
            return 0 if result["ok"] else 1
    except CraftTraceError as error:
        print(f"REFUSED {error.code}: {error.message}", file=sys.stderr)
        print(f"  how_to_fix: {error.how_to_fix}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
