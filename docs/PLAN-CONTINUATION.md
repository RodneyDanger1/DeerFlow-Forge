# Plan continuation — DeerFlow Forge (2026-11-05)

**Status:** W1 (tool-call idempotency persistence), W5 (eval-row persistence), stale in-flight
recovery, and the first half of the executor seam (registered process executor) are implemented and
tested. The console is **deployed and live on the VPS**, with 22/22 live black-box checks and CUA native
evidence. **No production Forge DB/service, no Craft registry, and no consumer pipeline yet.**

Verified by command: console **65/65**; Forge local **132 passed / 15 skipped**; staging
**186 passed / 4 skipped**; gateway **36/36**; SQL **18/18**; browser controls **22/22 live checks**;
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
  `E_IDEMPOTENCY_IN_FLIGHT`. **W1 tests: 5 real-PostgreSQL tests + 36 gateway unit tests.**
- Repository: `ForgeRepo.transition()` appends exactly one event; jobs/leases/reaper tested.
  `ForgeGatewayRepo.abandon_stale_in_flight()` is an explicit, deadline- and limit-bounded operator
  recovery; it marks old in-flight rows failed and later calls replay `E_IDEMPOTENCY_STALE`. It is not
  an automatic daemon.
- Executor: `forge_executor.ProcessExecutor` validates absolute binaries at registration, builds argv
  without a shell, runs in an explicit work root with a bounded timeout, captures bounded stderr,
  hashes artifacts, and fails on required-missing artifacts. **7/7 tests.**
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
3. **Stale in-flight recovery is explicit, not automatic.** `abandon_stale_in_flight(older_than_s,
   limit)` marks old in-flight rows failed with `E_IDEMPOTENCY_STALE`; it never re-executes. A later
   daemon may call it on a schedule after the owner chooses a deadline.
4. **Process executor owns work-root execution** and hashes artifacts after success. It is registered
   by `(tool_id, cmd_id)` and does not know Craft semantics; a Craft registry is still required.
5. **Service remains loopback-only.** No auth/TLS claim until W8.
6. **Console remains a viewer.** No fake run/backend control.
7. **No learning claim.** L0 remains until retrieval/A-B/promotion/rollback exist.

## Completed in this increment

| Item | File | Evidence |
|---|---|---|
| W1 async gateway + persisted repo | `forge_gateway.py`, `forge_repo.py` | 36 gateway tests; 3 real-PG tests: success/replay one row, in-flight refusal, executor-crash failed row |
| W1 atomic in-flight before executor | `ForgeGatewayRepo.begin` | unique-key `ON CONFLICT DO NOTHING`; row inspected after execute |
| W1 replay context | `ToolResult` episode/tool/cmd/params/argv/duration | replay assertions |
| Stale in-flight recovery | `ForgeGatewayRepo.abandon_stale_in_flight` | 2 real-PG tests: old row→failed/replay; fresh row untouched |
| Process executor (first half) | `forge_executor.py` | 7/7 tests: absolute binary, hash, timeout kill, missing artifact, unknown command, registration refusal |
| W5 eval row writer | `ForgeRepo.record_eval` | baseline+memory rows; duplicate `E_EVAL_EXISTS`; invalid arm `ValueError`; missing episode `E_EPISODE_NOT_FOUND` |
| Full suite | staging | **186 passed, 4 skipped** in 16.30 s |
| Local suite | `unittest` | **132 passed, 15 skipped** |
| VPS console | live deployment | 22/22 checks + CUA evidence |
| Docs | README, capability matrix, this plan | current, with historical files retained |

## Next: Craft registry (second half of executor seam)

**Outcome:** one real Craft tool call runs on a copy through an absolute-path binary, produces a real
artifact, and returns a persisted `ToolResult`; an absent engine refuses by name.

**Done first half:** `forge_executor.py` provides absolute-binary validation, argv templates, timeout,
bounded output, artifact hashing and named refusals; 7/7 tests.

**Remaining files:** a Craft command registry (tool/cmd → absolute binary + argv template + artifact
globs), a `--version` probe for each registered binary, and one worker job kind.

**Rules:** no bare names/PATH shims; explicit roots; copy inputs into a scratch directory; absent
DesignCraft/EffectCraft/FilmCraft refuses by name; no model-reported success.

**Tests:** a real VectorCraft/PhotoCraft trace command in a scratch directory; absent engine →
`E_TOOL_NOT_INSTALLED`; timeout → killed process; artifact SHA recorded. **Rollback:** remove registry;
generic executor stays.

**Out of scope:** production DB/service, publish, DeerFlow, autonomous promotion.

## Next: consumer seam

Wire gateway → executor → verifier/critic/eval in one worker job, persisting `forge_tool_call`, artifact,
gate/critique and eval rows. Acceptance: one job produces evidence rows with hashes, and a failed gate
produces a named refusal—not a success. Do not claim this until the Craft registry is real.

## Remaining sequence

1. Craft registry + version probe (second half of executor seam).
2. Consumer seam: worker job → gateway → verifier/critic/eval → persisted rows.
3. W7 clean-env dependencies; W8 systemd/TLS/auth/migrations/backup-restore.
4. DeerFlow MCP registration, then W4-B learning.

## Blockers / not claimed

- No production `forge` DB, service unit, TLS/auth, deploy, or publish.
- Generic process executor exists, but **no Craft registry**; Craft cannot execute through it yet.
- No verifier/critic/eval consumer; they are libraries.
- `forge_eval` rows have no route/worker caller yet.
- Stale in-flight recovery is manual (no scheduled daemon).
- No DeerFlow MCP registration; no native GUI/CUA bridge beyond the tested Chrome window.
- 4 staging skips require their named services; vision accuracy and learning above L0 unmeasured.
