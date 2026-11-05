/**
 * The ordered operation pipeline.
 *
 * One step = the first *applicable* operation in this list. Operations mutate a
 * draft and return an outcome; the machine appends exactly one event, commits,
 * and re-enters. Policies (approval, repair, compaction) are operations, not
 * branches buried inside a dispatch function, which is what makes the pipeline
 * re-entrant after a crash or a human decision.
 *
 * Order is a safety property, not a style choice:
 *   reconcile  — never dispatch while an unknown outcome is outstanding
 *   approval   — decide before planning a side effect
 *   retry      — repair or stop before dispatching again
 *   compaction — shrink the view before spending tokens on a new step
 *   checkpoint — hash-chain the progress for audit
 *   verify     — check the last effect before starting the next one
 *   dispatch   — the only operation with an external side effect
 *   finalize   — refuse to finish on unverified evidence
 */

import { STATUS, REPAIRABLE_STATUSES, digest, idempotencyKeyFor, isAllowedByProfile, validateCommandRequest } from './envelope.mjs';
import { buildContinuationNote } from './ports.mjs';

const ESTIMATE_CHARS_PER_TOKEN = 4;

function clone(value) {
  return structuredClone(value);
}

function planStepById(state, planStepId) {
  return state.plan.find((s) => s.planStepId === planStepId) ?? null;
}

function pendingStep(state) {
  return state.plan.find((s) => s.status === 'pending') ?? null;
}

function failedStep(state) {
  return state.plan.find((s) => s.status === 'failed') ?? null;
}

function lastLedgerEntry(state, key) {
  for (let i = state.ledgerEntries.length - 1; i >= 0; i -= 1) {
    if (state.ledgerEntries[i].idempotencyKey === key) return state.ledgerEntries[i];
  }
  return null;
}

function lastResultEvent(state, planStepId) {
  for (let i = state.events.length - 1; i >= 0; i -= 1) {
    const event = state.events[i];
    if (event.kind === 'command_result' && event.payload?.planStepId === planStepId) return event;
  }
  return null;
}

function evidenceFor(state, planStepId) {
  return state.evidence.filter((row) => row.planStepId === planStepId);
}

/** Estimated tokens of the un-compacted tail, plus the current note. */
export function estimateTailTokens(state) {
  let chars = (state.compaction?.lastNote?.length ?? 0) || 0;
  for (const event of state.events) {
    if (event.seq <= (state.compaction?.consumedSeq ?? 0)) continue;
    chars += JSON.stringify(event).length;
  }
  return Math.ceil(chars / ESTIMATE_CHARS_PER_TOKEN);
}

function recordFailure(state, step, status, feedback) {
  step.status = 'failed';
  step.lastFeedback = { status, feedback: String(feedback ?? '') };
  state.counters.failures += 1;
}

function closeIntent(state, idempotencyKey) {
  state.inFlight = state.inFlight.filter((i) => i.idempotencyKey !== idempotencyKey);
}

function recordResult(state, { planStepId, commandId, idempotencyKey, status, observation, undoToken, reconciledVia }) {
  const step = planStepById(state, planStepId);
  state.ledgerEntries.push({
    idempotencyKey,
    planStepId,
    commandId,
    status,
    observation: String(observation ?? ''),
    undoToken: undoToken ?? null,
    reconciledVia: reconciledVia ?? null,
    at: state.updatedAt,
  });
  state.counters.dispatches += 1;
  closeIntent(state, idempotencyKey);
  if (status === STATUS.OK) {
    step.status = 'ok';
    step.lastFeedback = null;
  } else {
    recordFailure(state, step, status, observation);
  }
}

/* ------------------------------------------------------------------ */

/** Evaluation order. Sorted by name so the array literal cannot silently drift from the docs. */
export const OPERATION_ORDER = Object.freeze([
  'reconcile',
  'approval',
  'retry',
  'compaction',
  'checkpoint',
  'verify',
  'dispatch',
  'finalize',
]);

