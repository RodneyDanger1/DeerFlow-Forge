---
name: artcraft-path-geometry
description: "Use when vector geometry must change: unite/subtract/intersect shapes, simplify or clean paths, offset, outline strokes, make compound paths/holes, group/align/distribute, transform, arrange, lock. Exact ArtCraft ids, parameter traps, runnable recipes. Triggers: pathfinder, simplify path, outline stroke, offset path, compound path, align objects, boolean shapes, clean up vectors."
version: 1.0.0
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [artcraft, vectorcraft, pathfinder, paths, geometry, compound-path, align]
    related_skills: [artcraft-vector-trace, artcraft-command-atlas, artcraft-svg-production, apparel-print-master]
---

# ArtCraft path geometry

Changes vector geometry without changing the art direction: booleans, path cleanup, offset, outline
stroke, compound paths, structure, alignment and transforms. Every id is from the installed
catalogue; the full family index is `artcraft-command-atlas/references/vc-object-path.md`.

## When to use / not use

- Use to combine/subtract/intersect shapes, clean a trace, offset a silhouette, outline a stroke, make
  holes, group/align marks, or transform objects.
- Use when a print provider needs one filled silhouette with clean anchors.
- Not for tracing raster (`artcraft-vector-trace`), text outlining (`artcraft-typography-outlines`), or
  SVG delivery/validation (`artcraft-svg-production`).
- Not for photo cutouts/masks (PhotoCraft selection skills).

## Inputs

- Vector file (SVG/AI/VectorCraft) + `identify` not needed; use `document.inspect`/`document.json`.
- The operation and the objects/selection it applies to; stacking order for booleans.
- Target: editable master or flattened delivery copy; print width if relevant.
- Rights and a preserved source.

## Exact commands (Linux VPS)

```bash
cd /opt/pod-pipeline
VC=/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli
PY=/opt/pod-pipeline/.venv/bin/python
# Linux VPS only. From Windows: ssh -i ~/.ssh/id_ed25519_hostinger root@179.197.88.181 'cd /opt/pod-pipeline && bash -s' < script.sh; stop if unavailable.
```

Core ids (read full params with `$VC commands` before use):

`object.pathfinder.unite`, `.minusFront`, `.minusBack`, `.intersect`, `.exclude`, `.divide`, `.trim`,
`.merge`, `.crop`, `.outline`, `.trap`, `.options` · `object.path.simplify`, `.cleanUp`, `.smooth`,
`.addAnchorPoints`, `.outlineStroke`, `.offsetPath`, `.divideObjectsBelow`, `.splitIntoGrid` ·
`object.compoundPath.make`, `.release` · `object.compoundShape.make`, `.setMode`, `.expand`, `.release` ·
`object.group`, `object.ungroup`, `object.arrange.bringToFront`, `.sendToBack`, `.bringForward`,
`.sendBackward`, `.sendToCurrentLayer` · `object.align`, `object.distribute`, `object.distributeSpacing` ·
`object.transform`, `object.transformAgain`, `object.transformEach` · `object.lock`, `.unlockAll`,
`.hide`, `.hide.above`, `.hide.otherLayers`, `.hide.unselected` · `select.all`, `select.none`.

## Decision table

| Goal | Use | Trap |
|---|---|---|
| Merge overlapping fills | `object.pathfinder.unite` | destroys inputs and palette separation |
| Punch a hole | `object.compoundPath.make` | even-odd vs nonzero; release to edit children |
| Subtract front/back | `object.pathfinder.minusFront`/`minusBack` | stacking order decides result |
| Split overlaps for recolour | `object.pathfinder.divide` | many faces/objects |
| Trim/merge/crop outlines | `object.pathfinder.trim`/`merge`/`crop`/`outline` | each has different params; read |
| Reduce anchor count | `object.path.simplify` (`level` 0–100) | rounds corners; not a trace substitute |
| Remove stray/empty/unpainted | `object.path.cleanUp` | can delete intentional tiny details |
| Smooth curves | `object.path.smooth` | different from simplify |
| Stroke → fill | `object.path.outlineStroke` | destroys stroke editability |
| Offset silhouette | `object.path.offsetPath` | joins/miter affect corners; not stroke width |
| Combine objects into structure | `object.group` / `object.ungroup` | group affects clipping context |
| Align/distribute | `object.align`, `object.distribute` | key object/anchor choice |
| Transform repeatedly | `object.transform`, `.transformAgain`, `.transformEach` | repeat applies last transform |
| Protect finished art | `object.lock`/`object.hide` variants | `.unlockAll` is global |

