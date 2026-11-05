"""W2-C repository tests against a disposable PostgreSQL 16 database."""
from __future__ import annotations

import asyncio
import json
import os
import unittest
import uuid

from forge_repo import ForgeRepo, RepoShapeError

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
