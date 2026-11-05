---
name: artcraft-document-export-formats
description: "Use when ArtCraft documents must be created, saved, packaged or exported: exact PNG/JPEG/WebP/SVG/PDF/EPS/DXF sizes and DPI, artboard and selection scopes, export presets, colour mode, print/web settings. Exact ids plus verification gates. Triggers: export SVG, export PDF, export PNG 300 DPI, artboard export, save copy, package, document formats, print settings."
version: 1.0.0
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [artcraft, vectorcraft, export, document, pdf, svg, png, artboards, print]
    related_skills: [artcraft-svg-production, artcraft-path-geometry, apparel-print-master, artcraft-command-atlas]
---

# ArtCraft document and export formats

Delivery is a separate operation from design: choose the right document scope, format, ppi and
colour model, then verify the artifact. Full family map:
`artcraft-command-atlas/references/vc-file-document-export.md`.

## When to use / not use

- Use to create/open/save/place documents, export PNG/JPEG/WebP/SVG/PDF/EPS/DXF, export artboards or
  selections, set document colour mode, or package assets.
- Use when exact pixel/DPI outputs, export presets, or print/web settings matter.
- Not for SVG structure/accessibility optimisation (`artcraft-svg-production`), path geometry
  (`artcraft-path-geometry`), or physical print proofing.

## Inputs

- Source document/master and target formats/sizes/DPI/colour mode.
- Which artboard(s)/selection, transparent vs filled background, fonts/licences.
- Output directory/paths, platform/print constraints, file-size cap.
- Intent: editable master vs delivery derivative.

## Exact commands (Linux VPS)

```bash
VC=/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli
# Linux VPS only. From Windows: ssh -i ~/.ssh/id_ed25519_hostinger root@179.197.88.181 'cd /opt/pod-pipeline && bash -s' < script.sh; stop if unavailable.
```

Document/file: `file.new`, `file.open`, `file.save`, `file.saveAs`, `file.saveCopy`, `file.place`,
`file.info`, `file.list`, `file.close`, `file.package`, `file.revert`, `file.documentColorMode`,
`file.newPresets`, `file.newPresets.save`, `file.newFromTemplate`, `file.saveAsTemplate`.
Inspect: `document.inspect`, `document.json`, `document.info`, `document.formats`, `document.setup`,
`document.setUnits`, `document.switchUnits`, `document.rulerOrigin`, `document.pdfInfo`,
`document.exportSettings`.
Export: `document.export`, `document.exportSelection`, `document.exportForScreens`,
`document.exportPdf`, `document.exportEps`, `document.exportDxf`, `document.exportForWeb`,
`document.exportForOffice`, `document.exportPresets.list/save/delete/import/export`,
`file.export`, `file.exportForScreens`, `webExport.settings`, `webExport.presets.*`.
Print: `print.setup`, `print.preview`, `print.presets.*`, `print.tiling.set`, `print.tiling`.

## Decision table

| Target | Use | Verify |
|---|---|---|
| Editable master | `file.saveAs` | path/hash; do not overwrite source |
| Delivery copy | `file.saveCopy` | new path, master unchanged |
| PNG at exact px/DPI | `document.export` `format:"png"`, `ppi` | `identify` dimensions + px/cm |
| JPEG/WebP | `document.export`/`file.export` | quality, bytes, dimensions |
| SVG | `document.export` `format:"svg"` + `svg` options | real paths, viewBox, text/embedded raster |
| PDF | `document.exportPdf`/`document.export` `format:"pdf"` | page size, fonts, colour mode |
| EPS | `document.exportEps` | flattened transparency, legacy compatibility |
| DXF | `document.exportDxf` | units/scale |
| One artboard | `document.export` artboard option | bounds match that artboard |
| Selection only | `document.export` `selectedOnly:true` or `document.exportSelection` | crop/bounds |
| Multiple screen sizes | `document.exportForScreens` | every output size/format |
| Package for handoff | `file.package` | fonts/links/images collected |
| Change colour mode | `file.documentColorMode` | RGB vs CMYK; not a proof |

## Workflow / state machine

`inspect → copy → set scope/format → export → verify → record`.
A delivery artifact is not proof of physical colour or print quality.

1. `document.inspect`/`document.formats`: confirm artboards, units, formats, fonts.
2. Copy the master; never export over it.
3. Decide scope (document/artboard/selection), format, ppi/scale, background/colour model.
4. Export one probe to a new path; read JSON; `identify`/PDF/XML-check it.
5. Export the full set; verify every file's dimensions/format/bytes.
6. Package if handing off; record paths, settings and any unverified print claims.

## Acceptance gates

- Output exists, non-zero bytes, exact expected dimensions and format (`identify`/PDF info).
- DPI/ppi metadata matches the request (118.11 px/cm = 300 DPI; 28.35 = 72 DPI).
- Artboard/selection scope matches; no clipped or extra content.
- SVG has real paths; PDF fonts/links resolve; no unexpected raster fallback.
- Colour mode/profile as agreed; print colour flagged unverified without proof.
- Source/master unchanged; package contains required assets.
- Report lists command ids, settings, paths/sizes and gate results.

## Refusals / failure modes

- Do not claim a print proof from an RGB screen render; CMYK/PDF is not a proof.
- Do not overwrite a master with `file.saveAs` when a copy is intended.
- Do not assume `document.export` exports all artboards; choose the scope.
- `ppi` wins over `scale`; calculate px = pt ÷ 72 × ppi before setting values.
- SVG text/raster options can change editability; verify the artifact, not just the result.
- Exporters may be plugins (`plugin.<id>`); query their options before use.
- Batch export can flatten names/collide; use separate directories/naming.

## Worked recipes

**1. Web image set.** `document.export` PNG at ppi 72/144/216 → `identify` each → record
1200/2400/3600 px for a 1200-pt document (verified behaviour).

**2. Print PDF.** `document.exportPdf` (or `document.export` `format:"pdf"`) → check page size, fonts,
transparency/colour mode; send only after a vendor proof.

**3. One-artboard pack.** `document.inspect` artboards → `document.export` per artboard to distinct
paths → `identify` each; never rely on the default artboard.

**4. Selection export.** Select art → `document.export` `selectedOnly:true` (or
`document.exportSelection`) → check the crop/bounds include strokes/effects.

**5. Handoff package.** `file.package` → inspect collected fonts/links → `file.saveCopy` for the
working master; record the package contents.

## Agent operating protocol

**Preflight:** inspect document/formats/artboards/fonts; copy; define scope/format/ppi/colour; read
params.

**Execution loop:** one probe export; parse JSON; verify artifact; then the full set; stop on mismatch.

**Evidence contract:** ids/settings, artifact paths/sizes/DPI/format, verification commands, print
claim status; exit 0 alone is not proof.

**Stop/escalate:** missing exporter/plugin; font/link unresolved; ambiguous artboard/scope; print
proof required but unavailable; output would overwrite a master.

**Never:** invent options; claim print quality from screen; export over source; skip artifact checks.

## Sources & verification

- **VERIFIED:** export ids and schema (`document.export` nested `svg`/PDF, `ppi` vs `scale`); 1200-unit
  document exported 1200/2400/3600 px at 72/144/216 ppi; PDF 4,311 B test; `file.place` physical size;
  `document.formats`/`inspect` patterns.
- **ATLAS:** `artcraft-command-atlas/references/vc-file-document-export.md`, `00-intent-map.md`.
- **DOCS:** local ArtCraft docs; official README; Adobe export/PDF concepts.
