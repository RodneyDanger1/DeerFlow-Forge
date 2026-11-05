# W2 Gate 1 — logic-gatekeeper

**Change:** add the local Forge skeleton (schema + gateway + tests). No service, no production DB, no publish.

```json
{
  "phase1": {
    "architecture": "New blueprint/files/forge package holds the pure gateway; sql/schema_forge.sql holds the 13-table contract; tests/test_forge_gateway.py proves it. The service/worker/DB wiring is NOT part of this change. Existing pod_pipeline DB/worker patterns are reference only.",
    "dataFlow": "TaskEnvelope/episode -> ToolCall (role, cmd_id, params, paths, input hashes) -> spec/role/cmd allowlist -> realpath roots -> canonical idempotency key -> replay lookup -> executor -> outcome -> terminal/retryable refusal classification -> stored ToolResult -> evidence verdict -> episode state. Untrusted input enters at ToolCall; no Craft CLI or network is called by the gateway.",
    "edgeCases": [
      "same idempotency key twice must call the executor once and return the stored result",
      "role not in ToolSpec.allowed_roles must return a named refusal without executing",
      "cmd_id not in the exact allowlist must refuse (no prefix wildcard)",
      "path containing '..' or outside roots must refuse after realpath, before execution",
      "missing process/artifact/gate evidence must produce unverified, not accepted"
    ],
    "rootCause": "The Forge control plane has no executable gateway or schema in the deployable tree, so its idempotency, root confinement, refusal and transition contracts cannot be tested or called by any future service."
  }
}
```

**Phase 2 boundary:** all policy checks run at `Gateway.execute` entry, before `Executor.run`; the
executor is a protocol/test double at this stage. No production caller is changed.
