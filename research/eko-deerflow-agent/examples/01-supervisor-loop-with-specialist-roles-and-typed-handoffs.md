# Example 1 — Supervisor loop with specialist roles and typed handoffs

> Extracted from `wave2/07-EXAMPLES.md` (task-7). Original code/design, validated as recorded there; not production code.

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
