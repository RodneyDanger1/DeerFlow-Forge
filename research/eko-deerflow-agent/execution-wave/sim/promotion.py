"""Core promotion-policy primitives for the Forge Conductor simulation.

Pure standard library, no side effects. These functions implement the policy
specified in research/eko-deerflow-agent/wave2/06-LEARNING-LOOPS.md section 10:

  * Wilson score lower bound for a binomial success rate;
  * the N-success promotion rule with a Wilson guard;
  * the episode acceptance function (gates + artifact contract + rights + human);
  * a demotion monitor (rolling-window failures, consecutive failures, CUSUM).

They are policy arithmetic, not a model of Craft quality. A simulation that
calls them measures how the *rule* behaves under assumed success probabilities.
"""

from __future__ import annotations

import math

# Two-sided 95% normal quantile.
Z95 = 1.959963984540054


def wilson_lower_bound(k: int, n: int, z: float = Z95) -> float:
    """Lower bound of the Wilson score interval for k successes in n trials.

    LB = (p + z^2/(2n) - z*sqrt(p(1-p)/n + z^2/(4n^2))) / (1 + z^2/n)

    Unlike k/n this does not report 3/3 as certainty; it is the statistic the
    promotion rule uses so that small samples cannot promote on their own.
    """
    if n <= 0:
        raise ValueError("n must be positive")
    if k < 0 or k > n:
        raise ValueError("k must satisfy 0 <= k <= n")
    p = k / n
    z2 = z * z
    denom = 1.0 + z2 / n
    center = p + z2 / (2.0 * n)
    margin = z * math.sqrt(p * (1.0 - p) / n + z2 / (4.0 * n * n))
    return (center - margin) / denom


def two_proportion_z(k1: int, n1: int, k2: int, n2: int) -> tuple[float, float]:
    """Two-sided two-proportion z test. Returns (z, p_value)."""
    if n1 <= 0 or n2 <= 0:
        raise ValueError("sample sizes must be positive")
    p1 = k1 / n1
    p2 = k2 / n2
    pool = (k1 + k2) / (n1 + n2)
    se = math.sqrt(pool * (1.0 - pool) * (1.0 / n1 + 1.0 / n2))
    if se == 0.0:
        return 0.0, 1.0
    z = (p1 - p2) / se
    # Two-sided p for a standard normal: erfc(|z| / sqrt(2)).
    p_value = math.erfc(abs(z) / math.sqrt(2.0))
    return z, p_value


def evaluate_promotion(
    k: int,
    n: int,
    p0: float = 0.5,
    delta: float = 0.10,
    n_min: int = 3,
    ratio_min: float = 0.75,
    z: float = Z95,
) -> dict:
    """Apply the documented N-success + ratio + Wilson-guard promotion rule.

    The rule as written in 06 does not fix the evaluation horizon `n`; callers
    must choose it. This function evaluates one (k, n) record.
    """
    if n_min < 1:
        raise ValueError("n_min must be >= 1")
    lb = wilson_lower_bound(k, n, z)
    ratio = k / n
    threshold = p0 + delta
    checks = {
        "n_min": k >= n_min,
        "ratio": ratio >= ratio_min,
        "wilson": lb > threshold,
    }
    return {
        "n": n,
        "k": k,
        "ratio": ratio,
        "wilson_lb": lb,
        "wilson_threshold": threshold,
        "checks": checks,
        "promote": all(checks.values()),
    }


def acceptance_decision(
    gates_pass: bool,
    artifact_ok: bool,
    rights_ok: bool,
    human_score: float | None = None,
    taste_claim: bool = True,
    human_min: int = 3,
) -> tuple[bool, dict]:
    """The episode acceptance function from 06 section 10.1.

    A gate pass alone is never enough: the artifact contract and rights record
    are independent checks, and a taste claim additionally requires a human
    score at or above `human_min`.
    """
    checks = {
        "gates": bool(gates_pass),
        "artifact": bool(artifact_ok),
        "rights": bool(rights_ok),
    }
    if taste_claim:
        checks["human"] = human_score is not None and human_score >= human_min
    else:
        checks["human"] = True
    return all(checks.values()), checks


class DemotionMonitor:
    """Demotion triggers from 06 section 10.4.

    Rules:
      * rolling window: `max_failures` failures within the last `window` uses;
      * consecutive: `consecutive` failures in a row;
      * CUSUM: S_t = max(0, S_{t-1} + failure_t - k); trigger when S_t > h.

    A trigger is a safety action (reduce exposure), so it is allowed to be
    automatic. The simulation measures false alarms on a healthy skill and
    detection delay after a version/catalogue drift.
    """

    def __init__(
        self,
        window: int = 20,
        max_failures: int = 2,
        consecutive: int | None = None,
        cusum_k: float | None = None,
        cusum_h: float | None = None,
    ) -> None:
        if window < 1:
            raise ValueError("window must be >= 1")
        if max_failures < 1:
            raise ValueError("max_failures must be >= 1")
        self.window = window
        self.max_failures = max_failures
        self.consecutive = consecutive
        self.cusum_k = cusum_k
        self.cusum_h = cusum_h
        self._history: list[bool] = []
        self._cusum = 0.0

    @property
    def cusum_state(self) -> float:
        return self._cusum

    def update(self, success: bool) -> dict:
        """Record one use; return the trigger state after it."""
        self._history.append(bool(success))
        failures = self._history[-self.window :].count(False)

        window_hit = failures >= self.max_failures
        consecutive_hit = (
            self.consecutive is not None
            and len(self._history) >= self.consecutive
            and not any(self._history[-self.consecutive :])
        )

        cusum_hit = False
        if self.cusum_k is not None and self.cusum_h is not None:
            failure = 0.0 if success else 1.0
            self._cusum = max(0.0, self._cusum + failure - self.cusum_k)
            cusum_hit = self._cusum > self.cusum_h

        triggered = window_hit or consecutive_hit or cusum_hit
        reason = None
        if window_hit:
            reason = "window"
        elif consecutive_hit:
            reason = "consecutive"
        elif cusum_hit:
            reason = "cusum"
        return {
            "triggered": triggered,
            "reason": reason,
            "failures_in_window": failures,
            "cusum": self._cusum,
        }
