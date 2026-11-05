# Example 5 — Skill promotion and rollback: candidate → active, evidence, version pin

> Extracted from `wave2/07-EXAMPLES.md` (task-7). Original code/design, validated as recorded there; not production code.

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
