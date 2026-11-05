---
name: ai-art-vectorize-vectorcraft
description: "Use for the production path from an AI-generated illustration to a clean vector print master: strict white cutout, AI text erased and retyped, custom limited-palette imageTrace.make, Expand, SVG, print-pixel render, ten gates. Triggers: vectorize AI art, AI illustration to SVG, print-ready vector, retype AI text, badge to vector, clean AI vector, apparel vector master."
version: 1.1.0
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [ai, vectorcraft, trace, retype, print, gates, apparel]
    related_skills: [artcraft-vector-trace, ai-diffusion-artifact-cleanup, apparel-print-master, artcraft-command-catalog]
---

# AI art to vector with VectorCraft

The production path for an AI-generated illustration: strict white pre-cutout, AI text erased and
retyped, custom limited-palette `imageTrace.make`, Expand, SVG export, print-pixel render, ten gates.
`artcraft-vector-trace` covers simple flat logos.

## When to use / not use

- Use for an AI illustration, badge or crest that must become clean editable SVG for print/brand.
- Use when the source carries diffusion texture, soft edges, or AI lettering that must be retyped.
- Use when a print master needs proof: 300 DPI canvas, transparent white, 2–40 fills, 10/10 gates.
- Not for true flat vector logos (`imageTrace.make {preset:"Flat Logo"}` is enough).
- Not for photographic DTG art (keep raster) or stitch files (no engine). Untraceable AI text → stop.

## Inputs

- Source raster (PNG/JPG/WebP) + `identify` dimensions; rights confirmed.
- Print width in inches, DPI (300 apparel), canvas pixels, brand hex list if required.
- **Retype JSON for this design** — text, font path, boxes measured on the ORIGINAL image. The repo
  file `config/retype-ridgeboundia.json` is the Ridgeboundia example only; never reuse its boxes on
  other art. Without text, omit it.
- Template/area when the output is an apparel print master.

## Exact commands (verified 2026-11-05)

```bash
cd /opt/pod-pipeline
VC=/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli
PY=/opt/pod-pipeline/.venv/bin/python
# Linux VPS only. From Windows: ssh -i ~/.ssh/id_ed25519_hostinger root@179.197.88.181 'cd /opt/pod-pipeline && bash -s' < script.sh; stop if unavailable (the /opt CLIs do not exist on Windows).
```

Production wrapper (cutout → erase AI text bands → trace → expand → rsvg → retype → gates):

```bash
$PY -m tools.craft_trace --input /tmp/art.png \
  --template pro_e4677535402b4eeb81 --area front_large --dpi 300 --print-width-in 8 \
  --colors 12 --paths 65 --corners 45 --noise 12 --palette limited --mode color \
  --retype-json /tmp/art_retype.json \
  --output /tmp/art_master.png --svg /tmp/art_master.svg \
  --report-json /tmp/art_master.json --preview-dir /tmp/previews_art
```

Explicit canvas instead of provider geometry (canvas is the full master canvas; art is rendered at
`print_width_in × dpi` and centred). `coverage` is the **art-frame** alpha fill, not canvas occupancy,
so canvas margins do not change it; use the provider canvas for the final output:

```bash
$PY -m tools.craft_trace --input /tmp/art.png \
  --canvas-width 2400 --canvas-height 3000 --dpi 300 --print-width-in 8 \
  --output /tmp/art_master.png --svg /tmp/art_master.svg \
  --report-json /tmp/art_master.json
```

Manual equivalent when driving VectorCraft yourself — prep canvas then trace:

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

Run `$VC run --in /tmp/art_cut.png --commands /tmp/trace-steps.json`; render
`rsvg-convert -w 2400 -o /tmp/art_2400.png /tmp/art.svg`. `document.export` does accept nested SVG
options (`svg.decimals` etc. — schema-verified). The report's `ok` is the verdict; `identify` must
show 118.11 px/cm at 300 DPI.

Retype JSON shape (boxes measured on the original image, `text` empty string erases only):

```json
[{"box":[382,448,998,568],"text":"RIDGEBOUNDIA","font":"FreeSansBold.ttf","fill":"#33614a","stroke":"#d9caa4","stroke_px":6},
 {"box":[378,580,952,655],"text":"MADE FOR THE LONG WAY ROUND","font":"FreeSansBold.ttf","fill":"#e8dcc0","stroke":"#33614a","stroke_px":3},
 {"box":[110,588,250,662],"text":"","font":"FreeSansBold.ttf","fill":"#000000","stroke_px":0}]
```

## Workflow / states

`inspect → cutout → erase text → trace/expand → SVG → render at print px → retype → gates → master`.
Stop on any failed gate; never upload an `ok:false` report.

1. Inspect; require ≥150 px per print inch. Regenerate below that.
2. Pre-cutout every white (`--mode white --clean-rim`); cream/tan survives. If there is no white
   background, the cutout refuses `E_SUBJECT_FULL_FRAME`: use `--mode none` deliberately, or
   `--mode alpha` only when the file has a real alpha channel.
3. Erase AI text bands; trace with custom params; expand and export SVG.
4. Render at `print_width_in × dpi`; retype at mapped boxes; run ten gates and previews.
5. Keep the SVG, PNG master and report JSON together.

## Acceptance gates

`craft_trace` writes `ok:true` only when all ten pass (exit 0; exit 1 = gate failure, 2 = refusal):

- `white_residual_ratio` ≤0.002; `edge_specks` = 0; `transparent_corners` true.
- `coverage` 0.05–0.95; `dpi` ≥300; `canvas_geometry` both sides ≥1500 px.
- `vector_fill_colours` 2–40; `edge_definition` ≥0.01; `alpha_hard_edges` ≥0.85.
- `retyped_text_present`: each text box holds ≥2000 alpha pixels and the overlay covers them.
- Standalone trace: advisory 100–1500 paths, SVG <6 MB, 2–40 fills; no fringe/grain/lost strokes.

