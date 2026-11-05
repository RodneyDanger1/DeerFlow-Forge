# W4-A — evaluation and promotion contract

**Date:** 2026-11-05 · **Scope:** pure local evaluator/proposer. **No model training, no activation,
no production DB.** Recon: `docs/W4A-RECON.md` · Gate: `docs/W4A-GATE1.md`.

## Added

- `blueprint/files/forge_eval.py` — Wilson lower bound, golden evaluation, promotion **proposal**.
- `blueprint/files/tests/test_forge_eval.py` — 13 tests.

## Rules enforced

- Wilson 95% lower bound is computed, not guessed. `3/3 = 0.4385`, so the old “3 successes” rule cannot
  promote under a >0.60 threshold.
- Candidate policy inputs: `n >= min_n` (default 8), `successes >= min_successes` (default 7),
  `LB > baseline`, zero regressions, and **human approval**.
- Every refusal has a named reason: `E_EVAL_SAMPLE_TOO_SMALL`, `E_EVAL_TOO_FEW_SUCCESSES`,
  `E_EVAL_BELOW_BASELINE`, `E_EVAL_REGRESSION`, `E_EVAL_HUMAN_REQUIRED`.
- A passing result is `promote_candidate` with `active:false`; this module never flips a skill pointer.

## Proof

```text
python -m unittest -v tests.test_forge_eval
Ran 13 tests ... OK

pytest tests -q   # scratch PostgreSQL + G0 bundle
139 passed, 4 skipped
```

Key checks: 3/3 refused for sample size; 8/8 without human refused; 8/8 with human a candidate only;
7/8 can clear baseline 0.5; 6/8 refused; baseline 0.7 refuses 8/8; any regression refuses.

## Not done / unverified

- **No learning claim.** Module computes/proposes only; no retrieval, A/B, promotion activation, or
  rollback drill.
- Horizon (n=8, k≥7, p0) is a **simulation-derived suggestion**, not an owner-adopted policy.
- No real episode corpus/goldens, no live model evaluation, no persistence of candidate skill rows.
- No production service/DB.
