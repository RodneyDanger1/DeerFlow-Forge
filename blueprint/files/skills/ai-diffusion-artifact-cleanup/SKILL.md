---
name: ai-diffusion-artifact-cleanup
description: "Use when an AI-diffusion render looks dirty at print size: soft/haloed edges, grey rim, speckle, semi-transparent fringe or JPEG blocking. Measures defects, applies the strict white cutout, restores colour/saturation and sharpens at final size before tracing or print. Triggers: diffusion artefacts, AI image cleanup, halo, grey rim, speckles, fringe, denoise AI, clean AI art, prepare AI image for print."
version: 1.1.0
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [ai, diffusion, cleanup, cutout, alpha, print, trace, prep]
    related_skills: [artcraft-image-cleanup, artcraft-vector-trace, ai-art-vectorize-vectorcraft, ai-image-upscale-print]
---

# AI diffusion artefact cleanup

Diffusion renders look clean at thumbnail size and dirty at print size: soft edges, halos,
speckle, a semi-transparent fringe, JPEG blocking. Measure → cut out white → restore → sharpen at
final size → trace or master. Do not trace before this pass.

## When to use / not use

- Use when a diffusion/AI render is about to be cut out, traced or printed.
- Use when the cutout shows a grey rim, light halo under lettering, speckle in flat fills or a
  fuzzy edge.
- Use when a JPEG-sourced AI image shows blocking that would survive a trace.
- Not for a photo/scan (`artcraft-image-cleanup`), vectorising (`artcraft-vector-trace`), or
  upscaling (`ai-image-upscale-print`). Melted letterforms/geometry are a generation defect:
  regenerate — no filter invents structure.

## Inputs

Source with rights (never overwrite), route (trace vs raster master), print width, target DPI
(300), provider geometry if apparel, brand hex list, and which glow is intentional vs a halo.

## Verified pipeline (2026-11-05)

```bash
cd /opt/pod-pipeline; PY=.venv/bin/python
PC=/opt/craft/photocraft/photocraft-0.20.2-linux-x86_64/bin/photocraft-cli
# Linux VPS only. From Windows: ssh -i ~/.ssh/id_ed25519_hostinger root@179.197.88.181 'cd /opt/pod-pipeline && bash -s' < script.sh
# Stop if SSH/key is unavailable: /opt/pod-pipeline and the CLIs do not exist on Windows.
```

**Step 0 — audit before touching pixels.** Save as `/tmp/artefact_audit.py`:

```python
import json, sys, numpy as np
from PIL import Image
from skimage import filters, measure
im = Image.open(sys.argv[1]).convert("RGBA"); a = np.asarray(im.getchannel("A")); o = a > 127
rgb = np.asarray(im.convert("RGB")).astype(np.int16); g = np.asarray(im.convert("L"), dtype=np.float32) / 255.0
hsv = np.asarray(im.convert("RGB").convert("HSV"), dtype=np.float32)
print(json.dumps({"hard_alpha_share": round(float(((a == 0) | (a == 255)).mean()), 4),
 "semi_transparent_share": round(float(((a > 0) & (a < 255)).mean()), 4),
 "white_residual_ratio": round(float((np.all(rgb >= 245, axis=-1) & o).sum()) / max(1, int(o.sum())), 5),
 "specks_under_150_px": sum(1 for r in measure.regionprops(measure.label(o)) if r.area < 150),
 "edge_sharpness_laplacian": round(float(filters.laplace(g).var()), 5),
 "mean_saturation_opaque": round(float(hsv[..., 1][o].mean()) / 255.0, 3)}))
```

**Step 1 — strict white cutout.** Every neutral white transparent (background, paper edge, snow,
sky); cream/tan survives. Use the source's actual W×H for `--width-px/--height-px` (do not force a
square on a rectangular source).

```bash
# 1024 below is a square example: set W/H from identify for a rectangular source.
# Mode routing: --mode alpha needs a real alpha channel (opaque JPEG refuses E_SUBJECT_FULL_FRAME);
# --mode white needs a white background; use --mode none deliberately for full-bleed art.
$PY -m tools.prep_print_art --input /tmp/art.png --output /tmp/art_cut.png \
  --width-px 1024 --height-px 1024 --dpi 300 --mode white --clean-rim \
  --min-component 60 --edge-clean-px 26 --edge-clean-lum 140 --margin-px 0 \
  --print-width-in 3.413333 --report-json /tmp/art_cut.json
```

