---
name: fourthwall-beanie-embroidery
description: "Produce the exact Fourthwall Otto Knit Beanie embroidery master for template pro_12abde5f29c34ffbb2 — embroidery_front 5x1.75 in, 1500x525 at 300 DPI, wordmark lockup with a measured 0.454 in cap, ≤6 thread colours, strokes ≥0.05 in and caps ≥0.3 in. Includes the font/render/measure/export steps, the real template-row check (note: 4x4 in chest embroidery rows exist on other products, not this one), and the hard rule that vector art is NOT a .DST/.PES stitch file. Use when the user says beanie master, beanie embroidery, hat embroidery art, wordmark lockup, embroidery file, DST/PES"
version: 1.0.0
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [fourthwall, embroidery, otto, beanie, wordmark, thread-colours, stitch-limits]
    triggers: [beanie master, beanie embroidery, hat embroidery art, wordmark lockup, embroidery file, DST, PES]
    related_skills: [embroidery-art, brand-system, fourthwall-product-publish, merch-mockup-proof, fourthwall-tee-vector]
---

# Fourthwall beanie embroidery
One 5×1.75 in embroidery row, one stitch-legal wordmark, one set of measured limits. Output is art
(PNG at real size) plus constraints — never a machine stitch file.

## When to use / when not
**Use for:** a beanie lockup for `pro_12abde5f29c34ffbb2`; re-proving the shipped wordmark; checking
caps/strokes/thread colours before upload; any request for "the beanie art".

**Do not use for:** DTG tees/hoodies (`fourthwall-tee-vector`, `fourthwall-hoodie-vector`); a 4×4 in chest embroidery on apparel (other rows); a `.DST/.PES/.EXP` order (no digitizer).

## Required inputs
- Brand wordmark `RIDGEBOUNDIA` (or a simplified icon + short word) and the garment colour (Black).
- The font `/usr/share/fonts/truetype/freefont/FreeSansBold.ttf`, `config/fourthwall-template-details.json`, and owner approval for any store change.

## Product contract (read 2026-11-05: template row + live API)
| Field | Exact value |
|---|---|
| Template | Otto Knit Beanie `pro_12abde5f29c34ffbb2`, `productionMethod: EMBROIDERY`, `supportsBackendRendering: true` |
| Region | `embroidery_front` — 5×1.75 in; 1500×525 px at 300 DPI (provider native 300) |
| Areas | Only `Front` exists on this template — there is **no** 4×4 in chest row on the beanie |
| Garment / sizes | Black (6 colours: Black, Navy, Red, Dark green, Gray, White); one size fits most |
| Price / live product | $24.29 flat (cost $13.29, margin $11.00); `lost-and-learning-beanie-3`, id `6e655114-1d1d-40fb-977c-d413f8ee54bf`, AVAILABLE |
| Current master | `rb_beanie_v3.png` (1500×525) + `rb_beanie_v3.json`: mode alpha, print width 4.9 in, subject 1434×144, coverage 0.1341, no warnings |
| Lockup | `RIDGEBOUNDIA`, FreeSansBold 44 pt, `#EFE6CF`, **1 thread colour**, cap 0.454 in measured |

The 4×4 in EMBROIDERY chest row is real on other templates (e.g. `pro_VI45gehfQJqavT6bllGWeQ`
Lane Seven Urban Hoodie: `embroidery_chest_center`/`_left`, 4×4 in, 1200×1200 @300) — not a beanie row.

## Exact commands

```bash
cd /opt/pod-pipeline
PY=/opt/pod-pipeline/.venv/bin/python
VC=/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli
FONT=/usr/share/fonts/truetype/freefont/FreeSansBold.ttf
```

Read the real row and prove the 4×4 chest rows belong to other products:

```bash
$PY - <<'PY'
import json
rows = json.load(open('/opt/pod-pipeline/config/fourthwall-template-details.json'))
r = next(x for x in rows if x['productId'] == 'pro_12abde5f29c34ffbb2')
print(r['name'], r['productionMethod'], r['supportsBackendRendering'], r['colors'])
print(json.dumps(r['areaGeometry'], indent=1))
for x in rows:
    for k, v in (x.get('areaGeometry') or {}).items():
        if v.get('productionMethod') == 'EMBROIDERY' and k.startswith('embroidery_chest'):
            print(x['productId'], x['name'], k, v['inchesWidth'], 'x', v['inchesHeight'])
PY
```

Render the wordmark at final size (44 pt, 5×1.75 in document, 300 ppi export):

```bash
cat > /tmp/beanie_lockup.json <<'JSON'
[{"command":"file.new","params":{"width":"5 in","height":"1.75 in","colorMode":"rgb","backgroundContents":"transparent"}},
 {"command":"text.create","params":{"x":20,"y":80,"text":"RIDGEBOUNDIA","font":"FreeSans","style":"Bold","size":44,"color":"#EFE6CF"}},
 {"command":"document.export","params":{"path":"/tmp/beanie_wordmark.png","format":"png","ppi":300}}]
JSON
$VC run --commands /tmp/beanie_lockup.json
identify -format '%f %wx%h\n' /tmp/beanie_wordmark.png    # 1500x525
```

Measure cap height and the thinnest stem (render `H` and `I` at the same size):

```bash
magick -background none -density 300 -fill '#EFE6CF' -font "$FONT" -pointsize 44 label:'H' -trim +repage /tmp/cap_H.png
magick -background none -density 300 -fill '#EFE6CF' -font "$FONT" -pointsize 44 label:'I' -trim +repage /tmp/stem_I.png
identify -format '%f h=%h w=%w\n' /tmp/cap_H.png /tmp/stem_I.png   # H height = cap, I width = stem; ÷300 = in
```

Count design colours and the ink box (antialias shades collapse to one thread colour):

```bash
$PY - <<'PY'
from PIL import Image
from collections import Counter
im = Image.open('/tmp/beanie_wordmark.png').convert('RGBA')
c = Counter(p[:3] for p in im.getdata() if p[3] > 200)
xs = [i % im.width for i, p in enumerate(im.getdata()) if p[3] > 128]
ys = [i // im.width for i, p in enumerate(im.getdata()) if p[3] > 128]
print('design_colours', len(c), c.most_common(4), 'ink_px', max(xs)-min(xs)+1, max(ys)-min(ys)+1)
PY
```

Compose on the provider canvas (real size, transparent, geometry from the row):

```bash
$PY -m tools.prep_print_art --input /tmp/beanie_wordmark.png \
  --template pro_12abde5f29c34ffbb2 --area embroidery_front --dpi 300 \
  --mode alpha --print-width-in 4.9 \
  --output data/ai-uploads/rb_beanie_v4.png \
  --report-json data/ai-uploads/rb_beanie_v4.json \
  --preview-dir data/ai-uploads/previews_rb_beanie_v4
```

Publish is owner-approved and owned by `fourthwall-product-publish`; create hidden, flip PUBLIC on `$NEW_ID`, flip `6e655114-1d1d-40fb-977c-d413f8ee54bf` to HIDDEN, then run its index/sync/verify path.

## Workflow
1. Decide the lockup first: wordmark only; a full badge at 1.75 in cannot meet 0.3 in caps.
2. Read the row; confirm `embroidery_front` 5×1.75 and that no chest row exists here.
3. Render 44 pt FreeSansBold, export 1500×525 PNG at 300 ppi on transparent.
4. Measure cap (≥0.3), stroke (≥0.05), colours (≤6), spacing (≥0.05) — record the numbers.
5. Compose with `prep_print_art --mode alpha` at 4.9 in, review at real size, label the file **art**, then hand off and sample.