### Gate failure → next move (retry once, then escalate)

| Failed gate | First adjustment |
|---|---|
| `white_residual_ratio` | re-cutout; raise `--edge-clean-lum`/`--min-component`; inspect step 1 report |
| `edge_specks` | raise `--noise` (e.g. 12→20), raise `--filter-speckle`, raise cleanup component |
| `coverage` | art is nearly full-frame: add a transparent margin/background or accept it is unsuitable for this gate (canvas margins do NOT change the metric) |
| `vector_fill_colours` | lower `--colors` (e.g. 12→8) and/or simplify source |
| `edge_definition` | raise `--paths` (65→90), lower `--noise`; check 100 % render |
| `alpha_hard_edges` | binarise alpha (craft_trace does; don't feed a feathered cutout) |
| `retyped_text_present` | verify box mapping, font file, and that the overlay actually covers the box |
| `canvas_geometry` | use `--template/--area` or canvas ≥1500 px each side |

**Font check:** the retype overlay uses Pillow `ImageFont.truetype(font_path)` — the font must exist
as a file. `text.fontList` is VectorCraft's font list, not this one; verify with
`ls /usr/share/fonts/**/<font>` or `fc-match <family>`.

**Gate truth:** the report includes `retype_boxes`; `retyped_text_present` defaults to true when there
is no retype spec. `pass:true` with `retype_boxes:0` is vacuous — if the art has text, you must pass
`--retype-json` or stop; never cite that gate as text proof.

**Stale-master caveat:** the live tee master (`rb_tee_craft.json`) was generated before the gate was
tightened to `edge_specks == 0`; its report shows `edge_specks: 4, pass: true` under the old rule.
Regenerate before claiming 10/10 today.

## Measured preset comparison

1024² AI badge, same pre-cutout, exported SVG measured (vault 09/13, 2026-11-05):

| Preset | SVG bytes | paths | fills | Result |
|---|---:|---:|---:|---|
| Flat Logo | 2,501,270 | 3,982 | 3 | overfits texture into specks; grain; rough text |
| Auto Color | 758,967 | 762 | 32 | cleaner, but keeps off-white paper |
| **Custom limited** | **410,571** | **281** | **6** | all ten gates passed at the recorded run |

Production band: colors 10–16, paths 60–90, corners 40–60, noise 6–20 px, method abutting. Presets
are leads, not production settings.

## Coordinate-mapping trap

`prep_print_art` crops to `subject_bbox` and re-centres on its prep canvas (`usable` above), so the
trace input is the full prep canvas. A box measured on the original maps to rendered-art pixels as:

```text
cx = ox + (x - bbox_x0)*s ;  rx = cx * print_px / prep_w ;  print_px = print_width_in*dpi
s  = usable / (bbox_x1 - bbox_x0) ;  usable = min(prep_w - 2*margin, print_width_in*dpi)
ox = (prep_w - usable)//2 ;  oy = (prep_h - round(bbox_h*s))//2
```

`craft_trace` applies this to erase bands and retype boxes. Hand-rolled steps must read the prep
report (`subject_bbox`, `canvas_px`, `subject_px`, `upscale_factor`, `usable_width_px`); applying it
twice or mixing provider/prep canvases reproduces the known ghost-text/misplaced-label bug.

## Refusals / failure modes

- No `--dry-run`; work on a copy, write new paths.
- No stitch engine (`.DST/.PES/.EXP`); below ~150 px/in regenerate.
- Never trace AI lettering; never ship a failed gate.
- Never reuse another design's retype boxes; wrong boxes = invisible/misplaced text.
- No mockup as print proof; rendered PNG + physical sample are proof.
- Do not overwrite an existing master/source.


## Agent operating protocol (follow every time)

**Preflight**
1. Tool versions and source file/dimensions recorded; rights confirmed.
2. Route decision stated (see the decision table); template/area or canvas chosen.
3. Output paths are new; source is preserved.
4. For text: retype JSON exists and the font path resolves on this machine (PIL does the retype, not
   VectorCraft's font list); check before running.

**Execution loop**
1. Probe one step on a copy; parse the JSON, not just the exit code.
2. Run the pipeline; stop at the first failed gate or non-zero step.
3. Verify the artifact (`identify`, report JSON, previews) before claiming a master.

**Evidence contract**
Report commands, artifact paths/sizes, the gate table, and unverified items. A mockup is not proof.

**Stop / escalate**
Missing template/area; missing font; gate still failing after one documented parameter retry; source
below 150 px per print inch; unlicensed asset; tool unavailable; missing print width/template/text/
font/rights — ask, do not invent.

**Never**
Trace AI text; reuse another design's retype boxes; overwrite a master; ship `ok:false`; invent a
parameter; call a screen render print proof.
Command alternatives and parameter tips: **artcraft-command-atlas** (`vc-trace-addon.md`); SVG delivery: **artcraft-svg-production**.
## Sources & verification

- **VERIFIED:** `craft_trace` gate names/thresholds and `ok` semantics; nested `params.params`;
  `select.all` mandatory; `document.export` nested SVG options (schema + export test); retype mapping
  from the tool source; the measured preset table; `vectorize_art --help`; 410,571-byte / 281-path /
  6-fill record; stale 4-speck report.
- **SCHEMA:** `/opt/craft/catalogues/vectorcraft-commands.json`; vault 17.
- **DOCS:** `image-trace-adjustments.md`, `image-trace-quality.md`; Adobe panel options
  https://helpx.adobe.com/illustrator/desktop/manage-objects/traces-mockups-symbols/image-trace-panel-options.html
