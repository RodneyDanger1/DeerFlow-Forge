# Plan continuation — 2026-11-05

**Read first:** `research/eko-deerflow-agent/README.md`, `GOALS.md`, `ARCHITECTURE.md`,
`execution-wave/09-GOAL-GAP-PLAN.md`, `execution-wave/11-G0-EVIDENCE.md`, `docs/TRACE/03-fixes.md`.

## Status

| Step | Status |
|---|---|
| W0 docs integrity | done |
| W1-A launcher/argv/preflight/mutation/gate truth | done on staging; 53 pass/4 skip |
| W1-B Craft MCP direct proof | done: 33/26 tools + PhotoCraft `command_batch` |
| W1-B DeerFlow registration | not applied |
| G0 real trace/retouch | passed on staging; Lead-run |
| W1-C skill guidance | **DONE** — 39/39, both runtimes; guidance only |
| Independent W1-C/console review | **PASS** (`13-INDEPENDENT-REVIEW`) |
| Independent G0 artifact review | **PASS (artifact consistency)**; execution provenance **U** (`14-G0-ARTIFACT-REVIEW`) |
| G0 artifact bundle | copied to `execution-wave/g0/` + 22-entry MANIFEST; D2 vacuous retype gate fixed; report regenerated as 9/9 applicable |
| G0 provenance | **CLOSED independently** (`16-G0-PROVENANCE.md`): fresh staging-only run reproduced artifacts byte-identically |
| W2 Forge service/DDL/queue | **W2 local gate PASS** (at close: 97 pass/9 skip); current full suite **139 pass/4 skip**; 18/18 SQL; 9 ms SKIP LOCKED; real HTTP→repo→worker→reaper e2e. No production deploy |
| UI/agent bug audit | **DONE for tested surfaces**: copy fallback, health 503, verifier malformed check, reaper abandoned; UI 15/15 checks, 139 pass/4 skip |
| W3-A verifier | **DONE**: 8/8 tests; real G0 pair passes; tamper/vacuous/failed/malformed checks refuse; staging 139 pass/4 skip |
| W3-B critic | **DONE (contract)**: 14/14 blind-critic tests; gate authoritative; disagreement → needs_human; no model claim |
| W4-A eval/promotion | **DONE (contract)**: 13/13 tests; 3/3 refused, 8/8 candidate only with human, regressions refuse; no activation/learning claim |
| W4-B learning loop | not started |

## Decision

G0 is closed: artifact consistency PASS and independent provenance PASS. W2 is closed **locally**
(gateway, DDL, repository, worker, loopback service; no production DB or deploy). W3-A verifier and
W3-B critic contract are local and tested. Production cutover, a supervised service, DeerFlow MCP
registration and any learning claim remain blocked/unverified.

Historical note: earlier text in this file instructed “do not start W2” until provenance was
independently closed. That condition was satisfied by `16-G0-PROVENANCE.md`; the instruction is
superseded and retained only in history.

## Historical W1-C scope (completed; kept for audit)

**Goal:** patch only skills whose guidance still contradicts Phase 0 or omits a safety boundary.

**Files:**
- `blueprint/files/skills/forge-harness-architect/SKILL.md` — promotion rule is stale (3/3).
- `blueprint/files/skills/craft-mcp-drive/SKILL.md` — await dependent MCP calls; interleaving.
- `blueprint/files/skills/apparel-print-master/SKILL.md` — bind approval to artifact SHA-256.
- `blueprint/files/skills/craft-agent-operator/SKILL.md` — already has evidence/preflight; no rewrite.
- `blueprint/files/skills/harness-code-adapter/SKILL.md` — already has donor provenance; no rewrite.

**Not goal:** runtime code, new skills, renaming installed skills, claiming behavior is enforced.

**Verify:** `validate_skills.py` → 39/39; `check_skill_commands.py` → 0 unknown; install both runtimes;
then run a fresh verifier on local tests and G0 evidence (VPS access is a known verifier limitation).

---

## W1 gaps — decision-complete next step (2026-11-05, task-33)

Source: `docs/TRACE/2026-11-05/PLAN-WIRING-AUDIT.md` §3 (W1–W8) and
`docs/TRACE/2026-11-05/PLAN-FIXES-W2.md`. This wave closes W2/W6; it does **not** fix W1/W3/W5.

Closed in this wave:
- **W2 worker entry point:** `blueprint/files/forge_worker.py` now has `python -m forge_worker --once`
  (`--lease-s`, `--worker-id`, `--dsn`, `--handler module:async_callable`) with bounded one-line JSON
  errors and exit codes 0 (ok) / 1 (runtime `E_*`) / 2 (config `E_*`).
- **W2b guarded finish (D3):** `ForgeWorker._finish` raises `FinishRefused` for
  `E_JOB_STATE`/`E_PARAM_REJECTED`/`E_TIMEOUT`; other driver errors become `E_REPO`. No swallowed finish.
- **W6 SQL invariants:** `tests/test_forge_sql.py` makes the existing
  `forge_schema_assertions.py` + `forge_schema_skiplock.py` collectable; it **skips explicitly** when
  `FORGE_TEST_DSN` is unset (`pytest.ini` marker `sql_integration`). A green run never silently claims them.

Next step (owners, in order):
1. **W1 idempotency persistence** — `forge_repo.py` has no `find`/`store` for `forge_tool_call`; add a
   `PgRepo` adapter + real-DB duplicate-call test. Owner: repo task, not worker.
2. **W3 double-append** — read `forge_repo.py:63-79`; make exactly one owner of `episode.transition`
   event append; add an event-count assertion.
3. **W5 eval persistence** — `forge_eval.py` is a pure decision function; no eval row is written.
4. **W7 clean-env deps** — confirm `asyncpg`/`Pillow` in `requirements.txt`.
5. **W8 service auth** — owned by the `05-SECURITY` plan.

Do not claim W1/W3/W5 closed until the owning task lands with a test; worker tests prove only W2/W2b.
