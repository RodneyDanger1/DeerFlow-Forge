/**
 * The Craft adapter: wires the pipeline to concrete ports and the plan.
 *
 * This is the file production replaces. Everything Craft-specific — command
 * transport, approval queue, document verifier — is injected here, so the
 * pipeline stays testable and the app boundary stays a single seam.
 */

import { AdapterError, validatePlan } from './envelope.mjs';
import { Conductor } from './machine.mjs';
import { OPERATION_ORDER } from './operations.mjs';
import { createDocumentVerifier, allowAllPolicy } from './ports.mjs';

/** Operation names in evaluation order, imported from the implementation so docs cannot drift. */
export const PIPELINE = OPERATION_ORDER;

function assertPort(port, name, methods) {
  if (!port || typeof port !== 'object') throw new AdapterError('E_PORT_MISSING', `${name} port is required`);
  for (const method of methods) {
    if (typeof port[method] !== 'function') throw new AdapterError('E_PORT_MISSING', `${name} port is missing ${method}()`);
  }
  return port;
}

/**
 * Build a Conductor for one Craft episode.
 *
 * @param {object} options
 * @param {{load: Function, commit: Function}} options.store  MemoryStore or FileStore
 * @param {object} options.craftPort   execute/inspect/snapshot; production = Craft IPC/CLI/MCP transport
 * @param {object} [options.approvalPolicy]  decide() -> allow|deny|require_human
 * @param {object} [options.verifier]  check(postconditions) -> rows; defaults to document verifier
 * @param {Array} options.plan  ordered step descriptors validated before the episode starts
 * @param {string} options.episodeId
 */
export function createCraftConductor({
  store,
  craftPort,
  approvalPolicy = allowAllPolicy(),
  verifier = null,
  plan,
  episodeId,
  writerId = 'forge-conductor',
  config = {},
  hooks = {},
  now,
}) {
  assertPort(craftPort, 'craft', ['execute', 'inspect', 'snapshot']);
  assertPort(approvalPolicy, 'approval', ['decide']);
  const resolvedVerifier = verifier ?? createDocumentVerifier({ port: craftPort });
  assertPort(resolvedVerifier, 'verify', ['check']);

  const validated = validatePlan(plan);
  if (!validated.ok) {
    throw new AdapterError('E_PLAN_INVALID', 'plan failed validation', validated.errors);
  }

  return new Conductor({
    store,
    ports: { craft: craftPort, approval: approvalPolicy, verify: resolvedVerifier },
    episodeId,
    writerId,
    plan,
    config,
    hooks,
    now,
  });
}

/** One-line summary of a finished run, for logs and for the adapter report. */
export function summarizeRun(result) {
  const { status, state } = result;
  return {
    status,
    episodeId: state.episodeId,
    steps: state.plan.length,
    ledgerEntries: state.ledgerEntries.length,
    duplicates: state.counters.duplicates,
    repairs: state.counters.repairs,
    compactions: state.counters.compactions,
    checkpoints: state.counters.checkpoints,
    events: state.events.length,
    halt: state.halt,
    finished: state.finished,
  };
}
