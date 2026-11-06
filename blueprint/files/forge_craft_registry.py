"""Measured Craft command registry for the Forge process executor.

This binds the two command lines proven by `pod_pipeline/routes.py` to the
absolute binaries installed under `/opt/craft`. The registry is data plus a
version probe; it does not execute Craft on import.
"""
from __future__ import annotations

import os
from pathlib import Path

from forge_executor import ProcessCommand, ProcessExecutor

VECTORCRAFT_DEFAULT = "/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli"
PHOTOCRAFT_DEFAULT = "/opt/craft/photocraft/photocraft-0.20.2-linux-x86_64/bin/photocraft-cli"
VECTORCRAFT_VERSION = "vectorcraft-cli 0.21.1"
PHOTOCRAFT_VERSION = "photocraft-cli 0.20.2"

VECTOR_KEY = ("vectorcraft.trace", "imageTrace.make")
PHOTO_KEY = ("photocraft.trim", "trim")


class CraftRegistryError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def build_registry(vector_bin: str | None = None,
                   photo_bin: str | None = None) -> dict[tuple[str, str], ProcessCommand]:
    vector = Path(vector_bin or os.environ.get("FORGE_VECTORCRAFT_BIN", VECTORCRAFT_DEFAULT))
    photo = Path(photo_bin or os.environ.get("FORGE_PHOTOCRAFT_BIN", PHOTOCRAFT_DEFAULT))
    return {
        VECTOR_KEY: ProcessCommand(
            binary=str(vector),
            base_args=("run",),
            args_template=(
                "--in", "{param:input_png}",
                "--cmd", "select.all",
                "--cmd", "imageTrace.make",
                "--params", '{"params":{param:trace_params_json}}',
                "--cmd", "imageTrace.expand",
                "--export", "{work_root}/traced.svg",
                "--export", "{work_root}/traced.pdf",
            ),
            artifact_globs=("traced.svg", "traced.pdf"),
            timeout_s=900,
            require_artifacts=True,
            version_args=("--version",),
        ),
        PHOTO_KEY: ProcessCommand(
            binary=str(photo),
            base_args=("run",),
            args_template=(
                "{param:input_png}",
                "--cmd", "image.trim",
                "--params", '{"basedOn":"transparent"}',
                "--cmd", "image.imageSize",
                "--params", "{param:resize_params_json}",
                "--cmd", "edit.convertToProfile",
                "--params", '{"profile":"srgb"}',
                "--out", "{work_root}/trimmed.png",
            ),
            artifact_globs=("trimmed.png",),
            timeout_s=900,
            require_artifacts=True,
            version_args=("--version",),
        ),
    }


def verify_probes(probes: dict[tuple[str, str], dict],
                  expected: dict[tuple[str, str], str] | None = None) -> None:
    expected = expected or {VECTOR_KEY: VECTORCRAFT_VERSION,
                            PHOTO_KEY: PHOTOCRAFT_VERSION}
    for key, wanted in expected.items():
        probe = probes.get(key)
        if not probe or not probe.get("ok"):
            raise CraftRegistryError(
                "E_TOOL_NOT_INSTALLED",
                f"{key}: {probe.get('message') if probe else 'not probed'}")
        version = probe.get("version") or ""
        if wanted not in version:
            raise CraftRegistryError(
                "E_TOOL_VERSION_DRIFT", f"{key}: expected {wanted!r}, got {version!r}")


def load_verified_registry(*, work_root: str | Path, vector_bin: str | None = None,
                           photo_bin: str | None = None,
                           timeout_s: int = 900) -> tuple[ProcessExecutor, dict[tuple[str, str], dict]]:
    """Build, validate and version-probe the real Craft executor.

    Raises ``E_TOOL_NOT_INSTALLED``/``E_TOOL_VERSION_DRIFT`` before any tool call.
    """
    registry = build_registry(vector_bin=vector_bin, photo_bin=photo_bin)
    executor = ProcessExecutor(registry, work_root=work_root, timeout_s=timeout_s)
    probes = executor.probe_binaries()
    verify_probes(probes)
    return executor, probes
