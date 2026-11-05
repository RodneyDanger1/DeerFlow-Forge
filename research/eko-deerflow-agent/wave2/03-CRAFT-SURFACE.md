# 03 — Craft surface audit: what VectorCraft / PhotoCraft / FilmCraft actually expose to an agent

**Task:** `task-3` (owner `craft-surface-auditor`) · **Date:** 2026-11-05 · **Method:** read-only
local evidence + read-only SSH probes on `root@179.197.88.181` (`srv2108523`).
**Audit window (UTC):** 2026-11-05T16:10Z → 16:25Z. **Nothing in the repo or on the host was
modified.** Every write below was to a new `/tmp/aud-*` path created for the probe, or to the two
`wave2/03-*` deliverables.

---

## 1. Method and evidence labels

Labels used in this document (same scheme as `REPORT.md` §“Method and evidence bar”):

| Label | Meaning |
|---|---|
| **VERIFIED** | I executed the command on the VPS or parsed the local file, and the output is quoted or counted here. |
| **READ** | I read the file/source at the cited path and line range; not executed. |
| **DOCS** | Stated by the shipped ArtCraft docs, the repo dossier, or Adobe help; not re-executed here. |
| **INFERRED** | My conclusion from the evidence; no direct probe. |
| **UNVERIFIED** | Could not be probed (blocked, out of scope, or would require a change to the host). |

**Probe rules I held to:** no source edits, no artifact overwrite, no publish, no `--in-place`,
no desktop app left running, no system package installed. GUI probe processes were killed and the
listening-port check re-run after cleanup.

### What I read locally
- `blueprint/files/skills/artcraft-command-atlas/references/` — `README.md`,
  `coverage.json`, `group-index.md`, `command-tips.md`, `sources.md`, `00-intent-map.md`,
  `catalogues/{vectorcraft,photocraft}-commands.json`, `check_atlas.py`, `command_lookup.py`,
  `recipes-vectorcraft.md`, `pc-batch-automation.md`.
- Skills: `craft-mcp-drive/SKILL.md`, `apparel-print-master/SKILL.md`,
  `ai-art-vectorize-vectorcraft/SKILL.md`, `artcraft-vector-trace/SKILL.md`,
  `artcraft-image-cleanup/SKILL.md`, `artcraft-photocraft-layers/SKILL.md`,
  `craft-agent-operator/SKILL.md` + `references/evaluation.md`.
- Tools source: `blueprint/files/tools/craft_trace.py` (390 lines),
  `blueprint/files/tools/prep_print_art.py` (440 lines).

### What I ran on the VPS (all read-only or `/tmp`-only)
`--version` on both CLIs; `commands` / `commands --json`; `--help` on both CLIs and on
`run`/`mcp`/`batch`/`commands`; a full MCP `initialize` → `notifications/initialized` →
`tools/list` → `resources/list` → `prompts/list` → `resources/templates/list` handshake for each
app; live `tools/call` probes (`open_file`, `render_preview`, `document.inspect`, `export`,
`command_batch`, `doc_open`, `doc_save`, `ui_screenshot`, out-of-root paths);
`craft_trace` on a synthetic 1024² badge (pass-path attempt + gate-fail + refusal);
`prep_print_art` (success + `E_SUBJECT_FULL_FRAME` refusal); record comparison
(`rsvg-convert` vs engine render, RMSE/MAE/SSIM); `xvfb-run vectorcraft --version` and an
`xvfb-run … --control 7999` launch attempt.

---

## 2. Environment inventory (exact paths)

| Item | Value | Evidence |
|---|---|---|
| Host | `srv2108523`, `root@179.197.88.181`, Linux `7.0.0-38-generic` | VERIFIED |
| VectorCraft CLI | `/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli` → `vectorcraft-cli 0.21.1` | VERIFIED |
| PhotoCraft CLI | `/opt/craft/photocraft/photocraft-0.20.2-linux-x86_64/bin/photocraft-cli` → `photocraft-cli 0.20.2 (7c12f6471, 2026-11-05)` | VERIFIED |
| Desktop binaries | same `bin/` dirs: `vectorcraft` (169,774,080 B), `photocraft` (139,617,776 B) | VERIFIED |
| FilmCraft | **absent.** `/opt/pod-pipeline/bin/filmcraft-cli` is a 122-byte `#!/bin/sh` stub printing `filmcraft-cli: vendor binary not installed. Replace this file and rebuild pod-craft-runner.` and exiting **127**. No `/opt/craft/filmcraft*`, no `filmcraft-cli` on PATH. | VERIFIED |
| Doc/design/effect CLIs | `/opt/pod-pipeline/bin/{vectorcraft-cli,photocraft-cli,designcraft-cli,effectcraft-cli}` are the **same stubs** (127). The real CLIs are only under `/opt/craft/*/bin/`. | VERIFIED |
| ArtCraft docs | `/opt/craft/artcraft-docs/{architecture,development,mcp,image-trace-adjustments,image-trace-quality,print-tiling,typography-lettering}.md` (`mcp.md` is 7,150 lines) | VERIFIED |
| Shot of the catalogue dir | `/opt/craft/catalogues/` contains `vectorcraft-commands.json` (552,309 B, real JSON) and `photocraft-commands.json` (84,052 B, **not JSON** — a 965-line plain-text table of id/label/menu). | VERIFIED |
| Gate tools | `/opt/pod-pipeline/tools/{craft_trace,prep_print_art,vectorize_art,artcraft,fetch_fourthwall_details}.py`; runner `/opt/pod-pipeline/.venv/bin/python` (Pillow/numpy/skimage — system `python3` has **no PIL**) | VERIFIED |
| Provider geometry | `/opt/pod-pipeline/config/fourthwall-template-details.json`, `…-details.csv`, `fourthwall-product-templates.json`, `retype-ridgeboundia.json` | VERIFIED (listing) |
| Media tooling | ImageMagick **7.1.2-18**, `rsvg-convert` **2.61.3**, `identify`, `compare`, `composite`, `magick`, `ffmpeg`, `fc-match`. No `inkscape`, no `exiftool`. `Xvfb` + `xvfb-run` present. | VERIFIED |
| Display | `DISPLAY` unset, `WAYLAND_DISPLAY` unset, no `/tmp/.X11-unix` sockets | VERIFIED |

