# PLAN-FIXES-W2 — task-33 (Wave 2 plan/wiring fixes)

**Status: PARTIAL — hard stop before any edit.** 2026-11-05 · Seat: harness-architect.
Task claimed (task-33, rev 2, owner harness-architect). **No source, test or doc file was changed;
no tests were run.** This receipt records exact remaining work so the next seat can start immediately.

## Why PARTIAL

The Lead issued a 2-minute hard stop before recon finished. The first required step —
`forgewright-logic-gatekeeper` Phase-1 gate (architecture, data flow, root cause, one edge case)
— could not be loaded: the skill name `forgewright-logic-gatekeeper` is **not resolvable** in this
session (`skill` tool: "unknown or no longer available"). Per the ForgeWright contract, mutation
without the gate is not permitted, and no edit was started rather than landing a guessed one.

## Scope that was claimed (unchanged)

| File | Planned change | Current state |
|---|---|---|
| `blueprint/files/forge_worker.py` | guarded `finish_job` (D3) + `python -m forge_worker --once` CLI with bounded, named errors | **unmodified** |
| `blueprint/files/tests/test_forge_worker_cli.py` | new CLI tests (success, empty queue, guarded-finish refusal, named error, exit code) | **not created** |
| `blueprint/files/tests/test_forge_sql.py` | pytest wrapper invoking existing `forge_schema_assertions.py` / `forge_schema_skiplock.py`; `pytest.skip("FORGE_TEST_DSN unset")` otherwise | **not created** |
| `blueprint/files/pytest.ini` | marker registration for the SQL integration tests | **unmodified** |
| `docs/PLAN-CONTINUATION.md` | W1 gaps + decision-complete next step | **unmodified** |
| `docs/TRACE/2026-11-05/PLAN-FIXES-W2.md` | this receipt | written |

## Evidence already established (from the task-26 audit, symbol-level)

- `forge_worker.py:46-74` — `ForgeWorker`, `run_once`, `drain`; **no `__main__`, no argparse**
  (contrast `forge_verifier.py:109,136`). This is the reason the CLI is required.
- `forge_worker.py:65` — `drain(max_jobs)` exists; finish path is `repo.finish_job` (`:18` protocol)
  with no local guard, so a non-claimable job's `E_JOB_STATE` would surface as a raw exception.
- `tests/forge_schema_assertions.py:17` and `tests/forge_schema_skiplock.py:12` — standalone
  `asyncio` scripts requiring `FORGE_TEST_DSN`; names are not `test_*.py`, so `pytest.ini:1-2`
  (`testpaths = tests`) never collects them.
- `pytest.ini:1-6` — `testpaths = tests`, `pythonpath = .`, `asyncio_mode = auto`; no markers block.

## Decision-complete next step (execute in this order)

1. **Read first** `forge_worker.py` (all 90 lines), `tests/test_forge_worker.py`,
   `tests/forge_schema_assertions.py`, `tests/forge_schema_skiplock.py`, `pytest.ini`.
2. **Guarded finish (D3):** add a worker-local `FinishRefused(Exception)` carrying
   `code in {E_JOB_STATE, E_PARAM_REJECTED, E_TIMEOUT}`; wrap the `repo.finish_job` call in
   `run_once`/`drain`; map DB `E_JOB_STATE` to `FinishRefused`; never swallow. Test: finishing an
   already-finished job raises the bounded error and leaves the row unchanged.
3. **CLI:** add `argparse` with `--once` (default) and `--lease-s`; `if __name__ == "__main__"` →
   `asyncio.run(main())`; errors print one-line JSON `{"ok":false,"code":"E_..."}` to stderr and exit
   non-zero; success prints `{"ok":true,"claimed":N,"finished":M}` and exits 0. Test both paths plus
   empty queue (`{"ok":true,"claimed":0}`).
4. **SQL tests:** `tests/test_forge_sql.py` reads `FORGE_TEST_DSN`;
   `pytest.skip("FORGE_TEST_DSN unset")` at module level when absent; otherwise runs the two
   existing scripts via `subprocess.run([sys.executable, script], env=..., check=True)` and asserts
   exit 0. No assertion duplication.
5. **pytest.ini:** add `markers = sql_integration: needs FORGE_TEST_DSN` (and nothing else).
6. **Docs:** append a dated W1-gap next-step block to `PLAN-CONTINUATION.md` pointing at steps 2–5
   and the task-33 receipt.
7. **Verify:** `cd blueprint/files && python -m pytest tests -q` (expect existing suite unaffected);
   `python -m forge_worker --once` against a scratch DSN; with no DSN, `test_forge_sql.py` must SKIP,
   not fail.

## Rollback

Every change is additive (new file, new function, marker line, docs paragraph). Inverse:
delete `test_forge_sql.py` / `test_forge_worker_cli.py`, revert the two small edits and the docs block
(`git checkout -- blueprint/files/forge_worker.py blueprint/files/pytest.ini docs/PLAN-CONTINUATION.md`).

## Blockers / coordination

- `forgewright-logic-gatekeeper` skill unavailable in this session — gate must be obtained before edits
  (or explicitly waived by the Lead in writing).
- Claim returned `writeScopeWarnings: overlap with task-28`; `forge_worker.py` must be single-owner.
  Confirm task-28 is not editing it before starting.

## Explicit UNVERIFIED

- Function bodies and test bodies (not read at stop time).
- Whether a scratch `FORGE_TEST_DSN` is available in this environment.
- Exact D3 wording from the originating decision register (file not located at stop time).

*No code was tested, so no test result is claimed. Zero changed files besides this receipt.*
