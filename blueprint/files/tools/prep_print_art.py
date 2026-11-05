#!/usr/bin/env python3
"""Turn a raster artwork into a provider-ready print master.

Generalises the first successful run (2026-11-05, "Abyssal Signal" tee) into a
repeatable tool. It does NOT assume one image's magic numbers:

  * every threshold has a default, but `--report` prints the measured histogram
    statistics so an operator can see why a default fits or must be tuned;
  * hard gates refuse a bad output instead of shipping an invisible or
    background-filled design (coverage floor, coverage ceiling, empty bbox);
  * a DPI warning refuses to pretend a low-resolution source is print quality.

Usage (inside /opt/pod-pipeline):

    .venv/bin/python -m tools.prep_print_art \
      --input data/ai-uploads/art.jpg \
      --template pro_e4677535402b4eeb81 --area front_large \
      --dpi 300 --mode glow --brightness 1.18 --saturation 1.25 --bloom 6 \
      --output data/ai-uploads/print_master.png \
      --report-json data/ai-uploads/print_master.report.json

The template/area lookup uses config/fourthwall-template-details.json (written
by the catalogue fetch); geometry comes from the provider, never from a guess.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageEnhance, ImageFilter

MODES = ("glow", "lineart", "white", "white-flood", "alpha", "none")
DEFAULT_GATES = {"min_coverage": 0.005, "max_coverage": 0.62, "max_upscale": 2.5}


class PrepError(RuntimeError):
    """Named refusal: nothing is written when this is raised."""

    def __init__(self, code: str, message: str, how_to_fix: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
        self.how_to_fix = how_to_fix


def clamp01(value: float) -> float:
    return 0.0 if value <= 0 else 1.0 if value >= 1 else value


def image_stats(src: Image.Image) -> dict[str, float]:
    """Measured colour/luminance statistics used to justify threshold choice."""
    rgb = src.convert("RGB")
    width = rgb.width
    small = rgb.resize((min(400, width), max(1, round(min(400, width) * rgb.height / width))))
    pixels = list(small.getdata())
    lums = [0.2126 * r + 0.7152 * g + 0.0722 * b for r, g, b in pixels]
    lums.sort()
    bright = [(r, g, b) for (r, g, b) in pixels if (0.2126 * r + 0.7152 * g + 0.0722 * b) > lums[int(len(lums) * 0.9)]]
    cyan = sum(1 for r, g, b in bright if b > r * 1.15 and g > r * 1.05) / max(1, len(bright))
    chroma = statistics.fmean([max(p) - min(p) for p in bright]) if bright else 0.0
    border: list[tuple[int, int, int]] = []
    step = max(1, small.width // 24)
    for x in range(0, small.width, step):
        border.append(pixels[x])
        border.append(pixels[(small.height - 1) * small.width + x])
    for y in range(0, small.height, step):
        border.append(pixels[y * small.width])
        border.append(pixels[y * small.width + small.width - 1])
    near_white = sum(1 for (r, g, b) in border if min(r, g, b) >= 255 - 26) / max(1, len(border))
    return {
        "luminance_median": round(statistics.median(lums), 1),
        "luminance_p90": round(lums[int(len(lums) * 0.9)], 1),
        "luminance_p99": round(lums[min(len(lums) - 1, int(len(lums) * 0.99))], 1),
        "bright_pixel_cyan_fraction": round(cyan, 3),
        "bright_pixel_mean_chroma": round(chroma, 1),
        "border_near_white_fraction": round(near_white, 3),
    }


def choose_mode(stats: dict[str, float]) -> str:
    """White-locked background → white key; colourful subject on dark → glow."""
    if stats["border_near_white_fraction"] >= 0.9:
        return "white"
    if stats["bright_pixel_cyan_fraction"] >= 0.45 and stats["bright_pixel_mean_chroma"] >= 60:
        return "glow"
    return "lineart"


def drop_small_components(mask: Image.Image, min_area: int) -> Image.Image:
    """Zero out isolated specks (paper texture highlights) that survive the key."""
    width, height = mask.size
    alpha = mask.load()
    seen = bytearray(width * height)
    stack: list[tuple[int, int]] = []
    for y in range(height):
        for x in range(width):
            index = y * width + x
            if seen[index] or alpha[x, y] < 16:
                continue
            component: list[tuple[int, int]] = []
            stack.append((x, y))
            seen[index] = 1
            while stack:
                cx, cy = stack.pop()
                component.append((cx, cy))
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if nx < 0 or ny < 0 or nx >= width or ny >= height:
                        continue
                    neighbour = ny * width + nx
                    if seen[neighbour] or alpha[nx, ny] < 16:
                        continue
                    seen[neighbour] = 1
                    stack.append((nx, ny))
            if len(component) < min_area:
                for cx, cy in component:
                    alpha[cx, cy] = 0
    return mask


def white_key_alpha(src: Image.Image, args: argparse.Namespace) -> Image.Image:
    """Remove EVERY neutral-white pixel, not just the border-connected ones.

    This is the owner's rule for the Ridgeboundia badge: white is the only colour
    that becomes transparent, everywhere (background, torn-paper edge, snow, sky),
    while saturated colours and cream/tan lettering are kept. A flood fill is
    available as `white-flood` when enclosed whites must survive instead.
    """
    rgb = src.convert("RGB")
    width, height = rgb.size
    pixels = rgb.load()
    mask = Image.new("L", (width, height))
    out = mask.load()
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            maximum = max(r, g, b)
            minimum = min(r, g, b)
            lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
            saturation = 0.0 if maximum == 0 else (maximum - minimum) / maximum
            neutral = clamp01((args.white_saturation - saturation) / 0.06)
            bright = clamp01((lum - args.white_lum_floor) / 100)
            whiteness = neutral * bright
            alpha = 1.0 - whiteness
            out[x, y] = 0 if alpha < args.alpha_floor else int(round(alpha * 255))
    if args.min_component > 0:
        mask = drop_small_components(mask, args.min_component)
    if args.clean_rim:
        # Torn-paper shadows and antialiased white edges survive as semi-transparent
        # grey rims. Threshold hard, erode one pixel, then re-soften the edge.
        mask = mask.point(lambda v: 0 if v < 128 else 255)
        mask = mask.filter(ImageFilter.MinFilter(3))
    if args.edge_clean_px > 0:
        # Light paper flecks cling to the outer silhouette. Remove light pixels that
        # sit close to the transparent exterior, leaving interior cream lettering.
        transparent = mask.point(lambda v: 255 if v < 16 else 0)
        near_background = transparent.filter(ImageFilter.MaxFilter(args.edge_clean_px * 2 + 1))
        luminance = src.convert("L")
        mask_px = mask.load()
        near_px = near_background.load()
        lum_px = luminance.load()
        for y in range(height):
            for x in range(width):
                if near_px[x, y] > 0 and lum_px[x, y] > args.edge_clean_lum and mask_px[x, y] > 0:
                    mask_px[x, y] = 0
    return mask.filter(ImageFilter.GaussianBlur(args.feather))


def white_flood_alpha(src: Image.Image, tolerance: float) -> Image.Image:
    """Remove the border-connected near-white background, keep enclosed whites.

    Flood fill from the frame edges only. White *inside* the subject (a snow cap,
    a white letter enclosed by ink) is not reachable from the border, so it stays
    opaque — the difference between "background removed" and "all white erased".
    """
    rgb = src.convert("RGB")
    width, height = rgb.size
    pixels = rgb.load()
    alpha = Image.new("L", (width, height), 255)
    visited = bytearray(width * height)
    stack: list[tuple[int, int]] = []
    for x in range(width):
        stack.append((x, 0))
        stack.append((x, height - 1))
    for y in range(height):
        stack.append((0, y))
        stack.append((width - 1, y))
    limit = tolerance * 3
    while stack:
        x, y = stack.pop()
        if x < 0 or y < 0 or x >= width or y >= height:
            continue
        index = y * width + x
        if visited[index]:
            continue
        r, g, b = pixels[x, y]
        if (255 - r) + (255 - g) + (255 - b) > limit:
            continue
        visited[index] = 1
        alpha.putpixel((x, y), 0)
        stack.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    return alpha


def build_alpha(src: Image.Image, args: argparse.Namespace) -> Image.Image:
    width, height = src.size
    mode = args.mode
    if mode == "alpha":
        if src.mode != "RGBA":
            raise PrepError("E_ALPHA_MISSING", "The input has no alpha channel.", "Use --mode glow/lineart/white for opaque inputs.")
        return src.getchannel("A").copy()
    if mode == "white":
        return white_key_alpha(src, args)
    if mode == "white-flood":
        return white_flood_alpha(src, args.white_tolerance).filter(ImageFilter.GaussianBlur(args.feather))
    pixels = src.convert("RGB").load()
    mask = Image.new("L", (width, height))
    out = mask.load()
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
            if mode == "glow":
                a_lum = clamp01((lum - args.lum_floor) / args.lum_div)
                a_chroma = clamp01((b - r - args.cyan_floor) / args.cyan_div)
                alpha = min(a_lum, a_chroma) ** args.gamma
            elif mode == "lineart":
                value = 255 - lum if args.invert else lum
                alpha = clamp01((value - args.lum_floor) / args.lum_div) ** args.gamma
            else:
                alpha = 1.0
            out[x, y] = 0 if alpha < args.alpha_floor else int(round(alpha * 255))
    mask = mask.filter(ImageFilter.MedianFilter(args.median))
    if args.min_component > 0:
        mask = drop_small_components(mask, args.min_component)
    if args.feather > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(args.feather))
    return mask


def resolve_canvas(args: argparse.Namespace) -> tuple[int, int, str]:
    """Return (width_px, height_px, source) — provider geometry or explicit px."""
    if args.width_px and args.height_px:
        return args.width_px, args.height_px, "explicit"
    if not args.template or not args.area:
        raise PrepError(
            "E_GEOMETRY_MISSING",
            "No canvas geometry was given.",
            "Pass --template <productId> --area <region> with the details JSON, or --width-px/--height-px.",
        )
    details_path = Path(args.details) if args.details else Path("config/fourthwall-template-details.json")
    if not details_path.is_file():
        raise PrepError(
            "E_GEOMETRY_MISSING",
            f"The template details file {details_path} does not exist.",
            "Run the catalogue fetch first (tools/fetch_fourthwall_details.py) or pass --width-px/--height-px.",
        )
    rows = json.loads(details_path.read_text(encoding="utf-8"))
    row = next((r for r in rows if r.get("productId") == args.template), None)
    if row is None:
        raise PrepError("E_TEMPLATE_UNKNOWN", f"Template {args.template} is not in {details_path}.", "Fetch the catalogue first.")
    if not row.get("supportsBackendRendering") or row.get("productionMethod") == "KNITTING":
        raise PrepError(
            "E_TEMPLATE_UNRENDERABLE",
            f"{row.get('name')} cannot take a backend-rendered design image.",
            "Pick a template with supportsBackendRendering=true and a non-KNITTING production method.",
        )
    areas = row.get("areas") or []
    # The compact details file only carries names; geometry comes from the live
    # area dimensions the fetch can enrich (or the CLI flags).
    geometry = row.get("areaGeometry") or {}
    dims = geometry.get(args.area)
    if not dims:
        raise PrepError(
            "E_AREA_UNKNOWN",
            f'Template {args.template} has no recorded geometry for area "{args.area}" (known: {[a.get("name") for a in areas]}).',
            "Enrich the details file with areaGeometry {area: {inchesWidth, inchesHeight}} or pass --width-px/--height-px.",
        )
    width_px = round(float(dims["inchesWidth"]) * args.dpi)
    height_px = round(float(dims["inchesHeight"]) * args.dpi)
    return width_px, height_px, f"template:{args.template}/{args.area}"


def run(args: argparse.Namespace) -> dict[str, Any]:
    source = Path(args.input)
    if not source.is_file():
        raise PrepError("E_INPUT_MISSING", f"Input image {source} does not exist.", "Check the path.")
    src = Image.open(source).convert("RGBA")
    stats = image_stats(src)
    if args.mode == "auto":
        args.mode = choose_mode(stats)

    width_px, height_px, geometry_source = resolve_canvas(args)
    mask = build_alpha(src, args)
    coverage = sum(1 for value in mask.getdata() if value > 8) / (mask.width * mask.height)
    bbox = mask.point(lambda value: 255 if value > 12 else 0).getbbox()
    if bbox is None or coverage < args.min_coverage:
        raise PrepError(
            "E_SUBJECT_EMPTY",
            f"The mask removed everything (coverage {coverage:.4f}); thresholds are wrong for this image.",
            f"Lower --lum-floor/--cyan-floor or raise --gamma, then re-run. Measured stats: {json.dumps(stats)}.",
        )
    if coverage > args.max_coverage:
        raise PrepError(
            "E_SUBJECT_FULL_FRAME",
            f"The mask kept {coverage:.1%} of the frame, which means the background was not separated.",
            "Raise the thresholds or use --mode none deliberately for a full-bleed print.",
        )

    art = src.copy()
    art.putalpha(mask)
    art = art.crop(bbox)
    if args.brightness != 1.0:
        art = ImageEnhance.Brightness(art).enhance(args.brightness)
    if args.saturation != 1.0:
        art = ImageEnhance.Color(art).enhance(args.saturation)
    if args.bloom > 0:
        art = Image.alpha_composite(art.filter(ImageFilter.GaussianBlur(args.bloom)), art)

    margin = args.margin_px
    usable = max(1, width_px - 2 * margin)
    if args.print_width_in:
        usable = max(1, min(usable, round(args.print_width_in * args.dpi)))
    upscale = usable / art.width
    scaled = art.resize((usable, max(1, round(art.height * usable / art.width))), Image.LANCZOS)
    master = Image.new("RGBA", (width_px, height_px), (0, 0, 0, 0))
    master.alpha_composite(scaled, ((width_px - scaled.width) // 2, (height_px - scaled.height) // 2))
    if args.sharpen > 0:
        alpha = master.getchannel("A")
        sharpened = master.convert("RGB").filter(ImageFilter.UnsharpMask(radius=2, percent=int(args.sharpen), threshold=2))
        master = sharpened.convert("RGBA")
        master.putalpha(alpha)
    master.save(args.output, dpi=(args.dpi, args.dpi))

    warnings: list[str] = []
    if upscale > args.max_upscale:
        warnings.append(
            f"source upscaled {upscale:.2f}x (gate {args.max_upscale}x): glow art tolerates this, fine line art will not. "
            "Regenerate the source at a higher resolution for crisp linework."
        )
    previews: list[str] = []
    if args.preview_dir:
        preview_dir = Path(args.preview_dir)
        preview_dir.mkdir(parents=True, exist_ok=True)
        for name, background in (("black", (20, 19, 19, 255)), ("white", (255, 255, 255, 255))):
            flat = Image.new("RGBA", master.size, background)
            flat.alpha_composite(master)
            path = preview_dir / f"{Path(args.output).stem}_{name}.jpg"
            flat.convert("RGB").save(path, quality=92)
            previews.append(str(path))

    report = {
        "ok": True,
        "input": str(source),
        "output": str(args.output),
        "mode": args.mode,
        "geometry_source": geometry_source,
        "canvas_px": [width_px, height_px],
        "dpi": args.dpi,
        "canvas_inches": [round(width_px / args.dpi, 2), round(height_px / args.dpi, 2)],
        "subject_bbox": list(bbox),
        "subject_px": [bbox[2] - bbox[0], bbox[3] - bbox[1]],
        "coverage": round(coverage, 4),
        "upscale_factor": round(upscale, 3),
        "print_width_in": args.print_width_in,
        "usable_width_px": usable,
        "source_stats": stats,
        "thresholds": {
            "lum_floor": args.lum_floor, "lum_div": args.lum_div,
            "cyan_floor": args.cyan_floor, "cyan_div": args.cyan_div,
            "alpha_floor": args.alpha_floor, "gamma": args.gamma,
            "median": args.median, "feather": args.feather,
        },
        "previews": previews,
        "warnings": warnings,
    }
    if args.report_json:
        Path(args.report_json).write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare a raster artwork as a Fourthwall print master.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--mode", choices=("auto", "glow", "lineart", "white", "white-flood", "alpha", "none"), default="auto")
    parser.add_argument("--template", help="Fourthwall productTemplateId (geometry lookup)")
    parser.add_argument("--area", default="front_large")
    parser.add_argument("--details", help="Path to fourthwall-template-details.json")
    parser.add_argument("--width-px", type=int)
    parser.add_argument("--height-px", type=int)
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--margin-px", type=int, default=100)
    parser.add_argument("--white-tolerance", type=float, default=26.0, help="white-flood mode: per-channel distance from 255 treated as background")
    parser.add_argument("--white-saturation", type=float, default=0.135, help="white mode: max saturation still treated as white")
    parser.add_argument("--white-lum-floor", type=float, default=140.0, help="white mode: luminance below this is always kept")
    parser.add_argument("--clean-rim", action="store_true", default=True, help="white mode: drop semi-transparent white rim pixels")
    parser.add_argument("--no-clean-rim", dest="clean_rim", action="store_false")
    parser.add_argument("--min-component", type=int, default=24, help="white mode: drop isolated specks smaller than this many pixels")
    parser.add_argument("--edge-clean-px", type=int, default=0, help="white mode: radius near transparent exterior to strip light flecks")
    parser.add_argument("--edge-clean-lum", type=int, default=150, help="white mode: luminance above which near-edge pixels are removed")
    parser.add_argument("--print-width-in", type=float, help="Physical print width in inches (defaults to the full provider area)")
    parser.add_argument("--lum-floor", type=float, default=95.0)
    parser.add_argument("--lum-div", type=float, default=80.0)
    parser.add_argument("--cyan-floor", type=float, default=30.0)
    parser.add_argument("--cyan-div", type=float, default=55.0)
    parser.add_argument("--alpha-floor", type=float, default=0.12)
    parser.add_argument("--gamma", type=float, default=0.9)
    parser.add_argument("--median", type=int, default=3)
    parser.add_argument("--feather", type=float, default=0.5)
    parser.add_argument("--invert", action="store_true", help="For lineart mode: dark ink on light ground")
    parser.add_argument("--brightness", type=float, default=1.0)
    parser.add_argument("--saturation", type=float, default=1.0)
    parser.add_argument("--bloom", type=float, default=0.0)
    parser.add_argument("--sharpen", type=float, default=0.0, help="Unsharp-mask percent after scaling (restores edge definition)")
    parser.add_argument("--preview-dir")
    parser.add_argument("--report-json")
    parser.add_argument("--min-coverage", type=float, default=DEFAULT_GATES["min_coverage"])
    parser.add_argument("--max-coverage", type=float, default=DEFAULT_GATES["max_coverage"])
    parser.add_argument("--max-upscale", type=float, default=DEFAULT_GATES["max_upscale"])
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = run(args)
    except PrepError as error:
        print(f"REFUSED {error.code}: {error.message}", file=sys.stderr)
        print(f"  how_to_fix: {error.how_to_fix}", file=sys.stderr)
        return 2
    print(json.dumps({key: report[key] for key in ("ok", "mode", "canvas_px", "dpi", "coverage", "upscale_factor", "warnings")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