---

## 3. Command surface

### 3.1 Registry size and provenance

| App | Rows | Groups | Capture | Byte identity |
|---|---:|---:|---|---|
| VectorCraft | **918** | **64** | `vectorcraft-cli commands` → 552,309 B JSON | local `catalogues/vectorcraft-commands.json` md5 `D197F7DB99DF9021A3FCB23A6FDB4B4F` **==** `/opt/craft/catalogues/vectorcraft-commands.json` md5 (byte-identical) — VERIFIED |
| PhotoCraft | **965** | **38** | `photocraft-cli commands --json` → 392,959 B JSON | local copy (md5 `630BD8BE7DF9E8915A0DD5742CE097C2`) is the **same size** as a fresh capture; the VPS `/opt/craft/catalogues/photocraft-commands.json` is a *different* 84,052 B text table — VERIFIED |
| FilmCraft | **unknown** | unknown | `filmcraft-cli commands` → exit **127**, 0 bytes | not installable here — VERIFIED (absence) |

Row shape — VectorCraft: `{enabled, id, label, menu, params, shortcut}`.
PhotoCraft adds `{needsDocument, disabledReason}`. Every row in both registries carries a `params`
prose schema (918/918 and 965/965) — that prose, not JSON Schema, is the contract for arguments.

### 3.2 Command-state requirements (`enabled` is state, not capability)

Both catalogues were snapshotted **with no document open**, so `enabled` reports the empty-document
state. Treating it as “this command is unsupported” would be wrong.

| Statistic | VectorCraft | PhotoCraft |
|---|---:|---:|
| `enabled: false` at snapshot | **771 / 918** (147 enabled) | **783 / 965** (182 enabled) |
| `needsDocument: true` | field absent | **731** (234 do not need a document) |
| `disabledReason` | field absent | 783 non-null: 661 “no document open”, 39 “no document”, 31 “no active document”, 13 “no selection”, 8 “select three or more layers to distribute” |

**Proof that `enabled` is *state*, not capability (VERIFIED):** the catalogue lists all 55 `select`
commands as `enabled:false`, yet `select.all` executed successfully inside an MCP `command_batch`
on an open document and returned `{"count":3}`. A statically-disabled command could not have run.

Worst-gated groups (disabled/total): VectorCraft `select` 55/55, `object` 148/151, `path` 34/34,
`layer` 26/26, `addon` 59/62; PhotoCraft has ten groups with **zero** disabled
(`tools`, `session`, `command`, `actions`, `swatches`, `prefs`, `updates`, `tool`, `cloneSource`,
`jobs`).

**State facts the harness must encode** (VERIFIED unless marked):
- Nothing runs before a document exists except `file.new`/`file.open`/`file.place`,
  `commands`, `info`, and the 234 PhotoCraft `needsDocument:false` rows.
- `select.all` is a precondition for `imageTrace.*` and most path/effect commands; missing it
  produces the named step error `step 0 (imageTrace.make): nothing selected` (DOCS/READ).
- Selection is mutable across commands; `ids` params override it where accepted (READ).
- `layer.setCurrent` / active layer decides where new art lands (READ; PhotoCraft 224-command
  `layer` family).
- Live effects stay live until expanded; text outlining (`type.createOutlines`) is irreversible
  (READ).
- There is **no `--dry-run`** in either CLI (VERIFIED from `--help`; probed unknown flag on
  PhotoCraft → exit 2).

### 3.3 CLI subcommand matrix

| App | Subcommands (VERIFIED from `--help`) |
|---|---|
| `vectorcraft-cli` | `mcp`, `run`, `commands`, `convert`, `info`, `bench`, `perf`. **No `batch` subcommand** — batch work is `run --commands`. Subcommand `--help` is not subcommand-scoped: `run --help`, `mcp --help`, `commands --help` all print the same global page. |
| `photocraft-cli` | `convert`, `info`, `run`, `batch`, `droplet`, `commands`, `mcp`, `serve`, `help`, each with its own `--help`. |

Notable flags (VERIFIED):

