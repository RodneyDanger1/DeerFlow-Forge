# Capability and Documentation Truth Audit — 2026-11-05

**Task:** task-23 (Wave 1, read-only) · **Seat:** examples-skills-packager (capability/documentation truth)
**Snapshot:** 2026-11-05 ~16:20–16:30 America/Chicago · **Source edits:** none · **Production access:** none

Scope audited: `README.md`, `docs/CAPABILITY-MATRIX.md`, `docs/PLAN-CONTINUATION.md`,
`research/eko-deerflow-agent/README.md`, `research/eko-deerflow-agent/00-START-HERE.md`,
`research/eko-deerflow-agent/ARCHITECTURE.md`. Probe commands run from the repo root:
`git ls-files`, recursive file/dir counts under `research/eko-deerflow-agent`, `blueprint/files/skills`,
`C:\Users\Riley\Desktop\Ridgeboundia-Agent-Research`, `Select-String` test-definition counts, and
`CREATE TABLE` counts in `blueprint/files/sql/schema_forge.sql`. No test suite, browser, MCP or
model call was executed in this pass.

## 0. Verdict summary

- **Counts that still hold:** 179 source-corpus files, 189-file Desktop package, 400 answers,
  8 diagram sources (+1 integration map), 13 Forge tables, 39 skills (40 dirs incl. `_meta`), 6 examples.
- **Stale / unsupported in scope:** "10 skills" in the 189-file Desktop package; "orchestrated by
  DeerFlow 2.2"; "stub tests"; conflicting W1/W2 pass counts in `PLAN-CONTINUATION.md`; and several
  runner claims presented as static facts.
- **Unverified this pass (must not be quoted as verified):** every `npm test`/lint/typecheck/build
  number, Playwright/smoke counts, pipeline/Forge test counts, MCP 33/26 tool proof, G0 9/9/hash/DPI,
  4,456-byte download, 18/18 SQL assertions, 36 schema transitions, 15/15 UI checks.

## 1. Claim vs evidence (numeric claims)

