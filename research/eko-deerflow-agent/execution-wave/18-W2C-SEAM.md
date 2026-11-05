# W2-C — repository, worker and loopback service seam

**Date:** 2026-11-05 · **Status:** local source + tests; **no deployment, no production DB**.
Recon: `docs/W2C-RECON.md` · Gate: `docs/W2C-GATE1.md`.

## Added

| File | Purpose |
|---|---|
| `blueprint/files/forge_repo.py` | asyncpg repository: health, episode create/get, transition, event append, job create/claim/finish, expired-lease requeue |
| `blueprint/files/forge_worker.py` | one claim → handler → truthful finish; failure records failed; drain stops on empty |
| `blueprint/files/forge_service.py` | loopback-only stdlib HTTP service: `/healthz`, `POST /v1/episodes`, `GET /v1/episodes/{id}` |
| `blueprint/files/tests/test_forge_repo.py` | 3 scratch-Postgres tests (skipped without DSN) |
| `blueprint/files/tests/test_forge_worker.py` | 4 fake-repository worker tests |
| `blueprint/files/tests/test_forge_service.py` | 4 fake-repository loopback HTTP tests |

## Proof

```text
# local worker + service (no DB)
python -m unittest -v tests.test_forge_worker tests.test_forge_service
Ran 8 tests ... OK

# scratch PostgreSQL 16 container, schema applied, then removed
FORGE_TEST_DSN=… python -m unittest -v tests.test_forge_repo
Ran 3 tests ... OK
  - episode create/get + job claim/finish
  - expired lease requeued exactly once; second reap returns 0
  - unknown episode returns None

# full staging suite
pytest tests -q
95 passed, 7 skipped
```

The 7 skips include the 4 pre-existing DB-dependent tests plus the 3 repository tests when no
`FORGE_TEST_DSN` is set. They are skipped, not passed.

## Defects found and fixed

1. `forge_repo.create_episode/create_job/append_event` passed Python dicts to `jsonb`; asyncpg
   requires serialized JSON. Now uses `json.dumps`.
2. The service initially used `asyncio.run` per request, which cannot share an asyncpg pool bound to
   another loop. It now owns one service event loop (`_Loop`) shared by request threads.
3. The repository test expected `None` from a second reap; the contract correctly returns `0` after
   the first requeue. The assertion was corrected; code was not weakened.

## Not done / unverified

- `ForgeService` is proven only with a fake repository. It has **not** been wired to `ForgeRepo` in
  the same event loop, so real HTTP→DB behavior is unverified.
- Lease reaper is a manual `reap_expired_jobs()` call; no periodic reaper process.
- No service unit/systemd, no auth, no production `forge` DB/role, no deployment.
- W2 gate **G1 is not fully passed**: repository/worker/service seams exist and are locally tested;
  service→real repository integration and deployment are open.
- No Craft execution or publish path is exercised by these modules.
