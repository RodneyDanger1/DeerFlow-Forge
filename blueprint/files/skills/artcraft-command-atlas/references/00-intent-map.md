# Intent → command map

Use this when the user describes a job in designer language. Find the intent, take the command id,
then read the full params text from the catalogue before running:

```bash
$VC commands | python3 -c 'import json,sys; c=json.load(sys.stdin); print(next(x["params"] for x in c if x["id"]=="OBJECT.ID"))'
$PC commands --json | python3 -c 'import json,sys; c=json.load(sys.stdin); print(next(x["params"] for x in c if x["id"]=="OBJECT.ID"))'
```

Ids below are verified against the snapshot (2026-11-05). Some intents are CLI workflows, not engine
commands; they are marked `CLI` and link to a recipe. If no row matches, search by label/menu:

```bash
$VC commands | python3 -c 'import json,sys; c=json.load(sys.stdin); [print(x["id"], "—", x["label"]) for x in c if "KEYWORD" in (x["label"]+" "+" ".join(x["menu"])).lower()]'
```

## VectorCraft intents

| Intent | Command(s) | Notes |
|---|---|---|
| New document | `file.new` | units, artboards, bleed, colour mode, background |
| Open a file | `file.open` | use `file.list` to see open documents |
| Save in place | `file.save` | `file.saveAs` changes the working path; `file.saveCopy` preserves it |
| Place a raster/PDF/SVG | `file.place` | raster at physical size (ppi), `rect` for exact fit |
| Export SVG/PNG/PDF | `document.export` | `format`, `ppi`/`scale`, `artboard(s)`, `selectedOnly`, `svg` options |
| Export PDF specifically | `document.exportPdf` | check fonts/transparency/colour; not a press proof |
| Export EPS | `document.exportEps` | legacy exchange; transparency may flatten |
| Export DXF | `document.exportDxf` | CAD exchange; check units |
| Export for screens | `document.exportForScreens` | multiple sizes/presets; verify each output |
| List installed export formats | `document.formats` | confirms format support before export |
| Inspect document | `document.inspect` | JSON snapshot; `document.json` full serialization |
| Set document units | `document.setUnits` | affects numeric params interpreted in units |
| Set colour mode | `file.documentColorMode` | RGB/CMYK; print colour still needs proof |
| Select everything | `select.all` | required before many trace/path commands |
| Clear selection | `select.none` | later commands then use their explicit `ids` |
| Select by fill/stroke | `select.same.fillColor`, `select.same.strokeColor` | then paint/transform |
| Select stray points | `select.object.strayPoints` | clean-up precursor |
| Trace an image | `imageTrace.make` | select raster first; settings in `params.params` |
| Expand a trace | `imageTrace.expand` | makes editable paths; required before path work |
| Simplify paths | `object.path.simplify` | level 0–100; compare anchor counts |
| Clean up paths | `object.path.cleanUp` | removes stray/empty/unpainted items |
| Smooth anchors | `object.path.smooth` | gentler than simplify; inspect curves |
| Add anchor points | `object.path.addAnchorPoints` | more control, larger file |
| Join/open paths | `path.join`, `path.close` | verify exact ids in the `path` group |
| Outline a stroke | `object.path.outlineStroke` | stroke becomes filled outlines |
| Offset a path | `object.path.offsetPath` | joins/miter affect corners; not a stroke width |
| Unite shapes | `object.pathfinder.unite` | flattens palette/objects; work on a copy |
| Subtract front/back | `object.pathfinder.minusFront`, `object.pathfinder.minusBack` | stacking order decides the result |
| Intersect/exclude | `object.pathfinder.intersect`, `object.pathfinder.exclude` | boolean result may create many anchors |
| Divide overlaps | `object.pathfinder.divide` | splits into faces for recolouring |
| Trim/merge/crop/outline | `object.pathfinder.trim`, `object.pathfinder.merge`, `object.pathfinder.crop`, `object.pathfinder.outline` | Illustrator-compatible operations |
| Make compound path | `object.compoundPath.make` | holes/even-odd; release with `object.compoundPath.release` |
| Make compound shape | `object.compoundShape.make` | live shape boolean; expand with `object.compoundShape.expand` |
| Group/ungroup | `object.group`, `object.ungroup` | group changes structure and clipping context |
| Arrange stacking | `object.arrange.bringToFront`, `object.arrange.sendToBack`, `object.arrange.bringForward`, `object.arrange.sendBackward` | object-level, not layer-level |
| Align/distribute | `object.align`, `object.distribute`, `object.distributeSpacing` | choice of key object/anchors matters |
| Transform | `object.transform`, `object.transformAgain`, `object.transformEach` | repeat last transform / each object |
| Lock/hide | `object.lock`, `object.hide`, `.above`, `.otherLayers`, `.unselected` | protect finished art |
| New layer | `layer.new`, `layer.newSublayer` | then `layer.setCurrent` before adding |
| Move art to layer | `layer.move`, `layer.collectInNew` | move vs collect has different source handling |
| Duplicate/delete layer | `layer.duplicate`, `layer.delete` | delete is destructive; check target |
| Merge/flatten layers | `layer.merge`, `layer.flatten` | destructive; keep a layered master |
| Clipping mask | `layer.clippingMask.toggle` | clipping object above content |
| New artboard | `artboard.new`, `artboard.duplicate` | `document.export` chooses artboard |
| Fit artboard | `artboard.fitToArt`, `artboard.fitToSelection` | changes output bounds |
| Rearrange artboards | `artboard.rearrange`, `artboard.reorder` | check the resulting order before export |
| Recolour artwork | `recolor.colors`, `recolor.apply`, `recolor.reduce` | verify every output hex |
| Create swatch | `swatch.new`, `swatch.newGroup` | name/spot/global options |
| Edit swatch | `swatch.edit`, `swatch.setSpot` | global edits affect all users of the swatch |
| List swatches | `swatch.list` | audit the palette before a brand pass |
| Apply gradient | `gradient.presets.apply`, `paint.setFill` | geometry via `paint.setGradientGeom` |
| Paint fill/stroke | `paint.setFill`, `paint.setStroke` | accepts colour/none/gradient/swatch per schema |
| Remove paint | `paint.none` | clears fill or stroke depending on target |
| Sample colour | `paint.sampleColor` | from art/placed image; record result |
| Apply graphic style | `graphicStyle.apply` | can overwrite local appearance |
| Add effect | `effect.apply` | live appearance; expand before some exports |
| Expand effect | `effect.expandAppearance` | irreversible; keep master |
| Opacity mask | `transparency.makeOpacityMask` | release/enable/link commands exist |
| Set opacity/blend | `transparency.set` | verify on final background |
| Create text | `text.create` | content + font/style/size/position |
| Set text style | `text.setStyle`, `text.setFormat` | range vs whole object |
| List fonts | `text.fontList` | installed families; not a licence |
| Find missing fonts | `text.missingFonts`, `text.findFontFiles` | resolve before export |
| Replace font | `text.replaceFont` | across document; record fallback/licence |
| Area type options | `text.areaOptions` | rows/columns/inset for paragraph areas |
| Thread text | `text.thread.create`, `text.thread.add`, `text.thread.info` | linked text frames |
| Text on a path | `text.createInPath` | path must exist; check start offset |
| Fit headline | `text.fitHeadline`, `type.fitHeadline` | auto-size to area; verify bounds |
| Create outlines | `type.createOutlines` | irreversible; keep live text master |
| Area ↔ point type | `type.convertToAreaType`, `type.convertToPointType` | changes wrapping behaviour |
| Change case | `type.changeCase` | UPPER/lower/title per params |
| Vertical type | `type.orientation.vertical`, `type.orientation.horizontal` | layout only |
| Create symbol | `symbol.new`, `symbol.place` | editing symbol changes all instances |
| Break symbol link | `symbol.breakLink` | instance becomes independent |
| Update symbols | `symbol.update` | propagates edits; confirm scope |
| New variable | `variable.define`, `variable.bind` | data-driven art; test one record |
| New dataset | `dataset.new`, `dataset.set`, `dataset.capture` | validate every row/output |
| Set up print | `print.setup`, `print.preview` | not a physical proof |
| Tile print | `print.tiling.set`, `print.tiling` | large-format tiling |
| Export web assets | `webExport.settings`, `document.exportForWeb` | check exact pixel sizes |
| Add interactivity | `svgInteractivity.*` | web SVG only; no print effect |
| Run a plugin exporter | `plugin.info`, `document.export` | format `plugin.<id>`; query first |

