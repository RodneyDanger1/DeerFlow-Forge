#!/usr/bin/env python3
"""Visual-defect corpus + metric study for the Craft visual critic.

Generates one synthetic print-master reference, 15 labelled defect variants (7 classes,
two severities each plus one flat-colour blind-spot case) and 2 clean controls, then
measures for every pair:

  * global SSIM (RGB), global RMSE / MAE (RGBA, normalised)
  * tile-wise 64x64 SSIM (min, p05, count < 0.95) and tile RMSE (max, p95)
  * diff-mask statistics at delta>8 and delta>32 (area fraction, bbox, components)
  * gate-equivalent metrics using craft_trace's own definitions
    (white_residual_ratio, edge_specks, coverage)
  * composite RMSE on black and on white backgrounds

Writes PNG fixtures + metrics.json. Touches nothing outside --out.
Run on the VPS: /opt/pod-pipeline/.venv/bin/python vd_build.py --out /tmp/vd/fixtures
"""
from __future__ import annotations

import argparse
import io
import json
import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage
from skimage.metrics import structural_similarity as ssim

W, H = 1200, 1500
CX, CY = W // 2, 720
SEED = 20261105
TILE = 64
FONT_CANDIDATES = (
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
)
NAVY = (27, 42, 65, 255)
CREAM = (239, 230, 207, 255)
GOLD = (243, 201, 105, 255)
RUST = (228, 87, 46, 255)


def font(size: int):
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    raise SystemExit("no bold sans font found")


