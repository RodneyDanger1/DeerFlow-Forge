# VectorCraft Select Edit

Auto-generated from the installed 918-command catalogue (snapshot 2026-11-05). Every row is a real command id; params are abbreviated from the catalogue's own text. Read the full params string with `$VC commands` before running. Tips are practical notes, not substitutes for the schema.

Commands: **106** across 8 groups.

## Coverage

`attributes` 2 · `clipboard` 12 · `dimension` 3 · `edit` 30 · `image` 1 · `node` 1 · `select` 55 · `tool` 2

## `attributes` (2)

Attributes hold non-geometric metadata (e.g. overprint). Check them when output differs from the screen.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `attributes.info` | Attributes |  | {ids?\|id?, item?, target?: "object"\|"contents"} → {ids, overprintFill, overprintStroke, showCenter, imageMap: "none"\|"rectangle"\|"polygon", url, note, fillRule: "nonZero"\|"evenOdd" (of the … | disabled in catalogue snapshot |
| `attributes.set` | Attributes |  | {overprintFill?: bool, overprintStroke?: bool (aimed as object.setOverprint's fill and stroke, item? too), showCenter?: bool (the canvas shows the selected object's centre point), imageMap?… | disabled in catalogue snapshot |

## `clipboard` (12)

Clipboard commands move data between documents/apps. Clipboard state is external to the file; do not rely on it for reproducibility.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `clipboard.conflicts` | Swatch Conflicts |  | {} → {swatches: [{name, document, clipboard, spot}]} the global or spot swatches the copied objects use whose name the active document gives another colour (`document`/`clipboard`: #rrggbb)… | disabled in catalogue snapshot |
| `clipboard.exportPdf` | Clipboard as PDF |  | {} → {dataBase64, warnings} a one-page PDF of the copied objects, the page their visual bounds (dataBase64 null when the clipboard is empty); warnings as for document.export |  |
| `clipboard.exportPng` | Clipboard as PNG |  | {scale?: 1 (pixels per point, up to 64)} → {dataBase64, width, height (px), warnings} the copied objects cropped to their visual bounds, transparent around them (dataBase64 null when the cl… |  |
| `clipboard.exportSvg` | Clipboard as SVG |  | {} → {svg} the copied objects as standalone SVG (null when the clipboard is empty) |  |
| `clipboard.exportText` | Clipboard as Text |  | {} → {text} the copied type objects' text, one object per line (null unless every copied object is type, or a group of type) |  |
| `clipboard.flavours` | Clipboard Formats |  | {} → {flavours: [mime…]} what Copy offers other apps for the current clipboard, best first, by the Clipboard Handling preferences: text/plain (a type-only copy's text, else the SVG markup w… |  |
| `clipboard.importEmf` | Load Metafile into Clipboard |  | {dataBase64 (EMF or WMF bytes), center?: [x, y]} replace the clipboard with the picture's objects (paths, clipping groups, images, point type; the images they use), centred on `center` (def… | disabled in catalogue snapshot |
| `clipboard.importEps` | Load EPS into Clipboard |  | {dataBase64 (EPS or other PostScript bytes), center?: [x, y]} replace the clipboard with the picture's objects as document.open reads an EPS (editable paths, type and images, with the image… | disabled in catalogue snapshot |
| `clipboard.importImage` | Load Image into Clipboard |  | {dataBase64 (PNG, JPEG, GIF, WebP, TIFF or BMP bytes), mime?: the type the system clipboard gave (an image/… type; the format is read from the bytes), center?: [x, y]} replace the clipboard… | disabled in catalogue snapshot |
| `clipboard.importPdf` | Load PDF into Clipboard |  | {dataBase64, page?: 1, password? (an encrypted PDF), editingData?: false (true: the data is a .ai or .ait file, read as document.open reads it; when document.open would use its editing data… | disabled in catalogue snapshot |
| `clipboard.importSvg` | Load SVG into Clipboard |  | {svg \| dataBase64 (SVG or SVGZ bytes), center?: [x, y]} replace the clipboard with the SVG's objects (and the images, patterns and symbols they use), centred on `center` (default: the first… | disabled in catalogue snapshot |
| `clipboard.importText` | Load Text into Clipboard |  | {text, center?: [x, y]} replace the clipboard with point text of `text` (one paragraph per line; trailing line breaks dropped) in the default type style, centred on `center` (default: the f… | disabled in catalogue snapshot |

## `dimension` (3)

Dimension objects annotate technical drawings; they are not part of a brand asset unless intended.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `dimension.applyToAll` | Apply to All |  | {id?: dimension id (default the first selected dimension)} gives every dimension in the document that dimension's style (its scale too), as one undo step → {ids} | disabled in catalogue snapshot |
| `dimension.create` | Create Dimension |  | {mode?: linear\|angular\|radius\|diameter, a?: [x,y], b?: [x,y], vertex?: [x,y], source?: {kind: segment, edge: {node,subpath,segment}}\|{kind: angle, first: edge, second: edge}\|{kind: circle, … | disabled in catalogue snapshot |
| `dimension.update` | Update Dimensions |  | {ids?: [dimension ids] (default selection), options?: dimension options, offset?: pt} restyle or move existing dimensions → {ids} | disabled in catalogue snapshot |

## `edit` (30)

Edit commands manipulate clipboard/undo/duplicate state. Undo/redo are not a substitute for a copy of the file.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `edit.assignProfile` | Assign Profile… | Edit | {rgb?: profile\|null, cmyk?: profile\|null} tag the document with profiles (colour numbers are kept) → {rgb, cmyk} | disabled in catalogue snapshot |
| `edit.clear` | Clear | Edit | {ids?, guides?: bool (with ids: also delete the selected ruler guides)} delete the objects `ids`, else the selection (fully selected objects and direct-selected anchors together, else ruler… | disabled in catalogue snapshot |
| `edit.clearHistory` | Clear History |  | {} remove every undo and redo step of the active document (the History panel menu's Clear History): the document stays as it is, and clearing is not an undo step → {cleared: the number of s… | disabled in catalogue snapshot |
| `edit.colorSettings` | Color Settings… | Edit | {rgb?: profile, cmyk?: profile, intent?: "perceptual"\|"relative"\|"saturation"\|"absolute", bpc?: bool} set the working spaces → {rgb, cmyk, intent, bpc, profiles: [{name, kind, builtin}]} |  |
| `edit.colors.adjustBalance` | Adjust Color Balance… | Edit > Edit Colors | {mode?: "rgb"\|"cmyk"\|"gray"\|"global" (default: from the channels given), r?, g?, b? \| c?, m?, y?, k? \| gray? \| tint?: -100..100 (% added per channel, default 0; `tint` is global mode: it sh… | disabled in catalogue snapshot |
| `edit.colors.blendFrontToBack` | Blend Front to Back | Edit > Edit Colors | {} ≥3 filled objects (solid fills or gradient meshes, which keep their shading): intermediate fills graded between the frontmost and backmost fill → {changed} | disabled in catalogue snapshot |
| `edit.colors.blendHorizontally` | Blend Horizontally | Edit > Edit Colors | {} ≥3 filled objects or meshes: fills graded between the leftmost and rightmost → {changed} | disabled in catalogue snapshot |
| `edit.colors.blendVertically` | Blend Vertically | Edit > Edit Colors | {} ≥3 filled objects or meshes: fills graded between the topmost and bottommost → {changed} | disabled in catalogue snapshot |
| `edit.colors.invert` | Invert Colors | Edit > Edit Colors | {fill?: true, stroke?: true, includeImages?: true, includePatterns?: true, ids?} replace each colour by its RGB inverse (keeps the colour model) in fills, strokes, text, gradient meshes (wi… | disabled in catalogue snapshot |
| `edit.colors.overprintBlack` | Overprint Black… | Edit > Edit Colors | {remove?: false, percentage?: 100, fill?: true, stroke?: true, includeCmyBlacks?: false, includeSpotBlacks?: false, ids?} make the black fills and/or strokes of the selection (or ids; group… | disabled in catalogue snapshot |
| `edit.colors.saturate` | Saturate… | Edit > Edit Colors | {intensity: -100..100 (%; a number outside the range counts as its nearest end), fill?, stroke?, includeImages?, includePatterns?, ids?} scale saturation by (1 + intensity/100), reaching wh… | disabled in catalogue snapshot |
| `edit.colors.toCMYK` | Convert to CMYK | Edit > Edit Colors | {fill?, stroke?, includeImages?, includePatterns?, ids?} (as edit.colors.invert) → {changed} | disabled in catalogue snapshot |
| `edit.colors.toGrayscale` | Convert to Grayscale | Edit > Edit Colors | {fill?, stroke?, includeImages?, includePatterns?, ids?} (as edit.colors.invert) → {changed} | disabled in catalogue snapshot |
| `edit.colors.toRGB` | Convert to RGB | Edit > Edit Colors | {fill?, stroke?, includeImages?, includePatterns?, ids?} (as edit.colors.invert) → {changed} | disabled in catalogue snapshot |
| `edit.copy` | Copy | Edit | {} the selection with what it uses, and the selected ruler guides (pasted on the layer new art goes to, moved as the objects are; alone, where they were); the Artboard tool chosen: artboard… | disabled in catalogue snapshot |
| `edit.cut` | Cut | Edit | {} (selected ruler guides go too; the Artboard tool chosen: artboard.cut) | disabled in catalogue snapshot |
| `edit.dropSelection` | Drop Artwork |  | {sourceDocument: uid, ids: [id…], grab: [x,y], at: [x,y]} copy 1–10000 editable source objects from an open document to the active document, preserving the grab point and clipboard, as one … | disabled in catalogue snapshot |
| `edit.duplicate` | Duplicate | Edit | {ids?: [id…] (selected first; default: the selection), dx?, dy?} duplicate the selection in place (offset optional) | disabled in catalogue snapshot |
| `edit.findNext` | Find Next | Edit | {find, matchCase?, wholeWord?} select the next text object (after the selected one, wrapping) containing `find` → {id\|null} | disabled in catalogue snapshot |
| `edit.findReplace` | Find and Replace… | Edit | {find, replace?: "", matchCase?: false, wholeWord?: false, ids?} replace in every text object (or ids) → {count}. Matches never span style runs. | disabled in catalogue snapshot |
| `edit.paste` | Paste | Edit | {center?: [x, y], dx?, dy?, swatchConflict?} paste centred on `center` (the app passes the view centre), else offset by dx/dy (default: the Paste Offset preference). Pasting brings the imag… | disabled in catalogue snapshot |
| `edit.pasteInBack` | Paste in Back | Edit | {swatchConflict?, artboard?: index (as edit.pasteInFront)} paste in place just below the bottom selected object, or at the bottom of the current layer when nothing is selected (resources an… | disabled in catalogue snapshot |
| `edit.pasteInFront` | Paste in Front | Edit | {swatchConflict?, artboard?: index (the active artboard: the objects go where they were on the artboard they were copied from, on this one)} paste in place just above the top selected objec… | disabled in catalogue snapshot |
| `edit.pasteInPlace` | Paste in Place | Edit | {swatchConflict?, artboard?: index (as edit.pasteInFront)} paste where the objects were copied (resources, layers and drawing modes as edit.paste) → {ids, added, merged, renamed} | disabled in catalogue snapshot |
| `edit.pasteOnAllArtboards` | Paste on All Artboards | Edit | {swatchConflict?} paste a copy on every artboard at the offset the objects had to the artboard they were copied from (resources, layers and drawing modes as edit.paste) → {ids, added, merge… | disabled in catalogue snapshot |
| `edit.pasteWithoutFormatting` | Paste without Formatting | Edit | {center?, dx?, dy?, swatchConflict?} paste as edit.paste; pasted text takes the default character style (one run) and leaves its character and paragraph styles behind → {ids, added, merged,… | disabled in catalogue snapshot |
| `edit.redo` | Redo | Edit | {} | disabled in catalogue snapshot |
| `edit.undo` | Undo | Edit | {} | disabled in catalogue snapshot |
| `edit.undoGroup.begin` | Begin Undo Group |  | {label?: string} until edit.undoGroup.end, the edits made in the document active at the begin, and in each document opened or created before then (also when no document is open; the edits o… |  |
| `edit.undoGroup.end` | End Undo Group |  | {cancel?: bool} close the undo group: its edits stay one undo step or, with `cancel`, are undone |  |

## `image` (1)

VectorCraft's `image` group has only `image.info`; raster placement uses `file.place`, raster cropping `object.cropImage`, rasterizing `object.rasterize`.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `image.info` | Image Info |  | {id?} an image object (default: the one selected) → {id, name, linked, link, colorMode: RGB\|Grayscale\|CMYK, pixelWidth, pixelHeight, ppi: [x, y] at its placed size, width, height} | disabled in catalogue snapshot |

## `node` (1)

Node editing is a low-level path operation; confirm the target object and node indices.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `node.move` | Reorder |  | {id, parent?: id (null = top level), index} put a row at `index` (0 = bottom) of `parent` (layers only at the top level or in layers), deselecting every selected object left hidden or locke… | disabled in catalogue snapshot |

## `select` (55)

Selection commands define what later commands affect. `select.all` is required before many trace/path operations; `select.set` replaces a selection, `select.add` extends it.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `select.add` | Add to Selection |  | {ids: [id…]} all ids must be non-negative integers naming existing objects → {count, ids} (resulting selection) | disabled in catalogue snapshot |
| `select.all` | All | Select | {} → {count}; while the Type tool edits text, all of that text instead → {editing, start, end} (byte offsets); in a frame of threaded text, the whole story: the tool edits the thread's firs… | disabled in catalogue snapshot |
| `select.allOnArtboard` | All on Active Artboard | Select | {artboard?: index (0-based; the app passes the active one; default: the first)} | disabled in catalogue snapshot |
| `select.anchors` | Select Anchors |  | {id, anchors: [[subpath, anchor]…], mode: "set"\|"add"\|"toggle"} | disabled in catalogue snapshot |
| `select.anchorsMany` | Select Anchors |  | {items: [{id, anchors}], mode?: "set"\|"add"\|"toggle"\|"subtract" (set by default; add: true is mode add), add?: bool (an older way to ask for mode add)}: toggle selects the anchors not selec… | disabled in catalogue snapshot |
| `select.color` | Select by Color |  | {fill?: colour, stroke?: colour (as paint.setFill's color, #rrggbbaa and #rgba refused; at least one)} select the objects whose fill (and stroke) reads as that colour in #rrggbb, as documen… | disabled in catalogue snapshot |
| `select.editSaved` | Edit Selection… | Select | {name, newName?: rename, delete?: bool} \| {edits: [{name, newName?, delete?}…]} rename or delete saved selections, all in one undo step; names are those before the edit and must stay unique | disabled in catalogue snapshot |
| `select.font` | Select Text by Font |  | {family, style?} select the text objects using the font, and the instances of the symbols whose art uses it, that are not hidden or locked, in a hidden or locked group or layer, or on a loc… | disabled in catalogue snapshot |
| `select.globalEdit` | Start Global Edit | Select | {appearance?: bool, size?: bool, artboards?: "all" \| range such as "1, 3-5", includeCanvas?: bool} (each defaults to the Global Edit Options) while Global Edit is off: start it on the one s… | disabled in catalogue snapshot |
| `select.globalEditExclude` | Leave Out of Global Edit |  | {id} while Global Edit is on: leave the object `id` of the Global Edit (not the one it started from) out of it, as a Shift-click on it with the Selection tool does: it is no longer highligh… | disabled in catalogue snapshot |
| `select.globalEditOptions` | Global Edit Options |  | {appearance?: bool, size?: bool, artboards?: "all" \| range such as "1, 3-5", includeCanvas?: bool} set the options Start Global Edit matches with (defaults: shape only, all artboards, objec… | disabled in catalogue snapshot |
| `select.inverse` | Inverse | Select | {} | disabled in catalogue snapshot |
| `select.key` | Cancel Key Object |  | {id?: a selected top-level object (not a layer, a compound-path member or an object inside another selected object); one of two or more or the only one with ruler guides selected (the Selec… | disabled in catalogue snapshot |
| `select.magicWand` | Magic Wand |  | {id, mode?: set\|add\|subtract} select objects similar to `id` by the Magic Wand settings → {count} | disabled in catalogue snapshot |
| `select.nextAbove` | Next Object Above | Select | {} | disabled in catalogue snapshot |
| `select.nextBelow` | Next Object Below | Select | {} | disabled in catalogue snapshot |
| `select.none` | Deselect | Select | {} | disabled in catalogue snapshot |
| `select.object.allOnSameLayers` | All on Same Layers | Select > Object | {} | disabled in catalogue snapshot |
| `select.object.areaText` | Area Text Objects | Select > Object | {} → {count} | disabled in catalogue snapshot |
| `select.object.bristleBrushStrokes` | Bristle Brush Strokes | Select > Object | {} objects whose topmost stroke has a bristle brush (type bristle in brush.list), whatever the brush is named → {count} | disabled in catalogue snapshot |
| `select.object.brushStrokes` | Brush Strokes | Select > Object | {} → {count} | disabled in catalogue snapshot |
| `select.object.clippingMasks` | Clipping Masks | Select > Object | {} | disabled in catalogue snapshot |
| `select.object.directionHandles` | Direction Handles | Select > Object | {} direct-select every anchor (showing all handles) of the selected paths and the paths inside the selected objects, leaving out paths that are hidden or locked, inside a hidden or locked o… | disabled in catalogue snapshot |
| `select.object.openPaths` | Open Paths | Select > Object | {} | disabled in catalogue snapshot |
| `select.object.pointText` | Point Text Objects | Select > Object | {} → {count} | disabled in catalogue snapshot |
| `select.object.slices` | Slices | Select > Object | {} select every user and object slice → {count} | disabled in catalogue snapshot |
| `select.object.strayPoints` | Stray Points | Select > Object | {} | disabled in catalogue snapshot |
| `select.object.textObjects` | All Text Objects | Select > Object | {} | disabled in catalogue snapshot |
| `select.recall` | Recall Selection | Select | {name} select the objects of a saved selection, leaving out those deleted since and those that are hidden or locked, inside a hidden or locked object or layer, on a template layer, or outsi… | disabled in catalogue snapshot |
| `select.reselect` | Reselect | Select | {} | disabled in catalogue snapshot |
| `select.same.appearance` | Appearance | Select > Same | {} | disabled in catalogue snapshot |
| `select.same.appearanceAttribute` | Appearance Attribute | Select > Same | {item?: appearance item index} the objects sharing an appearance attribute of the first selected object: its fill or stroke `item` (default: the Appearance panel's active item), else its fi… | disabled in catalogue snapshot |
| `select.same.blendingMode` | Blending Mode | Select > Same | {} | disabled in catalogue snapshot |
| `select.same.fillAndStroke` | Fill & Stroke | Select > Same | {} the objects with the first selected object's fill and stroke colours (tints, compound paths and Live Paint faces as select.same.fillColor) | disabled in catalogue snapshot |
| `select.same.fillColor` | Fill Color | Select > Same | {} the objects filled with the first selected object's fill colour (any tint of its global or spot swatch, the same tint with prefs selectSameTintPercent); a member path of a compound path … | disabled in catalogue snapshot |
| `select.same.fontFamily` | Font Family | Select > Same | {} → {count} | disabled in catalogue snapshot |
| `select.same.fontFamilyStyle` | Font Family & Style | Select > Same | {} → {count} | disabled in catalogue snapshot |
| `select.same.fontFamilyStyleSize` | Font Family, Style & Size | Select > Same | {} → {count} | disabled in catalogue snapshot |
| `select.same.fontSize` | Font Size | Select > Same | {} → {count} | disabled in catalogue snapshot |
| `select.same.graphicStyle` | Graphic Style | Select > Same | {} the objects linked to the graphic style the first selected object is linked to (compound paths as select.same.fillColor) | disabled in catalogue snapshot |
| `select.same.linkBlockSeries` | Link Block Series | Select > Same | {} select every frame of the threads of the selected type objects (and of the type inside selected groups); type in no thread selects itself; type and frames that are hidden or locked, insi… | disabled in catalogue snapshot |
| `select.same.opacity` | Opacity | Select > Same | {} | disabled in catalogue snapshot |
| `select.same.shapeType` | Shape | Select > Same | {} | disabled in catalogue snapshot |
| `select.same.strokeColor` | Stroke Color | Select > Same | {} the objects stroked with the first selected object's stroke colour (tints and compound paths as select.same.fillColor) | disabled in catalogue snapshot |
| `select.same.strokeWeight` | Stroke Weight | Select > Same | {} | disabled in catalogue snapshot |
| `select.same.symbolInstance` | Symbol Instance | Select > Same | {} select the instances of the symbol of the first selected object that can be selected, including a group member selected on its own; when that object is not a symbol instance, such as a g… | disabled in catalogue snapshot |
| `select.same.textFillAndStrokeColor` | Text Fill & Stroke Color | Select > Same | {} select the type objects with characters whose fill and stroke both match the first character of the first selected type → {count} | disabled in catalogue snapshot |
| `select.same.textFillColor` | Text Fill Color | Select > Same | {} → {count} | disabled in catalogue snapshot |
| `select.same.textStrokeColor` | Text Stroke Color | Select > Same | {} → {count} | disabled in catalogue snapshot |
| `select.save` | Save Selection… | Select | {name?} save the current selection under a name, in the document (default "Selection N"; an existing name is replaced; at most 25, names up to 255 characters) → {name} | disabled in catalogue snapshot |
| `select.savedList` | Saved Selections |  | {} → [name…] for the active document | disabled in catalogue snapshot |
| `select.segments` | Select Segments |  | {id, segments: [[subpath, segment]…], mode?: "set"\|"add"\|"toggle"} select path segments; their endpoints move with them, Delete removes only their connections | disabled in catalogue snapshot |
| `select.set` | Select Objects |  | {ids: [id…]} all ids must be non-negative integers naming existing objects → {count, ids} (resulting selection) | disabled in catalogue snapshot |
| `select.toggle` | Toggle Selection |  | {id} or {ids: [id…]}: each selected one leaves the selection, the others join it; all ids must be non-negative integers naming existing objects → {count, ids} (resulting selection) | disabled in catalogue snapshot |
| `select.update` | Update Selection | Select | {} make the saved selection last recalled (`select.recall`) hold the selected objects instead of its own, in one undo step → {name} | disabled in catalogue snapshot |

## `tool` (2)

Tool commands activate an editing tool. Headless automation should prefer the direct command, not tool activation.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `tool.select` | Select Tool |  | {tool} e.g. selection, directSelection, pen, rectangle, ellipse, polygon, star, lineSegment |  |
| `tool.setOption` | Tool Option |  | {key?, value? \| values?: {key: value…}, tool?: id (default: the active tool)} → the tool's options (`{}` reads them); kept options last across tool switches |  |
