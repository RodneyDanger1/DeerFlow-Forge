---
name: ad-creative
description: "Use when a feed, portrait or story/reel ad still is needed at a standard canvas (1080×1080, 1080×1350, 1080×1920): brand kit, safe margins, one message, exact-pixel PNG plus lossy WebP. Triggers: make an ad, Instagram post, Facebook creative, story ad, sale graphic, promo image, paid social asset, launch creative."
version: 1.1.0
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [ads, social, creative, design, webp, safe-margins, brand]
    related_skills: [brand-system, web-banner, shipping-card-tag, artcraft-command-catalog]
---

# Ad creative

Builds a finished ad still with the brand kit, at the platform's pixel size, text inside safe
margins, one job per creative. Output is PNG + lossy WebP at exact dimensions; copy/claims remain
the owner's responsibility.

## When to use / not use

- Use for feed, portrait or story/reel ads at a standard canvas.
- Use for sale/launch announcements that need the same template across sizes.
- Use to resize existing creative without re-laying it out badly.
- Not for website hero/banner (`web-banner`), print/garment art, video, or platform policy/targeting.
- Not a licence/claims review — refuse unlicensed assets and unapproved claims.

## Required inputs

- Offer and the single message; approved claims and required wording.
- Canvas: 1080×1080 feed, 1080×1350 portrait, 1080×1920 story/reel.
- Brand assets: logo SVG, palette hex, licensed art/photo.
- CTA and landing URL text (the platform usually overlays the URL).
- Delivery path and platform file-size cap.

## Exact commands (verified 2026-11-05)

```bash
cd /opt/pod-pipeline
VC=/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli
PC=/opt/craft/photocraft/photocraft-0.20.2-linux-x86_64/bin/photocraft-cli
# Linux VPS only. From Windows: ssh -i ~/.ssh/id_ed25519_hostinger root@179.197.88.181 'cd /opt/pod-pipeline && bash -s' < script.sh
# Stop if SSH/key is unavailable: /opt/pod-pipeline and the CLIs do not exist on Windows.
```

Square feed — exact pixels; `ppi:72` means 1 px per point, so a 1080 pt document exports 1080 px:

```bash
magick -size 1080x1080 -units PixelsPerInch -density 72 xc:'#101312' /tmp/ad_bg.png
magick /tmp/brand_art.png -resize 1080x1080^ -gravity center -extent 1080x1080 -units PixelsPerInch -density 72 /tmp/ad_art.png
cat > /tmp/ad.json <<'JSON'
[{"command":"file.new","params":{"width":1080,"height":1080,"units":"Pixels","colorMode":"rgb","backgroundContents":"transparent"}},
 {"command":"file.place","params":{"path":"/tmp/ad_bg.png","rect":[0,0,1080,1080]}},
 {"command":"file.place","params":{"path":"/tmp/ad_art.png","rect":[80,80,920,920]}},
 {"command":"text.create","params":{"x":80,"y":560,"text":"MADE FOR THE LONG WAY ROUND","font":"FreeSans","style":"Bold","size":52,"color":"#efe6cf"}},
 {"command":"text.create","params":{"x":80,"y":700,"text":"SHOP THE DROP","font":"FreeSans","style":"Bold","size":40,"color":"#d9caa4"}},
 {"command":"document.export","params":{"path":"/tmp/ad_feed.png","format":"png","ppi":72}}]
JSON
$VC run --commands /tmp/ad.json
$PC convert /tmp/ad_feed.png /tmp/ad_feed.webp --quality 82
identify -format '%f %wx%h %m %b\n' /tmp/ad_feed.png /tmp/ad_feed.webp
convert /tmp/ad_feed.png -format 'corner=%[pixel:p{5,5}] center=%[pixel:p{540,540}]\n' info:
```

Portrait/story: same steps with `{"width":1080,"height":1350}` or `{"width":1080,"height":1920}`;
keep the message inside the central safe band.

