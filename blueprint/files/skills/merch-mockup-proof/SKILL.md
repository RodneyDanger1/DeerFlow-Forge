---
name: merch-mockup-proof
description: Pull a live Ridgeboundia product's mockups from its product page and Fourthwall CDN into a dated proof folder, inspect placement/colour/cut-off with your own eyes, record the evidence in the vault, and run the sample-order checklist for print scale. Use when the user says check the mockup, does the print look right, is it cut off, proof this product, compare the old and new tee, or make a mockup evidence pack.
version: 1.0.0
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [fourthwall, mockup, proof, product, visual-qc, sample-order, ridgeboundia]
    related_skills: [fourthwall-product-publish, fourthwall-catalog-audit, apparel-print-master, embroidery-art]
---

# Merch mockup proof

Takes a live product, downloads the images the store actually serves, and records what a human sees: placement, cut-off, colour, edge margins and whether the design matches the master. Mockups are authoritative for placement/cut-off, but they are **not** print proof. Print scale, exact colour and stitch quality need a physical sample, and this skill keeps that distinction explicit.

## When to use
- A product was just published or replaced and the storefront needs a visual check.
- A design looks off and you must prove or disprove “it is cut off”.
- Old and new generations must be compared side by side.
- A sample order needs an evidence pack and a receipt checklist.

## When not to use
- Editing or creating the print master — `apparel-print-master` / `embroidery-art`.
- Publishing or hiding the product — `fourthwall-product-publish`.
- Deciding what is live — `fourthwall-catalog-audit`.
- Claiming print size, exact colour or stitch quality from a mockup — impossible; order a sample.
- Downloading art you do not own or have rights to use.

## Inputs
- Live slug and Fourthwall id; template, region and print size (for example tee `front_large` 15×18 in).
- The storefront page URL (`https://ridgeboundia.com/product/<slug>`) and/or the DB image URLs.
- A dated proof folder under the vault; brand hex/colour expectation; the master PNG for comparison.
- Owner approval and budget for a sample order when print verification is requested.

## What a mockup can and cannot prove
- **Can prove:** where the design sits on the garment, which region was used, whether the mockup shows a visible cut-off, and the intended colourway.
- **Cannot prove:** printed size in inches, exact colour, fabric hand, embroidery stitch quality, or wash durability.
- Fourthwall's rule: a visible cut-off in the Mockup panel means it prints cut off. Observed here, a 2250 px and a 4500 px master rendered visually identical mockups, so scale cannot be inferred — only a sample settles it.

## Exact commands
Create the proof folder (parent paths exist; the dated folder is new):

```bash
SLUG=lost-and-learning-tee-4
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
OUT=/srv/vaults/storefront/30-reference/art-learning/assets/proofs/$SLUG-$STAMP
mkdir -p "$OUT"
```

Pull the live page and its Open Graph image (the image the store actually serves):

```bash
curl -fsS "https://ridgeboundia.com/product/$SLUG" -o "$OUT/page.html"
OG=$(grep -o 'property="og:image" content="[^"]*"' "$OUT/page.html" | head -1 | cut -d'"' -f4)
printf '%s\n' "$OG" > "$OUT/og-url.txt"
curl -fsS "$OG" -o "$OUT/og.webp"
```

Pull every product image on the Fourthwall CDN through the local image rows (read-only):

```bash
n=0
docker exec ridgeboundia-postgres psql -U ridgeboundia -d ridgeboundia -At -c \
  "select url from \"ProductImage\" i join \"Product\" p on p.id=i.\"productId\" where p.slug='$SLUG' order by i.sort" |
while IFS= read -r url; do n=$((n+1)); curl -fsS "$url" -o "$OUT/$(printf '%02d' "$n").webp"; done
```

Verify the download, hash it, and build a contact sheet for a first look:

```bash
identify -format '%f %wx%h %m\n' "$OUT"/*.webp
sha256sum "$OUT"/*.webp > "$OUT/sha256.txt"
magick montage "$OUT"/*.webp -tile 3x -geometry 600x800+8+8 -background '#f2f2f2' "$OUT/contact.jpg"
identify -format '%f %wx%h\n' "$OUT/contact.jpg"
```

Open `og.webp` and `contact.jpg` and inspect them yourself at full size. Do not accept a filename, a status code or a montage thumbnail as visual proof.

## Visual inspection checklist
- Placement: centred on the intended region; no unintended left/right or up/down shift.
- Cut-off: no letter, outline or graphic touches or crosses a seam, cuff, collar or print boundary.
- Margins: the design keeps a visible clear margin on every side of the region; record the tightest side.
- Colour: compare the rendered colour to the approved brand hex and the master; note hue/saturation drift.
- Artwork integrity: no stray white box, halo, fringe, ghost text, banding or missing element.
- Variant/repetition: the mockup matches the live colour/size set (Black tee, White GRU hoodie) and the image set shows the same design consistently.
- Verdict: PASS (placement/cut-off clean), CONDITIONAL (flag to owner), or FAIL (visible cut-off/missing art).

