---
name: ai-diffusion-artifact-cleanup
description: "Diagnose and remove AI diffusion artefacts before tracing or print export — soft/blurred edges, halo or drop-shadow around lettering, speckle and grain, semi-transparent fringes and JPEG noise — with hard-alpha cutout, edge-fleck and component filtering, saturation/contrast restore and measured deblur/denoise. Use when the user says clean up AI art, remove the halo, fix the fuzzy edges, get rid of the grain or speckle, denoise this AI image, the cutout has a grey fringe, or prep this diffusion render for tracing or print."
version: 1.0.0
author: DeerFlow Forge
license: original
platforms: [linux, windows]
metadata:
  hermes:
    tags: [ai-art, diffusion-artifacts, cleanup, alpha, print, dtg, image-processing]
    related_skills: [artcraft-image-cleanup, artcraft-vector-trace, ai-image-upscale-print, apparel-print-master]
---

# AI diffusion artefact cleanup

Diffusion renders look clean at thumbnail size and dirty at print size: soft edges, halos, speckle, a semi-transparent fringe and JPEG blocking. Measure, remove, then trace.

## When to use

- A diffusion/AI render is about to be cut out, traced or placed on a print master.
- The cutout shows a grey rim, a light halo under lettering, speckle in flat fills or a fuzzy edge.
- A JPEG-sourced AI image shows blocking/mosquito noise that would survive a trace.

## When not to use

- A photo/scan — `artcraft-image-cleanup`; vectorisation — `artcraft-vector-trace`; upscale — `ai-image-upscale-print`.
- Melted letterforms or inconsistent geometry: a generation defect. Regenerate; no filter invents structure.

## Inputs

- Source with rights (never overwrite), route (trace vs raster master), print width, target DPI (300),
  provider geometry if apparel, brand hex list, and which "glow" is intentional versus a diffusion halo.

## Command pipeline

```bash
cd /opt/pod-pipeline; PY=.venv/bin/python; PC=/opt/craft/photocraft/photocraft-0.20.2-linux-x86_64/bin/photocraft-cli
```

**Step 0 — audit before touching pixels.** Save as `/tmp/artefact_audit.py`, then run `$PY /tmp/artefact_audit.py /tmp/art.png`:

```python
import json, sys, numpy as np
from PIL import Image
from skimage import filters, measure
im = Image.open(sys.argv[1]).convert("RGBA"); a = np.asarray(im.getchannel("A")); o = a > 127
rgb = np.asarray(im.convert("RGB")).astype(np.int16); g = np.asarray(im.convert("L"), dtype=np.float32) / 255.0
hsv = np.asarray(im.convert("RGB").convert("HSV"), dtype=np.float32)
print(json.dumps({"hard_alpha_share": round(float(((a == 0) | (a == 255)).mean()), 4), "semi_transparent_share": round(float(((a > 0) & (a < 255)).mean()), 4),
 "white_residual_ratio": round(float((np.all(rgb >= 245, axis=-1) & o).sum()) / max(1, int(o.sum())), 5), "specks_under_150_px": sum(1 for r in measure.regionprops(measure.label(o)) if r.area < 150),
 "edge_sharpness_laplacian": round(float(filters.laplace(g).var()), 5), "mean_saturation_opaque": round(float(hsv[..., 1][o].mean()) / 255.0, 3)}))
```

**Step 1 — strict white cutout.** Owner rule: every neutral white is transparent (background, paper edge, snow, sky); cream/tan survives. `--clean-rim` hard-thresholds alpha, erodes one pixel, re-softens 0.5 px; `--edge-clean-px 26 --edge-clean-lum 140` strips light flecks. Use the source's longest side for width and height (1024 here).

```bash
$PY -m tools.prep_print_art --input /tmp/art.png --output /tmp/art_cut.png \
  --width-px 1024 --height-px 1024 --dpi 300 --mode white --clean-rim \
  --min-component 60 --edge-clean-px 26 --edge-clean-lum 140 --margin-px 0 \
  --print-width-in 3.413333 --report-json /tmp/art_cut.json
```

