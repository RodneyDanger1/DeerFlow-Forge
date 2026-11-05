---
name: artcraft-command-catalog
description: "Query and execute the ArtCraft command catalogues: 918 VectorCraft commands in 64 groups and the 965-row PhotoCraft engine registry. Use when the user asks what command does X, which id to use, how to batch VectorCraft or PhotoCraft, whether a command exists, or to find exact ids and params instead of guessing a menu name."
version: 1.0.0
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [artcraft, vectorcraft, photocraft, command-catalogue, cli, automation, json]
    related_skills: [ai-art-vectorize-vectorcraft, craft-mcp-drive, artcraft-vector-trace, artcraft-image-cleanup]
---

# ArtCraft command catalogue

Do not memorise command ids. Query the installed catalogue, then run the exact id. It is the
contract: 918 VectorCraft commands in 64 groups, and a 965-row PhotoCraft engine registry. A guessed
id fails by name, not silently.

## When to use / not use

- Use to find the id and params for a design job: trace, type, path, colour, layer, artboard, export.
- Use to confirm a command exists, or to port an Illustrator/Photoshop menu habit to a real id.
- Not for the AI-art trace recipe (`ai-art-vectorize-vectorcraft`) or MCP transport (`craft-mcp-drive`).

## Inputs

- The job in menu terms ("simplify paths", "unsharp mask", "export at 300 ppi"), the binary paths
  below, and an output path; nothing else is needed to query.

## Exact commands

```bash
VC=/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli
PC=/opt/craft/photocraft/photocraft-0.20.2-linux-x86_64/bin/photocraft-cli
CAT=/opt/craft/catalogues/vectorcraft-commands.json
```

List and count — python is the working path on the VPS (VERIFIED 2026-11-05):

```bash
$VC commands | python3 -c 'import json,sys,collections; c=json.load(sys.stdin); g=collections.Counter(x["id"].split(".")[0] for x in c); print(len(c), len(g))'
$VC commands | python3 -c 'import json,sys; c=json.load(sys.stdin); print("\n".join(x["id"] for x in c if x["id"].startswith("imageTrace."))); print(next(x["params"] for x in c if x["id"]=="object.path.simplify"))'
```

`jq` equivalent — **UNVERIFIED: jq is not installed on the VPS or host** (checked 2026-11-05):

```bash
jq -r '.[] | select(.id|startswith("imageTrace.")) | .id' "$CAT"
```

PhotoCraft registry — 965 rows; `--json` adds param schemas (VERIFIED):

```bash
$PC commands --json | python3 -c 'import json,sys; c=json.load(sys.stdin); print(next(x["params"] for x in c if x["id"]=="filter.sharpen.unsharpMask"))'
```

Execute one command, then a step list (a `--commands` file is the repeatable form):

```bash
$VC run --in /tmp/art.svg --cmd select.all --cmd object.path.simplify \
  --params '{"level":60}' --export /tmp/art_clean.svg
$PC run --in /tmp/photo.jpg --cmd filter.noise.reduceNoise --params '{"strength":6}' \
  --cmd image.adjustments.levels --params '{"inBlack":8,"gamma":1.1,"inWhite":247}' \
  --cmd filter.sharpen.unsharpMask --params '{"amount":110,"radius":1.0,"threshold":3}' \
  --out /tmp/photo_clean.png
$PC batch --actions /tmp/actions.json --in /tmp/raw --out /tmp/out --recursive --stop-on-error
```

Step-list shape (`/tmp/steps.json`; `"id"` is accepted for `"command"`):

```json
[{"command":"select.all"},
 {"command":"imageTrace.make","params":{"params":{"mode":"color","palette":"limited","colors":5,"paths":70,"corners":60,"noise":8,"method":"overlapping","ignoreWhite":true}}},
 {"command":"object.path.simplify","params":{"level":60}},
 {"command":"document.export","params":{"path":"/tmp/out.svg","format":"svg"}}]
```

## Key groups (918 commands, 64 groups)

`object 151 · addon 62 · select 55 · document 35 · text 35 · path 34 · edit 30 · file 28`
`layer 26 · swatch 23 · type 23 · paint 22 · color 6 · artboard 13 · imageTrace 8 · effect 8 · image 1`

Traps: `text` (content) and `type` (conversion) differ; `path` is pen/anchor maths while path
objects live under `object`; `image` has only `image.info` (use `file.place`, `object.cropImage`,
`object.rasterize`).

## PhotoCraft engine (965 rows)

Every row runs via `run --cmd` or `batch --actions`. Retouch ids and schemas that matter:

- `filter.sharpen.unsharpMask {"amount":1..500=50,"radius":0.1..1000=1,"threshold":0..255=0}`
- `filter.sharpen.smartSharpen {"amount":100,"radius":1,"reduceNoise":10}`
- `filter.noise.reduceNoise {"strength":6,"preserveDetails":60,"reduceColorNoise":45}`
- `filter.noise.dustAndScratches {"radius":1,"threshold":0}`; `filter.noise.median {"radius":1}`;
  `filter.noise.despeckle {}`; `filter.noise.addNoise {"amount":12.5,"distribution":"uniform"}`
