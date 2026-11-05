# W2-C recon — repository, worker/lease, service

**Status:** recon/gate only until the code below is proven. No production change.

## Target behavior

Expose a durable repository seam over the proven `forge` schema, a worker that claims one job at a
time and returns it to the queue when a lease expires, and a loopback service that creates/reads
episodes without touching the console or `pod_pipeline`.

## Entry points / callers

- Existing gateway: `blueprint/files/forge_gateway.py:241` `Repo` protocol, `:261` `Gateway`.
- Schema functions: `forge_claim_job` (line 464), `forge_finish_job` (492),
  `forge_transition_episode` (150), `forge_append_event` (229), `forge_replay_tool_call` (359).
- Existing worker pattern: `pod_pipeline/worker.py:28` `drain`, `:69` `recover_stale_runs`.
- No Forge service exists; no console caller should be added.

## Data flow

`service request -> ForgeRepo -> SQL function/table -> job claim -> worker handler -> finish_job ->
episode/event -> response`. Failure path: expired lease -> requeue; handler exception -> failed job;
unknown episode -> named 404/E_EPISODE_NOT_FOUND.

## Tests

- Pure worker tests with a fake repo: claim/process/finish, empty queue, handler failure.
- Repository tests against a disposable PostgreSQL 16 container: create episode, claim/finish job,
  expired-lease requeue, no duplicate claim.
- Service tests on an ephemeral loopback port with a fake repo; health and 404.
- No production DB/container; scratch container removed after run.

## Unknowns

- Lease reaper interval and retry/abandon policy (not specified in the skeleton).
- Service auth model; loopback only for now.
- Whether to expose job claim over HTTP or keep it worker-internal. Default: worker-internal; HTTP
  service is episode read/create only.

## Implementation status (after recon)

W2-C repository/worker/service files now exist locally. Worker+service: **8/8** fake-repo tests;
repository: **3/3** scratch-Postgres tests; full staging: **95 passed, 7 skipped**. Service→real
repository wiring, periodic reaper and deployment remain unverified. See `18-W2C-SEAM.md`.
