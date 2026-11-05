---
name: ai-image-upscale-print
description: "Decide and execute the print-resolution step for AI/raster art: 150 vs 300 DPI pixel math, the 2.5x upscale gate, when upscaling is acceptable versus when the source must be regenerated, Lanczos resampling, UnsharpMask at final size, composition on exact provider geometry, and pixel-math verification with a JSON report. Use when the user says upscale this for print, is this big enough to print, what DPI do I need, make this 300 DPI, fix the resolution, enlarge this art to 8 inches, or check whether this file will print sharp."
version: 1.0.0
author: DeerFlow Forge
license: original
platforms: [linux, windows]
metadata:
  hermes:
    tags: [print, resolution, dpi, upscale, sharpening, dtg, canvas-geometry]
    related_skills: [ai-diffusion-artifact-cleanup, apparel-print-master, artcraft-image-cleanup, artcraft-vector-trace]
---

# AI image upscale for print

Pixels = print inches × DPI, measured on the **subject**, not the file canvas. Upscale at most 2.5×, only when the art tolerates it; sharpen once at final size; compose on the provider's exact geometry.

## When to use

- A raster/AI image must print at a physical width, or someone asks "is this 300 DPI?", "will this print sharp at 8 in?", or "upscale this for the printer".

## When not to use

- Flat art that should be vector — `artcraft-vector-trace`; cleanup first — `ai-diffusion-artifact-cleanup`; web/social output where physical inches do not exist — use the pixel box directly.

## Inputs

- Source with rights and true pixel size (`identify`), not just its DPI tag; print width in inches (tee 8, hoodie 8.5); target DPI (300 house; 150 provider floor).
- Provider `productTemplateId`/area or explicit canvas pixels; whether the art is soft/painterly or linework.

## Command pipeline

Run from `/opt/pod-pipeline`; `PY=.venv/bin/python`;
`PC=/opt/craft/photocraft/photocraft-0.20.2-linux-x86_64/bin/photocraft-cli`.

**Step 0 — pixel math, before any resample.** Save as `/tmp/print_px.py`; the optional 4th argument is the subject width from the `prep_print_art` report (`subject_px[0]`), else the full width.

```python
import json, sys
from PIL import Image
src, print_in, dpi = sys.argv[1], float(sys.argv[2]), int(sys.argv[3])
im = Image.open(src); w, h = im.size; subject = int(sys.argv[4]) if len(sys.argv) > 4 else w
need = round(print_in * dpi); up = need / subject
print(json.dumps({"source_px": [w, h], "subject_px": subject, "print_in": print_in, "dpi": dpi,
  "required_px": need, "upscale": round(up, 3), "subject_px_per_in": round(subject / print_in, 1),
  "verdict": "ok" if up <= 2.5 and subject / print_in >= 150 else "regenerate"}, indent=2))
raise SystemExit(0 if up <= 2.5 and subject / print_in >= 150 else 1)
```

```bash
$PY /tmp/print_px.py /tmp/art.png 8 300 1024
```

**Step 1 — raster master with the gate report.** `--margin-px 0` is required for exact print-width math; the default 100 px margin shrinks `usable_width_px`. `upscale_factor` is `usable_width_px / subject_bbox width`; `--max-upscale` only writes a warning — it does not fail the run.
```bash
$PY -m tools.prep_print_art --input /tmp/art.png \
  --template pro_e4677535402b4eeb81 --area front_large --dpi 300 --margin-px 0 \
  --mode white --clean-rim --min-component 60 --print-width-in 8 \
  --saturation 1.18 --brightness 1.04 --sharpen 55 \
  --output /tmp/art_8in.png --report-json /tmp/art_8in.json --preview-dir /tmp/prev_8in
$PY -c "import json; d=json.load(open('/tmp/art_8in.json')); print(d['canvas_px'], d['upscale_factor'], d['subject_px'], d['print_width_in'], d['warnings'], d['ok'])"
identify -format '%f %wx%h %x %y\n' /tmp/art_8in.png
```

**Step 2 — explicit PhotoCraft resample** (verified 2026-11-05). Lanczos resize, then tag 300 ppi without a
second resample. `keepPrintSize:true` with only a resolution **does** resample (1024 → 4267 measured). The
file argument is positional; `--in` is a VectorCraft flag.

```bash
$PC run /tmp/art.png \
  --cmd image.imageSize --params '{"width":2400,"height":2400,"resample":"lanczos"}' \
  --cmd image.imageSize --params '{"resolution":300,"resample":"none"}' \
  --cmd filter.sharpen.unsharpMask --params '{"amount":110,"radius":1.0,"threshold":3}' \
  --out /tmp/art_8in_pc.png
identify -format '%f %wx%h %x %y\n' /tmp/art_8in_pc.png
```

**Step 3 — verify the delivered pixels and metadata.** Save as `/tmp/verify_print_px.py`; exits 1 on failure. `%x`/`%y` from `identify` are px/cm: 118.11 = 300 DPI, 59.06 = 150 DPI.

```python
import json, sys
from PIL import Image
path, print_in, dpi = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]); src = int(sys.argv[4]) if len(sys.argv) > 4 else None
im = Image.open(path); w, h = im.size; meta = im.info.get("dpi")
rep = {"px": [w, h], "dpi_meta": list(meta) if meta else None, "print_in": print_in, "target_dpi": dpi,
       "achieved_px_per_in": round(w / print_in, 2), "required_px": round(print_in * dpi),
       "upscale_from_source": round((print_in * dpi) / src, 3) if src else None}
rep["ok"] = (abs(w / print_in - dpi) < 1.5 and (meta is None or abs(float(meta[0]) - dpi) < 1.5)
             and w >= round(print_in * dpi) - 1 and (src is None or rep["upscale_from_source"] <= 2.5))
print(json.dumps(rep, indent=2)); raise SystemExit(0 if rep["ok"] else 1)
```

