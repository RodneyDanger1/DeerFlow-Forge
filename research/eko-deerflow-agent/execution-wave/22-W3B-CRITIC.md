# W3-B — blind critic contract and verdict resolver

**Date:** 2026-11-05 · **Scope:** contract only; **no vision model called**, no production.
Recon: `docs/W3B-RECON.md` · Gate: `docs/W3B-GATE1.md`.

## Added

| File | Purpose |
|---|---|
| `blueprint/files/forge_critic.py` | validate blind critique JSON; resolve gate × critic × human into final verdict |
| `blueprint/files/tests/test_forge_critic.py` | 14 tests, no network/model |

## Enforced contract

- verdict is one of `pass/fail/needs_human/unverified`;
- every dimension has a non-empty name, 1–5 score, positive `[x,y,w,h]` crop, observation and severity;
- defects have a known kind, positive crop and severity;
- confidence is 0–1, `model_id`/`prompt_version` are present, `unseen` is a list;
- a critique mentioning exit codes, gate reports/values, operator claims or `pass:true` is rejected as
  non-blind (`E_CRITIC_BLINDED`);
- `pass` with a major defect and `fail` with no defects are contradictions;
- a failed gate **always** wins over a passing critic;
- gate pass + critic fail → `needs_human` (`E_CRITIC_DISAGREES`);
- missing gate/critic → `unverified`, never pass;
- human reject → `needs_human`.

## Proof

```text
python -m unittest -v tests.test_forge_critic
Ran 14 tests ... OK

# full staging suite with scratch PostgreSQL and G0 bundle mounted
pytest tests -q
126 passed, 4 skipped
```

The 4 skips are the pre-existing DB-dependent tests outside the Forge scratch DSN.

## Not done / unverified

- **No vision model was run.** `deepseek-flash` vision accuracy and false-pass rate remain unmeasured;
  no ≥50 labelled defect set was executed.
- No human rubric/approval UI.
- Critic JSON is not persisted to `forge_critique` yet.
- No production service integration.
- A critic can still be wrong; this module enforces structure/blinding/disagreement, not visual truth.
