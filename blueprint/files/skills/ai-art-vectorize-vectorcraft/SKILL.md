---
name: ai-art-vectorize-vectorcraft
description: "AI illustration to clean vector print art with VectorCraft imageTrace.make: pre-cutout, erase and retype AI text, custom limited-palette trace, Expand, SVG export, rsvg at print pixels, 10 gates. Use when the user says vectorise this AI art, trace this illustration, make a print-ready SVG, clean vector art from Midjourney or DALL-E, turn this AI mark into vectors, or prepare vector art for a shirt."
version: 1.0.0
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [vectorization, image-trace, vectorcraft, artcraft, ai-art, svg, print]
    related_skills: [artcraft-vector-trace, apparel-print-master, artcraft-command-catalog, craft-mcp-drive]
---

# AI art to vector with VectorCraft

The production path for an AI-generated illustration: strict white pre-cutout, AI text erased and
retyped, custom limited-palette `imageTrace.make`, Expand, SVG export, print-pixel render, ten gates.
`artcraft-vector-trace` covers simple flat logos.

## When to use

- An AI illustration, badge or crest must become clean, editable SVG for print or brand use.
- The source carries diffusion texture, soft edges, or AI lettering that must be retyped.
- A print master needs proof: 300 DPI canvas, transparent white, 2–40 fills, 10/10 gates.

## When not to use

- True flat vector logos: `imageTrace.make {preset:"Flat Logo"}` is enough (`artcraft-vector-trace`).
- Photographic DTG art: keep it raster (`artcraft-image-cleanup` + `apparel-print-master`).
- Embroidery or stitch files: no stitch engine here (`embroidery-art`). Untraceable AI text: stop.

## Inputs

- Source raster (PNG/JPG/WebP) and `identify` dimensions; rights confirmed.
- Print width in inches, DPI (300 for apparel), canvas pixels, and brand hex list if required.
- Retype JSON — text, font path, boxes measured on the ORIGINAL — plus template/area for apparel.

## Exact commands

```bash
# from /opt/pod-pipeline
VC=/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli; PY=.venv/bin/python
```

Production wrapper — cutout, erase/retype, trace, expand, rsvg, 10 gates:

```bash
$PY -m tools.craft_trace --input /tmp/art.png \
  --canvas-width 2400 --canvas-height 3000 --dpi 300 --print-width-in 8 \
  --colors 12 --paths 65 --corners 45 --noise 12 --palette limited --mode color \
  --retype-json /opt/pod-pipeline/config/retype-ridgeboundia.json \
  --output /tmp/art_master.png --svg /tmp/art_master.svg \
  --report-json /tmp/art_master.json --preview-dir /tmp/previews_art
```

Provider geometry instead of canvas pixels: `--template pro_e4677535402b4eeb81 --area front_large`
(15×18 in → 4500×5400 px). Manual equivalent when driving VectorCraft yourself:

```bash
$PY -m tools.prep_print_art --input /tmp/art.png --output /tmp/art_cut.png \
  --width-px 1024 --height-px 1024 --dpi 300 --mode white --clean-rim \
  --min-component 60 --edge-clean-px 26 --edge-clean-lum 140 --margin-px 0 \
  --print-width-in 3.413333 --report-json /tmp/art_cut.json
```

```json
[{"command":"select.all"},
 {"command":"imageTrace.make","params":{"enhanced":false,"params":{
   "mode":"color","palette":"limited","colors":12,"paths":65,"corners":45,
   "noise":12,"method":"abutting","ignoreWhite":true,"fills":true,
   "strokes":false,"shapes":false,"autoGrouping":false,"gradients":false}}},
 {"command":"imageTrace.expand"},
 {"command":"document.export","params":{"path":"/tmp/art.svg","format":"svg","svg":{"decimals":3}}}]
```

Save as `/tmp/trace-steps.json`; run `$VC run --in /tmp/art_cut.png --commands /tmp/trace-steps.json`;
render `rsvg-convert -w 2400 -o /tmp/art_2400.png /tmp/art.svg`. The report's `ok` is the verdict, each
check carries `pass`, and `identify -format '%f %wx%h %x %y\n'` must show 118.11 px/cm.

## Workflow

1. Inspect the source; require at least 150 px per print inch. Regenerate below that.
2. Pre-cutout every white with `prep_print_art --mode white --clean-rim`; cream/tan survives.
3. Erase AI text bands; trace with the custom params; expand and export SVG.
4. Render at `print_width_in × dpi`; retype at the mapped boxes; run the ten gates and previews.

## Acceptance gates

`craft_trace` writes `ok: true` only when all ten pass (exit 0; exit 1 = gate failure, 2 = refusal):

