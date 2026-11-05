"""Post-step output validators. They are synchronous; the orchestrator runs them in a worker thread.

A validator raises ValidationError with a precise, short message. Validation failures are
deterministic, so the orchestrator never retries them (re-running the same tool gives the same file).
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Callable

from PIL import Image

Image.MAX_IMAGE_PIXELS = 400_000_000   # 4200x4800 print files are ~20 MP; this still blocks decompression bombs


class ValidationError(RuntimeError):
    pass


def parse_grid(spec: str) -> tuple[int, int]:
    """Factory grid spec 'COLSxROWS' (stitches x rows) -> (cols, rows)."""
    m = re.fullmatch(r"\s*(\d{1,5})\s*[xX]\s*(\d{1,5})\s*", spec or "")
    if not m:
        raise ValidationError(f"knit grid spec must look like 'COLSxROWS' (e.g. '112x140'), got {spec!r}")
    return int(m.group(1)), int(m.group(2))


def png_with_alpha(path: Path, cfg: dict[str, Any]) -> None:
    max_w, max_h = cfg.get("max_px", [4200, 4800])      # 14x16 in @ 300 dpi
    try:
        with Image.open(path) as im:
            im.load()
            if im.format != "PNG":
                raise ValidationError(f"{path.name}: expected PNG, got {im.format}")
            if im.width > max_w or im.height > max_h:
                raise ValidationError(f"{path.name}: {im.width}x{im.height}px exceeds {max_w}x{max_h}px print area")
            rgba = im.convert("RGBA")
            if rgba.getchannel("A").getbbox() is None:
                raise ValidationError(f"{path.name}: image is fully transparent")
    except OSError as exc:
        raise ValidationError(f"{path.name}: unreadable image ({exc})") from exc


def _bmp_header(path: Path) -> tuple[int, int, int, int]:
    """Return (width, height, bits_per_pixel, compression) straight from the BITMAPINFOHEADER.

    Pillow drops the alpha channel of 32-bit BMPs on read, so alpha must be judged from the header.
    """
    with open(path, "rb") as fh:
        head = fh.read(34)
    if len(head) < 34 or head[:2] != b"BM":
        raise ValidationError(f"{path.name}: not a BMP file")
    dib_size = int.from_bytes(head[14:18], "little")
    if dib_size < 40:
        raise ValidationError(f"{path.name}: unsupported legacy BMP header ({dib_size} bytes)")
    width = int.from_bytes(head[18:22], "little", signed=True)
    height = abs(int.from_bytes(head[22:26], "little", signed=True))
    bpp = int.from_bytes(head[28:30], "little")
    compression = int.from_bytes(head[30:34], "little")
    return width, height, bpp, compression


def knit_bmp(path: Path, cfg: dict[str, Any]) -> None:
    """Hard-edge, opaque, palette-limited, exact grid size, uncompressed."""
    cols, rows = parse_grid(str(cfg.get("knit_grid", "")))
    palette_limit = int(cfg.get("palette_limit", 6))
    width, height, bpp, compression = _bmp_header(path)
    if compression != 0:
        raise ValidationError(f"{path.name}: BMP must be uncompressed (BI_RGB), header says compression={compression}")
    if bpp not in (1, 4, 8, 24):
        raise ValidationError(
            f"{path.name}: {bpp}-bit BMP can carry an alpha channel; export 8-bit indexed (preferred) or 24-bit "
            "so every pixel is a 100% opaque thread color")
    if (width, height) != (cols, rows):
        raise ValidationError(f"{path.name}: grid is {width}x{height}, factory spec is {cols}x{rows}")
    try:
        with Image.open(path) as im:
            im.load()
            colors = im.convert("RGB").getcolors(maxcolors=palette_limit + 1)
    except OSError as exc:
        raise ValidationError(f"{path.name}: unreadable image ({exc})") from exc
    if colors is None:
        raise ValidationError(
            f"{path.name}: more than {palette_limit} distinct colors. Anti-aliased or gradient edge pixels "
            "produce extra colors; the factory yarn limit is a hard maximum")


def pdf_ok(path: Path, cfg: dict[str, Any]) -> None:
    with open(path, "rb") as fh:
        head = fh.read(8)
        fh.seek(0, 2)
        size = fh.tell()
        fh.seek(max(0, size - 2048))
        tail = fh.read()
    if not head.startswith(b"%PDF-"):
        raise ValidationError(f"{path.name}: missing %PDF header")
    if b"%%EOF" not in tail:
        raise ValidationError(f"{path.name}: missing %%EOF trailer (truncated write?)")


def mp4_ok(path: Path, cfg: dict[str, Any]) -> None:
    with open(path, "rb") as fh:
        head = fh.read(12)
    if len(head) < 12 or head[4:8] != b"ftyp":
        raise ValidationError(f"{path.name}: not an MP4/ISO-BMFF file (no ftyp box)")
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return   # container check only; install ffmpeg to also verify 1080x1920 / ~5 s
    want = cfg.get("reel", {"width": 1080, "height": 1920, "seconds": 5.0, "tolerance": 0.75})
    try:
        out = subprocess.run(
            [ffprobe, "-v", "error", "-select_streams", "v:0", "-show_entries",
             "stream=width,height:format=duration", "-of", "json", str(path)],
            capture_output=True, text=True, timeout=60, check=True).stdout
        info = json.loads(out)
        w, h = info["streams"][0]["width"], info["streams"][0]["height"]
        dur = float(info["format"]["duration"])
    except (subprocess.SubprocessError, KeyError, IndexError, ValueError) as exc:
        raise ValidationError(f"{path.name}: ffprobe could not read the video ({exc})") from exc
    if (w, h) != (want["width"], want["height"]):
        raise ValidationError(f"{path.name}: video is {w}x{h}, expected {want['width']}x{want['height']} (9:16)")
    if abs(dur - want["seconds"]) > want["tolerance"]:
        raise ValidationError(f"{path.name}: duration {dur:.2f}s, expected about {want['seconds']}s")


VALIDATORS: dict[str, Callable[[Path, dict[str, Any]], None]] = {
    "png_with_alpha": png_with_alpha,
    "knit_bmp": knit_bmp,
    "pdf": pdf_ok,
    "mp4": mp4_ok,
}
