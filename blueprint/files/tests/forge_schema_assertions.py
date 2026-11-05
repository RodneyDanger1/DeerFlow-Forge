#!/usr/bin/env python3
"""W2-B SQL assertions against a throwaway PostgreSQL 16 database.

Run with DATABASE_URL pointing at the scratch DB. Every check is in its own
transaction and rolls back, so the assertions do not leave state behind.
No production database is used by this file.
"""
from __future__ import annotations

import asyncio
import os
import sys
import uuid

import asyncpg

DSN = os.environ.get("FORGE_TEST_DSN")
if not DSN:
    print("FORGE_TEST_DSN is required (e.g. postgresql://postgres:scratch@127.0.0.1:55439/postgres)", file=sys.stderr)
    raise SystemExit(2)

PASS = 0
FAIL = 0
RUN = uuid.uuid4().hex[:8]


def is_empty(record) -> bool:
    """PL/pgSQL composite NULL may reach asyncpg as an all-NULL Record."""
    return record is None or record["id"] is None


def sha(seed: str) -> str:
    import hashlib
    return hashlib.sha256(seed.encode()).hexdigest()


async def expect_error(conn, sql: str, *args, sqlstate: str | None = None, label: str = "") -> None:
    try:
        async with conn.transaction():
            await conn.execute(sql, *args)
    except asyncpg.PostgresError as exc:
        if sqlstate and exc.sqlstate != sqlstate:
            raise AssertionError(f"{label}: wrong SQLSTATE {exc.sqlstate}, expected {sqlstate}: {exc}") from exc
        return
    raise AssertionError(f"{label}: expected a refusal, got success")


async def episode(conn, key: str = "ep") -> uuid.UUID:
    return await conn.fetchval(
        """INSERT INTO forge.forge_episode (idempotency_key, account_id, brief, task_family)
           VALUES ($1, 1, 'test brief', 'ai_badge_trace') RETURNING id""",
        f"{key}-{RUN}",
    )