| # | Claim and location | Recompute / evidence | Verdict |
|---|---|---|---|
| 1 | 179 source files — `research/.../README.md:49`; `docs/CAPABILITY-MATRIX.md:25` | `Get-ChildItem research/eko-deerflow-agent -Recurse -File` excluding `__pycache__` = **179** | **VERIFIED** |
| 2 | 189-file Desktop package — same lines; `CAPABILITY-MATRIX.md:61` | `C:\Users\Riley\Desktop\Ridgeboundia-Agent-Research` recursive file count = **189** | **VERIFIED** |
| 3 | 400 answers — `research/.../README.md:49`; `CAPABILITY-MATRIX.md:25` | `REPORT.md` `**Qn.` = **200** + `wave2/08-200-QUESTIONS.md` = **200** → **400** | **VERIFIED** |
| 4 | 8 diagrams (+1 integration map) — `README.md:195–196`; `CAPABILITY-MATRIX.md:25,66` | `diagrams/*.mmd` = **8**; `INTEGRATIONS.mmd` separate | **VERIFIED** |
| 5 | 6 examples — `CAPABILITY-MATRIX.md:25`; `research/.../README.md:49` | `research/eko-deerflow-agent/examples/` = 6 example `.md` + README | **VERIFIED** |
| 6 | 39 skills — `README.md` (capability table), `CAPABILITY-MATRIX.md:24`; `PLAN-CONTINUATION.md:15,51` | `blueprint/files/skills` = **40 directories**: 39 skills + `_meta` | **VERIFIED (as 39 skills)** |
| 7 | 13 Forge tables — `README.md:103`; `CAPABILITY-MATRIX.md:15` | `CREATE TABLE` in `blueprint/files/sql/schema_forge.sql` = **13** | **VERIFIED** |
| 8 | 36 schema transitions/edges — `README.md:103`; `research/.../README.md:88`; `CAPABILITY-MATRIX.md:15` | Not recomputed in this pass (query returned 0 because the probe used a relative path from a fresh shell) | **UNVERIFIED** |
| 9 | "189-file desktop package includes 10 skills" — `CAPABILITY-MATRIX.md:25` | Observed `<package>\skills` = **6 directories** (not 10); exact skill names not enumerated in this pass | **STALE / INACCURATE** |
| 10 | `npm run test` 65/65 — `README.md:30,203` | Not executed. Static `test(`/`it(` occurrences = 272, so 65 is a runner-qualified figure, not statically reproducible | **UNVERIFIED** |
| 11 | lint 0 errors / 5 warnings — `README.md:29` | Not executed | **UNVERIFIED** |
| 12 | `tsc --noEmit` clean, build with `node-server` — `README.md:28,203` | Not executed | **UNVERIFIED** |
| 13 | Pipeline/Forge suite 139 pass / 4 skip — `README.md:206`; `CAPABILITY-MATRIX.md:26`; `PLAN-CONTINUATION.md:20,22` | Not executed. Static `def test_` count in `blueprint/files/tests` = **141**, which is neither 139 nor 139+4 | **UNVERIFIED** |
| 14 | W1-A 53 pass/4 skip — `PLAN-CONTINUATION.md:11` | Same file reports 139 pass/4 skip at lines 20, 22 | **HISTORICAL / INTERNAL CONFLICT** |
| 15 | W2 close 97 pass/9 skip — `PLAN-CONTINUATION.md:20` | Superseded in the same sentence by 139 pass/4 skip | **HISTORICAL** |
| 16 | Gateway 33/33, SQL 18/18, repo 4/4, service 5/5, verifier 8/8, critic 14/14, e2e 2/2 — `README.md:208–209`; `CAPABILITY-MATRIX.md:14–23` | Not executed this pass | **UNVERIFIED** |
| 17 | 15/15 Playwright control checks; smoke 0 errors/0 failures/0 overflow — `README.md:205`; `CAPABILITY-MATRIX.md:11–12` | Not executed this pass | **UNVERIFIED** |
| 18 | MCP 33/26 tools proven; `command_batch` — `research/.../README.md:43,59,81`; `CAPABILITY-MATRIX.md:41`; `PLAN-CONTINUATION.md:12` | No MCP server started; no `tools/list` call | **UNVERIFIED** |
| 19 | G0 9/9 applicable, hash `ab64aad7…`, 1500×1800 @ 299.9994 DPI, 22/22 hashes — `CAPABILITY-MATRIX.md:23,73–74`; `README.md:210–211` | Not re-executed; artifact bundle not re-hashed | **UNVERIFIED / HISTORICAL EVIDENCE** |
| 20 | Download 4,456 bytes — `CAPABILITY-MATRIX.md:12` | Not measured this pass | **UNVERIFIED** |
| 21 | Promotion Wilson 95% LB for 3/3 = 0.4385 — `CAPABILITY-MATRIX.md:67,71`; `research/.../README.md:113` | Recomputed Wilson lower bound at 95% for 3/3 = **0.4385** (standalone arithmetic) | **VERIFIED (arithmetic)** |
| 22 | "5 tabs" console — `CAPABILITY-MATRIX.md:11` | Tab names in `README.md:12` are 5 (board, routes, sandbox, playbook, sources), but route/file count was not recomputed | **UNVERIFIED (UI)** |
| 23 | 39/39 skill validation, 0 unknown commands — `PLAN-CONTINUATION.md:15,51`; `CAPABILITY-MATRIX.md:24` | Validator not executed | **UNVERIFIED** |

## 2. Non-numeric capability claims that need correction

