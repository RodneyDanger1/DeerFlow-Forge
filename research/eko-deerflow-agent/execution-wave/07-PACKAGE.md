# 07 — Packaging Freeze Record (SUPERSEDED)

**Task:** task-14 · **Status:** SUPERSEDED — the Lead froze the source and executed the final copy
**Frozen:** 2026-11-05T16:50:20Z · **Producer:** `examples-skills-packager`

> **STOP — this is a historical freeze record, not an executable manifest.**
> The Lead halted this task at the freeze point and confirmed that the final package was already
> built and copied by the Lead. The earlier 55-file default manifest is superseded and must not be
> copied, merged, or used to overwrite anything. No file was copied to the Desktop target or the
> vault by this task.

## 1. What happened

- This seat built a **55-file candidate** (50 copies + 5 generated: `research/` corpus subset,
  five canonical skills, extracted examples, generated `INDEX.json` and `BIBLIOGRAPHY.md`) and
  validated it in a temporary staging tree.
- The source corpus was still being written during the build (`00-START-HERE.md`, `GOALS.md`,
  `ERRATA.md`, `examples/`, `diagrams/index.html`, and new `execution-wave/` files appeared between
  10:42 and 10:50 local). A follow-up run staged 56 files and its word-count reconciliation failed,
  which is why the build was halted.
- The Lead issued **FREEZE NOW**, froze the source at `2026-11-05T16:50:20Z`, and built the final
  package. The Lead's 129-file package supersedes this manifest.

## 2. Final package (Lead-executed; observed read-only at freeze)

| Property | Value |
|---|---|
| Destination | `C:\Users\Riley\Desktop\Ridgeboundia-Agent-Research` |
| Files | **129** (observed read-only by this task) |
| Bytes | 4,499,906 |
| Top level | `00-START-HERE.md`, `BIBLIOGRAPHY.md`, `ERRATA.md`, `GOALS.md`, `INDEX.json`, `README.md`, `REPORT.md`, `diagrams/`, `examples/`, `execution-wave/`, `skills/`, `wave2/` |
| Vault staging | `/srv/vaults/storefront/30-reference/art-learning/29-AGENT-HARNESS-RESEARCH` (Lead-owned; not accessed from this seat) |
| Vault index | `00-ART-LEARNING-INDEX.md` (Lead-owned append) |

The final layout is flat: the corpus lives at the package root, with `skills/`, `examples/` and the
execution-wave deliverables alongside it. The superseded candidate used `research/` as a corpus
subdirectory and is shown only for provenance.

## 3. Superseded 55-file candidate (historical)

| Validation (temporary staging) | Result |
|---|---|
| Files staged | 55 = 50 copies + 5 generated |
| JSON parsed | 9; **0 errors** |
| Markdown links | 20/20 resolved; **0 broken**, 0 escaping the package |
| Words | 105,794 |
| Empty files | 0 |
| Case-insensitive duplicate paths | none |
| Example copies (`examples/` vs `research/wave2/`) | byte-identical |
| Source files unchanged during that run | yes |
| Drift before freeze | later run staged 56; word totals no longer reconciled → halted |

These numbers describe the candidate subset only. They are not the final package's counts, and the
candidate's hashes are stale after the freeze. The two files in this folder are the only outputs
this task wrote.

## 4. Snapshot caveat

- **Freeze authority:** the Lead's build is authoritative; this record does not re-verify its 129
  files or its vault copy.
- **No action:** there is no copy script in this version. Do not copy from, or apply, this manifest.
- **Source at freeze:** 117 files / 4,335,911 bytes observed (excluding `__pycache__` and these two
  manifest files); the source tree was not modified by this task.
- **Vault:** the actual vault copy and the `00-ART-LEARNING-INDEX.md` entry are Lead-owned and were
  not available from this seat.
- **Historical counts:** the earlier word/URL/link counts apply only to the superseded 55-file
  candidate; they must not be quoted as final-package metrics.

## 5. Completion

task-14 is marked complete **with this snapshot caveat**: the packaging question ("can the corpus and
skills be assembled without breaking links or JSON?") was answered by the candidate validation, but
the final artifact is the Lead-built 129-file package, not this manifest.

See `07-PACKAGE.json` for the machine-readable freeze record, observed counts, and caveats.
