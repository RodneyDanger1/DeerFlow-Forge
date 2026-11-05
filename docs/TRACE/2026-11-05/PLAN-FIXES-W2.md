# PLAN-FIXES-W2 — task-33 receipt (Wave 2 worker CLI + SQL test wiring)

**Status: COMPLETE (local, no deploy).** 2026-11-05 · Seat: harness-architect · Gate: Lead-written
Phase-1 waiver for the unavailable `logic-gatekeeper` skill (architecture / dataFlow / edgeCases /
rootCause supplied by the Lead in-session). Supersedes the earlier PARTIAL receipt for the same task.

## Changed files (6; no service/repo/verifier/critic/eval touched)

| File | Change |
|---|---|
| `blueprint/files/forge_worker.py` | guarded finish (D3) + `python -m forge_worker --once` CLI, bounded named errors, exit codes (72 → 275 lines) |
| `blueprint/files/tests/test_forge_worker_cli.py` | **new** — 12 tests: guarded finish, bounded repo errors, handler failure recorded, empty queue, CLI config/runtime exits |
| `blueprint/files/tests/test_forge_sql.py` | **new** — collects the 18-assertion script + SKIP LOCKED script; explicit skip when `FORGE_TEST_DSN` unset |
| `blueprint/files/pytest.ini` | registered `sql_integration` marker (+2 lines) |
| `docs/PLAN-CONTINUATION.md` | appended "W1 gaps — decision-complete next step" (W2/W2b/W6 closed; owners for W1/W3/W5) |
| `docs/TRACE/2026-11-05/PLAN-FIXES-W2.md` | this receipt |

## Behaviour added (D3 + CLI)

- `WorkerError(code, message)` / `FinishRefused(code, message)`; codes:
  `E_INVALID_ARG`, `E_DSN_MISSING`, `E_HANDLER_MISSING`, `E_HANDLER_INVALID`, `E_JOB_STATE`,
  `E_PARAM_REJECTED`, `E_TIMEOUT`, `E_REPO`, `E_WORKER`.
- `ForgeWorker._finish()` wraps `repo.finish_job`: `E_JOB_STATE`/`E_PARAM_REJECTED`/`E_TIMEOUT` →
  `FinishRefused`; other driver errors → `E_REPO`; nothing swallowed; no traceback is the contract.
- CLI: `--once` (required), `--lease-s` (1..86400, validated before any I/O), `--worker-id`, `--dsn`,
  `--handler module:async_callable`. DSN order: `--dsn` → `FORGE_DSN` → `FORGE_TEST_DSN` → `DATABASE_URL`.
  `forge_repo` is imported lazily, so CLI tests need no asyncpg. Output: one JSON object;
  exit `0` ok, `1` runtime `E_*`, `2` config `E_*`. Repo `close()` always awaited.

## Tests run (local, Python 3.14.7; pytest is not installed here)

| Command | Observed |
|---|---|
| `python -m py_compile forge_worker.py tests/test_forge_worker_cli.py tests/test_forge_sql.py` | exit 0 |
| `python -m unittest tests.test_forge_worker_cli -v` | **Ran 12 tests — OK** |
| `python -m unittest tests.test_forge_sql -v` | **Ran 2 tests — OK (skipped=2)**; reason: "FORGE_TEST_DSN unset: SQL invariants not run (explicit skip, not a pass)" |
| `python -m unittest tests.test_forge_worker` (existing) | **Ran 6 tests — OK** (no regression) |
| `python -m forge_worker` | `{"ok":false,"code":"E_INVALID_ARG","message":"only --once is supported; no daemon mode"}` exit 2 |
| `python -m forge_worker --once` with no DSN | `{"ok":false,"code":"E_DSN_MISSING",...}` exit 2 |
| `python -m forge_worker --once --lease-s 0` | `{"ok":false,"code":"E_INVALID_ARG","message":"--lease-s out of range 1..86400: 0"}` exit 2 |

`pytest` is **not installed** in this local Python (`No module named pytest`), so the new files were
executed with `unittest`; they are pytest-compatible (`IsolatedAsyncioTestCase` + `skipUnless`, and
`pytest.ini` already sets `asyncio_mode = auto`). **The pytest run itself is UNVERIFIED here.**

## Rollback

Delete the two new test files; revert the three edited files
(`git checkout -- blueprint/files/forge_worker.py blueprint/files/pytest.ini docs/PLAN-CONTINUATION.md`).
No schema, no migration, no data, no service.

## Not done / out of scope (unchanged, do not read as fixed)

- W1 idempotency persistence (`forge_repo.py` `find`/`store`) — repo owner.
- W3 potential double-append (`forge_repo.py:63,79`) — repo owner; body not read.
- W5 eval persistence; W7 clean-env deps; W8 service auth — their owners.
- Live DB run of the 18 SQL assertions / SKIP LOCKED — requires `FORGE_TEST_DSN`; skipped explicitly.
- No production DB, deploy, commit, or DeerFlow registration touched.

## UNVERIFIED

1. `pytest` execution of the new/changed files (module absent locally; the `unittest` equivalents passed).
2. SQL integration outcomes (skipped without `FORGE_TEST_DSN`).
3. `python -m forge_worker --once` against a real `ForgeRepo` (CLI tested with an injected repo factory).
4. `asyncpg` import path on the deployment host (lazy import exercised only via injection).
