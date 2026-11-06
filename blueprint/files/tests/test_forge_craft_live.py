"""Opt-in live Craft integration: real binary, real PostgreSQL, persisted gateway call."""
from __future__ import annotations

import json
import os
import tempfile
import unittest
import uuid

from forge_craft_registry import VECTOR_KEY, load_verified_registry
from forge_gateway import Gateway, ToolCall, ToolSpec
from forge_repo import ForgeGatewayRepo, ForgeRepo

DSN = os.environ.get("FORGE_TEST_DSN")
LIVE = os.environ.get("FORGE_CRAFT_LIVE") == "1"
INPUT = os.environ.get(
    "FORGE_CRAFT_INPUT",
    "/opt/pod-pipeline-staging/data/staging/g0/retouch_input.png")
TRACE_PARAMS = {"mode": "color", "palette": "limited", "colors": 12,
                "ignoreWhite": True, "paths": 65}


class CountingExecutor:
    def __init__(self, inner):
        self.inner = inner
        self.calls = 0

    def run(self, spec, call):
        self.calls += 1
        return self.inner.run(spec, call)


@unittest.skipUnless(DSN and LIVE, "FORGE_TEST_DSN + FORGE_CRAFT_LIVE=1 required")
class LiveCraftGatewayTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.repo = await ForgeRepo.connect(DSN)
        self.episode = await self.repo.create_episode(
            idempotency_key=f"live-craft-{uuid.uuid4().hex}", account_id=1,
            brief="live craft", task_family="ai_badge_trace")
        self.work = tempfile.TemporaryDirectory(prefix="forge-live-craft-")
        real, self.probes = load_verified_registry(work_root=self.work.name)
        self.executor = CountingExecutor(real)
        spec = ToolSpec(tool_id=VECTOR_KEY[0], allowed_roles=("operator",),
                        allowed_cmds=(VECTOR_KEY[1],), roots=(self.work.name,))
        self.gateway = Gateway([spec], self.executor, ForgeGatewayRepo(self.repo.pool),
                               roles={"tok": "operator"})
        self.call = ToolCall(
            episode_id=str(self.episode["id"]), tool_id=VECTOR_KEY[0],
            cmd_id=VECTOR_KEY[1],
            params={"input_png": INPUT,
                    "trace_params_json": json.dumps(TRACE_PARAMS)})

    async def asyncTearDown(self):
        self.work.cleanup()
        await self.repo.close()

    async def test_real_trace_is_persisted_and_replayed(self):
        first = await self.gateway.execute(self.call, "tok")
        self.assertEqual(first.state, "succeeded")
        self.assertEqual(len(first.artifacts), 2)
        self.assertEqual(self.executor.calls, 1)
        second = await self.gateway.execute(self.call, "tok")
        self.assertTrue(second.replayed)
        self.assertEqual(self.executor.calls, 1)
        row = await self.repo.pool.fetchrow(
            "SELECT state, result::text FROM forge.forge_tool_call "
            "WHERE idempotency_key=$1", first.idempotency_key)
        self.assertEqual(row["state"], "succeeded")
        payload = json.loads(row["result"])
        self.assertEqual(len(payload["artifacts"]), 2)
        self.assertTrue(all(len(a["sha256"]) == 64 for a in payload["artifacts"]))


if __name__ == "__main__":
    unittest.main()
