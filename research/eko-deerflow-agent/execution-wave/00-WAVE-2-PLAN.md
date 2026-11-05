# Wave 2 — Execution & Differential Verification Plan

**Date:** 2026-11-05 · **Owner:** Lead · **Mode:** execution evidence, not another literature review.
**Directory:** `research/eko-deerflow-agent/execution-wave/` · **Production edits:** none allowed.

> **Dolphin / whale rule.** Wave 1 asked *“what is a dolphin?”* — inventories, counts, definitions,
> repository state. Wave 2 asks *“how does this dolphin swim, how is it trained, and what is a whale?”*
> — mechanism, executable evidence, differential comparison. Every task below starts from a Wave 1
> answer and asks a **different** question. Re-running an audit is a task failure, not thoroughness.

## Seat plan (reuse, don't clone)

The seven existing seats have the context. Wave 2 **reuses** them with new task IDs; a fresh seat is
added only for independent verification, when a slot frees. No new seat may duplicate an existing
owner's file.

| Seat | Wave 1 asset | Wave 2 task | New question | Output |
|---|---|---|---|---|
| `stack-vps-auditor` | 01 stack/VPS facts | **task-8** execution repair | “Exactly how do we replace the 127 shims, fix argv, and register MCP without breaking the pod?” | `01-EXECUTION-REPAIR.md/.json` |
| `harness-architect` | 04 harness design | **task-9** executable skeleton | “What is the minimal DDL/interface/state machine that makes the design runnable?” | `02-FORGE-SKELETON.md/.json` |
| `craft-surface-auditor` | 03 Craft surface | **task-10** defect corpus | “Which visual defects pass global metrics, and what test catches them?” | `03-VISUAL-DEFECTS.md/.json` + fixtures |
| `learning-loop-researcher` | 06 learning design | **task-11** promotion simulation | “Does the promotion rule behave correctly under synthetic evidence and null results?” | `04-PROMOTION-SIM.md/.json` + `sim/` |
| `agent-repos-scout` | 02 repo verification | **task-12** security/deploy | “What must be hardened/pinned before this is exposed or trusted?” | `05-SECURITY.md/.json` |
| `harness-code-archaeologist` | 05 code mechanisms | **task-13** adapter prototype | “Can the Goose operation-pipeline shape be adapted and tested in our gateway?” | `06-ADAPTER.md/.json` + `adapter/` |
| `examples-skills-packager` | 07 examples/skill specs | **task-14** packaging (after task-7) | “Can the corpus/skills be assembled for Desktop/vault without breaking links or JSON?” | `07-PACKAGE.md/.json` |
| **new** `wave2-verifier` | none | **task-15** independent verification | “Do the six deliverables actually do what they claim, independently?” | `08-VERIFICATION.md/.json` |

**Why no new seats yet:** active child capacity is 7 and all seven are occupied/running. The verifier is
spawned the moment one frees; creating it now would queue/reject and risk duplicate work. Packaging is
blocked by task-7, so it starts only after the examples file is frozen.

## Work packages

### WP-1 — Execution repair (task-8)
- Replace `/opt/pod-pipeline/bin/*-cli` stubs with absolute launchers to `/opt/craft/*/bin`.
- Rewrite `routes.py` argv to actual CLI contracts; no `trace`, no `--input` for PhotoCraft.
- Register VectorCraft/PhotoCraft MCP stdio in DeerFlow with read/write roots.
- Tests: `--version`, `run` trace, `render_preview`, refusal path, MCP `tools/list`.
- Rollback: restore shims + config file; no data migration.
- **Done:** one command of each app runs from the pipeline path; expected outputs quoted.

### WP-2 — Forge skeleton (task-9)
- Exact DDL for episode/event/handoff/tool_call/artifact/gate/critique/eval/skill/job/budget.
- Minimal Python tool-gateway signatures; idempotency key; `E_*` refusals; state transitions.
- Tests with a fake executor (permitted test double) for duplicate call, refusal, crash/resume.
- **Done:** schema applies on a scratch Postgres; tests pass; no production migration.

