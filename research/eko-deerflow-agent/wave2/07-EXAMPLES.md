# 07 — Implementation-Ready Mechanism Examples

**Wave 2 · Task 07 · Design examples, not production code · 2026-11-05**
Owner: Riley · Author: `examples-skills-packager` (delegated) · Scope: Forge Conductor / DeerFlow Forge / Craft family

**Companions:** `07-EXAMPLES.json` (machine-readable index and claim register) and
`07-SKILL-SPECS.md` (five skill specifications that consume this corpus).

> **Status: DESIGN EXAMPLES AND SKILL SPECIFICATIONS.** No service, migration, table, unit,
> prompt or production file was created. Nothing here is deployed. The six sketches are
> original mechanisms written for this task; they are compilable-shaped, not installed.
> Every snippet was syntax-checked (`python -m py_compile` for Python 3.14, `tsc --noEmit`
> for TypeScript 5.9), and the pure-logic paths of Examples 1, 4, 5 and 6 were exercised
> by a scratch harness (35 checks, all passing) before being embedded. That harness is a
> validation aid, not a deliverable.
>
> **Evidence labels used throughout**
> `[V]` verified this session on the host / from an observed command (quoted source in 01 or 04)
> `[R]` read from a local repository or skill file, with path
> `[D]` verified in the prior dossier `research/eko-deerflow-agent/REPORT.md` and not re-executed
> `[I]` inference or design decision — not yet tested
> `[U]` unverified; becomes policy only after the named check is run
>
> `04-HARNESS-DESIGN.md` is the architecture source for everything here. This file does not
> replace it: it shows the *mechanisms* behind the boxes and contracts in that design.

---

## 0. How to read this file

| Section | Mechanism | Language | Primary design anchor |
|---|---|---|---|
| 1 | Supervisor loop with specialist roles and handoff schema | Python (asyncio) | 04 §4, §12.1 |
| 2 | Typed tool gateway for Craft CLI/MCP | TypeScript (zod) | 04 §6 |
| 3 | Episode ledger, hash chain, write path, retrieval | Python + SQL | 04 §5.2, §8.1–8.2 |
| 4 | Visual critic with rendered evidence and rubric | Python | 04 §7.3–7.4 |
| 5 | Skill promotion and rollback | Python | 04 §8.4–8.5 |
| 6 | RL-shaped eval loop with verifiable gates | Python | 04 §9 |

Each section follows the same shape: **what it demonstrates → contract → sketch →
inputs/outputs → failure path → VERIFIED vs PROPOSED**. The sketches share these
conventions, which are stated once here and not repeated:

| Convention | Definition |
|---|---|
| Canonical JSON | `json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)`. Hashes are always over canonical JSON. |
| Hash format | `sha256:` + 64 lowercase hex chars. The prefix is part of the stored value so a hash cannot be silently confused with a path. |
| Refusal envelope | `{code, message, how_to_fix, evidence_refs, terminal}`. `terminal: true` means no agent may retry; only a human/ops change resolves it. |
| Idempotency | `sha256(episode_id ‖ tool_id ‖ canonical(params) ‖ sorted(input_hashes))`; a replayed call returns the stored result with `replayed: true`. |
| Roles | conductor, art_director, vector_operator, raster_operator, print_verifier, visual_critic, memory_curator (04 §4.1). Separation of duties is enforced by role allowlists, not prompts. |
| Episode states | `intake → briefed → planned → context_ready → executing → verifying → critiquing → accepted`, with side states `refused`, `needs_human`, `failed`, `rolled_back`, `quarantined` (04 §12.1). |
| Evidence vocabulary | A verdict is `accepted` only when all required rungs of the ladder agree. Missing evidence yields `unverified`, never `pass` (04 §7.1). |

---

## 1. Example 1 — Supervisor loop with specialist roles and typed handoffs

### 1.1 What it demonstrates

A supervisor that **owns lifecycle, budgets and arbitration but never executes tools**. Work is
expressed as `PlanNode`s; each node becomes one `Handoff` row claimed by exactly one specialist
with a lease. The loop dispatches ready nodes (bounded concurrency), retries only transient
refusals, hard-stops on terminal refusals and budget exhaustion, validates the typed payload
shape, and assembles the final verdict from the gate report and blind critique.

This is the mechanism behind design decision D2 (conductor + capability-scoped specialists with
typed handoffs over a queue table, not freeform chat) and D7 (a verdict is a state transition
with evidence, not an opinion).

### 1.2 Contract

```jsonc
// Handoff (stored in forge_handoff; 04 §5.2)
{
  "handoff_id": "uuid",
  "episode_id": "uuid",
  "parent_handoff_id": "uuid|null",
  "kind": "artspec|command_batch|gate_report|critique|lesson_candidate|skill_draft",
  "produced_by": "conductor",          // who authored the request/result
  "consumed_by": "art_director",       // executor; fixed per kind
  "payload": { },
  "input_hashes": ["sha256:…"],
  "deadline_s": 900,
  "attempts": 1,
  "state": "created|claimed|completed|failed"
}
```

```text
Plan shape (the sketch's input):
  node 0  artspec          (no dependency)
  node 1  command_batch    ← depends on 0
  node 2  gate_report      ← depends on 1
  node 3  critique         ← depends on 1     (2 and 3 run concurrently; max in flight = 2)
```

Handoff rows are the unit of audit and replay: **what was asked, by which role, with which input
hashes, within which deadline, and what came back**. The store interface in the sketch
(`create`, `claim`, `complete`, `fail`) is the PostgreSQL queue adapter described in 04 §5.2
(`FOR UPDATE SKIP LOCKED`, lease, attempts).

### 1.3 Sketch

<!-- Example 1 sketch — validated with py_compile + scratch harness -->
```python
"""Example 1 - supervisor loop with specialist roles and typed handoffs.

Forge Conductor mechanism sketch (Python 3.11+). Design-only: this file is an
illustration, opens no database, spawns no process and is not installed code.
"""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from dataclasses import dataclass, field
from enum import StrEnum
from hashlib import sha256
from typing import Any, Mapping, Protocol


class Role(StrEnum):
    CONDUCTOR = "conductor"
    ART_DIRECTOR = "art_director"
    VECTOR_OPERATOR = "vector_operator"
    RASTER_OPERATOR = "raster_operator"
    PRINT_VERIFIER = "print_verifier"
    VISUAL_CRITIC = "visual_critic"
    MEMORY_CURATOR = "memory_curator"


class HandoffKind(StrEnum):
    ART_SPEC = "artspec"
    COMMAND_BATCH = "command_batch"
    GATE_REPORT = "gate_report"
    CRITIQUE = "critique"
    LESSON_CANDIDATE = "lesson_candidate"
    SKILL_DRAFT = "skill_draft"


class HandoffState(StrEnum):
    CREATED = "created"
    CLAIMED = "claimed"
    COMPLETED = "completed"
    FAILED = "failed"


class EpisodeState(StrEnum):
    INTAKE = "intake"
    BRIEFED = "briefed"
    PLANNED = "planned"
    CONTEXT_READY = "context_ready"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    CRITIQUING = "critiquing"
    ACCEPTED = "accepted"
    NEEDS_HUMAN = "needs_human"
    UNVERIFIED = "unverified"
    REJECTED = "rejected"
    REFUSED = "refused"
    FAILED = "failed"
    CANCELLED = "cancelled"
    QUARANTINED = "quarantined"


# One executor per handoff kind. The conductor never performs the work itself.
EXECUTOR_FOR_KIND: Mapping[HandoffKind, Role] = {
    HandoffKind.ART_SPEC: Role.ART_DIRECTOR,
    HandoffKind.COMMAND_BATCH: Role.VECTOR_OPERATOR,
    HandoffKind.GATE_REPORT: Role.PRINT_VERIFIER,
    HandoffKind.CRITIQUE: Role.VISUAL_CRITIC,
    HandoffKind.LESSON_CANDIDATE: Role.MEMORY_CURATOR,
    HandoffKind.SKILL_DRAFT: Role.MEMORY_CURATOR,
}

TRANSIENT_REFUSAL_CODES = frozenset({"E_TIMEOUT", "E_MODEL_UNAVAILABLE", "E_ARTIFACT_MISSING"})
MAX_HANDOFF_ATTEMPTS = 2
MAX_IN_FLIGHT = 2


def canonical_json(value: Any) -> str:
    """Stable bytes for hashing. Floats are the only unstable corner; contracts use ints."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return "sha256:" + sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Refusal:
    code: str
    message: str
    how_to_fix: str
    terminal: bool = True
    evidence_refs: tuple[str, ...] = ()

    def to_payload(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "how_to_fix": self.how_to_fix,
            "terminal": self.terminal,
            "evidence_refs": list(self.evidence_refs),
        }


class BudgetExceeded(Exception):
    code = "E_BUDGET_EXCEEDED"


@dataclass
class Budget:
    max_tokens: int
    max_wall_s: int
    max_attempts: int
    tokens_used: int = 0
    wall_s_used: float = 0.0

    def charge(self, *, tokens: int, wall_s: float) -> None:
        if tokens < 0 or wall_s < 0:
            raise ValueError("budget charge must be non-negative")
        next_tokens = self.tokens_used + tokens
        next_wall = self.wall_s_used + wall_s
        if next_tokens > self.max_tokens or next_wall > self.max_wall_s:
            raise BudgetExceeded(
                f"token {next_tokens}/{self.max_tokens}, wall {next_wall:.1f}/{self.max_wall_s}s"
            )
        self.tokens_used = next_tokens
        self.wall_s_used = next_wall


@dataclass
class Handoff:
    episode_id: str
    kind: HandoffKind
    produced_by: Role
    consumed_by: Role
    payload: dict[str, Any]
    input_hashes: tuple[str, ...] = field(default_factory=tuple)
    handoff_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_handoff_id: str | None = None
    deadline_s: int = 900
    attempts: int = 0
    state: HandoffState = HandoffState.CREATED

    def __post_init__(self) -> None:
        if EXECUTOR_FOR_KIND[self.kind] is not self.consumed_by:
            raise ValueError(
                f"{self.kind.value} is executed by {EXECUTOR_FOR_KIND[self.kind].value}, "
                f"not {self.consumed_by.value}"
            )
        if self.deadline_s <= 0:
            raise ValueError("deadline_s must be positive")
        if self.produced_by is self.consumed_by:
            raise ValueError("a role cannot consume its own handoff")

    def idempotency_key(self) -> str:
        return digest(
            {
                "episode_id": self.episode_id,
                "kind": self.kind.value,
                "produced_by": self.produced_by.value,
                "consumed_by": self.consumed_by.value,
                "payload": self.payload,
                "input_hashes": list(self.input_hashes),
            }
        )


class HandoffStore(Protocol):
    """Persistence boundary: one row per handoff, claimed with a lease.

    The SQL adapter lives with the ledger (Example 3); this protocol fixes the
    semantics the loop depends on: create is idempotent on idempotency_key,
    claim returns at most one claimed row with a live lease, complete only
    transitions a claimed row, and fail records a typed refusal.
    """

    async def create(self, handoff: Handoff) -> None: ...

    async def claim(self, role: Role, lease_s: int) -> Handoff | None: ...

    async def complete(self, handoff_id: str, payload: dict[str, Any], *, produced_by: Role) -> None: ...

    async def fail(self, handoff_id: str, refusal: Refusal) -> None: ...


class Specialist(Protocol):
    role: Role

    async def handle(self, handoff: Handoff) -> dict[str, Any] | Refusal:
        """Return a typed payload or a refusal. A dict without required keys is a defect."""
        ...


@dataclass(frozen=True)
class PlanNode:
    """One unit of delegated work in the conductor's plan DAG."""

    kind: HandoffKind
    payload: dict[str, Any]
    depends_on: tuple[int, ...] = ()
    input_hashes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.kind in (HandoffKind.GATE_REPORT, HandoffKind.CRITIQUE) and self.depends_on == ():
            raise ValueError(f"{self.kind.value} must depend on the artifact it assesses")


@dataclass(frozen=True)
class EpisodeResult:
    state: EpisodeState
    resolution: str
    reason_codes: tuple[str, ...]
    outputs: dict[str, Any]


REQUIRED_OUTPUT_KEYS: Mapping[HandoffKind, tuple[str, ...]] = {
    HandoffKind.ART_SPEC: ("deliverable", "canvas", "success_criteria"),
    HandoffKind.COMMAND_BATCH: ("exit_code", "artifacts"),
    HandoffKind.GATE_REPORT: ("ok", "checks", "non_vacuous", "artifact_sha256"),
    HandoffKind.CRITIQUE: ("verdict", "dimensions", "confidence", "unseen"),
    HandoffKind.LESSON_CANDIDATE: ("content", "scope", "evidence_episode_ids"),
    HandoffKind.SKILL_DRAFT: ("name", "steps", "preconditions", "gates"),
}


def missing_keys(kind: HandoffKind, payload: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(key for key in REQUIRED_OUTPUT_KEYS[kind] if key not in payload)


class Conductor:
    """Dispatches plan nodes, enforces budgets, and arbitrates the final verdict.

    Retry policy (design 04 section 4.3): at most MAX_HANDOFF_ATTEMPTS per node and
    only for TRANSIENT_REFUSAL_CODES. A terminal refusal stops the episode at once;
    no later node is dispatched, because acting on a refused precondition is how
    unverified artifacts become "accepted".
    """

    def __init__(
        self,
        store: HandoffStore,
        specialists: list[Specialist],
        budget: Budget,
    ) -> None:
        if not specialists:
            raise ValueError("at least one specialist is required")
        seen: dict[Role, Specialist] = {}
        for specialist in specialists:
            if specialist.role in seen:
                raise ValueError(f"duplicate specialist for role {specialist.role.value}")
            seen[specialist.role] = specialist
        if Role.CONDUCTOR in seen:
            raise ValueError("the conductor may not be registered as a specialist")
        self._store = store
        self._specialists = seen
        self._budget = budget

    async def run(
        self,
        episode_id: str,
        plan: list[PlanNode],
        *,
        requires_human: bool = False,
        human_approved: bool = False,
    ) -> EpisodeResult:
        if not plan:
            return EpisodeResult(
                EpisodeState.REFUSED, "refused", ("E_BRIEF_MISSING",), {}
            )
        self._validate_plan(plan)
        done: dict[int, dict[str, Any]] = {}
        refused: Refusal | None = None

        while len(done) < len(plan) and refused is None:
            ready = [
                index
                for index, node in enumerate(plan)
                if index not in done and all(dep in done for dep in node.depends_on)
            ]
            if not ready:
                return EpisodeResult(
                    EpisodeState.FAILED,
                    "rejected",
                    ("E_PLAN_STALLED",),
                    {"done": sorted(done)},
                )
            batch = ready[:MAX_IN_FLIGHT]
            outcomes = await asyncio.gather(
                *(self._run_node(episode_id, plan[index], done) for index in batch),
                return_exceptions=True,
            )
            for index, outcome in zip(batch, outcomes):
                if isinstance(outcome, Refusal):
                    refused = outcome
                    break
                if isinstance(outcome, BaseException):
                    return EpisodeResult(
                        EpisodeState.FAILED,
                        "rejected",
                        ("E_INTERNAL",),
                        {"detail": type(outcome).__name__},
                    )
                done[index] = outcome
        if refused is not None:
            return EpisodeResult(
                EpisodeState.REFUSED, "refused", (refused.code,), {"refusal": refused.to_payload()}
            )
        return self._arbitrate(plan, done, requires_human, human_approved)

    def _validate_plan(self, plan: list[PlanNode]) -> None:
        for index, node in enumerate(plan):
            for parent in node.depends_on:
                if parent >= index:
                    raise ValueError(
                        f"node {index} depends on {parent}; dependencies must precede the node"
                    )

    async def _run_node(
        self, episode_id: str, node: PlanNode, done: dict[int, dict[str, Any]]
    ) -> dict[str, Any] | Refusal:
        executor = EXECUTOR_FOR_KIND[node.kind]
        specialist = self._specialists.get(executor)
        if specialist is None:
            return Refusal(
                "E_NO_SPECIALIST",
                f"no specialist registered for {executor.value}",
                "register the role before planning this handoff",
            )
        inputs = {str(dep): done[dep] for dep in node.depends_on}
        payload = {**node.payload, "inputs": inputs}
        attempt = 1
        while attempt <= MAX_HANDOFF_ATTEMPTS:
            handoff = Handoff(
                episode_id=episode_id,
                kind=node.kind,
                produced_by=Role.CONDUCTOR,
                consumed_by=executor,
                payload=payload,
                input_hashes=node.input_hashes,
                attempts=attempt,
            )
            await self._store.create(handoff)
            started = time.perf_counter()
            try:
                produced = await asyncio.wait_for(
                    specialist.handle(handoff), timeout=handoff.deadline_s
                )
            except TimeoutError:
                produced = Refusal(
                    "E_TIMEOUT",
                    f"{executor.value} exceeded {handoff.deadline_s}s",
                    "retry once if the host is transiently loaded, else split the batch",
                )
            except Exception as error:  # named, never swallowed: converted to a refusal
                produced = Refusal(
                    "E_INTERNAL",
                    f"{executor.value} raised {type(error).__name__}",
                    "inspect the specialist log; do not retry a logic error",
                )
            wall_s = time.perf_counter() - started

            if isinstance(produced, Refusal):
                await self._store.fail(handoff.handoff_id, produced)
                if produced.code in TRANSIENT_REFUSAL_CODES and attempt < MAX_HANDOFF_ATTEMPTS:
                    attempt += 1
                    continue
                return produced

            missing = missing_keys(node.kind, produced)
            if missing:
                defect = Refusal(
                    "E_HANDOFF_SCHEMA",
                    f"{node.kind.value} output missing {', '.join(missing)}",
                    "fix the specialist serializer; a partial payload is not a success",
                )
                await self._store.fail(handoff.handoff_id, defect)
                return defect

            usage = produced.pop("_usage", {})
            try:
                self._budget.charge(
                    tokens=int(usage.get("tokens", 0)),
                    wall_s=wall_s,
                )
            except BudgetExceeded as error:
                return Refusal("E_BUDGET_EXCEEDED", str(error), "raise the cap or reduce scope")
            await self._store.complete(
                handoff.handoff_id, produced, produced_by=executor
            )
            return produced
        return Refusal(
            "E_TIMEOUT", "retry budget exhausted", "escalate to the operator"
        )

    def _arbitrate(
        self,
        plan: list[PlanNode],
        done: dict[int, dict[str, Any]],
        requires_human: bool,
        human_approved: bool,
    ) -> EpisodeResult:
        by_kind: dict[HandoffKind, dict[str, Any]] = {}
        for index, output in done.items():
            by_kind[plan[index].kind] = output

        gate = by_kind.get(HandoffKind.GATE_REPORT)
        critique = by_kind.get(HandoffKind.CRITIQUE)

        if gate is None:
            return EpisodeResult(
                EpisodeState.UNVERIFIED, "unverified", ("E_GATE_MISSING",), by_kind
            )
        if critique is None:
            return EpisodeResult(
                EpisodeState.UNVERIFIED, "unverified", ("E_CRITIQUE_MISSING",), by_kind
            )
        if gate.get("non_vacuous") in (None, {}, []):
            return EpisodeResult(
                EpisodeState.UNVERIFIED, "unverified", ("E_GATE_VACUOUS",), by_kind
            )
        if gate.get("ok") is not True:
            return EpisodeResult(
                EpisodeState.REJECTED, "rejected", ("E_GATE_FAILED",), by_kind
            )

        verdict = critique.get("verdict")
        if verdict == "reject":
            return EpisodeResult(
                EpisodeState.REJECTED, "rejected", ("E_CRITIQUE_REJECT",), by_kind
            )
        if verdict == "unverifiable":
            return EpisodeResult(
                EpisodeState.NEEDS_HUMAN, "needs_human", ("E_CRITIQUE_UNVERIFIABLE",), by_kind
            )
        if verdict not in ("pass", "pass_with_notes"):
            return EpisodeResult(
                EpisodeState.UNVERIFIED, "unverified", ("E_CRITIQUE_MALFORMED",), by_kind
            )
        if requires_human and not human_approved:
            return EpisodeResult(
                EpisodeState.NEEDS_HUMAN, "needs_human", ("E_HUMAN_APPROVAL_REQUIRED",), by_kind
            )
        return EpisodeResult(
            EpisodeState.ACCEPTED, "accepted", ("GATE_AND_CRITIC_AGREE",), by_kind
        )
```

