# Plan continuation — DeerFlow Forge (2026-11-05)

**Status:** W1 (tool-call idempotency persistence) and W5 (eval-row persistence) are now implemented
and tested against real PostgreSQL. The console is **deployed and live on the VPS**, with 22/22 live
black-box checks and CUA native evidence. **No production Forge DB/service or Craft execution.**
The next implementation seam is the real executor/consumer path.

Verified by command: console **65/65**; Forge local **123 passed / 13 skipped**; staging
**177 passed / 4 skipped**; gateway **36/36**; SQL **18/18**; browser controls **22/22 live checks**;
keyboard/a11y **8/8**. Receipts: `docs/TRACE/2026-11-05/GATE-FINAL-W2.md`,
`docs/TRACE/2026-11-05/LIVE-VPS-VERIFICATION.md`, `docs/CAPABILITY-MATRIX.md`.

## Outcome

Forge can now persist a tool call before it executes and replay the stored result after a restart,
without re-executing the executor. It can also record one immutable evaluation row per episode and arm.
The next increment makes those libraries part of an actual pipeline: a registered Craft executor and a
worker/service consumer that writes artifacts, gates, critiques and evals.

## Current behavior (evidence)

- Gateway: `Gateway.execute()` is async; `ForgeGatewayRepo` inserts an `in_flight` row before execution,
  updates a terminal row after, and replays terminal results. A concurrent duplicate raises
  `E_IDEMPOTENCY_IN_FLIGHT`. **W1 tests: 3 real-PostgreSQL tests + 36 gateway unit tests.**
- Repository: `ForgeRepo.transition()` appends exactly one event; jobs/leases/reaper tested; jobs have
  no stale in-flight tool-call expiry (documented residual).
- Evaluation persistence: `ForgeRepo.record_eval()` validates arm/verdict/human/reviewer, inserts into
  `forge_eval`, maps unique conflicts to `E_EVAL_EXISTS`, and maps missing episodes to
  `E_EPISODE_NOT_FOUND`. **Real-PG test covers both arms, duplicate, invalid arm, missing episode.**
- Service: loopback `/healthz` and create/get episode only; no tool-call or eval route.
- Worker: `python -m forge_worker --once`; guarded finish; no gateway/verifier consumer.
- Verifier/critic/eval: verified contracts, no automated pipeline consumer.
- Console: static viewer; honest “Static blueprint · no live services” and “Simulation…” labels.
- VPS console: active at `09b20e5` runtime source; 22/22 live checks; CUA native checks.

## Decisions

1. **W1 is closed** with async gateway + atomic `in_flight` insert + persisted replay.
   *Rejected:* a sync wrapper around asyncpg and post-execution-only persistence (duplicate effects).
2. **W5 persistence is closed at repository level**, not as an automated consumer. A row is append-only
   and unique per `(episode_id, arm)`; no route/worker calls it yet. Do not claim an eval pipeline.
3. **Residual W1 risk:** a crashed executor leaves an `in_flight` row with no expiry. Until a recovery
   policy exists, duplicate calls for that key are refused—fail-closed, not re-executed. A future
   reaper must only abandon in-flight rows after a declared deadline and must preserve evidence.
4. **Service remains loopback-only.** No auth/TLS claim until W8.
5. **Console remains a viewer.** No fake run/backend control.
6. **No learning claim.** L0 remains until retrieval/A-B/promotion/rollback exist.

## Completed in this increment

| Item | File | Evidence |
|---|---|---|
| W1 async gateway + persisted repo | `forge_gateway.py`, `forge_repo.py` | 36 gateway tests; 3 real-PG tests: success/replay one row, in-flight refusal, executor-crash failed row |
| W1 atomic in-flight before executor | `ForgeGatewayRepo.begin` | unique-key `ON CONFLICT DO NOTHING`; row inspected after execute |
| W1 replay context | `ToolResult` episode/tool/cmd/params/argv/duration | replay assertions |
| W5 eval row writer | `ForgeRepo.record_eval` | baseline+memory rows; duplicate `E_EVAL_EXISTS`; invalid arm `ValueError`; missing episode `E_EPISODE_NOT_FOUND` |
| Full suite | staging | **177 passed, 4 skipped** in 14.42 s |
| Local suite | `unittest` | **123 passed, 13 skipped** |
| VPS console | live deployment | 22/22 checks + CUA evidence |
| Docs | README, capability matrix, this plan | current, with historical files retained |

## Next: executor seam (decision-complete)

**Outcome:** one registered Craft tool call runs on a copy through an absolute-path binary, produces a
real artifact, and returns a persisted `ToolResult`; an absent engine refuses by name.

**Files:** new `forge_executor.py`; extend `forge_gateway.ToolSpec` only if a binary/path field is
required; add `tests/test_forge_executor.py`; wire one worker job kind in `forge_worker` later.

**Rules:** resolve absolute binary path and verify `--version`; reject bare names/PATH shims; copy inputs
into the sandbox; explicit roots; timeout; no model-reported success; absent Design/Effect/Film refuses.

**Tests:** (1) a fake binary fixture writes a file and exits 0 → artifact path/hash recorded; (2) absent
binary → named `E_TOOL_NOT_INSTALLED`; (3) timeout → killed process, no success; (4) path outside roots
denied. **Rollback:** remove module; gateway `Executor` remains injectable.

**Out of scope:** production DB/service, publish, DeerFlow, autonomous promotion.

## Next: consumer seam

Wire executor → verifier/critic/eval in one worker job kind, persisting `forge_tool_call`, artifact,
gate/critique and eval rows. Acceptance: one job produces evidence rows with hashes, and a failed gate
produces a named refusal—not a success. Do not claim this until the executor is real.

## Remaining sequence

1. Executor seam (above).
2. Consumer seam: worker job → gateway → verifier/critic/eval → persisted rows.
3. W7 clean-env dependencies; W8 systemd/TLS/auth/migrations/backup-restore.
4. DeerFlow MCP registration, then W4-B learning.

## Blockers / not claimed

- No production `forge` DB, service unit, TLS/auth, deploy, or publish.
- No real executor; gateway cannot run Craft today.
- No verifier/critic/eval consumer; they are libraries.
- `forge_eval` rows have no route/worker caller yet.
- No DeerFlow MCP registration; no native GUI/CUA bridge beyond the tested Chrome window.
- 4 staging skips require their named services; vision accuracy and learning above L0 unmeasured.
- In-flight tool-call rows have no expiry/recovery policy yet.
