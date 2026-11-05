# PhotoCraft Text Vector Path

Auto-generated from the installed 965-command registry (snapshot 2026-11-05). Every row is a real command id; params are abbreviated. Query the full schema with `$PC commands --json`. PhotoCraft input is positional and `--out` must differ from input.

Commands: **192** across 8 groups.

## Coverage

`brush` 18 · `gradient` 12 · `paint` 28 · `path` 25 · `pattern` 10 · `shape` 9 · `swatches` 12 · `type` 78

## `brush` (18)

Brushes paint variable-width strokes. For print, expand strokes to outlines or verify the consumer supports the brush definition.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `brush.defineFromSelection` | Define Brush Preset… |  | {"name":string} | needs document; disabled in catalogue snapshot |
| `brush.get` | Get Brush |  | {} |  |
| `brush.mixer.clean` | Clean Mixer Brush |  | {} |  |
| `brush.mixer.load` | Load Mixer Brush |  | {"color":"#rrggbb"\|[r,g,b,a?] 0..1?=foreground} |  |
| `brush.mixer.sample` | Sample Mixer Brush |  | {"points":[[x,y,pressure?,tiltX?,tiltY?,rotation?]],"sampleAllLayers":bool=brush setting,"size":px?,"target":"pixels"\|"mask"\|"quickMask"\|{"channel":i}} | needs document; disabled in catalogue snapshot |
| `brush.presets.delete` | Delete Brush Preset |  | {"name":string} |  |
| `brush.presets.deleteGroup` | Delete Brush Group |  | {"group":string,"folder":[name]? (delete this nested folder instead)} → {deleted, count} |  |
| `brush.presets.importAbr` | Import Brushes… |  | {"path":".abr file"?,"data":base64 bytes?,"group":string?=file name,"replace":bool=false (first delete the non-built-in presets of a group of the same name; false imports beside it as <grou… |  |
| `brush.presets.importImage` | Import Brush from Image… |  | {"path":"image file (PNG, JPEG, TIFF, PSD…)"?,"data":base64 bytes?,"fileName":string? (with data: the file's name, for its format and the default preset name),"name":string?=file name,"sele… |  |
| `brush.presets.list` | List Brush Presets |  | {"full":bool=false} |  |
| `brush.presets.move` | Move Brush |  | {"name":string,"group":string?=its group ("" = ungrouped),"folder":[name]? (nested folder names in the group, outermost first; [] = the group itself)=before's folder, else its own if it sta… |  |
| `brush.presets.moveGroup` | Move Brush Group |  | {"group":string,"folder":[name]? (move this nested folder instead),"into":{"group":string?,"folder":[name]?}? (move it inside that folder of that group, [] = directly in the group; no group… |  |
| `brush.presets.rename` | Rename Brush |  | {"name":string,"newName":string} → {name} |  |
| `brush.presets.renameGroup` | Rename Brush Group |  | {"group":string,"folder":[name]? (rename this nested folder instead),"newName":string} → {group, folder?} |  |
| `brush.presets.save` | Save Brush Preset |  | {"name":string,"brush":{…BrushSettings}?=current brush,"captureSize":bool=true (false: picking it keeps the tool's size),"toolSettings":bool=true (false: picking it keeps the tool's mode, o… |  |
| `brush.presets.setCurrent` | Set Current Brush Preset |  | {"name":string} |  |
| `brush.presets.update` | Update Brush Preset |  | {"name":string?=the preset the current brush was picked from,"brush":{…BrushSettings}?=current brush} |  |
| `brush.texturePattern` | Brush Texture Pattern |  | {"pattern":id\|name,"scale":1..1000?,"enabled":bool=true} (sets the session brush's Texture to that pattern) |  |

## `gradient` (12)

Gradient commands apply presets and edit stops. Gradient geometry is separate (`paint.setGradientGeom`); verify direction and stops in the render.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `gradient.fill.create` | Gradient (Live) |  | {"from":[x,y],"to":[x,y],"style":"linear\|radial\|angle\|reflected\|diamond"="linear","gradient":preset name?,"stops":[[t,"#rrggbb"\|"foreground"\|"background"],…]?,"transparency":[[t,0..100],…]?… | needs document; disabled in catalogue snapshot |
| `gradient.fill.get` | Gradient Fill Settings |  | {"layer":id?} → {"style","angle","scale":%,"offset":[%,%],"reverse","dither","align","from":[x,y],"to":[x,y],"stops":[[t,"#hex"]],"transparency":[[t,%]],"midpoints":[…]} | needs document; disabled in catalogue snapshot |
| `gradient.fill.set` | Edit Gradient Fill |  | {"layer":id?,"from":[x,y]?,"to":[x,y]?,"style":"linear\|radial\|angle\|reflected\|diamond"?,"angle":deg?,"scale":%?,"offset":[x%,y%]?,"reverse":bool?,"dither":bool?,"align":bool?,"stops":[[t,"#… | needs document; disabled in catalogue snapshot |
| `gradient.fill.stop` | Edit Gradient Stop |  | {"layer":id?,"action":"add\|move\|delete\|color\|opacity\|midpoint","kind":"color\|opacity"="color","index":stop (midpoint: segment) number,"location":0..1 (midpoint: of the segment),"color":"#rr… | needs document; disabled in catalogue snapshot |
| `gradient.presets.apply` | New Gradient Fill Layer from Preset |  | {"preset":name?=current\|"stops":[[t 0..1,"#rrggbb"\|"foreground"\|"background"],…],"transparency":[[t,opacity 0..100],…]?,"angle":deg=90,"style":"linear\|radial\|angle\|reflected\|diamond"="linea… | needs document; disabled in catalogue snapshot |
| `gradient.presets.edit` | Edit Gradient Presets |  | {"action":"rename\|delete\|move\|newGroup\|renameGroup\|deleteGroup","preset":name\|[names] (rename/delete/move),"group":name? (narrows the lookup; the group for renameGroup/deleteGroup),"name":s… |  |
| `gradient.presets.importGrd` | Import Gradients… |  | {"path":".grd file"?,"data":base64 bytes?,"group":string?=file name,"replace":bool=false (first delete a group of the same name; false imports beside it as <group> (2))} → {group, imported,… |  |
| `gradient.presets.list` | Gradient Presets |  | {} → {groups:[{name,presets:[{name,stops,transparency}]}],current} |  |
| `gradient.presets.new` | New Gradient Preset |  | {"name":str="Custom","group":name?=first,"stops":[[t 0..1,"#rrggbb"\|"foreground"\|"background"],…],"transparency":[[t,opacity 0..100],…]? (default: the current gradient)} |  |
| `gradient.presets.reset` | Restore Default Gradients |  | {"append":bool=false} |  |
| `gradient.presets.select` | Select Gradient |  | {"preset":name\|"stops":[[t 0..1,"#rrggbb"\|"foreground"\|"background"],…],"transparency":[[t,opacity 0..100],…]?,"group":name?,"applyToLayer":bool=true (also recolours a selected Gradient Fil… |  |
| `gradient.presets.stop` | Edit Gradient Stop |  | {"action":"add\|move\|delete\|color\|opacity","kind":"color\|opacity"="color","index":stop number,"location":0..1,"color":"#rrggbb"\|"foreground"\|"background" (add: default the colour there),"opa… |  |

## `paint` (28)

Paint sets fill/stroke, gradients and sampled colours. `paint.none` removes paint; `paint.setFill`/`setStroke` are the workhorses.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `paint.artHistoryBrush` | Art History Brush |  | {"points":[[x,y,pressure?],…],"size":1..5000 px=tool size,"hardness":0..100=tool hardness,"opacity":1..100=100,"flow":1..100=100,"spacing":1..1000 (% of size)=Brush Settings spacing,"layer"… | needs document; disabled in catalogue snapshot |
| `paint.backgroundEraser` | Background Eraser |  | {"points":[[x,y,pressure?],…],"size":px?,"hardness":0..1?,"brush":{…}?,"preset":name?,"sampling":"continuous\|once\|backgroundSwatch"="continuous","limits":"discontiguous\|contiguous\|findEdges… | needs document; disabled in catalogue snapshot |
| `paint.blur` | Blur |  | {"points":[[x,y,pressure?],…],"size":1..5000 px=tool size,"hardness":0..100=tool hardness,"opacity":1..100=100,"flow":1..100=100,"spacing":1..1000 (% of size)=Brush Settings spacing,"layer"… | needs document; disabled in catalogue snapshot |
| `paint.bucket` | Paint Bucket |  | {"x":px,"y":px,"tolerance":0..255=32,"contiguous":bool=true,"antiAlias":bool=true,"sampleAllLayers":bool=false,"contents":"foreground\|pattern"="foreground","color":"#rrggbb"=foreground,"pat… | needs document; disabled in catalogue snapshot |
| `paint.burn` | Burn |  | {"points":[[x,y,pressure?],…],"size":1..5000 px=tool size,"hardness":0..100=tool hardness,"opacity":1..100=100,"flow":1..100=100,"spacing":1..1000 (% of size)=Brush Settings spacing,"layer"… | needs document; disabled in catalogue snapshot |
| `paint.cloneStamp` | Clone Stamp |  | {"points":[[x,y,pressure?],…],"size":1..5000 px=tool size,"hardness":0..100=tool hardness,"opacity":1..100=100,"flow":1..100=100,"spacing":1..1000 (% of size)=Brush Settings spacing,"layer"… | needs document; disabled in catalogue snapshot |
| `paint.colorReplacement` | Color Replacement |  | {"points":[…],"brush":{…}?,"size":px?,"mode":"hue\|saturation\|color\|luminosity"="color","sampling":"continuous\|once\|backgroundSwatch"="continuous","limits":"contiguous\|discontiguous\|findEdge… | needs document; disabled in catalogue snapshot |
| `paint.contentAwareMove` | Content-Aware Move |  | {"offset":[dx,dy] (how far the selection was dragged),"mode":"move\|extend"="move","structure":1..7=4 (3..7 copy the content exactly but for a band about a patch wide along its edge; 2 widen… | needs document; disabled in catalogue snapshot |
| `paint.dodge` | Dodge |  | {"points":[[x,y,pressure?],…],"size":1..5000 px=tool size,"hardness":0..100=tool hardness,"opacity":1..100=100,"flow":1..100=100,"spacing":1..1000 (% of size)=Brush Settings spacing,"layer"… | needs document; disabled in catalogue snapshot |
| `paint.gradient` | Gradient |  | {"from":[x,y],"to":[x,y],"style":"linear\|radial\|angle\|reflected\|diamond"="linear","colors":["#rrggbb",…]? (evenly spaced),"gradient":preset name?,"stops":[[t,"#rrggbb"\|"foreground"\|"backgro… | needs document; disabled in catalogue snapshot |
| `paint.healingBrush` | Healing Brush |  | {"points":[[x,y,pressure?],…],"size":1..5000 px=tool size,"hardness":0..100=tool hardness,"opacity":1..100=100,"flow":1..100=100,"spacing":1..1000 (% of size)=Brush Settings spacing,"layer"… | needs document; disabled in catalogue snapshot |
| `paint.historyBrush` | History Brush |  | {"points":[[x,y,pressure?],…],"size":1..5000 px=tool size,"hardness":0..100=tool hardness,"opacity":1..100=100,"flow":1..100=100,"spacing":1..1000 (% of size)=Brush Settings spacing,"layer"… | needs document; disabled in catalogue snapshot |
| `paint.magicEraser` | Magic Eraser |  | {"x":px,"y":px,"tolerance":0..255=32,"antiAlias":bool=true,"contiguous":bool=true,"sampleAllLayers":bool=false,"opacity":1..100=100} | needs document; disabled in catalogue snapshot |
| `paint.mixerBrush` | Mixer Brush |  | {"points":[…] (long segments are interpolated),"brush":{…}?,"preset":name?,"size":0.5..5000 px?,"wet":0..100=brush.mixer.wet,"load":0..100=brush.mixer.load,"mix":0..100=brush.mixer.mix,"flo… | needs document; disabled in catalogue snapshot |
| `paint.mixerLoad` | Load Mixer Brush |  | {"x":px,"y":px,"size":"point"\|1\|3\|5\|11\|31\|51\|101=1,"sampleAllLayers":bool=brush.mixer.sampleAllLayers} → {"loaded":bool,"color"?:[r,g,b,a]} (loads the Mixer Brush reservoir from the canvas … | needs document; disabled in catalogue snapshot |
| `paint.patch` | Patch |  | {"offset":[dx,dy] (how far the selection was dragged),"mode":"source\|destination"="source","contentAware":bool=false (fill the selection content-aware from the dragged-to place; a backgroun… | needs document; disabled in catalogue snapshot |
| `paint.patternStamp` | Pattern Stamp |  | {"points":[[x,y,pressure?],…],"size":1..5000 px=tool size,"hardness":0..100=tool hardness,"opacity":1..100=100,"flow":1..100=100,"spacing":1..1000 (% of size)=Brush Settings spacing,"layer"… | needs document; disabled in catalogue snapshot |
| `paint.pencil` | Pencil |  | {"points":[[x,y,pressure?,tiltX?,tiltY?,rotation?,timeMs?,wheel?],…],"brush":{…}?,"preset":name?,"size":0.5..5000 px?,"opacity":0..1?,"color":"#rrggbb"?=foreground,"mode":"normal\|multiply\|s… | needs document; disabled in catalogue snapshot |
| `paint.redEye` | Red Eye |  | {"x":px, "y":px} \| {"points":[[x,y],…] (at most 64)},"pupilSize":1..100=50,"darken":0..100=50,"layer":id?=active,"target":"pixels"\|"mask"\|"filterMask"\|"quickMask"\|{"channel":i} → {"damage":… | needs document; disabled in catalogue snapshot |
| `paint.remove` | Remove |  | {"points":[[x,y,pressure?],…],"size":1..5000 px=tool size,"hardness":0..100=tool hardness,"opacity":1..100=100,"flow":1..100=100,"spacing":1..1000 (% of size)=Brush Settings spacing,"layer"… | needs document; disabled in catalogue snapshot |
| `paint.setSymmetry` | Set Painting Symmetry |  | {"mode":"vertical\|horizontal\|dual\|diagonal","center":[x,y]?,"rotation":degrees=0} | needs document; disabled in catalogue snapshot |
| `paint.sharpen` | Sharpen |  | {"points":[[x,y,pressure?],…],"size":1..5000 px=tool size,"hardness":0..100=tool hardness,"opacity":1..100=100,"flow":1..100=100,"spacing":1..1000 (% of size)=Brush Settings spacing,"layer"… | needs document; disabled in catalogue snapshot |
| `paint.smudge` | Smudge |  | {"points":[[x,y,pressure?],…],"size":1..5000 px=tool size,"hardness":0..100=tool hardness,"opacity":1..100=100,"flow":1..100=100,"spacing":1..1000 (% of size)=Brush Settings spacing,"layer"… | needs document; disabled in catalogue snapshot |
| `paint.sponge` | Sponge |  | {"points":[[x,y,pressure?],…],"size":1..5000 px=tool size,"hardness":0..100=tool hardness,"opacity":1..100=100,"flow":1..100=100,"spacing":1..1000 (% of size)=Brush Settings spacing,"layer"… | needs document; disabled in catalogue snapshot |
| `paint.spotHealing` | Spot Healing Brush |  | {"points":[[x,y,pressure?],…],"size":1..5000 px=tool size,"hardness":0..100=tool hardness,"opacity":1..100=100,"flow":1..100=100,"spacing":1..1000 (% of size)=Brush Settings spacing,"layer"… | needs document; disabled in catalogue snapshot |
| `paint.stroke` | Brush Stroke |  | {"points":[[x,y,pressure?,tiltX?,tiltY?,rotation?,timeMs?,wheel?],…],"brush":{…BrushSettings}?,"preset":name?,"size":0.5..5000 px?,"hardness":0..1?,"opacity":0..1?,"flow":0..1?,"fill":bool=… | needs document; disabled in catalogue snapshot |
| `paint.symmetryDisable` | Disable Painting Symmetry |  | {} | disabled in catalogue snapshot |
| `paint.symmetryFromPath` | Make Symmetry Path |  | {"name":"work"\|"layer"\|savedPathName="work"} — mirror Brush, Pencil and Eraser strokes across the path | needs document; disabled in catalogue snapshot |

## `path` (25)

Path/anchor commands act on anchors and segments, not whole objects. `object.path.simplify` smooths, `object.path.cleanUp` removes stray points, `object.path.outlineStroke` converts a stroke to fills, `object.path.offsetPath` builds an offset contour. Selected anchors matter; inspect the result counts.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `path.addAnchor` | Add Anchor Point |  | {"name":str\|"work"\|"layer"="work","layer":id? (with "layer": a shape layer's path, a vector mask, or else type on a path's Type Path),"typePath":bool=false (with "layer": the Type Path even… | needs document; disabled in catalogue snapshot |
| `path.addToSelection` | Add Path to Selection |  | {"name":str\|"work"\|"layer"="work","feather":px=0,"antiAlias":bool=true} (path.toSelection with mode "add") | needs document; disabled in catalogue snapshot |
| `path.bendSegment` | Drag Segment |  | {"name":str\|"work"\|"layer"="work","layer":id? (with "layer": a shape layer's path, a vector mask, or else type on a path's Type Path),"typePath":bool=false (with "layer": the Type Path even… | needs document; disabled in catalogue snapshot |
| `path.clippingPath.clear` | Clear Clipping Path |  | {} | needs document; disabled in catalogue snapshot |
| `path.clippingPath.set` | Clipping Path |  | {"name":savedPathName,"flatness":0..100=0} (PSD export clipping path) | needs document; disabled in catalogue snapshot |
| `path.convertPoint` | Convert Point |  | {"name":str\|"work"\|"layer"="work","layer":id? (with "layer": a shape layer's path, a vector mask, or else type on a path's Type Path),"typePath":bool=false (with "layer": the Type Path even… | needs document; disabled in catalogue snapshot |
| `path.delete` | Delete Path |  | {"name":str\|"work"="work"} | needs document; disabled in catalogue snapshot |
| `path.deleteAnchor` | Delete Anchor Point |  | {"name":str\|"work"\|"layer"="work","layer":id? (with "layer": a shape layer's path, a vector mask, or else type on a path's Type Path),"typePath":bool=false (with "layer": the Type Path even… | needs document; disabled in catalogue snapshot |
| `path.fill` | Fill Path |  | {"name":str\|"work"\|"layer"="work","layer":id? (pixel layer, default active),"color":"#rrggbb"=foreground,"opacity":0..100=100,"mode":"normal\|multiply\|…"="normal","feather":px=0,"antiAlias":… | needs document; disabled in catalogue snapshot |
| `path.info` | Path Info |  | {"name":str\|"work"\|"layer"="work"} → {name,path} | needs document; disabled in catalogue snapshot |
| `path.list` | List Paths |  | {} → {paths:[{name,knots,subpaths}],workPath,clippingPath,layerPath (active layer's shape path / vector mask),typePath (active type layer's Type Path, if it is on a path)} | needs document; disabled in catalogue snapshot |
| `path.mergeShapeComponents` | Merge Shape Components |  | {"name":str\|"work"\|"layer"="work","layer":id? (with "layer": a shape layer's path, a vector mask, or else type on a path's Type Path),"typePath":bool=false (with "layer": the Type Path even… | needs document; disabled in catalogue snapshot |
| `path.moveAnchors` | Drag Anchor Points |  | {"name":str\|"work"\|"layer"="work","layer":id? (with "layer": a shape layer's path, a vector mask, or else type on a path's Type Path),"typePath":bool=false (with "layer": the Type Path even… | needs document; disabled in catalogue snapshot |
| `path.moveHandle` | Drag Direction Point |  | {"name":str\|"work"\|"layer"="work","layer":id? (with "layer": a shape layer's path, a vector mask, or else type on a path's Type Path),"typePath":bool=false (with "layer": the Type Path even… | needs document; disabled in catalogue snapshot |
| `path.rename` | Rename Path |  | {"name":str\|"work"="work","to":str} (renaming the work path saves it) | needs document; disabled in catalogue snapshot |
| `path.set` | Set Path |  | {"name":str\|"work"="work","path":{…},"op":"combine\|subtract\|intersect\|exclude"? (append to the existing path with this op instead of replacing)}. path: {"subpaths":[{"closed":bool=true,"op"… | needs document; disabled in catalogue snapshot |
| `path.setOperation` | Path Operation |  | {"name":str\|"work"\|"layer"="work","layer":id? (with "layer": a shape layer's path, a vector mask, or else type on a path's Type Path),"typePath":bool=false (with "layer": the Type Path even… | needs document; disabled in catalogue snapshot |
| `path.stroke` | Stroke Path |  | {"name":str\|"work"\|"layer"="work","layer":id? (pixel layer),"tool":"brush\|pencil\|eraser\|backgroundEraser\|cloneStamp\|patternStamp\|healingBrush\|spotHealingBrush\|historyBrush\|blur\|sharpen\|smud… | needs document; disabled in catalogue snapshot |
| `path.style.copyFill` | Copy Fill |  | {} (copies active shape layer fill) | needs document; disabled in catalogue snapshot |
| `path.style.copyStroke` | Copy Complete Stroke |  | {} (copies active shape layer stroke) | needs document; disabled in catalogue snapshot |
| `path.style.pasteFill` | Paste Fill |  | {"layer":id?} (pastes copied fill onto active shape layer) | needs document; disabled in catalogue snapshot |
| `path.style.pasteStroke` | Paste Complete Stroke |  | {"layer":id?} (pastes copied stroke onto active shape layer) | needs document; disabled in catalogue snapshot |
| `path.subtractFromSelection` | Subtract Path from Selection |  | {"name":str\|"work"\|"layer"="work","feather":px=0,"antiAlias":bool=true} (path.toSelection with mode "subtract") | needs document; disabled in catalogue snapshot |
| `path.toSelection` | Make Selection from Path |  | {"name":str\|"work"\|"layer"="work","feather":px=0,"antiAlias":bool=true,"mode":"replace\|add\|subtract\|intersect"="replace"} | needs document; disabled in catalogue snapshot |
| `path.transform` | Free Transform Path |  | {"name":str\|"work"\|"layer"="work","layer":id? (with layer target),"matrix":[a,b,c,d,e,f] \| "quad":[[x,y]×4] (Distort/Perspective: where the frame's corners go, clockwise from top-left) \| "s… | needs document; disabled in catalogue snapshot |

## `pattern` (10)

Pattern swatches tile artwork. Check seam alignment and output scale; patterns are easy to make too dense for print.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `pattern.delete` | Delete Pattern |  | {"pattern":id\|name} (library only; documents keep their copy) |  |
| `pattern.export` | Export Patterns… |  | {"path":".pat file","patterns":[id\|name]? (default: the whole library)} |  |
| `pattern.import` | Import Patterns… |  | {"path":".pat file"?,"data":base64 bytes? (instead of a path)} → {imported:[ids],count} |  |
| `pattern.list` | Patterns |  | {} → [{id,name,width,height,mode,depth,inDocument,inLibrary}] |  |
| `pattern.presets.apply` | New Pattern Fill Layer from Preset |  | {"pattern":id\|name?=selected,"scale":1..1000=100,"angle":deg=0} → {layer} | needs document; disabled in catalogue snapshot |
| `pattern.presets.edit` | Edit Pattern Presets |  | {"action":"rename\|delete\|move\|newGroup\|renameGroup\|deleteGroup","preset":name\|[names] (rename/delete/move),"group":name? (narrows the lookup; the group for renameGroup/deleteGroup),"name":s… |  |
| `pattern.presets.list` | Pattern Presets |  | {} → {groups:[{name,patterns:[{id,name,width,height}]}],current} |  |
| `pattern.presets.new` | New Pattern Preset |  | {"name":str?,"group":name?,"rect":[x0,y0,x1,y1]?} (Define Pattern from the selection/canvas into a group) | needs document; disabled in catalogue snapshot |
| `pattern.presets.select` | Select Pattern |  | {"pattern":id\|name,"applyToLayer":bool=true (also changes a selected Pattern Fill layer)} (Fill and new Pattern Fill layers default to it) |  |
| `pattern.rename` | Rename Pattern |  | {"pattern":id\|name,"name":str} |  |

## `shape` (9)

Shape commands create parametric shapes. Convert to paths before pathfinder/path editing if you need exact anchors.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `shape.create` | New Shape Layer | Layer > New | {"kind":"rect\|roundedRect\|ellipse\|polygon\|star\|line\|path"="rect","rect":[x,y,w,h] (rect/roundedRect/ellipse/polygon/star),"radii":[tl,tr,br,bl]\|r (roundedRect=10),"sides":3..100=5,"starRati… | needs document; disabled in catalogue snapshot |
| `shape.edit` | Edit Shape |  | {"layer":id?,"path":{…}? (replaces; drops live shape),"kind":str?,"rect":[x,y,w,h]?,"radii":[tl,tr,br,bl]\|r?,"sides":n?,"starRatio":r?,"cornerRadius":px?,"from":[x,y]?,"to":[x,y]?,"weight":… | needs document; disabled in catalogue snapshot |
| `shape.info` | Shape Layer Info |  | {"layer":id?} → {layer,name,kind,path,fill,stroke,live,bounds:[x,y,w,h]} | needs document; disabled in catalogue snapshot |
| `shape.presets.edit` | Edit Shape Presets |  | {"action":"rename\|delete\|move\|newGroup\|renameGroup\|deleteGroup","preset":name\|[names] (rename/delete/move),"group":name? (narrows the lookup; the group for renameGroup/deleteGroup),"name":s… |  |
| `shape.presets.list` | Shape Presets |  | {} → {groups:[{name,shapes:[{name,subpaths}]}]} |  |
| `shape.presets.new` | New Shape Preset |  | {"name":str="Shape","group":name?,"path":{…path}\|"M x y L …" (preset path language)\|"work"\|saved path name? (default: work path, active shape layer or vector mask)} |  |
| `shape.presets.place` | Place Custom Shape |  | {"preset":name,"group":name?,"rect":[x,y,w,h]? (default: centred, half the canvas),"keepAspect":bool=true,"fill":…?=foreground,"stroke":…?,"name":str?,"addTo":layerId?,"op":"combine\|subtrac… | needs document; disabled in catalogue snapshot |
| `shape.presets.reset` | Restore Default Shapes |  | {"append":bool=false} |  |
| `shape.rasterize` | Rasterize Shape | Layer > Rasterize | {"layer":id?} | needs document; disabled in catalogue snapshot |

## `swatches` (12)



| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `swatches.add` | New Swatch… |  | {"color":"#rrggbb"\|{"model":"rgb\|hsb\|cmyk\|lab\|gray","values":[rgb 0..255 \| hue°,s%,b% \| c%,m%,y%,k% \| L,a,b \| k%]}?=foreground,"name":str?="Color Swatch N","group":name?=first (created when… |  |
| `swatches.delete` | Delete Swatch |  | {"swatch":name (or "index":n across all groups),"group":name? (narrows the name lookup); "swatch" may be a list of names} → {deleted:[names]} |  |
| `swatches.deleteGroup` | Delete Swatch Group |  | {"group":name,"keepSwatches":bool=false (move its swatches into the group above)} → {group,deleted\|kept} |  |
| `swatches.export` | Export Swatches… |  | {"format":"aco\|act\|ase"?=from path, else aco,"path":file? (else the bytes come back as base64 `data`),"group":name? (only that group),"swatches":[names]? (only these)} → {format,count,bytes… |  |
| `swatches.import` | Import Swatches… |  | {"path":".aco, .act or .ase file"?,"data":base64 bytes?,"format":"aco\|act\|ase"? (detected; an .act by its .act path or its 768/772-byte length),"mode":"append\|replace"="append","group":str?… |  |
| `swatches.list` | Swatches |  | {} → {groups:[{name,swatches:[{name,model,values,hex,kind?}]}],count}. values are in Color Picker units; hex is the colour in the RGB working space. |  |
| `swatches.move` | Move Swatch |  | {"swatch":name (or "index":n across all groups),"group":name? (narrows the name lookup),"to":group?=its own group,"position":n?=end} → {group,position} |  |
| `swatches.newGroup` | New Swatch Group… |  | {"name":str="Group" (made unique),"swatches":[names]? (moved into the new group)} → {group,moved} |  |
| `swatches.rename` | Rename Swatch… |  | {"swatch":name (or "index":n across all groups),"group":name? (narrows the name lookup),"name":str} → {name} |  |
| `swatches.renameGroup` | Rename Swatch Group… |  | {"group":name,"name":str} → {group} |  |
| `swatches.reset` | Reset Swatches |  | {"append":bool=false (add the defaults instead of replacing the library)} → {groups,count} |  |
| `swatches.use` | Use Swatch |  | {"swatch":name (or "index":n across all groups),"group":name? (narrows the name lookup),"target":"foreground\|background"="foreground"} → {swatch,target,hex}. CMYK, Lab and gray swatches are… |  |

## `type` (78)

Type commands convert or transform type: outlines, area/point conversion, case, orientation, size. Outlining is irreversible; keep the live text master.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `type.antiAlias.crisp` | Crisp | Type > Anti-Alias | {"layer":id? or "layers":[id,…]? (default selected Type layers)} | needs document; disabled in catalogue snapshot |
| `type.antiAlias.none` | None | Type > Anti-Alias | {"layer":id? or "layers":[id,…]? (default selected Type layers)} | needs document; disabled in catalogue snapshot |
| `type.antiAlias.sharp` | Sharp | Type > Anti-Alias | {"layer":id? or "layers":[id,…]? (default selected Type layers)} | needs document; disabled in catalogue snapshot |
| `type.antiAlias.smooth` | Smooth | Type > Anti-Alias | {"layer":id? or "layers":[id,…]? (default selected Type layers)} | needs document; disabled in catalogue snapshot |
| `type.antiAlias.strong` | Strong | Type > Anti-Alias | {"layer":id? or "layers":[id,…]? (default selected Type layers)} | needs document; disabled in catalogue snapshot |
| `type.antiAlias.windows` | Windows | Type > Anti-Alias | {"layer":id? or "layers":[id,…]? (default selected Type layers)} | needs document; disabled in catalogue snapshot |
| `type.antiAlias.windowsLcd` | Windows LCD | Type > Anti-Alias | {"layer":id? or "layers":[id,…]? (default selected Type layers)} | needs document; disabled in catalogue snapshot |
| `type.attachToPath` | Type on a Path |  | {"layer":id? (default active Type layer),"shape":layerId? (a shape layer; default the work path),"subpath":index=0,"start":px=0 (offset along the path),"at":[x,y]? (instead of "start": begi… | needs document; disabled in catalogue snapshot |
| `type.caret` | Type Caret |  | {"layer":id?, "index":char (0..=length; empty text is 0)} → {"index","line","segment":[[x,y],[x,y]]} caret segment in document pixels, for rotated and vertical type too | needs document; disabled in catalogue snapshot |
| `type.characterStyle.apply` | Apply Character Style |  | {"id":u32\|0\|null (0/null: None / Basic Paragraph),"clearOverrides":bool=false (Alt-click),"layer":id? \| "layers":[id]? (default: the selected type layers),"range":[startChar,endChar]? (one … | needs document; disabled in catalogue snapshot |
| `type.characterStyle.clearOverride` | Clear Override |  | {"layer":id? \| "layers":[id]? (default: the selected type layers),"range":[startChar,endChar]? (one layer; default all text)} | needs document; disabled in catalogue snapshot |
| `type.characterStyle.delete` | Delete Style |  | {"id":u32} (text keeps its formatting as overrides) | needs document; disabled in catalogue snapshot |
| `type.characterStyle.duplicate` | Duplicate Style |  | {"id":u32} | needs document; disabled in catalogue snapshot |
| `type.characterStyle.list` | List Character Styles |  | {"layer":id? \| "layers":[id]? (default: the selected type layers),"range":[startChar,endChar]? (one layer; default all text)} → {"styles":[{"id","name",attributes,"resolved"}],"current":{"c… | needs document; disabled in catalogue snapshot |
| `type.characterStyle.new` | New Character Style |  | {"name":str?,"attrs":{model fields as in type.info ("size_pt":36,"font_family":"Inter","align":"Center",…) or Character/Paragraph panel keys as in type.setStyle ("size":36,"font":"Inter","c… | needs document; disabled in catalogue snapshot |
| `type.characterStyle.redefine` | Redefine Character Style |  | {"id":u32? (default: the targeted text's style),"layer":id? \| "layers":[id]? (default: the selected type layers),"range":[startChar,endChar]? (one layer; default all text)} (the style takes… | needs document; disabled in catalogue snapshot |
| `type.characterStyle.rename` | Rename Style |  | {"id":u32,"name":str} | needs document; disabled in catalogue snapshot |
| `type.characterStyle.set` | Character Style Options |  | {"id":u32 (paragraph: 0 = Basic Paragraph),"name":str?,"attrs":{model fields as in type.info ("size_pt":36,"font_family":"Inter","align":"Center",…) or Character/Paragraph panel keys as in … | needs document; disabled in catalogue snapshot |
| `type.convertToParagraphText` | Convert to Paragraph Text | Type | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `type.convertToPointText` | Convert to Point Text | Type | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `type.convertToShape` | Convert to Shape | Type | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `type.create` | New Type Layer | Layer > New | {"x":px,"y":px (baseline anchor of point text),"text":str,"box":[x,y,w,h]? (paragraph text),"name":str?,"align":"left\|center\|right\|justify…"?,"orientation":"horizontal\|vertical"="horizontal… | needs document; disabled in catalogue snapshot |
| `type.createSelection` | Type Mask |  | {"layer":id\|name? (a type layer whose glyphs become the selection),"removeLayer":bool=false (delete that layer in the same step: the Type Mask tools' temporary text),"operation":"new\|add\|su… | needs document; disabled in catalogue snapshot |
| `type.createWorkPath` | Create Work Path | Type | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `type.decreaseSize` | Decrease Type Size |  | {"layer":id?,"range":[startChar,endChar]? (default all),"by":pt? (as the layer appears)} | needs document; disabled in catalogue snapshot |
| `type.decreaseSizeMore` | Decrease Type Size by 10 |  | {"layer":id?,"range":[startChar,endChar]? (default all),"by":pt? (as the layer appears)} | needs document; disabled in catalogue snapshot |
| `type.detachFromPath` | Release Type from Path |  | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `type.edit` | Edit Type |  | {"layer":id?,"text":str? (replace all, styles kept),"replace":{"start":char,"end":char,"text":str}?,"runs":[{"start":char,"end":char,…character keys}]?,"box":[x,y,w,h]? (to paragraph text),… | needs document; disabled in catalogue snapshot |
| `type.fillPath` | Area Type |  | {"layer":id? (default active Type layer),"shape":layerId? (a shape layer; default the work path)} → the text wraps inside the path's closed subpaths, holes included | needs document; disabled in catalogue snapshot |
| `type.font.favorite` | Add to Favorites |  | {"family":str,"on":bool?=toggle} → family, favorite, favorites |  |
| `type.font.library` | Font Library |  | {} → favorites |  |
| `type.fonts` | List Fonts |  | {"family":str? (faces of one family)} |  |
| `type.hitTest` | Hit-Test Type |  | {"layer":id?, "x":px, "y":px} → {"layer","index":char,"line","inside":bool}. No layer: the topmost visible type layer whose laid-out text or rendered pixels contain the point (same order as… | needs document; disabled in catalogue snapshot |
| `type.increaseSize` | Increase Type Size |  | {"layer":id?,"range":[startChar,endChar]? (default all),"by":pt? (as the layer appears)} | needs document; disabled in catalogue snapshot |
| `type.increaseSizeMore` | Increase Type Size by 10 |  | {"layer":id?,"range":[startChar,endChar]? (default all),"by":pt? (as the layer appears)} | needs document; disabled in catalogue snapshot |
| `type.info` | Type Layer Info |  | {"layer":id?} → text, runs/paragraphs (char offsets + styles), shape, transform, laid-out lines (text space px), bounds | needs document; disabled in catalogue snapshot |
| `type.insertText` | Insert Glyph |  | {"layer":id?,"text":str,"at":char? (default: end of text),"range":[startChar,endChar]? (replaced),"label":str?} → {"layer","caret"} | needs document; disabled in catalogue snapshot |
| `type.loadDefaultTypeStyles` | Load Default Type Styles | Type | {"layer":id? or "layers":[id,…]? (default selected Type layers)} | needs document; disabled in catalogue snapshot |
| `type.navigate` | Navigate Type |  | {"layer":id?, "index":char, "move":"wordPrev\|wordNext\|linePrev\|lineNext\|lineStart\|lineEnd\|start\|end", "x":px?} → {"index"}. Words are alphanumeric runs. x is the document x to keep across l… | needs document; disabled in catalogue snapshot |
| `type.openType.contextualAlternates` | Contextual Alternates | Type > OpenType | {"layer":id? or "layers":[id,…]? (default selected Type layers),"on":bool? (default: toggle representative),"range":[startChar,endChar]? (single layer; default all)} | needs document; disabled in catalogue snapshot |
| `type.openType.discretionaryLigatures` | Discretionary Ligatures | Type > OpenType | {"layer":id? or "layers":[id,…]? (default selected Type layers),"on":bool? (default: toggle representative),"range":[startChar,endChar]? (single layer; default all)} | needs document; disabled in catalogue snapshot |
| `type.openType.fractions` | Fractions | Type > OpenType | {"layer":id? or "layers":[id,…]? (default selected Type layers),"on":bool? (default: toggle representative),"range":[startChar,endChar]? (single layer; default all)} | needs document; disabled in catalogue snapshot |
| `type.openType.numerals.default` | Default | Type > OpenType > Numerals | {"layer":id? or "layers":[id,…]? (default selected Type layers)} | needs document; disabled in catalogue snapshot |
| `type.openType.numerals.lining` | Lining | Type > OpenType > Numerals | {"layer":id? or "layers":[id,…]? (default selected Type layers)} | needs document; disabled in catalogue snapshot |
| `type.openType.numerals.oldstyle` | Oldstyle | Type > OpenType > Numerals | {"layer":id? or "layers":[id,…]? (default selected Type layers)} | needs document; disabled in catalogue snapshot |
| `type.openType.numerals.proportional` | Proportional | Type > OpenType > Numerals | {"layer":id? or "layers":[id,…]? (default selected Type layers)} | needs document; disabled in catalogue snapshot |
| `type.openType.numerals.proportionalLining` | Proportional Lining | Type > OpenType > Numerals | {"layer":id? or "layers":[id,…]? (default selected Type layers)} | needs document; disabled in catalogue snapshot |
| `type.openType.numerals.proportionalOldstyle` | Proportional Oldstyle | Type > OpenType > Numerals | {"layer":id? or "layers":[id,…]? (default selected Type layers)} | needs document; disabled in catalogue snapshot |
| `type.openType.numerals.tabular` | Tabular | Type > OpenType > Numerals | {"layer":id? or "layers":[id,…]? (default selected Type layers)} | needs document; disabled in catalogue snapshot |
| `type.openType.numerals.tabularLining` | Tabular Lining | Type > OpenType > Numerals | {"layer":id? or "layers":[id,…]? (default selected Type layers)} | needs document; disabled in catalogue snapshot |
| `type.openType.numerals.tabularOldstyle` | Tabular Oldstyle | Type > OpenType > Numerals | {"layer":id? or "layers":[id,…]? (default selected Type layers)} | needs document; disabled in catalogue snapshot |
| `type.openType.oldstyle` | Oldstyle | Type > OpenType | {"layer":id? or "layers":[id,…]? (default selected Type layers),"on":bool? (default: toggle representative),"range":[startChar,endChar]? (single layer; default all)} | needs document; disabled in catalogue snapshot |
| `type.openType.ordinals` | Ordinals | Type > OpenType | {"layer":id? or "layers":[id,…]? (default selected Type layers),"on":bool? (default: toggle representative),"range":[startChar,endChar]? (single layer; default all)} | needs document; disabled in catalogue snapshot |
| `type.openType.ornaments` | Ornaments | Type > OpenType | {"layer":id? or "layers":[id,…]? (default selected Type layers),"on":bool? (default: toggle representative),"range":[startChar,endChar]? (single layer; default all)} | needs document; disabled in catalogue snapshot |
| `type.openType.standardLigatures` | Standard Ligatures | Type > OpenType | {"layer":id? or "layers":[id,…]? (default selected Type layers),"on":bool? (default: toggle representative),"range":[startChar,endChar]? (single layer; default all)} | needs document; disabled in catalogue snapshot |
| `type.openType.stylisticAlternates` | Stylistic Alternates | Type > OpenType | {"layer":id? or "layers":[id,…]? (default selected Type layers),"on":bool? (default: toggle representative),"range":[startChar,endChar]? (single layer; default all)} | needs document; disabled in catalogue snapshot |
| `type.openType.swash` | Swash | Type > OpenType | {"layer":id? or "layers":[id,…]? (default selected Type layers),"on":bool? (default: toggle representative),"range":[startChar,endChar]? (single layer; default all)} | needs document; disabled in catalogue snapshot |
| `type.openType.titlingAlternates` | Titling Alternates | Type > OpenType | {"layer":id? or "layers":[id,…]? (default selected Type layers),"on":bool? (default: toggle representative),"range":[startChar,endChar]? (single layer; default all)} | needs document; disabled in catalogue snapshot |
| `type.orientation.horizontal` | Horizontal | Type > Orientation | {"layer":id? or "layers":[id,…]? (default selected Type layers)} | needs document; disabled in catalogue snapshot |
| `type.orientation.vertical` | Vertical | Type > Orientation | {"layer":id? or "layers":[id,…]? (default selected Type layers)} | needs document; disabled in catalogue snapshot |
| `type.paragraphStyle.apply` | Apply Paragraph Style |  | {"id":u32\|0\|null (0/null: None / Basic Paragraph),"clearOverrides":bool=false (Alt-click),"layer":id? \| "layers":[id]? (default: the selected type layers),"range":[startChar,endChar]? (one … | needs document; disabled in catalogue snapshot |
| `type.paragraphStyle.clearOverride` | Clear Override |  | {"layer":id? \| "layers":[id]? (default: the selected type layers),"range":[startChar,endChar]? (one layer; default all text)} | needs document; disabled in catalogue snapshot |
| `type.paragraphStyle.delete` | Delete Style |  | {"id":u32} (text keeps its formatting as overrides) | needs document; disabled in catalogue snapshot |
| `type.paragraphStyle.duplicate` | Duplicate Style |  | {"id":u32} | needs document; disabled in catalogue snapshot |
| `type.paragraphStyle.list` | List Paragraph Styles |  | {"layer":id? \| "layers":[id]? (default: the selected type layers),"range":[startChar,endChar]? (one layer; default all text)} → {"styles":[{"id","name",attributes,"resolved"}],"current":{"c… | needs document; disabled in catalogue snapshot |
| `type.paragraphStyle.new` | New Paragraph Style |  | {"name":str?,"attrs":{model fields as in type.info ("size_pt":36,"font_family":"Inter","align":"Center",…) or Character/Paragraph panel keys as in type.setStyle ("size":36,"font":"Inter","c… | needs document; disabled in catalogue snapshot |
| `type.paragraphStyle.redefine` | Redefine Paragraph Style |  | {"id":u32? (default: the targeted text's style),"layer":id? \| "layers":[id]? (default: the selected type layers),"range":[startChar,endChar]? (one layer; default all text)} (the style takes… | needs document; disabled in catalogue snapshot |
| `type.paragraphStyle.rename` | Rename Style |  | {"id":u32,"name":str} | needs document; disabled in catalogue snapshot |
| `type.paragraphStyle.set` | Paragraph Style Options |  | {"id":u32 (paragraph: 0 = Basic Paragraph),"name":str?,"attrs":{model fields as in type.info ("size_pt":36,"font_family":"Inter","align":"Center",…) or Character/Paragraph panel keys as in … | needs document; disabled in catalogue snapshot |
| `type.pasteLoremIpsum` | Paste Lorem Ipsum | Type | {"layer":id?,"at":char? (default end),"new":bool=false (new paragraph text layer)} | needs document; disabled in catalogue snapshot |
| `type.rasterize` | Rasterize Type | Layer > Rasterize | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `type.rasterizeTypeLayer` | Rasterize Type Layer | Type | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `type.replaceAllMissingFonts` | Replace All Missing Fonts | Type | {} (with the default family) | needs document; disabled in catalogue snapshot |
| `type.resolveMissingFonts` | Resolve Missing Fonts… | Type | {"map":{"Missing Family":"Installed Family"}?} (no map: list the missing families) | needs document; disabled in catalogue snapshot |
| `type.saveDefaultTypeStyles` | Save Default Type Styles | Type | {} (from the active type layer; new type layers start from them) | needs document; disabled in catalogue snapshot |
| `type.setStyle` | Set Type Style |  | {"layer":id? or "layers":[id,…]? (default selected Type layers),"range":[startChar,endChar]? (single layer; default all),"metricsAsShown":bool=false (size/leading/leadingBy include each lay… | needs document; disabled in catalogue snapshot |
| `type.updateAllTextLayers` | Update All Text Layers | Type | {} | needs document; disabled in catalogue snapshot |
| `type.warpText` | Warp Text… | Type | {"layer":id? or "layers":[id,…]? (default selected Type layers),"style":"none\|arc\|arcLower\|arcUpper\|arch\|bulge\|shellLower\|shellUpper\|flag\|wave\|fish\|rise\|fisheye\|inflate\|squeeze\|twist"="arc"… | needs document; disabled in catalogue snapshot |
