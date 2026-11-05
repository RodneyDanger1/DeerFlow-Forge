# RUNTIME FIXES — Wave 2 (task-28) — **PARTIAL / HARD STOP**

**Status: PARTIAL.** Hard stop arrived before any mutation. **No production file was edited.** Only this
receipt was written. Task `task-28` remains **in_progress** (not completed).
**Date:** 2026-11-05. **Mode:** Wave 2 fixes were authorised; stop instruction arrived at the gate stage.
**Changed files:** none (this file only). `git status` therefore shows no modification to `forge_service.py`,
`forge_repo.py`, `forge_worker.py`, or any test.

---

## 1. What was completed before the stop

| Step | Result |
|---|---|
| Baseline procedures | `/forgewright-lead`, `/forgewright-plan`, `/forgewright-recon`, `/forge` loaded; specialty `/integration-logic`, `/logic-debugger` loaded |
| `logic-gatekeeper` | Loaded. Phase 1 drafted (§2) but not yet applied — no mutating tool was used, so the gate was never crossed |
| Recon of the fix surface | Read `tests/test_forge_service.py` (95 ln), `tests/test_forge_repo.py` (65 ln), plus the three runtime files carried over from the Wave 1 audit |
| Baseline test run | **GREEN** — command and output in §3 |
| RED tests | **Not written** (hard stop before the tests-first step) |
| Fixes D1/D2/D6/D7 | **Not applied** (see §4 for the exact patch that was ready) |
| D3 | **Report only** by design (§5) — `forge_worker.py` is the plan seat's file and was not touched |

## 2. Phase 1 gate record (logic-gatekeeper) — drafted, not executed

```json
{
  "D1": {
    "architecture": "forge_service._Loop owns one asyncio loop on a daemon thread; Handler threads call loop.run() for every repo coroutine",
    "dataFlow": "HTTP request thread -> _Loop.run(coro) -> asyncio.run_coroutine_threadsafe -> repo coroutine -> response thread",
    "edgeCases": ["repo takes 31 s with a 30 s result timeout", "client retries after 503 while the first write commits"],
    "rootCause": "_Loop.run enforces a timeout with Future.result(timeout=30) but never cancels the underlying coroutine, so a slow write can still commit after the handler has already answered 503 E_SERVICE_UNAVAILABLE."
  },
  "D2": {
    "architecture": "forge_service.do_POST maps the repo's unique violation straight to an HTTP error; forge_repo exposes create and get-by-id only",
    "dataFlow": "POST body idempotency_key -> repo INSERT -> asyncpg UniqueViolation(sqlstate 23505) -> 409 E_EPISODE_EXISTS with no episode",
    "edgeCases": ["lost 201 response then retry with the same key", "same key with a different brief"],
    "rootCause": "The idempotency key is treated as an error discriminator rather than as the lookup key, so a replay can never return the episode the key exists to protect."
  },
  "D6": {
    "architecture": "forge_repo._row is the single mapping seam between SQL rows and service payloads",
    "dataFlow": "SQL RETURNING row -> _row(dict) -> service JSON; a row without 'id' is converted to None",
    "edgeCases": ["function returns a row with no 'id' column", "payload column is invalid JSON"],
    "rootCause": "_row conflates 'no row' with 'row of an unexpected shape', so a schema/function regression surfaces as 404 E_EPISODE_NOT_FOUND instead of a loud shape error."
  },
  "D7": {
    "architecture": "forge_service.do_POST validates two fields and str()-coerces the rest before handing them to the repo",
    "dataFlow": "JSON body -> do_POST field reads -> str(brief)/str(task_family) -> repo INSERT",
    "edgeCases": ["brief is null -> 'None'", "account_id is -5 or true", "budget is a list", "task_family contains spaces"],
    "rootCause": "Untrusted request fields reach persistence through coercion instead of validation, so malformed input is accepted as valid data and later fails as a 503 rather than a 400."
  }
}
```

Phase 2 (entry checks at the function entry, reject before write) was **not applied**.

## 3. Tests run (evidence)

```
$ cd blueprint/files/tests
$ $env:PYTHONPATH=".."; python -m unittest test_forge_service -v
test_bad_body_400_named ... ok
test_create_and_get_episode ... ok
test_health ... ok
test_unhealthy_repo_is_503 ... ok
test_unknown_episode_404_named ... ok
Ran 5 tests in 3.359s
OK
```

- `test_forge_repo.py` requires `FORGE_TEST_DSN` (skipped by `@unittest.skipUnless`); no database was
  contacted, per the read-only/no-production constraint.
