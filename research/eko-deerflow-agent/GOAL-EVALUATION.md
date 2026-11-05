# Goal evaluation and research plan

**Date:** 2026-11-05 · **Status:** evaluation is current; implementation is not started.
**Companions:** [`GOALS.md`](GOALS.md) · [`execution-wave/09-GOAL-GAP-PLAN.md`](execution-wave/09-GOAL-GAP-PLAN.md) ·
[`execution-wave/10-CLAIM-REGISTER.md`](execution-wave/10-CLAIM-REGISTER.md).

## 1. What we set out to achieve

Build an AI agent that can design and ship real Craft work, learn from its runs, remember what
works, use the existing VPS + DeepSeek V4.1 Flash, and be truthful about its limits.

## 2. Goal-by-goal outcome

| Goal | Desired outcome | Current outcome | Status | Evidence |
|---|---|---|---|---|
| **G1** Execute Craft | run trace/retouch/print through the pipeline | direct real VC trace + PC retouch + 10/10 CraftTrace checks on staging; production path still stubbed | **PARTIAL (staging)** | `11-G0-EVIDENCE.md`; `01-EXECUTION-REPAIR.md` |
| **G2** Native tools | typed CLI/MCP surface, no GUI guessing | 33/26 MCP tools listed; PhotoCraft `command_batch` works; DeerFlow registration not applied | **PARTIAL** | S3; `11-G0-EVIDENCE.md`; `02-FORGE-SKELETON` |
| **G3** Verify | artifact + gates + render + blind critic + human | gates exist but can be vacuous/pre-artifact; no integrated critic | **PARTIAL** | S3; `03-VISUAL-DEFECTS`; `04` |
| **G4** Learn | improve from verified episodes, remember | no episode/eval/skill tables; DeerMem facts only; L0 | **NOT STARTED (L0)** | S1; S6; `04-PROMOTION-SIM` |
| **G5** Host | run on the existing VPS/key | DeerFlow 2.2 + `deepseek-flash` running; 2 vCPU/no GPU; key unverified | **FEASIBLE** | S1; S12 |
| **G6** Publish safely | human-approved, verified product | no approval queue; templates unset; no autonomous publish | **BLOCKED** | S1; S12 |
| **G7** Truth | labels, claims, gaps, no invention | 400 answers, claim register, errata; README claim still needs correction | **IMPROVING** | REPORT; 10-claim; ERRATA |

## 3. What we actually know

### Verified

- The VPS is 2 vCPU / 7.9 GB / 36 GB free, no GPU/display.
- DeerFlow 2.2.0 runs `deepseek-flash` (“DeepSeek V4.1 Flash”), 1,048,576 ctx, 8,192 output.
- VectorCraft 0.21.1 and PhotoCraft 0.20.2 are installed; their MCP servers work standalone.
- `/opt/pod-pipeline/bin/*-cli` are stubs exiting 127; `routes.py` argv is invented.
- Only `forge` MCP (3 pipeline tools) is registered in DeerFlow.
- `pod` DB is empty; no episode/eval/skill tables.
- 39 skills, 400 answers, 8 diagrams, 6 examples, 131-file package.
- Adapter: 30/30 tests. Promotion sim: 23/23 tests. Visual composite: 15/15 with 0/4 false alarms
  on the synthetic corpus.

### Not verified / not true

- The DeepSeek key’s live validity.
- The README’s live E2E claim (historical/unreproducible now).
- FilmCraft/DesignCraft/EffectCraft availability.
- Real gate/human rates, human inter-rater agreement, cost per accepted artifact.
- “The agent learns art direction” and “better than a human designer.”
- A production DDL migration or live deployment.

## 4. What is possible now

1. **Fix the execution path** on a staging copy; run one real trace and one retouch; capture artifacts.
2. **Register the Craft MCP servers** and prove `tools/list`/`command_batch`.
3. **Run the Forge skeleton** DDL/tests against a scratch Postgres; prove duplicate/refusal/crash.
4. **Run the visual critic** on the 19-case synthetic corpus; require 15/15 and 0/4.
5. **Run the promotion simulation** and choose a policy; 3/3 is not a policy.
6. **Validate the key without spend** via `/user/balance` and `/models`.

## 5. What is not possible on this VPS now

- Driving FilmCraft/DesignCraft/EffectCraft: not installed.
- Fine-tuning/RL: API model, no GPU/open weights/corpus.
- Pixel-first GUI automation: no display; control bridge missing a library.
- Autonomous publish: no approval queue; template ids unset.
- A claim of artistic superiority: no blind study.

## 6. The best path (decision)

**DeerFlow 2.2 as front door/runtime + Forge Conductor as a third plane + native Craft CLI/MCP +
Postgres ledger/queue + DeerMem facts + versioned skills.** Do not build a new generic harness; do
not start with GUI or training; do not make the pipeline the agent.

## 7. Research continuation plan

These are new questions, not repeats of the 400.

| # | Question | Method | Output | Stop condition |
|---|---|---|---|---|
| R1 | Does the repaired launcher/argv execute a real trace? | staging copy + real CLI; artifact + JSON | `R1-RESULT.md` | first missing artifact |
| R2 | Can DeerFlow load a stdio MCP server with roots? | register + `tools/list` + batch | `R2-RESULT.md` | handshake failure |
| R3 | Does DDL apply twice and enforce transitions? | scratch PG16 + duplicate/refusal tests | `R3-RESULT.md` | SQL assertion fail |
| R4 | Does the visual composite generalize? | new photographic/gradient corpus + human labels | `R4-RESULT.md` | false alarm > budget |
| R5 | What promotion policy is defensible? | simulate n/k/p0, then real episodes | `R5-RESULT.md` | no separation from null |
| R6 | Does retrieval improve first-attempt pass? | A/B 10–50 goldens, two arms | `R6-RESULT.md` | no gain → disable |
| R7 | Does the blind critic agree with humans? | blind ratings, precision/recall | `R7-RESULT.md` | low agreement → needs_human |
| R8 | What is the real cost per accepted artifact? | usage ledger + balance delta | `R8-RESULT.md` | budget cap exceeded |
| R9 | Is the key valid without spend? | `/user/balance` + `/models` | `R9-RESULT.md` | 401/402 |
| R10 | Can publish be made safe? | approval bind + read-back | `R10-RESULT.md` | any unapproved write |

## 8. Re-evaluation rule

Re-run this evaluation after every phase. A goal moves from `BLOCKED/PARTIAL` to `ACHIEVED` only when
the named gate has a reproduced command/output and the claim register is updated. A null result is a
valid outcome; a design is not an achievement.

## 9. Current verdict

**Research/design: strong. Execution: blocked at Phase 0. Learning: not started. Product: feasible
narrowly (VectorCraft + PhotoCraft) once the execution path and approval are real.**
