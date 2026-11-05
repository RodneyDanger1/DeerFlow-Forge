# 13 — Independent Review of W1-C and G0

**Task:** `task-17` · **Reviewer:** `wave2-verifier` (independent seat; did not write W1-C, G0 or TRACE fixes)
**Date:** 2026-11-05 · **Repo:** `C:\Users\Riley\Desktop\DeerFlow Forge` · **Write scope:** this file + `.json` only.
**Constraints honoured:** no source/test edit, no test weakening, no production change; tree left clean (`git status`
empty after removing only the screenshots my smoke run regenerated).

**Status vocabulary:** `PASS` (reproduced by this seat), `FAIL`, `U` (not independently reproducible — no access
or artifact), `READ` (source inspected, not executed). The reviewer's SSH to the VPS is known-denied; every
VPS/staging claim below is `U`, not assumed true.

---

## 1. Commands run and observed output

| # | Command (cwd repo root unless stated) | Observed output | Exit | Status |
|---|---|---|---|---|
| C1 | `python validate_skills.py` (`blueprint/files/skills/_meta`) | `39 skills checked \| 39 passed \| 0 failed`; `Runtime: DSH current=39 missing=0 differs=0 \| Hermes current=39 missing=0 differs=0` | 0 | **PASS** |
| C2 | `python check_skill_commands.py` | `62 files scanned (39 SKILL.md + 23 references); 0 with unknown command ids` | 0 | **PASS** |
| C3 | `python check_atlas.py` (`…/artcraft-command-atlas/references`) | `atlas check OK: VC 918 ids / 64 groups; PC 965 ids / 38 groups`; intent map VC 127, PC 96 | 0 | **PASS** |
| C4 | `npm.cmd run typecheck` | `tsc --noEmit`, no output | 0 | **PASS** |
| C5 | `npm.cmd test` | `tests 65  suites 18  pass 65  fail 0  cancelled 0  skipped 0  todo 0`, `duration_ms 1845.98` | 0 | **PASS** |
| C6 | `npm.cmd run lint` | `✖ 5 problems (0 errors, 5 warnings)` — all in `research/eko-deerflow-agent/execution-wave/adapter/src/*.mjs` | 0 | **PASS** |
| C7 | `node --test scripts/blueprint-parity.test.mjs` | `tests 3  pass 3  fail 0` | 0 | **PASS** |
| C8 | `node --experimental-strip-types --test src/lib/blueprint/model.test.ts` | `tests 6  pass 6  fail 0` | 0 | **PASS** |
| C9 | `node .output/server/index.mjs` (PORT=8092) then `node scripts/visual-console-smoke.mjs http://127.0.0.1:8092` | server `Listening on: http://127.0.0.1:8092/`; smoke `"ok": true`, `"failures": []`; desktop + mobile status 200, all five tabs with content, `consoleErrors: []`, `pageErrors: []`, `failedRequests: []`, mobile `overflowPx: 0` | 0 | **PASS** |
| C10 | `git status --porcelain` (before and after) | start: empty; after smoke: 5 tracked `screenshots/console-*-mobile.png` modified; restored with `git restore -- screenshots`; final: empty | — | **PASS (tree restored)** |
| C11 | `git show --stat 7314c2a` (W1-C) | only `blueprint/files/skills/**` (`_meta`, three patched SKILL.md), `docs/PLAN-CONTINUATION.md`, `execution-wave/12-W1C-EVIDENCE.md` | — | **PASS (scope)** |
| C12 | JSON parse + server list of `blueprint/files/deploy/deerflow-craft-extensions.example.json` | `JSON_OK`; `servers ['vectorcraft', 'photocraft']` | 0 | **PASS** |

---

## 2. W1-C — claim → status

