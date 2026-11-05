#!/usr/bin/env python3
"""Build the ArtCraft command atlas from the installed, verified catalogues.

Reads ``_meta/catalogues/vectorcraft-commands.json`` (918 rows) and
``_meta/catalogues/photocraft-commands.json`` (965 rows) and writes the
reference files used by the ``artcraft-command-atlas`` skill. Every catalogue
id is emitted exactly once; the script fails if coverage is incomplete.

Run: python _meta/build_command_guide.py
"""
from __future__ import annotations

import collections
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAT = ROOT / "_meta" / "catalogues"
OUT = ROOT / "artcraft-command-atlas" / "references"

VC = json.loads((CAT / "vectorcraft-commands.json").read_text(encoding="utf-8"))
PC = json.loads((CAT / "photocraft-commands.json").read_text(encoding="utf-8"))

VC_FAMILIES = {
    "object": "vc-object-path.md",
    "path": "vc-object-path.md",
    "shape": "vc-object-path.md",
    "shapeBuilder": "vc-object-path.md",
    "livePaint": "vc-object-path.md",
    "shaper": "vc-object-path.md",
    "magicWand": "vc-object-path.md",
    "text": "vc-text-type.md",
    "type": "vc-text-type.md",
    "charStyle": "vc-text-type.md",
    "paraStyle": "vc-text-type.md",
    "layer": "vc-layer-artboard.md",
    "artboard": "vc-layer-artboard.md",
    "symbol": "vc-layer-artboard.md",
    "perspective": "vc-layer-artboard.md",
    "guide": "vc-layer-artboard.md",
    "view": "vc-layer-artboard.md",
    "slice": "vc-layer-artboard.md",
    "graph": "vc-layer-artboard.md",
    "color": "vc-color-style.md",
    "swatch": "vc-color-style.md",
    "gradient": "vc-color-style.md",
    "paint": "vc-color-style.md",
    "graphicStyle": "vc-color-style.md",
    "appearance": "vc-color-style.md",
    "transparency": "vc-color-style.md",
    "recolor": "vc-color-style.md",
    "pattern": "vc-color-style.md",
    "colorTheme": "vc-color-style.md",
    "brush": "vc-color-style.md",
    "stroke": "vc-color-style.md",
    "effect": "vc-color-style.md",
    "flattener": "vc-color-style.md",
    "svgInteractivity": "vc-color-style.md",
    "eyedropper": "vc-color-style.md",
    "file": "vc-file-document-export.md",
    "document": "vc-file-document-export.md",
    "print": "vc-file-document-export.md",
    "pdf": "vc-file-document-export.md",
    "webExport": "vc-file-document-export.md",
    "css": "vc-file-document-export.md",
    "links": "vc-file-document-export.md",
    "assets": "vc-file-document-export.md",
    "library": "vc-file-document-export.md",
    "variable": "vc-file-document-export.md",
    "dataset": "vc-file-document-export.md",
    "importMatches": "vc-file-document-export.md",
    "plugin": "vc-file-document-export.md",
    "help": "vc-file-document-export.md",
    "prefs": "vc-file-document-export.md",
    "script": "vc-file-document-export.md",
    "command": "vc-file-document-export.md",
    "action": "vc-file-document-export.md",
    "shortcutSet": "vc-file-document-export.md",
    "select": "vc-select-edit.md",
    "edit": "vc-select-edit.md",
    "clipboard": "vc-select-edit.md",
    "image": "vc-select-edit.md",
    "node": "vc-select-edit.md",
    "attributes": "vc-select-edit.md",
    "dimension": "vc-select-edit.md",
    "tool": "vc-select-edit.md",
    "imageTrace": "vc-trace-addon.md",
    "addon": "vc-trace-addon.md",
}

