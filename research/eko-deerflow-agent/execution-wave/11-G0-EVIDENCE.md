# G0 evidence — Phase 0 staging gate

**Date:** 2026-11-05 · **Status:** **PASS for direct CLI execution**; **PARTIAL** for DeerFlow MCP registration.
**Environment:** `/opt/pod-pipeline-staging` (copy of `/opt/pod-pipeline`), real binaries under `/opt/craft`.
**Production change:** none. `/opt/pod-pipeline`, the `pod` DB, and the live DeerFlow config were not modified.

## 1. What was run

| Check | Command (staging) | Result |
|---|---|---|
| VectorCraft version | `vectorcraft-cli --version` | `0.21.1` |
| PhotoCraft version | `photocraft-cli --version` | `0.20.2 (7c12f6471, 2026-11-05)` |
| Direct VectorCraft trace | `run --in rb_tee_clean.png --cmd select.all --cmd imageTrace.make --params '<measured>' --cmd imageTrace.expand --export direct_trace.svg --export direct_trace.pdf` | exit 0; SVG **979,800 B**, PDF **1,572,959 B** (hash-pinned; earlier byte figures in this table were transposed from a different copy) |
| CraftTrace pipeline | `python -m tools.craft_trace … --prep-mode alpha --canvas-width 1500 --canvas-height 1800` | exit 0; `ok:true`, `saved:true`, **9/9 applicable checks pass**; retype gate `not_requested` (`applicable:false`), not a decorative pass |
| PhotoCraft retouch | `run retouch_input.png --cmd image.trim --params '{"basedOn":"transparent"}' --cmd image.imageSize --params '{"resolution":300,"resample":"lanczos"}' --out retouch_master.png` | exit 0; PNG **1438×148**, DPI 299.9994 |
| Full staging tests | `pytest tests -q` | **54 passed, 4 skipped** |
| Launcher syntax | `bash -n deploy/setup-pipeline.sh` | exit 0 |
| MCP VectorCraft | `mcp --headless --automation-read-root … --automation-write-root …` + `initialize` + `tools/list` | **33 tools** |
| MCP PhotoCraft | `mcp --automation-read-root … --automation-write-root …` + `tools/list` | **26 tools** |
| MCP command batch | PhotoCraft `doc_open` + `command_batch [{"id":"image.imageSize"}]` | `completed:1 failed:0`, `{width:1500,height:525}` |

## 2. Artifact hashes

| Artifact | SHA-256 |
|---|---|
| `trace_master.png` (CraftTrace output) | `ab64aad724c50ecdaf99c1a873f3497a9c618ad7e9eebfa96e5df2b3572657a1` |
| `trace_master.svg` | `ba64dbe3e6301a50291a8ed44458882e67950f7e817cb80d0c74aaf2f630ae95` |
| `trace_report.json` | `c6719594e96f82bd981a246ed3f64e91bc93c68dac2655408449e40489019407` |
| `direct_trace.svg` | `9f2233e570f46aac3c00039db02200a0d5d42818d39a839553f380c6caa0ad05` |
| `direct_trace.pdf` | `66c4697dfb879dac3b4f0607f82d0fa052410932be98690e8ec8f7becaa49b65` |
| `retouch_master.png` | `2995916558c82088b73d2edc5a3119bb98fceee4d5ff54f46231cb69381b3ace` |

CraftTrace checks: `white_residual_ratio`, `edge_specks`, `coverage`, `dpi`, `canvas_geometry`,
`vector_fill_colours`, `edge_definition`, `alpha_hard_edges`, `transparent_corners` all pass;
`retyped_text_present` is **not applicable** because no retype was requested. After the independent
review found the old decorative pass, the gate was corrected and the real report regenerated.

**Artifacts are now copied into `execution-wave/g0/`** with a generated `MANIFEST.json` covering all
22 files (including the three previews); this closes the “absent from workspace” and partial-manifest
gaps for artifact inspection. It does not make the execution independently reproducible without VPS access.

**Correction (independent review D2):** the original report showed `retype_boxes:0` but
`retyped_text_present: pass:true`. That was a decorative pass; the gate now reports
`applicable:false` and `pass:null`, and the real report was regenerated. The run is **9/9 applicable
gates**, not 10/10.

## 3. What this proves

- The real VectorCraft binary accepts the measured `run` contract and produces SVG/PDF.
- The real PhotoCraft binary accepts `run FILE --cmd … --out`.
- The new preflight/argv/gate/source-mutation code passes the full staging suite.
- CraftTrace can now use an existing alpha channel (`--prep-mode alpha`) instead of failing the
  white-key cutout on a full-frame RGBA asset. Without this option, the real trace refused with
  `E_SUBJECT_FULL_FRAME`; that is a real input-mode gap, now fixed for the alpha case.
- Both MCP servers expose the expected tool counts in staging.

## 4. What this does NOT prove

- **DeerFlow registration** of the two MCP servers was **not applied**; only direct `tools/list` and
  a direct `command_batch` were tested. The production `extensions_config.json` and gateway were not
  modified. A staging example is at `blueprint/files/deploy/deerflow-craft-extensions.example.json`.
- The full product route still stops at absent DesignCraft/EffectCraft/FilmCraft steps; only
  VectorCraft/PhotoCraft are present.
- No production cutover, no `pod` DB write, no publish, no token spend.
- The real retouch is a trim/size operation, not a creative retouch; it proves the transport and
  size contract, not artistic quality.

## 5. Verdict

**G0 = PASS for real VC trace + PC retouch + staging tests + MCP tool discovery.**
**I2 registration remains PARTIAL until the staging/production DeerFlow config is applied and an
agent turn lists `vectorcraft_*` / `photocraft_*` tools.**