```bash
$PY /tmp/verify_print_px.py /tmp/art_8in.png 8 300 1024
```

## Workflow

1. Read true pixels with `identify`; ignore a DPI tag that does not match. Compute `need = print_in × dpi`
   and decide with `need / subject_px` and `subject_px / print_in`.
2. ≤2.5× and ≥150 px/in and soft art → upscale; otherwise regenerate or vectorise flat art.
3. Resize once with Lanczos, tag the DPI, unsharp at final size — never before the resize. Compose on
   provider geometry, run the verify script, keep the JSON, inspect at 100 % and thumbnail.

## Acceptance gates

- `required_px` equals `print_in × dpi`; source `subject_px / print_in` ≥ 150 px/in.
- `upscale_factor` (report) and `upscale` (script) ≤ 2.5; above it, no ship — regenerate.
- `prep_print_art` report `ok: true`, `warnings: []`; `identify` shows 118.11 px/cm for 300 DPI (59.06 for 150).
- Canvas equals `round(area_inches × 300)` from `areaGeometry` (front_large 15×18 in → 4500×5400); sharpening
  visible at 100 % without halos/crunch; text clean; `verify_print_px.py` exits 0.

## Refusals

- No AI upscaler, super-resolution or "enhance" engine exists here; only interpolation happens. Never claim
  recovered detail.
- >2.5× → regenerate; line art, lettering and hard-edged logos → regenerate well before 2.5×. Interpolation
  softens exactly the edges that matter; do not resize an already-sharpened file, or sharpen twice.
- <150 px per print inch → regenerate; do not stretch a thumbnail onto a garment. Provider uploads are
  PNG/JPG only; SVG/AI/PDF/PSD/TIFF are working masters, never the upload.

## Worked example

1024 px source, 8 in print, 300 DPI — needs `8 × 300 = 2400 px`; `2400 / 1024 = 2.344×`. It passes the
2.5 gate but supplies only `1024 / 8 = 128` source px/in, below the 150 floor: regenerate or vectorise. A
1200 px source is the smallest that passes both (`150 px/in`; `2400 / 1200 = 2.0×`).

- Measured on the 1024² synthetic test: `prep_print_art` reported `upscale_factor 5.568` for 8 in because the **subject bbox** was 431 px wide (2400/431), not the 1024 canvas. The report was `ok: true` with a non-empty `warnings` list and exit 0 — the 2.5 gate is a warning, not a failure. Treat it as a refusal.
- PhotoCraft Lanczos 1024→2400 produced 2400×2400 at 28.35 px/cm; `resolution:300, resample:"none"` re-tagged 118.11 px/cm; unsharp `100/1.2/2` raised Laplacian variance `0.00024 → 0.00056`; `verify_print_px.py` returned `upscale_from_source 2.344`, `ok: true`, exit 0.

## Pitfalls

- **DPI metadata is not pixels.** `image.imageSize` with only `resolution` + `keepPrintSize:true` resamples
  (1024 → 4267 measured); use `resample:"none"` to tag only.
- **The 2.5 gate is soft in code.** `prep_print_art` always writes `ok: true`; `upscale_factor` and
  `warnings` are the real evidence. `craft_trace` has no upscale gate (it is vector).
- **Default margin 100 px:** `usable = min(canvas_w - 200, print_width_in × dpi)`; pass `--margin-px 0`.
  The gate also measures the subject bbox, not the canvas, so a small subject inflates the ratio (5.568).
- **150 vs 300:** provider geometry is authored at 150 DPI (front_large 2250×2700); the 300 DPI master
  (4500×5400) is 2× headroom, not a provider requirement.
- **PhotoCraft is positional** (`run FILE`); `--in` is a VectorCraft flag. `bicubicSharper` bakes sharpening
  into the resize, which then double-sharpens.

## Sources & verification

- **VERIFIED (executed 2026-11-05):** `tools.prep_print_art` report (`/tmp/up8.json`: `upscale_factor 5.568`,
  `warnings` non-empty, `ok: true`, exit 0); PhotoCraft 1024→2400 Lanczos + `resolution:300, resample:"none"`
  → 2400×2400 at 118.11 px/cm; `keepPrintSize:true` → 4267×4267; unsharp `0.00024 → 0.00056` at 2400; `verify_print_px.py` exit 0 with `upscale 2.344`.
- **SCHEMA / SOURCE:** `image.imageSize` `{width, height, units px|pt, percent, resolution ppi, keepPrintSize,
  resample automatic|preserveDetails|bicubicSmoother|bicubicSharper|bicubicAutomatic|bicubic|nearest|bilinear|
  lanczos|none}` and `filter.sharpen.unsharpMask` `{amount 1–500=50, radius 0.1–1000=1, threshold 0–255=0}`
  from the PhotoCraft 0.20.2 registry; `tools/prep_print_art.py:323-343` (`usable`, margin, LANCZOS resize,
  `upscale`, warning, post-scale unsharp), `:355-379` (report fields); `config/fourthwall-template-details.json`
  (623 rows; `front_large` 15×18 in, 2250×2700 @150).
- **DOCS:** vault `02-VECTORIZATION-AND-QUALITY.md` (DPI math, 2.5× rule, 150 px/in floor), `09-WORKFLOWS.md`
  §C, `15-APPAREL-PRINT-MARKETING-WORKFLOWS.md` §A; Pillow 13.0.0 `ImageFilter.UnsharpMask` —
  https://pillow.readthedocs.io/en/stable/reference/ImageFilter.html . Adobe Photoshop "Change print dimensions and resolution" was fetched 2026-11-05 (HTTP 200) but returned only the navigation shell.
