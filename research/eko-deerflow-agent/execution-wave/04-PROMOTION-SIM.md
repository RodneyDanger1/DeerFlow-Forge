# Execution Wave / 04 — Promotion-Policy Simulation and Null-Result A/B

**Task:** `task-11` (revision 2, owner `learning-loop-researcher`)
**Date:** 2026-11-05, 10:33–10:55 America/Chicago ≈ 16:33–16:55 UTC
**Mode:** execution evidence, not another literature review. This file **executes** the policy specified in `wave2/06-LEARNING-LOOPS.md` §10; it does not re-review papers.
**Inputs:** `wave2/06-LEARNING-LOOPS.md` §10.1–§10.4 (acceptance, promotion, demotion), `blueprint/files/skills/craft-agent-operator/references/evaluation.md` (A/B, claim rules).
**Writes:** `execution-wave/sim/{promotion.py, simulate.py, test_promotion.py, README.md}`, `execution-wave/04-PROMOTION-SIM.md`, `execution-wave/04-PROMOTION.json`. **No production edits.**

> **Non-claim.** Every number below is the arithmetic consequence of assumed success probabilities on synthetic episodes. No Craft artifact was produced or judged; no model, gate, MCP server or human was executed. This is **not** evidence that Craft quality improved, and the "calibrated" variant is a simulation-derived suggestion, not an accepted policy.

## Evidence labels

| Label | Meaning |
|---|---|
| `RUN` | Observed in this session's command output (quoted). |
| `CODE` | Implemented at the cited file:function. |
| `ASSUMED` | A probability or hazard chosen for the synthetic model; not measured from real runs. |
| `INFERRED` | Consequence of `RUN`/`CODE`/`ASSUMED`, not independently reproduced. |
| `UNVERIFIED` | Not established by this work. |

---

## 1. What was built

| File | Role |
|---|---|
| `sim/promotion.py` | Wilson lower bound, two-proportion z test, the documented N-success + ratio + Wilson promotion rule, the acceptance function, and the demotion monitor (rolling window, consecutive, CUSUM). Pure standard library. |
| `sim/simulate.py` | Nine deterministic Monte-Carlo scenarios (S1–S8 plus a power check) and the JSON writer. |
| `sim/test_promotion.py` | 23 unit tests pinning the arithmetic and failure paths. |
| `sim/README.md` | Run instructions. |
| `04-PROMOTION.json` | Machine-readable results: seed, trial count, per-scenario tables, generated findings, limitations. |

The policy parameters are the ones written in `06`: `p0 = 0.50`, `delta = 0.10` (Wilson threshold 0.60), `N_min = 3`, `ratio_min = 0.75`, `z = 1.96`. The demotion rules tested are the document's "2 failures in the last 20 uses" plus three alternatives.

## 2. How to run

```powershell
cd "C:\Users\Riley\Desktop\DeerFlow Forge\research\eko-deerflow-agent\execution-wave\sim"
python -m unittest -v test_promotion     # 23 tests
python simulate.py                       # writes ../04-PROMOTION.json, seed 20261105, 20,000 trials
```

`RUN` unit tests: `Ran 23 tests in 0.002s / OK` (exit 0).
`RUN` determinism: running `python simulate.py` twice produced an identical `results` hash (`8147c9273557b649`); only `generatedAtUtc` differs by design.
`RUN` full simulation exit 0, `trials=20000`, `seed=20261105`.

## 3. Method and assumptions

- Monte Carlo over independent Bernoulli success draws. RNG is `random.Random(seed + scenario offset)`; no clock, network or model call.
- The acceptance and promotion functions are the ones in `promotion.py`; scenarios only supply synthetic `(gates, human, rights)` outcomes.
- `ASSUMED` reward-hacking model: honest strategy gate 0.80 / human 0.90; gate-optimising strategy gate 0.95 / human 0.05.
- `ASSUMED` demotion model: healthy skill `p = 0.95` for 30 uses, then drift to `p = 0.30` for up to 30 uses.
- `ASSUMED` regression model: 80% of goldens were previously passing; a risky skill regresses each with probability `r`.
- `ASSUMED` A/B model: two identical arms at `p = 0.70` (null) and a real `0.70 vs 0.85` difference (power).

---

## 4. Results

### S1 — Wilson lower bound against the documented threshold (0.60)

`RUN`:

```text
k   n   k/n    wilson_lb  passes
3   3   1.000  0.4385     False
4   5   0.800  0.3755     False
7   8   0.875  0.5291     False
8   8   1.000  0.6756     True
9   10  0.900  0.5958     False
10  10  1.000  0.7225     True
19  20  0.950  0.7639     True
20  20  1.000  0.8389     True
```

### S2 — Minimum k that passes the Wilson guard, by evaluation horizon n

`RUN`:

```text
n   k_min  k_min/n   achievable
3   None   -         False
4   None   -         False
5   None   -         False
6   6      1.0       True
7   7      1.0       True
8   8      1.0       True
9   9      1.0       True
10  10     1.0       True
11  10     0.9091    True
12  11     0.9167    True
```

### S3 — Policy calibration: promotion rate by rule reading

