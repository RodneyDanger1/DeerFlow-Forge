# Wave 1 — Evidence / Verifier / Eval Audit (READ-ONLY)

**Date:** 2026-11-05 16:21–16:35 America/Chicago
**Seat:** `learning-loop-researcher` (evidence/verifier/eval) · **Task:** `task-22`
**Scope:** `blueprint/files/forge_verifier.py`, `forge_critic.py`, `forge_eval.py`, and the tests named in `blueprint/files/tests/`.
**Mode:** read-only. No source/doc edit, commit, deploy, or production access. Only file written: this report.
**Persona/skills:** senior coding engineer; `/agent-learning-loop`, `/truthseeker`, `/evidence-check`. `/forgewright-*` baseline not run: this wave touches no code (read-only), so the "when code is touched" precondition is not met.
**Non-claims:** no vision-accuracy claim, no claim above learning level L0, no claim that any model/gate/critic is accurate. Accuracy requires a run; no model or Craft process was executed.

## Evidence labels

| Label | Meaning |
|---|---|
| `RAN` | Command executed in this session; output quoted. |
| `STATIC` | Confirmed by reading the cited lines and tracing the control flow; not executed. |
| `UNVERIFIED` | Not established; probe missing (e.g., pytest unavailable). |

## 1. Files and recomputed hashes (RAN, PowerShell `Get-FileHash`)

| File | Lines | SHA-256 |
|---|---|---|
| `forge_verifier.py` | 137 | `44970DC3CABF65B814444A9A0B0538432D29248C35E1E4B0466C4C7685CC40E3` |
| `forge_critic.py` | 102 | `87A1B7AF42E8CF440B81025DC23ECD825C16A058FAF3BDCA30503301636E2766` |
| `forge_eval.py` | 83 | `BECD2A3E1DC0343D04613930D572F3749DC2F831EDC797FDFEFDBDCE90447FCD` |

Tests present but not read in full (timebox): `tests/test_forge_verifier.py`, `tests/test_forge_critic.py`, `tests/test_forge_eval.py`; also `test_forge_e2e.py`, `test_forge_gateway.py`, `test_forge_service.py`, `test_forge_repo.py`, `test_forge_worker.py`, `forge_schema_assertions.py`.

## 2. Algorithm checks

### 2.1 Wilson lower bound (RAN)

`forge_eval.py:12-21` implements the standard Wilson score lower bound with default `z = 1.96` (line 12). Recomputation against an independent implementation (`z = 1.959964`):

| k/n | forge_eval (z=1.96) | reference (z=1.959964) | delta |
|---|---|---|---|
| 3/3 | 0.438494 | 0.438492 | +2e-6 |
| 8/8 | 0.675584 | 0.675584 | 0 |
| 9/10 | 0.595844 | 0.595772 | +7.2e-5 |
| 19/20 | 0.763864 | 0.763864 | 0 |

**Finding A1 (Info, not a defect):** the formula is correct and matches the standard definition; the only divergence is the truncated `z=1.96` default, which makes the bound optimistic by ≤7.2e-5 at these sizes. Practically irrelevant; if exact 95% is claimed, prefer `1.959963984540054` and say so.

### 2.2 Applicable-check counting (`forge_verifier.py:69-84`, STATIC)

- `applicable` = every check whose `applicable` value is **not exactly `False`** (line 69-70). A missing, `null`, `0`, or `"false"` marker counts as applicable. Fail direction is safe for a `pass` check (it must be `is True`), but `applicable_checks` arithmetic can be surprising; document the exact rule.
- `failed` requires `pass is True` (line 71-73); `len(applicable) == 0` → `E_GATE_VACUOUS` (line 78-79). Fail-closed. No defect beyond documentation.

### 2.3 Golden aggregation (`forge_eval.py:24-53`, STATIC)

- `n`, `passed`, `regressions` are recomputed from rows; `rate = passed/n`, `wilson_lower` from `passed/n`. Arithmetic is consistent.
- **Defect D1 (Medium):** duplicate `id` values are silently accepted (no uniqueness check, lines 30-43). Two rows with `id="g"` count as `n=2`, inflating `n` and the Wilson bound. Fix: reject duplicates with `E_EVAL_DUPLICATE_ID`.

### 2.4 Promotion policy (`forge_eval.py:56-83`, STATIC)

- This implements the **calibrated** horizon from execution-wave task-11 (`min_n=8`, `min_successes=7`, `LB > baseline`, regressions 0, human required) and never activates (`active: False`, line 59/72). Consistent with the honest policy; the parameters are a simulation-derived suggestion, not an adopted policy (state this wherever the module is surfaced).
- **Defect D2 (Low):** `successes + regressions <= n` is not enforced. `propose_promotion(successes=8, n=8, regressions=1)` is impossible evidence but passes the line-68 check (`regressions > n` only). Fix: also require `successes + regressions <= n`.
- **Defect D3 (Low):** `baseline` is validated only by `0 <= baseline <= 1` (line 60-61). `True` is accepted as `1`; a string raises a bare `TypeError` instead of a named `E_EVAL_INVALID`. Fix: `isinstance(baseline,(int,float)) and not isinstance(baseline,bool)`.

## 3. Verifier checks (`forge_verifier.py`, STATIC unless marked)