## PhotoCraft intents

| Intent | Command(s) | Notes |
|---|---|---|
| New/open image | `file.new`, `file.openAs` | CLI `run`/`convert` also opens |
| Inspect document | `info --compact` (CLI) | size/mode/depth/layers/warnings |
| Resize image | `image.imageSize` | `keepPrintSize`/resample decide pixel vs print size |
| Crop | `image.crop` | destructive unless pixels preserved |
| Canvas size | `image.canvasSize` | anchor decides existing-pixel position |
| Rotate/flip | `image.imageRotation.*` | canvas vs layer rotation differ |
| Trim borders | `image.trim` | trims transparency/border colour per params |
| Convert to RGB/CMYK/Lab | `image.mode.rgb`, `image.mode.cmyk`, `image.mode.lab` | CMYK conversion is not proof |
| 8/16/32-bit | `image.mode.bits8`, `image.mode.bits16`, `image.mode.bits32` | tool support varies by filter |
| Auto tone/contrast/colour | `image.autoTone`, `image.autoContrast`, `image.autoColor` | one-click corrections; verify |
| Levels/curves | `image.adjustments.levels`, `image.adjustments.curves` | fix cast/contrast before saturation |
| Exposure/vibrance | `image.adjustments.exposure`, `image.adjustments.vibrance` | subtle; protect brand colours |
| Hue/saturation | `image.adjustments.hueSaturation` | target channels; check skin |
| Colour balance | `image.adjustments.colorBalance` | shadows/mids/highlights |
| Black & white | `image.adjustments.blackWhite` | channel mix, not desaturate |
| Photo filter | `image.adjustments.photoFilter` | warming/cooling |
| Channel mixer | `image.adjustments.channelMixer` | CMYK/duotone prep |
| Shadows/highlights | `image.adjustments.shadowsHighlights` | recover clipped areas |
| Replace colour | `image.adjustments.replaceColor` | targeted hue replacement |
| Match colour | `image.adjustments.matchColor` | source/target; check result |
| Gradient map | `image.adjustments.gradientMap` | tonal mapping |
| Selective colour | `image.adjustments.selectiveColor` | CMYK-oriented |
| Invert/posterize/threshold | `image.adjustments.invert`, `.posterize`, `.threshold` | destructive; keep original |
| Equalize | `image.adjustments.equalize` | can blow highlights |
| Colour lookup/LUT | `image.adjustments.colorLookup`, `file.export.colorLookupTables` | LUT omits masks/clipping |
| Auto/quick export | `file.export.quickExport`, `file.export.presets.*` | verify path/format/bytes |
| Export layers | `file.export.layersToFiles` | naming/hidden layers matter |
| Export artboards | `file.export.artboardsToFiles`, `file.export.artboardsToPdf` | one file per artboard |
| Export paths to Illustrator | `file.export.pathsToIllustrator` | vector handoff |
| Save for web legacy | `file.export.saveForWebLegacy` | format/preset-specific |
| Batch automation | `CLI batch`, `file.automate.batch` | prefer CLI; use `--stop-on-error` |
| Create droplet | `file.automate.createDroplet`, `file.automate.runDroplet` | recorded action; validate |
| Subject select | `select.subject` | refine and inspect the mask |
| Sky select | `select.sky` | inspect horizon/edge |
| Colour range select | `select.colorRange` | tolerance/fuzziness |
| Magic wand | `select.magicWand` | contiguous vs global |
| Quick select | `select.quick` | brush-driven; size matters |
| Refine edge | `select.refineEdge` | hair/edge halos; check black/white |
| Feather/smooth/expand/contract | `select.modify.feather`, `.smooth`, `.expand`, `.contract` | selection-only; apply to mask |
| Save/load selection | `select.saveSelection`, `select.loadSelection` | alpha channels; name them |
| Selection to path | `select.toWorkPath` | tolerance; becomes vector path |
| Selection to shape | `select.convertToShape` | shape layer, editable |
| Layer mask from selection | `layer.layerMask.revealSelection` | non-destructive; check density |
| Layer mask all | `layer.layerMask.revealAll`, `.hideAll`, `.apply`, `.delete` | apply/delete destructive |
| Clipping mask | `layer.createClippingMask`, `layer.releaseClippingMask` | base layer below clipped content |
| New adjustment layer | `layer.newAdjustmentLayer.levels` etc. | non-destructive vs `image.adjustments.*` |
| Fill layer | `layer.newFillLayer.solidColor`, `.gradient` | editable fill |
| Layer style | `layer.layerStyle.dropShadow` etc. | live effects; flatten for delivery |
| Layer group | `layer.new.group`, `layer.groupLayers` | organise before export |
| Duplicate/delete/arrange | `layer.duplicate`, `layer.delete`, `layer.arrange.*` | verify target layer |
| Merge/flatten | `layer.mergeDown`, `layer.mergeGroup`, `layer.flattenImage` | destructive; keep master |
| New channel | `channel.new`, `channel.newSpot` | alpha vs spot |
| Alpha channel from selection | `channel.new` (selection) / `select.saveSelection` | name for reuse |
| Spot channel | `channel.newSpot`, `channel.mergeSpot` | print separations |
| Create type | `type.create` | font/size/colour/box |
| Edit type | `type.edit`, `type.setStyle` | range/paragraph styles |
| Rasterize type | `type.rasterize`, `type.rasterizeTypeLayer` | irreversible; keep live master |
| Type to work path | `type.createWorkPath` | vector handoff |
| Type to shape | `type.convertToShape` | editable vector shape |
| Warp text | `type.warpText` | style/amount; check bounds |
| OpenType features | `type.openType.*` | ligatures/numerals/styles |
| Missing fonts | CLI warning, `type.resolveMissingFonts` | resolve deliberately |
| Blur | `filter.blur.gaussianBlur`, `.motionBlur`, `.radialBlur` | destructive; radius/quality |
| Sharpen | `filter.sharpen.unsharpMask`, `.smartSharpen` | last, at final size |
| Denoise | `filter.noise.reduceNoise`, `.despeckle`, `.median`, `.dustAndScratches` | before sharpening |
| Add noise | `filter.noise.addNoise` | usually for texture; seed if available |
| Pixelate/stylize/distort | `filter.pixelate.*`, `filter.stylize.*`, `filter.distort.*` | creative effects; preserve original |
| Content-aware fill | `edit.contentAwareFill` | structure repair; check edges |
| Content-aware move | `paint.contentAwareMove` | moves+repairs; verify |
| Healing/patch | `paint.healingBrush`, `paint.patch` | behaviour unverified here |
| Dodge/burn/sponge | `paint.dodge`, `paint.burn`, `paint.sponge` | destructive local edits |
| Fill | `edit.fill`, `edit.fillForeground`, `edit.fillBackground` | target selection/layer/channel |
| Gradient fill | `gradient.fill.create`, `.set`, `.stop` | layer or paint gradient |
| Actions batch | CLI `batch --actions`, `--action`, `--stop-on-error`, `--naming` | action file may be actions.json/droplet/.atn |
| Run droplet | CLI `droplet FILE|DIR` | recorded automation; validate scope |
| Export LUT | `file.export.colorLookupTables` | size 2–129; masks omitted |
| Export data sets | `file.export.dataSetsAsFiles` | validate every record |
| Render video | `file.export.renderVideo` | timeline-dependent; verify frames |

## Routing rules when the intent is ambiguous

1. If the user names an Illustrator/Photoshop menu item, map it to the closest id **and** read its
   params/label; menu names do not always map 1:1.
2. If the job needs pixels → PhotoCraft; if it needs editable vectors → VectorCraft.
3. If it needs both, split: PhotoCraft for pixel cleanup, VectorCraft for trace/paths/export.
4. If no intent row exists, search labels/menus (command above); do not invent an id.
5. Record the chosen id and the catalogue line you read in the answer.
