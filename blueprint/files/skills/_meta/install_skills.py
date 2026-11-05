#!/usr/bin/env python3
"""Cross-platform installer and validator for DeerFlow Forge skills.

Scans a skills tree (one directory per skill, each holding SKILL.md), validates
every SKILL.md against the skill contract, then copies byte-identical files to
the DSH and Hermes runtime skill roots. Copies are atomic, verified by SHA-256,
and never overwrite an existing file that differs unless --force is passed.

Python 3.8+ standard library only. Works on Windows, macOS and Linux.

Exit codes:
    0  every requested skill is valid and every requested target is current
    1  at least one requested skill failed validation (or the run could not start)
    2  at least one target was refused because it differs and --force was absent
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

INSTALLER_NAME = "install_skills.py"
INSTALLER_VERSION = "1.0.0"
SCHEMA_VERSION = 1

DESCRIPTION_MIN = 80
DESCRIPTION_MAX = 600
LINES_MIN = 40
LINES_MAX = 220

TARGET_NAMES = ("dsh", "hermes")
SUPPORT_DIRS = ("references", "assets")
TARGET_LABELS = {"dsh": "DSH", "hermes": "Hermes"}

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
BANNED_RE = re.compile(r"\b(TODO|FIXME|XXX|HACK|PLACEHOLDER|TBD)\b", re.IGNORECASE)

SECRET_PATTERNS: Tuple[Tuple[str, "re.Pattern[str]"], ...] = (
    ("private key block", re.compile(r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    (
        "credential assignment",
        re.compile(
            r"(?i)\b(?:api[_-]?key|secret|token|passwd|password)\s*[:=]\s*['\"]?"
            r"([A-Za-z0-9/+_\-]{16,})"
        ),
    ),
)

FILLER_WORDS = (
    "your",
    "example",
    "sample",
    "change",
    "replace",
    "insert",
    "redacted",
    "dummy",
    "xxxx",
    "todo",
    "here",
)


class SkillError(Exception):
    """A validation problem with a skill file."""


# ---------------------------------------------------------------------------
# Small utilities
# ---------------------------------------------------------------------------


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def configured_stdio() -> None:
    """Force UTF-8 on redirected stdout/stderr (Windows defaults to a legacy code page)."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write_bytes(path: Path, data: bytes) -> None:
    """Write data to path atomically (temp file in the same directory, then os.replace)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=str(path.parent)
    )
    temp_path = Path(temp_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    except BaseException:
        try:
            temp_path.unlink()
        except OSError:
            pass
        raise


def atomic_write_text(path: Path, text: str) -> None:
    atomic_write_bytes(path, text.encode("utf-8"))


def _line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


# ---------------------------------------------------------------------------
# Minimal YAML frontmatter reader (the subset used by agent skills)
# ---------------------------------------------------------------------------


def _indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _is_skippable(line: str) -> bool:
    stripped = line.strip()
    return not stripped or stripped.startswith("#")


def _prefix_of(line: str) -> str:
    return line[: len(line) - len(line.lstrip(" \t"))]


def _split_key(content: str) -> Tuple[str, str]:
    quote: Optional[str] = None
    for index, character in enumerate(content):
        if quote is not None:
            if character == quote:
                quote = None
            continue
        if character in ("'", '"'):
            quote = character
        elif character == ":":
            return content[:index].strip(), content[index + 1 :].strip()
    raise SkillError(f"frontmatter line is not a 'key: value' pair: {content!r}")


def _strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        inner = value[1:-1]
        if value[0] == '"':
            return (
                inner.replace('\\"', '"')
                .replace("\\\\", "\\")
                .replace("\\n", "\n")
                .replace("\\t", "\t")
            )
        return inner.replace("''", "'")
    return value


def _split_inline_list(text: str) -> List[str]:
    parts: List[str] = []
    buffer: List[str] = []
    quote: Optional[str] = None
    index = 0
    while index < len(text):
        character = text[index]
        if quote is not None:
            buffer.append(character)
            if character == quote:
                if quote == "'" and index + 1 < len(text) and text[index + 1] == "'":
                    buffer.append("'")
                    index += 1
                else:
                    quote = None
            elif character == "\\" and quote == '"' and index + 1 < len(text):
                buffer.append(text[index + 1])
                index += 1
        elif character in ("'", '"'):
            quote = character
            buffer.append(character)
        elif character == ",":
            parts.append("".join(buffer))
            buffer = []
        else:
            buffer.append(character)
        index += 1
    parts.append("".join(buffer))
    return [part.strip() for part in parts if part.strip()]


def _parse_scalar(text: str) -> Any:
    text = text.strip()
    if not text:
        return ""
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(part) for part in _split_inline_list(inner)]
    return _strip_quotes(text)


def _parse_block_scalar(
    lines: Sequence[str], start: int, parent_indent: int, style: str
) -> Tuple[str, int]:
    chunks: List[str] = []
    block_indent: Optional[int] = None
    index = start
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            chunks.append("")
            index += 1
            continue
        indent = _indent_of(line)
        if indent <= parent_indent:
            break
        if block_indent is None:
            block_indent = indent
        if indent < block_indent:
            break
        chunks.append(line[block_indent:])
        index += 1
    while chunks and not chunks[-1].strip():
        chunks.pop()
    if style.startswith(">"):
        return " ".join(chunk.strip() for chunk in chunks if chunk.strip()), index
    return "\n".join(chunks), index


def _parse_map(lines: Sequence[str], start: int, indent: int) -> Tuple[Dict[str, Any], int]:
    result: Dict[str, Any] = {}
    index = start
    while index < len(lines):
        line = lines[index]
        if _is_skippable(line):
            index += 1
            continue
        if "\t" in _prefix_of(line):
            raise SkillError("tab indentation in frontmatter is not supported")
        current_indent = _indent_of(line)
        if current_indent < indent:
            break
        if current_indent > indent:
            raise SkillError(f"unexpected indentation at frontmatter line {index + 2}")
        content = line.strip()
        if content.startswith("- "):
            raise SkillError(f"sequence item where a mapping key was expected at line {index + 2}")
        key, rest = _split_key(content)
        key = _strip_quotes(key)
        if not key:
            raise SkillError(f"empty frontmatter key at line {index + 2}")
        if key in result:
            raise SkillError(f"duplicate frontmatter key {key!r}")
        if rest in ("|", ">", "|-", ">-", "|+", ">+"):
            value, index = _parse_block_scalar(lines, index + 1, current_indent, rest)
        elif rest == "":
            lookahead = index + 1
            while lookahead < len(lines) and _is_skippable(lines[lookahead]):
                lookahead += 1
            if lookahead < len(lines) and _indent_of(lines[lookahead]) > current_indent:
                nested_indent = _indent_of(lines[lookahead])
                if lines[lookahead].strip().startswith("- "):
                    value, lookahead = _parse_list(lines, lookahead, nested_indent)
                else:
                    value, lookahead = _parse_map(lines, lookahead, nested_indent)
                index = lookahead
            else:
                value = None
                index += 1
        else:
            value = _parse_scalar(rest)
            index += 1
        result[key] = value
    return result, index


def _parse_list(lines: Sequence[str], start: int, indent: int) -> Tuple[List[Any], int]:
    items: List[Any] = []
    index = start
    while index < len(lines):
        line = lines[index]
        if _is_skippable(line):
            index += 1
            continue
        if "\t" in _prefix_of(line):
            raise SkillError("tab indentation in frontmatter is not supported")
        current_indent = _indent_of(line)
        if current_indent < indent:
            break
        if current_indent > indent:
            raise SkillError(f"unexpected indentation at frontmatter line {index + 2}")
        content = line.strip()
        if not content.startswith("- "):
            break
        item = content[2:].strip()
        if re.match(r"^[A-Za-z0-9_.-]+:\s", item) or item.endswith(":"):
            raise SkillError("mapping items inside frontmatter sequences are not supported")
        if item in ("|", ">", "|-", ">-", "|+", ">+"):
            raise SkillError("block scalars inside frontmatter sequences are not supported")
        items.append(_parse_scalar(item))
        index += 1
    return items, index


def parse_frontmatter(text: str) -> Tuple[Dict[str, Any], str]:
    """Return (frontmatter mapping, body) or raise SkillError."""
    lines = text.splitlines()
    if not lines:
        raise SkillError("SKILL.md is empty")
    if lines[0].strip() != "---":
        raise SkillError("file must start with a '---' frontmatter delimiter on line 1")
    closing: Optional[int] = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            closing = index
            break
    if closing is None:
        raise SkillError("frontmatter is not closed by a '---' delimiter")
    frontmatter_lines = lines[1:closing]
    body = "\n".join(lines[closing + 1 :])
    first = next((i for i, line in enumerate(frontmatter_lines) if not _is_skippable(line)), None)
    if first is None:
        raise SkillError("frontmatter block is empty")
    if _indent_of(frontmatter_lines[first]) != 0:
        raise SkillError("frontmatter keys must start at column 1")
    data, consumed = _parse_map(frontmatter_lines, first, 0)
    leftover = [line for line in frontmatter_lines[consumed:] if not _is_skippable(line)]
    if leftover:
        raise SkillError(f"unparsed frontmatter line: {leftover[0]!r}")
    if not isinstance(data, dict):
        raise SkillError("frontmatter did not parse to a mapping")
    return data, body


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


@dataclass
class SkillReport:
    dir_name: str
    path: Path
    raw: bytes = b""
    text: str = ""
    sha256: str = ""
    size_bytes: int = 0
    line_count: int = 0
    frontmatter: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    description_chars: int = 0
    version: str = ""
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.errors


def _looks_like_live_credential(value: str) -> bool:
    candidate = value.strip("'\"")
    lowered = candidate.lower()
    if any(word in lowered for word in FILLER_WORDS):
        return False
    if candidate.startswith(("<", "$", "{", "[")) or candidate.endswith(">"):
        return False
    if len(candidate) < 20:
        return False
    return any(c.isupper() for c in candidate) and any(c.isdigit() for c in candidate)


def _check_optional_fields(frontmatter: Dict[str, Any], report: SkillReport) -> None:
    version = frontmatter.get("version")
    if version is not None:
        if isinstance(version, str) and VERSION_RE.match(version):
            report.version = version
        else:
            report.warnings.append("'version' is not a semantic version string")

    author = frontmatter.get("author")
    if author is not None and not isinstance(author, str):
        report.warnings.append("'author' is not a string")

    license_value = frontmatter.get("license")
    if license_value is not None and not isinstance(license_value, str):
        report.warnings.append("'license' is not a string")

    platforms = frontmatter.get("platforms")
    if platforms is not None:
        if not isinstance(platforms, list):
            report.warnings.append("'platforms' is not a list")
        else:
            known = {"windows", "linux", "macos"}
            for platform in platforms:
                if not isinstance(platform, str):
                    report.warnings.append("'platforms' contains a non-string value")
                elif platform.lower() not in known:
                    report.warnings.append(f"unknown platform {platform!r}")

    metadata = frontmatter.get("metadata")
    if metadata is not None and not isinstance(metadata, dict):
        report.warnings.append("'metadata' is not a mapping")
    if isinstance(metadata, dict):
        hermes = metadata.get("hermes")
        if hermes is not None and not isinstance(hermes, dict):
            report.warnings.append("'metadata.hermes' is not a mapping")
        if isinstance(hermes, dict):
            for key in ("tags", "related_skills"):
                if key in hermes and not isinstance(hermes[key], list):
                    report.warnings.append(f"'metadata.hermes.{key}' is not a list")


def _check_hermes_superset(frontmatter: Dict[str, Any], report: SkillReport) -> None:
    for key in ("version", "author", "license", "platforms"):
        if not frontmatter.get(key):
            report.errors.append(f"Hermes frontmatter requires '{key}'")
    metadata = frontmatter.get("metadata")
    if not isinstance(metadata, dict):
        report.errors.append("Hermes frontmatter requires a 'metadata' mapping")
    elif not isinstance(metadata.get("hermes"), dict):
        report.errors.append("Hermes frontmatter requires 'metadata.hermes'")


def validate_skill(skill_dir: Path, require_hermes: bool = False) -> SkillReport:
    report = SkillReport(dir_name=skill_dir.name, path=skill_dir / "SKILL.md")
    try:
        raw = report.path.read_bytes()
    except OSError as exc:
        report.errors.append(f"cannot read SKILL.md: {exc}")
        return report
    report.raw = raw
    report.sha256 = sha256_bytes(raw)
    report.size_bytes = len(raw)
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        report.errors.append(f"SKILL.md is not valid UTF-8: {exc}")
        return report
    report.text = text
    report.line_count = len(text.splitlines())

    if not (LINES_MIN <= report.line_count <= LINES_MAX):
        report.errors.append(
            f"line count {report.line_count} is outside the required {LINES_MIN}-{LINES_MAX}"
        )

    frontmatter: Dict[str, Any] = {}
    try:
        frontmatter, _body = parse_frontmatter(text)
        report.frontmatter = frontmatter
    except SkillError as exc:
        report.errors.append(f"frontmatter: {exc}")

    name = frontmatter.get("name")
    if not isinstance(name, str) or not name.strip():
        report.errors.append("frontmatter is missing a 'name'")
    else:
        name = name.strip()
        if name != skill_dir.name:
            report.errors.append(
                f"name {name!r} does not match directory name {skill_dir.name!r}"
            )
        if not NAME_RE.match(name):
            report.warnings.append(f"name {name!r} is not lowercase-hyphenated")

    description = frontmatter.get("description")
    if not isinstance(description, str) or not description.strip():
        report.errors.append("frontmatter is missing a 'description'")
    else:
        report.description = description.strip()
        report.description_chars = len(report.description)
        if not (DESCRIPTION_MIN <= report.description_chars <= DESCRIPTION_MAX):
            report.errors.append(
                f"description length {report.description_chars} is outside the required "
                f"{DESCRIPTION_MIN}-{DESCRIPTION_MAX} characters"
            )

    seen_markers: Dict[str, int] = {}
    for match in BANNED_RE.finditer(text):
        marker = match.group(0)
        if marker not in seen_markers:
            seen_markers[marker] = _line_of(text, match.start())
    for marker, line in seen_markers.items():
        report.errors.append(f"unfinished-work marker {marker!r} at line {line}")

    for label, pattern in SECRET_PATTERNS:
        for match in pattern.finditer(text):
            if label == "credential assignment" and not _looks_like_live_credential(
                match.group(1)
            ):
                continue
            report.errors.append(f"possible {label} at line {_line_of(text, match.start())}")
            break

    _check_optional_fields(frontmatter, report)
    if require_hermes:
        _check_hermes_superset(frontmatter, report)

    if not any(line.startswith("# ") for line in text.splitlines()):
        report.warnings.append("no level-1 heading")

    return report


# ---------------------------------------------------------------------------
# Scanning and target state
# ---------------------------------------------------------------------------


def scan_repo(repo_root: Path, require_hermes: bool = False) -> Tuple[List[SkillReport], List[str]]:
    if not repo_root.is_dir():
        raise SkillError(f"skills source directory does not exist: {repo_root}")
    skill_dirs: List[Path] = []
    ignored: List[str] = []
    for entry in sorted(repo_root.iterdir(), key=lambda item: item.name.lower()):
        if not entry.is_dir():
            continue
        if (entry / "SKILL.md").is_file():
            skill_dirs.append(entry)
        else:
            ignored.append(entry.name)
    reports = [validate_skill(directory, require_hermes=require_hermes) for directory in skill_dirs]
    return reports, ignored


def select_reports(
    reports: Sequence[SkillReport], requested: Optional[Sequence[str]]
) -> Tuple[List[SkillReport], List[str]]:
    if not requested:
        return list(reports), []
    wanted: List[str] = []
    for chunk in requested:
        for piece in chunk.split(","):
            piece = piece.strip()
            if piece:
                wanted.append(piece)
    by_name = {report.dir_name: report for report in reports}
    unknown = [name for name in wanted if name not in by_name]
    selected = [report for report in reports if report.dir_name in set(wanted)]
    return selected, unknown


def target_state(name: str, target_root: Path, source_sha: str) -> Dict[str, Any]:
    target = target_root / name / "SKILL.md"
    state: Dict[str, Any] = {"path": str(target), "status": "missing", "sha256": None}
    if not target.exists():
        return state
    try:
        existing_sha = sha256_file(target)
    except OSError as exc:
        state["status"] = "unreadable"
        state["error"] = str(exc)
        return state
    state["sha256"] = existing_sha
    state["status"] = "current" if existing_sha == source_sha else "differs"
    return state


def iter_support_files(skill_dir: Path) -> Iterable[Tuple[Path, Path]]:
    """Yield (source, relative path) for reference/support files under a skill."""
    for dirname in SUPPORT_DIRS:
        base = skill_dir / dirname
        if not base.is_dir():
            continue
        for source in sorted(base.rglob("*")):
            if source.is_file() and not source.is_symlink():
                yield source, source.relative_to(skill_dir)


def sync_support_files(
    skill_dir: Path, skill_name: str, target_root: Path, force: bool
) -> Dict[str, Any]:
    """Mirror references/ (and assets/) into the installed skill directory."""
    result: Dict[str, Any] = {
        "files": 0,
        "created": 0,
        "updated": 0,
        "unchanged": 0,
        "conflicts": [],
        "errors": [],
    }
    for source, relative in iter_support_files(skill_dir):
        result["files"] += 1
        target = target_root / skill_name / relative
        try:
            source_sha = sha256_file(source)
            if target.exists():
                if sha256_file(target) == source_sha:
                    result["unchanged"] += 1
                    continue
                if not force:
                    result["conflicts"].append(str(relative))
                    continue
                action = "updated"
            else:
                action = "created"
            atomic_write_bytes(target, source.read_bytes())
            if sha256_file(target) != source_sha:
                raise OSError(f"post-write hash mismatch for {relative}")
            result[action] += 1
        except OSError as exc:
            result["errors"].append(f"{relative}: {exc}")
    return result


def install_to_target(report: SkillReport, target_root: Path, force: bool) -> Dict[str, Any]:
    state = target_state(report.dir_name, target_root, report.sha256)
    result: Dict[str, Any] = {
        "path": state["path"],
        "status": state["status"],
        "action": "skipped",
        "sha256": state.get("sha256"),
    }
    if state["status"] == "unreadable":
        result["action"] = "error"
        result["reason"] = state.get("error", "existing target is unreadable")
        return result
    if state["status"] == "differs" and not force:
        result["action"] = "conflict"
        result["existing_sha256"] = state.get("sha256")
        result["reason"] = "target exists with different content; pass --force to replace it"
        return result
    if state["status"] == "current":
        result["action"] = "unchanged"
    else:
        try:
            atomic_write_bytes(Path(state["path"]), report.raw)
            written_sha = sha256_file(Path(state["path"]))
        except OSError as exc:
            result["action"] = "error"
            result["reason"] = str(exc)
            return result
        if written_sha != report.sha256:
            result["action"] = "error"
            result["reason"] = f"post-write hash mismatch (wrote {written_sha[:12]})"
            return result
        result["sha256"] = written_sha
        result["status"] = "current"
        result["action"] = "created" if state["status"] == "missing" else "updated"
    support = sync_support_files(report.path.parent, report.dir_name, target_root, force)
    result["support"] = support
    if support["errors"]:
        result["action"] = "error"
        result["reason"] = "; ".join(support["errors"][:3])
    elif support["conflicts"]:
        result["action"] = "conflict"
        result["reason"] = (
            "reference files differ; pass --force to replace them: "
            + ", ".join(support["conflicts"][:3])
        )
    elif support["created"] or support["updated"]:
        result["status"] = "current"
        if result["action"] == "unchanged":
            result["action"] = "updated"
    return result


def summarize_actions(results: Iterable[Dict[str, Any]]) -> str:
    actions = {result.get("action") for result in results}
    if "error" in actions:
        return "error"
    if "conflict" in actions:
        return "conflict"
    if actions & {"created", "updated"}:
        return "installed"
    if actions and actions <= {"unchanged"}:
        return "unchanged"
    return "skipped"


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------


def _empty_manifest() -> Dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "skills": []}


def load_manifest(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return _empty_manifest()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        backup = path.with_name(f"{path.name}.corrupt-{utc_now().replace(':', '')}")
        try:
            path.replace(backup)
            notice = f"unreadable manifest moved to {backup.name}"
        except OSError:
            notice = "unreadable manifest could not be backed up"
        print(f"warning: {exc}; {notice}", file=sys.stderr)
        return _empty_manifest()
    if not isinstance(data, dict) or not isinstance(data.get("skills"), list):
        print("warning: manifest has an unexpected shape; starting a new one", file=sys.stderr)
        return _empty_manifest()
    return data


def update_manifest(
    manifest: Dict[str, Any],
    *,
    reports: Sequence[SkillReport],
    run_results: Dict[str, Dict[str, Any]],
    repo_root: Path,
    dsh_root: Path,
    hermes_root: Path,
    target_names: Sequence[str],
    timestamp: str,
) -> Dict[str, Any]:
    entries: Dict[str, Dict[str, Any]] = {}
    for entry in manifest.get("skills", []):
        if isinstance(entry, dict) and isinstance(entry.get("skill"), str):
            entries[entry["skill"]] = entry

    for report in reports:
        result = run_results[report.dir_name]
        entry = entries.get(report.dir_name, {})
        entry["skill"] = report.dir_name
        entry["source"] = str(report.path)
        entry["source_sha256"] = report.sha256
        entry["source_lines"] = report.line_count
        entry["description_chars"] = report.description_chars
        entry["valid"] = report.valid
        if report.errors:
            entry["errors"] = list(report.errors)
        else:
            entry.pop("errors", None)
        target_map = entry.get("targets")
        if not isinstance(target_map, dict):
            target_map = {}
        for target_name in target_names:
            target_result = dict(result["targets"].get(target_name, {}))
            target_result["timestamp"] = timestamp
            target_map[target_name] = target_result
        entry["targets"] = target_map
        entry["action"] = result["action"]
        entry["timestamp"] = timestamp
        entries[report.dir_name] = entry

    manifest.update(
        {
            "schema_version": SCHEMA_VERSION,
            "installer": {"name": INSTALLER_NAME, "version": INSTALLER_VERSION},
            "generated_at": timestamp,
            "source_root": str(repo_root),
            "targets": {"dsh": str(dsh_root), "hermes": str(hermes_root)},
            "skills": [entries[name] for name in sorted(entries)],
        }
    )
    return manifest


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def _target_counts(reports: Sequence[SkillReport], root: Path) -> Dict[str, int]:
    counts = {"current": 0, "missing": 0, "differs": 0, "unreadable": 0}
    for report in reports:
        status = target_state(report.dir_name, root, report.sha256)["status"]
        if status not in counts:
            status = "unreadable"
        counts[status] += 1
    return counts


def _skill_payload(
    report: SkillReport, dsh_root: Path, hermes_root: Path
) -> Dict[str, Any]:
    return {
        "skill": report.dir_name,
        "path": str(report.path),
        "valid": report.valid,
        "errors": list(report.errors),
        "warnings": list(report.warnings),
        "line_count": report.line_count,
        "description_chars": report.description_chars,
        "sha256": report.sha256,
        "size_bytes": report.size_bytes,
        "frontmatter": report.frontmatter,
        "targets": {
            "dsh": target_state(report.dir_name, dsh_root, report.sha256),
            "hermes": target_state(report.dir_name, hermes_root, report.sha256),
        },
    }


def _format_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    widths = [len(header) for header in headers]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))
    lines = [
        "  ".join(header.ljust(widths[index]) for index, header in enumerate(headers)).rstrip(),
        "  ".join("-" * width for width in widths),
    ]
    for row in rows:
        lines.append(
            "  ".join(cell.ljust(widths[index]) for index, cell in enumerate(row)).rstrip()
        )
    return "\n".join(lines)


def _print_failures(reports: Sequence[SkillReport], stream: Any) -> None:
    failed = [report for report in reports if report.errors]
    if not failed:
        return
    print("", file=stream)
    print("Failures:", file=stream)
    for report in failed:
        print(f"  {report.dir_name}", file=stream)
        for error in report.errors:
            print(f"    - {error}", file=stream)
    warned = [report for report in reports if report.warnings]
    if warned:
        print("", file=stream)
        print("Warnings:", file=stream)
        for report in warned:
            for warning in report.warnings:
                print(f"  {report.dir_name}: {warning}", file=stream)


def run_check(
    *,
    repo_root: Path,
    dsh_root: Path,
    hermes_root: Path,
    require_hermes: bool = False,
    as_json: bool = False,
    selected_names: Optional[Sequence[str]] = None,
) -> int:
    if not repo_root.is_dir():
        return _fatal(f"skills source directory does not exist: {repo_root}", as_json)
    reports, ignored = scan_repo(repo_root)
    selected, unknown = select_reports(reports, selected_names)
    if unknown:
        return _fatal(f"unknown skill name(s): {', '.join(unknown)}", as_json)
    if require_hermes:
        selected = [
            validate_skill(repo_root / report.dir_name, require_hermes=True)
            for report in selected
        ]

    valid = [report for report in selected if report.valid]
    invalid = [report for report in selected if not report.valid]
    timestamp = utc_now()

    if as_json:
        payload = {
            "mode": "check",
            "ok": not invalid,
            "generated_at": timestamp,
            "installer": {"name": INSTALLER_NAME, "version": INSTALLER_VERSION},
            "source_root": str(repo_root),
            "targets": {"dsh": str(dsh_root), "hermes": str(hermes_root)},
            "ignored_directories": ignored,
            "require_hermes": require_hermes,
            "summary": {
                "scanned": len(reports),
                "selected": len(selected),
                "valid": len(valid),
                "invalid": len(invalid),
                "failed": [report.dir_name for report in invalid],
                "invalid_unselected": [
                    report.dir_name
                    for report in reports
                    if not report.valid and report.dir_name not in {item.dir_name for item in selected}
                ],
                "targets": {
                    "dsh": _target_counts(valid, dsh_root),
                    "hermes": _target_counts(valid, hermes_root),
                },
            },
            "skills": [_skill_payload(report, dsh_root, hermes_root) for report in selected],
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0 if not invalid else 1

    print("DeerFlow Forge skill check")
    print(f"Source: {repo_root}")
    print(f"Targets: dsh={dsh_root} | hermes={hermes_root}")
    if require_hermes:
        print("Mode: require Hermes-superset frontmatter")
    print("")
    rows = []
    for report in selected:
        rows.append(
            [
                report.dir_name,
                str(report.line_count),
                str(report.description_chars),
                str(len(report.errors)),
                str(len(report.warnings)),
                "PASS" if report.valid else "FAIL",
            ]
        )
    print(_format_table(("SKILL", "LINES", "DESC", "ERRORS", "WARN", "STATUS"), rows))
    print("")
    print(
        f"{len(selected)} skills checked | {len(valid)} passed | {len(invalid)} failed"
    )
    dsh_counts = _target_counts(valid, dsh_root)
    hermes_counts = _target_counts(valid, hermes_root)
    print(
        "Runtime: "
        f"DSH current={dsh_counts['current']} missing={dsh_counts['missing']} "
        f"differs={dsh_counts['differs']} | "
        f"Hermes current={hermes_counts['current']} missing={hermes_counts['missing']} "
        f"differs={hermes_counts['differs']}"
    )
    if ignored:
        print(f"Directories without SKILL.md (not skills): {', '.join(ignored)}")
    _print_failures(selected, sys.stdout)
    return 0 if not invalid else 1


def _render_index(
    *,
    reports: Sequence[SkillReport],
    repo_root: Path,
    dsh_root: Path,
    hermes_root: Path,
    ignored: Sequence[str],
    timestamp: str,
) -> str:
    valid = [report for report in reports if report.valid]
    invalid = [report for report in reports if not report.valid]
    dsh_counts = _target_counts(valid, dsh_root)
    hermes_counts = _target_counts(valid, hermes_root)

    def summarize(text: str, limit: int = 150) -> str:
        flat = " ".join(text.split())
        if len(flat) <= limit:
            return flat
        cut = flat[: limit - 1].rstrip()
        if " " in cut:
            cut = cut.rsplit(" ", 1)[0]
        return cut + "\u2026"

    def cell(text: str) -> str:
        return summarize(text).replace("|", "\\|")

    lines: List[str] = []
    lines.append("# DeerFlow Forge skills index")
    lines.append("")
    lines.append(
        f"Generated **{timestamp}** by `{INSTALLER_NAME}` {INSTALLER_VERSION}. "
        "Counts and runtime states are computed at generation time; read this file "
        "instead of assuming a fixed catalogue."
    )
    lines.append("")
    lines.append(f"- Source of truth: `{repo_root}`")
    lines.append(f"- DSH runtime: `{dsh_root}`")
    lines.append(f"- Hermes runtime: `{hermes_root}`")
    lines.append("")
    lines.append(
        f"**{len(reports)} skill directories scanned | {len(valid)} installable | "
        f"{len(invalid)} failing validation.**"
    )
    lines.append("")
    lines.append(
        f"Runtime parity for installable skills: DSH current={dsh_counts['current']}, "
        f"missing={dsh_counts['missing']}, differs={dsh_counts['differs']}; "
        f"Hermes current={hermes_counts['current']}, missing={hermes_counts['missing']}, "
        f"differs={hermes_counts['differs']}."
    )
    lines.append("")
    lines.append("## Installable skills")
    lines.append("")
    if valid:
        lines.append("| Skill | What it does (trigger summary) | Lines | Version | DSH | Hermes | SHA-256 |")
        lines.append("|---|---|---|---|---|---|---|")
        for report in valid:
            dsh = target_state(report.dir_name, dsh_root, report.sha256)["status"]
            hermes = target_state(report.dir_name, hermes_root, report.sha256)["status"]
            version = report.version or "\u2014"
            lines.append(
                f"| `{report.dir_name}` | {cell(report.description)} | {report.line_count} | "
                f"{version} | {dsh} | {hermes} | `{report.sha256[:12]}` |"
            )
    else:
        lines.append("No skill currently passes every validation gate.")
    lines.append("")
    lines.append("## Present but not installable")
    lines.append("")
    if invalid:
        lines.append(
            "These directories contain a SKILL.md that fails at least one gate. "
            "They are never copied to a runtime."
        )
        lines.append("")
        lines.append("| Skill | Errors |")
        lines.append("|---|---|")
        for report in invalid:
            joined = "; ".join(report.errors).replace("|", "\\|")
            lines.append(f"| `{report.dir_name}` | {joined} |")
    else:
        lines.append("None at generation time.")
    lines.append("")
    if ignored:
        lines.append(
            "Directories without a SKILL.md (tooling, not skills): "
            + ", ".join(f"`{name}`" for name in ignored)
            + "."
        )
        lines.append("")
    lines.append("## Regenerate")
    lines.append("")
    lines.append("This file is generated; do not edit it by hand. Rebuild it and the runtime copies with:")
    lines.append("")
    lines.append("```powershell")
    lines.append(f'python "{repo_root / "_meta" / "install_skills.py"}" --targets both')
    lines.append("```")
    lines.append("")
    lines.append(
        "Use `--check` for validation only. Every copied SKILL.md is byte-identical "
        "to its source, so the source SHA-256 identifies both runtime copies."
    )
    lines.append("")
    return "\n".join(lines)


def run_install(
    *,
    repo_root: Path,
    dsh_root: Path,
    hermes_root: Path,
    target_names: Sequence[str],
    force: bool,
    require_hermes: bool = False,
    as_json: bool = False,
    selected_names: Optional[Sequence[str]] = None,
    manifest_path: Path,
    index_path: Path,
) -> int:
    if not repo_root.is_dir():
        return _fatal(f"skills source directory does not exist: {repo_root}", as_json)
    reports, ignored = scan_repo(repo_root)
    selected, unknown = select_reports(reports, selected_names)
    if unknown:
        return _fatal(f"unknown skill name(s): {', '.join(unknown)}", as_json)
    if not selected:
        return _fatal("no skills selected", as_json)
    if require_hermes:
        selected = [
            validate_skill(repo_root / report.dir_name, require_hermes=True)
            for report in selected
        ]

    timestamp = utc_now()
    roots = {"dsh": dsh_root, "hermes": hermes_root}
    run_results: Dict[str, Dict[str, Any]] = {}
    for report in selected:
        if not report.valid:
            skipped = {}
            for target_name in target_names:
                state = target_state(report.dir_name, roots[target_name], report.sha256)
                state["action"] = "skipped"
                state["reason"] = "source failed validation"
                skipped[target_name] = state
            run_results[report.dir_name] = {"action": "invalid", "targets": skipped}
            continue
        target_results = {
            target_name: install_to_target(report, roots[target_name], force)
            for target_name in target_names
        }
        run_results[report.dir_name] = {
            "action": summarize_actions(target_results.values()),
            "targets": target_results,
        }

    manifest = update_manifest(
        load_manifest(manifest_path),
        reports=selected,
        run_results=run_results,
        repo_root=repo_root,
        dsh_root=dsh_root,
        hermes_root=hermes_root,
        target_names=target_names,
        timestamp=timestamp,
    )
    index_text = _render_index(
        reports=reports,
        repo_root=repo_root,
        dsh_root=dsh_root,
        hermes_root=hermes_root,
        ignored=ignored,
        timestamp=timestamp,
    )
    try:
        atomic_write_text(manifest_path, json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
        atomic_write_text(index_path, index_text)
    except OSError as exc:
        return _fatal(f"could not write manifest or index: {exc}", as_json)

    valid = [report for report in selected if report.valid]
    invalid = [report for report in selected if not report.valid]
    action_counts = {"created": 0, "updated": 0, "unchanged": 0, "conflict": 0, "error": 0, "skipped": 0}
    for result in run_results.values():
        for target_result in result["targets"].values():
            action = target_result.get("action", "error")
            action_counts[action] = action_counts.get(action, 0) + 1
    conflicts = action_counts["conflict"] > 0
    errors = action_counts["error"] > 0

    if as_json:
        payload = {
            "mode": "install",
            "ok": not invalid and not conflicts and not errors,
            "generated_at": timestamp,
            "installer": {"name": INSTALLER_NAME, "version": INSTALLER_VERSION},
            "source_root": str(repo_root),
            "targets": {"dsh": str(dsh_root), "hermes": str(hermes_root)},
            "selected_targets": list(target_names),
            "force": force,
            "ignored_directories": ignored,
            "manifest": str(manifest_path),
            "index": str(index_path),
            "summary": {
                "scanned": len(reports),
                "selected": len(selected),
                "valid": len(valid),
                "invalid": len(invalid),
                "failed": [report.dir_name for report in invalid],
                "invalid_unselected": [
                    report.dir_name
                    for report in reports
                    if not report.valid and report.dir_name not in {item.dir_name for item in selected}
                ],
                "actions": action_counts,
            },
            "skills": [],
        }
        for report in selected:
            result = run_results[report.dir_name]
            skill_payload = _skill_payload(report, dsh_root, hermes_root)
            skill_payload["action"] = result["action"]
            for target_name in target_names:
                skill_payload["targets"][target_name].update(result["targets"][target_name])
            payload["skills"].append(skill_payload)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        if invalid:
            return 1
        return 2 if (conflicts or errors) else 0

    print(f"DeerFlow Forge skill install  ({timestamp})")
    print(f"Source: {repo_root}")
    print(f"Targets: {', '.join(TARGET_LABELS[name] for name in target_names)}")
    print("")
    for report in selected:
        result = run_results[report.dir_name]
        print(f"[{result['action']}] {report.dir_name}")
        for target_name in target_names:
            target_result = result["targets"][target_name]
            detail = target_result.get("action", "error")
            if target_result.get("reason"):
                detail += f" ({target_result['reason']})"
            print(f"    {TARGET_LABELS[target_name]}: {detail} -> {target_result['path']}")
    print("")
    print(
        f"{len(selected)} skills processed | {len(valid)} valid | {len(invalid)} invalid | "
        f"{action_counts['created']} created | {action_counts['updated']} updated | "
        f"{action_counts['unchanged']} unchanged | {action_counts['conflict']} conflicts | "
        f"{action_counts['error']} errors"
    )
    print(f"Manifest: {manifest_path}")
    print(f"Index: {index_path}")
    _print_failures(selected, sys.stdout)
    if invalid:
        return 1
    return 2 if (conflicts or errors) else 0


def _fatal(message: str, as_json: bool) -> int:
    if as_json:
        print(json.dumps({"ok": False, "error": message}, indent=2, ensure_ascii=False))
    else:
        print(f"error: {message}", file=sys.stderr)
    return 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=INSTALLER_NAME,
        description=(
            "Validate DeerFlow Forge SKILL.md files and install them into the DSH and "
            "Hermes runtime skill roots."
        ),
        epilog=(
            "Exit codes: 0 success, 1 validation or run failure, 2 refused conflicts. "
            "With --check nothing is written."
        ),
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
        help="DSH runtime skill root (default: ~/.dsh/skills)",
    )
    parser.add_argument(
        "--hermes",
        type=Path,
        default=Path.home() / ".hermes" / "skills",
        help="Hermes runtime skill root (default: ~/.hermes/skills)",
    )
    parser.add_argument(
        "--check", action="store_true", help="validate only; never write files"
    )
    parser.add_argument(
        "--json", action="store_true", help="emit a machine-readable JSON report on stdout"
    )
    parser.add_argument(
        "--targets",
        choices=("both", "dsh", "hermes"),
        default="both",
        help="runtime roots to write (default: both)",
    )
    parser.add_argument(
        "--skills",
        action="append",
        default=[],
        metavar="NAME[,NAME]",
        help="limit the run to named skills (repeatable, comma-separated)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="replace a target that already exists with different content",
    )
    parser.add_argument(
        "--require-hermes",
        action="store_true",
        help="also require version, author, license, platforms and metadata.hermes",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="manifest path (default: <repo>/_meta/manifest.json)",
    )
    parser.add_argument(
        "--index",
        type=Path,
        default=None,
        help="generated index path (default: <repo>/_meta/SKILLS-INDEX.md)",
    )
    parser.add_argument(
        "--version", action="version", version=f"{INSTALLER_NAME} {INSTALLER_VERSION}"
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    configured_stdio()
    args = build_parser().parse_args(argv)
    repo_root = args.repo.resolve()
    dsh_root = args.dsh.resolve()
    hermes_root = args.hermes.resolve()
    target_names = TARGET_NAMES if args.targets == "both" else (args.targets,)
    if args.check:
        return run_check(
            repo_root=repo_root,
            dsh_root=dsh_root,
            hermes_root=hermes_root,
            require_hermes=args.require_hermes,
            as_json=args.json,
            selected_names=args.skills,
        )
    manifest_path = (args.manifest or (repo_root / "_meta" / "manifest.json")).resolve()
    index_path = (args.index or (repo_root / "_meta" / "SKILLS-INDEX.md")).resolve()
    return run_install(
        repo_root=repo_root,
        dsh_root=dsh_root,
        hermes_root=hermes_root,
        target_names=target_names,
        force=args.force,
        require_hermes=args.require_hermes,
        as_json=args.json,
        selected_names=args.skills,
        manifest_path=manifest_path,
        index_path=index_path,
    )


if __name__ == "__main__":
    sys.exit(main())