## Acceptance gates
- Canvas exactly 1500×525 at 300 DPI, transparent background.
- Capital height ≥0.3 in (90 px); shipped lockup measures 0.454 in (136 px).
- Lowercase ≥0.25 in (75 px) if used; shape thickness ≥0.05 in (15 px); spacing ≥0.05 in.
- ≤6 thread colours; shipped art has exactly 1 (`#EFE6CF`); solid fills only.
- No gradients, photographs, shadows or semi-transparent fills; outline font.
- Real-size preview reviewed at 100 %; text legible on Black; the handoff says **art**, not stitch file; stitch count/thread match needs a sample/digitizer.

## Refusals
- No `.DST/.PES/.EXP` writer or digitizer in this environment — vector art is **not** a stitch file.
- Fourthwall accepts PNG/JPG and digitizes the uploaded art (its docs warn background graphics may be digitized); a machine stitch file needs a digitizer/provider.
- No 4×4 in chest row on the beanie — do not import a row from another product.
- The full badge at 1.75 in is refused (the attempt is 468 px = 1.56 in tall with 3 colours).
- No product create/publish/hide/sync without owner approval; never upload the SVG; never claim thread match from hex alone; no stitch-quality promise from a screen.

## Worked example
The shipped `rb_beanie_wordmark.png` is one colour (`#EFE6CF`, 97,433 opaque px), ink box 1425×143 px
= 4.75×0.477 in at 300 DPI. The 143 px box exceeds the 0.454 in (136 px) cap recorded in the vault, so
measure the strokeless `H` rather than the trimmed box; FreeSansBold's `sCapHeight` is 729/1000, so 44 pt
gives 0.4455 in geometrically, and all three clear 0.3 in. `rb_beanie_v3.json` composes it at 1500×525,
print width 4.9 in, coverage 0.1341.

## Pitfalls
- **Cap height ≠ font size, and the ink box can exceed the cap.** Measure a strokeless `H`; 44 pt lands at ~0.45 in (143 px boxes ≠ cap).
- **Full badge at 1.75 in** is the classic failure: caps cannot shrink below 0.3 in.
- **Render 4× then downsample; one colour per element.** Gradients/shadows cannot be stitched; Fourthwall's palette has 15 threads and a 6-colour cap.
- **Beanie ≠ 4×4; art ≠ stitch file.** The 15,000-stitch ceiling is for standard 4×4 areas, 5×1.75 is smaller, and a digitizer still has to produce the machine file.

## Sources & verification
| Claim | Source | Status |
|---|---|---|
| Template id, EMBROIDERY, embroidery_front 5×1.75, 1500×525 @300, 6 colours, $13.29 | `config/fourthwall-template-details.json`, VPS 2026-11-05 | VERIFIED |
| v3 master: 1500×525, print width 4.9, subject 1434×144, coverage 0.1341, no warnings | `data/ai-uploads/rb_beanie_v3.json` | VERIFIED |
| `prep_print_art --mode alpha` surface; VectorCraft `text.create` 44 pt / `document.export` ppi 300 | `tools/prep_print_art.py` MODES + the two command JSONs | SCHEMA |
| Wordmark 1 opaque colour `#EFE6CF`, ink box 1425×143 px | PIL count on `rb_beanie_wordmark.png` | VERIFIED |
| Cap 0.454 in measured; FreeSansBold capHeight 729/1000 → 0.4455 in at 44 pt | vault `04-CONSISTENCY-SPEC.md` + `OS/2.sCapHeight` in `FreeSansBold.ttf` | DOCS + VERIFIED |
| 4×4 chest rows exist on other products, not the beanie | details scan (`embroidery_chest_*`) | VERIFIED |
| Live product name/id/state, $24.29 flat | vault `03-PRODUCT-MANIFEST.md` + API readback | DOCS + VERIFIED |
| 6 thread colours, 0.05 in stroke, 0.3 in caps, 0.25 in lowercase, 15,000 stitches / 4×4 | [Fourthwall embroidery best practices](https://help.fourthwall.com/create-and-sell-products/best-practices/embroidery-best-practices), [design file guidelines](https://help.fourthwall.com/create-and-sell-products/best-practices/design-file-guidelines-and-templates-for-merchandise/) | DOCS |
