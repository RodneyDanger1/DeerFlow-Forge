# RUNTIME AUDIT — Forge service / repo / worker (Wave 1, read-only)

**Task:** task-21. **Date:** 2026-11-05. **Mode:** read-only — no source, docs, tests, DB or deploy touched.
**Files written:** this file only.
**Scope read:** `blueprint/files/forge_service.py` (130 ln), `forge_repo.py` (120 ln), `forge_worker.py` (72 ln),
`docs/TRACE/AGENT-INSTRUCTIONS.md` (33 ln).
**NOT read (UNVERIFIED, timebox):** `sql/schema_forge.sql`, `tests/*` (incl. `test_forge_service/repo/worker/e2e`,
`forge_schema_assertions.py`), `forge_gateway.py`, `forge_verifier.py`, `forge_critic.py`, `forge_eval.py`.
Every defect below is **READ** (static code) unless labelled **VERIFIED** (run). No test was executed; no DB
was contacted, so all runtime claims are static.

Labels: **VERIFIED** = command+output. **READ** = file:line. **INFERRED** = from read code, not executed.
**UNVERIFIED** = not checked.

---

## 1. Invariants as coded

| # | Invariant | Evidence | Status |
|---|---|---|---|
| I1 | Service binds loopback only | `forge_service.py:112-113` rejects host outside `127.0.0.1/::1/localhost` | READ |
| I2 | Exactly one repo source (`repo` xor `repo_factory`) | `forge_service.py:114-115` | READ |
| I3 | Service is a thin HTTP seam; never calls Craft/publishes | docstring `:1-4`; no Craft import in file | READ |
| I4 | One episode per `idempotency_key` | inferred only from 23505 → 409 mapping `forge_service.py:101-102`; schema constraint **UNVERIFIED** | INFERRED |
| I5 | Job state machine: `claimed/running` → `queued` or `abandoned` on lease expiry | `forge_repo.py:111-119` | READ |
| I6 | `run_once` claims one job, runs one handler, always records a finish | `forge_worker.py:52-63` — **violated when `finish_job` itself fails** (D3) | READ (defect) |
| I7 | Reaper is bounded and cancellable | `forge_worker.py:32-43` (`wait_for(stop.wait())`), `:24-26` interval validation | READ |
| I8 | Every request gets a body; errors are named `E_*` | `forge_service.py:94-95,100-104` | READ (partial, D7) |

## 2. Call chains (entry → handler → repo → SQL → response)

**POST `/v1/episodes`**
`do_POST` `forge_service.py:80` → path check `:81` → body size/parse/field check `:84-93` →
`_Loop.run` `:33-34` → `ForgeRepo.create_episode` `forge_repo.py:46` → `SET search_path` `:49` →
`INSERT … RETURNING *` `:50-54` → `_row()` `:20-29` → `201` JSON `:105`. Failure branches: 400 `:95`,
409 `:102`, 503 `:104`.

**GET `/v1/episodes/{id}`**
`do_GET` `:51` → path prefix/slash guard `:65-69` → `loop.run` `:71` → `get_episode` `forge_repo.py:57` →
`SELECT * … WHERE id=$1` `:60` → `_row` → `200/404`.

**GET `/healthz`** — `:53-64` → `health()` `forge_repo.py:38` → `SELECT 1` + `information_schema` count `:41-43`.

**Worker tick** — `ForgeWorker.run_once` `forge_worker.py:52` → `claim_job` `:53` →
`forge_claim_job` SQL `forge_repo.py:97` → handler `:57` → `finish_job` `:62` → `forge_finish_job` `:103`.

**Reaper tick** — `LeaseReaper.run` `:32` → `run_once` `:29` → `reap_expired_jobs` `forge_repo.py:106` →
**direct UPDATE** `:110-119` (bypasses the SQL functions used everywhere else — D4).

## 3. Confirmed defects (severity, repro, proposed fix)

### D1 — HIGH — Timed-out request is neither cancelled nor idempotent; a 503 can follow a committed write
**Evidence:** `forge_service.py:33-34` `.result(timeout=30)` raises on timeout but the coroutine keeps
running (no `future.cancel()`); `:100-104` maps any exception to `503 E_SERVICE_UNAVAILABLE`; the write
path `forge_repo.py:50-54` has no idempotent upsert.
**Consequence:** slow DB → client sees 503, episode row may still be committed; client retry then hits
D2 (409) or creates a second row if the schema constraint is absent.
**Repro (not run — deterministic by construction):** inject repo whose `create_episode` sleeps 31 s, POST
once, observe 503; query table afterwards (row present) and POST again (409 or duplicate).
**Fix:** `future.cancel()` + return `504 E_SERVICE_TIMEOUT`; add `get_episode_by_idempotency_key` and make
create `INSERT … ON CONFLICT (idempotency_key) DO UPDATE/DO NOTHING RETURNING *` so a retry returns the
same episode.

