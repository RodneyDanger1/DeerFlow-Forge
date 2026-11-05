---
name: craft-mcp-drive
description: "Drive VectorCraft and PhotoCraft over MCP: start the stdio server headless or connected, initialize and list tools, map design jobs to the 33 VectorCraft and 26 PhotoCraft tools, confine file access with automation roots, and run a safe JSON-RPC command batch. Use when the user says drive VectorCraft over MCP, connect an agent to ArtCraft, use the MCP server, or automate the craft apps from an MCP client."
version: 1.0.0
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [mcp, vectorcraft, photocraft, artcraft, json-rpc, automation, agent]
    related_skills: [artcraft-command-catalog, ai-art-vectorize-vectorcraft, artcraft-vector-trace]
---

# Drive the craft apps over MCP

VectorCraft and PhotoCraft expose stdio MCP servers over the same command engine. Start the server,
initialize, list tools, then call the tool for the job. Probed facts are labelled separately from
documented behaviour in Sources.

## When to use / not use

- Use when an MCP client should drive VectorCraft/PhotoCraft, or you must pick the right tool.
- Use to confine automation to a project folder rather than the whole filesystem.
- Not for reproducible batch work (`vectorcraft-cli run`, `photocraft-cli batch`) or the AI-art recipe.

## Inputs

- Binary paths, existing read/write roots, the design job, and an output path in the write root; client registration is client-side.

## Exact commands

```bash
VC=/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli
PC=/opt/craft/photocraft/photocraft-0.20.2-linux-x86_64/bin/photocraft-cli
$VC mcp --headless --automation-read-root /opt/pod-pipeline/data/ai-uploads \
  --automation-write-root /tmp/craft-out
$VC mcp --connect 127.0.0.1:7979     # app must run as: vectorcraft --control 7979
$PC mcp                             # 26 tools; same root flags apply
```

`--connect` and roots cannot be combined (roots imply `--headless`). With no mode flag the server
tries `127.0.0.1:7979` once, then falls back to an **unconfined** headless session.

## Protocol

Newline-delimited JSON-RPC 2.0 on stdio; logs go to stderr, stdout carries protocol messages only.
Revision `2025-06-18` is current (`2025-03-26` and `2024-11-05` accepted). One message per line, at
most 16 MiB; a batch holds at most 64 messages; `command_batch` at most 256 steps and 8 MiB.
Order: `initialize` → `notifications/initialized` → `tools/list` → `tools/call`.

## Tools (probed `tools/list`)

```text
VectorCraft 33: command_list, command_run, command_batch, doc_inspect, render_preview, ui_inspect,
ui_screenshot, list_commands, run_command, inspect_document, inspect_ui, select_tool, pointer_gesture,
draw_path, draw_shape, set_paint, press_key, type_text, answer_dialog, invoke_menu, open_panel,
screenshot, open_file, save_file, export, add_text, apply_effect, pathfinder, transform, create_graph, text_wrap, undo, redo
PhotoCraft 26: command_batch, command_list, command_run, control_call, doc_close, doc_export,
doc_export_data_sets, doc_export_layers, doc_import_data_sets, doc_inspect, doc_new, doc_open,
doc_place, doc_render_preview, doc_replace_smart_object, doc_save, doc_select, jobs_cancel, jobs_list,
render_preview, session_list, ui_inspect, ui_menu_invoke, ui_pointer, ui_screenshot, ui_set
```

## Design job to tool

| Job | Tool | Underlying command |
|---|---|---|
| Discover / run any | `command_list`, `command_run` / `run_command` | any |
| Multi-step atomic edit | `command_batch` | any + `draw_*` steps |
| Trace a raster | `command_batch` / `command_run` | `imageTrace.make`, `.expand` |
| Add text | `add_text` | `text.create` |
| Draw a path or shape | `draw_path`, `draw_shape` | — |
| Inspect structure | `inspect_document` / `doc_inspect` | `document.inspect` |
| Visual check | `render_preview` (inline PNG) | — |
| Export / open / save / screenshot | `export`, `open_file`, `save_file`, `screenshot` | `document.export`, `file.open`, `document.save` |
| Raster retouch | PhotoCraft `command_run`/`command_batch` | `filter.*`, `image.adjustments.*` |

## File roots

- Read root: `open_file`, `file.place`, relinking, linked images, library/preset loads, scripts.
- Write root: `save_file`, `export`, `screenshot {path}`, Export for Screens/Web, print to file.
- Read and write are separate. Once either flag is used, access is deny-by-default per kind: a kind
  you leave out grants none (read-only cannot write). **Without any flag nothing is confined** —
  always pass both roots.
- Roots must exist or the server stops. A refused path is a readable tool error, e.g.
  `automation path rejected: outside the write root /tmp/craft-out: /etc/x.png`.

