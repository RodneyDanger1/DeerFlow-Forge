---
name: web-banner
description: Produce website hero and banner art at desktop (1920x600-800) and mobile (800x1000) sizes, keeping type as HTML wherever possible and exporting WebP/PNG inside a file-size budget. Use when the user says website banner, hero image, homepage banner, site header art, responsive banner, or needs web art that is light and correctly cropped.
---

# Web banner

Builds the image layer of a site banner, at exact web dimensions, with a separate mobile
composition and a real file-size budget. Type should live in HTML/CSS whenever the page can
render it; this skill bakes type only when the banner is used as a flat image.

## When to use

- A storefront or landing page needs hero/banner artwork.
- An existing banner must be resized for desktop and mobile without bad crops.
- A campaign image must be delivered as WebP under a size budget.
- You need a repeatable banner template for the brand kit.

## When not to use

- Social/paid ads — `ad-creative` (its canvases and safe zones differ).
- Print or garment work — apparel/shipping skills.
- Full page design, layout code or CMS wiring — that is the web app's job.
- Video/animated banners — stills only here.

## Required inputs

- Headline/subcopy and whether the page will render them as HTML.
- Desktop canvas (typically 1920×600–800) and mobile canvas (typically 800×1000).
- Brand art/photo (licensed), logo SVG, palette hex.
- Target file-size budget (team default ≤200 KB per image).
- Focal point: what must never be cropped (face, product, logo).

## Exact commands

```bash
cd /opt/pod-pipeline
VC=/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli
```

Desktop banner, exact pixels, WebP delivery (verified: 1920×700 export at `ppi:72`):

```bash
magick -size 1920x700 xc:'#101312' /tmp/banner_bg.png
magick /tmp/banner_art.png -resize 1920x700^ -gravity center -extent 1920x700 /tmp/banner_art_fit.png
cat > /tmp/banner.json <<'JSON'
[{"command":"file.new","params":{"width":1920,"height":700,"units":"Pixels","colorMode":"rgb","backgroundContents":"transparent"}},
 {"command":"file.place","params":{"path":"/tmp/banner_bg.png"}},
 {"command":"file.place","params":{"path":"/tmp/banner_art_fit.png"}},
 {"command":"document.export","params":{"path":"/tmp/banner_desktop.png","format":"png"}},
 {"command":"document.export","params":{"path":"/tmp/banner_desktop.png","format":"png","ppi":72}}]
JSON
$VC run --commands /tmp/banner.json
identify -format '%f %wx%h %m %b\n' /tmp/banner_desktop.webp /tmp/banner_desktop.png
```

If type must be baked in (no HTML layer), add before the exports:

```json
{"command":"text.create","params":{"x":120,"y":300,"text":"MADE FOR THE LONG WAY ROUND","font":"FreeSans","style":"Bold","size":64,"color":"#efe6cf"}}
```

Mobile composition — a separate 800×1000 canvas, not a blind crop of the desktop:

```bash
magick -size 800x1000 xc:'#101312' /tmp/banner_mobile_bg.png
magick /tmp/banner_art.png -resize 800x1000^ -gravity center -extent 800x1000 /tmp/banner_art_mobile.png
cat > /tmp/banner_mobile.json <<'JSON'
[{"command":"file.new","params":{"width":800,"height":1000,"units":"Pixels","colorMode":"rgb","backgroundContents":"transparent"}},
 {"command":"file.place","params":{"path":"/tmp/banner_mobile_bg.png"}},
 {"command":"file.place","params":{"path":"/tmp/banner_art_mobile.png"}},
 {"command":"document.export","params":{"path":"/tmp/banner_mobile.png","format":"png"}}]
JSON
$VC run --commands /tmp/banner_mobile.json
identify -format '%f %wx%h %m %b\n' /tmp/banner_mobile.webp
```

Inspect a centre crop to sanity-check the mobile focal point:

```bash
magick /tmp/banner_desktop.png -gravity center -crop 800x700+0+0 +repage /tmp/banner_crop_check.png
```

## Workflow

1. Decide whether the headline is HTML text (preferred: SEO, accessibility, i18n) or baked.
2. Agree the focal point and the desktop/mobile canvases before placing art.
3. Place art to cover the canvas; never stretch — crop or scale proportionally.
4. If baking type, keep it inside the central band that survives the mobile crop.
5. Export PNG; convert to lossy WebP with `photocraft-cli convert /tmp/banner_desktop.png /tmp/banner_desktop.webp --quality 82` (VectorCraft WebP is lossless-only, verified) and check bytes.
6. Build the mobile canvas separately; verify the subject still reads at 800 px wide.
7. Record canvas sizes, focal point and file sizes for the web team.
8. Confirm the page will set explicit `width`/`height`/`srcset`; the image alone cannot fix CLS.

## Acceptance gates

- Exact dimensions: desktop 1920×600–800, mobile 800×1000 — verified with `identify`.
- WebP/PNG byte size within budget (team default ≤200 KB); PNG is the working copy, lossy WebP is the delivery.
- Mobile composition preserves the focal point; nothing critical is cropped out.
- Text (if baked) has ≥4.5:1 contrast and stays out of the outer 60 px.
- No upscaled art; source resolution explains the final pixels.
- No AVIF delivered: these releases have no AVIF exporter (verified); use WebP.
- Type as HTML where the page supports it; if baked, the copy is final and localised.

## Refusal conditions

- No browser automation: cannot verify the live page, LCP or CLS from here. Say so plainly.
- No AVIF export in VectorCraft 0.21.1 / PhotoCraft 0.20.2 — do not promise it.
- Unlicensed imagery/fonts — refuse.
- Cannot guarantee Core Web Vitals: image weight is one input, hosting and JS are others.
- No dry-run flag — export to new paths and inspect.

## Worked examples

**1. Storefront hero.** 1920×700 desktop with the product art right of centre and no baked
headline (HTML renders it). Export PNG, convert to lossy WebP with PhotoCraft `--quality 82`; if it exceeds 200 KB, reduce quality in
steps of 4 and re-check bytes rather than cropping the art. Mobile is a separate 800×1000
composition with the product centred.

**2. Campaign strip.** 1920×600 with a short baked line at 64 px inside the central 1200 px so
it survives a narrow viewport. Export WebP + PNG, then crop the desktop at 800×600 from the
centre to preview what a mid-width layout would show.

## Pitfalls

- **Baked text blocks localisation and hurts SEO** — prefer HTML type; bake only for flat images.
- **One crop cannot serve both canvases** — build the mobile composition deliberately.
- **Gradients inflate WebP size** — check bytes after every export change.
- **`ppi` controls pixel count** — `ppi:72` on a px document keeps 1 px per point; a larger
  ppi silently multiplies the canvas.
- **Retina** — deliver at least 2× the CSS width when the layout uses high-DPI images.
- **No stretched art** — scale proportionally and crop; distorted hero art is an instant reject.
- **`file.place` keeps native pixels** — a 4000 px photo overflows a 1920 canvas; resize/extent
  first. `backgroundContents` only accepts `transparent|white` (verified), so grounds are images.
