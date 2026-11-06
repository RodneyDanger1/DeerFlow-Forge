"""W2-C worker tests: one claim, handler, truthful finish. No DB/network."""
from __future__ import annotations

import asyncio
import unittest

from forge_worker import ForgeWorker, LeaseReaper


class FakeRepo:
    def __init__(self, jobs):
        self.jobs = list(jobs)
        self.finished = []

    async def claim_job(self, worker, *, lease_s=300):
        return self.jobs.pop(0) if self.jobs else None

    async def finish_job(self, job_id, *, ok, error=None):
        self.finished.append({"id": job_id, "ok": ok, "error": error})
        return {"id": job_id, "state": "succeeded" if ok else "failed"}

    async def reap_expired_jobs(self):
        return 0


class WorkerTests(unittest.IsolatedAsyncioTestCase):
    async def test_success_finishes_once(self):
        repo = FakeRepo([{"id": 1, "payload": {"x": 1}}])
        seen = []
        worker = ForgeWorker(repo, lambda payload: _ok(seen, payload))
        result = await worker.run_once()
        self.assertTrue(result["ok"])
        self.assertEqual(repo.finished, [{"id": 1, "ok": True, "error": None}])
        self.assertEqual(seen, [{"x": 1}])

    async def test_empty_queue_returns_none_and_finishes_nothing(self):
        repo = FakeRepo([])
        worker = ForgeWorker(repo, _noop)
        self.assertIsNone(await worker.run_once())
        self.assertEqual(repo.finished, [])

    async def test_handler_exception_finishes_failed(self):
        repo = FakeRepo([{"id": 2, "payload": {}}])

        async def boom(_):
            raise RuntimeError("handler broke")

        worker = ForgeWorker(repo, boom)
        result = await worker.run_once()
        self.assertFalse(result["ok"])
        self.assertIn("RuntimeError: handler broke", result["error"])
        self.assertEqual(repo.finished, [{"id": 2, "ok": False, "error": "RuntimeError: handler broke"}])

    async def test_reaper_runs_one_iteration_and_stops(self):
        repo = FakeRepo([])
        stop = asyncio.Event()
        reaper = LeaseReaper(repo, interval_s=0.01)
        stop.set()
        self.assertEqual(await reaper.run(stop), 0)
        self.assertEqual(repo.finished, [])

    async def test_reaper_requeues_then_stops(self):
        repo = FakeRepo([])
        reaper = LeaseReaper(repo, interval_s=0.01)
        stop = asyncio.Event()
        task = asyncio.create_task(reaper.run(stop))
        await asyncio.sleep(0.02)
        stop.set()
        await task
        self.assertEqual(repo.finished, [])

    async def test_kind_mismatch_fails_without_running_handler(self):
        repo = FakeRepo([{"id": 9, "kind": "other.job", "payload": {}}])
        seen = []
        worker = ForgeWorker(repo, lambda payload: _ok(seen, payload),
                             kind="forge.tool_call")
        result = await worker.run_once()
        self.assertFalse(result["ok"])
        self.assertIn("E_JOB_KIND", result["error"])
        self.assertEqual(seen, [])
        self.assertEqual(repo.finished[0]["ok"], False)

    async def test_matching_kind_runs_handler(self):
        repo = FakeRepo([{"id": 10, "kind": "forge.tool_call", "payload": {"x": 2}}])
        seen = []
        worker = ForgeWorker(repo, lambda payload: _ok(seen, payload),
                             kind="forge.tool_call")
        result = await worker.run_once()
        self.assertTrue(result["ok"])
        self.assertEqual(seen, [{"x": 2}])

    async def test_drain_stops_on_empty(self):
        repo = FakeRepo([{"id": 3, "payload": {}}, {"id": 4, "payload": {}}])
        worker = ForgeWorker(repo, _noop)
        results = await worker.drain(max_jobs=5)
        self.assertEqual([r["id"] for r in results], [3, 4])
        self.assertEqual(len(repo.finished), 2)


async def _noop(_):
    return None


async def _ok(seen, payload):
    seen.append(payload)


if __name__ == "__main__":
    unittest.main()

