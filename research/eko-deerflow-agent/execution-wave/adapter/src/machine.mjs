/**
 * The machine: one step, one operation, one committed event.
 *
 * Re-entrancy rules:
 *  - operations mutate a draft and never talk to the store directly, except via
 *    `ctx.commit` when they must make an intent durable before a side effect;
 *  - the machine appends exactly one event per step and commits once (dispatch
 *    commits twice by design: intent, then result);
 *  - a resumed process calls `open()` (which re-validates the session) and
 *    `run()`; nothing else is required.
 */

import { AdapterError, toPlanEntry, validatePlan } from './envelope.mjs';
import { createOperations } from './operations.mjs';
import { SESSION_SCHEMA_VERSION, assertSession, createInitialSession } from './store.mjs';

export const RUN_STATUS = Object.freeze({
  FINISHED: 'finished',
  HALTED: 'halted',
  AWAITING_HUMAN: 'awaiting_human',
  AWAITING_EVIDENCE: 'awaiting_evidence',
  IDLE: 'idle',
  STEP_LIMIT: 'step_limit',
});

const DECISIONS = new Set(['allow', 'deny']);

export class Conductor {
  constructor({ store, ports, episodeId, writerId = 'forge-conductor', plan = null, config = {}, hooks = {}, now = () => new Date().toISOString(), operations = null }) {
    if (!store || typeof store.load !== 'function' || typeof store.commit !== 'function') {
      throw new AdapterError('E_STORE_CONTRACT', 'store must implement load() and commit()');
    }
    if (!ports || !ports.craft || !ports.approval || !ports.verify) {
      throw new AdapterError('E_PORTS_CONTRACT', 'ports must provide craft, approval and verify');
    }
    for (const method of ['execute', 'inspect', 'snapshot']) {
      if (typeof ports.craft[method] !== 'function') {
        throw new AdapterError('E_PORTS_CONTRACT', `craft port is missing ${method}()`);
      }
    }
    if (typeof ports.approval.decide !== 'function') throw new AdapterError('E_PORTS_CONTRACT', 'approval port is missing decide()');
    if (typeof ports.verify.check !== 'function') throw new AdapterError('E_PORTS_CONTRACT', 'verify port is missing check()');

    this.store = store;
    this.ports = ports;
    this.episodeId = episodeId;
    this.writerId = writerId;
    this.plan = plan;
    this.config = config;
    this.hooks = hooks;
    this.now = now;
    this.operations = operations ?? createOperations({ ports });
    this.state = null;
  }

  /** Convenience constructor: build, open, return the conductor. */
  static async start(options) {
    const conductor = new Conductor(options);
    await conductor.open();
    return conductor;
  }

  /**
   * Load an existing session or create a new one. A session from another
   * episode, a different writer, or a different schema is refused — never
   * "resumed" into a half-empty state.
   */
  async open() {
    const loaded = this.store.load();
    if (loaded) {
      if (loaded.episodeId !== this.episodeId) {
        throw new AdapterError('E_EPISODE_MISMATCH', `store holds episode ${loaded.episodeId}, not ${this.episodeId}`);
      }
      if (loaded.writerId !== this.writerId) {
        throw new AdapterError('E_WRITER_MISMATCH', `store writer is ${loaded.writerId}, adapter expects ${this.writerId}`);
      }
      this.state = loaded;
      return this;
    }
    if (!this.plan) {
      throw new AdapterError('E_NO_PLAN', 'cannot create a session without a plan');
    }
    const validated = validatePlan(this.plan);
    if (!validated.ok) {
      throw new AdapterError('E_PLAN_INVALID', 'plan failed validation', validated.errors);
    }
    const session = createInitialSession({
      episodeId: this.episodeId,
      writerId: this.writerId,
      plan: this.plan.map(toPlanEntry),
      config: this.config,
      createdAt: this.now(),
    });
    assertSession(session);
    session.events.push({
      seq: 1,
      at: this.now(),
      op: 'bootstrap',
      kind: 'episode_started',
      payload: {
        schemaVersion: SESSION_SCHEMA_VERSION,
        steps: session.plan.map((s) => s.planStepId),
        writerId: this.writerId,
      },
    });
    session.cursor.seq = 1;
    this.store.commit(session);
    this.state = session;
    return this;
  }

  _commit(draft) {
    this.store.commit(draft);
    this.state = draft;
  }

  _ctx(draft) {
    return {
      ports: this.ports,
      hooks: this.hooks,
      now: this.now,
      commit: (next) => {
        this.store.commit(next);
        this.state = next;
      },
    };
  }