PC_FAMILIES = {
    "file": "pc-file-document-layer.md",
    "document": "pc-file-document-layer.md",
    "layer": "pc-file-document-layer.md",
    "layerComp": "pc-file-document-layer.md",
    "history": "pc-file-document-layer.md",
    "image": "pc-image-adjust.md",
    "filter": "pc-filter-effect.md",
    "style": "pc-filter-effect.md",
    "select": "pc-selection-channel.md",
    "channel": "pc-selection-channel.md",
    "type": "pc-text-vector-path.md",
    "path": "pc-text-vector-path.md",
    "shape": "pc-text-vector-path.md",
    "swatches": "pc-text-vector-path.md",
    "gradient": "pc-text-vector-path.md",
    "brush": "pc-text-vector-path.md",
    "paint": "pc-text-vector-path.md",
    "pattern": "pc-text-vector-path.md",
    "actions": "pc-batch-automation.md",
}

GROUP_TIPS = {
    "object": "Object commands act on whole objects/layers, not anchors. Most take `ids` or use the selection; `object.arrange.*` changes stacking, `object.group`/`ungroup` changes structure, `object.transform.*` changes geometry. Run `select.all` first only when you intend every object.",
    "path": "Path/anchor commands act on anchors and segments, not whole objects. `object.path.simplify` smooths, `object.path.cleanUp` removes stray points, `object.path.outlineStroke` converts a stroke to fills, `object.path.offsetPath` builds an offset contour. Selected anchors matter; inspect the result counts.",
    "shape": "Shape commands create parametric shapes. Convert to paths before pathfinder/path editing if you need exact anchors.",
    "shapeBuilder": "Shape Builder merges or erases regions of overlapping art. It is destructive to the source objects; work on a copy and verify region counts.",
    "livePaint": "Live Paint treats overlapping fills as paintable regions. Expand before exporting to plain SVG when the consumer cannot read live-paint groups.",
    "shaper": "Shaper builds shapes from drawn segments; use it for deliberate geometric construction, not auto-tracing.",
    "magicWand": "Selects by colour/appearance similarity. It is selection-only; follow with a paint or object command.",
    "text": "Text commands manage content, styles, threading and font resolution. Character/paragraph styles are separate groups. Use `text.fontList` to see installed families and `text.missingFonts` before export.",
    "type": "Type commands convert or transform type: outlines, area/point conversion, case, orientation, size. Outlining is irreversible; keep the live text master.",
    "charStyle": "Character styles store reusable glyph formatting. Apply them for consistency across a wordmark system.",
    "paraStyle": "Paragraph styles store paragraph-level formatting (alignment, indents, spacing). Use for multi-line brand copy.",
    "layer": "Layer commands manage structure and stacking. `layer.move`/`layer.collectInNew` move selected art; `layer.merge`/`flatten` are destructive. Lock/hide commands protect finished layers.",
    "artboard": "Artboards define output regions. Export uses the artboard; check its bounds before `document.export`.",
    "symbol": "Symbols are reusable instances. Editing the symbol changes every instance; break the link before one-off changes.",
    "perspective": "Perspective commands place art on a perspective grid. Duplicate the art first; transforms are hard to invert.",
    "guide": "Guides are layout aids; they should not export. Clear them before delivery if the exporter includes them.",
    "view": "View commands change the editing view, not the artwork. Do not expect them to affect exported pixels.",
    "slice": "Slices define web-export regions. They only matter if the export path consumes slices.",
    "graph": "Graph commands create chart objects. Style them after creation; data editing is a separate operation.",
    "color": "Colour commands set or convert colour values. Record the exact colour space (RGB/CMYK/spot) because screen hex is not a press value.",
    "swatch": "Swatches are reusable named colours. Use global/spot swatches for brand colours so one edit updates the artwork; check spot options before print.",
    "gradient": "Gradient commands apply presets and edit stops. Gradient geometry is separate (`paint.setGradientGeom`); verify direction and stops in the render.",
    "paint": "Paint sets fill/stroke, gradients and sampled colours. `paint.none` removes paint; `paint.setFill`/`setStroke` are the workhorses.",
    "graphicStyle": "Graphic styles bundle fill/stroke/effects. Applying one can overwrite local appearance; keep a copy of the source.",
    "appearance": "Appearance commands stack fills/strokes/effects on one object. Expand appearance before export if the consumer cannot render the stack.",
    "transparency": "Transparency/blending commands affect compositing. The rendered PNG/SVG must be checked on the final background, not the editor checkerboard.",
    "recolor": "Recolor commands remap a palette. They are ideal for brand variants; verify every output colour against the approved hex list.",
    "pattern": "Pattern swatches tile artwork. Check seam alignment and output scale; patterns are easy to make too dense for print.",
    "colorTheme": "Colour themes are groups of harmonised colours. Use them as candidates, then lock the approved palette into swatches.",
    "brush": "Brushes paint variable-width strokes. For print, expand strokes to outlines or verify the consumer supports the brush definition.",
    "stroke": "Stroke commands set width, caps, joins, dashes and alignment. Outline strokes before a pathfinder operation that expects fills.",
    "effect": "Effects are live appearances (shadow, glow, etc.). `effect.expandAppearance` is required before some exporters and before path operations; expanded effects are no longer editable.",
    "flattener": "Flattening converts transparency/effects for output. Keep the unflattened master and flatten only a delivery copy.",
    "svgInteractivity": "SVG interactivity adds links/events for web SVG. It does not affect print output.",
    "eyedropper": "Samples appearance from art. Check whether it samples fill, stroke, type or effects before applying.",
    "file": "File commands create/open/save/place documents. `file.place` uses the raster's physical size (ppi), not pixel count; `file.saveAs` changes the working file, `file.saveCopy` preserves the original.",
    "document": "Document commands inspect/serialize/export the whole document. `document.export` is the main delivery path; `document.exportPdf`/`exportEps`/`exportDxf` are format-specific. Check `document.formats` for installed exporters.",
    "print": "Print commands set print options. They do not prove a physical print; colour and stock need a proof.",
    "pdf": "PDF commands create/inspect PDF output. Check fonts, transparency flattening and colour space before sending to a printer.",
    "webExport": "Web export produces web-oriented assets. Use exact pixel/ppi settings and compare bytes; lossy formats can grow on flat art.",
    "css": "CSS export extracts style rules for web use. Treat it as generated code, not a design master.",
    "links": "Linked files can change outside the document. Update links and package assets before delivery.",
    "assets": "Assets are reusable exported items. Name them so downstream skills can find them.",
    "library": "Libraries share assets between documents. Export a copy when delivering to someone without the library.",
    "variable": "Variables drive data-driven artwork. Test one record and check every text/fill mapping before a batch.",
    "dataset": "Datasets are variable-data records. Validate row count and final rendered files, not only the dataset.",
    "importMatches": "Import matching maps incoming files to placed art. Verify which file matched which placement.",
    "plugin": "Plugins extend the engine. A plugin's exporter format is `plugin.<id>`; query `plugin.info` before use.",
    "help": "Help/menu commands expose reference information. They do not change the artwork.",
    "prefs": "Preferences change app behaviour, not the document. Avoid relying on them for reproducible output.",
    "script": "Scripts run host code. They are powerful and untrusted; run only vetted scripts in an isolated environment.",
    "command": "Command-palette helpers. They do not replace reading the catalogue.",
    "action": "Actions record/replay steps. Validate the recorded params against the current catalogue before replay.",
    "shortcutSet": "Keyboard shortcut sets are UI-only; automation must call command ids.",
    "select": "Selection commands define what later commands affect. `select.all` is required before many trace/path operations; `select.set` replaces a selection, `select.add` extends it.",
    "edit": "Edit commands manipulate clipboard/undo/duplicate state. Undo/redo are not a substitute for a copy of the file.",
    "clipboard": "Clipboard commands move data between documents/apps. Clipboard state is external to the file; do not rely on it for reproducibility.",
    "image": "VectorCraft's `image` group has only `image.info`; raster placement uses `file.place`, raster cropping `object.cropImage`, rasterizing `object.rasterize`.",
    "node": "Node editing is a low-level path operation; confirm the target object and node indices.",
    "attributes": "Attributes hold non-geometric metadata (e.g. overprint). Check them when output differs from the screen.",
    "dimension": "Dimension objects annotate technical drawings; they are not part of a brand asset unless intended.",
    "tool": "Tool commands activate an editing tool. Headless automation should prefer the direct command, not tool activation.",
    "imageTrace": "Image Trace: select a raster, `imageTrace.make` with nested `params`, then `imageTrace.expand` to edit paths. Presets are leads; custom limited palettes usually win.",
    "addon": "Add-on commands are specialised helpers (cleanup, text, pattern, etc.). Read the exact params text; many are narrower than their names suggest.",
}

