"""W3-A verifier tests against the real G0 artifact/report pair."""
from __future__ import annotations

import copy
import json
import os
import unittest
from pathlib import Path

from forge_verifier import verify_artifact, verify_gate_report

ROOT = Path(__file__).resolve().parents[3]
G0 = Path(os.environ.get("FORGE_G0_DIR", ROOT / "research" / "eko-deerflow-agent" / "execution-wave" / "g0"))


@unittest.skipUnless((G0 / "trace_report.json").is_file() and (G0 / "trace_master.png").is_file(),
                     "G0 artifact/report not present")
class VerifierTests(unittest.TestCase):
    def setUp(self):
        self.report = json.loads((G0 / "trace_report.json").read_text(encoding="utf-8"))
        self.artifact = G0 / "trace_master.png"

    def test_real_g0_artifact_passes(self):
        result = verify_artifact(self.artifact, self.report,
                                 expected_px=(1500, 1800), expected_dpi=300.0)
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["verdict"], "pass")
        self.assertEqual(result["applicable_checks"], 9)
        self.assertEqual(result["artifact"]["sha256"],
                         "ab64aad724c50ecdaf99c1a873f3497a9c618ad7e9eebfa96e5df2b3572657a1")

    def test_tampered_report_hash_fails(self):
        report = copy.deepcopy(self.report)
        report["output_sha256"] = "0" * 64
        result = verify_artifact(self.artifact, report)
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "E_ARTIFACT_HASH_MISMATCH")

    def test_vacuous_gate_fails(self):
        report = copy.deepcopy(self.report)
        report["applicable_checks"] = 0
        report["checks"] = {k: {**v, "applicable": False} for k, v in report["checks"].items()}
        result = verify_artifact(self.artifact, report)
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "E_GATE_VACUOUS")

    def test_failed_check_fails(self):
        report = copy.deepcopy(self.report)
        report["checks"]["white_residual_ratio"]["pass"] = False
        result = verify_artifact(self.artifact, report)
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "E_GATE_CHECK_FAILED")

    def test_missing_artifact_fails_named(self):
        result = verify_artifact(G0 / "does-not-exist.png", self.report)
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "E_ARTIFACT_MISSING")

    def test_wrong_dimensions_fail(self):
        result = verify_artifact(self.artifact, self.report, expected_px=(1500, 1801))
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "E_DIMENSION_MISMATCH")

    def test_report_requires_matching_artifact_sha(self):
        result = verify_gate_report(self.report, "f" * 64)
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "E_ARTIFACT_HASH_MISMATCH")

    def test_malformed_check_is_named_not_crash(self):
        report = copy.deepcopy(self.report)
        report["checks"]["white_residual_ratio"] = "not-an-object"
        result = verify_gate_report(report, self.report["output_sha256"])
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "E_REPORT_INVALID")


if __name__ == "__main__":
    unittest.main()