  /** Advance exactly one operation. Returns a structured result; never throws for a command outcome. */
  async step() {
    if (!this.state) throw new AdapterError('E_NOT_OPEN', 'call open() before step()');
    if (this.state.halt) return { op: null, outcome: 'halted', halt: this.state.halt };
    if (this.state.finished) return { op: null, outcome: 'finished' };

    const draft = structuredClone(this.state);
    for (const operation of this.operations) {
      const applicable = await operation.applicable(draft);
      if (!applicable) continue;

      const result = await operation.run(draft, this._ctx(draft));
      const event = {
        seq: draft.cursor.seq + 1,
        at: this.now(),
        op: operation.name,
        kind: result.kind,
        payload: result.payload ?? null,
      };
      draft.events.push(event);
      draft.cursor.seq = event.seq;
      draft.cursor.steps += 1;
      draft.updatedAt = this.now();
      if (typeof result.mutate === 'function') result.mutate(draft);

      this._commit(draft);
      return { op: operation.name, outcome: result.outcome, kind: result.kind, event };
    }
    return { op: null, outcome: 'idle' };
  }

  /** Run until the pipeline yields, halts, finishes, idles, or hits the step limit. */
  async run({ maxSteps } = {}) {
    if (!this.state) throw new AdapterError('E_NOT_OPEN', 'call open() before run()');
    const limit = maxSteps ?? this.state.config.maxSteps;
    const results = [];
    for (let i = 0; i < limit; i += 1) {
      const result = await this.step();
      results.push(result);
      if (['idle', 'halted', 'finished', 'yielded'].includes(result.outcome)) break;
    }
    return { status: this.status(results.at(-1)?.outcome), results, state: this.state };
  }

  status(outcome) {
    if (this.state.halt) return RUN_STATUS.HALTED;
    if (this.state.finished) return RUN_STATUS.FINISHED;
    const lastEvent = this.state.events.at(-1);
    if (lastEvent?.kind === 'approval_required') return RUN_STATUS.AWAITING_HUMAN;
    if (lastEvent?.kind === 'awaiting_evidence') return RUN_STATUS.AWAITING_EVIDENCE;
    if (outcome === 'idle') return RUN_STATUS.IDLE;
    return RUN_STATUS.STEP_LIMIT;
  }

  /**
   * Operator API: record a human decision for an approval-gated step.
   * `deny` halts the episode; `allow` unblocks dispatch on the next run.
   */
  async recordDecision(planStepId, decision, { decidedBy = 'operator', reason = '' } = {}) {
    if (!this.state) throw new AdapterError('E_NOT_OPEN', 'call open() before recordDecision()');
    if (!DECISIONS.has(decision)) throw new AdapterError('E_DECISION', `decision must be allow or deny, got ${String(decision)}`);
    const draft = structuredClone(this.state);
    const step = draft.plan.find((s) => s.planStepId === planStepId);
    if (!step) throw new AdapterError('E_UNKNOWN_STEP', `no plan step ${planStepId}`);

    draft.approvals[planStepId] = { decision, reason, decidedBy, at: this.now() };
    if (decision === 'deny') {
      step.status = 'denied';
      draft.halt = { reason: 'DENIED_BY_POLICY', detail: reason || 'denied by operator' };
    }
    const event = {
      seq: draft.cursor.seq + 1,
      at: this.now(),
      op: 'human',
      kind: 'human_decision',
      payload: { planStepId, decision, decidedBy, reason },
    };
    draft.events.push(event);
    draft.cursor.seq = event.seq;
    draft.updatedAt = this.now();
    this._commit(draft);
    return { planStepId, decision, event };
  }

  /**
   * The model-facing view: a pinned head, the last continuation note, and the
   * uncompacted tail. Events themselves are never removed.
   */
  view() {
    if (!this.state) throw new AdapterError('E_NOT_OPEN', 'call open() before view()');
    const head = this.state.events.slice(0, this.state.config.headEvents);
    const consumedSeq = this.state.compaction?.consumedSeq ?? 0;
    const tail = this.state.events.filter((event) => event.seq > consumedSeq);
    return {
      episodeId: this.state.episodeId,
      head,
      note: this.state.compaction?.lastNote ?? null,
      generation: this.state.compaction?.generation ?? 0,
      tail,
      totalEvents: this.state.events.length,
      omittedEvents: Math.max(0, this.state.events.length - head.length - tail.length),
    };
  }

  /** Full session, for audit and tests. Read-only by convention. */
  snapshot() {
    if (!this.state) throw new AdapterError('E_NOT_OPEN', 'call open() before snapshot()');
    return structuredClone(this.state);
  }
}