- `white_residual_ratio` ≤ 0.002; `edge_specks` = 0; `transparent_corners` true.
- `coverage` 0.05–0.95; `dpi` ≥ 300; `canvas_geometry` both sides ≥ 1500 px.
- `vector_fill_colours` 2–40; `edge_definition` ≥ 0.01; `alpha_hard_edges` ≥ 0.85.
- `retyped_text_present`: each box holds ≥ 2000 alpha pixels and the overlay covers them.
- Standalone trace: 100–1500 paths, SVG under 6 MB, 2–40 fills; no fringe, grain or lost strokes at 100 %.

## Measured preset comparison

1024² AI badge, same pre-cutout, exported SVG measured (vault 09/13, 2026-11-05):

| Preset | SVG bytes | paths | fills | Result |
|---|---:|---:|---:|---|
| Flat Logo | 2,501,270 | 3,982 | 3 | overfits texture into specks; grain in mountains; text rough |
| Auto Color | 758,967 | 762 | 32 | cleaner, but keeps the off-white paper (ignoreWhite removes only true white) |
| **Custom limited** | **~460,000** | **281** | **6–7** | all ten gates pass |

Presets are leads, not production settings. Production band: colors 10–16, paths 60–90, corners
40–60, noise 6–20 px, method abutting. `Flat Logo` is capped at 1024 px/side and has no enhanced variant.

## Coordinate-mapping trap

`prep_print_art` crops to `subject_bbox` and re-centres on its **prep canvas** (craft_trace uses the
source W×H), so the trace input is the full prep canvas. A box measured on the original maps:

```text
cx = ox + (x - bbox_x0)*s;  rx = cx * print_px / prep_w;  print_px = print_width_in * dpi
s = usable / (bbox_x1 - bbox_x0);  ox,oy = ((prep_w - scaled_w)//2, (prep_h - scaled_h)//2)
usable = min(prep_w - 2*margin_px, print_width_in * dpi)
```

`craft_trace` applies this internally to `--retype-json` boxes and erase bands. Hand-rolled steps
must use the prep report's `subject_bbox`, `canvas_px`, `subject_px`, `upscale_factor`; applying
the transform twice — or mixing provider-canvas and prep-canvas coordinates — produces the known
ghost-text and misplaced-label bug.

## Refusals

- No `--dry-run` in `vectorcraft-cli` or the pipeline tools. Work on a copy, write a new path.
- No stitch-file engine: refuse `.DST/.PES/.EXP` (`embroidery-art`); below ~150 px/in, regenerate.
- Never trace AI lettering; never ship a failed gate.
- No mockup as print proof; a rendered PNG and a physical sample are proof.
- Do not overwrite an existing master or the source; export to a new path.

## Worked example

Ridgeboundia badge (1024² AI art, 2400×3000 canvas, 8 in at 300 DPI). Flat Logo gave 3,982 paths
and 2.5 MB of texture noise; Auto Color gave 762 paths but kept off-white. The custom run (12
colours, paths 65, corners 45, noise 12) produced 410,571 bytes, 281 paths, 6 fills, 10/10 gates.

## Pitfalls

- `select.all` before `imageTrace.make`, or `nothing selected` at step 0.
- Trace settings live under `params.params`; unknown outer keys are rejected by name.
- `ignoreWhite` drops only true white; off-white paper survives unless you pre-cutout.
- Abutting shares edges and can leave a hairline in SVG/PDF; use `method:"overlapping"` on dark garments (DOCS).
- More than 8,000,000 anchors is refused; raise `noise` or lower `paths`/`colors`. Unite only single-colour art; `object.pathfinder.unite` flattens a multi-colour palette.
- A screen render is not a print check: `rsvg-convert -w` at print pixels, then inspect at 100 %.
- `identify` px/cm: 118.11 = 300 DPI, 28.35 = 72 DPI.

## Sources & verification

- **VERIFIED** (executed/probed 2026-11-05 on srv2108523): `imageTrace.make`/`expand` with nested
  params; `select.all` mandatory (error `nothing selected`); gate names/thresholds from
  `/opt/pod-pipeline/tools/craft_trace.py`; `rsvg-convert 2.61.3`; ImageMagick 7.1.2; tool `--help`.
  Preset numbers are the measured record in vault 09/13.
- **SCHEMA**: `/opt/craft/catalogues/vectorcraft-commands.json` — `imageTrace.*`, `document.export`,
  `select.all` ids/ranges, and `document.export` `svg.decimals`.
- **DOCS**: `/opt/craft/artcraft-docs/image-trace-adjustments.md` (Flat Logo 1024 px cap, 8 M anchors,
  abutting seams); `image-trace-quality.md` (palette, paths, corners, noise behaviour).
- Adobe Image Trace panel options (fetched): https://helpx.adobe.com/illustrator/desktop/manage-objects/traces-mockups-symbols/image-trace-panel-options.html · VectorCraft README (fetched): https://raw.githubusercontent.com/storytold/vectorcraft/main/README.md · product page: https://getartcraft.com/apps/vectorcraft
