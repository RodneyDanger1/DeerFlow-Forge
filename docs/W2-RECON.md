# W2 recon — Forge Conductor local skeleton

**Status:** recon only; no W2 source or production edits. Read-only.
Per `forgewright-recon`; gate decision remains in `docs/PLAN-CONTINUATION.md`.

## Target behavior

Add the Forge Conductor’s local skeleton: 13-table `forge` schema, pure tool gateway, 36-edge
transition/refusal/idempotency contract, queue/lease shape, and tests — without a live service,
publisher, or production deployment.

## Entry point

There is no Forge source yet. The contract to implement is:
- `research/eko-deerflow-agent/execution-wave/02-FORGE-SKELETON.md` §3 DDL, §4 transitions,
  §5 idempotency, §6 refusal, §7 gateway, §8 tests.
- Existing DB pattern: `blueprint/files/pod_pipeline/db.py:16` `create_pool`, `:37` `enqueue_run`,
  `:74` `claim_run`, `:103` `recover_stale_runs`, `:127` `start_step`.
- Existing queue worker: `blueprint/files/pod_pipeline/worker.py:28` `drain`, `:69` recovery call.

## Callers

- Console: read-only viewer; must not own Forge state.
- DeerFlow: future task envelope caller; not registered for Forge yet.
- `pod_pipeline`: existing deterministic run path; Forge must not be embedded in it or the console.
- No current caller can invoke Forge; that is expected pre-W2.

## Tests + command

- Python gateway tests: `02` §8.2/§8.5 (`test_forge_gateway.py`), run with the VPS `.venv`
  (`/opt/pod-pipeline-staging/.venv/bin/python`).
- SQL assertions: `02` §8.1, scratch PostgreSQL 16; **not runnable locally without a scratch DB**.
- Existing staging suite: `cd /opt/pod-pipeline-staging && .venv/bin/python -m pytest tests -q`
  → 54 passed, 4 skipped (latest).
- No W2 test command exists in the repo yet.

## Data flow

`TaskEnvelope → spec/role/cmd allowlist → roots → idempotency key → replay or executor → outcome →
classify refusal → store ToolResult → evidence verdict → episode state`.

Failure path: missing evidence → `unverified`; forbidden role/cmd/root → terminal `E_*`; duplicate
key → stored result, zero executor calls.

## Unknowns / evidence still needed

- Scratch PostgreSQL 16 for DDL apply/double-apply; not created (production `pod` must stay untouched).
- Whether the `forge` schema/role may be created on the shared cluster; owner/platform decision.
- Actual Forge service/API shape and queue semantics beyond the skeleton contract.
- G0 execution provenance remains **U** for the independent verifier; W2 gate decision is unresolved.
- No cross-caller contract test exists yet.

## Files I expect to touch (when authorized)

- `blueprint/files/forge_gateway.py` (top-level module; contract test imports `forge_gateway`).
- `blueprint/files/sql/schema_forge.sql`.
- `blueprint/files/tests/test_forge_gateway.py` and SQL assertion harness.
- No `pod_pipeline/`, `src/`, console, or production file.

## Implementation status (after recon)

W2-A gateway/DDL/test files now exist locally and the pure suite is **33/33 on staging**; the DDL
applies twice on scratch PG, **18/18 SQL assertions** pass and two-worker `SKIP LOCKED` completes in
9 ms. The repository/service/worker/lease-reaper remain open. See `execution-wave/17-W2-SKELETON.md`.

## Stop condition

Recon is complete for a **local skeleton**, but implementation is blocked until the owner chooses:
(a) verifier VPS read-only access to close G0 provenance, or (b) explicit conditional acceptance of
Lead-run G0 + artifact consistency. Do not create the `forge` DB/schema or service before that.