## Remote-only tools

Headless returns a tool error for `ui_inspect` / `inspect_ui`, `ui_screenshot` /
`screenshot {window:true}`, `type_text`, `answer_dialog`, `open_panel`. `press_key`, `select_tool`,
`pointer_gesture` and `invoke_menu` still work headless, with documented shortcut limits.

## Safe JSON-RPC example

Send these as single lines to the server's stdin (no pretty-printing):

```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"forge-agent","version":"1.0.0"}}}
{"jsonrpc":"2.0","method":"notifications/initialized"}
{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"open_file","arguments":{"path":"/opt/pod-pipeline/data/ai-uploads/art.png"}}}
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"command_batch","arguments":{"atomic":true,"label":"Trace art","steps":[{"id":"select.all"},{"id":"imageTrace.make","params":{"params":{"mode":"color","palette":"limited","colors":12,"paths":65,"corners":45,"noise":12,"method":"abutting","ignoreWhite":true}}},{"id":"imageTrace.expand"},{"id":"document.export","params":{"path":"/tmp/craft-out/art.svg","format":"svg"}}]}}}
{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"render_preview","arguments":{"max_side":1024}}}
```

One-shot form: pipe the five lines above into `$VC mcp --headless ...`. `command_run` takes `{"id":"select.all","params":{}}`; `run_command` takes `command` instead of `id`.

## Workflow

1. Create/confirm both roots; start `mcp --headless` with both flags; send `initialize`, read the
   result, then `notifications/initialized`.
2. `tools/list` and confirm 33 (VectorCraft) or 26 (PhotoCraft) tools.
3. `open_file` under the read root; edit with `command_batch`/`command_run`; `doc_inspect` the result.
4. `render_preview` for pixels; `export`/`save_file` under the write root; parse each reply.

## Gates

- `initialize` returns serverInfo `vectorcraft` 0.21.1 or `photocraft` 0.20.2, protocol `2025-06-18`.
- `tools/list` returns exactly 33 / 26 tools; one JSON object per line parses.
- A path outside a root returns `automation path rejected` or `filesystem access is not granted`.
- A remote-only tool headless returns `isError`, not success; `imageTrace.make` needs `select.all`.
- `render_preview` returns `image/png`; `export` returns a path and byte count.

## Refusals

- Never run unconfined on untrusted files; always pass both roots.
- No dry-run: exports and saves are real writes; do not overwrite outside the write root.
- Do not claim UI screenshots or dialog automation from a headless session; remote-only tools error.
- Do not claim the server is registered in a client; this skill only starts/talks to it.
- No product-store or customer-data writes without explicit owner approval; secrets belong in no config.

## Worked example

Flat-logo trace over MCP: headless with read `/opt/pod-pipeline/data/ai-uploads`, write
`/tmp/craft-out`; `open_file` the logo; `command_batch` with `select.all`, `imageTrace.make`
`{"preset":"Flat Logo"}`, `imageTrace.expand`, `document.export` SVG. Recorded probe (vault 17 §3G):
make `{"anchors":12,"colors":2,"id":6,"paths":3}`, expand `{"ids":[6]}`, export 956 bytes/3 paths.

## Pitfalls

- `--connect` needs the app started with `--control 7979`; roots plus `--connect` is an error.
- No mode flag falls back to headless **unconfined**; never rely on that for a real job.
- Pretty-printed JSON breaks the one-message-per-line framing.
- `initialize` must precede `notifications/initialized` and every `tools/call`.
- `command_run` takes `id`; `run_command` takes `command`; `command_batch` steps use `id`.
- Trace settings still live under `params.params`; unknown keys are rejected by name.
- `command_batch` steps can use `"$N.path"` / `"$last.path"` from earlier results.
- Headless failures are JSON-RPC `isError` results; do not retry a remote-only tool.

## Sources & verification

- **PROBED** (2026-11-05, srv2108523, this build): `initialize` returned serverInfo
  `{"name":"vectorcraft","version":"0.21.1"}` and `{"name":"photocraft","version":"0.20.2"}`,
  protocol `2025-06-18`; `tools/list` returned 33 and 26 tools, exactly as listed; CLI `--help`
  shows the roots flags and the deny-by-default wording.
- **PRIOR PROBE** (vault 17 §3G): `command_batch` trace/export over MCP executed with the quoted counts; this skill's own probe was `tools/list` only — no tool calls.
- **DOCS**: `/opt/craft/artcraft-docs/mcp.md` (roots, remote-only tools, limits, protocol);
  VectorCraft README (fetched): https://raw.githubusercontent.com/storytold/vectorcraft/main/README.md;
  **SCHEMA**: `/opt/craft/catalogues/vectorcraft-commands.json` for the command ids.
