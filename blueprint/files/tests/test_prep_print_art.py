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


def test_white_mode_removes_every_white_including_enclosed(tmp_path: Path) -> None:
    """Owner's rule: white is transparent everywhere, enclosed whites included."""
    source = tmp_path / "white_ground.png"
    image = Image.new("RGB", (160, 100), (255, 255, 255))
    for x in range(30, 130):
        for y in range(20, 80):
            image.putpixel((x, y), (40, 100, 60))  # green panel
    for x in range(60, 100):  # enclosed white shape
        for y in range(40, 60):
            image.putpixel((x, y), (255, 255, 255))
    image.save(source)
    output = tmp_path / "white_master.png"
    report_path = tmp_path / "report.json"
    code = main([
        "--input", str(source), "--output", str(output), "--mode", "white",
        "--width-px", "900", "--height-px", "900", "--bloom", "0", "--report-json", str(report_path),
    ])
    assert code == 0
    master = Image.open(output)
    assert master.getpixel((5, 5))[3] == 0, "outer white background must become transparent"
    assert master.getpixel((450, 450))[3] == 0, "white enclosed by the subject is still white, so it must be transparent"


def test_white_mode_keeps_saturated_cream_lettering(tmp_path: Path) -> None:
    """A cream/tan wordmark is not white and must survive the white key."""
    source = tmp_path / "cream.png"
    image = Image.new("RGB", (160, 100), (255, 255, 255))
    for x in range(40, 120):
        for y in range(40, 70):
            image.putpixel((x, y), (239, 230, 207))  # cream lettering
    image.save(source)
    output = tmp_path / "cream_master.png"
    code = main([
        "--input", str(source), "--output", str(output), "--mode", "white",
        "--width-px", "900", "--height-px", "900", "--bloom", "0",
    ])
    assert code == 0
    master = Image.open(output)
    assert master.getpixel((450, 450))[3] > 0, "cream lettering must not be keyed out"
    assert master.getpixel((5, 5))[3] == 0


def test_white_mode_drops_isolated_cream_specks(tmp_path: Path) -> None:
    """Paper-texture highlights share the lettering's chroma; small specks must die."""
    source = tmp_path / "speck.png"
    image = Image.new("RGB", (160, 100), (255, 255, 255))
    for x in range(40, 90):  # large cream block (kept)
        for y in range(40, 70):
            image.putpixel((x, y), (239, 230, 207))
    for x in range(130, 132):  # 2x2 cream speck (dropped)
        for y in range(10, 12):
            image.putpixel((x, y), (239, 230, 207))
    image.save(source)
    output = tmp_path / "speck_master.png"
    report = tmp_path / "report.json"
    code = main([
        "--input", str(source), "--output", str(output), "--mode", "white",
        "--width-px", "900", "--height-px", "900", "--bloom", "0", "--min-component", "24",
        "--report-json", str(report),
    ])
    assert code == 0
    master = Image.open(output)
    assert master.getpixel((450, 450))[3] > 0, "the large cream block must survive"
    bbox = json.loads(report.read_text(encoding="utf-8"))["subject_bbox"]
    assert (bbox[2] - bbox[0]) < 70, "the isolated speck must not expand the subject bbox"


def test_white_flood_mode_keeps_enclosed_whites(tmp_path: Path) -> None:
    """The explicit flood variant is still available when enclosed whites must survive."""
    source = tmp_path / "white_ground.png"
    image = Image.new("RGB", (160, 100), (255, 255, 255))
    for x in range(30, 130):
        for y in range(20, 80):
            image.putpixel((x, y), (40, 100, 60))
    for x in range(60, 100):
        for y in range(40, 60):
            image.putpixel((x, y), (255, 255, 255))
    image.save(source)
    output = tmp_path / "flood_master.png"
    code = main([
        "--input", str(source), "--output", str(output), "--mode", "white-flood",
        "--width-px", "900", "--height-px", "900", "--bloom", "0",
    ])
    assert code == 0
    master = Image.open(output)
    assert master.getpixel((5, 5))[3] == 0
    assert master.getpixel((450, 450))[3] > 0, "flood mode keeps enclosed white"


def test_alpha_mode_uses_the_input_alpha_channel(tmp_path: Path) -> None:
    source = tmp_path / "precut.png"
    image = Image.new("RGBA", (160, 100), (0, 0, 0, 0))
    for x in range(50, 110):
        for y in range(30, 70):
            image.putpixel((x, y), (200, 120, 40, 255))
    image.save(source)
    output = tmp_path / "precut_master.png"
    report_path = tmp_path / "report.json"
    code = main([
        "--input", str(source), "--output", str(output), "--mode", "alpha",
        "--width-px", "800", "--height-px", "800", "--bloom", "0", "--report-json", str(report_path),
    ])
    assert code == 0
    master = Image.open(output)
    assert master.getpixel((5, 5))[3] == 0
    assert master.getpixel((400, 400))[3] > 0


def test_auto_picks_white_mode_for_a_white_bordered_image(tmp_path: Path) -> None:
    source = tmp_path / "white_ground.png"
    image = Image.new("RGB", (160, 100), (255, 255, 255))
    for x in range(40, 120):
        for y in range(30, 70):
            image.putpixel((x, y), (30, 80, 50))
    image.save(source)
    report_path = tmp_path / "report.json"
    code = main([
        "--input", str(source), "--output", str(tmp_path / "master.png"), "--mode", "auto",
        "--width-px", "600", "--height-px", "600", "--report-json", str(report_path),
    ])
    assert code == 0
    assert json.loads(report_path.read_text(encoding="utf-8"))["mode"] == "white"


def test_print_width_in_controls_physical_art_size(tmp_path: Path) -> None:
    source = tmp_path / "glow.png"
    _glow_image(source)
    report_path = tmp_path / "report.json"
    code = main([
        "--input", str(source), "--output", str(tmp_path / "master.png"), "--mode", "glow",
        "--width-px", "4500", "--height-px", "5400", "--dpi", "300", "--print-width-in", "10",
        "--lum-floor", "60", "--lum-div", "60", "--cyan-floor", "20", "--cyan-div", "60",
        "--report-json", str(report_path),
    ])
    assert code == 0
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["usable_width_px"] == 3000, "10 inches at 300 DPI is 3000 px"
    assert any("upscaled" in warning for warning in report["warnings"])