def build_reference() -> tuple[Image.Image, dict]:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([CX - 360, CY - 360, CX + 360, CY + 360], fill=NAVY)
    d.ellipse([CX - 330, CY - 330, CX + 330, CY + 330], fill=CREAM)
    inner = [CX - 300, CY - 300, CX + 300, CY + 300]
    d.ellipse(inner, fill=NAVY)
    f1, f2 = font(96), font(44)

    def centre(text, fnt, cy, fill):
        box = d.textbbox((0, 0), text, font=fnt)
        w, h = box[2] - box[0], box[3] - box[1]
        d.text((CX - w // 2 - box[0], cy - h // 2 - box[1]), text, font=fnt, fill=fill)
        return [CX - w // 2, cy - h // 2, CX + w // 2, cy + h // 2]

    word_box = centre("RIDGE", f1, CY - 40, CREAM)
    centre("FORGE", f2, CY + 55, GOLD)
    rule = [CX - 150, CY + 120, CX + 150, CY + 122]
    d.rectangle(rule, fill=CREAM)
    tri = [(CX - 60, CY + 200), (CX + 60, CY + 200), (CX, CY + 280)]
    d.polygon(tri, fill=RUST)
    tri_box = [min(p[0] for p in tri), min(p[1] for p in tri), max(p[0] for p in tri), max(p[1] for p in tri)]
    regions = {
        "art": list(img.getchannel("A").getbbox()),
        "wordmark": word_box,
        "rule": rule,
        "triangle": tri_box,
        "inner_disc": inner,
    }
    return img, regions


def expand(box, pad):
    return [int(box[0] - pad), int(box[1] - pad), int(box[2] + pad), int(box[3] + pad)]


def union(a, b):
    return [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]


# ---------------------------------------------------------------- defect generators


def make_white_fringe(ref, px, alpha):
    a = ref.getchannel("A")
    rim = ImageChops.subtract(a.filter(ImageFilter.MaxFilter(2 * px + 1)), a)
    layer = Image.new("RGBA", ref.size, (255, 255, 255, 0))
    layer.putalpha(rim.point(lambda v: int(v * alpha / 255)))
    return Image.alpha_composite(ref, layer), expand(ref.getchannel("A").getbbox(), px), {"px": px, "alpha": alpha}


def make_halo(ref, radius, peak):
    a = ref.getchannel("A").point(lambda v: 255 if v > 127 else 0)
    ring = ImageChops.subtract(a.filter(ImageFilter.GaussianBlur(radius)), a)
    layer = Image.new("RGBA", ref.size, CREAM[:3] + (0,))
    layer.putalpha(ring.point(lambda v: int(v * peak / 255)))
    return Image.alpha_composite(ref, layer), expand(ref.getchannel("A").getbbox(), radius), {"radius": radius, "peak": peak}


def make_ghost_text(ref, regions, dx, dy, alpha):
    layer = Image.new("RGBA", ref.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f1 = font(96)
    b = regions["wordmark"]
    d.text((b[0] + dx, b[1] + dy), "RIDGE", font=f1, fill=CREAM[:3] + (alpha,))
    return Image.alpha_composite(ref, layer), expand(regions["wordmark"], max(abs(dx), abs(dy)) + 2), {"dx": dx, "dy": dy, "alpha": alpha}


def make_speck(ref, regions, n, size):
    rng = np.random.default_rng(SEED)
    art = regions["art"]
    out = ref.copy()
    d = ImageDraw.Draw(out)
    pts = []
    while len(pts) < n:
        x = int(rng.integers(60, W - 60))
        y = int(rng.integers(60, H - 60))
        if art[0] - 70 <= x <= art[2] + 70 and art[1] - 70 <= y <= art[3] + 70:
            pts.append((x, y))
            d.rectangle([x, y, x + size - 1, y + size - 1], fill=(255, 255, 255, 255))
    box = [min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts) + size, max(p[1] for p in pts) + size]
    return out, box, {"count": n, "size": size}


def make_lost_stroke(ref, regions, frac):
    out = ref.copy()
    d = ImageDraw.Draw(out)
    x0, y0, x1, y1 = regions["rule"]
    cut = x1 if frac >= 1.0 else x0 + int((x1 - x0) * frac)
    d.rectangle([x0, y0, cut, y1], fill=(0, 0, 0, 0))
    return out, [x0, y0, cut, y1], {"fraction": frac}


def make_wrong_colour(ref, regions, kind, colour):
    out = ref.copy()
    if kind == "triangle":
        d = ImageDraw.Draw(out)
        cx, cy = CX, CY
        d.polygon([(cx - 60, cy + 200), (cx + 60, cy + 200), (cx, cy + 280)], fill=colour)
        box = regions["triangle"]
    else:  # flat inner disc: recolour only exact NAVY pixels inside the disc
        arr = np.array(out)
        x0, y0, x1, y1 = regions["inner_disc"]
        mask = np.zeros(arr.shape[:2], dtype=bool)
        mask[y0:y1, x0:x1] = True
        navy = np.all(arr[:, :, :3] == np.array(NAVY[:3]), axis=-1)
        sel = mask & navy
        arr[sel, :3] = colour[:3]
        arr[sel, 3] = 255
        out = Image.fromarray(arr, "RGBA")
        box = regions["inner_disc"]
    return out, list(box), {"kind": kind, "colour": list(colour[:3])}


def make_margin_shift(ref, regions, dx):
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.paste(ref, (dx, 0))
    return out, union(regions["art"], [regions["art"][0] + dx, regions["art"][1], regions["art"][2] + dx, regions["art"][3]]), {"dx": dx}


def make_margin_overflow(ref, regions, scale):
    art = ref.crop(regions["art"])
    nw, nh = int(round(art.width * scale)), int(round(art.height * scale))
    big = art.resize((nw, nh), Image.LANCZOS)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.alpha_composite(big, (CX - nw // 2, CY - nh // 2))
    box = [CX - nw // 2, CY - nh // 2, CX + nw // 2, CY + nh // 2]
    return out, box, {"scale": scale}


def make_recompressed(ref, fmt="jpeg", quality=92):
    rgb = ref.convert("RGB")
    buf = io.BytesIO()
    if fmt == "webp":
        rgb.save(buf, "WEBP", quality=quality)
    else:
        rgb.save(buf, "JPEG", quality=quality)
    buf.seek(0)
    j = Image.open(buf).convert("RGB").convert("RGBA")
    j.putalpha(ref.getchannel("A"))
    return j, None, {"format": fmt, "quality": quality}


# ---------------------------------------------------------------------- metrics


def to_arr(img):
    return np.array(img, dtype=np.float64)


def composite_rmse(ref, var, bg):
    a = ref[:, :, 3:4] / 255.0
    b = var[:, :, 3:4] / 255.0
    ra = ref[:, :, :3] * a + np.array(bg, dtype=np.float64) * (1 - a)
    va = var[:, :, :3] * b + np.array(bg, dtype=np.float64) * (1 - b)
    return float(np.sqrt(np.mean((ra - va) ** 2)) / 255.0)


def diff_stats(dmax, thr):
    m = dmax > thr
    area = int(m.sum())
    rec = {"threshold": thr, "area_px": area, "area_frac": round(area / m.size, 8), "bbox": None, "components": 0, "largest_bbox": None}
    if area == 0:
        return rec
    ys, xs = np.where(m)
    rec["bbox"] = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
    lab, n = ndimage.label(m, structure=np.ones((3, 3)))
    rec["components"] = int(n)
    sizes = ndimage.sum(m, lab, range(1, n + 1))
    k = int(np.argmax(sizes)) + 1
    ys2, xs2 = np.where(lab == k)
    rec["largest_bbox"] = [int(xs2.min()), int(ys2.min()), int(xs2.max()) + 1, int(ys2.max()) + 1]
    return rec


def iou(a, b):
    if not a or not b:
        return None
    x0, y0 = max(a[0], b[0]), max(a[1], b[1])
    x1, y1 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0, x1 - x0) * max(0, y1 - y0)
    ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return round(inter / ua, 4) if ua > 0 else None


def tile_metrics(ref, var, tile=TILE):
    h, w = ref.shape[:2]
    ssim_vals, rmse_vals = [], []
    for y in range(0, h - tile + 1, tile):
        for x in range(0, w - tile + 1, tile):
            a = ref[y:y + tile, x:x + tile, :3]
            b = var[y:y + tile, x:x + tile, :3]
            r = float(np.sqrt(np.mean((a - b) ** 2)) / 255.0)
            if r == 0.0:
                s = 1.0
            else:
                s = float(ssim(a, b, channel_axis=2, data_range=255, win_size=7))
                if not np.isfinite(s):
                    s = 0.0
            ssim_vals.append(s)
            rmse_vals.append(r)
    s = np.array(ssim_vals)
    r = np.array(rmse_vals)
    return {
        "tiles": int(s.size),
        "ssim_min": round(float(s.min()), 6),
        "ssim_p05": round(float(np.percentile(s, 5)), 6),
        "ssim_p50": round(float(np.percentile(s, 50)), 6),
        "tiles_below_0_95": int((s < 0.95).sum()),
        "tiles_below_0_99": int((s < 0.99).sum()),
        "rmse_max": round(float(r.max()), 6),
        "rmse_p95": round(float(np.percentile(r, 95)), 6),
    }


def gate_equiv(var):
    alpha_bool = var[:, :, 3] > 127
    rgb = var[:, :, :3]
    near_white = np.all(rgb >= 245, axis=-1) & alpha_bool
    coverage = float(alpha_bool.sum()) / alpha_bool.size
    lab, n = ndimage.label(alpha_bool, structure=np.ones((3, 3)))
    sizes = ndimage.sum(alpha_bool, lab, range(1, n + 1)) if n else np.array([])
    specks = int((sizes < 150).sum())
    return {
        "white_residual_ratio": round(float(near_white.sum() / max(1, alpha_bool.sum())), 6),
        "edge_specks": specks,
        "coverage": round(coverage, 6),
        "alpha_components": int(n),
    }


def measure(ref_img, var_img):
    ref, var = to_arr(ref_img), to_arr(var_img)
    rgb_ssim = float(ssim(ref[:, :, :3], var[:, :, :3], channel_axis=2, data_range=255))
    alpha_ssim = float(ssim(ref[:, :, 3], var[:, :, 3], data_range=255))
    d4 = ref - var
    rmse = float(np.sqrt(np.mean(d4 ** 2)) / 255.0)
    mae = float(np.mean(np.abs(d4)) / 255.0)
    dmax = np.abs(d4).max(axis=2)
    tiles = tile_metrics(ref, var)
    return {
        "global_ssim_rgb": round(rgb_ssim, 6),
        "global_ssim_alpha": round(alpha_ssim, 6),
        "global_rmse": round(rmse, 6),
        "global_mae": round(mae, 6),
        "tile": tiles,
        "diff_delta8": diff_stats(dmax, 8),
        "diff_delta32": diff_stats(dmax, 32),
        "gate_equiv": gate_equiv(var),
        "composite_rmse_black": round(composite_rmse(ref, var, (20, 19, 19)), 6),
        "composite_rmse_white": round(composite_rmse(ref, var, (255, 255, 255)), 6),
    }


# ------------------------------------------------------------------------- main


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/tmp/vd/fixtures")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    ref, regions = build_reference()
    ref.save(out / "00_reference.png")

    cases = [
        ("01", "white_fringe", "mild", lambda r: make_white_fringe(r, 1, 90)),
        ("02", "white_fringe", "strong", lambda r: make_white_fringe(r, 2, 235)),
        ("03", "halo", "mild", lambda r: make_halo(r, 8, 60)),
        ("04", "halo", "strong", lambda r: make_halo(r, 16, 140)),
        ("05", "ghost_text", "mild", lambda r: make_ghost_text(r, regions, 6, 6, 45)),
        ("06", "ghost_text", "strong", lambda r: make_ghost_text(r, regions, 14, 14, 110)),
        ("07", "speck", "mild", lambda r: make_speck(r, regions, 6, 2)),
        ("08", "speck", "strong", lambda r: make_speck(r, regions, 24, 3)),
        ("09", "lost_stroke", "full", lambda r: make_lost_stroke(r, regions, 1.0)),
        ("10", "lost_stroke", "partial", lambda r: make_lost_stroke(r, regions, 0.4)),
        ("11", "wrong_colour", "mild_triangle", lambda r: make_wrong_colour(r, regions, "triangle", (237, 226, 200, 255))),
        ("12", "wrong_colour", "strong_triangle", lambda r: make_wrong_colour(r, regions, "triangle", (255, 0, 255, 255))),
        ("13", "wrong_colour", "flat_inner_disc", lambda r: make_wrong_colour(r, regions, "disc", (72, 20, 92, 255))),
        ("14", "margin", "shift_40px", lambda r: make_margin_shift(r, regions, 40)),
        ("15", "margin", "overflow_8pct", lambda r: make_margin_overflow(r, regions, 1.08)),
    ]

    records = []
    controls = [
        ("16", "clean", "identical", lambda r: (r.copy(), None, {})),
        ("17", "clean", "recompressed_jpeg92", lambda r: make_recompressed(r, "jpeg", 92)),
        ("18", "clean", "recompressed_jpeg75", lambda r: make_recompressed(r, "jpeg", 75)),
        ("19", "clean", "recompressed_webp80", lambda r: make_recompressed(r, "webp", 80)),
    ]

    for cid, cls, sev, fn in cases:
        var, gt, params = fn(ref)
        path = out / f"{cid}_{cls}_{sev}.png"
        var.save(path)
        m = measure(ref, var)
        rec = {
            "id": cid,
            "case": f"{cls}/{sev}",
            "class": cls,
            "severity": sev,
            "file": path.name,
            "params": params,
            "gt_bbox": gt,
            "metrics": m,
            "localization": {
                "iou_delta8": iou(m["diff_delta8"]["bbox"], gt),
                "iou_delta32": iou(m["diff_delta32"]["bbox"], gt),
                "iou_largest_component": iou(m["diff_delta32"]["largest_bbox"], gt),
            },
        }
        records.append(rec)

    for cid, cls, sev, fn in controls:
        var, gt, params = fn(ref)
        path = out / f"{cid}_{cls}_{sev}.png"
        var.save(path)
        m = measure(ref, var)
        records.append({
            "id": cid, "case": f"{cls}/{sev}", "class": cls, "severity": sev,
            "file": path.name, "params": params, "gt_bbox": None, "metrics": m,
            "localization": {"iou_delta8": None, "iou_delta32": None, "iou_largest_component": None},
        })

    (out / "metrics.json").write_text(json.dumps({"seed": SEED, "canvas": [W, H], "tile": TILE,
                                                  "reference": "00_reference.png",
                                                  "regions": regions, "records": records}, indent=2))
    # compact stdout table
    print(f"{'id':<4}{'case':<34}{'gSSIM':>8}{'gRMSE':>9}{'tmin':>8}{'tmaxRMSE':>10}{'d8frac':>10}{'d32comp':>8}{'specks':>8}{'wr':>8}")
    for r in records:
        m = r["metrics"]
        print(f"{r['id']:<4}{r['case']:<34}{m['global_ssim_rgb']:>8.5f}{m['global_rmse']:>9.5f}"
              f"{m['tile']['ssim_min']:>8.4f}{m['tile']['rmse_max']:>10.5f}"
              f"{m['diff_delta8']['area_frac']:>10.6f}{m['diff_delta32']['components']:>8}"
              f"{m['gate_equiv']['edge_specks']:>8}{m['gate_equiv']['white_residual_ratio']:>8.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
