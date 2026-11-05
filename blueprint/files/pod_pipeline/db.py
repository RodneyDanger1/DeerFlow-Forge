"""All SQL lives here. Parameterised queries only; no string-built SQL."""
from __future__ import annotations

import json
import os
import uuid
from typing import Any, Sequence

import asyncpg

from .config import ConfigError, Settings

Pool = asyncpg.Pool


async def create_pool(settings: Settings, *, min_size: int = 1, max_size: int = 6) -> Pool:
    return await asyncpg.create_pool(settings.database_url, min_size=min_size, max_size=max_size, command_timeout=60)


def _rec(row: asyncpg.Record | None) -> dict[str, Any] | None:
    return dict(row) if row is not None else None


# ------------------------------------------------------------------------ runs
RUN_SELECT = """
SELECT j.id AS job_id, j.run_id, j.account_id, j.asset_id, j.product_type, j.status AS job_status,
       j.error_digest, j.exit_code,
       a.source_path, a.original_filename, a.sha256, a.trace_state,
       acc.auto_publish, acc.fourthwall_api_user
  FROM processing_jobs j
  JOIN ingested_assets a   ON a.id = j.asset_id
  JOIN users_saas_accounts acc ON acc.id = j.account_id
 WHERE j.module = 'orchestrator'
"""


async def enqueue_run(pool: Pool, *, account_id: int, asset_id: int, product_type: str) -> tuple[uuid.UUID, bool]:
    """Insert the run row. Returns (run_id, created). If a live run exists for the same
    (asset, product_type) the partial unique index rejects the insert and the existing run_id is returned.

    The conflict lookup can legitimately find nothing: the live run may finish between the
    rejected INSERT and the SELECT. Returning that as (None, False) made callers report
    run_id "None", so retry the insert once and otherwise refuse by name.
    """
    run_id = uuid.uuid4()
    for _attempt in range(2):
        try:
            async with pool.acquire() as con:
                async with con.transaction():
                    await con.execute(
                        """INSERT INTO processing_jobs (run_id, account_id, asset_id, product_type, module, step_name, step_index, status)
                           VALUES ($1,$2,$3,$4,'orchestrator','pipeline_run',0,'queued')""",
                        run_id, account_id, asset_id, product_type)
                    await con.execute(
                        "UPDATE ingested_assets SET status='queued' WHERE id=$1 AND status IN ('pending','failed','processed')",
                        asset_id)
                return run_id, True
        except asyncpg.UniqueViolationError:
            async with pool.acquire() as con:
                existing = await con.fetchval(
                    """SELECT run_id FROM processing_jobs WHERE asset_id=$1 AND product_type=$2
                          AND module='orchestrator' AND status IN ('queued','running') LIMIT 1""", asset_id, product_type)
            if existing is not None:
                return existing, False
            # The conflicting run became terminal between the INSERT and the SELECT.
            # Re-attempt once against the now-free slot; a second conflict means a
            # different live run won the race again.
            run_id = uuid.uuid4()
            continue
    raise RuntimeError(
        f"asset {asset_id}/{product_type}: a run is finishing concurrently; retry the request once it settles")


async def claim_run(pool: Pool, run_id: uuid.UUID | None, pid: int) -> dict[str, Any] | None:
    """Atomically move one queued run to running. run_id=None -> oldest queued run. SKIP LOCKED keeps
    concurrent workers (MCP-spawned child + timer-driven drain) from taking the same run."""
    async with pool.acquire() as con:
        row = await con.fetchrow(
            """UPDATE processing_jobs SET status='running', pid=$2, started_at=now()
                WHERE id = (SELECT id FROM processing_jobs
                             WHERE module='orchestrator' AND status='queued'
                               AND ($1::uuid IS NULL OR run_id=$1)
                             ORDER BY id FOR UPDATE SKIP LOCKED LIMIT 1)
            RETURNING id, run_id""", run_id, pid)
        if row is None:
            return None
        return _rec(await con.fetchrow(RUN_SELECT + " AND j.id=$1", row["id"]))


async def get_run(pool: Pool, run_id: uuid.UUID) -> dict[str, Any] | None:
    async with pool.acquire() as con:
        return _rec(await con.fetchrow(RUN_SELECT + " AND j.run_id=$1", run_id))


