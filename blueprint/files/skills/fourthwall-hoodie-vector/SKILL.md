---
name: fourthwall-hoodie-vector
description: "Produce the exact Fourthwall Gildan Classic Hoodie master for template pro_gUu4CvXsRm-BxogjB89KzA — front 14x14 in, 4200x4200 at 300 DPI, 8.5 in art width, Black, S–2XL — with the same cutout, VectorCraft trace, retype, compose and zero-speck gate as the tee. Warns that the live rb_hoodie_v6.png is a raster with no gate-proven vector master, and separates mockup placement from print proof. Use when the user says hoodie master, hoodie print file, Lost And Learning hoodie, Gildan Classic Hoodie art, vectorise the hoodie, or check the hoodie before upload."
version: 1.0.0
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [fourthwall, dtg, gildan, hoodie, vector, print-master, raster-v6, gates]
    triggers: [hoodie master, hoodie print file, Lost And Learning hoodie, Gildan Classic Hoodie art, vectorise the hoodie]
    related_skills: [fourthwall-tee-vector, apparel-print-master, artcraft-vector-trace, fourthwall-product-publish, merch-mockup-proof]
---

# Fourthwall hoodie vector

Same art family as the tee, different provider row: 14×14 in front, 8.5 in width, 4200×4200 canvas. The live
master is still raster v6 — this skill produces and proves the vector; it does not pretend one exists.

## When to use / when not
**Use for:** a vector master for `pro_gUu4CvXsRm-BxogjB89KzA`; replacing the raster
`rb_hoodie_v6.png`; re-proving the hoodie after a gate or quality failure.

**Do not use for:** tees (`fourthwall-tee-vector`, 15×18 in, 8 in width); beanies/embroidery
(`fourthwall-beanie-embroidery`); the hoodie's 2×3 in wrist embroidery rows (not a print route).

## Required inputs
- Source art with rights: `data/ai-uploads/rb_logo.jpg` (1024×1024).
- The retype spec `config/retype-ridgeboundia.json` (the same file the tee uses); `config/fourthwall-template-details.json`; owner approval for any store change.

## Product contract (read 2026-11-05: template row + live API)

| Field | Exact value |
|---|---|
| Template | Gildan Classic Hoodie `pro_gUu4CvXsRm-BxogjB89KzA`, `DTG`, `supportsBackendRendering: true` |
| Region | `front` — 14×14 in; provider row 2100×2100 px at its native 150 DPI |
| Master canvas | 4200×4200 px @300 DPI (`inches × 300`, never provider pixels) |
| Print width | 8.5 in = 2550 px, centred, aspect preserved |
| Garment / sizes | Black (26 colours exist); S, M, L, XL, 2XL |
| Price | S–XL $33.20 (cost $22.20); 2XL $35.20 (cost $24.20); margin $11.00 at every size |
| Live product | `lost-and-learning-hoodie-3`, id `84305616-1446-490f-b022-adff79b9bdb4`, AVAILABLE |
| Current master | `rb_hoodie_v6.png` (4200×4200) + `rb_hoodie_v6.json` — raster, not vector |
| Vector status | **No craft_trace/gated hoodie master exists.** `rb_hoodie_final.json` (4,292 paths, 2,189,300 bytes) and `rb_hoodie_vec3.json` (295 paths, 417,194 bytes) are earlier SVG attempts, not 10-gate passes. |

The live product also exposes 3XL–5XL at +$2.00 cost/retail per step (API readback); this skill's set
is S–2XL. The row also carries EMBROIDERY wrist areas (2×3 in, 300 DPI, render false) — not this pipeline.

## Exact commands

```bash
cd /opt/pod-pipeline
PY=/opt/pod-pipeline/.venv/bin/python
```

Read the real row and confirm the region is `front`:

```bash
$PY - <<'PY'
import json
rows = json.load(open('/opt/pod-pipeline/config/fourthwall-template-details.json'))
r = next(x for x in rows if x['productId'] == 'pro_gUu4CvXsRm-BxogjB89KzA')
print(r['name'], r['productionMethod'], r['supportsBackendRendering'], r['basePrice'])
print(json.dumps(r['areaGeometry']['front'], indent=1))
PY
```

Vector route — prep → trace → retype → compose → gate:

```bash
$PY -m tools.craft_trace \
  --input data/ai-uploads/rb_logo.jpg \
  --template pro_gUu4CvXsRm-BxogjB89KzA --area front \
  --dpi 300 --print-width-in 8.5 \
  --retype-json config/retype-ridgeboundia.json \
  --output data/ai-uploads/rb_hoodie_craft_v1.png \
  --svg data/ai-uploads/rb_hoodie_craft_v1.svg \
  --report-json data/ai-uploads/rb_hoodie_craft_v1.json \
  --preview-dir data/ai-uploads/previews_rb_hoodie_craft_v1
```

Gate readback — a clean report is the only thing that earns "vector master":

```bash
$PY - <<'PY'
import json
d = json.load(open('data/ai-uploads/rb_hoodie_craft_v1.json'))
print('ok', d['ok'], 'paths', d['svg_paths'], 'canvas', d['canvas_px'], 'art', d['art_px'], 'warnings', d.get('warnings'))
for k, v in d['checks'].items(): print(('PASS' if v['pass'] else 'FAIL'), k, v['value'])
PY
identify -format '%f %wx%h %x %y\n' data/ai-uploads/rb_hoodie_craft_v1.png
```

Retype boxes are 1024² source coordinates; `craft_trace` maps them through `subject_bbox`, offset and
scale for erasing and retyping. Do not re-measure them per area.

