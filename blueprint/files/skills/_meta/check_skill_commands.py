#!/usr/bin/env python3
"""Semantic check: every command id quoted in a SKILL.md must exist in the installed catalogues.

Structural validation (validate_skills.py) cannot catch an invented command id. This does:
  * actual runnable steps — JSON {"command": "id"} / {"id": "id"} / `--cmd id` — must exist;
  * documented ids in backticks must exist unless the line marks them as absent/wrong/guessed;
  * ids are checked against `_meta/catalogues/vectorcraft-ids.json` (918) and
    `_meta/catalogues/photocraft-ids.txt` (965), snapshotted from the installed apps.

Usage: python _meta/check_skill_commands.py [--json]
Exit 0 when clean, 1 when any unknown id is found.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOGUES = ROOT / "_meta" / "catalogues"
VC = json.loads((CATALOGUES / "vectorcraft-ids.json").read_text(encoding="utf-8"))
VC_IDS = set(VC["ids"])
VC_GROUPS = set(VC["groups"])
PC_IDS = set((CATALOGUES / "photocraft-ids.txt").read_text(encoding="utf-8").split())
COMMAND_GROUPS = VC_GROUPS | {
    "filter", "image", "file", "paint", "path", "object", "text", "type", "document",
    "select", "layer", "swatch", "color", "artboard", "effect", "imageTrace", "addon",
}
IGNORE_WORDS = ("absent", "missing", "guessed", "wrong group", "not a ", "does not exist")


def scan(skill: Path) -> list[dict]:
    text = skill.read_text(encoding="utf-8")
    lines = text.splitlines()
    findings: list[dict] = []

    for pattern, kind in (
        (r'"command"\s*:\s*"([^"]+)"', "json-command"),
        (r'"id"\s*:\s*"([A-Za-z][A-Za-z0-9_.-]*)"', "json-id"),
        (r'--cmd\s+([A-Za-z][A-Za-z0-9_.-]*)', "cli-cmd"),
    ):
        for match in re.finditer(pattern, text):
            cid = match.group(1)
            if "." not in cid:
                continue
            if cid not in VC_IDS and cid not in PC_IDS:
                line = text.count("\n", 0, match.start()) + 1
                findings.append({"line": line, "id": cid, "kind": kind, "verdict": "UNKNOWN"})

    for match in re.finditer(r"`([a-z][a-z0-9]+\.[A-Za-z][A-Za-z0-9_.]+)`", text):
        cid = match.group(1)
        line = text.count("\n", 0, match.start()) + 1
        line_text = lines[line - 1] if line - 1 < len(lines) else ""
        if any(word in line_text.lower() for word in IGNORE_WORDS):
            continue
        if cid.split(".")[0] not in COMMAND_GROUPS:
            continue
        if cid not in VC_IDS and cid not in PC_IDS:
            findings.append({"line": line, "id": cid, "kind": "doc-id", "verdict": "UNKNOWN"})
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    skills = sorted(ROOT.glob("*/SKILL.md"))
    report = {skill.parent.name: scan(skill) for skill in skills}
    bad = sum(1 for findings in report.values() if findings)
    if args.json:
        print(json.dumps({"skills": len(skills), "with_unknown_ids": bad, "report": report}, indent=2))
        return 1 if bad else 0
    print(f"{len(skills)} skills scanned; {bad} with unknown command ids")
    for name, findings in report.items():
        if not findings:
            continue
        print(f"\n{name}")
        for finding in findings:
            print(f"  line {finding['line']}: {finding['id']} ({finding['kind']})")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
