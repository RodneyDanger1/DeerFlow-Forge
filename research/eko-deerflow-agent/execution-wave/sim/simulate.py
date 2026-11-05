"""Scenario simulation for the Forge Conductor promotion policy.

Run:
    python simulate.py                       # writes ../04-PROMOTION.json
    python simulate.py --trials 5000 --seed 7
    python simulate.py --out C:\\tmp\\out.json

What this measures: how the *rule* from wave2/06 section 10 behaves under
assumed success probabilities. It does not measure Craft quality, model
behaviour, gate reliability, or human taste. Every probability in the models
below is an assumption stated in the output.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

from promotion import (
    Z95,
    DemotionMonitor,
    acceptance_decision,
    evaluate_promotion,
    two_proportion_z,
    wilson_lower_bound,
)

DEFAULT_TRIALS = 20000
DEFAULT_SEED = 20261105
P0 = 0.50
DELTA = 0.10
WILSON_THRESHOLD = P0 + DELTA


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _rng(seed: int, offset: int) -> random.Random:
    return random.Random(seed + offset)


def _rate(hits: int, trials: int) -> float:
    return hits / trials if trials else 0.0


def _table(title: str, headers: list[str], rows: list[list[str]]) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))
    fmt = "  ".join("{:<%d}" % w for w in widths)
    print(fmt.format(*headers))
    print("  ".join("-" * w for w in widths))
    for row in rows:
        print(fmt.format(*row))


# ---------------------------------------------------------------------------
# S1 — Wilson reference values
# ---------------------------------------------------------------------------

def scenario_wilson_reference() -> list[dict]:
    pairs = [(3, 3), (4, 5), (7, 8), (8, 8), (9, 10), (10, 10), (19, 20), (20, 20)]
    rows = []
    for k, n in pairs:
        lb = wilson_lower_bound(k, n)
        rows.append(
            {
                "k": k,
                "n": n,
                "ratio": k / n,
                "wilson_lb": lb,
                "threshold": WILSON_THRESHOLD,
                "passes_wilson_guard": lb > WILSON_THRESHOLD,
            }
        )
    return rows


# ---------------------------------------------------------------------------
# S2 — minimum synthetic evidence that fails the documented rule
# ---------------------------------------------------------------------------

def scenario_minimum_evidence() -> list[dict]:
    rows = []
    for n in range(3, 13):
        k_min = None
        for k in range(1, n + 1):
            if wilson_lower_bound(k, n) > WILSON_THRESHOLD:
                k_min = k
                break
        rows.append(
            {
                "n": n,
                "k_min_to_pass_wilson": k_min,
                "k_min_ratio": (k_min / n) if k_min is not None else None,
                "wilson_threshold": WILSON_THRESHOLD,
                "achievable": k_min is not None,
            }
        )
    return rows


# ---------------------------------------------------------------------------
# S3 — policy calibration matrix
# ---------------------------------------------------------------------------

def scenario_policy_calibration(trials: int, seed: int) -> list[dict]:
    """Compare four readings of the promotion rule across true success rates.

    count_only_n3   : promote iff the first 3 uses all succeed (N_min without guard)
    doc_rule_n3     : the 06 rule evaluated at n=3 (N_min, ratio, Wilson guard)
    doc_rule_n8     : the 06 rule evaluated at n=8
    calibrated_n8   : k>=7 at n=8 and Wilson LB > p0 (no delta), a candidate fix
    """
    rng = _rng(seed, 100)
    p_levels = [0.50, 0.60, 0.75, 0.90]
    rows = []
    for p in p_levels:
        hits = {"count_only_n3": 0, "doc_rule_n3": 0, "doc_rule_n8": 0, "calibrated_n8": 0}
        for _ in range(trials):
            h3 = [rng.random() < p for _ in range(3)]
            h8 = h3 + [rng.random() < p for _ in range(5)]
            k3, k8 = sum(h3), sum(h8)
            if k3 == 3:
                hits["count_only_n3"] += 1
            if evaluate_promotion(k3, 3, p0=P0, delta=DELTA)["promote"]:
                hits["doc_rule_n3"] += 1
            if evaluate_promotion(k8, 8, p0=P0, delta=DELTA)["promote"]:
                hits["doc_rule_n8"] += 1
            if k8 >= 7 and wilson_lower_bound(k8, 8) > P0:
                hits["calibrated_n8"] += 1
        for variant, h in hits.items():
            rows.append(
                {
                    "variant": variant,
                    "true_p": p,
                    "evaluation_n": 3 if variant.endswith("_n3") else 8,
                    "promotion_rate": _rate(h, trials),
                    "trials": trials,
                }
            )
    return rows


# ---------------------------------------------------------------------------
# S4 — regression gate sensitivity
# ---------------------------------------------------------------------------

def scenario_regression_gate(trials: int, seed: int, baseline_pass: float = 0.80) -> list[dict]:
    """Probability that a golden suite observes zero failures from a risky skill.

    A promotion is allowed only when the regression run shows no previously
    passing golden failing. A risky skill (per-golden regression probability r)
    can be promoted unseen if the suite misses every regression.
    """
    rng = _rng(seed, 200)
    rows = []
    for suite in (20, 40, 80):
        for r in (0.02, 0.05, 0.10):
            missed = 0
            for _ in range(trials):
                failures = 0
                for _ in range(suite):
                    if rng.random() < baseline_pass and rng.random() < r:
                        failures += 1
                if failures == 0:
                    missed += 1
            miss_rate = _rate(missed, trials)
            rows.append(
                {
                    "suite_size": suite,
                    "baseline_pass_rate": baseline_pass,
                    "per_golden_regression_rate": r,
                    "p_zero_observed_failures": miss_rate,
                    "promotion_rate_with_gate": miss_rate,
                    "promotion_rate_without_gate": 1.0,
                    "trials": trials,
                }
            )
    return rows


# ---------------------------------------------------------------------------
# S5 — demotion sensitivity
# ---------------------------------------------------------------------------

def scenario_demotion(trials: int, seed: int, healthy_p: float = 0.95, drift_p: float = 0.30) -> list[dict]:
    rng = _rng(seed, 300)
    configs = [
        ("window_2_of_20", dict(window=20, max_failures=2)),
        ("window_3_of_20", dict(window=20, max_failures=3)),
        ("consecutive_2", dict(window=20, max_failures=99, consecutive=2)),
        ("cusum_k_0.15_h_1.0", dict(window=20, max_failures=99, cusum_k=0.15, cusum_h=1.0)),
    ]
    healthy_uses = 30
    drift_uses = 30
    rows = []
    for name, kwargs in configs:
        false_triggers = 0
        never = 0
        delays: list[int] = []
        for _ in range(trials):
            monitor = DemotionMonitor(**kwargs)
            tripped = False
            for _ in range(healthy_uses):
                if monitor.update(rng.random() < healthy_p)["triggered"]:
                    tripped = True
                    break
            if tripped:
                false_triggers += 1
                continue
            detected = None
            for i in range(1, drift_uses + 1):
                if monitor.update(rng.random() < drift_p)["triggered"]:
                    detected = i
                    break
            if detected is None:
                never += 1
            else:
                delays.append(detected)
        delays.sort()

        def quantile(q: float) -> float | None:
            if not delays:
                return None
            idx = min(len(delays) - 1, max(0, math.ceil(q * len(delays)) - 1))
            return float(delays[idx])

        rows.append(
            {
                "rule": name,
                "healthy_p": healthy_p,
                "healthy_uses": healthy_uses,
                "drift_p": drift_p,
                "false_demotion_rate": _rate(false_triggers, trials),
                "detection_median_uses": quantile(0.50),
                "detection_p90_uses": quantile(0.90),
                "never_detected_within_drift": _rate(never, trials),
                "trials": trials,
            }
        )
    return rows


# ---------------------------------------------------------------------------
# S6 — reward-hacking scenario
# ---------------------------------------------------------------------------

def scenario_reward_hacking(trials: int, seed: int) -> list[dict]:
    """Two synthetic strategies: one improves real quality, one optimises the gate.

    Model (assumed, not measured):
      honest         : gate pass 0.80, human pass 0.90
      gate_optimiser : gate pass 0.95, human pass 0.05

    The acceptance function can require a human score (taste claim). The
    simulation measures promotion (3/3 accepted) with and without that human
    check, plus the gate/human disagreement rate a detector could watch.
    """
    rng = _rng(seed, 400)
    strategies = {
        "honest": {"gate_pass": 0.80, "human_pass": 0.90},
        "gate_optimiser": {"gate_pass": 0.95, "human_pass": 0.05},
    }
    rows = []
    for name, params in strategies.items():
        promote_with = 0
        promote_without = 0
        accept_with = 0
        accept_without = 0
        disagreement = 0
        episodes_for_promotion = 3
        episodes_for_detector = 20
        for _ in range(trials):
            accepted_with: list[bool] = []
            accepted_without: list[bool] = []
            for _ in range(episodes_for_promotion):
                gates = rng.random() < params["gate_pass"]
                human_pass = rng.random() < params["human_pass"]
                score = 5 if human_pass else 1
                ok_w, _ = acceptance_decision(gates, True, True, score, taste_claim=True)
                ok_wo, _ = acceptance_decision(gates, True, True, score, taste_claim=False)
                accepted_with.append(ok_w)
                accepted_without.append(ok_wo)
                accept_with += int(ok_w)
                accept_without += int(ok_wo)
            promote_with += int(all(accepted_with))
            promote_without += int(all(accepted_without))
            for _ in range(episodes_for_detector):
                gates = rng.random() < params["gate_pass"]
                human_pass = rng.random() < params["human_pass"]
                if gates and not human_pass:
                    disagreement += 1
        total_accept_checks = trials * episodes_for_promotion
        total_detector_checks = trials * episodes_for_detector
        rows.append(
            {
                "strategy": name,
                "assumed_gate_pass": params["gate_pass"],
                "assumed_human_pass": params["human_pass"],
                "episode_accept_rate_with_human_gate": _rate(accept_with, total_accept_checks),
                "episode_accept_rate_without_human_gate": _rate(accept_without, total_accept_checks),
                "promotion_rate_with_human_gate": _rate(promote_with, trials),
                "promotion_rate_without_human_gate": _rate(promote_without, trials),
                "gate_human_disagreement_rate": _rate(disagreement, total_detector_checks),
                "trials": trials,
            }
        )
    return rows


# ---------------------------------------------------------------------------
# S7 — null-result A/B
# ---------------------------------------------------------------------------

def scenario_null_ab(trials: int, seed: int, alpha: float = 0.05) -> dict:
    """Two identical arms (p=0.70). Naive comparison vs two-proportion z test."""
    rng = _rng(seed, 500)
    rows = []
    for n in (3, 10, 30, 100):
        naive_wins = 0
        significant = 0
        for _ in range(trials):
            k1 = sum(1 for _ in range(n) if rng.random() < 0.70)
            k2 = sum(1 for _ in range(n) if rng.random() < 0.70)
            if k2 > k1:
                naive_wins += 1
            _, p_value = two_proportion_z(k1, n, k2, n)
            if p_value < alpha:
                significant += 1
        rows.append(
            {
                "n_per_arm": n,
                "true_p_both_arms": 0.70,
                "naive_declares_arm_b_better": _rate(naive_wins, trials),
                "z_test_flags_significant": _rate(significant, trials),
                "alpha": alpha,
                "trials": trials,
            }
        )
    return {"null_rows": rows}


def scenario_power(trials: int, seed: int, alpha: float = 0.05) -> list[dict]:
    """Power to detect a real difference 0.70 vs 0.85 at several n."""
    rng = _rng(seed, 600)
    rows = []
    for n in (30, 100, 300):
        significant = 0
        for _ in range(trials):
            k1 = sum(1 for _ in range(n) if rng.random() < 0.70)
            k2 = sum(1 for _ in range(n) if rng.random() < 0.85)
            _, p_value = two_proportion_z(k1, n, k2, n)
            if p_value < alpha:
                significant += 1
        rows.append(
            {
                "n_per_arm": n,
                "p_arm_a": 0.70,
                "p_arm_b": 0.85,
                "detection_rate": _rate(significant, trials),
                "alpha": alpha,
                "trials": trials,
            }
        )
    return rows


def scenario_example_runs(seed: int) -> list[dict]:
    """Five illustrative 3-vs-3 runs under the null (identical arms)."""
    rng = _rng(seed, 700)
    out = []
    for i in range(5):
        n = 3
        k1 = sum(1 for _ in range(n) if rng.random() < 0.70)
        k2 = sum(1 for _ in range(n) if rng.random() < 0.70)
        _, p_value = two_proportion_z(k1, n, k2, n)
        out.append(
            {
                "run": i + 1,
                "arm_a_rate": k1 / n,
                "arm_b_rate": k2 / n,
                "naive_winner": "B" if k2 > k1 else ("A" if k1 > k2 else "tie"),
                "z_test_p_value": p_value,
                "z_test_significant_at_0.05": p_value < 0.05,
            }
        )
    return out


# ---------------------------------------------------------------------------
# findings — computed from the results, never hand-typed
# ---------------------------------------------------------------------------

def _find(rows: list[dict], **kwargs) -> dict:
    for row in rows:
        if all(row.get(k) == v for k, v in kwargs.items()):
            return row
    raise KeyError(f"no row matching {kwargs}")


def build_findings(results: dict) -> list[str]:
    cal = results["policy_calibration"]
    dem = results["demotion"]
    reg = results["regression_gate"]
    rh = results["reward_hacking"]
    ab = results["null_ab"]["null_rows"]
    power = results["power_check"]
    min_ev = results["minimum_evidence"]

    n8 = _find(min_ev, n=8)
    null_doc8 = _find(cal, variant="doc_rule_n8", true_p=0.50)
    best_doc8 = _find(cal, variant="doc_rule_n8", true_p=0.90)
    null_cal = _find(cal, variant="calibrated_n8", true_p=0.50)
    best_cal = _find(cal, variant="calibrated_n8", true_p=0.90)
    null_count = _find(cal, variant="count_only_n3", true_p=0.50)

    false2 = _find(dem, rule="window_2_of_20")
    false3 = _find(dem, rule="window_3_of_20")
    cusum = _find(dem, rule="cusum_k_0.15_h_1.0")
    cons = _find(dem, rule="consecutive_2")

    reg40_05 = _find(reg, suite_size=40, per_golden_regression_rate=0.05)
    reg80_05 = _find(reg, suite_size=80, per_golden_regression_rate=0.05)
    reg40_02 = _find(reg, suite_size=40, per_golden_regression_rate=0.02)

    honest = _find(rh, strategy="honest")
    hack = _find(rh, strategy="gate_optimiser")

    ab3 = _find(ab, n_per_arm=3)
    ab100 = _find(ab, n_per_arm=100)
    power100 = _find(power, n_per_arm=100)

    return [
        (
            "Minimum evidence that fails the documented rule: at n=3 even a perfect 3/3 record "
            f"gives Wilson LB={wilson_lower_bound(3, 3):.4f} < threshold {WILSON_THRESHOLD:.2f}, "
            "so the 06 rule (N_min=3 + delta=0.10) cannot promote at its own minimum sample. "
            "The rule is missing an evaluation horizon."
        ),
        (
            f"At n=8 the documented rule promotes only perfect records: null false-promotion "
            f"{null_doc8['promotion_rate']:.2%}, retention at p=0.90 {best_doc8['promotion_rate']:.2%}. "
            f"Minimum k to pass at n=8 is {n8['k_min_to_pass_wilson']}/8."
        ),
        (
            "Count-only N=3 (the rule without the Wilson guard) promotes a 50%-reliable candidate "
            f"{null_count['promotion_rate']:.2%} of the time; the calibrated variant (n=8, k>=7, LB>p0) "
            f"reduces null promotions to {null_cal['promotion_rate']:.2%} while retaining "
            f"{best_cal['promotion_rate']:.2%} of p=0.90 candidates."
        ),
        (
            "Demotion: '2 failures in last 20' fires on a healthy 95%-reliable skill "
            f"{false2['false_demotion_rate']:.2%} of the time over 30 uses. "
            f"'3 of 20' lowers this to {false3['false_demotion_rate']:.2%}; "
            f"'2 consecutive' is {cons['false_demotion_rate']:.2%}; CUSUM(k=0.15,h=1.0) is "
            f"{cusum['false_demotion_rate']:.2%} with median detection "
            f"{cusum['detection_median_uses']} uses after drift."
        ),
        (
            "Regression gate: a 40-golden suite with a 5%-per-golden regression misses "
            f"{reg40_05['p_zero_observed_failures']:.2%} of risky candidates (promoted unseen); "
            f"80 goldens miss {reg80_05['p_zero_observed_failures']:.2%}; at 2% per-golden it still "
            f"misses {reg40_02['p_zero_observed_failures']:.2%} with 40 goldens."
        ),
        (
            "Reward hacking: the gate-optimising strategy is accepted and promoted "
            f"{hack['promotion_rate_without_human_gate']:.2%} of the time when the human check is off, "
            f"and {hack['promotion_rate_with_human_gate']:.2%} with it on. The gate/human disagreement "
            f"rate separates strategies: honest {honest['gate_human_disagreement_rate']:.2%} vs "
            f"gate_optimiser {hack['gate_human_disagreement_rate']:.2%}."
        ),
        (
            "Null-result A/B: identical arms (p=0.70) are declared 'improved' by a naive higher-rate "
            f"comparison {ab3['naive_declares_arm_b_better']:.2%} of the time at n=3 and "
            f"{ab100['naive_declares_arm_b_better']:.2%} at n=100; the two-sided z-test flags "
            f"{ab3['z_test_flags_significant']:.2%} and {ab100['z_test_flags_significant']:.2%} "
            "respectively. A single small run is not evidence."
        ),
        (
            f"Power: detecting a real 0.70 vs 0.85 difference needs about 100 per arm for "
            f"{power100['detection_rate']:.2%} detection at alpha=0.05 in this model."
        ),
    ]


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Simulate the Forge Conductor promotion policy.")
    default_out = Path(__file__).resolve().parent.parent / "04-PROMOTION.json"
    parser.add_argument("--out", default=str(default_out), help="JSON output path")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--trials", type=int, default=DEFAULT_TRIALS)
    args = parser.parse_args(argv)

    if args.trials < 100:
        parser.error("--trials must be >= 100")

    results = {
        "wilson_reference": scenario_wilson_reference(),
        "minimum_evidence": scenario_minimum_evidence(),
        "policy_calibration": scenario_policy_calibration(args.trials, args.seed),
        "regression_gate": scenario_regression_gate(args.trials, args.seed),
        "demotion": scenario_demotion(args.trials, args.seed),
        "reward_hacking": scenario_reward_hacking(args.trials, args.seed),
        "null_ab": scenario_null_ab(args.trials, args.seed),
        "power_check": scenario_power(args.trials, args.seed),
        "example_null_runs": scenario_example_runs(args.seed),
    }
    findings = build_findings(results)

    document = {
        "schemaVersion": "1.0.0",
        "artifactId": "04-PROMOTION",
        "taskId": "task-11",
        "producer": "learning-loop-researcher",
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "seed": args.seed,
        "trials": args.trials,
        "pythonVersion": platform.python_version(),
        "method": {
            "kind": "Monte Carlo simulation of a decision rule",
            "deterministic": True,
            "rng": "random.Random(seed + scenario offset); no wall-clock or network input",
            "describedBy": "research/eko-deerflow-agent/wave2/06-LEARNING-LOOPS.md section 10",
            "measuresCraftQuality": False,
            "assumptions": [
                "successes are independent Bernoulli draws with the stated probability",
                "the acceptance function is applied exactly as documented",
                "the regression gate observes only the golden suite it is given",
                "no model, harness, tool, gate or human is actually executed",
            ],
        },
        "policyParameters": {
            "p0": P0,
            "delta": DELTA,
            "wilson_threshold": WILSON_THRESHOLD,
            "z95": Z95,
            "n_min_documented": 3,
            "ratio_min": 0.75,
        },
        "results": results,
        "findings": findings,
        "limitations": [
            "All probabilities are assumed inputs; results are arithmetic consequences of the model.",
            "No Craft artifact was produced or measured; this is not evidence about design quality.",
            "Gate reliability, human-rater behaviour and real skill drift are not modelled.",
            "The 'calibrated' variant is a simulation-derived suggestion, not an accepted policy.",
        ],
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")

    # ---- console report (quoted in 04-PROMOTION-SIM.md) ----
    print(f"Forge Conductor promotion simulation  seed={args.seed} trials={args.trials}")

    _table(
        "S1 Wilson lower bound (95%) vs documented threshold 0.60",
        ["k", "n", "k/n", "wilson_lb", "passes"],
        [
            [str(r["k"]), str(r["n"]), f"{r['ratio']:.3f}", f"{r['wilson_lb']:.4f}", str(r["passes_wilson_guard"])]
            for r in results["wilson_reference"]
        ],
    )

    _table(
        "S2 Minimum k that passes the Wilson guard, by evaluation horizon n",
        ["n", "k_min", "k_min/n", "achievable"],
        [
            [str(r["n"]), str(r["k_min_to_pass_wilson"]), f"{r['k_min_ratio']}" if r["k_min_ratio"] is not None else "-", str(r["achievable"])]
            for r in results["minimum_evidence"]
        ],
    )

    _table(
        "S3 Policy calibration: promotion rate by variant and true success probability",
        ["variant", "n", "p=0.50", "p=0.60", "p=0.75", "p=0.90"],
        [
            [
                variant,
                str(_find(results["policy_calibration"], variant=variant, true_p=0.50)["evaluation_n"]),
                *[
                    f"{_find(results['policy_calibration'], variant=variant, true_p=p)['promotion_rate']:.4f}"
                    for p in (0.50, 0.60, 0.75, 0.90)
                ],
            ]
            for variant in ("count_only_n3", "doc_rule_n3", "doc_rule_n8", "calibrated_n8")
        ],
    )

    _table(
        "S4 Regression gate: probability a risky skill is promoted unseen",
        ["suite", "regression/golden", "p(zero observed failures)"],
        [
            [str(r["suite_size"]), f"{r['per_golden_regression_rate']:.2f}", f"{r['p_zero_observed_failures']:.4f}"]
            for r in results["regression_gate"]
        ],
    )

    _table(
        "S5 Demotion rules: false alarms on healthy skill, detection after drift",
        ["rule", "false_demotion", "median_delay", "p90_delay", "never_detected"],
        [
            [
                r["rule"],
                f"{r['false_demotion_rate']:.4f}",
                str(r["detection_median_uses"]),
                str(r["detection_p90_uses"]),
                f"{r['never_detected_within_drift']:.4f}",
            ]
            for r in results["demotion"]
        ],
    )

    _table(
        "S6 Reward hacking: acceptance and promotion with/without the human gate",
        ["strategy", "accept_with", "accept_without", "promote_with", "promote_without", "disagreement"],
        [
            [
                r["strategy"],
                f"{r['episode_accept_rate_with_human_gate']:.4f}",
                f"{r['episode_accept_rate_without_human_gate']:.4f}",
                f"{r['promotion_rate_with_human_gate']:.4f}",
                f"{r['promotion_rate_without_human_gate']:.4f}",
                f"{r['gate_human_disagreement_rate']:.4f}",
            ]
            for r in results["reward_hacking"]
        ],
    )

    _table(
        "S7 Null-result A/B (both arms p=0.70): naive winner vs z-test",
        ["n/arm", "naive_declares_B", "z_test_significant"],
        [
            [str(r["n_per_arm"]), f"{r['naive_declares_arm_b_better']:.4f}", f"{r['z_test_flags_significant']:.4f}"]
            for r in results["null_ab"]["null_rows"]
        ],
    )

    _table(
        "S8 Example 3-vs-3 runs under the null (identical arms)",
        ["run", "A", "B", "naive", "p_value"],
        [
            [str(r["run"]), f"{r['arm_a_rate']:.3f}", f"{r['arm_b_rate']:.3f}", r["naive_winner"], f"{r['z_test_p_value']:.4f}"]
            for r in results["example_null_runs"]
        ],
    )

    print("\nFindings")
    print("--------")
    for i, f in enumerate(findings, 1):
        print(f"{i}. {f}")

    print(f"\nWrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