- `image.adjustments.levels {"inBlack":0,"gamma":1,"inWhite":255,"outBlack":0,"outWhite":255}`
- `image.adjustments.curves {"points":[[0,0],[64,72],[192,200],[255,255]]}`
- `image.adjustments.hueSaturation {"hue":0,"saturation":0,"lightness":0}`
- `paint.sharpen` / `paint.blur` are brush tools, not filters.

## Real ids vs menu guesses

| Guessed id | Reality | Use instead |
|---|---|---|
| `path.simplify` | absent | `object.path.simplify` |
| `layer.rename` | absent | `layer.setProps {ids,name}` |
| `layer.arrange.sendToBack` | absent (arrange is on objects) | `object.arrange.sendToBack {ids}`; `layer.move` |
| `image.crop`, `image.adjust` | absent in **VectorCraft** (`image` has only `image.info`); PhotoCraft has its own `image.*` registry | `object.cropImage`, `object.rasterize`, `object.maskImage`; PhotoCraft via `photocraft-cli commands` |
| `text.convertToOutlines` | wrong group | `type.createOutlines` |
| `trace.*`, `document.cleanup` | absent | `imageTrace.*`; `object.path.cleanUp` + `addon.cleanup.*` |

## Pitfalls (gotchas)

- `select.all` before `imageTrace.make`, `type.createOutlines`, `object.expand`, path ops; else `nothing selected`.
- Trace settings live under `params.params`; unknown keys are rejected by name, not defaulted.
- `ppi` wins over `scale`: px = pt ÷ 72 × ppi (240×160 pt at 300 ppi = 1000×667 px).
- No dry-run in either CLI. Run on a copy, read each step's JSON, export to a new path.
- `command_batch` caps: ≤256 steps, ≤8 MiB kept results, ≤16 MiB per JSON-RPC line (MCP).
- `--params` binds to the `--cmd` before it; reorder and it lands on the wrong command.
- `text.fonts` lists fonts *in the document* (45 are bundled); a missing family falls back to Source Sans 3 with a `warning`, and outlining captures the fallback. Require `status: "exact"`.
- `--export FILE` derives format from the extension; use a `document.export` step for `ppi`, `artboard`, `selectedOnly`, `svg.decimals`.
- Result shapes differ: `filter.*` echoes params, `image.adjustments.*` returns `null`.
- The cheatsheet `/srv/vaults/storefront/30-reference/art-learning/tooling/craft-command-cheatsheet.json`
  is an excerpt (291/918 VectorCraft, 166/965 PhotoCraft), not the catalogue.

## Workflow

1. Translate the job to a group; query its ids and read the params text; check `enabled`.
2. Run one command on a copy; parse stdout JSON and confirm the result shape.
3. Write the step list; keep steps atomic and ordered; export to a new path and verify it.

## Gates

- `vectorcraft-cli commands` returns 918 entries across 64 groups; `photocraft-cli commands` 965 rows.
- Every id appears exactly (case-sensitive) and its params text was read.
- `run` exits 0 with one JSON object per step; a failure names `step N (command.id)`; the output exists with non-zero bytes and `identify` matches the requested size/DPI.

## Refusals

- Never invent an id or parameter; if absent, report it and name the real command.
- Do not run `object.pathfinder.unite` on a multi-colour trace: it flattens the palette.
- Do not claim success without the JSON result; exit 0 alone is not proof of output.

## Worked example

Find and run path simplification. The query returns `object.path.simplify` with its params
(`tolerance`, `level` 0–100, `auto`, `cornerAngle`). Run the `$VC run` line above. Observed (vault 17
§1.8): `{"after":10,"before":12,"ids":[2,3,4],"level":58.0}` — accepted, level derived from selection.

## Sources & verification

- **VERIFIED** (probed 2026-11-05 on srv2108523): 918/64; 965 PhotoCraft rows and `--json` schemas;
  every id named here exists; the python one-liners returned the quoted output; `run`, `commands`,
  `--help` contracts. `jq` returned `command not found`.
- **SCHEMA**: `/opt/craft/catalogues/vectorcraft-commands.json`,
  `/opt/craft/catalogues/photocraft-commands.json`; cheatsheet meta records 291/918 and 166/965.
- **DOCS**: `/opt/craft/artcraft-docs/mcp.md` (batch limits, key rejection); vault
  `17-CRAFT-COMMAND-PLAYBOOK.md` §1–§9 (execute-verified ids and gotchas).
- READMEs (fetched): https://raw.githubusercontent.com/storytold/vectorcraft/main/README.md · https://raw.githubusercontent.com/storytold/photocraft/main/README.md
