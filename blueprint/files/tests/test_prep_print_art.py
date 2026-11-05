"""Tests for tools/prep_print_art.py — the art-to-print master tool.

Synthetic images only: a bright cyan subject on a dark ground (glow mode), black
ink on white (lineart/invert), a blank frame (must refuse) and a fake template
details file (geometry must come from the provider, never a guess).
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from tools.prep_print_art import main


def _glow_image(path: Path) -> None:
    image = Image.new("RGB", (160, 100), (6, 6, 10))
    for x in range(40, 120):
        for y in range(35, 65):
            image.putpixel((x, y), (40, 200, 255))
    image.save(path)


def _lineart_image(path: Path) -> None:
    image = Image.new("RGB", (160, 100), (250, 250, 250))
    for x in range(20, 140):
        for y in range(45, 55):
            image.putpixel((x, y), (10, 10, 10))
    image.save(path)


def test_glow_mask_removes_background_and_keeps_subject(tmp_path: Path) -> None:
    source = tmp_path / "glow.png"
    _glow_image(source)
    output = tmp_path / "master.png"
    report_path = tmp_path / "report.json"
    previews = tmp_path / "previews"
    code = main([
        "--input", str(source), "--output", str(output), "--mode", "glow",
        "--width-px", "1200", "--height-px", "1200",
        "--lum-floor", "60", "--lum-div", "60", "--cyan-floor", "20", "--cyan-div", "60",
        "--bloom", "0", "--preview-dir", str(previews), "--report-json", str(report_path),
    ])
    assert code == 0
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["canvas_px"] == [1200, 1200]
    assert report["dpi"] == 300
    assert report["coverage"] > 0.02
    master = Image.open(output)
    assert master.size == (1200, 1200) and master.mode == "RGBA"
    assert master.getpixel((5, 5))[3] == 0, "corner background must be transparent"
    assert master.getpixel((600, 600))[3] > 0, "subject must survive the mask"
    assert (previews / "master_black.jpg").exists()


def test_lineart_invert_keeps_dark_ink_on_light_ground(tmp_path: Path) -> None:
    source = tmp_path / "lineart.png"
    _lineart_image(source)
    output = tmp_path / "lineart_master.png"
    report_path = tmp_path / "report.json"
    code = main([
        "--input", str(source), "--output", str(output), "--mode", "lineart", "--invert",
        "--width-px", "900", "--height-px", "900",
        "--lum-floor", "50", "--lum-div", "60", "--report-json", str(report_path),
    ])
    assert code == 0
    report = json.loads(report_path.read_text(encoding="utf-8"))
    master = Image.open(output)
    assert master.getpixel((5, 5))[3] == 0, "white ground must become transparent"
    assert master.getpixel((450, 450))[3] > 0, "ink strokes must survive"
    assert report["coverage"] > 0.01


def test_blank_frame_is_refused_by_name(tmp_path: Path) -> None:
    source = tmp_path / "blank.png"
    Image.new("RGB", (120, 80), (5, 5, 5)).save(source)
    output = tmp_path / "should_not_exist.png"
    code = main([
        "--input", str(source), "--output", str(output), "--mode", "glow",
        "--width-px", "600", "--height-px", "600",
    ])
    assert code == 2
    assert not output.exists()


def test_geometry_comes_from_template_details(tmp_path: Path) -> None:
    source = tmp_path / "glow.png"
    _glow_image(source)
    details = tmp_path / "details.json"
    details.write_text(json.dumps([{
        "productId": "pro_test", "name": "Test Tee", "supportsBackendRendering": True,
        "productionMethod": "DTG", "areas": ["Front Large"],
        "areaGeometry": {"front_large": {"inchesWidth": 15, "inchesHeight": 18}},
    }]), encoding="utf-8")
    output = tmp_path / "master.png"
    code = main([
        "--input", str(source), "--output", str(output), "--mode", "glow",
        "--template", "pro_test", "--area", "front_large", "--details", str(details), "--dpi", "300",
        "--lum-floor", "60", "--lum-div", "60", "--cyan-floor", "20", "--cyan-div", "60",
    ])
    assert code == 0
    assert Image.open(output).size == (4500, 5400), "15x18in at 300dpi must be 4500x5400"


def test_unrenderable_template_is_refused(tmp_path: Path) -> None:
    source = tmp_path / "glow.png"
    _glow_image(source)
    details = tmp_path / "details.json"
    details.write_text(json.dumps([{
        "productId": "pro_knit", "name": "Knit", "supportsBackendRendering": False,
        "productionMethod": "KNITTING", "areas": ["Front"],
        "areaGeometry": {"front": {"inchesWidth": 12, "inchesHeight": 16}},
    }]), encoding="utf-8")
    code = main([
        "--input", str(source), "--output", str(tmp_path / "x.png"), "--mode", "glow",
        "--template", "pro_knit", "--area", "front", "--details", str(details),
        "--lum-floor", "60", "--lum-div", "60", "--cyan-floor", "20", "--cyan-div", "60",
    ])
    assert code == 2


def test_low_resolution_source_raises_an_upscale_warning(tmp_path: Path) -> None:
    source = tmp_path / "tiny.png"
    _glow_image(source)  # 160 px wide
    report_path = tmp_path / "report.json"
    output = tmp_path / "master.png"
    code = main([
        "--input", str(source), "--output", str(output), "--mode", "glow",
        "--width-px", "4500", "--height-px", "5400",
        "--lum-floor", "60", "--lum-div", "60", "--cyan-floor", "20", "--cyan-div", "60",
        "--report-json", str(report_path),
    ])
    assert code == 0
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["upscale_factor"] > 2.5
    assert any("upscaled" in warning for warning in report["warnings"])
