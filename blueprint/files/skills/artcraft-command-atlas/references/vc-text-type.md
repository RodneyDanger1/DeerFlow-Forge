# VectorCraft Text Type

Auto-generated from the installed 918-command catalogue (snapshot 2026-11-05). Every row is a real command id; params are abbreviated from the catalogue's own text. Read the full params string with `$VC commands` before running. Tips are practical notes, not substitutes for the schema.

Commands: **77** across 4 groups.

## Coverage

`charStyle` 10 · `paraStyle` 9 · `text` 35 · `type` 23

## `charStyle` (10)

Character styles store reusable glyph formatting. Apply them for consistency across a wordmark system.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `charStyle.apply` | Apply Character Style |  | {name, clearOverrides?, ids?\|id?, start?, end? (id with start and end: a Type tool range; character styles style it, paragraph styles apply to the paragraphs it touches)} → {count} | disabled in catalogue snapshot |
| `charStyle.delete` | Delete Character Style | Window > Type > Character Styles | {name} \| {names: [name…]} delete styles in one undo step (text keeps its look; never the Normal style) | disabled in catalogue snapshot |
| `charStyle.duplicate` | Duplicate Character Style | Window > Type > Character Styles | {name} → {name} | disabled in catalogue snapshot |
| `charStyle.edit` | Edit Character Style |  | {name, to, attrs: {…}} replace name and sparse attributes in one undo step; users keep local overrides; changed numeric attrs: size 0.1..=1296 pt, explicit leading 0.1..=5000 pt, h/v scale … | disabled in catalogue snapshot |
| `charStyle.list` | Character Styles |  | {} → {styles: [{name, attrs, uses}]} | disabled in catalogue snapshot |
| `charStyle.new` | New Character Style | Window > Type > Character Styles | {name? (trimmed, as rename trims `to`), attrs?: {…} (default: selected text), id?, start?: byte, end?: byte} → {name}; a nonempty character range samples its first selected character; start… | disabled in catalogue snapshot |
| `charStyle.redefine` | Redefine Character Style | Window > Type > Character Styles | {name, id?, start?: byte, end?: byte} from selected text; nonempty character ranges sample their first selected character, start alone keeps insertion affinity, paragraph styles sample star… | disabled in catalogue snapshot |
| `charStyle.rename` | Rename Character Style |  | {name, to} | disabled in catalogue snapshot |
| `charStyle.setAttrs` | Character Style Options |  | {name, attrs: {…}} replace the style's attributes; users keep their overrides; changed numeric attrs: size 0.1..=1296 pt, explicit leading 0.1..=5000 pt, h/v scale 1..=10000%, baseline shif… | disabled in catalogue snapshot |
| `charStyle.unused` | Select All Unused | Window > Type > Character Styles | {} → {names: [the styles no text uses, in panel order; never the Normal style]} (the panel highlights them) | disabled in catalogue snapshot |

## `paraStyle` (9)

