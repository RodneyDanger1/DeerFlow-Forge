---
name: artcraft-layers-artboards-symbols
description: "Use when an ArtCraft document needs structure: layers/groups, clipping masks, stacking, locking/hiding, alignment, artboards for output sizes, symbol instances and overrides, or perspective placement. Exact VectorCraft ids, order/ownership traps and export-ready recipes. Triggers: layers, groups, artboards, symbols, clipping mask, arrange, lock, align, output sizes."
version: 1.0.0
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [artcraft, vectorcraft, layers, artboards, symbols, clipping, organization]
    related_skills: [artcraft-path-geometry, artcraft-document-export-formats, artcraft-command-atlas]
---

# Layers, artboards and symbols

Structure decides output: which artboard exports, what a clipping mask clips, which layer receives
new art, and which symbol instances update. Load **artcraft-command-atlas**, then read `references/vc-layer-artboard.md`.

## When to use / not use

- Use to organise a working file, clip art, lock finished layers, arrange stacking, or align groups.
- Use to create/duplicate/arrange artboards for output sizes and export each one.
- Use to build reusable symbols and override/update instances.
- Not for boolean/path cleanup (`artcraft-path-geometry`), export formats
  (`artcraft-document-export-formats`), or brand rules (`brand-system`).

## Inputs

- Document structure: current layers/groups, object ownership, artboard list (`document.inspect`).
- Output requirements: artboard sizes/count, which object belongs to which layer, clipping intent.
- Symbol reuse scope: which instances must share edits, which are one-off.
- Source copy and a delivery path.

## Exact commands (Linux VPS)

```bash
VC=/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli
# Linux VPS only. From Windows: ssh -i ~/.ssh/id_ed25519_hostinger root@179.197.88.181 'cd /opt/pod-pipeline && bash -s' < script.sh; stop if unavailable.
```

Layers: `layer.new`, `layer.newSublayer`, `layer.setCurrent`, `layer.setProps`, `layer.move`,
`layer.duplicate`, `layer.delete`, `layer.collectInNew`, `layer.merge`, `layer.flatten`,
`layer.clippingMask.toggle`, `layer.reverse`, `layer.template`, `layer.releaseToLayers`,
`layer.hideOthers`, `layer.showAll`, `layer.lockOthers`, `layer.unlockAll`, `layer.locate`,
`layer.selectAll`.
Objects: `object.group`, `object.ungroup`, `object.arrange.bringToFront`, `.bringForward`,
`.sendBackward`, `.sendToBack`, `.sendToCurrentLayer`, `object.align`, `object.distribute`,
`object.distributeSpacing`, `object.lock`, `object.unlockAll`, `object.hide`, `object.hide.above`,
`object.hide.otherLayers`, `object.hide.unselected`.
Artboards: `artboard.new`, `artboard.delete`, `artboard.deleteEmpty`, `artboard.setProps`,
`artboard.fitToArt`, `artboard.fitToSelection`, `artboard.move`, `artboard.rearrange`,
`artboard.reorder`, `artboard.duplicate`, `artboard.convertToArtboards`, `artboard.copy`, `artboard.cut`.
Symbols: `symbol.new`, `symbol.place`, `symbol.list`, `symbol.edit`, `symbol.exitEditing`,
`symbol.update`, `symbol.breakLink`, `symbol.replace`, `symbol.delete`, `symbol.duplicate`,
`symbol.setCurrent`, `symbol.unused`, `symbol.selectInstances`, `symbol.instance.setAppearance`,
`symbol.instance.reset`, `symbol.options`.

## Decision table

| Goal | Use | Trap |
|---|---|---|
| New empty layer | `layer.new` + `layer.setCurrent` | otherwise new art lands elsewhere |
| Group/ungroup | `object.group` / `object.ungroup` | group changes clipping context |
| Move selected art | `layer.move`/`layer.collectInNew` | check source layer after move |
| Clip art | `layer.clippingMask.toggle` | clipping object must be above content |
| Stacking | `object.arrange.*` | object-level, not layer order |
| Align to key | `object.align` | anchor/key-object choice changes result |
| Duplicate artboard | `artboard.duplicate` | duplicated names/order |
| Fit artboard | `artboard.fitToArt`/`fitToSelection` | output bounds change |
| Reusable instance | `symbol.place` | editing symbol edits all instances |
| One-off edit | `symbol.breakLink` first | breaking is irreversible link-wise |
| Update all instances | `symbol.update` | confirm scope before propagating |
| Protect finished art | `object.lock`/`object.hide` variants | `.unlockAll` is global |

