/**
 * Approval, compaction and retry operations.
 *
 * These are the three "policy as a step" operations: they must be able to
 * decide, defer, shrink or repeat work without ever blocking the pipeline or
 * inventing evidence.
 */

import assert from 'node:assert/strict';
import test from 'node:test';

import { STATUS } from '../src/envelope.mjs';
import { Conductor } from '../src/machine.mjs';
import {
  allowAllPolicy,
  createDocumentVerifier,
  createMemoryCraftPort,
  denyAllPolicy,
  requireHumanPolicy,
} from '../src/ports.mjs';
import { MemoryStore } from '../src/store.mjs';
import { PLANS, manyLayerPlan, makeConductor } from './fixtures/harness.mjs';

const gatedPlan = () => [{ ...PLANS.single[0], requiresApproval: true }];

test('approval deny halts before any side effect reaches the app', async () => {
  const { conductor, port } = await makeConductor({ plan: gatedPlan(), approval: denyAllPolicy('not allowed') });
  const result = await conductor.run();

  assert.equal(result.status, 'halted');
  assert.equal(conductor.state.halt.reason, 'DENIED_BY_POLICY');
  assert.equal(conductor.state.plan[0].status, 'denied');
  assert.equal(port.calls.length, 0);
  assert.equal(conductor.state.events.at(-1).payload.decision, 'deny');
});

test('require_human yields once, then an operator decision resumes the episode', async () => {
  const { conductor, port } = await makeConductor({ plan: gatedPlan(), approval: requireHumanPolicy('needs Riley') });

  const first = await conductor.run();
  assert.equal(first.status, 'awaiting_human');
  assert.equal(port.calls.length, 0);
  assert.equal(conductor.state.events.at(-1).kind, 'approval_required');
  const eventsAfterFirst = conductor.state.events.length;

  // Re-running must not spam the log while the human decides.
  const second = await conductor.run();
  assert.equal(second.status, 'awaiting_human');
  assert.equal(conductor.state.events.length, eventsAfterFirst);

  await conductor.recordDecision('add-layer', 'allow', { decidedBy: 'riley', reason: 'approved in review' });
  const third = await conductor.run();

  assert.equal(third.status, 'finished');
  assert.equal(port.calls.length, 1);
  assert.equal(conductor.state.approvals['add-layer'].decision, 'allow');
  assert.ok(conductor.state.events.some((e) => e.kind === 'human_decision'));
});

test('an operator deny halts the episode', async () => {
  const { conductor, port } = await makeConductor({ plan: gatedPlan(), approval: requireHumanPolicy() });
  await conductor.run();
  await conductor.recordDecision('add-layer', 'deny', { decidedBy: 'riley', reason: 'too risky' });

  assert.equal(conductor.state.halt.reason, 'DENIED_BY_POLICY');
  const result = await conductor.run();
  assert.equal(result.status, 'halted');
  assert.equal(port.calls.length, 0);
});

test('compaction fires on a token budget, keeps the pinned head and never rewrites events', async () => {
  const { conductor } = await makeConductor({
    plan: manyLayerPlan(8),
    config: { compactionThresholdTokens: 50, checkpointEveryEvents: 999 },
  });
  const result = await conductor.run();
  assert.equal(result.status, 'finished');

  const view = conductor.view();
  assert.ok(conductor.state.counters.compactions >= 1, 'compaction must have fired');
  assert.equal(view.head.length, 2, 'pinned head must survive compaction');
  assert.ok(view.note.includes('Goal:'), 'compaction must publish a continuation note');
  assert.ok(view.omittedEvents > 0, 'the view must actually omit the compacted middle');
  assert.equal(
    conductor.state.events.filter((e) => e.kind === 'command_result').length,
    8,
    'the event log is immutable: compaction adds a note, it does not delete history',
  );
  assert.ok(conductor.state.compaction.consumedSeq > 0);
});

test('retry repairs a repairable failure and the episode finishes', async () => {
  const { conductor, port } = await makeConductor({
    plan: PLANS.single,
    craft: { plannedFailures: [STATUS.NO_MATCH] },
  });
  const result = await conductor.run();

  assert.equal(result.status, 'finished');
  assert.equal(conductor.state.counters.repairs, 1);
  assert.equal(conductor.state.plan[0].attempts, 2);
  assert.equal(port.calls.length, 2, 'one failed attempt plus one repaired attempt');

  const repair = conductor.state.events.find((e) => e.kind === 'repair_scheduled');
  assert.ok(repair, 'a repair must be scheduled');
  assert.equal(repair.payload.status, STATUS.NO_MATCH);
  assert.match(repair.payload.feedback, /planned NO_MATCH/);

  const statuses = conductor.state.ledgerEntries.map((entry) => entry.status);
  assert.deepEqual(statuses, [STATUS.NO_MATCH, STATUS.OK], 'both attempts stay in the audit ledger');
  assert.equal(conductor.state.plan[0].status, 'ok');
});

test('repair budget exhaustion halts instead of looping forever', async () => {
  const { conductor, port } = await makeConductor({
    plan: PLANS.single,
    craft: { plannedFailures: [STATUS.NO_MATCH, STATUS.NO_MATCH, STATUS.NO_MATCH] },
    config: { repairBudget: 1 },
  });
  const result = await conductor.run();

  assert.equal(result.status, 'halted');
  assert.equal(conductor.state.halt.reason, 'REPAIR_BUDGET_EXHAUSTED');
  assert.equal(port.calls.length, 2, 'first attempt plus one repair, then stop');
  assert.equal(conductor.state.counters.repairs, 1);
});

test('an environment failure is terminal, not repairable', async () => {
  const base = createMemoryCraftPort({});
  let calls = 0;
  const throwingPort = {
    async execute() {
      calls += 1;
      throw new Error('ipc pipe closed');
    },
    inspect: (key) => base.inspect(key),
    snapshot: () => base.snapshot(),
  };
  const ports = {
    craft: throwingPort,
    approval: allowAllPolicy(),
    verify: createDocumentVerifier({ port: base }),
  };
  const conductor = new Conductor({ store: new MemoryStore(), ports, episodeId: 'ep-env', plan: PLANS.single });
  await conductor.open();
  const result = await conductor.run();

  assert.equal(result.status, 'halted');
  assert.equal(conductor.state.halt.reason, 'TERMINAL_ENVIRONMENT');
  assert.equal(calls, 1, 'an environment fault must not be retried');
  assert.equal(conductor.state.counters.repairs, 0);
});
