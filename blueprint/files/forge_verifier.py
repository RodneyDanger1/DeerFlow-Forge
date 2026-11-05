"""Fail-closed artifact + gate-report verifier (G3 / W3-A).

Pure consumer: no Craft process, no database, no publish. A report is not a pass
until the artifact bytes, declared hash, applicable checks and dimensions agree.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from PIL import Image


def _fail(code: str, detail: str, **extra: Any) -> dict[str, Any]:
    return {"ok": False, "verdict": "fail", "code": code, "detail": detail, **extra}


def inspect_png(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.is_file():
        return _fail("E_ARTIFACT_MISSING", f"{p} is not a file")
    try:
        data = p.read_bytes()
    except OSError as exc:
        return _fail("E_ARTIFACT_UNREADABLE", f"{p}: {exc}")
    if not data:
        return _fail("E_ARTIFACT_EMPTY", f"{p} is zero bytes")
    try:
        with Image.open(p) as img:
            width, height = img.size
            dpi = img.info.get("dpi")
    except Exception as exc:
        return _fail("E_ARTIFACT_FORMAT", f"{p}: {exc}")
    dpi_value = None
    if isinstance(dpi, (tuple, list)) and len(dpi) >= 1:
        dpi_value = float(dpi[0])
    elif isinstance(dpi, (int, float)):
        dpi_value = float(dpi)
    return {
        "ok": True,
        "path": str(p),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "width": width,
        "height": height,
        "dpi": dpi_value,
    }


def verify_gate_report(report: dict[str, Any], artifact_sha256: str) -> dict[str, Any]:
    if not isinstance(report, dict):
        return _fail("E_REPORT_INVALID", "report is not an object")
    checks = report.get("checks")
    if not isinstance(checks, dict) or not checks:
        return _fail("E_REPORT_INVALID", "report.checks must be a non-empty object")
    if report.get("ok") is not True or report.get("saved") is not True:
        return _fail("E_GATE_FAILED", "report ok/saved is not true")
    declared = report.get("output_sha256")
    if not isinstance(declared, str) or declared != artifact_sha256:
        return _fail("E_ARTIFACT_HASH_MISMATCH",
                     f"report={declared!r} actual={artifact_sha256!r}")
    applicable = [name for name, value in checks.items()
                  if not (isinstance(value, dict) and value.get("applicable") is False)]
    failed = [name for name, value in checks.items()
              if not (isinstance(value, dict) and value.get("applicable") is False)
              and value.get("pass") is not True]
    declared_count = report.get("applicable_checks")
    if declared_count != len(applicable):
        return _fail("E_GATE_COUNT_MISMATCH",
                     f"applicable_checks={declared_count!r} computed={len(applicable)}")
    if len(applicable) == 0:
        return _fail("E_GATE_VACUOUS", "no applicable checks")
    if failed:
        return _fail("E_GATE_CHECK_FAILED", "failed checks: " + ", ".join(failed),
                     failed=failed)
    return {"ok": True, "verdict": "pass", "applicable_checks": len(applicable),
            "failed": [], "output_sha256": artifact_sha256}


def verify_artifact(path: str | Path, report: dict[str, Any], *,
                    expected_px: tuple[int, int] | None = None,
                    expected_dpi: float | None = 300.0,
                    dpi_tolerance: float = 0.01) -> dict[str, Any]:
    info = inspect_png(path)
    if not info["ok"]:
        return info
    if info["width"] <= 0 or info["height"] <= 0:
        return _fail("E_ARTIFACT_FORMAT", "non-positive dimensions")
    gate = verify_gate_report(report, info["sha256"])
    if not gate["ok"]:
        return gate
    if expected_px is not None and (info["width"], info["height"]) != tuple(expected_px):
        return _fail("E_DIMENSION_MISMATCH",
                     f"actual={info['width']}x{info['height']} expected={expected_px}")
    if expected_dpi is not None:
        if info["dpi"] is None or abs(info["dpi"] - expected_dpi) > dpi_tolerance:
            return _fail("E_DPI_MISMATCH",
                         f"actual={info['dpi']!r} expected={expected_dpi}±{dpi_tolerance}")
    return {"ok": True, "verdict": "pass", **gate, "artifact": info}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Verify a Forge artifact against its gate report")
    ap.add_argument("--artifact", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--expected-px", default=None, help="WIDTHxHEIGHT")
    ap.add_argument("--expected-dpi", type=float, default=300.0)
    args = ap.parse_args(argv)
    try:
        report = json.loads(Path(args.report).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        result = _fail("E_REPORT_INVALID", f"{args.report}: {exc}")
    else:
        expected_px = None
        if args.expected_px:
            try:
                w, h = args.expected_px.lower().split("x")
                expected_px = (int(w), int(h))
            except ValueError:
                result = _fail("E_PARAM_REJECTED", "--expected-px must be WIDTHxHEIGHT")
                print(json.dumps(result, sort_keys=True))
                return 1
        result = verify_artifact(args.artifact, report, expected_px=expected_px,
                                 expected_dpi=args.expected_dpi)
    print(json.dumps(result, sort_keys=True))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
