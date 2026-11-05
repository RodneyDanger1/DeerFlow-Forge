"""Blind critic contract and verdict resolver (W3-B).

No vision model is called here. The critic is deliberately blinded to exit
codes, gate reports and operator claims; this module enforces that contract and
resolves gate/critic/human disagreement without allowing critic override.
"""
from __future__ import annotations

import json
import re
from typing import Any

VERDICTS = {"pass", "fail", "needs_human", "unverified"}
SEVERITIES = {"none", "minor", "major"}
DEFECT_KINDS = {"halo", "fringe", "ghost_text", "speck", "layout", "colour"}
BLIND_LEAKS = re.compile(r"\b(exit\s*code|exit\s*0|gate\s*report|gate\s*value|operator|pass\s*:\s*true)\b",
                         re.IGNORECASE)


def _invalid(code: str, detail: str) -> dict[str, Any]:
    return {"ok": False, "verdict": "unverified", "code": code, "detail": detail}


def _crop(value: Any) -> bool:
    return (isinstance(value, list) and len(value) == 4
            and all(isinstance(v, int) and not isinstance(v, bool) for v in value)
            and value[0] >= 0 and value[1] >= 0 and value[2] > 0 and value[3] > 0)


def validate_critique(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return _invalid("E_CRITIC_INVALID", "critique is not an object")
    verdict = data.get("verdict")
    if verdict not in VERDICTS:
        return _invalid("E_CRITIC_INVALID", f"verdict {verdict!r} is not one of {sorted(VERDICTS)}")
    dimensions = data.get("dimensions")
    if not isinstance(dimensions, list) or not dimensions:
        return _invalid("E_CRITIC_INVALID", "dimensions must be a non-empty list")
    for index, dim in enumerate(dimensions):
        if not isinstance(dim, dict):
            return _invalid("E_CRITIC_INVALID", f"dimension {index} is not an object")
        if not isinstance(dim.get("name"), str) or not dim["name"].strip():
            return _invalid("E_CRITIC_INVALID", f"dimension {index} has no name")
        score = dim.get("score")
        if not isinstance(score, int) or isinstance(score, bool) or not 1 <= score <= 5:
            return _invalid("E_CRITIC_INVALID", f"dimension {dim['name']} score must be 1..5")
        if not _crop(dim.get("crop")):
            return _invalid("E_CRITIC_INVALID", f"dimension {dim['name']} needs a positive crop")
        if not isinstance(dim.get("observation"), str) or not dim["observation"].strip():
            return _invalid("E_CRITIC_INVALID", f"dimension {dim['name']} needs an observation")
        if dim.get("severity") not in SEVERITIES:
            return _invalid("E_CRITIC_INVALID", f"dimension {dim['name']} severity invalid")
    defects = data.get("defects", [])
    if not isinstance(defects, list):
        return _invalid("E_CRITIC_INVALID", "defects must be a list")
    for index, defect in enumerate(defects):
        if not isinstance(defect, dict) or defect.get("kind") not in DEFECT_KINDS:
            return _invalid("E_CRITIC_INVALID", f"defect {index} has an unknown kind")
        if not _crop(defect.get("crop")):
            return _invalid("E_CRITIC_INVALID", f"defect {index} needs a positive crop")
        if defect.get("severity") not in SEVERITIES:
            return _invalid("E_CRITIC_INVALID", f"defect {index} severity invalid")
    confidence = data.get("confidence")
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0 <= confidence <= 1:
        return _invalid("E_CRITIC_INVALID", "confidence must be 0..1")
    if not isinstance(data.get("unseen"), list):
        return _invalid("E_CRITIC_INVALID", "unseen must be a list")
    if not isinstance(data.get("model_id"), str) or not data["model_id"].strip():
        return _invalid("E_CRITIC_INVALID", "model_id is required")
    if not isinstance(data.get("prompt_version"), str) or not data["prompt_version"].strip():
        return _invalid("E_CRITIC_INVALID", "prompt_version is required")
    if BLIND_LEAKS.search(json.dumps(data, ensure_ascii=False)):
        return _invalid("E_CRITIC_BLINDED", "critique mentions exit/gate/operator evidence")
    if verdict == "pass" and any(d.get("severity") == "major" for d in dimensions):
        return _invalid("E_CRITIC_CONTRADICTION", "pass with a major defect")
    if verdict == "fail" and not defects:
        return _invalid("E_CRITIC_CONTRADICTION", "fail requires at least one defect")
    return {"ok": True, "verdict": verdict, "dimensions": len(dimensions),
            "defects": len(defects), "confidence": float(confidence)}


def combine(gate_ok: bool | None, critique: Any | None, *, human: str | None = None) -> dict[str, Any]:
    if gate_ok is None:
        return {"verdict": "unverified", "reason": "E_GATE_MISSING"}
    if gate_ok is False:
        return {"verdict": "fail", "reason": "E_GATE_FAILED"}
    if critique is None:
        return {"verdict": "unverified", "reason": "E_CRITIC_MISSING"}
    checked = validate_critique(critique)
    if not checked["ok"]:
        return {"verdict": "unverified", "reason": checked["code"], "detail": checked["detail"]}
    if human == "reject":
        return {"verdict": "needs_human", "reason": "E_HUMAN_REJECT"}
    if critique["verdict"] == "fail":
        return {"verdict": "needs_human", "reason": "E_CRITIC_DISAGREES"}
    if critique["verdict"] == "needs_human":
        return {"verdict": "needs_human", "reason": "E_CRITIC_NEEDS_HUMAN"}
    if critique["verdict"] == "unverified":
        return {"verdict": "unverified", "reason": "E_CRITIC_UNVERIFIED"}
    if human == "accept":
        return {"verdict": "pass", "reason": "E_HUMAN_ACCEPT"}
    return {"verdict": "pass", "reason": "E_EVIDENCE_AGREES"}