async def finish_run(pool: Pool, run_id: uuid.UUID, *, ok: bool, digest: str | None) -> None:
    async with pool.acquire() as con:
        await con.execute(
            """UPDATE processing_jobs SET status=$2, finished_at=now(), error_digest=$3
                WHERE run_id=$1 AND module='orchestrator'""",
            run_id, "succeeded" if ok else "failed", (digest or None) and digest[:8000])


async def recover_stale_runs(pool: Pool) -> int:
    """Runs marked 'running' whose worker PID is gone (crash/reboot) go back to 'queued'."""
    n = 0
    async with pool.acquire() as con:
        rows = await con.fetch("SELECT id, pid FROM processing_jobs WHERE module='orchestrator' AND status='running'")
        for r in rows:
            if r["pid"] and _alive(r["pid"]):
                continue
            await con.execute("UPDATE processing_jobs SET status='queued', pid=NULL, started_at=NULL WHERE id=$1", r["id"])
            n += 1
    return n


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


# ----------------------------------------------------------------------- steps
async def start_step(pool: Pool, run: dict[str, Any], *, module: str, step_name: str, step_index: int,
                     attempt: int, tier: int, argv: Sequence[str]) -> int:
    async with pool.acquire() as con:
        return await con.fetchval(
            """INSERT INTO processing_jobs (run_id, account_id, asset_id, product_type, module, step_name,
                                            step_index, attempt, fallback_tier, status, argv, started_at)
               VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,'running',$10,now()) RETURNING id""",
            run["run_id"], run["account_id"], run["asset_id"], run["product_type"], module, step_name,
            step_index, attempt, tier, list(argv))


async def finish_step(pool: Pool, job_id: int, *, status: str, exit_code: int | None, pid: int | None,
                      digest: str | None, log_path: str | None, output_path: str | None) -> None:
    async with pool.acquire() as con:
        await con.execute(
            """UPDATE processing_jobs SET status=$2, exit_code=$3, pid=$4, error_digest=$5, log_path=$6,
                      output_path=$7, finished_at=now() WHERE id=$1""",
            job_id, status, exit_code, pid, (digest or None) and digest[:8000], log_path, output_path)


# ---------------------------------------------------------------------- assets
async def set_asset(pool: Pool, asset_id: int, *, status: str | None = None, trace_state: str | None = None,
                    trace_bounds: dict[str, Any] | None = None) -> None:
    async with pool.acquire() as con:
        await con.execute(
            """UPDATE ingested_assets SET status=COALESCE($2,status), trace_state=COALESCE($3,trace_state),
                      trace_bounds=COALESCE($4::jsonb,trace_bounds) WHERE id=$1""",
            asset_id, status, trace_state, json.dumps(trace_bounds) if trace_bounds is not None else None)


async def register_asset(pool: Pool, *, account_id: int, source_path: str, filename: str, sha256: str,
                         byte_size: int, mime: str | None, width: int | None, height: int | None,
                         dpi: int | None, color_space: str, has_alpha: bool | None) -> int | None:
    async with pool.acquire() as con:
        return await con.fetchval(
            """INSERT INTO ingested_assets (account_id, source_kind, source_path, original_filename, sha256, byte_size,
                                            mime_type, width_px, height_px, source_dpi, color_space, has_alpha)
               VALUES ($1,'directory',$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)
               ON CONFLICT DO NOTHING RETURNING id""",
            account_id, source_path, filename, sha256, byte_size, mime, width, height, dpi, color_space, has_alpha)


async def pending_assets(pool: Pool, *, stuck_after_s: int, account_id: int | None = None,
                         limit: int = 200) -> tuple[list[dict[str, Any]], bool]:
    """Pending/stuck assets plus an honest truncation flag.

    Fetches limit+1 rows so a full page can say "there are more" instead of an
    agent silently believing a 200-row cap is the whole queue.
    """
    async with pool.acquire() as con:
        rows = await con.fetch(
            """SELECT id, account_id, original_filename, source_path, byte_size, mime_type, width_px, height_px,
                      color_space, has_alpha, status, trace_state, created_at, updated_at,
                      (status IN ('queued','processing') AND updated_at < now() - make_interval(secs => $1)) AS stuck
                 FROM ingested_assets
                WHERE ($2::bigint IS NULL OR account_id=$2)
                  AND (status IN ('pending','failed')
                       OR (status IN ('queued','processing') AND updated_at < now() - make_interval(secs => $1)))
                ORDER BY created_at LIMIT $3""", float(stuck_after_s), account_id, limit + 1)
        truncated = len(rows) > limit
        return [dict(r) for r in rows[:limit]], truncated


