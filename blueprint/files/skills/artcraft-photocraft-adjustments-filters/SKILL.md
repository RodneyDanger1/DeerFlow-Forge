---
name: artcraft-photocraft-adjustments-filters
description: "Use when PhotoCraft pixels need tone/colour correction or destructive filters: levels, curves, exposure, vibrance, hue/saturation, colour balance, B&W, photo filter, channel mixer, CMYK/Lab, auto tone, blur/sharpen/denoise, pixelate/stylize/distort and LUT export. Exact ids, order rules, gates. Triggers: colour grade, retouch tone, curves, levels, sharpen, denoise, black and white, CMYK, LUT, filter."
version: 1.0.0
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [photocraft, adjustments, filters, color, cmyk, sharpen, denoise, lut]
    related_skills: [artcraft-image-cleanup, artcraft-selections-masks, ai-diffusion-artifact-cleanup, artcraft-command-atlas]
---

# PhotoCraft adjustments and filters

Correct in an order: exposure/tone → colour balance → saturation → denoise → sharpen last. Prefer
adjustment layers for a master; destructive filters belong on a copy. Load **artcraft-command-atlas**, then read `references/pc-image-adjust.md` and `pc-filter-effect.md`.

## When to use / not use

- Use to correct cast/exposure/contrast, grade colour, convert B&W/CMYK, denoise/sharpen, or apply a
  creative filter/LUT.
- Use when an image needs a documented retouch/grade path with verification.
- Not for cutouts/masks (`artcraft-selections-masks`), AI-art cleanup pipelines
  (`ai-diffusion-artifact-cleanup`), or vector colour (`artcraft-color-swatches-styles`).

## Inputs

- Source + rights; colour mode/bit depth; intended output (screen/print).
- Defect/goal: cast, exposure, contrast, saturation, noise, sharpness, creative look.
- Adjustment-layer vs destructive route; proof expectations.
- Source copy and a delivery path.

## Exact commands (Linux VPS)

```bash
PC=/opt/craft/photocraft/photocraft-0.20.2-linux-x86_64/bin/photocraft-cli
cd /opt/pod-pipeline
# Linux VPS only. From Windows: ssh -i ~/.ssh/id_ed25519_hostinger root@179.197.88.181 'cd /opt/pod-pipeline && bash -s' < script.sh; stop if unavailable.
```

Tone/colour: `image.adjustments.levels`, `.curves`, `.exposure`, `.brightnessContrast`, `.vibrance`,
`.hueSaturation`, `.colorBalance`, `.blackWhite`, `.photoFilter`, `.channelMixer`, `.invert`,
`.posterize`, `.threshold`, `.gradientMap`, `.selectiveColor`, `.colorLookup`, `.equalize`,
`.shadowsHighlights`, `.replaceColor`, `.matchColor`, `.hdrToning`, `.colorLookup.list`,
`.desaturate`.
Auto: `image.autoTone`, `image.autoContrast`, `image.autoColor`.
Modes: `image.mode.rgb`, `.grayscale`, `.cmyk`, `.lab`, `.bits8`, `.bits16`, `.bits32`,
`.indexedColor`, `.duotone`, `.multichannel`.
Non-destructive: `layer.newAdjustmentLayer.brightnessContrast`, `.levels`, `.curves`, `.exposure`,
`.vibrance`, `.hueSaturation`, `.colorBalance`, `.blackWhite`, `.photoFilter`, `.channelMixer`,
`.invert`, `.posterize`, `.threshold`, `.gradientMap`, `.selectiveColor`, `.colorLookup`.
Filters: `filter.blur.gaussianBlur`, `.motionBlur`, `.radialBlur`, `.boxBlur`, `.surfaceBlur`,
`filter.sharpen.unsharpMask`, `.smartSharpen`, `.sharpen`, `.sharpenMore`, `.sharpenEdges`,
`filter.noise.reduceNoise`, `.despeckle`, `.median`, `.dustAndScratches`, `.addNoise`,
`filter.pixelate.*`, `filter.stylize.*`, `filter.distort.*`, `filter.other.highPass`, `.minimum`,
`.maximum`, `.offset`, `filter.lastFilter`.
LUT/export: `file.export.colorLookupTables`, `file.export.quickExport`.

## Decision table

