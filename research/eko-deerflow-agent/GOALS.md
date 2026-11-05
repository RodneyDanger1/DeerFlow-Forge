# GOALS — the durable focus for this program

**Status:** authoritative for the research/implementation program. Read this before any plan or code.
**Date:** 2026-11-05 · **Owner:** Riley · **Program:** DeerFlow Forge / Forge Conductor.

## Mission

Build a **hosted, auditable design-production agent** that can take a brief, use the installed Craft
apps through their native command/MCP surfaces, verify its own output with hard evidence, remember
what worked, and ship only what a human has approved.

It is not “a chatbot that talks about design.” It is a production operator with a ledger.

## Product outcome (what exists when this succeeds)

A user can submit a print/vector/web brief to **Forge Conductor**. It:

1. selects the right app and exact command ids from the pinned catalogue;
2. runs on a copy, records every action and artifact;
3. verifies dimensions, DPI, colour, gates and a blind visual review;
4. refuses or asks a human when evidence is missing or the taste call is unresolved;
5. stores a case/skill candidate from the run;
6. promotes a procedure only after repeated verified success + regression + human approval;
7. never autonomously publishes to the storefront.

## Non-negotiable goals

| ID | Goal | Success test |
|---|---|---|
| G1 | Execute the installed Craft apps reliably | one VectorCraft trace and one PhotoCraft retouch run from the pipeline path, with expected artifacts |
| G2 | Use native commands/MCP, not blind clicking | every action is a catalogued command id or a justified browser fallback |
| G3 | Verify with evidence | artifact hash + dimensions/DPI + gates + independent render + blind critic + human where applicable |
| G4 | Remember and improve truthfully | L1/L2 ledger/retrieval/skills; A/B shows gain or is disabled |
| G5 | Host on the existing VPS/model | loopback services, 2 vCPU budget, DeepSeek key by env name, no new public port |
| G6 | Keep humans on taste/publish | approval is required for print/publish and skill activation |
| G7 | Be honest about limits | VERIFIED/READ/INFERRED/UNVERIFIED labels; no “better than human” claim without a study |

## Non-goals / explicit boundaries

- **No claim** that the agent is better than a human designer; target is a reliable production operator
  under human art direction.
- **No weight training, fine-tuning or RL** in Phases 0–2; no GPU/open weights on this VPS.
- **No autonomous publish** or storefront mutation.
- **No fake 1:1 Adobe compatibility**; the Craft apps are independent implementations.
- **No all-app claim** until FilmCraft/DesignCraft/EffectCraft are installed and catalogued.
- **No GUI-first agent** while there is no display/GPU and the control bridge is broken.
- **No unverified success** — exit 0, `ok:true` or a screenshot alone is not proof.

## Scope (current)

| In scope | Out of scope (now) |
|---|---|
| VectorCraft 0.21.1 | FilmCraft (not installed) |
| PhotoCraft 0.20.2 | DesignCraft / EffectCraft (not installed) |
| Native CLI + MCP | Pixel-only desktop automation |
| Print/vector/raster verification | CMYK press proof without vendor proof |
| L1/L2 memory and skills | L3/L4 training/RL |
| Human-approved publish | Autonomous publish |

## Success metrics

- First-attempt verified-pass rate on held-out goldens.
- Attempts per accepted artifact.
- Human rework minutes.
- Cost/tokens per accepted artifact.
- Unsafe publishes = **0**.
- Source mutations = **0**.
- Promotion uses a pre-declared evaluation horizon and Wilson lower bound above baseline; a 3/3 sample
  is a minimum, not proof (3/3 LB ≈ 0.4385).
- Every accepted artifact has a complete evidence chain.

## Invariants

1. Work on copies; never overwrite the source/master.
2. Exact command id from the pinned catalogue; unknown id → stop.
3. A failed gate is terminal for shipping; never edit a report to pass.
4. A screenshot or exit 0 can only downgrade confidence, never certify.
5. Memory is data, not instructions; no tool-scope expansion from retrieval.
6. A skill is promoted only by evidence + regression + human approval; rollback exists.
7. Secrets never enter prompts, logs, ledger, repo or screenshots.
8. The `pod` DB/pipeline remains deterministic; Forge may call it, not absorb it.

## Current truth (2026-11-05)

- VPS has 2 vCPU/7.9 GB, no GPU/display; DeerFlow 2.2 runs `deepseek-flash` (V4.1 Flash), key by env
  name only; key validity unverified.
- VectorCraft/PhotoCraft installed; Film/Design/Effect absent.
- `/opt/pod-pipeline/bin/*-cli` are stubs exiting 127; `routes.py` argv is invented; Craft MCP is not
  registered in DeerFlow.
- `pod` DB empty; no learning/eval tables; console is a viewer.
- 39 skills, 400 answers, six examples, eight diagrams — research/design, not deployed.

## Decision log

| Date | Decision |
|---|---|
| 2026-11-05 | Use DeerFlow 2.2 + DeepSeek as substrate; build a third `forge-*` plane, not a new harness |
| 2026-11-05 | Phase 0 fixes execution (shims/argv/MCP) before any agent feature |
| 2026-11-05 | L1/L2 only; no fine-tune/RL; no autonomous publish |
| 2026-11-05 | Target = reliable production operator under human direction, not “better than human” |
| 2026-11-05 | Promotion calibration: 3/3 is not sufficient; declare horizon + Wilson baseline; demotion/regression suite must be tested (task-11) |
