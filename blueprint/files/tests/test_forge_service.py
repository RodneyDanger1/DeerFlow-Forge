"""W2-C service tests over an ephemeral loopback port with a fake repository."""
from __future__ import annotations

import asyncio
import json
import threading
import time
import unittest
from http.client import HTTPConnection

from forge_service import ServiceConfigError, _parse_config, main, make_server


class FakeRepo:
    def __init__(self, healthy=True):
        self.rows = {}
        self.healthy = healthy

    async def health(self):
        return {"ok": self.healthy, "tables": 13}

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
        status, body = self._request("GET", "/healthz")
        self.assertEqual(status, 200)
        self.assertTrue(body["ok"])
        self.assertEqual(body["repo"]["tables"], 13)

    def test_unhealthy_repo_is_503(self):
        server = make_server(FakeRepo(healthy=False), port=0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            conn = HTTPConnection("127.0.0.1", server.server_address[1], timeout=5)
            conn.request("GET", "/healthz")
            response = conn.getresponse()
            self.assertEqual(response.status, 503)
            self.assertEqual(json.loads(response.read())["error"]["code"], "E_SERVICE_UNHEALTHY")
            conn.close()
        finally:
            server.shutdown()
            server.server_close()

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


class _ConflictError(Exception):
    """Stands in for asyncpg's UniqueViolation at the service boundary."""

    sqlstate = "23505"


class ReplayRepo(FakeRepo):
    """Honours the idempotency contract: same key returns the stored episode."""

    def __init__(self):
        super().__init__()
        self.by_key = {}

    async def create_episode(self, *, idempotency_key, account_id, brief, task_family, budget=None):
        if idempotency_key in self.by_key:
            raise _ConflictError("duplicate key")
        row = await super().create_episode(idempotency_key=idempotency_key, account_id=account_id,
                                           brief=brief, task_family=task_family, budget=budget)
        self.by_key[idempotency_key] = row
        return row

    async def get_episode_by_idempotency_key(self, key):
        return self.by_key.get(key)


class LegacyConflictRepo(FakeRepo):
    """No lookup-by-key: replay must degrade to a named 409, not a 500."""

    async def create_episode(self, **kwargs):
        raise _ConflictError("duplicate key")


class ShapeRepo(FakeRepo):
    async def get_episode(self, episode_id):
        return {"state": "intake"}  # a row with no id is a shape error, not a 404


class SlowRepo(FakeRepo):
    def __init__(self):
        super().__init__()
        self.cancelled = False

    async def create_episode(self, **kwargs):
        try:
            await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            self.cancelled = True
            raise
        return await super().create_episode(**kwargs)


class Wave2ServiceTests(unittest.TestCase):
    """D1/D2/D6/D7 regressions: timeout, replay, shape, field validation."""

    def _start(self, repo, **kwargs):
        server = make_server(repo, port=0, **kwargs)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        return server, server.server_address[1]

    def _request(self, port, method, path, body=None):
        conn = HTTPConnection("127.0.0.1", port, timeout=5)
        payload = json.dumps(body) if body is not None else None
        conn.request(method, path, body=payload,
                     headers={"Content-Type": "application/json"} if payload else {})
        response = conn.getresponse()
        data = json.loads(response.read())
        conn.close()
        return response.status, data

    def test_slow_create_times_out_504_and_cancels_the_call(self):
        repo = SlowRepo()
        server, port = self._start(repo, call_timeout_s=0.05)
        status, body = self._request(port, "POST", "/v1/episodes", {
            "idempotency_key": "slow-1", "account_id": 1,
            "brief": "slow", "task_family": "ai_badge_trace"})
        self.assertEqual(status, 504)
        self.assertEqual(body["error"]["code"], "E_SERVICE_TIMEOUT")
        time.sleep(0.2)
        self.assertTrue(repo.cancelled, "the in-flight coroutine must be cancelled")

    def test_replay_returns_the_existing_episode_200(self):
        repo = ReplayRepo()
        server, port = self._start(repo)
        payload = {"idempotency_key": "replay-1", "account_id": 1,
                   "brief": "replay", "task_family": "ai_badge_trace"}
        first_status, first = self._request(port, "POST", "/v1/episodes", payload)
        self.assertEqual(first_status, 201)
        second_status, second = self._request(port, "POST", "/v1/episodes", payload)
        self.assertEqual(second_status, 200)
        self.assertEqual(second["episode"]["id"], first["episode"]["id"])
        self.assertTrue(second.get("replayed"))

    def test_conflict_without_lookup_degrades_to_named_409(self):
        server, port = self._start(LegacyConflictRepo())
        status, body = self._request(port, "POST", "/v1/episodes", {
            "idempotency_key": "conflict-1", "account_id": 1,
            "brief": "conflict", "task_family": "ai_badge_trace"})
        self.assertEqual(status, 409)
        self.assertEqual(body["error"]["code"], "E_EPISODE_EXISTS")

    def test_row_shape_error_is_named_500_not_404(self):
        server, port = self._start(ShapeRepo())
        status, body = self._request(port, "GET", "/v1/episodes/whatever")
        self.assertEqual(status, 500)
        self.assertEqual(body["error"]["code"], "E_REPO_SHAPE")

    def test_malformed_post_fields_400(self):
        base = {"idempotency_key": "valid-1", "account_id": 1,
                "brief": "ok", "task_family": "ai_badge_trace"}
        cases = [
            {**base, "brief": None},
            {**base, "account_id": -5},
            {**base, "account_id": True},
            {**base, "budget": [1, 2]},
            {**base, "task_family": "Bad Family!"},
            {**base, "idempotency_key": "   "},
        ]
        server, port = self._start(FakeRepo())
        for case in cases:
            with self.subTest(case=case):
                status, body = self._request(port, "POST", "/v1/episodes", case)
                self.assertEqual(status, 400)
                self.assertEqual(body["error"]["code"], "E_REQUEST_INVALID")


class ServiceConfigTests(unittest.TestCase):
    def test_valid_config(self):
        cfg = _parse_config(["--dsn", "postgresql://x/y", "--port", "0"])
        self.assertEqual(cfg["host"], "127.0.0.1")
        self.assertEqual(cfg["port"], 0)
        self.assertEqual(cfg["call_timeout_s"], 30.0)

    def test_missing_dsn_is_named(self):
        with self.assertRaises(ServiceConfigError):
            _parse_config([])

    def test_non_loopback_rejected(self):
        with self.assertRaises(ServiceConfigError):
            _parse_config(["--dsn", "postgresql://x/y", "--host", "0.0.0.0"])

    def test_bad_port_and_timeout_rejected(self):
        for argv in (["--dsn", "d", "--port", "70000"],
                     ["--dsn", "d", "--call-timeout-s", "0"]):
            with self.subTest(argv=argv), self.assertRaises(ServiceConfigError):
                _parse_config(argv)

    def test_main_without_dsn_exits_2(self):
        self.assertEqual(main(["--dsn", ""]), 2)


if __name__ == "__main__":
    unittest.main()
