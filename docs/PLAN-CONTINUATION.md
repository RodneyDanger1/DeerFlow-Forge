# Plan continuation — 2026-11-05

**Read first:** `research/eko-deerflow-agent/README.md`, `GOALS.md`, `ARCHITECTURE.md`,
`execution-wave/09-GOAL-GAP-PLAN.md`, `execution-wave/11-G0-EVIDENCE.md`, `docs/TRACE/03-fixes.md`.

## Status

| Step | Status |
|---|---|
| W0 docs integrity | done |
| W1-A launcher/argv/preflight/mutation/gate truth | done on staging; **historical** W1-A gate: 53 pass/4 skip |
| W1-B Craft MCP direct proof | done: 33/26 tools + PhotoCraft `command_batch` |
| W1-B DeerFlow registration | not applied |
| G0 real trace/retouch | passed on staging; Lead-run |
| W1-C skill guidance | **DONE** — 39/39, both runtimes; guidance only |
| Independent W1-C/console review | **PASS** (`13-INDEPENDENT-REVIEW`) |
| Independent G0 artifact review | **PASS (artifact consistency)**; execution provenance **U** (`14-G0-ARTIFACT-REVIEW`) |
| G0 artifact bundle | copied to `execution-wave/g0/` + 22-entry MANIFEST; D2 vacuous retype gate fixed; report regenerated as 9/9 applicable |
| G0 provenance | **CLOSED independently** (`16-G0-PROVENANCE.md`): fresh staging-only run reproduced artifacts byte-identically |
| W2 Forge service/DDL/queue | **W2 local gate PASS**; current full suite **165 pass/4 skip**; 18/18 SQL; real HTTP→repo→worker→reaper e2e. No production deploy |
| W2b worker CLI + guarded finish | **DONE**: `python -m forge_worker --once`; 12 CLI + 6 worker tests; explicit SQL skip without DSN |
| Wave-2 runtime defects D1/D2/D6/D7 | **DONE**: cancellable timeout→504, replay→200, `E_REPO_SHAPE`, strict POST validation; staging green |
| UI/agent bug audit | **DONE for tested surfaces**: copy fallback, health 503, verifier malformed check, reaper abandoned; **18/18** control + **8/8** a11y browser checks; 165 pass/4 skip |
| W3-A verifier | **DONE**: 8/8 tests; real G0 pair passes; PNG + both-DPI checks; staging 165 pass/4 skip |
| W3 transition-event ownership | **CLOSED**: `SELECT * FROM` composite fix; exactly one `episode.transition` event asserted on real PostgreSQL |
| W3-B critic | **DONE (contract)**: 14/14 blind-critic tests; gate authoritative; invalid human/gate refuse; no model claim |
| W4-A eval/promotion | **DONE (contract)**: 13/13 tests; duplicate goldens refuse; 3/3 refused, 8/8 candidate only with human; no activation/learning claim |
| W4-B learning loop | not started |

## Decision

G0 is closed: artifact consistency PASS and independent provenance PASS. W2 is closed **locally**
(gateway, DDL, repository, worker, loopback service; no production DB or deploy), with the wave-2
runtime/worker fixes verified on staging. W3-A verifier, W3-B critic contract and W3 transition-event ownership are local and tested.
The rebuilt console passes the real browser control and a11y gates
(`docs/TRACE/2026-11-05/GATE-FINAL-W2.md`). Production cutover, a supervised service, DeerFlow MCP
registration, W1 idempotency persistence, W5 eval persistence and any learning claim remain blocked/unverified.

**Current next step is the W1 API decision below**, then W5 eval persistence. Do not claim W1/W5 closed
until each lands with a real-DB test. W3 is closed by the event-count test. Full staging is
**165 passed, 4 skipped**; local Forge-only is **111 passed, 9 skipped**.

Historical note: earlier text in this file instructed “do not start W2” until provenance was
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

---

## Wiring gaps — current position (2026-11-05, wave 2 closeout)

Source: `docs/TRACE/2026-11-05/PLAN-WIRING-AUDIT.md` and `GATE-FINAL-W2.md`.

Closed in this wave:

- **W2 worker entry point:** `python -m forge_worker --once` (`--lease-s`, `--worker-id`, `--dsn`,
  `--handler module:async_callable`), bounded one-line JSON errors, exit 0/1/2.
- **W2b guarded finish (D3):** `FinishRefused` for `E_JOB_STATE`/`E_PARAM_REJECTED`/`E_TIMEOUT`;
  other driver errors become `E_REPO`; no swallowed finish.
- **W3 transition-event ownership:** `forge_repo.transition()` and `append_event()` used
  `SELECT fn(...)`, returning a single composite column that `_row()` correctly refused. Changed to
  `SELECT * FROM fn(...)`. A real-PostgreSQL test now asserts exactly one `episode.transition` event
  with `from=intake`, `to=briefed`. **W3 CLOSED.**
- **W6 SQL invariants:** `tests/test_forge_sql.py` collects the existing assertion + SKIP LOCKED
  scripts and skips explicitly without `FORGE_TEST_DSN`; `pytest.ini` registers `sql_integration`.

Next step — **W1 tool-call idempotency persistence is blocked by a contract mismatch, not by time**:

- `forge_gateway.py:241-243`: `Repo.find(key) -> ToolResult | None` / `store(key, result)` is
  synchronous and carries no episode/tool/params context.
- `schema_forge.sql:324-351`: `forge_tool_call` requires `episode_id`, `tool_id`, `params`, and a
  constraint-valid `sha256:...` key; `forge_replay_tool_call(p_key)` already exists.
- A sync adapter cannot safely use the async `asyncpg` pool.

Decision (implement one, with a real-DB duplicate-call test):

1. **Preferred:** extend `ToolResult` with `episode_id`, `tool_id`, `params`; make `Gateway.execute`
   and `Repo` async; add `ForgeGatewayRepo` over `asyncpg`; keep `InMemoryRepo` as a classified test
   double. This changes the gateway API and every caller/test in one deliberate commit.
2. Alternative: keep the sync gateway and add an async `execute_async` wrapper that owns persistence;
   rejected unless a caller proves it needs sync execution, because it duplicates the execution path.

Remaining, in order:

1. **W1** as decided above.
2. **W5 eval persistence** — `forge_eval.py` is a pure decision function; no `forge_eval` row writer.
3. **W7 clean-env deps** — `asyncpg` and `Pillow` are present; validate a clean install in CI.
4. **W8 service auth** — owned by the existing security plan; service is loopback-only today.

Do not claim W1/W5 closed until their owning task lands with a real-DB test. Do not claim full Craft
execution, production service, DeerFlow registration, publish, vision-critic accuracy, or learning
above L0.
