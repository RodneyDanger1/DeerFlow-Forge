---
name: brand-system
description: Assemble a usable brand kit — logo variants (primary, inverse, mono, icon), palette hex, type pairing with licences, clear-space and minimum-size rules, print rules and reusable templates — with the masters stored next to the notes. Use when the user says build a brand kit, brand guidelines, logo variants, colour palette, typography system, brand assets, or make the collection consistent.
---

# Brand system

Turns a mark and a colour idea into a kit another person can apply without asking questions:
master files plus a short rules document, not a mood board.

## When to use

- A new brand/store needs its first complete asset set.
- The collection drifts (different hues, widths, treatments) and needs one source of truth.
- Downstream work (ads, banners, cards, garment prints) needs approved assets and rules.

## When not to use

- One-off ad or banner production — use those skills; they consume this kit.
- Trademark clearance, competitor conflicts or naming risk — that is a research task, not this.
- A garment master — `apparel-print-master` handles provider geometry.
- Embroidery lockups — `embroidery-art` owns the stitch-legal variant.

## Required inputs

- Brand name, positioning line, and the mark (vector preferred, raster acceptable).
- Palette: existing hex list, or references to derive it from.
- Type: licensed fonts available on the machine (`text.fontList`), or a decision to use the
  open families already installed.
- Usage contexts: storefront, social, print, embroidery, packaging.
- Where masters must live (the vault art-learning folder and the repo), and who approves.

## Exact commands

```bash
cd /opt/pod-pipeline
VC=/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli
PC=/opt/craft/photocraft/photocraft-0.20.2-linux-x86_64/bin/photocraft-cli
PY=/opt/pod-pipeline/.venv/bin/python
```

1) Vectorise a flat mark (full workflow in `artcraft-vector-trace`):

```bash
$PY -m tools.prep_print_art --input /tmp/logo.png --output /tmp/logo_cut.png \
  --width-px 1200 --height-px 1200 --dpi 300 --mode white --clean-rim --min-component 60 \
  --print-width-in 4 --report-json /tmp/logo_cut.json
cat > /tmp/logo-steps.json <<'JSON'
[{"command":"select.all"},
 {"command":"imageTrace.make","params":{"params":{"mode":"color","palette":"limited","colors":8,
   "paths":70,"corners":45,"noise":12,"ignoreWhite":true,"method":"abutting",
   "fills":true,"strokes":false,"shapes":false,"autoGrouping":false,"gradients":false}}},
 {"command":"imageTrace.expand"}]
JSON
$VC run --in /tmp/logo_cut.png --commands /tmp/logo-steps.json --export /tmp/logo.svg
```

2) Build a brand sheet and export the raster sizes (verified: an 8 in document exported at
`ppi:300` gives 2400 px):

```bash
cat > /tmp/sheet.json <<'JSON'
[{"command":"file.new","params":{"width":1200,"height":1200,"units":"Pixels","colorMode":"rgb","backgroundContents":"white"}},
 {"command":"file.place","params":{"path":"/tmp/logo.svg"}},
 {"command":"text.create","params":{"x":80,"y":1020,"text":"RIDGEBOUNDIA","font":"FreeSans","style":"Bold","size":64,"color":"#33614a"}},
 {"command":"document.export","params":{"path":"/tmp/brand_sheet.svg","format":"svg"}},
 {"command":"document.export","params":{"path":"/tmp/brand_sheet@1x.png","format":"png","ppi":72}},
 {"command":"document.export","params":{"path":"/tmp/brand_sheet@2x.png","format":"png","ppi":144}},
 {"command":"document.export","params":{"path":"/tmp/brand_sheet@3x.png","format":"png","ppi":216}}]
JSON
$VC run --commands /tmp/sheet.json
identify -format '%f %wx%h\n' /tmp/brand_sheet@1x.png /tmp/brand_sheet@2x.png /tmp/brand_sheet@3x.png
```

3) Monochrome raster variant and palette chips (ImageMagick is installed):

```bash
$PC run /tmp/logo_1200.png --cmd image.adjustments.desaturate --out /tmp/logo_mono.png
magick -size 240x240 xc:'#33614a' /tmp/chip_33614a.png
magick -size 240x240 xc:'#d9caa4' /tmp/chip_d9caa4.png
```

4) Available families (choose only from installed fonts, or ship the licensed file):

```bash
$VC run --cmd text.fontList
```

## Workflow

1. Audit what exists: raster marks, old hex values, fonts actually installed.
2. Fix the palette first: name each colour, record hex, decide print equivalents with the vendor.
3. Produce the four lockups: primary, inverse (for dark grounds), monochrome, icon/square.
4. Set clear space (a fixed fraction of the mark) and minimum sizes in px and inches; measure them.
5. Choose type: one display family, one text family; record licence and fallbacks.
6. Write the application rules: garment print width, white rule, vector rule, embroidery limits.
7. Export masters: SVG (working master), PNG 1x/2x/3x for web, PDF for print.
8. Store masters and the rules document next to the art-learning notes; index the file names.

## Acceptance gates

- Each variant opens and renders at 1x, and the SVG has real paths (not an embedded raster).
- Palette table names every colour with hex; no colour appears in art that is absent from the table.
- Type table lists family, weights used, licence source and fallback.
- Clear space and minimum size are stated with numbers, not "use good judgement".
- Print rules include: every white transparent, 300 DPI masters, embroidery exception.
- Masters are stored at the agreed path and referenced by filename in the kit document.
- Downstream skills can use the kit without re-deriving colours or type.

## Refusal conditions

- Unlicensed fonts or stock art — refuse to bake them into brand assets; choose installed open
  families or obtain a licence.
- Trademark/naming clearance — out of scope; do not imply legal clearance.
- No invented hex values or "brand colours" without a source; derive and record instead.
- No browser automation — prove web usage from exported PNGs, not a live page.
- Mockups and sheets prove layout only; print colour needs a physical proof.

## Worked examples

**1. Four-lockup logo set.** Trace a flat PNG to `logo.svg` (8 colours, 70 paths, 45 corners).
Export primary; make inverse by recolouring on a dark ground; make monochrome with
`image.adjustments.desaturate` for raster use (or a black-and-white trace for vector); crop the
icon square. Record minimum sizes: 120 px wide for web, 0.75 in for print, 1.5 in for embroidery
contexts.

**2. Palette + type sheet.** Six named colours with hex, two families (display + text), a sheet
at 1200×1200 px exported at 72/144/216 ppi, plus chips for each colour. Rules document states
the garment print width (tee 8 in, hoodie 8.5 in) and the white-transparent rule so
`apparel-print-master` needs no decisions.

## Pitfalls

- **Traced text is not a brand asset** — retype the wordmark with a real font.
- **Off-white paper** survives `ignoreWhite`; cut out before tracing, every time.
- **Colour drift** between traced SVG and raster exports is normal; correct it deliberately and
  record the final hex.
- **RGB vs CMYK**: screen hex is not a press colour; agree print equivalents with the vendor.
- **Two masters diverge** — one SVG master per lockup, everything else exports from it.
- **Font availability** differs between machines; record fallbacks or embed/outline text.
