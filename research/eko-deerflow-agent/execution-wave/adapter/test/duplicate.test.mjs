/**
 * Duplicate suppression.
 *
 * The idempotency key is a pure function of (episode, plan step). A step that is
 * replayed — by an operator, by a resumed run, or by a duplicate event — must
 * read the recorded outcome instead of touching the app again.
 */

import assert from 'node:assert/strict';
import test from 'node:test';

import { idempotencyKeyFor } from '../src/envelope.mjs';
import { Conductor } from '../src/machine.mjs';
import { PLANS, makeConductor } from './fixtures/harness.mjs';

test('replaying a completed step is suppressed and does not re-execute', async () => {
  const { conductor, ports, store, port } = await makeConductor({ plan: PLANS.happy, episodeId: 'ep-dup' });
  await conductor.run();
  assert.equal(port.calls.length, 2);

  // Simulate an operator re-queueing step 1 after a completed episode (for
  // example after an ambiguous UI report). The ledger must catch it.
  const draft = structuredClone(conductor.state);
  draft.plan[0].status = 'pending';
  draft.plan[0].verified = false;
  draft.finished = false;
  draft.finishedAt = null;
  store.commit(draft);

  const resumed = new Conductor({ store, ports, episodeId: 'ep-dup', plan: PLANS.happy });
  await resumed.open();
  const result = await resumed.run();

  assert.equal(result.status, 'finished');
  assert.equal(resumed.state.counters.duplicates, 1);
  assert.equal(port.calls.length, 2, 'the duplicate must not reach the app');
  assert.equal(resumed.state.ledgerEntries.length, 2, 'no new ledger entry for the duplicate');

  const duplicate = resumed.state.events.find((event) => event.kind === 'duplicate_suppressed');
  assert.ok(duplicate, 'a duplicate_suppressed event must be recorded');
  assert.equal(duplicate.payload.status, 'OK');
  assert.equal(duplicate.payload.idempotencyKey, idempotencyKeyFor('ep-dup', 'add-layer'));
  assert.equal(resumed.state.plan[0].status, 'ok');
});

test('duplicate suppression keeps a failed outcome failed and does not re-run it', async () => {
  const { conductor, ports, store, port } = await makeConductor({
    plan: PLANS.single,
    episodeId: 'ep-dup-fail',
    craft: {},
  });
  await conductor.run();
  assert.equal(port.calls.length, 1);
  assert.equal(conductor.state.ledgerEntries.length, 1);

  // Make the recorded outcome terminal-but-failed, as an environment failure
  // would be, then replay the step.
  const draft = structuredClone(conductor.state);
  draft.ledgerEntries[0].status = 'ENVIRONMENT';
  draft.plan[0].status = 'pending';
  draft.plan[0].verified = false;
  draft.finished = false;
  draft.finishedAt = null;
  store.commit(draft);

  const resumed = new Conductor({ store, ports, episodeId: 'ep-dup-fail', plan: PLANS.single });
  await resumed.open();
  const result = await resumed.run();

  assert.equal(result.status, 'halted');
  assert.equal(resumed.state.halt.reason, 'TERMINAL_ENVIRONMENT');
  assert.equal(resumed.state.counters.duplicates, 1);
  assert.equal(port.calls.length, 1, 'a terminal failed outcome must not be re-executed');
});

test('idempotency keys are independent per episode', async () => {
  const first = await makeConductor({ plan: PLANS.single, episodeId: 'ep-a' });
  const second = await makeConductor({ plan: PLANS.single, episodeId: 'ep-b' });
  await first.conductor.run();
  await second.conductor.run();

  const keyA = first.port.calls[0].idempotencyKey;
  const keyB = second.port.calls[0].idempotencyKey;
  assert.notEqual(keyA, keyB);
  assert.equal(keyA, idempotencyKeyFor('ep-a', 'add-layer'));
  assert.equal(keyB, idempotencyKeyFor('ep-b', 'add-layer'));
});
