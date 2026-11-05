"""Forge repository seam over the proven `forge` schema.

This is local source, not a deployed service. It uses asyncpg and the SQL
functions in sql/schema_forge.sql. No Craft call, no publish, no production DB.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import asyncpg


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
        for key in ("payload", "result", "budget", "params"):
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