`RUN`:

```text
variant        n  p=0.50  p=0.60  p=0.75  p=0.90
count_only_n3  3  0.1221  0.2192  0.4193  0.7286
doc_rule_n3    3  0.0000  0.0000  0.0000  0.0000
doc_rule_n8    8  0.0042  0.0160  0.0981  0.4275
calibrated_n8  8  0.0351  0.1061  0.3639  0.8114
```

- `count_only_n3` = promote when the first 3 uses all succeed (the N-success rule with the Wilson guard removed).
- `doc_rule_n3` = the `06` rule evaluated at `n = 3`.
- `doc_rule_n8` = the `06` rule evaluated at `n = 8`.
- `calibrated_n8` = simulation-derived variant: `n = 8`, `k ≥ 7`, `WilsonLB > p0` (delta 0).

### S4 — Regression gate: probability a risky skill is promoted unseen

`RUN`:

```text
suite  regression/golden  p(zero observed failures)
20     0.02               0.7211
20     0.05               0.4415
20     0.10               0.1879
40     0.02               0.5195
40     0.05               0.1948
40     0.10               0.0342
80     0.02               0.2774
80     0.05               0.0387
80     0.10               0.0019
```

### S5 — Demotion: false alarms on a healthy skill, detection after drift

`RUN`:

```text
rule                false_demotion  median_delay  p90_delay  never_detected
window_2_of_20      0.4122          2.0           4.0        0.0000
window_3_of_20      0.1510          3.0           5.0        0.0000
consecutive_2       0.0688          2.0           6.0        0.0000
cusum_k_0.15_h_1.0  0.2298          2.0           4.0        0.0000
```

`false_demotion` is "triggered at least once during 30 uses at p=0.95"; `median_delay` is uses after the drift to p=0.30, conditional on detection.

### S6 — Reward-hacking scenario: acceptance and promotion with/without the human gate

`RUN`:

```text
strategy        accept_with  accept_without  promote_with  promote_without  disagreement
honest          0.7171       0.7974          0.3688        0.5081           0.0802
gate_optimiser  0.0476       0.9501          0.0001        0.8573           0.9023
```

`disagreement` = fraction of episodes where the gate passed but the human would fail — the signal a detector can watch.

### S7 — Null-result A/B (both arms p = 0.70)

`RUN`:

```text
n/arm  naive_declares_B  z_test_significant
3      0.3306            0.0178
10     0.4031            0.0376
30     0.4465            0.0503
100    0.4718            0.0489
```

### S8 — Five illustrative 3-vs-3 runs under the null

`RUN`:

```text
run  A      B      naive  p_value
1    0.667  0.000  A      0.0833
2    0.667  0.667  tie    1.0000
3    0.667  1.000  B      0.2733
4    1.000  1.000  tie    1.0000
5    0.667  0.667  tie    1.0000
```

### S9 — Power check (real difference 0.70 vs 0.85)

`RUN`: detection rate 72.75% at `n = 100` per arm, alpha 0.05 (30 per arm lower; 300 higher — see JSON `power_check`).

---

## 5. Findings

1. **The documented rule cannot promote at its own minimum sample.** `RUN` S1/S2: a perfect 3/3 gives Wilson LB 0.4385 against a 0.60 threshold, and no `k` passes at `n = 3, 4, 5`. The `06` promotion rule omits the evaluation horizon `n`; with `N_min = 3` and `delta = 0.10` it is internally unsatisfiable until `n ≥ 6`, and then only on a perfect record until `n = 11`.
2. **The guard is strict enough to reject near-perfect evidence.** `RUN` S1: 9/10 gives LB 0.5958 — failing a 0.60 threshold by 0.0042. Any policy using `delta = 0.10` must expect near-perfect records, not merely good ones.
3. **Removing the guard is worse.** `RUN` S3: count-only N=3 promotes a 50%-reliable candidate 12.21% of the time (analytic 0.5³ = 12.5%). The calibrated variant (`n = 8`, `k ≥ 7`, `LB > p0`) cuts null promotions to 3.51% while retaining 81.14% of 90%-reliable candidates — a defensible trade-off, derived from, not proven by, this simulation.
4. **"2 failures in last 20" is miscalibrated for a reliable skill.** `RUN` S5: it false-demotes a 95%-reliable skill 41.22% of the time over 30 uses. `3 of 20` (15.10%), `2 consecutive` (6.88%) and CUSUM with `k=0.15, h=1.0` (22.98%) all reduce this, at a detection cost of roughly 0–2 extra uses. The document's demotion rule should be revised or explicitly justified.
5. **Regression-suite size is a hidden assumption.** `RUN` S4: a 40-golden suite misses 19.48% of skills that regress 5% of goldens, and 51.95% at 2%; 80 goldens miss 3.87% at 5%. "Run the goldens" is not sufficient unless the suite is sized to the regression rate that matters.
6. **The human gate is load-bearing against reward hacking, and a disagreement metric separates strategies.** `RUN` S6: the gate-optimising strategy is promoted 85.73% of the time with the human check off and 0.01% with it on; gate/human disagreement is 8.02% (honest) vs 90.23% (gate optimiser). A validator that only checks the gate cannot see this failure.
7. **A naive A/B declares winners under the null.** `RUN` S7/S8: with identical arms, "arm B's rate is higher" declares B better 33.06% of the time at n=3 and 47.17% at n=100; the two-sided z test flags 1.78% and 4.89%. One 3-vs-3 run (S8) can show a 0.667-vs-0.000 "winner" at p = 0.083 — exactly the anecdote the evaluation protocol forbids.
8. **Power is expensive at the effect sizes a Craft skill change would produce.** `RUN` S9: detecting 0.70 vs 0.85 needs ≈100 runs per arm for 72.75% power. A 3-run A/B cannot detect a real 15-point difference reliably.

