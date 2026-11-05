---
name: apparel-print-master
description: Build a provider-ready DTG print master at 300 DPI on the exact Fourthwall area geometry — trace or raster route, retype AI text, compose, run the 10 gates, then hand off to publish. Use when the user says put this on a shirt, make a tee/hoodie design, prepare a print master, replace the product art, print this on apparel, or check the print file before upload.
---

# Apparel print master

Produces the file that goes to the print provider: correct canvas, 300 DPI, transparent
background, verified art. It consumes a raster or the SVG from `artcraft-vector-trace` and ends
at a gated PNG plus JSON report. Publishing is a separate, owner-approved step.

## When to use

- A design must go on a tee, hoodie or other DTG garment.
- An existing product's art must be replaced with a new master.
- A master is suspect (white fringe, blur, ghost text) and needs re-proving.
- You need provider geometry exactness (area inches × 300 DPI), not a guess.

## When not to use

- Embroidery/knit — read `embroidery-art`; KNITTING templates are refused by the tools.
- Embroidered or woven labels — no stitch engine exists here.
- Web/social/shipping layouts — different skills.
- Painterly art with no vector-worthy silhouette: the raster route is allowed, but never
  upload a failed gate.

## Required inputs

- Art file (raster or SVG) with rights, and a retype JSON if AI text is present.
- Fourthwall `productTemplateId` and region (`front_large`, `front`, `back`, …).
- Print width in inches (team standard: tee 8 in, hoodie 8.5 in) and garment colour.
- The provider details file: `/opt/pod-pipeline/config/fourthwall-template-details.json`.
- Owner approval before any store change.

## Exact commands

```bash
cd /opt/pod-pipeline
PY=/opt/pod-pipeline/.venv/bin/python
```

Vector route (current standard — cutout, retype, trace, render, 10 gates):

```bash
$PY -m tools.craft_trace \
  --input data/ai-uploads/badge.png \
  --template pro_e4677535402b4eeb81 --area front_large --dpi 300 --print-width-in 8 \
  --retype-json config/retype-ridgeboundia.json \
  --output data/ai-uploads/badge_tee.png --svg data/ai-uploads/badge_tee.svg \
  --report-json data/ai-uploads/badge_tee.json --preview-dir data/ai-uploads/previews_badge_tee
```

Raster fallback for painterly art that must not be traced:

```bash
$PY -m tools.prep_print_art --input data/ai-uploads/art.png \
  --template pro_e4677535402b4eeb81 --area front_large --dpi 300 \
  --mode white --clean-rim --min-component 60 --edge-clean-px 26 --edge-clean-lum 140 \
  --print-width-in 8 --saturation 1.18 --brightness 1.04 --sharpen 55 \
  --output data/ai-uploads/art_tee.png --report-json data/ai-uploads/art_tee.json \
  --preview-dir data/ai-uploads/previews_art_tee
```

Flat logo without retype: `tools.vectorize_art` (full command in `artcraft-vector-trace`).

Verify the master and read the gate report:

```bash
identify -format '%f %wx%h %x %y\n' data/ai-uploads/badge_tee.png
$PY -c "import json; d=json.load(open('data/ai-uploads/badge_tee.json')); \
print('ok:', d['ok']); print(json.dumps(d['checks'], indent=1))"
```

## Workflow

1. Read the template row; confirm `supportsBackendRendering` and production method is not `KNITTING`.
2. Take the area geometry (`inchesWidth`, `inchesHeight`, `pixelsWidth`, `pixelsHeight`, `dpi`)
   — never guess canvas pixels.
3. Choose the route: vector for flat/AI illustration with a silhouette; raster for painterly.
4. Ensure every white is transparent; keep cream/tan lettering.
5. Erase AI text bands and retype with a real font at mapped boxes (`--retype-json`).
6. Compose the art centred on the provider canvas at the print width, aspect preserved.
7. Run the gates; on failure fix the cause and re-run — never hand-edit the report.
8. Review the black and white previews and the 100 % crop with your own eyes, then hand off
   to publish (below) and order a sample to prove colour/scale.

