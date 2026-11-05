/**
 * Crash and resume tests.
 *
 * The child process is killed for real (exit 9) after the app applied its
 * effect but before the pipeline recorded the outcome. The parent then proves:
 *  - the write-ahead intent survived,
 *  - resume reconciles instead of re-executing,
 *  - the episode can finish from the reconciled state,
 *  - an unresolvable intent halts instead of guessing,
 *  - a schema mismatch refuses to load.
 */

import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

import { idempotencyKeyFor, toPlanEntry } from '../src/envelope.mjs';
import { Conductor } from '../src/machine.mjs';
import { allowAllPolicy, createDocumentVerifier } from '../src/ports.mjs';
import { FileStore, createInitialSession } from '../src/store.mjs';
import { FileCraftPort } from './fixtures/file-craft-port.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const childPath = join(here, 'fixtures', 'crash-child.mjs');

const PLAN = [
  {
    planStepId: 'add-layer',
    commandId: 'craft://document/add-layer',
    args: { name: 'Ink' },
    capabilityProfile: 'edit',
    postconditions: [{ kind: 'layer-count', equals: 1 }],
  },
];

function buildResumer(directory, episodeId, plan = PLAN) {
  const port = new FileCraftPort(directory);
  const conductor = new Conductor({
    store: new FileStore(directory),
    ports: {
      craft: port,
      approval: allowAllPolicy(),
      verify: createDocumentVerifier({ port }),
    },
    episodeId,
    plan,
  });
  return { conductor, port };
}