| # | Claim and location | Problem | Proposed correction |
|---|---|---|---|
| 1 | "orchestrated by **DeerFlow 2.2** (DeepSeek V4.1-Flash)" — `README.md:5` | The pipeline is deterministic; DeerFlow has no registered access to Forge/pipeline tools (`README.md:212–213`; `research/.../README.md:43,48`). This reads as runtime orchestration. | Say: "asset pipeline is orchestrated by a deterministic Python state machine; DeerFlow 2.2 is the intended agent front door and is **not registered** with the tools in this checkout." |
| 2 | "`blueprint/files/` ... and **stub tests**" — `README.md:13` | The same repo documents 141 real `def test_` functions and contract doubles under `tests/stubs/` (`README.md:78–79`). "Stub tests" understates real tests. | "real test suite plus contract doubles in `tests/stubs/`." |
| 3 | "Current verified state" heading — `README.md:199–201` | The section mixes executed results with counts not reproducible without the documented staging environment; several are marked as verified without a date/command in that block. | Retitle to "Last reported state (2026-11-05; runner-qualified)" and attach the exact command/environment for each line. |
| 4 | "This file is the current capability answer" — `CAPABILITY-MATRIX.md:5` | Correct as intent, but individual rows are not provenance-tagged per row; several are UNVERIFIED in this pass. | Add a `last-run`/`probe` column per row; do not date the file alone. |

## 3. Required corrections to stale numbers (exact)

1. `docs/CAPABILITY-MATRIX.md:25` — replace "189-file desktop package includes 10 skills" with
   "189-file desktop package; `<package>/skills/` currently has 6 directories (exact skill names not
   enumerated in this audit)". Do not state 10 without a listing.
2. `docs/PLAN-CONTINUATION.md:11` — 53 pass/4 skip is **historical W1-A**; label it explicitly and
   keep one current runner figure (line 20's 139/4 or its replacement) as the only current number.
3. `README.md:30` and `README.md:203` — duplicate 65/65 claims: keep one, attach
   `npm test` command/environment and date; otherwise mark UNVERIFIED.
4. `README.md:13` — remove "stub tests" (tests are real; only contract doubles are stubs).
5. `README.md:5` — remove the implication that DeerFlow 2.2 currently orchestrates the pipeline.
6. `README.md:206` / `docs/CAPABILITY-MATRIX.md:26` — 139 pass/4 skip must name the environment
   (throwaway PostgreSQL 16 + G0 bundle) inline, not only in `.tool` prose.

## 4. UNVERIFIED items (probe required before any claim)

| Item | Missing probe |
|---|---|
| npm test 65/65, lint warnings, typecheck/build | `npm run test`, `npm run lint`, `npm run typecheck`, `npm run build` |
| Pipeline/Forge 139/4, gateway 33/33, SQL 18/18, repo 4/4, service 5/5, verifier 8/8, critic 14/14 | pytest with documented DSN/staging env |
| SQL 36 transitions/edges | `SELECT count(*) FROM forge_transition` on scratch DB, or grep the seed inserts with absolute path |
| Playwright 15/15, smoke 0/0/0 | `node scripts/visual-console-smoke.mjs ...` with a running build |
| MCP 33/26 tools + `command_batch` | Craft MCP `tools/list` + one batch on the installed apps |
| G0 9/9, hash, DPI, 22/22 hashes | re-run the G0 staging reproduction and hash the bundle |
| Download 4,456 bytes, clipboard `Copied` | manual/browser probe with permission state |
| 39/39 skill validation, 0 unknown commands | `validate_skills.py`, `check_skill_commands.py` |
| 5 tabs | enumerate routes/tabs in `src/routes` and the console UI |

## 5. HISTORICAL (must not be presented as current)

- `docs/PLAN-CONTINUATION.md:11` (W1-A 53/4) and `:20` (W2 close 97/9) — superseded by the same
  file's later "current 139/4".
- `README.md:215–218` already labels 207 JS tests / 31 pipeline tests / live VPS E2E / DeerFlow
  loading Forge tools / enabled units as historical. That correction is correct and should be kept.
- G0 evidence and any execution-wave counts remain dated staging evidence, not current production state.

## 6. Scope limits of this audit

- Read-only: no source/docs were edited; no test, browser, MCP or model run was executed; no VPS or
  production access was used.
- Counts are filesystem/grep counts at snapshot time; they can drift as the corpus grows (the Desktop
  package was rebuilt during earlier tasks).
- Claims about model behaviour, vision accuracy, retrieval lift, publish and VPS state were not probed
  and are outside this pass; they remain UNVERIFIED as the audited docs already state.