PC_TIPS = {
    "file": "File commands open/save/place/export. `file.export.quickExport` and `file.export.presets.*` are faster than save-as; check the output bytes/dimensions. `file.automate.*` commands are batch helpers.",
    "document": "Document commands manage the whole document: mode, size, metadata. Use `image.mode.*` for colour-space conversion.",
    "layer": "Layer commands are the largest group. `layer.new.layer/group`, `layer.arrange.*`, masks, clipping and adjustment layers. Verify the active layer before a destructive command.",
    "layerComp": "Layer comps store alternative visibility states. Export each comp separately; do not assume a comp is a file.",
    "history": "History commands undo/redo or step through states. A saved history is not a version-control backup.",
    "image": "Image commands resize/crop/canvas/mode, plus `image.adjustments.*`. `image.imageSize` resamples; `keepPrintSize` controls whether pixels scale with resolution. `image.crop` is destructive unless pixels are preserved.",
    "filter": "Filters are destructive pixel operations. Work on a copy; sharpen last at final size; noise reduction before sharpening. Check params schema because ranges differ by filter.",
    "style": "Layer styles are live effects. Keep the editable document; flatten only for delivery.",
    "select": "Selection commands define the edit region. `select.subject`/`select.sky` are content-aware; always inspect the mask at 100% and feather/refine before masking.",
    "channel": "Channels store alpha/spot/colour data. Saving a selection writes an alpha channel; spot channels are for print separations.",
    "type": "Type commands create/edit/rasterize text and OpenType features. `type.rasterize` is irreversible; keep the live type master. Missing fonts produce warnings; resolve them deliberately.",
    "path": "Path commands create/edit vector paths inside PhotoCraft. Use `type.createWorkPath` for text shapes and `select.toWorkPath` for selections.",
    "shape": "Shape layers are vector; rasterize only for pixel effects.",
    "swatches": "Swatches are reusable colours. Check CMYK/spot values before print.",
    "gradient": "Gradients can be fill layers or applied paint. Verify direction/stops and banding at print size.",
    "brush": "Brushes paint pixels; for print art, brush strokes are resolution-dependent. Work at final size.",
    "paint": "Paint commands fill/stroke pixels or selections. `edit.fill` is the usual fill path; check the target channel/layer.",
    "pattern": "Patterns tile pixels/vectors. Check seam and scale; patterns at low resolution print soft.",
    "actions": "Actions record/replay command lists. Batch uses an actions file; validate the steps against the current registry and use `--stop-on-error`.",
}

