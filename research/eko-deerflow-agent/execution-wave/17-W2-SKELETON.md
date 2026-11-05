# W2 skeleton — local gateway and DDL contract

**Date:** 2026-11-05 · **Status:** W2-A partial; **no service, no production DB, no deploy**.
Gate: `docs/W2-GATE1.md` (logic-gatekeeper Phase 1/2).

## Added

| File | Contents |
|---|---|
| `blueprint/files/forge_gateway.py` | Original 310-line gateway: canonical idempotency key, role/cmd allowlists, realpath roots, replay, refusal classification, verdict ladder |
| `blueprint/files/sql/schema_forge.sql` | 663-line Forge DDL contract: 13 tables, state reference, append-only guards, queue/approval/budget/skill |
| `blueprint/files/tests/test_forge_gateway.py` | 255-line stdlib unittest suite; exact import is `forge_gateway` |

The initial extraction was written as `forge/gateway.py`; the contract test imports
`forge_gateway`, so the file was moved to the top-level module. This is the kind of stale/wiring
mismatch that must be caught before a service imports it.

## Proof

```text
cd /opt/pod-pipeline-staging
.venv/bin/python -m unittest -v tests.test_forge_gateway
Ran 33 tests in 0.003s
OK
```

Covered: same-key replay (executor called once), role/cmd/root refusals, path traversal refusal,
terminal vs retryable refusal, source-mutation rejection, vacuous gate rejection, missing evidence =
unverified, human reject overrides critic pass.

## Not proven / not done

- DDL has **not** been applied to a scratch PostgreSQL, so “apply twice / 18 SQL assertions” is still open.
- No Forge repo/service/queue/lease implementation exists.
- No production `forge` DB/role, no service unit, no publish path.
- W2 gate **G1 is not passed**; this is W2-A only.
- Next: W2-B (repository + DDL apply on scratch PG + queue/lease tests) before any service.

## Non-goals

No change to `pod_pipeline`, `pod` DB, console, storefront, or production.