## Sample-order checklist
1. Owner approval and budget; samples are priced at cost, not free.
2. Pick the same template, colour and size as the live SKU, plus the risky size if fit is in question.
3. Place it through the shop's own order flow (Orders → Place order) and record the order id and UTC date.
4. On receipt, measure the printed width/height and compare with the region spec (tee `front_large` 15×18 in, hoodie `front` 14×14 in, beanie `embroidery_front` 5×1.75 in).
5. Judge colour in daylight against the master and brand hex; record DTG/embroidery differences honestly.
6. Check cut-off, seam crossing, cracking after a wash, and embroidery density/legibility.
7. Photograph the sample flat and worn, store the photos in the proof folder, and only then may the log say **print scale/colour verified**.

## Evidence log in the vault
Write `40-logs/YYYY-MM-DD-HHMM-<slug>-mockup-proof.md` with the vault frontmatter and link the proof folder:

```markdown
---
title: Mockup proof — <product> (<slug>)
tags: [fourthwall, mockup, proof, visual-qc]
status: current
updated: <ISO-8601 UTC>
confidentiality: internal
---
- Product / Fourthwall id / template / region:
- Folder + image count + sha256 file:
- Page and og:image URLs:
- Observed placement / cut-off / margins / colour:
- Verdict: PASS | CONDITIONAL | FAIL
- Print scale and exact colour: UNVERIFIED until sample <order id>
```

## Workflow
1. Confirm the product is live and record its slug/id; a 404 cannot be mockup-proofed.
2. Create the dated proof folder and pull the page, og:image and all DB images.
3. Verify every file with `identify` and `sha256sum`; build the contact sheet.
4. Inspect the originals one by one against the checklist; write observations as you go.
5. Compare against the master and the previous generation when replacing.
6. Record the log and verdict; keep the unresolved print-scale line explicit.
7. Order the sample when print verification is in scope, then close the loop with measurements.

## Acceptance gates
- Page returns 200 and `og:image` downloads; the numbered image count equals the live DB image count (`og.webp` is an extra copy of the first).
- Every image has a dimension/format line and a SHA-256 in `sha256.txt`.
- Each checklist item is observed and recorded; no item is inferred from a status code.
- Verdict is one of PASS/CONDITIONAL/FAIL with the reason and the tightest margin.
- The vault log exists and links the proof folder; print scale remains UNVERIFIED without a sample.
- No mockup was edited, cropped to hide a defect, or presented as a print proof.

## Refusals
- “The mockup looks good, so it prints fine” — refuse; placement is not print proof.
- “Use the mockup to confirm the exact printed size/colour” — refuse; order a sample.
- “Stretch/crop the mockup so it looks centred” — refuse; the mockup is evidence, not a design tool.
- “Proof a hidden/404 product from the public page” — impossible; publish it or use the media library.
- “Skip the sample, the owner does not want to pay” — allowed, but the log must say print scale is unverified.
- Any claim of stitch quality, wash durability or exact Pantone/hex match without physical evidence.

## Worked example
On 2026-11-05, `lost-and-learning-tee-4` returned 200 with title “Lost And Learning Tee — Ridgeboundia”; its og:image was a 1536×2048 WEBP and the DB held 10 images. Visual inspection showed the green mountain/wordmark print centred on the chest, the full wordmark and tagline visible, no cut-off and no stray white; the design looked small relative to the shirt, which is a mockup-rendering observation, not a print-size measurement. `lost-and-learning-beanie-3` returned 200 with 7 images; its 1536×2048 mockup showed the white wordmark spanning the cuff with the glyph edges close to both sides — flagged for a margin check against the 1500×525 master, not called cut off. Neither product has a sample order recorded, so both remain print-scale UNVERIFIED.

## Pitfalls
- **The page and the CDN are different sources**: `og:image` is one image; the DB rows are the full set. Pull both.
- **imgproxy URLs are long and signed**; never hand-edit them, re-pull from the page/DB.
- **WEBP**: some Windows viewers fail to decode it; use ImageMagick or the harness image reader.
- **The mockup scale is fixed**; a bigger master does not make a bigger mockup print.
- **Colour shifts are expected**: DTG on dark fabric and embroidery thread are not screen RGB; a sample is the only colour proof.
- **GRU is White**, not Black; confirm the variant on the mockup instead of assuming.
- **Hidden products 404**; do not treat a 404 as a missing image set.
- **Samples cost money**; get approval before ordering and never imply a sample is free.

## Sources & verification
- VERIFIED — 2026-11-05: tee-4 page 200, title and 1536×2048 WEBP og:image; 10 DB images; beanie-3 7 images; `identify`, `sha256sum` and `magick montage` commands executed; the proof-folder path's parent directories exist; visual inspection of tee-4 and beanie-3 mockups.
- SCHEMA — `lib/fourthwall/product-map.ts` maps `images[]`; `prisma/schema.prisma:177` (`ProductImage`); vault paths `30-reference/art-learning/assets/` and `40-logs/`.
- DOCS — fetched 2026-11-05: [Design file guidelines](https://help.fourthwall.com/create-and-sell-products/best-practices/design-file-guidelines-and-templates-for-merchandise.md) (mockup cut-off rule; 150 DPI apparel; samples), [Artwork best practices](https://help.fourthwall.com/create-and-sell-products/best-practices/artwork-best-practices.md) (colour differences; samples at cost).
- UNVERIFIED — print scale and exact colour for every live product; the 2250 vs 4500 px observation is an internal vault record, not a provider statement. No sample order exists yet.
