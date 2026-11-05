# PhotoCraft Image Adjust

Auto-generated from the installed 965-command registry (snapshot 2026-11-05). Every row is a real command id; params are abbreviated. Query the full schema with `$PC commands --json`. PhotoCraft input is positional and `--out` must differ from input.

Commands: **66** across 1 groups.

## Coverage

`image` 66

## `image` (66)

VectorCraft's `image` group has only `image.info`; raster placement uses `file.place`, raster cropping `object.cropImage`, rasterizing `object.rasterize`.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `image.adjustments.blackWhite` | Black & White… | Image > Adjustments | {"reds":-200..300=40,"yellows":-200..300=60,"greens":-200..300=40,"cyans":-200..300=60,"blues":-200..300=20,"magentas":-200..300=80,"tint":bool=false,"tintColor":"#rrggbb"} | needs document; disabled in catalogue snapshot |
| `image.adjustments.brightnessContrast` | Brightness/Contrast… | Image > Adjustments | {"brightness":-150..150=0,"contrast":-50..100=0,"legacy":bool=false} | needs document; disabled in catalogue snapshot |
| `image.adjustments.channelMixer` | Channel Mixer… | Image > Adjustments | {"red":json,"green":json,"blue":json,"gray":json,"monochrome":bool=false} (per output channel [red %, green %, blue %, constant %] in -200..200; gray = the monochrome mix) | needs document; disabled in catalogue snapshot |
| `image.adjustments.colorBalance` | Color Balance… | Image > Adjustments | {"shadows":json,"midtones":json,"highlights":json,"preserveLuminosity":bool=true} (each tone [cyan-red, magenta-green, yellow-blue] in -100..100) | needs document; disabled in catalogue snapshot |
| `image.adjustments.colorLookup` | Color Lookup… | Image > Adjustments | {"lut":"none\|warm\|cool\|tealOrange\|bleachBypass\|fadedFilm\|dayForNight\|monoContrast\|crossProcess"="none","file":text,"interpolation":"trilinear\|tetrahedral"="trilinear","dither":bool=false,"d… | needs document; disabled in catalogue snapshot |
| `image.adjustments.colorLookup.list` | List Color Lookup Looks |  | {} |  |
| `image.adjustments.curves` | Curves… | Image > Adjustments | {"points":json,"red":json,"green":json,"blue":json,"pencil":bool=false,"smooth":0..10=0,"eyedropper":json} (curves as [[in,out],…] in 0..255, 2..19 points: points = composite; red/green/blu… | needs document; disabled in catalogue snapshot |
| `image.adjustments.desaturate` | Desaturate | Image > Adjustments | {"target":"pixels"\|"mask"\|{"color":i}\|{"colors":[i,…]}?=Channels panel target,"layer":id\|name?=active} | needs document; disabled in catalogue snapshot |
| `image.adjustments.equalize` | Equalize | Image > Adjustments | {} | needs document; disabled in catalogue snapshot |
| `image.adjustments.exposure` | Exposure… | Image > Adjustments | {"exposure":-20..20=0,"offset":-0.5..0.5=0,"gamma":0.01..9.99=1} | needs document; disabled in catalogue snapshot |
| `image.adjustments.gradientMap` | Gradient Map… | Image > Adjustments | {"stops":json,"reverse":bool=false,"dither":bool=false} (stops [[location 0..1, "#rrggbb"], …], 2..64) | needs document; disabled in catalogue snapshot |
| `image.adjustments.hdrToning` | HDR Toning… | Image > Adjustments | {"radius":1..500=30,"strength":0.1..4=0.5,"gamma":0.1..2=1,"exposure":-5..5=0,"detail":-100..300=30,"shadow":-100..100=0,"highlight":-100..100=0,"vibrance":-100..100=0,"saturation":-100..10… | needs document; disabled in catalogue snapshot |
| `image.adjustments.hueSaturation` | Hue/Saturation… | Image > Adjustments | {"hue":-180..180=0,"saturation":-100..100=0,"lightness":-100..100=0,"colorize":bool=false,"reds":json,"yellows":json,"greens":json,"cyans":json,"blues":json,"magentas":json} (per range {"hu… | needs document; disabled in catalogue snapshot |
| `image.adjustments.invert` | Invert | Image > Adjustments | {} | needs document; disabled in catalogue snapshot |
| `image.adjustments.levels` | Levels… | Image > Adjustments | {"inBlack":0..253=0,"gamma":0.01..9.99=1,"inWhite":2..255=255,"outBlack":0..255=0,"outWhite":0..255=255,"red":json,"green":json,"blue":json,"eyedropper":json} (top level = composite; per ch… | needs document; disabled in catalogue snapshot |
| `image.adjustments.matchColor` | Match Color… | Image > Adjustments | {"source":doc,"sourceLayer":json,"luminance":1..200=100,"intensity":1..200=100,"fade":0..100=0,"neutralize":bool=false,"useSelectionInSource":bool=false,"useSelectionInTarget":bool=false} (… | needs document; disabled in catalogue snapshot |
| `image.adjustments.photoFilter` | Photo Filter… | Image > Adjustments | {"filter":"warming85\|warmingLBA\|warming81\|cooling80\|coolingLBB\|cooling82\|red\|orange\|yellow\|green\|cyan\|blue\|violet\|magenta\|sepia\|deepRed\|deepBlue\|deepEmerald\|deepYellow\|underwater","color":"… | needs document; disabled in catalogue snapshot |
| `image.adjustments.posterize` | Posterize… | Image > Adjustments | {"levels":2..255=4} | needs document; disabled in catalogue snapshot |
| `image.adjustments.replaceColor` | Replace Color… | Image > Adjustments | {"localized":bool=false,"color":color,"fuzziness":0..200=40,"range":0..100=100,"hue":-180..180=0,"saturation":-100..100=0,"lightness":-100..100=0,"points":[[x,y],…]?,"labMinimum":[L,a,b]?,"… | needs document; disabled in catalogue snapshot |
| `image.adjustments.selectiveColor` | Selective Color… | Image > Adjustments | {"method":"relative\|absolute"="relative","colors":"reds\|yellows\|greens\|cyans\|blues\|magentas\|whites\|neutrals\|blacks"="reds","cyan":-100..100=0,"magenta":-100..100=0,"yellow":-100..100=0,"bla… | needs document; disabled in catalogue snapshot |
| `image.adjustments.shadowsHighlights` | Shadows/Highlights… | Image > Adjustments | {"shadowAmount":0..100=35,"shadowTone":0..100=50,"shadowRadius":0..2500=30,"highlightAmount":0..100=0,"highlightTone":0..100=50,"highlightRadius":0..2500=30,"color":-100..100=20,"midtone":-… | needs document; disabled in catalogue snapshot |
| `image.adjustments.threshold` | Threshold… | Image > Adjustments | {"level":1..255=128} | needs document; disabled in catalogue snapshot |
| `image.adjustments.vibrance` | Vibrance… | Image > Adjustments | {"vibrance":-100..100=0,"saturation":-100..100=0} | needs document; disabled in catalogue snapshot |
| `image.analysis.countTool` | Count Tool | Image > Analysis | {} → count groups and markers (edit with count.*) | needs document; disabled in catalogue snapshot |
| `image.analysis.info` | Analysis Info |  | {} → scale, ruler readout, count groups, note and log counts | needs document; disabled in catalogue snapshot |
| `image.analysis.placeScaleMarker` | Place Scale Marker… | Image > Analysis | {"length":logical units=nice ≈ width/5,"font":str?,"fontSize":pt=12,"displayText":bool=true,"textPosition":"top\|bottom"="bottom","color":"black\|white"="black"} | needs document; disabled in catalogue snapshot |
| `image.analysis.recordMeasurements` | Record Measurements | Image > Analysis | {"source":"auto\|selection\|ruler\|count"="auto"} → appended Measurement Log rows (selection: summary + one row per feature) | needs document; disabled in catalogue snapshot |
| `image.analysis.rulerTool` | Ruler Tool | Image > Analysis | {"start":[x,y],"end":[x,y],"protractor":[x,y]\|null?,"clear":bool=false} (no params: read) → X/Y/W/H/angle/L1/L2 | needs document; disabled in catalogue snapshot |
| `image.analysis.selectDataPoints` | Select Data Points… | Image > Analysis | {"selection":[keys]\|{key:bool}?,"ruler":[keys]\|{key:bool}?,"count":[keys]\|{key:bool}?,"reset":bool=false} (keys: label,dateTime,document,source,scale,scaleUnits,scaleFactor,count,area,perim… |  |
| `image.analysis.setMeasurementScale` | Set Measurement Scale… | Image > Analysis | {"preset":"default\|custom"="custom","pixelLength":px,"logicalLength":number,"units":str (e.g. "mm")} (no params: read the scale) | needs document; disabled in catalogue snapshot |
| `image.analysis.straightenLayer` | Straighten Layer |  | {"crop":bool=(active layer is the Background)} (rotates so the ruler line is level; crop = rotate the canvas and crop to the image) | needs document; disabled in catalogue snapshot |
| `image.applyDataSet` | Apply Data Set… | Image | {name\|index} → {applied, index}: sets layer visibility/text/pixels from the data set (one history step) | needs document; disabled in catalogue snapshot |
| `image.applyImage` | Apply Image… | Image | {"source":{"document":index?,"layer":id\|name\|{"name":str}\|{"background":true}\|"merged"="merged","channel":"composite"\|"red\|…"\|index\|"selection"\|"transparency"\|"mask"="composite","invert":bo… | needs document; disabled in catalogue snapshot |
| `image.autoColor` | Auto Color | Image | {} | needs document; disabled in catalogue snapshot |
| `image.autoContrast` | Auto Contrast | Image | {} | needs document; disabled in catalogue snapshot |
| `image.autoTone` | Auto Tone | Image | {} | needs document; disabled in catalogue snapshot |
| `image.calculations` | Calculations… | Image | {"source1":{"document","layer","channel","invert"},"source2":{…},"blending":"multiply\|…"="multiply","opacity":0..100=100,"scale":1..2=1,"offset":-255..255=0,"mask":{…}?,"result":"newChannel… | needs document; disabled in catalogue snapshot |
| `image.canvasSize` | Canvas Size… | Image | {"width":number,"height":number,"units":"px\|percent"="px" (percent uses each current side; absolute sizes only),"relative":bool=false,"anchor":"topLeft\|top\|topRight\|left\|center\|right\|bottom… | needs document; disabled in catalogue snapshot |
| `image.crop` | Crop | Image | {"x":px,"y":px,"width":px,"height":px,"angle":-3600..3600=0,"deleteCroppedPixels":bool=true,"contentAware":bool=false,"targetWidth":px,"targetHeight":px,"resolution":ppi,"resample":"bicubic… | needs document; disabled in catalogue snapshot |
| `image.detectFaces` | Detect Faces |  | {"minScore":0..1=0.5,"sampleAllLayers":bool=true} → {"faces":[{"score","rect":[x,y,w,h],"landmarks":{"rightEye","leftEye","nose","mouthRight","mouthLeft"}: [x,y] each},…]} (best first; "rig… | needs document; disabled in catalogue snapshot |
| `image.duplicate` | Duplicate… | Image | {"name":str,"mergedOnly":bool=false} | needs document; disabled in catalogue snapshot |
| `image.imageRotation.180` | 180° | Image > Image Rotation | {} | needs document; disabled in catalogue snapshot |
| `image.imageRotation.90ccw` | 90° Counter Clockwise | Image > Image Rotation | {} | needs document; disabled in catalogue snapshot |
| `image.imageRotation.90cw` | 90° Clockwise | Image > Image Rotation | {} | needs document; disabled in catalogue snapshot |
| `image.imageRotation.flipCanvasHorizontal` | Flip Canvas Horizontal | Image > Image Rotation | {} | needs document; disabled in catalogue snapshot |
| `image.imageRotation.flipCanvasVertical` | Flip Canvas Vertical | Image > Image Rotation | {} | needs document; disabled in catalogue snapshot |
| `image.imageSize` | Image Size… | Image | {"width":number,"height":number,"units":"px\|pt"="px" (points use the document's current resolution),"percent":%? (both sides; an explicit side wins),"resolution":ppi,"keepPrintSize":bool=fa… | needs document; disabled in catalogue snapshot |
| `image.mode.bitmap` | Bitmap… | Image > Mode | {"resolution":1..30000=document,"method":"diffusion\|threshold\|pattern\|halftone\|customPattern"="diffusion","frequency":1..999=53,"angle":-180..180=45,"shape":"round\|ellipse\|line\|square\|diamo… | needs document; disabled in catalogue snapshot |
| `image.mode.bits16` | 16 Bits/Channel | Image > Mode | {} | needs document; disabled in catalogue snapshot |
| `image.mode.bits32` | 32 Bits/Channel | Image > Mode | {} | needs document; disabled in catalogue snapshot |
| `image.mode.bits8` | 8 Bits/Channel | Image > Mode | {} | needs document; disabled in catalogue snapshot |
| `image.mode.cmyk` | CMYK Color | Image > Mode | {"profile":"<builtin id>\|working\|/path/to/profile.icc"=working,"intent":"perceptual\|relative\|saturation\|absolute"="relative","bpc":bool=true} | needs document; disabled in catalogue snapshot |
| `image.mode.colorTable` | Color Table… | Image > Mode | {"table":"custom\|blackBody\|grayscale\|spectrum\|systemMac\|systemWindows\|web"="custom","colors":json,"entries":json,"transparent":json} (colors: ["#rrggbb", …]; entries: {"index": "#rrggbb"}; … | needs document; disabled in catalogue snapshot |
| `image.mode.duotone` | Duotone… | Image > Mode | {"type":"duotone\|monotone\|tritone\|quadtone"="duotone","inks":json} (inks: [{"name","color":"#rrggbb","curve":[[in,out],…] in 0..100}, …]) | needs document; disabled in catalogue snapshot |
| `image.mode.grayscale` | Grayscale | Image > Mode | {"profile":"<builtin id>\|working\|/path/to/profile.icc"=working,"intent":"perceptual\|relative\|saturation\|absolute"="relative","bpc":bool=true} | needs document; disabled in catalogue snapshot |
| `image.mode.indexedColor` | Indexed Color… | Image > Mode | {"palette":"selective\|perceptual\|adaptive\|exact\|systemMac\|systemWindows\|web\|uniform"="selective","colors":2..256=256,"forced":"blackWhite\|none\|primaries\|web"="blackWhite","transparency":boo… | needs document; disabled in catalogue snapshot |
| `image.mode.lab` | Lab Color | Image > Mode | {"profile":"<builtin id>\|working\|/path/to/profile.icc"=working,"intent":"perceptual\|relative\|saturation\|absolute"="relative","bpc":bool=true} | needs document; disabled in catalogue snapshot |
| `image.mode.multichannel` | Multichannel | Image > Mode | {} (flattens; RGB → Cyan/Magenta/Yellow, CMYK → Cyan/Magenta/Yellow/Black, Lab → Alpha 1–3, Grayscale → Black, Duotone → its inks) | needs document; disabled in catalogue snapshot |
| `image.mode.rgb` | RGB Color | Image > Mode | {"profile":"<builtin id>\|working\|/path/to/profile.icc"=working,"intent":"perceptual\|relative\|saturation\|absolute"="relative","bpc":bool=true} | needs document; disabled in catalogue snapshot |
| `image.perspectiveCrop` | Perspective Crop |  | {"corners":[[x,y],[x,y],[x,y],[x,y]] (top-left, top-right, bottom-right, bottom-left; a convex quad, document px),"width":px,"height":px,"resolution":ppi,"interpolation":"bicubic\|bilinear\|n… | needs document; disabled in catalogue snapshot |
| `image.revealAll` | Reveal All | Image | {} | needs document; disabled in catalogue snapshot |
| `image.rotation.arbitrary` | Arbitrary… | Image > Image Rotation | {"angle":-359.99..359.99=0,"direction":"cw\|ccw"="cw","interpolation":"bicubic\|bilinear\|nearest"="bicubic"} | needs document; disabled in catalogue snapshot |
| `image.trap` | Trap… | Image | {width:px>=1=1} → {trapped,width}: spread inks at colour edges (CMYK only) | needs document; disabled in catalogue snapshot |
| `image.trim` | Trim… | Image | {"basedOn":"transparent\|topLeft\|bottomRight"="transparent","top":bool=true,"bottom":bool=true,"left":bool=true,"right":bool=true} | needs document; disabled in catalogue snapshot |
| `image.variables.dataSets` | Data Sets… | Image > Variables | {dataSets:[{name, values:[{variable, kind:visibility\|text\|pixels, value}]}], append?} → {defs,dataSets,active} | needs document; disabled in catalogue snapshot |
| `image.variables.define` | Define… | Image > Variables | {defs:[{name, layer:id, type:visibility\|textReplacement\|pixelReplacement, method?:fit\|fill\|asIs\|conform, align?, clip?}]} → {defs,dataSets,active} | needs document; disabled in catalogue snapshot |