**Step 2 — binarise alpha only when the next stage traces.** The 0.5 px feather becomes a key-colour rim; `vectorize_art`/`craft_trace` re-binarise at 128. For a hand-rolled vtracer call:

```bash
$PY -c "from PIL import Image; im=Image.open('/tmp/art_cut.png').convert('RGBA'); im.putalpha(im.getchannel('A').point(lambda v:255 if v>=128 else 0)); im.save('/tmp/art_hard.png')"
```

**Step 3 — colour restore, unsharp last at final size** (`--sharpen` runs after scaling):

```bash
$PY -m tools.prep_print_art --input /tmp/art.png \
  --template pro_e4677535402b4eeb81 --area front_large --dpi 300 \
  --mode white --clean-rim --min-component 60 --edge-clean-px 26 --edge-clean-lum 140 \
  --print-width-in 8 --saturation 1.18 --brightness 1.04 --sharpen 55 \
  --output /tmp/art_master.png --report-json /tmp/art_master.json --preview-dir /tmp/prev_art
```

**Step 4 — JPEG noise and colour with PhotoCraft** (schema-verified; chain executed 2026-11-05).
PhotoCraft takes the file positionally; `--in` is a VectorCraft flag.

```bash
$PC run /tmp/art.jpg \
  --cmd filter.noise.reduceNoise --params '{"strength":6,"preserveDetails":60,"reduceColorNoise":45,"sharpenDetails":25,"removeJpegArtifact":true}' \
  --cmd image.adjustments.levels --params '{"inBlack":6,"gamma":1.05,"inWhite":249}' \
  --cmd filter.sharpen.unsharpMask --params '{"amount":100,"radius":1.2,"threshold":3}' \
  --out /tmp/art_clean.png
```

**Step 5 — deblur/denoise stages in `tools/artcraft.py`:** Richardson-Lucy (`psf sigma 1.1`, 15 iterations)
at `artcraft.py:70`; CLAHE `clip_limit 0.02` on Lab L at `:84`; bilateral `sigma_color 0.06,
sigma_spatial 3.0` at `:98`. **The tool is broken on this install (verified 2026-11-05):** `:84` passes
Lab L in 0–100 to `equalize_adapthist` → `ValueError: Images of type float must be between -1 and 1.`;
after patching that in a `/tmp` copy, `:303` passes a PIL Image to `flatten_on_key`, which calls
`Image.open(...)` → `AttributeError: 'Image' object has no attribute 'read'`. Do not claim a successful
`tools.artcraft` run. Use Step 1/4, or the same calls with `lab[..., 0] / 100.0` and `* 100.0`
(EXPERIMENT: that normalised sequence ran and wrote a 1024² RGB result).

## Workflow

1. `identify` and audit; decide route/print width; under 150 px per print inch, stop and regenerate.
2. Run the white cutout; audit again. A surviving grey rim means the key is wrong for this image.
3. Tracing: binarise alpha and hand off to `artcraft-vector-trace`; raster: saturation/brightness,
   unsharp at final size, compose on provider geometry.
4. Compare at 100 % on black and white; re-audit, store the report, keep the source.

## Acceptance gates

- `white_residual_ratio` ≤ 0.002; `specks_under_150_px` = 0; trace coverage 0.05–0.95 (prep gate 0.005–0.62).
- Trace input: `hard_alpha_share` ≥ 0.85 after binarisation; the trace still passes the 10 `craft_trace`
  gates (white residual, specks, coverage, DPI, canvas, fill colours, edge density, hard alpha,
  transparent corners, retyped text).
- Raster master: 300 DPI, `upscale_factor` ≤ 2.5, `warnings: []` in the `prep_print_art` report.
- Edge sharpness after the final unsharp ≥ 1.0× the same-size pre-sharpen value (1.06× synthetic test;
  2.34× PhotoCraft chain).