| Goal | Use | Trap |
|---|---|---|
| Fix cast | `levels`/`curves`/`colorBalance` | clipping highlights/shadows |
| Contrast | `curves`/`brightnessContrast` | over-contrast loses detail |
| Saturation | `vibrance`/`hueSaturation` | skin/brand colours |
| B&W | `blackWhite` (channel mix) | desaturate is not the same |
| Creative look | `gradientMap`/`colorLookup`/photoFilter | preserve original |
| Denoise | `reduceNoise`/`despeckle`/`median`/`dustAndScratches` | before sharpening |
| Sharpen | `unsharpMask`/`smartSharpen` | last, final size; halos |
| Creative blur/distort | `filter.blur.*`/`filter.distort.*` | destructive; copy |
| CMYK | `image.mode.cmyk` | not a press proof |
| Non-destructive | `layer.newAdjustmentLayer.*` | masks/clipping affect scope |
| LUT | `file.export.colorLookupTables` | colour-only; masks omitted |

## Workflow / state machine

`copy → inspect → tone/exposure → colour balance → saturation → denoise → sharpen → proof/export`.
Keep the source; use adjustment layers for the master.

1. Copy/inspect mode/depth/resolution; decide screen vs print.
2. Correct exposure/levels/curves first; check histogram/clipping.
3. Balance colour; then saturation/vibrance; protect skin/brand colours.
4. Denoise before sharpening; use the least destructive filter.
5. Sharpen last at final size; inspect 100 % for halos.
6. Convert mode if print; flag CMYK/print as unverified without a proof.
7. Export; compare original/final; record adjustment chain and artifacts.

## Acceptance gates

- No clipped highlights/shadows unless intentional; histogram inspected.
- Colour cast removed; neutrals neutral where intended; brand colours match.
- Denoise did not erase structure; sharpen has no halos/crunch.
- Adjustment-layer path remains editable; destructive path has a copy.
- Mode/depth/output correct; CMYK/print proof status stated.
- Artifact dimensions/metadata verified; source unchanged.

## Refusals / failure modes

- Do not claim print colour from an RGB/screen render.
- Do not sharpen before the final resize; do not denoise after sharpening.
- Do not use auto tone as a final grade without checking skin/brand colours.
- Do not resample/convert modes without recording the source.
- LUT export cannot represent masks/clipping; do not claim otherwise.
- Healing/content-aware are not adjustment/filter fallbacks for structural repair.

## Worked recipes

**1. Correct a colour cast.** `curves`/`levels` → `colorBalance` → `vibrance` → export; compare
before/after and neutral patches.

**2. Product retouch.** `levels` → `hueSaturation` (small) → `reduceNoise` if needed →
`unsharpMask` at final size → export; pixel-sample brand colours.

**3. B&W conversion.** `blackWhite` with channel mix → `curves` for contrast → export; do not use
`desaturate` if control is needed.

**4. CMYK handoff.** `image.mode.cmyk` → export; record profile/vendor requirements; mark press proof
unverified.

**5. LUT.** Grade with adjustment layers → `file.export.colorLookupTables` size 33 → apply to test
images; masks are not represented.

## Agent operating protocol

**Lookup:** load **artcraft-command-atlas** and use `references/command_lookup.py` for exact ids/params.

**Preflight:** copy; inspect mode/depth; define output/proof; choose layer vs destructive; read params.

**Execution loop:** one correction step; inspect histogram/100 %; then next; preserve original.

**Evidence contract:** adjustment/filter ids/params, before/after stats/samples, mode, artifact,
proof status; exit 0 alone is not proof.

**Stop/escalate:** clipping cannot be recovered; structure lost; print proof required; missing
profile/vendor spec; destructive chain without copy.

**Never:** invent adjustment/filter params; claim CMYK proof; sharpen before resize; use LUT as a
mask-preserving export.

## Sources & verification

- **VERIFIED:** all ids above exist in the 965-row registry; adjustment/filter params read from
  `commands --json`; PhotoCraft positional run/out; LUT constraints from official CLI book.
- **ATLAS:** `references/pc-image-adjust.md`, `pc-filter-effect.md`,
  `recipes-photocraft.md`.
- **DOCS:** local ArtCraft docs; official README/CLI book; Adobe levels/curves/actions concepts.
