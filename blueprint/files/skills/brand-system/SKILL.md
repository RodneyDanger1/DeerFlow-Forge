---
name: brand-system
description: "Use to assemble a usable brand kit from a mark and palette: four lockups, palette hex + print equivalents, type with licences, clear-space/min-size rules, application rules, and stored masters (SVG/PNG/PDF). Triggers: brand kit, brand guidelines, logo variants, colour palette, typography system, brand assets, make the collection consistent."
version: 1.2.0
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [branding, logo, palette, typography, brand-kit, print, design-system]
    related_skills: [ad-creative, web-banner, shipping-card-tag, artcraft-vector-trace, apparel-print-master]
---

# Brand system

Turns a mark and a colour idea into a kit another person can apply without asking questions:
master files plus a short rules document, not a mood board.

## When to use / not use

- Use when a new brand/store needs its first complete asset set.
- Use when the collection drifts (hues, widths, treatments) and needs one source of truth.
- Use when downstream work (ads, banners, cards, garment prints) needs approved assets/rules.
- Not for one-off ad/banner production (those consume this kit), trademark clearance, garment
  masters (`apparel-print-master`) or embroidery lockups (`embroidery-art`).

## Required inputs

- Brand name, positioning line, and the mark (vector preferred; raster acceptable with rights).
- Palette: existing hex list or references to derive from.
- Type: licensed fonts installed on the machine (`text.fontList`), or a deliberate open-family choice.
- Usage contexts: storefront, social, print, embroidery, packaging.
- Master storage: vault `30-reference/art-learning/assets/` + repo `blueprint/files/`; approver.
- Ask if the palette source, mark rights or approver is missing; never invent brand values.

## Exact commands (verified 2026-11-05)

```bash
cd /opt/pod-pipeline
VC=/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli
PC=/opt/craft/photocraft/photocraft-0.20.2-linux-x86_64/bin/photocraft-cli
PY=/opt/pod-pipeline/.venv/bin/python
# Linux VPS only. From Windows: ssh -i ~/.ssh/id_ed25519_hostinger root@179.197.88.181 'cd /opt/pod-pipeline && bash -s' < script.sh
# Stop if SSH/key is unavailable: /opt/pod-pipeline and the CLIs do not exist on Windows.
```

**1) Vectorise a flat mark** (full workflow in `artcraft-vector-trace`):

```bash
$PY -m tools.prep_print_art --input /tmp/logo.png --output /tmp/logo_cut.png \
  --width-px 1200 --height-px 1200 --dpi 300 --mode white --clean-rim --min-component 60 \
  --print-width-in 4 --report-json /tmp/logo_cut.json
cat > /tmp/logo-steps.json <<'JSON'
[{"command":"select.all"},
 {"command":"imageTrace.make","params":{"enhanced":false,"params":{"mode":"color","palette":"limited","colors":8,
   "paths":70,"corners":45,"noise":12,"ignoreWhite":true,"method":"abutting",
   "fills":true,"strokes":false,"shapes":false,"autoGrouping":false,"gradients":false}}},
 {"command":"imageTrace.expand"}]
JSON
$VC run --in /tmp/logo_cut.png --commands /tmp/logo-steps.json --export /tmp/logo.svg
```

**2) Build a brand sheet and export web sizes + PDF.** A 1200×1200 px document (72 ppi ⇒ 1200 pt) exported at ppi 72
gives 1200 px; ppi 144 gives 2400 px; ppi 216 gives 3600 px (pixels = points ÷ 72 × ppi). `file.place`
SVG physical sizing is not verified; use `rect` for exact placement:

```bash
cat > /tmp/sheet.json <<'JSON'
[{"command":"file.new","params":{"width":1200,"height":1200,"units":"Pixels","colorMode":"rgb","backgroundContents":"white"}},
 {"command":"file.place","params":{"path":"/tmp/logo.svg","rect":[80,80,1040,800]}},
 {"command":"text.create","params":{"x":80,"y":1020,"text":"RIDGEBOUNDIA","font":"FreeSans","style":"Bold","size":64,"color":"#33614a"}},
 {"command":"document.export","params":{"path":"/tmp/brand_sheet.svg","format":"svg","svg":{"decimals":3}}},
 {"command":"document.export","params":{"path":"/tmp/brand_sheet.pdf","format":"pdf"}},
 {"command":"document.export","params":{"path":"/tmp/brand_sheet@1x.png","format":"png","ppi":72}},
 {"command":"document.export","params":{"path":"/tmp/brand_sheet@2x.png","format":"png","ppi":144}},
 {"command":"document.export","params":{"path":"/tmp/brand_sheet@3x.png","format":"png","ppi":216}}]
JSON
$VC run --commands /tmp/sheet.json
identify -format '%f %wx%h %x %y\n' /tmp/brand_sheet@1x.png /tmp/brand_sheet@2x.png /tmp/brand_sheet@3x.png
```

**3) Monochrome raster variant and palette chips:**

```bash
# create the raster working copy the next command needs (SVG -> PNG at 1200 px)
magick -background none /tmp/logo.svg -resize 1200x1200 /tmp/logo_1200.png
$PC run /tmp/logo_1200.png --cmd image.adjustments.desaturate --out /tmp/logo_mono.png
magick -size 240x240 xc:'#33614a' /tmp/chip_33614a.png
magick -size 240x240 xc:'#d9caa4' /tmp/chip_d9caa4.png
```