The example omits the approved logo for brevity; production adds `file.place` for the logo inside the safe zone. **Placement math (important):** `file.place` brings raster images in at **100 % of their physical
size** (the file's ppi, else 72), not their pixel count. A 2000×1500 image at 300 ppi lands as
**480×360 pt centred at (300, 360)** on a 1080 canvas; at 72 ppi it lands **2000×1500 centred at
(−460, −210)**. Two safe options:
- pre-resize to the final pixel box with `magick … -resize WxH^ -gravity center -extent WxH` (72 ppi),
  or
- place with `rect: [x, y, w, h]` (fit inside, aspect kept) — verified by execution (2026-11-05).

## Workflow / state machine

`brief → canvas + safe zone → layout (logo, headline, proof, CTA) → contrast check → export PNG →
lossy WebP → thumbnail test → record sources`.

1. Write the one-sentence message; two messages = two creatives.
2. Safe margins ≥60 px each side; story keeps text out of the top/bottom ~250 px UI bands.
3. Type ≥24 px at 1080; long headline 44–56 px (measure `bounds`), short headline ≤96 px; one
   visual focus; CTA overlaid by the platform.
4. Check contrast where text crosses art; add a scrim or move type rather than eyeball.
5. Export PNG; convert to lossy WebP; inspect both bytes and dimensions.
6. View at 100 % and at phone-thumbnail size; fix hierarchy if unreadable.
7. Record canvas, copy and claim sources next to the files.

## Acceptance gates

- Exact canvas 1080×1080 / 1080×1350 / 1080×1920 (`identify`).
- **Text bounds fit:** `text.create` returns `bounds`; require `x ≥ 60`, `y ≥ 60`, `x + width ≤ canvas − 60`
  and `y + height ≤ canvas − 60`. The original 72 px headline measured **1,229 pt wide**, overflowing a
  1080 canvas — that is why the example uses 52 px (888 pt). Wrap or shrink before exporting.
- Background is opaque at the sampled corners (`convert … -format 'corner=…'`), not transparent/white.
- All text inside safe margins; nothing critical within 60 px of an edge.
- Headline contrast vs its background ≥4.5:1 (WCAG AA); sample actual pixels.
- One message, one CTA, one focus; type ≥24 px; no orphan single words.
- Logo legible at thumbnail; nothing stretched/recoloured.
- File size within the platform cap (team default ≤500 KB for stills).
- No unlicensed fonts/imagery; claims match owner-approved wording.
- Missing offer/claims/canvas/brand kit → ask or route `brand-system`; never invent copy or claims.

Contrast check (WCAG relative luminance) — save as `contrast.py` and run with sampled hex values:

```python
def lum(h):
    c=[int(h[i:i+2],16)/255 for i in (1,3,5)]
    c=[x/12.92 if x<=0.04045 else ((x+0.055)/1.055)**2.4 for x in c]
    return 0.2126*c[0]+0.7152*c[1]+0.0722*c[2]
def ratio(a,b):
    la,lb=sorted([lum(a),lum(b)], reverse=True)
    return (la+0.05)/(lb+0.05)
print(ratio('#efe6cf','#101312'))
```
The script takes design tokens; confirm the background sample against the exported PNG (`convert … -format '%[pixel:p{x,y}]'`).

## Refusals / failure modes

- Unlicensed fonts/stock/AI art with unclear rights — refuse to ship.
- No browser automation: cannot preview inside the platform feed; local render is the proof.
- No performance/"guaranteed conversion" claims; no fabricated reviews/screenshots.
- Do not bake in platform UI or fake engagement counts; do not duplicate the platform CTA text.
- No dry-run in either CLI; export to new paths and inspect.
- `backgroundContents` accepts only `transparent|white` (verified); coloured grounds are placed images.
- WebP: VectorCraft writes lossless-only (quality ignored); PhotoCraft `convert --quality` makes
  lossy WebP — and on flat art the lossy file can be **larger** (measured 2,718 B vs 1,372 B for a
  1080² flat test). Compare both, keep the smaller acceptable file.

## Worked examples

**1. 1080×1080 sale card.** Dark ground, art right-of-centre, headline 52 px (bounds 888×52), CTA
40 px, both inside 80 px margins. Export `ad_feed.png`; convert lossy WebP `--quality 82`; verify 1080×1080 and
contrast of `#efe6cf` on `#101312`.

**2. 1080×1920 story.** Same message, headline 52 px (bounds 888×52; 88 px was 1,503 px wide and
overflowed), subject middle band, CTA around y=1600; top and
bottom 250 px free of text. Export PNG + WebP; check UI bands and thumbnail legibility.

## Integration handoffs

- Brand assets/rules → `brand-system`.
- Website hero → `web-banner`; print inserts → `shipping-card-tag`.
- Product art → `apparel-print-master`; never bake a mockup into an ad as if it were the product.

## Pitfalls

- Safe zones are not optional; platform chrome eats the edges.
- Text over busy art is the usual contrast failure — scrim or move.
- One message per creative; cramming kills the read.
- `file.place` uses physical size (see math above); use `rect` or pre-resize.
- Thumbnail test: design for the small size first.
- `--quality` on the wrong tool: VectorCraft ignores WebP quality; use PhotoCraft for lossy.


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

Palette/type/command mapping: **artcraft-command-atlas**, **brand-system**, **artcraft-typography-outlines**.

## Sources & verification

- **VERIFIED:** PhotoCraft `convert --quality` runs and warns "lossy compression"; q82 vs lossless
  byte sizes on a 1080² flat test; VectorCraft `document.export ppi` exact pixels; `file.place`
  physical-size rule (schema + earlier probe); `backgroundContents` values; `text.fontList` 45 families.
- **SCHEMA:** `file.place {path|name|dataBase64, at, rect, page, crop, link, …}`;
  `document.export {path, format, ppi, scale, background, svg:{…}}`; PhotoCraft `convert/run`.
- **DOCS:** vault 15; WCAG contrast formula.
