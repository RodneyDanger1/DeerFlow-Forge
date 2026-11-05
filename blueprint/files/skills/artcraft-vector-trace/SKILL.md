---
name: artcraft-vector-trace
description: "Use when a raster logo, badge, crest or illustration must become a clean SVG master plus a rendered check PNG: strict white cutout, VectorCraft imageTrace.make with Illustrator-compatible params, Expand, SVG export, print-pixel render. Triggers: vectorise this, trace logo, image to SVG, AI art to vector, clean vector art, trace for print, brand mark vector."
version: 1.1.0
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [artcraft, vectorcraft, trace, svg, logo, print, vectorize]
    related_skills: [ai-art-vectorize-vectorcraft, artcraft-command-catalog, apparel-print-master, brand-system]
---

# ArtCraft vector trace

Turns a raster image into a scalable vector: an SVG master plus a rendered check PNG — not a
mockup and not a provider print master (continue with `apparel-print-master` for that).

## When to use / not use

- Use for a flat logo, badge, crest or illustration that must become SVG.
- Use for an AI-generated mark that needs a crisp scalable version.
- Not for painterly texture that auto-trace turns into grain/banding — regenerate flatter/higher-res.
- Not for AI-rendered lettering: erase/retype (the production wrapper does this); never trace it.
- Not for photographic DTG art, stitch files or proofing.

## Required inputs

- Source raster (PNG/JPG/WebP) with rights and `identify` dimensions.
- Target: SVG master only, or SVG + print master; brand hex list if palette must stay on-brand.
- Wordmark/tagline text + font when AI text must be retyped.
- Print inches and provider `productId`/`area` when the trace feeds apparel.

## Exact commands (verified 2026-11-05)

```bash
cd /opt/pod-pipeline
VC=/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli
PY=/opt/pod-pipeline/.venv/bin/python
# Linux VPS only. From Windows: ssh -i ~/.ssh/id_ed25519_hostinger root@179.197.88.181 'cd /opt/pod-pipeline && bash -s' < script.sh
# Stop if SSH/key is unavailable: /opt/pod-pipeline and the CLIs do not exist on Windows.
```

**Step 1 — strict white cutout.** Every neutral white transparent (owner rule); cream/tan stays.
`prep_print_art` computes `usable = min(width_px - 2*margin, print_width_in*dpi)`, crops to
`subject_bbox`, scales the subject to `usable`, and centres it on `width_px × height_px`. The command
below assumes a **1024 px square** source; for a different source use its actual W×H and set
`--print-width-in` to `W/300` (or your intended print width). If the input is already a clean alpha
cutout, use `--mode alpha` instead of removing white again. `--mode alpha` on an opaque file refuses
`E_SUBJECT_FULL_FRAME`; `--mode white` refuses when there is no white background — use `--mode none`
deliberately for full-bleed art:

```bash
$PY -m tools.prep_print_art --input /tmp/art.png --output /tmp/art_cut.png \
  --width-px 1024 --height-px 1024 --dpi 300 --mode white --clean-rim \
  --min-component 60 --edge-clean-px 26 --edge-clean-lum 140 --margin-px 0 \
  --print-width-in 3.413333 --report-json /tmp/art_cut.json
```

**Step 2 — trace steps.** `imageTrace.make` takes `id|preset|savedPreset|enhanced|params|view|ids`;
the panel settings live inside `params`. `select.all` is mandatory:

```bash
cat > /tmp/trace-steps.json <<'JSON'
[{"command":"select.all"},
 {"command":"imageTrace.make","params":{"enhanced":false,"params":{
   "mode":"color","palette":"limited","colors":12,"paths":65,"corners":45,"noise":12,
   "ignoreWhite":true,"method":"abutting","fills":true,"strokes":false,
   "shapes":false,"autoGrouping":false,"gradients":false}}},
 {"command":"imageTrace.expand"}]
JSON
$VC run --in /tmp/art_cut.png --commands /tmp/trace-steps.json --export /tmp/art.svg
```

**Step 3 — render and inspect at print pixels:**

```bash
rsvg-convert -w 2400 -o /tmp/art_2400.png /tmp/art.svg
grep -c '<path' /tmp/art.svg; ls -l /tmp/art.svg; identify /tmp/art_2400.png
```

**Production wrapper** (cutout + erase AI text bands + retype + rsvg + 10 gates + previews). The
`--retype-json` file is **design-specific** — generate boxes on the original image, or omit it for
art with no text. The `<template>/<area>` form uses provider geometry; the `--canvas-width/height`
form is explicit:

```bash
$PY -m tools.craft_trace --input /tmp/art.png \
  --template pro_e4677535402b4eeb81 --area front_large --dpi 300 --print-width-in 8 \
  --colors 12 --paths 65 --corners 45 --noise 12 --palette limited --mode color \
  --retype-json /tmp/art_retype.json \
  --output /tmp/art_master.png --svg /tmp/art_master.svg \
  --report-json /tmp/art_master.json --preview-dir /tmp/previews_art
```

**Venv tracer alternative** for genuinely flat art (no VectorCraft, no retype/gates). Flags confirmed
by `python -m tools.vectorize_art --help`: `--canvas-width/--canvas-height`, `--cutout`,
`--binary-alpha`, `--report-json`:

```bash
$PY -m tools.vectorize_art --input /tmp/art.png --svg /tmp/art_vec.svg --output /tmp/art_vec.png \
  --canvas-width 2400 --canvas-height 3000 --dpi 300 --print-width-in 8 --cutout white \
  --binary-alpha --report-json /tmp/art_vec.json
```