**Step 2 — binarise alpha only when the next stage traces.** The 0.5 px feather becomes a key-colour
rim; `vectorize_art`/`craft_trace` re-binarise at 128. **Route now:** trace → feed `/tmp/art_hard.png`
to `artcraft-vector-trace`; raster → skip this step and use `/tmp/art_clean.png` from Step 4. Do not
silently mix `/tmp/art.png`, `/tmp/art_cut.png` and `/tmp/art_hard.png` between steps:

```bash
$PY -c "from PIL import Image; im=Image.open('/tmp/art_cut.png').convert('RGBA'); im.putalpha(im.getchannel('A').point(lambda v:255 if v>=128 else 0)); im.save('/tmp/art_hard.png')"
```

**Step 3 — colour restore + unsharp at final size** (`--sharpen` runs after scaling):

```bash
$PY -m tools.prep_print_art --input /tmp/art.png \
  --template pro_e4677535402b4eeb81 --area front_large --dpi 300 \
  --mode white --clean-rim --min-component 60 --edge-clean-px 26 --edge-clean-lum 140 \
  --print-width-in 8 --saturation 1.18 --brightness 1.04 --sharpen 55 \
  --output /tmp/art_master.png --report-json /tmp/art_master.json --preview-dir /tmp/prev_art
```

**Step 4 — JPEG noise/colour with PhotoCraft** (positional input; chain executed 2026-11-05):

```bash
$PC run /tmp/art.jpg \
  --cmd filter.noise.reduceNoise --params '{"strength":6,"preserveDetails":60,"reduceColorNoise":45,"sharpenDetails":25,"removeJpegArtifact":true}' \
  --cmd image.adjustments.levels --params '{"inBlack":6,"gamma":1.05,"inWhite":249}' \
  --cmd filter.sharpen.unsharpMask --params '{"amount":100,"radius":1.2,"threshold":3}' \
  --out /tmp/art_clean.png
```

**Step 5 — deblur/flatten research path in `tools/artcraft.py` (FIXED 2026-11-05).** The two original
defects (Lab L passed to `equalize_adapthist`; PIL Image passed to `flatten_on_key`) are fixed in the
repo and deployed. Verified smoke command:

```bash
$PY -m tools.artcraft --input /tmp/art.png --canvas-width 1500 --canvas-height 1500 --dpi 300 \
  --print-width-in 3.413333 --output /tmp/art_ac.png --svg /tmp/art_ac.svg \
  --report-json /tmp/art_ac.json --preview-dir /tmp/prev_ac
```

Observed on a synthetic badge (canvas 1500×1500, print width 3.413 in): report written,
`structure_ssim 0.9011`, `white_residual 0`, `magenta_residual 0`, `edge_specks 0`,
`coverage 0.1165` (passes 0.03–0.92 after the coverage metric was fixed to measure art pixels against
the canvas, not the art frame), `edge_sharpness_ratio 1.165`, `svg paths 9`; **`colour_histogram_corr`
0.345 fails the 0.65 gate** on two-colour synthetic art. So `ok:false` can be a legitimate quality
verdict, not a crash. Inspect the gate table; it is an experimental path, not a replacement for Steps 1–4.

## Workflow / gates

1. `identify` + audit; decide route/print width; under 150 px per print inch → stop, regenerate.
2. White cutout; audit again. A surviving grey rim means the key is wrong for this image.
3. Tracing: binarise alpha → `artcraft-vector-trace`; raster: saturation/brightness → unsharp at
   final size → compose on provider geometry.
4. Compare at 100 % on black and white; re-audit; store the report; keep the source.

Gate sets differ by tool — quote the right one:
- `prep_print_art`: coverage 0.005–0.62, `E_SUBJECT_EMPTY`, `E_SUBJECT_FULL_FRAME`, upscale warning
  above 2.5× (report `ok` stays true; the warning is the gate).
- `craft_trace`: 10 gates, `ok:true` only when all pass (white residual, specks 0, art-frame coverage
  0.05–0.95, DPI ≥300, canvas ≥1500², 2–40 fill colours, edge density ≥0.01, hard alpha ≥0.85,
  transparent corners, retyped text present).
- `artcraft`: 10 checks, coverage 0.03–0.92; full-bleed art legitimately fails coverage.

Additional gates (measure alpha/white on the **cutout**, not the opaque source — a JPEG's alpha is
255 everywhere, so `hard_alpha_share` 1.0 means nothing): `white_residual_ratio` ≤0.002;
`specks_under_150_px` = 0; `hard_alpha_share` ≥0.85; raster master 300 DPI, `upscale_factor` ≤2.5;
edge sharpness after unsharp ≥1.0× the same-size pre-sharpen value (verified 1.06× prep, 2.34×
PhotoCraft chain). Visual: no grey halo, dark rim, speckle, lost thin stroke.