| # | Claim (`12-W1C-EVIDENCE.md`) | Independent check | Status |
|---|---|---|---|
| W1 | `forge-harness-architect/SKILL.md` D7 corrected: pre-declared horizon, LB above baseline, 3/3 LB 0.4385 does not pass, simulation is input not policy | Read file line 48: exact wording present | **PASS (READ)** |
| W2 | `craft-mcp-drive/SKILL.md` has explicit await rule (read response by `id`; PhotoCraft can interleave; timeout ≠ replay) | Read lines 116–120: exact rule present | **PASS (READ)** |
| W3 | `apparel-print-master/SKILL.md` binds approval to bytes (SHA-256 + canvas/DPI/template/area/width + gate-report hash; stale/void on re-export) | Read lines 109–116: exact rule present | **PASS (READ)** |
| W4 | `39 skills checked \| 39 passed` | C1 | **PASS** |
| W5 | `check_skill_commands … 0 unknown` | C2 | **PASS** |
| W6 | `Runtime after install: DSH 39/0/0, Hermes 39/0/0` | C1 | **PASS** |
| W7 | `Runtime before install: DSH current=36 differs=3 \| Hermes current=36 differs=3` | Historical state; no captured command log in the evidence file, state is now 39/0/0 and cannot be rewound | **U** |
| W8 | `install_skills --targets both --force: installed` | Not re-run by this seat (would reinstall); current parity verified instead | **U (action) / PASS (state)** |
| W9 | Guidance only, not runtime enforcement; no production/pipeline file touched | C11: commit touches only skills/meta/docs | **PASS (scope)** |

No W1-C claim **failed**. The three patches are real and the runtime parity they assert is true now.

---

## 3. G0 — claim → status

| # | Claim (`11-G0-EVIDENCE.md`) | Independent check | Status |
|---|---|---|---|
| G1 | VectorCraft `--version` 0.21.1; PhotoCraft `0.20.2 (7c12f6471, 2026-11-05)` | VPS binaries; not present on this workstation; SSH denied | **U** |
| G2 | Direct trace exit 0; SVG 958,860 B; PDF 1,618,404 B | VPS artifact; absent locally | **U** |
| G3 | CraftTrace exit 0, `ok:true`, `saved:true`, 10/10 checks | VPS run; no local report/artifact | **U** |
| G4 | PhotoCraft retouch exit 0; PNG 1438×148, DPI 299.9994 | VPS run; absent locally | **U** |
| G5 | Staging `pytest tests -q` → 53 passed, 4 skipped | VPS staging tree; not reproducible here | **U** |
| G6 | `bash -n deploy/setup-pipeline.sh` → 0 | Could be checked only on a POSIX shell; not run here | **U** |
| G7 | MCP VC 33 tools / PC 26 tools; `command_batch` completed:1 failed:0 | VPS MCP servers; no local log | **U** |
| G8 | Five artifact SHA-256 values (`trace_master.png/svg`, `trace_report.json`, `direct_trace.svg`, `retouch_master.png`) | Artifacts not in the repo (`ABSENT` search for all five + both input PNGs); no way to fetch from VPS | **U** |
| G9 | "Production change: none" (VPS prod not modified) | Cannot inspect VPS; local repo changes are source-only and were not deployed by this seat | **U (VPS) / PASS (local tree)** |
| G10 | Staging extensions example exists at `blueprint/files/deploy/deerflow-craft-extensions.example.json` | C12: valid JSON, `vectorcraft` + `photocraft` servers | **PASS (local)** |
| G11 | Phase-0 launchers exist and target absolute `/opt/craft/...` paths | Read `craft-launchers/vectorcraft-cli`, `photocraft-cli`: correct absolute paths + named `E_TOOL_NOT_INSTALLED` refusal | **PASS (local READ)** |
| G12 | Headline "PASS for direct CLI execution; PARTIAL for DeerFlow MCP registration" | The file itself qualifies §4: registration **not applied**; direct tools/list only. Self-consistent; the word "PASS" applies only to direct CLI, which this seat cannot re-run | **U w/ self-qualified scope** |