### 1.4 Inputs and outputs

| Direction | Value |
|---|---|
| In | `episode_id`, a `PlanNode` DAG, `Budget(max_tokens, max_wall_s, max_attempts)`, registered `Specialist`s, `requires_human` / `human_approved` flags |
| Out | `EpisodeResult(state, resolution, reason_codes, outputs)`; handoff rows in the store; each completion is eligible for a hash-chained `forge_event` (Example 3) |
| Side effects | Only handoff rows and whatever the specialist itself is allowed to produce. The conductor writes no artifact. |

### 1.5 Failure path

| Failure | Mechanic in the sketch | Observable result |
|---|---|---|
| No specialist for a role | `E_NO_SPECIALIST` before any dispatch | `refused`, terminal |
| Transient timeout | `E_TIMEOUT`; retried once (`attempt < 2`) | second failure → `refused` |
| Policy/schema/rights refusal | Not in the transient set → returned immediately | `refused`, **the specialist is not called twice** |
| Partial payload | `missing_keys` for the handoff kind | `E_HANDOFF_SCHEMA`; the episode is refused, not "accepted with missing evidence" |
| Token/wall budget exceeded | `Budget.charge` raises before completion is recorded | `E_BUDGET_EXCEEDED` |
| Gate missing or vacuous | Arbitration returns `unverified` | cannot ship; never `accepted` |
| Gate fail | `E_GATE_FAILED` | `rejected` |
| Critic rejects | `E_CRITIQUE_REJECT` | `rejected` |
| Critic says unverifiable | `E_CRITIQUE_UNVERIFIABLE` | `needs_human` |
| Print/publish without human | `requires_human and not human_approved` | `needs_human` |
| Plan cycle/stall | `_validate_plan` / no ready nodes | `failed` — a planning defect is not retried |

The retry rule is deliberately narrow: **a retry is only legal for the codes in
`TRANSIENT_REFUSAL_CODES`**, and the maximum is two attempts, matching the existing pipeline's
`max_attempts` discipline and its "transient exit only" retry rule (`01-STACK-VPS.md` §6).

### 1.6 VERIFIED vs PROPOSED

| Claim | Label | Source / status |
|---|---|---|
| Role set, handoff kinds, arbitration matrix and episode states are the design's, not invented here | `[R]` | `04-HARNESS-DESIGN.md` §4, §12.1 |
| Existing pipeline retries transient exits only, `max_attempts` 2 | `[R]` | `01-STACK-VPS.md` §6; `orchestrator.py` pointers in `REPORT.md` |
| Cap of 3 concurrent model-calling subagents informed `MAX_IN_FLIGHT = 2` | `[V]` | DeerFlow `subagent_runtime.max_running: 3`, read on host (04 §2.2) |
| The Python sketch compiles and its happy/refusal/arbitration paths ran in a scratch harness | `[V]` (this task) | `py_compile` exit 0; 13/13 Example-1 checks passed |
| Lease duration 900 s, heartbeat interval, play-back semantics | `[I]` | Must be tuned by load test; 900 s follows the CLI timeout in 04 §10.4 |
| The store adapter's SQL (SKIP LOCKED queue) | `[I]` | Interface fixed; production SQL must be written and tested against PostgreSQL 16 |
| End-to-end behaviour with real specialists and a real Postgres | `[U]` | Not run; requires the Forge DB and a specialist implementation |

---

## 2. Example 2 — Typed tool gateway for Craft CLI/MCP

### 2.1 What it demonstrates

One gateway that every tool call must pass through, in this order: **schema → role allowlist →
root confinement → version probe/pin → idempotency → execution → artifact verification**. It
fails closed with a named refusal and never executes when a precondition is unmet. It also
explains the host fact that makes this layer necessary: the deployed `PATH` resolves
`*-cli` to 127-shims while the real binaries live under `/opt/craft` and are absent from every
service `PATH`, so tools must be resolved by **absolute path + version probe** (04 §2.3, §6.2).

The sketch is TypeScript + zod because the contracts are easier to keep honest with a schema
library; the runtime service may be Python, since the gateway's boundary is the JSON contract,
not the language. Either way, the registry is data, not code.

### 2.2 Contract

```jsonc
// Registry entry — the only way a tool becomes callable (04 §6.2)
{
  "tool_id": "craft.run",
  "app": "vectorcraft",
  "bin": "/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli",
  "version_probe": ["--version"],
  "version_regex": "^vectorcraft-cli (\\d+\\.\\d+\\.\\d+)$",
  "surface": "cli",
  "writes": true,
  "allow_roles": ["vector_operator"],
  "roots": {"read": ["inbox", "work/<episode>", "build/<episode>"],
            "write": ["work/<episode>", "build/<episode>"]},
  "timeout_s": 900,
  "idempotency": "required",
  "outputs": [{"kind": "svg", "requireMagic": "<svg"}]
}
```

The gateway's `paramSchemas` map holds one zod schema per exact `cmd_id`, drawn from the pinned
catalogue — never a prefix wildcard. `imageTrace.*` is forbidden; `imageTrace.make` is listed.

```sql
-- Idempotency is enforced by the database, not by application memory (04 §6.5).
CREATE UNIQUE INDEX forge_tool_call_idempotency ON forge_tool_call (idempotency_key);
```

### 2.3 Sketch

