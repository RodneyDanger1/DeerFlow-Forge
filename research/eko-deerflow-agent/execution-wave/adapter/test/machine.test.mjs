/**
 * Pipeline mechanics: happy path, re-entrancy, event integrity, checkpoint
 * hash chain, and the finalize refusal for unverified evidence.
 */

import assert from 'node:assert/strict';
import test from 'node:test';

import { Conductor } from '../src/machine.mjs';
import { createOperations } from '../src/operations.mjs';
import { denyAllPolicy } from '../src/ports.mjs';
import { PLANS, eventKinds, makeConductor } from './fixtures/harness.mjs';

test('happy path: two commands, verified, finished', async () => {
  const { conductor, port } = await makeConductor({ plan: PLANS.happy });
  const result = await conductor.run();

  assert.equal(result.status, 'finished');
  assert.equal(conductor.state.finished, true);
  assert.equal(conductor.state.ledgerEntries.length, 2);
  assert.equal(port.calls.length, 2);
  assert.deepEqual(port.document.layers, ['Ink']);
  assert.deepEqual(port.document.artifacts, ['final.png']);

  const kinds = eventKinds(conductor);
  assert.equal(kinds[0], 'episode_started');
  assert.equal(kinds.at(-1), 'episode_finished');
  assert.equal(kinds.filter((k) => k === 'command_result').length, 2);
  assert.equal(kinds.filter((k) => k === 'verification').length, 2);
  assert.equal(conductor.state.evidence.every((row) => row.label === 'V' && row.holds === true), true);
});

test('event sequence is contiguous and every step advances the cursor', async () => {
  const { conductor } = await makeConductor({ plan: PLANS.happy });
  await conductor.run();
  conductor.state.events.forEach((event, index) => {
    assert.equal(event.seq, index + 1, 'event seq must be contiguous');
    assert.ok(event.op.length > 0);
    assert.ok(event.kind.length > 0);
    assert.ok(typeof event.at === 'string');
  });
  assert.equal(conductor.state.cursor.seq, conductor.state.events.length);
});

test('running a finished episode again is a no-op', async () => {
  const { conductor, port } = await makeConductor({ plan: PLANS.happy });
  await conductor.run();
  const eventsAfterFirst = conductor.state.events.length;
  const callsAfterFirst = port.calls.length;

  const second = await conductor.run();
  assert.equal(second.status, 'finished');
  assert.equal(conductor.state.events.length, eventsAfterFirst);
  assert.equal(port.calls.length, callsAfterFirst);
});

test('checkpoints form a hash chain', async () => {
  const { conductor } = await makeConductor({
    plan: PLANS.happy,
    config: { checkpointEveryEvents: 2 },
  });
  await conductor.run();

  const checkpoints = conductor.state.events.filter((event) => event.kind === 'checkpoint');
  assert.ok(checkpoints.length >= 2, `expected >=2 checkpoints, got ${checkpoints.length}`);
  assert.equal(checkpoints[0].payload.prevHash, null);
  for (let i = 1; i < checkpoints.length; i += 1) {
    assert.equal(checkpoints[i].payload.prevHash, checkpoints[i - 1].payload.hash, 'checkpoint chain must link');
  }
  assert.equal(conductor.state.lastCheckpointHash, checkpoints.at(-1).payload.hash);
});

test('finalize refuses to close an episode on unverified evidence', async () => {
  const { conductor, ports, store } = await makeConductor({ plan: PLANS.happy });

  // Craft a state where a step claims success but carries no verified evidence.
  const draft = structuredClone(conductor.state);
  draft.plan[0].status = 'ok';
  draft.plan[0].verified = false;
  draft.plan[1].status = 'ok';
  draft.plan[1].verified = true;
  store.commit(draft);

  const finalizeOnly = createOperations({ ports }).filter((op) => op.name === 'finalize');
  const blocked = new Conductor({ store, ports, episodeId: 'ep-test', plan: PLANS.happy, operations: finalizeOnly });
  await blocked.open();
  const result = await blocked.run();

  assert.equal(result.status, 'awaiting_evidence');
  assert.equal(blocked.state.finished, false);
  assert.equal(blocked.state.events.at(-1).kind, 'awaiting_evidence');
  assert.deepEqual(blocked.state.events.at(-1).payload.steps, ['add-layer']);
});

test('a halted episode does not advance on further runs', async () => {
  const { conductor, port } = await makeConductor({
    plan: [{ ...PLANS.single[0], requiresApproval: true }],
    approval: denyAllPolicy('test denial'),
  });

  const first = await conductor.run();
  assert.equal(first.status, 'halted');
  assert.equal(conductor.state.halt.reason, 'DENIED_BY_POLICY');
  const eventsAtHalt = conductor.state.events.length;

  const second = await conductor.run();
  assert.equal(second.status, 'halted');
  assert.equal(conductor.state.events.length, eventsAtHalt, 'a halted episode must not append events');
  assert.equal(port.calls.length, 0, 'a denied command must never reach the app');
});