**G0 cannot be independently reproduced from this seat.** It is neither confirmed nor refuted: the VPS/staging
artifacts are unreachable (SSH denied, artifacts absent from the workspace). Local corroboration is limited to
the launchers and the extensions example, which are consistent with the documented plan but do not prove execution.

---

## 4. `docs/TRACE/03-fixes.md` — claim → status

| # | Claim | Independent check | Status |
|---|---|---|---|
| T1 | `npm run typecheck` → exit 0 | C4 | **PASS** |
| T2 | `npm test` → 65 passed, 0 failed | C5: `tests 65 pass 65 fail 0` | **PASS** |
| T3 | `npm run lint` → 0 errors, 5 pre-existing warnings in research adapter files | C6: exactly 0 errors, 5 warnings, all in `execution-wave/adapter/src/*.mjs` | **PASS** |
| T4 | `model.test.ts` → 6/6 | C8 | **PASS** |
| T5 | `blueprint-parity.test.mjs` → 3/3 | C7 | **PASS** |
| T6 | `package.json` includes `model.test.ts` in `npm test` | Read `package.json:19`: present | **PASS (READ)** |
| T7 | `copy-button.tsx` shows explicit `Copied`/`Copy failed` | Read `:6,13,18,25`: state machine present | **PASS (READ)** |
| T8 | `sources.ts` adds two launchers + MCP example | Read `:29-31,81-83`: present | **PASS (READ)** |
| T9 | `playbook-view.tsx` measured run example + 39 skills | Read `:243-245` (`--cmd imageTrace.make … --cmd imageTrace.expand`), `:273` ("agent skills (39, DSH + Hermes)") | **PASS (READ)** |
| T10 | `routes.py` distress step input `{work}/trimmed.png` | Read `routes.py`: `Step("effectcraft_distress" … ("effectcraft-cli","--input","{work}/trimmed.png" …)` | **PASS (READ)** |
| T11 | Built server + `visual-console-smoke` → `ok:true`, five tabs, no errors, desktop+mobile | C9: `ok:true`, `failures:[]`, all five tabs, zero console/page/request errors, mobile overflow 0 | **PASS** |
| T12 | `npm run build` → built; `.output` rebuilt with `NITRO_PRESET=node-server` | Build **not re-run** by this seat; the existing `.output` (server/index.mjs, 12:37) served the smoke OK, but its preset/provenance was not re-derived | **U (build not reproduced; served artifact works)** |
| T13 | Copy success (`Copied`) and denied-clipboard (`Copy failed`) browser probes | Source state machine verified; the two permission probes were not re-run | **U (probe) / READ (code)** |
| T14 | Staging `pytest tests -q` → 53 passed, 4 skipped | VPS staging; not reproducible here | **U** |

---

## 5. Contradictions / discrepancies (reported, not fixed)

