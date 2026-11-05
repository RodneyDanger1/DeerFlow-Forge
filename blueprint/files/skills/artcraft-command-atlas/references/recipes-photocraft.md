# PhotoCraft recipes

## Verification status

- **VERIFIED end-to-end here:** the crop → dust/levels/hue/unsharp → imageSize chain (4032×3024 →
  2400×3000, 118.11 px/cm, exit 0); `convert` lossy/lossless byte comparison.
- **SCHEMA-VERIFIED only:** subject/sky selection + masks, adjustment layers, batch, layer/artboard
  export, LUT, droplets. The ids/params exist; these exact sequences were not run here. Treat them as
  starting points and probe one input first.

PhotoCraft takes the input file positionally, chain order matters, and `--out` must differ from the
input unless `--in-place`. Always keep the source and inspect every step's JSON result.

## 0. Inspect and choose the route

```bash
PC=/opt/craft/photocraft/photocraft-0.20.2-linux-x86_64/bin/photocraft-cli
$PC info /tmp/photo.jpg --compact
identify -format '%f %wx%h %x %y %[colorspace] %z-bit\n' /tmp/photo.jpg
```

Record size, mode, depth and resolution. Decide the destination pixels/DPI before editing.

## 1. Crop → retouch → colour → sharpen → size

```bash
$PC run /tmp/photo.jpg \
  --cmd image.crop --params '{"x":0,"y":0,"width":2400,"height":3000,"deleteCroppedPixels":true}' \
  --cmd filter.noise.dustAndScratches --params '{"radius":1,"threshold":12}' \
  --cmd image.adjustments.levels --params '{"inBlack":4,"gamma":1.05,"inWhite":250}' \
  --cmd image.adjustments.hueSaturation --params '{"saturation":8}' \
  --cmd filter.sharpen.unsharpMask --params '{"amount":90,"radius":1.2,"threshold":2}' \
  --cmd image.imageSize --params '{"width":2400,"height":3000,"resolution":300,"resample":"lanczos"}' \
  --out /tmp/photo_clean.png
identify -format '%f %wx%h %x %y\n' /tmp/photo_clean.png
```

Verified end-to-end (2026-11-05) on a 4032×3024 JPEG: output 2400×3000 sRGB at 118.11 px/cm, exit 0.
Crop bounds: x/y ≥ 0 and x+width/y+height ≤ source. Compute the resize ratio against the **crop**.

## 2. Non-destructive adjustment-layer grade

```bash
$PC run /tmp/photo_clean.png \
  --cmd layer.newAdjustmentLayer.levels --params '{"inBlack":5,"gamma":1.02,"inWhite":250}' \
  --cmd layer.newAdjustmentLayer.curves --params '{"points":[[0,0],[64,72],[192,200],[255,255]]}' \
  --cmd layer.newAdjustmentLayer.hueSaturation --params '{"saturation":6}' \
  --out /tmp/photo_graded.png
```

Adjustment layers keep the original pixels; flatten only for delivery. Check the target layer and
colour space. CMYK conversion is `image.mode.cmyk` and is not a press proof.

## 3. Subject cutout + mask

```bash
$PC run /tmp/photo_graded.png \
  --cmd select.subject --params '{}' \
  --cmd select.refineEdge --params '{"radius":1,"smooth":2,"feather":0.5}' \
  --cmd layer.layerMask.revealSelection --params '{}' \
  --out /tmp/photo_cutout.png
```

Inspect at 100 % on black and white. `select.subject` is a proposal; refine/feather can create halos.
For hair, check `select.refineEdge` params schema. Save the selection (`select.saveSelection`) when you
need to reuse it; alpha channels are named.

## 4. Sky / colour-range selection

```bash
$PC run /tmp/photo.jpg \
  --cmd select.sky --params '{}' \
  --cmd select.modify.feather --params '{"radius":2}' \
  --cmd layer.layerMask.revealSelection --params '{}' \
  --out /tmp/photo_sky.png
```

`select.sky` is content-aware; verify horizon edges. `select.colorRange`/`select.magicWand` need
contiguous/fuzziness decisions; inspect before applying.

## 5. Batch resize with naming

```bash
cat > /tmp/resize-actions.json <<'JSON'
[{"command":"image.imageSize","params":{"width":1600,"height":1600,"units":"px","keepPrintSize":false,"resample":"lanczos"}},
 {"command":"filter.sharpen.unsharpMask","params":{"amount":60,"radius":0.8,"threshold":3}}]
JSON
$PC batch --actions /tmp/resize-actions.json --in /tmp/raw --out /tmp/resized \
  --recursive --stop-on-error --naming '{name}-{serial}'
```

Output is flat: `{name}-{serial}` prevents collisions. The output dir must differ from input unless
`--in-place`. Verify a sample from each subfolder and the total file count.

## 6. Export layers / artboards / paths

```bash
$PC run /tmp/source.psd --cmd file.export.layersToFiles --params '{"path":"/tmp/layers","format":"png"}'
$PC run /tmp/source.psd --cmd file.export.artboardsToFiles --params '{"path":"/tmp/boards","format":"png"}'
$PC run /tmp/source.psd --cmd file.export.pathsToIllustrator --params '{"path":"/tmp/paths.ai"}'
```

Check naming, skipped hidden/empty layers, and that every output has the expected dimensions.

## 7. Export a .cube LUT from adjustment layers

```bash
$PC run /tmp/graded.png --cmd file.export.colorLookupTables --params '{"size":33,"scope":"selected","path":"/tmp/look.cube"}'
```

The LUT is colour-only: masks, vector masks and clipping are omitted. Selected IDs must be visible
top-level adjustments; groups are not exported as independent layers. Check `size` (2–129) and layer
count in the result.

## 8. Quick export and compression

```bash
$PC convert /tmp/photo_clean.png /tmp/photo_clean.webp --quality 82
$PC convert /tmp/photo_clean.png /tmp/photo_lossless.webp
ls -l /tmp/photo_clean.webp /tmp/photo_lossless.webp
identify -format '%f %wx%h %m %b\n' /tmp/photo_clean.webp /tmp/photo_lossless.webp
```

Lossy WebP can be larger than lossless on flat art; compare. `--quality` is ignored for formats that
do not support it (it does not make a PNG lossy). Keep a PNG/TIFF intermediate for further edits.

## 9. Actions file / droplet

```bash
$PC droplet /tmp/records --out /tmp/droplet_out
$PC batch --actions /tmp/actions.json --action "Web resize" --in /tmp/raw --out /tmp/out --stop-on-error
```

Actions files may be `actions.json`, a droplet, or `.atn`; a multi-action set needs `--action NAME`.
Validate the recorded steps against the current registry and test on a copy.

## 10. Delivery checks

- `identify` dimensions/DPI/mode; `info --compact` mode/depth/layers/warnings.
- Missing-font warnings are surfaced; resolve or accept them explicitly.
- No same-path output; source hash unchanged; every batch output exists.
- Colour: screen render only; press colour needs a physical proof.
