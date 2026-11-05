# ArtCraft command atlas — reference map

This folder is the full, generated command knowledge base behind the `artcraft-command-atlas` skill.
It is installed alongside the skill by `install_skills.py` (references/ is mirrored to both runtimes).

## Coverage

- VectorCraft: **918 / 918** command ids, 64 groups (`coverage.json`).
- PhotoCraft: **965 / 965** command ids, 38 groups (`coverage.json`).
- Every command row: id, label, menu path, abbreviated params from the catalogue, practical note,
  and state flags where the catalogue provides them.

## Files

| File | Answers |
|---|---|
| `00-intent-map.md` | "I want to …" → exact command id(s), for both apps |
| `command-tips.md` | CLI/MCP rules, params/units, selection/state, export, batch, failure map |
| `vc-object-path.md` | objects, paths, shapes, pathfinder, live paint, shape builder |
| `vc-text-type.md` | text content/styles, type conversion, fonts, styles |
| `vc-layer-artboard.md` | layers, artboards, symbols, perspective, guides, view, slices, graphs |
| `vc-color-style.md` | colour, swatches, gradients, paint, strokes, appearance, effects, patterns |
| `vc-file-document-export.md` | file/document/save/export, PDF/print/web/CSS, libraries, variables |
| `vc-select-edit.md` | selection, editing, clipboard, image info, attributes, dimensions |
| `vc-trace-addon.md` | image trace and add-on commands |
| `vc-other-groups.md` | any groups not in the specialist maps (none expected; coverage asserted) |
| `pc-file-document-layer.md` | PhotoCraft file/document/layer/comps/history |
| `pc-image-adjust.md` | image size/crop/mode and all `image.adjustments.*` |
| `pc-filter-effect.md` | every `filter.*` family and layer styles |
| `pc-selection-channel.md` | selections, refine, masks, alpha/spot channels |
| `pc-text-vector-path.md` | type, path, shape, gradients, swatches, brushes, paint, patterns |
| `pc-batch-automation.md` | actions/batch/droplet-oriented commands |
| `pc-other-groups.md` | remaining PhotoCraft groups |
| `recipes-vectorcraft.md` | runnable multi-step VectorCraft recipes |
| `recipes-photocraft.md` | runnable multi-step PhotoCraft recipes |
| `group-index.md` | group prefix → family file + command count |
| `command_lookup.py` | fast id/intent/group lookup over `catalogues/` |
| `check_atlas.py` | coverage + app-scoped intent + group-index validation |
| `sources.md` | official docs, local docs, claim labels, what is not claimed |

## Rebuild

```bash
python blueprint/files/skills/_meta/build_command_guide.py
```

The builder asserts full coverage, rewrites the family files, copies the machine catalogues and
regenerates `group-index.md`. Run `python check_atlas.py` after edits. Curated files (`00-intent-map.md`,
`command-tips.md`, recipes, sources, this map) are maintained by hand.

## Reading rules

1. Open the intent map first when the job is phrased in designer language.
2. Open the family file for the group; copy the exact id.
3. Read the full params string from the catalogue before running; the table abbreviates it.
4. Verify the artifact; a command returning a result is not proof the output is correct.
