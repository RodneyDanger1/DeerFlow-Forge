---
name: print-mockup-composite
description: "Compose a finished print master or design onto a garment/product canvas or a flat mockup for review: exact canvas sizes, integer centring math, alpha-safe image placement, black and white previews, and a placement report. Use when the user says make a mockup, put this design on a shirt, show it on the product, check the placement or cut-off, centre this on the garment, or produce black/white previews of a print master. A mockup proves placement and cut-off only — never print size or colour."
version: 1.0.0
author: DeerFlow Forge
license: original
platforms: [linux, windows]
metadata:
  hermes:
    tags: [mockup, composite, placement, centring, print, dtg, imagemagick, pillow, vectorcraft]
    related_skills: [apparel-print-master, ai-image-upscale-print, artcraft-vector-trace, ad-creative]
---

# Print mockup composite

A mockup is a **placement and cut-off check**, not print proof. Compose the design at exact pixels on an exact canvas, centre it with recorded integers, produce black and white previews, and say plainly that scale, colour and ink still need a physical sample.

## When to use

- A finished design/master needs a placement or cut-off review, or black/white previews plus a JSON record.
- A flat review image is needed for a listing, deck or owner approval (not as print proof).

## When not to use

- Proving print size, colour, ink coverage or texture — order a sample. No perspective/garment-warp or
  CMYK/press proofing here; flat RGB composites only. Creating the master itself — `apparel-print-master`.

## Inputs

- Design/master PNG with alpha, its pixel size, the print width in inches, and the canvas choice: provider
  geometry (`front_large` 15×18 in → 4500×5400 px at 300 DPI) or a flat review canvas (2000×2000 px exact).
- Garment/product background colour or photo; intended DPI (300); preview colours (`#141313`, `#ffffff`).

## Command pipeline

```bash
cd /opt/pod-pipeline; PY=.venv/bin/python; VC=/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli
```

**Step 0 — pick the canvas and the centring math.** Proof canvas = `round(area_inches × dpi)` from `config/fourthwall-template-details.json`; review canvas = an exact downscale of the proof, never a re-layout. Centre with `x = (W - w) // 2`, `y = (H - h) // 2`; an odd remainder goes left/top, so record the actual margins rather than claiming perfect symmetry.

**Step 1 — PIL composite** (verified 2026-11-05; 1000×800 on 2000×2000 → offsets `[500, 600]`). Save as
`/tmp/mockup_composite.py`; args: base, design, out-prefix, canvas width, canvas height, optional DPI.

```python
import json, sys
from PIL import Image
base_path, design_path, out_prefix = sys.argv[1:4]
W, H = int(sys.argv[4]), int(sys.argv[5]); dpi = int(sys.argv[6]) if len(sys.argv) > 6 else 300
base = Image.open(base_path).convert("RGBA")
if base.size != (W, H): raise SystemExit(f"REFUSED base {base.size} != canvas {(W, H)}")
design = Image.open(design_path).convert("RGBA"); w, h = design.size
if w > W or h > H: raise SystemExit(f"REFUSED design {w}x{h} exceeds canvas {W}x{H}")
x, y = (W - w) // 2, (H - h) // 2
canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0)); canvas.alpha_composite(base); canvas.alpha_composite(design, (x, y))
for name, colour in (("black", (20, 19, 19, 255)), ("white", (255, 255, 255, 255))):
    flat = Image.new("RGBA", canvas.size, colour); flat.alpha_composite(canvas)
    flat.convert("RGB").save(f"{out_prefix}_{name}.png", dpi=(dpi, dpi))
report = {"canvas_px": [W, H], "design_px": [w, h], "offset_px": [x, y],
          "margins": [x, W - w - x, y, H - h - y], "canvas_in": [round(W / dpi, 2), round(H / dpi, 2)],
          "design_print_in": [round(w / dpi, 2), round(h / dpi, 2)],
          "previews": [f"{out_prefix}_black.png", f"{out_prefix}_white.png"]}
json.dump(report, open(f"{out_prefix}.json", "w"), indent=2); print(json.dumps(report, indent=2))
```

```bash
$PY /tmp/mockup_composite.py /tmp/garment_canvas.png /tmp/art_8in.png /tmp/mock_8in 4500 5400 300
```

**Step 2 — ImageMagick one-liner** (verified: 2000×2000 output; design spanned x=500–1499; pixel 1500 was
background). `-gravity center -composite` centres the overlay; `-density` only writes metadata.

```bash
magick /tmp/mock_base.png /tmp/mock_design.png -gravity center -composite \
  -units PixelsPerInch -density 300 /tmp/mock_out.png
identify -format '%f %wx%h %x %y\n' /tmp/mock_out.png
magick /tmp/mock_out.png -format '%[pixel:p{500,1000}] %[pixel:p{1500,1000}]\n' info:
```

**Step 3 — VectorCraft composite** (verified 2026-11-05). `file.new` numeric `width`/`height` are **points**;
use inch strings. `file.place` `at` is the **centre** and `rect` is `[x, y, w, h]` in **points**; a raster
comes in at 100 % of its physical size (its ppi, else 72). `document.export` `ppi` computes
`px = pt ÷ 72 × ppi`.

```bash
$VC run --cmd file.new --params '{"width":"15 in","height":"18 in","units":"Inches","rasterEffectsPpi":300}' \
  --cmd file.place --params '{"path":"/tmp/art_8in_300ppi.png"}' \
  --cmd document.export --params '{"path":"/tmp/mock_vc.png","format":"png","ppi":300,"includeArtboardFill":false}'
identify -format '%f %wx%h %x %y\n' /tmp/mock_vc.png
```

