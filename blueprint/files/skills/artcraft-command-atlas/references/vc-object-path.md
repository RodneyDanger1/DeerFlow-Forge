# VectorCraft Object Path

Auto-generated from the installed 918-command catalogue (snapshot 2026-11-05). Every row is a real command id; params are abbreviated from the catalogue's own text. Read the full params string with `$VC commands` before running. Tips are practical notes, not substitutes for the schema.

Commands: **212** across 7 groups.

## Coverage

`livePaint` 8 · `magicWand` 2 · `object` 151 · `path` 34 · `shape` 10 · `shapeBuilder` 2 · `shaper` 5

## `livePaint` (8)

Live Paint treats overlapping fills as paintable regions. Expand before exporting to plain SVG when the consumer cannot read live-paint groups.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `livePaint.expand` | Expand | Object > Live Paint | {id?, ids?: [id…] (instead of id)} turn Live Paint groups into plain groups of their painted faces and edges → {ids} | disabled in catalogue snapshot |
| `livePaint.fill` | Live Paint Bucket |  | {group?: id \| ids?\|id?: [id…] (paths to make live first, as livePaint.make does), point: [x,y], color?\|swatch?\|gradient?\|none? (default: current fill; a color in #rrggbbaa or #rgba is refus… | disabled in catalogue snapshot |
| `livePaint.gapOptions` | Gap Options |  | {id?, ids?: [id…] (instead of id; default: the selected Live Paint groups), detect?: bool (Gap Detection: paint stops at gaps up to size wide), size?: "small" (3 pt) \| "medium" (6 pt) \| "la… | disabled in catalogue snapshot |
| `livePaint.info` | Live Paint Info |  | {group, id?: object id (default: the selection)} → {faces: [{id, fill, bounds}], edges: [{id, stroke, width}], sources, gapOptions: {detect, size: "small"\|"medium"\|"large"\|pt, points, color… | disabled in catalogue snapshot |
| `livePaint.make` | Make | Object > Live Paint | {ids?\|id?} build a Live Paint group from the selected paths (paths, compound paths and groups of them; type, images and other objects are refused, nothing changes); each covered face starts… | disabled in catalogue snapshot |
| `livePaint.merge` | Merge | Object > Live Paint | {ids?\|id?} add the other selected paths (compound paths, groups of paths and Live Paint groups too; type, images and other objects are refused, nothing changes) to the bottom-most Live Pain… | disabled in catalogue snapshot |
| `livePaint.release` | Release | Object > Live Paint | {id?, ids?: [id…] (instead of id)} replace Live Paint groups with their original paths → {ids} | disabled in catalogue snapshot |
| `livePaint.strokeEdge` | Live Paint Bucket (Stroke) |  | {group: id, point: [x,y], color?\|swatch?\|none? (default: current stroke), width?: pt (default: current weight), tolerance?: pt (4), tint?: 0..100, keepModel?: bool (both as paint.setFill)} … | disabled in catalogue snapshot |

## `magicWand` (2)

Selects by colour/appearance similarity. It is selection-only; follow with a paint or object command.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `magicWand.options` | Magic Wand Settings |  | {} → the Magic Wand settings |  |
| `magicWand.set` | Magic Wand Options | Window > Magic Wand | {fillColor?, fillTolerance?: 0-255, strokeColor?, strokeTolerance?: 0-255, strokeWeight?, weightTolerance?: pt, opacity?, opacityTolerance?: %, blendingMode?, reset?: bool} → the settings |  |

## `object` (151)

Object commands act on whole objects/layers, not anchors. Most take `ids` or use the selection; `object.arrange.*` changes stacking, `object.group`/`ungroup` changes structure, `object.transform.*` changes geometry. Run `select.all` first only when you intend every object.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `object.align` | Align | Window > Align | {horizontal?: "left"\|"center"\|"right", vertical?: "top"\|"center"\|"bottom", to?: "selection"\|"artboard"\|"key" (default: the key object when the selection has one, select.key, else the select… | disabled in catalogue snapshot |
| `object.arrange.bringForward` | Bring Forward | Object > Arrange | {ids?: [id…] (selected first; default: the selection)} | disabled in catalogue snapshot |
| `object.arrange.bringToFront` | Bring to Front | Object > Arrange | {ids?: [id…] (selected first; default: the selection)} | disabled in catalogue snapshot |
| `object.arrange.sendBackward` | Send Backward | Object > Arrange | {ids?: [id…] (selected first; default: the selection)} | disabled in catalogue snapshot |
| `object.arrange.sendToBack` | Send to Back | Object > Arrange | {ids?: [id…] (selected first; default: the selection)} | disabled in catalogue snapshot |
| `object.arrange.sendToCurrentLayer` | Send to Current Layer | Object > Arrange | {ids?: [id…] (selected first; default: the selection)} | disabled in catalogue snapshot |
| `object.blend.expand` | Expand | Object > Blend | {} replace the selected blends by groups of their keys and steps, each keeping the blend's id, name, transparency (knockout and isolation included), opacity mask and appearance → {ids} | disabled in catalogue snapshot |
| `object.blend.info` | Blend Info |  | {} the options of the first selected blend, else those new blends start with → {target: blend\|defaults, id?, spacing: smooth\|steps\|distance, steps, distance, orientation: page\|path, easingT… |  |
| `object.blend.make` | Make | Object > Blend | {ids?, steps?: n \| distance?: pt \| smooth?: bool, orientation?: page\|path (default: the Blend Options set with nothing selected, else smooth colour and page), starts?: [anchor index \| null,… | disabled in catalogue snapshot |
| `object.blend.options` | Blend Options… | Object > Blend | {spacing?: smooth\|steps\|distance, value?: n, steps?: n, distance?: pt, orientation?: page\|path, smooth?: bool, easingType?: easeIn\|easeOut\|easeInOut\|easeOutIn, ramp?: pct, colorShift?: pct}… |  |
| `object.blend.release` | Release | Object > Blend | {} release the selected blends: the key objects come back and the spine stays as a path with no fill or stroke, below them; a blend with a name, opacity, blend mode, isolation, opacity mask… | disabled in catalogue snapshot |
| `object.blend.replaceSpine` | Replace Spine | Object > Blend | {} use the selected path as the spine of the selected blend (the path is consumed) | disabled in catalogue snapshot |
| `object.blend.reverseFrontToBack` | Reverse Front to Back | Object > Blend | {} reverse the stacking order of the selected blends | disabled in catalogue snapshot |
| `object.blend.reverseSpine` | Reverse Spine | Object > Blend | {} reverse the order of the key objects along the spine | disabled in catalogue snapshot |
| `object.blend.spine.addAnchor` | Add Spine Point |  | {id? (default: the selected blend), x, y} add a point to the blend's spine where it passes nearest (x, y) → {anchor} | disabled in catalogue snapshot |
| `object.blend.spine.convertAnchor` | Convert Anchor Point |  | {id? (default: the selected blend), anchor: index, to: smooth\|corner, x?, y?} convert a blend spine point: dragging a corner creates symmetric smooth handles, clicking a point with handles … | disabled in catalogue snapshot |
| `object.blend.spine.moveAnchor` | Move Spine Point |  | {id? (default: the selected blend), anchor: index, x, y, handle?: in\|out, independent?: bool} move a point of the blend's spine (its handles along), or with `handle` place that handle's end… | disabled in catalogue snapshot |
| `object.blend.spine.removeAnchor` | Delete Spine Point |  | {id? (default: the selected blend), anchor: index} delete a point of the blend's spine that no key object sits on | disabled in catalogue snapshot |
| `object.blend.spine.reshapeSegment` | Reshape Spine Segment |  | {id? (default: the selected blend), segment: index, t: 0..1, dx, dy, perpendicular?: bool} bend a segment of the blend's spine so its point at t moves by (dx, dy), as path.reshapeSegment be… | disabled in catalogue snapshot |
| `object.clippingMask.editContents` | Edit Contents | Object > Clipping Mask | {} select the clipped art of the selected clip groups → {count} | disabled in catalogue snapshot |
| `object.clippingMask.editMask` | Edit Clipping Path | Object > Clipping Mask | {} select the clipping paths of the selected clip groups → {count} | disabled in catalogue snapshot |
| `object.clippingMask.make` | Make | Object > Clipping Mask | {ids?: [id…] (selected first; default: the selection)} the topmost selected object (a path, compound path or text, which loses its paint) clips the others: compound holes, even-odd fills an… | disabled in catalogue snapshot |
| `object.clippingMask.release` | Release | Object > Clipping Mask | {ids?: [id…] (selected first; default: the selection)} the selected clip groups become plain groups; their clipping path (path, compound path or text) stays, with the paint it has (none unl… | disabled in catalogue snapshot |
| `object.compoundPath.make` | Make | Object > Compound Path | {ids?: [id…] (selected first; default: the selection)} | disabled in catalogue snapshot |
| `object.compoundPath.release` | Release | Object > Compound Path | {ids?: [id…] (selected first; default: the selection)} release the selected compound paths into their paths, each with the compound path's paint; a path of several subpaths (an SVG `d` with… | disabled in catalogue snapshot |
| `object.compoundShape.expand` | Expand Compound Shape | Window > Pathfinder | {ids?: [id…] (selected first; default: the selection)} the selected compound shapes (and those holding the selected objects) become the path, or compound path, of the area they draw, painte… | disabled in catalogue snapshot |
| `object.compoundShape.make` | Make Compound Shape | Window > Pathfinder | {ids?: [id…] (selected first; default: the selection), mode?: "add"\|"subtract"\|"intersect"\|"exclude" (default add; Alt-clicking a Shape Mode button gives its mode)} the two or more selected… | disabled in catalogue snapshot |
| `object.compoundShape.release` | Release Compound Shape | Window > Pathfinder | {ids?: [id…] (selected first; default: the selection)} the selected compound shapes (and those holding the selected objects) become their members again, as they were before Make Compound Sh… | disabled in catalogue snapshot |
| `object.compoundShape.setMode` | Shape Mode | Window > Pathfinder | {mode: "add"\|"subtract"\|"intersect"\|"exclude", ids?: [id…] (selected first; default: the selection)} the members of compound shapes that the selected objects are or are in take the shape mo… | disabled in catalogue snapshot |
| `object.convertDocumentColorMode` | Convert Document Color Mode |  | {…as file.documentColorMode} same as file.documentColorMode: {mode: "cmyk"\|"rgb", convert?: true, intent?, grays?} → {changed} (an alias kept for older scripts; the command palette leaves i… | disabled in catalogue snapshot |
| `object.createObjectMosaic` | Create Object Mosaic… | Object | {columns=10, rows=10 (whole numbers, kept within 1..1000), width?, height? (new size in pt; default the image's), spacingX=0, spacingY=0 (pt between tiles), gray?: bool, deleteRaster?: bool… | disabled in catalogue snapshot |
| `object.createTrimMarks` | Create Trim Marks | Object | {style?: "roman"\|"japanese" (default: the japaneseCropMarks preference; japanese: double lines at the trim and bleed edges plus centre marks), allArtboards?: bool (default: true when nothin… | disabled in catalogue snapshot |
| `object.cropImage` | Crop Image | Object | {rect?: [x, y, width, height] \| trim?: true (to the pixels that aren't fully transparent, pixel for pixel; an image with none to cut is left as it is, trimmed: false)} crop the selected ima… | disabled in catalogue snapshot |
| `object.distort` | Free Distort |  | {corners: [[x,y]×4] (TL, TR, BR, BL), from?: [x0,y0,x1,y1] (default: selection bounds), ids?} projective warp of anchors and handles | disabled in catalogue snapshot |
| `object.distribute` | Distribute | Window > Align | {horizontal?: "left"\|"center"\|"right", vertical?: "top"\|"center"\|"bottom", spacing?: pt (used with a key, select.key: the key object, or the key guide, select.key {guide}, stays put and the… | disabled in catalogue snapshot |
| `object.distributeSpacing` | Distribute Spacing | Window > Align | {axis?: "horizontal"\|"vertical" (default: "horizontal"), spacing?: pt (the key object, select.key, or the key guide, select.key {guide}, stays put and the others are spaced from it; a key g… | disabled in catalogue snapshot |
| `object.envelope.editContents` | Edit Contents | Object > Envelope Distort | {editing?: bool} toggle Edit Contents / Edit Envelope → {editing} | disabled in catalogue snapshot |
| `object.envelope.expand` | Expand | Object > Envelope Distort | {} replace the selected envelopes by groups of their distorted content (type outlined), keeping name, opacity, blend mode, isolation, knockout and opacity mask → {ids} | disabled in catalogue snapshot |
| `object.envelope.info` | Envelope Info |  | {} the selected envelope's settings, or with none selected the defaults new envelopes get → {id: n\|null, type: warp\|mesh\|topObject, style, bend, h, v, horizontal, rows, cols, fidelity, anti… | disabled in catalogue snapshot |
| `object.envelope.makeWithMesh` | Make with Mesh… | Object > Envelope Distort | {ids?, rows?: 1..50 (4), cols?: 1..50 (4), columns?: as cols} envelope the selected objects with a mesh of rows × cols patches → {id} | disabled in catalogue snapshot |
| `object.envelope.makeWithTopObject` | Make with Top Object | Object > Envelope Distort | {ids?} the topmost selected path becomes the envelope of the others → {id} | disabled in catalogue snapshot |
| `object.envelope.makeWithWarp` | Make with Warp… | Object > Envelope Distort | {ids?, style?: arc\|arcLower\|arcUpper\|arch\|bulge\|shellLower\|shellUpper\|flag\|wave\|fish\|rise\|fisheye\|inflate\|squeeze\|twist (arc), bend?: % -100..100 (50), h?: horizontal distortion % -100..100… | disabled in catalogue snapshot |
| `object.envelope.options` | Envelope Options… | Object > Envelope Distort | {fidelity?: 0..100, antiAlias?: bool, preserveShape?: clippingMask\|transparency, distortAppearance?: bool, distortLinearGradients?: bool, distortPatternFills?: bool (the last two work with … | disabled in catalogue snapshot |
| `object.envelope.release` | Release | Object > Envelope Distort | {} release the selected envelopes into their content and their shape (a grey gradient mesh for warp and mesh envelopes, the path for a top-object envelope; the content keeps the envelope's … | disabled in catalogue snapshot |
| `object.envelope.resetWithMesh` | Reset with Mesh… | Object > Envelope Distort | {rows?: 1..50, cols?: 1..50 (unset: a mesh envelope's own, else 4), maintainShape?: bool (true: the mesh follows the current envelope shape; false: a flat grid over the content), columns?: … | disabled in catalogue snapshot |
| `object.envelope.resetWithWarp` | Reset with Warp… | Object > Envelope Distort | {style?, bend?, h?, v?, horizontal? \| orientation? (as makeWithWarp; unset: the envelope's current warp, else arc 50 %), horizontalDistortion?: as h, verticalDistortion?: as v} make the sel… | disabled in catalogue snapshot |
| `object.envelope.setMeshPoint` | Move Envelope Mesh Point |  | {id, index, x, y, handle?: 0 right\|1 left\|2 down\|3 up} move a point of a mesh envelope (its handles follow), or with `handle` place that handle end at (x, y); object.mesh.movePoint, addLine… | disabled in catalogue snapshot |
| `object.exitIsolation` | Exit Isolation Mode |  | {} | disabled in catalogue snapshot |
| `object.expand` | Expand… | Object | {object?: true (symbol instances without effects (their fills' and strokes' included) and not in perspective → their art, as Break Link to Symbol places it (the instances that art holds sta… | disabled in catalogue snapshot |
| `object.expand.info` | Expand Options |  | {} what each Expand option would change in the selection → {object, fill, stroke, gradient, appearance, symbolArt?: {fill, stroke, gradient}} (true: something to expand; gradient: a gradien… | disabled in catalogue snapshot |
| `object.expandBrush` | Expand Brush Strokes |  | {ids?\|id?} replace brushed paths (in the selection) with groups of the brush art → {ids} | disabled in catalogue snapshot |
| `object.expandShape` | Expand Shape | Object > Shape | {} convert live shapes to plain paths | disabled in catalogue snapshot |
| `object.flattenTransparency` | Flatten Transparency… | Object | {preset?: "high"\|"medium"\|"low" or a saved preset's name (see flattener.presets.list; default medium), balance?: 0..100 (raster/vector balance; 0 rasterizes everything), lineArtPpi?: 1..240… | disabled in catalogue snapshot |
| `object.group` | Group | Object | {ids?: [id…] (selected first; default: the selection)} → {id} | disabled in catalogue snapshot |
| `object.hide` | Selection | Object > Hide | {ids?: [id…] (selected first; default: the selection; in isolation mode, only those inside the isolated object)} | disabled in catalogue snapshot |
| `object.hide.above` | All Artwork Above | Object > Hide | {} hide objects in the same layer that are above and overlap the selection, deselecting every selected object left hidden or locked (the key object too); in isolation mode, hide the selecte… | disabled in catalogue snapshot |
| `object.hide.otherLayers` | Other Layers | Object > Hide | {} hide every layer that holds no selected object; in isolation mode, change nothing and return a count of 0 → {count} | disabled in catalogue snapshot |
| `object.hide.unselected` | Unselected Artwork | Object > Hide | {} hide, in one undo step, every object select.all takes that is not selected and holds no selected object; in a group that holds one it hides the other members one by one, and a clip group… | disabled in catalogue snapshot |
| `object.intertwine.arrange` | Arrange Intertwine Area |  | {id?: Intertwine group (default: the selected one), at?: [x,y] (the overlap area under this point, as a click picks it) \| area?: [[x,y]…] (a closed polygon drawn around overlap areas: every… | disabled in catalogue snapshot |
| `object.intertwine.edit` | Edit | Object > Intertwine | {} choose the Intertwine tool for the selected Intertwine group (Esc or Enter goes back to the tool before) | disabled in catalogue snapshot |
| `object.intertwine.make` | Make | Object > Intertwine | {ids?: two or more objects (default: the selection)} put the objects in an Intertwine group and choose the Intertwine tool, which arranges its overlap areas (object.intertwine.arrange) → {i… | disabled in catalogue snapshot |
| `object.intertwine.release` | Release | Object > Intertwine | {} give the objects of the selected Intertwine groups back as they were made, dropping the arranged areas → {ids} | disabled in catalogue snapshot |
| `object.isolate` | Enter Isolation Mode |  | {id?} isolate a group, a layer or a single object (default: the first selected object); type, a hidden or locked object, an object in a hidden or locked group or layer, and a guide path whi… | disabled in catalogue snapshot |
| `object.liquify` | Liquify |  | {tool: warp\|twirl\|pucker\|bloat\|scallop\|crystallize\|wrinkle, points: [[x,y,pressure?]…] (the brush stroke; pen pressure 0..1, default 1), diameter?\|width?, height? (pt, default 100), angle?,… | disabled in catalogue snapshot |
| `object.lock` | Selection | Object > Lock | {ids?: [id…] (selected first; default: the selection; in isolation mode, only those inside the isolated object)} | disabled in catalogue snapshot |
| `object.lock.above` | All Artwork Above | Object > Lock | {} lock objects in the same layer that are above and overlap the selection, deselecting every selected object left locked or hidden (the key object too); in isolation mode, lock the selecte… | disabled in catalogue snapshot |
| `object.lock.otherLayers` | Other Layers | Object > Lock | {} lock every layer that holds no selected object; in isolation mode, change nothing and return a count of 0 → {count} | disabled in catalogue snapshot |
| `object.lock.unselected` | Unselected Artwork | Object > Lock | {} lock unselected artwork in one undo step, including unselected members of partly selected groups, clipping groups and compound paths, and guides while Lock Guides is on; hidden art and a… | disabled in catalogue snapshot |
| `object.makePixelPerfect` | Make Pixel Perfect | Object | {ids?\|id?} snap each object's edges to the pixel grid (odd stroke weights on half pixels) and round stroke weights | disabled in catalogue snapshot |
| `object.maskImage` | Mask |  | {} clip the selected image with a rectangle around it (its own outline, rotated with it) and select that clipping path, whose handles then crop it; one undo step → {id: the clip group, path… | disabled in catalogue snapshot |
| `object.mesh.addLine` | Add Mesh Line |  | {id, x, y, color? (#rrggbbaa and #rgba are refused), keepModel?: bool (as paint.setFill), tolerance?: pt (0)} add a row and a column through (x, y) to a gradient mesh (new point in `color`)… | disabled in catalogue snapshot |
| `object.mesh.create` | Create Gradient Mesh… | Object | {ids?, rows?: n (4), cols?: n (4), appearance?: flat\|center\|edge, highlight?: % (100), at?: [x,y], tolerance?: pt (0), columns?: as cols} convert filled paths into gradient meshes in their … | disabled in catalogue snapshot |
| `object.mesh.deletePoint` | Delete Mesh Point |  | {id, index} delete the mesh lines through a point of a gradient mesh or mesh envelope | disabled in catalogue snapshot |
| `object.mesh.expand` | Expand Gradient Mesh | Object | {} replace the selected meshes by groups of flat-coloured pieces → {ids} | disabled in catalogue snapshot |
| `object.mesh.movePoint` | Move Mesh Point |  | {id, index, x, y, handle?: 0 right\|1 left\|2 down\|3 up} move a point of a gradient mesh or mesh envelope (its handles follow), or with `handle` place that handle end at (x, y) | disabled in catalogue snapshot |
| `object.mesh.movePoints` | Move Mesh Points |  | {id, points: [index…] \| items: [{id, index \| points}…], dx, dy} move points of gradient meshes or mesh envelopes by (dx, dy), their handles with them (one undo step; an index out of range c… | disabled in catalogue snapshot |
| `object.mesh.setPointColor` | Set Mesh Point Color |  | {id, index \| points: [index…] \| items: [{id, index \| points}…], color? (#rrggbbaa and #rgba are refused), keepModel?: bool (as paint.setFill), opacity?: 0..1} colour and/or opacity of gradi… | disabled in catalogue snapshot |
| `object.move` | Move… | Object > Transform | {ids?: [id…] (selected first; default: the selection), dx, dy, copy?, objects?: bool (Transform Objects, default true; false: the art stays and, with patterns, only its pattern tiles transf… | disabled in catalogue snapshot |
| `object.nudge` | Nudge |  | {dx: -1\|0\|1, dy: -1\|0\|1, big?: bool (×10), copy?: bool, patterns?: bool (Transform Patterns: pattern fills and strokes transform with the objects that move whole; default: prefs transformPa… | disabled in catalogue snapshot |
| `object.objectsOnPath.attach` | Attach | Object > Objects on Path | {path?: id of the path to attach to (without it: choose the Objects on Path tool, whose click on a path attaches the selection to it), ids?: the objects to attach (default: the selection; t… | disabled in catalogue snapshot |
| `object.objectsOnPath.expand` | Expand | Object > Objects on Path | {ids?: Objects on Path groups or objects in them (default: the selection)} make the groups plain groups of the path and the objects where they are → {ids} | disabled in catalogue snapshot |
| `object.objectsOnPath.options` | Objects on Path Options |  | {ids?: Objects on Path groups or objects in them (default: the selection), pivot?: 0-8 (the reference point of each object that attaches to the path, row by row from the top left; 4: the ce… | disabled in catalogue snapshot |
| `object.path.addAnchorPoints` | Add Anchor Points | Object > Path | {} → {ids} | disabled in catalogue snapshot |
| `object.path.cleanUp` | Clean Up… | Object > Path | {strayPoints?: true, unpaintedObjects?: true, emptyTextPaths?: true} → {removed} | Removes stray points, empty text and unpainted objects. Run after tracing; it can remove intentional tiny details, so compare counts.; disabled in catalogue snapshot |
| `object.path.divideObjectsBelow` | Divide Objects Below | Object > Path | {} cut the objects below with the selected path (which is removed) → {ids} | disabled in catalogue snapshot |
| `object.path.offsetPath` | Offset Path… | Object > Path | {offset: pt (negative insets), joins?: "miter"\|"round"\|"bevel", miterLimit?: 4} → {ids} (new objects above the originals) | Creates an offset contour; joins/miter limit affect sharp corners. Offset is not a stroke-width change.; disabled in catalogue snapshot |
| `object.path.outlineStroke` | Outline Stroke | Object > Path | {} replace stroked paths with filled outlines → {ids} | Converts strokes to filled outlines. Required before some pathfinder/boolean operations and for robust SVG consumers.; disabled in catalogue snapshot |
| `object.path.simplify` | Simplify… | Object > Path | {tolerance?: pt (1), level?: 0..100 (the Simplify slider, in place of tolerance: 0 fewest anchor points, 50 is 1 pt, every 10 levels halves or doubles it), auto?: bool (Auto-Simplify: the l… | `level` 0-100; higher removes more anchors. The result counts anchors before/after; do not simplify a wordmark until text is retyped/outlined.; disabled in catalogue snapshot |
| `object.path.smooth` | Smooth… | Object > Path | {level?: 0..100 (50; the Smooth slider: 0 minimum smoothing, the path staying within 0.1% of its longer side, 100 maximum: smoothed along its length by up to 5% of it and refitted with curv… | disabled in catalogue snapshot |
| `object.path.splitIntoGrid` | Split Into Grid… | Object > Path | {rows?: 2, columns?: 2, gutter?: pt (12; rowGutter?, columnGutter?: one of the two), totalHeight?, totalWidth?: pt (the grid's size; the selected paths' when left out), height?, width?: pt … | disabled in catalogue snapshot |
| `object.pathfinder.crop` | Crop | Window > Pathfinder | {ids?: [id…] (selected first; default: the selection), precision?: pt 0.001..10, removeRedundantPoints?: bool, removeUnpainted?: bool (default: the Pathfinder Options, see object.pathfinder… | disabled in catalogue snapshot |
| `object.pathfinder.divide` | Divide | Window > Pathfinder | {ids?: [id…] (selected first; default: the selection), precision?: pt 0.001..10, removeRedundantPoints?: bool, removeUnpainted?: bool (default: the Pathfinder Options, see object.pathfinder… | Splits overlaps into separate faces; useful for recolouring regions, but produces many objects. Check object count.; disabled in catalogue snapshot |
| `object.pathfinder.exclude` | Exclude | Window > Pathfinder | {ids?: [id…] (selected first; default: the selection), precision?: pt 0.001..10, removeRedundantPoints?: bool, removeUnpainted?: bool (default: the Pathfinder Options, see object.pathfinder… | disabled in catalogue snapshot |
| `object.pathfinder.intersect` | Intersect | Window > Pathfinder | {ids?: [id…] (selected first; default: the selection), precision?: pt 0.001..10, removeRedundantPoints?: bool, removeUnpainted?: bool (default: the Pathfinder Options, see object.pathfinder… | disabled in catalogue snapshot |
| `object.pathfinder.merge` | Merge | Window > Pathfinder | {ids?: [id…] (selected first; default: the selection), precision?: pt 0.001..10, removeRedundantPoints?: bool, removeUnpainted?: bool (default: the Pathfinder Options, see object.pathfinder… | disabled in catalogue snapshot |
| `object.pathfinder.minusBack` | Minus Back | Window > Pathfinder | {ids?: [id…] (selected first; default: the selection), precision?: pt 0.001..10, removeRedundantPoints?: bool, removeUnpainted?: bool (default: the Pathfinder Options, see object.pathfinder… | disabled in catalogue snapshot |
| `object.pathfinder.minusFront` | Minus Front | Window > Pathfinder | {ids?: [id…] (selected first; default: the selection), precision?: pt 0.001..10, removeRedundantPoints?: bool, removeUnpainted?: bool (default: the Pathfinder Options, see object.pathfinder… | disabled in catalogue snapshot |
| `object.pathfinder.options` | Pathfinder Options… | Window > Pathfinder | {precision?: pt 0.001..10 (0.01; how closely the Pathfinder operations follow the paths: results are refit to within it and pieces thinner than it are dropped), removeRedundantPoints?: bool… |  |
| `object.pathfinder.outline` | Outline | Window > Pathfinder | {ids?: [id…] (selected first; default: the selection), precision?: pt 0.001..10, removeRedundantPoints?: bool, removeUnpainted?: bool (default: the Pathfinder Options, see object.pathfinder… | disabled in catalogue snapshot |
| `object.pathfinder.trap` | Trap… | Window > Pathfinder | {ids?: [id…] (selected first; default: the selection), thickness?: pt 0.01..5000 (0.25; how far the lighter colour reaches into the darker one across vertical edges), heightWidth?: % 1..100… | disabled in catalogue snapshot |
| `object.pathfinder.trim` | Trim | Window > Pathfinder | {ids?: [id…] (selected first; default: the selection), precision?: pt 0.001..10, removeRedundantPoints?: bool, removeUnpainted?: bool (default: the Pathfinder Options, see object.pathfinder… | disabled in catalogue snapshot |
| `object.pathfinder.unite` | Unite | Window > Pathfinder | {ids?: [id…] (selected first; default: the selection), precision?: pt 0.001..10, removeRedundantPoints?: bool, removeUnpainted?: bool (default: the Pathfinder Options, see object.pathfinder… | Flattens selected shapes into one; destroys individual objects and can flatten palette. Use on a copy when colour separation matters.; disabled in catalogue snapshot |
| `object.pattern.cancel` | Cancel |  | {} leave pattern editing mode, discarding changes | disabled in catalogue snapshot |
| `object.pattern.done` | Done |  | {} leave pattern editing mode, saving the tile art into the pattern | disabled in catalogue snapshot |
| `object.pattern.edit` | Edit Pattern | Object > Pattern | {name?} edit a pattern (default: the selected object's fill pattern) in pattern editing mode; refused while an opacity mask is edited | disabled in catalogue snapshot |
| `object.pattern.make` | Make | Object > Pattern | {ids?, name? (trimmed; blank: New Pattern N), tileType?: grid\|brickByRow\|brickByColumn\|hexByColumn\|hexByRow, brickOffset?: 0..1 (0.5), width?, height?, edit?: bool (true)} make a pattern sw… | disabled in catalogue snapshot |
| `object.pattern.saveCopy` | Save a Copy |  | {name? (trimmed; blank: <pattern> copy)} while editing, save the current tile as a new pattern swatch → {name} | disabled in catalogue snapshot |
| `object.puppetWarp` | Puppet Warp |  | {id?\|ids? (default: selection), pins: [[x,y]…] (current pin positions), moved: [[x,y]…] (targets, same length), angles?: [deg\|null…] (same length: the turn the art takes around each pin, as… | disabled in catalogue snapshot |
| `object.puppetWarp.pins` | Puppet Warp Pins |  | {id?\|ids? (default: selection), expand?: pt} → {ids, pins, moved, angles, expand, rest: true, auto} the Puppet Warp pins on the art: pins = where each sits on the shape they started from, m… | disabled in catalogue snapshot |
| `object.rasterize` | Rasterize… | Object | {ppi?, background?: transparent\|white\|black\|"#rrggbb" (#rrggbbaa and #rgba are refused), antiAlias?: none\|art\|type (text snapped to pixels)\|bool, padding?\|addAround?: pt (0–1000), colorMode… | disabled in catalogue snapshot |
| `object.reflect` | Reflect… | Object > Transform | {ids?: [id…] (selected first; default: the selection), axis: "vertical"\|"horizontal"\|deg, origin?, copy?, objects?: bool (Transform Objects, default true; false: the art stays and, with pat… | disabled in catalogue snapshot |
| `object.repeat.expand` | Expand Repeat |  | {} replace the selected repeats by groups of their instances → {ids} | disabled in catalogue snapshot |
| `object.repeat.grid` | Grid | Object > Repeat | {ids?, hSpacing?: pt, vSpacing?: pt (¼ of the art size), rows?: n (3), cols?: n (3)} grid repeat of the selection → {id} | disabled in catalogue snapshot |
| `object.repeat.mirror` | Mirror | Object > Repeat | {ids?, angle?: deg (90 = vertical axis), offset?: pt (10)} mirror repeat of the selection → {id} | disabled in catalogue snapshot |
| `object.repeat.options` | Options… | Object > Repeat | {instances?, radius?, reverseOverlap?, startAngle?, endAngle?, center?: [x,y] \| hSpacing?, vSpacing?, rows?, cols?, gridType?, flipRows?, flipCols? \| angle?} set the options of the selected… | disabled in catalogue snapshot |
| `object.repeat.radial` | Radial | Object > Repeat | {ids?, instances?: n (8), radius?: pt} radial repeat of the selection (or switch the selected repeat to radial) → {id} | disabled in catalogue snapshot |
| `object.repeat.release` | Release | Object > Repeat | {} release the selected repeats back to their source art → {ids} | disabled in catalogue snapshot |
| `object.resetBoundingBox` | Reset Bounding Box | Object > Transform | {} square the bounding box of the selected objects to the page again after a rotation (their geometry stays; one undo step, none when no box is rotated) → {changed: objects reset} | disabled in catalogue snapshot |
| `object.rotate` | Rotate… | Object > Transform | {ids?: [id…] (selected first; default: the selection), angle: deg (counter-clockwise), absolute?: bool (angle is the bounding box's new angle, not an amount), origin?: [x,y] (default: the b… | disabled in catalogue snapshot |
| `object.scale` | Scale… | Object > Transform | {ids?: [id…] (selected first; default: the selection), sx: %, sy?: %, origin?: [x,y], copy?, strokes?: bool (Scale Strokes & Effects: stroke weights, dashes and effect distances scale; off … | disabled in catalogue snapshot |
| `object.setBounds` | Set Bounds |  | {x?, y?, width?, height?, reference?: 0..8 (9-point grid; a number past 8 is read as 8), proportional?, strokes?, corners?, copy?: bool, patterns?: bool (Transform Patterns), typeAreas?: bo… | disabled in catalogue snapshot |
| `object.setLiveShape` | Live Shape Properties |  | {id?, ids?, radius?: pt (or % of each corner's maximum when `relativeRadii` is true), kind?: "round"\|"invertedRound"\|"chamfer", relativeRadii?: bool (Relative rounding, as in the reference … | disabled in catalogue snapshot |
| `object.setOverprint` | Overprint |  | {fill?: bool, stroke?: bool, item?: appearance item index\|null, ids?\|id?, target?: "object"\|"contents"} make fills and/or strokes overprint (Overprint Preview, Separations Preview) or knock… | disabled in catalogue snapshot |
| `object.setProps` | Object Properties |  | {ids?\|id?, name?, visible?, locked? (visible: false or locked: true deselects every selected object hidden or locked after the call, the key object included), opacity?: 0..100, blend?: "Mul… | disabled in catalogue snapshot |
| `object.shape.convertToShape` | Convert to Shape | Object > Shape | {} turn paths that are rectangles (any rotation) or axis-aligned ellipses into live shapes → {converted} | disabled in catalogue snapshot |
| `object.shear` | Shear… | Object > Transform | {ids?: [id…] (selected first; default: the selection), angle: deg, axis?: "horizontal"\|"vertical", origin?, copy?, objects?: bool (Transform Objects, default true; false: the art stays and,… | disabled in catalogue snapshot |
| `object.showAll` | Show All | Object | {scope?: "document"\|"group" (default document, which in isolation mode is the isolated object; group: only the objects inside the groups that hold the selected objects, a selected group hol… | disabled in catalogue snapshot |
| `object.slice.clipToArtboard` | Clip to Artboard | Object > Slice | {on?: bool} toggle (or set) Clip to Artboard: on, slices are clipped to the artboards and auto slices fill them; off, auto slices cover the art and the slices → {on} | disabled in catalogue snapshot |
| `object.slice.combine` | Combine Slices | Object > Slice | {} replace the two or more selected slices with one user slice over their bounds (the first one's options; object slices are released) → {id} | disabled in catalogue snapshot |
| `object.slice.create` | Create Slice |  | {x, y, width, height} a user slice over that rectangle, selected (the Slice tool's drag) → {id} | disabled in catalogue snapshot |
| `object.slice.delete` | Delete Slices |  | {slices?: [id…] (default: the selected slices)} delete the user slices and release the object slices (their objects stay) → {count} | disabled in catalogue snapshot |
| `object.slice.deleteAll` | Delete All | Object > Slice | {} delete every user slice and release every object slice → {count} | disabled in catalogue snapshot |
| `object.slice.divide` | Divide Slices… | Object > Slice | {rows?: slices down, rowHeight?: pt per slice, columns?: slices across, columnWidth?: pt per slice} cut each selected slice into a grid of user slices (evenly by count, or by size with a sm… | disabled in catalogue snapshot |
| `object.slice.duplicate` | Duplicate Slice | Object > Slice | {dx?: pt (default 10), dy?: pt (default 10)} copy the selected slices as user slices with their options, offset by dx, dy; the copies are selected → {ids} | disabled in catalogue snapshot |
| `object.slice.fromGuides` | Create from Guides | Object > Slice | {} replace the user slices with the grid the ruler guides cut the artboards into (two vertical and two horizontal guides give 9) → {ids} | disabled in catalogue snapshot |
| `object.slice.fromSelection` | Create from Selection | Object > Slice | {ids?\|id?} a user slice over the visual bounds of the selected objects (or ids), selected → {id} | disabled in catalogue snapshot |
| `object.slice.make` | Make | Object > Slice | {ids?} make each selected object (or ids) an object slice: its slice follows the object's bounds → {ids: the new object slices} | disabled in catalogue snapshot |
| `object.slice.move` | Move Slices |  | {slices?: [id…] (default: the selected slices), dx, dy} move the slices: user slices move, object slices move their objects → {ids} | disabled in catalogue snapshot |
| `object.slice.options` | Slice Options… | Object > Slice | {kind?: "image"\|"noImage"\|"htmlText" (object slices of type only), name?, url?, target?, message?, alt?: (image), text?: cell text; HTML allowed (noImage), background?: ""\|"matte"\|"#rrggbb"… | disabled in catalogue snapshot |
| `object.slice.release` | Release | Object > Slice | {} release the selected slices: an object slice leaves its object as it was, a user slice becomes an unpainted rectangle; the objects end up selected → {ids} | disabled in catalogue snapshot |
| `object.slice.select` | Select Slices |  | {slices?: [id…] (user slice ids or ids of objects with an object slice; none: deselect the slices), toggle?: bool (Shift: add the unselected ones, drop the selected ones)} select slices as … | disabled in catalogue snapshot |
| `object.slice.setRect` | Set Slice Rectangle |  | {id: user slice, x, y, width, height} move or resize a user slice (an object slice follows its object) → {id} | disabled in catalogue snapshot |
| `object.textWrap.make` | Make | Object > Text Wrap | {offset?: pt (6), invert?: bool, ids?} area type below the selected objects (same layer) wraps around them → {ids} | disabled in catalogue snapshot |
| `object.textWrap.options` | Text Wrap Options… | Object > Text Wrap | {offset?: pt, invert?: bool, ids?} set the options of the selected wrap objects; no options → the current {offset, invert} | disabled in catalogue snapshot |
| `object.textWrap.release` | Release | Object > Text Wrap | {ids?} → {ids} | disabled in catalogue snapshot |
| `object.transform` | Transform |  | {matrix: [a,b,c,d,e,f], copy?: bool, ids?, strokes?: bool, corners?: bool, typeAreas?: bool, anchors?: bool, objects?: bool (Transform Objects, default true; false: the art stays and, with … | disabled in catalogue snapshot |
| `object.transformAgain` | Transform Again | Object > Transform | {copy?, strokes?, corners?, patterns?, typeAreas?: bool (as object.transform's; default: the value the transform it repeats used, else object.transform's default)} the last transform's matr… | disabled in catalogue snapshot |
| `object.transformEach` | Transform Each… | Object > Transform | {scaleH?: % (100), scaleV?: % (100), relative?: bool (true: scaleH and scaleV are percentages of each object's size, as the dialog's Relative; false: Absolute, scaleH and scaleV are the wid… | disabled in catalogue snapshot |
| `object.ungroup` | Ungroup | Object | {ids?: [id…] (selected first; default: the selection)} | disabled in catalogue snapshot |
| `object.unlockAll` | Unlock All | Object | {scope?: "document"\|"group" (default document, which in isolation mode is the isolated object; group: only the objects inside the groups that hold the selected objects, a selected group hol… | disabled in catalogue snapshot |
| `object.vectorHalftone` | Vector Halftone… | Object | {shape?: "circle"\|"ellipse"\|"square"\|"diamond"\|"line" (circle), frequency?: lines per inch 1–300 (20), angle?: deg (45; CMYK: the black screen's, cyan −30°, magenta +30°, yellow −45° from i… | disabled in catalogue snapshot |

## `path` (34)

Path/anchor commands act on anchors and segments, not whole objects. `object.path.simplify` smooths, `object.path.cleanUp` removes stray points, `object.path.outlineStroke` converts a stroke to fills, `object.path.offsetPath` builds an offset contour. Selected anchors matter; inspect the result counts.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `path.appendAnchor` | Add Anchor (Pen) |  | {id, x, y, in?: [x,y], out?: [x,y], subpath?: usize (the open subpath to extend, 0 included; an invalid or closed one is an error; default: the last open subpath)} append to the end of an o… | disabled in catalogue snapshot |
| `path.average` | Average… | Object > Path | {axis?: "horizontal"\|"vertical"\|"both"} | disabled in catalogue snapshot |
| `path.averageJoin` | Average & Join… | Object > Path | {to: "corner"\|"smooth" (the joined anchor: corner retracts both handles, smooth pulls handles in line with the neighbours), ids?: [path, ...] (default: the selection; a compound path ID exp… | disabled in catalogue snapshot |
| `path.blob` | Blob Brush |  | {points: [[x,y]…] or [[x,y,pressure]…] (pen pressure 0..1), size?: pt (10), sizeMode?: "fixed" (default) \| "pressure" (Blob Brush Tool Options' Size set to Pressure: the brush is size − siz… | disabled in catalogue snapshot |
| `path.close` | Close Path |  | {id, subpath?: usize (the open subpath to close, 0 included; default: the last open one), in?: [x,y] (handle into the first anchor), independent?: bool} | disabled in catalogue snapshot |
| `path.convertAnchor` | Convert Anchor Point |  | {id, subpath?, anchor, to: "corner"\|"smooth", x?, y?} (smooth with x/y: out handle there, in handle mirrored; without: as the Curvature tool curves a point, along the circle through it and … | disabled in catalogue snapshot |
| `path.convertAnchors` | Convert Anchor Points |  | {to: "corner"\|"smooth"} convert the direct-selected anchors (all anchors of fully selected paths, every point of a selected blend's spine; a spine from Replace Spine changes only its handle… | disabled in catalogue snapshot |
| `path.create` | Create Path |  | {anchors: [{x, y, in?: [x,y], out?: [x,y]}], closed?: bool, d?: SVG path data} → {id} | disabled in catalogue snapshot |
| `path.curvature` | Curvature |  | {points: [{x, y, corner?}], closed?, id?} create (or with id: replace) a path curving through the points → {id} | disabled in catalogue snapshot |
| `path.curvatureEdit` | Curvature |  | {id, subpath?, op: "move"\|"insert"\|"extend"\|"close", anchor?, segment?, t?, end?: "start"\|"end", from?: "keep"\|"smooth"\|"corner", corner?, x?, y?} edit a path as the Curvature tool does, it… | disabled in catalogue snapshot |
| `path.cutAtAnchors` | Cut Path at Selected Anchor Points |  | {} cut the paths at their direct-selected anchors (one undo step): a closed path opens there, an open one becomes one path per piece; one of each cut's two coincident anchors stays selected… | disabled in catalogue snapshot |
| `path.deleteAnchors` | Delete Anchor Points |  | {} delete the direct-selected anchors and their segments, opening closed paths there, and delete objects selected whole alongside them; what remains of a path stays selected, so a second De… | disabled in catalogue snapshot |
| `path.eraseRegion` | Eraser |  | {points: [[x,y]…] or [[x,y,pressure]…] (pen pressure 0..1), size?: pt (10), sizeMode?: "fixed" (default) \| "pressure" (Eraser Tool Options' Size set to Pressure: the tip is size − sizeVaria… | disabled in catalogue snapshot |
| `path.eraseSegments` | Path Eraser |  | {points: [[x,y]…], width?: pt (8)} erase the parts of selected paths under the drag → {ids} | disabled in catalogue snapshot |
| `path.freehand` | Pencil |  | {points: [[x,y]…] or [[x,y,pressure]…] or [[x,y,pressure,tiltX,tiltY,rotation]…] (pen pressure 0..1: the stroke keeps it, for Calligraphic and Scatter brushes with Pressure variation; a poi… | disabled in catalogue snapshot |
| `path.insertAnchor` | Add Anchor Point |  | {id, subpath?, segment, t: 0..1} | disabled in catalogue snapshot |
| `path.join` | Join | Object > Path | {ids?: [path, ...] (default: the selected paths; a compound path ID expands to its open member paths), subpaths?: [usize, usize] (which subpaths to join), ends?: ["first"\|"last", "first"\|"l… | disabled in catalogue snapshot |
| `path.joinScrub` | Join |  | {points: [[x,y]…], tolerance?: pt (12)} join the open-path endpoints scrubbed over → {id} | disabled in catalogue snapshot |
| `path.knife` | Knife |  | {points: [[x,y]…]} cut closed shapes (selected, or all when nothing is selected) along the polyline → {ids} | disabled in catalogue snapshot |
| `path.lineCut` | Line Cut |  | {from: [x,y], to: [x,y]} split the selected paths and compound paths along the line through both points, extended across the art: filled shapes become their pieces on each side (holes kept)… | disabled in catalogue snapshot |
| `path.mirrorCut` | Mirror & Cut |  | {axis?: "vertical"\|"horizontal"\|"free" (vertical), from?: [x,y], to?: [x,y] (free: the axis through both; vertical/horizontal: the axis through `from`, default the selection's centre), keep… | disabled in catalogue snapshot |
| `path.moveAnchor` | Move Anchor Point |  | {id, subpath?, anchor, x, y} move one anchor to (x, y), its handles with it | disabled in catalogue snapshot |
| `path.moveAnchors` | Move Anchors |  | {dx, dy, patterns?: bool (Transform Patterns: pattern fills and strokes transform with the objects that move whole; default: prefs transformPatternTiles)} move direct-selected anchors (whol… | disabled in catalogue snapshot |
| `path.rectCut` | Rectangle Cut |  | {rect: [x, y, width, height]} or {from: [x,y], to: [x,y]} (opposite corners) crop the selected paths and compound paths to the rectangle as real geometry (not a clipping mask): filled shape… | disabled in catalogue snapshot |
| `path.removeAnchor` | Delete Anchor Point |  | {id, subpath?, anchor, curvature?} remove one anchor, re-fitting the curve (with curvature: true, the curve where it was follows the remaining anchors, as the Curvature tool curves its poin… | disabled in catalogue snapshot |
| `path.removeAnchors` | Remove Anchor Points | Object > Path | {} remove the direct-selected anchors without opening their paths, refitting the curve round each; the anchor after each removed one is selected, so running it again goes on along the path … | disabled in catalogue snapshot |
| `path.reshape` | Reshape |  | {id, x, y, dx, dy, tol=3, radius?} Reshape tool: grab the path at (x, y) (adding an anchor there unless one is within tol) and drag it by (dx, dy); nearby anchors follow with a smooth fallo… | disabled in catalogue snapshot |
| `path.reshapeSegment` | Reshape Segment |  | {id, subpath?, segment, t, dx, dy, perpendicular?: bool} bend a segment so the point at t moves by (dx, dy); with perpendicular (Shift), both handles stand at right angles to the line betwe… | disabled in catalogue snapshot |
| `path.reverse` | Reverse Path Direction | Object > Path | {ids?\|id?, subpath?: usize (reverse only this subpath of each path, 0 included; default: every subpath), reversed?: bool (true: every subpath runs counter-clockwise on screen, false: clockw… | disabled in catalogue snapshot |
| `path.setAnchors` | Set Anchors |  | {id, subpaths: [{anchors: [{x,y,in?,out?}], closed}]} replace a path's geometry | disabled in catalogue snapshot |
| `path.setFillRule` | Fill Rule |  | {rule: "nonZero"\|"evenOdd", ids?\|id?} the fill rule of the paths and compound paths in ids or the selection (groups: those inside), as one undo step → {changed} | disabled in catalogue snapshot |
| `path.setHandle` | Move Direction Handle |  | {id, subpath?, anchor, which: "in"\|"out", x, y, independent?: bool} | disabled in catalogue snapshot |
| `path.smoothRegion` | Smooth |  | {points: [[x,y]…], radius?: pt (12), fidelity?: pt (2.5)} smooth selected paths near the drag → {ids, before, after} | disabled in catalogue snapshot |
| `path.split` | Split Path |  | {id, subpath?, segment, t} or {id, subpath?, anchor}: closed paths open there, open paths become two → {ids} | disabled in catalogue snapshot |

## `shape` (10)

Shape commands create parametric shapes. Convert to paths before pathfinder/path editing if you need exact anchors.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `shape.arc` | Arc |  | {x1, y1, x2, y2, closed?, slope?} or {x, y, lengthX, lengthY, reference?, baseAlong?: x\|y, slope?, closed?, fillArc?} → {id} | disabled in catalogue snapshot |
| `shape.ellipse` | Ellipse |  | {x, y, width, height, rotation?: deg (about centre)} → {id} | disabled in catalogue snapshot |
| `shape.flare` | Flare |  | {cx, cy, diameter=100, opacity=50 (%), brightness=30 (%), growth=20 (%), fuzziness=50 (%), rays=15, longest=300 (%), rayFuzziness=100 (%), rotation=0 (deg, turns the rays clockwise), x2?, y… | disabled in catalogue snapshot |
| `shape.line` | Line Segment |  | {x1, y1, x2, y2, fill?: bool (Fill Line: the current fill, else none)} → {id} | disabled in catalogue snapshot |
| `shape.polarGrid` | Polar Grid |  | {x, y, width, height, concentric=5, radial=5, concentricSkew=0, radialSkew=0 (−500…500 %: + crowds the ellipses toward the outside, the radial dividers clockwise of the top one), compound=f… | disabled in catalogue snapshot |
| `shape.polygon` | Polygon |  | {cx, cy, radius, sides=6, rotation?: deg} → {id} | disabled in catalogue snapshot |
| `shape.rectangle` | Rectangle |  | {x, y, width, height, radius?: pt, rotation?: deg (about centre)} → {id} | disabled in catalogue snapshot |
| `shape.rectangularGrid` | Rectangular Grid |  | {x, y, width, height, rows=5, columns=5, rowSkew=0, columnSkew=0 (−500…500 %: + crowds the horizontal dividers toward the top, the vertical ones toward the right), frame=true (the outside a… | disabled in catalogue snapshot |
| `shape.spiral` | Spiral |  | {cx, cy, radius, decay=80 (%), segments=10, clockwise?} → {id} | disabled in catalogue snapshot |
| `shape.star` | Star |  | {cx, cy, radius1, radius2, points=5, rotation?: deg} → {id} | disabled in catalogue snapshot |

## `shapeBuilder` (2)

Shape Builder merges or erases regions of overlapping art. It is destructive to the source objects; work on a copy and verify region counts.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `shapeBuilder.merge` | Shape Builder |  | {ids?\|id?: [id…] (default: selection), points: [[x,y]…] (drag path; one point = click; may be left out with rect), rect?: [x, y, width, height] (Shift-drag marquee from where the drag start… | disabled in catalogue snapshot |
| `shapeBuilder.regions` | Shape Builder Regions |  | {ids?\|id?, gap?: pt (0–72; 0: Gap Detection off), openFilledAsClosed?: true (as shapeBuilder.merge)} → {regions: [{bounds: [x0,y0,x1,y1], area, sources: [id…]}], lines: [{bounds, source: id… | disabled in catalogue snapshot |

## `shaper` (5)

Shaper builds shapes from drawn segments; use it for deliberate geometric construction, not auto-tracing.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `shaper.expand` | Expand Shaper Group | Object > Shaper | {id? (default: selection)} keep the visible result as ordinary paths → {id} | disabled in catalogue snapshot |
| `shaper.release` | Release Shaper Group | Object > Shaper | {id? (default: selection)} restore the original paths → {ids} | disabled in catalogue snapshot |
| `shaper.releaseSource` | Remove from Shaper Group |  | {source: id, group?: id (default: the Shaper Group that holds `source`)} take one original shape out of its Shaper Group: it becomes a path just above the group, keeps its look and is selec… | disabled in catalogue snapshot |
| `shaper.scribble` | Shaper |  | {points: [[x,y]…], ids?: [id…] (default: nearby art), tolerance?: pt (4)} interior scribbles remove fills; scribbles through several regions merge with the origin fill; ending outside remov… | disabled in catalogue snapshot |
| `shaper.select` | Select Shaper Face |  | {point: [x,y], source?: bool} click selects a group, then a face; source enters construction isolation and selects an original (while an opacity mask or a pattern is edited, it selects the … | disabled in catalogue snapshot |
