# Lease reaper terminal-state gate

```json
{
  "phase1": {
    "architecture": "forge_job.state holds queued/claimed/running/succeeded/failed/abandoned; attempts and max_attempts bound retries. ForgeRepo.reap_expired_jobs is the only recovery writer.",
    "dataFlow": "expired claimed/running job -> reaper UPDATE -> queued (retry available) or abandoned (attempts >= max_attempts) -> worker claim only sees queued.",
    "edgeCases": [
      "job at attempts=max_attempts expires -> must become abandoned, not queued",
      "job below max_attempts expires -> queued and claimable once",
      "reaper runs twice -> second pass changes nothing",
      "abandoned job must never be claimed"
    ],
    "rootCause": "The reaper releases every expired lease back to queued without checking attempts/max_attempts, so a permanently failing job can cycle forever and consume worker slots."
  }
}
```

**Phase 2:** the reaper is the boundary; it sets terminal `abandoned` when the attempt cap is reached and leaves a named error.
