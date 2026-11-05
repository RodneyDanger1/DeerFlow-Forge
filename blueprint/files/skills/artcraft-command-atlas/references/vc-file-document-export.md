# VectorCraft File Document Export

Auto-generated from the installed 918-command catalogue (snapshot 2026-11-05). Every row is a real command id; params are abbreviated from the catalogue's own text. Read the full params string with `$VC commands` before running. Tips are practical notes, not substitutes for the schema.

Commands: **166** across 19 groups.

## Coverage

`action` 1 · `assets` 6 · `command` 1 · `css` 3 · `dataset` 12 · `document` 35 · `file` 28 · `help` 5 · `importMatches` 3 · `library` 16 · `links` 11 · `pdf` 5 · `plugin` 7 · `prefs` 4 · `print` 9 · `script` 1 · `shortcutSet` 1 · `variable` 14 · `webExport` 4

## `action` (1)

Actions record/replay steps. Validate the recorded params against the current catalogue before replay.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `action.batch` | Batch… |  | {commands: [{command, params}] (the action's steps), source?: folder (default) \| datasets, folder? (required for folder: the source folder), includeSubdirs?: false, destination?: none (defa… |  |

## `assets` (6)

Assets are reusable exported items. Name them so downstream skills can find them.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `assets.add` | Collect for Export | Object > Collect for Export | {ids?: [id…] (default: the selected objects; a layer id collects the art under it, including in its sublayers), multiple?: true (an asset per object; false: one asset of them all), name?: (… | disabled in catalogue snapshot |
| `assets.export` | Export Assets |  | {assets?: [asset id…] (default all), folder?, zip?, openLocation?, formats?, preset?, settings?, prefix?, subfolders?, antiAlias?} each asset's art alone, cropped to it, in every format row… | disabled in catalogue snapshot |
| `assets.list` | Assets |  | {} → {assets: [{id, name, nodes: [id…], bounds: [x, y, width, height] \| null (the crop: the bounds the renderer measures for what its art draws, effects included)}]} the Asset Export panel'… | disabled in catalogue snapshot |
| `assets.remove` | Remove Asset |  | {assets: [asset id…]} take assets out of the Asset Export panel (their art stays) → {removed: n} | disabled in catalogue snapshot |
| `assets.rename` | Rename Asset |  | {asset: id, name} rename an asset (its files' names) | disabled in catalogue snapshot |
| `assets.settings.set` | Asset Export Settings |  | {exportPreset?: (a preset of document.exportPresets.list: its formats or preset, its format settings over the saved ones, its prefix (none when it has none), its folders (or subfolders: row… | disabled in catalogue snapshot |

## `command` (1)

Command-palette helpers. They do not replace reading the catalogue.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `command.batch` | Batch |  | {label?, commands: [{command, params}], artboard?: index (the active artboard; the app passes it: each edit.pasteInPlace, edit.pasteInFront, edit.pasteInBack, object.align, object.distribut… | disabled in catalogue snapshot |

## `css` (3)

CSS export extracts style rules for web use. Treat it as generated code, not a design master.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `css.export` | Export CSS |  | {path?, scope?: selection\|all (default selection; ids? picks the objects), …options as css.selection, id?: object id (default: the selection)} write the CSS (css.selection, or css.generate … | disabled in catalogue snapshot |
| `css.generate` | Generate CSS |  | {…options as css.selection} css.selection of every object in the document | disabled in catalogue snapshot |
| `css.selection` | CSS Properties |  | {ids?\|id?: [id…] (default: the selection), units?: px\|pt\|mm\|cm\|in (default px; 1 px = 1 pt, as in SVG export), position?: false (position: absolute, left and top from the artboard's top-lef… | disabled in catalogue snapshot |

## `dataset` (12)

Datasets are variable-data records. Validate row count and final rendered files, not only the dataset.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `dataset.capture` | Capture Data Set | Window > Variables | {name?} record what the bound objects hold right now as a new dataset (Data Set 1…), and make it the active one; a frame of threaded text holds its whole story, every frame's text in thread… | disabled in catalogue snapshot |
| `dataset.delete` | Delete Data Set | Window > Variables | {names?} delete datasets (default: the active one) | disabled in catalogue snapshot |
| `dataset.export` | Export Data Sets… | Window > Variables | {path?} write every dataset as CSV (header: one column per variable and no dataset names: `#Name` for a visibility variable, `@Name` for an image variable, and the name alone for a text or … | disabled in catalogue snapshot |
| `dataset.import` | Import Data Sets… | Window > Variables | {path? \| data? \| dataBase64? \| csv?} replace every dataset with the rows of a CSV, comma- or tab-separated, in UTF-16 with a byte-order mark, UTF-8 or else Windows-1252 (header: one variabl… | disabled in catalogue snapshot |
| `dataset.list` | List Data Sets |  | {} → datasets with their values, the active one, and which rows the art still matches | disabled in catalogue snapshot |
| `dataset.new` | New Data Set… | Window > Variables | {name, values?: {variable: value}} add a dataset | disabled in catalogue snapshot |
| `dataset.next` | Next Data Set | Window > Variables | {} apply the next dataset, wrapping | disabled in catalogue snapshot |
| `dataset.prev` | Previous Data Set | Window > Variables | {} apply the previous dataset, wrapping | disabled in catalogue snapshot |
| `dataset.rename` | Rename Data Set | Window > Variables | {name, newName} rename a dataset | disabled in catalogue snapshot |
| `dataset.select` | Select Data Set | Window > Variables | {name} apply a dataset in one undo step (none when it leaves the document as it was), deselecting every selected object left hidden or locked (the key object too); a text value bound to a f… | disabled in catalogue snapshot |
| `dataset.set` | Edit Data Set… | Window > Variables | {name, newName?, values?: {variable: value}} replace a dataset's values; a variable left out loses its value in this row. `newName` also renames the dataset in the same undo step, refused w… | disabled in catalogue snapshot |
| `dataset.update` | Update Data Set | Window > Variables | {all?: bool} write what the bound objects hold now into the active dataset, for each variable the dataset holds; a variable whose objects report no value (locked, inside a locked layer or g… | disabled in catalogue snapshot |

## `document` (35)

Document commands inspect/serialize/export the whole document. `document.export` is the main delivery path; `document.exportPdf`/`exportEps`/`exportDxf` are format-specific. Check `document.formats` for installed exporters.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `document.activate` | Activate Document |  | {index} |  |
| `document.dxfInfo` | DXF Info |  | {path} or {name?, dataBase64} what a DXF drawing holds → {version (2018, R12…), units (its drawing unit: Millimeters, Inches, Unitless…), layouts: ["Model", paper layouts…], layers: [name…]… |  |
| `document.export` | Export Document |  | {path?, format?: svg\|svgz\|pdf\|ai\|png\|jpg\|webp\|gif\|png8\|txt\|dxf\|eps\|emf\|wmf\|tiff\|bmp\|tga\|psd\|vectorcraft\|template (default: from the path's extension, else png; png8 writes an indexed .png; … | Main delivery command: `path`, `format`, `ppi`/`scale`, `artboard(s)`, `selectedOnly`, plus nested `svg`/PDF options. `ppi` wins over `scale`.; disabled in catalogue snapshot |
| `document.exportDxf` | Export DXF |  | {path?, version?: R12\|R13\|R14\|2000\|2004\|2007\|2010\|2013\|2018 (default), unit?: mm (default; any unit name: pt, in, cm…), scale?: 1 (drawing units per unit), scaleLineweights?: false, colors?… | disabled in catalogue snapshot |
| `document.exportEps` | Export EPS |  | {path?, level?: 2\|3 (default; PostScript language level: 3 writes smooth gradients and masks transparent image pixels out, 2 steps gradients and writes those pixels white), previewFormat?: … | EPS is a legacy print exchange; transparency/effects may flatten. Keep the SVG/PDF master.; disabled in catalogue snapshot |
| `document.exportForOffice` | Save for Office Documents… | File | {path?, ppi?: 150 (72, 150, 300… pixels per inch), transparent?: false (else on white), artboard?: 0, acknowledgeLoss?: bool (write over the file the document was read from although reading… | disabled in catalogue snapshot |
| `document.exportForScreens` | Export for Screens | File > Export | {folder?, zip?: false (one .zip of every file, each deflated or stored, whichever is smaller: no folder → {name, dataBase64, bytes, files: [name…]}; with a folder it is written there → {pat… | disabled in catalogue snapshot |
| `document.exportForWeb` | Save for Web |  | {path?, preset?: a webExport.presets name (its settings, then these keys), format?: gif (default)\|jpg\|png8\|png24, reduction?: perceptual\|selective (default)\|adaptive\|web\|blackWhite\|gray (gi… | disabled in catalogue snapshot |
| `document.exportForWeb.preview` | Save for Web Preview |  | {…the settings of document.exportForWeb (preset?, format?…), slice?: n (1-based, from slice.list; default the whole image), kbps?: 56.6 (connection speed for the download time), image?: fal… | disabled in catalogue snapshot |
| `document.exportPdf` | Export PDF |  | {path?, preset?: "VectorCraft Default" (built-in or saved: pdf.preset.list), artboard? \| artboards?: [i…] \| range?: "1-3, 5" (1-based; default all, one page each), standard?: none\|pdfA2b\|pd… | PDF-specific export; check fonts, transparency and colour space. A PDF that looks right on screen is not colour proof.; disabled in catalogue snapshot |
| `document.exportPresets.delete` | Delete Export Preset |  | {name} delete a saved batch export preset (built-in ones stay) → {deleted} |  |
| `document.exportPresets.export` | Export Export Presets |  | {names?: [preset names, built-in ones too] (default: every saved preset), path?} write the presets as a .vcexportpresets file (JSON); more than 1000 presets or a file larger than 4194304 by… |  |
| `document.exportPresets.import` | Import Export Presets |  | {path? \| data?: file text \| dataBase64?, replace?: false (replace saved presets of the same names; else the imported ones get a number)} add the presets of a .vcexportpresets file (as docum… |  |
| `document.exportPresets.list` | Export Presets |  | {} → {presets: [{name, builtIn, settings}]} the built-in batch export presets (Logo Package, Print-Ready PDF), then the saved ones; any name works as document.exportForScreens' exportPreset |  |
| `document.exportPresets.save` | Save Export Preset |  | {name, settings: {formats, settings, preset, name, prefix, counterStart, counterPer, folders, subfolders, includeBleed, includeArtboardFill, antiAlias, folder, fullDocument} (as document.ex… |  |
| `document.exportSelection` | Export Selection… | File | {path?, format?: png\|jpg\|webp\|svg\|svgz\|pdf\|ai\|gif\|png8\|tiff\|bmp\|tga\|psd\|txt\|dxf\|eps\|emf\|wmf\|vectorcraft\|template (default: from the extension, else png), scale?: 1, …the format's options} t… | disabled in catalogue snapshot |
| `document.exportSettings` | Export for Screens Settings |  | {} → {settings}: the document.exportForScreens params the document last exported with ({} when never; saved with the document, the dialog reopens on them) | disabled in catalogue snapshot |
| `document.find` | Find Objects |  | {name?: substring of the Layers panel name, kind?: panel label such as Group; Path; Type or Image (exact), text?: substring of type content, within?: [x, y, width, height] (an object's geom… | disabled in catalogue snapshot |
| `document.formats` | File Formats |  | {} → {formats: [{id, label, extensions, mime, read, write, raster, options: {name: {type, default, description}}, plugin?: the id of the exporter plug-in that adds the format (its id is plu… |  |
| `document.info` | Document Info | Window > Document Info | {selectionOnly?, category?: document\|objects\|graphicStyles\|brushes\|spotColors\|patterns\|gradients\|symbols\|fonts\|fontDetails\|linkedImages\|embeddedImages\|repeats (only that one in sections and… | disabled in catalogue snapshot |
| `document.inspect` | Inspect Document |  | {depth?, childLimit?, ids?: [id…] (list just these nodes, of any level, in this order, under `nodes` in place of `layers`; an unknown id is an error; at most 10000), kind?: panel label such… | disabled in catalogue snapshot |
| `document.json` | Document JSON |  | {} → complete document model | disabled in catalogue snapshot |
| `document.node` | Inspect Object |  | {id, summary?: compact summary, depth?: child levels in the summary (default all), childLimit?: children shown per node (default all; a level that shows fewer reports childCount)} → one obj… | disabled in catalogue snapshot |
| `document.open` | Open Document |  | {path \| name \| dataBase64 (a file's path, or its name with its bytes), pages?: "2-3, 5" (PDF/.ai: 1-based, default all; one artboard each) \| page?: n, cropTo?: bounding\|art\|crop (default)\|t… |  |
| `document.pdfInfo` | PDF Info |  | {path \| name? \| dataBase64 (a file's path, or its bytes), password?, thumbnail?: page (1-based), thumbnailSize?: 160 (px, longest side), cropTo?: crop (the thumbnail's box)} → {pages, needs… |  |
| `document.pdfSettings` | PDF Settings |  | {preset?, includeDocument?: false, …options of document.exportPdf} → {settings (the preset with the options applied), presets: [name…], changed: [{option: "compression.compressText", value}… |  |
| `document.rasterEffectsSettings` | Document Raster Effects Settings… | Effect | {resolution?: ppi (1–2400) \| "screen" (72) \| "medium" (150) \| "high" (300), colorModel?: "rgb"\|"cmyk" (the document's mode)\|"grayscale"\|"bitmap", background?: "transparent"\|"white", antiAli… | disabled in catalogue snapshot |
| `document.resetRulerOrigin` | Reset Ruler Origin |  | {artboard?: index=0} reset the rulers' zero point to that artboard's top-left corner (with artboard rulers, that artboard's own zero point) | disabled in catalogue snapshot |
| `document.rulerOrigin` | Ruler Origin |  | {artboard?: index=0 (the active artboard, which artboard rulers measure from)} → {x, y} the rulers' zero point, in absolute document points | disabled in catalogue snapshot |
| `document.save` | Save Document |  | {path?, format?: vectorcraft\|template\|pdf\|svg\|svgz\|ai\|eps (default: the path's extension, else the document's own format), options?: {…the format's options, see file.formatOptions; default:… | disabled in catalogue snapshot |
| `document.serialize` | Serialize Document |  | {format?: vectorcraft (default)\|template\|svg\|svgz\|pdf\|ai\|png\|jpg\|webp\|gif\|png8\|txt\|dxf\|eps\|emf\|wmf\|tiff\|bmp\|tga\|psd (ait, a .ait template, is written by file.saveAsTemplate), …the format's … | disabled in catalogue snapshot |
| `document.setRulerOrigin` | Ruler Origin |  | {x, y, artboard?: index=0} set the rulers' zero point in absolute document points: the document's with global rulers, that artboard's with artboard rulers (it moves with the artboard); art,… | disabled in catalogue snapshot |
| `document.setUnits` | Units | File > Document Setup | {units: "Points"\|"Picas"\|"Inches"\|"Millimeters"\|"Centimeters"\|"Pixels"\|"Feet & Inches"\|"Meters"\|"Yards"\|"Feet"} the document's units: every length the UI shows and reads (General) | disabled in catalogue snapshot |
| `document.setup` | Document Setup |  | {units?: "Points"\|"Inches"\|"Millimeters"\|…, bleed?: pt (all sides)\|[top, bottom, left, right]\|{top?, bottom?, left?, right?} (0–72 pt), outlineImages?: bool (show images in Outline mode), h… | disabled in catalogue snapshot |
| `document.switchUnits` | Switch Units |  | {} the document's units become the next of Points, Picas, Inches, Millimeters, Centimeters, Pixels, Feet & Inches, Meters, Yards and Feet (the order a right-click on a ruler lists them), Fe… | disabled in catalogue snapshot |

## `file` (28)

File commands create/open/save/place documents. `file.place` uses the raster's physical size (ppi), not pixel count; `file.saveAs` changes the working file, `file.saveCopy` preserves the original.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `file.close` | Close | File | {index?} | disabled in catalogue snapshot |
| `file.closeAll` | Close All | File | {} → {closed} | disabled in catalogue snapshot |
| `file.documentColorMode` | Document Color Mode | File > Document Color Mode | {mode: "cmyk"\|"rgb", convert?: true (convert every color of the art (opacity masks, effect colors and graphs' series and label paints included), symbols, graph designs, pattern tiles, graph… | disabled in catalogue snapshot |
| `file.export` | Export… |  | {…as document.export} = document.export {path?, format?, artboard?, range?, scale?, …} (no path → dataBase64) |  |
| `file.exportForScreens` | Export for Screens… |  | {folder?, zip?, artboards? \| range? \| fullDocument? \| assets?, includeBleed?, includeArtboardFill?, subfolders?, preset?, formats?, settings?, prefix?} = document.exportForScreens (no folde… |  |
| `file.formatOptions` | Format Options |  | {format?: a writable format id or ait (default: the document's own)} → {id, label, extensions, mime, read, write, raster, options: {name: {type, default, description, value}}, saveFormats: … |  |
| `file.info` | File Info… | File | {title?, author?, authorTitle?, description?, keywords?: [string…]\|"a, b" (each once), rating?: 0–5, copyrightStatus?: "unknown"\|"copyrighted"\|"publicDomain", copyrightNotice?, copyrightUrl… | disabled in catalogue snapshot |
| `file.list` | List Folder |  | {path} the files and folders in folder `path`, by name: what an agent may open there (held to the automation read root when one is in force) → {path, entries: [{name, kind: file\|folder\|link… |  |
| `file.new` | New… | File | {preset?: a name from file.newPresets (start from it; the other params change it), name?\|title?: document name (default Untitled-N), width?: pt=612\|"210 mm", height?: pt=792, units?: "Pixel… |  |
| `file.newFromTemplate` | New from Template… | File | {path} or {name, dataBase64}: open a template (or any readable file) as a new untitled document → {index, title, format, warnings} |  |
| `file.newPresets` | New Document Presets |  | {category?: "Recent"\|"Saved"\|"Mobile"\|"Web"\|"Print"\|"Film & Video"\|"Art & Illustration"\|"Branding"\|"Social"} the New Document presets by category (Recent: the last sizes used; Saved: the us… |  |
| `file.newPresets.delete` | Delete Preset |  | {name} delete a saved New Document preset → {deleted} | disabled in catalogue snapshot |
| `file.newPresets.save` | Save Preset |  | {name, preset?: start from this preset, …settings as file.new (default: Letter in prefs unitsGeneral)} save New Document settings as a user preset (the Saved category; same name = replace) … |  |
| `file.open` | Open… |  | {path} open any readable file (see document.formats) as a new document; templates open untitled |  |
| `file.package` | Package |  | {folder?, name?: (default: "<document> Folder"), copyLinks?: true, linksFolder?: true (the linked files go in Links/, else next to the document), relink?: true (the packaged document links … | disabled in catalogue snapshot |
| `file.place` | Place… | File | {path \| name \| dataBase64 (a file's path, or its name with its bytes), link?: true (a raster image keeps its file's path; a VectorCraft document at path becomes one locked placed document s… | Places raster at its physical size (ppi), not pixel count; SVG/PDF become placed/locked or editable per `link`. Use `rect` for exact fit.; disabled in catalogue snapshot |
| `file.place.info` | Placed File Info |  | {path \| name \| dataBase64 (a file's path, or its name with its bytes), page?, crop?, password?, thumbnail?: px, link?: bool, dxf?: {…} (both as file.place)} what file.place would place, wit… |  |
| `file.place.queue` | Load Place Cursor |  | {paths?: [path…], files?: [{name, dataBase64}…], link?, template?, page?, crop?, text?, dxf?, thumbnail?: px} load the place cursor (the `place` tool) with up to 100 files (as file.place re… | disabled in catalogue snapshot |
| `file.print` | Print |  | {preset?: name (as print.setup's: its settings instead of the document's; the saved settings stay), settings?: {…settings of print.setup} (over the document's or the preset's), includeArtbo… | disabled in catalogue snapshot |
| `file.recovery.discard` | Discard Recovered Documents |  | {file?} delete a copy left behind by a crash (default: every one; copies of open documents and of running VectorCraft apps stay) → {discarded: [file…]} | disabled in catalogue snapshot |
| `file.recovery.list` | Recovery Data |  | {} the recovery copies in the store → {copies: [{file ("<area>/<name>"), title, path (the document's file, if it had one), format, saved (Unix seconds or null), open (the copy of a document… | disabled in catalogue snapshot |
| `file.recovery.restore` | Restore Recovered Documents |  | {file?} open a copy left behind by a crash (default: every one; a running VectorCraft's copies are never taken) as a new document titled "<name> [Recovered]": modified, and Save asks where … | disabled in catalogue snapshot |
| `file.recovery.save` | Save Recovery Data |  | {} write a recovery copy of every modified document changed since its last copy, in this app's own area of the store (the app does this every autosaveInterval minutes while autosaveRecovery… | disabled in catalogue snapshot |
| `file.revert` | Revert | File | {confirmed?: bool (the app's own: it asks first, then runs the command with it)} discard the changes: reload the saved file into the same tab (history cleared; the tab keeps its place and v… | disabled in catalogue snapshot |
| `file.save` | Save |  | {…as document.save} = document.save {path?, format?, options?, svg?: {…SVG options}}: .vectorcraft, .ai (a PDF that reopens editable), .pdf, .svg or .svgz (default: the document's own path … |  |
| `file.saveAs` | Save As… | File | {…as document.save} {path?, format?: vectorcraft\|template\|pdf\|svg\|svgz\|ai\|eps (default: the path's extension, else the document's own; ait, a .ait template, is written by file.saveAsTemplat… | Changes the working file path; `file.saveCopy` preserves the source. Never save over a master.; disabled in catalogue snapshot |
| `file.saveAsTemplate` | Save as Template… | File | {…as document.save} {path? (saved with the format's extension: one naming another format is replaced, and one is added to a name without it), format?: template (default) \| ait (also when fo… | disabled in catalogue snapshot |
| `file.saveCopy` | Save a Copy… | File | {…as document.save} {path?, format?, options?, precision?} write a copy; the document keeps its path, title and modified state → {path, format, bytes, warnings}; no path → {dataBase64, form… | disabled in catalogue snapshot |

## `help` (5)

Help/menu commands expose reference information. They do not change the artwork.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `help.appPage` | VectorCraft on getartcraft.com | Help | {} → {url} this app's page |  |
| `help.discord` | Join Our Discord | Help | {} → {url} the ArtCraft community Discord |  |
| `help.github` | VectorCraft on GitHub | Help | {} → {url} source code, issues and releases |  |
| `help.links` | Links |  | {} → {discord, website, appPage, github} |  |
| `help.website` | ArtCraft Website | Help | {} → {url} |  |

## `importMatches` (3)

Import matching maps incoming files to placed art. Verify which file matched which placement.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `importMatches.list` | Import Matches |  | {kind?: name\|key\|modifiers, query?: text (in the name, target or label; any case)} the matches the user confirmed when importing other apps' files (shortcut sets), kept with the preferences… |  |
| `importMatches.reset` | Forget Import Matches |  | {kind?: name\|key\|modifiers} forget the import matches, all of them or those of one kind → {removed} |  |
| `importMatches.set` | Remember Import Matches |  | {matches: [{kind: name\|key\|modifiers, name: as the file writes it (codes in decimal), target: a command id, tool:<id> or panel:<id> (name), a key as Edit › Keyboard Shortcuts writes it (key… |  |

## `library` (16)

Libraries share assets between documents. Export a copy when delivering to someone without the library.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `library.add` | Add to Library |  | {library?: id or name (default: the current library, made when there is none), kind: graphic\|fillColor\|strokeColor\|fillGradient\|strokeGradient\|fillPattern\|strokePattern\|charStyle\|paraStyle,… | disabled in catalogue snapshot |
| `library.create` | Create New Library |  | {name?: "My Library"} a new empty library (its file in the library folder), made the current one → {id, name} |  |
| `library.createGroup` | New Library Group |  | {library?, name?: "Group" (a name the library's groups have, ignoring case, gets a number), items?: [{kind, item}] (moved into it out of their groups)} a new group of items, after the other… |  |
| `library.delete` | Delete Library |  | {library?} delete a library (default: the current one) and its file; not undoable → null |  |
| `library.deleteGroup` | Delete Library Group |  | {library?, group: name} delete a group: its items stay in the library, ungrouped → {library, ungrouped: how many} |  |
| `library.export` | Export Library |  | {library?: id or name (default: the current library), path?} write a library (its colours, gradients, patterns, styles, graphics with their art and thumbnails, and groups) as a .vclibrary f… |  |
| `library.get` | Library |  | {library?: id or name (default: the current library)} → {id, name, graphics: [{id, name, width, height, thumbnail: PNG base64}], colors: [{name, hex, color}], gradients: [{name, gradient: {… |  |
| `library.import` | Import Library |  | {path? \| data?: file text \| dataBase64?, name?: the library's name (default: the file's)} add the library of a .vclibrary file (as library.export writes) as a new library, made the current … |  |
| `library.list` | Libraries |  | {} → {libraries: [{id, name, graphics, colors, gradients, patterns, charStyles, paraStyles, groups} (counts)], current: the current library's id or null, folder: the library folder, or null… |  |
| `library.moveGroup` | Move Library Group |  | {library?, group: name, to: index} move a group to position `to` of the library's groups (0 = first; past the end: last), as dragging its header in the Libraries panel does → {library, grou… |  |
| `library.moveItem` | Move Library Item to Group |  | {library?, kind, item: name (graphic: id or name), group?: name (null or none: out of its group), before?: item \| after?: item (an item of the same kind, named as `item` is)} put an item in… |  |
| `library.removeItem` | Delete Library Item |  | {library?, kind, item: name (graphic: id or name)} delete an item (out of its group too) → null |  |
| `library.rename` | Rename Library |  | {library?, name} rename a library (default: the current one) → {id, name} |  |
| `library.renameGroup` | Rename Library Group |  | {library?, group: name, name} rename a group (another group's name, ignoring case, is an error) → {library, group: the new name} |  |
| `library.setCurrent` | Show Library |  | {library: id or name} the library the Libraries panel shows, which library commands without a `library` act on → {id} |  |
| `library.use` | Use Library Item |  | {library?, kind, item: name (graphic: id or name), center?: [x, y] (graphic; default: the first artboard's centre), to?: fill\|stroke (colors, gradients, patterns; default: the kind's), reco… | disabled in catalogue snapshot |

## `links` (11)

Linked files can change outside the document. Update links and package assets before delivery.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `links.check` | Check Links |  | {ids?: [image or placed document ids] (default: every linked image and placed document)} where each linked file is and whether it changed since it was read → {links: [{name, path, status: o… | disabled in catalogue snapshot |
| `links.embed` | Embed Image |  | {ids?: [image or placed document ids] (default: the selected linked ones)} break the links (the Links panel's Break Link): images keep the linked files' pixels in the document; a placed doc… | disabled in catalogue snapshot |
| `links.findFiles` | Find Linked Files |  | {folder?: an absolute path, ids?: [image or placed document ids] (default: the active document's missing links), maxSeconds?: 60 (1 to 600), stop?: false (true: stop the last search)} with … |  |
| `links.goTo` | Go To Link |  | {id?} select image or placed document `id` (default: the first selected one); the Links panel scrolls it into view → {id, bounds: [x0, y0, x1, y1]} | disabled in catalogue snapshot |
| `links.info` | Link Info |  | {id?} an image's or placed document's Link Info (default: the one selected) → image.info's fields (id, name, linked, link, colorMode, pixelWidth, pixelHeight, width, height) and status: ok\|… | disabled in catalogue snapshot |
| `links.list` | Links |  | {show?: all (default)\|missing\|modified\|embedded, sort?: name\|kind (file format)\|status (missing, modified, ok, embedded); default: stacking order; top first} every image object and placed d… | disabled in catalogue snapshot |
| `links.placementOptions` | Placement Options |  | {ids?: [image or placed document ids] (default: the selected ones), preserve?: transforms\|bounds (default)\|fileDimensions\|fit\|fill, align?: topLeft\|top\|topRight\|left\|center (default)\|right\|… | disabled in catalogue snapshot |
| `links.relink` | Relink |  | {ids?: [image or placed document ids] (default: the selected ones; with folder and nothing selected, every missing link), path \| folder, copy?: false (with path, for images of a saved docum… | disabled in catalogue snapshot |
| `links.unembed` | Unembed |  | {id?: an embedded image (default: the one selected), path?} write the image's pixels to the file at path (PNG, JPEG, GIF or WebP as stored, other images as PNG; a path ending in .png/.jpg/.… | disabled in catalogue snapshot |
| `links.update` | Update Links |  | {ids?: [image or placed document ids] (default: the linked images whose file was modified or is showing its preview, and placed documents whose file was modified)} read their linked files a… | disabled in catalogue snapshot |
| `links.updateChanged` | Update Changed Links |  | {} read again the active document's linked files that changed on disk since they were last seen (size or modification time), whatever Preferences → File Handling → Update Links says; the de… | disabled in catalogue snapshot |

## `pdf` (5)

PDF commands create/inspect PDF output. Check fonts, transparency flattening and colour space before sending to a printer.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `pdf.preset.delete` | Delete PDF Preset |  | {name} delete a saved preset (built-in ones stay) → {deleted: name} |  |
| `pdf.preset.export` | Export PDF Presets |  | {names?: [preset names, built-in ones too] (default: every saved preset), path?} write the presets as a .vcpdfpresets file (JSON) → {path, count}; without path → {data: the file's text, cou… |  |
| `pdf.preset.import` | Import PDF Presets |  | {path? \| data?: file text \| dataBase64?, replace?: false (replace saved presets of the same names; else imported ones whose name is taken get a number)} add the presets of a .vcpdfpresets f… |  |
| `pdf.preset.list` | PDF Presets |  | {} → {presets: [{name, builtIn, supported (the writer produces its standard), description, settings (as document.pdfSettings)}]} the built-in presets (VectorCraft Default first), then the s… |  |
| `pdf.preset.save` | Save PDF Preset |  | {name?: (default: a new "PDF Preset N"), newName?: rename it, description?, preset?: the preset to start from (default: the saved preset `name`, else VectorCraft Default), …options of docum… |  |

## `plugin` (7)

Plugins extend the engine. A plugin's exporter format is `plugin.<id>`; query `plugin.info` before use.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `plugin.info` | Plug-in Info |  | {id} → plugin.list's entry plus {manifest, defaults, lastError (a live effect's last failure, null)} |  |
| `plugin.inspect` | Inspect Plug-in |  | {path: a .wasm file (desktop) \| dataBase64: the module, name?: the file name shown as its source (with dataBase64)} validate a WebAssembly plug-in without installing it → the plugin.list en… |  |
| `plugin.install` | Install Plug-in |  | {path: a .wasm file (desktop) \| dataBase64: the module (+ name?: shown as its source), replace?: bool (true: a plug-in with the same id is replaced), name?: file name (with dataBase64), all… |  |
| `plugin.list` | List Plug-ins |  | {} → {plugins: [{id, name, version, kind: "filter"\|"effect"\|"exporter", author, description, params (doc), paramsSchema, effect? (the effect id of a live effect: plugin.<id>), format? and e… |  |
| `plugin.reload` | Reload Plug-ins | Object > Plug-ins | {path?: a folder (default: the Additional Plug-ins Folder preference)} install every *.wasm in it (desktop; a bad module is reported and skipped) → {folder, loaded: [id], failed: [{file, er… |  |
| `plugin.remove` | Remove Plug-in |  | {id} uninstall a plug-in (its live effects then leave the geometry as it is) → {removed} |  |
| `plugin.run` | Run Plug-in |  | {id, params?: {…} (the plug-in's parameters; or give them as top-level keys; missing ones take their defaults, see plugin.info), ids?: [..] (default: the selection), …the plug-in's paramete… | disabled in catalogue snapshot |

## `prefs` (4)

Preferences change app behaviour, not the document. Avoid relying on them for reproducible output.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `prefs.get` | Get Preferences |  | {key?} → the value of one preference (or preference group: eyedropper), or {prefs: {…all…}} |  |
| `prefs.list` | List Preferences |  | {} → [{key, category, section, label, kind, value, …}] every preference |  |
| `prefs.reset` | Reset Preferences |  | {category?} reset one category (or everything) to defaults |  |
| `prefs.set` | Set Preference |  | {key, value} or {values: {key: value, …}} set preferences (validated; see prefs.list; lengths in pt or strings with a unit; unitsGeneral also sets the active document's units, one undo step… |  |

## `print` (9)

Print commands set print options. They do not prove a physical print; colour and stock need a proof.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `print.presets.delete` | Delete Print Preset |  | {name} delete a saved preset ([Default] stays) → {deleted: name} |  |
| `print.presets.export` | Export Print Presets |  | {names?: [preset names, [Default] too] (default: every saved preset), path?} write the presets as a .vcprintpresets file (JSON) → {path, count}; without path → {data: the file's text, count} |  |
| `print.presets.import` | Import Print Presets |  | {path? \| data?: file text \| dataBase64?, replace?: false (replace saved presets of the same names; else imported ones whose name is taken get a number)} add the presets of a .vcprintpresets… |  |
| `print.presets.list` | Print Presets |  | {} → {presets: [{name, builtIn, settings (as print.setup's), changed: [{option, value}] (how it differs from [Default])}]} [Default] (the default print settings, protected) first, then the … |  |
| `print.presets.save` | Save Print Preset |  | {name?: (default: a new "Print Preset N"), newName?: rename it, preset?: the preset to start from (default: the saved preset `name`, else [Default]), settings?: {…settings of print.setup} (… |  |
| `print.preview` | Print Preview |  | {preset?: name (as print.setup's: its settings instead of the document's), settings?: {…settings of print.setup} (over the document's or the preset's)} → {pages (copies included), sheets: [… | disabled in catalogue snapshot |
| `print.setup` | Print Setup |  | {preset?: name ([Default] or a saved print preset, any case: print.presets.list; its settings replace the document's, as choosing it in the Print dialog does), settings?: {copies: 1 (1–999)… | disabled in catalogue snapshot |
| `print.tiling` | Print Tiling Pages |  | {settings?: {…settings of print.setup} (over the document's)} the pages as View → Show Print Tiling draws them, from print.preview's layout → {tileOrigin, pages: [{artboard (0-based; null w… | disabled in catalogue snapshot |
| `print.tiling.set` | Print Tiling |  | {origin: [x, y] (document point: the top-left corner of the first page's imageable area), artboard? (0-based: the artboard it is measured from; default the printed artboard containing origi… | disabled in catalogue snapshot |

## `script` (1)

Scripts run host code. They are powerful and untrusted; run only vetted scripts in an isolated environment.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `script.check` | Check Script |  | {path? \| data?: the script's text \| dataBase64?, name?: the file's name (default: the path's; with a path, only the reply's name), includes?: false (with a path: also check the files its #i… |  |

## `shortcutSet` (1)

Keyboard shortcut sets are UI-only; automation must call command ids.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `shortcutSet.read` | Read Shortcut Set File |  | {path? \| data?: the file's text \| dataBase64?, name?: the file's name (default: the path's)} read a shortcut set another app saved as text (.kys, starting "/Menus {") without changing anyth… |  |

## `variable` (14)

Variables drive data-driven artwork. Test one record and check every text/fill mapping before a batch.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `variable.bind` | Bind Variable | Window > Variables | {variable, ids?} bind objects (default: the selection) to a variable; text needs type, image needs an image object, graph needs a graph root, locked art is refused. An object may hold sever… | disabled in catalogue snapshot |
| `variable.define` | New Variable… | Window > Variables | {name, kind: text\|visibility\|image\|graph} define a variable (graph: CSV data on a graph root); refused while the variables are locked | disabled in catalogue snapshot |
| `variable.delete` | Delete Variable | Window > Variables | {names?} delete variables with their bindings and values (default: the highlighted one); refused while the variables are locked | disabled in catalogue snapshot |
| `variable.highlight` | Highlight Variable |  | {variable?} highlight one Variables panel row (a click); what the panel's Delete, Options… and Select Bound Object act on. An empty or missing `variable` clears it. Not an undo step → {vari… | disabled in catalogue snapshot |
| `variable.list` | List Variables |  | {} → variables with kinds and binding counts, and whether they are locked → {variables, locked} | disabled in catalogue snapshot |
| `variable.loadLibrary` | Load Variable Library… | Window > Variables | {path? \| xml? \| dataBase64?} replace the document's variables and data sets with a variable library's (XML: `variableSets` › `variableSet` › `variables` of `variable` elements with `varName… | disabled in catalogue snapshot |
| `variable.lock` | Lock Variables | Window > Variables | {locked?: bool} lock or unlock the variables (default: toggle); saved with the document; a change is one undo step. While locked, variable.define, variable.delete, variable.rename, variable… | disabled in catalogue snapshot |
| `variable.makeGraphDynamic` | Make Graph Dynamic | Window > Variables | {} define a graph variable over the selected graph root(s), named after it and bound to it; each dataset row supplies CSV as graph.setData; refused while the variables are locked | disabled in catalogue snapshot |
| `variable.makeImageDynamic` | Make Image Dynamic | Window > Variables | {} define an image variable over the selection, named after it and bound to it; refused while the variables are locked | disabled in catalogue snapshot |
| `variable.makeTextDynamic` | Make Text Dynamic | Window > Variables | {} define a text variable over the selection, named after it and bound to it; refused while the variables are locked | disabled in catalogue snapshot |
| `variable.makeVisibilityDynamic` | Make Visibility Dynamic | Window > Variables | {} define a visibility variable over the selection, named after it and bound to it; refused while the variables are locked | disabled in catalogue snapshot |
| `variable.rename` | Rename Variable | Window > Variables | {name, newName} rename a variable, with its bindings and its values in every dataset; refused while the variables are locked | disabled in catalogue snapshot |
| `variable.saveLibrary` | Save Variable Library… | Window > Variables | {path?} write the document's text variables and every data set as a variable library, the XML that variable.loadLibrary reads: a `variable` element with `varName` and `trait="textcontent"` … | disabled in catalogue snapshot |
| `variable.unbind` | Unbind Variable | Window > Variables | {ids?, variable?} drop bindings (default: the selection): `variable` drops that one, else every variable the object has | disabled in catalogue snapshot |

## `webExport` (4)

Web export produces web-oriented assets. Use exact pixel/ppi settings and compare bytes; lossy formats can grow on flat art.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `webExport.presets.delete` | Delete Save for Web Preset |  | {name} delete a saved preset (built-in ones stay) → {deleted: name} |  |
| `webExport.presets.list` | Save for Web Presets |  | {} → {presets: [{name, builtIn, settings}]} the built-in presets, then the saved ones; any name works as `preset` in document.exportForWeb |  |
| `webExport.presets.save` | Save Save for Web Preset |  | {name, newName?: rename it, preset?: start from this preset (default: the saved preset `name`, else the defaults), settings?: {…}, …the settings of document.exportForWeb} create or change a… |  |
| `webExport.settings` | Save for Web Settings |  | {reset?: false, preset?, …the settings of document.exportForWeb} remember settings for the Save for Web dialog (it opens on them): the keys given change the remembered ones, a preset replac… |  |
