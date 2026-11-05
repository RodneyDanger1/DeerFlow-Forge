# PhotoCraft File Document Layer

Auto-generated from the installed 965-command registry (snapshot 2026-11-05). Every row is a real command id; params are abbreviated. Query the full schema with `$PC commands --json`. PhotoCraft input is positional and `--out` must differ from input.

Commands: **322** across 5 groups.

## Coverage

`document` 11 · `file` 59 · `history` 14 · `layer` 224 · `layerComp` 14

## `document` (11)

Document commands inspect/serialize/export the whole document. `document.export` is the main delivery path; `document.exportPdf`/`exportEps`/`exportDxf` are format-specific. Check `document.formats` for installed exporters.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `document.activate` | Activate Document |  | {"document":index\|{"index":uint}} or {"offset":int} (numeric document: zero-based tab index; typed index: one-based opening order; offset: places after the active document in opening order,… | needs document; disabled in catalogue snapshot |
| `document.inspect` | Inspect Document |  | {"document":index?} | needs document; disabled in catalogue snapshot |
| `document.move` | Move Document |  | {"document":index?,"to":index} | needs document; disabled in catalogue snapshot |
| `document.pixel` | Read Composite Pixel |  | {"x":i32,"y":i32} | needs document; disabled in catalogue snapshot |
| `document.presets.delete` | Delete Document Preset |  | {"name":str} |  |
| `document.presets.get` | Get Document Preset |  | {"name":str} -> {preset,params} (params for file.new; no document is created) |  |
| `document.presets.list` | List Document Presets |  | {} |  |
| `document.presets.save` | Save Document Preset |  | {"name":str (trimmed, ASCII case-insensitive unique, 1..255 characters),"settings":{"width":px,"height":px,"resolution":ppi=72,"mode":"rgb\|gray\|cmyk\|lab"="rgb","depth":8\|16\|32=8,"background… |  |
| `document.recent.add` | Add Recent Document Settings |  | {"settings":{same fields as document.presets.save}} (File › New records each document it creates; newest first, max 20, duplicates collapsed) |  |
| `document.recent.list` | List Recent Document Settings |  | {} -> {recent:[settings]} (newest first; each settings.command params minus unit/resolutionUnit go to file.new) |  |
| `document.sampleColor` | Sample Color |  | {"x":f64,"y":f64,"size":"point"\|1\|3\|5\|11\|31\|51\|101=1,"sampleLayer":"current"\|"currentAndBelow"\|"all"\|"allNoAdjustments"\|"currentAndBelowNoAdjustments"="all"} → [r,g,b,a] (the Eyedropper's S… | needs document; disabled in catalogue snapshot |

## `file` (59)

File commands create/open/save/place documents. `file.place` uses the raster's physical size (ppi), not pixel count; `file.saveAs` changes the working file, `file.saveCopy` preserves the original.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `file.approveMemory` | Approve High Memory PSD Import |  | {"id":u64,"approve":bool=true,"background":bool=true} |  |
| `file.automate.batch` | Batch… | File > Automate | {"steps":[[commandId,params]\|{"command":id,"params":{}}…] (a recorded action; Save/Save As marks the result),"source":"folder\|open"="folder" (open: run on live open documents),"input":folde… |  |
| `file.automate.conditionalModeChange` | Conditional Mode Change… | File > Automate | {"from":["rgb","grayscale","cmyk","lab","indexed","bitmap",…]\|"any"="any","to":"rgb\|grayscale\|cmyk\|lab"} | needs document; disabled in catalogue snapshot |
| `file.automate.contactSheetII` | Contact Sheet II… | File > Automate | {"input":folder\|[paths],"units":"inches\|cm\|mm\|pixels"="inches","width":8,"height":10,"resolution":ppi=300,"mode":"rgb\|gray\|cmyk\|lab"="rgb","depth":8\|16=8,"columns":5,"rows":6,"placeAcrossFi… |  |
| `file.automate.createDroplet` | Create Droplet… | File > Automate | {"path":str (.pcdroplet),"steps":[[id,params]…] (the action),"name":str?,"output":folder?,"format":"same\|png\|jpg\|…"?,"quality":0..12?,"shim":bool=true on Unix (writes <name>.command calling… |  |
| `file.automate.cropAndStraightenPhotos` | Crop and Straighten Photos | File > Automate | {} → one new document per photo found on the scan (inside the selection when there is one) | needs document; disabled in catalogue snapshot |
| `file.automate.fitImage` | Fit Image… | File > Automate | {"width":px,"height":px,"dontEnlarge":bool=false,"resample":"automatic\|preserveDetails\|bicubicSmoother\|bicubicSharper\|bicubicAutomatic\|bicubic\|nearest\|bilinear\|lanczos"="bicubic"} | needs document; disabled in catalogue snapshot |
| `file.automate.lensCorrection` | Lens Correction… | File > Automate | {"input":folder\|[files],"output":folder,"format":"same\|jpg\|png\|tif\|psd","quality":0..12?, …Filter › Lens Correction params ("profile" defaults to "auto")} |  |
| `file.automate.mergeToHdrPro` | Merge to HDR Pro… | File > Automate | {"paths":[str]\|folder,"useOpenDocuments":bool=false,"exposures":[ev]? (default EXIF, else estimated),"align":bool=true,"removeGhosts":bool=false,"ghostBase":int?,"mode":"32\|16\|8","method":"… |  |
| `file.automate.photomerge` | Photomerge… | File > Automate | {"paths":[str]\|folder,"useOpenDocuments":bool=false,"layout":"auto\|perspective\|cylindrical\|spherical\|collage\|reposition","blend":bool=true,"vignetteRemoval":bool=false,"geometricCorrection"… |  |
| `file.automate.runDroplet` | Run Droplet |  | {"droplet":path,"input":[files or folders],"output":folder? (default: droplet's, else <input folder>/droplet-output)} → {files, errors} (an input whose output name was already written in th… |  |
| `file.close` | Close | File | {"document":index?,"save":"discard\|ask"\|false="discard"} (false means discard; ask refuses to close a changed document in headless playback) | needs document; disabled in catalogue snapshot |
| `file.closeAll` | Close All | File | {} | needs document; disabled in catalogue snapshot |
| `file.closeOthers` | Close Others | File | {"document":index? (the one to keep; default active)} | needs document; disabled in catalogue snapshot |
| `file.export.artboardsToFiles` | Artboards to Files… | File > Export | {"dir":folder,"format":"png\|jpg\|psd\|tiff\|…"="png","prefix":str=document name ("" = none),"artboards":[id]? (default all),"quality":0..12?} → {files} | needs document; disabled in catalogue snapshot |
| `file.export.artboardsToPdf` | Artboards to PDF… | File > Export | {"path":str (.pdf),"artboards":[id]?,"quality":0..12=10} → {path, pages} (one raster page per board) | needs document; disabled in catalogue snapshot |
| `file.export.colorLookupTables` | Color Lookup Tables… | File > Export | {"path":str? (.cube; omit to return the text),"size":2..129=33,"title":str?,"scope":"all\|selected"="all","layers":[id,…]?} (selected layer IDs use original document stacking; masks are spat… | needs document; disabled in catalogue snapshot |
| `file.export.dataSetsAsFiles` | Data Sets as Files… | File > Export | {dir, format?:png, dataSets?[names], naming?:"{name}\|{index}\|{document}"} → {files,count}: apply each data set and export the flattened document; colliding filenames are rejected before wri… | needs document; disabled in catalogue snapshot |
| `file.export.exportPreferences` | Export Preferences… | File > Export | {"quickExportFormat":"png\|jpg\|gif\|webp\|exr"?,"quickExportLocation":"ask\|sameFolder"?,"jpegQuality":1..100?,"webpLossless":bool?,"webpQuality":1..100?,"metadata":"none\|copyright\|all"?,"conve… |  |
| `file.export.layerCompsToFiles` | Layer Comps to Files… | File > Export | {"dir":folder,"format":"png\|jpg\|psd\|tiff\|…"="png","prefix":str=document name,"selectedOnly":bool=false (only the last applied comp),"comps":[id]?,"quality":0..12?} → {files} | needs document; disabled in catalogue snapshot |
| `file.export.layersToFiles` | Layers to Files… | File > Export | {"dir":folder,"format":"png\|jpg\|psd\|tiff\|…"="png","prefix":str=document name,"visibleOnly":bool=true,"trim":bool=false,"quality":0..12?,"jpegFormat":"baseline\|optimized\|progressive"?,"tiffL… | needs document; disabled in catalogue snapshot |
| `file.export.pathsToIllustrator` | Paths to Illustrator… | File > Export | {"path":str? (.ai; omit to return the text),"paths":"all\|work\|<path name>"="all"} → {path, paths} | needs document; disabled in catalogue snapshot |
| `file.export.presets.delete` | Delete Export Preset |  | {"name":str} |  |
| `file.export.presets.get` | Get Export Preset |  | {"name":str} -> {preset} (settings for Export As; nothing is exported) |  |
| `file.export.presets.list` | List Export Presets |  | {} |  |
| `file.export.presets.save` | Save Export Preset |  | {"name":str,"settings":{"format":"png\|jpg\|webp\|tif\|tga\|ico","quality":1..100,"lossless":bool,"transparency":bool,"scale":1..1000,"width":px,"height":px,"lockAspect":bool,"sizing":"scale\|pix… |  |
| `file.export.quickExport` | Quick Export |  | {"path":str? (required unless Export Preferences › Location is "sameFolder" and the document is saved)} → {path, format, bytes, warnings} | needs document; disabled in catalogue snapshot |
| `file.export.renderVideo` | Render Video… | File > Export | {} → {} | needs document; disabled in catalogue snapshot |
| `file.export.saveForWebLegacy` | Save for Web (Legacy)… | File > Export | {"preset":"GIF 128 Dithered\|JPEG High\|PNG-24\|…"?,"format":"gif\|png8\|png24\|jpeg\|wbmp\|webp"="png24","palette":"perceptual\|selective\|adaptive\|restrictive\|exact\|systemMac\|systemWindows\|uniform"… | needs document; disabled in catalogue snapshot |
| `file.exrParts` | EXR Parts Info |  | {"path":str (the EXR file)} |  |
| `file.fileInfo` | File Info… | File | {"title":str?,"author":str?,"authorTitle":str?,"description":str?,"keywords":[str]\|"a; b"?,"copyright":str?,"copyrightStatus":"unknown\|copyrighted\|publicDomain"?,"copyrightUrl":str?} (no ke… | needs document; disabled in catalogue snapshot |
| `file.generate.imageAssets` | Image Assets | File > Generate | {"on":bool? (default: toggle),"dir":folder? (default <document>-assets next to the file)} → {enabled, files, errors}; layers named like "foo.png", "200% foo@2x.png", "48x48 icons/a.png8", "… | needs document; disabled in catalogue snapshot |
| `file.import.notes` | Notes… | File > Import | {"path":".psd\|.psb\|.pcraft with notes"} | needs document; disabled in catalogue snapshot |
| `file.import.variableDataSets` | Variable Data Sets… | File > Import | {path, delimiter?} → {imported}: CSV header = variable names, each row a data set (first column may be the data-set name) | needs document; disabled in catalogue snapshot |
| `file.import.videoFramesToLayers` | Video Frames to Layers… | File > Import | {} → {} | needs document; disabled in catalogue snapshot |
| `file.import.wiaSupport` | WIA Support… | File > Import | {} → {available, devices, note}: acquire from a scanner/camera (Windows only) |  |
| `file.new` | New… | File | {"width":1..300000=1920,"height":1..300000=1080 (pixel counts are rounded),"mode":"rgb\|gray\|grayscale\|cmyk\|lab"="rgb","depth":8\|16\|32=8,"background":"white\|black\|backgroundColor\|transparent… |  |
| `file.newFromClipboard` | New from Clipboard | File | {} (a new document the size of the clipboard image, holding it as one layer) | disabled in catalogue snapshot |
| `file.openAs` | Open As… | File | {"path":str,"as":"psd\|png\|jpg\|tiff\|…"? (decode as this format),"approveHighMemory":bool=false (explicitly approve high memory usage)} |  |
| `file.openExrParts` | Open EXR Parts… | File | {"path":str (the EXR file),"view":"both\|left\|right"="both","part/<name>":bool (import this part as a layer),"group/<name>":bool (import this channel group as a layer),"precomp":bool=false (… |  |
| `file.package` | Package… | File | {"dir":folder,"format":"pcraft\|psd\|psb"="pcraft"} → {folder, document, links, missing} (copies the document and its linked files into <dir>/<name>/, relinked to Links/) | needs document; disabled in catalogue snapshot |
| `file.placeEmbedded` | Place Embedded… | File | {"path":str,"scale":%? (default: fit when larger than the canvas),"fit":bool? (default: Preferences > General > Resize Image During Place),"smartObject":bool? (default: Preferences > Genera… | needs document; disabled in catalogue snapshot |
| `file.placeLinked` | Place Linked… | File | {"path":str,"scale":%?,"fit":bool? (default: Preferences > General > Resize Image During Place),"center":[x,y]?,"approveHighMemory":bool=false (explicitly approve high memory usage)} | needs document; disabled in catalogue snapshot |
| `file.print` | Print… | File | {"printerSettings":hex? (Windows driver settings),"printer":name? (default printer),"copies":1..999=1,"paper":"letter\|legal\|tabloid\|a3\|a4\|a5\|4x6\|5x7"\|[w,h] pt="letter","orientation":"portra… | needs document; disabled in catalogue snapshot |
| `file.print.page` | Printer Page |  | {"printer":name? (default printer),"printerSettings":hex?,"orientation":"portrait\|landscape"? (turn the settings, or the printer's own, that way)} → {printer, paper: [w,h] pt, printable: [x… |  |
| `file.print.printers` | Printers |  | {} → {supported, printers: [{name, default}]} (supported: Windows; elsewhere Print spools with lp) |  |
| `file.printOneCopy` | Print One Copy | File | {} (the last Print settings, one copy; any Print key overrides) | needs document; disabled in catalogue snapshot |
| `file.printers` | Printers |  | {} → {printers:[{name, default}], default:name\|null} (the system spooler's printers; a name is Print's "printer") |  |
| `file.revealInFinder` | Reveal in Finder |  | {"document":index? (default active),"dryRun":bool=false} | needs document; disabled in catalogue snapshot |
| `file.revert` | Revert | File | {} (reloads the saved file as one undoable step) | needs document; disabled in catalogue snapshot |
| `file.saveACopy` | Save a Copy… | File | {"path":str (format from the extension),"quality":0..12? (JPEG),"jpegFormat":"baseline\|optimized\|progressive"? (JPEG; default baseline),"layers":bool=true,"overwrite":bool=false (replace th… | needs document; disabled in catalogue snapshot |
| `file.scripts.browse` | Browse… | File > Scripts | {"path":script file \| "script":text \| "steps":[[id,params]…]} (JSON action, or one `command.id {json}` per line) → {steps, ok, results} |  |
| `file.scripts.deleteAllEmptyLayers` | Delete All Empty Layers | File > Scripts | {} | needs document; disabled in catalogue snapshot |
| `file.scripts.flattenAllLayerEffects` | Flatten All Layer Effects | File > Scripts | {} | needs document; disabled in catalogue snapshot |
| `file.scripts.flattenAllMasks` | Flatten All Masks | File > Scripts | {} (pixel layers; masks on other layer kinds are left) | needs document; disabled in catalogue snapshot |
| `file.scripts.imageProcessor` | Image Processor… | File > Scripts | {"input":folder\|[paths],"includeSubfolders":bool=false (a folder input also takes the images in its subfolders, up to 32 levels and 100000 files; each result keeps its subfolder under outpu… |  |
| `file.scripts.loadFilesIntoStack` | Load Files into Stack… | File > Scripts | {"paths":[str]\|folder,"align":bool=false (Auto-Align Layers on them first),"createSmartObject":bool=false} → new document with one layer per file (inside one smart object with createSmartOb… |  |
| `file.scripts.scriptEventsManager` | Script Events Manager… | File > Scripts | {"enabled":bool?,"add":{"event":"startApplication\|newDocument\|openDocument\|saveDocument\|closeDocument\|print\|export\|everything","script":path?\|"steps":[…]?,"name":str?}?,"remove":index?,"rem… |  |
| `file.scripts.statistics` | Statistics… | File > Scripts | {"mode":"mean\|median\|maximum\|minimum\|range\|summation\|variance\|standardDeviation\|skewness\|kurtosis\|entropy"="median","input":folder\|[paths],"align":bool=false (Auto-Align first)} → new docum… |  |

## `history` (14)



| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `history.clear` | Clear History |  | {} → {states,current,label}: removes every History state but the current one without changing the image; Edit › Undo restores them | needs document; disabled in catalogue snapshot |
| `history.deleteSnapshot` | Delete Snapshot |  | {"snapshot":id} → {snapshot,snapshots}: the document and its history are unchanged | needs document; disabled in catalogue snapshot |
| `history.deleteState` | Delete State |  | {"state":index?} (History entry, 0 = oldest; default the current state) → {states,current}: removes the state and every later one (with Allow Non-Linear History only that state, a later dim… | disabled in catalogue snapshot |
| `history.newDocument` | New Document from State |  | {"state":index?,"name":str?} (History entry, 0 = oldest; default the current state) → {document,name} | needs document; disabled in catalogue snapshot |
| `history.newSnapshot` | New Snapshot |  | {"name":str?="Snapshot N","from":"fullDocument"\|"mergedLayers"\|"currentLayer"="fullDocument","replaceExisting":bool=false (drop snapshots of the same name first)} → {snapshot,name}: a named… | needs document; disabled in catalogue snapshot |
| `history.options` | History Options… |  | {"allowNonLinearHistory":bool?,"makeLayerVisibilityChangesUndoable":bool?} → both values (no params: report them). Allow Non-Linear History: an edit after stepping back keeps the later stat… |  |
| `history.redo` | Redo |  | {} (the same action as `edit.redo`) | disabled in catalogue snapshot |
| `history.renameSnapshot` | Rename Snapshot |  | {"snapshot":id,"name":str} → {snapshot,name} | needs document; disabled in catalogue snapshot |
| `history.selectSnapshot` | Select Snapshot |  | {"snapshot":id} → {snapshot,name}: the document returns to the snapshot as a new history state named after it | needs document; disabled in catalogue snapshot |
| `history.selectState` | Select History State |  | {"state":index} (History entry as the panel lists them: 0 = oldest, then the current state, then the redo states) → {state,changed,current?}: returns the document to that state in one step;… | needs document; disabled in catalogue snapshot |
| `history.setSource` | Set History Brush Source |  | {"state":row} \| {"snapshot":id} (state: a History panel row, 0 = oldest state, then the current one, then the greyed redo states; snapshot: a history.newSnapshot id) → {state,label} \| {snap… | needs document; disabled in catalogue snapshot |
| `history.stepBackward` | Step Backward |  | {} → {states,current,label}: makes the previous History state current (Err when there is none) | needs document; disabled in catalogue snapshot |
| `history.stepForward` | Step Forward |  | {} → {states,current,label}: makes the next History state current (Err when there is none) | needs document; disabled in catalogue snapshot |
| `history.undo` | Undo |  | {} (the same action as `edit.undo`) | disabled in catalogue snapshot |

## `layer` (224)

Layer commands manage structure and stacking. `layer.move`/`layer.collectInNew` move selected art; `layer.merge`/`flatten` are destructive. Lock/hide commands protect finished layers.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `layer.addAboveToSelection` | Add Layer Above to Selection |  | {} (follows the Layers panel's rows; collapsed groups are one row) | needs document; disabled in catalogue snapshot |
| `layer.addBelowToSelection` | Add Layer Below to Selection |  | {} (follows the Layers panel's rows; collapsed groups are one row) | needs document; disabled in catalogue snapshot |
| `layer.align.bottomEdges` | Bottom Edges | Layer > Align | {"to":"auto\|layers\|selection\|canvas"="auto"} (auto: the active selection's bounds when there is one, however many layers are selected; else one layer aligns to the canvas and several to the… | needs document; disabled in catalogue snapshot |
| `layer.align.horizontalCenters` | Horizontal Centers | Layer > Align | {"to":"auto\|layers\|selection\|canvas"="auto"} (auto: the active selection's bounds when there is one, however many layers are selected; else one layer aligns to the canvas and several to the… | needs document; disabled in catalogue snapshot |
| `layer.align.leftEdges` | Left Edges | Layer > Align | {"to":"auto\|layers\|selection\|canvas"="auto"} (auto: the active selection's bounds when there is one, however many layers are selected; else one layer aligns to the canvas and several to the… | needs document; disabled in catalogue snapshot |
| `layer.align.rightEdges` | Right Edges | Layer > Align | {"to":"auto\|layers\|selection\|canvas"="auto"} (auto: the active selection's bounds when there is one, however many layers are selected; else one layer aligns to the canvas and several to the… | needs document; disabled in catalogue snapshot |
| `layer.align.topEdges` | Top Edges | Layer > Align | {"to":"auto\|layers\|selection\|canvas"="auto"} (auto: the active selection's bounds when there is one, however many layers are selected; else one layer aligns to the canvas and several to the… | needs document; disabled in catalogue snapshot |
| `layer.align.verticalCenters` | Vertical Centers | Layer > Align | {"to":"auto\|layers\|selection\|canvas"="auto"} (auto: the active selection's bounds when there is one, however many layers are selected; else one layer aligns to the canvas and several to the… | needs document; disabled in catalogue snapshot |
| `layer.arrange.bringForward` | Bring Forward | Layer > Arrange | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.arrange.bringToFront` | Bring to Front | Layer > Arrange | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.arrange.reverse` | Reverse | Layer > Arrange | {} | disabled in catalogue snapshot |
| `layer.arrange.sendBackward` | Send Backward | Layer > Arrange | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.arrange.sendToBack` | Send to Back | Layer > Arrange | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.artboard.addBeside` | Add Artboard Beside |  | {"layer":id? (default: the active artboard),"side":"left\|right\|top\|bottom"="right","duplicate":bool=false (copy the board with its contents instead of an empty one)} → {layer, rect} (the Ar… | disabled in catalogue snapshot |
| `layer.artboard.set` | Edit Artboard |  | {"layer":id? (default: the active artboard),"x","y","width","height"?\|"rect":[x,y,w,h]?,"preset":str?,"background":"white\|black\|transparent\|custom"?,"color":…?,"name":str?,"moveContents":bo… | disabled in catalogue snapshot |
| `layer.combineShapes.excludeOverlappingShapes` | Exclude Overlapping Shapes |  | {"layer":id?,"subpath":index? (default all but the first)} (no layer/subpath and two or more shape layers selected: merges them into the top-most, whose components above the bottom layer's … | needs document; disabled in catalogue snapshot |
| `layer.combineShapes.intersectShapeAreas` | Intersect Shape Areas |  | {"layer":id?,"subpath":index? (default all but the first)} (no layer/subpath and two or more shape layers selected: merges them into the top-most, whose components above the bottom layer's … | needs document; disabled in catalogue snapshot |
| `layer.combineShapes.mergeShapeComponents` | Merge Shape Components |  | {"layer":id?,"tolerance":px=0.1} (bakes the path operations into plain combined outlines, traced from the exact coverage; no layer and several shape layers selected: merges them into the to… | needs document; disabled in catalogue snapshot |
| `layer.combineShapes.subtractFrontShape` | Subtract Front Shape |  | {"layer":id?,"subpath":index? (default all but the first)} (no layer/subpath and two or more shape layers selected: merges them into the top-most, whose components above the bottom layer's … | needs document; disabled in catalogue snapshot |
| `layer.combineShapes.unite` | Unite Shapes |  | {"layer":id?,"subpath":index? (default all but the first)} (no layer/subpath and two or more shape layers selected: merges them into the top-most, whose components above the bottom layer's … | needs document; disabled in catalogue snapshot |
| `layer.copyToDocument` | Copy Layers to Document |  | {"document":index (destination),"layers":[id,…]?=the source's selected layers,"source":index?=active,"center":bool=false (centre on the destination's canvas),"at":[x,y]? (centre the copies … | needs document; disabled in catalogue snapshot |
| `layer.createClippingMask` | Create Clipping Mask | Layer | {"layer":id?} (no layer: every selected layer but the lowest clips to the layer below it) | needs document; disabled in catalogue snapshot |
| `layer.delete` | Delete Layer | Layer > Delete | {"layer":id?} (no layer: every selected layer) | needs document; disabled in catalogue snapshot |
| `layer.delete.hiddenLayers` | Hidden Layers | Layer > Delete | {} | needs document; disabled in catalogue snapshot |
| `layer.distribute.bottomEdges` | Bottom Edges | Layer > Distribute | {} | disabled in catalogue snapshot |
| `layer.distribute.horizontalCenters` | Horizontal Centers | Layer > Distribute | {} | disabled in catalogue snapshot |
| `layer.distribute.horizontally` | Horizontally | Layer > Distribute | {} (equal horizontal gaps) | disabled in catalogue snapshot |
| `layer.distribute.leftEdges` | Left Edges | Layer > Distribute | {} | disabled in catalogue snapshot |
| `layer.distribute.rightEdges` | Right Edges | Layer > Distribute | {} | disabled in catalogue snapshot |
| `layer.distribute.topEdges` | Top Edges | Layer > Distribute | {} | disabled in catalogue snapshot |
| `layer.distribute.verticalCenters` | Vertical Centers | Layer > Distribute | {} | disabled in catalogue snapshot |
| `layer.distribute.vertically` | Vertically | Layer > Distribute | {} (equal vertical gaps) | disabled in catalogue snapshot |
| `layer.duplicate` | Duplicate Layer… | Layer | {"layer":id?,"inPlace":bool=false (artboards: keep the copy on the original instead of beside it),"name":str? (one layer: the copy's name),"document":index\|"new"=same document (Photoshop's … | needs document; disabled in catalogue snapshot |
| `layer.exportAs` | Export As… | Layer | {"layer":id?,"path":text,"scale":1..1000=100,"resample":"bicubicAutomatic\|bicubic\|bicubicSmoother\|bicubicSharper\|bilinear\|nearest"="bicubicAutomatic"} (format from the path's extension; the… | needs document; disabled in catalogue snapshot |
| `layer.fill.pattern.set` | Pattern Fill… |  | {"layer":id\|name? (default active; a Pattern Fill layer),"document":id? (reject a stale dialog),"pattern":id\|name?,"patternName":name? (then `pattern` is an id; the name is used when no pat… | needs document; disabled in catalogue snapshot |
| `layer.fill.solidColor.set` | Solid Color… |  | {"layer":id\|name? (default active),"document":id? (reject a stale dialog),"color":"#rrggbb"\|"#rrggbbaa"\|[r,g,b,a?]\|{mode,c:[f32;4],alpha:f32},"cmyk":[c,m,y,k]? (inks 0..1 the colour was pic… | needs document; disabled in catalogue snapshot |
| `layer.flattenImage` | Flatten Image | Layer | {} | needs document; disabled in catalogue snapshot |
| `layer.groupLayers` | Group Layers | Layer | {"layer":id?,"name":text?,"color":"none\|red\|orange\|yellow\|green\|seafoam\|blue\|indigo\|magenta\|fuchsia\|violet\|gray"="none","mode":str="passThrough" (blend mode),"opacity":0..100=100 (percent)}… | needs document; disabled in catalogue snapshot |
| `layer.hideLayers` | Hide Layers | Layer | {"layer":id?} (shows them instead when every targeted layer is already hidden, so ⌘, toggles) | needs document; disabled in catalogue snapshot |
| `layer.layerContentOptions` | Layer Content Options… | Layer | {} | needs document; disabled in catalogue snapshot |
| `layer.layerMask.apply` | Apply | Layer > Layer Mask | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.layerMask.delete` | Delete | Layer > Layer Mask | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.layerMask.edit` | Edit Layer Mask |  | {"layer":id? (default active),"document":id? (reject a stale dialog),"density":0..100?,"feather":0..1000? (pixels)} → {layer,density,feather}; at least one property required; mask pixels ar… | needs document; disabled in catalogue snapshot |
| `layer.layerMask.enabled` | Disable Layer Mask | Layer > Layer Mask | {"layer":id?,"enabled":bool? (default: toggle)} | needs document; disabled in catalogue snapshot |
| `layer.layerMask.fromTransparency` | From Transparency | Layer > Layer Mask | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.layerMask.hideAll` | Hide All | Layer > Layer Mask | {"layer":id?} (no layer: every selected layer that can take a mask) | needs document; disabled in catalogue snapshot |
| `layer.layerMask.hideSelection` | Hide Selection | Layer > Layer Mask | {"layer":id?} (no layer: every selected layer that can take a mask) | needs document; disabled in catalogue snapshot |
| `layer.layerMask.linked` | Unlink Layer Mask | Layer > Layer Mask | {"layer":id?,"linked":bool? (default: toggle)} | needs document; disabled in catalogue snapshot |
| `layer.layerMask.revealAll` | Reveal All | Layer > Layer Mask | {"layer":id?} (no layer: every selected layer that can take a mask) | needs document; disabled in catalogue snapshot |
| `layer.layerMask.revealSelection` | Reveal Selection | Layer > Layer Mask | {"layer":id?} (no layer: every selected layer that can take a mask) | disabled in catalogue snapshot |
| `layer.layerStyle.bevelEmboss` | Bevel & Emboss… | Layer > Layer Style | {"style":"inner\|outer\|emboss\|pillow\|stroke","technique":"smooth\|chiselHard\|chiselSoft","contour":bool,"contourName":name\|curve,"contourRange":1..100=50,"contourAntiAlias":bool,"glossContour… | needs document; disabled in catalogue snapshot |
| `layer.layerStyle.blendingOptions` | Blending Options… | Layer > Layer Style | {"layer":id?,"blend":"normal\|multiply\|…"?,"opacity":0..100?,"fillOpacity":0..100?,"blendIf":{"channel":"gray\|red\|green\|blue\|cyan\|…"\|index="gray","thisLayer":[black,white]\|[blackLo,blackHi,w… | needs document; disabled in catalogue snapshot |
| `layer.layerStyle.clear` | Clear Layer Style | Layer > Layer Style | {"layer":id? (no layer: every selected layer that has a style),"effect":index? (only that effect of "layer", as an effect row dropped on the Layers panel's Delete button)} | needs document; disabled in catalogue snapshot |
| `layer.layerStyle.colorOverlay` | Color Overlay… | Layer > Layer Style | {"color":"#rrggbb","opacity":0..100=100,"blend":str,"add":bool} | needs document; disabled in catalogue snapshot |
| `layer.layerStyle.contours.delete` | Delete Contour |  | {"name":str} → {deleted, count} |  |
| `layer.layerStyle.contours.list` | List User Contours |  | {} → {count, contours:[{name, contour: curve object usable as any `contour` param}]} |  |
| `layer.layerStyle.contours.load` | Load Contours… |  | {"path":".shc file"?,"data":base64 bytes?,"mode":"append"\|"replace"="append"} → {loaded, count, skipped} (picker menu: Load Contours… / Replace Contours…) |  |
| `layer.layerStyle.contours.new` | New Contour… |  | {"contour":name\|{"name":str,"points":[[in 0..1,out 0..1],…],"corners":[bool,…]},"name":str?="Contour N"} → {name (made unique, never a standard contour's name), contour, count} (Contour Edi… |  |
| `layer.layerStyle.contours.save` | Save Contours… |  | {"path":".shc file"?,"names":[str]?=all} → {count, bytes, path \| data (base64 when no path)} |  |
| `layer.layerStyle.copyLayerStyle` | Copy Layer Style | Layer > Layer Style | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.layerStyle.createLayer` | Create Layer | Layer > Layer Style | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.layerStyle.defaultFor` | Layer Style Default |  | {"kind":str} → {"params":{…},"user":bool} (the saved user default, else the factory defaults) |  |
| `layer.layerStyle.dropShadow` | Drop Shadow… | Layer > Layer Style | {"color":"#rrggbb","opacity":0..100=75,"blend":str="multiply","angle":deg=120,"useGlobalLight":bool,"distance":px=5,"spread":0..100,"size":px=5,"contour":"Linear\|Cone\|Cone - Inverted\|Cove -… | needs document; disabled in catalogue snapshot |
| `layer.layerStyle.globalLight` | Global Light… | Layer > Layer Style | {"angle":-180..180=120,"altitude":0..90=30} | needs document; disabled in catalogue snapshot |
| `layer.layerStyle.gradientOverlay` | Gradient Overlay… | Layer > Layer Style | {"from":"#rrggbb","to":"#rrggbb","stops":[[0..1,"#rrggbb"],.]? (2..256 source stops),"opacityStops":[[0..1,0..100],.]?,"method":"classic\|perceptual\|linear\|smooth"? (Photoshop's interpolatio… | needs document; disabled in catalogue snapshot |
| `layer.layerStyle.hideAllEffects` | Hide All Effects | Layer > Layer Style | {} | needs document; disabled in catalogue snapshot |
| `layer.layerStyle.innerGlow` | Inner Glow… | Layer > Layer Style | {"color":"#rrggbb","opacity":0..100=75,"blend":str="screen","technique":"softer\|precise","source":"edge\|center","choke":0..100,"size":px,"range":1..100=50,"contour":name\|curve,"antiAlias":b… | needs document; disabled in catalogue snapshot |
| `layer.layerStyle.innerShadow` | Inner Shadow… | Layer > Layer Style | {"color":"#rrggbb","opacity":0..100=75,"blend":str,"angle":deg,"distance":px,"choke":0..100,"size":px,"contour":name\|curve,"antiAlias":bool,"noise":0..100,"add":bool} | needs document; disabled in catalogue snapshot |
| `layer.layerStyle.makeDefault` | Make Layer Style Default |  | {"kind":"stroke\|dropShadow\|innerShadow\|outerGlow\|innerGlow\|colorOverlay\|gradientOverlay\|patternOverlay\|satin\|bevelEmboss","params":{…param set…}} (stores the user default the Layer Style di… |  |
| `layer.layerStyle.outerGlow` | Outer Glow… | Layer > Layer Style | {"color":"#rrggbb","opacity":0..100=75,"blend":str="screen","technique":"softer\|precise","spread":0..100,"size":px,"range":1..100=50,"contour":name\|curve,"antiAlias":bool,"noise":0..100,"ad… | needs document; disabled in catalogue snapshot |
| `layer.layerStyle.pasteLayerStyle` | Paste Layer Style | Layer > Layer Style | {"layer":id?,"allowGroups":bool=true} (no layer: every selected layer but the Background; false skips groups, refusing if none remain) | needs document; disabled in catalogue snapshot |
| `layer.layerStyle.patternOverlay` | Pattern Overlay… | Layer > Layer Style | {"pattern":id\|name?=first library pattern,"opacity":0..100=100,"blend":str,"scale":1..1000=100,"angle":deg=0,"link":bool=true,"phaseX":px,"phaseY":px,"add":bool} | needs document; disabled in catalogue snapshot |
| `layer.layerStyle.replace` | Edit Layer Style |  | {"layer":id,"effects":[{"kind":"dropShadow\|innerShadow\|outerGlow\|innerGlow\|stroke\|colorOverlay\|gradientOverlay\|patternOverlay\|satin\|bevelEmboss","params":{…layer.layerStyle.<kind> params…},… | needs document; disabled in catalogue snapshot |
| `layer.layerStyle.satin` | Satin… | Layer > Layer Style | {"color":"#rrggbb","opacity":0..100=50,"blend":str,"angle":deg,"distance":px,"size":px,"contour":name\|curve,"antiAlias":bool=true,"invert":bool,"add":bool} | needs document; disabled in catalogue snapshot |
| `layer.layerStyle.scaleEffects` | Scale Effects… | Layer > Layer Style | {"scale":1..1000=100} | needs document; disabled in catalogue snapshot |
| `layer.layerStyle.showAllEffects` | Show All Effects |  | {} | needs document; disabled in catalogue snapshot |
| `layer.layerStyle.stroke` | Stroke… | Layer > Layer Style | {"size":px=1,"position":"inside\|outside\|center","color":"#rrggbb","from":"#rrggbb","to":"#rrggbb","method":"classic\|perceptual\|linear\|smooth"?,"smoothness":0..100=100,"style":str,"angle":de… | needs document; disabled in catalogue snapshot |
| `layer.layerStyle.transferEffects` | Move Layer Effects |  | {"from":id,"to":id,"effect":index? (default: all effects),"copy":bool=false} | needs document; disabled in catalogue snapshot |
| `layer.linkLayers` | Link Layers | Layer | {"linked":bool?} (omitted: toggle; explicit true links, false unlinks) | needs document; disabled in catalogue snapshot |
| `layer.list` | List Layers |  | {"document":index?,"flat":bool=false} → {"layers":[{"id","name","kind","visible","bounds":[x,y,w,h]\|null,"selected","active","children"?}],"activeLayer":id?} (top-down; groups list their "c… | needs document; disabled in catalogue snapshot |
| `layer.lockLayers` | Lock Layers… | Layer | {"transparency":bool?,"pixels":bool?,"position":bool?,"artboard":bool?,"all":bool?} (none given: toggle lock all) | disabled in catalogue snapshot |
| `layer.maskAllObjects` | Mask All Objects | Layer | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.matting.colorDecontaminate` | Color Decontaminate… | Layer > Matting | {"amount":0..100=100,"radius":1..100=4} | needs document; disabled in catalogue snapshot |
| `layer.matting.defringe` | Defringe… | Layer > Matting | {"width":1..200=1} | needs document; disabled in catalogue snapshot |
| `layer.matting.removeBlackMatte` | Remove Black Matte | Layer > Matting | {} | needs document; disabled in catalogue snapshot |
| `layer.matting.removeWhiteMatte` | Remove White Matte | Layer > Matting | {} | needs document; disabled in catalogue snapshot |
| `layer.mergeDown` | Merge Down | Layer | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.mergeGroup` | Merge Group | Layer | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.mergeLayers` | Merge Layers | Layer | {} (one layer selected: Merge Down) | disabled in catalogue snapshot |
| `layer.mergeVisible` | Merge Visible | Layer | {} | needs document; disabled in catalogue snapshot |
| `layer.moveTo` | Reorder Layer |  | {"layer":id\|{"index":uint}\|{"ordinal":"Trgt\|Frwr\|Bckw\|Frnt\|Back"}?\| "layers":[id,…]?, "target":id\|name\|{"index":uint},"targetOccurrence":n? (which of several layers named `target`, in docum… | needs document; disabled in catalogue snapshot |
| `layer.new.artboard` | Artboard… | Layer > New | {"rect":[x,y,w,h]? \| "x","y","width","height"? (default: canvas size, right of the last board),"preset":"iPhone 14\|Web 1920\|A4\|…"?,"name":str?,"background":"white\|black\|transparent\|custom"=… | needs document; disabled in catalogue snapshot |
| `layer.new.artboardFromGroup` | Artboard from Group… | Layer > New | {"layer":id? (a top-level group; default active),"background":…?,"color":[r,g,b]\|"#rrggbb"?,"preset":str? (tag only; does not resize),"guideIDs":[int]? (ignored recording metadata),"changeB… | needs document; disabled in catalogue snapshot |
| `layer.new.artboardFromLayers` | Artboard from Layers… | Layer > New | {"name":text,"background":"white\|black\|transparent\|custom"="white","color":color,"width":px=0,"height":px=0} (the selected layers; name: empty gives Artboard N; color: for custom; width, he… | needs document; disabled in catalogue snapshot |
| `layer.new.backgroundFromLayer` | Background From Layer | Layer > New | {"layer":id?} (the active layer by default; transparent pixels take the background colour and the layer drops to the bottom as the locked Background) | needs document; disabled in catalogue snapshot |
| `layer.new.frame` | New Frame |  | {"x":i32,"y":i32,"width":u32,"height":u32,"shape":"rectangle\|ellipse"="rectangle","layer":id?,"name":str?} → {layer, frame:[x,y,w,h], shape}: Frame tool; a group clipped to the shape, holdi… | needs document; disabled in catalogue snapshot |
| `layer.new.frameFromLayers` | Frame from Layers | Layer > New | {"name":str?} → {layer, frame:[x,y,w,h]}: groups the selected layers and clips them to a frame rect | needs document; disabled in catalogue snapshot |
| `layer.new.group` | Group… | Layer > New | {"name":text?,"color":"none\|red\|orange\|yellow\|green\|seafoam\|blue\|indigo\|magenta\|fuchsia\|violet\|gray"="none","mode":str="passThrough" (blend mode),"opacity":0..100=100 (percent),"position":"… | needs document; disabled in catalogue snapshot |
| `layer.new.groupFromLayers` | Group from Layers… | Layer > New | {"layer":id?,"name":text?,"color":"none\|red\|orange\|yellow\|green\|seafoam\|blue\|indigo\|magenta\|fuchsia\|violet\|gray"="none","mode":str="passThrough" (blend mode),"opacity":0..100=100 (percent)}… | disabled in catalogue snapshot |
| `layer.new.layer` | Layer… | Layer > New | {"name":str?,"clipToPrevious":bool=false (Use Previous Layer to Create Clipping Mask; inside a clip group the layer joins it anyway),"color":"none\|red\|orange\|yellow\|green\|seafoam\|blue\|indig… | needs document; disabled in catalogue snapshot |
| `layer.new.layerFromBackground` | Layer From Background… | Layer > New | {"ifPresent":bool=false (true: a document without a Background is left as it is, as a Photoshop action's step needs on an image that opened as a normal layer),"select":bool=true (false: the… | needs document; disabled in catalogue snapshot |
| `layer.new.layerViaCopy` | Layer via Copy | Layer > New | {} | needs document; disabled in catalogue snapshot |
| `layer.new.layerViaCut` | Layer via Cut | Layer > New | {} | needs document; disabled in catalogue snapshot |
| `layer.newAdjustmentLayer.blackWhite` | Black & White… | Layer > New Adjustment Layer | {"reds":-200..300=40,"yellows":-200..300=60,"greens":-200..300=40,"cyans":-200..300=60,"blues":-200..300=20,"magentas":-200..300=80,"tint":bool=false,"tintColor":"#rrggbb"} + {"path":"work"… | needs document; disabled in catalogue snapshot |
| `layer.newAdjustmentLayer.brightnessContrast` | Brightness/Contrast… | Layer > New Adjustment Layer | {"brightness":-150..150=0,"contrast":-50..100=0,"legacy":bool=false} + {"path":"work"\|saved path name\|{…path}? (the active path: becomes the vector mask; else the selection is the layer mas… | needs document; disabled in catalogue snapshot |
| `layer.newAdjustmentLayer.channelMixer` | Channel Mixer… | Layer > New Adjustment Layer | {"red":json,"green":json,"blue":json,"gray":json,"monochrome":bool=false} (per output channel [red %, green %, blue %, constant %] in -200..200; gray = the monochrome mix) + {"path":"work"\|… | needs document; disabled in catalogue snapshot |
| `layer.newAdjustmentLayer.colorBalance` | Color Balance… | Layer > New Adjustment Layer | {"shadows":json,"midtones":json,"highlights":json,"preserveLuminosity":bool=true} (each tone [cyan-red, magenta-green, yellow-blue] in -100..100) + {"path":"work"\|saved path name\|{…path}? (… | needs document; disabled in catalogue snapshot |
| `layer.newAdjustmentLayer.colorLookup` | Color Lookup… | Layer > New Adjustment Layer | {"lut":"none\|warm\|cool\|tealOrange\|bleachBypass\|fadedFilm\|dayForNight\|monoContrast\|crossProcess"="none","file":text,"interpolation":"trilinear\|tetrahedral"="trilinear","dither":bool=false,"d… | needs document; disabled in catalogue snapshot |
| `layer.newAdjustmentLayer.curves` | Curves… | Layer > New Adjustment Layer | {"points":json,"red":json,"green":json,"blue":json,"pencil":bool=false,"smooth":0..10=0,"eyedropper":json} (curves as [[in,out],…] in 0..255, 2..19 points: points = composite; red/green/blu… | needs document; disabled in catalogue snapshot |
| `layer.newAdjustmentLayer.exposure` | Exposure… | Layer > New Adjustment Layer | {"exposure":-20..20=0,"offset":-0.5..0.5=0,"gamma":0.01..9.99=1} + {"path":"work"\|saved path name\|{…path}? (the active path: becomes the vector mask; else the selection is the layer mask, o… | needs document; disabled in catalogue snapshot |
| `layer.newAdjustmentLayer.gradientMap` | Gradient Map… | Layer > New Adjustment Layer | {"stops":json,"reverse":bool=false,"dither":bool=false} (stops [[location 0..1, "#rrggbb"], …], 2..64) + {"path":"work"\|saved path name\|{…path}? (the active path: becomes the vector mask; e… | needs document; disabled in catalogue snapshot |
| `layer.newAdjustmentLayer.hueSaturation` | Hue/Saturation… | Layer > New Adjustment Layer | {"hue":-180..180=0,"saturation":-100..100=0,"lightness":-100..100=0,"colorize":bool=false,"reds":json,"yellows":json,"greens":json,"cyans":json,"blues":json,"magentas":json} (per range {"hu… | needs document; disabled in catalogue snapshot |
| `layer.newAdjustmentLayer.invert` | Invert | Layer > New Adjustment Layer | {} + {"path":"work"\|saved path name\|{…path}? (the active path: becomes the vector mask; else the selection is the layer mask, or white with no selection),"opacity":0..1=1} | needs document; disabled in catalogue snapshot |
| `layer.newAdjustmentLayer.levels` | Levels… | Layer > New Adjustment Layer | {"inBlack":0..253=0,"gamma":0.01..9.99=1,"inWhite":2..255=255,"outBlack":0..255=0,"outWhite":0..255=255,"red":json,"green":json,"blue":json,"eyedropper":json} (top level = composite; per ch… | needs document; disabled in catalogue snapshot |
| `layer.newAdjustmentLayer.photoFilter` | Photo Filter… | Layer > New Adjustment Layer | {"filter":"warming85\|warmingLBA\|warming81\|cooling80\|coolingLBB\|cooling82\|red\|orange\|yellow\|green\|cyan\|blue\|violet\|magenta\|sepia\|deepRed\|deepBlue\|deepEmerald\|deepYellow\|underwater","color":"… | needs document; disabled in catalogue snapshot |
| `layer.newAdjustmentLayer.posterize` | Posterize… | Layer > New Adjustment Layer | {"levels":2..255=4} + {"path":"work"\|saved path name\|{…path}? (the active path: becomes the vector mask; else the selection is the layer mask, or white with no selection),"opacity":0..1=1} | needs document; disabled in catalogue snapshot |
| `layer.newAdjustmentLayer.selectiveColor` | Selective Color… | Layer > New Adjustment Layer | {"method":"relative\|absolute"="relative","colors":"reds\|yellows\|greens\|cyans\|blues\|magentas\|whites\|neutrals\|blacks"="reds","cyan":-100..100=0,"magenta":-100..100=0,"yellow":-100..100=0,"bla… | needs document; disabled in catalogue snapshot |
| `layer.newAdjustmentLayer.threshold` | Threshold… | Layer > New Adjustment Layer | {"level":1..255=128} + {"path":"work"\|saved path name\|{…path}? (the active path: becomes the vector mask; else the selection is the layer mask, or white with no selection),"opacity":0..1=1} | needs document; disabled in catalogue snapshot |
| `layer.newAdjustmentLayer.vibrance` | Vibrance… | Layer > New Adjustment Layer | {"vibrance":-100..100=0,"saturation":-100..100=0} + {"path":"work"\|saved path name\|{…path}? (the active path: becomes the vector mask; else the selection is the layer mask, or white with no… | needs document; disabled in catalogue snapshot |
| `layer.newFillLayer.gradient` | Gradient… | Layer > New Fill Layer | {"from":"#rrggbb","to":"#rrggbb","angle":deg=90,"style":"linear\|radial\|angle\|reflected\|diamond","reverse":bool,"path":"work"\|saved path name\|{…path}? (the active path: becomes the vector ma… | needs document; disabled in catalogue snapshot |
| `layer.newFillLayer.pattern` | Pattern… | Layer > New Fill Layer | {"pattern":id\|name?=first library pattern,"patternName":name? (then `pattern` is an id; the name is used when no pattern has that id),"scale":1..1000=100,"angle":deg=0,"link":bool=true,"pha… | needs document; disabled in catalogue snapshot |
| `layer.newFillLayer.solidColor` | Solid Color… | Layer > New Fill Layer | {"color":"#rrggbb"=foreground,"cmyk":[c,m,y,k]? (inks 0..1 the colour was picked as: a CMYK document's fill holds exactly these; default the foreground's CMYK pick),"path":"work"\|saved path… | needs document; disabled in catalogue snapshot |
| `layer.newLayerBasedSlice` | New Layer Based Slice | Layer | {"layer":id?,"name":str?,"url":str?,"alt":str?} (follows the layer's bounds with effects) → {slice, rect} | needs document; disabled in catalogue snapshot |
| `layer.pickAt` | Auto-Select Layer |  | {"x":px,"y":px,"target":"layer\|group"="layer","select":bool=true,"mode":"replace\|toggle\|add"="replace","list":bool=false (return visible layers at the point, including text bounds, topmost … | needs document; disabled in catalogue snapshot |
| `layer.quickExportAsPng` | Quick Export as PNG | Layer | {"layer":id?,"path":text} | needs document; disabled in catalogue snapshot |
| `layer.rasterize.allLayers` | All Layers | Layer > Rasterize | {} | needs document; disabled in catalogue snapshot |
| `layer.rasterize.fillContent` | Fill Content | Layer > Rasterize | {"layer":id?} (no layer: every selected layer it applies to) | needs document; disabled in catalogue snapshot |
| `layer.rasterize.layer` | Layer | Layer > Rasterize | {"layer":id?} (no layer: every selected layer it applies to) | needs document; disabled in catalogue snapshot |
| `layer.rasterize.layerStyle` | Layer Style | Layer > Rasterize | {"layer":id?} (no layer: every selected layer with effects; bakes the effects, fill opacity and masks into the pixels) | needs document; disabled in catalogue snapshot |
| `layer.rasterize.shape` | Rasterize Shape |  | {"layer":id?} (no layer: every selected shape layer) | needs document; disabled in catalogue snapshot |
| `layer.rasterize.smartObject` | Smart Object | Layer > Rasterize | {"layer":id?} (no layer: every selected layer it applies to) | needs document; disabled in catalogue snapshot |
| `layer.rasterize.type` | Type | Layer > Rasterize | {"layer":id?} (no layer: every selected layer it applies to) | needs document; disabled in catalogue snapshot |
| `layer.rasterize.vectorMask` | Rasterize Vector Mask |  | {"layer":id?} (multiplied into the layer mask) | needs document; disabled in catalogue snapshot |
| `layer.rasterize.video` | Video | Layer > Rasterize | {} → {} | needs document; disabled in catalogue snapshot |
| `layer.releaseClippingMask` | Release Clipping Mask | Layer | {"layer":id?} (no layer: every selected layer) | needs document; disabled in catalogue snapshot |
| `layer.removeBackground` | Remove Background |  | {"layer":id?,"sampleAllLayers":bool=false,"refine":bool=true} → {layer,bounds} (adds a layer mask from Select Subject; the Background becomes a normal layer) | needs document; disabled in catalogue snapshot |
| `layer.renameLayer` | Rename Layer | Layer | {"layer":id?,"name":str} | disabled in catalogue snapshot |
| `layer.select` | Select Layer |  | {"layer":id\|str\|{"index":uint}\|{"ordinal":"Trgt\|Frwr\|Bckw\|Frnt\|Back"} \| "name":str,"occurrence":index?,"mode":"replace\|toggle\|range\|add\|remove"="replace"} (typed references use the recorded… | needs document; disabled in catalogue snapshot |
| `layer.selectAbove` | Select Layer Above |  | {} (follows the Layers panel's rows; collapsed groups are one row) | needs document; disabled in catalogue snapshot |
| `layer.selectBelow` | Select Layer Below |  | {} (follows the Layers panel's rows; collapsed groups are one row) | needs document; disabled in catalogue snapshot |
| `layer.selectBottom` | Select Bottom Layer |  | {} (follows the Layers panel's rows; collapsed groups are one row) | needs document; disabled in catalogue snapshot |
| `layer.selectInRect` | Select Layers in Marquee |  | {"x":px,"y":px,"width":px,"height":px,"target":"layer\|group"="layer","mode":"replace\|add"="replace"} → {layers} (the layers whose content touches the rect, topmost first; none leaves the se… | needs document; disabled in catalogue snapshot |
| `layer.selectLinkedLayers` | Select Linked Layers | Layer | {} | needs document; disabled in catalogue snapshot |
| `layer.selectTop` | Select Top Layer |  | {} (follows the Layers panel's rows; collapsed groups are one row) | needs document; disabled in catalogue snapshot |
| `layer.setAdjustment` | Adjustment Properties |  | {"layer":id?, …params of that adjustment kind} (Levels, Curves: "eyedropper":{"point":"black\|gray\|white","at":[x,y],"size":1..101=1} or {"point",…,"color":[r,g,b] 0..1} = the Properties pan… | needs document; disabled in catalogue snapshot |
| `layer.setEffectsExpanded` | Expand/Collapse Effects |  | {"layer":id?,"expanded":bool?,"all":bool?} (no expanded: toggle; all: every layer with effects or smart filters; view state, not an undo step) | needs document; disabled in catalogue snapshot |
| `layer.setEffectsVisible` | Show/Hide Effects |  | {"layer":id?,"index":n?,"visible":bool?} (no index: all of the layer's effects, the "Effects" row; index: the effect at that position in the layer's list; no visible: toggle) | needs document; disabled in catalogue snapshot |
| `layer.setExpanded` | Expand/Collapse Group |  | {"layer":id?,"expanded":bool?,"all":bool?} (no expanded: toggle; all: every group; not an undo step) | needs document; disabled in catalogue snapshot |
| `layer.setLabelColor` | Layer Color |  | {"color":"none\|red\|orange\|yellow\|green\|seafoam\|blue\|indigo\|magenta\|fuchsia\|violet\|gray","layer":id\|name\|{"background":true}?} (no layer: selected layers; groups include descendants) | needs document; disabled in catalogue snapshot |
| `layer.setProps` | Layer Properties |  | {"layer":id?,"layers":[id,…]? (the same change to each, one step: the Layers panel's controls with several layers selected),"name":str? (one layer only),"visible":bool?,"opacity":0..1?,"fil… | needs document; disabled in catalogue snapshot |
| `layer.showLayers` | Show Layers |  | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.showOnly` | Show Only This Layer |  | {"layer":id?} → {shownAlone} (⌥-click a layer's eye; again restores the other layers' visibility) | needs document; disabled in catalogue snapshot |
| `layer.smartFilter.blendingOptions` | Blending Options… | Layer > Smart Filter | {"layer":id?,"index":u32? (0 = bottom; default top),"blend":str?,"opacity":0..1?} | needs document; disabled in catalogue snapshot |
| `layer.smartFilter.clearSmartFilters` | Clear Smart Filters | Layer > Smart Filter | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.smartFilter.delete` | Delete Smart Filter |  | {"layer":id?,"index":u32?} | needs document; disabled in catalogue snapshot |
| `layer.smartFilter.deleteFilterMask` | Delete Filter Mask | Layer > Smart Filter | {"layer":id?,"ifPresent":bool=false (true: a smart object without a filter mask is left as it is, as a Photoshop action's step needs where Photoshop added the mask by default)} | needs document; disabled in catalogue snapshot |
| `layer.smartFilter.disableFilterMask` | Disable Filter Mask | Layer > Smart Filter | {"layer":id?,"enabled":bool? (default: toggle)} | needs document; disabled in catalogue snapshot |
| `layer.smartFilter.disableSmartFilters` | Disable Smart Filters | Layer > Smart Filter | {"layer":id?,"enabled":bool? (default: toggle)} | needs document; disabled in catalogue snapshot |
| `layer.smartFilter.move` | Move Smart Filter |  | {"layer":id?,"index":u32?,"to":u32} | needs document; disabled in catalogue snapshot |
| `layer.smartFilter.setParams` | Edit Smart Filter |  | {"layer":id?,"index":u32?,"params":{…} (merged)} | needs document; disabled in catalogue snapshot |
| `layer.smartFilter.setVisible` | Show/Hide Smart Filter |  | {"layer":id?,"index":u32?,"visible":bool? (default: toggle)} | needs document; disabled in catalogue snapshot |
| `layer.smartFilter.transfer` | Move or Copy Smart Filters |  | {"from":id,"to":id,"filter":u32? (default: all, with the filter mask),"copy":bool=false} | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.convertToEmbedded` | Convert to Embedded | Layer > Smart Objects | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.convertToLayers` | Convert to Layers | Layer > Smart Objects | {"layer":id?} (contents unpacked at the placement: one layer, or a group named after the smart object; smart filters are discarded) | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.convertToLinked` | Convert to Linked… | Layer > Smart Objects | {"layer":id?,"path":str} (writes the contents there) | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.convertToSmartObject` | Convert to Smart Object | Layer > Smart Objects | {"layer":id?} (default: combine selected layers) | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.editContents` | Edit Contents | Layer > Smart Objects | {"layer":id?} → opens the contents as a new document; saving (layer.smartObjects.saveContents) or closing it updates the smart object | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.exportContents` | Export Contents… | Layer > Smart Objects | {"layer":id?,"path":str (another extension than the contents' own exports them in that format)} | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.exportSvg` | Export SVG Contents |  | {"layer":id?} → {document,svg?\|sourceBase64?,extension,sourceSize,fingerprint,contentsId} | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.newSmartObjectViaCopy` | New Smart Object via Copy | Layer > Smart Objects | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.perspectiveWarp` | Perspective Warp | Layer > Smart Objects | {"planes":[{"src":[[x,y]×4],"dst":[[x,y]×4]}…] (corners clockwise from top-left; corners that coincide in src are linked),"straighten":"horizontal\|vertical\|auto"?,"interpolation":"bicubic\|b… | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.puppetWarp` | Puppet Warp | Layer > Smart Objects | {"pins":[{"src":[x,y],"dst":[x,y],"rotate":deg?,"depth":n?}…],"mode":"rigid\|normal\|distort"="normal","density":"fewer\|normal\|more"="normal","expansion":px=2,"interpolation":"bicubic\|bilinea… | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.rasterize` | Rasterize | Layer > Smart Objects | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.relinkToFile` | Relink to File… | Layer > Smart Objects | {"layer":id?,"path":str} | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.replaceContents` | Replace Contents… | Layer > Smart Objects | {"layer":id?,"path":str} | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.revealInFinder` | Reveal in Finder | Layer > Smart Objects | {"dryRun":bool=false} | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.saveContents` | Save Contents |  | {} (in an Edit Contents document) | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.stackMode.entropy` | Entropy | Layer > Smart Objects > Stack Mode | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.stackMode.kurtosis` | Kurtosis | Layer > Smart Objects > Stack Mode | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.stackMode.maximum` | Maximum | Layer > Smart Objects > Stack Mode | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.stackMode.mean` | Mean | Layer > Smart Objects > Stack Mode | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.stackMode.median` | Median | Layer > Smart Objects > Stack Mode | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.stackMode.minimum` | Minimum | Layer > Smart Objects > Stack Mode | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.stackMode.none` | None | Layer > Smart Objects > Stack Mode | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.stackMode.range` | Range | Layer > Smart Objects > Stack Mode | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.stackMode.skewness` | Skewness | Layer > Smart Objects > Stack Mode | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.stackMode.standardDeviation` | Standard Deviation | Layer > Smart Objects > Stack Mode | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.stackMode.summation` | Summation | Layer > Smart Objects > Stack Mode | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.stackMode.variance` | Variance | Layer > Smart Objects > Stack Mode | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.updateAllModifiedContent` | Update All Modified Content | Layer > Smart Objects | {} | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.updateChanged` | Update Changed Linked Content |  | {} — re-render the active document's linked smart objects whose files changed on disk since they were last seen (size or modification time); the desktop app does this by itself every two se… | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.updateModifiedContent` | Update Modified Content | Layer > Smart Objects | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.updateSvg` | Update SVG Contents |  | {"document":id,"layer":id,"svg":"<svg …>","fingerprint":"original BLAKE3 hex","contentsId":id} → {layer,contentsId,fingerprint,updated} | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.updateVectorSource` | Update Vector Contents |  | {"document":id,"layer":id,"sourceBase64":"native bytes","extension":"ai\|pdf\|eps","previewSvg":"bounded display SVG","fingerprint":"original BLAKE3 hex","contentsId":id} | needs document; disabled in catalogue snapshot |
| `layer.smartObjects.warp` | Warp | Layer > Smart Objects | {"layer":id?,"rect":[x0,y0,x1,y1]? (warp box; default = layer content ∩ selection),"style":"custom\|none\|arc\|arcLower\|arcUpper\|arch\|bulge\|shellLower\|shellUpper\|flag\|wave\|fish\|rise\|fisheye\|in… | needs document; disabled in catalogue snapshot |
| `layer.stampDown` | Stamp Down |  | {} → {layer} (a copy of the active layer merged into the pixel layer below; several selected: into a new layer above them) | needs document; disabled in catalogue snapshot |
| `layer.stampVisible` | Stamp Visible |  | {} → {layer} (visible layers merged into a new layer above the active one, or into the active one if it is an empty pixel layer) | needs document; disabled in catalogue snapshot |
| `layer.toggleLockTransparency` | Lock Transparent Pixels |  | {"layer":id?} (toggles; several layers selected: locks them all unless every one is locked) | needs document; disabled in catalogue snapshot |
| `layer.toggleMaskOverlay` | Toggle Layer Mask Overlay |  | {"layer":id?} (shows or hides the active layer's mask as a rubylith over the composite, the `\` key; red at 50% unless Layer Mask Display Options, channel.options {"channel":"mask"}, set it… | needs document; disabled in catalogue snapshot |
| `layer.translate` | Move Layer |  | {"layer":id?,"dx":i32,"dy":i32,"units":"px"\|"pt"="px" (pt: points, whole pixels at the document's resolution),"target":"pixels"\|"mask"="pixels","selection":bool=false} (no layer: every sele… | needs document; disabled in catalogue snapshot |
| `layer.ungroupLayers` | Ungroup Layers | Layer | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.vectorMask.add` | Add Vector Mask | Layer > Vector Mask | {"layer":id?,"path":{…}? \| "name":str\|"work"? (copy a document path),"hide":bool=false (Hide All = inverted)} → vector mask info. Without a path the mask reveals all. | needs document; disabled in catalogue snapshot |
| `layer.vectorMask.currentPath` | Vector Mask: Current Path |  | {"layer":id?,"name":str\|"work"="work"} | needs document; disabled in catalogue snapshot |
| `layer.vectorMask.delete` | Delete Vector Mask | Layer > Vector Mask | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.vectorMask.edit` | Edit Vector Mask |  | {"layer":id?,"path":{…}?,"enabled":bool?,"linked":bool?,"density":0..100?,"feather":0..1000? (pixels),"invert":true?}. On a shape layer (whose path is its vector mask) only density and feat… | needs document; disabled in catalogue snapshot |
| `layer.vectorMask.enabled` | Enable Vector Mask |  | {"layer":id?,"enabled":bool? (default: toggle)} | needs document; disabled in catalogue snapshot |
| `layer.vectorMask.fromPath` | Vector Mask from Current Path | Layer > Vector Mask | {"layer":id?,"name":str\|"work"="work"} | needs document; disabled in catalogue snapshot |
| `layer.vectorMask.hideAll` | Vector Mask: Hide All |  | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.vectorMask.info` | Vector Mask Info |  | {"layer":id?} → {layer,path,enabled,linked,density,feather} | needs document; disabled in catalogue snapshot |
| `layer.vectorMask.linked` | Link Vector Mask |  | {"layer":id?,"linked":bool? (default: toggle)} | needs document; disabled in catalogue snapshot |
| `layer.vectorMask.revealAll` | Vector Mask: Reveal All |  | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `layer.videoLayers.deleteFrame` | Delete Frame | Layer > Video Layers | {} → {} | needs document; disabled in catalogue snapshot |
| `layer.videoLayers.duplicateFrame` | Duplicate Frame | Layer > Video Layers | {} → {} | needs document; disabled in catalogue snapshot |
| `layer.videoLayers.insertBlankFrame` | Insert Blank Frame | Layer > Video Layers | {} → {} | needs document; disabled in catalogue snapshot |
| `layer.videoLayers.interpretFootage` | Interpret Footage… | Layer > Video Layers | {} → {} | needs document; disabled in catalogue snapshot |
| `layer.videoLayers.newBlankVideoLayer` | New Blank Video Layer | Layer > Video Layers | {} → {} | needs document; disabled in catalogue snapshot |
| `layer.videoLayers.newVideoLayerFromFile` | New Video Layer from File… | Layer > Video Layers | {} → {} | needs document; disabled in catalogue snapshot |
| `layer.videoLayers.rasterize` | Rasterize | Layer > Video Layers | {} → {} | needs document; disabled in catalogue snapshot |
| `layer.videoLayers.reloadFrame` | Reload Frame | Layer > Video Layers | {} → {} | needs document; disabled in catalogue snapshot |
| `layer.videoLayers.replaceFootage` | Replace Footage… | Layer > Video Layers | {} → {} | needs document; disabled in catalogue snapshot |
| `layer.videoLayers.restoreAllFrames` | Restore All Frames | Layer > Video Layers | {} → {} | needs document; disabled in catalogue snapshot |
| `layer.videoLayers.restoreFrame` | Restore Frame | Layer > Video Layers | {} → {} | needs document; disabled in catalogue snapshot |
| `layer.videoLayers.showAlteredVideo` | Show Altered Video | Layer > Video Layers | {} → {} | needs document; disabled in catalogue snapshot |
| `layer.xmpMetadata` | Layer XMP Metadata |  | {"layer":id?,"rawData":string\|null?} → {"layer","rawData","changed"} (no layer: the active layer; no rawData: read it; a string sets the layer's XMP packet, null removes it; as Photoshop's … | needs document; disabled in catalogue snapshot |

## `layerComp` (14)



| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `layerComp.apply` | Apply Layer Comp |  | {"comp":id\|name\|{"index":int}\|{"id":uint}\|{"ordinal":"Trgt\|Nxt\|Prvs\|Frst\|Lst\|Al"}? (default: last applied; typed index is one-based panel order, invalid indexes do nothing)} → {comp, missin… | needs document; disabled in catalogue snapshot |
| `layerComp.delete` | Delete Layer Comp |  | {"comp":id\|name?} | needs document; disabled in catalogue snapshot |
| `layerComp.duplicate` | Duplicate Layer Comp |  | {"comp":id\|name?} → {comp} | needs document; disabled in catalogue snapshot |
| `layerComp.list` | List Layer Comps |  | {} → {comps:[{id,name,comment,visibility,position,appearance,layers,missingLayers}],lastApplied,hasLastDocumentState} | needs document; disabled in catalogue snapshot |
| `layerComp.new` | New Layer Comp… |  | {"name":str="Layer Comp N","comment":str="","visibility":bool=true,"position":bool=true,"appearance":bool=true} → {comp} | needs document; disabled in catalogue snapshot |
| `layerComp.next` | Apply Next Layer Comp |  | {} | needs document; disabled in catalogue snapshot |
| `layerComp.previous` | Apply Previous Layer Comp |  | {} | needs document; disabled in catalogue snapshot |
| `layerComp.rename` | Rename Layer Comp |  | {"comp":id\|name?,"name":str} | needs document; disabled in catalogue snapshot |
| `layerComp.reorder` | Reorder Layer Comp |  | {"comp":id\|name?,"index":integer (zero-based final position)} | needs document; disabled in catalogue snapshot |
| `layerComp.restoreLastDocumentState` | Restore Last Document State |  | {} | needs document; disabled in catalogue snapshot |
| `layerComp.setComment` | Layer Comp Comment |  | {"comp":id\|name?,"comment":str} | needs document; disabled in catalogue snapshot |
| `layerComp.setOptions` | Layer Comp Options… |  | {"comp":id\|name?,"visibility":bool?,"position":bool?,"appearance":bool?,"name":str?,"comment":str?} | needs document; disabled in catalogue snapshot |
| `layerComp.update` | Update Layer Comp |  | {"comp":id\|name\|"*"? (default: last applied; "*" = all),"what":"all\|visibility\|position\|appearance"="all"} | needs document; disabled in catalogue snapshot |
| `layerComp.updateWarnings` | Layer Comp Warnings |  | {"comp":id\|name? (default: every comp; limits the report and the clear to that comp),"clear":bool=false (drop states of deleted layers)} → {warnings:[{comp,name,missingLayers}],count} | needs document; disabled in catalogue snapshot |
