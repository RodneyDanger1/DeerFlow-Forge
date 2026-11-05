---
name: artcraft-vector-trace
description: Trace raster logos, badges and AI illustration into clean editable SVG with ArtCraft VectorCraft (Illustrator Image Trace equivalent) — white cutout, Illustrator-compatible imageTrace params, Expand, rendered check. Use when the user says vectorise this, trace this logo, make this an SVG, convert image to vector, AI art to vector, clean vector art, trace for print, or brand mark vector.
---

# ArtCraft vector trace

Turns a raster image into a scalable vector: an **SVG master plus a rendered check PNG** — not
a mockup and not a provider print master (continue with `apparel-print-master` for that).

## When to use

- A flat logo, badge, crest or illustration must become an SVG/vector asset.
- An AI-generated mark needs a crisp, scalable version for brand or print use.

## When not to use

- Painterly art whose texture auto-trace turns into grain/banding — regenerate flatter or
  higher-resolution art first; do not ship a traced mess.
- AI-rendered lettering: erase and retype (the production wrapper does this). Never trace it.
- Photographic reproduction for DTG — use `artcraft-image-cleanup` and the raster fallback.
- Embroidery/stitch files — there is no stitch engine; see `embroidery-art`.

## Required inputs

- Source raster (PNG/JPG/WebP) with rights, and its pixel dimensions.
- Target: SVG master only, or SVG + print master.
- Brand hex list, if the palette must stay on brand.
- Wordmark/tagline text and font when AI text must be retyped.
- Print inches and provider `productId`/`area` when the trace feeds apparel.

## Exact commands

```bash
cd /opt/pod-pipeline
VC=/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli
PY=/opt/pod-pipeline/.venv/bin/python
```

Step 1 — strict white cutout (owner rule: every white transparent; cream/tan stays):

```bash
$PY -m tools.prep_print_art --input /tmp/art.png --output /tmp/art_cut.png \
  --width-px 1024 --height-px 1024 --dpi 300 --mode white --clean-rim \
  --min-component 60 --edge-clean-px 26 --edge-clean-lum 140 --margin-px 0 \
  --print-width-in 3.413333 --report-json /tmp/art_cut.json
```

Step 2 — trace steps. `imageTrace.make` takes `id|preset|savedPreset|enhanced|params|view|ids`;
the trace panel settings live **inside** `params`:

```bash
cat > /tmp/trace-steps.json <<'JSON'
[{"command":"select.all"},
 {"command":"imageTrace.make","params":{"params":{
   "mode":"color","palette":"limited","colors":12,"paths":65,"corners":45,"noise":12,
   "ignoreWhite":true,"method":"abutting","fills":true,"strokes":false,
   "shapes":false,"autoGrouping":false,"gradients":false}}},
 {"command":"imageTrace.expand"}]
JSON
$VC run --in /tmp/art_cut.png --commands /tmp/trace-steps.json --export /tmp/art.svg
```

Step 3 — render a check PNG at real pixels and inspect:

```bash
rsvg-convert -w 2400 -o /tmp/art_2400.png /tmp/art.svg
grep -c '<path' /tmp/art.svg && ls -l /tmp/art.svg && identify /tmp/art_2400.png
```

Production wrapper (cutout + erase AI text bands + retype + rsvg + 10 gates + previews):

```bash
$PY -m tools.craft_trace --input /tmp/art.png --canvas-width 2400 --canvas-height 3000 \
  --dpi 300 --print-width-in 8 --retype-json config/retype-ridgeboundia.json \
  --output /tmp/art_master.png --svg /tmp/art_master.svg --report-json /tmp/art_master.json \
  --preview-dir /tmp/previews_art
```

Venv tracer alternative for flat art (no VectorCraft, no retype/gates):

```bash
$PY -m tools.vectorize_art --input /tmp/art.png --svg /tmp/art.svg --output /tmp/master.png \
  --canvas-width 2400 --canvas-height 3000 --dpi 300 --print-width-in 8 --cutout white \
  --report-json /tmp/master.json
```

## Workflow

1. Inspect the source (`identify`) and confirm ≥150 px per print inch.
2. Cut out white with `prep_print_art --mode white`; cream lettering must survive.
3. Write the step JSON: `select.all`, `imageTrace.make`, `imageTrace.expand`.
4. Run the trace on the cutout — never on the untouched photo.
5. Render the SVG at print pixels with `rsvg-convert -w`, then review at 100 % and thumbnail
   for banding, key rims, lost thin strokes and texture grain.
6. If AI text exists, run `tools.craft_trace` with a retype JSON; keep the SVG/PNG masters.

## Acceptance gates

- `select.all` ran (a trace without it fails: `step 0 (imageTrace.make): nothing selected`).
- Gate JSON `ok: true` when the wrapper is used — all ten checks (white residual ≤0.002,
  specks 0, coverage 0.05–0.95, DPI ≥300, canvas ≥1500², 2–40 fill colours, edge density
  ≥0.01, hard alpha ≥0.85, transparent corners, retyped text present).
- Standalone trace: 100–1500 paths typical for a logo; SVG < 6 MB; 2–40 distinct fills.
- Visual: no white paper edge, no magenta/key fringe, no grain inside flat fills.
- Text is live type or a proven retype overlay — never traced AI lettering.
- Colour compared against the brand hex list (trace drift is normal; correct it deliberately).

## Refusal conditions

- No stitch-file engine: refuse `.DST/.PES/.EXP` requests; that is `embroidery-art` + a digitizer.
- No dry-run flag exists (`vectorcraft-cli` rejects `--dry-run`). Run on a copy, export to a
  new path, inspect the per-step JSON; never assume a step succeeded.
- No browser automation in this environment — a rendered PNG is the proof, a page screenshot is not.
- Do not claim print quality from a screen render; mockups prove placement only.
- Refuse a trace when the source is below ~150 px per print inch: regenerate, do not upscale.

## Worked examples

**1. Flat two-colour mark → SVG.** A 1024² cutout traced with `colors:6, paths:65, corners:45,
noise:8, ignoreWhite:true` returned `{"anchors":10,"colors":1,"id":4,"paths":1}` and a 768-byte
SVG — quote the JSON as evidence, then review the 2400 px render; it is not proof of quality.

**2. AI badge → print-ready.** Pre-cutout, custom limited-palette params, SVG at print pixels,
AI text bands erased and retyped with FreeSansBold at the mapped boxes. Measured on the
Ridgeboundia badge (vault 09/13, 2026-11-05): ~460 KB SVG, 366 paths, 6–7 fills, all 10 gates
passing versus Flat Logo's 3,982 paths / 2.5 MB failure.

## Pitfalls

- **`select.all` before trace** — otherwise "nothing selected"; this is the most common miss.
- **Params nesting** — trace settings go under `params.params`; unknown outer keys are rejected
  by name, and unknown inner keys print the accepted list.
- **Preset overfitting** — measured on AI art: Flat Logo 3,982 paths/2.5 MB, Auto Color 762
  paths/32 fills and keeps off-white paper, Black & White Logo 86 paths/1 fill (silhouette
  only), custom limited-palette params best. Presets are leads, not settings.
- **White rule** — `ignoreWhite` drops only true white; off-white paper survives unless you
  cut out first.
- **AI text** — diffusion erosion/shadow cannot be traced back; erase and retype.
- **Upscaling is not vectorising** — a blurred source stays blurred no matter the SVG.
