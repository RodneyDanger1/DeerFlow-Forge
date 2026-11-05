---
name: artcraft-command-atlas
description: "Use when you need to map a design job or menu habit to the exact ArtCraft command across 918 VectorCraft and 965 PhotoCraft commands: intent map, family indexes with params, CLI/MCP flags, tips, pitfalls, recipes. Triggers: which command, command map, all commands, how do I, menu to command, ArtCraft command lookup, VectorCraft/PhotoCraft API, batch/export mapping."
version: 1.0.0
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [artcraft, vectorcraft, photocraft, commands, mapping, reference, cli, mcp]
    related_skills: [artcraft-command-catalog, artcraft-path-geometry, artcraft-typography-outlines, artcraft-document-export-formats, artcraft-photocraft-adjustments-filters]
---

# ArtCraft command atlas

The **mapping layer** over the installed engines: 918 VectorCraft commands in 64 groups and 965
PhotoCraft commands in 38 groups (snapshot 2026-11-05). Every id in this skill's references was read
from the installed catalogue, not guessed. Use this when the question is "which command do I run for
this job?" rather than "show me the CLI contract" (`artcraft-command-catalog`).

## Coverage and where the detail lives

This SKILL.md is the router. The full indexes live in `references/` (installed alongside it):

| Reference | Contents |
|---|---|
| `references/00-intent-map.md` | designer intent → exact id(s), both apps |
| `references/command-tips.md` | params/units, state/selection, export/batch, failure map |
| `references/vc-object-path.md` | objects, paths, shapes, pathfinder, live paint |
| `references/vc-text-type.md` | text content/style, type conversion, fonts |
| `references/vc-layer-artboard.md` | layers, artboards, symbols, perspective, guides |
| `references/vc-color-style.md` | colour, swatches, gradients, paint, appearance, effects |
| `references/vc-file-document-export.md` | file/document/save/export, PDF/web, libraries, variables |
| `references/vc-select-edit.md` | selection, editing, clipboard, image info |
| `references/vc-trace-addon.md` | image trace and add-on commands |
| `references/pc-file-document-layer.md` | PhotoCraft file/document/layer/comps/history |
| `references/pc-image-adjust.md` | image size/crop/mode + all image adjustments |
| `references/pc-filter-effect.md` | every filter family and layer styles |
| `references/pc-selection-channel.md` | selections, refine, masks, alpha/spot channels |
| `references/pc-text-vector-path.md` | type/path/shape/gradient/swatch/brush/paint/pattern |
| `references/pc-batch-automation.md` | actions/batch/droplet commands |
| `references/recipes-vectorcraft.md`, `recipes-photocraft.md` | runnable multi-step recipes |
| `references/sources.md` | official docs/URLs, local docs, claim labels |

Read `references/README.md` first if unsure which file to open. Each family index lists every id,
label, menu path, abbreviated params and a practical note; the catalogue's full params text is still
the authority.

## When to use / not use

- Use when translating a design goal or an Illustrator/Photoshop menu item into an ArtCraft id.
- Use when you need the full family map, parameter hints, or the "which of these 900 commands" answer.
- Use when planning a multi-step task and you want the alternative commands and their traps.
- Not for proof of CLI syntax (`artcraft-command-catalog`), trace quality (`artcraft-vector-trace`),
  AI-art cleanup (`ai-diffusion-artifact-cleanup`), or MCP transport (`craft-mcp-drive`).
- Not for a legal/licence/trademark decision; mapping a command is not clearance.

## Inputs

- The job in product terms: "outline this wordmark", "export print PDF", "mask the subject".
- The app/route: editable vectors (VectorCraft) vs pixels (PhotoCraft) — or both, split at the seam.
- Source file/paths, target format, dimensions/DPI, rights.
- The installed binaries (Linux VPS) or the SSH wrapper from the execution block below.

## Exact lookup commands (Linux VPS)

```bash
VC=/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli
PC=/opt/craft/photocraft/photocraft-0.20.2-linux-x86_64/bin/photocraft-cli
# Linux VPS only. From Windows: ssh -i ~/.ssh/id_ed25519_hostinger root@179.197.88.181 'cd /opt/pod-pipeline && bash -s' < script.sh; stop if unavailable (/opt does not exist on Windows).
$VC commands | python3 -c 'import json,sys,collections; c=json.load(sys.stdin); print(len(c), len({x["id"].split(".")[0] for x in c}))'
$PC commands --json | python3 -c 'import json,sys; c=json.load(sys.stdin); print(len(c), len({x["id"].split(".")[0] for x in c}))'
$VC commands | python3 -c 'import json,sys; c=json.load(sys.stdin); print(next(x["params"] for x in c if x["id"]=="object.path.simplify"))'
$PC commands --json | python3 -c 'import json,sys; c=json.load(sys.stdin); print(next(x["params"] for x in c if x["id"]=="image.crop"))'
$VC commands | python3 -c 'import json,sys; c=json.load(sys.stdin); [print(x["id"], "—", x["label"]) for x in c if "simplify" in (x["id"]+x["label"]).lower()]'
```

## Mapping procedure

