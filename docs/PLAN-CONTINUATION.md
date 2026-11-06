# Plan continuation — DeerFlow Forge (2026-11-05)

**Status:** W1, W5, stale in-flight recovery, the registered/version-probed Craft executor, a real
VectorCraft trace through gateway → PostgreSQL, the consumer, and a real `forge_worker` job handler with
kind guard are complete. The next work is artifact/gate/critique/eval evidence adapters, PhotoCraft live
trim, and the service route. **No production Forge DB/service and no publish.**

Verified by command: console **65/65**; Forge local **154 passed / 16 skipped**; staging
**207 passed / 5 skipped**; gateway **36/36**; SQL **18/18**; browser controls **22/22 live checks**;
keyboard/a11y **8/8**. Receipts: `docs/TRACE/2026-11-05/GATE-FINAL-W2.md`,
`docs/TRACE/2026-11-05/LIVE-VPS-VERIFICATION.md`, `docs/CAPABILITY-MATRIX.md`.

## Outcome

Forge can persist/replay a tool call, execute a registered Craft command, accept a worker payload through
the consumer, and run it as a real guarded worker job. The next increment adds artifact, gate, critique
and eval evidence rows, proves PhotoCraft, and exposes the service route.

## Current behavior (evidence)

- Gateway: `Gateway.execute()` is async; `ForgeGatewayRepo` inserts an `in_flight` row before execution,
  updates a terminal row after, and replays terminal results. A concurrent duplicate raises
  `E_IDEMPOTENCY_IN_FLIGHT`. **W1 tests: 5 real-PostgreSQL tests + 36 gateway unit tests.**
- Repository: `ForgeRepo.transition()` appends exactly one event; jobs/leases/reaper tested.
  `ForgeGatewayRepo.abandon_stale_in_flight()` is an explicit, deadline- and limit-bounded operator
  recovery; it marks old in-flight rows failed and later calls replay `E_IDEMPOTENCY_STALE`. It is not
  an automatic daemon.
- Executor: `forge_executor.ProcessExecutor` validates absolute binaries at registration, builds argv
  without a shell, runs in an explicit work root with bounded timeout, captures bounded stderr, hashes
  artifacts, and fails on required-missing artifacts. **8/8 tests.**
- Craft registry: `forge_craft_registry` binds the measured VectorCraft 0.21.1 and PhotoCraft 0.20.2
  command lines to absolute binaries, probes `--version`, and refuses drift/missing binaries. **The real
  VPS probe passes; a real VectorCraft trace through the gateway produced 2 artifacts and replayed from
  PostgreSQL without re-execution.**
- Evaluation persistence: `ForgeRepo.record_eval()` validates arm/verdict/human/reviewer, inserts into
  `forge_eval`, maps unique conflicts to `E_EVAL_EXISTS`, and maps missing episodes to
  `E_EPISODE_NOT_FOUND`. **Real-PG test covers both arms, duplicate, invalid arm, missing episode.**
- Service: loopback `/healthz` and create/get episode only; no tool-call or eval route.
- Worker: `python -m forge_worker --once`; guarded finish and optional `--kind` guard. A wrong-kind job
  fails with `E_JOB_KIND` before the handler runs. `forge_tool_job:handle` builds the real repo,
  registry, gateway and consumer from `FORGE_DSN` + `FORGE_WORK_ROOT`; a real job completed and wrote
  one tool-call row plus 2 artifacts.
- Consumer: `forge_consumer.ToolCallConsumer` validates `episode_id`/`tool_id`/`cmd_id`/`params`/paths/
  hashes, maps payload to `ToolCall`, executes through the gateway, and raises named `ConsumerError` for
  refused/failed calls. **7/7 tests; live Craft trace also passes through the consumer.**
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
4. **Process executor and Craft registry own work-root execution.** The registry is data plus version
   evidence; the executor hashes artifacts after success and refuses absent/drifted binaries.
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
| Process executor | `forge_executor.py` | 8/8 tests: absolute binary, hash, timeout kill, missing artifact, token expansion, version probe, registration refusal |
| Craft registry + real trace | `forge_craft_registry.py` | VPS probe VectorCraft 0.21.1 / PhotoCraft 0.20.2; real gateway trace: 2 artifacts, persisted, replayed without re-execution |
| W5 eval row writer | `ForgeRepo.record_eval` | baseline+memory rows; duplicate `E_EVAL_EXISTS`; invalid arm `ValueError`; missing episode `E_EPISODE_NOT_FOUND` |
| Consumer first half | `forge_consumer.py` | 7/7 tests: payload validation, success result, refused/failed errors, worker finish truth; live Craft trace via consumer passes |
| Worker job + kind guard | `forge_tool_job.py`, `forge_worker.py` | real CLI job: `--kind forge.tool_call` succeeded, 1 tool row, 2 artifacts; wrong kind failed `E_JOB_KIND`, 0 tool rows; 4 config tests + 2 worker tests |
| Full suite | staging | **207 passed, 5 skipped** in 16.30 s |
| Local suite | `unittest` | **154 passed, 16 skipped** |
| VPS console | live deployment | 22/22 checks + CUA evidence |
| Docs | README, capability matrix, this plan | current, with historical files retained |

## Next: evidence adapters + PhotoCraft + service (decision-complete)

**Done consumer path:** payload validation → `ToolCall` → gateway → registered Craft executor →
persisted tool call, invoked by a real `forge_worker --once --kind forge.tool_call` job.

**Remaining:**
1. **Artifact/gate/critique/eval adapters:** after a successful tool result, verify each artifact by
   path/hash; persist gate evidence; critic stays `unverified` without a model; write `record_eval`
   rows for the configured arms. A failed gate must finish the job failed with a named code.
2. **PhotoCraft live trim:** run the registered trim on the G0 retouch input; verify PNG dimensions/DPI
   and hash. Do not claim the command works until this passes.
3. **Scheduled stale recovery:** choose a deadline and invoke `abandon_stale_in_flight` from a bounded
   daemon (not an unbounded loop).
4. **Service `/v1/tool-calls`:** add only after the worker path and evidence adapters exist; loopback-only.

**Tests:** worker job writes artifact/gate/critique/eval rows; failed gate → job failed; PhotoCraft trim
produces a valid PNG; duplicate payload replays without re-execution; malformed payload fails
`E_REQUEST_INVALID`. **Rollback:** remove adapters/job handler; gateway/executor stay.

**Out of scope:** production service, TLS/auth, DeerFlow registration, publish, autonomous promotion.

## Remaining sequence

1. Evidence adapters + PhotoCraft live trim.
2. Service `/v1/tool-calls` after the worker path is complete.
3. Scheduled stale recovery.
4. W7 clean-env dependencies; W8 systemd/TLS/auth/migrations/backup-restore.
5. DeerFlow MCP registration, then W4-B learning.

## Blockers / not claimed

- No production `forge` DB, service unit, TLS/auth, deploy, or publish.
- Worker handler is selected by CLI (`--handler`), not a code-level kind→handler registry; one handler is
  configured per worker invocation.
- No verifier/critic/eval adapter writes rows after a tool call.
- `forge_eval` rows have no route/worker caller yet.
- PhotoCraft registry registered/probed but no live PhotoCraft command proven yet.
- Stale in-flight recovery is manual (no scheduled daemon).
- No DeerFlow MCP registration; no native GUI/CUA bridge beyond the tested Chrome window.
- 5 staging skips (4 services + opt-in live Craft off by default); vision accuracy and learning above L0
  unmeasured.