| # | Finding | Evidence | Severity |
|---|---|---|---|
| D1 | **Board scope gap**: task-17 `writeScopes` lists only `execution-wave/13-INDEPENDENT-REVIEW.md`, while the task text requires `.md` **and** `.json`. The `.json` is outside the recorded advisory scope. | `team_task_list` task-17 vs Lead instruction | Low |
| D2 | **Uncaptured "before" state**: `12-W1C-EVIDENCE.md` asserts `DSH current=36 differs=3` before install, but presents no command log for that state; it cannot be re-observed now (state is 39/0/0). An evidence file should not contain an unquotable historical measurement. | `12-W1C-EVIDENCE.md:20` vs C1 | Low |
| D3 | **"PASS" headline vs PARTIAL content**: `11-G0-EVIDENCE.md` title/§5 say **PASS** for direct CLI execution while §4 says DeerFlow registration was **not applied**. The file is internally qualified, but the one-line status can be over-read as "G0 fully passed". | `11-G0-EVIDENCE.md:3,48-50,59-61` | Low (readability) |
| D4 | **Build claim not reproducible as written**: `03-fixes.md:19-22` claims a specific rebuild (`NITRO_PRESET=node-server npm run build`) and start of `.output/server/index.mjs`; the build was not re-run, and `npm run build` also chains `db:migrate` (needs `DATABASE_URL`). Only the served `.output` was verified. | `package.json:11`, `03-fixes.md:19-22`, C9 | Low |
| D5 | **Verification dirties tracked artifacts**: the official `visual-console-smoke.mjs` overwrote 5 tracked `screenshots/console-*-mobile.png`. A verifier running the sanctioned smoke changes the tree; no instruction says to restore. This review restored them (`git restore -- screenshots`) to leave the tree clean. | C10 | Low (operational) |
| D6 | **G0 hashes are unverifiable as evidence**: five SHA-256 values are listed with no artifact names crossing into the repo, no fetch command, and no path; the artifacts are absent from the workspace. They are well-formed but uncheckable from a non-VPS seat. | `11-G0-EVIDENCE.md:22-30`; local search `ABSENT` | Medium (for G0's claim class) |
| D7 | **Commit labels vs content**: commit `3c52bf3` ("W1: record G0 staging evidence") contains only docs/PDF metadata, while the actual Phase-0 code changes (launchers, routes argv, tool tests) are in `5a926ce`. Not a contradiction, but the commit that carries the G0 claim does not contain the code it claims G0 tested. | C11-style `git show --stat` | Low (provenance) |
| D8 | **04 description vs live runtime in W1-C**: the file says the install used `--force`; a current run without `--force` still reports `differs=0`, so the forced install outcome is consistent but the action itself is not reproduced. | `12-W1C-EVIDENCE.md:22-23` vs C1 | Very low |

No contradiction was found in the **app-side** results: typecheck, unit/integration test count, lint counts,
the two focused test suites, and the browser smoke all reproduce exactly as `03-fixes.md` states.

---

## 6. What could not be reproduced (residual `U`)

1. **All G0 execution evidence** — VPS/staging unreachable from this seat (SSH known-denied) and none of the
   five artifacts or inputs exist in the workspace. G0 is neither confirmed nor refuted independently.
2. **G0 "production change: none"** — the live `/opt/pod-pipeline`, `pod` DB and DeerFlow config were not
   inspected; only the local git tree is clean.
3. **Staging `pytest` 53/4** — VPS-only.
4. **MCP tool counts 33/26 and `command_batch` result** — VPS-only.
5. **`npm run build` / `NITRO_PRESET=node-server` rebuild** — not re-run; the existing `.output` served the
   smoke cleanly, which proves the served artifact works, not the build command.
6. **Clipboard granted/denied probes** — source code verified; the two browser permission probes were not
   re-run.
7. **W1-C historical "before install" counts (36/3)** — no captured log; current state is 39/0/0.

---

## 7. Verdict

| Area | Verdict | Basis |
|---|---|---|
| **W1-C skill patches** | **PASS** | three patches present and correct; 39/39 valid; command ids clean; DSH+Hermes parity 39/0/0 |
| **Console / TRACE fixes** | **PASS** | typecheck 0; `npm test` 65/65; lint 0 errors/5 warnings; model 6/6; parity 3/3; browser smoke `ok:true` on desktop+mobile with zero errors |
| **G0 real CLI/staging evidence** | **U** | VPS/staging unreachable; artifacts absent locally; cannot independently reproduce or refute |
| **Repo hygiene** | **PASS** | git tree clean before and after (smoke-regenerated screenshots restored); no source/test edits by this seat |

W1-C and the console fixes are independently reproduced. G0 remains `U` from this seat — the evidence is
self-consistent and locally corroborated only by the launchers and the extensions example, but the real-binary
runs, staging test counts, MCP tool counts and artifact hashes require the VPS the reviewer cannot reach.