COMMAND_TIPS = {
    "imageTrace.make": "Requires a raster object selected (`select.all` first). Trace settings go under `params.params`; `enhanced` is a sibling of `params`. Presets are starting points, not production proof.",
    "imageTrace.expand": "Turns the live trace into editable paths. Run it before path simplification or export; expansion is what the gates measure.",
    "object.path.simplify": "`level` 0-100; higher removes more anchors. The result counts anchors before/after; do not simplify a wordmark until text is retyped/outlined.",
    "object.path.cleanUp": "Removes stray points, empty text and unpainted objects. Run after tracing; it can remove intentional tiny details, so compare counts.",
    "object.path.outlineStroke": "Converts strokes to filled outlines. Required before some pathfinder/boolean operations and for robust SVG consumers.",
    "object.path.offsetPath": "Creates an offset contour; joins/miter limit affect sharp corners. Offset is not a stroke-width change.",
    "type.createOutlines": "Irreversible: live text becomes paths. Keep the live-type master; outline a delivery copy or after font resolution.",
    "text.replaceFont": "Replaces a family across text objects. Use `text.missingFonts`/`text.fontList` first; record licence.",
    "text.createArea": "Area type fills a rect; point type is a single line. Use area type for paragraphs, point type for short labels.",
    "layer.new": "Creates an empty layer and may change the current layer. Check `layer.setCurrent` before adding art.",
    "layer.clippingMask.toggle": "Creates/releases a clipping mask from the selected stack. Order matters: clipping object above, content below.",
    "artboard.new": "Adds an output region. `document.export` with artboard options chooses which one; do not assume artboard 1.",
    "document.export": "Main delivery command: `path`, `format`, `ppi`/`scale`, `artboard(s)`, `selectedOnly`, plus nested `svg`/PDF options. `ppi` wins over `scale`.",
    "document.exportPdf": "PDF-specific export; check fonts, transparency and colour space. A PDF that looks right on screen is not colour proof.",
    "document.exportEps": "EPS is a legacy print exchange; transparency/effects may flatten. Keep the SVG/PDF master.",
    "file.place": "Places raster at its physical size (ppi), not pixel count; SVG/PDF become placed/locked or editable per `link`. Use `rect` for exact fit.",
    "file.saveAs": "Changes the working file path; `file.saveCopy` preserves the source. Never save over a master.",
    "object.pathfinder.unite": "Flattens selected shapes into one; destroys individual objects and can flatten palette. Use on a copy when colour separation matters.",
    "object.pathfinder.divide": "Splits overlaps into separate faces; useful for recolouring regions, but produces many objects. Check object count.",
    "effect.expandAppearance": "Bakes live effects into paths/pixels. Keep the unexpanded master for edits.",
    "paint.setFill": "Sets fill paint; accepts colour/none/gradient/swatch depending on schema. Verify the active target.",
    "swatch.new": "Creates a named colour. Use global/spot deliberately; record the hex/CMYK equivalents.",
    "image.crop": "Destructive crop unless pixels are preserved/retained. Check x/y/width/height against the source bounds.",
    "image.imageSize": "Resamples to width/height; `keepPrintSize` controls whether the print size stays fixed as resolution changes. Compute the ratio before use.",
    "image.canvasSize": "Changes canvas without resampling; anchor decides where existing pixels land. Verify transparency.",
    "image.mode.cmyk": "Converts to CMYK; screen hex is not a press value and the conversion is not a proof. Agree profiles with the vendor.",
    "image.adjustments.levels": "Input/output black/white and gamma. Correct cast before saturation; do not clip highlights.",
    "image.adjustments.curves": "Points map input→output; an S-curve adds contrast. Check the point list schema.",
    "image.adjustments.hueSaturation": "Hue/saturation/lightness with optional target channels. Small moves; check skin/brand colours.",
    "filter.sharpen.unsharpMask": "Amount/radius/threshold; sharpen last at final size. Halos mean radius/amount too high.",
    "filter.sharpen.smartSharpen": "Sharpens with noise reduction; useful on photos, not a substitute for resolution.",
    "filter.noise.reduceNoise": "Strength/preserve details/colour noise/JPEG artifact. Denoise before sharpening, never after.",
    "filter.noise.dustAndScratches": "Radius/threshold; removes small specks but can erase texture. Check at 100%.",
    "select.subject": "Content-aware subject selection. Always refine/feather and inspect the mask; it is a proposal, not truth.",
    "select.refineEdge": "Refines hair/edges. Over-refining creates halos; check on black and white.",
    "select.saveSelection": "Writes an alpha channel; name it so a later load is unambiguous.",
    "layer.layerMask.revealSelection": "Adds a mask from the selection. Non-destructive; check mask density and edge.",
    "type.rasterize": "Irreversible pixel conversion; keep the live text version for edits and font substitution.",
    "file.export.quickExport": "Fast export using presets; verify path, dimensions and format. It may use the document's colour profile.",
    "file.export.layersToFiles": "One file per layer; check naming and skipped hidden/empty layers.",
    "file.export.colorLookupTables": "Exports a .cube from visible top-level adjustment layers; masks/vector masks/clipping are omitted (colour-only LUT).",
    "file.automate.batch": "Batch automation command; the CLI `batch`/`droplet` is usually safer. Output directory must differ from input unless `--in-place`.",
}