Paragraph styles store paragraph-level formatting (alignment, indents, spacing). Use for multi-line brand copy.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `paraStyle.apply` | Apply Paragraph Style |  | {name, clearOverrides?, ids?\|id?, start?, end? (id with start and end: a Type tool range; character styles style it, paragraph styles apply to the paragraphs it touches)} → {count} | disabled in catalogue snapshot |
| `paraStyle.delete` | Delete Paragraph Style | Window > Type > Paragraph Styles | {name} \| {names: [name…]} delete styles in one undo step (text keeps its look; never the Normal style) | disabled in catalogue snapshot |
| `paraStyle.duplicate` | Duplicate Paragraph Style | Window > Type > Paragraph Styles | {name} → {name} | disabled in catalogue snapshot |
| `paraStyle.list` | Paragraph Styles |  | {} → {styles: [{name, attrs, uses}]} | disabled in catalogue snapshot |
| `paraStyle.new` | New Paragraph Style | Window > Type > Paragraph Styles | {name? (trimmed, as rename trims `to`), attrs?: {…} (default: selected text), id?, start?: byte, end?: byte} → {name}; a nonempty character range samples its first selected character; start… | disabled in catalogue snapshot |
| `paraStyle.redefine` | Redefine Paragraph Style | Window > Type > Paragraph Styles | {name, id?, start?: byte, end?: byte} from selected text; nonempty character ranges sample their first selected character, start alone keeps insertion affinity, paragraph styles sample star… | disabled in catalogue snapshot |
| `paraStyle.rename` | Rename Paragraph Style |  | {name, to} | disabled in catalogue snapshot |
| `paraStyle.setAttrs` | Paragraph Style Options |  | {name, attrs: {…}} replace the style's attributes; users keep their overrides | disabled in catalogue snapshot |
| `paraStyle.unused` | Select All Unused | Window > Type > Paragraph Styles | {} → {names: [the styles no text uses, in panel order; never the Normal style]} (the panel highlights them) | disabled in catalogue snapshot |

## `text` (35)