1. Restate the job as an output artifact (SVG/PNG/PDF/PSD/print) rather than a tool name.
2. Pick the app: vectors → VectorCraft; pixels → PhotoCraft; both → split at a file boundary.
3. Open `references/00-intent-map.md`; take the exact id(s); read their full catalogue params.
4. Open the family index for alternatives, parameter hints and traps.
5. Probe one step on a copy; inspect the JSON result and artifact; then chain.
6. If no intent row exists, search labels/menus; do not invent an id.

## Fast intent shortcuts

| Job | Start with |
|---|---|
| Trace logo/AI art | `imageTrace.make` → `imageTrace.expand` |
| Simplify/clean paths | `object.path.simplify`, `object.path.cleanUp` |
| Boolean shapes | `object.pathfinder.unite/divide/minusFront/intersect` |
| Outline text | `type.createOutlines` (keep live master) |
| Area vs point type | `type.convertToAreaType`, `type.convertToPointType` |
| Fix missing font | `text.missingFonts`, `text.replaceFont` |
| Recolour brand art | `recolor.colors`, `recolor.apply` |
| Apply brand swatch | `swatch.new`, `paint.setFill` |
| Group/clip/lock | `object.group`, `layer.clippingMask.toggle`, `object.lock` |
| New artboard/export | `artboard.new`, `document.export` |
| Export PDF/SVG/PNG | `document.export`, `document.exportPdf` |
| Place image | `file.place` (`rect` for exact fit) |
| Save copy | `file.saveCopy` (not `file.saveAs`) |
| Photo crop/resize | `image.crop`, `image.imageSize` |
| Photo levels/curves | `image.adjustments.levels`, `.curves` |
| Photo subject mask | `select.subject`, `select.refineEdge`, `layer.layerMask.revealSelection` |
| Photo denoise/sharpen | `filter.noise.reduceNoise` then `filter.sharpen.unsharpMask` |
| Photo batch | CLI `batch` (or `file.automate.batch`) |
| LUT export | `file.export.colorLookupTables` |
| Layers/artboards export | `file.export.layersToFiles`, `file.export.artboardsToFiles` |

## Command/state rules (must know)

- Catalogue `enabled:false` usually means no open document, not a missing command. PhotoCraft exposes
  `needsDocument`/`disabledReason`; VectorCraft does not.
- `select.all` is mandatory before trace and many path/effect commands; a "nothing selected" error is
  the top failure.
- `--params` binds to the preceding `--cmd`; interleaving errors bind params to the wrong step.
- No dry-run. Copy the source, write a new output path, read the step JSON, then verify the artifact.
- Pathfinder/flatten/merge/rasterize/outline are destructive. Keep a layered/live master.
- `file.place` uses physical size at ppi; `document.export ppi` wins over `scale`.
- Fonts: installed ≠ licensed; missing fonts fall back with a warning. Resolve or outline a copy.
- Batch: output must differ from input unless `--in-place`; `--recursive` flattens names — use
  `--naming '{name}-{serial}'` and `--stop-on-error`.

## Agent operating protocol

**Preflight:** read the intent and family reference; confirm the app/route; confirm source/output
paths; read the exact params text for every planned id; check template/area/fonts/rights.

**Execution loop:** probe one step on a copy; parse JSON; verify artifact; then chain; stop at the
first failure; do not "fix" a gate by skipping it.

**Evidence contract:** report the intent, ids used, full commands, artifact paths/sizes, gate values
and an UNVERIFIED list. A menu-name match is not proof.

**Stop/escalate:** no intent match; no verified id; missing source/font/template; destructive op
without a copy; output path would overwrite a master; unclear rights; no single command covers the job.

**Never:** invent ids/params; quote a command you did not read; treat a label match as proof; run
destructive operations on the only master; claim print colour from a screen render.

## Worked examples

**1. "Make the wordmark editable vector."** Intent map → `type.createOutlines` if the type already
exists; if it is raster, route to `artcraft-vector-trace`. Keep the live text document; outline a
copy; inspect for lost counters and font fallback.

**2. "Export a 300 DPI PNG and a print PDF from this SVG."** `document.export` twice: PNG with
`ppi:300`, PDF with `format:"pdf"`; check `identify`/PDF fonts; the SVG is the editable master, the
PNG/PDF are delivery derivatives.

**3. "Clean the photo and cut out the subject."** `image.crop` → retouch/levels → `select.subject` →
`select.refineEdge` → `layer.layerMask.revealSelection`; keep the source and a layered master.

## Gates / verification

- The id exists in the installed catalogue and its params text was read.
- Selection/document state matches the command (probe first).
- Artifact exists, non-zero bytes, expected dimensions/format; JSON result read.
- Destructive step had a copy and a rollback path.
- Report separates VERIFIED (run), READ (catalogue/docs), and UNVERIFIED.

## Sources & verification

- **VERIFIED:** 918/64 and 965/38 counts; all ids in the indexes and intent map; CLI help contracts;
  `commands --json`, `--filter`, `run/convert/batch/info`; catalogue params; local tool source.
- **DOCS:** local `/opt/craft/artcraft-docs/*`; official READMEs, PhotoCraft CLI book, MCP guide;
  Adobe Image Trace panel options and Photoshop batch/actions help (concepts only).
- Full bibliography and claim labels: `references/sources.md`; coverage: `references/coverage.json`.
- Rebuild indexes: `python blueprint/files/skills/_meta/build_command_guide.py`.
