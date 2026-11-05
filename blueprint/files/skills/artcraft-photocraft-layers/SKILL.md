---
name: artcraft-photocraft-layers
description: "Use when a PhotoCraft document needs layer structure: groups, stacking/arrange, masks, clipping masks, layer styles, smart objects, adjustment/fill layers, layer comps, history and per-layer export. Exact ids, order/ownership traps, verification gates. Triggers: PhotoCraft layers, group layers, layer mask, clipping mask, smart object, layer style, layer comp, flatten."
version: 1.0.0
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [photocraft, layers, masks, smart-objects, layer-styles, layer-comps, flatten]
    related_skills: [artcraft-selections-masks, artcraft-photocraft-adjustments-filters, artcraft-batch-automation, artcraft-command-atlas]
---

# PhotoCraft layers and smart objects

The layer stack is the document's logic: visibility, masks, clipping, styles and smart-object links
change what every export contains. Load **artcraft-command-atlas**, then read
`references/pc-file-document-layer.md` for the full 224-command layer family.

## When to use / not use

- Use to create/group/arrange/merge layers, build masks or clipping masks, apply layer styles, work
  with smart objects, create adjustment/fill layers, manage layer comps, or export layers.
- Use when an export shows the wrong content because of visibility, mask, clipping or stacking.
- Not for selection/refine-edge (`artcraft-selections-masks`), global colour grading
  (`artcraft-photocraft-adjustments-filters`), or batch folders (`artcraft-batch-automation`).

## Inputs

- Source PSD/document + rights; intended composite and output.
- Layer ownership: which art belongs to which layer/group; which layers are hidden/locked.
- Mask/clipping intent; smart-object source files; style/adjustment scope.
- Master (layered) vs delivery (flattened) copy.

## Exact commands (Linux VPS)

```bash
PC=/opt/craft/photocraft/photocraft-0.20.2-linux-x86_64/bin/photocraft-cli
cd /opt/pod-pipeline
# Linux VPS only. From Windows: ssh -i ~/.ssh/id_ed25519_hostinger root@179.197.88.181 'cd /opt/pod-pipeline && bash -s' < script.sh; stop if unavailable.
$PC info /tmp/source.psd --compact
```

Core ids (read full params before use):

- Create/select: `layer.new.layer`, `layer.new.group`, `layer.groupLayers`, `layer.select`,
  `layer.duplicate`, `layer.delete`, `layer.setProps`, `layer.moveTo`, `layer.translate`.
- Arrange: `layer.arrange.bringForward`, `.sendBackward`, `.bringToFront`, `.sendToBack`,
  `.reverse`.
- Masks/clipping: `layer.layerMask.revealAll`, `.hideAll`, `.revealSelection`, `.hideSelection`,
  `.delete`, `.apply`, `.enabled`, `.linked`, `.fromTransparency`, `.edit`,
  `layer.createClippingMask`, `layer.releaseClippingMask`, `layer.maskAllObjects`.
- Merge/flatten: `layer.mergeDown`, `layer.mergeGroup`, `layer.flattenImage`.
- Fill/adjustment: `layer.newFillLayer.solidColor`, `.gradient`, `.pattern`,
  `layer.newAdjustmentLayer.brightnessContrast`, `.levels`, `.curves`, `.exposure`, `.vibrance`,
  `.hueSaturation`, `.colorBalance`, `.blackWhite`, `.photoFilter`, `.channelMixer`, `.invert`,
  `.posterize`, `.threshold`, `.gradientMap`, `.selectiveColor`, `.colorLookup`.
- Styles: `layer.layerStyle.dropShadow`, `.innerShadow`, `.outerGlow`, `.innerGlow`, `.stroke`,
  `.colorOverlay`, `.gradientOverlay`, `.patternOverlay`, `.bevelEmboss`, `.satin`,
  `.replace`, `.clear`, `.copyLayerStyle`, `.pasteLayerStyle`, `.hideAllEffects`,
  `.showAllEffects`, `.blendingOptions`, `.globalLight`, `.scaleEffects`.
- Smart objects: `layer.smartObjects.convertToSmartObject`, `.convertToLayers`,
  `.convertToEmbedded`, `.convertToLinked`, `.newSmartObjectViaCopy`, `.editContents`,
  `.saveContents`, `.replaceContents`, `.relinkToFile`, `.updateModifiedContent`,
  `.updateChanged`, `.updateAllModifiedContent`, `.rasterize`, `.exportContents`,
  `.exportSvg`, `.updateSvg`, `.updateVectorSource`.
- Comps/history: `layerComp.new`, `.update`, `.apply`, `.list`, `.duplicate`, `.rename`, `.delete`,
  `.reorder`, `.setOptions`, `history.undo`, `.redo`, `.newSnapshot`, `.selectSnapshot`,
  `.clear`, `.stepForward`, `.stepBackward`.
- Export: `file.export.layersToFiles`, `file.export.layerCompsToFiles`,
  `file.export.layersToFiles` (params path/format), `file.export.quickExport`.

## Decision table

