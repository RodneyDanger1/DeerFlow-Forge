---
name: artcraft-image-cleanup
description: "Use when a supplied photo, scan or AI raster needs cleanup before print or web: crop, dust/scratches, noise, colour cast, levels/curves, saturation, sharpen last, exact DPI — then a strict white cutout if it feeds print/trace. Triggers: clean image, retouch photo, remove dust, denoise, fix colour cast, set 300 DPI, prepare raster for print, sharpen image, PhotoCraft cleanup."
version: 1.0.0
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [artcraft, photocraft, retouch, cleanup, print, dpi, sharpen]
    related_skills: [ai-image-upscale-print, artcraft-vector-trace, ai-diffusion-artifact-cleanup, apparel-print-master]
---

# ArtCraft image cleanup

Raster retouch for supplied or AI images that stay raster. Output is a corrected image at a known
size and DPI. Flat art that should become vector belongs to `artcraft-vector-trace`.

## When to use

- A photo, scan or AI raster needs crop/retouch/colour before print or web.
- The image must carry exact pixel dimensions and DPI for a provider.
- Dust, scratches, speckle, noise or a colour cast must go.
- Art needs a clean transparent cutout before tracing/compositing.

## When not to use

- Flat logo/illustration that should be vector — trace it.
- AI lettering that must be crisp — erase/retype in the trace pipeline.
- Upscale beyond 2.5× — regenerate; this skill does not invent detail.
- Embroidery/stitch files, ad layout or colour-managed CMYK proofing — different skills; CMYK
  conversion may exist but press proofing is not verified.

## Required inputs

- Source file and its current size/depth/mode/resolution.
- Destination: print inches + DPI, or screen pixel box + format.
- The defect: crop, dust, colour cast, dull colour, softness, noise.
- Rights and whether the original must be preserved (it must; never overwrite).
- Vendor colour mode for print.

## Exact commands (verified 2026-11-05)

```bash
cd /opt/pod-pipeline
PC=/opt/craft/photocraft/photocraft-0.20.2-linux-x86_64/bin/photocraft-cli
PY=/opt/pod-pipeline/.venv/bin/python
# Linux VPS only. From Windows: ssh -i ~/.ssh/id_ed25519_hostinger root@179.197.88.181 'cd /opt/pod-pipeline && bash -s' < script.sh
# Stop if SSH/key is unavailable: /opt/pod-pipeline and the CLIs do not exist on Windows.
```

Inspect first — PhotoCraft takes the file positionally:

```bash
$PC info /tmp/photo.jpg --compact
```

Photoshop-order retouch chain (crop → retouch → colour → sharpen last → resolution). `image.crop`
exists in PhotoCraft; params include x,y,width,height,angle,deleteCroppedPixels,contentAware,
targetWidth,targetHeight,resolution,resample. The final `--out` must differ from input unless
`--in-place`:

```bash
$PC run /tmp/photo.jpg \
  --cmd image.crop --params '{"x":0,"y":0,"width":2400,"height":3000,"deleteCroppedPixels":true}' \
  --cmd filter.noise.dustAndScratches --params '{"radius":1,"threshold":12}' \
  --cmd image.adjustments.levels --params '{"inBlack":4,"gamma":1.05,"inWhite":250}' \
  --cmd image.adjustments.hueSaturation --params '{"saturation":8}' \
  --cmd filter.sharpen.unsharpMask --params '{"amount":90,"radius":1.2,"threshold":2}' \
  --cmd image.imageSize --params '{"width":2400,"height":3000,"resolution":300,"resample":"lanczos"}' \
  --out /tmp/photo_clean.png
```

Other verified engine commands: `filter.noise.despeckle`, `filter.noise.median {"radius":1}`,
`filter.sharpen.smartSharpen {"amount":100,"radius":1,"reduceNoise":10}`,
`image.adjustments.curves {"points":[[0,0],[64,72],[192,200],[255,255]]}`,
`image.adjustments.brightnessContrast`, `image.adjustments.desaturate`, `image.canvasSize`,
`file.saveACopy`, `file.export.quickExport`.

