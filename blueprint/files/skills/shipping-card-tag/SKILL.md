---
name: shipping-card-tag
description: Lay out thank-you cards, package inserts, hang tags and product/QR cards with bleed, safe margins and 300 DPI, exported as print PDF or PNG. Use when the user says thank-you card, shipping insert, hang tag, product tag, clothing label, QR card, packaging insert, or needs a print-ready card for a vendor.
---

# Shipping card / tag

Produces print-ready inserts and tags: correct trim size, bleed, safe margin, 300 DPI output
and a QR that has actually been scanned. Vendor specs are confirmed before art starts.

## When to use

- A thank-you card, package insert or product card must ship with orders.
- A hang tag/label needs artwork at a real trim size.
- A QR card must point to a product, care page or review flow.
- A print vendor asked for a specific file (PDF or 300 DPI PNG) and dimensions.

## When not to use

- Garment print masters — `apparel-print-master`.
- Embroidery/woven labels — `embroidery-art`; confirm the material spec first.
- Social/web graphics — `ad-creative` / `web-banner`.
- Any job where the vendor's size, bleed or colour mode is unknown — ask first.

## Required inputs

- Kind: thank-you card, insert, hang tag, label, QR card.
- Trim size and orientation (team defaults: 4×6 in card, 3.5×2 in insert, 2×3.5 or 2×4 in tag).
- Bleed and safe margin from the vendor (defaults: 0.125 in bleed, 0.25 in safe margin).
- Colour mode the vendor wants (RGB or CMYK) and the file format they accept.
- Approved copy, logo asset, QR target URL and its QR image.
- Hole size/position for hang tags (0.125–0.1875 in), if applicable.

## Exact commands

```bash
cd /opt/pod-pipeline
VC=/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli
```

Build at **bleed size** (trim + 0.125 in each side ⇒ 4.25×6.25 in for a 4×6 card), tell the
document its bleed, and export:

```bash
magick -size 306x450 xc:'#efe6cf' /tmp/card_bg.png   # 4.25x6.25 in in points
cat > /tmp/card.json <<'JSON'
[{"command":"file.new","params":{"width":"4.25 in","height":"6.25 in","colorMode":"rgb","backgroundContents":"transparent"}},
 {"command":"document.setup","params":{"bleed":9}},
 {"command":"file.place","params":{"path":"/tmp/card_bg.png"}},
 {"command":"file.place","params":{"path":"/tmp/brand_logo.svg"}},
 {"command":"text.create","params":{"x":72,"y":120,"text":"THANK YOU","font":"FreeSans","style":"Bold","size":28,"color":"#33614a"}},
 {"command":"document.export","params":{"path":"/tmp/card_print.pdf","format":"pdf"}},
 {"command":"document.export","params":{"path":"/tmp/card_300.png","format":"png","ppi":300}}]
JSON
$VC run --commands /tmp/card.json
identify -format '%f %wx%h %x %y\n' /tmp/card_300.png
file /tmp/card_print.pdf
```

`9` is 0.125 in in points (72 pt = 1 in). A 4.25 in document exported at `ppi:300` is
1275×1875 px (verified conversion: inches × ppi = pixels).

Hang tag with a drill hole: keep art ≥0.25 in away from the hole and place the hole in the
layout spec for the vendor; there is no verified "punch hole" command — mark its centre and
diameter in the handoff notes, not as art.

QR card: place the supplied QR PNG with `file.place` at its final size (≥0.8 in / 240 px at
300 DPI) with its quiet zone intact; never redraw or recolour the QR.

## Workflow

1. Get the vendor spec in writing: trim, bleed, safe margin, colour mode, format, stock/fold.
2. Compute the document size: trim + 2 × bleed on both axes.
3. Lay out with all copy inside the safe box (bleed + 0.25 in from the trim edge).
4. Place the logo and QR at final size; check the QR quiet zone.
5. Export PDF for the vendor (or 300 DPI PNG if they require raster).
6. Verify dimensions, DPI and that the bleed area is covered by background/art.
7. Have the QR scanned and the copy proofread by a human.
8. Test-print one insert before the order run; check colour, fold and cut.

## Acceptance gates

- Document = trim + bleed; trim size matches the vendor spec exactly.
- 300 DPI effective for raster (118.11 px/cm in `identify`); PDF keeps vectors.
- All text and the logo inside the safe margin (≥0.25 in from trim).
- Background/art extends through the bleed — no white slivers at the cut edge.
- QR present, unmodified, ≥0.8 in, quiet zone intact **and actually scanned** to the right URL.
- Vendor colour mode honoured; no RGB-only neon colours when CMYK is required.
- One test print inspected before a production run.

## Refusal conditions

- No vendor spec — refuse to art a job with an unknown trim/bleed/colour mode; ask first.
- No QR generator is installed here (verified: no `qrencode`/`zbarimg`). A QR must be supplied;
  never draw a fake QR or claim scannability without a scan.
- No browser automation; proof is the exported file plus a physical test print.
- No dry-run flag in the craft CLIs — export to new paths and inspect.
- Do not promise exact press colour; screen and printer differ.

## Worked examples

**1. 4×6 thank-you card.** Document 4.25×6.25 in with 9 pt bleed, cream ground, logo top, one
line of thanks, QR bottom-right ≥0.8 in. Export `card_print.pdf` and `card_300.png`
(1275×1875 px). Confirm the safe box: trim at 0.125 in, so text starts ≥0.375 in from the
document edge.

**2. 2×3.5 hang tag.** Document 2.25×3.75 in, hole centre 0.25 in from the top edge with a
0.1875 in diameter noted in the handoff, logo and short line below the hole. Export PDF; verify
the hole keeps 0.25 in clearance from art.

## Pitfalls

- **Bleed vs trim** — a 4×6 file with no bleed shows white edges after cutting.
- **Safe margin vs bleed** — text 0.125 in from the edge looks placed but gets trimmed.
- **Hole through art** — reserve the drill area before layout, not after.
- **QR quiet zone** — cropping the white border around a QR breaks scanning.
- **RGB neon** — vivid screen colours may be unreachable in CMYK; get a proof.
- **Mockups lie about scale** — a test print is the only proof of size and colour.
- **Vendor formats vary** — confirm PDF vs PNG and whether crop marks are required.
- **`file.place` uses the file's physical size at its ppi** — pre-size the logo/QR with `magick -resize`/`-extent` so a 2× asset does not overflow the card.
- **`backgroundContents` only accepts `transparent|white`** (verified) — the cream ground is a
  placed image, as in the example.
