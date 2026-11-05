# ERRATA — append-only corrections

## 2026-11-05 — Promotion rule was unsatisfiable as written

**Original claim** (`wave2/06-LEARNING-LOOPS.md`; `agent-learning-loop` v1; `craft-agent-operator`
`references/memory-ledger.md`): “≥3 independent successes + Wilson 95% lower bound > 0.60 + regression
+ human” is the promotion rule.

**Correction** (`execution-wave/04-PROMOTION-SIM.md`, task-11; 23 tests, 20,000 simulated trials,
seed 20261105):
- 3/3 gives Wilson LB **0.4385**, so `LB > 0.60` cannot pass at N=3; no k passes at n=3, 4 or 5.
- The rule omitted the evaluation horizon `n`. A **simulation-derived** variant `n=8, k≥7, LB>p0`
  gave 3.51% null promotions and 81.14% retention at p=0.90; this is **not adopted** — the owner
  chooses p0/n and the false-promotion budget.
- “2 failures in last 20” false-demoted a 95%-reliable skill **41.22%** over 30 uses. Alternatives:
  3-in-20 15.10%, 2-consecutive 6.88%, CUSUM 22.98%; select and test.
- Regression: 40 goldens at 5%/golden misses **19.48%**; 80 misses **3.87%**; at 2%/golden, 40 misses
  **51.95%**. Suite size is part of the policy.
- Human gate: gate-optimising strategy promoted **85.73%** without it vs **0.01%** with it.

**Changed files:** `blueprint/files/skills/agent-learning-loop/SKILL.md`;
`blueprint/files/skills/craft-agent-operator/references/memory-ledger.md`;
`execution-wave/09-GOAL-GAP-PLAN.md` (D7/T9); `GOALS.md` (success metric).

**Status:** CORRECTED in active guidance; original `06` kept as historical research (not silent
rewrite). The simulation’s probabilities are `ASSUMED`, not measured on Craft episodes.

## 2026-11-05 — README live-E2E claim is historical/unreproducible

The README says a live VPS E2E succeeded through trace/trim/effect and wrote `apparel_final.png`
(`README.md:191–194`). Current verified state: `pod` DB empty, the last real run failed at the first
step on stub `exit 127`, and `/opt/pod-pipeline/bin/*-cli` remain stubs. Treat the claim as
`HISTORICAL/UNREPRODUCIBLE` until a fresh run with the repaired path passes and the DB rows are shown.

## 2026-11-05 — README `AGENTS.md` is a foreign contract

The repo `AGENTS.md` describes a Grok App Builder `/workspace`, port 8080, `startup.sh`, Vercel — not
this VPS/pipeline. Do not use it as the DeerFlow Forge operational contract. The actual VPS contract is
in `wave2/01-STACK-VPS.md` + `execution-wave/09-GOAL-GAP-PLAN.md`.

## 2026-11-05 — Eko docs host unavailable

`eko.fellou.ai` / `fellou.ai/eko` docs returned HTTP 503 on 2026-11-05. Eko claims beyond the
README/package/source/examples remain `UNVERIFIED`; no docs claim is promoted.
