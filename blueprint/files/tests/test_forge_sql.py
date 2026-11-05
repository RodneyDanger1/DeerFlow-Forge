"""Pytest wrapper for the out-of-band SQL invariant scripts.

The real assertions live in `tests/forge_schema_assertions.py` (18 checks) and
`tests/forge_schema_skiplock.py` (two-worker SKIP LOCKED). This module makes
them visible to `pytest` without duplicating a single assertion.

They need a scratch Postgres: set `FORGE_TEST_DSN`. Without it the module skips
explicitly — a green run never silently claims the SQL invariants passed.

Run: python -m pytest tests/test_forge_sql.py -q
"""
from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
DSN = os.environ.get("FORGE_TEST_DSN", "").strip()
SKIP_REASON = "FORGE_TEST_DSN unset: SQL invariants not run (explicit skip, not a pass)"

SCRIPTS = {
    "schema_assertions": TESTS_DIR / "forge_schema_assertions.py",
    "schema_skiplock": TESTS_DIR / "forge_schema_skiplock.py",
}


def _run(script: Path) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "FORGE_TEST_DSN": DSN}
    return subprocess.run([sys.executable, str(script)], capture_output=True, text=True,
                          env=env, timeout=180)


@unittest.skipUnless(DSN, SKIP_REASON)
class SqlInvariantTests(unittest.TestCase):
    def test_schema_assertions(self):
        script = SCRIPTS["schema_assertions"]
        result = _run(script)
        self.assertEqual(result.returncode, 0, result.stderr[-2000:])
        self.assertIn("RESULT pass=", result.stdout)
        self.assertNotIn("fail=0", result.stderr)

    def test_skiplock(self):
        script = SCRIPTS["schema_skiplock"]
        result = _run(script)
        self.assertEqual(result.returncode, 0, result.stderr[-2000:])
        self.assertIn("T-SKIPLOCK", result.stdout)


if __name__ == "__main__":
    if not DSN:
        print(f"SKIP: {SKIP_REASON}")
        sys.exit(0)
    unittest.main(verbosity=2)
