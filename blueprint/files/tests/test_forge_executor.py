"""Process executor tests: real child processes, no shell, no mocks."""
from __future__ import annotations

import json
import sys
import tempfile
import time
import unittest
from pathlib import Path

from forge_executor import ProcessCommand, ProcessExecutor
from forge_gateway import PolicyError, ToolCall, ToolSpec

FIXTURE = """
import json, pathlib, sys, time
args = sys.argv[1:]
if "--version" in args:
    print("fixture-cli 1.2.3")
    raise SystemExit(0)
if "--sleep" in args:
    time.sleep(5)
if "--fail" in args:
    print("fixture failed", file=sys.stderr)
    raise SystemExit(3)
payload = json.loads(args[args.index("--payload") + 1])
if "--noout" not in args:
    pathlib.Path("out.txt").write_text(payload["text"], encoding="utf-8")
"""


class ProcessExecutorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="forge-exec-")
        self.root = Path(self.tmp.name)
        self.script = self.root / "fixture.py"
        self.script.write_text(FIXTURE, encoding="utf-8")
        self.spec = ToolSpec(tool_id="tool.run", allowed_roles=("operator",),
                             allowed_cmds=("run",), roots=(str(self.root),))
        self.call = ToolCall(episode_id="ep", tool_id="tool.run", cmd_id="run",
                             params={"text": "hello"})

    def tearDown(self):
        self.tmp.cleanup()

    def command(self, **overrides) -> ProcessCommand:
        base = dict(binary=sys.executable, base_args=(str(self.script),),
                    args_template=("--payload", "{params_json}"),
                    artifact_globs=("out.txt",), require_artifacts=True)
        base.update(overrides)
        return ProcessCommand(**base)

    def test_absolute_binary_runs_and_hashes_artifact(self):
        executor = ProcessExecutor({("tool.run", "run"): self.command()},
                                   work_root=self.root)
        outcome = executor.run(self.spec, self.call)
        self.assertEqual(outcome.exit_code, 0)
        self.assertEqual(len(outcome.artifacts), 1)
        artifact = outcome.artifacts[0]
        self.assertTrue(artifact["path"].endswith("out.txt"))
        self.assertEqual(artifact["bytes"], len("hello"))
        self.assertEqual(len(artifact["sha256"]), 64)
        self.assertIn("--payload", outcome.argv)
        self.assertIn('{"text":"hello"}', outcome.argv)

    def test_nonzero_exit_is_failure_with_bounded_stderr(self):
        command = self.command(base_args=(str(self.script), "--fail"))
        executor = ProcessExecutor({("tool.run", "run"): command},
                                   work_root=self.root)
        outcome = executor.run(self.spec, self.call)
        self.assertEqual(outcome.exit_code, 3)
        self.assertIn("fixture failed", outcome.message)

    def test_timeout_kills_process_and_returns_named_refusal(self):
        command = self.command(base_args=(str(self.script), "--sleep"),
                               timeout_s=1)
        executor = ProcessExecutor({("tool.run", "run"): command},
                                   work_root=self.root, timeout_s=5)
        started = time.monotonic()
        outcome = executor.run(self.spec, self.call)
        elapsed = time.monotonic() - started
        self.assertEqual(outcome.exit_code, 124)
        self.assertEqual(outcome.refusal_code, "E_TIMEOUT")
        self.assertLess(elapsed, 4)

    def test_success_without_required_artifact_is_failure(self):
        command = self.command(artifact_globs=("missing.txt",))
        executor = ProcessExecutor({("tool.run", "run"): command},
                                   work_root=self.root)
        outcome = executor.run(self.spec, self.call)
        self.assertEqual(outcome.exit_code, 1)
        self.assertIn("E_ARTIFACT_MISSING", outcome.message)

    def test_unknown_command_is_named_refusal(self):
        executor = ProcessExecutor({}, work_root=self.root)
        with self.assertRaises(PolicyError) as caught:
            executor.run(self.spec, self.call)
        self.assertEqual(caught.exception.code, "E_COMMAND_UNKNOWN")

    def test_relative_or_missing_binary_is_rejected_at_registration(self):
        for binary in ("python", str(self.root / "absent-binary")):
            with self.subTest(binary=binary), self.assertRaises(ValueError) as caught:
                ProcessExecutor({("tool.run", "run"): self.command(binary=binary)},
                                work_root=self.root)
            self.assertIn("E_TOOL_NOT_INSTALLED", str(caught.exception))

    def test_artifact_glob_escaping_root_is_rejected(self):
        with self.assertRaises(ValueError) as caught:
            ProcessExecutor({("tool.run", "run"): self.command(
                artifact_globs=("../escape.txt",))}, work_root=self.root)
        self.assertIn("E_ROOT_DENIED", str(caught.exception))

    def test_typed_params_and_work_root_expand(self):
        command = self.command(args_template=(
            "--payload", "{params_json}",
            "--input", "{param:input_png}",
            "--root", "{work_root}"))
        executor = ProcessExecutor({("tool.run", "run"): command},
                                   work_root=self.root)
        call = ToolCall(episode_id="ep", tool_id="tool.run", cmd_id="run",
                        params={"text": "hello", "input_png": "/tmp/input.png"})
        argv = executor._argv(command, call)
        self.assertIn("/tmp/input.png", argv)
        self.assertIn(str(self.root.resolve()), argv)
        with self.assertRaises(PolicyError) as caught:
            executor._argv(command, self.call)  # missing input_png
        self.assertEqual(caught.exception.code, "E_PARAM_REJECTED")

    def test_version_probe_returns_bounded_version(self):
        command = self.command(version_args=(str(self.script), "--version"))
        executor = ProcessExecutor({("tool.run", "run"): command},
                                   work_root=self.root)
        probes = executor.probe_binaries()
        self.assertTrue(probes[("tool.run", "run")]["ok"])
        self.assertEqual(probes[("tool.run", "run")]["version"], "fixture-cli 1.2.3")


if __name__ == "__main__":
    unittest.main()
