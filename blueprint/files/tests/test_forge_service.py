"""W2-C service tests over an ephemeral loopback port with a fake repository."""
from __future__ import annotations

import json
import threading
import unittest
from http.client import HTTPConnection

from forge_service import make_server


class FakeRepo:
    def __init__(self):
        self.rows = {}

    async def create_episode(self, *, idempotency_key, account_id, brief, task_family, budget=None):
        row = {"id": "00000000-0000-0000-0000-000000000001",
               "idempotency_key": idempotency_key, "account_id": account_id,
               "brief": brief, "task_family": task_family, "status": "intake"}
        self.rows[row["id"]] = row
        return row

    async def get_episode(self, episode_id):
        return self.rows.get(episode_id)


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.server = make_server(FakeRepo(), port=0)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def _request(self, method, path, body=None):
        conn = HTTPConnection("127.0.0.1", self.port, timeout=5)
        payload = json.dumps(body) if body is not None else None
        conn.request(method, path, body=payload,
                     headers={"Content-Type": "application/json"} if payload else {})
        response = conn.getresponse()
        data = json.loads(response.read())
        conn.close()
        return response.status, data

    def test_health(self):
        self.assertEqual(self._request("GET", "/healthz"), (200, {"ok": True, "service": "forge"}))

    def test_create_and_get_episode(self):
        status, created = self._request("POST", "/v1/episodes", {
            "idempotency_key": "svc-test", "account_id": 1,
            "brief": "test", "task_family": "ai_badge_trace"})
        self.assertEqual(status, 201)
        episode_id = created["episode"]["id"]
        status, fetched = self._request("GET", f"/v1/episodes/{episode_id}")
        self.assertEqual(status, 200)
        self.assertEqual(fetched["episode"]["id"], episode_id)

    def test_unknown_episode_404_named(self):
        status, body = self._request("GET", "/v1/episodes/does-not-exist")
        self.assertEqual(status, 404)
        self.assertEqual(body["error"]["code"], "E_EPISODE_NOT_FOUND")

    def test_bad_body_400_named(self):
        status, body = self._request("POST", "/v1/episodes", {"brief": "missing key"})
        self.assertEqual(status, 400)
        self.assertEqual(body["error"]["code"], "E_REQUEST_INVALID")


if __name__ == "__main__":
    unittest.main()
