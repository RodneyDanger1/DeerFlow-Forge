# Example 3 — Episode ledger, hash chain, write path and retrieval

> Extracted from `wave2/07-EXAMPLES.md` (task-7). Original code/design, validated as recorded there; not production code.

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
