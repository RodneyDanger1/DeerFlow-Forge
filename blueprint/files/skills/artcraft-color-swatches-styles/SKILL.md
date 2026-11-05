---
name: artcraft-color-swatches-styles
description: "Use when ArtCraft artwork needs controlled colour: named swatches/global/spot colours, fills/strokes, gradients, brand recolour, graphic styles, effects/appearance, opacity masks or stroke profiles. Exact ids, colour-space traps and print-safe recipes. Triggers: brand colours, swatches, gradient, recolor, graphic style, drop shadow, opacity mask, spot colour, stroke."
version: 1.0.0
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [artcraft, vectorcraft, color, swatches, gradients, recolor, appearance, effects]
    related_skills: [brand-system, artcraft-path-geometry, ad-creative, artcraft-command-atlas]
---

# Colour, swatches and styles

Colour is a controlled asset, not a picker result. This skill applies named colours, gradients,
brand recolouring, graphic styles, live effects and opacity masks with a record of what changed.
Full map: `artcraft-command-atlas/references/vc-color-style.md`.

## When to use / not use

- Use to define/apply brand swatches, spot/global colours, fills/strokes and gradients.
- Use to recolour a variant, apply a reusable graphic style, add/expand effects, or build an opacity
  mask/stroke profile.
- Not for palette selection/contrast rules (`brand-system`, `ad-creative`), CMYK press proofing, or
  photo colour grading (PhotoCraft adjustment skills).

## Inputs

- Approved palette: names, hex, print equivalents, spot/global intent.
- Target objects/layers and the appearance slot (fill/stroke/effect).
- Colour space/mode (RGB vs CMYK), output format, and proof expectations.
- Source copy; colour drift tolerance.

## Exact commands (Linux VPS)

```bash
VC=/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli
# Linux VPS only. From Windows: ssh -i ~/.ssh/id_ed25519_hostinger root@179.197.88.181 'cd /opt/pod-pipeline && bash -s' < script.sh; stop if unavailable.
```

Swatches: `swatch.new`, `swatch.newGroup`, `swatch.edit`, `swatch.list`, `swatch.duplicate`,
`swatch.delete`, `swatch.setSpot`, `swatch.spotOptions`, `swatch.addUsedColors`, `swatch.unused`,
`swatch.merge`, `swatch.library.list/get/add`, `swatch.library.save/load`.
Paint/stroke: `paint.setFill`, `paint.setStroke`, `paint.none`, `paint.swap`, `paint.sampleColor`,
`paint.invert`, `paint.complement`, `paint.editGradient`, `paint.setGradientGeom`, `stroke.set`,
`stroke.setAdvanced`, `stroke.widthProfile.add/delete/reset/list/set`.
Gradients: `gradient.presets.list`, `.apply`, `.save`, `.delete`, `gradient.selectStop`.
Recolour: `recolor.colors`, `recolor.apply`, `recolor.reduce`, `recolor.randomize`.
Styles/appearance: `graphicStyle.apply`, `.new`, `.list`, `.breakLink`, `.rename`, `.delete`,
`appearance.addFill`, `.addStroke`, `.addEffect`, `.clear`, `.reduceToBasic`, `.setItem`,
`.removeItem`, `.copyFrom`, `.moveItem`.
Effects/transparency: `effect.apply`, `.list`, `.setParams`, `.remove`, `.expandAppearance`,
`.duplicate`, `.move`, `transparency.set`, `transparency.makeOpacityMask`,
`.releaseOpacityMask`, `.enableOpacityMask`, `.disableOpacityMask`, `.linkOpacityMask`,
`.unlinkOpacityMask`, `.setOpacityMask`, `.opacityMaskInfo`, `.info`, `.toggleNewMasksClipping`.

## Decision table

