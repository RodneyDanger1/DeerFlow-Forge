/**
 * Envelope and plan validation: the boundary that decides what may even reach
 * the pipeline. These are pure functions, so the tests are exhaustive cheaply.
 */

import assert from 'node:assert/strict';
import test from 'node:test';

import {
  CAPABILITY_PROFILES,
  REPAIRABLE_STATUSES,
  STATUS,
  digest,
  idempotencyKeyFor,
  isAllowedByProfile,
  stableStringify,
  validateCommandRequest,
  validatePlan,
} from '../src/envelope.mjs';

const VALID = {
  planStepId: 'add-layer',
  commandId: 'craft://document/add-layer',
  args: { name: 'Ink' },
  capabilityProfile: 'edit',
  postconditions: [{ kind: 'layer-count', equals: 1 }],
};

test('a well-formed request validates', () => {
  const result = validateCommandRequest(VALID);
  assert.equal(result.ok, true, JSON.stringify(result.errors));
  assert.deepEqual(result.errors, []);
});

test('malformed requests are rejected at the boundary', () => {
  assert.equal(validateCommandRequest(null).errors[0].code, 'E_REQUEST_NOT_OBJECT');
  assert.equal(validateCommandRequest({ ...VALID, commandId: 'document/add-layer' }).errors[0].code, 'E_COMMAND_ID');
  assert.equal(validateCommandRequest({ ...VALID, commandId: 'craft://Document/Add' }).errors[0].code, 'E_COMMAND_ID');
  assert.equal(validateCommandRequest({ ...VALID, planStepId: 'Add_Layer' }).errors[0].code, 'E_PLAN_STEP_ID');
  assert.equal(validateCommandRequest({ ...VALID, args: null }).errors[0].code, 'E_ARGS_NOT_OBJECT');
  assert.equal(validateCommandRequest({ ...VALID, dryRun: 'yes' }).errors[0].code, 'E_DRY_RUN_NOT_BOOLEAN');
  assert.equal(validateCommandRequest({ ...VALID, capabilityProfile: 'root' }).errors[0].code, 'E_CAPABILITY_PROFILE');
});

test('postcondition kinds are a closed set with validated assertions', () => {
  const unknown = validateCommandRequest({ ...VALID, postconditions: [{ kind: 'pixel-diff' }] });
  assert.equal(unknown.ok, false);
  assert.ok(unknown.errors.some((e) => e.code === 'E_POSTCONDITION_KIND'));

  const badCount = validateCommandRequest({ ...VALID, postconditions: [{ kind: 'layer-count', equals: -1 }] });
  assert.ok(badCount.errors.some((e) => e.code === 'E_POSTCONDITION_ASSERTION'));

  const missingFlag = validateCommandRequest({ ...VALID, postconditions: [{ kind: 'document-flag', flag: 'exported' }] });
  assert.ok(missingFlag.errors.some((e) => e.code === 'E_POSTCONDITION_ASSERTION'));

  const notArray = validateCommandRequest({ ...VALID, postconditions: { kind: 'layer-count' } });
  assert.ok(notArray.errors.some((e) => e.code === 'E_POSTCONDITIONS_NOT_ARRAY'));
});

test('capability profiles project command families and deny by default', () => {
  assert.equal(isAllowedByProfile('inspect', 'craft://document/add-layer'), true);
  assert.equal(isAllowedByProfile('inspect', 'craft://export/png'), false);
  assert.equal(isAllowedByProfile('export', 'craft://document/export'), true);
  assert.equal(isAllowedByProfile('batch', 'craft://export/png'), true);
  assert.equal(isAllowedByProfile('does-not-exist', 'craft://document/add-layer'), false);
  assert.deepEqual(CAPABILITY_PROFILES.inspect, ['document']);
});

test('idempotency keys are stable, deterministic and episode-scoped', () => {
  const a = idempotencyKeyFor('ep-1', 'add-layer');
  const b = idempotencyKeyFor('ep-1', 'add-layer');
  const otherEpisode = idempotencyKeyFor('ep-2', 'add-layer');
  const otherStep = idempotencyKeyFor('ep-1', 'export-png');
  assert.equal(a, b);
  assert.notEqual(a, otherEpisode);
  assert.notEqual(a, otherStep);
  assert.match(a, /^idem_[0-9a-f]{24}$/);
});

test('plan validation rejects empty plans, duplicate step ids and nested request faults', () => {
  assert.equal(validatePlan([]).errors[0].code, 'E_PLAN_EMPTY');
  assert.equal(validatePlan('nope').errors[0].code, 'E_PLAN_EMPTY');

  const duplicate = validatePlan([VALID, { ...VALID }]);
  assert.ok(duplicate.errors.some((e) => e.code === 'E_PLAN_STEP_DUPLICATE'));

  const badStep = validatePlan([{ ...VALID, commandId: 'nope' }]);
  assert.ok(badStep.errors.some((e) => e.code === 'E_COMMAND_ID' && e.path.startsWith('[0].')));
});

test('digests are independent of key order and sensitive to values', () => {
  const left = { a: 1, b: { c: 2, d: [3, 4] } };
  const right = { b: { d: [3, 4], c: 2 }, a: 1 };
  assert.equal(stableStringify(left), stableStringify(right));
  assert.equal(digest(left), digest(right));
  assert.notEqual(digest(left), digest({ ...left, a: 2 }));
});

test('only transport-ish faults are repairable', () => {
  for (const status of [STATUS.SCHEMA_INVALID, STATUS.PRECONDITION_UNMET, STATUS.NO_MATCH, STATUS.TIMEOUT]) {
    assert.equal(REPAIRABLE_STATUSES.has(status), true, status);
  }
  for (const status of [STATUS.OK, STATUS.DENIED, STATUS.ENVIRONMENT, STATUS.UNVERIFIED]) {
    assert.equal(REPAIRABLE_STATUSES.has(status), false, status);
  }
  assert.equal(Object.isFrozen(STATUS), true);
});
