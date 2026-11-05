---
name: ad-creative
description: Produce social and paid-ad creatives at exact pixel canvases (1080 square, 1080x1350, 1080x1920) with safe margins, one message, readable type and correct exports. Use when the user says make an ad, Instagram post, Facebook creative, story ad, sale graphic, promo image, paid social asset, or launch creative.
---

# Ad creative

Builds a finished ad image with the brand kit, at the platform's pixel size, with the text
inside safe margins and one job per creative. Output is PNG/WebP at exact dimensions; the
copy deck and claims stay the owner's responsibility.

## When to use

- A feed, portrait or story/reel ad is needed at a standard canvas.
- A sale/launch announcement needs a consistent template across sizes.
- Existing creative must be resized without re-laying it out badly.
- You need a repeatable ad template for the store's brand kit.

## When not to use

- Website hero/banner work — `web-banner` (different sizes and crops).
- Print or garment art — apparel/shipping skills.
- Video or motion creatives — this skill produces stills only.
- Ad platform policy review, audience targeting or performance claims — outside this skill.

## Required inputs

- Offer and the single message; approved claims and any legally required wording.
- Canvas: 1080×1080 feed, 1080×1350 portrait, 1080×1920 story/reel.
- Brand assets: logo SVG, palette hex, approved art/photo (licensed).
- CTA and landing URL text (the URL is usually overlaid by the platform, not baked in).
- Where the file must be delivered and any platform file-size cap.

## Exact commands

```bash
cd /opt/pod-pipeline
VC=/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli
```

Square feed — 1080 px document, exact-pixel export (verified: `ppi:72` means 1 px per point):

```bash
magick -size 1080x1080 xc:'#101312' /tmp/ad_bg.png
magick /tmp/brand_art.png -resize 1080x1080^ -gravity center -extent 1080x1080 /tmp/ad_art.png
cat > /tmp/ad.json <<'JSON'
[{"command":"file.new","params":{"width":1080,"height":1080,"units":"Pixels","colorMode":"rgb","backgroundContents":"transparent"}},
 {"command":"file.place","params":{"path":"/tmp/ad_bg.png"}},
 {"command":"file.place","params":{"path":"/tmp/ad_art.png"}},
 {"command":"text.create","params":{"x":80,"y":560,"text":"MADE FOR THE LONG WAY ROUND","font":"FreeSans","style":"Bold","size":72,"color":"#efe6cf"}},
 {"command":"text.create","params":{"x":80,"y":700,"text":"SHOP THE DROP","font":"FreeSans","style":"Bold","size":40,"color":"#d9caa4"}},
 {"command":"document.export","params":{"path":"/tmp/ad_feed.png","format":"png","ppi":72}},
 {"command":"document.export","params":{"path":"/tmp/ad_feed.png","format":"png","ppi":72}}]
JSON
$VC run --commands /tmp/ad.json
identify -format '%f %wx%h %m %b\n' /tmp/ad_feed.png /tmp/ad_feed.webp
```

Portrait / story: same steps with `{"width":1080,"height":1350}` or
`{"width":1080,"height":1920}`; keep the message inside the central safe band.

Brand assets helper: `document.export` for SVG logos at any size, `imageTrace.make` when only a
raster logo exists (see `brand-system`).

## Workflow

1. Write the one-sentence message. If there are two messages, split into two creatives.
2. Pick the canvas and the safe margins: ≥60 px each side; for story, keep text clear of the
   top ~250 px and bottom ~250 px where platform UI sits.
3. Lay out: logo, headline, proof point, CTA. Type ≥24 px at 1080 (headline 64–96 px).
4. Place art so the subject is not cropped by the safe margin; check contrast where text
   crosses art.
5. Export PNG for QC; VectorCraft writes only lossless WebP, so produce the delivery WebP with `photocraft-cli convert /tmp/ad_feed.png /tmp/ad_feed.webp --quality 82` (lossy, verified) and check bytes.
6. View at 100 % and at thumbnail (phone size) — if the headline is unreadable at thumbnail,
   fix the hierarchy.
7. Record the canvas, copy and claim sources next to the file.

## Acceptance gates

- Exact canvas: 1080×1080, 1080×1350 or 1080×1920 — verified with `identify`.
- All text inside the safe margin; nothing critical within 60 px of an edge.
- Headline contrast against its background ≥4.5:1 (WCAG AA for text); sample the actual pixels,
  do not eyeball.
- One message, one CTA, one visual focus.
- Type ≥24 px at 1080; no line breaks that orphan a single word.
- Logo legible at thumbnail size; no stretched or recoloured mark.
- File size within the platform's cap (team default ≤500 KB for stills).
- No unlicensed fonts/imagery; claims match owner-approved wording.

## Refusal conditions

- Unlicensed fonts, stock photos or AI art with unclear rights — refuse to ship.
- No browser automation here: you cannot preview the ad inside the platform's feed. Say so;
  a local render is the proof you have.
- No performance or "guaranteed conversion" claims; no fabricated reviews or screenshots.
- Do not bake in platform UI or fake engagement counts.
- No dry-run in the CLIs — export to new paths and inspect every time.

## Worked examples

**1. 1080×1080 sale card.** Dark ground, art placed right-of-centre, headline at 72 px, CTA at
40 px, both inside 80 px margins. Export `ad_feed.png` (1080×1080); make lossy WebP with PhotoCraft `convert --quality 82` (VectorCraft's WebP is lossless-only). Check thumbnail legibility and the contrast of `#efe6cf` on `#101312`.

**2. 1080×1920 story.** Same message, larger type (88 px), subject in the middle band, CTA at
1,600 px height. Keep the top 250 px and bottom 250 px free of text for platform chrome. Export
PNG and WebP; verify the dimensions and that nothing important sits in the UI bands.

## Pitfalls

- **Safe zones are not optional** — profile name, CTA button and swipe-up chrome eat the edges.
- **Text over busy art** is the usual contrast failure; add a scrim or move the type.
- **One message per creative** — cramming price, story and CTA halves the read.
- **Baked-in CTA vs platform CTA**: don't duplicate the button text in the image.
- **Thumbnail test** — most feeds show the creative small; design for that size.
- **WebP quality**: VectorCraft ignores `quality` for WebP (lossless only, verified); use PhotoCraft `convert --quality` for lossy delivery and re-check bytes after every change. Raised quality inflates size
  cap demands it.
- **`file.place` keeps native pixels** — a 2000×1500 image on a 1080 canvas lands at
  (-460,-210) and overflows (verified); resize/extent to the placement size first.
- **`backgroundContents` only accepts `transparent|white`** (verified) — coloured grounds are
  placed images, as in the example.