**4) Available families** (choose only installed fonts or ship the licensed file):

```bash
$VC run --cmd text.fontList
```

**5) Contrast check** for each text/background pair (WCAG relative luminance):

```python
def lum(h):
    c=[int(h[i:i+2],16)/255 for i in (1,3,5)]
    c=[x/12.92 if x<=0.04045 else ((x+0.055)/1.055)**2.4 for x in c]
    return 0.2126*c[0]+0.7152*c[1]+0.0722*c[2]
def ratio(a,b):
    la,lb=sorted([lum(a),lum(b)], reverse=True)
    return (la+0.05)/(lb+0.05)
```

## Workflow / state machine

`audit → palette → lockups → clear space/min sizes → type → application rules → export masters → store + index`.

1. Audit what exists: raster marks, old hex values, fonts actually installed (`text.fontList`).
2. Fix the palette first: name every colour, record hex, agree print equivalents with the vendor.
3. Produce four lockups: primary, inverse (dark ground image + primary lockup; backgroundContents is
   only transparent|white), monochrome, icon/square.
4. Set clear space (fixed fraction of the mark) and minimum sizes in px and inches; measure them.
5. Kit document must include: palette (name/hex/print equivalent), type (family/weights/licence/
   fallback), lockup files, clear space, minimum sizes, application rules, contrast results.
5. Choose type: one display + one text family; record licence and fallbacks.
6. Write application rules: garment print width, white-transparent rule, vector rule, embroidery limits.
7. Export masters: SVG (working), PNG 1×/2×/3×, PDF for print.
8. Store under `30-reference/art-learning/assets/brand/` and `assets/print-masters/`; index filenames.
9. Verify every master opens and renders; audit every palette colour appears in the table.

## Acceptance gates

- Each lockup opens/renders at 1×; SVG has real paths, not an embedded raster.
- Palette table names every colour with hex; no art colour absent from the table.
- Type table lists family, weights, licence source and fallback.
- Clear space and minimum sizes are stated with numbers.
- Print rules include every-white-transparent, 300 DPI masters, embroidery exception.
- Masters stored at the agreed paths and referenced by filename in the kit document.
- Contrast passes AA for intended text/background pairs.
- Downstream skills can use the kit without re-deriving colours or type.

## Refusals / failure modes

- Unlicensed fonts/stock art — refuse to bake them in; use installed open families or obtain a licence.
- Trademark/naming clearance — out of scope; never imply legal clearance.
- No invented hex values/"brand colours" without a source; derive and record.
- No browser automation — prove web usage from exported PNGs, not a live page.
- Mockups/sheets prove layout only; print colour needs a physical proof.
- `file.place` physical-size rule can make a large raster overflow — use `rect` or pre-resize.
- A missing font falls back to Source Sans 3 with a warning; outlining captures the fallback — check
  `text.fonts` status `exact` before outlining or export a licensed/embedded font.

## Brand asset inventory (current)

- Vault: `30-reference/art-learning/assets/brand/README.md` (inventory; masters not all produced),
  `assets/print-masters/README.md` (tee/hoodie/beanie/whale masters + reports, with gaps).
- Server masters: `/opt/pod-pipeline/data/ai-uploads/` (e.g. `rb_tee_craft.png/.svg/.json`).
- Known missing: vector logo variants (primary/inverse/mono/icon), palette file, type licence table,
  print masters index. Produce them; do not claim a complete kit before they exist.

## Worked examples

**1. Four-lockup logo set.** Trace a flat PNG to `logo.svg` (8 colours, 70 paths, 45 corners); export
primary; make inverse on a dark ground; monochrome via `image.adjustments.desaturate` (raster) or a
B&W trace (vector); crop the icon square. Record minimum sizes: 120 px web, 0.75 in print, 1.5 in
embroidery context.

**2. Palette + type sheet.** Six named colours with hex; two families (display + text); sheet exported
at ppi 72/144/216 (1200/2400/3600 px) plus PDF; chips per colour. Rules state tee 8 in / hoodie 8.5 in
and the white-transparent rule so `apparel-print-master` needs no decisions.

## Pitfalls

- **Traced text is not a brand asset** — retype the wordmark.
- **Off-white paper survives `ignoreWhite`**; cut out before tracing.
- **Colour drift** between traced SVG and raster exports is normal; correct deliberately, record hex.
- **RGB vs CMYK**: screen hex is not a press colour; agree print equivalents with the vendor.
- **One SVG master per lockup**; everything else exports from it.
- **Font availability differs**; record fallbacks or embed/outline (check exact status first).
- **ppi scaling**: pixels = points ÷ 72 × ppi; a 1200 pt doc at ppi 72 = 1200 px, at 144 = 2400 px.


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

## Sources & verification

- **VERIFIED:** `text.fontList` returned 45 families; `document.export` accepts nested
  `svg {decimals,…}` and `pdf`; ppi scaling (8×10 in at 300 → 2400×3000; 1200 pt at 72/144/216 ppi → 1200/2400/3600 px, verified);
  `file.place` physical-size rule; PhotoCraft `desaturate` schema; `imageTrace.make` params.
- **SCHEMA:** VectorCraft/PhotoCraft catalogues at `/opt/craft/catalogues/`; vault 17.
- **DOCS:** vault 04/15; `assets/brand/README.md`; `assets/print-masters/README.md`.
