# START HERE — Ridgeboundia Agent Harness Research

**Date:** 2026-11-05 · **Status:** research + execution plans complete/in progress; no production deploy.
**Owner:** Riley · **Canonical repo path:** `research/eko-deerflow-agent/`.

## What this corpus is for

Answer one question with evidence: **what must we build so an AI agent can reliably operate the Craft
apps, learn from its runs, and ship print-ready work on the existing VPS?**

The answer is not “a new superagent.” It is a **Forge Conductor** control plane on the existing
DeerFlow 2.2 + DeepSeek runtime, with a typed Craft gateway, evidence ledger, blind visual critic,
human approval and calibrated L1/L2 learning.

## Read in this order

| Order | File | Why |
|---|---|---|
| 1 | `GOALS.md` | durable goals, non-goals, scope, success metrics |
| 2 | `execution-wave/09-GOAL-GAP-PLAN.md` | goal→research→code→product gap matrix and decision-complete plan |
| 3 | `execution-wave/RECON-LEDGER.md` | entry points, call chain, tests, unknowns |
| 4 | `execution-wave/01-EXECUTION-REPAIR.md` | measured CLI contracts and Phase 0 repair plan |
| 5 | `wave2/01`–`03` | VPS, harnesses, Craft surface evidence |
| 6 | `wave2/04` | full Forge Conductor design |
| 7 | `wave2/05`–`07` | code mechanisms, learning, examples |
| 8 | `wave2/08-200-QUESTIONS.md` + `REPORT.md` | 400 answered questions |
| 9 | `execution-wave/04-PROMOTION-SIM.md` | simulation that corrected the 3/3 promotion rule |
| 10 | `execution-wave/05-SECURITY.md` | key validation, MCP auth, dependency/security |
| 11 | `diagrams/` | eight validated flow/architecture/state diagrams |
| 12 | `ERRATA.md` | corrections, including the promotion rule and README claim |

## The product outcome

A hosted operator that takes a brief → selects exact command ids → runs on copies → verifies artifact,
gates, render and blind critique → records a hash-chained episode → proposes only evidence-backed
lessons → requires human approval for print/publish. It is **not** an autonomous artist and does not
claim to beat a human designer.

## Current truth (read this before promising anything)

- DeerFlow 2.2 is running with `deepseek-flash` (“DeepSeek V4.1 Flash”, 1,048,576 ctx, 8,192 output);
  key validity is **unverified**.
- VectorCraft 0.21.1 + PhotoCraft 0.20.2 are installed; Film/Design/Effect are **not**.
- `/opt/pod-pipeline/bin/*-cli` are stubs (exit 127); `routes.py` argv is invented; Craft MCP is not
  registered.
- `pod` DB is empty; no learning/eval tables; console is a viewer.
- 39 skills and 400 answers are research/instructions, not a running agent.
- Phase 0 is execution repair; Phase 1 is gateway/verifier; learning is L1/L2 only.

## Evidence labels

`VERIFIED` (executed/read this wave) · `READ` (source read) · `INFERRED` · `UNVERIFIED` ·
`HISTORICAL` · `PROPOSED` (design). Never promote a lower label without evidence.

## Gaps (open)

DeepSeek key validity; Film/Design/Effect; stdio MCP registration; PhotoCraft concurrency under load;
SVG flatten fidelity; human agreement; real gate/human rates; cost per artifact; publish templates.

## Maintenance

Add new research as a new file/wave; append corrections to `ERRATA.md`; never delete an old answer;
re-fetch before changing a policy; update this map and `INDEX.json` on every addition.
