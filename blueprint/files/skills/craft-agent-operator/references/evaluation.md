# Evaluation protocol

**Status:** proposed. The repository has technical tests and Craft gates, but no design-quality
benchmark yet. This document defines the minimum evaluation that would let a claim of “learning” or
“improvement” be tested.

## What is measured

| Dimension | Metric | Evidence |
|---|---|---|
| Reliability | first-attempt gate pass rate | `craft_trace`/`prep_print_art` report |
| Efficiency | attempts per accepted artifact | ledger `agent_action` |
| Cost | model tokens + wall seconds per accepted artifact | ledger `cost` |
| Quality | blind human rubric (1–5) | two reviewers, disagreements recorded |
| Safety | source overwritten / unsafe publish count | must be **0** |
| Regression | old goldens still pass | suite run |

## Golden task record

```json
{
  "id": "vc-ai-badge-001",
  "task_family": "ai_badge_trace",
  "app": {"name": "VectorCraft", "version": "0.21.1"},
  "input": {"path": "fixtures/badge.png", "sha256": "..."},
  "brief": "8 in front print, 2400x3000 canvas, transparent white, 10/10 gates",
  "reference_plan": ["prep_print_art", "imageTrace.make", "imageTrace.expand", "document.export"],
  "required_gates": {"ok": true, "dpi": 300, "retype_boxes": ">0 if text"},
  "human_rubric": {"brief_fit": 0, "hierarchy": 0, "typography": 0, "colour": 0, "print_safety": 0},
  "rights": {"source": "...", "licence": "..."},
  "accepted_artifact": "sha256-or-null"
}
```

Fixtures must have recorded rights; do not use Adobe tutorial media or customer art without permission.

## Baseline

Before adding memory/skills, run every golden **without** retrieval/lessons:

- record pass/fail, attempt count, gate values, duration, tokens;
- record the exact failure code for failures;
- store the baseline artifact hash for regression comparison.

Do not compare a memory-enabled run against a different model/version; freeze model, app and catalogue.

## A/B protocol

1. Same model, app version and inputs.
2. Arm A: no retrieval/lessons; Arm B: retrieval + active skills only.
3. Run each golden at least 3 times (variance matters); randomise order.
4. Blind the human reviewer to arm.
5. Report pass rate with confidence interval, median attempts, cost, and human scores.
6. Reject a lesson if it improves one task and regresses another.

A single successful demo is an anecdote, not evidence.

## Human rubric

Score 1–5 with written anchors; require two reviewers for promoted skills:

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| Brief fit | wrong deliverable | mostly right | exactly the brief |
| Hierarchy | unreadable | usable | clear at thumbnail |
| Typography | broken/overflow | correct | crafted |
| Colour | off-brand | acceptable | brand-accurate and balanced |
| Print safety | unsafe | minor risk | production-safe |

Report inter-rater disagreement; do not hide it in an average.

## Anti-reward-hacking

- Do not optimize only path count, coverage, speed, or file size.
- A gate pass with a visibly bad artifact is a failure; keep human review.
- Reject lessons that exploit a threshold, change the gate, or narrow the brief.
- Hold out a private golden set the agent cannot retrieve.
- Log every tool call; a suspiciously short run is reviewed.

## Test cases for the evaluation harness

| Test | Expected |
|---|---|
| no golden fixtures | refuses with `E_EVAL_EMPTY`; no fake score |
| gate missing from report | marks `UNVERIFIED`, not pass |
| artifact hash differs | regression flagged |
| model/app version changed | baseline invalidated; new label |
| retrieval returns no cases | run baseline arm; no invented precedent |
| contradictory lessons | conflict reported; neither auto-promoted |
| unsafe publish attempt | blocked; `E_PUBLISH_NOT_APPROVED` |
| same input twice | deterministic command results or documented variance |

## Reporting

Every evaluation report must include: model id, app versions, catalogue hash, golden set version,
arm assignment, sample size, per-task results, aggregate with CI, human scores, cost, failures and an
explicit `UNVERIFIED` list. A report without those fields is not a benchmark.

## Claim rule

- “Improved” requires a statistically credible gain on held-out tasks.
- “Learns” requires the gain to persist and transfer to new briefs, not just memorise fixtures.
- “Better than human” requires a blind, representative study; none exists here.