async def get_asset(pool: Pool, asset_id: int) -> dict[str, Any] | None:
    async with pool.acquire() as con:
        return _rec(await con.fetchrow("SELECT * FROM ingested_assets WHERE id=$1", asset_id))


# -------------------------------------------------------------------- products
async def upsert_product(pool: Pool, run: dict[str, Any], **fields: Any) -> dict[str, Any]:
    """Create the (account, asset, product_type) row if needed, then apply `fields`."""
    allowed = {"fw_template_id", "media_id", "media_file_url", "fw_product_id", "fw_slug", "variants", "skus",
               "publish_state", "last_error", "published_at"}
    bad = set(fields) - allowed
    if bad:
        raise ValueError(f"unknown product columns: {sorted(bad)}")
    async with pool.acquire() as con:
        async with con.transaction():
            await con.execute(
                """INSERT INTO fourthwall_products (account_id, asset_id, run_id, product_type)
                   VALUES ($1,$2,$3,$4) ON CONFLICT (account_id, asset_id, product_type) DO UPDATE SET run_id=EXCLUDED.run_id""",
                run["account_id"], run["asset_id"], run["run_id"], run["product_type"])
            sets, args = [], [run["account_id"], run["asset_id"], run["product_type"]]
            for col, val in fields.items():
                args.append(json.dumps(val) if col == "variants" else val)
                sets.append(f"{col}=${len(args)}" + ("::jsonb" if col == "variants" else ""))
            if sets:
                await con.execute(
                    f"UPDATE fourthwall_products SET {', '.join(sets)} WHERE account_id=$1 AND asset_id=$2 AND product_type=$3", *args)
            return dict(await con.fetchrow(
                "SELECT * FROM fourthwall_products WHERE account_id=$1 AND asset_id=$2 AND product_type=$3",
                run["account_id"], run["asset_id"], run["product_type"]))


async def get_product_row(pool: Pool, ref: str) -> dict[str, Any] | None:
    """`ref` is either our numeric row id or a Fourthwall product id."""
    async with pool.acquire() as con:
        if ref.isdigit():
            return _rec(await con.fetchrow("SELECT * FROM fourthwall_products WHERE id=$1", int(ref)))
        return _rec(await con.fetchrow("SELECT * FROM fourthwall_products WHERE fw_product_id=$1 LIMIT 1", ref))


# --------------------------------------------------------------- credentials / logs
async def get_fw_credentials(pool: Pool, settings: Settings, account_id: int) -> tuple[str, str] | None:
    """Per-tenant credentials (secret decrypted in SQL with POD_CREDENTIAL_KEY), else env single-tenant fallback."""
    async with pool.acquire() as con:
        if settings.credential_key:
            row = await con.fetchrow(
                """SELECT fourthwall_api_user AS u,
                          CASE WHEN fourthwall_api_secret_enc IS NULL THEN NULL
                               ELSE pgp_sym_decrypt(fourthwall_api_secret_enc, $2) END AS s
                     FROM users_saas_accounts WHERE id=$1""", account_id, settings.credential_key)
        else:
            row = None
    if row and row["u"] and row["s"]:
        return row["u"], row["s"]
    if settings.fw_api_user and settings.fw_api_secret:
        return settings.fw_api_user, settings.fw_api_secret
    return None


async def log_sync(pool: Pool, *, account_id: int | None, direction: str, channel: str, event_type: str,
                   run_id: uuid.UUID | None = None, http_method: str | None = None, url: str | None = None,
                   status_code: int | None = None, success: bool | None = None, duration_ms: int | None = None,
                   payload: Any = None, fw_product_row_id: int | None = None, external_event_id: str | None = None) -> None:
    if success is None and status_code is not None:
        success = 200 <= status_code < 300
    async with pool.acquire() as con:
        await con.execute(
            """INSERT INTO agent_sync_logs (account_id, direction, channel, event_type, external_event_id, http_method, url,
                                            status_code, success, duration_ms, payload, run_id, fw_product_row_id)
               VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11::jsonb,$12,$13) ON CONFLICT DO NOTHING""",
            account_id, direction, channel, event_type, external_event_id, http_method, url, status_code, success,
            duration_ms, json.dumps(payload, default=str) if payload is not None else None, run_id, fw_product_row_id)


def require(value: Any, what: str) -> Any:
    if value is None:
        raise ConfigError(what)
    return value