| Goal | Use | Trap |
|---|---|---|
| New layer/group | `layer.new.layer`/`.new.group` | active layer decides target |
| Move selected art | `layer.moveTo`/`layer.translate` | source vs target layer |
| Reorder | `layer.arrange.*` | bring/send is relative to stack |
| Hide/lock context | `layer.setProps` | visibility affects exports |
| Mask from selection | `layer.layerMask.revealSelection` | selection must exist; check black/white |
| Apply/delete mask | `.apply`/`.delete` | destructive; keep copy |
| Clip adjustment | `layer.createClippingMask` | base layer below clipped content |
| Merge/flatten | `.mergeDown`/`.mergeGroup`/`.flattenImage` | destructive; keep layered master |
| Fill/adjustment layer | `layer.newFillLayer.*`/`.newAdjustmentLayer.*` | scope/mask/clipping |
| Layer style | `layer.layerStyle.*` | live effect; flatten only delivery |
| Smart object | `.convertToSmartObject` | source link/embedded behaviour |
| Update smart object | `.updateModifiedContent`/`.updateAllModifiedContent` | confirm scope |
| Snapshot/comp | `layerComp.new`/`history.newSnapshot` | comps are visibility states, not files |
| Export layers | `file.export.layersToFiles` | hidden/empty layers/naming |

## Workflow / state machine

`inspect → copy → structure → masks/clipping → styles/adjustments → merge/flatten? → export → verify`.
The layered master is the deliverable; flatten only a delivery copy.

1. `info --compact`: read layer tree, visibility, masks, mode, size; copy source.
2. Create/group/select/arrange layers; set the active layer before destructively editing.
3. Build masks (`layer.layerMask.*`) and clipping masks; inspect on black/white.
4. Add fill/adjustment layers or styles; keep them live for the master.
5. Convert to smart object when non-destructive transforms/filters are needed; record source.
6. Only flatten/merge on a copy; label the delivery file.
7. Export; verify per-layer/composite outputs and hidden/visible content.

## Acceptance gates

- Layer tree matches the intended structure; no art on the wrong layer/group.
- Masks/clipping show the intended content; non-destructive where required.
- Styles/adjustments are scoped correctly (layer, group, clip, mask).
- Smart-object source/link status recorded; updates propagate as intended.
- Flatten/merge only on the delivery copy; master retained.
- Export files exist with expected dimensions/names; hidden/empty layers handled deliberately.
- Source unchanged; report lists layer ids/paths and artifacts.

## Refusals / failure modes

- Do not flatten/merge the only master; keep a layered copy.
- Do not apply/delete a mask without a copy.
- Do not assume the active layer; check before editing.
- Do not treat a layer comp as a file; export it deliberately.
- Smart-object updates can change many instances; verify scope.
- Hidden layers may still affect some exports; verify the artifact.
- No dry-run; probe one step and inspect JSON.

## Worked recipes

**1. Organise a flat PSD.** `info --compact` → `layer.new.group` → `layer.groupLayers` →
`layer.arrange.*` → `layer.setProps` (names/visibility) → export a test composite.

**2. Masked adjustment.** Select region → `layer.layerMask.revealSelection` on an adjustment layer →
inspect mask; use `layer.layerMask.enabled`/`.linked` deliberately.

**3. Clipping stack.** Base layer + clipped fill/adjustment above →
`layer.createClippingMask` → verify only base is affected; release when editing.

**4. Smart object.** `layer.smartObjects.convertToSmartObject` → `.editContents`/`.saveContents` or
`.replaceContents` → `.updateModifiedContent`; record embedded/linked state.

**5. Delivery flatten.** Duplicate document/file → `layer.mergeGroup`/`layer.flattenImage` →
export; keep the layered master untouched.

**6. Per-layer export.** `file.export.layersToFiles` with path/format; inspect naming and skipped
hidden/empty layers.

## Agent operating protocol

**Preflight:** inspect layer tree/mode/size; copy; define target layers/mask/clip/scope; read params.

**Execution loop:** one structural/visual change; inspect tree/JSON; verify composite; then next.

**Evidence contract:** layer ids, mask/clip/style/smart status, artifact paths/sizes, hidden/visible
decisions; exit 0 alone is not proof.

**Stop/escalate:** ambiguous active layer; destructive merge/flatten without copy; missing smart-object
source; hidden/export mismatch; no layered master.

**Never:** flatten the master; assume layer order; claim per-layer export without checking files;
treat comps as files; invent ids/params.

## Sources & verification

- **VERIFIED:** all ids above exist in the 965-row PhotoCraft registry; layer/smart-object/layer-style/
  layer-comp/history params read from `commands --json`; `info --compact` and export commands.
- **ATLAS:** load `artcraft-command-atlas` and read `references/pc-file-document-layer.md`,
  `command-tips.md`, `recipes-photocraft.md`; use `references/command_lookup.py`.
- **DOCS:** local ArtCraft docs; official PhotoCraft README/CLI book; Photoshop layers/smart-object
  concepts (commands are ArtCraft's).
