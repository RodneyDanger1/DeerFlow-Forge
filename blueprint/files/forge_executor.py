"""Registered process executor for the Forge gateway.

First half of the executor seam: absolute-path binary validation, explicit
argument templates, a bounded process, bounded output capture, and artifact
hashing. It does not know Craft command semantics; the caller supplies the
registry. No shell, no PATH lookup, no model-reported success.
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from forge_gateway import ExecutionOutcome, PolicyError, ToolCall, ToolSpec, canonical_json


@dataclass(frozen=True)
class ProcessCommand:
    """One registered tool/cmd binding.

    ``args_template`` items may contain ``{cmd_id}`` and ``{params_json}``.
    ``artifact_globs`` are relative to the work root; they are hashed after a
    successful exit.
    """

    binary: str
    base_args: tuple[str, ...] = ()
    args_template: tuple[str, ...] = ()
    artifact_globs: tuple[str, ...] = ()
    timeout_s: int | None = None
    require_artifacts: bool = False
    version_args: tuple[str, ...] | None = None


class ProcessExecutor:
    def __init__(self, registry: Mapping[tuple[str, str | None], ProcessCommand], *,
                 work_root: str | Path, timeout_s: int = 900,
                 max_output_bytes: int = 65536) -> None:
        root = Path(work_root)
        if not root.is_absolute() or not root.is_dir():
            raise ValueError("E_ROOT_INVALID: work_root must be an absolute directory")
        if isinstance(timeout_s, bool) or not isinstance(timeout_s, int) or not 1 <= timeout_s <= 86400:
            raise ValueError("E_PARAM_REJECTED: timeout_s must be 1..86400")
        if not isinstance(max_output_bytes, int) or max_output_bytes < 1:
            raise ValueError("E_PARAM_REJECTED: max_output_bytes must be positive")
        self.work_root = root.resolve()
        self.timeout_s = timeout_s
        self.max_output_bytes = max_output_bytes
        self._registry = dict(registry)
        for key, command in self._registry.items():
            if not isinstance(key, tuple) or len(key) != 2:
                raise ValueError("E_REGISTRY_INVALID: key must be (tool_id, cmd_id)")
            self._validate_command(key, command)

    @staticmethod
    def _validate_command(key: tuple[str, str | None], command: ProcessCommand) -> None:
        if not isinstance(command, ProcessCommand):
            raise ValueError(f"E_REGISTRY_INVALID: {key} value is not ProcessCommand")
        binary = Path(command.binary)
        if not binary.is_absolute() or not binary.name:
            raise ValueError(f"E_TOOL_NOT_INSTALLED: {key} binary must be an absolute path")
        if not binary.is_file():
            raise ValueError(f"E_TOOL_NOT_INSTALLED: {key} binary does not exist: {binary}")
        if command.timeout_s is not None and (
                isinstance(command.timeout_s, bool) or command.timeout_s < 1):
            raise ValueError(f"E_PARAM_REJECTED: {key} timeout_s must be positive")
        for pattern in command.artifact_globs:
            if Path(pattern).is_absolute() or ".." in Path(pattern).parts:
                raise ValueError(f"E_ROOT_DENIED: {key} artifact glob escapes work_root")

    def command(self, call: ToolCall) -> ProcessCommand:
        command = self._registry.get((call.tool_id, call.cmd_id))
        if command is None:
            raise PolicyError("E_COMMAND_UNKNOWN",
                              f"no registered executor for {call.tool_id}/{call.cmd_id}")
        return command

    def _argv(self, command: ProcessCommand, call: ToolCall) -> list[str]:
        params_json = canonical_json(call.params)
        cmd_id = call.cmd_id or ""
        param_re = re.compile(r"\{param:([A-Za-z_][A-Za-z0-9_]*)\}")
        try:
            template = []
            for part in command.args_template:
                part = part.replace("{cmd_id}", cmd_id)
                part = part.replace("{params_json}", params_json)
                part = part.replace("{work_root}", str(self.work_root))
                for name in param_re.findall(part):
                    if name not in call.params:
                        raise PolicyError("E_PARAM_REJECTED", f"missing parameter {name}")
                    value = call.params[name]
                    if not isinstance(value, str):
                        raise PolicyError("E_PARAM_REJECTED",
                                          f"parameter {name} must be a string")
                    part = part.replace("{param:" + name + "}", value)
                template.append(part)
        except (KeyError, ValueError) as exc:
            raise PolicyError("E_PARAM_REJECTED", f"argv template: {exc}") from exc
        return [command.binary, *command.base_args, *template]

    def _artifacts(self, command: ProcessCommand) -> tuple[dict, ...]:
        found: list[dict] = []
        for pattern in command.artifact_globs:
            for path in sorted(self.work_root.glob(pattern)):
                resolved = path.resolve()
                if self.work_root not in resolved.parents:
                    raise PolicyError("E_ROOT_DENIED", f"artifact outside work_root: {resolved}")
                if not resolved.is_file():
                    continue
                data = resolved.read_bytes()
                found.append({"path": str(resolved), "bytes": len(data),
                              "sha256": hashlib.sha256(data).hexdigest()})
        return tuple(found)

    def run(self, spec: ToolSpec, call: ToolCall) -> ExecutionOutcome:
        del spec  # policy roots are enforced by the gateway; this executor owns work_root
        command = self.command(call)
        binary = Path(command.binary)
        if not binary.is_file():
            return ExecutionOutcome(exit_code=127, duration_ms=0, argv=(str(binary),),
                                    refusal_code="E_TOOL_NOT_INSTALLED",
                                    message=f"binary missing: {binary}")
        argv = self._argv(command, call)
        timeout = min(self.timeout_s, command.timeout_s or self.timeout_s)
        started = time.monotonic()
        with tempfile.TemporaryFile() as out_file, tempfile.TemporaryFile() as err_file:
            try:
                proc = subprocess.Popen(
                    argv, cwd=str(self.work_root), stdin=subprocess.DEVNULL,
                    stdout=out_file, stderr=err_file,
                    env=self._safe_env(), shell=False)
            except OSError as exc:
                return ExecutionOutcome(exit_code=126, duration_ms=0, argv=tuple(argv),
                                        refusal_code="E_EXEC_FAILED", message=str(exc))
            try:
                exit_code = proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
                duration = int((time.monotonic() - started) * 1000)
                return ExecutionOutcome(
                    exit_code=124, duration_ms=duration, argv=tuple(argv),
                    refusal_code="E_TIMEOUT",
                    message=f"process exceeded {timeout}s and was killed")
            stderr = self._tail(err_file)
        duration = int((time.monotonic() - started) * 1000)
        if exit_code != 0:
            return ExecutionOutcome(exit_code=exit_code, duration_ms=duration,
                                    argv=tuple(argv), message=stderr[-4000:])
        artifacts = self._artifacts(command)
        if command.require_artifacts and not artifacts:
            return ExecutionOutcome(
                exit_code=1, duration_ms=duration, argv=tuple(argv),
                message="E_ARTIFACT_MISSING: process exited 0 but wrote no artifact")
        return ExecutionOutcome(exit_code=0, duration_ms=duration, argv=tuple(argv),
                                artifacts=artifacts)

    def _safe_env(self) -> dict[str, str]:
        keys = ("PATH", "SYSTEMROOT", "WINDIR", "LANG", "LC_ALL")
        env = {key: os.environ[key] for key in keys if key in os.environ}
        env["HOME"] = str(self.work_root)
        env["TMPDIR"] = str(self.work_root)
        return env

    def _tail(self, stream) -> str:
        stream.seek(0, os.SEEK_END)
        size = stream.tell()
        stream.seek(max(0, size - self.max_output_bytes))
        return stream.read().decode("utf-8", errors="replace")

    def verify_binaries(self) -> dict[tuple[str, str | None], bool]:
        """Read-only existence check; version probing is caller-specific."""
        return {key: Path(command.binary).is_file()
                for key, command in self._registry.items()}

    def probe_binaries(self, *, version_args: tuple[str, ...] = ("--version",),
                       timeout_s: int = 10) -> dict[tuple[str, str | None], dict]:
        """Run each registered binary with version args; never executes a tool command."""
        if not isinstance(timeout_s, int) or timeout_s < 1:
            raise ValueError("E_PARAM_REJECTED: timeout_s must be positive")
        results: dict[tuple[str, str | None], dict] = {}
        for key, command in self._registry.items():
            binary = Path(command.binary)
            if not binary.is_file():
                results[key] = {"ok": False, "code": "E_TOOL_NOT_INSTALLED",
                                "version": None, "message": str(binary)}
                continue
            try:
                argv = [str(binary), *(command.version_args
                                       if command.version_args is not None
                                       else version_args)]
                proc = subprocess.run(
                    argv, cwd=str(self.work_root),
                    stdin=subprocess.DEVNULL, capture_output=True, timeout=timeout_s,
                    env=self._safe_env(), shell=False, check=False)
            except (OSError, subprocess.TimeoutExpired) as exc:
                results[key] = {"ok": False, "code": "E_TOOL_PROBE_FAILED",
                                "version": None, "message": str(exc)}
                continue
            text = (proc.stdout + proc.stderr).decode("utf-8", errors="replace")
            text = text[-self.max_output_bytes:]
            ok = proc.returncode == 0
            results[key] = {"ok": ok,
                            "code": None if ok else "E_TOOL_PROBE_FAILED",
                            "version": text.strip().splitlines()[0] if text.strip() else None,
                            "message": "" if ok else text[-2000:]}
        return results