### D2 — HIGH — Idempotency key answers 409 with no body instead of returning the existing episode
**Evidence:** `forge_service.py:101-102` (23505 → `409 E_EPISODE_EXISTS`, no episode payload);
`forge_repo.py` exposes no lookup-by-key (`:46-61`).
**Consequence:** the key cannot do its job. A caller that lost the 201 response can never recover the
episode; it must treat 409 as success *or* guess the id — both are unsound.
**Repro:** POST identical body twice → second response is 409 with `{"error":…}` only.
**Fix:** repo `get_episode_by_idempotency_key()`; service returns `200 {"episode": row}` for a same-key
replay (and 409 only for same key + different payload, if that is the chosen contract).

### D3 — MEDIUM-HIGH — Worker can leave a job `running` after a successful handler, and can mask the handler error
**Evidence:** `forge_worker.py:56-63` — on handler success, `:62 finish_job(ok=True)` is unguarded: if the
DB call raises, it propagates; the job stays `claimed/running` until lease expiry and is then re-run
(at-least-once with no worker-level idempotency record). On handler failure, `:60 finish_job(ok=False)` is
also unguarded: a finish error replaces the handler's exception (masking).
**Consequence:** duplicate side effects on re-run; the logged error is the DB error, not the real job error.
**Repro:** fake repo whose `finish_job` raises once; run `run_once` → exception escapes, job not finished.
**Fix:** wrap both finish calls; on finish failure log `(job_id, handler_error, finish_error)` and retry
once; make `run_once` return an explicit `{"ok": false, "error": "E_FINISH_FAILED"}` while persisting
`last_error` best-effort. Document at-least-once and require handler idempotency.

### D4 — MEDIUM — Reaper bypasses the SQL state-machine functions with a raw UPDATE
**Evidence:** `forge_repo.py:106-119` updates `forge_job.state`/`lease_until`/`last_error` directly, while
claim/finish go through `forge_claim_job` / `forge_finish_job` (`:97`, `:103`).
**Consequence:** any CHECK constraint, trigger, or job-event row implemented inside those SQL functions is
skipped; reaper-driven abandonment is invisible to whatever audit the functions maintain.
**UNVERIFIED:** whether `schema_forge.sql` actually has such triggers/audit (file not read).
**Fix:** add `forge_reap_expired_jobs()` SQL function and call it; keep the Python as a thin wrapper.

### D5 — MEDIUM — Reaper reports abandoned jobs as "requeued" (observability lie)
**Evidence:** `forge_repo.py:119` returns `len(rows)` regardless of the CASE result `:112-116`;
`forge_worker.py:32-43` accumulates that count as `requeued`.
**Consequence:** dashboards say "requeued N" when N were abandoned; hides a job-loss signal.
**Fix:** return `{requeued, abandoned}` from the repo; log both; make `run_once` return the breakdown.

### D6 — MEDIUM — `_row()` converts shape errors into "not found"
**Evidence:** `forge_repo.py:20-29` returns `None` whenever `id` is absent, for *all* callers; service maps
`None` to `404 E_EPISODE_NOT_FOUND` (`forge_service.py:75-76`). `transition` `:63-71` and `append_event`
`:73-78` also pass through `_row`, so a function returning a row without `id` is indistinguishable from
"no such episode".
**Consequence:** a schema/function regression silently becomes a 404 (or `None` result) instead of a loud
`E_REPO_SHAPE` — the exact failure class the read-only audit exists to prevent.
**Fix:** raise `E_REPO_SHAPE` (named error with row keys) when `id` is missing; only `get_episode` may map
absence to `None`.

### D7 — MEDIUM — POST validation is partial; coercion hides bad input
**Evidence:** `forge_service.py:84-99` — only `idempotency_key` (str, non-empty) and `account_id` (int) are
checked `:92-93`; `brief`/`task_family` are only coerced by `str()` `:98-99` (a dict brief becomes
`"{'a': 1}"`, `None` becomes `"None"`); no length caps; `budget` is forwarded as arbitrary JSON `:99` and a
non-serialisable value raises inside `json.dumps` in the repo (`forge_repo.py:90`), surfacing as 503, not 400;
`account_id` accepts `0`/negatives.
**Repro:** POST `{"brief": {"x": 1}, "task_family": null, "account_id": -5, …}` → 201 with coerced strings.
**Fix:** validate types + max lengths (`brief ≤ 8 KiB`, `task_family` regex), reject `account_id <= 0`,
require `budget` to be a JSON object, and return `400 E_REQUEST_INVALID` on any failure *before* dispatch.

