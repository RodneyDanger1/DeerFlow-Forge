/**
 * Command envelope: the only shape a Craft command may arrive in.
 *
 * Boundary validation lives here so every transport (in-app IPC, CLI, MCP) is
 * validated once, before any operation sees the request. The envelope is
 * deliberately transport-agnostic: the id encodes the family and command, and
 * the adapter resolves the transport later.
 */

import { createHash } from 'node:crypto';

/** Terminal/step statuses used across the adapter. */
export const STATUS = Object.freeze({
  OK: 'OK',
  SCHEMA_INVALID: 'SCHEMA_INVALID',
  PRECONDITION_UNMET: 'PRECONDITION_UNMET',
  NO_MATCH: 'NO_MATCH',
  TIMEOUT: 'TIMEOUT',
  ENVIRONMENT: 'ENVIRONMENT',
  DENIED: 'DENIED',
  UNVERIFIED: 'UNVERIFIED',
  AWAITING_HUMAN: 'AWAITING_HUMAN',
});

/**
 * Statuses the retry operation may repair. Everything else is terminal for the
 * step: a denial is a decision, not a fault, and an environment failure is not
 * something the model can fix by rephrasing.
 */
export const REPAIRABLE_STATUSES = Object.freeze(
  new Set([STATUS.SCHEMA_INVALID, STATUS.PRECONDITION_UNMET, STATUS.NO_MATCH, STATUS.TIMEOUT]),
);

/** Postcondition kinds the verifier knows how to decide. Unknown kinds become UNVERIFIED. */
export const POSTCONDITION_KINDS = Object.freeze(
  new Set(['layer-count', 'param-equals', 'artifact-exists', 'document-flag']),
);

/** Capability profiles projected onto command families. Wildcard is explicit, never implicit. */
export const CAPABILITY_PROFILES = Object.freeze({
  inspect: Object.freeze(['document']),
  edit: Object.freeze(['document', 'layer', 'shape', 'path', 'color']),
  export: Object.freeze(['document', 'export']),
  batch: Object.freeze(['*']),
});

const COMMAND_ID_PATTERN = /^craft:\/\/[a-z0-9][a-z0-9-]*\/[a-z0-9][a-z0-9-]*$/;
const PLAN_STEP_ID_PATTERN = /^[a-z0-9][a-z0-9-]{0,63}$/;

/** Raised for programmer errors, never for a command outcome. */
export class AdapterError extends Error {
  constructor(code, message, detail) {
    super(message);
    this.name = 'AdapterError';
    this.code = code;
    this.detail = detail ?? null;
  }
}