| Goal | Use | Trap |
|---|---|---|
| Named brand colour | `swatch.new` (global/spot options) | global edits affect all users |
| Apply a fill/stroke | `paint.setFill`/`setStroke` | target selected object/appearance slot |
| Remove paint | `paint.none` | clears the active fill/stroke only |
| Gradient | `gradient.presets.apply` + `paint.setGradientGeom` | stops/direction must be verified |
| Recolour a variant | `recolor.colors` → `recolor.apply` | nearest-colour mapping drifts |
| Reduce palette | `recolor.reduce` | can merge distinct brand colours |
| Reusable style | `graphicStyle.apply` | overwrites local appearance |
| Add shadow/glow | `effect.apply` | live effect; expand before some exports |
| Opacity mask | `transparency.makeOpacityMask` | compositing, not a path boolean |
| Stroke shape | `stroke.set`/`setAdvanced` | cap/join/alignment affect geometry |
| Outline stroke | `object.path.outlineStroke` | see path-geometry skill |

## Workflow / state machine

`palette → swatches → apply paint → gradients/styles → effects/masks → export → colour audit`.
Record the final hex/CMYK/spot values; screen colour is not press proof.

1. Copy source; lock the approved palette (names/hex/print equivalents).
2. Create/update swatches; mark spot/global deliberately; audit unused/duplicates.
3. Apply fill/stroke/gradient; verify the target and appearance slot.
4. Recolour variants; compare every output colour to the palette; fix drift.
5. Apply graphic styles/effects; expand only on a delivery copy.
6. Build opacity masks only when compositing is intended; check final background.
7. Export; sample pixels/colour values from the artifact; record the table.

## Acceptance gates

- Every applied colour is in the approved palette (or an explicitly approved addition).
- Spot/global intent is correct; no accidental spot separation.
- Gradient direction/stops match the design; no banding at print size.
- Recolour preserves the intended number of colour roles; no merged brand colours.
- Effects/masks render correctly on the final background; expanded copies are labelled.
- Export artifact colour-sampled; source/master retained; colour table recorded.
- CMYK/print claims are flagged as unverified unless a physical proof exists.

## Refusals / failure modes

- No invented hex values/palette entries; derive from the approved source or ask.
- Do not treat an RGB screen render as CMYK proof; no press claim without proof.
- Do not expand effects/outline strokes on the only master.
- Do not recolour a multi-colour trace without accepting palette flattening.
- Spot colours are not RGB approximations; record the actual separation.
- Do not use opacity masks as a substitute for clipping/path booleans.

## Worked recipes

**1. Brand palette.** `swatch.new` for each name/hex → `swatch.list` audit → apply via `paint.setFill`
→ export → sample artifact colours → record hex/print equivalents.

**2. Recolour a badge.** `recolor.colors` with approved list → `recolor.apply` → export SVG/PNG →
compare every fill; adjust drift deliberately; keep original.

**3. Gradient artwork.** `gradient.presets.apply` → `paint.setGradientGeom` (angle/position) →
`gradient.selectStop`/`paint.editGradient` for stops → export at print size; check banding.

**4. Graphic style + effect.** `graphicStyle.apply` → `effect.list`/`effect.setParams` → render →
`effect.expandAppearance` on a delivery copy; keep live style master.

**5. Opacity mask.** Select mask art/object → `transparency.makeOpacityMask` → verify on black/white
backgrounds; release/link as needed; export a flattened copy for consumers that cannot read it.

## Agent operating protocol

**Preflight:** approved palette, target objects, colour space, output/proof; copy; read params.

**Execution loop:** one colour/style operation; inspect appearance/colour values; render; then next.

**Evidence contract:** swatches/paint/effect ids, colour table, artifact samples, proof status;
exit 0 alone is not proof.

**Stop/escalate:** no approved palette; unlicensed spot/CMYK proof needed; ambiguous target; effect
expansion without a copy; colour drift outside tolerance.

**Never:** invent brand colours; claim press colour from RGB; flatten the master; use opacity masks
as booleans; ignore a spot/global side effect.

## Sources & verification

- **VERIFIED:** all ids above exist in the 918-row catalogue; swatch/paint/gradient/effect params read;
  `text.fontList` unrelated; colour tools return null for adjustments-style commands but paint/style
  commands return structured results.
- **ATLAS:** `artcraft-command-atlas/references/vc-color-style.md`, `00-intent-map.md`.
- **DOCS:** local ArtCraft docs; official README; Adobe swatch/gradient/effects concepts.
