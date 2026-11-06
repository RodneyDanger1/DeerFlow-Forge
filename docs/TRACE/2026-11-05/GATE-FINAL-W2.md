# Wave-2 final gate — 2026-11-05

**HEAD at start:** `551ede8` · **Tree:** clean before gate; uncommitted after gate: `forge_repo.py`,
`tests/test_forge_e2e.py`, `tests/test_forge_eval.py` · **Production:** not touched.

## Staging corpus (scratch PostgreSQL 16 + G0 bundle)

Command (on staging VPS, `.venv/bin/python -m pytest tests -q`):

```text
FORGE_TEST_DSN=postgresql://postgres:scratch@127.0.0.1:55439/postgres
FORGE_G0_DIR=/opt/pod-pipeline-staging/data/staging/g0
```

| Run | Result |
|---|---|
| Before fixes | **3 failed**, 160 passed, 4 skipped |
| After runtime fixes | 163 passed, 4 skipped |
| After W3 transition/event fix | **165 passed, 4 skipped**, 25 warnings, 8 subtests passed, 15.11 s |

Failures found and fixed:

1. `_row()` treated the DB's all-NULL composite (empty `claim_job`) as a malformed row.
   Fix: all-NULL dict → `None`; a partially populated row with missing `id` still raises
   `E_REPO_SHAPE`.
2. `test_forge_e2e` expected the old duplicate `409 E_EPISODE_EXISTS`; D2 deliberately changed
   replay to `200 {"episode":…, "replayed":true}`. Pin updated to the intended contract.
3. `test_forge_eval.test_regression_refuses` encoded an impossible `8/8 + 1 regression` (9 outcomes
   for n=8). Re-pinned to `7/8 + 1`; duplicate-golden and successes+regressions>n cases added.
4. **W3 real bug:** `ForgeRepo.transition()`/`append_event()` used `SELECT fn(...)`, which returns one
   composite column; asyncpg produced `{'forge_transition_episode': …}` and `_row` refused it. Fixed
   to `SELECT * FROM fn(...)`; added a real-DB test asserting exactly one `episode.transition` event
   with `from=intake`, `to=briefed`. This path had no prior coverage.

The 4 remaining skips are DB-dependent tests whose required service is not part of this scratch run;
they are named by pytest and are not counted as passes.

## W3 status

**CLOSED**: the SQL transition function is the single event writer, proved by an event-count
assertion on real PostgreSQL. No Python double-append exists on this path.

## W1 blocker (do not fake)

The gateway `Repo` protocol (`forge_gateway.py:241-243`) is synchronous and carries only a
`ToolResult`; `forge_tool_call` requires `episode_id`, `tool_id`, `params`, and constraint-valid
`idempotency_key` (`schema_forge.sql:324-351`). The current contract cannot populate that row, and a
sync adapter cannot use the async `asyncpg` pool. Decision required before W1 implementation:
extend `ToolResult` with persisted-call context and make `Gateway.execute`/`Repo` async, or add an
async gateway runner. No fake adapter was added.

## Local suite

`python -m unittest discover -s tests -p 'test_forge_*.py'` → **111 passed, 9 skipped in 7.92 s**.

## Console build and browser gate

Build: `NITRO_PRESET=node-server npm run build` → success; `.output/server/index.mjs` served on
`127.0.0.1:8092`, HTTP 200 (14,147 bytes).

`node scripts/visual-console-smoke.mjs http://127.0.0.1:8092` → `ok:true`, `failures: []`, all five
sections non-empty (Board 3,063 chars; Routes 1,842; Sandbox 2,959; Playbook 24,429; Sources 12,104).

Playwright control probe → **18/18 checks**, no console/page errors:

```text
tabs Board/Routes/Sandbox/Playbook/Sources; model radios Apparel/Knitwear/Accessories/Odd 3D/Stationery checked;
Run route completes; sandbox opens pod_pipeline/runner.py; Copy -> Copied; Download event fires;
desktop horizontal overflow 0; mobile 390x844 overflow 0; mobile source select visible with 34 options.
```

Playwright a11y probe → **8/8 checks**:

```text
one h1 ("Forge"); every button/select/input/link has an accessible name; 3 landmarks;
12/12 Tab stops visible and in nav order; mobile overflow 0; all visible tap targets >= 40x40;
zero runtime errors.
```

**Limit:** native GUI/CUA remains unavailable; no desktop-app claim is made. Browser permission
prompt behaviour for clipboard is not measured; the Copy control was observed reaching `Copied`.

## Frontend gate

| Command | Result |
|---|---|
| `npm.cmd test` | **65 passed, 0 failed, 0 skipped** (18 suites) |
| `npm.cmd run typecheck` | exit 0 |
| `npm.cmd run lint` | exit 0, **0 errors / 5 warnings** |

## Stub sweep

`Select-String` over the six changed product modules for
`TODO|FIXME|XXX|HACK|placeholder|NotImplemented|not implemented|mock|stub|dummy|lorem|simplified for|for illustration`
→ **zero hits**.

## Not verified

- Live production `forge` DB/service/systemd/TLS — none exists or was touched.
- The 4 skipped DB-dependent tests — require their named staging service.
- Craft execution through the Forge service — separate seam, not wired.
- Deploy/publish, DeerFlow MCP registration, critic vision accuracy, learning above L0.

## Update after this gate — W1/W5 closed

This report predates W1/W5. Current state:

- W1 (tool-call idempotency persistence) is **closed**: async gateway + `ForgeGatewayRepo` insert
  `in_flight` before execution, replay terminal rows, and refuse concurrent in-flight duplicates.
  Staging includes 3 additional real-PostgreSQL tests.
- W5 (eval-row persistence) is **closed at repository level**: `ForgeRepo.record_eval()` writes one
  immutable row per episode/arm; no consumer/route calls it yet.
- Current suites: **177 passed / 4 skipped** staging; **123 passed / 13 skipped** local.
- Historical entries above are retained; current truth is `docs/PLAN-CONTINUATION.md` and
  `docs/CAPABILITY-MATRIX.md`.