### WP-3 — Visual defect study (task-10)
- 10–20 synthetic fixtures: white fringe, halo, ghost text, speck, lost stroke, wrong colour, margin.
- Compare global SSIM/RMSE vs tile/diff; report false passes.
- **Done:** measured table with at least one defect global metrics miss; critic criteria updated.

### WP-4 — Promotion simulation (task-11)
- Synthetic episodes; Wilson lower-bound; N≥3; regression/demotion; reward-hacking; null A/B.
- **Done:** runnable simulation with commands/outputs; null result preserved; no Craft-quality claim.

### WP-5 — Security/deploy (task-12)
- `pod-mcp` loopback/auth; Docker-group risk; key validation without spend; version pins; licence/NOTICE.
- **Done:** prioritized checklist with owner/severity/test; no secrets.

### WP-6 — Adapter prototype (task-13)
- Original ordered operation pipeline: operations, persisted state, approval/compaction/retry.
- Tests: crash/resume, duplicate operation, approval refusal.
- **Done:** `py_compile`/test output; no verbatim donor code.

### WP-7 — Packaging (task-14)
- Desktop folder: `C:\Users\Riley\Desktop\Ridgeboundia-Agent-Research\`
  (`00-START-HERE.md`, `research/`, `skills/`, `examples/`, `INDEX.json`, `BIBLIOGRAPHY.md`).
- Vault staging: `/srv/vaults/storefront/30-reference/art-learning/29-AGENT-HARNESS-RESEARCH/`
  (Lead performs final copy/commit; seat produces manifest).
- **Done:** link/JSON/word-count validation; no source-corpus mutation.

### WP-8 — Independent verification (task-15)
- Fresh seat; cannot verify its own writing.
- Re-run tests; re-check file:line; confirm no production edits; validate 200 answers and 5 skills.
- **Done:** contradiction table; `VERIFIED`/`UNVERIFIED` per claim; no self-certification.

## Differential questions (new, not Wave 1 repeats)

1. What is the smallest patch that makes the pipeline execute, and what is the failure mode of each
   replacement (absolute path vs shim vs wrapper)?
2. Which argv claim in `routes.py` is invented, and what is the exact real command?
3. Does registering Craft MCP require a bind mount, host bridge, or stdio proxy — and which is safest?
4. What DDL constraint prevents duplicate promotion/duplicate publish?
5. Which visual defect is invisible to global SSIM, and what tile metric catches it?
6. What is the minimum synthetic evidence that makes the Wilson rule fail a candidate?
7. What does a reward-hacking episode look like in the simulation, and which control catches it?
8. What is the exact DeepSeek key validation that does not spend quota?
9. What is the licence/NOTICE delta for each borrowed mechanism?
10. Does the Goose operation-pipeline shape survive crash/resume/duplicate tests in our adapter?
11. What links/JSON break when the corpus is assembled for Desktop/vault?
12. What did each Wave 2 deliverable claim that independent verification could not reproduce?

## Schedule / gates

| Stage | Tasks | Gate |
|---|---|---|
| 2A (now) | 8, 9, 10, 11, 12, 13 in parallel | each writes its file, runs its own tests |
| 2B | task-14 packaging after 7 | link/JSON/word-count clean |
| 2C | task-15 verifier when a slot frees | independent reproduction; no contradictions unresolved |
| 2D | Lead synthesis + vault/Desktop copy + commit | all gates + final report |

## Explicit non-goals

- Do not re-audit the VPS, re-count commands, re-review the same papers, or re-design the harness.
- Do not edit production code, the pipeline, the console, the DB, or the Craft apps.
- Do not claim the 200 answers are re-verified by this wave; they are a fixed corpus.
- Do not claim learning/print quality from a simulation.
- Do not create a second source of truth; the Lead owns final integration.

## Status reporting

Each seat returns: task id, files, what changed vs its Wave 1 asset, commands/outputs, blockers,
`UNVERIFIED` list. The Lead updates this plan and starts the verifier/packaging when dependencies clear.
