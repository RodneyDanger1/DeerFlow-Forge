---
name: artcraft-selections-masks
description: "Use when PhotoCraft pixels need a controlled region: subject/sky/colour-range selection, refine edge, feather/expand/contract, quick mask, save/load alpha channels, layer masks, clipping masks, content-aware fill and patch. Exact PhotoCraft ids with verification gates. Triggers: select subject, cut out, mask, refine edge, alpha channel, clipping mask, content aware fill, hair mask."
version: 1.0.0
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [photocraft, selection, mask, channel, cutout, refine-edge, content-aware]
    related_skills: [artcraft-image-cleanup, ai-diffusion-artifact-cleanup, artcraft-photocraft-adjustments-filters, artcraft-command-atlas]
---

# PhotoCraft selections and masks

A selection is a temporary region; a mask is persistent; an alpha channel is stored data. Keep the
layered master and inspect masks on black and white. Full map:
`artcraft-command-atlas/references/pc-selection-channel.md`.

## When to use / not use

- Use to cut out a subject, replace a sky, isolate a colour range, refine hair/edges, or localise an
  adjustment.
- Use to save/reload selections as alpha channels, build layer/clipping masks, or run content-aware
  fill/patch.
- Not for vector tracing (`artcraft-vector-trace`), AI-art cleanup pipelines
  (`ai-diffusion-artifact-cleanup`), or global colour grading (adjustments skill).

## Inputs

- Source file, rights, intended composite/background.
- Target region (subject/sky/colour/object) and acceptable halo/edge behaviour.
- Feather/refine amount, mask persistence, output format/transparency.
- Layered master and delivery copy.

## Exact commands (Linux VPS)

```bash
PC=/opt/craft/photocraft/photocraft-0.20.2-linux-x86_64/bin/photocraft-cli
cd /opt/pod-pipeline
# Linux VPS only. From Windows: ssh -i ~/.ssh/id_ed25519_hostinger root@179.197.88.181 'cd /opt/pod-pipeline && bash -s' < script.sh; stop if unavailable.
```

Select: `select.all`, `select.deselect`, `select.inverse`, `select.rect`, `select.quick`,
`select.subject`, `select.sky`, `select.colorRange`, `select.magicWand`, `select.lasso`,
`select.magneticLasso`, `select.object`, `select.similar`, `select.grow`, `select.focusArea`,
`select.refineEdge`, `select.modify.feather`, `.smooth`, `.expand`, `.contract`, `.border`,
`select.transformSelection`, `select.saveSelection`, `select.loadSelection`, `select.toWorkPath`,
`select.convertToShape`, `select.editInQuickMaskMode`, `select.loadLuminosity`, `select.loadSelection`.
Channels: `channel.new`, `channel.newSpot`, `channel.list`, `channel.target`, `channel.target.composite`,
`channel.target.layerMask`, `channel.duplicate`, `channel.delete`, `channel.rename`, `channel.move`,
`channel.setVisible`, `channel.options`, `channel.split`, `channel.merge`, `channel.mergeSpot`.
Masks/compositing: `layer.layerMask.revealAll`, `.hideAll`, `.revealSelection`, `.hideSelection`,
`.delete`, `.apply`, `.enabled`, `.linked`, `.fromTransparency`, `.edit`, `layer.createClippingMask`,
`layer.releaseClippingMask`, `edit.contentAwareFill`, `paint.contentAwareMove`, `paint.patch`,
`paint.healingBrush`.

## Decision table

| Need | Use | Trap |
|---|---|---|
| Subject cutout | `select.subject` → `select.refineEdge` | proposal; inspect hair/edges |
| Sky replace | `select.sky` | horizon/foliage edges |
| Specific colour | `select.colorRange`/`select.magicWand` | contiguous vs global; fuzziness |
| Object select | `select.object` | layer/object scope |
| Feather/expand | `select.modify.*` | applied to selection, not mask after |
| Hair/edge refine | `select.refineEdge` | over-refine creates halos |
| Save selection | `select.saveSelection`/`channel.new` | name alpha channel |
| Load selection | `select.loadSelection` | channel must exist |
| Non-destructive mask | `layer.layerMask.revealSelection` | inspect on black/white |
| Apply/delete mask | `layer.layerMask.apply`/`delete` | destructive; keep copy |
| Clipping mask | `layer.createClippingMask` | base layer below |
| Fill removed object | `edit.contentAwareFill` | structure/edges; verify |
| Move object + repair | `paint.contentAwareMove` | complex backgrounds fail |

## Workflow / state machine

`inspect → copy → rough select → refine/modify → mask/save → composite check → export`.
A selection that looks good on the checkerboard may fail on black or white.

1. Copy source; inspect mode/depth/layers.
2. Rough selection (`select.subject`/`sky`/`colorRange`/`quick`).
3. Refine/modify (`select.refineEdge`, feather/smooth/expand/contract); check black/white.
4. Persist (`saveSelection`/alpha channel) or convert to layer mask.
5. Composite on the real background; fix halos/spill.
6. Export delivery copy; keep the layered master and channel names.

## Acceptance gates

- Mask/selection covers exactly the intended region; no holes/missing islands.
- Edge quality acceptable on black and white; no white/coloured halo.
- Alpha channel saved/loaded with a meaningful name; mask non-destructive where required.
- Clipping base/content order correct; mask enabled/linked as intended.
- Content-aware fill has no obvious repeated structure/seams.
- Delivery transparent where expected; artifact verified; master retained.

## Refusals / failure modes

- Do not claim a perfect cutout from one click; content-aware selection is a proposal.
- Do not apply/delete a mask on the only master; keep a copy.
- Do not confuse selection feathering with mask feathering after creation.
- Do not use content-aware fill for large missing structures; regenerate/reshoot if it fails.
- Spot/alpha channels are not interchangeable; record the type.
- No browser preview; proof is the rendered PNG/composite.

## Worked recipes

**1. Subject cutout.** `select.subject` → `select.refineEdge` → `layer.layerMask.revealSelection` →
export PNG; verify on black/white and at 100 %.

**2. Sky replacement.** `select.sky` → `select.modify.feather` → mask → composite new sky → check
horizon; export.

**3. Save/reload a selection.** `select.colorRange` → `select.saveSelection` (name) → later
`select.loadSelection`; verify channel in `channel.list`.

**4. Content-aware remove.** `select.rect`/lasso around object → `edit.contentAwareFill` → inspect
seams/texture; if poor, retry with a tighter region or regenerate.

**5. Clipping adjustment.** Base layer + clipped adjustment layer above →
`layer.createClippingMask`; verify only the base is affected.

## Agent operating protocol

**Preflight:** copy; inspect; define region/mask persistence; read params.

**Execution loop:** rough select → refine → mask/alpha → composite check; one change at a time.

**Evidence contract:** command ids, selection/mask/channel names, black/white renders, artifact path;
exit 0 alone is not proof.

**Stop/escalate:** no acceptable edge after refine; missing channel; destructive mask on master;
complex fill fails; rights unclear.

**Never:** claim a perfect mask without renders; apply/delete the only mask; invent channel names;
use content-aware fill as a structural repair guarantee.

## Sources & verification

- **VERIFIED:** all ids above exist in the 965-row registry; select/mask/channel params read from
  `commands --json`; PhotoCraft positional run/out behavior.
- **ATLAS:** `artcraft-command-atlas/references/pc-selection-channel.md`, `recipes-photocraft.md`.
- **DOCS:** local ArtCraft docs; official README; Adobe selection/refine-edge concepts.
