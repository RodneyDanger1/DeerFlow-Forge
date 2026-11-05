# START HERE — Ridgeboundia Agent Harness Research

**Date:** 2026-11-05 · **Status:** research + execution evidence + integration plan complete; Phase 0
staging gate passed for one real trace/retouch; **no production deploy**. **Owner:** Riley ·
**Canonical repo path:** `research/eko-deerflow-agent/`.

## What this corpus is for

Answer one question with evidence: **what must we build so an AI agent can reliably operate the Craft
apps, learn from its runs, and ship print-ready work on the existing VPS?**

The answer is not “a new superagent.” It is a **Forge Conductor** control plane on the existing
DeerFlow 2.2 + DeepSeek runtime, with a typed Craft gateway, evidence ledger, blind visual critic,
human approval and calibrated L1/L2 learning.

## Read in this order

| Order | File | Why |
|---|---|---|
| 1 | `README.md` | master map: outcome, 6 integrations, 8 Python + 8 agent changes |
| 2 | `GOALS.md` | durable goals, non-goals, scope, success metrics |
| 3 | `ARCHITECTURE.md` | as-is/target system, contracts, failure modes, rollback |
| 4 | `GOAL-EVALUATION.md` | goal-by-goal outcome + R1–R10 research plan |
| 5 | `execution-wave/09-GOAL-GAP-PLAN.md` | decision-complete goal→code plan |
| 6 | `PLAIN-ENGLISH.md` | full human explanation |
| 7 | `execution-wave/RECON-LEDGER.md` | entry points, call chain, tests, unknowns |
| 8 | `execution-wave/01-EXECUTION-REPAIR.md` | measured CLI contracts and Phase 0 plan |
| 9 | `execution-wave/10-CLAIM-REGISTER.md` | what is proven / contradicted / missing |
| 10 | `wave2/01`–`03` | VPS, harnesses, Craft surface evidence |
| 11 | `wave2/04`–`06` | full design, code mechanisms, learning |
| 12 | `wave2/07` + `examples/` | six worked examples |
| 13 | `wave2/08-200-QUESTIONS.md` + `REPORT.md` | 400 answered questions |
| 14 | `execution-wave/04-PROMOTION-SIM.md` | simulation that corrected the 3/3 rule |
| 15 | `execution-wave/05-SECURITY.md` | key validation, MCP auth, dependency/security |
| 16 | `execution-wave/08-VERIFICATION-INDEPENDENT.md` | fresh-seat verification |
| 17 | `diagrams/` + `INTEGRATIONS.mmd` | 8 system diagrams + 1 integration map, validated |
| 18 | `PDF-CATALOGUE.md` + `docs/pdf/` | 29-page indexed binder and text audit |
| 19 | `ERRATA.md` | corrections and historical claims |

## The product outcome

A hosted operator that takes a brief → selects exact command ids → runs on copies → verifies artifact,
gates, render and blind critique → records a hash-chained episode → proposes only evidence-backed
lessons → requires human approval for print/publish. It is **not** an autonomous artist and does not
claim to beat a human designer.

## Current truth (read this before promising anything)

- DeerFlow 2.2 is running with `deepseek-flash` (“DeepSeek V4.1 Flash”, 1,048,576 ctx, 8,192 output);
  key validity is **unverified**.
- VectorCraft 0.21.1 + PhotoCraft 0.20.2 are installed; Film/Design/Effect are **not**.
- Production `/opt/pod-pipeline/bin/*-cli` may still be stubs; `deploy/craft-launchers` are pinned;
  `routes.py` argv was corrected and staging-proven. Production deploy not applied.
- Craft MCP works standalone but is **not registered** in DeerFlow.
- Local Forge core exists: gateway, DDL, repository, worker, loopback service, verifier contract and
  blind-critic contract; all tested on scratch PostgreSQL/local HTTP. **No production service.**
- `pod` DB is untouched; local `forge` schema is not a production database; no learning/eval claim
  beyond **L0**; console is a viewer.
- 39 skills and 400 answers are research/instructions, not a running learner.
- Phase 0 execution repair is staging-proven; Phase 1 local core is implemented, not deployed;
  learning remains L1/L2 research only.

## Evidence labels

`VERIFIED` (executed/read this wave) · `READ` (source read) · `INFERRED` · `UNVERIFIED` ·
`HISTORICAL` · `PROPOSED` (design). Never promote a lower label without evidence.

## Gaps (open)

DeepSeek key validity; Film/Design/Effect; stdio MCP registration; PhotoCraft concurrency under load;
SVG flatten fidelity; human agreement; real gate/human rates; cost per artifact; publish templates.

## Maintenance

Add new research as a new file/wave; append corrections to `ERRATA.md`; never delete an old answer;
re-fetch before changing a policy; update this map and `INDEX.json` on every addition.