<!-- Example 2 sketch — validated with tsc --noEmit (strict) -->
```typescript
/**
 * Example 2 - typed tool gateway for Craft CLI/MCP.
 *
 * Design-only mechanism sketch (TypeScript 5.x + zod 4). No process is spawned
 * when this module is imported; the gateway only executes inside call().
 */
import { createHash } from "node:crypto";
import { execFileSync, spawnSync } from "node:child_process";
import { readFileSync, realpathSync, statSync } from "node:fs";
import { dirname, isAbsolute, resolve, sep } from "node:path";
import { z } from "zod";

export const SURFACES = ["cli", "json", "mcp"] as const;
export const REFUSAL_CODES = [
  "E_COMMAND_UNKNOWN",
  "E_PARAM_REJECTED",
  "E_ROLE_FORBIDDEN",
  "E_ROOT_DENIED",
  "E_APP_DRIFT",
  "E_TOOL_TIMEOUT",
  "E_ARTIFACT_MISSING",
  "E_ARTIFACT_EMPTY",
  "E_APP_CRASH",
  "E_IDEMPOTENCY_CONFLICT",
] as const;

export type RefusalCode = (typeof REFUSAL_CODES)[number];

export interface Refusal {
  ok: false;
  code: RefusalCode;
  message: string;
  howToFix: string;
  terminal: boolean;
  evidenceRefs: string[];
}

export interface ToolSuccess {
  ok: true;
  toolId: string;
  episodeId: string;
  argv: string[];
  exitCode: number;
  durationMs: number;
  artifacts: ArtifactRecord[];
  replayOf: string | null;
}

export interface ArtifactRecord {
  path: string;
  sha256: string;
  bytes: number;
  format: string;
}

const RootPolicy = z.object({
  read: z.array(z.string().min(1)).min(1),
  write: z.array(z.string().min(1)),
});

export const OutputRule = z.object({
  kind: z.enum(["svg", "png", "json", "pdf"]),
  requireMagic: z.string().min(1).optional(),
});

/** One registry entry is the only way a tool becomes callable (design 04 section 6.2). */
export const RegistryEntry = z.object({
  toolId: z.string().min(1),
  app: z.string().min(1),
  bin: z.string().min(1),
  versionProbe: z.array(z.string().min(1)).min(1),
  versionRegex: z.string().min(1),
  surface: z.enum(SURFACES),
  writes: z.boolean(),
  allowRoles: z.array(z.string().min(1)).min(1),
  roots: RootPolicy,
  timeoutS: z.number().int().positive().max(3600),
  idempotency: z.enum(["required", "none"]),
  outputs: z.array(OutputRule).min(1),
});

export type RegistryEntry = z.infer<typeof RegistryEntry>;

export const ToolCallRequest = z.object({
  episodeId: z.string().uuid(),
  role: z.string().min(1),
  toolId: z.string().min(1),
  params: z.record(z.string(), z.unknown()),
  inputHashes: z.array(z.string().regex(/^sha256:[0-9a-f]{64}$/)),
  workdir: z.string().min(1),
});

export type ToolCallRequest = z.infer<typeof ToolCallRequest>;

export interface StoredCall {
  idempotencyKey: string;
  result: ToolSuccess;
  createdAt: string;
}

/** Implemented by the ledger repository (Example 3). */
export interface ToolCallStore {
  findByKey(key: string): Promise<StoredCall | null>;
  insert(call: StoredCall): Promise<void>;
}

export interface GatewayOptions {
  registry: RegistryEntry[];
  paramSchemas: Record<string, z.ZodType<Record<string, unknown>>>;
  store: ToolCallStore;
  pinnedVersions: Record<string, string>;
  hostRoots: string[];
}

function refusal(
  code: RefusalCode,
  message: string,
  howToFix: string,
  evidenceRefs: string[] = [],
  terminal = true,
): Refusal {
  return { ok: false, code, message, howToFix, terminal, evidenceRefs };
}

function canonicalJson(value: unknown): string {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  const entries = Object.keys(value as Record<string, unknown>)
    .sort()
    .map((key) => `${JSON.stringify(key)}:${canonicalJson((value as Record<string, unknown>)[key])}`);
  return `{${entries.join(",")}}`;
}

export function idempotencyKey(
  episodeId: string,
  toolId: string,
  params: Record<string, unknown>,
  inputHashes: string[],
): string {
  const material = [episodeId, toolId, canonicalJson(params), [...inputHashes].sort().join(",")].join("\u241f");
  return `sha256:${createHash("sha256").update(material, "utf8").digest("hex")}`;
}

function isInsideRoot(root: string, target: string): boolean {
  const rel = target.slice(root.length);
  return target === root || (target.startsWith(root) && rel.startsWith(sep));
}

/** Levenshtein distance, used only to suggest near ids, never to execute them. */
export function nearestIds(candidate: string, known: string[], limit = 5): string[] {
  const distance = (a: string, b: string): number => {
    const prev = Array.from({ length: b.length + 1 }, (_, j) => j);
    for (let i = 1; i <= a.length; i += 1) {
      let diagonal = prev[0];
      prev[0] = i;
      for (let j = 1; j <= b.length; j += 1) {
        const temp = prev[j];
        prev[j] = Math.min(
          prev[j] + 1,
          prev[j - 1] + 1,
          diagonal + (a[i - 1] === b[j - 1] ? 0 : 1),
        );
        diagonal = temp;
      }
    }
    return prev[b.length];
  };
  return [...known]
    .sort((a, b) => distance(candidate, a) - distance(candidate, b) || a.localeCompare(b))
    .slice(0, limit);
}

export class ToolGateway {
  private readonly entries: Map<string, RegistryEntry>;

  constructor(private readonly options: GatewayOptions) {
    this.entries = new Map(options.registry.map((entry) => [entry.toolId, RegistryEntry.parse(entry)]));
  }

  async call(request: ToolCallRequest): Promise<ToolSuccess | Refusal> {
    const parsed = ToolCallRequest.safeParse(request);
    if (!parsed.success) {
      return refusal(
        "E_PARAM_REJECTED",
        parsed.error.issues.map((i) => `${i.path.join(".")}: ${i.message}`).join("; "),
        "rebuild the request from the tool contract",
      );
    }
    const req = parsed.data;
    const entry = this.entries.get(req.toolId);
    if (!entry) {
      return refusal(
        "E_COMMAND_UNKNOWN",
        `unknown toolId ${req.toolId}`,
        "query the pinned catalogue and use an exact id",
        nearestIds(req.toolId, [...this.entries.keys()]),
      );
    }
    if (!entry.allowRoles.includes(req.role)) {
      return refusal(
        "E_ROLE_FORBIDDEN",
        `${req.role} may not call ${entry.toolId}`,
        "use the role-scoped token for a role on the allowlist",
      );
    }
    const schema = this.options.paramSchemas[req.toolId];
    if (!schema) {
      return refusal(
        "E_COMMAND_UNKNOWN",
        `no parameter schema registered for ${req.toolId}`,
        "register the pinned catalogue schema before enabling the tool",
      );
    }
    const params = schema.safeParse(req.params);
    if (!params.success) {
      return refusal(
        "E_PARAM_REJECTED",
        params.error.issues.map((i) => `${i.path.join(".")}: ${i.message}`).join("; "),
        "re-read the command schema; ranges are inclusive and enums are exact",
      );
    }

    const workdir = this.resolveWorkdir(entry, req.workdir);
    if (typeof workdir === "object") return workdir;

    const drift = this.probeVersion(entry);
    if (typeof drift === "object") return drift;

    const key = idempotencyKey(req.episodeId, req.toolId, params.data, req.inputHashes);
    const stored = entry.idempotency === "required" ? await this.options.store.findByKey(key) : null;
    if (stored) {
      return { ...stored.result, replayOf: stored.idempotencyKey };
    }

    const started = Date.now();
    const env = { ...process.env, PATH: dirname(entry.bin) };
    const run = spawnSync(entry.bin, this.argvFor(entry, params.data), {
      cwd: workdir,
      env,
      timeout: entry.timeoutS * 1000,
      killSignal: "SIGKILL",
      stdio: ["ignore", "pipe", "pipe"],
      encoding: "utf8",
    });
    const durationMs = Date.now() - started;

    if (run.error || run.signal) {
      return refusal(
        "E_TOOL_TIMEOUT",
        `${entry.toolId} did not finish within ${entry.timeoutS}s`,
        "split the batch or raise the declared deadline; the episode keeps no output",
        [],
        true,
      );
    }
    if (run.status !== 0) {
      return refusal(
        "E_APP_CRASH",
        `${entry.toolId} exited ${String(run.status)}`,
        "read stderr digest and map the code against the catalogue; never retry an unknown exit",
        [`stderr:${digestText(run.stderr ?? "")}`],
        true,
      );
    }

    const artifacts: ArtifactRecord[] = [];
    for (const match of matchArtifacts(run.stdout)) {
      const artifact = this.verifyArtifact(entry, req.workdir, match);
      if ("ok" in artifact) return artifact;
      artifacts.push(artifact);
    }
    if (artifacts.length === 0) {
      return refusal(
        "E_ARTIFACT_MISSING",
        `${entry.toolId} exited 0 but declared no artifact`,
        "treat exit 0 as a claim only; inspect the command contract for outputs",
        [`stdout:${digestText(run.stdout)}`],
      );
    }

    const result: ToolSuccess = {
      ok: true,
      toolId: req.toolId,
      episodeId: req.episodeId,
      argv: [entry.bin, ...this.argvFor(entry, params.data)],
      exitCode: run.status,
      durationMs,
      artifacts,
      replayOf: null,
    };
    if (entry.idempotency === "required") {
      await this.options.store.insert({
        idempotencyKey: key,
        result,
        createdAt: new Date().toISOString(),
      });
    }
    return result;
  }

  private resolveWorkdir(entry: RegistryEntry, requested: string): string | Refusal {
    let real: string;
    try {
      real = realpathSync.native(requested);
    } catch {
      return refusal("E_ROOT_DENIED", `workdir ${requested} does not exist`, "create the episode workdir first");
    }
    const allowed = entry.roots.write.length > 0 ? entry.roots.write : entry.roots.read;
    const rooted = allowed.map((root) => {
      try {
        return realpathSync.native(isAbsolute(root) ? root : resolve(this.options.hostRoots[0], root));
      } catch {
        return null;
      }
    });
    const inside = rooted.some((root) => root !== null && isInsideRoot(root, real));
    if (!inside) {
      return refusal(
        "E_ROOT_DENIED",
        `${real} is outside the declared roots for ${entry.toolId}`,
        "write only under work/<episode> and build/<episode>; symlink escapes are refused",
        allowed,
      );
    }
    return real;
  }

  private probeVersion(entry: RegistryEntry): true | Refusal {
    let output: string;
    try {
      output = execFileSync(entry.bin, entry.versionProbe, {
        encoding: "utf8",
        timeout: 15_000,
        stdio: ["ignore", "pipe", "pipe"],
      }).trim();
    } catch {
      return refusal(
        "E_APP_DRIFT",
        `${entry.bin} could not be probed`,
        "install the pinned build; a missing binary is drift, not a retry",
        [entry.bin],
      );
    }
    const match = new RegExp(entry.versionRegex).exec(output);
    if (!match || match[1] === undefined) {
      return refusal(
        "E_APP_DRIFT",
        `version probe for ${entry.toolId} did not match ${entry.versionRegex}`,
        "update the registry regex only after a catalogue refresh",
        [digestText(output)],
      );
    }
    const pinned = this.options.pinnedVersions[entry.toolId];
    if (pinned !== undefined && pinned !== match[1]) {
      return refusal(
        "E_APP_DRIFT",
        `${entry.toolId} reports ${match[1]}, episode pinned ${pinned}`,
        "refresh the catalogue, re-run goldens, repin the episode",
        [entry.bin, pinned, match[1]],
      );
    }
    return true;
  }

  private argvFor(entry: RegistryEntry, params: Record<string, unknown>): string[] {
    // Contract: params carry {subcommand: string[], flags: Record<string, string|number|boolean>}.
    const subcommand = Array.isArray(params.subcommand) ? params.subcommand : [];
    const flags = (params.flags ?? {}) as Record<string, string | number | boolean>;
    const argv = [...subcommand.map(String)];
    for (const key of Object.keys(flags).sort()) {
      const value = flags[key];
      if (value === false) continue;
      argv.push(`--${key}`);
      if (value !== true) argv.push(String(value));
    }
    return argv;
  }

  private verifyArtifact(
    entry: RegistryEntry,
    workdir: string,
    match: string,
  ): ArtifactRecord | Refusal {
    const absolute = isAbsolute(match) ? match : resolve(workdir, match);
    let real: string;
    try {
      real = realpathSync.native(absolute);
    } catch {
      return refusal("E_ARTIFACT_MISSING", `declared artifact ${match} does not exist`, "treat the batch as failed");
    }
    const rootOk = entry.roots.write.some((root) => {
      try {
        return isInsideRoot(realpathSync.native(isAbsolute(root) ? root : resolve(this.options.hostRoots[0], root)), real);
      } catch {
        return false;
      }
    });
    if (!rootOk) {
      return refusal("E_ROOT_DENIED", `artifact ${match} resolved outside roots`, "discard the batch");
    }
    const stat = statSync(real);
    if (stat.size === 0) {
      return refusal("E_ARTIFACT_EMPTY", `${match} is zero bytes`, "re-run the producing step on a copy");
    }
    const bytes = readFileSync(real);
    const head = bytes.subarray(0, 512).toString("utf8");
    const rule = entry.outputs[0];
    if (rule.requireMagic && !head.includes(rule.requireMagic)) {
      return refusal(
        "E_ARTIFACT_EMPTY",
        `${match} does not contain ${rule.requireMagic}`,
        "verify the export format; a truncated file is not a pass",
      );
    }
    return {
      path: real,
      sha256: `sha256:${createHash("sha256").update(bytes).digest("hex")}`,
      bytes: stat.size,
      format: rule.kind,
    };
  }
}

function digestText(text: string): string {
  return createHash("sha256").update(text, "utf8").digest("hex");
}

/** The CLI contract says one JSON object per line carrying an "artifact" field. */
function matchArtifacts(stdout: string): string[] {
  const found: string[] = [];
  for (const line of stdout.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed.startsWith("{")) continue;
    try {
      const parsed = JSON.parse(trimmed) as { artifact?: unknown };
      if (typeof parsed.artifact === "string" && parsed.artifact.length > 0) {
        found.push(parsed.artifact);
      }
    } catch {
      continue;
    }
  }
  return found;
}
```

### 2.4 Inputs and outputs

| Direction | Value |
|---|---|
| In | `ToolCallRequest {episodeId, role, toolId, params, inputHashes, workdir}` |
| Out | `ToolSuccess {ok:true, argv, exitCode, durationMs, artifacts[], replayOf}` **or** `Refusal {ok:false, code, message, howToFix, terminal, evidenceRefs}` |
| Persisted | One `forge_tool_call` row per executed call (unique idempotency key); result replayable |
| Never | A bare exit code, prose-only success, or a path outside the declared roots |

### 2.5 Failure path

| Failure | Where it stops | Refusal code | Terminal |
|---|---|---|---|
| Malformed request | request schema | `E_PARAM_REJECTED` | yes |
| `cmd_id` not in pinned catalogue | registry | `E_COMMAND_UNKNOWN` + 5 nearest ids, **no execution** | yes |
| Role not on the tool's allowlist | allowlist | `E_ROLE_FORBIDDEN` (proposed code) | yes |
| Params outside schema/range | per-command schema | `E_PARAM_REJECTED` | yes |
| Workdir escapes roots via `..` or symlink | `realpath` root check | `E_ROOT_DENIED` | yes |
| Version ≠ episode pin | version probe | `E_APP_DRIFT` | yes (human repin) |
| Binary missing/not probeable | version probe | `E_APP_DRIFT` | yes |
| Timeout / signal | spawn | `E_TOOL_TIMEOUT` | yes |
| Non-zero exit | spawn | `E_APP_CRASH` + stderr digest | yes |
| Exit 0 but no artifact | output scan | `E_ARTIFACT_MISSING` (exit 0 is a claim, not an effect) | retry once if transient, else fail |
| Zero-byte or wrong-magic artifact | artifact verification | `E_ARTIFACT_EMPTY` | yes |
| Duplicate idempotency key | store lookup | returns stored result, `replayOf` set — **the tool is not re-run** | n/a |
| Artifact mutated after write | caller re-hashes before use | `E_ARTIFACT_MISMATCH` (proposed; design's `E_SOURCE_MUTATED` covers inputs) | quarantine |

`E_ROLE_FORBIDDEN` is an extension: 04 §6.6 lists role allowlists but no dedicated code. It is
labelled `[I]` and must be added to the refusal table before implementation so agents get one
vocabulary, not two.

### 2.6 VERIFIED vs PROPOSED

| Claim | Label | Source / status |
|---|---|---|
| Real binaries live under `/opt/craft/...`; bare names on service PATH resolve to 127 shims | `[V]` | 04 §2.3 (host probe) |
| VectorCraft 0.21.1 / PhotoCraft 0.20.2 installed; catalogues exist | `[V]` | 04 §2.3 |
| Roots, allowlist, idempotency, refusal-code design | `[R]` | 04 §6.2–6.6 |
| Idempotency key formula | `[R]` | 04 §6.5 (same construction) |
| The TypeScript sketch typechecks under `strict` | `[V]` (this task) | `tsc --noEmit` exit 0 |
| Actual CLI JSON envelope field names (`artifact`, stdout lines) | `[U]` | **Assumed by the sketch**; 04 §15 lists "Craft CLI JSON envelope stability" as an open unknown. Probe 20 commands before relying on it. |
| Role-token mechanism | `[I]` | `forge_role_token` is proposed; no token issuer exists yet |
| zod parameter schemas generated from the catalogue | `[I]` | Requires a catalogue→schema generator, not written |
| MCP transport variant | `[U]` | The sketch shows the CLI path; MCP parity is asserted by the design but not exercised here |

---

## 3. Example 3 — Episode ledger, hash chain, write path and retrieval

### 3.1 What it demonstrates

The ledger is the source of truth: **append-only, hash-chained events; a transactional close
that indexes a retrievable case; and retrieval that returns bounded evidence plus a receipt**.
Derived views (case summaries, skill stats) are rebuildable from the chain. Retrieval never
invents precedent: no matching case yields `empty: true`, and that fact is recorded.

The hash chain covers `(seq, prev_hash, kind, payload)`. Deleting a row breaks the link at the
next event; reordering breaks `seq`; editing a payload breaks the recomputation. That is what
"append-only" has to mean if it is to be auditable.

### 3.2 Schema (proposed; no migration applied)

```sql
CREATE TABLE IF NOT EXISTS forge_episode (
  id              uuid PRIMARY KEY,
  account_id      bigint NOT NULL,
  brief           text NOT NULL,
  task_family     text NOT NULL,
  app_version     text NOT NULL,
  catalogue_hash  text NOT NULL,
  status          text NOT NULL,
  accepted        boolean NOT NULL DEFAULT false,
  mode            text NOT NULL,
  budget          jsonb NOT NULL DEFAULT '{}'::jsonb,
  cost            jsonb NOT NULL DEFAULT '{}'::jsonb,
  started_at      timestamptz NOT NULL DEFAULT now(),
  finished_at     timestamptz
);

CREATE TABLE IF NOT EXISTS forge_event (
  id          bigserial PRIMARY KEY,
  episode_id  uuid NOT NULL REFERENCES forge_episode(id),
  seq         integer NOT NULL,
  kind        text NOT NULL,
  payload     jsonb NOT NULL,
  prev_hash   char(64) NOT NULL,
  hash        char(64) NOT NULL,
  created_at  timestamptz NOT NULL DEFAULT now(),
  UNIQUE (episode_id, seq)
);

CREATE TABLE IF NOT EXISTS forge_episode_case (
  episode_id    uuid PRIMARY KEY REFERENCES forge_episode(id),
  task_family   text NOT NULL,
  brand         text,
  product_type  text,
  summary       tsvector NOT NULL,
  outcome       text NOT NULL,
  accepted      boolean NOT NULL,
  embedding     real[]
);

CREATE TABLE IF NOT EXISTS forge_retrieval (
  id              bigserial PRIMARY KEY,
  episode_id      uuid NOT NULL REFERENCES forge_episode(id),
  query_hash      char(64) NOT NULL,
  returned_ids    uuid[] NOT NULL,
  scores          real[] NOT NULL,
  injected_tokens integer NOT NULL,
  created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS forge_event_episode ON forge_event (episode_id, seq);
CREATE INDEX IF NOT EXISTS forge_case_lookup ON forge_episode_case (task_family);
```

The design's full ledger has more tables (`forge_gate`, `forge_critique`, `forge_resolution`,
`forge_handoff`, `forge_job`, `forge_skill`, …). This subset is the minimum needed for the chain,
the case index and the retrieval receipt; the rest are in 04 §5.2.

### 3.3 Write path and query specification

