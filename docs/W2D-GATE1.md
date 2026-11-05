# W2-D Gate 1 — logic-gatekeeper

```json
{
  "phase1": {
    "architecture": "ForgeRepo owns an asyncpg pool bound to exactly one event loop. ForgeService currently creates a private loop but receives a repo created on the caller's loop, so a real pool would be used from the wrong loop. ForgeWorker owns claim/finish; LeaseReaper owns periodic expired-lease requeue.",
    "dataFlow": "HTTP request thread -> service _Loop -> repo coroutine -> asyncpg pool -> SQL -> JSON. Reaper -> repo.reap_expired_jobs -> queued job. Worker -> claim -> handler -> finish.",
    "edgeCases": [
      "service started with a real DSN must create its repo on its own loop, not the caller's",
      "a repo pool closed on the wrong loop must fail rather than appear healthy",
      "reaper exception must be logged and the loop must continue; it must not stop silently",
      "reaper must not requeue a job whose lease is still live",
      "HTTP create with duplicate idempotency key must return a named conflict, not a 500"
    ],
    "rootCause": "The service and repository use different event loops, so the seam is untested and a real asyncpg pool cannot be shared safely; the lease reaper is also only a manual method, so expired jobs are never recovered automatically."
  }
}
```

**Phase 2 boundary:** service creates its repo through an injected async factory on its own
loop; HTTP input remains validated at entry; worker/reaper never call Craft; no production DB.