test('crash after the effect: resume reconciles by inspect and never re-executes', async () => {
  const directory = mkdtempSync(join(tmpdir(), 'forge-crash-'));
  try {
    const child = spawnSync(process.execPath, [childPath, directory], { encoding: 'utf8', timeout: 30_000 });
    assert.equal(child.status, 9, `child must die mid-step; stderr=${child.stderr ?? ''}`);

    const session = JSON.parse(readFileSync(join(directory, 'session.json'), 'utf8'));
    assert.equal(session.inFlight.length, 1, 'write-ahead intent must survive the crash');
    assert.equal(session.ledgerEntries.length, 0, 'no result may be recorded before the crash');
    assert.equal(session.plan[0].status, 'pending');
    assert.equal(session.finished, false);

    const crashedPort = new FileCraftPort(directory);
    assert.equal(crashedPort.countCalls(), 1);
    assert.equal(crashedPort.countEffects(), 1);

    const { conductor, port } = buildResumer(directory, 'ep-crash');
    await conductor.open();
    const result = await conductor.run();

    assert.equal(result.status, 'finished');
    assert.equal(conductor.state.finished, true);
    assert.equal(conductor.state.inFlight.length, 0, 'resume must clear the intent');
    assert.equal(conductor.state.ledgerEntries.length, 1);
    assert.equal(conductor.state.ledgerEntries[0].reconciledVia, 'inspect');
    assert.equal(conductor.state.ledgerEntries[0].status, 'OK');
    assert.equal(conductor.state.plan[0].status, 'ok');

    const reconciled = conductor.state.events.find((event) => event.kind === 'reconciled');
    assert.ok(reconciled, 'resume must emit a reconciled event');
    assert.equal(reconciled.payload.via, 'inspect');
    assert.equal(conductor.state.counters.duplicates, 0);

    assert.equal(port.countCalls(), 1, 'the command must not be executed twice');
    assert.equal(port.countEffects(), 1, 'the effect must not be applied twice');
    assert.deepEqual(port.readDocument().layers, ['Ink']);

    const journal = readFileSync(join(directory, 'journal.jsonl'), 'utf8').trim().split('\n');
    assert.ok(journal.length >= 2, 'journal must record both the crashed and the resumed commit');
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});

test('unresolvable intent halts with MANUAL_RECONCILE instead of guessing', async () => {
  const directory = mkdtempSync(join(tmpdir(), 'forge-manual-'));
  try {
    const { conductor } = buildResumer(directory, 'ep-manual');
    await conductor.open();

    // Simulate a process that wrote the intent and died before calling Craft:
    // the app has no effect for this key and the document does not satisfy the
    // declared postcondition.
    const draft = structuredClone(conductor.state);
    draft.inFlight.push({
      idempotencyKey: idempotencyKeyFor('ep-manual', 'add-layer'),
      planStepId: 'add-layer',
      commandId: 'craft://document/add-layer',
      attempt: 1,
      startedAt: new Date().toISOString(),
    });
    conductor.store.commit(draft);

    const resumed = buildResumer(directory, 'ep-manual');
    await resumed.conductor.open();
    const result = await resumed.conductor.run();

    assert.equal(result.status, 'halted');
    assert.equal(resumed.conductor.state.halt.reason, 'MANUAL_RECONCILE');
    assert.equal(resumed.conductor.state.finished, false);
    assert.equal(resumed.port.countCalls(), 0, 'an unknown outcome must not be replayed');
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});

test('when the app cannot answer, declared postconditions decide the recovery', async () => {
  const directory = mkdtempSync(join(tmpdir(), 'forge-verify-recover-'));
  try {
    // A crashed session plus a document that shows the effect happened, while
    // the effects log is gone (the app cannot answer for the key at all).
    const setup = buildResumer(directory, 'ep-verify');
    await setup.conductor.open();
    setup.port.writeDocument({ layers: ['Ink'], artifacts: [], params: {}, flags: { unsaved: true } });
    const draft = structuredClone(setup.conductor.state);
    draft.inFlight.push({
      idempotencyKey: idempotencyKeyFor('ep-verify', 'add-layer'),
      planStepId: 'add-layer',
      commandId: 'craft://document/add-layer',
      attempt: 1,
      startedAt: new Date().toISOString(),
    });
    setup.conductor.store.commit(draft);

    const filePort = new FileCraftPort(directory);
    const forgetfulPort = {
      execute: (request) => filePort.execute(request),
      inspect: () => ({ known: false }),
      snapshot: () => filePort.snapshot(),
    };
    const resumed = new Conductor({
      store: new FileStore(directory),
      ports: {
        craft: forgetfulPort,
        approval: allowAllPolicy(),
        verify: createDocumentVerifier({ port: filePort }),
      },
      episodeId: 'ep-verify',
      plan: PLAN,
    });
    await resumed.open();
    const result = await resumed.run();

    assert.equal(result.status, 'finished');
    assert.equal(resumed.state.ledgerEntries[0].reconciledVia, 'verification');
    assert.equal(resumed.state.ledgerEntries[0].status, 'OK');
    assert.equal(filePort.countCalls(), 0, 'verification-based recovery must not re-execute');
    assert.equal(resumed.state.evidence.some((row) => row.source === 'reconcile'), true);
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});

test('schema mismatch fails closed on load', () => {
  const directory = mkdtempSync(join(tmpdir(), 'forge-schema-'));
  try {
    const session = createInitialSession({
      episodeId: 'ep-schema',
      writerId: 'forge-conductor',
      plan: [toPlanEntry(PLAN[0])],
    });
    writeFileSync(join(directory, 'session.json'), JSON.stringify({ ...session, schemaVersion: 99 }), 'utf8');
    const store = new FileStore(directory);
    assert.throws(() => store.load(), (error) => error.code === 'E_SCHEMA_MISMATCH');
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});

test('corrupt session file fails closed on load', () => {
  const directory = mkdtempSync(join(tmpdir(), 'forge-corrupt-'));
  try {
    writeFileSync(join(directory, 'session.json'), '{"schemaVersion":1,', 'utf8');
    const store = new FileStore(directory);
    assert.throws(() => store.load(), (error) => error.code === 'E_CORRUPT');
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});

test('an existing session for another episode is refused', async () => {
  const directory = mkdtempSync(join(tmpdir(), 'forge-episode-'));
  try {
    const first = buildResumer(directory, 'ep-one');
    await first.conductor.open();
    const second = buildResumer(directory, 'ep-two');
    await assert.rejects(() => second.conductor.open(), (error) => error.code === 'E_EPISODE_MISMATCH');
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});
