---
name: fourthwall-tee-vector
description: "Produce the exact Fourthwall Gildan Heavyweight Tee master for template pro_e4677535402b4eeb81 — front_large 15x18 in, 4500x5400 at 300 DPI, 8 in art width, Black, S–2XL with 2XL cost upcharges — through strict cutout, VectorCraft trace, retyped wordmark, provider compose and the zero-speck gate. Use when the user says tee master, shirt print file, Lost And Learning tee, front_large, DTG tee art, regenerate the tee, or check the tee before upload."
version: 1.0.0
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [fourthwall, dtg, gildan, tee, vector, print-master, retype, gates]
    triggers: [tee master, shirt print file, Lost And Learning tee, front_large, DTG tee art, regenerate the tee]
    related_skills: [apparel-print-master, artcraft-vector-trace, fourthwall-product-publish, merch-mockup-proof, brand-system]
---

# Fourthwall tee vector
One provider row, one canvas, one gate set; ends at a gated PNG plus report. Publishing is separate and owner-approved.

## When to use / when not
**Use for:** a new or re-proven master for `pro_e4677535402b4eeb81` / the live Lost And Learning
Tee; a replacement that needs exact tee geometry; any "check the tee before upload".

**Do not use for:** hoodies (`fourthwall-hoodie-vector`); beanies/embroidery
(`fourthwall-beanie-embroidery`, no DTG gates); generic apparel (`apparel-print-master`); stitch files (no digitizer).

## Required inputs
- Source art with rights: `data/ai-uploads/rb_logo.jpg` (1024×1024) for the current badge.
- The retype spec `config/retype-ridgeboundia.json` (included verbatim below).
- `config/fourthwall-template-details.json`, and owner approval for any store change.

## Product contract (read 2026-11-05: template row + live API)
| Field | Exact value |
|---|---|
| Template | Gildan Heavyweight T-Shirt `pro_e4677535402b4eeb81`, `DTG`, `supportsBackendRendering: true` |
| Region | `front_large` — 15×18 in; provider row 2250×2700 px at its native 150 DPI |
| Master canvas | 4500×5400 px @300 DPI (our 2× standard; `inches × 300`, never provider pixels) |
| Print width | 8 in = 2400 px, centred, aspect preserved |
| Garment / sizes | Black (35 colours exist); S, M, L, XL, 2XL |
| Price | S–XL $20.50 (cost $9.50); 2XL $22.50 (cost $11.50); margin $11.00 at every size |
| Live product | `lost-and-learning-tee-4`, id `5d40b2c7-5687-46bb-a0a0-75c19d4b9a9e`, AVAILABLE |
| Current master | `data/ai-uploads/rb_tee_craft.png` (4500×5400) + `rb_tee_craft.json`: 281 paths, 410,571 bytes, 6 fills |

The live product also exposes 3XL–5XL at +$2.00 cost/retail per step (API readback); this skill's set is S–2XL — no extra sizes without owner approval.

## Exact commands
```bash
cd /opt/pod-pipeline
PY=/opt/pod-pipeline/.venv/bin/python
```

Read the real row before touching art:

```bash
$PY - <<'PY'
import json
rows = json.load(open('/opt/pod-pipeline/config/fourthwall-template-details.json'))
r = next(x for x in rows if x['productId'] == 'pro_e4677535402b4eeb81')
print(r['name'], r['productionMethod'], r['supportsBackendRendering'], r['basePrice'], r['colorCount'])
print(json.dumps(r['areaGeometry']['front_large'], indent=1))
PY
```

Prep → trace → retype → compose → gate in one wrapper (stages internal):

```bash
$PY -m tools.craft_trace \
  --input data/ai-uploads/rb_logo.jpg \
  --template pro_e4677535402b4eeb81 --area front_large \
  --dpi 300 --print-width-in 8 \
  --retype-json config/retype-ridgeboundia.json \
  --output data/ai-uploads/rb_tee_craft_v2.png \
  --svg data/ai-uploads/rb_tee_craft_v2.svg \
  --report-json data/ai-uploads/rb_tee_craft_v2.json \
  --preview-dir data/ai-uploads/previews_rb_tee_craft_v2
```

Gate readback — every check plus the zero-speck rule:

```bash
$PY - <<'PY'
import json
d = json.load(open('data/ai-uploads/rb_tee_craft_v2.json'))
print('ok', d['ok'], 'paths', d['svg_paths'], 'canvas', d['canvas_px'], 'art', d['art_px'])
for k, v in d['checks'].items(): print(('PASS' if v['pass'] else 'FAIL'), k, v['value'])
PY
identify -format '%f %wx%h %x %y\n' data/ai-uploads/rb_tee_craft_v2.png
```

Included retype config (`config/retype-ridgeboundia.json`):

```json
[
  {"box": [250, 448, 1000, 570], "text": "RIDGEBOUNDIA", "font": "FreeSansBold.ttf", "fill": "#33614a", "stroke": "#d9caa4", "stroke_px": 6},
  {"box": [250, 580, 960, 660], "text": "MADE FOR THE LONG WAY ROUND", "font": "FreeSansBold.ttf", "fill": "#e8dcc0", "stroke": "#33614a", "stroke_px": 3},
  {"box": [110, 588, 250, 662], "text": "", "font": "FreeSansBold.ttf", "fill": "#000000", "stroke_px": 0}
]
```

Boxes are in 1024² source coordinates; `craft_trace` maps them through `subject_bbox`, offset and
scale for erasing and retyping — do not re-measure them per area.