Lossy export and batch:

```bash
$PC convert /tmp/photo_clean.png /tmp/photo_clean.webp --quality 82   # warn: lossy compression
$PC batch --actions /tmp/cleanup.json --in /tmp/in --out /tmp/out --recursive --stop-on-error --naming '{name}-{serial}'
```

`batch` action steps are `{"command":id,"params":{…}}` / `[id, params]` / bare ids. With
`--recursive` results flatten into `--out`, so same names overwrite; use `--naming`.

Strict white cutout only when the cleaned raster feeds print/trace (a photo that must keep white content skips it):

```bash
$PY -m tools.prep_print_art --input /tmp/photo_clean.png --output /tmp/clean_cut.png \
  --width-px 2400 --height-px 3000 --dpi 300 --mode white --clean-rim \
  --min-component 60 --edge-clean-px 26 --edge-clean-lum 140 --margin-px 0 \
  --print-width-in 8 --report-json /tmp/clean_cut.json
```

Verify (`%x`/`%y` px/cm: 118.11 = 300 DPI, 28.35 = 72 DPI):

```bash
identify -format '%f %wx%h %x %y %[colorspace]\n' /tmp/photo_clean.png
```

## Preflight math (agent-critical)

Before touching pixels, compute and record:

- `target_px = print_inches × dpi` (or the screen box).
- `upscale = target_px / baseline_px`, where `baseline_px` is the **crop that feeds the resize**, not
the original frame (a 2400×3000 crop of a 4032×3024 source resized to 2400×3000 is 1.0×, not 0.6×).
  **Refuse if > 2.5×**; send to `ai-image-upscale-print` or regenerate; name the ratio in the report.
- Crop bounds: `x ≥ 0`, `y ≥ 0`, `x+width ≤ source_width`, `y+height ≤ source_height`; otherwise the
  crop params are wrong for that file.
- Output path differs from input; PhotoCraft refuses same-path `--out` unless `--in-place`.
- Read `info` before/after: size, mode, depth, resolution.
- Ask for destination print size/DPI, defect and rights when absent; never choose 300 DPI silently.
- If the source has no white background (dark/full-bleed photo), `--mode white` refuses
  `E_SUBJECT_FULL_FRAME`; use `--mode none` deliberately, or `--mode alpha` only when the file has a real
  alpha channel.

## Workflow / state machine

1. `info` → record size, depth, resolution; confirm the file is readable.
2. Decide output pixels **before** touching pixels: print inches × DPI, or screen box.
3. Crop/straighten to the final aspect; never crop after sharpening.
4. Retouch noise/dust with the least destructive filter that works; re-check at 100 %.
5. Correct colour with levels/curves, then hue/saturation — one intent per step.
6. Sharpen last, at final size; then set size/resolution once with `image.imageSize`.
7. Export to a new path; `identify`; compare original vs result at 100 % and thumbnail.
8. If print/trace: run the white cutout and check its report.

States: `inspected → cropped → retouched → colour-corrected → sharpened → sized → exported → verified`.
A failed step leaves the previous file untouched; never continue on a refused `--out`.

## Acceptance gates

- Output dimensions equal the requested box; DPI equals the requested value (`identify`).
- Colourspace/bit depth expected (normally sRGB 8-bit; 16-bit flatten is a decision).
- No upscale >2.5×; record `output_px/source_px` when close.
- Sharpening visible at 100 % with no halos/crunch; denoise did not erase detail.
- Brand colours land on the hex list; original file unchanged; result at a new path.
- Print: 300 DPI canvas and every neutral white transparent (owner rule) when applicable.

## Refusals / failure modes

- No dry-run. Run on a copy, write a new path, read each step's JSON.
- `photocraft-cli run --out` equal to input is refused (`--in-place` permits it, deliberately only).
- Clone/heal/spot ids exist (`paint.cloneStamp`, `paint.healingBrush`, `paint.spotHealing`,
  `paint.patch`) but their behaviour is **UNVERIFIED** here; dust & scratches, despeckle and median
  are the verified retouch chain. Structural repair without a verified tool → escalate.