- **No failures.** The suite is green *because the defects are still present*: the current tests do not
  cover D1/D2/D6/D7 (no slow-repo, no replay, no shape, no field-validation cases).
- RED was not produced; the planned RED tests are listed in §4.

## 4. Prepared patch (ready to apply, NOT applied)

**`forge_repo.py`** (D2, D6)
- `class RepoShapeError(RuntimeError): code = "E_REPO_SHAPE"`.
- `_row`: when a row is present but `id` is missing, or a JSON column fails to parse → raise
  `RepoShapeError` with the row keys; only `get_episode`'s `row is None` stays `None`.
- new `async def get_episode_by_idempotency_key(key)` → `SELECT * FROM forge_episode WHERE idempotency_key=$1`
  (after `SET search_path`), mapped through `_row`.

**`forge_service.py`** (D1, D2, D6, D7)
- `_Loop.__init__(timeout_s=30.0)`; `_Loop.run`: `future = run_coroutine_threadsafe(...)`, and on
  `concurrent.futures.TimeoutError` → `future.cancel()` then `raise ServiceTimeout("E_SERVICE_TIMEOUT")`;
  `make_server`/`serve` accept `call_timeout_s`.
- `do_POST`: replace the ad-hoc reads with one `_parse_create_body()` that rejects non-object bodies,
  `idempotency_key` not a non-empty string, `account_id` not a positive `int` (bool excluded),
  `brief` not a 1..8192-char string, `task_family` not `^[a-z0-9][a-z0-9_-]{0,63}$`, and `budget` present
  but not a JSON object → `400 E_REQUEST_INVALID` before dispatch.
- `do_POST` conflict branch: on `sqlstate == "23505"` call `get_episode_by_idempotency_key`; found →
  `200 {"episode": row, "replayed": true}`; missing lookup or no row → `409 E_EPISODE_EXISTS`.
- `ServiceTimeout` → `504 E_SERVICE_TIMEOUT`; exception with `code == "E_REPO_SHAPE"` → `500 E_REPO_SHAPE`
  (mapped by attribute, so `forge_service` does not import `asyncpg`).

**Planned RED tests (not written):** slow repo + `call_timeout_s=0.05` → 504 and coroutine cancelled;
replay after 23505 → 200 with the same episode id; repo returning a row without `id` → 500
`E_REPO_SHAPE`; five invalid bodies → 400 `E_REQUEST_INVALID`; `_row({})` → `RepoShapeError` in
`test_forge_repo.py` (no DSN needed).

**Residual on D1 (must stay in the report):** `future.cancel()` is best-effort. If the DB call is already
executing, it may complete after the 504. That is safe only **after D2** lands, because the client's retry
then replays the committed episode instead of creating a duplicate. D1 and D2 must ship together;
D1 alone would return 504 with a second possible 409.

## 5. D3 seam report (no edit made — plan seat owns `forge_worker.py`)

**Exact seam:** `blueprint/files/forge_worker.py:56-63`.

| Line | Code | Problem |
|---|---|---|
| `:56-57` | `try: await self.handler(...)` | handler invocation |
| `:58-61` | `except Exception: … await self.repo.finish_job(job["id"], ok=False, error=…)` | a failure inside `finish_job` here replaces the handler's exception; the real error is masked |
| `:62` | `await self.repo.finish_job(job["id"], ok=True)` | unguarded: if the DB call raises, `run_once` propagates and the job stays `claimed/running` until lease expiry → the handler is re-run (at-least-once) with no worker-level idempotency record |

**Contract the plan seat must implement:** `finish_job` must be idempotent and non-throwing for a duplicate
finish; `run_once` must (a) attempt the finish, (b) on finish failure log `(job_id, handler_error,
finish_error)`, retry once, and (c) return `{"ok": False, "error": "E_FINISH_FAILED"}` while best-effort
persisting `last_error`, never overwriting the handler error in the log. Handler must be documented as
at-least-once and idempotent. **Nothing in `forge_worker.py` was modified.**

## 6. Remaining work (resume order)

1. Write the RED tests in `tests/test_forge_service.py` (+ `_row` shape test in `tests/test_forge_repo.py`).
2. Apply the §4 patch; capture GREEN.
3. Cross-check the existing 5 service tests still pass (they pin: 201 create, 200 fetch, 404 named,
   503 unhealthy, 400 bad body).
4. Hand D3 to the plan seat with §5; do not touch `forge_worker.py` here.
5. Optional follow-up from the Wave 1 audit, not in this task: D4/D5 reaper SQL function and split
   counters, D8 shutdown, D9 timeouts/Content-Type.