/** Canonical JSON: sorted keys, so digests are stable across processes and key order. */
export function stableStringify(value) {
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(stableStringify).join(',')}]`;
  const keys = Object.keys(value).sort();
  return `{${keys.map((k) => `${JSON.stringify(k)}:${stableStringify(value[k])}`).join(',')}}`;
}

/** Digest of any JSON-able value. Used for results and for the ledger hash chain. */
export function digest(value) {
  return createHash('sha256').update(stableStringify(value)).digest('hex');
}

/**
 * Idempotency key: a pure function of (episode, plan step). Stable across
 * retries and resumes by construction, which is what lets the dispatch
 * operation suppress a duplicate and lets the crash path reconcile.
 */
export function idempotencyKeyFor(episodeId, planStepId) {
  const h = createHash('sha256').update(`${episodeId}|${planStepId}`).digest('hex');
  return `idem_${h.slice(0, 24)}`;
}

function isPlainObject(value) {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function checkPostcondition(postcondition, index, errors) {
  const base = `postconditions[${index}]`;
  if (!isPlainObject(postcondition)) {
    errors.push({ code: 'E_POSTCONDITION_NOT_OBJECT', path: base });
    return;
  }
  if (!POSTCONDITION_KINDS.has(postcondition.kind)) {
    errors.push({ code: 'E_POSTCONDITION_KIND', path: `${base}.kind`, detail: String(postcondition.kind) });
    return;
  }
  switch (postcondition.kind) {
    case 'layer-count':
      if (!Number.isInteger(postcondition.equals) || postcondition.equals < 0) {
        errors.push({ code: 'E_POSTCONDITION_ASSERTION', path: `${base}.equals` });
      }
      break;
    case 'param-equals':
      if (typeof postcondition.path !== 'string' || postcondition.path.length === 0) {
        errors.push({ code: 'E_POSTCONDITION_ASSERTION', path: `${base}.path` });
      }
      if (!('value' in postcondition)) {
        errors.push({ code: 'E_POSTCONDITION_ASSERTION', path: `${base}.value` });
      }
      break;
    case 'artifact-exists':
      if (typeof postcondition.name !== 'string' || postcondition.name.length === 0) {
        errors.push({ code: 'E_POSTCONDITION_ASSERTION', path: `${base}.name` });
      }
      break;
    case 'document-flag':
      if (typeof postcondition.flag !== 'string' || postcondition.flag.length === 0) {
        errors.push({ code: 'E_POSTCONDITION_ASSERTION', path: `${base}.flag` });
      }
      if (typeof postcondition.equals !== 'boolean') {
        errors.push({ code: 'E_POSTCONDITION_ASSERTION', path: `${base}.equals` });
      }
      break;
    default:
      errors.push({ code: 'E_POSTCONDITION_KIND', path: `${base}.kind` });
  }
}

/**
 * Validate one dispatchable request.
 *
 * Returns `{ok, errors}`; never throws for bad input. `requireApproval` is a
 * plan-level fact, not a request-level fact, so it is validated by the plan
 * validator instead.
 */
export function validateCommandRequest(request) {
  const errors = [];
  if (!isPlainObject(request)) {
    return { ok: false, errors: [{ code: 'E_REQUEST_NOT_OBJECT', path: '' }] };
  }

  if (typeof request.commandId !== 'string' || !COMMAND_ID_PATTERN.test(request.commandId)) {
    errors.push({ code: 'E_COMMAND_ID', path: 'commandId', detail: String(request.commandId) });
  }
  if (typeof request.planStepId !== 'string' || !PLAN_STEP_ID_PATTERN.test(request.planStepId)) {
    errors.push({ code: 'E_PLAN_STEP_ID', path: 'planStepId', detail: String(request.planStepId) });
  }
  if (!isPlainObject(request.args)) {
    errors.push({ code: 'E_ARGS_NOT_OBJECT', path: 'args' });
  }
  if ('dryRun' in request && typeof request.dryRun !== 'boolean') {
    errors.push({ code: 'E_DRY_RUN_NOT_BOOLEAN', path: 'dryRun' });
  }
  if ('capabilityProfile' in request && !(request.capabilityProfile in CAPABILITY_PROFILES)) {
    errors.push({ code: 'E_CAPABILITY_PROFILE', path: 'capabilityProfile', detail: String(request.capabilityProfile) });
  }
  if ('postconditions' in request) {
    if (!Array.isArray(request.postconditions)) {
      errors.push({ code: 'E_POSTCONDITIONS_NOT_ARRAY', path: 'postconditions' });
    } else {
      request.postconditions.forEach((p, i) => checkPostcondition(p, i, errors));
    }
  }
  return { ok: errors.length === 0, errors };
}

/**
 * Capability check. A profile allows a set of families; `batch` allows all.
 * Kept here (not in the port) so every transport enforces the same projection.
 */
export function isAllowedByProfile(profile, commandId) {
  const families = CAPABILITY_PROFILES[profile];
  if (!families) return false;
  if (families.includes('*')) return true;
  const match = /^craft:\/\/([a-z0-9-]+)\//.exec(commandId);
  return match ? families.includes(match[1]) : false;
}

/** Validate a plan (ordered list of step descriptors) before an episode starts. */
export function validatePlan(plan) {
  if (!Array.isArray(plan) || plan.length === 0) {
    return { ok: false, errors: [{ code: 'E_PLAN_EMPTY', path: '' }] };
  }
  const errors = [];
  const seen = new Set();
  plan.forEach((step, index) => {
    const base = `[${index}]`;
    if (!isPlainObject(step)) {
      errors.push({ code: 'E_PLAN_STEP_NOT_OBJECT', path: base });
      return;
    }
    const requestResult = validateCommandRequest(step);
    if (!requestResult.ok) {
      for (const e of requestResult.errors) errors.push({ ...e, path: `${base}.${e.path}` });
    }
    if (seen.has(step.planStepId)) {
      errors.push({ code: 'E_PLAN_STEP_DUPLICATE', path: `${base}.planStepId` });
    }
    seen.add(step.planStepId);
    if ('requiresApproval' in step && typeof step.requiresApproval !== 'boolean') {
      errors.push({ code: 'E_REQUIRES_APPROVAL_NOT_BOOLEAN', path: `${base}.requiresApproval` });
    }
  });
  return { ok: errors.length === 0, errors };
}

/** Normalise a validated plan step into the request+flags the pipeline stores. */
export function toPlanEntry(step) {
  return {
    planStepId: step.planStepId,
    request: {
      commandId: step.commandId,
      planStepId: step.planStepId,
      args: step.args,
      dryRun: step.dryRun === true,
      capabilityProfile: step.capabilityProfile ?? 'edit',
      postconditions: step.postconditions ?? [],
    },
    requiresApproval: step.requiresApproval === true,
    status: 'pending',
    attempts: 0,
  };
}
