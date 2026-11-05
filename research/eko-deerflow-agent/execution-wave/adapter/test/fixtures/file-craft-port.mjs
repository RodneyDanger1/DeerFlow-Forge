/**
 * File-backed Craft port used by the crash/resume test.
 *
 * It stands in for the real app boundary and, unlike the in-memory double, it
 * survives a process exit: effects and calls are appended to JSONL, and the
 * document is written atomically. `inspect(key)` reads the effects log, which
 * is exactly what the pipeline asks after a crash.
 *
 * Tolerance policy: a torn final JSONL line (process killed mid-append) is
 * skipped with an explicit warning object, never silently treated as data.
 */

import { appendFileSync, existsSync, mkdirSync, readFileSync, renameSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

import { STATUS } from '../../src/envelope.mjs';

function readJsonl(path) {
  if (!existsSync(path)) return [];
  const rows = [];
  for (const line of readFileSync(path, 'utf8').split('\n')) {
    if (line.trim() === '') continue;
    try {
      rows.push(JSON.parse(line));
    } catch {
      rows.push({ __torn: true, raw: line.slice(0, 120) });
    }
  }
  return rows;
}

const EMPTY_DOCUMENT = () => ({ layers: [], artifacts: [], params: {}, flags: {} });

export class FileCraftPort {
  constructor(directory) {
    this.directory = directory;
    this.documentPath = join(directory, 'document.json');
    this.effectsPath = join(directory, 'effects.jsonl');
    this.callsPath = join(directory, 'calls.jsonl');
    mkdirSync(directory, { recursive: true });
  }

  readDocument() {
    if (!existsSync(this.documentPath)) return EMPTY_DOCUMENT();
    return JSON.parse(readFileSync(this.documentPath, 'utf8'));
  }

  writeDocument(document) {
    const temp = `${this.documentPath}.${process.pid}.tmp`;
    writeFileSync(temp, JSON.stringify(document, null, 2), 'utf8');
    renameSync(temp, this.documentPath);
  }

  applyCommand(document, commandId, args) {
    switch (commandId) {
      case 'craft://document/add-layer': {
        const name = String(args.name ?? '');
        if (name === '') return { status: STATUS.SCHEMA_INVALID, observation: 'name required' };
        if (document.layers.includes(name)) {
          return { status: STATUS.PRECONDITION_UNMET, observation: `layer ${name} exists` };
        }
        document.layers.push(name);
        document.flags.unsaved = true;
        return { status: STATUS.OK, observation: `added ${name}` };
      }
      case 'craft://document/export': {
        const name = String(args.name ?? 'export');
        if (document.layers.length === 0) return { status: STATUS.PRECONDITION_UNMET, observation: 'nothing to export' };
        document.artifacts.push(name);
        document.flags.exported = true;
        return { status: STATUS.OK, observation: `exported ${name}`, artifacts: [name] };
      }
      default:
        return { status: STATUS.NO_MATCH, observation: `unknown command ${commandId}` };
    }
  }

  async execute({ commandId, args, idempotencyKey, dryRun = false }) {
    appendFileSync(
      this.callsPath,
      `${JSON.stringify({ at: new Date().toISOString(), commandId, idempotencyKey, dryRun })}\n`,
      'utf8',
    );
    if (dryRun) {
      return { status: STATUS.OK, observation: 'dry run', undoToken: `undo_${idempotencyKey}` };
    }
    const document = this.readDocument();
    const outcome = this.applyCommand(document, commandId, args);
    this.writeDocument(document);
    // Effect is appended after the document write. A crash between the two
    // leaves "document changed, effect unknown", which the pipeline resolves by
    // verification rather than by re-executing the command.
    appendFileSync(
      this.effectsPath,
      `${JSON.stringify({ at: new Date().toISOString(), commandId, idempotencyKey, status: outcome.status, observation: outcome.observation })}\n`,
      'utf8',
    );
    return { ...outcome, undoToken: `undo_${idempotencyKey}` };
  }

  inspect(idempotencyKey) {
    const known = readJsonl(this.effectsPath).find((row) => row.idempotencyKey === idempotencyKey && !row.__torn);
    return known ? { known: true, status: known.status } : { known: false };
  }

  snapshot() {
    return this.readDocument();
  }

  countEffects() {
    return readJsonl(this.effectsPath).filter((row) => !row.__torn).length;
  }

  countCalls() {
    return readJsonl(this.callsPath).filter((row) => !row.__torn).length;
  }

  calls() {
    return readJsonl(this.callsPath);
  }
}
