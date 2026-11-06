"""W2-C repository tests against a disposable PostgreSQL 16 database."""
from __future__ import annotations

import asyncio
import json
import os
import unittest
import uuid

from forge_gateway import (
    ExecutionOutcome, Gateway, PolicyError, ToolCall, ToolSpec, idempotency_key,
)
from forge_repo import ForgeGatewayRepo, ForgeRepo, RepoShapeError

DSN = os.environ.get("FORGE_TEST_DSN")


@unittest.skipUnless(DSN, "FORGE_TEST_DSN not set")
class RepoTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.repo = await ForgeRepo.connect(DSN)
        self.run_id = uuid.uuid4().hex

    async def asyncTearDown(self):
        await self.repo.close()

    async def test_health_episode_and_job_roundtrip(self):
        episode = await self.repo.create_episode(
            idempotency_key=f"repo-{self.run_id}", account_id=1, brief="repo test",
            task_family="ai_badge_trace")
        self.assertEqual((await self.repo.get_episode(episode["id"]))["status"], "intake")

        job_id = await self.repo.create_job(kind="test", payload={"n": 1})
        claimed = await self.repo.claim_job("repo-worker", lease_s=30)
        self.assertIsNotNone(claimed)
        self.assertEqual(claimed["id"], job_id)
        self.assertIsNone(await self.repo.claim_job("repo-worker", lease_s=30))
        finished = await self.repo.finish_job(job_id, ok=True)
        self.assertEqual(finished["state"], "succeeded")

    async def test_expired_lease_is_requeued_once(self):
        job_id = await self.repo.create_job(kind="lease")
        first = await self.repo.claim_job("lease-worker", lease_s=1)
        self.assertEqual(first["id"], job_id)
        await asyncio.sleep(1.2)
        self.assertGreaterEqual(await self.repo.reap_expired_jobs(), 1)
        second = await self.repo.claim_job("lease-worker", lease_s=30)
        self.assertEqual(second["id"], job_id)
        self.assertEqual(second["attempts"], 2)
        self.assertEqual(await self.repo.reap_expired_jobs(), 0)

    async def test_exhausted_lease_is_abandoned_not_requeued(self):
        job_id = await self.repo.create_job(kind="poison", max_attempts=1)
        claimed = await self.repo.claim_job("poison-worker", lease_s=1)
        self.assertEqual(claimed["id"], job_id)
        await asyncio.sleep(1.2)
        self.assertEqual(await self.repo.reap_expired_jobs(), 1)
        state, error = await self.repo.pool.fetchrow(
            "SELECT state, last_error FROM forge.forge_job WHERE id=$1", job_id)
        self.assertEqual(state, "abandoned")
        self.assertEqual(error, "E_LEASE_EXPIRED_MAX_ATTEMPTS")
        self.assertIsNone(await self.repo.claim_job("poison-worker", lease_s=30))

    async def test_unknown_episode_is_none(self):
        self.assertIsNone(await self.repo.get_episode(str(uuid.uuid4())))

    async def test_eval_rows_are_immutable_per_arm(self):
        episode = await self.repo.create_episode(
            idempotency_key=f"eval-{self.run_id}", account_id=1, brief="eval",
            task_family="ai_badge_trace")
        base = await self.repo.record_eval(
            episode_id=str(episode["id"]), arm="baseline",
            technical={"n": 8, "passed": 7, "wilson_lower": 0.5291},
            verdict="unverified", human={"score": 3}, reviewer="lead")
        self.assertEqual(base["arm"], "baseline")
        self.assertEqual(base["technical"]["n"], 8)
        self.assertEqual(base["human"], {"score": 3})
        memory = await self.repo.record_eval(
            episode_id=str(episode["id"]), arm="memory",
            technical={"n": 8, "passed": 8, "wilson_lower": 0.6306},
            verdict="needs_human")
        self.assertEqual(memory["arm"], "memory")
        with self.assertRaises(PolicyError) as caught:
            await self.repo.record_eval(
                episode_id=str(episode["id"]), arm="baseline",
                technical={}, verdict="pass")
        self.assertEqual(caught.exception.code, "E_EVAL_EXISTS")
        with self.assertRaises(ValueError):
            await self.repo.record_eval(
                episode_id=str(episode["id"]), arm="other",
                technical={}, verdict="pass")
        with self.assertRaises(PolicyError) as caught:
            await self.repo.record_eval(
                episode_id=str(uuid.uuid4()), arm="baseline",
                technical={}, verdict="pass")
        self.assertEqual(caught.exception.code, "E_EPISODE_NOT_FOUND")

    async def test_transition_appends_exactly_one_event(self):
        """W3: the SQL transition function owns the event append; repo must not double-write."""
        episode = await self.repo.create_episode(
            idempotency_key=f"tx-{self.run_id}", account_id=1, brief="tx",
            task_family="ai_badge_trace")
        moved = await self.repo.transition(episode["id"], "briefed")
        self.assertEqual(moved["status"], "briefed")
        count = await self.repo.pool.fetchval(
            "SELECT count(*) FROM forge.forge_event WHERE episode_id=$1 "
            "AND kind='episode.transition'", episode["id"])
        self.assertEqual(count, 1)
        payload = await self.repo.pool.fetchval(
            "SELECT payload::text FROM forge.forge_event WHERE episode_id=$1 "
            "ORDER BY seq DESC LIMIT 1", episode["id"])
        payload = json.loads(payload)
        self.assertEqual(payload["from"], "intake")
        self.assertEqual(payload["to"], "briefed")


