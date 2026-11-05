# 14 — Independent G0 Artifact-Consistency Review

**Task:** `task-18` · **Reviewer:** `wave2-verifier` (independent; did not produce the G0 bundle)
**Date:** 2026-11-05 · **Bundle:** `research/eko-deerflow-agent/execution-wave/g0/` + `MANIFEST.json`
**Write scope:** this file + `.json` only. No source/test edit, no test weakening, no production change.
**Result split:** artifact consistency **PASS** · execution provenance **U** (no VPS access; reviewer's SSH is known-denied).

**Method:** recomputed SHA-256 and byte counts for every manifest entry; parsed PNG IHDR and pHYs chunks
directly; parsed `trace_report.json`; parsed every MCP JSONL line. No external tool was trusted to
"confirm" its own output.

---

## 1. Checks performed and observed results

| # | Check | Observed | Status |
|---|---|---|---|
| A1 | `MANIFEST.json` SHA-256 + byte count vs files on disk (19 entries) | `manifest entries=19 ok=19 bad=0` | **PASS** |
| A2 | `trace_report.json` parse + gate summary | `ok: true`; `saved: true`; `checks: 10`; `all pass: True` | **PASS** |
| A3 | `canvas_px` / `art_px` | `[1500, 1800]` / `[1500, 1800]` | **PASS** |
| A4 | `dpi` | `300` | **PASS** |
| A5 | `output_sha256` vs actual `trace_master.png` hash | `ab64aad724c50ecdaf99c1a873f3497a9c618ad7e9eebfa96e5df2b3572657a1` == actual | **PASS** |
| A6 | `output` / `svg` paths exist in bundle | `data/staging/g0/trace_master.png` / `…svg` (names resolve to bundle files) | **PASS** |
| A7 | `svg_bytes` 2465883 vs actual `trace_master.svg` | 2,465,883 == 2,465,883 | **PASS** |
| A8 | `svg_paths` 1109 vs actual `<path` count | 1109 == 1109 | **PASS** |
| A9 | `trace_master.png` real pixel size (IHDR) | **1500 × 1800** | **PASS** |
| A10 | retouch stdout dimensions | `image.trim` → `{height:148,width:1438}`; `image.imageSize` → `{height:148,width:1438}` | **PASS** |
| A11 | `retouch_master.png` real pixel size (IHDR) | **1438 × 148** (matches stdout) | **PASS** |
| A12 | Encoded DPI (pHYs) — retouch and trace masters | `11811 px/m` = **299.9994 DPI** on both | **PASS** |
| A13 | Direct trace SVG presence/size vs captured export line | file 979,800 B == stdout `bytes:979800`; manifest byte count same | **PASS** |
| A14 | Direct trace PDF presence/size vs captured export line | file 1,572,959 B == stdout `bytes:1572959`; manifest byte count same | **PASS** |
| A15 | Direct trace SVG SHA-256 | `9f2233e570f46aac3c00039db02200a0d5d42818d39a839553f380c6caa0ad05` (manifest == 11-G0 §2) | **PASS** |
| A16 | Direct trace PDF SHA-256 | `66c4697dfb879dac3b4f0607f82d0fa052410932be98690e8ec8f7becaa49b65` (manifest) | **PASS** |
| A17 | MCP VectorCraft `tools/list` count | **33 tools** (`command_list`, `command_run`, `command_batch`, `doc_inspect`, `render_preview`, …) | **PASS** |
| A18 | MCP PhotoCraft `tools/list` count | **26 tools** (`command_batch`, `command_list`, `command_run`, `control_call`, `doc_close`, …) | **PASS** |
| A19 | `command_batch` completion | `{"completed":1,"failed":0,...}`; `doc_open` = 1500×525 matching `retouch_input.png` IHDR 1500×525 | **PASS** |
| A20 | Repo tree after review | only the two new review files untracked; no tracked diff | **PASS** |

---

## 2. Claim → status

| Claim (source) | Independent result | Status |
|---|---|---|
| MANIFEST hashes/sizes describe the bundle | 19/19 entries match on disk | **PASS** |
| `trace_report`: 10/10 checks pass | 10 checks, all `pass:true` | **PASS (literal)** |
| `trace_report`: canvas 1500×1800, DPI 300, `saved:true` | all present and correct; PNG IHDR confirms 1500×1800; pHYs confirms 299.9994 DPI | **PASS** |
| `output_sha256` equals `trace_master.png` | exact match | **PASS** |
| Retouch is 1438×148 | stdout AND PNG IHDR both 1438×148 | **PASS** |
| Direct trace produces SVG/PDF (979,800 / 1,572,959 B) | files present; sizes match capture and manifest | **PASS** |
| MCP counts 33 (VC) / 26 (PC) | counted from captured `tools/list` responses | **PASS** |
| `command_batch completed:1 failed:0` | captured result shows exactly that | **PASS** |
| Artifacts originate from `/opt/pod-pipeline-staging/data/staging/g0` on the VPS | `MANIFEST.source` records it; **no VPS access to confirm provenance** | **U** |
| The VPS binaries/versions in `11-G0-EVIDENCE.md` §1 ran these commands | No `--version` capture inside the bundle; SSH denied | **U** |
| `11-G0-EVIDENCE.md` direct-trace sizes: SVG **958,860 B**, PDF **1,618,404 B** | Actual artifacts + captured stdout: SVG **979,800 B**, PDF **1,572,959 B**. The committed HEAD still carries the old figures; **during this review the working tree was independently corrected** (see D1) | **FAIL in HEAD → corrected in working tree (uncommitted)** |

---

## 3. Contradictions / discrepancies (reported, not fixed)

| # | Finding | Evidence | Severity |
|---|---|---|---|
| **D1** | **`11-G0-EVIDENCE.md:13` byte sizes were wrong in committed HEAD.** At review start it stated direct trace "SVG **958,860 B**, PDF **1,618,404 B**"; the bundle's files, `MANIFEST.json` and `direct_trace_stdout.txt` all say **979,800 B** and **1,572,959 B**. The three SHA-256 values that doc lists were already correct. **Concurrent correction:** while this review was running, another seat updated the working-tree file to the correct sizes and added the note "earlier byte figures in this table were transposed from a different copy". That edit is uncommitted and was not made by this reviewer; artifact-vs-HEAD is still inconsistent until it is committed. | `11-G0-EVIDENCE.md:13` (HEAD) vs `MANIFEST.json`, `direct_trace_stdout.txt`, actual files; working-tree diff | **Medium (resolved uncommitted)** |
| **D2** | **The 10/10 pass includes a vacuous retype check.** `trace_report.json` has `retyped:false`, `retype_boxes:0`, yet `retyped_text_present = {value:true, pass:true}`. In `craft_trace.py` `text_ok` defaults to `True` and is only falsified when `spec is not None`, so with no retype requested the check passes without evidence. "10/10" is literally true but one gate is decorative for this run — exactly the vacuity flagged earlier in `09-GOAL-GAP-PLAN.md` C9. | `trace_report.json:33-34,82-85`; `craft_trace.py:212-217,256` | **Medium** |
| **D3** | **MANIFEST does not cover every file in the bundle.** 19 entries; the directory has 24 files. Unhashed: `MANIFEST.json`, `g0-artifacts.tgz`, and the three `previews_trace/*` images — which `trace_report.json` itself references as evidence. | manifest coverage scan: `on_disk 24`, `not_in_manifest = [MANIFEST.json, g0-artifacts.tgz, previews_trace/trace_master_100pct.png, …black.jpg, …white.jpg]` | Low |
| **D4** | **`11-G0-EVIDENCE.md` §2 lists no hash for `direct_trace.pdf`.** The manifest has one and it verifies, but the evidence table omits the PDF hash (and all retouch/input hashes are likewise absent from the prose table). | `11-G0-EVIDENCE.md:22-30` vs `MANIFEST.json` | Low |
| **D5** | **Provenance is self-asserted only.** `MANIFEST.source` is a text field; nothing binds the bundle to the VPS (no signed `--version` capture, no hostname/date log inside the bundle). Artifact *internal* consistency is strong; artifact *origin* remains `U`. | `MANIFEST.json:2`; bundle contents | Low (inherent, given no VPS) |

No failure was found in **artifact consistency** itself: every hash, size, dimension, gate, count and
batch result that the Lead asked to be checked is internally correct and matches the captured stdout.

---

## 4. Not reproducible from this seat

- **Execution provenance:** the bundle was allegedly produced in `/opt/pod-pipeline-staging`; the reviewer has
  no VPS access (SSH known-denied). Origin is `U`, not `PASS`/`FAIL`.
- **Binary versions / staging pytest / host environment:** not captured inside the bundle.
- **The `g0-artifacts.tgz` archive:** listing matches the 19 files plus `previews_trace/`; its internal hashes
  were not separately compared because the extracted files already hash-match the manifest.

---

## 5. Verdict

| Area | Verdict |
|---|---|
| MANIFEST ↔ artifacts (19/19 SHA-256 + sizes) | **PASS** |
| `trace_report.json` invariants (10/10, canvas 1500×1800, DPI 300, `saved`, `output_sha256`) | **PASS** |
| Retouch 1438×148 (stdout + PNG IHDR) | **PASS** |
| Direct SVG/PDF hashes and sizes | **PASS** |
| MCP tool counts 33/26 and `command_batch` completed:1 failed:0 | **PASS** |
| **Execution provenance (VPS/staging)** | **U** |
| **`11-G0-EVIDENCE.md` direct-trace byte counts** | **FAIL in committed HEAD** (958,860/1,618,404 vs actual 979,800/1,572,959) — **corrected in the working tree during this review, uncommitted** |

The G0 bundle is internally consistent and self-corroborating: all 19 manifest hashes and sizes verify,
the trace report's hashes/dimensions/gates agree with the files, the retouch and direct-trace logs agree
with the PNG dimensions and file sizes, and both MCP captures show 33/26 tools with a clean batch. The one
artifact-level contradiction — the stale size figures in `11-G0-EVIDENCE.md` — was being corrected by
another seat in the working tree while this review ran; it remains a HEAD-level inconsistency until that
edit is committed. The vacuous retype gate and the partial manifest coverage are noted above. Where the
bundle *came from* cannot be verified here.

**Note on concurrency:** this review made no edit to `11-G0-EVIDENCE.md`. The working-tree change to that
file appeared during the review and is attributed to another seat; the reviewer re-read it after the change
to confirm the corrected figures match the artifacts (they do).
