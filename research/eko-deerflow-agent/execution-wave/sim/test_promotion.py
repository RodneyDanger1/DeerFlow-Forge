"""Unit tests for the promotion-policy primitives.

Run from this directory:
    python -m unittest -v test_promotion

These tests pin the arithmetic the simulation depends on (Wilson bounds,
promotion boundaries, acceptance, demotion triggers) and a few failure paths.
They do not simulate the full scenarios; simulate.py does that.
"""

from __future__ import annotations

import math
import unittest

from promotion import (
    Z95,
    DemotionMonitor,
    acceptance_decision,
    evaluate_promotion,
    two_proportion_z,
    wilson_lower_bound,
)


class WilsonLowerBoundTest(unittest.TestCase):
    def test_known_values(self) -> None:
        # 3/3: numerator is exactly 1.0, denominator 1 + z^2/3.
        self.assertAlmostEqual(wilson_lower_bound(3, 3), 1.0 / (1.0 + Z95**2 / 3.0), places=12)
        self.assertAlmostEqual(wilson_lower_bound(3, 3), 0.4385, places=4)
        self.assertAlmostEqual(wilson_lower_bound(8, 8), 0.6756, places=4)
        self.assertAlmostEqual(wilson_lower_bound(19, 20), 0.7639, places=4)

    def test_monotone_in_k_and_n(self) -> None:
        self.assertLess(wilson_lower_bound(3, 3), wilson_lower_bound(8, 8))
        self.assertLess(wilson_lower_bound(6, 8), wilson_lower_bound(7, 8))
        self.assertLess(wilson_lower_bound(9, 10), wilson_lower_bound(10, 10))

    def test_bounds(self) -> None:
        for k, n in [(0, 5), (1, 5), (5, 5), (19, 20), (20, 20)]:
            lb = wilson_lower_bound(k, n)
            self.assertGreaterEqual(lb, 0.0)
            self.assertLessEqual(lb, k / n)

    def test_rejects_bad_input(self) -> None:
        with self.assertRaises(ValueError):
            wilson_lower_bound(0, 0)
        with self.assertRaises(ValueError):
            wilson_lower_bound(4, 3)
        with self.assertRaises(ValueError):
            wilson_lower_bound(-1, 3)


class TwoProportionTest(unittest.TestCase):
    def test_identical_rates_are_not_significant(self) -> None:
        _, p = two_proportion_z(7, 10, 7, 10)
        self.assertGreater(p, 0.5)

    def test_large_difference_is_significant(self) -> None:
        _, p = two_proportion_z(20, 100, 40, 100)
        self.assertLess(p, 0.01)

    def test_no_variance_case(self) -> None:
        z, p = two_proportion_z(0, 5, 0, 5)
        self.assertEqual(z, 0.0)
        self.assertEqual(p, 1.0)


class PromotionRuleTest(unittest.TestCase):
    def test_documented_rule_at_n3_cannot_promote(self) -> None:
        # The 06 rule with N_min=3 and delta=0.10 (p0=0.5) fails on 3/3.
        result = evaluate_promotion(3, 3, p0=0.5, delta=0.10)
        self.assertFalse(result["checks"]["wilson"])
        self.assertFalse(result["promote"])
        self.assertAlmostEqual(result["wilson_lb"], 0.4385, places=4)

    def test_perfect_record_at_n8_promotes(self) -> None:
        result = evaluate_promotion(8, 8, p0=0.5, delta=0.10)
        self.assertTrue(result["promote"])

    def test_one_failure_at_n10_fails_wilson_guard(self) -> None:
        result = evaluate_promotion(9, 10, p0=0.5, delta=0.10)
        self.assertFalse(result["checks"]["wilson"])
        self.assertFalse(result["promote"])

    def test_ratio_check_is_independent(self) -> None:
        # 6/10 has a low ratio even though k >= n_min.
        result = evaluate_promotion(6, 10, p0=0.1, delta=0.0, ratio_min=0.75)
        self.assertFalse(result["checks"]["ratio"])
        self.assertFalse(result["promote"])

    def test_rejects_invalid_n_min(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_promotion(1, 1, n_min=0)


class AcceptanceTest(unittest.TestCase):
    def test_all_checks_must_pass(self) -> None:
        ok, checks = acceptance_decision(True, True, True, human_score=4)
        self.assertTrue(ok)
        self.assertTrue(all(checks.values()))

    def test_gate_pass_with_bad_human_is_rejected(self) -> None:
        ok, _ = acceptance_decision(True, True, True, human_score=1)
        self.assertFalse(ok)

    def test_missing_human_score_is_rejected_for_taste_claim(self) -> None:
        ok, checks = acceptance_decision(True, True, True, human_score=None)
        self.assertFalse(ok)
        self.assertFalse(checks["human"])

    def test_taste_claim_false_does_not_require_human(self) -> None:
        ok, _ = acceptance_decision(True, True, True, human_score=None, taste_claim=False)
        self.assertTrue(ok)

    def test_failed_artifact_blocks_even_with_human(self) -> None:
        ok, _ = acceptance_decision(True, False, True, human_score=5)
        self.assertFalse(ok)


class DemotionTest(unittest.TestCase):
    def test_window_rule_triggers_two_failures_in_twenty(self) -> None:
        monitor = DemotionMonitor(window=20, max_failures=2)
        monitor.update(False)
        self.assertFalse(monitor.update(True)["triggered"])
        self.assertTrue(monitor.update(False)["triggered"])

    def test_healthy_streak_does_not_trigger_window_rule(self) -> None:
        monitor = DemotionMonitor(window=20, max_failures=3)
        for _ in range(30):
            self.assertFalse(monitor.update(True)["triggered"])

    def test_consecutive_rule(self) -> None:
        monitor = DemotionMonitor(window=20, max_failures=99, consecutive=2)
        monitor.update(False)
        self.assertFalse(monitor.update(True)["triggered"])
        monitor.update(False)
        self.assertTrue(monitor.update(False)["triggered"])

    def test_cusum_accumulates_failures(self) -> None:
        monitor = DemotionMonitor(window=20, max_failures=99, cusum_k=0.15, cusum_h=1.0)
        triggered = False
        for _ in range(10):
            triggered = monitor.update(False)["triggered"] or triggered
        self.assertTrue(triggered)
        self.assertGreater(monitor.cusum_state, 1.0)

    def test_cusum_decays_on_success(self) -> None:
        monitor = DemotionMonitor(window=20, max_failures=99, cusum_k=0.15, cusum_h=5.0)
        monitor.update(False)
        before = monitor.cusum_state
        monitor.update(True)
        self.assertLess(monitor.cusum_state, before)

    def test_rejects_bad_config(self) -> None:
        with self.assertRaises(ValueError):
            DemotionMonitor(window=0)
        with self.assertRaises(ValueError):
            DemotionMonitor(max_failures=0)


if __name__ == "__main__":
    unittest.main()