class FakeExecutor:
    """Permitted test double for the external CLI."""

    def __init__(self, outcome=None, error=None):
        self.calls = 0
        self.outcome = outcome or ExecutionOutcome(
            exit_code=0, duration_ms=12, argv=("fake-cli", "--trace"),
            artifacts=({"path": "build/x.png", "sha256": "a" * 64, "bytes": 10},))
        self.error = error

    def run(self, spec, call):
        self.calls += 1
        if self.error is not None:
            raise self.error
        return self.outcome


SPEC = ToolSpec(tool_id="craft.run", allowed_roles=("operator",),
                allowed_cmds=("imageTrace.make",), roots=())


@unittest.skipUnless(DSN, "FORGE_TEST_DSN not set")
class GatewayRepoDBTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.repo = await ForgeRepo.connect(DSN)
        self.episode = await self.repo.create_episode(
            idempotency_key=f"gw-{uuid.uuid4().hex}", account_id=1,
            brief="gateway repo test", task_family="ai_badge_trace")
        self.gateway_repo = ForgeGatewayRepo(self.repo.pool)
        self.executor = FakeExecutor()
        self.gateway = Gateway([SPEC], self.executor, self.gateway_repo,
                               roles={"tok-op": "operator"})
        self.call = ToolCall(episode_id=self.episode["id"], tool_id="craft.run",
                             cmd_id="imageTrace.make", params={"palette": 6})

    async def asyncTearDown(self):
        await self.repo.close()

    async def test_stale_in_flight_is_abandoned_then_replayed_as_failed(self):
        key = idempotency_key(self.call.episode_id, self.call.tool_id,
                              self.call.params, self.call.input_hashes)
        self.assertIsNone(await self.gateway_repo.begin(key, self.call))
        await self.repo.pool.execute(
            "UPDATE forge.forge_tool_call SET created_at=now() - interval '1 hour' "
            "WHERE idempotency_key=$1", key)
        abandoned = await self.gateway_repo.abandon_stale_in_flight(
            older_than_s=60, limit=10)
        self.assertIn(key, abandoned)
        row = await self.repo.pool.fetchrow(
            "SELECT state, result::text FROM forge.forge_tool_call "
            "WHERE idempotency_key=$1", key)
        self.assertEqual(row["state"], "failed")
        self.assertIn("E_IDEMPOTENCY_STALE", row["result"])
        self.assertEqual(await self.gateway_repo.abandon_stale_in_flight(
            older_than_s=60, limit=10), [])
        replay = await self.gateway.execute(self.call, "tok-op")
        self.assertEqual(replay.state, "failed")
        self.assertTrue(replay.replayed)
        self.assertEqual(self.executor.calls, 0)

    async def test_stale_abandonment_does_not_touch_fresh_in_flight(self):
        fresh = ToolCall(episode_id=self.episode["id"], tool_id="craft.run",
                         cmd_id="imageTrace.make", params={"palette": 8})
        fresh_key = idempotency_key(fresh.episode_id, fresh.tool_id,
                                    fresh.params, fresh.input_hashes)
        self.assertIsNone(await self.gateway_repo.begin(fresh_key, fresh))
        self.assertNotIn(fresh_key, await self.gateway_repo.abandon_stale_in_flight(
            older_than_s=60, limit=10))
        self.assertEqual((await self.gateway_repo.find(fresh_key)).state, "in_flight")

    async def test_execute_then_replay_persists_one_row(self):
        first = await self.gateway.execute(self.call, "tok-op")
        second = await self.gateway.execute(self.call, "tok-op")
        self.assertEqual(first.state, "succeeded")
        self.assertFalse(first.replayed)
        self.assertTrue(second.replayed)
        self.assertEqual(self.executor.calls, 1)
        row = await self.repo.pool.fetchrow(
            "SELECT state, episode_id::text, tool_id, cmd_id, params::text, argv, "
            "duration_ms, result::text FROM forge.forge_tool_call "
            "WHERE idempotency_key=$1", first.idempotency_key)
        self.assertEqual(row["state"], "succeeded")
        self.assertEqual(row["episode_id"], str(self.episode["id"]))
        self.assertEqual(row["tool_id"], "craft.run")
        self.assertEqual(row["cmd_id"], "imageTrace.make")
        self.assertIn('"palette": 6', row["params"])
        self.assertEqual(row["argv"], ["fake-cli", "--trace"])
        self.assertEqual(row["duration_ms"], 12)
        count = await self.repo.pool.fetchval(
            "SELECT count(*) FROM forge.forge_tool_call WHERE episode_id=$1",
            self.episode["id"])
        self.assertEqual(count, 1)

    async def test_in_flight_duplicate_refuses_without_execution(self):
        key = idempotency_key(self.call.episode_id, self.call.tool_id,
                              self.call.params, self.call.input_hashes)
        self.assertIsNone(await self.gateway_repo.begin(key, self.call))
        with self.assertRaises(PolicyError) as caught:
            await self.gateway.execute(self.call, "tok-op")
        self.assertEqual(caught.exception.code, "E_IDEMPOTENCY_IN_FLIGHT")
        self.assertFalse(caught.exception.terminal)
        self.assertEqual(self.executor.calls, 0)

    async def test_executor_exception_is_persisted_failed_and_replayed(self):
        failing = FakeExecutor(error=RuntimeError("driver crashed"))
        gateway = Gateway([SPEC], failing, self.gateway_repo,
                          roles={"tok-op": "operator"})
        with self.assertRaises(RuntimeError):
            await gateway.execute(self.call, "tok-op")
        key = idempotency_key(self.call.episode_id, self.call.tool_id,
                              self.call.params, self.call.input_hashes)
        row = await self.repo.pool.fetchrow(
            "SELECT state, result::text FROM forge.forge_tool_call "
            "WHERE idempotency_key=$1", key)
        self.assertEqual(row["state"], "failed")
        self.assertIn("RuntimeError: driver crashed", row["result"])
        replay = await gateway.execute(self.call, "tok-op")
        self.assertEqual(replay.state, "failed")
        self.assertTrue(replay.replayed)
        self.assertEqual(failing.calls, 1)


class RowShapeUnitTests(unittest.TestCase):
    """D6: _row must fail loudly on a shape problem; no database needed."""

    def test_row_without_id_raises_shape_error(self):
        with self.assertRaises(RepoShapeError):
            ForgeRepo._row({"state": "intake"})

    def test_all_null_composite_is_none(self):
        self.assertIsNone(ForgeRepo._row({"id": None, "state": None, "kind": None}))

    def test_row_with_unparseable_json_column_raises_shape_error(self):
        with self.assertRaises(RepoShapeError):
            ForgeRepo._row({"id": "x", "payload": "{not json"})

    def test_none_row_stays_none(self):
        self.assertIsNone(ForgeRepo._row(None))


if __name__ == "__main__":
    unittest.main()