- `inspect_png` (22-51): file existence, readability, non-empty, PIL open, size, `dpi` (`tuple[0]` or scalar), sha256 of bytes. Good fail-closed ordering.
- **Defect D4 (Medium):** no image-format assertion. `Image.open` accepts JPEG/GIF/WebP; a non-PNG at a `.png` path yields width/height/dpi and a valid sha, so `verify_artifact` can pass a mislabeled artifact. Fix: require `img.format == "PNG"` → `E_ARTIFACT_FORMAT`.
- **Defect D5 (Medium):** only the x-axis DPI is read (`dpi[0]`, lines 39-40); `dpi=(300,150)` passes a 300-DPI contract. Print DPIs must agree. Fix: reject non-equal x/y or check both axes.
- `verify_gate_report` (54-84): requires non-empty `checks` object, `ok is True`, `saved is True`, declared `output_sha256 ==` actual, declared `applicable_checks` equals computed, non-vacuous, zero failed. Strong.
- **Gap G1 (Low):** truncated-but-openable images are not decode-verified (`Image.open` is lazy; no `.load()`). A gate report could cover bytes whose pixel data is corrupt. Fix: `img.load()` inside the try, or document that gate coverage is the only pixel proof.

## 4. Critic contract checks (`forge_critic.py`, STATIC)

- `validate_critique` (30-79): typed dimensions (name, score 1–5, positive integer crop, observation, severity), defects (kind/severity/crop), confidence 0–1, `unseen` list, `model_id`, `prompt_version`, blind-leak scan, pass-with-major contradiction, fail-without-defect contradiction. Strong.
- **Defect D6 (Medium-High):** `combine` (82-102) accepts any `human` value. Only `"reject"` (line 92) and `"accept"` (line 100) are honoured; `"Accept"`, `"accepted"`, `"maybe"` are silently treated as no human and can yield `pass` with reason `E_EVIDENCE_AGREES` (line 102). Fix: validate `human in {None,"accept","reject"}` or refuse `E_HUMAN_INVALID`.
- **Defect D7 (Medium):** `gate_ok` is type-confused. `combine("false", critique)` is neither `None` nor `False`, so it proceeds as a passed gate (lines 83-86). Fail-closed requires `gate_ok is True` to proceed. Fix: `if gate_ok is not True: return fail/unverified`.
- **Defect D8 (Low):** `BLIND_LEAKS` (16-17) false-positives on the word "operator" in legitimate free text (e.g., "the operator renamed the layer"), rejecting a valid critique as `E_CRITIC_BLINDED`. Fix: narrow to evidence phrasing or allow an allow-list of observation terms.
- **Gap G2 (Low):** no duplicate-dimension-name check; duplicates can double-weight a score in downstream consumers.

## 5. Confirmed defects summary

| ID | Severity | File:line | Defect | Status |
|---|---|---|---|---|
| D6 | Medium-High | `forge_critic.py:82-102` | invalid `human` value silently ignored → pass | STATIC |
| D7 | Medium | `forge_critic.py:83-86` | non-bool truthy `gate_ok` treated as pass | STATIC |
| D4 | Medium | `forge_verifier.py:33-37` | no PNG format assertion | STATIC |
| D5 | Medium | `forge_verifier.py:39-42` | x-DPI only; anisotropic DPI passes | STATIC |
| D1 | Medium | `forge_eval.py:30-43` | duplicate golden ids inflate n | STATIC |
| D2 | Low | `forge_eval.py:68-70` | impossible `successes+regressions>n` allowed | STATIC |
| D3 | Low | `forge_eval.py:60-61` | `baseline` accepts bool / bare TypeError | STATIC |
| D8 | Low | `forge_critic.py:16-17` | blind-leak regex false positive on "operator" | STATIC |
| G1 | Low | `forge_verifier.py:33-37` | no decode (`img.load()`) on truncated image | STATIC |
| G2 | Low | `forge_critic.py:36-52` | duplicate dimension names allowed | STATIC |
| A1 | Info | `forge_eval.py:12` | `z=1.96` truncated vs 1.959964 (≤7.2e-5) | RAN |

**Reproduction status:** no behavioural defect was executed. Pytest is **not installed** for this interpreter (`RAN`: `No module named pytest`), so the three test files were not run. Each defect above is confirmed by code reading and has a proposed reproduction; none is claimed as a runtime failure.

## 6. UNVERIFIED claims / missing probes

| Item | Status | What would verify it |
|---|---|---|
| `tests/test_forge_{verifier,critic,eval}.py` pass | UNVERIFIED | install pytest (`python -m pip install pytest`) then `python -m pytest tests/test_forge_*.py -q` |
| `forge_verifier` imports (PIL availability) | UNVERIFIED | `python -c "import forge_verifier"` |
| D1–D8 reproduce at runtime | UNVERIFIED | the per-defect repro scripts; none run (timebox) |
| End-to-end forge gateway/service/worker behaviour | UNVERIFIED | out of scope for this read-only seat |
| Any vision/critic accuracy or "learning" claim | **NOT CLAIMED** | requires a labelled run; forbidden by task |
| Rendered PNG DPI round-trip values | UNVERIFIED | write/read a 300-DPI PNG and compare |

## 7. Recommended next actions (owner)

1. Fix D6/D7 first: they are the only paths found where invalid evidence can reach `pass`.
2. Add the PNG-format and dual-DPI checks (D4/D5) before any print/publish path trusts `verify_artifact`.
3. Add duplicate-id rejection to `evaluate_goldens` (D1) and the `successes+regressions<=n` guard (D2).
4. Install pytest in the audit interpreter and run the three suites; this audit does not certify them.
5. State in module docstrings that the `min_n=8/7` promotion parameters are a simulation-derived suggestion (task-11), not an adopted policy.