export function createOperations({ ports }) {
  const operations = [
    /* 1. Reconcile an outcome that was interrupted between intent and record. */
    {
      name: 'reconcile',
      applicable(state) {
        return state.inFlight.length > 0;
      },
      async run(state, ctx) {
        const intent = state.inFlight[0];
        const step = planStepById(state, intent.planStepId);
        const inspected = await ports.craft.inspect(intent.idempotencyKey);
        if (inspected.known) {
          state.updatedAt = ctx.now();
          recordResult(state, {
            planStepId: intent.planStepId,
            commandId: intent.commandId,
            idempotencyKey: intent.idempotencyKey,
            status: inspected.status,
            observation: 'reconciled from the app: the command did run',
            reconciledVia: 'inspect',
          });
          return {
            outcome: 'applied',
            kind: 'reconciled',
            payload: { planStepId: intent.planStepId, commandId: intent.commandId, status: inspected.status, via: 'inspect' },
          };
        }
        // The app cannot answer for the key. Decide from declared postconditions
        // instead of guessing, and refuse to proceed if they do not all hold.
        const checks = await ports.verify.check(step.request.postconditions);
        state.evidence.push(...checks.map((c) => ({ planStepId: step.planStepId, ...c, at: ctx.now(), source: 'reconcile' })));
        const allHold = checks.length > 0 && checks.every((c) => c.holds === true);
        if (allHold) {
          state.updatedAt = ctx.now();
          recordResult(state, {
            planStepId: intent.planStepId,
            commandId: intent.commandId,
            idempotencyKey: intent.idempotencyKey,
            status: STATUS.OK,
            observation: 'reconciled by verifying the declared postconditions',
            reconciledVia: 'verification',
          });
          return {
            outcome: 'applied',
            kind: 'reconciled',
            payload: { planStepId: intent.planStepId, commandId: intent.commandId, status: STATUS.OK, via: 'verification' },
          };
        }
        state.halt = {
          reason: 'MANUAL_RECONCILE',
          detail: `outcome of ${intent.commandId} is unknown and postconditions do not prove completion`,
        };
        return {
          outcome: 'halt',
          kind: 'reconcile_required',
          payload: { planStepId: intent.planStepId, checks },
        };
      },
    },

    /* 2. Approval: decide before a side effect, never block on a human. */
    {
      name: 'approval',
      applicable(state) {
        const step = pendingStep(state);
        if (!step || !step.requiresApproval) return false;
        const recorded = state.approvals[step.planStepId];
        if (recorded === undefined) return true;
        // A pending human decision is reported once, not once per run.
        return recorded.decision === 'require_human' && step.approvalRequested !== true;
      },
      async run(state, ctx) {
        const step = pendingStep(state);
        const recorded = state.approvals[step.planStepId];
        const markRequested = (next) => {
          const target = planStepById(next, step.planStepId);
          if (target) target.approvalRequested = true;
        };
        if (recorded?.decision === 'require_human') {
          state.updatedAt = ctx.now();
          return {
            outcome: 'yielded',
            kind: 'approval_required',
            payload: { planStepId: step.planStepId, commandId: step.request.commandId, reason: recorded.reason, requestedAt: recorded.at },
            mutate: markRequested,
          };
        }
        const decision = await ports.approval.decide({ request: step.request, planStep: clone(step) });
        state.approvals[step.planStepId] = {
          decision: decision.decision,
          reason: decision.reason ?? '',
          decidedBy: decision.decidedBy ?? 'policy',
          at: ctx.now(),
        };
        if (decision.decision === 'allow') {
          return {
            outcome: 'applied',
            kind: 'approval_decided',
            payload: { planStepId: step.planStepId, decision: 'allow', reason: decision.reason ?? '' },
          };
        }
        if (decision.decision === 'require_human') {
          return {
            outcome: 'yielded',
            kind: 'approval_required',
            payload: { planStepId: step.planStepId, commandId: step.request.commandId, reason: decision.reason ?? '' },
            mutate: markRequested,
          };
        }
        step.status = 'denied';
        state.halt = { reason: 'DENIED_BY_POLICY', detail: decision.reason ?? 'denied' };
        return {
          outcome: 'halt',
          kind: 'approval_decided',
          payload: { planStepId: step.planStepId, decision: 'deny', reason: decision.reason ?? '' },
        };
      },
    },

    /* 3. Repair a failed step, or stop honestly when repair cannot help. */
    {
      name: 'retry',
      applicable(state) {
        const failed = failedStep(state);
        if (!failed) return false;
        const status = failed.lastFeedback?.status;
        if (status === undefined) return false;
        return true;
      },
      async run(state, ctx) {
        const step = failedStep(state);
        const status = step.lastFeedback?.status;
        if (!REPAIRABLE_STATUSES.has(status)) {
          state.halt = { reason: `TERMINAL_${status}`, detail: step.lastFeedback?.feedback ?? '' };
          return { outcome: 'halt', kind: 'halted', payload: { planStepId: step.planStepId, reason: `TERMINAL_${status}` } };
        }
        const repairsSoFar = Math.max(0, step.attempts - 1);
        if (repairsSoFar >= state.config.repairBudget) {
          state.halt = { reason: 'REPAIR_BUDGET_EXHAUSTED', detail: step.lastFeedback?.feedback ?? '' };
          return { outcome: 'halt', kind: 'halted', payload: { planStepId: step.planStepId, reason: 'REPAIR_BUDGET_EXHAUSTED' } };
        }
        state.counters.repairs += 1;
        step.status = 'pending';
        return {
          outcome: 'applied',
          kind: 'repair_scheduled',
          payload: {
            planStepId: step.planStepId,
            commandId: step.request.commandId,
            attempt: step.attempts + 1,
            status,
            feedback: step.lastFeedback?.feedback ?? '',
          },
        };
      },
    },

    /* 4. Compaction: shrink the view, never touch the log. */
    {
      name: 'compaction',
      applicable(state) {
        if (state.events.length <= state.config.headEvents + 1) return false;
        if ((state.compaction?.consumedSeq ?? 0) >= state.cursor.seq) return false;
        return estimateTailTokens(state) > state.config.compactionThresholdTokens;
      },
      async run(state, ctx) {
        const generation = (state.compaction?.generation ?? 0) + 1;
        // Consume through the event this operation is about to create, so the
        // same compaction cannot fire again on its own output (which would spin
        // the pipeline without making progress).
        const consumedSeq = state.cursor.seq + 1;
        const note = buildContinuationNote(state.events, { episodeId: state.episodeId });
        state.compaction = { generation, consumedSeq, lastNote: note, estTokens: estimateTailTokens(state) };
        state.counters.compactions += 1;
        return {
          outcome: 'applied',
          kind: 'compaction',
          payload: { generation, consumedSeq, note, thresholdTokens: state.config.compactionThresholdTokens },
        };
      },
    },

    /* 5. Dispatch: the only external side effect. */
    {
      name: 'dispatch',
      applicable(state) {
        const step = pendingStep(state);
        if (!step) return false;
        // An approval-gated step only becomes dispatchable once a decision of
        // "allow" exists. "require_human" is not a decision, so it does not pass.
        if (step.requiresApproval && state.approvals[step.planStepId]?.decision !== 'allow') return false;
        return true;
      },
      async run(state, ctx) {
        const step = pendingStep(state);
        const request = step.request;
        step.attempts += 1;
        state.updatedAt = ctx.now();

        const valid = validateCommandRequest(request);
        if (!valid.ok) {
          recordFailure(state, step, STATUS.SCHEMA_INVALID, JSON.stringify(valid.errors));
          return {
            outcome: 'applied',
            kind: 'command_result',
            payload: { planStepId: step.planStepId, commandId: request.commandId, status: STATUS.SCHEMA_INVALID, errors: valid.errors },
          };
        }

        if (!isAllowedByProfile(request.capabilityProfile, request.commandId)) {
          step.status = 'denied';
          state.halt = {
            reason: 'CAPABILITY_DENIED',
            detail: `${request.commandId} is outside profile "${request.capabilityProfile}"`,
          };
          return {
            outcome: 'halt',
            kind: 'command_result',
            payload: { planStepId: step.planStepId, commandId: request.commandId, status: STATUS.DENIED },
          };
        }

        const key = idempotencyKeyFor(state.episodeId, step.planStepId);
        const prior = lastLedgerEntry(state, key);
        // A completed or terminal outcome is final: suppress the duplicate.
        // A repairable failure is an attempt, not an outcome, so a retry may
        // legitimately re-dispatch it under the same key.
        if (prior && (prior.status === STATUS.OK || !REPAIRABLE_STATUSES.has(prior.status))) {
          state.counters.duplicates += 1;
          if (prior.status === STATUS.OK) step.status = 'ok';
          else recordFailure(state, step, prior.status, prior.observation);
          return {
            outcome: 'applied',
            kind: 'duplicate_suppressed',
            payload: { planStepId: step.planStepId, commandId: request.commandId, status: prior.status, idempotencyKey: key },
          };
        }

        // Write-ahead intent, committed before the side effect. If the process
        // dies after this point, `reconcile` owns the recovery.
        state.inFlight.push({
          idempotencyKey: key,
          planStepId: step.planStepId,
          commandId: request.commandId,
          attempt: step.attempts,
          startedAt: ctx.now(),
        });
        ctx.commit(state);

        let result;
        try {
          result = await ports.craft.execute({
            commandId: request.commandId,
            args: request.args,
            idempotencyKey: key,
            dryRun: request.dryRun,
            capabilityProfile: request.capabilityProfile,
          });
        } catch (error) {
          closeIntent(state, key);
          recordFailure(state, step, STATUS.ENVIRONMENT, error.message);
          return {
            outcome: 'applied',
            kind: 'command_result',
            payload: { planStepId: step.planStepId, commandId: request.commandId, status: STATUS.ENVIRONMENT, detail: error.message },
          };
        }

        if (ctx.hooks.afterExecute) {
          await ctx.hooks.afterExecute({ request, result, idempotencyKey: key });
        }

        recordResult(state, {
          planStepId: step.planStepId,
          commandId: request.commandId,
          idempotencyKey: key,
          status: result.status,
          observation: result.observation,
          undoToken: result.undoToken,
        });
        return {
          outcome: 'applied',
          kind: 'command_result',
          payload: {
            planStepId: step.planStepId,
            commandId: request.commandId,
            status: result.status,
            observation: result.observation ?? '',
            artifacts: result.artifacts ?? [],
            undoToken: result.undoToken ?? null,
          },
        };
      },
    },

    /* 6. Verify: turn claimed effects into evidence, or into a failure. */
    {
      name: 'verify',
      applicable(state) {
        const step = state.plan.find((s) => s.status === 'ok' && s.request.postconditions.length > 0 && s.verified !== true);
        return Boolean(step);
      },
      async run(state, ctx) {
        const step = state.plan.find((s) => s.status === 'ok' && s.request.postconditions.length > 0 && s.verified !== true);
        const checks = await ports.verify.check(step.request.postconditions);
        state.evidence.push(...checks.map((c) => ({ planStepId: step.planStepId, ...c, at: ctx.now(), source: 'postcondition' })));
        const failed = checks.filter((c) => c.holds !== true);
        step.verified = failed.length === 0;
        if (failed.length > 0) {
          recordFailure(state, step, STATUS.UNVERIFIED, failed.map((c) => `${c.kind}:${c.label}`).join(','));
        }
        return {
          outcome: 'applied',
          kind: 'verification',
          payload: {
            planStepId: step.planStepId,
            checks: checks.map((c) => ({ kind: c.kind, holds: c.holds, label: c.label })),
            allHold: failed.length === 0,
          },
        };
      },
    },

    /* 7. Finalize: refuse to close on evidence that is not there. */
    {
      name: 'finalize',
      applicable(state) {
        if (state.finished) return false;
        if (state.inFlight.length > 0) return false;
        return state.plan.every((s) => s.status === 'ok' || s.status === 'denied');
      },
      async run(state, ctx) {
        const unverified = state.plan.filter((s) => s.request.postconditions.length > 0 && s.verified !== true);
        if (unverified.length > 0) {
          return {
            outcome: 'yielded',
            kind: 'awaiting_evidence',
            payload: { steps: unverified.map((s) => s.planStepId) },
          };
        }
        state.finished = true;
        state.finishedAt = ctx.now();
        return {
          outcome: 'applied',
          kind: 'episode_finished',
          payload: { steps: state.plan.length, ledgerEntries: state.ledgerEntries.length },
        };
      },
    },

    /* 8. Checkpoint: hash-chained progress record for audit. */
    {
      name: 'checkpoint',
      applicable(state) {
        if (state.finished) return false;
        if (state.cursor.seq === 0) return false;
        return state.cursor.seq - (state.lastCheckpointSeq ?? 0) >= state.config.checkpointEveryEvents;
      },
      async run(state) {
        const prevHash = state.lastCheckpointHash ?? null;
        const hash = digest({
          episodeId: state.episodeId,
          seq: state.cursor.seq,
          ledger: state.ledgerEntries.length,
          plan: state.plan.map((s) => [s.planStepId, s.status]),
          prev: prevHash,
        });
        state.lastCheckpointSeq = state.cursor.seq;
        state.lastCheckpointHash = hash;
        state.counters.checkpoints += 1;
        return {
          outcome: 'applied',
          kind: 'checkpoint',
          payload: { seq: state.cursor.seq, hash, prevHash },
        };
      },
    },
  ];
  operations.sort(
    (a, b) => OPERATION_ORDER.indexOf(a.name) - OPERATION_ORDER.indexOf(b.name),
  );
  return operations;
}
