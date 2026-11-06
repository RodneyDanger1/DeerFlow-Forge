#!/usr/bin/env python3
"""Tests for the Forge gateway skeleton. Stdlib only: python -m unittest -v."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from forge_gateway import (
    EPISODE_STATES, TRANSITIONS, TERMINAL_STATES, Evidence, ExecutionOutcome, Gateway,
    InMemoryRepo, PolicyError, ToolCall, ToolSpec, build_verdict, can_transition,
    canonical_json, idempotency_key, is_terminal_refusal, may_retry, next_state,
    resolve_within, sha256_hex, validate_key,
)


class FakeExecutor:
    """Permitted test double for an external CLI (never a production branch)."""

    def __init__(self, outcome=None):
        self.calls = 0
        self.outcome = outcome or ExecutionOutcome(
            exit_code=0, duration_ms=12, argv=("fake-cli",),
            artifacts=({"path": "build/x.png", "sha256": "a" * 64, "bytes": 10},))

    def run(self, spec, call):
        self.calls += 1
        return self.outcome


SPEC = ToolSpec(
    tool_id="craft.run",
    allowed_roles=("vector_operator",),
    allowed_cmds=("imageTrace.make", "imageTrace.expand"),
    roots=("/tmp/forge-work",),
    writes=True,
)


class KeyTests(unittest.TestCase):
    def test_canonical_json_is_order_independent(self):
        self.assertEqual(canonical_json({"b": 1, "a": [2, {"d": 4, "c": 3}]}),
                         canonical_json({"a": [2, {"c": 3, "d": 4}], "b": 1}))

    def test_key_is_stable_and_well_formed(self):
        k1 = idempotency_key("ep", "craft.run", {"b": 2, "a": 1}, ["sha256:" + "f" * 64])
        k2 = idempotency_key("ep", "craft.run", {"a": 1, "b": 2}, ["sha256:" + "f" * 64])
        self.assertEqual(k1, k2)
        self.assertTrue(validate_key(k1))
        self.assertEqual(len(k1), 71)

    def test_key_changes_with_params_episode_and_inputs(self):
        base = idempotency_key("ep1", "t", {"a": 1})
        self.assertNotEqual(base, idempotency_key("ep2", "t", {"a": 1}))
        self.assertNotEqual(base, idempotency_key("ep1", "t", {"a": 2}))
        self.assertNotEqual(base, idempotency_key("ep1", "t", {"a": 1}, ["sha256:" + "1" * 64]))


class TransitionTests(unittest.TestCase):
    def test_transition_table_matches_design_count(self):
        self.assertEqual(len(TRANSITIONS), 36)
        self.assertTrue(set(EPISODE_STATES) >= {s for pair in TRANSITIONS for s in pair})

    def test_legal_transition(self):
        self.assertEqual(next_state("intake", "briefed"), "briefed")

    def test_illegal_transition_refused(self):
        for src, dst in (("intake", "accepted"), ("refused", "executing"),
                         ("accepted", "paused"), ("quarantined", "executing")):
            with self.assertRaises(PolicyError) as caught:
                next_state(src, dst)
            self.assertEqual(caught.exception.code, "E_TRANSITION_ILLEGAL")

    def test_unknown_state_refused(self):
        with self.assertRaises(PolicyError) as caught:
            next_state("not-a-state", "briefed")
        self.assertEqual(caught.exception.code, "E_EPISODE_STATE_UNKNOWN")

    def test_terminal_states_have_no_outgoing_edges(self):
        for state in TERMINAL_STATES:
            outgoing = {dst for src, dst in TRANSITIONS if src == state}
            self.assertEqual(outgoing, set(), f"{state} has outgoing edges")

    def test_can_transition_is_total(self):
        self.assertFalse(can_transition("intake", "accepted"))
        self.assertTrue(can_transition("critiquing", "accepted"))


class VerdictTests(unittest.TestCase):
    def full_pass(self, **overrides):
        base = dict(process_ok=True, artifact_ok=True, gate_ok=True, render_ok=True,
                    critique="pass", human=None, human_required=False)
        base.update(overrides)
        return build_verdict(Evidence(**base))

    def test_happy_path_passes(self):
        self.assertEqual(self.full_pass(), ("pass", []))

    def test_missing_gate_is_unverified_not_pass(self):
        verdict, reasons = self.full_pass(gate_ok=None)
        self.assertEqual(verdict, "unverified")
        self.assertIn("E_GATE_MISSING", reasons)

    def test_gate_failure_dominates_positive_critic(self):
        verdict, _ = self.full_pass(gate_ok=False)
        self.assertEqual(verdict, "reject")

    def test_vacuous_gate_is_reject(self):
        verdict, reasons = self.full_pass(gate_vacuous=True)
        self.assertEqual(verdict, "reject")
        self.assertIn("E_GATE_VACUOUS", reasons)

    def test_source_mutation_is_reject_before_everything(self):
        verdict, reasons = self.full_pass(source_mutated=True)
        self.assertEqual((verdict, reasons[0]), ("reject", "E_SOURCE_MUTATED"))

    def test_critic_reject_goes_to_human(self):
        verdict, _ = self.full_pass(critique="reject")
        self.assertEqual(verdict, "needs_human")

    def test_missing_critic_goes_to_human(self):
        verdict, _ = self.full_pass(critique=None)
        self.assertEqual(verdict, "needs_human")

    def test_human_required_blocks_acceptance(self):
        verdict, _ = self.full_pass(human_required=True)
        self.assertEqual(verdict, "needs_human")

    def test_human_reject_overrides_critic_pass(self):
        verdict, _ = self.full_pass(human_required=True, human="reject")
        self.assertEqual(verdict, "reject")


class PathTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="forge-root-")
        self.outside = tempfile.mkdtemp(prefix="forge-outside-")
        Path(self.root, "work").mkdir()

    def test_path_inside_root_resolves(self):
        target = str(Path(self.root, "work", "a.png"))
        self.assertEqual(resolve_within(target, [self.root]), Path(target))

    def test_traversal_is_denied(self):
        target = str(Path(self.root, "..", "escape.png"))
        with self.assertRaises(PolicyError) as caught:
            resolve_within(target, [self.root])
        self.assertEqual(caught.exception.code, "E_ROOT_DENIED")

    def test_sibling_root_is_denied(self):
        target = str(Path(self.outside, "a.png"))
        with self.assertRaises(PolicyError) as caught:
            resolve_within(target, [self.root])
        self.assertEqual(caught.exception.code, "E_ROOT_DENIED")


class RefusalTests(unittest.TestCase):
    def test_terminal_codes_never_retry(self):
        for code in ("E_SOURCE_MUTATED", "E_ROOT_DENIED", "E_PUBLISH_NOT_APPROVED",
                     "E_BUDGET_EXCEEDED", "E_COMMAND_UNKNOWN"):
            self.assertTrue(is_terminal_refusal(code))
            self.assertFalse(may_retry(code, 1, 3))

    def test_retryable_codes_retry_until_budget(self):
        self.assertFalse(is_terminal_refusal("E_ARTIFACT_MISSING"))
        self.assertTrue(may_retry("E_ARTIFACT_MISSING", 1, 2))
        self.assertFalse(may_retry("E_ARTIFACT_MISSING", 2, 2))

    def test_unknown_code_fails_closed(self):
        self.assertTrue(is_terminal_refusal("E_SOMETHING_NEW"))


class GatewayTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.repo = InMemoryRepo()
        self.executor = FakeExecutor()
        self.gw = Gateway([SPEC], self.executor, self.repo,
                          roles={"tok-op": "vector_operator", "tok-critic": "visual_critic"})
        self.call = ToolCall(episode_id="ep1", tool_id="craft.run",
                             cmd_id="imageTrace.make", params={"palette": 6},
                             paths=("/tmp/forge-work/out.svg",))

    async def test_success_then_replay_does_not_reexecute(self):
        r1 = await self.gw.execute(self.call, "tok-op")
        r2 = await self.gw.execute(self.call, "tok-op")
        self.assertEqual(r1.state, "succeeded")
        self.assertFalse(r1.replayed)
        self.assertTrue(r2.replayed)
        self.assertEqual(r1.idempotency_key, r2.idempotency_key)
        self.assertEqual(self.executor.calls, 1)

    async def test_different_params_produce_new_call(self):
        await self.gw.execute(self.call, "tok-op")
        other = ToolCall(episode_id="ep1", tool_id="craft.run",
                         cmd_id="imageTrace.make", params={"palette": 8})
        await self.gw.execute(other, "tok-op")
        self.assertEqual(self.executor.calls, 2)

    async def test_role_denied_is_refusal_not_exception(self):
        result = await self.gw.execute(self.call, "tok-critic")
        self.assertEqual(result.state, "refused")
        self.assertEqual(result.refusal_code, "E_ROLE_DENIED")
        self.assertEqual(self.executor.calls, 0)

    async def test_unknown_token_denied(self):
        result = await self.gw.execute(self.call, "nope")
        self.assertEqual(result.refusal_code, "E_ROLE_DENIED")

    async def test_cmd_not_allowlisted_fails_closed(self):
        bad = ToolCall(episode_id="ep1", tool_id="craft.run",
                       cmd_id="file.delete", params={})
        with self.assertRaises(PolicyError) as caught:
            await self.gw.execute(bad, "tok-op")
        self.assertEqual(caught.exception.code, "E_COMMAND_UNKNOWN")
        self.assertEqual(self.executor.calls, 0)

    async def test_unknown_tool_fails_closed(self):
        bad = ToolCall(episode_id="ep1", tool_id="craft.rm", cmd_id=None, params={})
        with self.assertRaises(PolicyError) as caught:
            await self.gw.execute(bad, "tok-op")
        self.assertEqual(caught.exception.code, "E_COMMAND_UNKNOWN")

    async def test_root_violation_refused_before_side_effect(self):
        bad = ToolCall(episode_id="ep1", tool_id="craft.run",
                       cmd_id="imageTrace.make", params={},
                       paths=("/etc/passwd",))
        with self.assertRaises(PolicyError) as caught:
            await self.gw.execute(bad, "tok-op")
        self.assertEqual(caught.exception.code, "E_ROOT_DENIED")
        self.assertEqual(self.executor.calls, 0)
        self.assertEqual(self.repo.rows, {})

    async def test_executor_refusal_is_stored_and_replayed(self):
        refusing = FakeExecutor(ExecutionOutcome(exit_code=127, duration_ms=1,
                                                 argv=("fake-cli",),
                                                 refusal_code="E_COMMAND_UNKNOWN",
                                                 message="vendor binary not installed"))
        gw = Gateway([SPEC], refusing, self.repo, roles={"tok-op": "vector_operator"})
        r1 = await gw.execute(self.call, "tok-op")
        r2 = await gw.execute(self.call, "tok-op")
        self.assertEqual((r1.state, r1.refusal_code), ("refused", "E_COMMAND_UNKNOWN"))
        self.assertTrue(r2.replayed)
        self.assertEqual(refusing.calls, 1)

    async def test_failed_exit_is_failed_not_succeeded(self):
        failing = FakeExecutor(ExecutionOutcome(exit_code=1, duration_ms=2,
                                                argv=("fake-cli",), message="boom"))
        gw = Gateway([SPEC], failing, self.repo, roles={"tok-op": "vector_operator"})
        result = await gw.execute(self.call, "tok-op")
        self.assertEqual(result.state, "failed")
        self.assertEqual(result.exit_code, 1)


    async def test_in_flight_duplicate_is_refused_without_execution(self):
        key = idempotency_key(self.call.episode_id, self.call.tool_id,
                              self.call.params, self.call.input_hashes)
        await self.repo.begin(key, self.call)
        with self.assertRaises(PolicyError) as caught:
            await self.gw.execute(self.call, "tok-op")
        self.assertEqual(caught.exception.code, "E_IDEMPOTENCY_IN_FLIGHT")
        self.assertFalse(caught.exception.terminal)
        self.assertEqual(self.executor.calls, 0)

    async def test_executor_exception_is_persisted_as_failed(self):
        class BoomExecutor:
            def __init__(self):
                self.calls = 0
            def run(self, spec, call):
                self.calls += 1
                raise RuntimeError("boom")
        boom = BoomExecutor()
        gw = Gateway([SPEC], boom, self.repo, roles={"tok-op": "vector_operator"})
        with self.assertRaises(RuntimeError):
            await gw.execute(self.call, "tok-op")
        key = idempotency_key(self.call.episode_id, self.call.tool_id,
                              self.call.params, self.call.input_hashes)
        row = await self.repo.find(key)
        self.assertEqual(row.state, "failed")
        self.assertIn("RuntimeError: boom", row.message)
        self.assertEqual(boom.calls, 1)
        replay = await gw.execute(self.call, "tok-op")
        self.assertTrue(replay.replayed)
        self.assertEqual(boom.calls, 1)

    async def test_replay_carries_persisted_call_context(self):
        first = await self.gw.execute(self.call, "tok-op")
        replay = await self.gw.execute(self.call, "tok-op")
        self.assertEqual(replay.idempotency_key, first.idempotency_key)
        self.assertEqual(replay.episode_id, "ep1")
        self.assertEqual(replay.tool_id, "craft.run")
        self.assertEqual(replay.params, {"palette": 6})
        self.assertEqual(replay.argv, ("fake-cli",))
        self.assertEqual(replay.duration_ms, 12)


if __name__ == "__main__":
    unittest.main(verbosity=2)
