# W4-A recon — evaluation and promotion contract

**Target:** pure evaluator for verified episode/golden results plus a *proposal* policy. No model
training, no activation, no production DB.

- **Current:** `forge_eval` table exists in the Forge DDL but code never computes metrics or promotion;
  `agent-learning-loop` remains L0.
- **Entry:** future verifier/critic results -> `evaluate_goldens` -> `propose_promotion`.
- **Data:** golden result `{id, passed, regression}`; metrics rate/LB; candidate decision needs n,
  successes, baseline, regressions and human approval.
- **Tests:** 3/3 is refused; 7/8 with LB > baseline and human approval becomes a *candidate*; no human
  approval refuses; a regression refuses; invalid inputs raise named `ValueError`; failed ids retained.
- **Unknowns:** owner must choose n, baseline p0, false-promotion budget; no A/B or live corpus yet.
- **Files:** `blueprint/files/forge_eval.py`, `tests/test_forge_eval.py`.
- **Non-goals:** no weights, no RL, no activation, no claim that a proposal is learning.
