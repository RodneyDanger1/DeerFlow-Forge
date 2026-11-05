---
name: artcraft-command-catalog
description: "Use when you need the exact ArtCraft command id, params or CLI flags for a design job — trace, type, path, colour, layer, artboard, export, PhotoCraft retouch. Queries the installed 918-command VectorCraft / 965-command PhotoCraft catalogues instead of guessing, and shows the verified batch/convert/batch-getcha contracts. Triggers: command id, which command, does this command exist, CLI flags, PhotoCraft run/convert/batch, ArtCraft catalogue, object.path.simplify, export options."
version: 1.0.0
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [artcraft, vectorcraft, photocraft, commands, cli, export, retouch]
    related_skills: [artcraft-vector-trace, artcraft-image-cleanup, craft-mcp-drive, ai-art-vectorize-vectorcraft]
---

# ArtCraft command catalogue

Do not memorise command ids — query the installed catalogue and run the exact id. It is the
contract: **918 VectorCraft commands in 64 groups** and a **965-row PhotoCraft engine registry**
(snapshot 2026-11-05; re-check before quoting counts). Unknown ids fail by name; typo'd params fail
or are rejected. A semantic checker (`_meta/check_skill_commands.py`) verifies every id quoted in a
SKILL.md against these catalogues.

## When to use / not use

- Use to find the id, parameter schema and CLI form for a design job.
- Use to confirm a command exists, or to port an Illustrator/Photoshop menu habit to a real id.
- Use to learn the batch/convert/export contracts before writing a script.
- Not for the AI-art trace recipe (`ai-art-vectorize-vectorcraft`) or MCP transport (`craft-mcp-drive`).

## Inputs

- The job in menu terms ("simplify paths", "unsharp mask", "export at 300 ppi").
- Installed binaries: `/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli`;
  `/opt/craft/photocraft/photocraft-0.20.2-linux-x86_64/bin/photocraft-cli`.
- An output path under `/tmp`; never overwrite the source.

## Exact commands (verified 2026-11-05)

```bash
VC=/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli
PC=/opt/craft/photocraft/photocraft-0.20.2-linux-x86_64/bin/photocraft-cli
CAT=/opt/craft/catalogues/vectorcraft-commands.json
```

List/count, filter, and read a parameter schema (python works; **jq is not installed**):

```bash
$VC commands | python3 -c 'import json,sys,collections; c=json.load(sys.stdin); g=collections.Counter(x["id"].split(".")[0] for x in c); print(len(c), len(g))'
$VC commands | python3 -c 'import json,sys; c=json.load(sys.stdin); print("\n".join(x["id"] for x in c if x["id"].startswith("imageTrace.")))'
$VC commands | python3 -c 'import json,sys; c=json.load(sys.stdin); print(next(x["params"] for x in c if x["id"]=="document.export"))'
$PC commands --filter sharpen          # 965 rows; --json adds param schemas
$PC commands --json | python3 -c 'import json,sys; c=json.load(sys.stdin); print(next(x["params"] for x in c if x["id"]=="filter.sharpen.unsharpMask"))'
```

Execute one command or a repeatable step list:

```bash
$VC run --in /tmp/art.svg --cmd select.all --cmd object.path.simplify --params '{"level":60}' --export /tmp/art_clean.svg
$VC run --in /tmp/art.png --commands /tmp/steps.json --export /tmp/out.svg
$PC run /tmp/photo.jpg --cmd filter.noise.reduceNoise --params '{"strength":6}' --cmd image.adjustments.levels --params '{"inBlack":8,"gamma":1.1,"inWhite":247}' --cmd filter.sharpen.unsharpMask --params '{"amount":110,"radius":1.0,"threshold":3}' --out /tmp/photo_clean.png
$PC convert /tmp/photo.png /tmp/photo.webp --quality 82     # lossy WebP (warning: lossy compression)
$PC batch --actions /tmp/actions.json --in /tmp/raw --out /tmp/out --recursive --stop-on-error
```

Step-list shape (`"id"` is accepted for `"command"`):

```json
[{"command":"select.all"},
 {"command":"imageTrace.make","params":{"enhanced":false,"params":{"mode":"color","palette":"limited","colors":5,"paths":70,"corners":60,"noise":8,"method":"overlapping","ignoreWhite":true}}},
 {"command":"object.path.simplify","params":{"level":60}},
 {"command":"document.export","params":{"path":"/tmp/out.svg","format":"svg","svg":{"decimals":3}}}]
```

## Document/state semantics (agent-critical)

