"""Craft registry construction and version-gate tests (no Craft execution)."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from forge_craft_registry import (
    PHOTO_KEY, VECTOR_KEY, CraftRegistryError, build_registry, verify_probes,
)
from forge_executor import ProcessExecutor
from forge_gateway import ToolCall


class CraftRegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="forge-craft-reg-")
        self.root = Path(self.tmp.name)
        self.registry = build_registry(sys.executable, sys.executable)
        self.executor = ProcessExecutor(self.registry, work_root=self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_both_measured_commands_are_registered(self):
        self.assertEqual(set(self.registry), {VECTOR_KEY, PHOTO_KEY})
        for key, command in self.registry.items():
            self.assertTrue(Path(command.binary).is_absolute(), key)
            self.assertEqual(command.base_args, ("run",), key)
            self.assertTrue(command.require_artifacts, key)

    def test_vector_argv_uses_input_and_measured_flags(self):
        command = self.registry[VECTOR_KEY]
        call = ToolCall(
            episode_id="ep", tool_id=VECTOR_KEY[0], cmd_id=VECTOR_KEY[1],
            params={"input_png": "/work/in.png",
                    "trace_params_json": '{"mode":"color"}'})
        argv = self.executor._argv(command, call)
        self.assertIn("--in", argv)
        self.assertIn("/work/in.png", argv)
        self.assertIn("imageTrace.expand", argv)
        self.assertIn('{"params":{"mode":"color"}}', argv)
        self.assertIn(str(self.root.resolve()) + "/traced.svg", argv)

    def test_photo_argv_uses_measured_flags_and_output(self):
        command = self.registry[PHOTO_KEY]
        call = ToolCall(
            episode_id="ep", tool_id=PHOTO_KEY[0], cmd_id=PHOTO_KEY[1],
            params={"input_png": "/work/art.svg",
                    "resize_params_json": '{"width":4200,"height":4800}'})
        argv = self.executor._argv(command, call)
        self.assertIn("/work/art.svg", argv)
        self.assertIn("image.trim", argv)
        self.assertIn(str(self.root.resolve()) + "/trimmed.png", argv)

    def test_missing_craft_parameter_refused(self):
        command = self.registry[VECTOR_KEY]
        call = ToolCall(episode_id="ep", tool_id=VECTOR_KEY[0],
                        cmd_id=VECTOR_KEY[1], params={})
        with self.assertRaises(Exception) as caught:
            self.executor._argv(command, call)
        self.assertEqual(getattr(caught.exception, "code", None), "E_PARAM_REJECTED")

    def test_version_gate_accepts_expected_and_rejects_drift(self):
        good = {
            VECTOR_KEY: {"ok": True, "version": "vectorcraft-cli 0.21.1"},
            PHOTO_KEY: {"ok": True, "version": "photocraft-cli 0.20.2 (abc)"},
        }
        verify_probes(good)
        bad = dict(good)
        bad[VECTOR_KEY] = {"ok": True, "version": "vectorcraft-cli 0.22.0"}
        with self.assertRaises(CraftRegistryError) as caught:
            verify_probes(bad)
        self.assertEqual(caught.exception.code, "E_TOOL_VERSION_DRIFT")

    def test_version_gate_refuses_missing_probe(self):
        with self.assertRaises(CraftRegistryError) as caught:
            verify_probes({})
        self.assertEqual(caught.exception.code, "E_TOOL_NOT_INSTALLED")


if __name__ == "__main__":
    unittest.main()
