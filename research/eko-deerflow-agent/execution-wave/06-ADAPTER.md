# 06 — ADAPTER PROTOTYPE: ordered re-entrant operation pipeline (task-13)

**Status:** execution-wave prototype. **No production code touched.** Only this file, `06-ADAPTER.json`
and `execution-wave/adapter/**` were written (verified with `git status`, §8).
**Date:** 2026-11-05. **Host:** Windows, Node **v26.7.0**, zero runtime dependencies.
**Donor mechanism:** `05-HARNESS-CODE.md` §M1 (Goose's ordered re-entrant operation pipeline). Only the
*idea* is borrowed — no donor source, prompt, schema or identifier is copied. Provenance and
non-copying statement: §1.3.

---

## 1. What was built, and what it is not

### 1.1 Selection

`05` lists twelve candidate mechanisms. M1 was selected for this wave because it is the only one that is
simultaneously (a) structural — it decides where every other policy lives — and (b) directly testable
without a model or an app: the pipeline's correctness is observable from persisted state alone. The Craft
Command Gateway needs exactly that property before it can touch a real document.

### 1.2 Deliverable

A runnable prototype of the gateway core:

| Concern | Implementation | Lines |
|---|---|---|
| Command envelope, status vocabulary, plan validation, idempotency key | `adapter/src/envelope.mjs` | 223 |
| Session persistence (memory + file, atomic commit, schema fail-closed) | `adapter/src/store.mjs` | 178 |
| Ports: Craft port, approval policy, verifier, continuation note (+ reference doubles) | `adapter/src/ports.mjs` | 208 |
| The eight operations | `adapter/src/operations.mjs` | 500 |
| Machine: step/apply/run, resume, operator decision API, view | `adapter/src/machine.mjs` | 238 |
| Wiring: `createCraftConductor`, pipeline order, run summary | `adapter/src/gateway.mjs` | 86 |
| Tests + fixtures | `adapter/test/**` (5 suites, 3 fixtures) | 926 |
| README + package manifest | `adapter/README.md`, `adapter/package.json` | 60 |

Total **2,419 lines / 16 files** (§8 for the exact command that produced this count).

**It is not** a Craft integration: there is no IPC call, no real document, no model. The app boundary is a
port (`craftPort`), and the only Craft implementations in the tree are test doubles that live in
`test/fixtures/`. §7 lists exactly what production replaces.

### 1.3 Donor provenance and non-copying statement

- Donor: `block/goose`, `crates/goose/src/agents/state_machine/mod.rs:1-6` and the operation modules at
  `:8-39` (Apache-2.0), as recorded in `05-HARNESS-CODE.md` §M1 with tree SHA `609d3432`.
- Borrowed at the level of *mechanism*: a step is the first applicable operation in an ordered list;
  operations are policy-shaped (approval, compaction, retry), re-entrant over persisted state; a machine
  applies effects and re-enters.
- **Not borrowed:** no Goose file was opened while writing this prototype (per instruction not to re-read
  the donor corpus); no identifier, module name, trait, prompt or code shape is reused. The names here
  (`Conductor`, `dispatch`, `reconcile`, `inFlight`) describe *this* design. If any resemblance to donor
  internals remains it is coincidental, not copied — and this prototype is prototype-only.

---

## 2. The pipeline

Order is a safety property. Each step evaluates operations top-down and runs the first applicable one;
the machine appends exactly one event and commits.

| # | Operation | Applicable when | External effect | Emits | Terminal behaviour |
|---|---|---|---|---|---|
| 1 | `reconcile` | an intent is in `inFlight` | `inspect`, else `verify` | `reconciled`, `reconcile_required` | halts `MANUAL_RECONCILE` when the outcome cannot be proven |
| 2 | `approval` | next step is gated and undecided, or a human decision is pending | `approval.decide` | `approval_decided`, `approval_required` | halts `DENIED_BY_POLICY` on deny; otherwise **yields**, never blocks |
| 3 | `retry` | a step failed with feedback | none | `repair_scheduled`, `halted` | halts `REPAIR_BUDGET_EXHAUSTED` or `TERMINAL_<status>` |
| 4 | `compaction` | tail tokens > threshold | none (view only) | `compaction` | never terminal |
| 5 | `checkpoint` | ≥ N events since last checkpoint | none | `checkpoint` | never terminal |
| 6 | `verify` | a step is `ok` with unchecked postconditions | `verify.check` | `verification` | marks step failed → `retry` handles it |
| 7 | `dispatch` | a pending, approved step exists | **`craft.execute`** | `command_result`, `duplicate_suppressed` | failure feeds `retry` |
| 8 | `finalize` | no pending/failed steps, no in-flight intent | none | `episode_finished` | yields `awaiting_evidence` if any required criterion is unverified |

Design notes that matter:

- **`reconcile` is first** so nothing new can be dispatched while an earlier outcome is unknown.
- **`checkpoint` is before `verify`/`dispatch`** so audit progress is recorded even when the run stops
  immediately after (making checkpoints observable in short episodes — the tests assert ≥2 chain links).
- **`finalize` refuses** instead of closing: unverified evidence yields `awaiting_evidence` and the
  episode stays open. This mirrors the `UNVERIFIED` discipline in `05` §M11 and the user's own
  definition-of-done rule; it is proven by a dedicated test.
- **Approval never blocks.** `require_human` records the request and yields; re-running does not spam
  events; `recordDecision()` is the operator API. This is the concrete fix for anti-pattern A4 in `05`
  ("interactive approval assumed to be available in a headless run").

---

## 3. Persisted state and the commit protocol

The session is one JSON document (`schemaVersion`, `writerId`, `episodeId`, plan, events, `inFlight`,
`ledgerEntries`, evidence, counters, compaction, halt, finished). `FileStore.commit()` writes a temp file
and renames it, then appends an audit line to `journal.jsonl` (the journal is not the source of truth; a
torn last line is irrelevant because resume reads the JSON document).

Fail-closed rules, all tested:

- `schemaVersion !== 1` → `E_SCHEMA_MISMATCH` (refuse to resume, never "start fresh" quietly).
- malformed JSON → `E_CORRUPT`.
- session for another `episodeId` / `writerId` → `E_EPISODE_MISMATCH` / `E_WRITER_MISMATCH`.
- event sequence must be contiguous and within the cursor.

**Idempotency key** = `sha256(episodeId | planStepId)` truncated. Stable by construction across retries
and resumes, independent per episode, and the single identity Craft needs to dedupe on its side.

**Dispatch protocol (write-ahead):**

1. validate the envelope again (defence in depth — the plan was validated at start);
2. capability profile check (`inspect`/`edit`/`export`/`batch` → command families; denied = terminal);
3. duplicate check against the ledger: a recorded **completed or terminal** outcome is replayed with no
   app call; a recorded **repairable** failure is an attempt, not an outcome, so a repair may re-dispatch;
4. append the intent to `inFlight` and **commit before the side effect**;
5. `craft.execute({commandId, args, idempotencyKey, dryRun, capabilityProfile})`;
6. append the result event + ledger entry (status, observation, undo token) and commit.

The window between (4) and (6) is the only place a crash can leave ambiguity, and operation 1 owns it.

---

## 4. Crash matrix (each row is a test)

| Crash point | What is on disk | What resume does | Outcome | Test |
|---|---|---|---|---|
| before intent commit | no intent, no effect | `dispatch` runs normally | command executes once | (not separately tested; trivial path) |
| after intent commit, before app call | intent, no effect | `inspect` → unknown → verify postconditions → fail | **halt `MANUAL_RECONCILE`** | `unresolvable intent halts…` |
| after app effect, before result commit | intent + effect | `inspect` → known → record result, no re-execution | **finished, effect count unchanged** | `crash after the effect…` (real child killed with exit 9) |
| app cannot answer, document proves it | intent, document mutated, no effect log | verify postconditions → hold → reconcile via verification | finished, reconciled `verification` | `when the app cannot answer…` |
| after result commit | intent cleared, ledger written | normal | — | happy-path / replay tests |

The crash test is not simulated inside the test process: `test/fixtures/crash-child.mjs` is spawned as a
child, runs a real dispatch against a file-backed double, and calls `process.exit(9)` from the
`afterExecute` hook — i.e. after the effect is persisted, before the result commit. The parent then
asserts the on-disk facts and resumes in a fresh conductor instance.

Measured on the recorded run:

- child exit code **9**;
- pre-resume: `inFlight.length = 1`, `ledgerEntries.length = 0`, `plan[0].status = "pending"`,
  `calls.jsonl = 1` line, `effects.jsonl = 1` line;
- post-resume: `finished = true`, `ledgerEntries[0].reconciledVia = "inspect"`, calls **still 1**,
  effects **still 1**, `journal.jsonl ≥ 2` lines, document layers `["Ink"]`.

---

## 5. Duplicate, repair and compaction semantics (and why they are shaped this way)

- **Duplicate suppression** keys on the ledger, not on wall-clock or a run counter: replaying a completed
  step emits `duplicate_suppressed` and leaves the app untouched (`counters.duplicates = 1`, calls
  unchanged). A *terminal failed* outcome is also final and is not retried.
- **Repair** distinguishes transport-shaped faults (`SCHEMA_INVALID`, `PRECONDITION_UNMET`, `NO_MATCH`,
  `TIMEOUT`) from everything else. Only the former consume the repair budget; `ENVIRONMENT` halts at once
  (`TERMINAL_ENVIRONMENT`, one app call, zero repairs). Both attempts stay in the ledger audit trail —
  suppression cares about the *last* entry, so `[NO_MATCH, OK]` is a legitimate history.
- **Compaction** never edits history. It writes a continuation note, advances `consumedSeq`, and the
  model-facing `view()` returns `head (2 events) + note + tail`. The test asserts the 8 `command_result`
  events are all still present after compaction fired, the pinned head survived, and `omittedEvents > 0`.
  The note is deterministic (`buildContinuationNote`) — a production binding replaces it with a model call
  (§7), and the shape is deliberately the "goal / completed / failed / verification / facts-only" note
  described in `05` §M8.
- **Checkpoints** hash `{episodeId, seq, ledger count, plan statuses, prevHash}`. The test asserts the
  first `prevHash` is null and each subsequent link matches the previous hash.

---

## 6. Tests

Command (from `execution-wave/adapter/`):

```powershell
node --test "test/*.test.mjs"
```

Observed result on this host (2026-11-05, Node v26.7.0):

```
tests 30   pass 30   fail 0   duration ~1.07 s
```

(`npm test` also passes via `npm.cmd test`; plain `npm test` is blocked on this host by the PowerShell
execution policy for `npm.ps1`, which is an environment restriction, not a code failure.)

| Suite | Proves |
|---|---|
| `envelope.test.mjs` (8) | closed postcondition set; boundary rejects every malformed field; capability projection; plan validation; idempotency stability; digest order-independence; only transport faults are repairable |
| `machine.test.mjs` (6) | happy path finishes with 2 ledger entries; contiguous event seq; finished episode re-run is a no-op; checkpoint hash chain; **finalize refuses unverified evidence**; halted episode does not advance |
| `approval-compaction-retry.test.mjs` (8) | deny halts before any app call; `require_human` yields once and resumes via `recordDecision`; operator deny halts; compaction fires on a token budget and keeps history + head; retry repairs `NO_MATCH` and finishes; repair budget exhaustion halts; environment failure is terminal |
| `duplicate.test.mjs` (3) | replay is suppressed with no app call; terminal failure is not re-executed; keys are episode-scoped |
| `crash-resume.test.mjs` (6) | real crash → intent survives → reconcile via inspect, no double effect; unresolvable → halt; verification-based recovery; schema mismatch, corrupt file, episode mismatch all fail closed |

---

## 7. Limits and what production must replace

This is a prototype, and the honest boundary is:

1. **No real Craft transport.** `craftPort` must be bound to Craft's IPC/CLI/MCP surface. Whether Craft can
   answer `inspect(idempotencyKey)` at all is **UNVERIFIED** — that is question Q1/Q4 in `05` §8. If it
   cannot, the fallback is postcondition verification (implemented and tested), and the `MANUAL_RECONCILE`
   halt is the honest outcome when that is also inconclusive.
2. **Deterministic continuation note.** `buildContinuationNote` is a stand-in for a model-written note;
   it is deliberately conservative (facts derived from events only). Replacing it is a single port call.
3. **Token estimate is crude** (chars/4 over the tail). Adequate to exercise the pipeline, not to tune a
   production budget; `05` §M9 calls for measured tokens and cost-tier headroom.
4. **No subagent runtime, telemetry sink, or pixel verification** — out of scope for this wave (Craft
   build items B1 only). `05` §7 lists them.
5. **The verifier is document-shape only** (`layer-count`, `param-equals`, `artifact-exists`,
   `document-flag`). Craft's real object model must supply the snapshot; pixel diff remains secondary.
6. **Single-writer assumption.** Two live conductors on one session directory would race on the atomic
   rename; a file lock or a single-owner queue is required before concurrent use.

No claim is made that this equals Goose's implementation, that it is production-ready, or that Craft can
be driven by it today.

---

## 8. Verification evidence (commands and observed output)

```text
$ cd "research\eko-deerflow-agent\execution-wave\adapter"
$ node --test "test/*.test.mjs"
  tests 30   pass 30   fail 0   duration ~1.07s
$ npm.cmd test            # same 30/30 via the package script
$ node -e "import('./src/gateway.mjs').then(m=>console.log(Object.keys(m)))"
  exports: PIPELINE,createCraftConductor,summarizeRun
$ node test/fixtures/crash-child.mjs <tmpdir>
  child-exit=9              # the crash fixture dies mid-dispatch, as designed
$ git status --porcelain -- research/eko-deerflow-agent/execution-wave
  ?? research/eko-deerflow-agent/execution-wave/    # only new files; nothing modified
```

Stub sweep over all `.mjs`/`.md`/`.json` in the adapter directory for
`TODO|FIXME|HACK|placeholder|NotImplemented|mock|stub|dummy|lorem|simplified for`:
**0 hits across 16 files.** The only double in the tree is the documented Craft boundary double
(`test/fixtures/*`), which is a permitted third-party-boundary double and is never imported by `src/`.

---

## 9. Next steps

1. Bind `craftPort` to a real Craft command surface and run the same suite against it (the tests are
   already written against the port, so this is a port adapter plus an `inspect` investigation).
2. Answer `05` §8 Q1–Q6 against the real app before choosing snapshot depth and postcondition vocabulary.
3. Replace the deterministic note with a model call only after the ledger can prove reuse (§7.3 of `05`);
   until then a model-written note is a cost, not a capability.
4. Add a session lock (single-writer) before any long-lived service embeds the conductor.
