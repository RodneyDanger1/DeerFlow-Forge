# W2-C Gate 1 — logic-gatekeeper

```json
{
  "phase1": {
    "architecture": "ForgeRepo wraps an asyncpg pool and the proven forge SQL functions. ForgeWorker owns claim/execute/finish and lease expiry. ForgeService is a loopback stdlib HTTP wrapper around repo create/get/health. The gateway remains the only policy layer; the service does not call Craft.",
    "dataFlow": "HTTP request -> service validation -> repo -> SQL function/table -> JSON response. Worker: claim_job -> handler(payload) -> finish_job. Expired lease -> SQL requeue in repo.reap_expired_jobs.",
    "edgeCases": [
      "empty queue claim must return None/all-NULL-safe and not finish anything",
      "handler exception must finish failed, not succeeded",
      "expired claimed job must be requeued exactly once, not duplicated",
      "GET unknown episode must return 404/E_EPISODE_NOT_FOUND",
      "malformed JSON / missing idempotency_key must 400 before any insert"
    ],
    "rootCause": "The proven schema and gateway have no production-shaped repository/worker/service seam, so a claimed job cannot be processed, a crashed lease cannot be recovered, and no caller can create/read a Forge episode without ad-hoc SQL."
  }
}
```

**Phase 2 boundary:** service validates at request entry; repo is the only SQL writer; worker finishes
on every path; no Craft execution or production DB.