| Need | VectorCraft | PhotoCraft |
|---|---|---|
| Open + run | `run [--in FILE] [--cmd ID [--params JSON]]… [--commands FILE\|-]… [--export FILE]… [--scale N]` | `run <FILE\|--new JSON> [--cmd ID [--params JSON]]… --out FILE [--in-place]` |
| Batch | `run --commands FILE` (array, or JSON Lines, or `-` for stdin): **≤64 MiB and ≤100,000 steps** | `batch --actions FILE --in DIR --out DIR` (`--naming`, `--start-serial`, `--recursive`, `--stop-on-error`, `--error-log`) |
| Convert | `convert IN OUT` + `--artboard/--range/--outline-text/--decimals/--ai-version/--hidden-objects/--transparent-images`; `OUT` may not be `IN` unless `--replace-lossy` | `convert IN OUT` |
| Inspect | `info FILE` → JSON (import warnings, title, colour mode, units, artboards, counts by kind, fonts) | `info FILE [--compact]` → size/mode/depth/resolution/layer tree |
| Discover | `commands` (JSON) | `commands [--json] [--filter TEXT]` — `--filter trace` observed returning `filter.stylize.traceContour` |
| Serve | `mcp` only | `mcp` **and** `serve` (one persistent headless session over stdio or `127.0.0.1:<PORT>`) |

**Per-step output is structured JSON, not prose.** `vectorcraft-cli run` emits one object per step
tagged `"step":"open"|"cmd"|"export"` (observed 5 lines for open + 3 cmds + 1 export);
`photocraft-cli run` prints each command's JSON result.

### 3.4 Observed exit codes (this is the gate contract)

| Case | Command | Exit | Output |
|---|---|---:|---|
| VectorCraft success | `run … --commands -` | 0 | 5 JSON lines, `document.export` `{"bytes":486…}` |
| VectorCraft unknown id | `run --cmd no.such.command` | **1** | stderr `vectorcraft-cli: step 0 (no.such.command): unknown command …` |
| VectorCraft gate failure | `craft_trace … --canvas-width 400 --canvas-height 300` | **1** | report `ok:false`, `canvas_geometry` fail |
| VectorCraft refusal | `craft_trace` with no geometry | **2** | `REFUSED E_GEOMETRY_MISSING` |
| PhotoCraft same-path `--out` | `run … --out <same file>` | **1** | `error: … is the input file, so the result would replace the original: choose another output, or pass --in-place` |
| PhotoCraft same in/out folder | `batch … --out <in dir>` | **1** | `error: --out … is the --in folder …` |
| PhotoCraft unknown id | `run --cmd no.such.command` | **1** | `error: … unknown command …` |
| PhotoCraft bad flag | `run --nonsense` | **2** | clap usage error |

> **Correction to the atlas.** `command-tips.md` §6 states “exit 2 = usage/refusal (PhotoCraft CLI)”.
> Probed: **exit 2 is argument-parser usage only**; semantic refusals (same path, unknown id) exit
> **1**. `craft_trace` really does use 0/1/2 (success / gate failure / refusal) — probed all three.

---

## 4. MCP surface

Both servers are newline-delimited JSON-RPC 2.0 on stdio; logs to stderr; one message per line;
`initialize` → `notifications/initialized` → `tools/list` → `tools/call`.

### 4.1 Handshake results (VERIFIED, 2026-11-05)

| | VectorCraft | PhotoCraft |
|---|---|---|
| `serverInfo` | `{"name":"vectorcraft","title":"VectorCraft","version":"0.21.1"}` | `{"name":"photocraft","version":"0.20.2"}` |
| Negotiated `protocolVersion` (client asked `2025-06-18`) | `2025-06-18` | `2025-06-18` |
| `capabilities` | `completions, logging, prompts, resources, tools` | `resources, tools` |
| `tools/list` | **33 tools** | **26 tools** |
| `resources/list` | 3: `document`, `document-json`, `commands` | 2: `document`, `commands` |
| `prompts/list` | 5: `poster`, `icon-set`, `recolor`, `trace-and-style`, `export-set` | **0** |
| `resources/templates/list` | 4: `object`, `command`, `effect`, `swatch` | **0** |

> A sibling audit recorded `protocolVersion: 2024-11-05` for VectorCraft. Both are true: the server
> echoes the version the **client requests**; `mcp.md` says `2025-06-18` is current with
> `2025-03-26`/`2024-11-05` accepted. The harness must pin one explicitly.

### 4.2 Tool matrix

**VectorCraft — 33 tools** (VERIFIED from `tools/list`):
`command_list`, `command_run`, `command_batch`, `doc_inspect`, `render_preview`, `ui_inspect`,
`ui_screenshot`, `list_commands`, `run_command`, `inspect_document`, `inspect_ui`, `select_tool`,
`pointer_gesture`, `draw_path`, `draw_shape`, `set_paint`, `press_key`, `type_text`,
`answer_dialog`, `invoke_menu`, `open_panel`, `screenshot`, `open_file`, `save_file`, `export`,
`add_text`, `apply_effect`, `pathfinder`, `transform`, `create_graph`, `text_wrap`, `undo`, `redo`.
That is a **semantic layer over the command engine**: `draw_path`, `draw_shape`, `add_text`,
`apply_effect`, `pathfinder`, `transform` are first-class, not menu replays.