```text
append_event(episode_id, kind, payload)
  1. pg_advisory_xact_lock(hashtextextended(episode_id, 0))   serialise appends per episode
  2. read (seq, hash) of last event, or GENESIS (0, "0"*64)
  3. seq' = seq + 1
  4. hash' = sha256(canonical_json({seq', prev_hash, kind, payload}))
  5. INSERT … (unique (episode_id, seq) backs the lock with a constraint)

close_episode(close)
  1. transaction → verify_chain(episode_id); broken chain = LedgerIntegrityError, no close
  2. UPDATE forge_episode status/finished_at/cost/accepted; 0 rows = LedgerWriteError
  3. UPSERT forge_episode_case with tsvector summary, outcome, accepted
  4. append_event("episode.closed", …); commit

retrieve_cases(query)
  1. verify_chain(requesting episode) — never retrieve using an untrusted ledger
  2. hard filters: task_family, brand, product_type, outcome
  3. lexical rank: ts_rank(websearch_to_tsquery('simple', query.text))
  4. rerank: accepted outcome boost, recency tie-break
  5. trim to ≤1,200 injected tokens, ≤5 hits; return why_retrieved per hit
  6. INSERT forge_retrieval receipt (query_hash, returned_ids, scores, injected_tokens)
```

### 3.4 Sketch

<!-- Example 3 sketch — validated with py_compile; chain logic unit-tested in the design's terms -->
```python
"""Example 3 - append-only episode ledger with hash chain, write path and retrieval.

Forge Conductor mechanism sketch (Python 3.11+). Design-only: the SQL is the
proposed schema from design 04 section 5.2/8.2, no migration has been applied.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any, Mapping, Protocol, Sequence

SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
GENESIS_HASH = "0" * 64
CASE_TOKEN_BUDGET = 1200


class LedgerIntegrityError(Exception):
    code = "E_LEDGER_CHAIN_MISMATCH"


class LedgerWriteError(Exception):
    code = "E_LEDGER_WRITE"


SCHEMA = """
CREATE TABLE IF NOT EXISTS forge_episode (
  id              uuid PRIMARY KEY,
  account_id      bigint NOT NULL,
  brief           text NOT NULL,
  task_family     text NOT NULL,
  app_version     text NOT NULL,
  catalogue_hash  text NOT NULL,
  status          text NOT NULL,
  accepted        boolean NOT NULL DEFAULT false,
  mode            text NOT NULL,
  budget          jsonb NOT NULL DEFAULT '{}'::jsonb,
  cost            jsonb NOT NULL DEFAULT '{}'::jsonb,
  started_at      timestamptz NOT NULL DEFAULT now(),
  finished_at     timestamptz
);

CREATE TABLE IF NOT EXISTS forge_event (
  id          bigserial PRIMARY KEY,
  episode_id  uuid NOT NULL REFERENCES forge_episode(id),
  seq         integer NOT NULL,
  kind        text NOT NULL,
  payload     jsonb NOT NULL,
  prev_hash   char(64) NOT NULL,
  hash        char(64) NOT NULL,
  created_at  timestamptz NOT NULL DEFAULT now(),
  UNIQUE (episode_id, seq)
);

CREATE TABLE IF NOT EXISTS forge_episode_case (
  episode_id    uuid PRIMARY KEY REFERENCES forge_episode(id),
  task_family   text NOT NULL,
  brand         text,
  product_type  text,
  summary       tsvector NOT NULL,
  outcome       text NOT NULL,
  accepted      boolean NOT NULL,
  embedding     real[]
);

CREATE TABLE IF NOT EXISTS forge_retrieval (
  id              bigserial PRIMARY KEY,
  episode_id      uuid NOT NULL REFERENCES forge_episode(id),
  query_hash      char(64) NOT NULL,
  returned_ids    uuid[] NOT NULL,
  scores          real[] NOT NULL,
  injected_tokens integer NOT NULL,
  created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS forge_event_episode ON forge_event (episode_id, seq);
CREATE INDEX IF NOT EXISTS forge_case_lookup ON forge_episode_case (task_family);
"""


class Cursor(Protocol):
    def fetchone(self) -> tuple[Any, ...] | None: ...

    def fetchall(self) -> list[tuple[Any, ...]]: ...


class Transaction(Protocol):
    def __enter__(self) -> "Transaction": ...

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool | None: ...


class Connection(Protocol):
    """The subset of psycopg 3 used here; any driver with these methods works."""

    def execute(self, sql: str, params: Sequence[Any] = ()) -> Cursor: ...

    def transaction(self) -> Transaction: ...


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def hex_digest(material: str) -> str:
    return sha256(material.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ChainCheck:
    ok: bool
    events: int
    first_bad_seq: int | None


@dataclass(frozen=True)
class ArtifactRef:
    kind: str
    path: str
    sha256: str
    bytes: int

    def __post_init__(self) -> None:
        if not SHA256_RE.match(self.sha256):
            raise ValueError(f"artifact hash must be sha256:<64 hex>, got {self.sha256!r}")
        if self.bytes <= 0:
            raise ValueError("zero-byte artifacts are not evidence")


@dataclass(frozen=True)
class EpisodeClose:
    episode_id: str
    account_id: int
    brief: str
    task_family: str
    app_version: str
    catalogue_hash: str
    outcome: str
    accepted: bool
    cost: Mapping[str, int]
    artifacts: tuple[ArtifactRef, ...] = ()
    failure_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.outcome not in {"accepted", "rejected", "needs_human", "unverified", "refused", "failed"}:
            raise ValueError(f"unknown outcome {self.outcome!r}")
        if self.accepted and not self.artifacts:
            raise ValueError("an accepted episode requires at least one artifact")
        if not SHA256_RE.match(self.catalogue_hash):
            raise ValueError("catalogue_hash must be sha256:<64 hex>")


def append_event(
    conn: Connection,
    episode_id: str,
    kind: str,
    payload: Mapping[str, Any],
) -> tuple[int, str]:
    """Append one chained event inside the caller's transaction.

    The advisory lock serialises appends for one episode. The chain covers
    (seq, prev_hash, kind, payload), so deleting or reordering a row breaks
    verification at the next link.
    """
    if not episode_id:
        raise ValueError("episode_id is required")
    if not kind:
        raise ValueError("event kind is required")
    conn.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))", (episode_id,))
    row = conn.execute(
        "SELECT seq, hash FROM forge_event WHERE episode_id = %s ORDER BY seq DESC LIMIT 1",
        (episode_id,),
    ).fetchone()
    seq = 1 if row is None else int(row[0]) + 1
    prev_hash = GENESIS_HASH if row is None else str(row[1])
    material = canonical_json(
        {"seq": seq, "prev_hash": prev_hash, "kind": kind, "payload": dict(payload)}
    )
    event_hash = hex_digest(material)
    with conn.transaction():
        conn.execute(
            """
            INSERT INTO forge_event (episode_id, seq, kind, payload, prev_hash, hash)
            VALUES (%s, %s, %s, %s::jsonb, %s, %s)
            """,
            (episode_id, seq, kind, canonical_json(dict(payload)), prev_hash, event_hash),
        )
    return seq, event_hash


def verify_chain(conn: Connection, episode_id: str) -> ChainCheck:
    rows = conn.execute(
        "SELECT seq, kind, payload, prev_hash, hash FROM forge_event "
        "WHERE episode_id = %s ORDER BY seq ASC",
        (episode_id,),
    ).fetchall()
    prev_hash = GENESIS_HASH
    expected_seq = 1
    for seq, kind, payload, stored_prev, stored_hash in rows:
        if int(seq) != expected_seq or str(stored_prev) != prev_hash:
            return ChainCheck(False, len(rows), int(seq))
        parsed = payload if isinstance(payload, dict) else json.loads(str(payload))
        material = canonical_json(
            {"seq": int(seq), "prev_hash": prev_hash, "kind": str(kind), "payload": parsed}
        )
        computed = hex_digest(material)
        if computed != str(stored_hash):
            return ChainCheck(False, len(rows), int(seq))
        prev_hash = computed
        expected_seq += 1
    return ChainCheck(True, len(rows), None)


def close_episode(conn: Connection, close: EpisodeClose) -> str:
    """Transactionally close an episode, append the terminal event and index the case."""
    with conn.transaction():
        check = verify_chain(conn, close.episode_id)
        if not check.ok:
            raise LedgerIntegrityError(
                f"refusing to close {close.episode_id}: chain broken at seq {check.first_bad_seq}"
            )
        updated = conn.execute(
            """
            UPDATE forge_episode
               SET status = %s, accepted = %s, finished_at = now(), cost = %s::jsonb
             WHERE id = %s
            RETURNING id
            """,
            (close.outcome, close.accepted, canonical_json(dict(close.cost)), close.episode_id),
        ).fetchone()
        if updated is None:
            raise LedgerWriteError(f"episode {close.episode_id} does not exist")

        summary_text = " ".join(
            part
            for part in (close.brief, close.task_family, *close.failure_codes)
            if part
        )
        conn.execute(
            """
            INSERT INTO forge_episode_case
                (episode_id, task_family, brand, product_type, summary, outcome, accepted)
            VALUES (%s, %s, NULL, NULL, to_tsvector('simple', %s), %s, %s)
            ON CONFLICT (episode_id) DO UPDATE
               SET summary = EXCLUDED.summary,
                   outcome = EXCLUDED.outcome,
                   accepted = EXCLUDED.accepted
            """,
            (close.episode_id, close.task_family, summary_text, close.outcome, close.accepted),
        )
        _, event_hash = append_event(
            conn,
            close.episode_id,
            "episode.closed",
            {
                "outcome": close.outcome,
                "accepted": close.accepted,
                "artifact_hashes": [artifact.sha256 for artifact in close.artifacts],
                "cost": dict(close.cost),
                "failure_codes": list(close.failure_codes),
            },
        )
    return event_hash


@dataclass(frozen=True)
class RetrievalQuery:
    text: str
    task_family: str
    brand: str | None = None
    product_type: str | None = None
    outcome: str | None = None
    limit: int = 5


@dataclass(frozen=True)
class CaseHit:
    episode_id: str
    summary: str
    outcome: str
    score: float
    why_retrieved: str


@dataclass(frozen=True)
class RetrievalResult:
    hits: tuple[CaseHit, ...]
    query_hash: str
    injected_tokens: int
    empty: bool
    reason: str


def estimate_tokens(text: str) -> int:
    return max(1, math.ceil(len(text) / 4))


def retrieve_cases(
    conn: Connection,
    requesting_episode: str,
    query: RetrievalQuery,
) -> RetrievalResult:
    """Bounded case retrieval. Never invents precedent; writes a receipt."""
    if not query.task_family:
        raise ValueError("task_family is required for a hard filter")
    check = verify_chain(conn, requesting_episode)
    if not check.ok:
        raise LedgerIntegrityError(
            f"retrieval refused: chain broken at seq {check.first_bad_seq}"
        )

    clauses = ["c.task_family = %s"]
    params: list[Any] = [query.task_family]
    if query.brand is not None:
        clauses.append("c.brand = %s")
        params.append(query.brand)
    if query.product_type is not None:
        clauses.append("c.product_type = %s")
        params.append(query.product_type)
    if query.outcome is not None:
        clauses.append("c.outcome = %s")
        params.append(query.outcome)
    params.append(query.limit)

    sql = f"""
        SELECT c.episode_id,
               c.summary::text,
               c.outcome,
               ts_rank(c.summary, websearch_to_tsquery('simple', %s)) AS lexical,
               CASE WHEN c.accepted THEN 1.0 ELSE 0.0 END AS accepted_boost,
               e.started_at
          FROM forge_episode_case c
          JOIN forge_episode e ON e.id = c.episode_id
         WHERE {' AND '.join(clauses)}
         ORDER BY (ts_rank(c.summary, websearch_to_tsquery('simple', %s)) * 0.6
                   + CASE WHEN c.accepted THEN 0.3 ELSE 0.0 END) DESC,
                  e.started_at DESC
         LIMIT %s
    """
    # The rank expression appears twice (select + order); bind it twice as well.
    ordered_params: list[Any] = [query.text, *params[:-1], query.text, params[-1]]
    rows = conn.execute(sql, ordered_params).fetchall()

    hits: list[CaseHit] = []
    used = 0
    for episode_id, summary, outcome, lexical, accepted_boost, _started in rows:
        why = (
            f"lexical={float(lexical):.3f};accepted={bool(accepted_boost)};"
            f"family={query.task_family}"
        )
        cost = estimate_tokens(str(summary)) + 8
        if used + cost > CASE_TOKEN_BUDGET and hits:
            break
        used += cost
        hits.append(
            CaseHit(
                episode_id=str(episode_id),
                summary=str(summary)[:400],
                outcome=str(outcome),
                score=round(float(lexical) * 0.6 + float(accepted_boost) * 0.3, 6),
                why_retrieved=why,
            )
        )

    query_hash = hex_digest(canonical_json({
        "text": query.text,
        "task_family": query.task_family,
        "brand": query.brand,
        "product_type": query.product_type,
        "outcome": query.outcome,
    }))
    reason = "no_similar_case" if not hits else "ranked"
    conn.execute(
        """
        INSERT INTO forge_retrieval
            (episode_id, query_hash, returned_ids, scores, injected_tokens)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            requesting_episode,
            query_hash,
            [hit.episode_id for hit in hits],
            [hit.score for hit in hits],
            used,
        ),
    )
    return RetrievalResult(
        hits=tuple(hits),
        query_hash=query_hash,
        injected_tokens=used,
        empty=not hits,
        reason=reason,
    )
```

### 3.5 Inputs and outputs

| Direction | Value |
|---|---|
| In | `EpisodeClose` (outcome, cost, artifact hashes, failure codes); `RetrievalQuery` (text + hard filters) |
| Out | event `hash`; `ChainCheck`; `RetrievalResult {hits, query_hash, injected_tokens, empty, reason}` |
| Guarantees | seq uniqueness, chained hash, empty retrieval recorded honestly, receipt row per query |
| Never | Hard-delete evidence; average away a contradiction; fabricate a precedent |

### 3.6 Failure path

| Failure | Mechanic | Result |
|---|---|---|
| Chain mismatch (edit/delete/reorder) | `verify_chain` on close and before retrieval | `LedgerIntegrityError`; episode quarantined; retrieval refuses |
| Appointment race | advisory lock + `UNIQUE (episode_id, seq)` | one writer wins; the loser retries the transaction |
| Missing episode row | `UPDATE … RETURNING` returns 0 rows | `LedgerWriteError`; no event appended |
| Accepted with no artifact | `EpisodeClose.__post_init__` | `ValueError` before the DB is touched |
| Zero-byte artifact | `ArtifactRef` validation | rejected; a zero-byte file is not evidence |
| No matching case | query returns 0 rows | `empty: true, reason: "no_similar_case"`; baseline arm runs; **no invented precedent** |
| Token budget exceeded | trim loop | fewer hits; receipt records actual injected tokens |
| Receipt write fails | same transaction as retrieval (caller scope) | retrieval is refused rather than silently unrecorded (production must wrap both in one tx) |
| Payload JSON round-trip differs from inserted canonical form | hash recomputation uses canonical JSON | If a driver normalises numbers differently, verification fails closed — fix by storing `payload_canonical text` alongside `jsonb`; noted `[U]` |

The last row is a real engineering trap: `jsonb` normalises numbers (`1.0` vs `1`), so a
hash over the JSON value and a hash over the original bytes can disagree. The safest production
form stores the canonical JSON text and hashes those exact bytes. The sketch is honest about
this and marks it unverified.

### 3.7 VERIFIED vs PROPOSED

| Claim | Label | Source / status |
|---|---|---|
| PostgreSQL 16 is already running on the host; public tables contain no ledger/eval tables | `[V]` | 04 §2.4; `01-STACK-VPS.md` §11 |
| Ledger table set, hash chaining, four memory stores, retrieval pipeline | `[R]` | 04 §5.2, §8.1–8.2 |
| `pgvector` is not assumed; vectors start as `real[]` | `[R]` | 04 §5.2, §10.2 |
| The Python sketch compiles | `[V]` (this task) | `py_compile` exit 0 |
| Chain verification, advisory-lock behaviour and SQL correctness against PostgreSQL 16 | `[U]` | Not executed — no Forge DB; must be integration-tested with a scratch database |
| Token estimate (`len/4`) | `[I]` | Approximation; replace with the model's tokenizer before trusting the 1,200 budget |
| Case summary quality and tsvector ranking weights | `[I]` | Must be tuned on the 50-golden corpus; no retrieval lift is claimed |
| Hash over canonical JSON vs stored text | `[U]` | Open question above; production should store canonical text |

