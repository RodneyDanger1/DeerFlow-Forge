"""Consumer seam: payload validation -> gateway -> worker success/failure truth."""
from __future__ import annotations

import unittest

from forge_consumer import ConsumerError, ToolCallConsumer, payload_to_call
from forge_gateway import PolicyError, ToolResult
from forge_worker import ForgeWorker


class FakeGateway:
    def __init__(self, result=None, error=None):
        self.result = result or ToolResult(
            idempotency_key="sha256:" + "a" * 64, state="succeeded")
        self.error = error
        self.calls = []

    async def execute(self, call, token):
        self.calls.append((call, token))
        if self.error is not None:
            raise self.error
        return self.result


class FakeWorkerRepo:
    def __init__(self, job):
        self.job = job
        self.finished = []

    async def claim_job(self, worker, *, lease_s=300):
        job, self.job = self.job, None
        return job

    async def finish_job(self, job_id, *, ok, error=None):
        self.finished.append((job_id, ok, error))
        return {"id": job_id, "state": "succeeded" if ok else "failed"}


PAYLOAD = {"episode_id": "ep-1", "tool_id": "vectorcraft.trace",
           "cmd_id": "imageTrace.make", "params": {"input_png": "/tmp/in.png"}}


class PayloadTests(unittest.TestCase):
    def test_valid_payload_maps_to_tool_call(self):
        call = payload_to_call(PAYLOAD)
        self.assertEqual(call.episode_id, "ep-1")
        self.assertEqual(call.tool_id, "vectorcraft.trace")
        self.assertEqual(call.params, {"input_png": "/tmp/in.png"})

    def test_malformed_payloads_refused_by_name(self):
        cases = [
            None,
            {},
            {**PAYLOAD, "episode_id": ""},
            {**PAYLOAD, "tool_id": 3},
            {**PAYLOAD, "cmd_id": ""},
            {**PAYLOAD, "params": []},
            {**PAYLOAD, "paths": "nope"},
            {**PAYLOAD, "input_hashes": [1]},
        ]
        for payload in cases:
            with self.subTest(payload=payload), self.assertRaises(ConsumerError) as caught:
                payload_to_call(payload)
            self.assertEqual(caught.exception.code, "E_REQUEST_INVALID")


class ConsumerTests(unittest.IsolatedAsyncioTestCase):
    async def test_success_returns_gateway_result(self):
        gateway = FakeGateway()
        consumer = ToolCallConsumer(gateway, "tok")
        result = await consumer(PAYLOAD)
        self.assertEqual(result.state, "succeeded")
        self.assertEqual(gateway.calls[0][1], "tok")

    async def test_refused_result_is_named_consumer_error(self):
        gateway = FakeGateway(ToolResult(idempotency_key="k", state="refused",
                                         refusal_code="E_COMMAND_UNKNOWN"))
        with self.assertRaises(ConsumerError) as caught:
            await ToolCallConsumer(gateway, "tok")(PAYLOAD)
        self.assertEqual(caught.exception.code, "E_COMMAND_UNKNOWN")

    async def test_failed_result_has_named_fallback(self):
        gateway = FakeGateway(ToolResult(idempotency_key="k", state="failed"))
        with self.assertRaises(ConsumerError) as caught:
            await ToolCallConsumer(gateway, "tok")(PAYLOAD)
        self.assertEqual(caught.exception.code, "E_TOOL_FAILED")

    async def test_gateway_policy_error_is_preserved(self):
        gateway = FakeGateway(error=PolicyError("E_ROOT_DENIED", "/etc/passwd"))
        with self.assertRaises(ConsumerError) as caught:
            await ToolCallConsumer(gateway, "tok")(PAYLOAD)
        self.assertEqual(caught.exception.code, "E_ROOT_DENIED")

    async def test_worker_marks_success_and_failure_truthfully(self):
        gateway = FakeGateway()
        consumer = ToolCallConsumer(gateway, "tok")
        repo = FakeWorkerRepo({"id": 1, "payload": PAYLOAD})
        worker = ForgeWorker(repo, consumer)
        result = await worker.run_once()
        self.assertTrue(result["ok"])
        self.assertEqual(repo.finished, [(1, True, None)])

        failing = FakeGateway(error=PolicyError("E_TIMEOUT", "slow"))
        repo2 = FakeWorkerRepo({"id": 2, "payload": PAYLOAD})
        worker2 = ForgeWorker(repo2, ToolCallConsumer(failing, "tok"))
        result2 = await worker2.run_once()
        self.assertFalse(result2["ok"])
        self.assertIn("E_TIMEOUT", result2["error"])
        self.assertFalse(repo2.finished[0][1])


if __name__ == "__main__":
    unittest.main()
