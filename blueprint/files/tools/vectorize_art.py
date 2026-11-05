#!/usr/bin/env python3
"""Vectorise flat artwork, then render it at print resolution.

The raster path (prep_print_art) upscales pixels and softens edges. For flat
illustration/logo art that is avoidable: trace the cutout to SVG with vtracer,
render the SVG with rsvg-convert at the exact print pixel size, and compose the
result on the provider canvas. Edges stay crisp at any size.

Usage (inside /opt/pod-pipeline):

    .venv/bin/python -m tools.vectorize_art \
      --input data/ai-uploads/logo.jpg \
      --svg data/ai-uploads/logo.svg \
      --template pro_e4677535402b4eeb81 --area front_large --dpi 300 --print-width-in 8 \
      --output data/ai-uploads/print_master.png \
      --report-json data/ai-uploads/print_master.report.json \
      --preview-dir data/ai-uploads/previews
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageEnhance

from tools.prep_print_art import drop_small_components

try:  # installed in the pipeline venv
    import vtracer
except ImportError:  # pragma: no cover - reported, never hidden
    vtracer = None

KEY_COLOR = (255, 0, 255)


def flatten_on_key(cutout: Path, target: Path, colors: int, binary_alpha: bool, alpha_threshold: int) -> Path:
    """Composite the transparent cutout on a magenta key, then optionally quantise.

    vtracer flattens RGBA to a background colour, which reinstates the white
    border we just removed. A colour that never appears in the art is used as the
    key instead; the matching SVG paths are dropped afterwards so the render is
    genuinely transparent.

    The important detail learned in testing: trace from a HARD alpha edge. Any
    half-transparent cutout pixel becomes a blend between art and key, which the
    tracer turns into a pink rim. Binarising alpha first removes those pixels, so
    the traced outline is clean.
    """
    art = Image.open(cutout).convert("RGBA")
    canvas = Image.new("RGBA", art.size, (*KEY_COLOR, 255))
    alpha = art.getchannel("A")
    mask = alpha.point(lambda value: 255 if value >= alpha_threshold else 0) if binary_alpha else alpha
    canvas.paste(art.convert("RGB"), (0, 0), mask)
    rgb = canvas.convert("RGB")
    if colors > 0:
        rgb = rgb.quantize(colors=colors, method=Image.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")
    rgb.save(target)
    return target


def strip_key_fills(svg_path: Path, tolerance: int = 120) -> int:
    """Replace key-coloured fills with none, so the SVG has real transparency."""
    text = svg_path.read_text(encoding="utf-8")
    removed = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal removed
        value = match.group(1)
        try:
            red, green, blue = int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)
        except ValueError:
            return match.group(0)
        distance = abs(red - KEY_COLOR[0]) + abs(green - KEY_COLOR[1]) + abs(blue - KEY_COLOR[2])
        if distance <= tolerance:
            removed += 1
            return 'fill="none"'
        return match.group(0)

    text = re.sub(r'fill="#([0-9a-fA-F]{6})"', replace, text)
    svg_path.write_text(text, encoding="utf-8")
    return removed


class VectorizeError(RuntimeError):
    def __init__(self, code: str, message: str, how_to_fix: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
        self.how_to_fix = how_to_fix


def geometry(args: argparse.Namespace) -> tuple[int, int, str]:
    """Canvas pixels + a description of where the geometry came from."""
    if args.canvas_width and args.canvas_height:
        return args.canvas_width, args.canvas_height, "explicit"
    details = Path(args.details) if args.details else Path("config/fourthwall-template-details.json")
    if not details.is_file():
        raise VectorizeError("E_GEOMETRY_MISSING", f"{details} does not exist.", "Run tools.fetch_fourthwall_details or pass --canvas-width/--canvas-height.")
    rows = json.loads(details.read_text(encoding="utf-8"))
    row = next((r for r in rows if r.get("productId") == args.template), None)
    if row is None:
        raise VectorizeError("E_TEMPLATE_UNKNOWN", f"Template {args.template} is not in the catalogue.", "Fetch the catalogue first.")
    if not row.get("supportsBackendRendering") or row.get("productionMethod") == "KNITTING":
        raise VectorizeError("E_TEMPLATE_UNRENDERABLE", f"{row.get('name')} cannot take a backend-rendered design.", "Pick a renderable template.")
    dims = (row.get("areaGeometry") or {}).get(args.area)
    if not dims:
        raise VectorizeError("E_AREA_UNKNOWN", f'No geometry for area "{args.area}".', "Pass a known area or explicit canvas pixels.")
    return round(float(dims["inchesWidth"]) * args.dpi), round(float(dims["inchesHeight"]) * args.dpi), f"template:{args.template}/{args.area}"


def cutout_source(args: argparse.Namespace, temp_dir: Path) -> Path:
    """Produce a transparent, source-resolution cutout without upscaling."""
    src = Image.open(args.input)
    if args.cutout == "none":
        return Path(args.input)
    if args.cutout == "auto" and src.mode == "RGBA" and src.getchannel("A").getextrema()[0] < 255:
        return Path(args.input)
    side = max(src.size)
    target = temp_dir / "cutout.png"
    command = [
        sys.executable, "-m", "tools.prep_print_art",
        "--input", str(Path(args.input).resolve()), "--output", str(target),
        "--width-px", str(side), "--height-px", str(side), "--dpi", "300",
        "--mode", "white", "--clean-rim", "--min-component", str(args.min_component),
        "--margin-px", "0", "--print-width-in", f"{side / 300:.6f}",
    ]
    result = subprocess.run(command, cwd=Path.cwd(), capture_output=True, text=True)
    if result.returncode != 0 or not target.is_file():
        raise VectorizeError("E_CUTOUT_FAILED", "The white-background cutout failed.", result.stderr[-500:])
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Vectorise flat art and render it at print resolution.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--svg", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--template")
    parser.add_argument("--area", default="front_large")
    parser.add_argument("--details")
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--print-width-in", type=float, default=8.0)
    parser.add_argument("--canvas-width", type=int)
    parser.add_argument("--canvas-height", type=int)
    parser.add_argument("--cutout", choices=("auto", "white", "none"), default="auto")
    parser.add_argument("--min-component", type=int, default=40)
    parser.add_argument("--quantize-colors", type=int, default=0, help="Pre-quantise before tracing (0 keeps full colour)")
    parser.add_argument("--palette", dest="quantize_colors", type=int, help="Alias for --quantize-colors")
    parser.add_argument("--binary-alpha", action="store_true", default=True, help="Trace from a hard alpha edge (removes key-blend rims)")
    parser.add_argument("--no-binary-alpha", dest="binary_alpha", action="store_false")
    parser.add_argument("--alpha-threshold", type=int, default=128)
    parser.add_argument("--art-min-component", type=int, default=200, help="Drop specks smaller than this in the rendered art")
    parser.add_argument("--filter-speckle", type=int, default=8)
    parser.add_argument("--color-precision", type=int, default=6)
    parser.add_argument("--layer-difference", type=int, default=24)
    parser.add_argument("--brightness", type=float, default=1.0)
    parser.add_argument("--saturation", type=float, default=1.0)
    parser.add_argument("--report-json")
    parser.add_argument("--preview-dir")
    args = parser.parse_args(argv)

    if vtracer is None:
        print("REFUSED E_VTRACER_MISSING: vtracer is not installed in this venv", file=sys.stderr)
        return 2
    try:
        canvas_w, canvas_h, geometry_source = geometry(args)
        with tempfile.TemporaryDirectory() as temp:
            cutout = cutout_source(args, Path(temp))
            keyed = flatten_on_key(cutout, Path(temp) / "keyed.png", args.quantize_colors, args.binary_alpha, args.alpha_threshold)
            svg_path = Path(args.svg)
            svg_path.parent.mkdir(parents=True, exist_ok=True)
            vtracer.convert_image_to_svg_py(
                str(keyed), str(svg_path),
                colormode="color", hierarchical="stacked", mode="spline",
                filter_speckle=args.filter_speckle, color_precision=args.color_precision,
                layer_difference=args.layer_difference, corner_threshold=60, length_threshold=4.0,
                max_iterations=10, splice_threshold=45, path_precision=3,
            )
            key_paths_removed = strip_key_fills(svg_path)
        art_width = round(args.print_width_in * args.dpi)
        rendered = Path(tempfile.mkdtemp()) / "render.png"
        render = subprocess.run(["rsvg-convert", "-w", str(art_width), "-o", str(rendered), str(svg_path)], capture_output=True, text=True)
        if render.returncode != 0 or not rendered.is_file():
            raise VectorizeError("E_RENDER_FAILED", "rsvg-convert could not render the SVG.", render.stderr[-400:])
        art = Image.open(rendered).convert("RGBA")
        if args.art_min_component > 0:
            cleaned = drop_small_components(art.getchannel("A").copy(), args.art_min_component)
            art.putalpha(cleaned)
        if args.brightness != 1.0 or args.saturation != 1.0:
            colour = art.convert("RGB")
            if args.brightness != 1.0:
                colour = ImageEnhance.Brightness(colour).enhance(args.brightness)
            if args.saturation != 1.0:
                colour = ImageEnhance.Color(colour).enhance(args.saturation)
            boosted = colour.convert("RGBA")
            boosted.putalpha(art.getchannel("A"))
            art = boosted
        master = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        if art.width > canvas_w or art.height > canvas_h:
            raise VectorizeError("E_ART_TOO_BIG", f"Rendered art {art.size} exceeds canvas {(canvas_w, canvas_h)}.", "Reduce --print-width-in or pick a larger area.")
        master.alpha_composite(art, ((canvas_w - art.width) // 2, (canvas_h - art.height) // 2))
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

        svg_text = svg_path.read_text(encoding="utf-8")
        report = {
            "ok": True,
            "vectorized": True,
            "input": str(args.input),
            "svg": str(svg_path),
            "svg_bytes": svg_path.stat().st_size,
            "svg_paths": svg_text.count("<path"),
            "key_paths_removed": key_paths_removed,
            "output": str(args.output),
            "canvas_px": [canvas_w, canvas_h],
            "dpi": args.dpi,
            "canvas_inches": [round(canvas_w / args.dpi, 2), round(canvas_h / args.dpi, 2)],
            "art_px": list(art.size),
            "geometry_source": geometry_source,
            "print_width_in": args.print_width_in,
            "previews": previews,
            "warnings": [],
        }
        if args.report_json:
            Path(args.report_json).write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps({key: report[key] for key in ("ok", "vectorized", "svg_paths", "art_px", "canvas_px", "dpi")}, indent=2))
        return 0
    except VectorizeError as error:
        print(f"REFUSED {error.code}: {error.message}", file=sys.stderr)
        print(f"  how_to_fix: {error.how_to_fix}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