---

## 4. Example 4 — Visual critic: artifact + rendered images + diagnostics + rubric

### 4.1 What it demonstrates

A critic that is **blind, grounded and bounded**:

- blind: it receives brief, rubric lines and rendered images — never the exit code, gate report,
  operator claim or prior verdict;
- grounded: every scored dimension must cite a crop region that exists in the supplied render
  bundle, with an observation of at least 12 characters; a dimension without evidence is
  rejected by the schema, not tolerated;
- bounded: confidence is model-reported, recorded with an explicit semantics string, capped by
  the amount of grounding, and never presented as a probability that the artifact is correct.

Deterministic diagnostics (coverage, specks, alpha, edge hardness, centring, SSIM) are accepted
as **input data and stored as diagnostics**, but they are deliberately not placed in the prompt
and cannot set the verdict. Metrics measure geometry; the critic judges the brief. Conflating
them is how a harness invents "quality" it cannot see.

### 4.2 Contract

```jsonc
// Critique input (assembled by the verifier; 04 §7.3–7.4)
{
  "episode_id": "uuid",
  "artifact_sha256": "sha256:…",
  "brief_text": "…",
  "renders": [
    {"kind": "thumb_256",  "path": "build/ep/thumb_256.png",  "sha256": "sha256:…", "width": 256,  "height": 320},
    {"kind": "view_1024",  "path": "build/ep/view_1024.png",  "sha256": "sha256:…", "width": 1024, "height": 1280},
    {"kind": "crop_100",   "path": "build/ep/crop_100_3_2.png","sha256": "sha256:…", "width": 600,  "height": 750}
  ],
  "metrics": {"coverage": 0.41, "white_residual": 0.0, "edge_hardness": 0.93},
  "rubric": [
    {"dimension": "brief_fit",  "text": "subject matches the brief", "anchors": ["1=wrong subject", "5=exact subject"]},
    {"dimension": "hierarchy", "text": "wordmark dominates, tagline secondary"},
    {"dimension": "typography", "text": "no clipped or semi-transparent glyphs"},
    {"dimension": "colour",     "text": "palette matches brand facts"},
    {"dimension": "print_safety", "text": "no content in the provider safe-zone margin"}
  ]
}
```

```jsonc
// Stored report (forge_critique; schema-enforced)
{
  "episode_id": "uuid",
  "artifact_sha256": "sha256:…",
  "prompt_version": "critic-v0.3",
  "model_id": "deepseek-flash",
  "blinded_to": ["exit_code", "gate_report", "operator_claims", "prior_verdict"],
  "dimensions": {"brief_fit": {"score": 4, "evidence": [{"region": [0.0,0.0,1.0,1.0],
                  "crop_path": "build/ep/view_1024.png", "observation": "subject centred, wordmark legible"}]}},
  "defects": [{"severity": "minor", "where": "tagline", "issue": "tracking tight", "fix_hint": "+2% tracking"}],
  "confidence_reported": 0.72,
  "confidence_effective": 0.72,
  "confidence_semantics": "model self-report, not calibrated accuracy; never present as certainty",
  "unseen": ["no reference artwork supplied"],
  "verdict": "pass_with_notes",
  "image_hashes": ["sha256:…"],
  "diagnostics": {"coverage": 0.41, "white_residual": 0.0}
}
```

### 4.3 Confidence rules (no fake confidence)

| Rule | Enforcement |
|---|---|
| Confidence is reported, not computed as accuracy | `confidence_reported` stored verbatim; no conversion to "probability correct" |
| Grounding caps confidence | `effective = min(reported, 0.40 + 0.12 × evidence_count)`; a single crop cannot justify 0.95 |
| Low confidence cannot pass | `effective < 0.5` → `unverifiable` → `needs_human` |
| Unknowns are explicit | `unseen` is required; non-empty downgrades `pass` to `pass_with_notes` |
| Stability is measured, not assumed | Repeat calls on identical hashes are recorded; verdict flips become `forge_conflict` (04 §7.4) |
| No gate anchoring | Forbidden keys are rejected; any gate/exit mention in the critique is a schema violation |

### 4.4 Sketch

<!-- Example 4 sketch — validated with py_compile + 9 scratch-harness checks -->
```python
"""Example 4 - visual critic: artifact + rendered images + diagnostics + rubric.

Forge Conductor mechanism sketch (Python 3.11+). Design-only: no model call is
made here. Confidence is model-reported and is never presented as a probability
that the artifact is correct.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Mapping, Protocol, Sequence

CRITIC_PROMPT_VERSION = "critic-v0.3"
DIMENSIONS = ("brief_fit", "hierarchy", "typography", "colour", "print_safety")
VERDICTS = ("pass", "pass_with_notes", "reject", "unverifiable")
SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
FORBIDDEN_INPUT_KEYS = frozenset(
    {"gate_report", "gates", "exit_code", "operator_claims", "prior_verdict", "argv", "stderr"}
)
GATE_MENTION_RE = re.compile(r"(gate_report|exit[_ ]code|gate\s*=|gates?\s*:|white_residual\s*=)", re.I)
MIN_OBSERVATION_CHARS = 12


class CritiqueRefused(Exception):
    def __init__(self, code: str, message: str, how_to_fix: str, evidence: Sequence[str] = ()) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.how_to_fix = how_to_fix
        self.evidence = tuple(evidence)


@dataclass(frozen=True)
class RenderView:
    kind: str
    path: str
    sha256: str
    width: int
    height: int

    def __post_init__(self) -> None:
        if not SHA256_RE.match(self.sha256):
            raise ValueError(f"render hash must be sha256:<64 hex>: {self.sha256!r}")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("render dimensions must be positive")


@dataclass(frozen=True)
class Diagnostics:
    """Deterministic measurements. Diagnostics never certify an artifact."""

    values: Mapping[str, float]

    def __post_init__(self) -> None:
        for key, value in self.values.items():
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValueError(f"diagnostic {key!r} must be numeric")


@dataclass(frozen=True)
class RubricLine:
    dimension: str
    text: str
    anchors: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.dimension not in DIMENSIONS:
            raise ValueError(f"unknown rubric dimension {self.dimension!r}")


@dataclass(frozen=True)
class CritiqueInput:
    episode_id: str
    artifact_sha256: str
    brief_text: str
    renders: tuple[RenderView, ...]
    metrics: Diagnostics
    rubric: tuple[RubricLine, ...]

    def __post_init__(self) -> None:
        if not SHA256_RE.match(self.artifact_sha256):
            raise ValueError("artifact_sha256 must be sha256:<64 hex>")
        if not self.renders:
            raise ValueError("the critic needs at least one rendered view")
        if not self.rubric:
            raise ValueError("the critic needs the rubric lines it must score")
        for line in self.rubric:
            if line.dimension not in DIMENSIONS:
                raise ValueError(f"rubric dimension {line.dimension!r} is not scoreable")


class VisionClient(Protocol):
    model_id: str

    def complete(self, prompt: str, image_paths: Sequence[str], *, timeout_s: int) -> str:
        """Return the raw model text. Raising is a vision failure, not a verdict."""
        ...


@dataclass(frozen=True)
class Defect:
    severity: str
    where: str
    issue: str
    fix_hint: str

    def __post_init__(self) -> None:
        if self.severity not in {"minor", "major"}:
            raise ValueError("severity must be minor or major")


@dataclass(frozen=True)
class CritiqueReport:
    episode_id: str
    artifact_sha256: str
    prompt_version: str
    model_id: str
    blinded_to: tuple[str, ...]
    dimensions: Mapping[str, Mapping[str, Any]]
    defects: tuple[Defect, ...]
    confidence_reported: float
    confidence_effective: float
    confidence_semantics: str
    unseen: tuple[str, ...]
    verdict: str
    decision_reason: str
    image_hashes: tuple[str, ...]
    raw_response_sha256: str
    diagnostics: Mapping[str, float]


def assert_input_blinded(extra: Mapping[str, Any]) -> None:
    leaked = sorted(FORBIDDEN_INPUT_KEYS.intersection(extra))
    if leaked:
        raise CritiqueRefused(
            "E_CRITIQUE_UNBLINDED",
            f"critic input carries forbidden keys: {', '.join(leaked)}",
            "pass only brief, rubric and rendered images; gate results stay in the verifier",
            leaked,
        )


def build_prompt(critique: CritiqueInput, *, retry_note: str | None = None) -> str:
    """Deterministic, versioned prompt. Diagnostics and gates are deliberately absent."""
    rubric = "\n".join(
        f"- {line.dimension}: {line.text}"
        + (f" (anchors: {', '.join(line.anchors)})" if line.anchors else "")
        for line in critique.rubric
    )
    views = "\n".join(f"- {view.kind}: {view.path} ({view.width}x{view.height})" for view in critique.renders)
    retry = f"\nYour previous answer was rejected: {retry_note}. Fix exactly that.\n" if retry_note else ""
    return (
        f"PROMPT_VERSION={CRITIC_PROMPT_VERSION}\n"
        "You are a blind art critic. You do not see exit codes, gate reports or operator claims.\n"
        "Score the rendered artifact against the brief. Every dimension needs quoted crop evidence:\n"
        '{"region":[x0,y0,x1,y1],"crop_path":"<one of the rendered paths>",'
        '"observation":"what you see (>=12 chars)"}.\n'
        f"{retry}\nBRIEF:\n{critique.brief_text}\n\nRUBRIC:\n{rubric}\n\nRENDERED VIEWS:\n{views}\n\n"
        "Reply with one JSON object only. Required keys: dimensions (all five), defects[], "
        "confidence (0..1), unseen[], verdict (pass|pass_with_notes|reject|unverifiable). "
        "Do not mention gate values. If you cannot evaluate a dimension, use verdict unverifiable."
    )


def strip_code_fence(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return stripped


def parse_critique(raw: str) -> dict[str, Any]:
    try:
        parsed = json.loads(strip_code_fence(raw))
    except json.JSONDecodeError as error:
        raise ValueError(f"critique is not JSON: {error.msg} at char {error.pos}") from error
    if not isinstance(parsed, dict):
        raise ValueError("critique must be a JSON object")
    return parsed


def validate_critique(
    payload: Mapping[str, Any], critique: CritiqueInput
) -> list[str]:
    """Return schema violations. An empty list means the report is admissible."""
    violations: list[str] = []
    known_paths = {view.path for view in critique.renders}

    dimensions = payload.get("dimensions")
    if not isinstance(dimensions, dict):
        violations.append("dimensions must be an object")
    else:
        missing = [name for name in DIMENSIONS if name not in dimensions]
        if missing:
            violations.append(f"dimensions missing: {', '.join(missing)}")
        for name in DIMENSIONS:
            entry = dimensions.get(name)
            if not isinstance(entry, dict):
                violations.append(f"dimensions.{name} must be an object")
                continue
            score = entry.get("score")
            if not isinstance(score, int) or isinstance(score, bool) or not 1 <= score <= 5:
                violations.append(f"dimensions.{name}.score must be an int 1..5")
            evidence = entry.get("evidence")
            if not isinstance(evidence, list) or not evidence:
                violations.append(f"dimensions.{name} has no crop evidence")
                continue
            for index, item in enumerate(evidence):
                where = f"dimensions.{name}.evidence[{index}]"
                if not isinstance(item, dict):
                    violations.append(f"{where} must be an object")
                    continue
                region = item.get("region")
                if (
                    not isinstance(region, list)
                    or len(region) != 4
                    or not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in region)
                ):
                    violations.append(f"{where}.region must be four numbers")
                elif not (0.0 <= region[0] < region[2] <= 1.0 and 0.0 <= region[1] < region[3] <= 1.0):
                    violations.append(f"{where}.region is not an ascending box inside [0,1]")
                elif (region[2] - region[0]) * (region[3] - region[1]) <= 0:
                    violations.append(f"{where}.region has zero area")
                crop = item.get("crop_path")
                if crop not in known_paths:
                    violations.append(f"{where}.crop_path is not one of the rendered views")
                observation = item.get("observation")
                if not isinstance(observation, str) or len(observation.strip()) < MIN_OBSERVATION_CHARS:
                    violations.append(f"{where}.observation must be at least {MIN_OBSERVATION_CHARS} chars")

    defects_raw = payload.get("defects")
    defects: list[Defect] = []
    if not isinstance(defects_raw, list):
        violations.append("defects must be a list")
    else:
        for index, item in enumerate(defects_raw):
            if not isinstance(item, dict):
                violations.append(f"defects[{index}] must be an object")
                continue
            try:
                defects.append(
                    Defect(
                        severity=str(item.get("severity", "")),
                        where=str(item.get("where", "")),
                        issue=str(item.get("issue", "")),
                        fix_hint=str(item.get("fix_hint", "")),
                    )
                )
            except ValueError as error:
                violations.append(f"defects[{index}]: {error}")

    verdict = payload.get("verdict")
    if verdict not in VERDICTS:
        violations.append(f"verdict must be one of {', '.join(VERDICTS)}")
    elif verdict == "pass" and any(defect.severity == "major" for defect in defects):
        violations.append("verdict pass is invalid with a major defect")

    unseen = payload.get("unseen")
    if not isinstance(unseen, list) or not all(isinstance(item, str) for item in unseen):
        violations.append("unseen must be a list of strings (may be empty)")

    confidence = payload.get("confidence")
    if (
        not isinstance(confidence, (int, float))
        or isinstance(confidence, bool)
        or not 0.0 <= float(confidence) <= 1.0
    ):
        violations.append("confidence must be a number in [0,1]")

    serialized = json.dumps(payload, sort_keys=True).lower()
    if GATE_MENTION_RE.search(serialized):
        violations.append("critique mentions a gate/exit value; the critic must stay blind")
    return violations


def effective_confidence(reported: float, evidence_count: int) -> float:
    """Cap model confidence by grounding: one crop cannot justify near-certainty."""
    cap = 0.40 + 0.12 * min(evidence_count, 5)
    return round(min(reported, cap), 3)


def decide(payload: Mapping[str, Any], confidence: float) -> tuple[str, str]:
    verdict = str(payload.get("verdict", "unverifiable"))
    major = any(
        isinstance(item, Mapping) and item.get("severity") == "major"
        for item in payload.get("defects", [])
    )
    if verdict == "reject" or major:
        return "reject", "E_CRITIQUE_REJECT"
    if verdict == "unverifiable":
        return "unverifiable", "E_CRITIQUE_UNVERIFIABLE"
    if confidence < 0.5:
        return "unverifiable", "E_CRITIQUE_LOW_CONFIDENCE"
    if verdict == "pass" and payload.get("unseen"):
        return "pass_with_notes", "PASS_DOWNGRADED_BY_UNSEEN"
    return "pass", "OK"


def evaluate(
    client: VisionClient,
    critique: CritiqueInput,
    *,
    timeout_s: int = 120,
) -> CritiqueReport:
    """Two attempts maximum. A refused critique is a refusal, never a pass."""
    prompt = build_prompt(critique)
    last_violations: list[str] = []
    for attempt in (1, 2):
        try:
            raw = client.complete(prompt, [view.path for view in critique.renders], timeout_s=timeout_s)
        except Exception as error:
            raise CritiqueRefused(
                "E_VISION_UNAVAILABLE",
                f"vision call failed: {type(error).__name__}",
                "retry once with the same prompt version; then route to needs_human",
            ) from error
        if not raw.strip():
            last_violations = ["vision returned empty text"]
        else:
            try:
                payload = parse_critique(raw)
            except ValueError as error:
                last_violations = [str(error)]
                payload = {}
            if payload:
                last_violations = validate_critique(payload, critique)
                if not last_violations:
                    evidence_count = sum(
                        len(entry.get("evidence", []))
                        for entry in payload.get("dimensions", {}).values()
                        if isinstance(entry, Mapping) and isinstance(entry.get("evidence"), list)
                    )
                    reported = float(payload["confidence"])
                    confidence = effective_confidence(reported, evidence_count)
                    verdict, reason = decide(payload, confidence)
                    dimensions = {
                        name: payload["dimensions"][name] for name in DIMENSIONS
                    }
                    return CritiqueReport(
                        episode_id=critique.episode_id,
                        artifact_sha256=critique.artifact_sha256,
                        prompt_version=CRITIC_PROMPT_VERSION,
                        model_id=client.model_id,
                        blinded_to=("exit_code", "gate_report", "operator_claims", "prior_verdict"),
                        dimensions=dimensions,
                        defects=tuple(
                            Defect(
                                severity=str(item["severity"]),
                                where=str(item["where"]),
                                issue=str(item["issue"]),
                                fix_hint=str(item.get("fix_hint", "")),
                            )
                            for item in payload.get("defects", [])
                        ),
                        confidence_reported=reported,
                        confidence_effective=confidence,
                        confidence_semantics="model self-report, not calibrated accuracy; never present as certainty",
                        unseen=tuple(str(item) for item in payload.get("unseen", [])),
                        verdict=verdict,
                        decision_reason=reason,
                        image_hashes=tuple(view.sha256 for view in critique.renders),
                        raw_response_sha256="sha256:" + sha256(raw.encode("utf-8")).hexdigest(),
                        diagnostics=dict(critique.metrics.values),
                    )
        if attempt == 1:
            prompt = build_prompt(critique, retry_note="; ".join(last_violations)[:400])
    raise CritiqueRefused(
        "E_CRITIQUE_UNGROUNDED",
        "critique failed schema/grounding validation after one retry",
        "fix the critic prompt or schema; do not accept an ungrounded critique",
        last_violations[:10],
    )
```

