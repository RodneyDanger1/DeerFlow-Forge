# Craft Command Gateway adapter — prototype

Original prototype of the **ordered re-entrant operation pipeline** for the Craft
Command Gateway. The mechanism is borrowed at the level of *idea* from the
harness archaeology in [`../../wave2/05-HARNESS-CODE.md`](../../wave2/05-HARNESS-CODE.md)
§M1 (Goose's state machine); no donor source is copied. See
[`../06-ADAPTER.md`](../06-ADAPTER.md) for the design rationale and evidence.

Zero runtime dependencies. Node ≥ 20 (tested on Node 26.7.0).

## Run the tests

```powershell
cd "research\eko-deerflow-agent\execution-wave\adapter"
node --test "test/*.test.mjs"        # 29 tests
node --test "test/crash-resume.test.mjs"   # crash/resume only
```

or, with npm:

```powershell
cd "research\eko-deerflow-agent\execution-wave\adapter"
npm test
```

## Layout

```
src/envelope.mjs    command envelope + status vocabulary + plan validation + idempotency key
src/store.mjs       session persistence (MemoryStore, FileStore atomic commit, schema fail-closed)
src/ports.mjs       Craft port / approval policy / verifier / continuation-note ports + reference doubles
src/operations.mjs  the eight ordered operations (reconcile, approval, retry, compaction, checkpoint, verify, dispatch, finalize)
src/machine.mjs     step/apply/run, one event per step, resume
src/gateway.mjs     wiring: createCraftConductor(), PIPELINE, summarizeRun()
test/               envelope, machine, approval/compaction/retry, duplicate, crash/resume
test/fixtures/      file-backed Craft double + real crash child process + shared harness
```

## The one invariant to remember

`dispatch` writes a **write-ahead intent** to the session *before* calling Craft.
If the process dies after the app changed but before the result is recorded, the
next run's `reconcile` operation asks the app (`inspect`) or verifies the declared
postconditions — it never re-fires the command blindly. If neither can prove what
happened, the episode **halts** with `MANUAL_RECONCILE` rather than guessing.
