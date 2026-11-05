import json
from pathlib import Path
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim

d = Path('/tmp/vd/fixtures')
meta = json.loads((d/'metrics.json').read_text())
ref_img = Image.open(d/'00_reference.png')
ref = np.array(ref_img, dtype=np.float64)
W, H = ref.shape[1], ref.shape[0]

def load(name):
    return np.array(Image.open(d/name), dtype=np.float64)

def content_bbox(arr):
    a = arr[:, :, 3] > 127
    ys, xs = np.where(a)
    if ys.size == 0:
        return None
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]

def region_stats(r, v, box, pad=12):
    x0 = max(0, box[0] - pad); y0 = max(0, box[1] - pad)
    x1 = min(W, box[2] + pad); y1 = min(H, box[3] + pad)
    a = r[y0:y1, x0:x1]; b = v[y0:y1, x0:x1]
    rmse = float(np.sqrt(np.mean((a - b) ** 2)) / 255.0)
    mae = float(np.mean(np.abs(a - b)) / 255.0)
    rgb_ssim = float(ssim(a[:, :, :3], b[:, :, :3], channel_axis=2, data_range=255))
    mask = (a[:, :, 3] > 127) | (b[:, :, 3] > 127)
    col = None
    if mask.any():
        da = a[:, :, :3][mask]; db = b[:, :, :3][mask]
        col = {"mean_abs_rgb_delta": round(float(np.mean(np.abs(da - db)) / 255.0), 6),
               "ref_mean_rgb": [round(float(x), 1) for x in da.mean(axis=0)],
               "var_mean_rgb": [round(float(x), 1) for x in db.mean(axis=0)]}
    return {"box": [x0, y0, x1, y1], "region_rmse": round(rmse, 6), "region_mae": round(mae, 6),
            "region_ssim_rgb": round(rgb_ssim, 6), "colour": col}

ctrl = load('17_clean_recompressed_jpeg92.png')
out = []
for rec in meta['records']:
    var = load(rec['file'])
    box = rec['gt_bbox'] or meta['regions']['art']
    rs = region_stats(ref, var, box)
    rc = region_stats(ref, ctrl, box)
    ratio = rs['region_rmse'] / max(rc['region_rmse'], 1e-9)
    cb_ref = content_bbox(ref); cb_var = content_bbox(var)
    out.append({
        "id": rec['id'], "case": rec['case'], "class": rec['class'], "severity": rec['severity'],
        "file": rec['file'], "gt_bbox": rec['gt_bbox'],
        "region": rs, "control_region": rc,
        "region_rmse_ratio_vs_benign": round(float(ratio), 3),
        "content_bbox_ref": cb_ref, "content_bbox_var": cb_var,
        "bbox_shift_px": None if (not cb_ref or not cb_var) else [cb_var[0]-cb_ref[0], cb_var[1]-cb_ref[1], cb_var[2]-cb_ref[2], cb_var[3]-cb_ref[3]],
        "global": {k: rec['metrics'][k] for k in ('global_ssim_rgb','global_rmse','global_mae','composite_rmse_black','composite_rmse_white')},
        "tile": rec['metrics']['tile'],
        "diff8": {"area_frac": rec['metrics']['diff_delta8']['area_frac'], "components": rec['metrics']['diff_delta8']['components']},
        "diff32": {"area_frac": rec['metrics']['diff_delta32']['area_frac'], "components": rec['metrics']['diff_delta32']['components']},
        "gate_equiv": rec['metrics']['gate_equiv'],
        "localization": rec['localization'],
    })

def rule(name, fn):
    det = [r for r in out if r['gt_bbox'] and fn(r)]
    fp = [r for r in out if not r['gt_bbox'] and fn(r)]
    miss = [r['case'] for r in out if r['gt_bbox'] and not fn(r)]
    return {"rule": name, "defectsDetected": len(det), "defectsTotal": sum(1 for r in out if r['gt_bbox']),
            "controlsFlagged": len(fp), "controlsTotal": sum(1 for r in out if not r['gt_bbox']),
            "missed": miss, "falsePositive": [r['case'] for r in fp]}

rules = [
    rule("R1_global_ssim_lt_0.99", lambda r: r['global']['global_ssim_rgb'] < 0.99),
    rule("R2_global_rmse_gt_0.01", lambda r: r['global']['global_rmse'] > 0.01),
    rule("R3_tile_min_ssim_lt_0.95", lambda r: r['tile']['ssim_min'] < 0.95),
    rule("R4_diff8_area_gt_0.001", lambda r: r['diff8']['area_frac'] > 0.001),
    rule("R5_edge_specks_gt_0", lambda r: r['gate_equiv']['edge_specks'] > 0),
    rule("R6_white_residual_gt_0.002", lambda r: r['gate_equiv']['white_residual_ratio'] > 0.002),
    rule("R7_composite_black_rmse_gt_0.01", lambda r: r['global']['composite_rmse_black'] > 0.01),
    rule("R8_region_ratio_gt_4", lambda r: r['region_rmse_ratio_vs_benign'] > 4.0),
    rule("R9_region_ratio_gt_4_and_region_rmse_gt_0.01", lambda r: r['region_rmse_ratio_vs_benign'] > 4.0 and r['region']['region_rmse'] > 0.01),
]
summary = {"cases": len(out), "defects": sum(1 for r in out if r['gt_bbox']), "controls": sum(1 for r in out if not r['gt_bbox']),
           "rules": rules, "records": out}
(d/'analysis.json').write_text(json.dumps(summary, indent=2))
print(json.dumps({"cases": summary['cases'], "rules": [{k: v[k] for k in ('rule','defectsDetected','controlsFlagged','missed','falsePositive')} for v in rules]}, indent=1))
print()
print(f"{'id':<4}{'case':<32}{'ratio':>8}{'regRMSE':>9}{'blackRMSE':>11}{'whiteRMSE':>11}{'shift':>10}")
for r in out:
    sh = r['bbox_shift_px']
    print(f"{r['id']:<4}{r['case']:<32}{r['region_rmse_ratio_vs_benign']:>8.2f}{r['region']['region_rmse']:>9.5f}"
          f"{r['global']['composite_rmse_black']:>11.5f}{r['global']['composite_rmse_white']:>11.5f}{str(sh):>10}")
