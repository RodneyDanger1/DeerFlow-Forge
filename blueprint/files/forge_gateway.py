#!/usr/bin/env python3
"""Forge Conductor skeleton: reference implementation of the tool gateway.

Executable contract only. No network, no Craft CLI, no database driver: the
repository and the executor are protocols so the logic can be tested with a
permitted test double (see test_forge_gateway.py).

Design rules proven by tests:
  * one canonical idempotency key per (episode, tool, params, input hashes)
  * a replayed key returns the stored result and never calls the executor again
  * role allowlists and command allowlists fail closed with E_* refusals
  * paths are resolved before the root comparison (no traversal)
  * refusals are terminal or retryable by code, not by caller opinion
  * a verdict is assembled from evidence rungs; missing evidence is unverified
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Literal, Protocol, Sequence

# --------------------------------------------------------------------------- states
EPISODE_STATES: tuple[str, ...] = (
    "intake", "briefed", "planned", "context_ready", "executing", "verifying",
    "critiquing", "needs_human", "paused", "accepted", "rejected", "refused",
    "failed", "cancelled", "quarantined",
)

# Edges mirror the seeded `forge_transition` table exactly (36 rows).
TRANSITIONS: frozenset[tuple[str, str]] = frozenset({
    ("intake", "briefed"), ("intake", "refused"), ("intake", "cancelled"),
    ("briefed", "planned"), ("briefed", "needs_human"), ("briefed", "refused"),
    ("briefed", "cancelled"),
    ("planned", "context_ready"), ("planned", "needs_human"), ("planned", "failed"),
    ("planned", "refused"),
    ("context_ready", "executing"), ("context_ready", "needs_human"),
    ("context_ready", "refused"), ("context_ready", "cancelled"),
    ("executing", "verifying"), ("executing", "paused"), ("executing", "failed"),
    ("executing", "needs_human"), ("executing", "quarantined"), ("executing", "cancelled"),
    ("verifying", "critiquing"), ("verifying", "rejected"), ("verifying", "needs_human"),
    ("verifying", "failed"),
    ("critiquing", "accepted"), ("critiquing", "rejected"), ("critiquing", "needs_human"),
    ("critiquing", "failed"),
    ("needs_human", "accepted"), ("needs_human", "rejected"), ("needs_human", "paused"),
    ("needs_human", "cancelled"),
    ("paused", "executing"), ("paused", "needs_human"), ("paused", "cancelled"),
})

TERMINAL_STATES: frozenset[str] = frozenset(
    {"accepted", "rejected", "refused", "failed", "cancelled", "quarantined"})

# Refusal taxonomy: terminal codes are never retried by any agent.
TERMINAL_REFUSALS: frozenset[str] = frozenset({
    "E_BRIEF_MISSING", "E_RIGHTS_MISSING", "E_ROOT_DENIED", "E_INPLACE_WRITE",
    "E_COMMAND_UNKNOWN", "E_APP_DRIFT", "E_CATALOGUE_STALE", "E_SOURCE_MUTATED",
    "E_UPSCALE_LIMIT", "E_TEXT_TRACE_FORBIDDEN", "E_WHITE_MODE_REFUSED",
    "E_BUDGET_EXCEEDED", "E_PUBLISH_NOT_APPROVED", "E_SURFACE_UNVERIFIABLE",
    "E_EVAL_EMPTY", "E_UNSUPPORTED_SURFACE", "E_EPISODE_NOT_FOUND",
})
RETRYABLE_REFUSALS: frozenset[str] = frozenset({
    "E_ARTIFACT_MISSING", "E_ARTIFACT_EMPTY", "E_DOCUMENT_STATE",
    "E_GATE_FAILED", "E_GATE_MISSING", "E_GATE_VACUOUS", "E_VISION_UNAVAILABLE",
    "E_CRITIQUE_UNGROUNDED", "E_TIMEOUT", "E_PARAM_REJECTED", "E_MEMORY_CONFLICT",
})


class PolicyError(RuntimeError):
    """A refusal raised before any side effect. Carries a named code."""

    def __init__(self, code: str, message: str, *, terminal: bool = True) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
        self.terminal = terminal


# --------------------------------------------------------------------------- keys
def canonical_json(value: Any) -> str:
    """Deterministic JSON for hashing. Rejects NaN/inf and non-UTF-8-safe input."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)


