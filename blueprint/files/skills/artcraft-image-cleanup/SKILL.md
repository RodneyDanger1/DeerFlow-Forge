---
name: artcraft-image-cleanup
description: PhotoCraft raster cleanup in the Photoshop order — crop, retouch, colour, sharpen last, export at the right DPI — plus the strict white cutout when art must go to print. Use when the user says clean up this image, retouch this photo, fix the colour, remove dust and scratches, denoise, set 300 DPI, prepare a raster for print, or the scan/phone photo looks dull or dirty.
---

# ArtCraft image cleanup

Raster retouch for supplied or AI images that stay raster. The output is a corrected image at
a known size and DPI; flat art that should become vector belongs to `artcraft-vector-trace`.

## When to use

- A photo, scan or AI raster needs crop/retouch/colour correction before print or web use.
- The image must carry the right pixel dimensions and DPI for a provider.
- Dust, scratches, speckle, noise or a colour cast must go.
- Art needs a clean transparent cutout before tracing or compositing.

## When not to use

- Flat logo/illustration that should be vector — trace it.
- AI-rendered text that needs to be crisp — erase/retype in the trace pipeline.
- Upscaling beyond 2.5× — regenerate the source instead; this skill does not invent detail.
- Embroidery, stitch files or ad layouts — different skills.
- Colour-managed CMYK proofing: conversion may be possible, but proofing is not verified.

## Required inputs

- Source file and its current size/depth/colour mode.
- Destination: print (physical inches, target DPI) or screen (pixel box, format).
- What "wrong" means: crop, dust, colour cast, dull colour, softness.
- Rights to the image, and whether the original must be preserved.
- Vendor colour mode if the result goes to a print shop.

## Exact commands

```bash
cd /opt/pod-pipeline
PC=/opt/craft/photocraft/photocraft-0.20.2-linux-x86_64/bin/photocraft-cli
PY=/opt/pod-pipeline/.venv/bin/python
```

Inspect first — size, mode, depth, resolution, layer tree:

```bash
$PC info /tmp/photo.jpg --compact
```

Full retouch chain in Photoshop order (crop → retouch → colour → sharpen last → resolution):

```bash
$PC run /tmp/photo.jpg \
  --cmd image.crop --params '{"x":0,"y":0,"width":2400,"height":3000}' \
  --cmd filter.noise.dustAndScratches --params '{"radius":1,"threshold":12}' \
  --cmd image.adjustments.levels --params '{"inBlack":4,"gamma":1.05,"inWhite":250}' \
  --cmd image.adjustments.hueSaturation --params '{"saturation":8}' \
  --cmd filter.sharpen.unsharpMask --params '{"amount":90,"radius":1.2,"threshold":2}' \
  --cmd image.imageSize --params '{"width":2400,"height":3000,"resolution":300}' \
  --out /tmp/photo_clean.png
```

Other verified engine commands: `filter.noise.despeckle`, `filter.noise.median {"radius":1}`,
`filter.sharpen.smartSharpen {"amount":100,"radius":1,"reduceNoise":10}`,
`image.adjustments.curves {"points":[[0,0],[64,72],[192,200],[255,255]]}`,
`image.adjustments.brightnessContrast`, `image.adjustments.desaturate`, `image.canvasSize`,
`file.saveACopy {"path":"..."}`, `file.export.quickExport`.

Batch a folder with an action list (JSON steps: `{"command":id,"params":{…}}`):

```bash
$PC batch --actions /tmp/cleanup.json --in /tmp/in --out /tmp/out --recursive --stop-on-error
```

Strict white cutout when the cleaned raster feeds print or trace:

```bash
$PY -m tools.prep_print_art --input /tmp/photo_clean.png --output /tmp/clean_cut.png \
  --width-px 2400 --height-px 3000 --dpi 300 --mode white --clean-rim \
  --min-component 60 --edge-clean-px 26 --edge-clean-lum 140 --margin-px 0 \
  --print-width-in 8 --report-json /tmp/clean_cut.json
```

Verify the result (`%x`/`%y` are px/cm: 118.11 = 300 DPI, 28.35 = 72 DPI):

```bash
identify -format '%f %wx%h %x %y %[colorspace]\n' /tmp/photo_clean.png
```

## Workflow

1. `info` the file; record size, depth and resolution.
2. Decide print inches × DPI (or the screen pixel box) **before** touching pixels.
3. Crop/straighten to the final aspect; never crop after sharpening.
4. Retouch noise/dust with the least destructive filter that works.
5. Correct colour with levels/curves, then hue/saturation — one intent per step.
6. Sharpen **last, at final size**; then set size and resolution in one `image.imageSize` call.
7. Export to a new path, `identify` it, and compare against the original at 100 % and thumbnail.

## Acceptance gates

- Output dimensions equal the requested pixel box; DPI equals the requested value.
- `identify` reports the expected colourspace (normally sRGB) and bit depth.
- No upscale beyond 2.5×; record `output_px / source_px` if it is close.
- Sharpening is visible at 100 % without halos or crunchy edges.
- Colour matches the reference/original at the same zoom; brand colours sit on the hex list.
- The original file is unchanged; the result lives at a new path.
- For print: 300 DPI canvas and every white transparent (owner rule) when applicable.

## Refusal conditions

- No dry-run: `photocraft-cli` has no preview flag. Write to a new path, inspect, and iterate.
- The CLI refuses `--out` equal to the input (verified: "the result would replace the
  original"); keep originals and use `--in-place` only deliberately.
- Clone/heal/spot commands exist in the PhotoCraft registry (`paint.cloneStamp`, `paint.healingBrush`, `paint.spotHealing`, `paint.patch`) but are unverified here; dust & scratches, despeckle and median are the
  documented retouch tools. If the defect needs structural repair, say so and escalate.
- No AI upscaler in this environment; do not claim detail was recovered.
- No browser automation; cannot verify how an image will look inside a live page.
- CMYK conversion and press proof are not verified — get a printed proof from the vendor.

## Worked examples

**1. Phone photo → 4×6 in print.** Source 4032×3024. Final 1200×1800 px at 300 DPI is a
downscale, so it is allowed: crop to 2:3, dust & scratches, levels, mild saturation, unsharp
mask, then `image.imageSize {"width":1200,"height":1800,"resolution":300}`. Confirm `%x` = 118.11.

**2. Scanned artwork with a yellow cast and dust.** `info` shows 16-bit RGB at 72 DPI.
Run dust & scratches, levels `{"inBlack":6,"gamma":1.0,"inWhite":248}`, hue/saturation `{"saturation":6}`,
then unsharp mask; export PNG and cut out white with `prep_print_art --mode white` only if the
art needs transparency.

## Pitfalls

- **`--params` binds to the `--cmd` before it** — reorder and the parameters land on the wrong
  filter.
- **Resolution metadata is not pixels** — `image.imageSize` with new width/height resamples;
  with only resolution it can set metadata (`keepPrintSize` controls the resample).
- **Sharpen last at final size** — sharpening before downscale throws the work away.
- **Filters are destructive** — always keep the original and chain on a copy.
- **16-bit sources** are reported as depth 16; flattening to 8-bit is a decision, not a default.
- **JPEG recompression** loses quality each save; keep PNG/TIFF intermediates and set
  `--quality` only on the final lossy output.