### D8 — LOW — No shutdown path: the service thread/event loop and repo pool leak
**Evidence:** `forge_service.py:110-130` — `_Loop` starts a daemon thread `:28-31`, `make_server` sets
`server.forge_loop/forge_repo` `:120-121`, but nothing stops the loop or closes the pool; loop creation
precedes server construction, so a failing `ThreadingHTTPServer(...)` leaves the thread running.
**Consequence:** repeated test/server construction leaks threads and DB connections (pool max 4, below).
**Fix:** `close()` on the server that stops the loop and awaits `repo.close()`; construct the server before
starting the loop, or guard with try/except.

### D9 — LOW — No socket/read timeouts and no `Content-Type` check on POST
**Evidence:** `forge_service.py:84-87` reads `Content-Length` then `self.rfile.read(length)` with no timeout;
`ThreadingHTTPServer` is constructed `:119` without a handler timeout; content type is not inspected.
**Consequence:** slow clients tie up one thread per connection (unbounded thread creation); JSON sent as
non-JSON content type is accepted.
**Fix:** set `Handler.timeout` (e.g. 15 s) and reject non-`application/json` bodies with
`415 E_REQUEST_UNSUPPORTED_MEDIA`. **UNVERIFIED:** whether tests pin the current permissive behaviour.

## 4. DB / runtime limits discovered (from code; schema UNVERIFIED)

| Limit | Value | Evidence |
|---|---|---|
| POST body cap | 1,048,576 bytes (rejects `<=0` and `>`1 MiB) | `forge_service.py:85` |
| Service-side call timeout | 30 s, **not cancelled on expiry** | `forge_service.py:34` (D1) |
| Connection pool | `min_size=1, max_size=4` | `forge_repo.py:33` |
| `search_path` | `forge, public`, `SET` per acquire (session-scoped round-trip) | `forge_repo.py:40,49,59,66,75,86,96,102,109` |
| `max_attempts` | validated 1..10; default 3 | `forge_repo.py:83-84`, `:82` |
| Job lease | default 300 s (worker + claim) | `forge_worker.py:48`, `forge_repo.py:94` |
| Reaper cadence | default 30 s, must be > 0 | `forge_worker.py:24-26` |
| Episode budget / job payload | JSONB (JSON-encoded at the seam) | `forge_repo.py:52-54, 88-91` |
| DB statement/lock timeouts, index/uniqueness on `idempotency_key`, JSONB size caps | **UNVERIFIED — schema not read** | `sql/schema_forge.sql` |

## 5. Contradictions between docstrings/README claims and code (READ)

1. `forge_service.py:1-4` says "Tests may inject a fake repo" — true (`:110-115`), but the repo also accepts
   `repo_factory`, and the docstring does not mention it (`:110`). Minor.
2. `forge_repo.py:107` docstring says "Recover expired leases; abandon a job once its attempt cap is
   reached" — the code also *counts* both outcomes as one number (D5). The doc claim and the counter disagree.
3. `forge_worker.py:1` "one claim, one handler, one truthful finish" — the finish can be non-truthful (D3).

## 6. Not verified / open questions (next wave)

1. **UNVERIFIED:** `sql/schema_forge.sql` — actual constraints, unique index on `idempotency_key`, job-state
   CHECK list, `forge_claim_job`/`forge_finish_job`/`forge_transition_episode` semantics, lock behaviour.
2. **UNVERIFIED:** tests — which invariants are pinned, and whether D1/D2/D3 are already covered by
   `test_forge_service.py` / `test_forge_repo.py` / `test_forge_worker.py`.
3. **UNVERIFIED:** `forge_gateway.py` — whether it calls this service and shares the idempotency contract.
4. **UNVERIFIED:** whether `asyncpg` exceptions in this version expose `.sqlstate` (code assumes it,
   `forge_service.py:101`); if not, all 23505 conflicts degrade to 503.
5. **UNVERIFIED:** whether episode rows are ever created by any other path (worker/gateway) that would make
   D2's "existing episode" lookup mandatory rather than desirable.

## 7. Proposed fix order (smallest true change first)

1. D2 (repo lookup + replay 200) — unblocks clients and makes D1's retry safe.
2. D1 (cancel on timeout, 504, upsert create).
3. D3 (guarded finish + explicit finish failure).
4. D6 (`E_REPO_SHAPE`) — prevents silent 404s.
5. D7 (validation) → D4/D5 (SQL reaper function + split counters) → D8/D9 (lifecycle + timeouts).

All fixes are read-only proposals; no code was changed in this wave.
