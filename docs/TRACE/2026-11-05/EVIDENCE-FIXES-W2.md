# Wave 2 — Evidence Contract Fixes (PARTIAL)

**Task:** `task-29` (revision 3, `learning-loop-researcher`) · **Date:** 2026-11-05 16:5x America/Chicago
**Status:** **PARTIAL** — fixes + tests complete and green; the RED leg was not captured separately before the hard stop (see §4).
**Gate:** Phase 1 approved by Lead (invalid human/gate_ok, PNG/DPI, duplicate goldens).
**Scope:** only `blueprint/files/forge_critic.py`, `forge_verifier.py`, `forge_eval.py` and their three tests; no production or other docs edits.

## 1. Root cause (approved Phase 1)

Each evidence contract under-constrained one input: `human` was not an enum, `gate_ok` was type-confused, the artifact format and y-DPI were unverified, golden IDs were not unique, and `successes + regressions > n` was accepted. Invalid evidence could therefore reach `pass`/`promote_candidate` or be double-counted.

## 2. Changed files and fixes

| File | Change |
|---|---|
| `forge_critic.py:82-91` | `combine`: proceed only when `gate_ok is True`; other non-`None` values → `unverified / E_GATE_INVALID`; `human` must be `None|accept|reject`, otherwise `unverified / E_HUMAN_INVALID`. |
| `forge_verifier.py:32-60` | `inspect_png`: capture `img.format`; reject non-PNG with `E_ARTIFACT_FORMAT`; read both DPI axes (`dpi_x`,`dpi_y`), keeping `dpi` as x for callers. |
| `forge_verifier.py:118-126` | `verify_artifact`: require both axes present and both within `dpi_tolerance` of `expected_dpi`; anisotropic evidence → `E_DPI_MISMATCH`. |
| `forge_eval.py:28-43` | `evaluate_goldens`: reject duplicate `id` with `E_EVAL_DUPLICATE_ID` (would inflate `n`). |
| `forge_eval.py:70-71` | `propose_promotion`: raise `E_EVAL_INVALID` when `successes + regressions > n`. |
| `tests/test_forge_critic.py` | +2 regression tests: unknown human value, non-bool `gate_ok`. |
| `tests/test_forge_verifier.py` | +3 regression tests: JPEG-with-.png rejected, anisotropic DPI rejected, matching DPI still passes (positive control). |
| `tests/test_forge_eval.py` | +2 regression tests: duplicate id rejected, `successes+regressions>n` rejected; re-pinned `test_regression_refuses` (OLD 8/8+1 regression = impossible evidence → NEW 7/8+1, with OLD→NEW comment). |

## 3. Tests run (VERIFIED)

Command (from `blueprint/files/tests`, `PYTHONPATH=..`):

```
python -m unittest -q test_forge_critic test_forge_eval test_forge_verifier
```

Observed: `Ran 35 tests in 0.053s` → `OK` → **exit 0**.

Intermediate failure found and fixed: `test_regression_refuses` used `successes=8, n=8, regressions=1`, which the new sanity check correctly rejects as impossible (9 outcomes for n=8). The test encoded the old contradiction; it was re-pinned to `successes=7, n=8, regressions=1` and passes.

## 4. RED → GREEN status

| Leg | Status |
|---|---|
| GREEN (new + existing suites) | **VERIFIED** — 35 tests OK, exit 0 |
| RED (new tests failing on old code before fix) | **UNVERIFIED** — hard stop arrived before a separate RED run; fixes were applied in the same window. The new tests assert the corrected closed behavior and target exactly the old return values (`pass`, `E_EVIDENCE_AGREES`, full-format pass, x-only DPI pass, `n=2` duplicate count), so they are regression pins, but no RED transcript exists. |

## 5. Not done / unverified

- RED transcript (above) — would be produced by `git stash`-free byte restore of the three modules and re-running the seven new tests.
- Full repo suite and `py_compile` of downstream callers not run (timebox).
- `test_forge_verifier.VerifierTests` depends on `research/.../execution-wave/g0`; if absent those cases skip (not separately counted in the -q output).
- No model/vision accuracy claim; no production behaviour exercised.
