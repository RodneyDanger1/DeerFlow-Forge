# PhotoCraft Selection Channel

Auto-generated from the installed 965-command registry (snapshot 2026-11-05). Every row is a real command id; params are abbreviated. Query the full schema with `$PC commands --json`. PhotoCraft input is positional and `--out` must differ from input.

Commands: **57** across 2 groups.

## Coverage

`channel` 22 · `select` 35

## `channel` (22)



| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `channel.delete` | Delete Channel |  | {"channel":index\|name?=targeted} | needs document; disabled in catalogue snapshot |
| `channel.duplicate` | Duplicate Channel… |  | {"channel":index\|name\|"red\|…"\|"composite"\|"quickMask","name":str?,"document":index\|"new"?=active,"invert":bool=false} | needs document; disabled in catalogue snapshot |
| `channel.list` | Channels |  | {} | needs document; disabled in catalogue snapshot |
| `channel.merge` | Merge Channels… |  | {"mode":"rgb\|cmyk\|lab"="rgb","documents":[index,…]?=open grayscale docs of the active size,"name":str?} | needs document; disabled in catalogue snapshot |
| `channel.mergeSpot` | Merge Spot Channel |  | {"channel":index\|name?=targeted or first spot} | needs document; disabled in catalogue snapshot |
| `channel.move` | Reorder Channel |  | {"channel":index\|name,"to":index} | needs document; disabled in catalogue snapshot |
| `channel.new` | New Channel… |  | {"name":str?,"fill":"black\|white\|selection"="black","color":"#rrggbb"="#ff0000","opacity":0..100=50,"indicates":"masked\|selected"="masked"} | needs document; disabled in catalogue snapshot |
| `channel.newSpot` | New Spot Channel… |  | {"name":str?,"color":"#rrggbb"="#ff0000","solidity":0..100=0,"fromSelection":bool=true} | needs document; disabled in catalogue snapshot |
| `channel.options` | Channel Options… |  | {"channel":index\|name\|"quickMask"\|"mask","name":str?,"indicates":"masked\|selected\|spot"?,"color":"#rrggbb"?,"opacity":0..100?,"solidity":0..100?} ("mask": Layer Mask Display Options, the ru… | needs document; disabled in catalogue snapshot |
| `channel.rename` | Rename Channel |  | {"channel":index\|name,"name":str} | needs document; disabled in catalogue snapshot |
| `channel.setVisible` | Channel Visibility |  | {"channel":"composite"\|"red\|…"\|index\|name\|"quickMask","visible":bool?=toggle} | needs document; disabled in catalogue snapshot |
| `channel.split` | Split Channels |  | {"closeOriginal":bool=true} | needs document; disabled in catalogue snapshot |
| `channel.target` | Target Channel |  | {"channel":"composite"\|"mask"\|"vectorMask"\|"red\|green\|blue\|…"\|index\|name\|{"color":index\|name}\|{"alpha":index}="composite","colors":[index,…]?,"extend":bool=false} (a color object selects on… | needs document; disabled in catalogue snapshot |
| `channel.target.composite` | Target Composite Channel |  | {} | needs document; disabled in catalogue snapshot |
| `channel.target.layerMask` | Target Layer Mask |  | {} | needs document; disabled in catalogue snapshot |
| `channel.target.slot3` | Target Channel 3 |  | {} | needs document; disabled in catalogue snapshot |
| `channel.target.slot4` | Target Channel 4 |  | {} | needs document; disabled in catalogue snapshot |
| `channel.target.slot5` | Target Channel 5 |  | {} | needs document; disabled in catalogue snapshot |
| `channel.target.slot6` | Target Channel 6 |  | {} | needs document; disabled in catalogue snapshot |
| `channel.target.slot7` | Target Channel 7 |  | {} | needs document; disabled in catalogue snapshot |
| `channel.target.slot8` | Target Channel 8 |  | {} | needs document; disabled in catalogue snapshot |
| `channel.target.slot9` | Target Channel 9 |  | {} | needs document; disabled in catalogue snapshot |

## `select` (35)

Selection commands define what later commands affect. `select.all` is required before many trace/path operations; `select.set` replaces a selection, `select.add` extends it.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `select.all` | All | Select | {} | needs document; disabled in catalogue snapshot |
| `select.allLayers` | All Layers | Select | {} | needs document; disabled in catalogue snapshot |
| `select.colorRange` | Color Range… | Select | {"select":"sampledColors\|reds\|yellows\|greens\|cyans\|blues\|magentas\|highlights\|midtones\|shadows\|skinTones\|outOfGamut"="sampledColors","color":"#rrggbb"=foreground,"colors":["#rrggbb",…]?,"poi… | needs document; disabled in catalogue snapshot |
| `select.convertToShape` | Convert to Shape |  | {"tolerance":0.5..10 px=2} → shape.info | disabled in catalogue snapshot |
| `select.deselect` | Deselect | Select | {} | disabled in catalogue snapshot |
| `select.deselectLayers` | Deselect Layers | Select | {} | needs document; disabled in catalogue snapshot |
| `select.drop` | Drop Floating Selection |  | {} → {dropped, offset} (drops the floating piece into its layer and moves the selection with it, shrunk to the moved pixels: the selection limited to where the layer has pixels, as in Photo… | needs document; disabled in catalogue snapshot |
| `select.editInQuickMaskMode` | Edit in Quick Mask Mode | Select | {"on":bool?=toggle} | needs document; disabled in catalogue snapshot |
| `select.findLayers` | Find Layers | Select | {"name":str (case-insensitive substring)} | needs document; disabled in catalogue snapshot |
| `select.float` | Float Selection |  | {"dx":px=0,"dy":px=0,"copy":bool=false,"target":"pixels"\|"mask"="pixels" (mask: float the selected part of the layer's mask, the hole takes the background colour)} → {layer, offset} (cuts t… | needs document; disabled in catalogue snapshot |
| `select.focusArea` | Focus Area… | Select | {"range":0..1=0.5,"noise":0..1=0,"sampleAllLayers":bool=true,"mode":"replace\|add\|subtract\|intersect"="replace"} | needs document; disabled in catalogue snapshot |
| `select.grow` | Grow | Select | {"tolerance":0..255=32,"sampleAllLayers":bool=false} | disabled in catalogue snapshot |
| `select.inverse` | Inverse | Select | {} | disabled in catalogue snapshot |
| `select.isolateLayers` | Isolate Layers | Select | {"on":bool? (default: toggle)} — Layers panel lists only the selected layers → {isolated, layers} | disabled in catalogue snapshot |
| `select.lasso` | Lasso |  | {"points":[[x,y],…],"mode":"replace\|add\|subtract\|intersect"="replace","antiAlias":bool=true,"feather":px=0} | needs document; disabled in catalogue snapshot |
| `select.loadLuminosity` | Load Luminosity |  | {} | needs document; disabled in catalogue snapshot |
| `select.loadSelection` | Load Selection… | Select | {"channel":index\|name\|"composite"\|"red\|green\|blue\|…"\|"transparency"\|"mask"\|"vectorMask"\|"quickMask"\|"selection"\|"targeted" (the Channels panel's target),"layer":id\|name\|{"name":str}\|{"backg… | needs document; disabled in catalogue snapshot |
| `select.magicWand` | Magic Wand |  | {"x":px,"y":px,"tolerance":0..255=32,"contiguous":bool=true,"antiAlias":bool=true,"sampleAllLayers":bool=false,"mode":"replace\|add\|subtract\|intersect"="replace"} (samples the visible alpha,… | needs document; disabled in catalogue snapshot |
| `select.magneticLasso` | Magnetic Lasso |  | {"points":[[x,y],…] (≥3 fastening points in order; with trace=false, the finished outline),"width":1..256=10 (px: follows edges this close to the points),"contrast":1..100=10 (%: weaker edg… | needs document; disabled in catalogue snapshot |
| `select.modify.border` | Border… | Select > Modify | {"radius":1..200=1} | disabled in catalogue snapshot |
| `select.modify.contract` | Contract… | Select > Modify | {"radius":1..500=1,"applyAtCanvasBounds":bool=false} | disabled in catalogue snapshot |
| `select.modify.expand` | Expand… | Select > Modify | {"radius":1..500=1,"applyAtCanvasBounds":bool=false} | disabled in catalogue snapshot |
| `select.modify.feather` | Feather… | Select > Modify | {"radius":0.1..1000=1,"applyAtCanvasBounds":bool=false} | disabled in catalogue snapshot |
| `select.modify.smooth` | Smooth… | Select > Modify | {"radius":1..500=1,"applyAtCanvasBounds":bool=false} | disabled in catalogue snapshot |
| `select.object` | Object Selection |  | {"rect":[x,y,w,h] \| "point":[x,y],"mode":"replace\|add\|subtract\|intersect"="replace","sampleAllLayers":bool=false} (point: the Object Finder's object under the point, as hovering previews it) | needs document; disabled in catalogue snapshot |
| `select.quick` | Quick Selection |  | {"points":[[x,y],…],"size":px=30,"mode":"add\|subtract\|replace"="add","sampleAllLayers":bool=false,"enhanceEdge":bool=false} | needs document; disabled in catalogue snapshot |
| `select.rect` | Rectangular Selection |  | {"x":i32,"y":i32,"width":u32,"height":u32,"mode":"replace\|add\|subtract\|intersect"="replace","ellipse":bool=false,"line":"row\|column"?,"antiAlias":bool=true,"feather":px=0} | needs document; disabled in catalogue snapshot |
| `select.refineEdge` | Refine Edge |  | {"radius":px=0,"smartRadius":bool=false,"smooth":0..100=0,"feather":px=0,"contrast":0..100=0,"shiftEdge":-100..100=0,"decontaminate":bool=false,"amount":0..100=100,"output":"selection\|layer… | needs document; disabled in catalogue snapshot |
| `select.reselect` | Reselect | Select | {} | needs document; disabled in catalogue snapshot |
| `select.saveSelection` | Save Selection… | Select | {"name":str?,"channel":"new"\|index\|name="new","document":index?,"operation":"new\|replace\|add\|subtract\|intersect"="new"} | needs document; disabled in catalogue snapshot |
| `select.similar` | Similar | Select | {"tolerance":0..255=32,"sampleAllLayers":bool=false} | disabled in catalogue snapshot |
| `select.sky` | Sky | Select | {"mode":"replace\|add\|subtract\|intersect"="replace","sampleAllLayers":bool=true,"threshold":0..100=50 (higher = stricter),"softness":0..100=50 (edge softness)} → {selected, changed, coverage… | needs document; disabled in catalogue snapshot |
| `select.subject` | Subject | Select | {"sampleAllLayers":bool=false,"mode":"replace\|add\|subtract\|intersect"="replace"} (samples the selected layer; the composite when no pixel layer is selected) | needs document; disabled in catalogue snapshot |
| `select.toWorkPath` | Make Work Path |  | {"tolerance":0.5..10 px=2} → {subpaths,knots} | disabled in catalogue snapshot |
| `select.transformSelection` | Transform Selection | Select | {"rect":[x0,y0,x1,y1]? (frame; default = selection bounds),"quad"\|"corners":[[x,y]×4]? (where the frame's corners go: distort/perspective),"matrix":[a,b,c,d,e,f]?,"scaleX":%=100,"scaleY":%=… | disabled in catalogue snapshot |