## Artefact → action routing

| Symptom | First move | Retry / stop |
|---|---|---|
| white/grey rim after cutout | re-run cutout with correct `--mode white`; audit alpha | still there → key wrong for image; hand-clean or regenerate |
| speckle in flat fills | `--min-component` higher; `--edge-clean-px` 26–40 | still → trace/grain source; regenerate |
| soft/fuzzy edge | `prep_print_art --sharpen` at final size; PhotoCraft unsharp | still → upscale decision/regenerate |
| lettering halo/shadow | erase bands + retype in `craft_trace` | never trace AI text |
| JPEG blocking | PhotoCraft reduceNoise with `removeJpegArtifact` | still → regenerate at higher quality |
| colour dull | saturation 1.15–1.25, brightness 1.03–1.06 | verify against brand hex |

## Agent operating protocol (follow every time)

**Preflight:** audit first; record alpha/white/speck/sharpness numbers; route decision (trace vs
raster) stated; source preserved.

**Execution loop:** one stage, re-audit, compare 100 % on black/white; stop if the metric worsens.

**Evidence:** before/after audit JSON, command output, previews, gate table; no page screenshots.

**Stop/escalate:** no verified filter fixes the defect; melted geometry; full-bleed art that fails the
chosen gate set; >2.5× upscale needed; route/print width/brand colours missing → ask.

**Never:** claim `tools.artcraft` is production; use `white-flood` by default; raise `edge-clean-lum`
until cream lettering disappears; call a non-crash failure a success.

## Refusals / failure modes

- `tools.artcraft` now runs but is experimental; do not present a full-bleed failure as success and
  do not prefer it over `prep_print_art`/PhotoCraft for production.
- No AI upscaler/super-resolution exists; regenerate melted letterforms.
- Do not use `--mode white-flood` by default: it keeps enclosed whites (snow, white lettering),
  violating the owner's every-white-transparent rule unless explicitly requested.
- Do not set `--edge-clean-lum` so high that cream lettering near the silhouette is removed.
- No browser automation; proof is a rendered PNG + JSON audit, not a page screenshot.
- JPEG 4:2:0 blocking cannot be fully removed; regenerate at higher quality if it survives.

## Pitfalls

- **Upscale is measured on the subject bbox, not the source canvas.** A 1024² source whose art is
  only 431 px wide reports `upscale_factor 5.568` for an 8 in print, not 2.34 — trim/regenerate.
- **`--clean-rim` erodes one pixel.** Hairlines and one-pixel serifs can disappear; check at 100 %.
- **White removal is global.** Snow, eye whites and highlights go transparent by design; the halo
  often lives in alpha, so audit `semi_transparent_share`.
- **CLAHE needs 0–1 floats** (fixed in the tool); Lab L is 0–100.
- **PhotoCraft is positional:** `photocraft-cli run FILE …`; `--in` is a VectorCraft flag.
- **Lossy WebP can grow:** on flat art `convert --quality 82` produced 2,718 B vs 1,372 B lossless —
  compare and pick the smaller, not the "higher quality" blindly.

Photo command depth: **artcraft-command-atlas** (`pc-image-adjust.md`, `pc-filter-effect.md`); batch runs: **artcraft-batch-automation**. Use atlas `command_lookup.py`.

## Sources & verification

- **VERIFIED (2026-11-05):** audit numbers from a synthetic diffusion-like test; `prep_print_art`
  report (`upscale_factor 5.568`, warnings, exit 0); PhotoCraft chain
  reduceNoise→levels→unsharpMask; `artcraft` fixed and smoke-run (1500 canvas: coverage 0.1165 pass, colour-histogram 0.345 fails
  0.65 on two-tone synthetic); PhotoCraft `convert --quality` measurement.
- **SCHEMA/SOURCE:** PhotoCraft 0.20.2 registry; `tools/prep_print_art.py`;
  `tools/artcraft.py`; `tools/craft_trace.py` gate list.
- **DOCS:** vault 02/15; scikit-image `exposure.equalize_adapthist`
  https://scikit-image.org/docs/stable/api/skimage.exposure.html ;
  Pillow `ImageFilter.UnsharpMask` https://pillow.readthedocs.io/en/stable/reference/ImageFilter.html