**PhotoCraft — 26 tools** (VERIFIED):
`command_batch`, `command_list`, `command_run`, `control_call`, `doc_close`, `doc_export`,
`doc_export_data_sets`, `doc_export_layers`, `doc_import_data_sets`, `doc_inspect`, `doc_new`,
`doc_open`, `doc_place`, `doc_replace_smart_object`, `doc_save`, `doc_select`, `jobs_cancel`,
`jobs_list`, `render_preview`, `session_list`, `ui_inspect`, `ui_menu_invoke`, `ui_pointer`,
`ui_screenshot`, `ui_set`.
PhotoCraft's layer is **document-centric with async jobs** (`jobs_list`, `jobs_cancel`, and
`command_batch` steps that accept `wait:false` to start a long command as a background job).

### 4.3 Roots, confinement and refusals (exact strings, VERIFIED)

- Flags: `--automation-read-root DIR` / `--automation-write-root DIR`, repeatable, deny-by-default
  once either is given, one direction only per flag, links followed. On VectorCraft the roots
  **imply `--headless`**; `--connect` and roots cannot be combined.
- Startup log when confined: `vectorcraft-cli: files confined: read /tmp/aud-ro; write /tmp/aud-rw`.
- Read-root refusal (VectorCraft `open_file /etc/hostname`):
  `open_file: automation path rejected: outside the read root /tmp/aud-ro: /etc/hostname` (`isError:true`).
- Write-root refusal (VectorCraft `export` to the read root):
  `export: automation path rejected: outside the write root /tmp/aud-rw: /tmp/aud-ro/vc_forbidden.png`.
- PhotoCraft refusal (different wording, JSON-in-text):
  `{"error":"automation path rejected: absolute paths must be inside the automation root: `/etc/hostname`"}`.
- PhotoCraft bridge mode: `--bridge 127.0.0.1:PORT` + `--control-token <64 hex>` or
  `--control-token-file PATH` (env `PHOTOCRAFT_CONTROL_PORT` / `_TOKEN` / `_TOKEN_FILE`);
  **root flags are refused in bridge mode** — roots belong to the desktop app there.
- Remote-only tools error headless (VERIFIED):
  - VC `ui_screenshot` → `ui_screenshot: \`screenshot {window:true}\` needs the desktop app: run \`vectorcraft --control 7979\` and start the server with \`vectorcraft-cli mcp --connect 127.0.0.1:7979\``.
  - PC `ui_screenshot` → `` `ui_screenshot` drives the live GUI and needs bridge mode: start the app with `photocraft --control <port> --control-token-file <path>`, then run `photocraft-cli mcp --bridge 127.0.0.1:<port> --control-token-file <path>` ``.

### 4.4 Batch / message limits

| Limit | Value | Source |
|---|---|---|
| MCP message size | 16 MiB, one JSON object per line; ≤64 messages per JSON-RPC batch | DOCS (`mcp.md` §Protocol), READ |
| `command_batch` steps | **maxItems 256** (`inputSchema`), whole call ≤8 MiB | VERIFIED (schema) |
| `command_batch` options | `atomic` (one undo step), `label`, `stop_on_error` default **true** | VERIFIED (schema) |
| `run --commands` | ≤64 MiB, ≤**100,000** steps | VERIFIED (`--help`) |
| `command_batch` result shape | `{completed, failed, created:[], results:[{ok,result}]}` | VERIFIED (probe) |

### 4.5 Concurrency hazard — PhotoCraft does not serialise `tools/call`

In one piped session I sent `doc_open` then `render_preview` then `doc_inspect` then a
`command_batch` that needs a document. **Responses arrived out of request order**, and the dependent
calls failed:

```
id 3 render_preview   isError=True  "no document open"
id 8 command_batch    {"completed":0,"failed":1,"results":[{"error":"command `image.crop` is not available right now: no document open","ok":false}]}
id 2 doc_open         isError=False {"height":300,"index":0,"layers":1,"name":"test.png",…}
```

VectorCraft, in the same style of piped session, answered **in order** and dependent calls worked
(`open_file` → `render_preview` returned a 256×192 PNG → `document.inspect` → `command_batch`).
**INFERRED (high confidence):** PhotoCraft's server dispatches calls concurrently; a harness must
await each response before issuing a dependent call, or use `command_batch` for atomic ordering.

### 4.6 Visual-inspection tools (exact schemas, VERIFIED)

| Tool | App | Arguments | Returns |
|---|---|---|---|
| `render_preview` | VC | `artboard` (0-based), `max_side` **1–4096**, `traceViews` (draw Image Trace in view mode) | inline `image/png` + text `{height,width}`; does **not** change the document. Observed: 256×192, 4,224 base64 chars |
| `screenshot` | VC | `artboard`, `max_side` 1–4096, `path` (also write PNG), `scale`, `traceViews`, `window` (desktop only) | inline PNG / file |
| `render_preview` | PC | `index` (headless only), `max_side` default **1024, max 2048** (0 = full within ceiling) | inline PNG; bridge mode returns the **window screenshot** and rejects `index` |
| `doc_render_preview` | PC | same as `render_preview` | inline PNG of the flattened document |