**Step 4 — verify and label.** `identify` the proof and both previews; check `canvas_px`, `margins`, and
`design_print_in` equals the intended print width (8 in). Store the JSON beside the previews and label the
deliverable "placement/cut-off only".

## Workflow

1. Decide proof canvas (provider geometry) vs review canvas (exact downscale); never invent geometry.
2. Render or pre-resize the design to the print width in pixels (2400 px for 8 in at 300 DPI).
3. Composite centred; if the design is larger than the canvas, stop — that is a cut-off failure, not a crop.
4. Save black (`#141313`) and white (`#ffffff`) previews plus the JSON placement report.
5. Downscale the proof to the review size with LANCZOS; do not re-centre during the downscale.
6. Inspect both previews at 100 % and thumbnail; hand off with the "not print proof" label.

## Acceptance gates

- Canvas equals provider geometry exactly (front_large 4500×5400) or the stated review size (2000×2000).
- `design_px` ≤ canvas; every margin ≥ 0; left/right and top/bottom differ by ≤ 1 px.
- `design_print_in` equals the intended print width (8 in for a 2400 px design at 300 DPI).
- Master stays RGBA before flattening; no white box or coloured matte behind the art.
- `identify` shows the exact pixel size and 118.11 px/cm (300 DPI) on the proof.
- Both previews exist and the design is visible on each; no cut-off at the garment/area boundary.
- Report JSON stored; the deliverable is labelled placement/cut-off proof only.

## Refusals

- Never present a mockup as print-size, colour or ink-coverage proof. Only a physical sample proves those.
- No perspective, fabric-fold or garment-warp simulation exists here; do not claim one.
- Do not use a mockup to "rescue" a failed print gate — a failed master stays failed.
- No browser automation and no store change; a mockup is a local review file. Do not claim CMYK or press proofing.

## Worked example

`front_large` is 15×18 in → 4500×5400 px at 300 DPI. Render the art at 8 in = 2400 px; centre:
`x = (4500 − 2400) // 2 = 1050`, `y = (5400 − 2400) // 2 = 1500`. The report shows margins
`[1050, 1050, 1500, 1500]` and `design_print_in [8.0, 8.0]`; both black and white previews are written.

- PIL test: 1000×800 on 2000×2000 → `offset_px [500, 600]`, margins `[500, 500, 600, 600]`, canvas 6.67 in, design 3.33×2.67 in; ImageMagick pixel probes: x=500 and x=999 red, x=1500 background.
- VectorCraft test: 8×8 in artboard = 576 pt; a 1024 px @300 ppi image placed at 245.76 pt (1024 px at 300
  ppi) at `(165.12, 165.12)`; the same file at 72 ppi placed at 1024 pt `(−224, −224)` and clipped. A numeric
  `{"width":8}` artboard exported 33×33 px at 300 ppi — numeric width is points, not inches.

## Pitfalls

- **`file.place` keeps physical size, not pixel count.** A 1024 px PNG with no ppi metadata lands 1024 pt wide
  (14.2 in) and clips; tag it 300 ppi or pass a `rect` in points (`px × 72/300`) and pre-resize.
- **`at` is the centre, not top-left.** `rect` is `[x, y, width, height]` in points and fits inside with the
  aspect kept; it wins over `at`.
- **Numeric `file.new` width is points.** `{"width":8}` is 8 pt (33 px at 300 ppi); use `"8 in"`.
- **ImageMagick defaults to 72 ppi** and `-density` only tags metadata; it never resamples.
- **Odd sizes break perfect symmetry.** One pixel goes right/bottom (floor division); record it instead of hiding it.
- **A black background hides dark halos; a white one hides white fringes.** Review both.

## Sources & verification

- **VERIFIED (executed 2026-11-05):** PIL composite (offsets/margins/previews above); ImageMagick
  `-gravity center -composite` on 2000×2000 with pixel probes; VectorCraft `file.new` + `file.place` +
  `document.export ppi:300` → 4500×5400 at 118.11 px/cm in the 15×18 test (2400×2400 in the 8×8 test); 72 ppi place clipped at `(−224, −224)`; numeric `{"width":8}` → 33×33 px.
- **SCHEMA:** VectorCraft 0.21.1 catalogue (918 commands): `file.new` `{width pt|"8 in", height, units,
  rasterEffectsPpi, ...}`; `file.place` `{path|name|dataBase64, at?: [x,y] centre, rect?: [x,y,w,h] fit
  inside, link?, page?, crop?, ...}` → `{ids, name, format, linked, width, height, warnings}`; "raster images
  come in at 100 % of their physical size (the file's ppi, else 72)"; `document.export` `{path, format, ppi,
  scale, artboard, background, ...}`, `ppi` wins over `scale`, `px = pt ÷ 72 × ppi`.
- **SOURCE:** `tools/craft_trace.py:186-189` (`compose_canvas` centres with `(canvas − art) // 2`);
  `tools/prep_print_art.py:329-330` and `tools/artcraft.py:328-330` (same centring on provider canvas).
- **DOCS:** provider geometry `config/fourthwall-template-details.json` (623 rows; `front_large` 15×18 in,
  2250×2700 @150); vault `02-VECTORIZATION-AND-QUALITY.md` line 66 ("Mockup is a cut-off check, not a
  print-size proof") and `15-APPAREL-PRINT-MARKETING-WORKFLOWS.md` §A/§I.
