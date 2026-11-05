"""W4-A evaluation/promotion tests (no model, no network)."""
from __future__ import annotations

import unittest

from forge_eval import evaluate_goldens, propose_promotion, wilson_lower_bound


class WilsonTests(unittest.TestCase):
    def test_three_of_three_does_not_clear_sixty_percent(self):
        self.assertAlmostEqual(wilson_lower_bound(3, 3), 0.4385, places=4)

    def test_seven_of_eight(self):
        self.assertAlmostEqual(wilson_lower_bound(7, 8), 0.5291, places=4)

    def test_invalid_counts(self):
        with self.assertRaises(ValueError):
            wilson_lower_bound(4, 3)
        with self.assertRaises(ValueError):
            wilson_lower_bound(0, 0)


class GoldenEvaluationTests(unittest.TestCase):
    def test_failed_and_regression_ids_are_retained(self):
        rows = [{"id": f"g{i}", "passed": True} for i in range(6)]
        rows += [{"id": "g6", "passed": False}, {"id": "g7", "passed": True, "regression": True}]
        result = evaluate_goldens(rows)
        self.assertEqual(result["n"], 8)
        self.assertEqual(result["passed"], 7)
        self.assertEqual(result["failed"], ["g6"])
        self.assertEqual(result["regressions"], ["g7"])
        self.assertAlmostEqual(result["rate"], 0.875)

    def test_empty_and_invalid(self):
        with self.assertRaises(ValueError):
            evaluate_goldens([])
        with self.assertRaises(ValueError):
            evaluate_goldens([{"id": "g", "passed": "yes"}])


class PromotionTests(unittest.TestCase):
    def test_three_of_three_is_refused_for_small_sample(self):
        result = propose_promotion(successes=3, n=3, human_approved=True)
        self.assertEqual(result["decision"], "refused")
        self.assertEqual(result["reason"], "E_EVAL_SAMPLE_TOO_SMALL")

    def test_eight_of_eight_without_human_is_refused(self):
        result = propose_promotion(successes=8, n=8)
        self.assertEqual(result["reason"], "E_EVAL_HUMAN_REQUIRED")

    def test_eight_of_eight_with_human_is_candidate_only(self):
        result = propose_promotion(successes=8, n=8, human_approved=True)
        self.assertEqual(result["decision"], "promote_candidate")
        self.assertFalse(result["active"])

    def test_seven_of_eight_can_pass_baseline(self):
        result = propose_promotion(successes=7, n=8, baseline=0.5, human_approved=True)
        self.assertEqual(result["decision"], "promote_candidate")

    def test_six_of_eight_is_refused(self):
        result = propose_promotion(successes=6, n=8, baseline=0.5, human_approved=True)
        self.assertEqual(result["reason"], "E_EVAL_TOO_FEW_SUCCESSES")

    def test_baseline_above_lower_bound_refuses(self):
        result = propose_promotion(successes=8, n=8, baseline=0.7, human_approved=True)
        self.assertEqual(result["reason"], "E_EVAL_BELOW_BASELINE")

    def test_regression_refuses(self):
        result = propose_promotion(successes=8, n=8, regressions=1, human_approved=True)
        self.assertEqual(result["reason"], "E_EVAL_REGRESSION")

    def test_invalid_horizon(self):
        with self.assertRaises(ValueError):
            propose_promotion(successes=2, n=2, min_n=2)
        with self.assertRaises(ValueError):
            propose_promotion(successes=1, n=1, baseline=1.5)


if __name__ == "__main__":
    unittest.main()