def sha256_hex(data: str | bytes) -> str:
    raw = data.encode("utf-8") if isinstance(data, str) else data
    return hashlib.sha256(raw).hexdigest()


def idempotency_key(episode_id: str, tool_id: str, params: dict[str, Any],
                    input_hashes: Sequence[str] = ()) -> str:
    """Stable key. Same logical call -> same key, regardless of dict order."""
    material = canonical_json({
        "episode_id": episode_id,
        "tool_id": tool_id,
        "params": params,
        "input_hashes": list(input_hashes),
        "schema": "forge-idem/1",
    })
    return "sha256:" + sha256_hex(material)


def validate_key(key: str) -> bool:
    return len(key) == 71 and key.startswith("sha256:") and all(
        c in "0123456789abcdef" for c in key[7:])


# ----------------------------------------------------------------------- transitions
def can_transition(current: str, target: str) -> bool:
    return (current, target) in TRANSITIONS


def next_state(current: str, target: str) -> str:
    if current not in EPISODE_STATES:
        raise PolicyError("E_EPISODE_STATE_UNKNOWN", current)
    if not can_transition(current, target):
        raise PolicyError("E_TRANSITION_ILLEGAL", f"{current} -> {target}")
    return target


# --------------------------------------------------------------------------- paths
def resolve_within(path: str, roots: Iterable[str]) -> Path:
    """Resolve symlinks and '..' BEFORE the root check; fail closed."""
    candidate = Path(os.path.realpath(os.path.abspath(path)))
    for root in roots:
        resolved_root = Path(os.path.realpath(os.path.abspath(root)))
        if candidate == resolved_root or resolved_root in candidate.parents:
            return candidate
    raise PolicyError("E_ROOT_DENIED", f"{path} is outside the declared roots")


# ------------------------------------------------------------------------ refusals
def is_terminal_refusal(code: str) -> bool:
    if code in TERMINAL_REFUSALS:
        return True
    if code in RETRYABLE_REFUSALS:
        return False
    return True  # unknown codes fail closed: terminal


def may_retry(code: str, attempt: int, max_attempts: int) -> bool:
    if is_terminal_refusal(code):
        return False
    return 0 < attempt < max_attempts


# ------------------------------------------------------------------------- verdicts
@dataclass(frozen=True)
class Evidence:
    """Rungs 1-6. Missing evidence is None, never a default of 'ok'."""
    process_ok: bool | None = None
    artifact_ok: bool | None = None
    gate_ok: bool | None = None
    gate_vacuous: bool = False
    source_mutated: bool = False
    render_ok: bool | None = None
    critique: Literal["pass", "pass_with_notes", "reject", "unverifiable"] | None = None
    human: Literal["accept", "reject"] | None = None
    human_required: bool = False


def build_verdict(ev: Evidence) -> tuple[str, list[str]]:
    """Return (verdict, reason_codes). Rules are order-independent and total."""
    reasons: list[str] = []
    if ev.source_mutated:
        return "reject", ["E_SOURCE_MUTATED"]
    if ev.process_ok is not True:
        return "unverified", ["E_ARTIFACT_MISSING"]
    if ev.artifact_ok is not True:
        return "reject", ["E_ARTIFACT_EMPTY"]
    if ev.gate_ok is None:
        return "unverified", ["E_GATE_MISSING"]
    if ev.gate_vacuous:
        return "reject", ["E_GATE_VACUOUS"]
    if ev.gate_ok is not True:
        return "reject", ["E_GATE_FAILED"]
    if ev.render_ok is not True:
        return "unverified", ["E_ARTIFACT_MISSING"]
    if ev.critique is None or ev.critique == "unverifiable":
        return "needs_human", ["E_VISION_UNAVAILABLE"]
    if ev.critique == "reject":
        return "needs_human", ["E_CRITIQUE_REJECT"]
    if ev.human_required:
        if ev.human is None:
            return "needs_human", ["E_HUMAN_REQUIRED"]
        if ev.human == "reject":
            return "reject", ["E_HUMAN_REJECT"]
    if ev.critique == "pass_with_notes":
        return "pass_with_notes", ["E_CRITIQUE_NOTES"]
    return "pass", []


