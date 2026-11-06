"""Forge repository seam over the proven `forge` schema.

This is local source, not a deployed service. It uses asyncpg and the SQL
functions in sql/schema_forge.sql. No Craft call, no publish, no production DB.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import asyncpg

from forge_gateway import PolicyError, ToolCall, ToolResult


class RepoShapeError(RuntimeError):
    """A row came back that cannot be mapped to the service contract."""

    code = "E_REPO_SHAPE"


class ForgeRepo:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self.pool = pool

    @staticmethod
    def _row(row) -> dict[str, Any] | None:
        if row is None:
            return None
        data = dict(row)
        if data and all(value is None for value in data.values()):
            return None  # PL/pgSQL composite NULL reaches asyncpg as all-NULL row
        if data.get("id") is None:
            raise RepoShapeError(f"row is missing id; keys={sorted(data)}")
        for key in ("payload", "result", "budget", "params", "technical", "human"):
            if isinstance(data.get(key), str):
                try:
                    data[key] = json.loads(data[key])
                except json.JSONDecodeError as exc:
                    raise RepoShapeError(
                        f"column {key} is not valid JSON: {exc.msg}") from exc
        return data

    @classmethod
    async def connect(cls, dsn: str, *, min_size: int = 1, max_size: int = 4) -> "ForgeRepo":
        return cls(await asyncpg.create_pool(dsn, min_size=min_size, max_size=max_size))

    async def close(self) -> None:
        await self.pool.close()

    async def health(self) -> dict[str, Any]:
        async with self.pool.acquire() as conn:
            await conn.execute("SET search_path = forge, public")
            value = await conn.fetchval("SELECT 1")
            tables = await conn.fetchval(
                "SELECT count(*) FROM information_schema.tables WHERE table_schema='forge'")
            return {"ok": value == 1, "tables": int(tables)}

    async def create_episode(self, *, idempotency_key: str, account_id: int, brief: str,
                             task_family: str, budget: dict[str, Any] | None = None) -> dict[str, Any]:
        async with self.pool.acquire() as conn:
            await conn.execute("SET search_path = forge, public")
            row = await conn.fetchrow(
                """INSERT INTO forge_episode (idempotency_key, account_id, brief, task_family, budget)
                   VALUES ($1, $2, $3, $4, $5::jsonb) RETURNING *""",
                idempotency_key, account_id, brief, task_family, json.dumps(budget or {}),
            )
            return self._row(row)

    async def get_episode(self, episode_id: str) -> dict[str, Any] | None:
        async with self.pool.acquire() as conn:
            await conn.execute("SET search_path = forge, public")
            row = await conn.fetchrow("SELECT * FROM forge_episode WHERE id=$1", episode_id)
            return self._row(row)

    async def get_episode_by_idempotency_key(self, key: str) -> dict[str, Any] | None:
        """Return the episode created for an idempotency key, if any (D2 replay path)."""
        async with self.pool.acquire() as conn:
            await conn.execute("SET search_path = forge, public")
            row = await conn.fetchrow(
                "SELECT * FROM forge_episode WHERE idempotency_key=$1", key)
            return self._row(row)

    async def record_eval(self, *, episode_id: str, arm: str,
                          technical: dict[str, Any], verdict: str,
                          human: dict[str, Any] | None = None,
                          reviewer: str | None = None) -> dict[str, Any]:
        """Persist one immutable eval row per (episode, arm)."""
        if not isinstance(episode_id, str) or not episode_id.strip():
            raise ValueError("E_EVAL_INVALID: episode_id is required")
        if arm not in ("baseline", "memory"):
            raise ValueError("E_EVAL_INVALID: arm must be baseline or memory")
        if not isinstance(technical, dict):
            raise ValueError("E_EVAL_INVALID: technical must be an object")
        if verdict not in ("pass", "fail", "needs_human", "unverified"):
            raise ValueError("E_EVAL_INVALID: verdict is not a known value")
        if human is not None and not isinstance(human, dict):
            raise ValueError("E_EVAL_INVALID: human must be an object or null")
        if reviewer is not None and (not isinstance(reviewer, str)
                                     or not reviewer.strip() or len(reviewer) > 200):
            raise ValueError("E_EVAL_INVALID: reviewer must be 1..200 chars or null")
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("SET search_path = forge, public")
                row = await conn.fetchrow(
                    """INSERT INTO forge_eval
                           (episode_id, arm, technical, human, verdict, reviewer)
                       VALUES ($1, $2, $3::jsonb, $4::jsonb, $5, $6)
                       RETURNING *""",
                    episode_id, arm, json.dumps(technical),
                    None if human is None else json.dumps(human), verdict, reviewer)
                return self._row(row)
        except asyncpg.UniqueViolationError as exc:
            raise PolicyError("E_EVAL_EXISTS", f"{episode_id}/{arm}") from exc
        except asyncpg.ForeignKeyViolationError as exc:
            raise PolicyError("E_EPISODE_NOT_FOUND", episode_id) from exc

    async def transition(self, episode_id: str, target: str, *, verdict: str | None = None,
                         reasons: list[str] | None = None) -> dict[str, Any]:
        async with self.pool.acquire() as conn:
            await conn.execute("SET search_path = forge, public")
            row = await conn.fetchrow(
                "SELECT * FROM forge_transition_episode($1, $2, $3, $4)", episode_id, target,
                verdict, reasons or [],
            )
            return self._row(row)

    async def append_event(self, episode_id: str, kind: str, payload: dict[str, Any]) -> dict[str, Any]:
        async with self.pool.acquire() as conn:
            await conn.execute("SET search_path = forge, public")
            row = await conn.fetchrow("SELECT * FROM forge_append_event($1, $2, $3::jsonb)",
                                      episode_id, kind, json.dumps(payload))
            return self._row(row)

    async def create_job(self, *, kind: str, payload: dict[str, Any] | None = None,
                         dedupe_key: str | None = None, run_after: datetime | None = None,
                         max_attempts: int = 3) -> int:
        if not isinstance(max_attempts, int) or not 1 <= max_attempts <= 10:
            raise ValueError("max_attempts must be an integer from 1 to 10")
        async with self.pool.acquire() as conn:
            await conn.execute("SET search_path = forge, public")
            return int(await conn.fetchval(
                """INSERT INTO forge_job (kind, payload, dedupe_key, run_after, max_attempts)
                   VALUES ($1, $2::jsonb, $3, $4, $5) RETURNING id""",
                kind, json.dumps(payload or {}), dedupe_key,
                run_after or datetime.now(timezone.utc), max_attempts,
            ))

    async def claim_job(self, worker: str, *, lease_s: int = 300) -> dict[str, Any] | None:
        async with self.pool.acquire() as conn:
            await conn.execute("SET search_path = forge, public")
            row = await conn.fetchrow("SELECT * FROM forge_claim_job($1, $2)", worker, lease_s)
            return self._row(row)

    async def finish_job(self, job_id: int, *, ok: bool, error: str | None = None) -> dict[str, Any]:
        async with self.pool.acquire() as conn:
            await conn.execute("SET search_path = forge, public")
            row = await conn.fetchrow("SELECT * FROM forge_finish_job($1, $2, $3)", job_id, ok, error)
            return self._row(row)

    async def reap_expired_jobs(self) -> int:
        """Recover expired leases; abandon a job once its attempt cap is reached."""
        async with self.pool.acquire() as conn:
            await conn.execute("SET search_path = forge, public")
            rows = await conn.fetch(
                """UPDATE forge_job
                      SET state = CASE WHEN attempts >= max_attempts THEN 'abandoned' ELSE 'queued' END,
                          lease_until = NULL,
                          last_error = CASE WHEN attempts >= max_attempts
                                            THEN 'E_LEASE_EXPIRED_MAX_ATTEMPTS'
                                            ELSE 'E_LEASE_EXPIRED' END
                    WHERE state IN ('claimed','running') AND lease_until IS NOT NULL
                      AND lease_until < now()
                    RETURNING id, state""")
            return len(rows)


class ForgeGatewayRepo:
    """Asyncpg adapter for the gateway's ``Repo`` protocol.

    The in-flight insert happens before the executor runs, so a crash leaves a
    row that refuses later duplicates instead of re-executing the tool. A
    terminal row is replayed with its persisted result.
    """

    def __init__(self, pool: asyncpg.Pool) -> None:
        self.pool = pool

    @staticmethod
    def _map(row) -> ToolResult | None:
        data = ForgeRepo._row(row)
        if data is None:
            return None
        payload = data.get("result") or {}
        if not isinstance(payload, dict):
            raise RepoShapeError("forge_tool_call.result is not an object")
        return ToolResult(
            idempotency_key=str(data["idempotency_key"]),
            state=data["state"],
            replayed=bool(data.get("replayed", False)),
            exit_code=data.get("exit_code"),
            refusal_code=data.get("refusal_code"),
            artifacts=tuple(payload.get("artifacts") or ()),
            message=str(payload.get("message") or ""),
            episode_id=str(data["episode_id"]),
            tool_id=str(data["tool_id"]),
            cmd_id=data.get("cmd_id"),
            params=data.get("params") or {},
            argv=tuple(data.get("argv") or ()),
            duration_ms=data.get("duration_ms"),
        )

    async def find(self, key: str) -> ToolResult | None:
        async with self.pool.acquire() as conn:
            await conn.execute("SET search_path = forge, public")
            row = await conn.fetchrow(
                "SELECT * FROM forge_tool_call WHERE idempotency_key=$1", key)
            return self._map(row)

    async def begin(self, key: str, call: ToolCall) -> ToolResult | None:
        async with self.pool.acquire() as conn:
            await conn.execute("SET search_path = forge, public")
            row = await conn.fetchrow(
                """INSERT INTO forge_tool_call
                       (episode_id, tool_id, cmd_id, params, idempotency_key, state)
                   VALUES ($1, $2, $3, $4::jsonb, $5, 'in_flight')
                   ON CONFLICT (idempotency_key) DO NOTHING
                   RETURNING *""",
                call.episode_id, call.tool_id, call.cmd_id,
                json.dumps(call.params), key)
            if row is not None:
                return None
            existing = await conn.fetchrow(
                "SELECT * FROM forge_tool_call WHERE idempotency_key=$1", key)
            if existing is None:
                raise RepoShapeError("idempotency conflict without a stored row")
            mapped = self._map(existing)
            if mapped is not None and mapped.state == "in_flight":
                raise PolicyError("E_IDEMPOTENCY_IN_FLIGHT", key, terminal=False)
            return mapped

    async def store(self, key: str, result: ToolResult) -> None:
        payload = {"artifacts": list(result.artifacts), "message": result.message}
        async with self.pool.acquire() as conn:
            await conn.execute("SET search_path = forge, public")
            tag = await conn.execute(
                """UPDATE forge_tool_call
                      SET state=$2, refusal_code=$3, exit_code=$4,
                          result=$5::jsonb, duration_ms=$6, argv=$7,
                          replayed=false, finished_at=now()
                    WHERE idempotency_key=$1""",
                key, result.state, result.refusal_code, result.exit_code,
                json.dumps(payload), result.duration_ms, list(result.argv))
            if tag != "UPDATE 1":
                raise RepoShapeError(f"tool-call finish updated {tag!r}, expected 'UPDATE 1'")

    async def abandon_stale_in_flight(self, *, older_than_s: int,
                                      limit: int = 100) -> list[str]:
        """Mark old in-flight rows failed so a crashed executor cannot block a key forever.

        This is deliberately operator-run. It does not re-execute anything; a later
        call for the key replays the recorded ``E_IDEMPOTENCY_STALE`` failure.
        """
        if (isinstance(older_than_s, bool) or not isinstance(older_than_s, int)
                or not 1 <= older_than_s <= 604800):
            raise ValueError("E_PARAM_REJECTED: older_than_s must be 1..604800")
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 1000:
            raise ValueError("E_PARAM_REJECTED: limit must be 1..1000")
        async with self.pool.acquire() as conn:
            await conn.execute("SET search_path = forge, public")
            rows = await conn.fetch(
                """UPDATE forge_tool_call
                      SET state='failed',
                          result=jsonb_build_object(
                              'message', 'E_IDEMPOTENCY_STALE',
                              'artifacts', '[]'::jsonb),
                          replayed=false,
                          finished_at=now()
                    WHERE idempotency_key IN (
                        SELECT idempotency_key FROM forge_tool_call
                         WHERE state='in_flight'
                           AND created_at < now() - ($1 * interval '1 second')
                         ORDER BY created_at
                         FOR UPDATE SKIP LOCKED
                         LIMIT $2)
                    RETURNING idempotency_key""",
                older_than_s, limit)
            return [str(row["idempotency_key"]) for row in rows]