Screenshot (`window:true` / `ui_screenshot`) is **GUI-only** and always errors headless. A hosted
harness therefore gets **document renders**, not window pixels — which is the better evidence
anyway, but it means UI-state claims (dialogs, panels, tool state) cannot be verified headless.

---

## 5. Verification gates

Gates are the only part of the surface that converts “the command returned” into “the artifact is
acceptable”. Two live Python tools implement them.

### 5.1 `tools/craft_trace.py` — ten gates (READ source lines 238–251; run VERIFIED)

Command (production form):
```bash
cd /opt/pod-pipeline && .venv/bin/python -m tools.craft_trace \
  --input /tmp/aud-ro/badge.png --template pro_e4677535402b4eeb81 --area front_large \
  --dpi 300 --print-width-in 8 --colors 12 --paths 65 --corners 45 --noise 16 \
  --retype-json /tmp/art_retype.json \
  --output /tmp/aud-rw/ct_master.png --svg /tmp/aud-rw/ct_master.svg \
  --report-json /tmp/aud-rw/ct_report.json --preview-dir /tmp/aud-rw/previews
```
(Or `--canvas-width/--canvas-height` instead of `--template/--area`.)

Report contract: `{ok, pipeline, vectorcraft, svg, output, canvas_px, dpi, art_px,
trace_params, retyped, retype_boxes, svg_paths, svg_bytes, previews, checks{…}}`;
`ok = all(checks[*].pass)`; exit **0** ok / **1** gate fail / **2** named refusal.

| Gate | Threshold (READ) | Observed on my synthetic 1024² badge (VERIFIED) | Verdict |
|---|---|---:|---|
| `white_residual_ratio` | ≤ 0.002 | 0.0 | pass |
| `edge_specks` | == 0 (components < 150 px) | 0 | pass |
| `coverage` | 0.05 ≤ x ≤ 0.95 (art-frame alpha fill) | 0.779 | pass |
| `dpi` | ≥ 300 | 300 | pass |
| `canvas_geometry` | both sides ≥ 1500 px | [2400, 3000] | pass |
| `vector_fill_colours` | 2–40 distinct `fill="#rrggbb"` | 3 | pass |
| `edge_definition` | ≥ 0.01 (Sobel > 0.08 per alpha px) | **0.0063** | **fail** |
| `alpha_hard_edges` | share of alpha ∈ {0,255} ≥ 0.85 | 1.0 | pass |
| `transparent_corners` | 4 corners transparent | true | pass |
| `retyped_text_present` | each text box ≥ 2000 alpha px **and** overlay ≥ 2000 px | true, **`retype_boxes: 0`** | **vacuous pass** |

Two behaviours the harness must not miss (both VERIFIED):
1. **The output artifact is written before the gates run.** My canvas-400×300 run failed
   `canvas_geometry` and still left `ct_small.png` (1,626 B) and `ct_small.svg` on disk. *Artifact
   existence is not a pass*; only `ok` / exit code is.
2. **`retyped_text_present` defaults to true with no retype spec** (`retype_boxes: 0`). A green
   gate table on text-bearing art with `retype_boxes == 0` proves **nothing** about the text.

Refusal codes (READ): `E_TEMPLATE_UNKNOWN`, `E_TEMPLATE_UNRENDERABLE` (also refuses
`productionMethod: KNITTING`), `E_AREA_UNKNOWN`, `E_GEOMETRY_MISSING`, `E_INPUT_MISSING`,
`E_FONT_MISSING`, `E_VECTORCRAFT_MISSING`, `E_CUTOUT_FAILED`, `E_TRACE_FAILED`, `E_RENDER_FAILED`.
Previews written: `<stem>_black.jpg`, `<stem>_white.jpg`, `<stem>_100pct.png` (VERIFIED paths).

### 5.2 `tools/prep_print_art.py` — raster master gates (READ source; run VERIFIED)

Modes: `auto | glow | lineart | white | white-flood | alpha | none`. Defaults:
`min_coverage 0.005`, `max_coverage 0.62`, `max_upscale 2.5`.
Report: `{ok, mode, geometry_source, canvas_px, dpi, canvas_inches, subject_bbox, subject_px,
coverage, upscale_factor, print_width_in, usable_width_px, source_stats, thresholds, previews,
warnings}`.

Observed:
- Success (badge → 2400×3000): exit 0, `coverage 0.3304`, `upscale_factor 3.609`,
  **`"ok": true` with a warning** `source upscaled 3.61x (gate 2.5x): …`.
- **`ok` is hard-coded `True` on the success path** (source line 356). The 2.5× upscale limit is a
  **warning, not a gate**. A harness that trusts `ok` will accept a 3.6× upscale.
- Refusal (dark 600² full frame, `--mode white`): exit **2**,
  `REFUSED E_SUBJECT_FULL_FRAME: The mask kept 100.0% of the frame…`.

### 5.3 Verification ladder for a hosted harness

