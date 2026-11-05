# Plan continuation — DeerFlow Forge (2026-11-05)

**Status:** wave-2 closeout complete for runtime, worker, verifier/critic/eval guards, service
entry point, console browser gates, and authoritative docs. **No production deployment.** Next
implementation is W1, blocked on an API decision documented below.

Verified by command (not prose): console **65/65**; Forge local **116 passed / 9 skipped**; staging
**170 passed / 4 skipped** on scratch PostgreSQL 16 + G0; gateway **33/33**; SQL **18/18**; browser
controls **18/18**; keyboard/a11y **8/8**. Full receipts: `docs/TRACE/2026-11-05/GATE-FINAL-W2.md`
and `docs/CAPABILITY-MATRIX.md`.

## Outcome

The next increment makes Forge tool calls durable and replay-safe across process restarts. Today the
gateway can compute and honour an idempotency key only inside an `InMemoryRepo`; the PostgreSQL table
exists but no adapter writes it. After W1, a caller that loses a response can reissue the same call and
receive the stored result without re-executing the tool, and the service/worker can prove that with a
real-DB duplicate-call test.

## Current behavior (evidence)

- Service: `forge_service.py` exposes `/healthz`, create/get episode; strict request validation;
  timeout → 504; duplicate episode → 200 replay; `python -m forge_service` constructs `ForgeRepo` on
  the service loop and refuses non-loopback binds.
- Repository: `forge_repo.py` creates/gets episodes, transitions with exactly one event append,
  claims/finishes jobs, reaps expired leases. `transition`/`append_event` use `SELECT * FROM fn(...)`.
- Worker: `python -m forge_worker --once` with guarded finish and named errors.
- Gateway: `Gateway.execute()` is synchronous and uses `Repo.find/store`; the only implementation is
  `InMemoryRepo`. `forge_tool_call` exists in `sql/schema_forge.sql` with a unique key and
  `forge_replay_tool_call(p_key)`.
- Verifier/critic/eval: pure functions with tests; no service/worker route or row writer.
- Console: static viewer; no HTTP client to Forge. Browser controls and a11y are verified.

## Decisions

1. **W1 API — accepted direction:** extend `ToolResult` with `episode_id`, `tool_id` and normalized
   `params`; make `Gateway.execute` and `Repo.find/store` async; implement `ForgeGatewayRepo` over
   `asyncpg`; keep `InMemoryRepo` as a classified test double.
   *Rejected:* a synchronous wrapper around the async pool (two execution paths, unsafe loop use) and
   writing tool calls after execution without an atomic pre-write marker (replay can duplicate effects).
2. **W1 persistence point:** insert an `in_flight` row before executor invocation, then update to
   `succeeded|failed|refused`; a duplicate key while `in_flight` returns a named retryable refusal,
   not a fake result. This preserves once-only execution under concurrent callers.
3. **Service remains loopback-only.** No auth/TLS claim until W8.
4. **Console remains a viewer.** Do not add a fake run/backend control.
5. **No learning claim.** W4-B remains out of scope until verification and eval persistence exist.

## File-by-file change for W1

| File | Change | Edge cases / errors |
|---|---|---|
| `blueprint/files/forge_gateway.py` | `ToolResult` gains episode/tool/params; `Repo` and `Gateway.execute` become async; `execute` validates context before lookup; preserve all named refusals | empty episode/tool, bad key, duplicate in-flight, executor timeout, store conflict |
| `blueprint/files/forge_repo.py` | New `ForgeGatewayRepo` adapter with async `find`/`store`; SQL uses `forge_tool_call` and `forge_replay_tool_call`; JSON params bounded | `23505` on same key, shape errors, 65,536-byte params limit |
| `blueprint/files/forge_service.py` | Add `/v1/tool-calls` POST only if the gateway has a real caller; otherwise W1 remains library-level | 400 boundary, 409 in-flight, 200 replay, 504 timeout |
| `blueprint/files/tests/test_forge_gateway.py` | Convert awaited calls; add async duplicate, in-flight, executor-not-called-on-replay tests | no test weakening; `InMemoryRepo` remains a test double |
| `blueprint/files/tests/test_forge_repo.py` | Real-DB test: first store → second find returns same result; unique key enforced; row state transitions | scratch DSN only; skip explicitly without `FORGE_TEST_DSN` |

**Rollback:** revert the W1 commit; `InMemoryRepo` path remains; DDL is unchanged; no data migration.
**Acceptance command:** `FORGE_TEST_DSN=... python -m pytest tests/test_forge_gateway.py
tests/test_forge_repo.py -q` plus full staging suite; all green with named skips.
**Out of scope:** real Craft executor, production auth/TLS, DeerFlow registration, publish.

## Done — crossed off

| Item | Evidence |
|---|---|
| Console viewer + copy/download + mobile | 65/65; visual smoke; 18/18 controls; 8/8 a11y |
| Forge DDL, 13 tables/36 transitions, apply-twice | 18/18 SQL; scratch PG |
| Repository episode/job/lease/abandon path | real-PG tests; W3 event-count pin |
| Worker CLI + guarded finish + reaper | 12 CLI + worker tests; staging green |
| Service create/get/health + timeout/replay/shape/validation | service tests + e2e; **service daemon entry point** |
| Gateway policy/idempotency/verdict | 33/33 (in-memory) |
| Verifier PNG/SHA/DPI/gate report | 8/8 + real G0 pair |
| Blind critic contract | 14/14; invalid human/gate refused |
| Eval/promotion contract | 13/13; duplicate/sanity refusals; inactive proposal |
| G0 provenance | independent byte-identical reproduction; 9/9 gates |
| Truth audit / docs corrections | README, CAPABILITY-MATRIX, this plan; historical docs labelled |
| Wave-2 RED→GREEN + full staging | 170/4 |

## Next steps in order

1. **W1** per the decision above — real-DB duplicate-call proof.
2. **W5 eval persistence** — write `forge_eval` rows from a consumer; schema exists, no writer.
3. **Executor seam** — registered absolute-path Craft executor; prove a real trace/retouch path and
   reject absent engines by name.
4. **Consumer seam** — verifier/critic/eval called by worker/service with persisted evidence.
5. **W7 clean-env deps** — verify `asyncpg`/`Pillow` from a clean install, not an ambient venv.
6. **W8 production hardening** — systemd, loopback+TLS/auth, migration/rollback, backup/restore drill.
7. **DeerFlow registration** — apply only after the executor/consumer seams are real.
8. **Learning** — retrieval/A-B/promotion/rollback after 1–7; otherwise stay L0.

## Blockers / not claimed

- No production `forge` DB, service unit, TLS/auth, deploy, or publish.
- No real executor; gateway cannot run Craft today.
- No verifier/critic/eval consumer; they are libraries.
- No DeerFlow MCP registration; no native GUI/CUA bridge.
- 4 staging skips require their named services; vision accuracy and learning above L0 unmeasured.