- No AI upscaler; do not claim detail was recovered. No browser automation; CMYK/press proof
  unverified — vendor proof required.
- Batch collision: `--recursive` without `--naming` can overwrite results.

## Integration handoffs

- Flat art → `artcraft-vector-trace` / `ai-art-vectorize-vectorcraft` (after cutout).
- AI diffusion artefacts → `ai-diffusion-artifact-cleanup` first.
- Large upscale decision → `ai-image-upscale-print`.
- Print master → `apparel-print-master` / exact product skill.
- Web/ad → `web-banner` / `ad-creative`.

## Worked examples

**1. Phone photo → 4×6 in print.** 4032×3024 source; final 1200×1800 at 300 DPI is a downscale:
crop to 2:3, dust & scratches, levels, mild saturation, unsharp, then
`image.imageSize {"width":1200,"height":1800,"resolution":300,"resample":"lanczos"}`. `%x` = 118.11.

**2. Scanned artwork with yellow cast and dust.** 16-bit RGB at 72 DPI: dust & scratches, levels
`{"inBlack":6,"gamma":1.0,"inWhite":248}`, hue/saturation `{"saturation":6}`, unsharp; export PNG;
white-cutout only if transparency is needed.

## Pitfalls

- **`--params` binds to the preceding `--cmd`** — reorder and params land on the wrong filter.
- **Resolution metadata ≠ pixels** — `image.imageSize` with width/height resamples; with only
  resolution it can set metadata; `keepPrintSize` controls the resample (verified schema).
- **Sharpen last at final size**; sharpening before downscale throws work away.
- Filters are destructive; chain on a copy and keep the original.
- 16-bit sources report depth 16; flattening is a decision.
- JPEG recompression loses quality; keep PNG/TIFF intermediates and set `--quality` only at the end.
- `photocraft-cli convert --quality` warns "lossy compression"; for flat art the lossy WebP can be
  *larger* than the lossless one (measured 2,718 B vs 1,372 B on a 1080² flat test) — compare bytes.

## Agent operating protocol (follow every time)

**Preflight:** run `info`; confirm mode/depth/resolution; compute target px, DPI, upscale ratio and
crop bounds; confirm the original is preserved; refuse >2.5× upscale or out-of-bounds crop.

**Execution loop:** run one filter step, parse its JSON result (filters echo params;
`image.adjustments.*` returns null — null is success here, but exit code must be 0); verify the image
after each destructive step; only then chain.

**Evidence:** `identify` before/after, step JSON, output path/size/DPI/colourspace, sharpness/visual
check; exit 0 is not proof.

**Stop/escalate:** missing input; crop out of bounds; >2.5× upscale; no verified repair tool for the
defect; CMYK/proof needed; batch name collision without `--naming`.

**Never:** overwrite the source; sharpen before final resize; trust a lossy export byte-size blindly;
claim CMYK proof from an RGB screen.

## Sources & verification

- **VERIFIED (2026-11-05):** `photocraft-cli` help for `run/convert/batch` (positional input,
  `--out`, `--quality`, `--format`, `--recursive`, `--stop-on-error`, `--naming`, refusal of
  same-path output); 965-row registry; `image.crop`, `image.imageSize`, `image.canvasSize`,
  `filter.noise.*`, `filter.sharpen.*`, `image.adjustments.*` schemas via `commands --json`;
  `convert --quality` output 2,718 B vs lossless 1,372 B on a flat 1080² test; `text.fontList`
  returned 45 families. **Chain executed end-to-end 2026-11-05:** 4032×3024 JPEG → crop 2400×3000 →
  filters → 2400×3000 sRGB at 118.11 px/cm, exit 0.
- **SCHEMA:** `/opt/craft/catalogues/photocraft-commands.json`; vault 17.
- **DOCS:** vault 02/15; Pillow UnsharpMask https://pillow.readthedocs.io/en/stable/reference/ImageFilter.html