- Visual at 100 %: no grey halo ring, no dark rim, no speckle in a flat fill, no lost thin stroke.

## Refusals

- `tools.artcraft` cannot complete end-to-end on this install (two defects above); never present its
  report as evidence until fixed.
- No AI upscaler, super-resolution or "detail recovery" exists here. Regenerate melted letterforms.
- Do not use `--mode white-flood` by default: it keeps enclosed whites (snow, white lettering), violating
  the owner's "every white transparent" rule unless the owner asks for it.
- Do not set `--edge-clean-lum` so high that cream lettering near the silhouette is removed. No browser
  automation; proof is a rendered PNG and a JSON audit, not a page screenshot.

## Worked example

Synthetic 1024² diffusion-like test (white ground, soft drop shadow, 400 speckles) — EXPERIMENT 2026-11-05:

- Before: `white_residual_ratio 0.811`, `hard_alpha_share 1.0`, `specks 0`, sharpness `0.00443`.
- After `prep_print_art` 1024→2400 with `--clean-rim --min-component 60 --edge-clean-px 26`:
  `white_residual 0.0`, `specks 0`, `hard_alpha 0.9557`, `semi_transparent 0.0443`, sharpness `0.01315`.
- Unsharp at final size: `0.01315 → 0.01394` (1.06×); PhotoCraft `0.00024 → 0.00056` (2.34×) at 2400 px; `tools.artcraft` exited 1 at the CLAHE line.

## Pitfalls

- **Upscale is measured on the subject bbox, not the source canvas.** A 1024² source whose art is only
  431 px wide reports `upscale_factor 5.568` for an 8 in print, not 2.34 — trim/regenerate first.
- **`--clean-rim` erodes one pixel.** Hairlines and one-pixel serifs can disappear; check at 100 %.
- **White removal is global.** Snow, eye whites and highlights go transparent by design; the halo often
  lives in alpha, so audit `semi_transparent_share`, not just colour.
- **CLAHE needs 0–1 floats.** The Lab L channel is 0–100; normalise before `equalize_adapthist`.
- **PhotoCraft is positional:** `photocraft-cli run FILE --cmd ...`; `--in` is rejected.

## Sources & verification

- **VERIFIED (executed 2026-11-05):** `tools.prep_print_art` report (`/tmp/up8.json`: `upscale_factor 5.568`, non-empty `warnings`, exit 0); audit numbers above; PhotoCraft chain `reduceNoise → levels → unsharpMask` returning per-step JSON and a 1024² sRGB PNG; `tools.artcraft` failing at `artcraft.py:84` and `:303`.
- **SCHEMA / SOURCE:** `filter.noise.reduceNoise` `{strength 0–10=6, preserveDetails 0–100=60,
  reduceColorNoise 0–100=45, sharpenDetails 0–100=25, removeJpegArtifact bool}` and
  `filter.sharpen.unsharpMask` `{amount 1–500=50, radius 0.1–1000=1, threshold 0–255=0}` from the
  PhotoCraft 0.20.2 registry; `tools/prep_print_art.py:124-169`; `tools/artcraft.py:70-133`.
- **DOCS:** vault `02-VECTORIZATION-AND-QUALITY.md` §Owner rules/Quality controls and
  `15-APPAREL-PRINT-MARKETING-WORKFLOWS.md` §C/D; Pillow 13.0.0 `ImageFilter.UnsharpMask` —
  https://pillow.readthedocs.io/en/stable/reference/ImageFilter.html; scikit-image 0.26.0
  `exposure.equalize_adapthist` — https://scikit-image.org/docs/stable/api/skimage.exposure.html .
  Adobe Photoshop noise/unsharp pages were fetched 2026-11-05 (HTTP 200) but returned only the navigation
  shell; cited for control names only.
