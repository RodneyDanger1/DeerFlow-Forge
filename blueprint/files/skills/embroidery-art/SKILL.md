---
name: embroidery-art
description: Produce stitch-legal embroidery artwork (caps, patches, beanies) with measured cap heights, minimum stroke widths and a thread-colour limit — artwork only, never a stitch file. Use when the user says embroider this, beanie design, cap logo, patch design, embroidery lockup, stitch-legal art, or asks for a DST/PES/EXP file.
---

# Embroidery art

Makes the art an embroidery service can stitch, and states the limits in measured numbers.
This skill produces **art plus constraints** — SVG/PNG at real size — not a `.DST`, `.PES` or
`.EXP` stitch file, because no digitizer exists here.

## When to use

- A brand mark must become a cap, patch, beanie or chest embroidery lockup.
- Text is too small/complex to stitch and the lockup must be simplified.
- You must prove a design is stitch-legal before sending it to a digitizer or provider.

## When not to use

- DTG/print work — use `apparel-print-master`.
- Any request for a stitch file, thread path, underlay or machine tape — refuse and route to a
  digitizer or the provider's embroidery service.
- Gradients, shadows, photoreal detail, fine serif hairlines — not stitchable as requested.
- Knitted products whose production method is `KNITTING` — the print tools refuse them too.

## Required inputs

- Brand text/icon, or the vector mark from `brand-system`.
- Embroidery area in inches (for example 5×1.75 in, 4×4 in) and its source row in
  `/opt/pod-pipeline/config/fourthwall-template-details.json`.
- Intended thread colours (≤6), the stitcher's thread palette, and the garment colour.

## Exact commands

```bash
cd /opt/pod-pipeline
PY=/opt/pod-pipeline/.venv/bin/python
FONT=/usr/share/fonts/truetype/freefont/FreeSansBold.ttf
```

Read the real area geometry (never guess it):

```bash
$PY - <<'PY'
import json
rows = json.load(open('/opt/pod-pipeline/config/fourthwall-template-details.json'))
row = next(r for r in rows if r.get('productId') == 'pro_REPLACE_ME')
print(row['name'], row['productionMethod'], row['supportsBackendRendering'])
print(json.dumps(row['areaGeometry'], indent=1))
PY
```

Render the wordmark at 4× then downsample (crisp edges, measured size):

```bash
magick -background none -fill '#33614a' -font "$FONT" -pointsize 520 \
  label:'RIDGEBOUNDIA' -trim +repage /tmp/wordmark_4x.png
magick /tmp/wordmark_4x.png -resize 25% /tmp/wordmark_1x.png
identify -format '%f %wx%h\n' /tmp/wordmark_1x.png
```

Measure capital height independently — render `H` at the same point size:

```bash
magick -background none -fill '#000000' -font "$FONT" -pointsize 520 \
  label:'H' -trim +repage /tmp/cap_4x.png
magick /tmp/cap_4x.png -resize 25% /tmp/cap_1x.png
identify -format '%h\n' /tmp/cap_1x.png     # pixels; divide by 300 for inches
```

Measured on FreeSansBold: `H` at pointsize 300 → 219 px before the 25% downsample used by the 4× render (55 px after it), i.e. cap ≈ 0.183 × point size.
0.3 in at 300 DPI = 90 px, so point size ≈ 492 (520 gives ≈0.317 in).

Exact-size vector art on the embroidery area (inches strings; `text.create` size is points,
1 in = 72 pt):

```bash
cat > /tmp/emb.json <<'JSON'
[{"command":"file.new","params":{"width":"5 in","height":"1.75 in","colorMode":"rgb","backgroundContents":"transparent"}},
 {"command":"text.create","params":{"x":20,"y":95,"text":"RIDGEBOUNDIA","font":"FreeSans","style":"Bold","size":44,"color":"#33614a"}},
 {"command":"document.export","params":{"path":"/tmp/embroidery_wordmark.png","format":"png","ppi":300}}]
JSON
/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli run --commands /tmp/emb.json
identify -format '%f %wx%h %x %y\n' /tmp/embroidery_wordmark.png
```

At 44 pt the cap height is ≈0.45 in at 300 DPI; the exported PNG is 1500×525 px.

## Workflow

1. Decide the lockup **before** drawing: full badge, simplified icon + short word, or
   single-colour wordmark. A dense badge at 1.75 in cannot meet 0.3 in capitals.
2. Read the real area from the details file; convert every limit to pixels at 300 DPI
   (0.3 in = 90 px, 0.25 in = 75 px, 0.05 in = 15 px).
3. Render the chosen lettering with a bold outline font, at 4× then downsampled.
4. Measure cap height (H), lowercase height (x) and the thinnest stroke; convert px ÷ 300.
5. Count colours: one thread colour per element, ≤6 total; map hex values to the stitcher's
   thread palette; no gradients, no shadows, no semi-transparent fills.
6. Export art at real size: PNG at 300 DPI (transparent) or SVG for the digitizer.
7. Preview at actual size (5×1.75 in on screen is not the same as print), record the
   measurements in the handoff, and label the file **art**, not a stitch file.

## Acceptance gates

- Capital height ≥0.3 in (90 px at 300 DPI) and lowercase ≥0.25 in (75 px), measured.
- Thinnest stroke ≥0.05 in (15 px); hairlines and thin serifs rejected.
- ≤6 thread colours, solid fills only, no gradients/transparency/shadows.
- Real-size preview reviewed; text legible at 100 % actual size.
- Measurements and the thread palette recorded next to the art.
- Art file is explicitly labelled **art**, not a stitch file.

## Refusal conditions

- No stitch-file engine: this environment has VectorCraft and PhotoCraft only — no digitizer,
  no DesignCraft, no `.DST/.PES/.EXP` writer. Never call an SVG/AI/PDF a stitch file.
- If the full badge cannot meet the minimums, refuse the badge and ship the wordmark lockup.
- No dry-run flag exists in the craft CLIs; export to new paths and inspect.
- No browser automation — prove legibility from rendered PNGs at real size.
- Do not promise stitch quality or thread colour from a screen render; that needs a sample.

## Worked examples

**1. Beanie wordmark, 5×1.75 in.** Full badge is impossible (0.3 in caps at 1.75 in height).
Use `RIDGEBOUNDIA` in FreeSansBold: render at 520 pt (≈95 px cap after the 4× render is
downsampled) → 0.317 in caps at 300 DPI, single thread colour, one line. Export PNG at 300 DPI
on a 1500×525 px canvas. Handoff notes: cap 0.317 in, stroke ≥0.05 in, 1 colour.

**2. 4×4 in patch.** Simplified icon (no text under 0.25 in): 3 thread colours, solid shapes,
outline stroke ≥15 px at 300 DPI. Export 1200×1200 px PNG plus SVG for the digitizer, with the
colour list. If the icon needs more than 6 colours, reduce it to 4.

## Pitfalls

- **Full badge at small area** is the classic failure: caps cannot shrink below 0.3 in.
- **Cap height is not font size** — measure the rendered `H`; the ratio is font-specific
  (FreeSansBold ≈0.183 × point size at 1×).
- **4× then downsample**, never render small and upscale.
- **One colour per element** — gradients and shadows cannot be stitched.
- **Thread palette, not screen hex** — map colours before production, not after.
- **Art ≠ stitch file** — the digitizer still has to produce the machine file.
