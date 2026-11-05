# W2 skeleton — local gateway and DDL contract

**Date:** 2026-11-05 · **Status:** W2-A partial; **no service, no production DB, no deploy**.
Gate: `docs/W2-GATE1.md` (logic-gatekeeper Phase 1/2).

## Added

| File | Contents |
|---|---|
| `blueprint/files/forge_gateway.py` | Original 310-line gateway: canonical idempotency key, role/cmd allowlists, realpath roots, replay, refusal classification, verdict ladder |
| `blueprint/files/sql/schema_forge.sql` | 663-line Forge DDL contract: 13 tables, state reference, append-only guards, queue/approval/budget/skill |
| `blueprint/files/tests/test_forge_gateway.py` | 255-line stdlib unittest suite; exact import is `forge_gateway` |
| `blueprint/files/tests/forge_schema_assertions.py` | 18-check scratch-Postgres assertion harness |
| `blueprint/files/tests/forge_schema_skiplock.py` | two-worker `SKIP LOCKED` concurrency proof |

The initial extraction was written as `forge/gateway.py`; the contract test imports
`forge_gateway`, so the file was moved to the top-level module. This is the kind of stale/wiring
mismatch that must be caught before a service imports it.

## Proof

Gateway:
```text
cd /opt/pod-pipeline-staging
.venv/bin/python -m unittest -v tests.test_forge_gateway
Ran 33 tests in 0.003s
OK
```

DDL on a throwaway `postgres:16-alpine` container (`forge-pg-test`, tmpfs, port 55439):
```text
psql -v ON_ERROR_STOP=1 -f schema_forge.sql   # applied twice: 13 tables / 36 transitions
FORGE_TEST_DSN=… .venv/bin/python tests/forge_schema_assertions.py
PASS T01–T18
RESULT pass=18 fail=0

FORGE_TEST_DSN=… .venv/bin/python tests/forge_schema_skiplock.py
PASS T-SKIPLOCK distinct jobs=1,2 elapsed_ms=9
```

Covered: DDL counts; legal/illegal/terminal transitions; event chain and append-only; forged-event
detection; duplicate episode/tool keys; job claim/lease/finish/empty; append-only trigger census;
budget cap rollback; approval single-use; zero-byte artifact; one-active-skill; and two-worker
`SKIP LOCKED` (9 ms, distinct jobs). The scratch container was removed after the run.

**Wiring defect found and fixed:** `forge_claim_job` / `forge_claim_handoff` returned an all-NULL
composite record instead of SQL NULL when empty; the functions now `RETURN NULL` explicitly and the
test helper treats a composite NULL as empty. Without this, a caller could believe it claimed a job
with a NULL id.

## Not proven / not done

- No Forge repository, service API, worker loop, lease reaper, or production `forge` DB/role exists.
- The 18 SQL assertions and `SKIP LOCKED` proof use a throwaway container; no migration path or
  production apply has been exercised.
- No service unit, status endpoint, or publish path.
- W2 gate **G1 is not fully passed**: DDL/queue contracts are proven; repository/service is not built.
- Next: repository seam + worker/lease loop + service API, then G1 review.

## Non-goals

No change to `pod_pipeline`, `pod` DB, console, storefront, or production.