# ------------------------------------------------------------------------- gateway
@dataclass(frozen=True)
class ToolSpec:
    tool_id: str
    allowed_roles: tuple[str, ...]
    allowed_cmds: tuple[str, ...]
    roots: tuple[str, ...]
    writes: bool = False
    timeout_s: int = 900


@dataclass(frozen=True)
class ToolCall:
    episode_id: str
    tool_id: str
    cmd_id: str | None
    params: dict[str, Any]
    paths: tuple[str, ...] = ()
    input_hashes: tuple[str, ...] = ()


@dataclass(frozen=True)
class ExecutionOutcome:
    exit_code: int
    duration_ms: int
    argv: tuple[str, ...]
    artifacts: tuple[dict[str, Any], ...] = ()
    refusal_code: str | None = None
    message: str = ""


@dataclass
class ToolResult:
    idempotency_key: str
    state: Literal["succeeded", "failed", "refused"]
    replayed: bool = False
    exit_code: int | None = None
    refusal_code: str | None = None
    artifacts: tuple[dict[str, Any], ...] = ()
    message: str = ""


class Executor(Protocol):
    def run(self, spec: ToolSpec, call: ToolCall) -> ExecutionOutcome: ...


class Repo(Protocol):
    def find(self, key: str) -> ToolResult | None: ...
    def store(self, key: str, result: ToolResult) -> None: ...


class InMemoryRepo:
    """Test double for the forge_tool_call table (unique key semantics)."""

    def __init__(self) -> None:
        self.rows: dict[str, ToolResult] = {}

    def find(self, key: str) -> ToolResult | None:
        return self.rows.get(key)

    def store(self, key: str, result: ToolResult) -> None:
        if key in self.rows:
            raise PolicyError("E_IDEMPOTENCY_CONFLICT", key)
        self.rows[key] = result


class Gateway:
    def __init__(self, specs: Sequence[ToolSpec], executor: Executor, repo: Repo,
                 roles: dict[str, str]) -> None:
        self._specs = {s.tool_id: s for s in specs}
        self._executor = executor
        self._repo = repo
        self._roles = roles            # token -> role

    def spec(self, tool_id: str) -> ToolSpec:
        try:
            return self._specs[tool_id]
        except KeyError:
            raise PolicyError("E_COMMAND_UNKNOWN", f"tool {tool_id}") from None

    def execute(self, call: ToolCall, token: str) -> ToolResult:
        spec = self.spec(call.tool_id)
        role = self._roles.get(token)
        if role is None or role not in spec.allowed_roles:
            return ToolResult(
                idempotency_key=idempotency_key(call.episode_id, call.tool_id,
                                                call.params, call.input_hashes),
                state="refused", refusal_code="E_ROLE_DENIED",
                message=f"role {role!r} may not call {call.tool_id}")

        if call.cmd_id is not None and call.cmd_id not in spec.allowed_cmds:
            raise PolicyError("E_COMMAND_UNKNOWN", f"cmd {call.cmd_id}")

        for path in call.paths:
            resolve_within(path, spec.roots)   # raises E_ROOT_DENIED before any effect

        key = idempotency_key(call.episode_id, call.tool_id, call.params, call.input_hashes)
        if not validate_key(key):
            raise PolicyError("E_KEY_SHAPE", key)
        prior = self._repo.find(key)
        if prior is not None:
            return ToolResult(**{**prior.__dict__, "replayed": True})

        outcome = self._executor.run(spec, call)
        if outcome.refusal_code:
            result = ToolResult(idempotency_key=key, state="refused",
                                refusal_code=outcome.refusal_code,
                                message=outcome.message)
        elif outcome.exit_code == 0:
            result = ToolResult(idempotency_key=key, state="succeeded",
                                exit_code=0, artifacts=outcome.artifacts)
        else:
            result = ToolResult(idempotency_key=key, state="failed",
                                exit_code=outcome.exit_code, message=outcome.message)
        self._repo.store(key, result)
        return result
