/**
 * Session persistence for the Conductor.
 *
 * Two implementations, one contract: `load()` returns a validated session or
 * null, `commit(session)` replaces it atomically. The file store fails closed on
 * a schema mismatch instead of "helpfully" resuming an empty episode — that
 * invariant is the whole point of storing the version alongside the data.
 */

import { appendFileSync, existsSync, mkdirSync, readFileSync, renameSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

import { AdapterError, digest } from './envelope.mjs';

export const SESSION_SCHEMA_VERSION = 1;
export const DEFAULT_CONFIG = Object.freeze({
  compactionThresholdTokens: 1200,
  repairBudget: 2,
  maxSteps: 200,
  checkpointEveryEvents: 8,
  headEvents: 2,
});

export class StoreError extends Error {
  constructor(code, message, detail) {
    super(message);
    this.name = 'StoreError';
    this.code = code;
    this.detail = detail ?? null;
  }
}

/** Structural validation. Throws on anything that would make replay unsafe. */
export function assertSession(session) {
  if (typeof session !== 'object' || session === null || Array.isArray(session)) {
    throw new StoreError('E_SESSION_NOT_OBJECT', 'session must be a plain object');
  }
  if (session.schemaVersion !== SESSION_SCHEMA_VERSION) {
    throw new StoreError(
      'E_SCHEMA_MISMATCH',
      `session schema ${String(session.schemaVersion)} cannot be resumed by this adapter (expected ${SESSION_SCHEMA_VERSION})`,
      { found: session.schemaVersion, expected: SESSION_SCHEMA_VERSION },
    );
  }
  if (typeof session.writerId !== 'string' || session.writerId.length === 0) {
    throw new StoreError('E_WRITER_MISSING', 'session writerId is required');
  }
  if (typeof session.episodeId !== 'string' || session.episodeId.length === 0) {
    throw new StoreError('E_EPISODE_MISSING', 'session episodeId is required');
  }
  if (!Array.isArray(session.plan) || !Array.isArray(session.events) || !Array.isArray(session.inFlight)) {
    throw new StoreError('E_SESSION_SHAPE', 'session plan, events and inFlight must be arrays');
  }
  if (!Array.isArray(session.ledgerEntries)) {
    throw new StoreError('E_SESSION_SHAPE', 'session ledgerEntries must be an array');
  }
  if (!Array.isArray(session.evidence)) {
    throw new StoreError('E_SESSION_SHAPE', 'session evidence must be an array');
  }
  const seq = session.cursor?.seq;
  if (!Number.isInteger(seq) || seq < 0) {
    throw new StoreError('E_CURSOR', 'session cursor.seq must be a non-negative integer');
  }
  for (const event of session.events) {
    if (!Number.isInteger(event.seq) || event.seq < 1 || event.seq > seq) {
      throw new StoreError('E_EVENT_SEQ', 'event sequence must be contiguous within the cursor');
    }
    if (typeof event.kind !== 'string' || event.kind.length === 0) {
      throw new StoreError('E_EVENT_KIND', 'event kind is required');
    }
  }
  return session;
}

/**
 * Build the session document a fresh episode starts from.
 * `ledgerEntries` is an array (not an object) so ordering is stable on disk and
 * the duplicate check is a single scan with no prototype-key hazards.
 */
export function createInitialSession({ episodeId, writerId, plan, config = {}, createdAt }) {
  const merged = { ...DEFAULT_CONFIG, ...config };
  const at = createdAt ?? new Date().toISOString();
  return {
    schemaVersion: SESSION_SCHEMA_VERSION,
    writerId,
    episodeId,
    createdAt: at,
    updatedAt: at,
    config: merged,
    cursor: { seq: 0, steps: 0 },
    plan,
    events: [],
    inFlight: [],
    ledgerEntries: [],
    evidence: [],
    approvals: {},
    counters: { dispatches: 0, duplicates: 0, repairs: 0, compactions: 0, checkpoints: 0, failures: 0 },
    compaction: { generation: 0, consumedSeq: 0, lastNote: null, estTokens: 0 },
    lastCheckpointSeq: 0,
    lastCheckpointHash: null,
    halt: null,
    finished: false,
    finishedAt: null,
  };
}

function clone(value) {
  return structuredClone(value);
}

/** In-memory store. Same contract as FileStore; used by fast tests and by embedding. */
export class MemoryStore {
  constructor(initial = null) {
    this.session = initial ? clone(initial) : null;
    this.commits = 0;
  }

  load() {
    return this.session ? clone(this.session) : null;
  }

  commit(next) {
    assertSession(next);
    this.session = clone(next);
    this.commits += 1;
    return this.session;
  }
}

/**
 * File-backed store: one JSON document, replaced atomically via write-then-rename.
 *
 * A process that dies mid-commit leaves the previous document intact (the temp
 * file is ignored on load). `journal.jsonl` is an append-only audit trail; it is
 * NOT the source of truth and a torn last line is tolerated, because the JSON
 * document is what resume reads.
 */
export class FileStore {
  constructor(directory) {
    this.directory = directory;
    this.sessionPath = join(directory, 'session.json');
    this.journalPath = join(directory, 'journal.jsonl');
    this.commits = 0;
  }

  load() {
    if (!existsSync(this.sessionPath)) return null;
    const raw = readFileSync(this.sessionPath, 'utf8');
    let parsed;
    try {
      parsed = JSON.parse(raw);
    } catch (error) {
      throw new StoreError('E_CORRUPT', `session.json is not valid JSON: ${error.message}`);
    }
    return assertSession(parsed);
  }

  commit(next) {
    assertSession(next);
    mkdirSync(this.directory, { recursive: true });
    const temp = `${this.sessionPath}.${process.pid}.tmp`;
    writeFileSync(temp, JSON.stringify(next, null, 2), 'utf8');
    renameSync(temp, this.sessionPath);
    try {
      appendFileSync(
        this.journalPath,
        `${JSON.stringify({ at: new Date().toISOString(), seq: next.cursor.seq, digest: digest(next) })}\n`,
        'utf8',
      );
    } catch (error) {
      // The session document already committed; a journal failure must not
      // pretend the commit failed. Surface it, keep the committed state.
      throw new AdapterError('E_JOURNAL_APPEND', `session committed but journal append failed: ${error.message}`);
    }
    this.commits += 1;
    return next;
  }
}
