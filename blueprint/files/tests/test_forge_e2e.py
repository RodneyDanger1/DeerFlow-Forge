"""W2-D end-to-end: real SQL repository + HTTP service + worker + reaper."""
from __future__ import annotations

import asyncio
import json
import os
import threading
import unittest
import uuid
from http.client import HTTPConnection

from forge_repo import ForgeRepo
from forge_service import make_server
from forge_worker import ForgeWorker, LeaseReaper

DSN = os.environ.get("FORGE_TEST_DSN")


@unittest.skipUnless(DSN, "FORGE_TEST_DSN not set")
class EndToEndTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.run_id = uuid.uuid4().hex
        self.repo = await ForgeRepo.connect(DSN)

    async def asyncTearDown(self):
        await self.repo.close()

    def _request(self, port, method, path, body=None):
        conn = HTTPConnection("127.0.0.1", port, timeout=10)
        payload = json.dumps(body) if body is not None else None
        conn.request(method, path, body=payload,
                     headers={"Content-Type": "application/json"} if payload else {})
        response = conn.getresponse()
        data = json.loads(response.read())
        conn.close()
        return response.status, data

    async def test_http_real_repository_create_get_and_conflict(self):
        server = make_server(repo_factory=lambda: ForgeRepo.connect(DSN), port=0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            health_status, health_body = await asyncio.to_thread(
                self._request, server.server_address[1], "GET", "/healthz")
            self.assertEqual(health_status, 200)
            self.assertTrue(health_body["repo"]["ok"])
            body = {"idempotency_key": f"e2e-{self.run_id}", "account_id": 1,
                    "brief": "e2e", "task_family": "ai_badge_trace"}
            status, created = await asyncio.to_thread(self._request, server.server_address[1], "POST", "/v1/episodes", body)
            self.assertEqual(status, 201)
            episode_id = created["episode"]["id"]
            status, fetched = await asyncio.to_thread(self._request, server.server_address[1], "GET", f"/v1/episodes/{episode_id}")
            self.assertEqual(status, 200)
            self.assertEqual(fetched["episode"]["id"], episode_id)
            status, conflict = await asyncio.to_thread(self._request, server.server_address[1], "POST", "/v1/episodes", body)
            self.assertEqual(status, 409)
            self.assertEqual(conflict["error"]["code"], "E_EPISODE_EXISTS")
        finally:
            server.shutdown()
            server.server_close()
            server.forge_loop.run(server.forge_repo.close())

    async def test_worker_finishes_real_job_and_reaper_requeues_expired(self):
        job_id = await self.repo.create_job(kind="e2e", payload={"n": 1})
        seen = []
        worker = ForgeWorker(self.repo, lambda payload: _capture(seen, payload))
        result = await worker.run_once()
        self.assertTrue(result["ok"])
        self.assertEqual(seen, [{"n": 1}])
        state = await self.repo.pool.fetchval("SELECT state FROM forge.forge_job WHERE id=$1", job_id)
        self.assertEqual(state, "succeeded")

        expired = await self.repo.create_job(kind="e2e-lease")
        await self.repo.claim_job("e2e-worker", lease_s=1)
        await asyncio.sleep(1.2)
        reaper = LeaseReaper(self.repo, interval_s=0.05)
        stop = asyncio.Event()
        task = asyncio.create_task(reaper.run(stop))
        await asyncio.sleep(0.12)
        stop.set()
        await task
        second = await self.repo.claim_job("e2e-worker", lease_s=30)
        self.assertEqual(second["id"], expired)
        self.assertEqual(second["attempts"], 2)


async def _capture(seen, payload):
    seen.append(payload)


if __name__ == "__main__":
    unittest.main()
