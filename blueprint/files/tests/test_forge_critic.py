"""W3-B blind-critic contract tests (no vision model, no network)."""
from __future__ import annotations

import copy
import unittest

from forge_critic import combine, validate_critique


def critique(**overrides):
    base = {
        "verdict": "pass",
        "dimensions": [{
            "name": "brief_fit", "score": 4, "crop": [0, 0, 100, 100],
            "observation": "subject is centred and legible", "severity": "none",
        }],
        "defects": [],
        "confidence": 0.8,
        "unseen": ["back print"],
        "model_id": "deepseek-flash",
        "prompt_version": "critic/1",
    }
    base.update(overrides)
    return base


class CriticValidationTests(unittest.TestCase):
    def test_valid_critique(self):
        result = validate_critique(critique())
        self.assertTrue(result["ok"])
        self.assertEqual(result["verdict"], "pass")

    def test_dimension_without_crop_rejected(self):
        data = critique()
        data["dimensions"][0].pop("crop")
        self.assertEqual(validate_critique(data)["code"], "E_CRITIC_INVALID")

    def test_empty_observation_rejected(self):
        data = critique()
        data["dimensions"][0]["observation"] = " "
        self.assertEqual(validate_critique(data)["code"], "E_CRITIC_INVALID")

    def test_pass_with_major_defect_rejected(self):
        data = critique()
        data["dimensions"][0]["severity"] = "major"
        self.assertEqual(validate_critique(data)["code"], "E_CRITIC_CONTRADICTION")

    def test_fail_without_defects_rejected(self):
        data = critique(verdict="fail")
        self.assertEqual(validate_critique(data)["code"], "E_CRITIC_CONTRADICTION")

    def test_blind_leak_rejected(self):
        data = critique()
        data["dimensions"][0]["observation"] = "exit code was zero"
        self.assertEqual(validate_critique(data)["code"], "E_CRITIC_BLINDED")

    def test_bad_confidence_rejected(self):
        self.assertEqual(validate_critique(critique(confidence=1.5))["code"], "E_CRITIC_INVALID")


class CombineTests(unittest.TestCase):
    def test_gate_failure_cannot_be_overridden(self):
        self.assertEqual(combine(False, critique())["verdict"], "fail")

    def test_missing_gate_is_unverified(self):
        self.assertEqual(combine(None, critique())["verdict"], "unverified")

    def test_missing_critic_is_unverified(self):
        self.assertEqual(combine(True, None)["verdict"], "unverified")

    def test_critic_fail_disagrees_to_human(self):
        bad = critique(verdict="fail", defects=[{
            "kind": "fringe", "crop": [1, 1, 10, 10], "severity": "major"}])
        result = combine(True, bad)
        self.assertEqual(result["verdict"], "needs_human")
        self.assertEqual(result["reason"], "E_CRITIC_DISAGREES")

    def test_human_reject_wins(self):
        result = combine(True, critique(), human="reject")
        self.assertEqual(result["verdict"], "needs_human")

    def test_human_accept_with_agreement_passes(self):
        result = combine(True, critique(), human="accept")
        self.assertEqual(result["verdict"], "pass")
        self.assertEqual(result["reason"], "E_HUMAN_ACCEPT")

    def test_invalid_critique_is_unverified_not_pass(self):
        data = copy.deepcopy(critique())
        data.pop("dimensions")
        result = combine(True, data)
        self.assertEqual(result["verdict"], "unverified")
        self.assertEqual(result["reason"], "E_CRITIC_INVALID")


if __name__ == "__main__":
    unittest.main()
