/**
 * Ports the pipeline talks to.
 *
 * The pipeline itself never knows how Craft is reached, who approves, or how a
 * screenshot is judged. Everything external is a port; the doubles in this file
 * are reference implementations for tests and for embedding, not production
 * bindings. Production wiring replaces the Craft port with the real command
 * transport and the summarizer with a model call — see 06-ADAPTER.md §6.
 */

import { STATUS } from './envelope.mjs';

/* ------------------------------------------------------------------ *
 * Craft port: the app boundary.
 *
 * Contract:
 *   execute({commandId, args, idempotencyKey, dryRun, capabilityProfile})
 *     -> {status, observation, undoToken?, artifacts?}
 *   inspect(idempotencyKey) -> {known: boolean, status?: string}
 *   snapshot() -> {layers: string[], artifacts: string[], params: object, flags: object}
 *
 * `inspect` is what makes crash recovery possible without guessing: after a
 * process dies between "we asked Craft" and "we recorded the answer", the
 * pipeline asks Craft what happened instead of firing the command again.
 * ------------------------------------------------------------------ */

export function createMemoryCraftPort({ plannedFailures = [], initialDocument = {}, now = () => new Date().toISOString() } = {}) {
  const document = {
    layers: structuredClone(initialDocument.layers ?? []),
    artifacts: structuredClone(initialDocument.artifacts ?? []),
    params: structuredClone(initialDocument.params ?? {}),
    flags: structuredClone(initialDocument.flags ?? {}),
  };
  const results = new Map();
  const calls = [];
  const failures = [...plannedFailures];
  let observation = '';

  function finish(commandId, key, outcome) {
    results.set(key, { status: outcome.status, observation: outcome.observation ?? '', commandId });
    observation = outcome.observation ?? '';
    return { ...outcome, undoToken: outcome.undoToken ?? `undo_${key}` };
  }

  function applyCommand(commandId, args) {
    switch (commandId) {
      case 'craft://document/add-layer': {
        const name = String(args.name ?? '');
        if (name === '') return { status: STATUS.SCHEMA_INVALID, observation: 'add-layer requires args.name' };
        if (document.layers.includes(name)) {
          return { status: STATUS.PRECONDITION_UNMET, observation: `layer "${name}" already exists` };
        }
        document.layers.push(name);
        document.flags.unsaved = true;
        return { status: STATUS.OK, observation: `added layer ${name}` };
      }
      case 'craft://layer/set-param': {
        const layer = String(args.layer ?? '');
        const path = String(args.path ?? '');
        if (layer === '' || path === '') {
          return { status: STATUS.SCHEMA_INVALID, observation: 'set-param requires args.layer and args.path' };
        }
        if (!document.layers.includes(layer)) {
          return { status: STATUS.NO_MATCH, observation: `layer "${layer}" not found` };
        }
        document.params[layer] = { ...(document.params[layer] ?? {}), [path]: args.value };
        document.flags.unsaved = true;
        return { status: STATUS.OK, observation: `set ${layer}.${path}` };
      }
      case 'craft://document/export': {
        const name = String(args.name ?? 'export');
        if (document.layers.length === 0) {
          return { status: STATUS.PRECONDITION_UNMET, observation: 'nothing to export' };
        }
        document.artifacts.push(name);
        document.flags.exported = true;
        return { status: STATUS.OK, observation: `exported ${name}`, artifacts: [name] };
      }
      default:
        return { status: STATUS.NO_MATCH, observation: `unknown command ${commandId}` };
    }
  }

  return {
    calls,
    document,
    async execute({ commandId, args, idempotencyKey, dryRun = false }) {
      calls.push({ commandId, idempotencyKey, args: structuredClone(args), dryRun, at: now() });
      if (dryRun) return finish(commandId, idempotencyKey, { status: STATUS.OK, observation: 'dry run: no change' });
      const planned = failures.shift();
      if (planned) return finish(commandId, idempotencyKey, { status: planned, observation: `planned ${planned}` });
      return finish(commandId, idempotencyKey, applyCommand(commandId, args));
    },
    inspect(idempotencyKey) {
      const known = results.get(idempotencyKey);
      return known ? { known: true, status: known.status } : { known: false };
    },
    snapshot() {
      return structuredClone(document);
    },
    lastObservation() {
      return observation;
    },
  };
}