**Coverage note:** `craft_trace` requires `coverage` 0.05–0.95, measured as **alpha fill of the art
frame** (`alpha.sum()/alpha.size`), not canvas occupancy. Provider-canvas margins do not change it; a
design that fills its own bounding box is refused. Inspect the report rather than guessing.

## Decision table

| Situation | Use | Why |
|---|---|---|
| Flat logo, clean edges | `imageTrace.make` custom params (or Flat Logo preset) | fast, clean |
| AI illustration / badge | `craft_trace` wrapper | cutout + retype + gates |
| Text in AI art | never trace; retype at mapped boxes | diffusion text is eroded |
| Painterly texture | regenerate flat/higher-res; raster master | trace turns texture into grain |
| Only SVG needed | standalone trace; path count/visual check | no print gates required |

## Workflow / states

`inspected → cutout → (text erased) → trace/expand → SVG → render at print px → retype → verify → master`.
A failed step must stop the chain; never export a failed gate.

1. `identify`; confirm ≥150 px per print inch; below that regenerate.
2. White cutout; cream lettering must survive.
3. Step JSON: `select.all`, `imageTrace.make`, `imageTrace.expand`; run on the cutout, never the
   untouched photo.
4. Render at print pixels; review 100 % + thumbnail for banding, key rims, lost thin strokes, grain.
5. If AI text exists, use `craft_trace` with a retype JSON; keep SVG + PNG masters.

## Acceptance gates

- `select.all` ran (missing it fails: `step 0 (imageTrace.make): nothing selected`).
- Wrapper: `ok:true` only when all ten pass (white residual ≤0.002, specks 0, coverage 0.05–0.95,
  DPI ≥300, canvas ≥1500², 2–40 fill colours, edge density ≥0.01, hard alpha ≥0.85, transparent
  corners, retyped text present). Exit 1 = gate fail, 2 = refusal.
- Standalone: 100–1500 paths is a typical logo band (advisory, not a gate); SVG <6 MB; 2–40 fills.
- Visual: no white paper edge, no magenta/key fringe, no grain inside flat fills.
- Text is live type or a proven retype overlay — never traced AI lettering.
- Colour compared against brand hex list; trace drift corrected deliberately.

## Refusals / failure modes

- No stitch-file engine (`.DST/.PES/.EXP` → `embroidery-art` + digitizer).
- No `--dry-run` (`vectorcraft-cli` rejects it); run on a copy and export new paths.
- No browser automation; a rendered PNG is the proof, a page screenshot is not.
- Never claim print quality from a screen render; mockups prove placement only.
- Below ~150 px per print inch → regenerate, do not upscale. Missing print width, text/font or rights
→ ask; do not invent them.
- A `--retype-json` with boxes from another design silently mislabels text; generate per design.
- Text-bearing art without a retype overlay → stop; a trace is not proof that text was handled.

## Worked examples

**1. Flat two-colour mark → SVG.** 1024² cutout, `colors:6, paths:65, corners:45, noise:8,
ignoreWhite:true` → `{"anchors":10,"colors":1,"id":4,"paths":1}`, 768-byte SVG. Quote the JSON, then
review the 2400 px render; the JSON is not print proof.

**2. AI badge → print-ready.** Pre-cutout, custom limited palette, SVG at print px, AI text erased
and retyped with FreeSansBold at mapped boxes. Measured Ridgeboundia record (vault 09/13): 410,571-byte
SVG, 281 paths, 6 fills, 10 gates passing; Flat Logo produced 3,982 paths / 2.5 MB and failed quality.

## Pitfalls

- **`select.all` before trace** — otherwise "nothing selected"; the most common miss.
- **Params nesting** — trace settings under `params.params`; unknown outer keys rejected by name.
- **`enhanced` is top-level** inside the command's `params` (e.g. `{"enhanced":false,"params":{...}}`),
  not inside the trace settings object.
- **Preset overfitting** — Flat Logo 3,982 paths/2.5 MB, Auto Color 762/32 keeps off-white, B&W 86/1
  silhouette only; custom limited-palette best. Presets are leads.
- **White rule** — `ignoreWhite` drops only true white; pre-cutout is mandatory.
- **AI text** — diffusion erosion/shadow cannot be traced back; erase/retype.
- **Upscaling is not vectorising** — a blurred source stays blurred in SVG.
- **`ignoreWhite` + Logo mode**: enclosed transparency can become white unless Ignore White is on
  (docs); verify holes at 100 %.


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
below 150 px per print inch; unlicensed asset; tool unavailable.

**Never**
Trace AI text; reuse another design's retype boxes; overwrite a master; ship `ok:false`; invent a
parameter; call a screen render print proof.

Deeper trace/SVG commands: **artcraft-command-atlas** (`vc-trace-addon.md`) and **artcraft-svg-production**.

## Sources & verification

- **VERIFIED:** `select.all` mandatory; nested trace params; `imageTrace.make`/`expand` JSON shapes;
  `document.export` supports nested `svg {decimals,…}`; `vectorize_art --help` flags; `craft_trace`
  gate names/thresholds; `text.fontList` 45 families; rsvg-convert 2.61.3; ImageMagick 7.1.2.
- **SCHEMA:** `/opt/craft/catalogues/vectorcraft-commands.json`; vault `17`.
- **DOCS:** `/opt/craft/artcraft-docs/image-trace-adjustments.md`, `image-trace-quality.md`; Adobe
  panel options https://helpx.adobe.com/illustrator/desktop/manage-objects/traces-mockups-symbols/image-trace-panel-options.html