## Workflow / state machine

`inspect → copy → select target → boolean/cleanup → simplify/offset → structure/align → export copy → verify`.
A failed step leaves the prior file intact; never continue after a failed step.

1. `document.inspect`/`document.json`: list objects/layers/artboards and the stacking order.
2. Duplicate the source (`file.saveCopy`) or work on a copy; record its hash.
3. Select exactly the operands (`select.set`, `select.all`, or explicit `ids`).
4. Run one geometry operation; read JSON/result counts; inspect at 100 %.
5. Clean/simplify only after the shape is correct; compare anchor/path counts.
6. Export to a new path; verify SVG paths and fill count; keep the layered master.

## Acceptance gates

- Boolean result has the expected object count and every intended hole/edge is present.
- No unintended open paths, stray points, or duplicated anchors; `cleanUp` report is understood.
- Outline stroke is filled (no live stroke dependence) and width is preserved visually.
- Offset is the requested distance in document units, with corners as agreed.
- Group/clipping order preserved; no object left on the wrong layer.
- Export has real paths, expected fill count and no embedded raster.
- Original file unchanged; new artifact path; values quoted in the report.

## Refusals / failure modes

- Never run `object.pathfinder.unite` on a multi-colour trace without accepting palette flattening.
- Do not use pathfinder as a substitute for clipping/opacity masks; they are different operations.
- Do not outline strokes/effects on the only master; expansion is irreversible.
- Do not simplify a wordmark that has not been retyped/outlined; it rounds letterforms.
- Do not claim a boolean succeeded from exit 0; inspect object counts and the render.
- No dry-run; copy + new output + read JSON is the safety model.

## Worked recipes

**1. Badge silhouette from overlapping shapes.** Create/select shapes → `object.pathfinder.unite` →
`object.path.cleanUp` → `object.path.simplify {"level":20}` → export SVG; check hole/edge count.

**2. Punch a transparent hole.** Select outer shape + inner shape → `object.compoundPath.make` →
export; verify hole in the 100 % render. Use `object.compoundPath.release` to edit later.

**3. Stroke to print-safe fill.** `select.all` → `object.path.outlineStroke` → `object.pathfinder.unite`
(if one silhouette is required) → export; compare stroke width before/after.

**4. Align a logo lockup.** `select.all` → `object.align` with the chosen key object/axis →
`object.distributeSpacing` for gaps → `object.group`; export and measure margins.

**5. Offset a print silhouette.** `select.all` → `object.path.offsetPath` with the requested distance
and join style → clean/simplify → export; verify outer bounds against the print width.

## Agent operating protocol

**Preflight:** read the family index and exact params; confirm object/selection/stacking; copy the
source; decide editable vs delivery output.

**Execution loop:** one operation, parse JSON, 100 % inspect, then next; stop on the first unexpected
count/shape.

**Evidence contract:** command ids, input/output paths, object/anchor/path counts, render path, gates;
exit 0 alone is not proof.

**Stop/escalate:** no exact id; destructive operation without a copy; ambiguous operand/stacking;
missing template/print width; result changes palette unexpectedly.

**Never:** invent ids; flatten the only master; treat a menu name as an id; claim print quality from a
screen render.

## Sources & verification

- **VERIFIED:** all ids above exist in the 918-row catalogue; params text read for the boolean/path
  commands; pathfinder/subtract behaviour and palette flattening recorded from local docs/vault.
- **ATLAS:** `artcraft-command-atlas/references/vc-object-path.md` and `00-intent-map.md`.
- **DOCS:** `/opt/craft/artcraft-docs/*`; official VectorCraft README; Adobe Illustrator Pathfinder
  concepts (see atlas `sources.md`). Commands are ArtCraft's, not Adobe's.
