# W3-A Gate 1 — logic-gatekeeper

```json
{
  "phase1": {
    "architecture": "forge_verifier.py is a pure consumer: it reads the artifact bytes/metadata and the gate report; it owns no database and calls no Craft process. The Forge ledger stores the resulting verdict later.",
    "dataFlow": "artifact path -> sha256/PNG IHDR+DPI; report JSON -> checks/applicable/output_sha256; verifier -> named verdict and reason codes -> caller.",
    "edgeCases": [
      "report ok:true but output_sha256 differs from the actual artifact",
      "applicable_checks=0 or every check applicable:false (vacuous gate)",
      "one check with pass:false while top-level ok is true",
      "missing or zero-byte artifact",
      "wrong dimensions or DPI outside tolerance"
    ],
    "rootCause": "The G0 report is treated as evidence only by prose; no code recomputes the artifact hash, checks applicability, or turns a failed/vacuous report into a refusing verdict."
  }
}
```

**Phase 2:** all checks at function entry; missing/malformed inputs return named failure; no caller
changes yet. Rejection is a returned verdict, not an exception swallowed.
