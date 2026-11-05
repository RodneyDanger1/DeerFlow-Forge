# W4-A Gate 1 — logic-gatekeeper

```json
{
  "phase1": {
    "architecture": "forge_eval.py is a pure calculator/proposer. Episode evidence stays in ForgeRepo/DB; no model and no pointer write here. A human/owner remains the promotion authority.",
    "dataFlow": "golden results -> validate -> pass/fail counts + regression -> Wilson LB; candidate policy inputs -> proposal verdict (never activation).",
    "edgeCases": [
      "3/3 successes: Wilson LB 0.4385, cannot satisfy a >0.60 rule",
      "n below declared minimum: refuse E_EVAL_SAMPLE_TOO_SMALL",
      "LB below baseline: refuse E_EVAL_BELOW_BASELINE",
      "any regression: refuse E_EVAL_REGRESSION",
      "missing human approval: refuse E_EVAL_HUMAN_REQUIRED"
    ],
    "rootCause": "There is no executable evaluation/promotion contract, so the old 3/3 rule can be mistaken for evidence and a candidate cannot be refused by a named policy."
  }
}
```

**Phase 2:** validation at function entry; every refusal is named; a passing proposal is explicitly
`candidate`, never active.
