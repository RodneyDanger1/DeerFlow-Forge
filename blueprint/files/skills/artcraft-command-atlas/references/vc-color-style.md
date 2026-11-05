# VectorCraft Color Style

Auto-generated from the installed 918-command catalogue (snapshot 2026-11-05). Every row is a real command id; params are abbreviated from the catalogue's own text. Read the full params string with `$VC commands` before running. Tips are practical notes, not substitutes for the schema.

Commands: **168** across 16 groups.

## Coverage

`appearance` 16 · `brush` 18 · `color` 6 · `colorTheme` 4 · `effect` 8 · `eyedropper` 1 · `flattener` 6 · `gradient` 5 · `graphicStyle` 18 · `paint` 22 · `pattern` 4 · `recolor` 4 · `stroke` 10 · `svgInteractivity` 6 · `swatch` 23 · `transparency` 17

## `appearance` (16)

Appearance commands stack fills/strokes/effects on one object. Expand appearance before export if the consumer cannot render the stack.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `appearance.addEffect` | Add Effect |  | {…as effect.apply} same as effect.apply (an alias): {effect: id, params?: {…}, item?: appearance item index\|null, ids?, target?} → {ids, index, item} | disabled in catalogue snapshot |
| `appearance.addFill` | Add New Fill | Window > Appearance | {ids?\|id?, target?: "object"\|"contents"} add a fill on top of each selected object's own stack, on an image right below its Contents row, with its top fill's paint (type without one: its ch… | disabled in catalogue snapshot |
| `appearance.addStroke` | Add New Stroke | Window > Appearance | {ids?\|id?, target?} add a stroke on top of each selected object's own stack, on an image right below its Contents row, with its top stroke's paint (else the default stroke) and that stroke'… | disabled in catalogue snapshot |
| `appearance.clear` | Clear Appearance | Window > Appearance | {ids?\|id?, target?} leave each object one empty fill and stroke (None; a group none of its own) and reset its opacity and blend mode | disabled in catalogue snapshot |
| `appearance.copyFrom` | Eyedropper |  | {source: id, ids?, pickUp?, apply? (trees as eyedropper.setOptions, merged over the Eyedropper Options for this call), reverse?: bool, append?: bool, defaultsOnly?: bool} copy the attribute… | disabled in catalogue snapshot |
| `appearance.duplicateItem` | Duplicate Item | Window > Appearance | {index \| indices: [..] (paint-order item indices), to?: paint-order index of the copy (with several, of the lowest copy: they land together in their order; default: each right above its ite… | disabled in catalogue snapshot |
| `appearance.moveItem` | Reorder Appearance Item |  | {from: paint-order item index \| "contents", indices?: [..] (several items instead of from: they move as one block in their order, the lowest landing at `to`; a block landing next to the Con… | disabled in catalogue snapshot |
| `appearance.newArt` | New Art Appearance |  | {} what the next object drawn gets → {basic: New Art Has Basic Appearance, appearance: {items, effects} (the model's JSON; placed gradients relative to the unit box), opacity: 0..100, blend… |  |
| `appearance.reduceToBasic` | Reduce to Basic Appearance | Window > Appearance | {ids?\|id?, target?} keep only one visible fill and stroke (without ids: the Appearance panel's active row in place of the topmost one of its kind; else the topmost), without their own opaci… | disabled in catalogue snapshot |
| `appearance.removeItem` | Remove Item |  | {index \| indices: [..] (paint-order item indices), ids?\|id?, target?, aligned?: bool (index and item are rows of the first target's stack: each other target edits its equal one, as the Appe… | disabled in catalogue snapshot |
| `appearance.setActiveItem` | Select Appearance Item |  | {index: paint-order item index in the first selected object's stack \| null} make that fill/stroke row the target of the paint.setFill/setStroke, stroke.set/setAdvanced, paint.editGradient/s… | disabled in catalogue snapshot |
| `appearance.setItem` | Appearance Item |  | {index: paint-order item index, ids?\|id? (default: the selection), target?: "object"\|"contents", opacity?: 0..100, blend?: name, visible?: bool, weight?: pt (strokes), color?\|none?\|swatch?\|… | disabled in catalogue snapshot |
| `appearance.setNewArtBasic` | New Art Has Basic Appearance | Window > Appearance | {on?: bool (omitted: toggle)} the Appearance panel option (the preference newArtBasic, on by default): on, new art takes one fill and stroke (with the Stroke panel's options); off, the whol… |  |
| `appearance.showAllHidden` | Show All Hidden Attributes | Window > Appearance | {ids?\|id?, target?} make every hidden fill, stroke and effect (the object's and each item's) of each selected object visible again; errors when nothing is hidden → {ids} | disabled in catalogue snapshot |
| `appearance.targetContents` | Target Contents |  | {ids?\|id?, target?: "object"\|"contents"} select the members of the selected groups and layers (or `ids`), as double-clicking the Appearance panel's Contents row does: the panel then lists, … | disabled in catalogue snapshot |
| `appearance.transfer` | Move Appearance |  | {source: id, target: id, copy?: bool} give `target` (a layer, group or object) the appearance (fills, strokes, effects) and transparency (opacity, blend mode, isolation, knockout) of `sourc… | disabled in catalogue snapshot |

## `brush` (18)

Brushes paint variable-width strokes. For print, expand strokes to outlines or verify the consumer supports the brush definition.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `brush.addFromLibrary` | Add to Brushes | Window > Brush Libraries | {library: id or name, name? \| names?: [brush names in the library] (default: all of it), apply?: false (also apply the first one to paths, as brush.apply does), ids?\|id? (the paths apply ta… | disabled in catalogue snapshot |
| `brush.apply` | Apply Brush |  | {name, ids?\|id?} apply a brush to the strokes of the selected paths (adds a stroke if missing) and make it current → {ids} | disabled in catalogue snapshot |
| `brush.delete` | Delete Brush |  | {name} \| {names: [name…]} delete brushes; strokes using them become plain strokes | disabled in catalogue snapshot |
| `brush.duplicate` | Duplicate Brush |  | {name, newName? (trimmed; blank: <name> copy)} \| {names: [name…]} → {name} \| {names} | disabled in catalogue snapshot |
| `brush.freehand` | Paintbrush |  | {…params as path.freehand, brush} paint a freehand stroke with a brush → {id} | disabled in catalogue snapshot |
| `brush.get` | Brush Definition |  | {name} → the brush definition (JSON) | disabled in catalogue snapshot |
| `brush.libraries` | Brush Libraries |  | {} → {libraries: [{id, name, category: "builtIn"\|"user" (User Defined: the .vectorcraft files in the user library folder, rescanned now)\|"loaded" (brush.loadLibrary), count, path?}], userFo… |  |
| `brush.library` | Brush Library |  | {library: id or name} → {id, name, category, brushes: [{name, type}] (as brush.list)} |  |
| `brush.list` | Brushes |  | {} → {brushes: [{name, type}], current} | disabled in catalogue snapshot |
| `brush.loadLibrary` | Other Library… | Window > Brush Libraries | {path? \| data?: file text \| dataBase64?, name?: file name (default: the path's)} load the brushes of any document VectorCraft opens (see document.formats; one without brushes of its own has… |  |
| `brush.move` | Move Brush |  | {name? \| names?: [brush names of one type, in order], to?: index among the brushes of that type in brush.list order (they go before the brush of that type now there that isn't moving; defau… | disabled in catalogue snapshot |
| `brush.new` | New Brush… |  | {type: calligraphic\|scatter\|art\|pattern\|bristle, name? (trimmed; blank: New <Type> Brush; a bristle brush name, with the number a taken name gets, has at most 31 characters), params?: {…def… | disabled in catalogue snapshot |
| `brush.options` | Brush Options… |  | {name, params?: {…fields to change (brush.get shows them; values outside their ranges are clamped). calligraphic: angle −180..180°, roundness 0..100%, size 0..1296 pt, variation: [angle°, r… | disabled in catalogue snapshot |
| `brush.remove` | Remove Brush Stroke |  | {ids?\|id?} remove brushes from the selected strokes → {ids} | disabled in catalogue snapshot |
| `brush.saveLibrary` | Save Brush Library… | Window > Brushes | {path?, names?: [brush names] (default: all), name?: library name (default: the document's), user?: false (save into the user library folder, listed under User Defined)} save the document's… | disabled in catalogue snapshot |
| `brush.selectionArt` | Brush Art |  | {ids?\|id?} → {art: the object brush.new takes as a new scatter or art brush's art and as a new pattern brush's side tile (several objects become one group), or null when nothing is selected… | disabled in catalogue snapshot |
| `brush.setCurrent` | Current Brush |  | {name: string\|null} the brush the Paintbrush tool paints with (not an undo step) | disabled in catalogue snapshot |
| `brush.unused` | Select All Unused |  | {} → {names: [the brushes no stroke paints with, in library order]} (the Brushes panel selects them): strokes in the art (opacity masks included), symbols, graph designs, pattern tiles (wit… | disabled in catalogue snapshot |

## `color` (6)

Colour commands set or convert colour values. Record the exact colour space (RGB/CMYK/spot) because screen hex is not a press value.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `color.convert` | Convert Color |  | {color (#rrggbbaa and #rgba are refused), to: "rgb"\|"cmyk"\|"gray"\|"lab", intent?} → {model, values, hex, lab: [L,a,b], outOfGamut, deltaE} |  |
| `color.gamutCheck` | Gamut Warning |  | {ids?\|id?, colors?: [color] (#rrggbbaa and #rgba are refused)} colours that can't be printed in the working CMYK (selection, or the whole document when nothing is selected) → {checked, outO… | disabled in catalogue snapshot |
| `color.harmony` | Color Guide |  | {color (#rrggbbaa and #rgba are refused), rule: complementary\|complementary2\|splitComplementary\|leftComplement\|rightComplement\|analogous\|analogous2\|monochromatic\|shades\|triad\|triad2\|triad3\|… |  |
| `color.loadProfile` | Load Color Profile… |  | {path: .icc/.icm file of at most 32 MB} register an ICC profile (native only). The desktop app and vectorcraft-cli keep a copy of the file in the `Color Profiles` folder next to the prefere… |  |
| `color.plates` | Plates |  | {} → {on, plates: [{name, spot, visible, rgb}]} |  |
| `color.removeProfile` | Remove Color Profile… |  | {name} forget a profile color.loadProfile loaded, and the copy kept of it (built-in profiles and the working spaces stay) → {removed: name} |  |

## `colorTheme` (4)

Colour themes are groups of harmonised colours. Use them as candidates, then lock the approved palette into swatches.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `colorTheme.addToSwatches` | Add to Swatches | Window > Color Themes | {name} add a saved theme's colours to the Swatches panel as a colour group named after it (as swatch.newGroup), as one undo step → {name: the group's, swatches: [names]} | disabled in catalogue snapshot |
| `colorTheme.delete` | Delete Theme | Window > Color Themes | {name} delete a saved colour theme → {deleted} | disabled in catalogue snapshot |
| `colorTheme.list` | Color Themes |  | {} the saved colour themes, in order → {themes: [{name, colors: ["#rrggbb"], keys: [colour keys, exact in each colour's model], rule?}]} |  |
| `colorTheme.save` | Save Theme | Window > Color Themes | {colors: [1–5 colours] (#rrggbbaa and #rgba are refused) \| color + rule (a harmony rule id or label, see color.harmony: its 5-colour theme from that base colour, base first), rule?: the rul… |  |

## `effect` (8)

Effects are live appearances (shadow, glow, etc.). `effect.expandAppearance` is required before some exporters and before path operations; expanded effects are no longer editable.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `effect.apply` | Apply Effect |  | {effect: id (see effect.list, e.g. "stylize.dropShadow", "distort.roughen", "warp.arc", or "plugin.<id>" for an installed effect plug-in), params?: {…} (missing keys take the dialog default… | disabled in catalogue snapshot |
| `effect.duplicate` | Duplicate Effect |  | {index: int, indices?: [int] (several positions in the same list instead of index; every one must exist), item?: appearance item index\|null (as effect.remove), ids?\|id?: [..], target?: "obj… | disabled in catalogue snapshot |
| `effect.expandAppearance` | Expand Appearance | Object | {ids?\|id?: [..], target?} turn each object's appearance into objects: every fill and stroke becomes an object of its own (a stroke stays a stroke, with its weight, dashes, arrowheads and wi… | Bakes live effects into paths/pixels. Keep the unexpanded master for edits.; disabled in catalogue snapshot |
| `effect.lightingPreset` | 3D Lighting Preset |  | {index: int, preset: standard\|diffuse\|topLeft\|right, item?: appearance item index\|null (omitted: the active item, else the object's), ids?\|id?: [..], target?: object\|contents, aligned?: boo… | disabled in catalogue snapshot |
| `effect.list` | Effects |  | {ids?\|id?: object ids (default: the selection), target?: "object"\|"contents"} → {catalog: [{id, label, menu, params, defaults, raster, lengths: {always, absolute (while relative is false)} … |  |
| `effect.move` | Move Effect |  | {from: int\|[int] (position in the source list; a list moves several effects of that list, which keep their order and land together), to: int (the position of the (first) moved effect in the… | disabled in catalogue snapshot |
| `effect.remove` | Remove Effect |  | {index: int (position in the effect list), indices?: [int] (several positions in the same list instead of index, removed in one undo step; every one must exist), item?: appearance item inde… | disabled in catalogue snapshot |
| `effect.setParams` | Effect Options |  | {index: int, params?: {…} (merged into the current parameters), warpStyle?: string (an existing Warp style suffix, e.g. arc or flag; changes only an applied Warp in place), visible?: bool, … | disabled in catalogue snapshot |

## `eyedropper` (1)

Samples appearance from art. Check whether it samples fill, stroke, type or effects before applying.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `eyedropper.setOptions` | Eyedropper Options |  | {sampleSize?: 1\|3\|5 (pixels square averaged when sampling an image: point, 3×3, 5×5), pickUp?, apply?: {appearance?: {transparency?, fill?: {color?, transparency?, overprint?}, stroke?: {co… |  |

## `flattener` (6)

Flattening converts transparency/effects for output. Keep the unflattened master and flatten only a delivery copy.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `flattener.presets.delete` | Delete Transparency Flattener Preset |  | {name} delete a saved preset (built-in ones stay) → {deleted: name} |  |
| `flattener.presets.export` | Export Transparency Flattener Presets |  | {names?: [preset names, built-in ones too] (default: every saved preset), path?} write the presets as a .vcflattener file (JSON) → {path, count}; without path → {data: the file's text, coun… |  |
| `flattener.presets.import` | Import Transparency Flattener Presets |  | {path? \| data?: file text \| dataBase64?, replace?: false (replace saved presets of the same names; else the imported ones get a number)} add the presets of a .vcflattener file (as flattener… |  |
| `flattener.presets.list` | Transparency Flattener Presets |  | {} → {presets: [{name, builtIn, options}]} the built-in presets (High, Medium and Low Resolution), then the saved ones; any of these names works as `preset` wherever flattener options are t… |  |
| `flattener.presets.save` | Save Transparency Flattener Preset |  | {name?: (default: a new "Flattener Preset N"), newName?: rename it, preset?: the preset to start from (default: the saved preset `name`, else medium), …options (the keys of object.flattenTr… |  |
| `flattener.preview` | Flattener Preview |  | {highlight?: "none"\|"rasterizedRegions" (areas the raster/vector balance rasterizes whole)\|"transparentObjects"\|"allAffected"\|"expandedPatterns" (pattern art taking part)\|"outlinedStrokes"\|… | disabled in catalogue snapshot |

## `gradient` (5)

Gradient commands apply presets and edit stops. Gradient geometry is separate (`paint.setGradientGeom`); verify direction and stops in the render.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `gradient.presets.apply` | Apply Gradient Preset |  | {name: a preset's name (gradient.presets.list), stroke?, item?, ids?\|id?, target? (as paint.editGradient)} give the gradient behind the active proxy (or the targeted fill or stroke) the pre… | disabled in catalogue snapshot |
| `gradient.presets.delete` | Delete Gradient Preset |  | {name?: a saved preset (default: the saved preset the active proxy's gradient is)} remove a saved preset; built-in presets can't be deleted, and painted art keeps its gradient → {deleted} | disabled in catalogue snapshot |
| `gradient.presets.list` | Gradient Presets |  | {} → {presets: [{name, library: the built-in library (theme) it comes from, null for a saved one, builtIn, gradient: {kind, stops, method?, dither?} (as paint.setFill's `gradient`)}]} the G… |  |
| `gradient.presets.save` | Save Gradient Preset |  | {name?: (default: a new "Gradient Preset N"; unique, any case, and not a built-in preset's)} save the gradient behind the active proxy (paint.toggleActive picks Fill or Stroke) as a preset,… | disabled in catalogue snapshot |
| `gradient.selectStop` | Select Gradient Stop |  | {index: stop index (0 = the start) \| null to clear} select a stop of the gradient behind the active proxy (the first selected object's, else the default paint): the stop the Gradient tool's… |  |

## `graphicStyle` (18)

Graphic styles bundle fill/stroke/effects. Applying one can overwrite local appearance; keep a copy of the source.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `graphicStyle.addFromLibrary` | Add to Graphic Styles | Window > Graphic Style Libraries | {library: id or name, name? \| names?: [style names in the library] (default: all of it), apply?: false (also apply the first one to `ids` or the selection, if any, as graphicStyle.apply), a… | disabled in catalogue snapshot |
| `graphicStyle.apply` | Apply Graphic Style | Window > Graphic Styles | {name, add?: bool, ids?\|id? (layers too), target?: "object"\|"contents"} give the objects (default: the selection; a group or layer itself, its fills and strokes painting its members and its… | disabled in catalogue snapshot |
| `graphicStyle.breakLink` | Break Link to Graphic Style | Window > Graphic Styles | {ids?\|id?, target?: "object"\|"contents"} unlink the objects (default: the selection) from their graphic style; they keep their look | disabled in catalogue snapshot |
| `graphicStyle.delete` | Delete Graphic Style | Window > Graphic Styles | {name} \| {names: [name…]} delete styles; their objects keep their look but are unlinked | disabled in catalogue snapshot |
| `graphicStyle.duplicate` | Duplicate Graphic Style | Window > Graphic Styles | {name} → {name} | disabled in catalogue snapshot |
| `graphicStyle.libraries` | Graphic Style Libraries |  | {} → {libraries: [{id, name, category: "builtIn"\|"user" (User Defined: the .vcstyles files in the user library folder, rescanned now)\|"loaded" (graphicStyle.loadLibrary), count, path?}], us… |  |
| `graphicStyle.library` | Graphic Style Library |  | {library: id or name} → {id, name, category, styles: [{name, fill, stroke, strokeWidth, fills, strokes, effects: [effect id…], opacity, blend, isolate, knockout}] (as graphicStyle.list)} |  |
| `graphicStyle.list` | List Graphic Styles |  | {} → {styles: [{id, name, fill, stroke, strokeWidth, fills, strokes, effects: [effect id…], opacity: 0..100, blend, isolate, knockout: "on"\|"off"\|"neutral", linked: [object ids]}], selected… | disabled in catalogue snapshot |
| `graphicStyle.loadLibrary` | Other Library… | Window > Graphic Style Libraries | {path? \| data?: file text \| dataBase64?, name?: file name (default: the path's)} load a .vcstyles library, or the graphic styles of any document VectorCraft opens (see document.formats), fo… |  |
| `graphicStyle.merge` | Merge Graphic Styles | Window > Graphic Styles | {names: [name…] (two or more), name?} add a style combining the styles' fills, strokes and effects (each style's on top of the ones before it) with the first one's opacity, blend mode, isol… | disabled in catalogue snapshot |
| `graphicStyle.move` | Move Graphic Style |  | {name, to: index} move the style to position `to` of the list (0 = first, clamped), as dragging it in the Graphic Styles panel does | disabled in catalogue snapshot |
| `graphicStyle.new` | New Graphic Style | Window > Graphic Styles | {name?, id?} a style from object `id` or the first selected object: its appearance, opacity, blend mode, isolate and knockout (a group without fills or strokes of its own lends its topmost … | disabled in catalogue snapshot |
| `graphicStyle.redefine` | Redefine Graphic Style | Window > Appearance | {name?, id?} replace the style (default: the one the object was last linked to) with the look of object `id` or the first selected object; the objects still linked to it update, and that ob… | disabled in catalogue snapshot |
| `graphicStyle.rename` | Rename Graphic Style | Window > Graphic Styles | {name, to} (Graphic Style Options; names are unique and linked objects stay linked) → {name} | disabled in catalogue snapshot |
| `graphicStyle.saveLibrary` | Save Graphic Style Library… | Window > Graphic Styles | {path?, names?: [style names] (default: all), name?: library name (default: the document's), user?: false (save into the user library folder, listed under User Defined)} save the document's… | disabled in catalogue snapshot |
| `graphicStyle.setOptions` | Graphic Styles Options |  | {overrideCharColor?: bool} Override Character Color (the preference `overrideCharColor`, on by default): applying a style to type replaces its characters' fill and stroke with the style's f… |  |
| `graphicStyle.sortByName` | Sort by Name | Window > Graphic Styles | {} sort the styles by name (the Default Graphic Style stays first) | disabled in catalogue snapshot |
| `graphicStyle.unused` | Select All Unused | Window > Graphic Styles | {} → {names: [the styles no object is linked to]} (the panel selects them) | disabled in catalogue snapshot |

## `paint` (22)

Paint sets fill/stroke, gradients and sampled colours. `paint.none` removes paint; `paint.setFill`/`setStroke` are the workhorses.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `paint.complement` | Complement |  | {stroke?: bool (default: the active proxy), ids?\|id?, item?: appearance item index\|null, target?: "object"\|"contents"} replace the active proxy's colours by their complements ((highest + lo… | disabled in catalogue snapshot |
| `paint.default` | Default Fill and Stroke |  | {ids?\|id?} white fill and 1 pt black stroke for the selection and the defaults; type gets black fill and no stroke | disabled in catalogue snapshot |
| `paint.editGradient` | Gradient | Window > Gradient | {stroke?: bool (default: the targeted item's kind, else the active proxy), kind?: linear\|radial\|freeform (freeform places points on each object, coloured along the stops), mode?: points\|lin… | disabled in catalogue snapshot |
| `paint.freeform.addLine` | Add Freeform Line |  | {points: [index, …] (at least two), ids?\|id?, stroke?: bool (default: the targeted item's kind, else the active proxy), item?: fill/stroke item index\|null (omitted: the Appearance panel's a… | disabled in catalogue snapshot |
| `paint.freeform.addPoint` | Add Freeform Point |  | {at: [x,y] (document coordinates), color? (default: the gradient's colour there; #rrggbbaa and #rgba are refused), keepModel?: bool (as paint.setFill), opacity?: 0..1 (or 0..100), spread?: … | disabled in catalogue snapshot |
| `paint.freeform.deletePoint` | Delete Freeform Point |  | {index? (default: the selected point), ids?\|id?, stroke?: bool (default: the targeted item's kind, else the active proxy), item?: fill/stroke item index\|null (omitted: the Appearance panel'… | disabled in catalogue snapshot |
| `paint.freeform.get` | Freeform Gradient |  | {stroke?: bool (default: the active proxy)} the freeform gradient behind the proxy of the first selected object → {mode: points\|lines, points: [{at: [x,y] (document coordinates), color, opa… | disabled in catalogue snapshot |
| `paint.freeform.selectPoint` | Select Freeform Point |  | {index: point index \| null to clear} select a point of the freeform gradient behind the active proxy (the first selected object's): the point the Gradient tool, the Gradient and Color panel… | disabled in catalogue snapshot |
| `paint.freeform.setPoint` | Edit Freeform Point |  | {index? (default: the selected point), at?: [x,y] (document coordinates), color? (#rrggbbaa and #rgba are refused), keepModel?: bool (as paint.setFill), opacity?: 0..1 (or 0..100), spread?:… | disabled in catalogue snapshot |
| `paint.freeform.splitLine` | Split Freeform Line |  | {line: line index, segment: the segment from the line's point `segment` to the next, t?: 0..1 along it (default 0.5), ids?\|id?, stroke?: bool (default: the targeted item's kind, else the ac… | disabled in catalogue snapshot |
| `paint.invert` | Invert |  | {stroke?: bool (default: the active proxy), ids?\|id?, item?: appearance item index\|null, target?: "object"\|"contents"} invert the active proxy's colours of the selection (or ids; groups rec… | disabled in catalogue snapshot |
| `paint.lastColor` | Apply Last Color |  | {stroke?: bool (default: the active proxy), ids?\|id?, item?: appearance item index\|null, target?: "object"\|"contents"} apply the last solid colour used (paint.recent lastColor) to the activ… | disabled in catalogue snapshot |
| `paint.lastGradient` | Apply Last Gradient |  | {stroke?: bool (default: the active proxy), ids?\|id?, item?: appearance item index\|null, target?: "object"\|"contents"} apply the last gradient used (paint.recent lastGradient), fitted to ea… | disabled in catalogue snapshot |
| `paint.none` | None |  | {} set the active proxy (fill or stroke) to None → {objects} | disabled in catalogue snapshot |
| `paint.proxies` | Fill and Stroke |  | {} → {fill, stroke: the paints the Fill/Stroke proxies show (the Appearance panel's active item for the proxy of its kind, else the first selected object's, a group's first painted object's… |  |
| `paint.recent` | Recent Colors |  | {} → {colors: [{hex, color}] newest first (fed by every paint command and the eyedropper), lastColor: {hex, color}, lastGradient: gradient paint} |  |
| `paint.sampleColor` | Sample Color |  | {color (#rrggbbaa and #rgba are refused), stroke?: bool (default: whichever proxy is active), ids?, stop?: index, clearStroke?: bool} sample a color into the active fill/stroke (and the sel… | disabled in catalogue snapshot |
| `paint.setFill` | Fill |  | {color?: "#rrggbb"\|[r,g,b]\|{c,m,y,k}\|{gray}\|{l,a,b} (CIE Lab; #rrggbbaa and #rgba are refused), none?: true, swatch?: name (a global or spot colour stays linked, so swatch edits recolour it… | Sets fill paint; accepts colour/none/gradient/swatch depending on schema. Verify the active target.; disabled in catalogue snapshot |
| `paint.setGradientGeom` | Gradient Vector |  | {start?: [x,y], end?: [x,y] (document coordinates; both or neither: omitted, the vector stays), aspect?: % (radial: the extent ellipse's height / width; default: kept), focal?: [x,y] (docum… | disabled in catalogue snapshot |
| `paint.setStroke` | Stroke |  | {…as paint.setFill, item?: the stroke item to set} same as paint.setFill, for the stroke | disabled in catalogue snapshot |
| `paint.swap` | Swap Fill and Stroke |  | {ids?\|id?} swap the fill and stroke of the selection (type too) and of the defaults | disabled in catalogue snapshot |
| `paint.toggleActive` | Toggle Fill/Stroke Focus |  | {fill?: bool (true: bring the Fill proxy forward, false: the Stroke proxy; omitted: swap which is in front)} → {fillActive} |  |

## `pattern` (4)

Pattern swatches tile artwork. Check seam alignment and output scale; patterns are easy to make too dense for print.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `pattern.delete` | Delete Pattern |  | {name} delete a pattern swatch (objects painted with it lose that paint) | disabled in catalogue snapshot |
| `pattern.list` | List Patterns |  | {} → {patterns: [{name, tileType, width, height, ...}], editing?} | disabled in catalogue snapshot |
| `pattern.options` | Pattern Options | Window > Pattern Options | {name? (default: the pattern being edited), newName? (trimmed; blank: the name is kept), tileType?, brickOffset?, width?, height?, hSpacing?, vSpacing?, sizeTileToArt?: bool, overlap?: {h: … | disabled in catalogue snapshot |
| `pattern.transform` | Transform Patterns |  | {ids?\|id?, matrix: [a,b,c,d,e,f]} transform only the pattern placement of the objects' pattern paints (Transform Patterns) | disabled in catalogue snapshot |

## `recolor` (4)

Recolor commands remap a palette. They are ideal for brand variants; verify every output colour against the approved hex list.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `recolor.apply` | Recolor Artwork | Edit > Edit Colors | {map: rows [{from: [colour keys (recolor.colors) or "#rrggbb" (every colour shown as that hex)], to: colour (hex, key, {c,m,y,k} or {l,a,b}) \| null (in from, to and groupColors, #rrggbbaa a… | disabled in catalogue snapshot |
| `recolor.colors` | Artwork Colors |  | {ids?: object ids (default: the selection, or with nothing selected the objects select.all takes, without the hidden and locked objects inside them)} → {colors: [{key: colour identity ("rgb… | disabled in catalogue snapshot |
| `recolor.randomize` | Randomize Colors |  | {map: rows as recolor.apply, order?: true (shuffle the new colours among the rows that aren't excluded), saturationBrightness?: false (random saturation and brightness, hue kept), seed?: 0}… |  |
| `recolor.reduce` | Reduce Colors |  | {colors?: n (rows; default: one per colour, with the tints of a global swatch in its row), method?: as recolor.apply; default scaleTints (picks each row's colour), preserve?: {white?: true,… | disabled in catalogue snapshot |

## `stroke` (10)

Stroke commands set width, caps, joins, dashes and alignment. Outline strokes before a pathfinder operation that expects fills.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `stroke.set` | Stroke Options | Window > Stroke | {weight?: pt, cap?: butt\|round\|square, join?: miter\|round\|bevel, miterLimit?, align?: center\|inside\|outside, dash?: [d,g,…]\|null (a 0 dash with a round or projecting cap draws dots or squar… | disabled in catalogue snapshot |
| `stroke.setAdvanced` | Stroke Options |  | {arrowScale?: [start %, end %], swapArrows?: bool, flipProfile?: "along"\|"across", brush?: name\|null, item?: stroke item index\|null, ids?\|id?, target?: "object"\|"contents"} Stroke panel ext… | disabled in catalogue snapshot |
| `stroke.widthPoint.copy` | Copy Width Point |  | {id, index: the width point to copy, t: 0..1 where the copy goes} → {index} (Alt-drag with the Width tool). Landing on another point makes a discontinuous point, as a stroke.widthPoint.set … | disabled in catalogue snapshot |
| `stroke.widthPoint.remove` | Delete Width Point |  | {id, index \| indices: [..]} remove width points (removing the last one leaves a uniform stroke) | disabled in catalogue snapshot |
| `stroke.widthPoint.set` | Width Point |  | {id, t: 0..1 (fraction of the path length), left, right: side widths in pt, index?: width point to edit or move, adjustAdjoining?: bool (the nearest points either side change their widths i… | disabled in catalogue snapshot |
| `stroke.widthProfile.add` | Add to Profiles |  | {name?} save the selected stroke's variable width to the Profile list (kept with the preferences) under `name` (default "Width Profile N"; unique, not a built-in's) → {name} | disabled in catalogue snapshot |
| `stroke.widthProfile.delete` | Delete Profile |  | {name?} remove a saved profile from the Profile list (default: the selected stroke's); built-in profiles can't be deleted, and strokes keep their widths → {deleted} | disabled in catalogue snapshot |
| `stroke.widthProfile.list` | Width Profiles |  | {} → {profiles: [{id (stroke.set `profile`), label, builtIn, points: [[t, left, right]…]}], current: the selected stroke's profile id or name (nothing selected: the next object drawn's), "c… |  |
| `stroke.widthProfile.reset` | Reset Profiles |  | {} remove every saved profile, leaving the built-ins → {removed: count} | disabled in catalogue snapshot |
| `stroke.widthProfile.set` | Width Profile |  | {ids?\|id?, points: [[t, left, right]…] (width factors, 1 = the stroke weight) \| null = uniform} | disabled in catalogue snapshot |

## `svgInteractivity` (6)

SVG interactivity adds links/events for web SVG. It does not affect print output.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `svgInteractivity.addFile` | Add JavaScript File |  | {file: path or URL (written as given, without surrounding spaces)} link a JavaScript file to the document, after the others: SVG export writes a <script xlink:href> for each linked file. A … | disabled in catalogue snapshot |
| `svgInteractivity.clearEvents` | Clear Events |  | {ids?\|id?} remove every event from ids or the selection, as one undo step → {changed: objects} | disabled in catalogue snapshot |
| `svgInteractivity.info` | SVG Interactivity |  | {ids?\|id?} → {ids, events: [{event, script}…] in the panel's order \| null (the objects' events differ), files: [the linked JavaScript files…], eventNames: [the events the panel lists…]} the… | disabled in catalogue snapshot |
| `svgInteractivity.removeEvent` | Remove Selected Entry |  | {event, ids?\|id?} remove an event and its JavaScript from ids or the selection, as one undo step → {changed: objects} | disabled in catalogue snapshot |
| `svgInteractivity.removeFile` | Remove JavaScript File |  | {file} unlink a JavaScript file from the document → {files} | disabled in catalogue snapshot |
| `svgInteractivity.setEvent` | Add Event |  | {event: "onclick"\|"onmouseover"\|… (svgInteractivity.info's eventNames), script: string (the JavaScript; "" removes the event), ids?\|id?} set the JavaScript an event runs on ids or the selec… | disabled in catalogue snapshot |

## `swatch` (23)

Swatches are reusable named colours. Use global/spot swatches for brand colours so one edit updates the artwork; check spot options before print.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `swatch.addUsedColors` | Add Used Colors | Window > Swatches | {selection?: false (only the selected art's colours; default: all the art's), global?: false (the new swatches are global and the matching unlinked colours in that art link to them)} add a … | disabled in catalogue snapshot |
| `swatch.delete` | Delete Swatch | Window > Swatches | {name? \| names?: [swatch or colour group names] (a group goes with its swatches), unlink?: true (art using a deleted global swatch keeps its colour, unlinked; false keeps the stale link)} d… | disabled in catalogue snapshot |
| `swatch.duplicate` | Duplicate Swatch | Window > Swatches | {name} | disabled in catalogue snapshot |
| `swatch.edit` | Swatch Options | Window > Swatches | {name, newName?, color? (e.g. {l, a, b} for a Lab colour; #rrggbbaa and #rgba are refused), keepModel?: bool (as paint.setFill; the swatch's own color and a color given with mode keep their… | disabled in catalogue snapshot |
| `swatch.editGroup` | Edit Color Group | Window > Swatches | {group: colour group, colors: [colour] (hex, key, {c,m,y,k} or {l,a,b}; #rrggbbaa and #rgba are refused; the group's swatches take them in order, extra colours become new swatches, swatches… | disabled in catalogue snapshot |
| `swatch.library.add` | Add to Swatches | Window > Swatch Libraries | {library: id or name, names?: [swatch or colour group names in the library] (default: all of it; a group comes as a colour group, a single swatch ungrouped), apply?: "fill"\|"stroke" (also a… | disabled in catalogue snapshot |
| `swatch.library.copyToUser` | Copy to User Defined | Window > Swatch Libraries | {library: id or name of a loaded library (category "loaded", swatch.library.load)} copy it into the user library folder of the desktop app, whose libraries VectorCraft lists as User Defined… | disabled in catalogue snapshot |
| `swatch.library.get` | Swatch Library |  | {library: id or name} → {id, name, category, swatches: [{name, kind, group, global, spot, color?, hex?, gradient?, pattern?}] (as swatch.list), groups: [{name, swatches: [names]}]} |  |
| `swatch.library.list` | Swatch Libraries |  | {} → {libraries: [{id, name, category: "builtIn"\|"gradients"\|"patterns"\|"user" (User Defined: the library files in the user library folder, rescanned now)\|"loaded" (swatch.library.load), co… |  |
| `swatch.library.load` | Other Library… | Window > Swatch Libraries | {path? \| data?: file text \| dataBase64?, name?: file name (default: the path's)} load a .vcswatches, .gpl, .ase (swatch exchange) or .acb (color book, read only) library, or the swatches of… |  |
| `swatch.library.save` | Save Swatch Library… | Window > Swatches | {path?, format?: "vcswatches" (lossless JSON: colour models, global, spot, gradients, groups) \| "gpl" (8-bit RGB palette; groups as `# Group:` comments) \| "ase" (swatch exchange, binary: so… | disabled in catalogue snapshot |
| `swatch.list` | Swatches |  | {group?: name (only that colour group's swatches)} → {swatches: [{name, kind: "none"\|"color"\|"gradient"\|"pattern", group, global, spot, color?, hex?, tintOf?: base swatch of a tint swatch, … | disabled in catalogue snapshot |
| `swatch.merge` | Merge Swatches | Window > Swatches | {names: [two or more solid-colour swatches], name?: the merged swatch's name (one swatch kept)} keep the first (its name and colour) and delete the others; paints linked to them take its co… | disabled in catalogue snapshot |
| `swatch.move` | Move Swatch | Window > Swatches | {name? \| names?: [swatch names, in order; or colour group names to reorder the groups], to?: index in the destination (they go before the swatch or group now there; default: the end), group… | disabled in catalogue snapshot |
| `swatch.new` | New Swatch | Window > Swatches | {name?, color? \| colors?: [colour] (one swatch each, in one undo step; #rrggbbaa and #rgba are refused) \| swatch? \| gradient? \| pattern?: name (default: the current fill), tint?: 0..100 (% … | Creates a named colour. Use global/spot deliberately; record the hex/CMYK equivalents.; disabled in catalogue snapshot |
| `swatch.newGroup` | New Color Group | Window > Swatches | {name?, swatches?: [names] (solid colours move into the group; gradients, patterns and None stay), colors?: [colour] (added as new swatches; #rrggbbaa and #rgba are refused), keepModel?: bo… | disabled in catalogue snapshot |
| `swatch.resetDefaults` | Default Swatches | Window > Swatch Libraries | {replace?: false} bring back the default swatches and colour groups of the document's colour mode that are missing (by name), as one undo step; replace: true makes the swatches exactly the … | disabled in catalogue snapshot |
| `swatch.setSpot` | Spot Color |  | {name, spot?: true} make a swatch a spot colour (prints on its own plate; spot swatches are global) → {name, spot} | disabled in catalogue snapshot |
| `swatch.sortByKind` | Sort by Kind | Window > Swatches | {} order the swatches of each list by kind (None first, then process colours, spot colours, gradients, patterns; colour groups stay after them), keeping their order within a kind, as one un… | disabled in catalogue snapshot |
| `swatch.sortByName` | Sort by Name | Window > Swatches | {} | disabled in catalogue snapshot |
| `swatch.spotOptions` | Spot Colors | Window > Swatches | {useLab?: bool (omitted: unchanged)} the document's Spot Colors options: spot colours defined in Lab show, print and export from their Lab values (true, the default: PDF Separation spaces g… | disabled in catalogue snapshot |
| `swatch.ungroup` | Ungroup Color Group | Window > Swatches | {name: colour group} move its swatches to the end of the ungrouped swatches and remove the group, as one undo step → {swatches: [names]} | disabled in catalogue snapshot |
| `swatch.unused` | Select All Unused | Window > Swatches | {} → {names: [the swatches nothing uses, in panel order]}: a colour is used when a paint links to it or an unlinked paint, gradient stop or mesh point has its colour; a gradient when a grad… | disabled in catalogue snapshot |

## `transparency` (17)

Transparency/blending commands affect compositing. The rendered PNG/SVG must be checked on the final background, not the editor checkerboard.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `transparency.disableOpacityMask` | Disable Opacity Mask | Window > Transparency | {id?\|ids?} keep the mask but stop applying it | disabled in catalogue snapshot |
| `transparency.editOpacityMask` | Edit Opacity Mask | Window > Transparency | {id?} edit the mask art of `id` (default: the first selected object with a mask) in place, as clicking the mask thumbnail in the Transparency panel does; refused in isolation mode and in pa… | disabled in catalogue snapshot |
| `transparency.enableOpacityMask` | Enable Opacity Mask | Window > Transparency | {id?\|ids?} | disabled in catalogue snapshot |
| `transparency.info` | Transparency Info |  | {id?\|ids?} → {ids, opacity: 0..100, blend, isolate, knockout: "on"\|"off"\|"neutral", knockoutShape, editingMask, pageIsolatedBlending, pageKnockoutGroup} the Transparency panel's values for … | disabled in catalogue snapshot |
| `transparency.linkOpacityMask` | Link Opacity Mask | Window > Transparency | {id?\|ids?} | disabled in catalogue snapshot |
| `transparency.makeOpacityMask` | Make Opacity Mask | Window > Transparency | {ids?, clip?, invert?} the topmost of the selected objects (or of `ids`) becomes the mask of the others (grouped if several; a layer among several stands for its art, so the topmost object … | disabled in catalogue snapshot |
| `transparency.opacityMaskInfo` | Opacity Mask Info |  | {id?\|ids?} → [{id, clip, invert, disabled, linked, art}] the opacity masks of `ids`, the selection, or the object whose mask is being edited | disabled in catalogue snapshot |
| `transparency.releaseOpacityMask` | Release Opacity Mask | Window > Transparency | {id?\|ids?} put the mask art back above each masked object (default: the selection, or the object whose mask is being edited, which leaves mask editing) | disabled in catalogue snapshot |
| `transparency.set` | Transparency | Window > Transparency | {ids?\|id?, opacity?: 0..100, blend?: name, isolate?, knockout?: "on"\|"off"\|"neutral"\|bool (true = on, false = neutral), knockoutShape?: bool, item?: appearance item index\|null, target?: "ob… | disabled in catalogue snapshot |
| `transparency.setOpacityMask` | Opacity Mask Options |  | {id?\|ids?, clip?, invert?, disabled?, linked?} change the opacity masks of `ids`, the selection, or the object whose mask is being edited | disabled in catalogue snapshot |
| `transparency.stopEditingOpacityMask` | Stop Editing Opacity Mask | Window > Transparency | {} leave mask editing (the object thumbnail) → {id} | disabled in catalogue snapshot |
| `transparency.toggleNewMasksClipping` | New Opacity Masks Are Clipping | Window > Transparency | {value?} → {value} |  |
| `transparency.toggleNewMasksInverted` | New Opacity Masks Are Inverted | Window > Transparency | {value?} → {value} |  |
| `transparency.togglePageIsolatedBlending` | Page Isolated Blending | Window > Transparency | {value?} make the page an isolated group (default: toggle): blend modes of top-level objects don't blend with what lies under the page; saved with the document and written to PDF → {value} | disabled in catalogue snapshot |
| `transparency.togglePageKnockoutGroup` | Page Knockout Group | Window > Transparency | {value?} make the page a knockout group (default: toggle): its layers (the contents of neutral layers) hide what they cover instead of showing it through their transparency; saved with the … | disabled in catalogue snapshot |
| `transparency.unlinkOpacityMask` | Unlink Opacity Mask | Window > Transparency | {id?\|ids?} the object moves without its mask | disabled in catalogue snapshot |
| `transparency.viewOpacityMask` | View Opacity Mask | Window > Transparency | {on?: bool (default: toggle), id?} show only the opacity mask of `id` (default: the object whose mask is edited, else the first selected object with a mask) on the canvas, as greyscale cove… | disabled in catalogue snapshot |