- Catalogue rows carry `enabled`. In a headless session most document commands (`imageTrace.make`,
  `select.all`, `document.export`) show `enabled:false` until a document is open — that is **not** a
  missing command. Open with `file.new` (VectorCraft `run --cmd file.new`) or `--in FILE`; PhotoCraft
  uses `run FILE` or `run --new JSON`. There is no `needsDocument` field in the 918-row snapshot;
  infer by opening a document first.
- Success envelope per step: `{"command":"<id>","result":<json>,"step":"cmd"}`. Failure: exit 1 and a
  stderr line naming the step/command (e.g. `step 0 (imageTrace.make): nothing selected`). Parse the
  envelope; do not treat a missing result as success.
- `--export` is a batch export of the result; use a `document.export` step when you need `ppi`,
  `artboard`, `selectedOnly`, `svg.decimals` or format-specific options.
- VectorCraft `run` can start from a new document (`--cmd file.new`) with no `--in`; PhotoCraft
  requires exactly one of `FILE` or `--new`.
- `commands` is a static catalogue; it does not validate your current selection. Selection errors only
  appear when the command runs.

## Agent operating protocol (follow every time)

**Preflight**
1. `--version` both CLIs; record versions.
2. Query the target group and read the exact `params` text for every id you plan to use.
3. Confirm the input exists and the output path is new.
4. Decide whether the job needs a document (`file.new`/`--in`/`--new`) or is document-free.

**Execution loop**
1. One-command probe on a copy; parse stdout JSON; confirm the result shape and output artifact.
2. Build the step list; run it; assert each step returned a result; export to a new path.
3. Verify the file (`identify`, size/DPI/format); only then claim success.

**Evidence contract**
Quote the command, the JSON result(s), the output path/size/dimensions, and any gate values.
Exit 0 alone is not proof; a missing JSON result is a failure.

**Stop / escalate**
Unknown id; command disabled and no document route; missing exporter/plugin; missing font; batch
limits exceeded (256 steps / 8 MiB / 16 MiB); permission/read-only errors. Name the missing piece.

**Output contract**
Return versions, ids confirmed, commands run, artifacts, gate values, UNVERIFIED list.

**Never**
Invent an id/parameter; run on the source; assume exit 0 means output; edit installed catalogues.

## CLI contract — verified facts

- `vectorcraft-cli run` accepts `--in FILE`, `--cmd ID` + `--params JSON` (the params bind to the
  preceding `--cmd`), `--commands FILE|-`, repeated `--export FILE`, `--scale`; one JSON result per
  step; a failure names the step and command; **no `--dry-run`**.
- `photocraft-cli run` takes the file **positionally** (`run FILE`, not `--in`), `--new JSON`,
  `--cmd/--params`, `--out FILE`, `--format EXT`, `--quality 1-100` (lossy WebP/JPEG; no quality =
  lossless WebP). `--out` equal to input is refused unless `--in-place`.
- `photocraft-cli convert IN OUT [--quality]` writes a format conversion; an output equal to input is
  refused unless `--in-place`.
- `photocraft-cli batch --actions FILE --in DIR --out DIR` supports `--recursive`, `--naming`,
  `--start-serial`, `--action NAME`, `--stop-on-error`, `--in-place`. With `--recursive`, results go
  flat into `--out`, so same-named files overwrite earlier ones — use `--naming {name}-{serial}`.
- `commands --json` and `--filter TEXT` exist on PhotoCraft; `commands` prints a text table.
- `document.export` accepts `path, format, params? (exporter plug-in), selectedOnly, includeArtboardFill,
  artboard(s), rect, range, useArtboards, ppi, scale, background, antiAlias, interlaced, embedIcc,
  quality, colorModel, method, scans, …`; SVG options are also accepted as a nested `svg` object
  (`styling, outlineText, images, objectIds, decimals, minify, responsive, useArtboards,
  preserveEditing, metadata, fewerTspans, hiddenLayers, encoding, profile, embedFonts`) or flat.
  `ppi` wins over `scale` (px = pt ÷ 72 × ppi; 240×160 pt at 300 ppi = 1000×667).
- `text.fontList` returns the bundled system fonts (45 families on this install; `$VC run --cmd
  text.fontList` returned the list). A family missing from a document falls back to Source Sans 3
  with a warning; outlining captures the fallback.
- Result shapes differ: filter.* echoes params; image.adjustments.* returns null; imageTrace.make
  returns `{anchors, colors, id, paths}`; expand returns `{ids}`; text.fontList `{families}`.

## Key groups

`object 151 · addon 62 · select 55 · document 35 · text 35 · path 34 · edit 30 · file 28 · layer 26 ·
swatch 23 · type 23 · paint 22 · artboard 13 · imageTrace 8 · effect 8 · image 1`