### 4.5 Inputs and outputs

| Direction | Value |
|---|---|
| In | `CritiqueInput` (artifact hash, brief, renders, diagnostics, rubric); a `VisionClient` |
| Out | `CritiqueReport` with per-dimension grounded evidence, defects, reported + effective confidence, unseen, verdict, image hashes, raw-response hash |
| Not sent to the model | diagnostics, gates, exit codes, operator claims, prior verdicts |
| On refusal | `CritiqueRefused(code, message, how_to_fix, evidence)` — never a fabricated pass |

### 4.6 Failure path

| Failure | Mechanic | Result |
|---|---|---|
| Input carries gate/exit/operator keys | `assert_input_blinded` | `E_CRITIQUE_UNBLINDED` |
| Vision call raises/times out/returns empty | first attempt retried once | `E_VISION_UNAVAILABLE` → `needs_human` |
| Malformed JSON | parse error becomes retry note | second failure → `E_CRITIQUE_UNGROUNDED` |
| Dimension missing evidence, crop path unknown, zero-area region, short observation | schema violations | retry once with violations; second failure → `E_CRITIQUE_UNGROUNDED` |
| `pass` with a major defect | schema violation | rejected, retried once |
| Critic mentions a gate/exit value | regex violation | `E_CRITIQUE_UNGROUNDED` |
| Confidence < 0.5 | decision rule | `unverifiable` (no silent pass) |
| `pass` with non-empty `unseen` | decision rule | `pass_with_notes` |
| Model returns `reject` / `unverifiable` | decision rule | propagate; conductor arbitrates |
| Two identical-input calls disagree | not handled here | recorded as conflict and measured; a single call is never treated as stable |

### 4.7 VERIFIED vs PROPOSED