Current raster v6 for comparison only: `rb_hoodie_v6.json` records `mode: white`, print width 8.5, `upscale_factor`
2.651, `coverage` 0.4261 and a softness warning. Reproduce with `tools.prep_print_art --mode white --print-width-in 8.5`,
never ship it as a vector.

Publish is owner-approved and owned by `fourthwall-product-publish`; create hidden, flip PUBLIC on
`$NEW_ID`, flip `84305616-1446-490f-b022-adff79b9bdb4` to HIDDEN, then run its index/sync/verify path.

## Workflow
1. Read the row: `front` is 14×14 in, DTG, renderable; anything else is a refusal.
2. Decide the route honestly: v6 is raster; a vector is done only when the 10-gate report passes.
3. Run `craft_trace` at 8.5 in with the retype JSON; keep `_v1` outputs until approved.
4. Check `canvas_px` `[4200, 4200]`, `art_px` `[2550, 2550]`, `dpi` 300, `edge_specks` 0.
5. Compare with v6 previews: if the glow art bands, stop, keep v6 and report it.
6. Review both previews and the 100 % crop, hand off to publish, order a sample.

## Acceptance gates
- All ten checks pass with `ok: true` and exit 0; `edge_specks` is 0, not ≤10.
- `canvas_px` `[4200, 4200]`, `dpi` 300, `art_px` `[2550, 2550]`; `identify` shows 118.11 px/in.
- `white_residual_ratio` ≤0.002, coverage 0.05–0.95, 2–40 fill colours, edge density ≥0.01.
- `alpha_hard_edges` ≥0.85, transparent corners, `retyped_text_present` true and covered.
- No report warnings; raster route only if `upscale_factor` ≤2.5.
- Previews show no fringe, ghost text, banding or key rim; upload the PNG, not the SVG; 2XL retail = $24.20 cost + $11.00 margin.

## Refusals
- Do not claim a gated vector hoodie master exists — none does; the live master is raster v6.
- Do not present `rb_hoodie_final.svg` (4,292 paths) or `rb_hoodie_vec3.svg` as production.
- Do not ship the raster v6 as "the vector"; do not overwrite it before approval.
- Area missing or template not DTG — fetch details, never invent geometry.
- Any gate failing, especially `edge_specks > 0` — fix and re-run; never edit the report; no product create/publish/hide/sync without owner approval; a mockup is not print proof.

## Worked example
The live v6 report: canvas `[4200, 4200]`, `print_width_in` 8.5, `usable_width_px` 2550,
`subject_px` `[962, 913]`, `upscale_factor` 2.651, coverage 0.4261, warnings `["source upscaled
2.65x (gate 2.5x): glow art tolerates this, fine line art will not..."]`. That is a raster master
with a known softness warning, not a vector. The earlier attempts (4,292 paths / 2,189,300 bytes;
295 paths / 417,194 bytes) carry no 10-gate `checks` block. A new `craft_trace` run is expected near
the tee's 281 paths, canvas `[4200, 4200]`, art `[2550, 2550]` — verify, do not assume.

## Pitfalls
- **Not-yet-vectored.** No craft_trace report exists for the hoodie; saying "vector master" today
  is false. Ship v6 or produce a gated `_craft_v1`.
- **4,292 paths is not a win.** That is the Flat Logo overfit on AI texture (2.19 MB); the tee's
  281-path run is the quality bar.
- **Soft source.** 1024² at 8.5 in is 120 px/in and v6 upscales 2.651×; the vector route avoids
  pixel upscale but inherits soft edges — regenerate the source if the trace is mushy.
- **Glow art bands.** The v6 PNG has 133,226 unique opaque colours; a 12-colour trace may band.
  Compare 100 % crops against v6 before replacing anything.
- **8.5 vs 8.** Same art family, different width; re-run the tool, never rescale the exported PNG.
- **Mockup ≠ proof.** Mockups prove placement/cut-off only (`merch-mockup-proof`); sample for colour and scale.

## Sources & verification

| Claim | Source | Status |
|---|---|---|
| Template id, DTG, front 14×14, native 2100×2100 @150, 26 colours, base $22.20 | `config/fourthwall-template-details.json`, VPS 2026-11-05 | VERIFIED |
| v6 raster: canvas 4200×4200, 8.5 in, 2550 px, upscale 2.651, warning | `data/ai-uploads/rb_hoodie_v6.json` | VERIFIED |
| No 10-gate hoodie vector; 4,292-path and 295-path attempts | `rb_hoodie_final.json`, `rb_hoodie_vec3.json` + file listing | VERIFIED |
| `craft_trace` argparse surface (template/area/dpi/print-width/retype/svg/report/preview) | `tools/craft_trace.py:257-281` | SCHEMA |
| 133,226 unique opaque colours in v6 (raster, not flat vector) | PIL count on `rb_hoodie_v6.png` | VERIFIED |
| S–5XL prices/costs, $11.00 margin, 2XL $35.20 | `GET /open-api/v1.0/products/84305616-1446-490f-b022-adff79b9bdb4` | VERIFIED |
| 8.5 in hoodie width, Black, $11.00 margin | vault `04-CONSISTENCY-SPEC.md` | DOCS |
| Live product name/id/state | vault `03-PRODUCT-MANIFEST.md` + API readback | DOCS + VERIFIED |
| 150 DPI apparel minimum, PNG/JPG only, mockup vs sample | [Fourthwall artwork](https://help.fourthwall.com/create-and-sell-products/best-practices/artwork-best-practices), [quality](https://help.fourthwall.com/create-and-sell-products/best-practices/product-quality-expectations) | DOCS |
