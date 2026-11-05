"""RED/GREEN tests for the craft_trace print-master gates.

These are synthetic cases, so they run without VectorCraft or the network. They pin
the behaviours that the owner-visible defects depended on:

  * a clean, fully transparent, hard-alpha master passes the ten checks;
  * a live retype overlay is required to claim text was retyped (ghost art in the
    text box must NOT satisfy the gate — that was the bug);
  * any residual white, or any isolated speck, fails the run;
  * the research tool imports without a placeholder / removed-skimage-API error.
"""
from __future__ import annotations

import importlib
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

from tools.craft_trace import verify


def _case(tmp: Path, *, with_overlay: bool = True, white_patch: bool = False,
          speck: bool = False) -> tuple[Image.Image, Image.Image, Image.Image, list[dict], dict, Path]:
    mapping = {"bbox": [0, 0, 1000, 1000], "canvas": [1000, 1000], "offset": (0, 0), "scale": 1.0}
    source = Image.new("RGBA", (1000, 1000), (0, 0, 0, 0))
    ImageDraw.Draw(source).rectangle([200, 200, 800, 800], fill=(40, 90, 60, 255))
    final = Image.new("RGBA", (1000, 1000), (0, 0, 0, 0))
    draw = ImageDraw.Draw(final)
    draw.rectangle([200, 200, 800, 800], fill=(40, 90, 60, 255))
    if white_patch:
        draw.rectangle([300, 300, 350, 350], fill=(255, 255, 255, 255))
    if speck:
        draw.rectangle([10, 10, 20, 20], fill=(40, 90, 60, 255))
    overlay = Image.new("RGBA", (1000, 1000), (0, 0, 0, 0))
    if with_overlay:
        ImageDraw.Draw(overlay).rectangle([420, 410, 580, 470], fill=(240, 230, 200, 255))
    spec = [{"box": [400, 400, 600, 480], "text": "TEST"}]
    svg = tmp / "plate.svg"
    svg.write_text('<svg xmlns="http://www.w3.org/2000/svg"><path fill="#285a3c"/><path fill="#f0e6c8"/></svg>', encoding="utf-8")
    return source, final, overlay, spec, mapping, svg


def _run(tmp: Path, **kwargs) -> dict:
    source, final, overlay, spec, mapping, svg = _case(tmp, **kwargs)
    return verify(source, final, (2400, 2400), 300, svg, spec, mapping, overlay)


def test_clean_master_passes_every_gate() -> None:
    with tempfile.TemporaryDirectory() as name:
        report = _run(Path(name))
    assert report["passed"] is True, report
    assert len(report["checks"]) == 10


def test_ghost_art_without_overlay_fails_text_gate() -> None:
    with tempfile.TemporaryDirectory() as name:
        report = _run(Path(name), with_overlay=False)
    assert report["passed"] is False
    assert report["checks"]["retyped_text_present"]["pass"] is False


def test_residual_white_fails() -> None:
    with tempfile.TemporaryDirectory() as name:
        report = _run(Path(name), white_patch=True)
    assert report["passed"] is False
    assert report["checks"]["white_residual_ratio"]["pass"] is False


def test_isolated_speck_fails() -> None:
    with tempfile.TemporaryDirectory() as name:
        report = _run(Path(name), speck=True)
    assert report["passed"] is False
    assert report["checks"]["edge_specks"]["pass"] is False


def test_research_tool_imports_without_removed_api() -> None:
    module = importlib.import_module("tools.artcraft")
    assert hasattr(module, "flatten_layers")
    assert "placeholder" not in Path(module.__file__).read_text(encoding="utf-8").lower()