Publish is a separate owner-approved step — `fourthwall-product-publish` owns the hidden create,
index wait, `runFourthwallSync`, whitelist SQL and HTTP matrix. The exact state flip is:

```bash
API=https://api.fourthwall.com/open-api/v1.0
curl -fsS -u "$FOURTHWALL_API_USERNAME:$FOURTHWALL_API_PASSWORD" -X PUT "$API/products/$NEW_ID/state" -H 'content-type: application/json' -d '{"state":"PUBLIC"}'
curl -fsS -u "$FOURTHWALL_API_USERNAME:$FOURTHWALL_API_PASSWORD" -X PUT "$API/products/5d40b2c7-5687-46bb-a0a0-75c19d4b9a9e/state" -H 'content-type: application/json' -d '{"state":"HIDDEN"}'
```

## Workflow
1. Confirm the row is DTG with `supportsBackendRendering`; the tool refuses otherwise.
2. Take geometry from `inchesWidth × dpi`: 15×18 in at 300 DPI = 4500×5400. Never 2250×2700.
3. Run `craft_trace` at 8 in with the retype JSON; never trace AI lettering.
4. Enforce `edge_specks == 0` (the live report's 4 is a stale pass), review both previews and the 100 % crop, then hand off and sample.

## Acceptance gates
- All ten checks pass with `ok: true` and exit 0; `edge_specks` is 0, not ≤10.
- `canvas_px` `[4500, 5400]`, `dpi` 300, `art_px` `[2400, 2400]`; `identify` shows 118.11 px/in.
- `white_residual_ratio` ≤0.002, coverage 0.05–0.95, 2–40 fill colours, edge density ≥0.01.
- `alpha_hard_edges` ≥0.85, transparent corners, `retyped_text_present` true and covered.
- Previews show no white fringe, ghost AI text, stray specks or key-colour rim; upload the PNG (Fourthwall rejects SVG/AI/PDF); 2XL retail = $11.50 + $11.00.

## Refusals
- Template not DTG, `supportsBackendRendering: false`, or `KNITTING` — stop.
- Area missing from `areaGeometry` — fetch the details file; never invent geometry.
- Any check failing, especially `edge_specks > 0` — not shippable; fix and re-run.
- Source under ~150 px per print inch on the raster route — regenerate, do not upscale.
- No product create/publish/hide/sync without owner approval; never upload the SVG; never "fix" an exported master with a global filter.

## Worked example
The shipped `rb_tee_craft.json` reports `ok: true`, canvas `[4500, 5400]`, `art_px`
`[2400, 2400]`, 281 paths, 410,571 bytes, 6 fill colours, coverage 0.4486, alpha hard edges
0.9973. Its `edge_specks` is **4 with `pass: true`** — evidence it predates the zero-speck gate,
not evidence of compliance. Re-run to `rb_tee_craft_v2.*`; under current code a 4-speck result
prints `FAIL edge_specks 4` and must be fixed before "all gates pass".

## Pitfalls
- **Stale gate pass.** `tools/craft_trace.py` now requires `specks == 0`; the live report's 4
  passed under the old ≤10 rule. Regenerate before claiming compliance.
- **Provider DPI trap / small region.** The row is 150 DPI (2250×2700), our master 300 (4500×5400); Fourthwall keeps full scale only inside the 11.5×13.8 in region, and 8 in is safe.
- **2XL pricing.** Each size step costs $2.00 more; retail must rise $2.00 to keep $11.00.
- **Source detail.** 1024² at 8 in is 128 px/in; fine only because the vector route re-renders
  at 2400 px. A raster route would be below Fourthwall's 150 DPI minimum.
- **Live master name.** Write `_v2` outputs; overwriting `rb_tee_craft.png` destroys the
  published art. Mockups prove placement only (`merch-mockup-proof`) — sample for colour/scale.

## Sources & verification
| Claim | Source | Status |
|---|---|---|
| Template id, DTG, front_large 15×18, native 2250×2700 @150, 35 colours, base $9.50 | `config/fourthwall-template-details.json`, VPS 2026-11-05 | VERIFIED |
| Canvas 4500×5400 @300, art 2400×2400, 281 paths, 6 fills, check values | `data/ai-uploads/rb_tee_craft.json` | VERIFIED |
| `edge_specks == 0` gate (report's 4 is stale) | `tools/craft_trace.py:241` | VERIFIED |
| `craft_trace` argparse surface (template/area/dpi/print-width/retype/svg/report/preview) | `tools/craft_trace.py:257-281` | SCHEMA |
| S–5XL prices/costs, $11.00 margin, 2XL $22.50 | `GET /open-api/v1.0/products/5d40b2c7-5687-46bb-a0a0-75c19d4b9a9e` | VERIFIED |
| 8 in tee width, Black, $11.00 margin; live product name/id/state | vault `04-CONSISTENCY-SPEC.md`, `03-PRODUCT-MANIFEST.md` + API readback | DOCS + VERIFIED |
| 150 DPI apparel minimum, PNG/JPG only, 15×18 large / 11.5×13.8 small regions | [Fourthwall artwork](https://help.fourthwall.com/create-and-sell-products/best-practices/artwork-best-practices), [file guidelines](https://help.fourthwall.com/create-and-sell-products/best-practices/design-file-guidelines-and-templates-for-merchandise/), [quality](https://help.fourthwall.com/create-and-sell-products/best-practices/product-quality-expectations) | DOCS |