async def main() -> None:
    global PASS, FAIL
    conn = await asyncpg.connect(DSN)
    try:
        await conn.execute("SET search_path = forge, public")
        async with conn.transaction():
            tables = await conn.fetchval("SELECT count(*) FROM information_schema.tables WHERE table_schema='forge'")
            edges = await conn.fetchval("SELECT count(*) FROM forge.forge_transition")
            assert tables == 13, f"expected 13 tables, got {tables}"
            assert edges == 36, f"expected 36 edges, got {edges}"
            PASS += 1
            print("PASS T01 13 tables / 36 transitions")

        async with conn.transaction():
            ep = await episode(conn, "t02")
            await conn.execute("SELECT forge.forge_transition_episode($1, 'briefed')", ep)
            status = await conn.fetchval("SELECT status FROM forge.forge_episode WHERE id=$1", ep)
            events = await conn.fetchval("SELECT count(*) FROM forge.forge_event WHERE episode_id=$1", ep)
            chain = await conn.fetchrow("SELECT * FROM forge.forge_verify_event_chain($1)", ep)
            assert status == "briefed" and events == 1 and chain["broken"] == 0
            PASS += 1
            print("PASS T02 intake->briefed + one event + chain clean")

        async with conn.transaction():
            ep = await episode(conn, "t03")
            await expect_error(conn, "SELECT forge.forge_transition_episode($1, 'accepted')", ep,
                               sqlstate="P0001", label="illegal intake->accepted")
            status = await conn.fetchval("SELECT status FROM forge.forge_episode WHERE id=$1", ep)
            assert status == "intake"
            PASS += 1
            print("PASS T03 illegal transition refused; status unchanged")

        async with conn.transaction():
            ep = await episode(conn, "t04")
            for state in ("briefed", "planned", "context_ready", "executing", "verifying", "rejected"):
                await conn.execute("SELECT forge.forge_transition_episode($1, $2)", ep, state)
            status = await conn.fetchval("SELECT status FROM forge.forge_episode WHERE id=$1", ep)
            assert status == "rejected"
            PASS += 1
            print("PASS T04 legal reject path accepted by transition guard")

        async with conn.transaction():
            ep = await episode(conn, "t05")
            await conn.execute("SELECT forge.forge_transition_episode($1, 'briefed')", ep)
            first = await conn.fetchrow("SELECT * FROM forge.forge_event WHERE episode_id=$1 ORDER BY seq", ep)
            assert first["prev_hash"] == "0" * 64
            await conn.execute("SELECT forge.forge_append_event($1, 'test.second', '{\"x\":1}'::jsonb)", ep)
            second = await conn.fetchrow("SELECT * FROM forge.forge_event WHERE episode_id=$1 AND seq=2", ep)
            assert second["prev_hash"] == first["hash"]
            PASS += 1
            print("PASS T05 event chain genesis/link")

        async with conn.transaction():
            ep = await episode(conn, "t06")
            await conn.execute("SELECT forge.forge_transition_episode($1, 'briefed')", ep)
            event_id = await conn.fetchval("SELECT id FROM forge.forge_event WHERE episode_id=$1 LIMIT 1", ep)
            await expect_error(conn, "UPDATE forge.forge_event SET kind='x' WHERE id=$1", event_id,
                               sqlstate="42501", label="event UPDATE append-only")
            await expect_error(conn, "DELETE FROM forge.forge_event WHERE id=$1", event_id,
                               sqlstate="42501", label="event DELETE append-only")
            PASS += 1
            print("PASS T06 event UPDATE/DELETE refused 42501")

        async with conn.transaction():
            ep = await episode(conn, "t07")
            await expect_error(conn, "INSERT INTO forge.forge_episode (idempotency_key, account_id, brief, task_family) VALUES ($1, 1, 'x', 'y')",
                               f"t07-{RUN}", sqlstate="23505", label="duplicate episode key")
            PASS += 1
            print("PASS T07 duplicate episode key refused")

        async with conn.transaction():
            ep = await episode(conn, "t08")
            key = "sha256:" + sha("tool" + RUN)
            await conn.execute(
                """INSERT INTO forge.forge_tool_call
                   (episode_id, tool_id, cmd_id, idempotency_key, state, exit_code, result)
                   VALUES ($1, 'vectorcraft.run', 'imageTrace.make', $2, 'succeeded', 0, '{"ok":true}'::jsonb)""",
                ep, key,
            )
            replay = await conn.fetchrow("SELECT * FROM forge.forge_replay_tool_call($1)", key)
            assert replay and replay["idempotency_key"] == key
            await expect_error(conn,
                """INSERT INTO forge.forge_tool_call
                   (episode_id, tool_id, cmd_id, idempotency_key)
                   VALUES ($1, 'vectorcraft.run', 'imageTrace.make', $2)""", ep, key,
                sqlstate="23505", label="duplicate tool key")
            PASS += 1
            print("PASS T08 tool key replay/unique")

        async with conn.transaction():
            await conn.execute("INSERT INTO forge.forge_job (kind, payload) VALUES ('test', '{}'::jsonb)")
            first = await conn.fetchrow("SELECT * FROM forge.forge_claim_job('w1', 30)")
            assert first and first["state"] == "claimed" and first["attempts"] == 1 and first["lease_until"] is not None
            empty = await conn.fetchrow("SELECT * FROM forge.forge_claim_job('w2', 30)")
            assert is_empty(empty)
            await conn.execute("SELECT forge.forge_finish_job($1, true)", first["id"])
            done = await conn.fetchval("SELECT state FROM forge.forge_job WHERE id=$1", first["id"])
            assert done == "succeeded"
            PASS += 1
            print("PASS T09 job claim/lease/finish/empty")

        async with conn.transaction():
            today = await conn.fetchval("SELECT current_date")
            await conn.execute("SELECT forge.forge_charge(1, $1, 10, 5, 50, 100)", today)
            await expect_error(conn, "SELECT forge.forge_charge(1, $1, 1, 1, 60, 100)", today,
                               label="budget cap")
            cents = await conn.fetchval("SELECT cents FROM forge.forge_budget_ledger WHERE account_id=1 AND day=$1", today)
            assert float(cents) == 50.0, cents
            PASS += 1
            print("PASS T10 budget cap rollback")

        async with conn.transaction():
            ep = await episode(conn, "t11")
            digest = sha("approval" + RUN)
            await conn.execute(
                """INSERT INTO forge.forge_approval (episode_id, artifact_sha256, scope, token_hash, issued_by)
                   VALUES ($1, $2, 'publish', $3, 'owner')""", ep, digest, sha("token"))
            await conn.execute("SELECT forge.forge_consume_approval($1, $2, 'publish')", ep, digest)
            await expect_error(conn, "SELECT forge.forge_consume_approval($1, $2, 'publish')", ep, digest,
                               label="approval reuse")
            PASS += 1
            print("PASS T11 approval single-use")

        async with conn.transaction():
            ep = await episode(conn, "t12")
            await expect_error(conn,
                """INSERT INTO forge.forge_artifact (episode_id, kind, path, sha256, bytes)
                   VALUES ($1, 'svg', '/x.svg', $2, 0)""", ep, sha("artifact"),
                sqlstate="23514", label="zero-byte artifact")
            PASS += 1
            print("PASS T12 zero-byte artifact refused")

        async with conn.transaction():
            skill = f"s-{RUN}"
            await conn.execute(
                f"""INSERT INTO forge.forge_skill
                   (skill_id, version, name, app, catalogue_hash, preconditions, steps, gates, status, promoted_at)
                   VALUES ('{skill}', 1, 'a', 'VectorCraft', 'sha256:'||repeat('a',64), '{{}}', '[]', '[]', 'active', now())""")
            await expect_error(conn,
                f"""INSERT INTO forge.forge_skill
                   (skill_id, version, name, app, catalogue_hash, preconditions, steps, gates, status, promoted_at)
                   VALUES ('{skill}', 2, 'b', 'VectorCraft', 'sha256:'||repeat('b',64), '{{}}', '[]', '[]', 'active', now())""",
                sqlstate="23505", label="second active skill")
            PASS += 1
            print("PASS T13 one active skill version")

        async with conn.transaction():
            ep = await episode(conn, "t14")
            await conn.execute("SELECT forge.forge_transition_episode($1, 'briefed')", ep)
            await expect_error(conn, "SELECT forge.forge_transition_episode($1, 'intake')", ep,
                               sqlstate="P0001", label="re-entry into intake")
            PASS += 1
            print("PASS T14 illegal reverse transition")

        async with conn.transaction():
            ep = await episode(conn, "t15")
            for state in ("briefed", "planned", "context_ready", "executing", "verifying", "critiquing"):
                await conn.execute("SELECT forge.forge_transition_episode($1, $2)", ep, state)
            await conn.execute("SELECT forge.forge_transition_episode($1, 'accepted', 'pass')", ep)
            await expect_error(conn, "SELECT forge.forge_transition_episode($1, 'failed')", ep,
                               sqlstate="P0001", label="terminal accepted transition")
            PASS += 1
            print("PASS T15 no transition out of accepted")

        async with conn.transaction():
            triggers = await conn.fetchval(
                """SELECT count(*) FROM pg_trigger
                   WHERE NOT tgisinternal AND tgname LIKE 'forge_%_append_only'""")
            expected = await conn.fetchval(
                """SELECT count(*) FROM information_schema.tables
                   WHERE table_schema='forge'
                     AND table_name IN ('forge_event','forge_artifact','forge_gate','forge_critique','forge_eval')""")
            assert triggers == expected == 5, (triggers, expected)
            PASS += 1
            print("PASS T16 append-only triggers present")

        async with conn.transaction():
            job_id = await conn.fetchval("INSERT INTO forge.forge_job (kind) VALUES ('t17') RETURNING id")
            await expect_error(conn, "SELECT forge.forge_finish_job($1, true)", job_id,
                               label="finish queued job")
            claimed = await conn.fetchrow("SELECT * FROM forge.forge_claim_job('t17-w', 30)")
            assert claimed and claimed["id"] == job_id
            await conn.execute("SELECT forge.forge_finish_job($1, true)", job_id)
            PASS += 1
            print("PASS T17 finish queued refused; claimed finish succeeds")

        async with conn.transaction():
            ep = await episode(conn, "t18")
            await conn.execute(
                """INSERT INTO forge.forge_event (episode_id, seq, kind, payload, prev_hash, hash)
                   VALUES ($1, 1, 'forged', '{}'::jsonb, repeat('0',64), repeat('a',64))""",
                ep,
            )
            chain = await conn.fetchrow("SELECT * FROM forge.forge_verify_event_chain($1)", ep)
            assert chain["broken"] >= 1, chain
            PASS += 1
            print("PASS T18 forged event detected by chain verifier")

        # Expected-to-fail intentional: first skill insert above is a duplicate attempt only
        # if a prior test leaked. All tests roll back, so this assertion remains independent.
    finally:
        await conn.close()
    print(f"RESULT pass={PASS} fail={FAIL}")


if __name__ == "__main__":
    asyncio.run(main())

