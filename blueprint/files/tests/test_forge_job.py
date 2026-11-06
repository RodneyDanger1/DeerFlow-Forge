"""Worker job factory configuration and spec construction (no Craft execution)."""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from forge_consumer import ConsumerError
from forge_craft_registry import PHOTO_KEY, VECTOR_KEY
from forge_tool_job import _dsn, _work_root, build_specs


class JobConfigTests(unittest.TestCase):
    def test_missing_dsn_is_named(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ConsumerError) as caught:
                _dsn()
        self.assertEqual(caught.exception.code, "E_DSN_MISSING")

    def test_missing_or_invalid_work_root_is_named(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ConsumerError) as caught:
                _work_root()
        self.assertEqual(caught.exception.code, "E_WORK_ROOT_MISSING")
        with patch.dict(os.environ, {"FORGE_WORK_ROOT": "relative"}, clear=True):
            with self.assertRaises(ConsumerError) as caught:
                _work_root()
        self.assertEqual(caught.exception.code, "E_WORK_ROOT_INVALID")

    def test_work_root_returns_absolute_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(os.environ, {"FORGE_WORK_ROOT": tmp}, clear=True):
                self.assertEqual(_work_root(), Path(tmp).resolve())

    def test_specs_cover_both_registered_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            specs = build_specs(Path(tmp).resolve())
        pairs = {(spec.tool_id, spec.allowed_cmds[0]) for spec in specs}
        self.assertEqual(pairs, {VECTOR_KEY, PHOTO_KEY})
        self.assertTrue(all(spec.roots == (str(Path(tmp).resolve()),) for spec in specs))
        self.assertTrue(all(spec.allowed_roles == ("operator",) for spec in specs))


if __name__ == "__main__":
    unittest.main()
