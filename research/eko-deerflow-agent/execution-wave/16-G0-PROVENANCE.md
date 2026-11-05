# 16 — G0 Provenance Review (independent, VPS-verified)

**Task:** `task-19` · **Reviewer:** `wave2-verifier` (independent; did not produce G0)
**Date:** 2026-11-05 · **Write scope:** this file + `.json` only. No source/test edit, no production change.

**Verdict: PROVENANCE CLOSED.** The explicit key `$env:USERPROFILE\.ssh\id_ed25519_hostinger` authenticated
to the VPS. A fresh, **staging-only** CraftTrace + PhotoCraft run — output written exclusively under
`/tmp/verifier-g0-*`, never `/opt/pod-pipeline`, never production — reproduced every G0 artifact
**byte-identically** (SHA-256 equal to `MANIFEST.json`). The report's retype gate is now correctly
`applicable:false` and the run is **9/9 applicable checks pass**.

---

## 1. Access (previously `U`, now resolved)

| Check | Result |
|---|---|
| Key used | `$env:USERPROFILE\.ssh\id_ed25519_hostinger` (411-byte ed25519), `-o BatchMode=yes` |
| Login | `SSH_OK` → `srv2108523` as `root` |
| UTC time | `2026-11-05T19:20:44Z` |
| Exit | 0 |

---

## 2. Read-only host checks

| # | Check | Observed |
|---|---|---|
| R1 | Host | `srv2108523`, `root` |
| R2 | VectorCraft | `vectorcraft-cli 0.21.1` |
| R3 | PhotoCraft | `photocraft-cli 0.20.2 (7c12f6471, 2026-11-05)` |
| R4 | Repo HEAD on VPS | `32fc71f1552bc623f4fc9636228c5cabd178be59` (`/opt/deerflow-forge`) |
| R5 | Staging tree | `/opt/pod-pipeline-staging` (copy; separate from `/opt/pod-pipeline`) |
| R6 | Staging `g0` bundle | 22 files (19 top-level + 3 `previews_trace/`) |
| R7 | Staging `g0` vs local `MANIFEST.json` | **22/22 SHA-256 + byte counts match** |
| R8 | Input asset | `data/ai-uploads/rb_tee_clean.png` = 4500×5400 RGBA |
| R9 | CraftTrace CLI | `python -m tools.craft_trace` (staging venv, Python 3.12.16) |

---

## 3. Fresh staging-only run (independent reproduction)

**Directory:** `/tmp/verifier-g0-20261105T192305Z`
**Commands (run from `/opt/pod-pipeline-staging`; outputs only to `/tmp`):**

```bash
.venv/bin/python -m tools.craft_trace \
  --input data/ai-uploads/rb_tee_clean.png \
  --output /tmp/verifier-g0-20261105T192305Z/trace_master.png \
  --svg    /tmp/verifier-g0-20261105T192305Z/trace_master.svg \
  --prep-mode alpha --canvas-width 1500 --canvas-height 1800 --print-width-in 5.0 \
  --report-json /tmp/verifier-g0-.../trace_report.json \
  --preview-dir /tmp/verifier-g0-.../previews_trace
# trace exit=0

cd data/staging/g0
/opt/craft/photocraft/photocraft-0.20.2-linux-x86_64/bin/photocraft-cli run retouch_input.png \
  --cmd image.trim --params '{"basedOn":"transparent"}' \
  --cmd image.imageSize --params '{"resolution":300,"resample":"lanczos"}' \
  --out /tmp/verifier-g0-.../retouch_master.png
# retouch exit=0
```

### 3.1 Artifact hashes — fresh run vs `MANIFEST.json`

| Artifact | Fresh SHA-256 | MANIFEST | Match |
|---|---|---|---|
| `trace_master.png` | `ab64aad724c50ecdaf99c1a873f3497a9c618ad7e9eebfa96e5df2b3572657a1` | same | **YES** |
| `trace_master.svg` | `ba64dbe3e6301a50291a8ed44458882e67950f7e817cb80d0c74aaf2f630ae95` | same | **YES** |
| `trace_stdout.txt` | `1c28a35b43bda34e520f067c3affc6395857c8f2b974a7b2dc9d5f3dd79f143c` | same | **YES** |
| `retouch_master.png` | `2995916558c82088b73d2edc5a3119bb98fceee4d5ff54f46231cb69381b3ace` | same | **YES** |
| `retouch_stdout.txt` | `27f2af2d108cd53d2bb4b4cb62c1f290ec1735d1b90a6fc5fc1708c35c0e459a` | same | **YES** |
| `previews_trace/*_100pct.png` | `d90f2879…4fac5df58` | same | **YES** |
| `previews_trace/*_black.jpg` | `5ac09038…7514887dd86` | same | **YES** |
| `previews_trace/*_white.jpg` | `0f4c9006…12b2ae9842a` | same | **YES** |
| `trace_report.json` | `19ba6546…a207577` | `c6719594…019407` | expected delta |

