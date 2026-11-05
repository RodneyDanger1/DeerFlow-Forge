"""Product routing table.

This file is the ONLY place that knows the Craft CLI command lines. Everything is data, so when a
Craft app changes a flag you edit one tuple here and nothing else.

Placeholders available inside argv/outputs templates (str.format syntax):
    {src}  copy of the raw input inside the run sandbox      {art}   current artwork (traced SVG, or the
    {work} per-run scratch dir                                        raster fallback PNG if tracing failed)
    {build} per-run output dir                               {fallback_dpi}  raster fallback DPI
    {run_id} {asset_id}                                      {cfg[key]}  per-category value from products.json

Items marked ASSUMPTION are not in the original spec and must be confirmed against the real CLIs.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .config import ConfigError

PRODUCT_TYPES = ("apparel", "knitwear", "accessories", "odd_3d", "stationery")

# Defaults merged under <root>/config/products.json[<product_type>]
DEFAULT_CFG: dict[str, dict[str, Any]] = {
    "apparel": {
        "regions": ["front"],
        "max_px": [4200, 4800],            # 14x16 in @ 300 dpi
        "trim_width_px": 4200,
        "trim_height_px": 4800,
    },
    "knitwear": {
        "regions": ["front"],
        "palette_limit": 6,                 # factory yarn colors: hard maximum
        "trace_colors": 6,                  # trace palette must not exceed the factory cap
        "knit_grid": "",                    # REQUIRED: factory 'COLSxROWS'; deliberately no default
    },
    "accessories": {
        "regions": ["front"],
        "template": "fourthwall_crossbody_v1",
        "care_text": "100% Polyester",
    },
    "odd_3d": {
        "regions": ["front"],
        "bleed_in": "0.25",
    },
    "stationery": {
        "regions": ["front"],
        "cover_template": "notebook_cover_template",
        "reel_template": "reel_promo_9_16",
        "reel_preset": "tiktok_1080p",
    },
}


# Trace settings shared by every product route. Values come from the exercised
# craft_trace.py defaults; per-product overrides may replace them.
TRACE_DEFAULTS: dict[str, Any] = {
    "trace_mode": "color",
    "trace_palette": "limited",
    "trace_colors": 12,
    "trace_paths": 65,
    "trace_corners": 45,
    "trace_noise": 16,
}

TRACE_PARAMS = (
    '{{"params":{{"mode":"{cfg[trace_mode]}","palette":"{cfg[trace_palette]}",'
    '"colors":{cfg[trace_colors]},"paths":{cfg[trace_paths]},"corners":{cfg[trace_corners]},'
    '"noise":{cfg[trace_noise]},"ignoreWhite":true,"method":"abutting","fills":true,'
    '"strokes":false,"shapes":false,"autoGrouping":false,"gradients":false}}}}'
)


@dataclass(frozen=True)
class Step:
    name: str
    module: str                                  # vectorcraft | photocraft | designcraft | effectcraft | filmcraft
    argv: tuple[str, ...]
    outputs: tuple[str, ...]                     # templates; may contain a glob '*'
    validators: tuple[tuple[str, str], ...] = ()  # (validator_name, output_template)
    timeout_s: int | None = None


@dataclass(frozen=True)
class Route:
    product_type: str
    steps: tuple[Step, ...]
    final: str                                   # template: the artifact this category produces
    upload: str | None                           # template: file sent to Fourthwall media library (None = skip)
    notes: str = ""


# --------------------------------------------------------------------------- stage 0 (shared)
def trace_step(route: Route) -> Step:
    """VectorCraft image trace, measured against vectorcraft-cli 0.21.1."""
    return Step(
        name="vector_trace",
        module="vectorcraft",
        argv=("vectorcraft-cli", "run", "--in", "{src}",
              "--cmd", "select.all",
              "--cmd", "imageTrace.make", "--params", TRACE_PARAMS,
              "--cmd", "imageTrace.expand",
              "--export", "{work}/traced.svg",
              "--export", "{work}/traced.pdf"),
        outputs=("{work}/traced.svg", "{work}/traced.pdf"),
    )


def raster_fallback_step() -> Step:
    """Tier-1 fallback when the vector trace exits 1: PhotoCraft resample, no tracing.
    Contract measured against photocraft-cli 0.20.2."""
    return Step(
        name="raster_fallback",
        module="photocraft",
        argv=("photocraft-cli", "run", "{src}",
              "--cmd", "image.imageSize",
              "--params", '{{"resolution":{fallback_dpi},"resample":"lanczos"}}',
              "--cmd", "edit.convertToProfile", "--params", '{{"profile":"srgb"}}',
              "--out", "{work}/raster.png"),
        outputs=("{work}/raster.png",),
    )


# ------------------------------------------------------------------------------------- routes
def _routes() -> dict[str, Route]:
    apparel = Route(
        product_type="apparel",
        steps=(
            Step("photocraft_trim", "photocraft",
                 # Measured against photocraft-cli 0.20.2: run FILE --cmd ... --out.
                 ("photocraft-cli", "run", "{art}",
                  "--cmd", "image.trim", "--params", '{{"basedOn":"transparent"}}',
                  "--cmd", "image.imageSize",
                  "--params", '{{"width":{cfg[trim_width_px]},"height":{cfg[trim_height_px]},'
                              '"resolution":300,"resample":"lanczos"}}',
                  "--cmd", "edit.convertToProfile", "--params", '{{"profile":"srgb"}}',
                  "--out", "{work}/trimmed.png"),
                 ("{work}/trimmed.png",)),
            Step("effectcraft_distress", "effectcraft",
                 ("effectcraft-cli", "--input", "{work}/trimmed.png",
                  "--filter", "vintage_screen_300", "--output", "{build}/apparel_final.png"),
                 ("{build}/apparel_final.png",),
                 validators=(("png_with_alpha", "{build}/apparel_final.png"),)),
        ),
        final="{build}/apparel_final.png",
        upload="{build}/apparel_final.png",
    )
    knitwear = Route(
        product_type="knitwear",
        steps=(
            Step("designcraft_stitch_matrix", "designcraft",
                 # ASSUMPTION: '--input {art}' added; the spec's reference line has no input argument.
                 ("designcraft-cli", "--mode", "stitch_matrix", "--input", "{art}",
                  "--palette-limit", "{cfg[palette_limit]}", "--grid-scale", "{cfg[knit_grid]}",
                  "--output", "{build}/knitwear_final.bmp"),
                 ("{build}/knitwear_final.bmp",),
                 validators=(("knit_bmp", "{build}/knitwear_final.bmp"),)),
        ),
        final="{build}/knitwear_final.bmp",
        upload="{build}/knitwear_final.bmp",
        notes="Fourthwall's media API is an image library; a BMP stitch grid may be refused -> needs_manual_upload.",
    )
    accessories = Route(
        product_type="accessories",
        steps=(
            Step("designcraft_template", "designcraft",
                 ("designcraft-cli", "--template", "{cfg[template]}", "--layer", "artwork", "--embed", "{art}",
                  "--layer", "care_label", "--text", "{cfg[care_text]}",
                  "--output", "{build}/accessory_final.pdf"),
                 ("{build}/accessory_final.pdf",),
                 validators=(("pdf", "{build}/accessory_final.pdf"),)),
        ),
        final="{build}/accessory_final.pdf",
        upload="{build}/accessory_final.pdf",
        notes="Safe-zone bbox checks and tracking/kerning auto-adjust must live inside DesignCraft.",
    )
    odd_3d = Route(
        product_type="odd_3d",
        steps=(
            Step("designcraft_wrap_tile", "designcraft",
                 ("designcraft-cli", "--mode", "wrap_tile", "--bleed", "{cfg[bleed_in]}", "--input", "{art}",
                  "--output", "{work}/odd/tiled.pdf"),
                 ("{work}/odd/tiled.pdf",),
                 validators=(("pdf", "{work}/odd/tiled.pdf"),)),
            Step("effectcraft_cylinder_taper", "effectcraft",
                 ("effectcraft-cli", "--cylinder-taper", "--input", "{work}/odd/tiled.pdf",
                  "--output", "{build}/odd_final.pdf"),
                 ("{build}/odd_final.pdf",),
                 validators=(("pdf", "{build}/odd_final.pdf"),)),
        ),
        final="{build}/odd_final.pdf",
        upload="{build}/odd_final.pdf",
    )
    stationery = Route(
        product_type="stationery",
        steps=(
            Step("designcraft_cover", "designcraft",
                 # ASSUMPTION: '--embed {art}' added so artwork reaches the template; '--variable-data order_id'
                 # is dropped here because a cover is built before any order exists.
                 ("designcraft-cli", "--input", "{cfg[cover_template]}", "--embed", "{art}",
                  "--output", "{build}/print_ready_stationery.pdf"),
                 ("{build}/print_ready_stationery.pdf",),
                 validators=(("pdf", "{build}/print_ready_stationery.pdf"),)),
            Step("filmcraft_reel", "filmcraft",
                 ("filmcraft-cli", "--template", "{cfg[reel_template]}", "--asset-layer", "product_front",
                  "--input", "{build}/print_ready_stationery.pdf", "--render-preset", "{cfg[reel_preset]}",
                  "--output", "{build}/promo_reel.mp4"),
                 ("{build}/promo_reel.mp4",),
                 validators=(("mp4", "{build}/promo_reel.mp4"),),
                 timeout_s=1800),
        ),
        final="{build}/print_ready_stationery.pdf",
        upload="{build}/print_ready_stationery.pdf",
        notes="promo_reel.mp4 is a marketing asset, not a Fourthwall upload. Packing slips are NOT built here.",
    )
    return {r.product_type: r for r in (apparel, knitwear, accessories, odd_3d, stationery)}


ROUTES: dict[str, Route] = _routes()


def merged_cfg(product_type: str, overrides: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if product_type not in ROUTES:
        raise ConfigError(f"unknown product_type {product_type!r}; expected one of {', '.join(PRODUCT_TYPES)}")
    merged = {**TRACE_DEFAULTS, **DEFAULT_CFG.get(product_type, {}), **overrides.get(product_type, {})}
    # The factory's palette cap is the trace colour cap for knitwear unless the
    # operator explicitly overrides trace_colors.
    if product_type == "knitwear" and "trace_colors" not in overrides.get(product_type, {}):
        merged["trace_colors"] = int(merged.get("palette_limit", TRACE_DEFAULTS["trace_colors"]))
    return merged


def render(template: str, variables: dict[str, Any], *, where: str) -> str:
    try:
        return template.format_map(variables)
    except (KeyError, IndexError) as exc:
        raise ConfigError(f"{where}: placeholder {exc} is not defined (check products.json)") from exc


def render_argv(step: Step, variables: dict[str, Any]) -> list[str]:
    out = [render(tok, variables, where=f"step {step.name}") for tok in step.argv]
    for tok in out:
        if tok == "":
            raise ConfigError(f"step {step.name}: an argument rendered empty; a required products.json value is missing")
    return out