## Acceptance gates

All ten checks must pass (`ok: true`, exit 0; exit 1 = gate failure, exit 2 = refusal):

- white residual ≤0.002, zero specks ≥150 px, coverage 0.05–0.95, DPI ≥300,
  canvas ≥1500×1500, 2–40 vector fill colours, edge density ≥0.01,
  binary-alpha share ≥0.85, transparent corners, retyped text present.
- Canvas equals `round(inches × 300)` from the provider row; print width equals the brief.
- `identify` shows the expected pixel size and 118.11 px/cm (300 DPI).
- Previews rendered on black and white backgrounds; no fringe, ghost text or stray white.
- Raster route: `upscale_factor` ≤2.5 and no warning in the report.

## Refusal conditions

- Unrenderable template or `KNITTING` production method — the tools exit 2; do not work around.
- Area not in `areaGeometry` — fetch/enrich the details file; never invent geometry.
- Source below ~150 px per print inch — regenerate the art; upscaling is not a fix.
- Any gate failing — not shippable. Report the failing values and stop.
- No dry-run flag exists; treat every export as real and keep the source.
- Mockups prove placement/cut-off only; never present one as print proof.
- No store change (create/publish/hide/sync) without explicit owner approval.

## Approval binding

- Compute and record the master’s SHA-256 **before** requesting approval: artifact hash, canvas, DPI,
  template/area, print width and the gate report hash.
- Bind the owner’s approval to that exact SHA-256. A stale approval (different bytes), a reused
  approval for another product, or an approval without the gate report is refused by name.
- Re-run the gates after any re-export or retouch. If the bytes change, the approval is void.
- The approval is for print/publish only; it is not evidence that the visual result is correct.

## Worked examples

**1. Tee front_large.** Provider row says 15×18 in, so the canvas is 4500×5400 px at 300 DPI.
Print width 8 in → art 2400 px wide, centred; the rest of the canvas stays transparent. Run
`tools.craft_trace` with `--template … --area front_large --print-width-in 8`, then confirm the
report's `canvas_px` is `[4500, 5400]` and every check passes.

**2. Hoodie.** Same master family, 8.5 in print width (2550 px at 300 DPI) from the same source
art, so the collection keeps one art width ratio. Re-run the tool; do not rescale the exported
PNG after the fact.

**3. Publish handoff (owner-approved).** The storefront client
`pod_pipeline/fourthwall.py` exposes: `POST /open-api/v1.0/media/upload-url`,
`POST /open-api/v1.0/media/images`, `POST /open-api/v1.0/products`,
`PUT /open-api/v1.0/products/{id}/state` (`PUBLIC`/`HIDDEN`), `GET /open-api/v1.0/products/{id}`.
Sequence: create hidden → publish `PUBLIC` → hide every older version → wait for the storefront
index → sync → activate the live ids, archive the rest → verify `/shop` and each product page 200.

## Pitfalls

- **Coverage is measured on the rendered art, not the canvas.** A flat full-bleed square test
  mark measured 0.9806 and edge density 0.007 → 8/10 checks, `ok:false`. The gates are strict;
  a silhouette-less rectangle is not a valid print master.
- **Coordinate mapping**: `prep_print_art` crops to the subject bbox and re-centres, so boxes
  measured on the original must be transformed for erasing and retyping. `craft_trace` does
  this internally; hand-rolled steps must use the report's `subject_bbox` and canvas offset.
- **`select.all` and params nesting** still apply when you build trace steps yourself.
- **AI text** is erased/retyped, never traced.
- **White rule**: every white transparent; `white-flood` is the exception when enclosed whites
  (snow, a white letter) must survive.
- **Do not upload on a failed gate**, and do not "fix" a master with a global filter after export.
