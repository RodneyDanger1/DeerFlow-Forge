"""Local evaluation and promotion *proposal* contract (W4-A).

No model training, no activation, no RL. The owner must adopt the horizon and approve a
candidate before any skill pointer changes.
"""
from __future__ import annotations

import math
from typing import Any, Iterable


def wilson_lower_bound(successes: int, n: int, z: float = 1.96) -> float:
    if not isinstance(successes, int) or not isinstance(n, int) or n <= 0 or not 0 <= successes <= n:
        raise ValueError("E_EVAL_INVALID: successes/n must be integers with 0 <= k <= n")
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    margin = z / denom * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return max(0.0, centre - margin)


def evaluate_goldens(results: Iterable[dict[str, Any]]) -> dict[str, Any]:
    rows = list(results)
    if not rows:
        raise ValueError("E_EVAL_EMPTY: at least one golden result is required")
    failed: list[str] = []
    regressions: list[str] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"E_EVAL_INVALID: result {index} is not an object")
        golden_id = row.get("id")
        if not isinstance(golden_id, str) or not golden_id.strip():
            raise ValueError(f"E_EVAL_INVALID: result {index} has no id")
        if not isinstance(row.get("passed"), bool):
            raise ValueError(f"E_EVAL_INVALID: {golden_id} passed must be boolean")
        if not isinstance(row.get("regression", False), bool):
            raise ValueError(f"E_EVAL_INVALID: {golden_id} regression must be boolean")
        if not row["passed"]:
            failed.append(golden_id)
        if row.get("regression", False):
            regressions.append(golden_id)
    n = len(rows)
    passed = n - len(failed)
    return {
        "n": n,
        "passed": passed,
        "failed": failed,
        "regressions": regressions,
        "rate": passed / n,
        "wilson_lower": wilson_lower_bound(passed, n),
    }


def propose_promotion(*, successes: int, n: int, baseline: float = 0.5,
                      min_n: int = 8, min_successes: int = 7,
                      regressions: int = 0, human_approved: bool = False) -> dict[str, Any]:
    """Return a candidate/refusal; this never activates a skill."""
    if not 0 <= baseline <= 1:
        raise ValueError("E_EVAL_INVALID: baseline must be 0..1")
    if min_n < 3 or not 0 <= min_successes <= min_n:
        raise ValueError("E_EVAL_INVALID: invalid evaluation horizon")
    if not isinstance(regressions, int) or regressions < 0:
        raise ValueError("E_EVAL_INVALID: regressions must be a non-negative integer")
    lb = wilson_lower_bound(successes, n)
    common = {"n": n, "successes": successes, "wilson_lower": lb,
              "baseline": baseline, "active": False}
    if n < min_n:
        return {**common, "decision": "refused", "reason": "E_EVAL_SAMPLE_TOO_SMALL"}
    if successes < min_successes:
        return {**common, "decision": "refused", "reason": "E_EVAL_TOO_FEW_SUCCESSES"}
    if lb <= baseline:
        return {**common, "decision": "refused", "reason": "E_EVAL_BELOW_BASELINE"}
    if regressions:
        return {**common, "decision": "refused", "reason": "E_EVAL_REGRESSION"}
    if not human_approved:
        return {**common, "decision": "refused", "reason": "E_EVAL_HUMAN_REQUIRED"}
    return {**common, "decision": "promote_candidate", "reason": "E_EVAL_POLICY_MET"}