def esc(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def short_params(value: str, limit: int = 190) -> str:
    text = " ".join(str(value or "").split())
    return text[: limit - 1] + "…" if len(text) > limit else text


def command_rows(rows, tips):
    lines = ["| id | label | menu | params (synopsis) | notes |", "|---|---|---|---|---|"]
    for row in sorted(rows, key=lambda r: r["id"]):
        menu = " > ".join(row.get("menu") or [])
        note = tips.get(row["id"], "")
        state = []
        if row.get("needsDocument"):
            state.append("needs document")
        if row.get("enabled") is False:
            state.append("disabled in catalogue snapshot")
        if state:
            note = (note + "; " if note else "") + "; ".join(state)
        lines.append(
            f"| `{row['id']}` | {esc(row.get('label',''))} | {esc(menu)} | {esc(short_params(row.get('params','')))} | {esc(note)} |"
        )
    return lines


def write_family(path: Path, title: str, intro: str, rows, tips):
    groups = collections.Counter(row["id"].split(".")[0] for row in rows)
    body = [f"# {title}", "", intro, "", f"Commands: **{len(rows)}** across {len(groups)} groups.", "", "## Coverage", ""]
    body.append(" · ".join(f"`{g}` {n}" for g, n in sorted(groups.items())))
    body.append("")
    for group in sorted(groups):
        body.append(f"## `{group}` ({groups[group]})")
        body.append("")
        body.append(GROUP_TIPS.get(group, ""))
        body.append("")
        body.extend(command_rows([r for r in rows if r["id"].split(".")[0] == group], tips))
        body.append("")
    path.write_text("\n".join(body), encoding="utf-8")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    vc_covered = set()
    for family in sorted(set(VC_FAMILIES.values())):
        rows = [r for r in VC if VC_FAMILIES.get(r["id"].split(".")[0]) == family]
        vc_covered.update(r["id"] for r in rows)
        title = "VectorCraft " + family.replace("vc-", "").replace(".md", "").replace("-", " ").title()
        intro = (
            "Auto-generated from the installed 918-command catalogue (snapshot 2026-11-05). "
            "Every row is a real command id; params are abbreviated from the catalogue's own text. "
            "Read the full params string with `$VC commands` before running. Tips are practical notes, "
            "not substitutes for the schema."
        )
        write_family(OUT / family, title, intro, rows, COMMAND_TIPS)
    leftovers = [r for r in VC if r["id"] not in vc_covered]
    if leftovers:
        write_family(OUT / "vc-other-groups.md", "VectorCraft Other Groups",
                     "Commands from groups not covered by the specialist maps. Same verification rules apply.",
                     leftovers, COMMAND_TIPS)
        vc_covered.update(r["id"] for r in leftovers)

    pc_covered = set()
    for family in sorted(set(PC_FAMILIES.values())):
        rows = [r for r in PC if PC_FAMILIES.get(r["id"].split(".")[0]) == family]
        pc_covered.update(r["id"] for r in rows)
        title = "PhotoCraft " + family.replace("pc-", "").replace(".md", "").replace("-", " ").title()
        intro = (
            "Auto-generated from the installed 965-command registry (snapshot 2026-11-05). "
            "Every row is a real command id; params are abbreviated. Query the full schema with "
            "`$PC commands --json`. PhotoCraft input is positional and `--out` must differ from input."
        )
        write_family(OUT / family, title, intro, rows, PC_TIPS)
    leftovers = [r for r in PC if r["id"] not in pc_covered]
    if leftovers:
        write_family(OUT / "pc-other-groups.md", "PhotoCraft Other Groups",
                     "Commands from groups not covered by the specialist maps. Same verification rules apply.",
                     leftovers, PC_TIPS)
        pc_covered.update(r["id"] for r in leftovers)

    missing = {r["id"] for r in VC} - vc_covered
    pc_missing = {r["id"] for r in PC} - pc_covered
    if missing or pc_missing:
        raise SystemExit(f"coverage failure: VC missing {len(missing)}, PC missing {len(pc_missing)}")
    (OUT / "coverage.json").write_text(json.dumps({
        "vectorcraft": {"total": len(VC), "covered": len(vc_covered), "groups": len({r['id'].split('.')[0] for r in VC})},
        "photocraft": {"total": len(PC), "covered": len(pc_covered), "groups": len({r['id'].split('.')[0] for r in PC})},
    }, indent=2) + "\n", encoding="utf-8")

    # Ship the machine catalogues with the atlas so command_lookup.py works from
    # either runtime (references/ is mirrored by the installer).
    machine = OUT / "catalogues"
    machine.mkdir(parents=True, exist_ok=True)
    shutil.copy2(CAT / "vectorcraft-commands.json", machine / "vectorcraft-commands.json")
    shutil.copy2(CAT / "photocraft-commands.json", machine / "photocraft-commands.json")
    (machine / "README.md").write_text(
        "# Catalogue snapshot\n\n"
        "Copied from the installed CLIs on 2026-11-05. Used by `../command_lookup.py`; "
        "the skill indexes are generated from the same files. Re-run `_meta/build_command_guide.py` "
        "after upgrading the apps.\n",
        encoding="utf-8",
    )

    vc_files = {}
    for group in sorted({r["id"].split(".")[0] for r in VC}):
        vc_files[group] = VC_FAMILIES.get(group, "vc-other-groups.md")
    pc_files = {}
    for group in sorted({r["id"].split(".")[0] for r in PC}):
        pc_files[group] = PC_FAMILIES.get(group, "pc-other-groups.md")
    groups = ["# Group → family index", "",
              "Use this to jump from a command prefix to the file that lists it. Do not load every family file; "
              "open only the one you need (or use `command_lookup.py`).", "",
              "## VectorCraft (64 groups)", "", "| Group | Commands | File |", "|---|---:|---|"]
    vc_counts = collections.Counter(r["id"].split(".")[0] for r in VC)
    for group in sorted(vc_counts):
        groups.append(f"| `{group}` | {vc_counts[group]} | `{vc_files[group]}` |")
    groups += ["", "## PhotoCraft (38 groups)", "", "| Group | Commands | File |", "|---|---:|---|"]
    pc_counts = collections.Counter(r["id"].split(".")[0] for r in PC)
    for group in sorted(pc_counts):
        groups.append(f"| `{group}` | {pc_counts[group]} | `{pc_files[group]}` |")
    (OUT / "group-index.md").write_text("\n".join(groups) + "\n", encoding="utf-8")
    print(f"atlas coverage OK: VC {len(vc_covered)}/{len(VC)}, PC {len(pc_covered)}/{len(PC)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