## Workflow / state machine

`inspect → copy → create/organise → set current → clip/lock → artboards → export → verify`.
Keep a layered master; export artboards as delivery derivatives.

1. `document.inspect`/`document.json`: read layers, objects and artboards; note ownership.
2. Copy source; decide master vs delivery file.
3. Create/rename/group layers; set current before adding/importing.
4. Clip with `layer.clippingMask.toggle`; verify the clip base/stack.
5. Align/distribute groups; lock/hide finished work to prevent accidental edits.
6. Create/duplicate/fit artboards; inspect order and names.
7. Export each artboard (`document.export` with artboard option); verify dimensions.
8. Keep the master; record layer/artboard structure in the report.

## Acceptance gates

- Every object is on the intended layer; no orphan art on a template layer.
- Clipping mask shows the intended content and can be released non-destructively.
- Stacking order matches the visual design; no hidden object unexpectedly exporting.
- Artboard bounds/order/names are exact; each export matches its artboard size.
- Symbol instances share the intended definition; one-off overrides are intentional.
- Locked/hidden layers are deliberate; `.unlockAll`/`showAll` was not run accidentally.
- Export artifacts verified; master retains structure.

## Refusals / failure modes

- Do not flatten/merge the only layered master; keep a copy.
- Do not use `object.arrange.*` to reorder layers; use `layer.move`/layer commands.
- Do not break symbol links casually; it may be irreversible for that instance.
- Do not assume artboard 1; read `document.inspect` and export by index/name.
- Hidden layers may still export in some paths; verify the artifact, not the editor view.
- No dry-run; probe and inspect JSON before a destructive structural change.

## Worked recipes

**1. Clean up a messy file.** `document.inspect` → create layers (`layer.new`) → assign via
`layer.move`/`collectInNew` → group objects → lock/hide finished layers → export a test artboard.

**2. Clipping mask.** Place content layer, put clipping object above → select both →
`layer.clippingMask.toggle` → verify 100 %; release with the same command when editing.

**3. Output artboard set.** `artboard.duplicate` for each size → `artboard.fitToArt`/`setProps` →
`document.export` per artboard → `identify` each output; record sizes.

**4. Symbol system.** `symbol.new` → `symbol.place` instances → edit definition
(`symbol.edit`/`exitEditing`) → `symbol.update` → verify all instances and any broken one-offs.

**5. Safe lock.** `object.lock`/`object.hide` finished groups; keep an editable copy; use
`object.unlockAll` only when ready to edit again.

## Agent operating protocol

**Lookup:** load **artcraft-command-atlas** and use `references/command_lookup.py` for exact ids/params.

**Preflight:** inspect structure/artboards; copy; define target layer/artboard/symbol scope; read params.

**Execution loop:** one structural change; inspect object/layer counts; verify render; then next.

**Evidence contract:** layer/artboard/symbol ids, output paths/sizes, clip/stack evidence; exit 0 alone
is not proof.

**Stop/escalate:** missing artboard/template; ambiguous ownership; destructive merge/flatten without
copy; symbol edit scope unclear; hidden/exported mismatch.

**Never:** invent ids; flatten the master; assume artboard index; edit symbols without checking
instances; claim output from the editor view.

## Sources & verification

- **VERIFIED:** all ids above exist in the 918-row catalogue; params text read for layer/artboard/
  symbol groups; `document.inspect`/`document.json` patterns probed.
- **ATLAS:** `references/vc-layer-artboard.md`, `00-intent-map.md`.
- **DOCS:** local ArtCraft docs; official VectorCraft README; Adobe artboard/symbol concepts.
