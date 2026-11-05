#!/usr/bin/env python3
"""Validate the command atlas against its catalogues.

Checks:
1. coverage.json totals equal the shipped catalogue totals;
2. every VectorCraft id in the intent map exists in VectorCraft (and no PhotoCraft-only id);
3. every PhotoCraft id in the intent map exists in PhotoCraft (and no VectorCraft-only id);
4. every group in either catalogue appears in group-index.md;
5. all family files referenced by group-index.md exist.

Exit 0 clean, 1 on any finding. Designed to run in CI or from the skill references.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
CAT = BASE / "catalogues"
FAMILIES = sorted(BASE.glob("vc-*.md")) + sorted(BASE.glob("pc-*.md"))


def ids_from(text: str) -> set[str]:
    return set(re.findall(r"`([a-z][a-z0-9]+\.[A-Za-z][A-Za-z0-9_.]+)`", text))


def main() -> int:
    problems: list[str] = []
    vc_ids: set[str] = set()
    pc_ids: set[str] = set()
    vc_groups: set[str] = set()
    pc_groups: set[str] = set()
    vc_total = 0
    pc_total = 0
    vc_found: set[str] = set()
    pc_found: set[str] = set()
    for app, name in (("vc", "vectorcraft-commands.json"), ("pc", "photocraft-commands.json")):
        path = CAT / name
        if not path.is_file():
            problems.append(f"missing catalogue {path}")
            continue
        rows = json.loads(path.read_text(encoding="utf-8"))
        ids = {row["id"] for row in rows}
        if app == "vc":
            vc_ids, vc_groups, vc_total = ids, {row["id"].split(".")[0] for row in rows}, len(rows)
        else:
            pc_ids, pc_groups, pc_total = ids, {row["id"].split(".")[0] for row in rows}, len(rows)

    coverage_path = BASE / "coverage.json"
    if coverage_path.is_file():
        coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        for app, label, expected in (("vc", "vectorcraft", vc_total), ("pc", "photocraft", pc_total)):
            got = coverage.get(label, {}).get("total")
            if expected is not None and got != expected:
                problems.append(f"coverage.json {label} total {got} != catalogue {expected}")

    intent_path = BASE / "00-intent-map.md"
    if intent_path.is_file():
        text = intent_path.read_text(encoding="utf-8")
        marker = "## PhotoCraft intents"
        if marker not in text:
            problems.append("intent map missing '## PhotoCraft intents' section")
        else:
            vc_text, pc_text = text.split(marker, 1)
            vc_found = {cid for cid in ids_from(vc_text) if cid.split(".")[0] in vc_groups}
            pc_found = {cid for cid in ids_from(pc_text) if cid.split(".")[0] in pc_groups}
            for cid in sorted(vc_found - vc_ids):
                where = "PhotoCraft-only" if cid in pc_ids else "absent"
                problems.append(f"intent map VectorCraft section uses {cid} ({where})")
            for cid in sorted(pc_found - pc_ids):
                where = "VectorCraft-only" if cid in vc_ids else "absent"
                problems.append(f"intent map PhotoCraft section uses {cid} ({where})")

    # Aliases in command_lookup.py must point at real catalogue ids.
    try:
        sys.path.insert(0, str(BASE))
        import command_lookup  # noqa: E402
        for alias, alias_ids in command_lookup.ALIASES.items():
            for cid in alias_ids:
                if cid not in vc_ids and cid not in pc_ids:
                    problems.append(f"command_lookup alias {alias!r} references unknown id {cid}")
    except Exception as exc:  # pragma: no cover - defensive
        problems.append(f"could not validate command_lookup aliases: {exc}")

    group_index = (BASE / "group-index.md").read_text(encoding="utf-8") if (BASE / "group-index.md").is_file() else ""
    for app, label, groups in (("vc", "VectorCraft", vc_groups), ("pc", "PhotoCraft", pc_groups)):
        for group in sorted(groups):
            if f"`{group}`" not in group_index:
                problems.append(f"group-index.md missing {label} group {group}")
    for family in re.findall(r"`((?:vc|pc)-[a-z0-9-]+\.md)`", group_index):
        if not (BASE / family).is_file():
            problems.append(f"group-index.md references missing file {family}")

    if problems:
        print(f"atlas check FAILED ({len(problems)} findings)")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print(f"atlas check OK: VC {vc_total} ids / {len(vc_groups)} groups; PC {pc_total} ids / {len(pc_groups)} groups")
    print(f"intent map ids: VC {len(vc_found)} checked, PC {len(pc_found)} checked; family files: {len(FAMILIES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
