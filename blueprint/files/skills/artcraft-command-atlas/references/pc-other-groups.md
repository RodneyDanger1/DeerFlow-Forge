# PhotoCraft Other Groups

Commands from groups not covered by the specialist maps. Same verification rules apply.

Commands: **177** across 19 groups.

## Coverage

`cloneSource` 5 · `color` 1 · `command` 1 · `count` 7 · `edit` 79 · `help` 1 · `jobs` 2 · `measurementLog` 3 · `notes` 4 · `plugin` 5 · `prefs` 3 · `session` 1 · `slice` 7 · `timeline` 7 · `tool` 5 · `tools` 13 · `updates` 1 · `variables` 1 · `view` 31

## `cloneSource` (5)



| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `cloneSource.list` | Clone Sources |  | {} → {active,sources:[{index,source,anchor,offset,layer,width,height,linked,rotation,flipH,flipV}],overlay} |  |
| `cloneSource.overlay` | Clone Source Overlay |  | {"show":bool?,"opacity":0..100?,"clipped":bool?,"autoHide":bool?,"invert":bool?,"blend":"normal\|darken\|lighten\|difference"?} |  |
| `cloneSource.resetTransform` | Reset Transform |  | {"index":0..4?=active} |  |
| `cloneSource.select` | Select Clone Source |  | {"index":0..4} |  |
| `cloneSource.set` | Set Clone Source |  | {"index":0..4?=active,"source":[x,y]? (⌥-click; re-pairs with the next stroke),"offset":[dx,dy]?,"width":%?,"height":%?\|"scale":[w%,h%]?,"linked":bool? (W/H link: a lone width or height sca… |  |

## `color` (1)

Colour commands set or convert colour values. Record the exact colour space (RGB/CMYK/spot) because screen hex is not a press value.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `color.profileMismatch` | Embedded Profile Mismatch |  | {"action":"preserve\|convert\|discard\|assignWorking"} | needs document; disabled in catalogue snapshot |

## `command` (1)

Command-palette helpers. They do not replace reading the catalogue.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `command.list` | List Commands |  | {} |  |

## `count` (7)



| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `count.add` | Add Count |  | {"x":px,"y":px,"group":index?} | needs document; disabled in catalogue snapshot |
| `count.clear` | Clear Count |  | {"group":index\|"all"=active} | needs document; disabled in catalogue snapshot |
| `count.deleteGroup` | Delete Count Group |  | {"group":index=active} | needs document; disabled in catalogue snapshot |
| `count.move` | Move Count |  | {"index":n,"group":index?,"to":[x,y]} \| {"x":px,"y":px,"to":[x,y]} | needs document; disabled in catalogue snapshot |
| `count.newGroup` | New Count Group |  | {"name":str?,"color":"#rrggbb"\|[r,g,b]?} | needs document; disabled in catalogue snapshot |
| `count.remove` | Remove Count |  | {"index":n,"group":index?} \| {"x":px,"y":px,"radius":px=6} | needs document; disabled in catalogue snapshot |
| `count.setGroup` | Count Group Options |  | {"group":index=active,"name":str?,"color":"#rrggbb"\|[r,g,b]?,"markerSize":1..10?,"labelSize":8..72?,"visible":bool?,"active":bool?} | needs document; disabled in catalogue snapshot |

## `edit` (79)

Edit commands manipulate clipboard/undo/duplicate state. Undo/redo are not a substitute for a copy of the file.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `edit.assignProfile` | Assign Profile… | Edit | {"profile":"working\|srgb\|display-p3\|adobe-rgb-compat\|prophoto-compat\|linear-srgb\|rec2020\|gray-gamma-2.2\|sgray\|dot-gain-20-compat\|lab-d50\|coated-cmyk\|none" (or a path to an .icc file)} | needs document; disabled in catalogue snapshot |
| `edit.autoAlignLayers` | Auto-Align Layers… | Edit | {"projection":"auto\|perspective\|cylindrical\|spherical\|collage\|reposition","reference":layer id?=the locked selected layer, else the bottom selected layer,"geometricCorrection":bool=false,"i… | needs document; disabled in catalogue snapshot |
| `edit.autoBlendLayers` | Auto-Blend Layers… | Edit | {"method":"panorama\|stack","seamlessTones":bool=true,"haloControl":0..8=2,"depthMap":bool=false} | needs document; disabled in catalogue snapshot |
| `edit.checkSpelling` | Check Spelling… | Edit | {"action":"list\|change\|changeAll\|addToDictionary\|removeFromDictionary\|suggest"="list","allLayers":bool=true,"layer":id\|name? (check one layer),"ignore":[word]? (Ignore All for this check),"… | needs document; disabled in catalogue snapshot |
| `edit.clear` | Clear | Edit | {"target":"mask"\|{"color":i}\|{"colors":[i,…]}?=Channels panel target,"layer":id\|name?=active} (a targeted mask, channel or Quick Mask is cleared alone) | needs document; disabled in catalogue snapshot |
| `edit.colorSettings` | Color Settings… | Edit | {"workingRgb":"srgb\|display-p3\|adobe-rgb-compat\|prophoto-compat\|linear-srgb\|rec2020","workingCmyk":"coated-cmyk","workingGray":"dot-gain-20-compat\|sgray\|gray-gamma-2.2","policyRgb":"preserv… |  |
| `edit.contentAwareFill` | Content-Aware Fill… | Edit | {"sampling":"auto\|rectangular\|custom","margin":px?,"area":[x,y,w,h]?,"channel":index\|name?,"samplingStrokes":[{"mode":"add\|subtract","size":px,"points":[[x,y],…]}]? (the workspace's Samplin… | needs document; disabled in catalogue snapshot |
| `edit.contentAwareScale` | Content-Aware Scale | Edit | {"width":px?,"height":px?,"scaleX":1..400=100,"scaleY":1..400=100,"x":px?,"y":px?,"amount":0..100=100,"protect":"none"\|channel index\|name,"protectSkinTones":bool=false} | needs document; disabled in catalogue snapshot |
| `edit.convertToProfile` | Convert to Profile… | Edit | {"profile":"srgb\|display-p3\|adobe-rgb-compat\|prophoto-compat\|linear-srgb\|rec2020\|gray-gamma-2.2\|sgray\|lab-d50\|coated-cmyk\|working" (or a path to an .icc file),"intent":"perceptual\|relative\|… | needs document; disabled in catalogue snapshot |
| `edit.copy` | Copy | Edit | {"target":"mask\|filterMask"\|{"color":i}\|{"colors":[i,…]}?=Channels panel target,"layer":id\|name?=active (colour targets only)} (a targeted mask, colour or alpha channel copies that channel … | needs document; disabled in catalogue snapshot |
| `edit.copyMerged` | Copy Merged | Edit | {} | needs document; disabled in catalogue snapshot |
| `edit.cut` | Cut | Edit | {"target":"mask\|filterMask"\|{"color":i}\|{"colors":[i,…]}?=Channels panel target,"layer":id\|name?=active (colour targets only)} (a targeted mask or colour channel cuts that channel only; a c… | needs document; disabled in catalogue snapshot |
| `edit.defineBrushPreset` | Define Brush Preset… | Edit | {"name":text} | disabled in catalogue snapshot |
| `edit.defineCustomShape` | Define Custom Shape… | Edit | {"name":text,"path":"work\|<saved path name>"?} | needs document; disabled in catalogue snapshot |
| `edit.definePattern` | Define Pattern… | Edit | {"name":text,"rect":[x0,y0,x1,y1]?} → {"pattern":id} (name: default the document's name numbered past the library's names; rect: default the selection bounds or else the canvas; added to th… | needs document; disabled in catalogue snapshot |
| `edit.deleteAndFillSelection` | Delete and Fill Selection |  | {} | needs document; disabled in catalogue snapshot |
| `edit.fade` | Fade… | Edit | {"opacity":0..100=100,"mode":"normal\|multiply\|screen\|overlay\|softLight\|hardLight\|darken\|lighten\|difference\|color\|luminosity"} | needs document; disabled in catalogue snapshot |
| `edit.fill` | Fill… | Edit | {"contents":"foreground\|background\|color\|contentAware\|pattern\|history\|black\|gray\|white"="color","color":"#rrggbb\|[r,g,b,a]"=foreground (contents=color),"pattern":id\|name (contents=pattern),… | needs document; disabled in catalogue snapshot |
| `edit.fillBackground` | Fill with Background Color |  | {"layer":id\|name?,"target":"pixels"\|"mask"\|"filterMask"\|"quickMask"\|{"channel":i}?} | needs document; disabled in catalogue snapshot |
| `edit.fillBackgroundPreserve` | Fill with Background Color, Preserve Transparency |  | {"layer":id\|name?,"target":"pixels"\|"mask"\|"filterMask"\|"quickMask"\|{"channel":i}?} | needs document; disabled in catalogue snapshot |
| `edit.fillForeground` | Fill with Foreground Color |  | {"layer":id\|name?,"target":"pixels"\|"mask"\|"filterMask"\|"quickMask"\|{"channel":i}?} | needs document; disabled in catalogue snapshot |
| `edit.fillForegroundPreserve` | Fill with Foreground Color, Preserve Transparency |  | {"layer":id\|name?,"target":"pixels"\|"mask"\|"filterMask"\|"quickMask"\|{"channel":i}?} | needs document; disabled in catalogue snapshot |
| `edit.fillHistory` | Fill from History |  | {"state":n? (default: the History Brush's source, the oldest state still held),"layer":id?,"target":"pixels"\|"mask"\|"quickMask"\|{"channel":i}?,"preserveTransparency":bool?} | needs document; disabled in catalogue snapshot |
| `edit.findAndReplaceText` | Find and Replace Text… | Edit | {"find":text,"replace":text,"action":"changeAll\|find\|change\|changeFind","caseSensitive":bool=false,"wholeWord":bool=false,"forward":bool=true,"allLayers":bool=true} | needs document; disabled in catalogue snapshot |
| `edit.installedProfiles` | Installed Profiles |  | {"class":"any\|input\|display\|output\|deviceLink\|colorSpace\|abstract\|namedColor"="any","colorSpace":"any\|rgb\|cmyk\|gray"="any"} → {profiles: [{path, description, class, colorSpace}], dirs} (the… |  |
| `edit.keyboardShortcuts` | Keyboard Shortcuts… | Edit | {"set":{"<command id>\|tools.temporary.hand\|zoomIn\|zoomOut":"Cmd+Shift+X"\|""(remove)\|null(default)}?,"alternates":{"<command id>":["F3",…]\|[](none)\|null(default)}?,"reset":true\|["<id>",…]?,"… |  |
| `edit.menus` | Menus… | Edit | {"hide":["<id>",…]?,"show":["<id>",…]?,"color":{"<id>":"red\|orange\|yellow\|green\|blue\|violet\|gray\|none"}?,"reset":bool=false} |  |
| `edit.paste` | Paste | Edit | {"as":"pixels\|path\|shape"? (explicit mode: active layered document/composite only; SVG canvas is centred, Path/Shape require retained vector source),"center":[x,y]? (finite explicit coordin… | disabled in catalogue snapshot |
| `edit.pasteSpecial.pasteInPlace` | Paste in Place | Edit > Paste Special | {"target":"pixels"\|"mask"\|"quickMask"\|{"channel":i}=Channels panel target (not pixels: the luminosity pasted into that mask or channel)} | needs document; disabled in catalogue snapshot |
| `edit.pasteSpecial.pasteInto` | Paste Into | Edit > Paste Special | {"center":[x,y]?,"target":"pixels"\|"mask"\|"quickMask"\|{"channel":i}=Channels panel target (not pixels: the luminosity pasted into that mask or channel)} | needs document; disabled in catalogue snapshot |
| `edit.pasteSpecial.pasteOutside` | Paste Outside | Edit > Paste Special | {"center":[x,y]?,"target":"pixels"\|"mask"\|"quickMask"\|{"channel":i}=Channels panel target (not pixels: the luminosity pasted into that mask or channel)} | needs document; disabled in catalogue snapshot |
| `edit.perspectiveWarp` | Perspective Warp | Edit | {"planes":[{"src":[[x,y]×4],"dst":[[x,y]×4]}…] (corners clockwise from top-left; corners that coincide in src are linked),"straighten":"horizontal\|vertical\|auto"?,"interpolation":"bicubic\|b… | needs document; disabled in catalogue snapshot |
| `edit.preferences.cursors` | Cursors… | Edit > Preferences | {} |  |
| `edit.preferences.enhancedControls` | Enhanced Controls… | Edit > Preferences | {} |  |
| `edit.preferences.export` | Export… | Edit > Preferences | {} |  |
| `edit.preferences.fileHandling` | File Handling… | Edit > Preferences | {} |  |
| `edit.preferences.general` | General… | Edit > Preferences | {} |  |
| `edit.preferences.guidesGridAndSlices` | Guides, Grid & Slices… | Edit > Preferences | {} |  |
| `edit.preferences.historyLog` | History Log… | Edit > Preferences | {} |  |
| `edit.preferences.integrations` | Integrations… | Edit > Preferences | {} |  |
| `edit.preferences.interface` | Interface… | Edit > Preferences | {} |  |
| `edit.preferences.performance` | Performance… | Edit > Preferences | {} |  |
| `edit.preferences.plugIns` | Plug-ins… | Edit > Preferences | {} |  |
| `edit.preferences.rawDefaults` | Camera Raw… | Edit > Preferences | {} |  |
| `edit.preferences.scratchDisks` | Scratch Disks… | Edit > Preferences | {} |  |
| `edit.preferences.tools` | Tools… | Edit > Preferences | {} |  |
| `edit.preferences.transparencyAndGamut` | Transparency & Gamut… | Edit > Preferences | {} |  |
| `edit.preferences.type` | Type… | Edit > Preferences | {} |  |
| `edit.preferences.unitsAndRulers` | Units & Rulers… | Edit > Preferences | {} |  |
| `edit.preferences.workspace` | Workspace… | Edit > Preferences | {} |  |
| `edit.presets.exportImportPresets` | Export/Import Presets… | Edit > Presets | {"action":"export\|import","kinds":["brushes","customShapes","tools"]?,"data":json (import),"includeBuiltins":bool=false} |  |
| `edit.presets.migratePresets` | Migrate Presets | Edit > Presets | {path} → {migrated, added:{gradients,styles,shapes,patternGroups,toolPresets}}: merge a presets/preferences file into the library (appends groups by name) |  |
| `edit.presets.presetManager` | Preset Manager… | Edit > Presets | {"action":"list\|rename\|delete\|move","kind":"brushes\|customShapes\|patterns","index":n?,"name":str?,"newName":str?,"to":n?} |  |
| `edit.profileInfo` | Profile Info |  | {"profile":"<builtin id>\|document\|/path/to/profile.icc"=document} |  |
| `edit.puppetWarp` | Puppet Warp | Edit | {"pins":[{"src":[x,y],"dst":[x,y],"rotate":deg?,"depth":n?}…],"mode":"rigid\|normal\|distort"="normal","density":"fewer\|normal\|more"="normal","expansion":px=2,"interpolation":"bicubic\|bilinea… | needs document; disabled in catalogue snapshot |
| `edit.purge.all` | All | Edit > Purge | {} | disabled in catalogue snapshot |
| `edit.purge.clipboard` | Clipboard | Edit > Purge | {} | disabled in catalogue snapshot |
| `edit.purge.histories` | Histories | Edit > Purge | {} | disabled in catalogue snapshot |
| `edit.purge.undo` | Undo | Edit > Purge | {} | disabled in catalogue snapshot |
| `edit.purge.videoCache` | Video Cache | Edit > Purge | {} |  |
| `edit.redo` | Redo | Edit | {} | disabled in catalogue snapshot |
| `edit.stroke` | Stroke… | Edit | {"width":1..250=1,"color":"#rrggbb\|[r,g,b,a]"=foreground,"location":"inside\|center\|outside"="center","mode":"any layer blend mode"="normal","opacity":0..100=100,"preserveTransparency":bool=… | needs document; disabled in catalogue snapshot |
| `edit.toggleLastState` | Toggle Last State | Edit | {} | needs document; disabled in catalogue snapshot |
| `edit.toolbar` | Toolbar… | Edit | {"hidden":["<tool>",…]?,"order":["<tool>",…]?,"reset":bool=false} |  |
| `edit.transform` | Free Transform |  | {"layer":id?,"layers":[id,…]? (several layers moved by one box, one step; default with neither = the selected layers but the Background, as Photoshop's Free Transform with several selected)… | disabled in catalogue snapshot |
| `edit.transform.again` | Again | Edit > Transform | {} | needs document; disabled in catalogue snapshot |
| `edit.transform.againCopy` | Transform Again on a Copy |  | {} (duplicates the active layer and repeats the last transform on the copy: step and repeat) | needs document; disabled in catalogue snapshot |
| `edit.transform.flipHorizontal` | Flip Horizontal | Edit > Transform | {"target":"pixels"\|"mask"\|"quickMask"\|{"channel":i}=Channels panel target (an unlinked mask, an alpha channel or the Quick Mask turns alone)} | needs document; disabled in catalogue snapshot |
| `edit.transform.flipVertical` | Flip Vertical | Edit > Transform | {"target":"pixels"\|"mask"\|"quickMask"\|{"channel":i}=Channels panel target (an unlinked mask, an alpha channel or the Quick Mask turns alone)} | needs document; disabled in catalogue snapshot |
| `edit.transform.removeWarpSplit` | Remove Warp Split | Edit > Transform | {"warp":{…}? (the warp being edited; returned split),"rect":[x0,y0,x1,y1]?,"at":[x,y]? (document point; default = middle of the patch)} — without `warp`, edits the active smart object's war… | disabled in catalogue snapshot |
| `edit.transform.rotate180` | Rotate 180° | Edit > Transform | {"target":"pixels"\|"mask"\|"quickMask"\|{"channel":i}=Channels panel target (an unlinked mask, an alpha channel or the Quick Mask turns alone)} | needs document; disabled in catalogue snapshot |
| `edit.transform.rotate90Ccw` | Rotate 90° Counter Clockwise | Edit > Transform | {"target":"pixels"\|"mask"\|"quickMask"\|{"channel":i}=Channels panel target (an unlinked mask, an alpha channel or the Quick Mask turns alone)} | needs document; disabled in catalogue snapshot |
| `edit.transform.rotate90Cw` | Rotate 90° Clockwise | Edit > Transform | {"target":"pixels"\|"mask"\|"quickMask"\|{"channel":i}=Channels panel target (an unlinked mask, an alpha channel or the Quick Mask turns alone)} | needs document; disabled in catalogue snapshot |
| `edit.transform.splitWarpCrosswise` | Split Warp Crosswise | Edit > Transform | {"warp":{…}? (the warp being edited; returned split),"rect":[x0,y0,x1,y1]?,"at":[x,y]? (document point; default = middle of the patch)} — without `warp`, edits the active smart object's war… | disabled in catalogue snapshot |
| `edit.transform.splitWarpHorizontally` | Split Warp Horizontally | Edit > Transform | {"warp":{…}? (the warp being edited; returned split),"rect":[x0,y0,x1,y1]?,"at":[x,y]? (document point; default = middle of the patch)} — without `warp`, edits the active smart object's war… | disabled in catalogue snapshot |
| `edit.transform.splitWarpVertically` | Split Warp Vertically | Edit > Transform | {"warp":{…}? (the warp being edited; returned split),"rect":[x0,y0,x1,y1]?,"at":[x,y]? (document point; default = middle of the patch)} — without `warp`, edits the active smart object's war… | disabled in catalogue snapshot |
| `edit.transform.warp` | Warp | Edit > Transform | {"layer":id?,"rect":[x0,y0,x1,y1]? (warp box; default = layer content ∩ selection),"style":"custom\|none\|arc\|arcLower\|arcUpper\|arch\|bulge\|shellLower\|shellUpper\|flag\|wave\|fish\|rise\|fisheye\|in… | disabled in catalogue snapshot |
| `edit.transform.warpGrid` | Warp Grid |  | {"warp":{…}? (the warp being edited; returned with the new mesh),"rect":[x0,y0,x1,y1]?,"size":n\|"default"\|"3"\|"4"\|"5" (square patches, 1..=64; 1 and "default" are the single-patch grid)} — … | disabled in catalogue snapshot |
| `edit.undo` | Undo | Edit | {} | disabled in catalogue snapshot |

## `help` (1)

Help/menu commands expose reference information. They do not change the artwork.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `help.checkForUpdates` | Check for Updates… | Help | {} | disabled in catalogue snapshot |

## `jobs` (2)



| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `jobs.cancel` | Cancel Background Job |  | {"job":u64? (default: every running job)} |  |
| `jobs.list` | List Background Jobs |  | {} |  |

## `measurementLog` (3)



| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `measurementLog.delete` | Delete Measurements |  | {"rows":[ids]}\|{"all":true} | disabled in catalogue snapshot |
| `measurementLog.export` | Export Measurements… |  | {"path":str? (CSV file; omitted → returns the CSV text),"rows":[ids]?} |  |
| `measurementLog.list` | Measurement Log |  | {} → rows and columns |  |

## `notes` (4)



| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `notes.add` | New Note |  | {"x":px,"y":px,"text":str="","author":str="","color":"#rrggbb"\|[r,g,b]=pale yellow,"open":bool=true} | needs document; disabled in catalogue snapshot |
| `notes.delete` | Delete Note |  | {"index":n}\|{"all":true} | needs document; disabled in catalogue snapshot |
| `notes.list` | Notes |  | {} → notes (index, author, text, colour, position, open, modified) | needs document; disabled in catalogue snapshot |
| `notes.set` | Edit Note |  | {"index":n,"text":str?,"author":str?,"color":"#rrggbb"\|[r,g,b]?,"x":px?,"y":px?,"open":bool?} | needs document; disabled in catalogue snapshot |

## `plugin` (5)

Plugins extend the engine. A plugin's exporter format is `plugin.<id>`; query `plugin.info` before use.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `plugin.install` | Install Plug-in… | Filter > Plug-ins | {"path":text,"data":json,"replace":bool=true} (path: a .wasm file, native only; data: the module as base64) |  |
| `plugin.list` | List Plug-ins |  | {} |  |
| `plugin.reload` | Reload Plug-ins |  | {"path":text} (a folder of .wasm plug-ins; default: the Plug-ins preference folder) |  |
| `plugin.remove` | Remove Plug-in |  | {"id":text} |  |
| `plugin.run` | Run Plug-in |  | {"id":text,"params":json} (plug-in parameters under "params" or at the top level; see plugin.list) | needs document; disabled in catalogue snapshot |

## `prefs` (3)

Preferences change app behaviour, not the document. Avoid relying on them for reproducible output.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `prefs.get` | Get Preferences |  | {"path":"section.key"?=everything (e.g. "performance.historyStates", "colorSettings.workingRgb")} |  |
| `prefs.reset` | Reset Preferences |  | {"path":"section\|section.key"?=everything} |  |
| `prefs.set` | Set Preferences |  | {"path":"section.key","value":json} or {"values":{"section.key":json,…}} (validated; all or nothing) |  |

## `session` (1)



| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `session.inspect` | Inspect Session |  | {} |  |

## `slice` (7)

Slices define web-export regions. They only matter if the export path consumes slices.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `slice.delete` | Delete Slice |  | {"slice":id \| "number":n \| "slices":[id…]} → {deleted} | needs document; disabled in catalogue snapshot |
| `slice.divide` | Divide Slice… |  | {"slice":id \| "number":n,"horizontal":n=1 (slices down),"vertical":n=1 (slices across); at most 10000 parts} → {slices} | needs document; disabled in catalogue snapshot |
| `slice.fromGuides` | Slices From Guides |  | {} (replaces every slice by the grid of the canvas guides) → {slices} | needs document; disabled in catalogue snapshot |
| `slice.list` | List Slices |  | {} → {slices:[{number,id,origin:auto\|layer\|user,name,rect:[x,y,w,h],kind,layer,url,alt,…,pieces?:[{number,name,rect}] (a stored slice's visible parts; number null when wholly covered)}], lo… | needs document; disabled in catalogue snapshot |
| `slice.new` | Slice Tool |  | {"rect":[x,y,w,h] \| "x","y","width","height", plus Slice Options ("name","kind":"image\|noImage\|table","url","target","message","alt","cellText","cellTextIsHtml","background":"none\|#rrggbb")… | needs document; disabled in catalogue snapshot |
| `slice.promote` | Promote |  | {"slice":id \| "number":n} (auto or layer-based → user slice) → {slice} | needs document; disabled in catalogue snapshot |
| `slice.set` | Slice Options… |  | {"slice":id \| "number":n (an auto slice is promoted), "name"?,"kind":"image\|noImage\|table"?,"url"?,"target"?,"message"?,"alt"?,"cellText"?,"cellTextIsHtml"?,"horizontalAlign":0..4?,"vertica… | needs document; disabled in catalogue snapshot |

## `timeline` (7)



| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `timeline.create` | Create Video Timeline |  | {duration?:30, fps?:30} → {timeline} | needs document; disabled in catalogue snapshot |
| `timeline.delete` | Delete Timeline |  | {} → {timeline:null} | needs document; disabled in catalogue snapshot |
| `timeline.info` | Timeline Info |  | {} → {timeline} | needs document; disabled in catalogue snapshot |
| `timeline.nextFrame` | Next Frame |  | {} → {timeline} | needs document; disabled in catalogue snapshot |
| `timeline.previousFrame` | Previous Frame |  | {} → {timeline} | needs document; disabled in catalogue snapshot |
| `timeline.setFrame` | Go to Frame |  | {frame} → {timeline} | needs document; disabled in catalogue snapshot |
| `timeline.setProps` | Timeline Settings |  | {fps?, duration?, workStart?, workEnd?} → {timeline} | needs document; disabled in catalogue snapshot |

## `tool` (5)

Tool commands activate an editing tool. Headless automation should prefer the direct command, not tool activation.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `tool.presets.edit` | Edit Tool Presets |  | {"action":"rename\|delete","preset":name\|[names],"name":str (rename)} |  |
| `tool.presets.list` | Tool Presets |  | {"tool":name? (Current Tool Only)} → {presets:[{name,tool}]} |  |
| `tool.presets.new` | New Tool Preset… |  | {"name":str?=tool (at most 255 characters; a taken name gets " 2", " 3"…),"tool":name ("crop" for Crop presets),"options":{…}? (opaque; "brush" defaults to the current brush for painting to… |  |
| `tool.presets.reset` | Reset Tool Presets |  | {} |  |
| `tool.presets.select` | Select Tool Preset |  | {"preset":name} → {name,tool,options} (applies "brush" and "foreground"; the shell switches tool and options) |  |

## `tools` (13)



| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `tools.decreaseBrushHardness` | Decrease Brush Hardness |  | {} |  |
| `tools.decreaseBrushSize` | Decrease Brush Size |  | {} |  |
| `tools.defaultColors` | Default Foreground and Background Colors |  | {} |  |
| `tools.firstBrush` | First Brush |  | {} |  |
| `tools.increaseBrushHardness` | Increase Brush Hardness |  | {} |  |
| `tools.increaseBrushSize` | Increase Brush Size |  | {} |  |
| `tools.lastBrush` | Last Brush |  | {} |  |
| `tools.nextBrush` | Next Brush |  | {} |  |
| `tools.previousBrush` | Previous Brush |  | {} |  |
| `tools.rotateBrush` | Rotate Brush Tip |  | {"degrees":-360..360 (positive anticlockwise; ← / → while painting send 1, ⇧ 15)} |  |
| `tools.setBrush` | Set Brush |  | {"preset":name?,"reset":bool?,…BrushSettings fields (camelCase, deep-merged; pose.overrideTiltX/Y:bool; pose.overrideTilt:legacy combined alias)} |  |
| `tools.setColors` | Set Colors |  | {"foreground":"#rrggbb"\|[r,g,b,a?]?,"background":same?,"foregroundCmyk":[c,m,y,k]? (inks 0..1 the foreground was picked as: a CMYK document is filled with exactly these),"backgroundCmyk":sa… |  |
| `tools.swapColors` | Switch Foreground and Background Colors |  | {} |  |

## `updates` (1)



| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `updates.status` | Update Check Status |  | {} |  |

## `variables` (1)



| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `variables.list` | List Variables |  | {} → {defs,dataSets,active} | needs document; disabled in catalogue snapshot |

## `view` (31)

View commands change the editing view, not the artwork. Do not expect them to affect exported pixels.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `view.clearCanvasGuides` | Clear Canvas Guides | View | {} | needs document; disabled in catalogue snapshot |
| `view.clearGuides` | Clear Guides | View | {} | needs document; disabled in catalogue snapshot |
| `view.clearSelectedArtboardGuides` | Clear Selected Artboard Guides | View | {} (guides inside the active artboard) | disabled in catalogue snapshot |
| `view.clearSlices` | Clear Slices | View | {} (deletes every user and layer-based slice) → {cleared} | needs document; disabled in catalogue snapshot |
| `view.colorSamplers.add` | Add Color Sampler |  | {"x":f64,"y":f64} → the new point {index, number, position, rgb, cmyk}; errors at the 10-point limit or off the canvas | needs document; disabled in catalogue snapshot |
| `view.colorSamplers.clear` | Clear Color Samplers |  | {} | needs document; disabled in catalogue snapshot |
| `view.colorSamplers.delete` | Delete Color Sampler |  | {"index":n} | needs document; disabled in catalogue snapshot |
| `view.colorSamplers.list` | Color Samplers |  | {} → {max, samplers:[{index, number, position, rgb, cmyk}]} | needs document; disabled in catalogue snapshot |
| `view.colorSamplers.move` | Move Color Sampler |  | {"index":n,"x":f64,"y":f64} | needs document; disabled in catalogue snapshot |
| `view.deleteGuide` | Delete Guide |  | {"orientation":"horizontal\|vertical","index":n} | needs document; disabled in catalogue snapshot |
| `view.editGuide` | Edit Guide |  | {"orientation":"horizontal\|vertical","index":n,"newOrientation":"horizontal\|vertical"?,"position":px or "<number><unit>"?,"color":name or "#rrggbb"?} (Edit Selected Guides: units and colour… | needs document; disabled in catalogue snapshot |
| `view.gamutWarning` | Gamut Warning | View | {"on":bool=toggle,"threshold":deltaE=4,"profile":"<proof profile override>"} | needs document; disabled in catalogue snapshot |
| `view.layerMask` | View Layer Mask |  | {"layer":id?,"mode":"off"\|"gray"\|"overlay"\|"toggleGray"\|"toggleOverlay"="toggleGray","mask":"layer"\|"filter"="layer" (filter: a smart object's filter mask)} (gray: the mask alone, ⌥-click i… | needs document; disabled in catalogue snapshot |
| `view.lockSlices` | Lock Slices | View | {"on":bool? (default: toggle)} → {locked} | needs document; disabled in catalogue snapshot |
| `view.moveGuide` | Move Guide |  | {"orientation":"horizontal\|vertical","index":n,"position":px or "<number><unit>","toOrientation":"horizontal\|vertical"?} (units as for view.newGuide; toOrientation turns the guide, its posi… | needs document; disabled in catalogue snapshot |
| `view.newGuide` | New Guide… | View | {"orientation":"horizontal\|vertical","position":px or "<number><unit>","color":"lightBlue\|lightRed\|green\|mediumBlue\|yellow\|magenta\|cyan\|lightGray\|black" or "#rrggbb"?} (units px, in, cm, mm… | needs document; disabled in catalogue snapshot |
| `view.newGuideLayout` | New Guide Layout… | View | {"columns":n=0,"width":len?,"gutter":len=0,"rows":n=0,"height":len?,"rowGutter":len=gutter,"margin":len\|[top,left,bottom,right]=0,"centerColumns":bool=false,"clearExisting":bool=false,"targ… | needs document; disabled in catalogue snapshot |
| `view.newGuidesFromShape` | New Guides From Shape | View | {"layer":id?} | needs document; disabled in catalogue snapshot |
| `view.proofColors` | Proof Colors | View | {"on":bool=toggle} | needs document; disabled in catalogue snapshot |
| `view.proofSetup` | Proof Setup… |  | {"profile":"working-cmyk\|srgb\|display-p3\|adobe-rgb-compat\|prophoto-compat\|linear-srgb\|rec2020\|gray-gamma-2.2\|sgray\|lab-d50\|coated-cmyk" (or a path to an .icc file)="working-cmyk","intent":"… | needs document; disabled in catalogue snapshot |
| `view.proofSetup.colorBlindnessDeuteranopia` | Color Blindness — Deuteranopia-type | View > Proof Setup | {} (sets the proof and turns Proof Colors on) | needs document; disabled in catalogue snapshot |
| `view.proofSetup.colorBlindnessProtanopia` | Color Blindness — Protanopia-type | View > Proof Setup | {} (sets the proof and turns Proof Colors on) | needs document; disabled in catalogue snapshot |
| `view.proofSetup.legacyMacintoshRgb` | Legacy Macintosh RGB | View > Proof Setup | {} (sets the proof and turns Proof Colors on) | needs document; disabled in catalogue snapshot |
| `view.proofSetup.workingBlackPlate` | Working Black Plate | View > Proof Setup | {} (sets the proof and turns Proof Colors on) | needs document; disabled in catalogue snapshot |
| `view.proofSetup.workingCmyPlate` | Working CMY Plate | View > Proof Setup | {} (sets the proof and turns Proof Colors on) | needs document; disabled in catalogue snapshot |
| `view.proofSetup.workingCyanPlate` | Working Cyan Plate | View > Proof Setup | {} (sets the proof and turns Proof Colors on) | needs document; disabled in catalogue snapshot |
| `view.proofSetup.workingMagentaPlate` | Working Magenta Plate | View > Proof Setup | {} (sets the proof and turns Proof Colors on) | needs document; disabled in catalogue snapshot |
| `view.proofSetup.workingYellowPlate` | Working Yellow Plate | View > Proof Setup | {} (sets the proof and turns Proof Colors on) | needs document; disabled in catalogue snapshot |
| `view.resetRulerOrigin` | Reset Ruler Origin |  | {} (zero point back at the image's top-left) | needs document; disabled in catalogue snapshot |
| `view.setRulerOrigin` | Set Ruler Origin |  | {"x":px,"y":px} (the rulers' zero point in document pixels; the rulers and Info panel measure from it) | needs document; disabled in catalogue snapshot |
| `view.thirtyTwoBitPreviewOptions` | 32-bit Preview Options… | View | {"method":"exposureGamma\|highlightCompression"="exposureGamma","exposure":-20..20=0,"gamma":0.1..9.99=1} | needs document; disabled in catalogue snapshot |