Text commands manage content, styles, threading and font resolution. Character/paragraph styles are separate groups. Use `text.fontList` to see installed families and `text.missingFonts` before export.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `text.addFontFiles` | Add Font Files |  | {files: [paths the last text.findFontFiles search found] (1 to 1000)} copy the font files into VectorCraft's own Fonts folder (next to the preferences; the desktop app and vectorcraft-cli r… |  |
| `text.areaOptions` | Area Type Options… | Type | {ids?\|id?, width?: pt, height?: pt, rows?, columns?, gutter?: pt (between rows and columns), rowGutter?: pt\|null (between rows when it differs from gutter, which is then between columns; gu… | disabled in catalogue snapshot |
| `text.convertListToText` | Convert to Text |  | {ids?\|id?, start?: byte, end?: byte} (Type › Bullets and Numbering › Convert to Text: the paragraphs of the selected type, or of `ids`, or those a start/end range touches) the marker of eac… | disabled in catalogue snapshot |
| `text.create` | Create Text |  | {x, y, text, rotation?: deg (about x, y), vertical?: bool = false, size?: pt, font?: family, style? (default Regular, or the family's closest style when it has no Regular), color? (#rrggbba… | disabled in catalogue snapshot |
| `text.createInPath` | Area / Path Type |  | {path: id, mode: "area"\|"onPath", text?: "", vertical?: bool = false, at?: [x, y] (on-path start: nearest point), size?, font?, style?, color?, keepModel? (as text.create), fit?: none\|autoH… | disabled in catalogue snapshot |
| `text.discardEmpty` | Discard Empty Type |  | {id} remove text object `id` if it has no characters (what the Type tool does with point type it placed when editing ends). When nothing but that text changed since the step that created it… | disabled in catalogue snapshot |
| `text.editRange` | Edit Text |  | {id, start: byte, end: byte, insert?: string, runs?: [{text, style}], clear?: [id…] (other type objects whose whole text goes in the same edit, as when typing replaces a threaded story that… | disabled in catalogue snapshot |
| `text.findFontFiles` | Find Font Files |  | {folder?: an absolute path, fonts?: [{family, style?}] (1 to 1000; default: the active document's missing fonts, as text.missingFonts lists them), maxSeconds?: 60 (1 to 600), stop?: false (… |  |
| `text.fitHeadline` | Fit Headline | Type | {ids?\|id?} track the first line of area type so it fills the frame width → {tracking} | disabled in catalogue snapshot |
| `text.fontList` | Font List |  | {family?, style?} → {families: [names]} sorted: the bundled fonts, fonts added and the fonts installed on the system (none on the web), each the family's English (canonical) name for `text.… |  |
| `text.fonts` | Fonts in Document |  | {selectionOnly?} (the type in the art of the symbols in scope included: all of the document's, or those the selected instances show) → [{family, style, runs, objects, missing, status: exact… | disabled in catalogue snapshot |
| `text.getRange` | Get Text Range |  | {id, start?, end?, effective?: bool = false, story?: bool = false (the whole text of the threaded story `id` is a frame of, its frames in thread order; no `start` or `end`)} → {text, runs: … | disabled in catalogue snapshot |
| `text.glyphAlternates` | Glyphs |  | {id, start: byte (a character of it)} the alternate glyphs of that character in its font, what the Glyphs panel's Show › Alternates for Current Selection lists: from the font's OpenType GSU… | disabled in catalogue snapshot |
| `text.insertInline` | Insert Inline Symbol | Type | {id?: text id (default: the text the Type tool edits), at?: byte offset (default: the Type tool's selection, which it replaces; clamped to the text), symbol?: symbol name (default: the Symb… | disabled in catalogue snapshot |
| `text.missingFonts` | Missing Fonts |  | {} → {fonts: [{family, style, status: missing\|substitute, resolved: {family, style}}] (sorted by name; at most 1000), count, fontsNextToDocument?} the fonts the active document's type uses,… | disabled in catalogue snapshot |
| `text.replaceFont` | Replace Font |  | {from: {family, style?}, to: {family (any of its names; stored as the font's own family name), style?}, selectionOnly?} (style omitted: every style of the family / keep the closest style); … | Replaces a family across text objects. Use `text.missingFonts`/`text.fontList` first; record licence.; disabled in catalogue snapshot |
| `text.rescanFonts` | Refresh Font List |  | {} scan the system font folders again, for fonts installed or removed since the app started; text in a font that became available redraws in it, and text in a family that was removed redraw… |  |
| `text.reshapeArea` | Reshape Type Area |  | {id, anchors: [[subpath, anchor]…], dx, dy} or {items: [{id, anchors}…], dx, dy} move anchors of area type's frame (the type area) by dx, dy points, with their handles; the text reflows at … | disabled in catalogue snapshot |
| `text.reshapePath` | Reshape Type Path |  | {id, anchors: [[subpath, anchor]…], dx, dy} move anchors of type on a path's path by dx, dy points, with their handles; the start and end brackets keep their fractions of the path and the t… | disabled in catalogue snapshot |
| `text.setFormat` | Character / Paragraph |  | {ids?\|id?, kerning?: 1/1000 em\|"auto"\|"optical", baselineShift?: pt, hScale?: %, vScale?: %, rotation?: deg, underline?, strikethrough?, allCaps?, smallCaps?: bool, position?: "normal"\|"sup… | disabled in catalogue snapshot |
| `text.setGlyphAlternate` | Glyphs |  | {id, start: byte (a character of it), gid: glyph id\|null} draw that one character with another glyph of its font as one undo step, what a double-click in the Glyphs panel's Show › Alternate… | disabled in catalogue snapshot |
| `text.setRangeStyle` | Character |  | {id? (default: the one selected type object), start?: byte, end?: byte (default: all text), story?: bool = false (all the text of every frame of the threaded story `id` is a frame of, in on… | disabled in catalogue snapshot |
| `text.setStyle` | Character |  | {ids?\|id?, font?, style? (font alone: the style is kept when the new family has it, else its closest), size?: pt, leading?: pt\|"auto", tracking?: 1/1000 em, justify?: "auto" (the start of e… | disabled in catalogue snapshot |
| `text.setText` | Set Text |  | {id?\|ids?, text} replace the contents of text objects (keeps the first run's style) → {ids, overflow?: [id…] (area type and type on a path whose text no longer fits; left out when all fits)} | disabled in catalogue snapshot |
| `text.startList` | Bullets and Numbering |  | {id, at?: byte (default: the end of the text)} start a list from typed characters, what the Type tool runs when a space is typed on its own: when the text from the start of the paragraph th… | disabled in catalogue snapshot |
| `text.tabs.clear` | Clear All Tabs | Window > Tabs | {ids?\|id?, start?: byte, end?: byte} | disabled in catalogue snapshot |
| `text.tabs.get` | Tab Stops |  | {ids?\|id?, start?: byte} → {stops} of the first selected text object (its paragraph at `start`; default the first) | disabled in catalogue snapshot |
| `text.tabs.set` | Set Tab Stops | Window > Tabs | {stops: [{position: pt, align?: left\|center\|right\|decimal, leader?: ". ", alignOn?: "."}], ids?\|id?, start?: byte, end?: byte} replace the tab stops of the selected text (with a range: of t… | disabled in catalogue snapshot |
| `text.thread.add` | Thread Text |  | {from, to?, rect?: [x, y, width, height], at?: [x, y], before?} thread area type or type on a path `from` (a click on its out port) into one more frame, put after it in its thread, or befor… | disabled in catalogue snapshot |
| `text.thread.break` | Break Thread |  | {id, port: "in"\|"out"} break the thread of area type or type on a path `id` before it (its in port) or after it (its out port), as a double-click on that port does: the story flows into the… | disabled in catalogue snapshot |
| `text.thread.create` | Create | Type > Threaded Text | {} thread the selected area type and type on a path (and closed paths, which become area frames) in stacking order → {ids} | disabled in catalogue snapshot |
| `text.thread.info` | Threads |  | {} → [[id…]] every thread in order | disabled in catalogue snapshot |
| `text.thread.releaseSelection` | Release Selection | Type > Threaded Text | {} take the selected frames out of their threads (the story re-flows through the rest) | disabled in catalogue snapshot |
| `text.thread.remove` | Remove Threading | Type > Threaded Text | {} break the selected frames' threads; each frame keeps the text it shows | disabled in catalogue snapshot |
| `text.touchType` | Touch Type |  | {id, start: byte (a character of it), dx?: pt, dy?: pt, hScale?: %, vScale?: %, rotation?: deg} change one character (a ligature, one glyph for several characters, as a whole) as a Touch Ty… | disabled in catalogue snapshot |

## `type` (23)

Type commands convert or transform type: outlines, area/point conversion, case, orientation, size. Outlining is irreversible; keep the live text master.

| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `type.changeCase` | Change Case | Type > Change Case | {case: "upper"\|"lower"\|"title"\|"sentence", ids?\|id?} → {ids} | disabled in catalogue snapshot |
| `type.convertToAreaType` | Convert To Area Type | Type | {ids?\|id?} point type → area type framed by its current layout bounds → {ids} | disabled in catalogue snapshot |
| `type.convertToPointType` | Convert To Point Type | Type | {ids?\|id?} area type → point type; soft line wraps become line breaks, and a frame of threaded text leaves its thread with the text it holds → {ids} | disabled in catalogue snapshot |
| `type.createOutlines` | Create Outlines | Type | {} convert the selected text to groups of compound paths (one per glyph); a frame of threaded text leaves its thread with the text it shows → {ids} | Irreversible: live text becomes paths. Keep the live-type master; outline a delivery copy or after font resolution.; disabled in catalogue snapshot |
| `type.fillPlaceholder` | Fill with Placeholder Text | Type | {ids?\|id?} replace selected text with placeholder text (area type is filled to its frame) → {ids} | disabled in catalogue snapshot |
| `type.fitHeadline` | Fit Headline | Type | {ids?\|id?} track the first line of area type so it fills the frame width → {ids, tracking} | disabled in catalogue snapshot |
| `type.fractionalWidths` | Fractional Widths |  | {ids?\|id?, on?: bool} turn Fractional Widths on or off for the selected type and every frame of its threads (on omitted: the opposite of the first object's setting). On (the default, and wh… | disabled in catalogue snapshot |
| `type.insert` | Insert Character | Type | {char: "bullet"\|"copyright"\|"ellipsis"\|"paragraph"\|"registered"\|"section"\|"trademark"\|"emDash"\|"enDash"\|"discretionaryHyphen"\|"nonBreakingHyphen"\|"doubleLeftQuote"\|"doubleRightQuote"\|"singl… | disabled in catalogue snapshot |
| `type.opticalMarginAlignment` | Optical Margin Alignment | Type | {ids?\|id?, on?: bool} turn Optical Margin Alignment on or off for the selected type and every frame of its threads (on omitted: the opposite of the first object's setting): in every paragra… | disabled in catalogue snapshot |
| `type.orientation.horizontal` | Horizontal | Type > Orientation | {ids?\|id?} set horizontal writing | disabled in catalogue snapshot |
| `type.orientation.vertical` | Vertical | Type > Orientation | {ids?\|id?} set vertical writing | disabled in catalogue snapshot |
| `type.pathOptions` | Type on a Path Options… | Type > Type on a Path | {ids?\|id?, start?: 0..1, end?: 0..1\|null, flip?: bool, effect?: rainbow\|skew\|3dRibbon\|stairStep\|gravity, alignToPath?: ascender\|descender\|center\|baseline, spacing?: pt} set the selected typ… | disabled in catalogue snapshot |
| `type.resetHorizontalScale` | Reset Horizontal Scale |  | {ids?: [id…]} set the horizontal scale to 100% (as the Character panel shows it, the object's own transform included) in all the text of the type objects in `ids`, else in the text the Type… | disabled in catalogue snapshot |
| `type.resetTracking` | Reset Tracking and Kerning |  | {ids?: [id…]} set tracking to 0 and clear manual kerning without changing the automatic method in all the text of the type objects in `ids`, else in the text the Type tool has selected (at … | disabled in catalogue snapshot |
| `type.ruby` | Ruby… |  | {ids?\|id?, start?: byte, end?: byte, text?: reading, position?: above\|below (vertical type: right\|left), align?: start\|center\|end, size?: 1–100 (percent of the base text's size, default 50)… | disabled in catalogue snapshot |
| `type.scaleTextAttributes` | Scale Text Attributes | Type | {ids?\|id?} bake each selected type object's transform scale into its character sizes (leading, baseline shift and horizontal scale included), leaving rotation and position in the affine → {… | disabled in catalogue snapshot |
| `type.size.decrease` | Decrease Font Size |  | {by?: steps (1)} type.step {attribute: size, by: -by} | disabled in catalogue snapshot |
| `type.size.decreaseByFive` | Decrease Font Size by Five Steps |  | {} type.step {attribute: size, by: -5}: five times the Size/Leading increment (typeSizeIncrement) | disabled in catalogue snapshot |
| `type.size.increase` | Increase Font Size |  | {by?: steps (1)} type.step {attribute: size} | disabled in catalogue snapshot |
| `type.size.increaseByFive` | Increase Font Size by Five Steps |  | {} type.step {attribute: size, by: 5}: five times the Size/Leading increment (typeSizeIncrement) | disabled in catalogue snapshot |
| `type.smartPunctuation` | Smart Punctuation… | Type | {quotes?: true (straight quotes become the Document Setup quotes), dashes?: true (-- → en dash, --- → em dash), ellipsis?: true (... → …), scope?: "selection"\|"document"} → {changed} | disabled in catalogue snapshot |
| `type.step` | Step Type |  | {attribute: "size"\|"leading"\|"tracking"\|"kerning"\|"baselineShift", by?: steps (1; negative steps down), id?, start?: byte, end?: byte, ids?: [id…] (instead of id)} step type by the Preferen… | disabled in catalogue snapshot |
| `type.systemLayout` | System Layout |  | {on?: bool} turn System Layout on or off for the document (on omitted: the opposite of the document's setting) and every text object in it. On, each character that takes any space advances … | disabled in catalogue snapshot |