| Level | Check | Tool / command | Proves |
|---|---|---|---|
| L0 | State: document open, artboards, layers, selection, dirty | `document.inspect` / `doc_inspect` / `info` | the edit targeted something real |
| L1 | Artifact exists, non-zero, expected format, sha256 | `document.export` result bytes + `sha256sum` | bytes were produced |
| L2 | Geometry: pixels, DPI, colourspace, alpha | `identify -format '%f %wx%h %x %y %[colorspace]'` | print size / resolution |
| L3 | Declarative gates: ten-gate report, coverage/upscale, warnings | `craft_trace`, `prep_print_art` | structural print-safety |
| L4 | Render + reference compare | `render_preview`/`rsvg-convert` + `compare -metric RMSE` | the render matches an independent renderer |
| L5 | Localized perceptual diff | per-tile SSIM, bounding-box diff, edge density | *where* it changed (global SSIM hides it) |
| L6 | VLM/human critique | model or reviewer on render + brief | taste, brand fit, legibility |
| L7 | Human sign-off | owner approval | print/publish |

---

## 6. Visual inspection: what is possible, and what a critic can and cannot infer

### 6.1 Probed metrics

Ground truth = `rsvg-convert -w 400 -h 300` of a 400×300 SVG; engine = `vectorcraft-cli convert`
of the same SVG.

| Comparison | RMSE (of 65535) | Normalized | MAE (0–255) | SSIM |
|---|---:|---:|---:|---:|
| engine vs rsvg (same document) | 73.7272 | 0.001125 | 0.013 | **0.99994** |
| rsvg vs same render with a 120×100 block whited out (≈4% of frame) | 6801.74 | 0.103788 | 7.587 | **0.97872** |

**The load-bearing finding:** a deliberate, obviously-wrong 120×100 block moved SSIM by only
0.021. Global SSIM/RMSE are **not** a defect oracle for small localized errors (a missing glyph, a
lost speck, a ghost retype, a 2-px fringe). A critic needs **tile-wise SSIM + a difference bounding
box + region metrics** (edge density, alpha coverage, colour histogram per region), not one number.

DPI is readable and exact: `identify -format '%x'` on a 300-DPI master ⇒ `118.11` px/cm
(= 300/2.54). Note `--scale` also rewrites DPI metadata: an export with `--scale 0.5` of a 72-DPI
document came back `200x150` at `14.17` px/cm = **36 DPI** (VERIFIED) — so “DPI” from a scaled
export is not the document's DPI.

### 6.2 What a visual critic **can** infer
Exact pixel dimensions and DPI; colourspace and bit depth; transparency/alpha structure and
corner transparency; palette size (distinct fill hexes from SVG); coverage and edge density;
per-tile structural agreement with a reference; presence/absence and bounding boxes of changed
regions; presence of non-transparent pixels in a designated text box; layer/object counts from
`document.inspect`; that an export is byte-identical (hash) to a previously accepted artifact.

### 6.3 What it **cannot** infer
- **Print colour.** An sRGB render is not a press proof; CMYK/spot/Lab conversion needs a vendor
  proof (DOCS + READ).
- **Physical scale/feel.** A screen render or mockup proves placement only.
- **Text correctness.** A trace of AI lettering is eroded; a retype can be pixel-“present” and still
  be the wrong font/kerning. `retyped_text_present: true` with `retype_boxes: 0` is vacuous
  (VERIFIED).
- **Design quality.** `ok:true` + all gates green does not mean the brief was met (my synthetic
  badge passed 9/10 gates and is not a design).
- **Localized defects from a single global score** — see §6.1.
- **Font licensing / rights / provenance.**
- **UI state or dialogs** — headless has no window; `ui_screenshot` always errors.
- **That a different renderer would agree.** Engine-vs-rsvg agreed here (SSIM 0.99994) but that is
  one document; a critic must not assume equivalence for filters, gradients, blend modes or text.

### 6.4 Critic design that matches this surface (proposal)

`render (engine) + render (independent) → geometry assertions → gate report → tile SSIM (e.g. 8×8
tiles, threshold per tile) → difference bounding box → colour/alpha histograms → VLM review of the
top-3 worst tiles and the 100 % crop → human sign-off`. Persist: artifact sha256, render sha256,
every metric, the gate JSON verbatim, and the model + app versions, so a later regression is
attributable to a version change rather than to taste.

---

## 7. GUI fallback

| Fact | Result | Evidence |
|---|---|---|
| App binaries present | yes (`vectorcraft` 169.8 MB, `photocraft` 139.6 MB) | VERIFIED |
| Virtual display available | `Xvfb` and `xvfb-run` installed | VERIFIED |
| Binary executes under Xvfb | `xvfb-run -a vectorcraft --version` → `vectorcraft 0.21.1`, exit 0 | VERIFIED |
| Desktop app with control port under Xvfb | **fails**: panic `Library libxkbcommon-x11.so could not be loaded` → `vectorcraft_engine::guard: recovered from a panic` → `VectorCraft stopped`; port 7999 never listened (checked with `ss -ltn`); process cleaned up | VERIFIED |
| What would fix it | install the system package providing `libxkbcommon-x11.so` (e.g. `libxkbcommon-x11-0`) and retry; then `vectorcraft --control PORT --automation-read-root …` + `vectorcraft-cli mcp --connect 127.0.0.1:PORT` | INFERRED |
| PhotoCraft bridge | needs `photocraft --control <port> --control-token-file <path>` + `mcp --bridge host:port --control-token-file …`; same missing-library blocker applies to the GUI | VERIFIED (requirements) / UNVERIFIED (launch) |
| GPU | none (`/dev/dri` absent per sibling audit) | READ |

