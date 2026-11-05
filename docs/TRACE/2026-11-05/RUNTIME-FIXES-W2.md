# RUNTIME FIXES — WAVE 2 (task-28) — COMPLETE (D1, D2, D6, D7 fixed; D3 seam reported)

**Status:** COMPLETE for the authorised scope. Gate Phase 1 approved by Lead waiver (2026-11-05).
**Scope touched:** `blueprint/files/forge_service.py`, `blueprint/files/forge_repo.py`,
`blueprint/files/tests/test_forge_service.py`, `blueprint/files/tests/test_forge_repo.py`.
**Deliberately NOT touched:** `forge_worker.py` (owned by plan seat — `git status` shows it modified by that
seat, not by me), `forge_verifier.py`, `forge_critic.py`, `forge_eval.py`, docs outside this receipt,
production, DB.
**Task:** task-28 (completed).

---

## 1. Phase 1 gate (approved)

The four-field gate for D1/D2/D6/D7 was written in the previous revision of this receipt (§2 of the PARTIAL
version) and approved by Lead waiver. This wave applied exactly that patch: entry checks at the boundary,
no coercion, one named error per failure class.

## 2. Changed files (mine)

| File | Change |
|---|---|
| `blueprint/files/forge_service.py` | D1 cancellable timeout (`ServiceTimeout`, `_Loop(timeout_s)`, `future.cancel()`), `504 E_SERVICE_TIMEOUT` on all paths; D2 replay (`_lookup_by_key`, `200 {"episode":…,"replayed":true}`, 409 only when no lookup/row); D6 `_valid_episode_row` → `500 E_REPO_SHAPE`; D7 `_validate_create()` at the boundary, `400 E_REQUEST_INVALID` before any write; `make_server/serve(call_timeout_s=…)`; loop stopped if server construction fails; `_error()` helper. |
| `blueprint/files/forge_repo.py` | D6 `RepoShapeError.code = "E_REPO_SHAPE"` raised by `_row()` for a missing `id` or unparseable JSON column (was silent `None`); D2 `get_episode_by_idempotency_key()` lookup. |
| `blueprint/files/tests/test_forge_service.py` | 5 new regression tests (timeout+cancel, replay 200, legacy 409 fallback, shape 500, six malformed-field 400 cases) + fixtures `ReplayRepo`, `LegacyConflictRepo`, `ShapeRepo`, `SlowRepo`, `_ConflictError(sqlstate="23505")`. |
| `blueprint/files/tests/test_forge_repo.py` | 3 new no-DB unit tests for `_row()` shape errors + `RepoShapeError` import. |

No mock/fake in a product path: the fakes live in tests only and model the asyncpg/HTTP boundary.

## 3. RED evidence (before the fix)

```
$ cd blueprint/files/tests; $env:PYTHONPATH=".."
$ python -m unittest test_forge_service
FAIL: test_row_shape_error_is_named_500_not_404 ... AssertionError: 200 != 500
Ran 10 tests in 5.144s
FAILED (failures=8, errors=1)
```
The pre-fix code failed 9 of 10 service tests: no timeout (hang/503), no replay (409 with no body),
no shape error (200/404), no field validation (201 with coerced values).
Repo `_row` had no shape defense: `_row({"state":"intake"})` returned `None` (silent "not found").

## 4. GREEN evidence (after the fix)

```
$ cd blueprint/files/tests; $env:PYTHONPATH=".."
$ python -m unittest test_forge_service
Ran 10 tests in 5.717s
OK

$ python -m unittest test_forge_repo.RowShapeUnitTests -v
test_row_without_id_raises_shape_error ... ok
test_row_with_unparseable_json_column_raises_shape_error ... ok
test_none_row_stays_none ... ok
Ran 3 tests in 0.001s
OK
```
Environment note: `asyncpg` was absent, so `test_forge_repo` could not import at all
(`ModuleNotFoundError`). It was installed into the test environment only (`python -m pip install asyncpg`),
after which the 3 no-DB shape tests ran. Database tests in that file remain skipped without
`FORGE_TEST_DSN` (no production DB was contacted).

**Old behaviour preserved:** the original 5 service tests (`test_health`, `test_unhealthy_repo_is_503`,
`test_create_and_get_episode`, `test_unknown_episode_404_named`, `test_bad_body_400_named`) pass unchanged
inside the same 10/10 run — the fix is additive at the boundary, not a contract change for valid callers.

## 5. D3 seam (report only — `forge_worker.py` untouched)

**Seam:** `blueprint/files/forge_worker.py:56-63`.
- `:58-61` — inside `except Exception`, `await self.repo.finish_job(..., ok=False, error=…)` is unguarded:
  a DB failure there replaces the handler's exception, so the logged cause is the finish failure, not the
  real job failure.
- `:62` — `await self.repo.finish_job(job["id"], ok=True)` is unguarded: if it raises, `run_once`
  propagates and the job stays `claimed/running` until lease expiry, then the handler is re-run
  (at-least-once) with no worker-level idempotency record.

**Contract for the plan seat:** `finish_job` must be idempotent and non-throwing for a duplicate finish;
`run_once` must attempt the finish, on failure log `(job_id, handler_error, finish_error)`, retry once,
return `{"ok": False, "error": "E_FINISH_FAILED"}` while best-effort persisting `last_error`, and never
mask the handler error. Document the handler as at-least-once and idempotent.

## 6. Residuals / unverified

1. **D1 + D2 are coupled by design:** `future.cancel()` is best effort. If the DB call is already running
   it may still commit after the `504`; the client's retry is then safe **only because** D2 returns the
   committed episode as `200 replayed:true`. Do not split these in review.
2. **DB-level replay** (`get_episode_by_idempotency_key`) is **UNVERIFIED** against PostgreSQL: no DSN was
   available, the repo test is skipped. The SQL is a single lookup on `forge_episode.idempotency_key`;
   whether that column is unique/indexed is still UNVERIFIED (`sql/schema_forge.sql` was not read).
3. **`asyncpg` install** was environment-only; no dependency manifest was edited (out of scope).
4. **D4/D5/D8/D9** from the Wave 1 audit are not in this task and remain open.
5. `Content-Type` is still not enforced (D9) — deferred deliberately to keep this diff minimal.

## 7. Commands run

```powershell
cd "C:\Users\Riley\Desktop\DeerFlow Forge\blueprint\files\tests"
$env:PYTHONPATH=".."
python -m unittest test_forge_service              # 10/10 OK  (RED before: 8 failures + 1 error)
python -m unittest test_forge_repo.RowShapeUnitTests   # 3/3 OK (after env-only asyncpg install)
cd "C:\Users\Riley\Desktop\DeerFlow Forge"; git status --porcelain -- blueprint docs/TRACE
```