`trace_report.json` differs **only because it embeds absolute `/tmp/...` output/svg/preview paths** instead of
the staging `data/staging/g0/...` paths; all content fields agree.

### 3.2 Report — 9/9 applicable (retype not requested)

| Field | Observed |
|---|---|
| `ok` / `saved` | `true` / `true` |
| `canvas_px` | `[1500, 1800]` |
| `art_px` | `[1500, 1800]` |
| `dpi` | `300` |
| `retyped` / `retype_boxes` | `false` / `0` |
| `applicable_checks` | **9** |
| `retyped_text_present` | `value:"not_requested"`, `pass:null`, **`applicable:false`** |
| applicable checks passing | **9 pass, 0 fail** |
| `output_sha256` | `ab64aad7…` = actual `trace_master.png` |

`white_residual_ratio 0.0`, `edge_specks 0`, `coverage 0.4098`, `dpi 300`, `canvas_geometry [1500,1800]`,
`vector_fill_colours 12`, `edge_definition 0.0576`, `alpha_hard_edges 1.0`, `transparent_corners true` — all pass.

### 3.3 Dimensions and DPI

| Artifact | IHDR | Encoded DPI (pHYs) |
|---|---|---|
| `trace_master.png` | **1500 × 1800** | 11811 px/m = **299.9994** |
| `retouch_master.png` | **1438 × 148** | 11811 px/m = **299.9994** |

Retouch stdout reproduced exactly:
`{"command":"image.trim","result":{"height":148,"width":1438,"x":37,"y":186}}`
`{"command":"image.imageSize","result":{"height":148,"width":1438}}`

---

## 4. Reproducibility finding (recipe was under-documented)

Byte-identical reproduction requires **`--print-width-in 5.0`**, which `11-G0-EVIDENCE.md:14` does not list.
With the default `8.0` the trace still passes and the **SVG is identical** (`ba64dbe3…`), but `art_px`
becomes `[2400, 2880]` and `trace_master.png` becomes `d17ab03b…` instead of `ab64aad7…`. The G0 report's
`art_px [1500,1800]` is the clue that recovers the flag. This is a documentation gap, not an artifact defect.

---

## 5. Status of earlier gaps

| Earlier finding | Status now |
|---|---|
| `11-G0-EVIDENCE.md` direct-trace sizes (958,860 / 1,618,404) | **RESOLVED in HEAD** (`b2f39e1`): now 979,800 / 1,572,959, matching artifacts |
| "10/10" included a vacuous retype gate | **RESOLVED in HEAD**: retype gate is `applicable:false` (`not_requested`); report states `applicable_checks: 9`, and the fresh run confirms 9/9 |
| MANIFEST omitted previews | **RESOLVED**: current MANIFEST has 22 entries including the three previews; staging 22/22 match |
| G0 execution provenance | **CLOSED**: host reachable; fresh run reproduces byte-identical artifacts |

---

## 6. Residual limits

- The **wall-clock 18:04 run cannot be replayed as history** — only its outputs can be reproduced. They now are,
  byte-for-byte, on the same host with the same binaries; a different host/rsvg build may differ.
- The trace recipe's `--print-width-in 5.0` is inferred from the artifact's `art_px`; the evidence file should
  record it.
- MCP counts (33/26) and `command_batch` were verified in the bundle in task-18 and the bundle is hash-identical
  to current staging; no live MCP re-handshake was performed in this task.
- Scratch outputs remain at `/tmp/verifier-g0-20261105T192305Z` on the VPS (non-production, safe to delete).

**No production file, service, DB, or `/opt/pod-pipeline` path was read-modified or written.** All writes were
under `/tmp/verifier-g0-*`.
