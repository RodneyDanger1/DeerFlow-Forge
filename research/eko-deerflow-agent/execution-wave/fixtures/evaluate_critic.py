#!/usr/bin/env python3
"""Evaluate a composite visual-critic rule against the labelled defect corpus.

Calibration control: 17_clean_recompressed_jpeg92 (benign encoder noise on the same
reference). Every check is expressed relative to that control where possible.

Sub-checks
  C1 geometry   : de-speckled content bbox differs from the reference by > 2 px
  C2 specks     : alpha components smaller than 150 px exist
  C3 region RMSE: region RMSE / control region RMSE > 4
  C4 region SSIM: control region SSIM - case region SSIM > 0.05
  C5 white key  : white_residual_ratio > 0.002 (craft_trace gate)

Verdict = any sub-check fires. Writes critique.json.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

D = Path("/tmp/vd/fixtures")
META = json.loads((D / "metrics.json").read_text())
ANALYSIS = json.loads((D / "analysis.json").read_text())
REF = np.array(Image.open(D / "00_reference.png"), dtype=np.float64)


def despeckled_bbox(arr, min_area=150):
    a = arr[:, :, 3] > 127
    lab, n = ndimage.label(a, structure=np.ones((3, 3)))
    keep = np.zeros_like(a)
    if n:
        sizes = ndimage.sum(a, lab, range(1, n + 1))
        for i, s in enumerate(sizes, 1):
            if s >= min_area:
                keep |= (lab == i)
    ys, xs = np.where(keep)
    if ys.size == 0:
        return None
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]


REF_BOX = despeckled_bbox(REF)
REGION = {r["id"]: r for r in ANALYSIS["records"]}
METRICS = {r["id"]: r for r in META["records"]}
TOL = 2
RATIO_T = 4.0
SSIM_DROP_T = 0.05
WHITE_T = 0.002

rows = []
for cid, rec in METRICS.items():
    a = REGION[cid]
    var = np.array(Image.open(D / rec["file"]), dtype=np.float64)
    box = despeckled_bbox(var)
    shift = None if (box is None or REF_BOX is None) else [box[i] - REF_BOX[i] for i in range(4)]
    drop = a["control_region"]["region_ssim_rgb"] - a["region"]["region_ssim_rgb"]
    checks = {
        "C1_geometry": bool(shift and max(abs(v) for v in shift) > TOL),
        "C2_specks": bool(rec["metrics"]["gate_equiv"]["edge_specks"] > 0),
        "C3_region_rmse": bool(a["region_rmse_ratio_vs_benign"] > RATIO_T),
        "C4_region_ssim": bool(drop > SSIM_DROP_T),
        "C5_white_key": bool(rec["metrics"]["gate_equiv"]["white_residual_ratio"] > WHITE_T),
    }
    fired = [k for k, v in checks.items() if v]
    rows.append({
        "id": cid, "case": rec["case"], "class": rec["class"], "severity": rec["severity"],
        "is_defect": rec["gt_bbox"] is not None,
        "despeckled_bbox": box, "despeckled_shift_px": shift,
        "region_rmse_ratio": a["region_rmse_ratio_vs_benign"],
        "region_ssim": a["region"]["region_ssim_rgb"],
        "control_region_ssim": a["control_region"]["region_ssim_rgb"],
        "region_ssim_drop": round(float(drop), 6),
        "white_residual_ratio": rec["metrics"]["gate_equiv"]["white_residual_ratio"],
        "edge_specks": rec["metrics"]["gate_equiv"]["edge_specks"],
        "checks": checks, "fired": fired,
        "verdict": "DEFECT" if fired else "CLEAN",
        "correct": (bool(fired) == bool(rec["gt_bbox"])),
    })

defects = [r for r in rows if r["is_defect"]]
controls = [r for r in rows if not r["is_defect"]]
summary = {
    "composite_rule": {
        "checks": ["C1_geometry(>2px)", "C2_specks(components<150px)", "C3_region_rmse(ratio>4)", "C4_region_ssim(drop>0.05)", "C5_white_key(>0.002)"],
        "verdict": "DEFECT if any check fires",
        "defectsDetected": sum(1 for r in defects if r["verdict"] == "DEFECT"),
        "defectsTotal": len(defects),
        "controlsFlagged": sum(1 for r in controls if r["verdict"] == "DEFECT"),
        "controlsTotal": len(controls),
        "missed": [r["case"] for r in defects if r["verdict"] == "CLEAN"],
        "falsePositives": [r["case"] for r in controls if r["verdict"] == "DEFECT"],
    },
    "perCheckRecall": {
        c: {"detected": sum(1 for r in defects if r["checks"][c]), "controlsFlagged": sum(1 for r in controls if r["checks"][c])}
        for c in ("C1_geometry", "C2_specks", "C3_region_rmse", "C4_region_ssim", "C5_white_key")
    },
    "rows": rows,
}
(D / "critique.json").write_text(json.dumps(summary, indent=2))
print(json.dumps(summary["composite_rule"], indent=1))
print(json.dumps(summary["perCheckRecall"], indent=1))
print(f"\n{'id':<4}{'case':<32}{'verdict':<9}{'fired':<34}{'ratio':>7}{'ssimdrop':>9}{'specks':>7}")
for r in rows:
    print(f"{r['id']:<4}{r['case']:<32}{r['verdict']:<9}{','.join(r['fired']):<34}"
          f"{r['region_rmse_ratio']:>7.2f}{r['region_ssim_drop']:>9.4f}{r['edge_specks']:>7}")
bad = [r for r in rows if not r["correct"]]
print("\nincorrect:", bad if bad else "none")