### Direct answer to the wave plan's differential question

> *"What is the minimum synthetic evidence that makes the Wilson rule fail a candidate?"*

`RUN` S1: **3 successes in 3 uses** (LB 0.4385 < 0.60) — the rule's own `N_min`. More generally, any record where `k/n < 1` at `n ≤ 10` fails: 9/10 = 0.5958 is the closest near-miss, and **one failure in ten is enough to block promotion** under `delta = 0.10`.

---

## 6. Recommended calibration (simulation-derived, not adopted)

| Parameter | Documented in `06` | Suggested after this simulation | Basis |
|---|---|---|---|
| Evaluation horizon `n` | unspecified | state it explicitly; `n = 8` as the default evaluation point | S2/S3 |
| Wilson margin `delta` | 0.10 | compare `delta = 0` (`LB > p0`) and decide from a false-promotion budget | S1/S3 |
| Promotion rule | `k ≥ 3`, ratio ≥ 0.75, `LB > p0+delta` | `n = 8`, `k ≥ 7`, `LB > p0` (≈3.5% null promotions, ≈81% retention at p=0.90) | S3 |
| Demotion | 2 failures in last 20 | 2 consecutive failures, or 3-in-20 | S5 |
| Regression suite | "goldens pass" | size the suite from the expected regression rate; ≥80 goldens for a 5% target | S4 |
| A/B | run each golden ≥3 times, report CI | pre-register; two-proportion test; ≥100/arm for a 15-point effect | S7/S9 |
| Human gate | required for taste claims | keep; add gate/human disagreement monitoring | S6 |

These are **policy-design recommendations measured inside the simulation**, not production decisions and not validated against real Craft episodes.

---

## 7. Limits and UNVERIFIED items

| Item | Status |
|---|---|
| Whether real Craft gate pass rates match the assumed probabilities | `UNVERIFIED` — no real episodes exist |
| Whether human raters behave like the assumed 0.90 / 0.05 pass rates | `UNVERIFIED` — no human study |
| Whether `2 consecutive` is the right demotion rule on real drift | `UNVERIFIED` — the drift model (`p` 0.95 → 0.30) is assumed |
| Whether the `calibrated_n8` variant is acceptable to the owner | `UNVERIFIED` — a product decision |
| Whether any of this improves Craft output | **NOT CLAIMED** — the simulation measures a decision rule, not design quality |
| Independence of episodes in real runs | `UNVERIFIED` — the simulation assumes independent Bernoulli successes, which real runs may violate (shared source, shared model temperature) |
| Self-correction / retrieval effects | Not modelled here beyond the two A/B arms |

One further caveat: a promotion rule is only as honest as its evidence. The simulation assumes each synthetic episode's success flag is correct; in the real stack that flag comes from gates plus human review, and `06` §11 lists the attacks against it. This simulation tests the statistics, not the verifier.

---

## 8. Reproduction record

`RUN`:
- `python -m unittest -v test_promotion` → `Ran 23 tests in 0.002s`, `OK`, exit 0.
- `python simulate.py` → exit 0, writes `04-PROMOTION.json` (16,722 bytes), `trials=20000`, `seed=20261105`.
- Re-run determinism: `results` hash identical (`8147c9273557b649`); `generatedAtUtc` differs.

`CODE` pointers:
- `sim/promotion.py::wilson_lower_bound` — Wilson LB.
- `sim/promotion.py::evaluate_promotion` — N_min + ratio + Wilson checks.
- `sim/promotion.py::acceptance_decision` — gates ∧ artifact ∧ rights ∧ human.
- `sim/promotion.py::DemotionMonitor` — window / consecutive / CUSUM.
- `sim/simulate.py::scenario_*` — S1–S8 and power.
- `sim/test_promotion.py` — 23 tests (Wilson known values, promotion boundaries, acceptance, demotion, z test).

## 9. What changed vs wave2/06

`06` *specified* the policy and asserted "3/3 gives WilsonLB≈0.44, so the count alone is not evidence". This execution wave **runs** it and adds three things `06` did not have: (a) the rule is unsatisfiable at `n = 3` and needs an explicit horizon; (b) the `2-in-20` demotion rule false-alarms 41% at 95% reliability and should be revised; (c) a sim-free claim ("human gate matters") is now quantified against a synthetic gate-optimiser (85.73% → 0.01% promotion). No paper was re-reviewed.
