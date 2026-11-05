# VectorCraft Layer Artboard

Auto-generated from the installed 918-command catalogue (snapshot 2026-11-05). Every row is a real command id; params are abbreviated from the catalogue's own text. Read the full params string with `$VC commands` before running. Tips are practical notes, not substitutes for the schema.

Commands: **119** across 8 groups.

## Coverage

`artboard` 13 · `graph` 6 · `guide` 6 · `layer` 26 · `perspective` 25 · `slice` 1 · `symbol` 23 · `view` 19

## `artboard` (13)

Artboards define output regions. Export uses the artboard; check its bounds before `document.export`.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `artboard.convertToArtboards` | Convert to Artboards | Object > Artboards | {} turn each selected object's bounds into a new artboard (the objects are removed) → {artboards} | disabled in catalogue snapshot |
| `artboard.copy` | Copy Artboard |  | {index? \| indices?, art?} (defaults as artboard.duplicate) put the artboards, and the art fully inside each when `art`, on the clipboard: edit.paste adds a copy of each, together right of t… | disabled in catalogue snapshot |
| `artboard.cut` | Cut Artboard |  | {index? \| indices?, art?} artboard.copy, then delete the artboards and that art in one undo step (one artboard is always left: the cut fails when it names every artboard, or a locked one; a… | disabled in catalogue snapshot |
| `artboard.delete` | Delete Artboard | Window > Artboards | {index \| indices: [index…]} delete artboards (with their guides) in one step; one is always left, and a locked one is an error | disabled in catalogue snapshot |
| `artboard.deleteEmpty` | Delete Empty Artboards | Window > Artboards | {} delete every artboard with no artwork on it (no object, hidden, locked and template art included, whose visual bounds meet or touch it, clip groups and clipping layers by their members i… | disabled in catalogue snapshot |
| `artboard.duplicate` | Duplicate Artboard | Window > Artboards | {index?: n \| indices?: [n…] (default: the artboards the Artboard tool has selected), art?: bool (default: the Artboard tool's moveArt option), patterns?: bool (Transform Patterns: pattern f… | disabled in catalogue snapshot |
| `artboard.fitToArt` | Fit to Artwork Bounds | Object > Artboards | {index?: n \| indices?: [n…] (0-based; the app passes the selected artboards: the Artboard tool's, else the active one; default: the first)} each artboard fits the art on it that shows (with… | disabled in catalogue snapshot |
| `artboard.fitToSelection` | Fit to Selected Art | Object > Artboards | {index?: n (0-based; the app passes the active artboard; default: the first)} the artboard fits the selected art (with its strokes); a locked artboard stays as it is (an error when the fit … | disabled in catalogue snapshot |
| `artboard.move` | Move Artboard |  | {index \| indices: [index…], dx, dy, moveArt?: bool, copy?: bool, patterns?: bool (Transform Patterns: pattern fills and strokes transform with the art; default: prefs transformPatternTiles)… | disabled in catalogue snapshot |
| `artboard.new` | New Artboard | Window > Artboards | {x?, y?, width?, height?, name?, color?: color (its background color, as artboard.setProps takes it, #rrggbbaa and #rgba refused; default: none), showCenterMark?: bool, showCrossHairs?: boo… | Adds an output region. `document.export` with artboard options chooses which one; do not assume artboard 1.; disabled in catalogue snapshot |
| `artboard.rearrange` | Rearrange All Artboards… | Object > Artboards | {layout?: gridByRow\|gridByColumn\|row\|column (gridByRow; byColumn?: true is gridByColumn), order?: leftToRight\|rightToLeft (leftToRight: right-to-left mirrors the order along the rows), colu… | disabled in catalogue snapshot |
| `artboard.reorder` | Move Artboard Up/Down |  | {index, to} change an artboard's number | disabled in catalogue snapshot |
| `artboard.setProps` | Artboard Options… | Window > Artboards | {index \| artboards: [{index, name?, color?, locked?, showCenterMark?, showCrossHairs?, showVideoSafeAreas?, videoRulerPixelAspectRatio?, x?, y?, width?, height?}…] (several artboards in one… | disabled in catalogue snapshot |

## `graph` (6)

Graph commands create chart objects. Style them after creation; data editing is a separate operation.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `graph.column` | Column… | Object > Graph | {id?, seriesIndexes?: [index], design?: name\|null, columnType?: vertical\|uniform\|repeating\|sliding, each?: value (more than 0), fractions?: chop\|scale} draw the columns or bars and the lege… | disabled in catalogue snapshot |
| `graph.create` | Create Graph |  | {type: column\|stackedColumn\|bar\|stackedBar\|line\|area\|scatter\|pie\|radar, x, y, width, height, series?: [..], categories?: [..], rows?: [[number\|null]], csv?} → {id}; an empty CSV cell or a n… | disabled in catalogue snapshot |
| `graph.design` | Design… | Object > Graph | {new?: name\|true (New Design: the selected art becomes a graph design, named "New Design" when true; put a rectangle at the back to set the size it draws at), rename?: name, to?: new name (… | disabled in catalogue snapshot |
| `graph.marker` | Marker… | Object > Graph | {id?, seriesIndexes?: [index], design?: name\|null} draw the data points and legend swatch of the series selected with Group Selection (or listed, or every series) with a graph design, scale… | disabled in catalogue snapshot |
| `graph.setData` | Data… | Object > Graph | {id?, series?, categories?, rows?, csv?: first row = series labels (first cell empty); then one row per category: label; values…; an empty cell or a null is a blank value; a quoted number a… | disabled in catalogue snapshot |
| `graph.setType` | Type… | Object > Graph | {id?, type?, seriesIndexes?: [index], columnWidth?: % (1–1000; past 100 columns overlap), clusterWidth?: % (1–1000), legend?: bool, markPoints?: bool, connectPoints?: bool, edgeToEdge?: boo… | disabled in catalogue snapshot |

## `guide` (6)

Guides are layout aids; they should not export. Clear them before delivery if the exporter includes them.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `guide.add` | Add Guide |  | {vertical: bool, pos: pt (x for vertical, y for horizontal), artboard?: index (an artboard guide: it runs across that artboard only and moves, is copied and is deleted with it; default a ca… | disabled in catalogue snapshot |
| `guide.list` | Guides |  | {} → [{index, vertical, pos, selected, artboard?: index (an artboard guide's), layer?: id (the layer it is on), shown, editable (its layer shown and unlocked)}…] the ruler guides | disabled in catalogue snapshot |
| `guide.move` | Move Guide |  | {index, pos: pt} \| {dx?, dy?: pt, copy?: bool} put ruler guide `index` at `pos`, or move the selected guides (vertical ones by dx, horizontal ones by dy); copy leaves them and selects the m… | disabled in catalogue snapshot |
| `guide.remove` | Remove Guide |  | {index?} delete ruler guide `index`, else the selected ones (as Delete / edit.clear does) → {count} | disabled in catalogue snapshot |
| `guide.select` | Select Guides |  | {indexes: [index…], toggle?: bool} select ruler guides on their own (deselecting the art); toggle adds or removes them instead, keeping the selected art (a Shift-click on a guide) → {select… | disabled in catalogue snapshot |
| `guide.setLayer` | Move Guide to Layer |  | {index?, indexes?: [index…], layer: id} put ruler guide `index` (or guides `indexes`), else the selected guides, on layer `layer` (a layer or sublayer), as dragging their rows onto that lay… | disabled in catalogue snapshot |

## `layer` (26)

Layer commands manage structure and stacking. `layer.move`/`layer.collectInNew` move selected art; `layer.merge`/`flatten` are destructive. Lock/hide commands protect finished layers.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `layer.clippingMask.toggle` | Make/Release Clipping Mask | Window > Layers | {id?: layer or group (default: the one highlighted layer or group row, else the one selected group, else the current layer)} make: its top object (a path, compound path or text, which loses… | Creates/releases a clipping mask from the selected stack. Order matters: clipping object above, content below.; disabled in catalogue snapshot |
| `layer.collectInNew` | Collect in New Layer | Window > Layers | {ids?} move rows (default: the highlighted rows, else the selected objects) into a new layer where the topmost of them was (a sublayer when they are in a layer), deselecting every selected … | disabled in catalogue snapshot |
| `layer.delete` | Delete Selection | Window > Layers | {ids?\|id?} delete rows: layers, sublayers, groups or objects with what they hold (default: the highlighted rows, else the current layer). The last layer stays → {deleted} | disabled in catalogue snapshot |
| `layer.duplicate` | Duplicate Selection | Window > Layers | {ids?\|id?} copy rows (default: the highlighted rows, else the current layer), each just above its original; a layer's copy is named `<name> copy`. The copies are highlighted → {ids} | disabled in catalogue snapshot |
| `layer.flatten` | Flatten Artwork | Window > Layers | {id?} (default: the highlighted row's top-level layer, else the current one's) move the art of every other visible top-level layer into this one, keeping the stacking order; hidden layers a… | disabled in catalogue snapshot |
| `layer.hideOthers` | Hide Others | Window > Layers | {ids?\|id?} hide every top-level layer but those holding the highlighted rows (else the current layer), which show. One undo step → {count} | disabled in catalogue snapshot |
| `layer.highlight` | Highlight Rows |  | {ids, mode?: "set"\|"add"\|"toggle"} highlight Layers panel rows (Shift-click: a range, Ctrl-click: toggle one); the last one's layer becomes current. Not an undo step → {rows} | disabled in catalogue snapshot |
| `layer.locate` | Locate Object | Window > Layers | {id?} (default: the last selected object) highlight the object's row; the Layers panel opens the layers around it and scrolls to it → {id, ancestry: [layer…, id]} | disabled in catalogue snapshot |
| `layer.lockOthers` | Lock Others | Window > Layers | {ids?\|id?} lock every top-level layer but those holding the highlighted rows (else the current layer), which unlock → {count} | disabled in catalogue snapshot |
| `layer.merge` | Merge Selected | Window > Layers | {ids?\|id?} (default: the highlighted rows) merge two or more rows into the layer listed (highlighted) last: the other layers' contents and the other rows move into it, keeping their stackin… | disabled in catalogue snapshot |
| `layer.move` | Move Rows |  | {ids\|id, target, place?: "above"\|"below"\|"inside" (default inside), copy?: bool} drag rows in the Layers panel: above or below the target row (beside it, in its layer or group), or inside a… | disabled in catalogue snapshot |
| `layer.new` | New Layer… | Window > Layers | {name?, top?: bool, below?: bool, color?, template?, locked?, visible?, printable?, preview?, dimImages?} a layer directly above the current layer, at its level (a sublayer beside a current… | Creates an empty layer and may change the current layer. Check `layer.setCurrent` before adding art.; disabled in catalogue snapshot |
| `layer.newSublayer` | New Sublayer… | Window > Layers | {parent?: layer id (default: the highlighted row's layer, else the current layer), bottom?: bool, name?, …options as layer.new} a sublayer on top of the parent's contents; `bottom`: under t… | disabled in catalogue snapshot |
| `layer.outlineOthers` | Outline Others | Window > Layers | {ids?\|id?} turn Preview off (outline view) for every top-level layer but those holding the highlighted rows (else the current layer), which preview → {count} | disabled in catalogue snapshot |
| `layer.pasteRemembersLayers` | Paste Remembers Layers | Window > Layers | {on?} (default: toggle) the document option: on, the Paste commands put objects back into the layers they were copied from (by name; a missing one is made on top), off into the current laye… | disabled in catalogue snapshot |
| `layer.previewAll` | Preview All Layers | Window > Layers | {} turn Preview on for every layer and sublayer → {count} | disabled in catalogue snapshot |
| `layer.releaseToLayers` | Release to Layers (Sequence) | Window > Layers | {id?: layer or group (default: the highlighted row, else the current layer), build?: bool} each object in it goes into a new sublayer of its own, in stacking order (a group's objects go int… | disabled in catalogue snapshot |
| `layer.releaseToLayersBuild` | Release to Layers (Build) | Window > Layers | {id?} layer.releaseToLayers with build: true → {ids} | disabled in catalogue snapshot |
| `layer.reverse` | Reverse Order | Window > Layers | {ids?\|id?} (default: the highlighted rows) reverse the stacking order of two or more rows that share a layer or group; each keeps the places the others held. One undo step | disabled in catalogue snapshot |
| `layer.selectAll` | Select Art |  | {id, add?: bool} the Layers panel's selection column: select the visible, unlocked art of a layer (its sublayers' too), or the object itself; `add` (Shift-click) adds it to the selection, o… | disabled in catalogue snapshot |
| `layer.setCurrent` | Set Current Layer |  | {id} click a row: it alone is highlighted, and the layer it is (or the layer it is in) becomes the current layer, where new art goes. Not an undo step → {id, layer} | disabled in catalogue snapshot |
| `layer.setProps` | Layer Options… | Window > Layers | {ids?\|id? (default: the highlighted rows, else the current layer), name? (with prefs.identifyObjectsBy xmlId: a valid XML ID, stored as the object name), visible?, locked?, template?, print… | disabled in catalogue snapshot |
| `layer.showAll` | Show All Layers | Window > Layers | {} show every layer and sublayer → {count} | disabled in catalogue snapshot |
| `layer.target` | Target |  | {id, add?: bool (Shift-click: the item joins the selection, or leaves it when all selected; nothing is targeted)} target a layer, group or object as clicking its target circle in the Layers… | disabled in catalogue snapshot |
| `layer.template` | Template | Window > Layers | {ids?\|id?, on?: bool (default: toggle the first)} make layers templates (locked, dimmed, left out of print and export) or ordinary layers again (layer.setProps template) → {on} | disabled in catalogue snapshot |
| `layer.unlockAll` | Unlock All Layers | Window > Layers | {} unlock every layer and sublayer → {count} | disabled in catalogue snapshot |

## `perspective` (25)

Perspective commands place art on a perspective grid. Duplicate the art first; transforms are hard to invert.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `perspective.attach` | Attach to Active Plane |  | {ids?\|id?, plane?: left\|right\|ground (default: the active plane)} project the objects onto the plane | disabled in catalogue snapshot |
| `perspective.draw` | Draw in Perspective |  | {command: shape.* id, params, plane?, snap?: bool (default: Snap to Grid), at?: [x, y] (a point of the plane the shape lies on, as the tool gives it)} run a shape command and attach the res… | disabled in catalogue snapshot |
| `perspective.editText` | Edit Text |  | {id? (default: the selected type)} Object › Perspective › Edit Text: show type in perspective flat where it is drawn, in isolation mode, to edit it (text.* commands, the Type tool); exiting… | disabled in catalogue snapshot |
| `perspective.grid.define` | Define Perspective Grid |  | {name?: preset name ("" = custom), kind?: 1\|2\|3, units?: unit name (points, pixels, inches, centimeters, millimeters…), scale?: [artboard, real world], gridline?: gridline every, angle?: vi… | disabled in catalogue snapshot |
| `perspective.grid.get` | Perspective Grid |  | {} → {grid: the model (as perspective.grid.set takes it), define: the Define Grid fields (as perspective.grid.define takes them), station: {x, y, distance} (the viewer: centre of vision on … | disabled in catalogue snapshot |
| `perspective.grid.lock` | Lock Grid |  | {on?: bool} (no param toggles) View › Perspective Grid › Lock Grid: the grid's widgets can't be dragged (the Plane Switching Widget still works). View state: not an undo step → {on} | disabled in catalogue snapshot |
| `perspective.grid.lockStation` | Lock Station Point |  | {on?: bool} (no param toggles) dragging one vanishing point moves the other around the station point (the viewing angle turns, the viewer stays). View state: not an undo step → {on} | disabled in catalogue snapshot |
| `perspective.grid.preset` | Perspective Grid Preset |  | {kind: 1\|2\|3 (its normal view) \| name: a preset (see perspective.presets.list)} reset the grid to the preset fitted to the first artboard (and show it; attached objects stay attached) | disabled in catalogue snapshot |
| `perspective.grid.rulers` | Show Rulers |  | {on?: bool} (no param toggles) a ruler up the line where the planes meet, in the grid's units at its scale. View state: not an undo step → {on} | disabled in catalogue snapshot |
| `perspective.grid.set` | Define Perspective Grid |  | {kind?: 1\|2\|3, origin?: [x,y], horizon?, vpLeft?, vpRight?, vpVertical?: [x,y], distance?, cell?, extent?, height?, visible?, plane?, leftOffset?, rightOffset?, groundOffset?: pt (planes mo… | disabled in catalogue snapshot |
| `perspective.grid.show` | Show Perspective Grid |  | {visible?: bool} (no param toggles). View state: not an undo step | disabled in catalogue snapshot |
| `perspective.grid.snap` | Snap to Grid |  | {on?: bool} (no param toggles) art drawn or moved in perspective lands on gridlines within a quarter cell (on by default). View state: not an undo step → {on} | disabled in catalogue snapshot |
| `perspective.move` | Move in Perspective |  | {ids?\|id?, from: [x,y], to: [x,y], plane?, copy?: bool (move copies, as Alt-dragging does), perpendicular?: bool (move along the plane's normal instead, as pressing 5 while dragging does), … | disabled in catalogue snapshot |
| `perspective.nudge` | Nudge in Perspective |  | {dx, dy: arrow direction (-1, 0 or 1), big?: bool (×10), copy?: bool} move the selection in perspective by the keyboard increment, as the arrow keys do with the Perspective Selection tool →… | disabled in catalogue snapshot |
| `perspective.plane.matchObject` | Move Plane to Match Object |  | {id? (default: the first selected object)} move the plane the object is attached to onto the object and make it the active plane → {plane, offset} | disabled in catalogue snapshot |
| `perspective.plane.move` | Move Plane |  | {plane?: left\|right\|ground (default: the active plane), offset?: pt (where along its normal; 0 is its place in the grid's definition) \| by?: pt, objects?: none\|move\|copy (default none: the … | disabled in catalogue snapshot |
| `perspective.plane.set` | Active Perspective Plane |  | {plane: left\|right\|ground\|none} Plane Switching widget. View state: not an undo step | disabled in catalogue snapshot |
| `perspective.presets.delete` | Delete Perspective Grid Preset |  | {name} delete a saved preset (built-in ones stay) → {deleted: name} |  |
| `perspective.presets.export` | Export Perspective Grid Presets |  | {names?: [preset names, built-in ones too] (default: every saved preset), path?} write the presets as a .vcperspective file (JSON) → {path, count}; without path → {data: the file's text, co… |  |
| `perspective.presets.import` | Import Perspective Grid Presets |  | {path? \| data?: file text \| dataBase64?, replace?: false (replace saved presets of the same names; else imported ones whose name is taken get a number)} add the presets of a .vcperspective … |  |
| `perspective.presets.list` | Perspective Grid Presets |  | {} → {presets: [{builtIn, name, kind, …the perspective.grid.define fields}]} the built-in views (fitted to the first artboard, protected) first, then the saved presets |  |
| `perspective.presets.save` | Save Perspective Grid Preset |  | {name?: (default: a new "Perspective Preset N"), newName?: rename it, preset?: the preset to start from (default: the saved preset `name`, else the document's grid), …the fields of perspect… |  |
| `perspective.release` | Release with Perspective |  | {ids?\|id?} detach from the grid (geometry unchanged) | disabled in catalogue snapshot |
| `perspective.transform` | Transform in Perspective |  | {ids?\|id?, matrix: [a,b,c,d,e,f] (affine map in plane coordinates, points: u along the plane, v up or away), depth?: pt to move along the plane's normal (default 0), copy?: bool, plane?} tr… | disabled in catalogue snapshot |
| `perspective.widget.options` | Perspective Grid Options |  | {show?: bool, position?: topLeft\|topRight\|bottomLeft\|bottomRight} the Plane Switching Widget: shown or not, and the corner of the document window it stays in (kept with the preferences; no … |  |

## `slice` (1)

Slices define web-export regions. They only matter if the export path consumes slices.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `slice.list` | List Slices |  | {} the slices as laid out, numbered left to right and top to bottom → {slices: [{number, id (null for auto slices), source: "user"\|"object"\|"auto", name, x, y, width, height, options, selec… | disabled in catalogue snapshot |

## `symbol` (23)

Symbols are reusable instances. Editing the symbol changes every instance; break the link before one-off changes.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `symbol.addFromLibrary` | Add to Symbols | Window > Symbol Libraries | {library: id or name, name? \| names?: [symbol names in the library] (default: all of it), place?: false (also place an instance of the first one, its registration point at x, y: default the… | disabled in catalogue snapshot |
| `symbol.adjust` | Symbolism Tool |  | {tool: shift\|scrunch\|size\|spin\|stain\|screen\|style, points: [[x,y]…], radius?: 40, intensity?: 1..10 (5), alt?: bool, color? (#rrggbbaa and #rgba are refused), keepModel?: bool (as paint.set… | disabled in catalogue snapshot |
| `symbol.breakLink` | Break Link to Symbol |  | {ids?\|id?} expand selected instances into plain art (with their appearance changes to a dynamic symbol), placed through the symbol's 9-slice guides when it has them, with the instance's opa… | disabled in catalogue snapshot |
| `symbol.delete` | Delete Symbol |  | {name \| names: [name…], expandInstances?: true} delete a symbol (or several, in one undo step); its instances are expanded (or deleted with false) | disabled in catalogue snapshot |
| `symbol.duplicate` | Duplicate Symbol |  | {name, newName?} → {name} | disabled in catalogue snapshot |
| `symbol.edit` | Edit Symbol |  | {id?, ids?: [id…] (instead of id), name?, x?, y?, artboard?: index=0 (the active artboard; the app passes it), viewCenter?: [x, y] (the app passes the view's center)} edit a symbol's art in… | disabled in catalogue snapshot |
| `symbol.exitEditing` | Exit Symbol Editing Mode |  | {} leave symbol editing mode; after an edit, select the instance it was entered from; leaving without having changed the art adds no undo step and restores the selection from before entry (… | disabled in catalogue snapshot |
| `symbol.instance.reset` | Reset Symbol Instance |  | {ids?\|id?} drop the selected dynamic symbol instances' own appearance changes, so they show the symbol's appearance again → {ids: the instances that had changes} | disabled in catalogue snapshot |
| `symbol.instance.setAppearance` | Symbol Instance Appearance |  | {id?\|ids?: [one id] (default: the one selected object), path: [i…] (the object in the symbol's art: child indices in paint order from the art's root down through its groups; [] the root), f… | disabled in catalogue snapshot |
| `symbol.libraries` | Symbol Libraries |  | {} → {libraries: [{id, name, category: "builtIn"\|"user" (User Defined: the .vectorcraft files in the user library folder, rescanned now)\|"loaded" (symbol.loadLibrary), count, path?}], userF… |  |
| `symbol.library` | Symbol Library |  | {library: id or name} → {id, name, category, symbols: [{name, size: [w, h], registration: 0..8, exportType}] (as symbol.list)} |  |
| `symbol.list` | Symbols |  | {} → {symbols: [{name, instances, size: [w,h], registration: 0..8, exportType: movieClip\|graphic, nineSlice, type: static\|dynamic}], current} | disabled in catalogue snapshot |
| `symbol.loadLibrary` | Other Library… | Window > Symbol Libraries | {path? \| data?: file text \| dataBase64?, name?: file name (default: the path's)} load the symbols of any document VectorCraft opens (see document.formats), a saved symbol library included, … |  |
| `symbol.new` | New Symbol… |  | {name?, ids?\|id?, registration?: 0..8 (9-point grid, 4 = centre; Symbol Options › Registration), exportType?: movieClip (default)\|graphic, nineSlice?: bool, nineSliceGuides?: array, type?: … | disabled in catalogue snapshot |
| `symbol.options` | Symbol Options… |  | {name?, newName?, registration?: 0..8, exportType?: movieClip\|graphic, nineSlice?: bool, nineSliceGuides?: array, type?: static\|dynamic} rename a symbol and/or set Symbol Options › Registra… | disabled in catalogue snapshot |
| `symbol.place` | Place Symbol Instance |  | {name?, x?, y?} place an instance so its registration point is at (x, y) (default: artboard centre; name default: current) → {id} | disabled in catalogue snapshot |
| `symbol.replace` | Replace Symbol |  | {name, ids?\|id?} swap the symbol of the selected instances (an instance given a different symbol drops its appearance changes; one given its own symbol keeps them) → {ids} | disabled in catalogue snapshot |
| `symbol.saveLibrary` | Save Symbol Library… | Window > Symbols | {path?, names?: [symbol names] (default: all), name?: library name (default: the document's), user?: false (save into the user library folder, listed under User Defined)} save the document'… | disabled in catalogue snapshot |
| `symbol.selectInstances` | Select All Instances |  | {name} select every instance of a symbol → {count} | disabled in catalogue snapshot |
| `symbol.setCurrent` | Current Symbol |  | {name} the symbol the symbolism tools spray (not an undo step) | disabled in catalogue snapshot |
| `symbol.spray` | Symbol Sprayer |  | {points: [[x,y]…], name?, radius?: 40, density?: 1..10 (5), scale?: 1, alt?: bool (remove instances)} spray instances into a symbol set → {id, count} | disabled in catalogue snapshot |
| `symbol.unused` | Select All Unused |  | {} → {names: [the symbols nothing places, in panel order]} (the Symbols panel selects them): instances in the art (opacity masks included), graph designs, pattern tiles (with the tiles that… | disabled in catalogue snapshot |
| `symbol.update` | Redefine Symbol |  | {name, ids?\|id?} replace the symbol's art with the selection (instances update, keeping their appearance changes to the objects at paths the new art still has; the selection becomes an inst… | disabled in catalogue snapshot |

## `view` (19)

View commands change the editing view, not the artwork. Do not expect them to affect exported pixels.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `view.capsLock` | Caps Lock Cursor State |  | {on?: bool} set or read the Caps Lock state the desktop app reports; while it is on, the drawing tools show the precise crosshair, and Use Precise Cursors keeps its saved value → {on} |  |
| `view.drawMode` | Drawing Mode |  | {mode?: normal\|behind\|inside} (inside needs one selected path, compound path or type; no param cycles normal → behind → inside → normal, going from behind back to normal when Draw Inside ca… | disabled in catalogue snapshot |
| `view.globalRulers` | Change to Global Rulers | View > Rulers | {global?: bool (default: toggle)} global rulers measure the whole document from one zero point; artboard rulers (a new document's) from the active artboard's top-left corner, or the zero po… | disabled in catalogue snapshot |
| `view.guides.clear` | Clear Guides | View > Guides | {} delete all ruler guides and guide paths → {count} | disabled in catalogue snapshot |
| `view.guides.lock` | Lock Guides | View > Guides | {locked?: bool} toggle (or set) the session's guide lock; locking deselects the ruler guides and guide paths in every open document → {locked} | disabled in catalogue snapshot |
| `view.guides.make` | Make Guides | View > Guides | {} turn the selected paths into guides → {count} | disabled in catalogue snapshot |
| `view.guides.release` | Release Guides | View > Guides | {index?: a ruler guide's index, ids?: [guide path id…]} turn guides into paths: index releases that ruler guide and ids release those guide paths (and the guide paths inside them); otherwis… | disabled in catalogue snapshot |
| `view.overprintPreview` | Overprint Preview | View | {on?: bool (default: toggle)} → proof state |  |
| `view.printTiling` | Show Print Tiling | View | {on?: bool (default: toggle)} show the pages of the document's print settings on the canvas (each document has its own setting; the Print Tiling tool shows them too) → {on} | disabled in catalogue snapshot |
| `view.proofColors` | Proof Colors | View | {on?: bool (default: toggle)} → proof state |  |
| `view.proofSetup` | Proof Setup | View > Proof Setup | {target?: "workingCmyk"\|"cmyk:<profile>"\|"legacyMacRgb"\|"srgb"\|"monitorRgb"\|"protanopia"\|"deuteranopia"\|"tritanopia", intent?, simulatePaper?, proof?: bool (also turn Proof Colors on)} → pr… |  |
| `view.saved.edit` | Edit Views… | View | {name, newName?: rename, delete?: bool} \| {edits: [{name, newName?, delete?}…]} rename or delete saved views, all in one undo step; names are those before the edit and must stay unique; no … | disabled in catalogue snapshot |
| `view.saved.list` | Saved Views |  | {} → {views: [{name, center, zoom, rotation}]} | disabled in catalogue snapshot |
| `view.saved.new` | New View… | View | {name?, center: [x, y], zoom: (1 = 100%), rotation?: deg} save a view in the document (the app fills in the current one; default "View N"; at most 25, names up to 255 characters, each name … | disabled in catalogue snapshot |
| `view.separationsPreview` | Separations Preview |  | {on?: bool, plates?: [names], toggle?: plate, only?: plate} Separations Preview: show the chosen plates (one plate = greyscale ink coverage) → {on, plates: [{name, spot, visible, rgb}]} |  |
| `view.slices.hide` | Hide Slices | View | {hidden?: bool} toggle (or set) whether the canvas hides the slices (session view state); hiding deselects the slices in every open document, and showing them again leaves them deselected a… | disabled in catalogue snapshot |
| `view.slices.lock` | Lock Slices | View | {locked?: bool} toggle (or set) the slice lock: locked slices can't be selected or edited with the Slice Selection tool; locking deselects the slices in every open document, and unlocking l… | disabled in catalogue snapshot |
| `view.snapToGlyph.options` | Snap to Glyph Options |  | {baseline?: bool, xHeight?: bool, bounds?: bool, proximity?: bool, angular?: bool, anchors?: bool} the Character panel's Snap to Glyph options, kept in the preferences (the glyphSnap group,… |  |
| `view.transparencyGrid` | Show Transparency Grid | View | {on?: bool (default: toggle)} show the transparency grid behind the active document's artboards (each document has its own setting) → {on} | disabled in catalogue snapshot |