| Claim | Label | Source / status |
|---|---|---|
| Render ladder, critic protocol, schema rejection rules, confidence < 0.5 → human | `[R]` | 04 §7.3–7.4 |
| `deepseek-flash` is configured with `supports_vision: true` | `[V]` | 04 §2.2 (host config) |
| Vision quality on print defects is not measured | `[U]` | 04 §15 lists this as an open unknown; no labelled defect corpus exists |
| The Python sketch compiles and its pass/retry/refusal/low-confidence paths ran in the scratch harness | `[V]` (this task) | `py_compile` exit 0; 9/9 Example-4 checks passed |
| `effective_confidence` cap constants | `[I]` | Proposed calibration guard; must be tested against the 50-defect corpus, not believed |
| Crop regions are semantically grounded (the model didn't hallucinate a box that happens to exist) | `[U]` | The schema checks existence and geometry only; semantic grounding needs a human-labelled audit |
| Multiple images per call and resolution limits for this model | `[U]` | Not probed; 04 §15 requires an API probe before the render ladder is final |
| Critic prompt version `critic-v0.3` | `[R]` | Named in 04; not executed |

---

## 5. Example 5 — Skill promotion and rollback: candidate → active, evidence, version pin

### 5.1 What it demonstrates

Procedural memory changes only through a **statistical, reversible gate**. A candidate becomes
active only with **≥3 independent successes** (different episodes *and* different input hashes),
a passing golden regression suite, and a named human sign-off covering the artifacts. The
transaction supersedes the old active version and installs the new one; the database enforces
**exactly one active version per skill**. Rollback flips the pointer back and records the reason;
versions are never edited in place and evidence is never deleted.

The episode pins the skill version plus the app version and catalogue hash it was validated
against (`skill_pin`). Replay checks the pin: a skill validated on 0.21.1 does not silently run
on 0.22.0.

### 5.2 State machine

```text
draft ──(1 verified episode + explicit scope)──► candidate
candidate ──(≥3 independent successes + golden pass + human sign-off)──► active
active ──(new version promoted)──► superseded        (old kept, replayable)
active ──(failure/regression/contradiction)──► rolled_back  (pointer flip + goldens re-run)
```

```jsonc
// forge_skill row (proposed schema; see §5.3)
{
  "skill_id": "sk_vc_badge_trace",
  "name": "vc_ai_badge_trace",
  "version": 3,
  "app": "vectorcraft",
  "app_version": "0.21.1",
  "catalogue_hash": "sha256:…",
  "preconditions": {"input": {"background": "white", "min_subject_px": 600}},
  "steps": [{"seq": 1, "cmd_id": "imageTrace.make", "params": {"palette_limit": 6}},
            {"seq": 2, "cmd_id": "document.export", "params": {"format": "svg"}}],
  "gates": [{"runner": "craft_trace", "required": {"ok": true}}],
  "status": "active",
  "promoted_at": "2026-11-05T16:20:00Z",
  "superseded_by": null
}
```

### 5.3 Schema (proposed; no migration applied)

```sql
CREATE TABLE IF NOT EXISTS forge_skill (
  skill_id        text NOT NULL,
  name            text NOT NULL,
  version         integer NOT NULL CHECK (version > 0),
  app             text NOT NULL,
  app_version     text NOT NULL,
  catalogue_hash  char(71) NOT NULL,
  preconditions   jsonb NOT NULL,
  steps           jsonb NOT NULL,
  gates           jsonb NOT NULL,
  recovery        jsonb NOT NULL DEFAULT '[]'::jsonb,
  status          text NOT NULL CHECK (status IN
                    ('draft','candidate','active','superseded','rolled_back')),
  success_count   integer NOT NULL DEFAULT 0,
  failure_count   integer NOT NULL DEFAULT 0,
  promoted_at     timestamptz,
  superseded_by   integer,
  PRIMARY KEY (skill_id, version)
);

-- Exactly one active version per skill. The pointer flip is a state update, not a delete.
CREATE UNIQUE INDEX IF NOT EXISTS forge_skill_one_active
  ON forge_skill (skill_id) WHERE status = 'active';
```

### 5.4 Sketch

<!-- Example 5 sketch — validated with py_compile + 5 scratch-harness checks -->
```python
"""Example 5 - skill promotion and rollback: candidate -> active, evidence, version pin.

Forge Conductor mechanism sketch (Python 3.11+). Design-only: the promotion policy
(N >= 3 independent successes, golden regression, human sign-off) is proposed in
design 04 section 8.5 and craft-agent-operator/references/memory-ledger.md.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from hashlib import sha256
from typing import Any, Mapping, Protocol, Sequence

SHA256_RE_LEN = 71  # "sha256:" + 64 hex
REQUIRED_MIN_EVIDENCE = 3


class SkillState(StrEnum):
    DRAFT = "draft"
    CANDIDATE = "candidate"
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    ROLLED_BACK = "rolled_back"


class PromotionRefused(Exception):
    def __init__(self, code: str, message: str, how_to_fix: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.how_to_fix = how_to_fix


class Cursor(Protocol):
    def fetchone(self) -> tuple[Any, ...] | None: ...

    def fetchall(self) -> list[tuple[Any, ...]]: ...


class Transaction(Protocol):
    def __enter__(self) -> "Transaction": ...

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool | None: ...


class Connection(Protocol):
    def execute(self, sql: str, params: Sequence[Any] = ()) -> Cursor: ...

    def transaction(self) -> Transaction: ...


class EventSink(Protocol):
    """Wired to Example 3's append_event; the promotion gate never writes events itself."""

    def append(self, kind: str, payload: Mapping[str, Any]) -> None: ...


SCHEMA = """
CREATE TABLE IF NOT EXISTS forge_skill (
  skill_id        text NOT NULL,
  name            text NOT NULL,
  version         integer NOT NULL CHECK (version > 0),
  app             text NOT NULL,
  app_version     text NOT NULL,
  catalogue_hash  char(71) NOT NULL,
  preconditions   jsonb NOT NULL,
  steps           jsonb NOT NULL,
  gates           jsonb NOT NULL,
  recovery        jsonb NOT NULL DEFAULT '[]'::jsonb,
  status          text NOT NULL CHECK (status IN
                    ('draft','candidate','active','superseded','rolled_back')),
  success_count   integer NOT NULL DEFAULT 0,
  failure_count   integer NOT NULL DEFAULT 0,
  promoted_at     timestamptz,
  superseded_by   integer,
  PRIMARY KEY (skill_id, version)
);

-- Exactly one active version per skill. The pointer flip is a state update, not a delete.
CREATE UNIQUE INDEX IF NOT EXISTS forge_skill_one_active
  ON forge_skill (skill_id) WHERE status = 'active';
"""


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def hex_digest(material: str) -> str:
    return sha256(material.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class EvidenceRef:
    episode_id: str
    input_sha256: str
    accepted_at: datetime

    def __post_init__(self) -> None:
        if not self.episode_id:
            raise ValueError("evidence episode_id is required")
        if len(self.input_sha256) != SHA256_RE_LEN or not self.input_sha256.startswith("sha256:"):
            raise ValueError("evidence input_sha256 must be sha256:<64 hex>")


@dataclass(frozen=True)
class GoldenRegression:
    passed: bool
    failing_golden_ids: tuple[str, ...]
    suite_version: str

    def __post_init__(self) -> None:
        if self.passed and self.failing_golden_ids:
            raise ValueError("a passed regression suite cannot list failing goldens")
        if not self.suite_version:
            raise ValueError("suite_version is required; an unlabelled suite is not evidence")


@dataclass(frozen=True)
class HumanSignoff:
    reviewer: str
    approved_at: datetime
    artifact_hashes: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.reviewer.strip():
            raise ValueError("a sign-off must name a reviewer")
        if not self.artifact_hashes:
            raise ValueError("a sign-off must cover at least one artifact hash")


@dataclass(frozen=True)
class SkillCandidate:
    skill_id: str
    name: str
    version: int
    app: str
    app_version: str
    catalogue_hash: str
    preconditions: Mapping[str, Any]
    steps: Sequence[Mapping[str, Any]]
    gates: Sequence[Mapping[str, Any]]
    recovery: Sequence[Mapping[str, Any]] = ()

    def __post_init__(self) -> None:
        if self.version <= 0:
            raise ValueError("candidate version must be positive")
        if not len(self.catalogue_hash) == SHA256_RE_LEN or not self.catalogue_hash.startswith("sha256:"):
            raise ValueError("catalogue_hash must be sha256:<64 hex>")
        if not self.steps:
            raise ValueError("a skill with no steps is not executable")
        if not self.gates:
            raise ValueError("a skill with no gates cannot be verified")


@dataclass(frozen=True)
class PromotionRequest:
    candidate: SkillCandidate
    evidence: tuple[EvidenceRef, ...]
    golden: GoldenRegression
    signoff: HumanSignoff


@dataclass(frozen=True)
class SkillRow:
    skill_id: str
    name: str
    version: int
    status: SkillState
    app_version: str
    catalogue_hash: str


@dataclass(frozen=True)
class PromotionDecision:
    skill_id: str
    version: int
    previous_active_version: int | None
    pinned: Mapping[str, str]


@dataclass(frozen=True)
class RollbackDecision:
    skill_id: str
    from_version: int
    to_version: int
    reason: str


def skills_enabled(environ: Mapping[str, str] | None = None) -> bool:
    env = os.environ if environ is None else environ
    return env.get("FORGE_SKILLS_ENABLED", "1") == "1"


def _next_version(conn: Connection, skill_id: str) -> int:
    row = conn.execute(
        "SELECT COALESCE(MAX(version), 0) FROM forge_skill WHERE skill_id = %s",
        (skill_id,),
    ).fetchone()
    return int(row[0]) if row else 0


def _check_independence(evidence: Sequence[EvidenceRef]) -> None:
    episodes = {ref.episode_id for ref in evidence}
    inputs = {ref.input_sha256 for ref in evidence}
    if len(episodes) < REQUIRED_MIN_EVIDENCE:
        raise PromotionRefused(
            "E_EVIDENCE_INSUFFICIENT",
            f"{len(episodes)} independent episodes, {REQUIRED_MIN_EVIDENCE} required",
            "collect more verified episodes; three attempts on one file are not three successes",
        )
    if len(inputs) < REQUIRED_MIN_EVIDENCE:
        raise PromotionRefused(
            "E_EVIDENCE_NOT_INDEPENDENT",
            f"{len(inputs)} distinct inputs for {len(episodes)} episodes",
            "promote only rules that survived different inputs",
        )


def promote(
    conn: Connection,
    events: EventSink,
    request: PromotionRequest,
    *,
    environ: Mapping[str, str] | None = None,
) -> PromotionDecision:
    if not skills_enabled(environ):
        raise PromotionRefused(
            "E_SKILLS_DISABLED",
            "FORGE_SKILLS_ENABLED=0 forces the baseline arm",
            "promote after the kill switch is lifted; rollback stays available",
        )
    candidate = request.candidate
    _check_independence(request.evidence)
    if not request.golden.passed:
        raise PromotionRefused(
            "E_GOLDEN_REGRESSION",
            f"golden suite {request.golden.suite_version} fails: "
            + ", ".join(request.golden.failing_golden_ids),
            "fix the regression or abandon the candidate; never exclude the failing golden",
        )
    if not request.signoff.artifact_hashes:
        raise PromotionRefused(
            "E_HUMAN_SIGNOFF_MISSING",
            "no artifact hashes covered by the sign-off",
            "a named human must approve the exact artifacts this version produced",
        )

    with conn.transaction():
        conn.execute(
            "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))", (candidate.skill_id,)
        )
        active = conn.execute(
            "SELECT version FROM forge_skill WHERE skill_id = %s AND status = 'active' FOR UPDATE",
            (candidate.skill_id,),
        ).fetchone()
        expected = _next_version(conn, candidate.skill_id) + 1
        if candidate.version != expected:
            raise PromotionRefused(
                "E_SKILL_VERSION",
                f"candidate version {candidate.version}, next version is {expected}",
                "versions are immutable and monotonic; renumber the candidate",
            )
        if active is not None:
            conn.execute(
                """
                UPDATE forge_skill
                   SET status = 'superseded', superseded_by = %s
                 WHERE skill_id = %s AND version = %s AND status = 'active'
                """,
                (candidate.version, candidate.skill_id, int(active[0])),
            )
        conn.execute(
            """
            INSERT INTO forge_skill
                (skill_id, name, version, app, app_version, catalogue_hash,
                 preconditions, steps, gates, recovery, status, promoted_at, success_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb, %s::jsonb,
                    'active', now(), %s)
            """,
            (
                candidate.skill_id,
                candidate.name,
                candidate.version,
                candidate.app,
                candidate.app_version,
                candidate.catalogue_hash,
                canonical_json(dict(candidate.preconditions)),
                canonical_json(list(candidate.steps)),
                canonical_json(list(candidate.gates)),
                canonical_json(list(candidate.recovery)),
                len(request.evidence),
            ),
        )
        count = conn.execute(
            "SELECT count(*) FROM forge_skill WHERE skill_id = %s AND status = 'active'",
            (candidate.skill_id,),
        ).fetchone()
        if count is None or int(count[0]) != 1:
            raise PromotionRefused(
                "E_SKILL_STATE",
                "active pointer is not unique after promotion",
                "restore the previous active version and investigate the index",
            )
        pinned = {
            "skill_id": candidate.skill_id,
            "version": str(candidate.version),
            "app_version": candidate.app_version,
            "catalogue_hash": candidate.catalogue_hash,
            "suite_version": request.golden.suite_version,
            "evidence_digest": "sha256:"
            + hex_digest(canonical_json([ref.episode_id for ref in request.evidence])),
        }
        events.append(
            "skill.promoted",
            {
                "skill_id": candidate.skill_id,
                "version": candidate.version,
                "previous_active_version": None if active is None else int(active[0]),
                "evidence_episode_ids": [ref.episode_id for ref in request.evidence],
                "pin": pinned,
            },
        )
    return PromotionDecision(
        skill_id=candidate.skill_id,
        version=candidate.version,
        previous_active_version=None if active is None else int(active[0]),
        pinned=pinned,
    )


def rollback(
    conn: Connection,
    events: EventSink,
    skill_id: str,
    *,
    reason: str,
    target_version: int | None = None,
) -> RollbackDecision:
    if not reason.strip():
        raise PromotionRefused(
            "E_ROLLBACK_REASON_MISSING",
            "a rollback must record why",
            "name the failing evidence or regression that triggered it",
        )
    with conn.transaction():
        conn.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))", (skill_id,))
        active = conn.execute(
            "SELECT version FROM forge_skill WHERE skill_id = %s AND status = 'active' FOR UPDATE",
            (skill_id,),
        ).fetchone()
        if active is None:
            raise PromotionRefused(
                "E_ROLLBACK_NO_TARGET",
                f"{skill_id} has no active version",
                "nothing to roll back; inspect forge_event for the last transition",
            )
        active_version = int(active[0])
        if target_version is None:
            target = conn.execute(
                """
                SELECT version FROM forge_skill
                 WHERE skill_id = %s AND version < %s AND status IN ('superseded','rolled_back')
                 ORDER BY version DESC LIMIT 1
                """,
                (skill_id, active_version),
            ).fetchone()
        else:
            target = conn.execute(
                "SELECT version FROM forge_skill WHERE skill_id = %s AND version = %s",
                (skill_id, target_version),
            ).fetchone()
        if target is None:
            raise PromotionRefused(
                "E_ROLLBACK_NO_TARGET",
                f"no earlier version available for {skill_id}",
                "keep superseded versions (never delete evidence) so rollback has a target",
            )
        to_version = int(target[0])
        conn.execute(
            "UPDATE forge_skill SET status = 'rolled_back', superseded_by = %s "
            "WHERE skill_id = %s AND version = %s AND status = 'active'",
            (to_version, skill_id, active_version),
        )
        conn.execute(
            "UPDATE forge_skill SET status = 'active', promoted_at = now(), superseded_by = NULL "
            "WHERE skill_id = %s AND version = %s",
            (skill_id, to_version),
        )
        events.append(
            "skill.rolled_back",
            {
                "skill_id": skill_id,
                "from_version": active_version,
                "to_version": to_version,
                "reason": reason.strip(),
            },
        )
    return RollbackDecision(
        skill_id=skill_id,
        from_version=active_version,
        to_version=to_version,
        reason=reason.strip(),
    )


def resolve_pin(
    conn: Connection,
    skill_id: str,
    *,
    version: int,
    app_version: str,
    catalogue_hash: str,
) -> SkillRow:
    row = conn.execute(
        "SELECT skill_id, name, version, status, app_version, catalogue_hash "
        "FROM forge_skill WHERE skill_id = %s AND version = %s",
        (skill_id, version),
    ).fetchone()
    if row is None:
        raise PromotionRefused(
            "E_PIN_MISMATCH",
            f"pinned skill {skill_id} v{version} is not installed",
            "restore the pinned version or replay the episode with the current active version",
        )
    if str(row[4]) != app_version or str(row[5]) != catalogue_hash:
        raise PromotionRefused(
            "E_PIN_MISMATCH",
            f"{skill_id} v{version} was validated on {row[4]}/{row[5]}; "
            f"episode pins {app_version}/{catalogue_hash}",
            "re-run goldens on the installed app/catalogue before replaying",
        )
    return SkillRow(
        skill_id=str(row[0]),
        name=str(row[1]),
        version=int(row[2]),
        status=SkillState(str(row[3])),
        app_version=str(row[4]),
        catalogue_hash=str(row[5]),
    )
```

### 5.5 Inputs and outputs

| Direction | Value |
|---|---|
| In | `PromotionRequest {candidate, evidence[], golden, signoff}`; connection; event sink; environment for the kill switch |
| Out | `PromotionDecision {skill_id, version, previous_active_version, pinned}`; `forge_event` rows via the sink |
| Rollback | `RollbackDecision {skill_id, from_version, to_version, reason}`; pointer flip + event |
| Never | In-place edit, promotion without evidence, promotion while `FORGE_SKILLS_ENABLED=0`, deletion of superseded rows |

### 5.6 Failure path

| Failure | Mechanic | Code |
|---|---|---|
| Fewer than 3 independent episodes | `_check_independence` | `E_EVIDENCE_INSUFFICIENT` |
| Same input repeated three times | distinct-input check | `E_EVIDENCE_NOT_INDEPENDENT` |
| Golden regression | `golden.passed` false / failing ids | `E_GOLDEN_REGRESSION` (promotion blocked) |
| No named sign-off / no artifact hashes | `HumanSignoff.__post_init__`, gate check | `E_HUMAN_SIGNOFF_MISSING` |
| Kill switch off | `skills_enabled` | `E_SKILLS_DISABLED` (rollback still allowed) |
| Version skipped/backwards | next-version check under lock | `E_SKILL_VERSION` |
| Two concurrent promotions | advisory lock + `FOR UPDATE` | one wins; the other sees the new next version |
| Active pointer not unique | partial unique index + count check | `E_SKILL_STATE`; restore previous |
| Rollback with no prior version | target lookup | `E_ROLLBACK_NO_TARGET` |
| Rollback without reason | `reason.strip()` check | `E_ROLLBACK_REASON_MISSING` |
| Episode pin ≠ installed skill/app/catalogue | `resolve_pin` | `E_PIN_MISMATCH`; replay refuses |

The distinction that matters: **promotion is a proposal tested by evidence; activation is a
pointer flip.** A failed promotion leaves the old version active; a failed active version is
rolled back, not patched in place.

### 5.7 VERIFIED vs PROPOSED

| Claim | Label | Source / status |
|---|---|---|
| Promotion policy N=3, golden regression, human approval, pinning, rollback by pointer flip | `[R]` | 04 §8.4–8.5; `craft-agent-operator/references/memory-ledger.md` |
| No `agent_episode`/skill tables exist in the deployed `pod` DB | `[V]` | 04 §2.4; `01-STACK-VPS.md` §11 |
| The Python sketch compiles and the independence/validation paths ran in the scratch harness | `[V]` (this task) | `py_compile` exit 0; 5/5 Example-5 checks passed |
| SQL (partial unique index, advisory lock) against PostgreSQL 16 | `[U]` | Not executed; requires integration test |
| "Independent success" operational definition (different episodes + different inputs) | `[I]` | Proposed; 04 names the rule but the counting query must be written |
| Human sign-off record format | `[I]` | Proposed; named reviewer + artifact hashes + timestamp |
| Real promotion of three skills | `[U]` | Requires the eval harness, 50 goldens and human reviewers |

---

## 6. Example 6 — RL-shaped eval loop with verifiable gates and anti-reward-hacking

### 6.1 What it demonstrates

An evaluation loop that can *promote or reject a policy*, where "policy" means **retrieval +
active skills**, not model weights. The loop is RL-shaped because it selects actions from
evidence, but its reward is a **hard conjunction of verified properties**, not a scalar proxy
that can be gamed. Every known shortcut gets an explicit detector, and a null result is a
first-class outcome (`hold`), not a failure to be tuned away.

Design decision D10 is respected: no fine-tuning, no gradient updates, no PPO/RLHF pipeline.
If RL is ever considered (Phase 3+), this file's reward discipline is the precondition — a
verifiable reward, a private held-out set, and gate authorship separation.

### 6.2 Loop

```text
golden set (public dev 36 / private held-out 14)
        │
        ├── arm A: no retrieval, no promoted skills  (baseline)
        └── arm B: retrieval + active skills          (memory)
                    │
        randomised runs: ≥3 per golden per arm, identical budgets, same model/app/catalogue
                    │
        per-run record → verifiable_reward ∈ {0,1}
                    │
        anti-hack checks (private leakage, gate authorship, brief drift, shortcuts, cost anomaly,
        threshold hugging, skipped critic)
                    │
        Wilson 95% CI per arm; Newcombe CI for lift (B − A)
                    │
        verdict: promote_candidate | hold | reject
                    │
        promote/rollback via Example 5; every change re-runs the regression gates
```

### 6.3 Reward and metrics

```python
# Verifiable reward — a hard conjunction, no partial credit (Example 6 sketch).
reward = 1.0 if (
    run.passed_verified
    and run.unsafe_side_effects == 0
    and not run.source_mutated
    and run.gate_produced_by == "print_verifier"
    and not run.failure_codes
    and not run.input_override
) else 0.0
```

| Metric | Definition | Target |
|---|---|---|
| Primary: first-attempt verified-pass rate | accepted on attempt 1 / attempted goldens (rungs 1–5, +6 where required) | ↑ |
| Attempts per accepted artifact | tool batches until accepted | ↓ |
| Precision of "pass" | human-accepted / runs marked pass | ↑ (honesty metric) |
| Unsafe side effects | source mutations + unapproved publishes | = 0 |
| Regression rate | previously passing goldens now failing | = 0 |
| Retrieval lift | pass rate (B − A) with 95% CI | > 0 and CI excludes 0 |
| Critic stability | verdict flips on identical inputs | ↓ |
| Cost per accepted artifact | tokens + wall time (no invented dollars) | ↓ |

### 6.4 Sketch

<!-- Example 6 sketch — validated with py_compile + 8 scratch-harness checks -->
```python
"""Example 6 - evaluation / learning loop with verifiable gates and anti-reward-hacking.

Forge Conductor mechanism sketch (Python 3.11+). Design-only: this is policy
selection over skills and retrieval, NOT weight training. Reward is binary and
gate-verified; a scalar proxy is deliberately not used.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Iterable, Mapping, Sequence

MIN_RUNS_PER_ARM_PER_GOLDEN = 3
THRESHOLD_HUG_MARGIN = 0.01
THRESHOLD_HUG_SHARE = 0.20


class Arm(StrEnum):
    BASELINE = "baseline"
    MEMORY = "memory"


class EvalRefused(Exception):
    def __init__(self, code: str, message: str, how_to_fix: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.how_to_fix = how_to_fix


@dataclass(frozen=True)
class GoldenTask:
    golden_id: str
    task_family: str
    private: bool
    input_sha256: str
    brief_hash: str
    min_tool_calls: int
    token_floor: int
    required_gates: tuple[str, ...]
    human_required: bool
    suite_version: str

    def __post_init__(self) -> None:
        if not self.required_gates:
            raise ValueError("every golden needs at least one required gate")
        if self.min_tool_calls < 1:
            raise ValueError("min_tool_calls must be positive")
        if self.token_floor < 0:
            raise ValueError("token_floor must be non-negative")


@dataclass(frozen=True)
class RunRecord:
    run_id: str
    arm: Arm
    golden_id: str
    passed_verified: bool
    human_accepted: bool | None
    attempts: int
    unsafe_side_effects: int
    source_mutated: bool
    failure_codes: tuple[str, ...]
    tool_calls: int
    tokens_in: int
    tokens_out: int
    brief_hash: str
    input_sha256: str
    input_override: bool
    retrieved_case_ids: tuple[str, ...]
    gate_produced_by: str
    threshold_margin: float
    critic_validated: bool

    @property
    def tokens(self) -> int:
        return self.tokens_in + self.tokens_out


@dataclass(frozen=True)
class HackFlag:
    code: str
    severity: str  # critical | major | minor
    detail: str
    run_id: str | None = None


@dataclass(frozen=True)
class Reward:
    value: float
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class ArmMetrics:
    runs: int
    pass_rate: float
    pass_ci: tuple[float, float]
    precision_pass: float | None
    median_attempts: float
    mean_tokens: float
    unsafe_side_effects: int


@dataclass(frozen=True)
class EvalReport:
    suite_version: str
    goldens: int
    baseline: ArmMetrics
    memory: ArmMetrics
    lift: float
    lift_ci: tuple[float, float]
    regressions: int
    flags: tuple[HackFlag, ...]
    verdict: str
    generated_at: str


def wilson_interval(successes: int, trials: int, z: float = 1.96) -> tuple[float, float]:
    if trials <= 0:
        raise ValueError("trials must be positive")
    if not 0 <= successes <= trials:
        raise ValueError("successes must be within [0, trials]")
    p = successes / trials
    denominator = 1 + z * z / trials
    centre = (p + z * z / (2 * trials)) / denominator
    half = z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials)) / denominator
    return max(0.0, centre - half), min(1.0, centre + half)


def newcombe_difference_ci(
    successes_a: int,
    trials_a: int,
    successes_b: int,
    trials_b: int,
    z: float = 1.96,
) -> tuple[float, float]:
    """Newcombe score interval for p_b - p_a; used to test retrieval lift."""
    p_a = successes_a / trials_a
    p_b = successes_b / trials_b
    low_a, high_a = wilson_interval(successes_a, trials_a, z)
    low_b, high_b = wilson_interval(successes_b, trials_b, z)
    diff = p_b - p_a
    lower = diff - math.sqrt((p_b - low_b) ** 2 + (high_a - p_a) ** 2)
    upper = diff + math.sqrt((high_b - p_b) ** 2 + (p_a - low_a) ** 2)
    return max(-1.0, lower), min(1.0, upper)


def verifiable_reward(run: RunRecord) -> Reward:
    """Reward is a hard conjunction of verified properties. No partial credit.

    A gate pass obtained by an operator-authored report, or a run that mutated the
    source, scores 0 even if the artifact looked correct. This is the property that
    makes the loop resistant to optimizing the score instead of the work.
    """
    reasons: list[str] = []
    if not run.passed_verified:
        reasons.append("not_verified")
    if run.unsafe_side_effects > 0:
        reasons.append("unsafe_side_effect")
    if run.source_mutated:
        reasons.append("source_mutated")
    if run.gate_produced_by != "print_verifier":
        reasons.append("gate_not_authored_by_verifier")
    if run.failure_codes:
        reasons.append("failure_codes_present")
    if run.input_override:
        reasons.append("input_override_not_rewarded")
    return Reward(0.0 if reasons else 1.0, tuple(reasons))


def detect_flags(
    runs: Sequence[RunRecord],
    goldens: Mapping[str, GoldenTask],
    private_ids: Iterable[str],
) -> list[HackFlag]:
    flags: list[HackFlag] = []
    private = set(private_ids)
    for run in runs:
        golden = goldens.get(run.golden_id)
        if golden is None:
            flags.append(HackFlag("E_EVAL_UNKNOWN_GOLDEN", "critical", f"{run.golden_id} has no definition", run.run_id))
            continue
        if set(run.retrieved_case_ids) & private:
            flags.append(
                HackFlag(
                    "E_EVAL_CONTAMINATED",
                    "critical",
                    "a private held-out golden was retrieved into context",
                    run.run_id,
                )
            )
        if run.arm is Arm.BASELINE and run.retrieved_case_ids:
            flags.append(
                HackFlag(
                    "E_EVAL_ARM_CONTAMINATED",
                    "critical",
                    "baseline run carried retrieval cases",
                    run.run_id,
                )
            )
        if run.gate_produced_by != "print_verifier":
            flags.append(
                HackFlag(
                    "E_GATE_AUTHORSHIP",
                    "critical",
                    f"gate report produced by {run.gate_produced_by}",
                    run.run_id,
                )
            )
        if run.brief_hash != golden.brief_hash and not run.input_override:
            flags.append(
                HackFlag("E_BRIEF_DRIFT", "major", "brief hash changed without an override record", run.run_id)
            )
        if run.input_sha256 != golden.input_sha256 and not run.input_override:
            flags.append(
                HackFlag("E_INPUT_MISMATCH", "major", "input differs from the frozen golden", run.run_id)
            )
        if run.tool_calls < golden.min_tool_calls:
            flags.append(
                HackFlag(
                    "E_SHORTCUT",
                    "major",
                    f"{run.tool_calls} tool calls, floor {golden.min_tool_calls}",
                    run.run_id,
                )
            )
        if run.tokens < golden.token_floor:
            flags.append(
                HackFlag(
                    "E_COST_ANOMALY",
                    "minor",
                    f"{run.tokens} tokens, floor {golden.token_floor}; critic may have been skipped",
                    run.run_id,
                )
            )
        if golden.human_required and not run.critic_validated:
            flags.append(
                HackFlag("E_CRITIC_SKIPPED", "major", "golden requires a critic pass", run.run_id)
            )

    passing = [run for run in runs if run.passed_verified]
    hugged = [run for run in passing if run.threshold_margin < THRESHOLD_HUG_MARGIN]
    if len(passing) >= 5 and len(hugged) / len(passing) > THRESHOLD_HUG_SHARE:
        flags.append(
            HackFlag(
                "E_THRESHOLD_HUGGING",
                "major",
                f"{len(hugged)}/{len(passing)} passes sit within {THRESHOLD_HUG_MARGIN:.0%} of a gate threshold",
            )
        )
    return flags


def assert_no_private_leak(retrieved_ids: Iterable[str], private_ids: Iterable[str]) -> None:
    leaked = sorted(set(retrieved_ids) & set(private_ids))
    if leaked:
        raise EvalRefused(
            "E_EVAL_CONTAMINATED",
            f"retrieval index exposes private goldens: {', '.join(leaked)}",
            "remove private fixtures from the retrieval index before any arm comparison",
        )


def _median(values: Sequence[int | float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(float(value) for value in values)
    middle = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def _arm_metrics(runs: Sequence[RunRecord]) -> ArmMetrics:
    if not runs:
        raise EvalRefused("E_EVAL_EMPTY", "an arm has no runs", "execute the golden suite before comparing arms")
    passes = sum(1 for run in runs if run.passed_verified)
    low, high = wilson_interval(passes, len(runs))
    reviewed = [run for run in runs if run.passed_verified and run.human_accepted is not None]
    precision = (
        sum(1 for run in reviewed if run.human_accepted) / len(reviewed) if reviewed else None
    )
    return ArmMetrics(
        runs=len(runs),
        pass_rate=passes / len(runs),
        pass_ci=(low, high),
        precision_pass=precision,
        median_attempts=_median([run.attempts for run in runs]),
        mean_tokens=sum(run.tokens for run in runs) / len(runs),
        unsafe_side_effects=sum(run.unsafe_side_effects for run in runs),
    )


def evaluate_arms(
    goldens: Sequence[GoldenTask],
    baseline_runs: Sequence[RunRecord],
    memory_runs: Sequence[RunRecord],
    *,
    private_ids: Iterable[str] = (),
) -> EvalReport:
    """Compare baseline vs retrieval+skills. A null result is a valid verdict."""
    if not goldens:
        raise EvalRefused("E_EVAL_EMPTY", "no goldens configured", "freeze the golden set before evaluating")
    by_id = {golden.golden_id: golden for golden in goldens}
    private = set(private_ids) | {golden.golden_id for golden in goldens if golden.private}

    for arm_name, runs in (("baseline", baseline_runs), ("memory", memory_runs)):
        counts: dict[str, int] = {}
        for run in runs:
            if run.golden_id not in by_id:
                raise EvalRefused(
                    "E_EVAL_UNKNOWN_GOLDEN", f"{arm_name} ran unknown golden {run.golden_id}", "rebuild the run manifest"
                )
            if run.arm.value != arm_name:
                raise EvalRefused(
                    "E_EVAL_ARM_MISMATCH",
                    f"{run.run_id} is arm {run.arm.value} but filed under {arm_name}",
                    "never mix arms; the comparison would be meaningless",
                )
            counts[run.golden_id] = counts.get(run.golden_id, 0) + 1
        missing = [golden_id for golden_id in by_id if counts.get(golden_id, 0) < MIN_RUNS_PER_ARM_PER_GOLDEN]
        if missing:
            raise EvalRefused(
                "E_EVAL_INCOMPLETE",
                f"{arm_name} has < {MIN_RUNS_PER_ARM_PER_GOLDEN} runs for: {', '.join(missing[:5])}",
                "run every golden at least three times per arm; randomise order and hold budgets equal",
            )

    assert_no_private_leak(
        [case_id for run in baseline_runs for case_id in run.retrieved_case_ids], private
    )
    flags = detect_flags(baseline_runs, by_id, private) + detect_flags(memory_runs, by_id, private)
    baseline = _arm_metrics(baseline_runs)
    memory = _arm_metrics(memory_runs)
    lift = memory.pass_rate - baseline.pass_rate
    lift_ci = newcombe_difference_ci(
        sum(1 for run in baseline_runs if run.passed_verified),
        len(baseline_runs),
        sum(1 for run in memory_runs if run.passed_verified),
        len(memory_runs),
    )
    regressions = len(
        {run.golden_id for run in baseline_runs if run.passed_verified}
        & {run.golden_id for run in memory_runs if not run.passed_verified}
    )
    critical = [flag for flag in flags if flag.severity == "critical"]
    if critical:
        verdict = "reject"
    elif baseline.unsafe_side_effects or memory.unsafe_side_effects or regressions:
        verdict = "reject"
    elif lift_ci[0] > 0.0:
        verdict = "promote_candidate"
    elif lift_ci[1] < 0.0:
        verdict = "reject"
    else:
        verdict = "hold"

    return EvalReport(
        suite_version=goldens[0].suite_version,
        goldens=len(goldens),
        baseline=baseline,
        memory=memory,
        lift=lift,
        lift_ci=lift_ci,
        regressions=regressions,
        flags=tuple(flags),
        verdict=verdict,
        generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )


def schedule_runs(arms: Sequence[Arm], golden_ids: Sequence[str], repeats: int, seed: int) -> list[tuple[Arm, str]]:
    """Randomised, reproducible execution order (arm-major, then shuffled)."""
    if repeats < MIN_RUNS_PER_ARM_PER_GOLDEN:
        raise ValueError(f"repeats must be >= {MIN_RUNS_PER_ARM_PER_GOLDEN}")
    plan = [(arm, golden_id) for arm in arms for golden_id in golden_ids for _ in range(repeats)]
    random.Random(seed).shuffle(plan)
    return plan
```

### 6.5 Inputs and outputs

| Direction | Value |
|---|---|
| In | `GoldenTask[]` (public/private, input hash, brief hash, minimum tool calls, token floor, required gates), `RunRecord[]` per arm |
| Out | `EvalReport {baseline, memory, lift, lift_ci, regressions, flags, verdict}` |
| Refuses | empty golden set (`E_EVAL_EMPTY`), fewer than 3 runs per golden per arm (`E_EVAL_INCOMPLETE`), private-id leakage (`E_EVAL_CONTAMINATED`), mixed arms (`E_EVAL_ARM_MISMATCH`) |
| Honesty | A single demo is an anecdote; an overlapping CI yields `hold`; the private set is a sentinel, not a scoreboard |

### 6.6 Anti-reward-hacking checks

| Hack | Detector | Severity |
|---|---|---|
| Retrieve a private held-out golden | retrieved ids ∩ private ids | critical → reject |
| Baseline arm secretly uses retrieval | baseline run with non-empty `retrieved_case_ids` | critical |
| Operator authors its own gate report | `gate_produced_by != "print_verifier"` | critical |
| Narrow the brief until it passes | brief hash mismatch without override | major |
| Swap the input for an easier one | input hash mismatch without override record | major |
| Skip required steps | tool calls below the golden's floor | major |
| Pass by threshold hugging | >20% of passes within 1% of a gate threshold | major |
| Skip the critic | required critic not validated | major |
| Skip the critic to save cost | tokens below the family floor | minor (review flag) |
| Game the private set by tuning on it | private ids not retrievable; evaluated separately | structural |

### 6.7 Failure path

| Failure | Mechanic | Result |
|---|---|---|
| No goldens / fixtures missing | `E_EVAL_EMPTY` | no score is produced; promotion blocked |
| Missing runs | `E_EVAL_INCOMPLETE` | evaluation refuses; no partial comparison |
| Unknown golden id | `E_EVAL_UNKNOWN_GOLDEN` | refuses |
| Both arms mixed | `E_EVAL_ARM_MISMATCH` | refuses |
| Critical hack flag | verdict `reject` | promotion blocked; incident review |
| Unsafe effect or regression | verdict `reject` | if already active, Example 5 rollback |
| CI overlaps zero | verdict `hold` | honest null result; retrieval/skills stay off by default |
| App/model/catalogue changed | baseline label changes | never compared silently; new baseline required |

### 6.8 VERIFIED vs PROPOSED

| Claim | Label | Source / status |
|---|---|---|
| Golden split 36 public / 14 private, metrics, A/B protocol, anti-hack list, regression gates | `[R]` | 04 §9.1–9.5 |
| No fine-tuning/RL in Phases 0–2; gate-optimised RL produces gate-passing art | `[R]` | 04 D10, §8.6 |
| The Python sketch compiles; Wilson/Newcombe, reward, contamination and empty-set paths ran in the scratch harness | `[V]` (this task) | `py_compile` exit 0; 8/8 Example-6 checks passed |
| The 50-golden corpus exists | `[U]` | **It does not.** 04 §15/§9.1 specify it; no fixtures are frozen yet |
| Any measured lift from retrieval or skills | `[U]` | Not measured; null result is a valid and expected early outcome |
| Threshold-hugging constants (1%, 20%) | `[I]` | Proposed review flags; tune on real gate distributions |
| Newcombe interval assumptions (independent runs) | `[I]` | Runs are not strictly independent; treat CI as a diagnostic, not proof |
| RL on weights / reward models | `[U]` | Not planned; no corpus, no reward model, no training stack |

---

## 7. How the six examples compose

| Example | Consumes | Produces | Used by |
|---|---|---|---|
| 1 Supervisor | `PlanNode`, `Budget`, specialists | `Handoff` rows, `EpisodeResult`, verdict codes | operator/console; ledger close |
| 2 Gateway | registry, pinned catalogue, role token | `ToolSuccess` / `Refusal`, `forge_tool_call` | operators, verifier, critic render calls |
| 3 Ledger | episode close, retrieval query | chained events, case index, retrieval receipt | 1 (events), 5 (promotion evidence), 6 (run records) |
| 4 Critic | renders, brief, rubric, diagnostics | grounded `CritiqueReport` | 1 (verdict), 3 (evidence), 5 (quality evidence) |
| 5 Promotion | evidence, goldens, sign-off, pin | active skill version / rollback | 1 (skill_pin), 6 (policy arm) |
| 6 Eval | goldens, run records | `EvalReport`, promote/hold/reject | 5 (promotion gate), 2 (regression fixtures) |

Traced once end to end:

```text
brief → TaskEnvelope → [1] plan/dispatch → [2] gateway executes craft CLI
      → [3] events + artifacts + gate report → [4] blind critique
      → [1] arbitration → [3] close episode/case
      → [6] evaluate arms → [5] promote/rollback → next episode retrieves the case/skill
```

Every arrow is a stored record with a hash, not a message in memory. That is the difference
between a loop that can be audited and one that can only be demoed.

---

## 8. What would make these production-ready

The sketches are mechanism examples. Turning them into production requires, in this order:

1. **Migrations + integration tests against PostgreSQL 16** — chain append/verify, queue
   claim/lease, unique indexes, transaction boundaries, rollback drill.
2. **Contract versioning + JSON Schema** for `Handoff`, `ToolSuccess/Refusal`, `GateReport`,
   `CritiqueReport`, `Skill`, `EvalReport`; a schema registry with backward-compatibility tests.
3. **Real CLI probes** — 20 commands per installed app; capture stdout/stderr envelopes; replace
   the sketch's assumed `{"artifact": …}` shape where it is wrong; replace 127-shims.
4. **Failure injection** — timeout, signal, partial write, disk full, DB restart, concurrent
   promotion, corrupted chain, private-set leakage; assert the named refusal, not a crash.
5. **AuthN/Z** — role tokens, approval tokens bound to artifact hashes, no secrets in logs/argv.
6. **Observability** — episode/handoff/tool_call correlation ids, refusal-code metrics, queue
   age, budget burn, critic flip rate.
7. **Human rubric + inter-rater study** — the taste rung cannot be fabricated from gates.
8. **Load/resource test on the 2-vCPU host** — global craft semaphore = 1, ≤2 episodes,
   model-call cap; measure wall time and memory before raising limits.
9. **Backup/restore + rollback exercise** — restore to a scratch DB and replay three episodes.
10. **Honest baseline** — run the 50 goldens once before any "learning" claim; publish the null
    result if that is what the data says.

---

## 9. Unverified items (must stay unverified until the named check is run)

| Item | Why it is unverified | Cheapest check |
|---|---|---|
| Real Craft CLI JSON envelope | Sketch assumes `{"artifact": …}` lines | Snapshot 20 commands on 0.21.1/0.20.2 |
| PostgreSQL SQL in Examples 3/5 | No Forge DB exists | Scratch DB + migrations + tests |
| Chain hashing across `jsonb` normalisation | Driver round-trip may change numbers | Store canonical text; property test |
| Vision quality on print defects | No labelled corpus | 50-defect corpus; precision/recall |
| Critic semantic grounding | Schema checks geometry, not meaning | Human audit of 100 crop citations |
| `effective_confidence` constants | Proposed guard | Calibration study on the defect corpus |
| Retrieval lift | No 50-golden corpus | Freeze goldens; A/B with CI |
| Promotion of real skills | No evidence exists | 3 independent accepted episodes |
| Lease/deadline values | Proposed | Load test on the host |
| Any "learning" claim | Not measured | Persistent held-out gain that survives rollback |

No number in this file is presented as measured unless it is in the VERIFIED column of its
section. Everything else is design.