Traps: `text` (content) vs `type` (conversion); `path` (pen/anchor maths) vs `object` (paths as
objects); VectorCraft `image` has only `image.info` — use `file.place`, `object.cropImage`,
`object.rasterize`; PhotoCraft has its own `image.*` registry (`image.crop`, `image.imageSize`,
`image.canvasSize`).

## Real ids vs menu guesses

| Guessed id | Reality | Use instead |
|---|---|---|
| `path.simplify` | absent | `object.path.simplify` |
| `layer.rename` | absent | `layer.setProps {ids,name}` |
| `layer.arrange.sendToBack` | absent (arrange is on objects) | `object.arrange.sendToBack {ids}`; `layer.move` |
| `image.crop` (VectorCraft) | absent in VectorCraft (`image` has only `image.info`); exists in PhotoCraft | VectorCraft: `object.cropImage`; PhotoCraft: `image.crop` |
| `text.convertToOutlines` | wrong group | `type.createOutlines` |
| `trace.*` / `document.cleanup` | absent | `imageTrace.*`; `object.path.cleanUp` + `addon.cleanup.*` |

## PhotoCraft retouch ids (schema-verified)

`filter.sharpen.unsharpMask {amount 1..500=50, radius 0.1..1000=1, threshold 0..255=0}` ·
`filter.sharpen.smartSharpen {amount=100, radius=1, reduceNoise=10}` ·
`filter.noise.reduceNoise {strength 0..10=6, preserveDetails=60, reduceColorNoise=45, sharpenDetails=25, removeJpegArtifact}` ·
`filter.noise.dustAndScratches {radius=1, threshold=0}` · `filter.noise.median {radius=1}` ·
`filter.noise.despeckle {}` · `image.adjustments.levels {inBlack,gamma,inWhite,outBlack,outWhite}` ·
`image.adjustments.curves {points}` · `image.adjustments.hueSaturation {hue,saturation,lightness}` ·
`image.adjustments.desaturate {target}` · `image.crop {x,y,width,height,angle,deleteCroppedPixels,contentAware,targetWidth,targetHeight,resolution,resample}` ·
`image.imageSize {width,height,units,percent,resolution,keepPrintSize,scaleStyles,resample}` ·
`image.canvasSize {...}` · `file.saveACopy`, `file.export.quickExport`.
`paint.sharpen`/`paint.blur` are brush tools, not filters.

## Workflow

1. Translate the job to a group; list ids; read the params text; check `enabled`.
2. Run one command on a copy; parse stdout JSON; confirm the result shape and that the output exists.
3. Write the step list; keep steps atomic/ordered; export to a new path and verify with `identify`.
4. Before saving a skill/script that quotes ids, run `cd blueprint/files/skills && python _meta/check_skill_commands.py` (or the absolute path).
5. If the snapshot catalogues are stale, regenerate `_meta/catalogues/` from the installed CLIs.

## Gates

- `vectorcraft-cli commands` → 918 entries / 64 groups; `photocraft-cli commands` → 965 rows.
- Every id is case-exact and its params text was read.
- `run` exit 0 with one JSON object per step; failure names `step N (command.id)`.
- Output exists, non-zero bytes; `identify` matches size/DPI; no unknown-key warnings.

## Refusals / failure modes

- Never invent an id or parameter; if absent, name the real command.
- Do not run `object.pathfinder.unite` on a multi-colour trace: it flattens the palette.
- Exit 0 is not proof of output; read the JSON and verify the file.
- No dry-run: run on a copy, write a new path, inspect, then commit.
- `--recursive` batch flattens names: collisions overwrite silently.

## Worked example

Path simplification: query returns `object.path.simplify` with `tolerance`, `level` 0–100, `auto`,
`cornerAngle`, `straightLines`, `wholePaths`. Verified run (vault 17 §1.8):
`{"after":10,"before":12,"ids":[2,3,4],"level":58.0}`. Then export and inspect.

## Sources & verification

- **VERIFIED (2026-11-05, srv2108523):** 918/64; 965 rows; `commands --json/--filter`; all quoted
  PhotoCraft schemas; `run`/`convert`/`batch` help contracts including `--quality` and
  `--stop-on-error`; `document.export` schema includes nested `svg {…decimals…}`; `text.fontList`
  returned 45 families; `select.all` requirement (`nothing selected`); `--params` binding; no
  `--dry-run`.
- **SCHEMA:** `/opt/craft/catalogues/*`; cheatsheet excerpt (291/918, 166/965), not the catalogue.
- **DOCS:** `/opt/craft/artcraft-docs/mcp.md`; vault `17-CRAFT-COMMAND-PLAYBOOK.md`.
- READMEs fetched: https://raw.githubusercontent.com/storytold/vectorcraft/main/README.md ·
  https://raw.githubusercontent.com/storytold/photocraft/main/README.md