**Verdict:** the GUI fallback is **not available on this VPS today**. Headless document rendering
(`render_preview`, `export`) is the only working visual path, and it is sufficient for artifact
critique — it is not sufficient for UI-state critique or window screenshots.

---

## 8. Adobe-tutorial transfer boundaries

| Adobe concept | Transfers | Does **not** transfer | Evidence |
|---|---|---|---|
| Illustrator Image Trace panel | the parameter vocabulary — mode, palette, colours, paths, corners, noise, ignoreWhite, method — maps to `imageTrace.make {params:{…}}` | exact presets, exact UI defaults, `.ai` fidelity | DOCS (`image-trace-*`), READ |
| Photoshop retouch order (crop → retouch → colour → sharpen last → resolution) | **the order** — it is already the shipped cleanup chain | the command names; here `image.crop`, `filter.noise.*`, `image.adjustments.*`, `image.imageSize` | VERIFIED chain (skill) + READ |
| Photoshop Actions/Batch | the model — actions sets, `.atn` import, batch with naming tokens, droplets | full `.atn` coverage: `actions.photoshopStep` exists exactly because some steps have **no PhotoCraft command** and fail at playback | READ `pc-batch-automation.md`, VERIFIED `batch --help` |
| Layer/mask/smart-object semantics | layer stacks, masks, clipping, smart objects, layer comps map to the 224-command `layer` family | comps are visibility states, not files; smart-object updates can fan out | READ skill |
| Project files | PSD/PSB round-trip (README: 307/309 corpus), SVG/PDF for vectors | `.aep` (no EffectCraft), `.prproj` (FilmCraft absent, and it does not open `.prproj` even when present) | DOCS |
| Verification | the *idea* of a proof (render, preview, sample) | Adobe’s acceptance criteria; ArtCraft’s gates are local thresholds — the provider (Fourthwall) geometry is a DeerFlow Forge artefact, not an Adobe one | READ |

**Rule for a curriculum:** an Adobe tutorial contributes **intent, order and visual conventions**;
every command id, parameter name, unit and threshold must be re-derived from the local catalogue and
the gate tools. A translated tutorial is a hypothesis until it passes a gate.

---

## 9. Which Craft app should be the first harness target

**VectorCraft. It is the only app where the whole loop — work, gate, render, compare — is already
closed.**

| Criterion | VectorCraft | PhotoCraft | FilmCraft |
|---|---|---|---|
| Catalogue in hand | **918/918, 64 groups**, byte-identical local vs host | 965/965, 38 groups; local copy differs in *format* from the host copy | none — stub only |
| MCP depth | **33 tools incl. semantic draw/transform/pathfinder/text**; 3 resources, 5 prompts, 4 templates | 26 tools, document-centric; 2 resources, 0 prompts, 0 templates | none |
| Deterministic batch | `run --commands` ≤100,000 steps, per-step JSON | `batch`/`droplet`/actions, naming tokens, `--stop-on-error` | none |
| Existing gates | **10-gate `craft_trace` + `prep_print_art` + provider geometry** | no equivalent gate tool; verification is `identify` + visual + filters | none |
| Visual evidence | `render_preview` inline PNG ≤4096 + `screenshot` | `render_preview` ≤2048 (headless) | none |
| Known hazards | no dry-run; destructive pathfinder/outline; `select.all` precondition | **MCP dispatch is concurrent** (probed); no gate tool | not installed |
| Existing production proof | tee/hoodie masters + measured preset table | retouch chain executed end-to-end | — |

Rationale: VectorCraft produces the artifact the gates already judge (a gated SVG/PNG print
master), gives the richest typed tool surface, and has the only complete, machine-checked catalogue.
The harness can therefore be built and *evaluated* against a real pass/fail signal on day one.
PhotoCraft is the natural second target (its raster path needs a gate tool written before it can be
evaluated the same way). FilmCraft cannot be a target at all until a vendor binary exists.

**Caveats to carry:** VectorCraft’s own README claims only ~65% “ready for real work” (DOCS); the
command set is alpha; and every workflow is destructive-by-default with no dry-run.

---

## 10. Gaps and unknowns

1. **FilmCraft is unverifiable here.** No binary; `filmcraft-cli commands` cannot be counted. The
   dossier’s “650+ engine commands” is a README claim (DOCS), **not** a local snapshot.
2. **`/opt/pod-pipeline/bin/*-cli` are stubs.** Any harness that resolves the CLIs from that
   directory (or from PATH) gets exit 127. Use `/opt/craft/*/bin/*-cli`.
3. **`/opt/craft/catalogues/photocraft-commands.json` is not JSON** (965-line text table). Parse
   `photocraft-cli commands --json` instead.
4. **PhotoCraft MCP ordering is unsafe to pipeline** — inferenced from out-of-order responses +
   failing dependent calls; not yet characterised under load.
5. **GUI fallback blocked** by missing `libxkbcommon-x11.so`; untested after install.
6. **No dry-run anywhere**, and `craft_trace` writes the artifact before gating — the harness must
   treat exit codes + report, never file existence, as the verdict.
