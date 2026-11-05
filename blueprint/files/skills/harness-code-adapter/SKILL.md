---
name: harness-code-adapter
description: "Use when borrowing a mechanism from another agent harness or repo: map the donor pattern to our contracts, write an original adapter, record provenance/license metadata, pin the source, and prove it with tests without copying proprietary code verbatim. Triggers: code donor, adapt harness, borrow mechanism, vendor a repo, wrap a framework, code stitching, port an agent loop, donor repo."
version: 1.0.0
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [harness, code, adapter, donor, provenance, architecture]
    related_skills: [forge-harness-architect, research-corpus-navigator, agent-learning-loop, visual-verification-critic]
---

# Harness code adapter

A donor repo is an **architecture source**, not a file to paste. Extract the mechanism, express it in our
interfaces, and prove it behaves. This is how to stitch code without creating an unmaintainable fork.

## When to use / not use

- Use when a pattern from DeerFlow, Eko, Harness², OpenAdapt, OpenHands, SWE-agent, Playwright MCP or a
  similar repo is worth reusing.
- Use when deciding vendor/fork/adapter/rewrite.
- Not for copying a whole runtime, or for a one-line dependency addition (just add it and test).

## Selection rules

1. **Prefer interface over implementation** — call the donor through MCP/CLI/HTTP/API where possible.
2. **Pin** the repo/commit/tree SHA and record it; never “latest main” in a design.
3. **License metadata** is recorded for redistribution; do not reproduce large verbatim code blocks.
4. **One mechanism at a time** — a donor’s loop, tool schema, checkpoint or verifier, not its worldview.
5. **No second source of truth** — the donor may not own our durable state.
6. **Behavior is unproven until run** — code reading is not a test.
7. **Delete the adapter if it adds no measured reliability**; no compatibility theater.

## Adapter contract

```text
probe()      -> {name, version, capabilities, limits, refusal_codes}
plan(task)   -> typed plan using only our command/capability ids
execute(op)  -> {ok, result, artifacts[], refusal?} with idempotency key
verify(op)   -> evidence: artifact hash + gates + read-back
normalize()  -> map donor errors/state to our E_* codes and state machine
```

The conductor sees only these five methods. Donor types, retries, logs and prompts do not leak upward.

## Procedure

1. **Recon** — read the donor’s loop/tool/state code, not just README; record `path:line`, commit, license.
2. **Extract the invariant** — what does the mechanism guarantee (“tool results are validated”, “a save is
   read back”, “context is compacted before overflow”)? Write it in one sentence.
3. **Map to our interfaces** — which contract field/state/table represents it? If none, propose a change;
   do not smuggle it into an unrelated field.
4. **Write the adapter skeleton** with the five methods and named refusals; no unfinished bodies.
5. **Test the invariant** — a failing case (bad result, missing artifact, duplicate call) and a passing
   case. A golden test is not enough.
6. **Prove integration** — one real call through the conductor, with ledger rows and evidence hashes.
7. **Record** — source, commit, license, mechanism, files, tests, known differences, rollback (delete
   adapter / feature flag).

## What to borrow, by donor

| Donor | Mechanism | Adapter shape |
|---|---|---|
| DeerFlow | checkpointed runtime, subagents, memory substrate | front door only; do not make it ledger owner |
| Eko | dependency graph, pause/abort, task snapshot | planner/handoff pattern, not the JS runtime |
| Harness² | 8 components + Propose–Probe–Compose | improvement loop around our verifier |
| OpenAdapt | compile/read-back/stop-on-uncertainty | verifier + approval gate |
| OpenHands/SWE-agent | tool loop + test-driven verification | executor/verifier pattern |
| Playwright MCP | a11y snapshots, read-only hints | web fallback adapter |

## What not to do

- Paste a donor’s agent loop into `pod_pipeline`.
- Make the donor’s memory the source of truth.
- Hide a donor’s failure behind a “best effort” catch.
- Strip license/attribution from redistributed code.
- Claim the donor’s benchmark transfers to Craft.
- Add a runtime “just in case” without a measured need.

## Example (original, pseudo-TypeScript)

```ts
interface DonorAdapter<Op, Result> {
  probe(): Promise<{name: string; version: string; caps: string[]}>;
  plan(task: TaskEnvelope): Promise<Plan>;
  execute(op: Op, key: string): Promise<Result>;
  verify(op: Op, result: Result): Promise<Evidence>;
  normalize(err: unknown): Refusal;
}

class CraftCommandAdapter implements DonorAdapter<CommandOp, CommandResult> {
  async probe() { return {name: "craft", version: await this.versionProbe(), caps: ["run","export"]}; }
  async execute(op: CommandOp, key: string) {
    if (await this.seen(key)) return this.prior(key);
    const argv = this.buildArgv(op);                 // absolute binary path, validated ids
    const out = await this.run(argv, {timeoutMs: op.timeoutMs});
    return this.normalizeResult(out);                // never return raw prose
  }
  async verify(op: CommandOp, res: CommandResult) {
    return this.artifactLadder(res.artifacts, op.expectedGates);
  }
}
```

## Output contract

Report: donor + pinned commit/license, invariant, adapter files, tests + commands, observed outputs,
known behavioural differences, and rollback. Mark unrun code `UNVERIFIED`.

## Sources

`wave2/05-HARNESS-CODE.md`, `wave2/02-AGENT-REPOS.md`, `wave2/04-HARNESS-DESIGN.md`; local interfaces.
