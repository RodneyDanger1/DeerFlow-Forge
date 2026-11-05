#!/usr/bin/env python3
"""Standalone validator for DeerFlow Forge skills.

Thin command-line wrapper around install_skills.py: it scans every directory that
contains a SKILL.md, prints one row per skill, lists every failure, and exits
non-zero when any skill is invalid. It never writes to the runtime roots.

Usage:
    python validate_skills.py
    python validate_skills.py --json
    python validate_skills.py --repo <skills-tree> --require-hermes
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True

import install_skills as core


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="validate_skills.py",
        description="Validate every SKILL.md in a DeerFlow Forge skills tree.",
        epilog="Exit codes: 0 all selected skills are valid, 1 any skill is invalid.",
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="skills source tree (default: the directory containing _meta)",
    )
    parser.add_argument(
        "--dsh",
        type=Path,
        default=Path.home() / ".dsh" / "skills",
        help="DSH runtime root used for the parity columns (default: ~/.dsh/skills)",
    )
    parser.add_argument(
        "--hermes",
        type=Path,
        default=Path.home() / ".hermes" / "skills",
        help="Hermes runtime root used for the parity columns (default: ~/.hermes/skills)",
    )
    parser.add_argument(
        "--json", action="store_true", help="emit a machine-readable JSON report on stdout"
    )
    parser.add_argument(
        "--require-hermes",
        action="store_true",
        help="also require version, author, license, platforms and metadata.hermes",
    )
    parser.add_argument(
        "--skills",
        action="append",
        default=[],
        metavar="NAME[,NAME]",
        help="limit validation to named skills (repeatable, comma-separated)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"validate_skills.py (install_skills.py {core.INSTALLER_VERSION})",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    core.configured_stdio()
    args = build_parser().parse_args(argv)
    return core.run_check(
        repo_root=args.repo.resolve(),
        dsh_root=args.dsh.resolve(),
        hermes_root=args.hermes.resolve(),
        require_hermes=args.require_hermes,
        as_json=args.json,
        selected_names=args.skills,
    )


if __name__ == "__main__":
    sys.exit(main())
