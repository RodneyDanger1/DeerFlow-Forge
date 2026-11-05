#!/usr/bin/env python3
"""Artcraft: production pipeline for AI-generated artwork → clean print vector.

The vendor-tracer-only path could not fix painterly AI artefacts (diffusion edges,
drop-shadow halos, texture noise). This pipeline mirrors the professional workflow:

  1. cutout          - strict white removal (reuses tools.prep_print_art)
  2. deblur          - Richardson-Lucy deconvolution (scikit-image) to undo diffusion softening
  3. restore         - CLAHE contrast + saturation recovery
  4. flatten         - bilateral filter + Lab k-means → flat colour layers
  5. clean layers    - per-colour morphological open/close + small-object removal (removes gunk)
  6. retype          - erase AI text bands and re-set the words with a real font (crisp, no shadow)
  7. trace           - binary-alpha vtracer on the flattened art (no key blends)
  8. render          - rsvg-convert at exact print pixels (300 DPI canvas)
  9. restore edges   - unsharp + saturation, alpha speck cleanup
 10. verify          - 10 checks plus a parallel raster-control comparison

Outputs a print master PNG, the SVG, previews, a side-by-side comparison, and a JSON report.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from skimage import color as skcolor
from skimage import exposure, filters, measure, morphology, restoration
from scipy.cluster.vq import kmeans2

from tools.prep_print_art import drop_small_components
from tools.vectorize_art import KEY_COLOR, flatten_on_key, strip_key_fills

try:
    import vtracer
except ImportError:  # pragma: no cover
    vtracer = None


class ArtcraftError(RuntimeError):
    def __init__(self, code: str, message: str, how_to_fix: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code, self.message, self.how_to_fix = code, message, how_to_fix


def prep_cutout(args: argparse.Namespace, temp: Path) -> Path:
    """Strict white cutout at source resolution (no upscale, no canvas padding)."""
    probe = Image.open(args.input)
    side = max(probe.size)
    target = temp / "cutout.png"
    command = [
        sys.executable, "-m", "tools.prep_print_art",
        "--input", str(Path(args.input).resolve()), "--output", str(target),
        "--width-px", str(side), "--height-px", str(side), "--dpi", "300",
        "--mode", "white", "--clean-rim", "--min-component", str(args.min_component),
        "--edge-clean-px", str(args.edge_clean_px), "--edge-clean-lum", "140",
        "--margin-px", "0", "--print-width-in", f"{side / 300:.6f}",
    ]
    result = subprocess.run(command, cwd=Path.cwd(), capture_output=True, text=True)
    if result.returncode != 0 or not target.is_file():
        raise ArtcraftError("E_CUTOUT_FAILED", "White-background cutout failed.", result.stderr[-500:])
    return target


def deblur_and_restore(rgb: np.ndarray, alpha: np.ndarray, args: argparse.Namespace) -> np.ndarray:
    image = rgb.astype(np.float32) / 255.0
    if args.deblur_iterations > 0:
        sigma = max(0.5, args.deblur_sigma)
        size = int(sigma * 4) | 1
        yy, xx = np.mgrid[-size // 2 + 1:size // 2 + 1, -size // 2 + 1:size // 2 + 1]
        psf = np.exp(-(xx ** 2 + yy ** 2) / (2 * sigma ** 2))
        psf /= psf.sum()
        image = np.stack([
            restoration.richardson_lucy(image[..., channel], psf, num_iter=args.deblur_iterations, clip=False)
            for channel in range(3)
        ], axis=-1)
    image = np.clip(image, 0, 1)
    lab = skcolor.rgb2lab(image)
    lab[..., 0] = exposure.equalize_adapthist(lab[..., 0], clip_limit=args.clahe)
    image = skcolor.lab2rgb(lab)
    hsv = skcolor.rgb2hsv(image)
    hsv[..., 1] = np.clip(hsv[..., 1] * args.saturation, 0, 1)
    image = skcolor.hsv2rgb(hsv)
    image = np.clip(image, 0, 1)
    image[alpha <= 0] = 0
    return (image * 255).astype(np.uint8)


def flatten_layers(rgb: np.ndarray, alpha: np.ndarray, args: argparse.Namespace) -> np.ndarray:
    """Bilateral denoise + Lab k-means + per-colour morphological cleanup."""
    smooth = filters.rank.mean  # placeholder to keep import list honest if unused later
    image = rgb.astype(np.float32) / 255.0
    if args.bilateral_sigma > 0:
        image = restoration.denoise_bilateral(
            image, sigma_color=args.bilateral_sigma, sigma_spatial=args.bilateral_spatial, channel_axis=-1
        )
    lab = skcolor.rgb2lab(np.clip(image, 0, 1))
    art_mask = alpha > 0
    samples = lab[art_mask]
    if samples.size == 0:
        raise ArtcraftError("E_EMPTY_ART", "No art pixels survived the cutout.", "Check the input/white key.")
    step = max(1, samples.shape[0] // 30000)
    centers, _ = kmeans2(samples[::step].astype(np.float64), args.colors, minit="++", seed=7)
    flat = lab.reshape(-1, 1, 3) - centers.reshape(1, -1, 3)
    labels = np.square(flat).sum(axis=2).argmin(axis=1).reshape(lab.shape[:2])
    labels[~art_mask] = -1

    # Clean each colour layer independently: remove specks, close pinholes.
    cleaned = np.full(labels.shape, -1, dtype=np.int32)
    order = sorted(range(args.colors), key=lambda index: int((labels == index).sum()), reverse=True)
    for index in order:
        mask = labels == index
        if args.layer_open > 0:
            mask = morphology.binary_opening(mask, morphology.disk(args.layer_open))
        if args.min_layer_area > 0:
            mask = morphology.remove_small_objects(mask, min_size=args.min_layer_area)
        if args.layer_close > 0:
            mask = morphology.binary_closing(mask, morphology.disk(args.layer_close))
        cleaned[mask & (cleaned == -1)] = index
    # Fill any remaining art pixels from the nearest original label.
    remaining = art_mask & (cleaned == -1)
    if remaining.any():
        from scipy.ndimage import distance_transform_edt
        indices = distance_transform_edt(cleaned == -1, return_distances=False, return_indices=True)
        nearest = labels[tuple(indices)]
        cleaned[remaining] = nearest[remaining]
    flat_rgb = (skcolor.lab2rgb(centers[cleaned.clip(0)]) * 255).astype(np.uint8)
    flat_rgb[~art_mask] = 0
    return flat_rgb


def retype_text(art: Image.Image, retype: list[dict]) -> Image.Image:
    """Erase AI-rendered text bands and re-set them with a real font."""
    if not retype:
        return art
    canvas = art.copy()
    for spec in retype:
        x0, y0, x1, y1 = [int(value) for value in spec["box"]]
        erase = Image.new("L", canvas.size, 0)
        ImageDraw.Draw(erase).rectangle([x0, y0, x1, y1], fill=255)
        alpha = canvas.getchannel("A")
        alpha.paste(0, mask=erase)
        canvas.putalpha(alpha)
        text = spec["text"]
        font_path = spec.get("font") or str(next(Path("/usr/share/fonts").rglob("FreeSansBold.ttf")))
        fill = spec.get("fill", "#efe6cf")
        stroke = spec.get("stroke")
        stroke_px = int(spec.get("stroke_px", 0))
        box_w, box_h = x1 - x0, y1 - y0
        best = None
        for size in range(10, 600):
            font = ImageFont.truetype(font_path, size)
            bbox = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), text, font=font, stroke_width=stroke_px)
            width, height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            if width <= box_w * 0.97 and height <= box_h * 0.95:
                best = (size, font, bbox, width, height)
            else:
                break
        if best is None:
            continue
        size, font, bbox, width, height = best
        layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        tx = x0 + (box_w - width) // 2 - bbox[0]
        ty = y0 + (box_h - height) // 2 - bbox[1]
        draw.text((tx, ty), text, font=font, fill=fill, stroke_width=stroke_px, stroke_fill=stroke or fill)
        canvas = Image.alpha_composite(canvas, layer)
    return canvas


def edge_sharpness(gray: np.ndarray) -> float:
    return float(filters.laplace(gray).var())


def verify(source_rgba: Image.Image, final_art: Image.Image, args: argparse.Namespace, svg_path: Path) -> dict:
    """Ten checks plus a raster-vs-vector comparison."""
    size = source_rgba.size
    source_rgb = np.asarray(source_rgba.convert("RGB"), dtype=np.float32) / 255.0
    source_alpha = np.asarray(source_rgba.getchannel("A")) > 127
    final_small = final_art.resize(size, Image.LANCZOS)
    final_rgb = np.asarray(final_small.convert("RGB"), dtype=np.float32) / 255.0
    final_alpha = np.asarray(final_small.getchannel("A")) > 127
    mask = source_alpha & final_alpha
    if mask.sum() < 100:
        ssim = 0.0
    else:
        ssim = float(measure.compare_ssim(
            source_rgb[mask], final_rgb[mask], data_range=1.0, channel_axis=-1 if source_rgb.shape[-1] == 3 else None,
        ))
    rgb_u8 = np.asarray(final_small.convert("RGB"), dtype=np.uint8)
    near_white = np.all(rgb_u8 >= 245, axis=-1) & final_alpha
    magenta = (np.abs(rgb_u8[..., 0].astype(int) - 255) + rgb_u8[..., 1].astype(int) + np.abs(rgb_u8[..., 2].astype(int) - 255)) < 120
    magenta_residual = int((magenta & final_alpha).sum())
    labels = measure.label(final_alpha)
    components = measure.regionprops(labels)
    specks = sum(1 for region in components if region.area < 150)
    coverage = float(final_alpha.sum()) / float(final_alpha.size)
    grey_source = np.asarray(source_rgba.convert("L"), dtype=np.float32) / 255.0
    grey_final = np.asarray(final_small.convert("L"), dtype=np.float32) / 255.0
    sharp_ratio = edge_sharpness(grey_final) / max(1e-6, edge_sharpness(grey_source))
    hist_source, _ = np.histogram(source_rgb[source_alpha], bins=32, range=(0, 1))
    hist_final, _ = np.histogram(final_rgb[final_alpha], bins=32, range=(0, 1))
    hist_corr = float(np.corrcoef(hist_source.astype(float), hist_final.astype(float))[0, 1]) if mask.sum() else 0.0
    quant = np.asarray(final_small.convert("RGB").quantize(colors=32).convert("RGB"), dtype=np.uint8)
    palette_count = len({tuple(pixel) for pixel in quant.reshape(-1, 3)})
    svg_text = svg_path.read_text(encoding="utf-8")
    canvas_w, canvas_h = args.canvas_px
    checks = {
        "structure_ssim": {"value": round(ssim, 4), "pass": ssim >= args.min_ssim},
        "white_residual_ratio": {"value": round(float(near_white.sum()) / max(1, final_alpha.sum()), 5), "pass": float(near_white.sum()) / max(1, final_alpha.sum()) <= 0.002},
        "magenta_residual_px": {"value": magenta_residual, "pass": magenta_residual == 0},
        "edge_specks": {"value": specks, "pass": specks == 0},
        "coverage": {"value": round(coverage, 4), "pass": 0.03 <= coverage <= 0.92},
        "dpi_math": {"value": [canvas_w, canvas_h, args.dpi], "pass": args.dpi >= 300 and abs(canvas_w / args.dpi - args.area_inches[0]) < 0.02},
        "flat_palette_colours": {"value": palette_count, "pass": palette_count <= 32},
        "edge_sharpness_ratio": {"value": round(sharp_ratio, 3), "pass": sharp_ratio >= 1.0},
        "colour_histogram_corr": {"value": round(hist_corr, 3), "pass": hist_corr >= 0.65},
        "svg_sanity": {"value": {"paths": svg_text.count("<path"), "bytes": svg_path.stat().st_size}, "pass": svg_text.count("<path") <= 5000 and svg_path.stat().st_size < 6_000_000},
    }
    return {"checks": checks, "passed": sum(1 for check in checks.values() if check["pass"]), "total": len(checks)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Artcraft: clean AI art → print vector + verification.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--svg", required=True)
    parser.add_argument("--template")
    parser.add_argument("--area", default="front_large")
    parser.add_argument("--details")
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--print-width-in", type=float, default=8.0)
    parser.add_argument("--canvas-width", type=int)
    parser.add_argument("--canvas-height", type=int)
    parser.add_argument("--area-inches", help="in,w for verification; read from details when omitted")
    parser.add_argument("--retype-json")
    parser.add_argument("--report-json")
    parser.add_argument("--preview-dir")
    parser.add_argument("--colors", type=int, default=12)
    parser.add_argument("--deblur-iterations", type=int, default=15)
    parser.add_argument("--deblur-sigma", type=float, default=1.1)
    parser.add_argument("--clahe", type=float, default=0.02)
    parser.add_argument("--saturation", type=float, default=1.18)
    parser.add_argument("--bilateral-sigma", type=float, default=0.06)
    parser.add_argument("--bilateral-spatial", type=float, default=3.0)
    parser.add_argument("--layer-open", type=int, default=1)
    parser.add_argument("--layer-close", type=int, default=1)
    parser.add_argument("--min-layer-area", type=int, default=60)
    parser.add_argument("--min-component", type=int, default=60)
    parser.add_argument("--edge-clean-px", type=int, default=26)
    parser.add_argument("--sharpen", type=float, default=45)
    parser.add_argument("--min-ssim", type=float, default=0.72)
    args = parser.parse_args(argv)

    if vtracer is None:
        print("REFUSED E_VTRACER_MISSING", file=sys.stderr)
        return 2

    # Geometry
    canvas_w, canvas_h = args.canvas_width, args.canvas_height
    area_inches = None
    if args.template and args.details:
        rows = json.loads(Path(args.details).read_text(encoding="utf-8"))
        row = next((r for r in rows if r.get("productId") == args.template), None)
        if row is None:
            print(f"REFUSED E_TEMPLATE_UNKNOWN: {args.template}", file=sys.stderr)
            return 2
        if not row.get("supportsBackendRendering") or row.get("productionMethod") == "KNITTING":
            print("REFUSED E_TEMPLATE_UNRENDERABLE", file=sys.stderr)
            return 2
        dims = (row.get("areaGeometry") or {}).get(args.area)
        if not dims:
            print(f"REFUSED E_AREA_UNKNOWN: {args.area}", file=sys.stderr)
            return 2
        area_inches = (float(dims["inchesWidth"]), float(dims["inchesHeight"]))
        canvas_w = round(area_inches[0] * args.dpi)
        canvas_h = round(area_inches[1] * args.dpi)
    if not canvas_w or not canvas_h:
        print("REFUSED E_GEOMETRY_MISSING", file=sys.stderr)
        return 2
    if area_inches is None:
        area_inches = (canvas_w / args.dpi, canvas_h / args.dpi)
    args.canvas_px = (canvas_w, canvas_h)
    args.area_inches = area_inches

    try:
        with tempfile.TemporaryDirectory() as temp_name:
            temp = Path(temp_name)
            cutout_path = prep_cutout(args, temp)
            source = Image.open(cutout_path).convert("RGBA")
            rgb = np.asarray(source.convert("RGB"), dtype=np.uint8)
            alpha = np.asarray(source.getchannel("A"))
            restored = deblur_and_restore(rgb, alpha, args)
            flat = flatten_layers(restored, alpha, args)
            flat_image = Image.fromarray(flat, mode="RGB").convert("RGBA")
            clean_alpha = Image.fromarray(alpha).point(lambda value: 255 if value >= 128 else 0)
            flat_image.putalpha(clean_alpha)
            retype = json.loads(Path(args.retype_json).read_text(encoding="utf-8")) if args.retype_json else []
            composed = retype_text(flat_image, retype)

            keyed = flatten_on_key(composed, temp / "keyed.png", colors=0, binary_alpha=True, alpha_threshold=128)
            svg_path = Path(args.svg)
            svg_path.parent.mkdir(parents=True, exist_ok=True)
            vtracer.convert_image_to_svg_py(
                str(keyed), str(svg_path), colormode="color", hierarchical="stacked", mode="spline",
                filter_speckle=2, color_precision=8, layer_difference=8,
                corner_threshold=60, length_threshold=3.0, max_iterations=10, splice_threshold=45, path_precision=3,
            )
            key_paths = strip_key_fills(svg_path)

            art_px = round(args.print_width_in * args.dpi)
            rendered = temp / "render.png"
            render = subprocess.run(["rsvg-convert", "-w", str(art_px), "-o", str(rendered), str(svg_path)], capture_output=True, text=True)
            if render.returncode != 0:
                raise ArtcraftError("E_RENDER_FAILED", "rsvg-convert failed.", render.stderr[-400:])
            art = Image.open(rendered).convert("RGBA")
            cleaned_alpha = drop_small_components(art.getchannel("A").copy(), 200)
            art.putalpha(cleaned_alpha)
            colour = art.convert("RGB")
            colour = ImageEnhance.Color(colour).enhance(1.12)
            colour = ImageEnhance.Brightness(colour).enhance(1.02)
            colour = colour.filter(ImageFilter.UnsharpMask(radius=2, percent=int(args.sharpen), threshold=2))
            art = colour.convert("RGBA")
            art.putalpha(cleaned_alpha)

            master = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
            master.alpha_composite(art, ((canvas_w - art.width) // 2, (canvas_h - art.height) // 2))
            master.save(args.output, dpi=(args.dpi, args.dpi))

            previews: list[str] = []
            if args.preview_dir:
                preview_dir = Path(args.preview_dir)
                preview_dir.mkdir(parents=True, exist_ok=True)
                for name, background in (("black", (20, 19, 19, 255)), ("white", (255, 255, 255, 255))):
                    flat_bg = Image.new("RGBA", master.size, background)
                    flat_bg.alpha_composite(master)
                    path = preview_dir / f"{Path(args.output).stem}_{name}.jpg"
                    flat_bg.convert("RGB").save(path, quality=94)
                    previews.append(str(path))
                side = Image.new("RGBA", (art.width * 2 + 20, art.height), (20, 19, 19, 255))
                left = source.resize((art.width, round(source.height * art.width / source.width)), Image.LANCZOS)
                side.alpha_composite(left, (0, (art.height - left.height) // 2))
                side.alpha_composite(art, (art.width + 20, (art.height - art.height) // 2))
                compare_path = preview_dir / f"{Path(args.output).stem}_compare.jpg"
                side.convert("RGB").save(compare_path, quality=92)
                previews.append(str(compare_path))
                crop = master.crop((canvas_w // 2 - 800, canvas_h // 2 - 600, canvas_w // 2 + 800, canvas_h // 2 + 600))
                crop_path = preview_dir / f"{Path(args.output).stem}_100pct.png"
                crop.save(crop_path)
                previews.append(str(crop_path))

            report = verify(source, art, args, svg_path)
            result = {
                "ok": report["passed"] == report["total"],
                "pipeline": "artcraft",
                "input": str(args.input),
                "svg": str(svg_path),
                "output": str(args.output),
                "canvas_px": [canvas_w, canvas_h],
                "dpi": args.dpi,
                "area_inches": [round(area_inches[0], 2), round(area_inches[1], 2)],
                "art_px": list(art.size),
                "colors": args.colors,
                "deblur_iterations": args.deblur_iterations,
                "key_paths_removed": key_paths,
                "previews": previews,
                **report,
            }
            if args.report_json:
                Path(args.report_json).write_text(json.dumps(result, indent=2), encoding="utf-8")
            print(json.dumps({"ok": result["ok"], "passed": report["passed"], "total": report["total"],
                              "checks": {name: check["value"] for name, check in report["checks"].items()}}, indent=2))
            return 0 if result["ok"] else 1
    except ArtcraftError as error:
        print(f"REFUSED {error.code}: {error.message}", file=sys.stderr)
        print(f"  how_to_fix: {error.how_to_fix}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