7. **`prep_print_art.ok` ignores the 2.5× upscale limit** (observed 3.609× with `ok:true`).
8. **`retyped_text_present` is vacuous without a retype spec.**
9. **Not probed:** CMYK/spot colour fidelity, PDF/EPS transparency flattening, `.ai`/PSD
   round-trip fidelity, `bench`/`perf`, PhotoCraft `droplet`/`serve`, data-set import/export,
   concurrent multi-document sessions, MCP `resources/read` payloads, `prompts/get`.
10. **Version drift** between the local repo catalogue and the host catalogue is zero for
    VectorCraft (byte-identical md5) but the PhotoCraft host copy is a different artefact — a
    harness must hash-pin whichever it loads.

---

## 11. Fifteen candidate questions

1. Does a harness that awaits each PhotoCraft MCP response reproduce deterministic ordering under
   load, and what is the p95 latency penalty versus pipelining?
2. Can the ten `craft_trace` gates be re-implemented as a pure function of (artifact, brief) so a
   critic can score an artifact produced by *any* app, not only the trace pipeline?
3. Is `ok:true` + all gates demonstrably insufficient? Build a fixture set where gates pass and a
   human rejects, and measure the disagreement rate.
4. What is the smallest localized-defect metric (tile SSIM? difference bbox? edge density) that
   catches a missing glyph and a 2-px key fringe that global SSIM misses?
5. Which subset of the 918 VectorCraft commands is safe to expose without a copy-and-new-path rule,
   and which are irreversible (outline, flatten, pathfinder, delete)?
6. Can the `select.all` precondition be inferred from `document.inspect` (selection non-empty) before
   a trace, eliminating the most common named failure?
7. What does `imageTrace.make` actually return across palette modes, and does the `colors` value
   predict the exported fill count within ±1?
8. Are VectorCraft and rsvg renders equivalent for every export format, or only for the simple SVG
   probed here (gradients, filters, blend modes, text, effects)?
9. Does `render_preview` at `max_side` 4096 preserve enough detail to detect a 1-px fringe, and what
   is the cost per call?
10. Can a VLM critique be calibrated against the human 1–5 rubric in
    `craft-agent-operator/references/evaluation.md` well enough to triage (not replace) review?
11. What is the deterministic-output claim for repeated identical command batches — byte-identical
    exports, or documented variance? (The eval protocol requires an answer.)
12. Which PhotoCraft commands are genuinely unavailable headless versus merely state-gated (the 234
    `needsDocument:false` set is the floor, but is it the whole floor)?
13. Does `commands --filter` plus the params prose give a cheaper, more reliable lookup than the
    918-row catalogue in context, and what is the token cost of each?
14. What is the correct conformance test for a gate tool: a fixture per gate (pass + fail), with the
    exit code and report asserted? (Both `craft_trace` and `prep_print_art` need this.)
15. If `libxkbcommon-x11` is installed, does `vectorcraft --control PORT` under Xvfb give a stable
    bridge session — and is a window screenshot ever better evidence than `render_preview` for what
    the harness needs to verify?

---

## 12. Appendix — exact identifiers used in this audit

**Paths**
`/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/{vectorcraft,vectorcraft-cli}` ·
`/opt/craft/photocraft/photocraft-0.20.2-linux-x86_64/bin/{photocraft,photocraft-cli}` ·
`/opt/craft/artcraft-docs/mcp.md` · `/opt/craft/catalogues/*.json` ·
`/opt/pod-pipeline/{tools,config,bin,.venv/bin/python}` ·
`blueprint/files/skills/artcraft-command-atlas/references/**` ·
`blueprint/files/tools/{craft_trace,prep_print_art}.py`

**Command ids used in probes or cited as anchors**
`file.new`, `file.open`, `file.place`, `select.all`, `select.none`, `object.path.simplify`,
`object.path.simplify {level}`, `object.path.cleanUp`, `object.path.outlineStroke`,
`object.path.offsetPath`, `object.compoundPath.make`, `imageTrace.make`, `imageTrace.expand`,
`type.createOutlines`, `text.create`, `document.inspect`, `document.json`, `document.export`,
`document.exportPdf`, `document.formats`, `image.imageSize`, `image.crop`, `image.canvasSize`,
`image.adjustments.levels`, `image.adjustments.curves`, `image.adjustments.brightnessContrast`,
`image.adjustments.hueSaturation`, `filter.noise.dustAndScratches`, `filter.noise.despeckle`,
`filter.sharpen.unsharpMask`, `filter.stylize.traceContour`,
`layer.layerMask.revealSelection`, `layer.createClippingMask`, `layer.smartObjects.convertToSmartObject`,
`layer.flattenImage`, `file.export.layersToFiles`, `actions.play`, `actions.photoshopStep`.

**Probe artifacts (host `/tmp`, disposable):** `/tmp/aud-ro/{test.svg,test.png,ref400.png,badge.png,dark.png}`,
`/tmp/aud-rw/{vc_out.png,vc400.png,altered.png,pc_out.png,ct_*,x1..x4*,stdin_run.*,previews/}`,
`/tmp/aud-batch/{in,out}`, `/tmp/aud-*.jsonl`. None are deliverables.