/* ------------------------------------------------------------------ *
 * Approval policy.
 *
 * decide({request, planStep}) -> {decision: 'allow'|'deny'|'require_human', reason}
 *
 * 'require_human' must never block the pipeline: the operation records the
 * request and yields, and an operator (or a queue) records the decision later.
 * ------------------------------------------------------------------ */

export function allowAllPolicy() {
  return { async decide() { return { decision: 'allow', reason: 'allow-all policy' }; } };
}

export function denyAllPolicy(reason = 'denied by policy') {
  return { async decide() { return { decision: 'deny', reason }; } };
}

export function requireHumanPolicy(reason = 'destructive command requires a human') {
  return { async decide() { return { decision: 'require_human', reason }; } };
}

/** Scripted policy: decisions are consumed in call order, then falls back. */
export function scriptedPolicy(decisions, fallback = { decision: 'allow', reason: 'script exhausted' }) {
  const queue = [...decisions];
  return {
    async decide() {
      const next = queue.shift();
      return next ?? fallback;
    },
  };
}

/* ------------------------------------------------------------------ *
 * Verifier.
 *
 * check(postconditions, {snapshot}) -> [{kind, holds: boolean|null, label, evidence}]
 *
 * `holds: null` means "not decidable here" and maps to UNVERIFIED. It is never
 * coerced to true. `label` uses the audit vocabulary: V = checked and holds,
 * U = could not be checked.
 * ------------------------------------------------------------------ */

export function evaluatePostcondition(postcondition, snapshot) {
  switch (postcondition.kind) {
    case 'layer-count': {
      const count = snapshot.layers.length;
      return { kind: postcondition.kind, holds: count === postcondition.equals, label: 'V', evidence: { count, expected: postcondition.equals } };
    }
    case 'param-equals': {
      const [layer, ...rest] = String(postcondition.path).split('.');
      const path = rest.join('.');
      const actual = snapshot.params?.[layer]?.[path];
      const holds = Object.is(actual, postcondition.value);
      return { kind: postcondition.kind, holds, label: 'V', evidence: { path: postcondition.path, actual, expected: postcondition.value } };
    }
    case 'artifact-exists': {
      const holds = snapshot.artifacts.includes(postcondition.name);
      return { kind: postcondition.kind, holds, label: 'V', evidence: { artifacts: snapshot.artifacts, expected: postcondition.name } };
    }
    case 'document-flag': {
      const actual = Boolean(snapshot.flags?.[postcondition.flag]);
      const holds = actual === postcondition.equals;
      return { kind: postcondition.kind, holds, label: 'V', evidence: { flag: postcondition.flag, actual, expected: postcondition.equals } };
    }
    default:
      return { kind: String(postcondition.kind), holds: null, label: 'U', evidence: { reason: 'NOT_DECIDABLE' } };
  }
}

export function createDocumentVerifier({ port }) {
  return {
    async check(postconditions) {
      const snapshot = port.snapshot();
      return postconditions.map((p) => evaluatePostcondition(p, snapshot));
    },
  };
}

/* ------------------------------------------------------------------ *
 * Summarizer: compaction note.
 *
 * Deterministic stand-in for a model-written continuation note. It reports the
 * goal, what was completed, what is outstanding, and the verification status,
 * and it never claims more than the events contain.
 * ------------------------------------------------------------------ */

export function buildContinuationNote(events, { episodeId = 'unknown' } = {}) {
  const completed = events.filter((e) => e.kind === 'command_result' && e.payload?.status === STATUS.OK);
  const failed = events.filter((e) => e.kind === 'command_result' && e.payload?.status !== STATUS.OK);
  const verified = events.filter((e) => e.kind === 'verification' && e.payload?.holds === true);
  const unverified = events.filter((e) => e.kind === 'verification' && e.payload?.holds !== true);
  const repairs = events.filter((e) => e.kind === 'repair_scheduled');
  const lines = [
    `Goal: continue Craft episode ${episodeId}.`,
    `Completed commands: ${completed.length === 0 ? 'none' : completed.map((e) => e.payload.commandId).join(', ')}.`,
    `Failed commands: ${failed.length === 0 ? 'none' : failed.map((e) => `${e.payload.commandId} (${e.payload.status})`).join(', ')}.`,
    `Verification: ${verified.length} checked-holds, ${unverified.length} not-holds-or-unknown.`,
    `Repairs scheduled: ${repairs.length}.`,
    'Facts above are derived from the event log; anything not listed is UNVERIFIED.',
  ];
  return lines.join('\n');
}
