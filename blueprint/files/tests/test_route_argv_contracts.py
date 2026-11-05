"""P1 contract tests: the argv the pipeline actually renders.

These pin the measured VectorCraft 0.21.1 / PhotoCraft 0.20.2 command lines and
the catalogue membership of every `--cmd` value. Pure tests: no binaries, no DB.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from pod_pipeline.config import ConfigError, Settings
from pod_pipeline.orchestrator import PipelineError, preflight_tool, _assert_source_unchanged
from pod_pipeline.routes import (
    ROUTES, Step, merged_cfg, raster_fallback_step, render_argv, trace_step,
)

ROOT = Path(__file__).resolve().parent.parent
CATALOGUES = {
    "vectorcraft": ROOT / "skills/artcraft-command-atlas/references/catalogues/vectorcraft-commands.json",
    "photocraft": ROOT / "skills/artcraft-command-atlas/references/catalogues/photocraft-commands.json",
}


def _vars(product: str) -> dict:
    cfg = merged_cfg(product, {"knitwear": {"knit_grid": "112x140"}})
    return {"src": "/in.png", "art": "/in.png", "work": "/w", "build": "/b",
            "run_id": "r", "asset_id": 1, "fallback_dpi": 600, "cfg": cfg}


def test_trace_argv_is_the_measured_contract() -> None:
    argv = render_argv(trace_step(ROUTES["apparel"]), _vars("apparel"))
    assert argv[:5] == ["vectorcraft-cli", "run", "--in", "/in.png", "--cmd"]
    assert argv[argv.index("--export"):] == ["--export", "/w/traced.svg", "--export", "/w/traced.pdf"]
    params = argv[argv.index("--params") + 1]
    assert json.loads(params) == {"params": {
        "mode": "color", "palette": "limited", "colors": 12, "paths": 65,
        "corners": 45, "noise": 16, "ignoreWhite": True, "method": "abutting",
        "fills": True, "strokes": False, "shapes": False, "autoGrouping": False,
        "gradients": False,
    }}


def test_raster_fallback_argv_is_the_measured_contract() -> None:
    argv = render_argv(raster_fallback_step(), _vars("apparel"))
    assert argv == [
        "photocraft-cli", "run", "/in.png",
        "--cmd", "image.imageSize", "--params", '{"resolution":600,"resample":"lanczos"}',
        "--cmd", "edit.convertToProfile", "--params", '{"profile":"srgb"}',
        "--out", "/w/raster.png",
    ]


def test_apparel_trim_argv_is_the_measured_contract() -> None:
    argv = render_argv(ROUTES["apparel"].steps[0], _vars("apparel"))
    assert argv[:3] == ["photocraft-cli", "run", "/in.png"]
    assert argv[argv.index("--out"):] == ["--out", "/w/trimmed.png"]
    assert json.loads(argv[argv.index("--params", 3) + 1]) == {"basedOn": "transparent"}
    size_params = argv[argv.index("--params", argv.index("--params") + 1) + 1]
    assert json.loads(size_params) == {"width": 4200, "height": 4800, "resolution": 300, "resample": "lanczos"}


def test_every_rendered_command_id_is_in_the_catalogue() -> None:
    catalogues = {name: {row["id"] for row in json.loads(p.read_text(encoding="utf-8"))}
                  for name, p in CATALOGUES.items()}
    for product, route in ROUTES.items():
        variables = _vars(product)
        steps = [trace_step(route), *route.steps]
        for step in steps:
            if step.module not in catalogues:
                continue  # absent-app steps are deliberately refused by preflight
            try:
                argv = render_argv(step, variables)
            except ConfigError:
                continue  # a deliberately unnamed optional step
            commands = [argv[i + 1] for i, token in enumerate(argv) if token == "--cmd"]
            assert commands, f"{product}/{step.name} has no --cmd"
            for command in commands:
                assert command in catalogues[step.module], f"{product}/{step.name}: {command} not in {step.module} catalogue"


def test_missing_app_refuses_before_a_job_or_spawn(tmp_path: Path) -> None:
    settings = Settings(root=tmp_path, database_url="postgresql://unused")
    step = Step("missing", "effectcraft", ("effectcraft-cli", "--input", "/x"), ("/x",))
    with pytest.raises(PipelineError) as exc:
        preflight_tool(settings, step, list(step.argv))
    assert "E_TOOL_NOT_INSTALLED effectcraft" in str(exc.value)


def test_source_mutation_is_refused(tmp_path: Path) -> None:
    source = tmp_path / "input.png"
    source.write_bytes(b"original")
    good = __import__("hashlib").sha256(b"original").hexdigest()
    _assert_source_unchanged(source, good)  # no raise
    source.write_bytes(b"mutated")
    with pytest.raises(PipelineError) as exc:
        _assert_source_unchanged(source, good)
    assert "changed during the run" in str(exc.value)
