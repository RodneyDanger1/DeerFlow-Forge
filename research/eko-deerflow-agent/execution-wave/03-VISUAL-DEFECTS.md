# 03 — Visual-defect corpus and metric false-pass study

**Task:** `task-10` (owner `craft-surface-auditor`) · **Date:** 2026-11-05 · **Method:** a synthetic,
labelled defect corpus generated and measured on the VPS; no product code was edited.
**Run window (UTC):** 2026-11-05T16:36Z → 16:44Z. **Corpus + scripts:** `execution-wave/fixtures/`.

This is new empirical work, not a re-audit of the Craft surface. It answers one question with
measurements: **which visual metrics can a hosted Craft critic trust, and which defects pass them
silently?**

---

## 1. The corpus

One reference print master, 15 labelled defects (7 classes, two severities each, plus one extra
colour case), and 4 clean controls. **20 PNGs**, 1200×1500 RGBA, deterministic (`seed 20261105`),
tile size 64 px. Every defect records the injected bounding box (`gt_bbox`), which makes
localization measurable, not just detection.

The reference is a plausible apparel badge: navy outer ring, cream ring, navy inner disc,
"RIDGE" wordmark, "FORGE" tagline, a **2 px rule** (the thin-stroke target), and a rust triangle
(the colour target). Art occupies 720×720 px centred on the canvas.

| # | File | Class | Severity | Injection | `gt_bbox` |
|---|---|---|---|---|---|
| — | `00_reference.png` | — | clean reference | — | — |
| 01 | `01_white_fringe_mild.png` | white fringe | mild | 1 px dilated rim, 35 % white | 239,359,962,1082 |
| 02 | `02_white_fringe_strong.png` | white fringe | strong | 2 px rim, 92 % white | 238,358,963,1083 |
| 03 | `03_halo_mild.png` | halo | mild | Gaussian r=8, 24 % cream | 232,352,969,1089 |
| 04 | `04_halo_strong.png` | halo | strong | Gaussian r=16, 55 % cream | 224,344,977,1097 |
| 05 | `05_ghost_text_mild.png` | ghost text | mild | wordmark copy +6 px, α=45 | 442,636,758,724 |
| 06 | `06_ghost_text_strong.png` | ghost text | strong | wordmark copy +14 px, α=110 | 434,628,766,732 |
| 07 | `07_speck_mild.png` | speck | mild | 6 specks, 2×2 px, white | 220,377,922,1113 |
| 08 | `08_speck_strong.png` | speck | strong | 24 specks, 3×3 px, white | 220,340,1031,1114 |
| 09 | `09_lost_stroke_full.png` | lost stroke | full | entire 2 px rule erased | 450,840,750,842 |
| 10 | `10_lost_stroke_partial.png` | lost stroke | partial | 40 % of the rule erased | 450,840,570,842 |
| 11 | `11_wrong_colour_mild_triangle.png` | wrong colour | near-identical | triangle #E4572E → #EDE2C8 | 540,920,660,1000 |
| 12 | `12_wrong_colour_strong_triangle.png` | wrong colour | obvious | triangle → #FF00FF | same |
| 13 | `13_wrong_colour_flat_inner_disc.png` | wrong colour | flat region | whole inner disc navy → purple | 300,420,900,1020 |
| 14 | `14_margin_shift_40px.png` | margin | shift | art moved +40 px x | 240,360,1001,1081 |
| 15 | `15_margin_overflow_8pct.png` | margin | overflow | art scaled ×1.08 about centre | 211,331,989,1109 |
| 16 | `16_clean_identical.png` | clean | identical | byte-identical copy | — |
| 17 | `17_clean_recompressed_jpeg92.png` | clean | benign encoder | JPEG q92 round-trip, alpha preserved | — |
| 18 | `18_clean_recompressed_jpeg75.png` | clean | noisy encoder | JPEG q75 round-trip | — |
| 19 | `19_clean_recompressed_webp80.png` | clean | noisy encoder | lossy WebP q80 round-trip | — |

**The four controls are the point of the study.** A defect metric is only usable if it stays quiet on
a file that was legitimately re-encoded. Absolute thresholds that look strict on a pristine render
must be compared with the noise floor a real exporter produces.

Reproduce (VPS, from `execution-wave/fixtures/`): `build_corpus.py` → `analyze_regions.py` →
`evaluate_critic.py`, with `/opt/pod-pipeline/.venv/bin/python`. `manifest.json` holds the SHA-256 of
every artefact and the recorded tool versions.

---

## 2. Metrics measured

| Family | Definition |
|---|---|
| `global_ssim_rgb` | `skimage.metrics.structural_similarity` over RGB, `data_range=255` |
| `global_rmse` / `global_mae` | over all four RGBA channels, normalised to 0–1 (`/255`) |
| `tile.ssim_min` / `p05` | 64×64 tiles (18×23 = 414), per-tile RGB SSIM |
| `tile.rmse_max` / `p95` | per-tile RGB RMSE |
| `diff_delta8` / `diff_delta32` | mask where `max\|ΔRGBA\|` > 8 / > 32: area fraction, bbox, 8-connected components |
| `gate_equiv` | **`craft_trace`'s own definitions** re-used: `white_residual_ratio` (RGB ≥245 & alpha >127, over alpha area), `edge_specks` (alpha components <150 px), `coverage` |
| `composite_rmse_black` / `_white` | RMSE after compositing both images on `#141313` and on white |
| `region_*` | the same statistics restricted to the injected bbox (pad 12 px) |
| `region_rmse_ratio_vs_benign` | `region_rmse(defect) / region_rmse(jpeg92 control)` **in the same box** — a per-defect, encoder-calibrated signal |
| `iou` | intersection-over-union of the detected diff bbox vs the injected bbox |

The gate-equivalent metrics are deliberately imported from `craft_trace.py` so that "would the
existing gate have caught it?" is answered by the gate's actual formulas, not by an approximation.

---

## 3. Measured results

### 3.1 Master table

| # | Case | global SSIM | global RMSE | tile min SSIM | diff>8 area | specks | white res. | black RMSE | white RMSE |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 01 | white_fringe/mild | 0.98750 | 0.03540 | 0.7528 | 0.001604 | 0 | 0.0000 | **0.01307** | **0.00000** |
| 02 | white_fringe/strong | 0.98565 | 0.05561 | 0.7220 | 0.003213 | 0 | **0.0140** | 0.04828 | **0.00000** |
| 03 | halo/mild | 0.96694 | 0.11144 | 0.4563 | 0.021102 | 0 | 0.0000 | 0.00641 | 0.00101 |
| 04 | halo/strong | 0.93704 | 0.17269 | 0.1595 | 0.050448 | 0 | 0.0000 | 0.02131 | 0.00336 |
| 05 | ghost_text/mild | **0.99788** | **0.00652** | 0.8508 | 0.003787 | 0 | 0.0000 | 0.00753 | 0.00753 |
| 06 | ghost_text/strong | **0.99567** | 0.01828 | 0.7217 | 0.004948 | 0 | 0.0000 | 0.02111 | 0.02111 |
| 07 | speck/mild | **0.99980** | **0.00334** | **0.9810** | **0.000013** | **4** | 0.0001 | 0.00326 | 0.00174 |
| 08 | speck/strong | **0.99897** | **0.00918** | **0.9632** | 0.000120 | **10** | 0.0005 | 0.00940 | 0.00676 |
| 09 | lost_stroke/full | **0.99803** | 0.02050 | 0.8032 | 0.000502 | 0 | 0.0000 | 0.01813 | 0.00286 |
| 10 | lost_stroke/partial | **0.99921** | 0.01300 | 0.8032 | 0.000202 | 0 | 0.0000 | 0.01150 | 0.00181 |
| 11 | wrong_colour/mild_triangle | **0.99857** | 0.02129 | 0.7585 | 0.002734 | 0 | 0.0000 | 0.02458 | 0.02458 |
| 12 | wrong_colour/strong_triangle | **0.99769** | 0.02337 | 0.5829 | 0.002734 | 0 | 0.0000 | 0.02699 | 0.02699 |
| 13 | wrong_colour/flat_inner_disc | 0.96610 | 0.04443 | 0.7925 | 0.158589 | 0 | 0.0000 | 0.05131 | 0.05131 |
| 14 | margin/shift_40px | 0.89818 | 0.17918 | 0.1042 | 0.090365 | 0 | 0.0000 | 0.17627 | 0.21854 |
| 15 | margin/overflow_8pct | 0.87838 | 0.18899 | 0.1308 | 0.113357 | 0 | 0.0000 | 0.18496 | 0.24380 |
| 16 | clean/identical | 1.00000 | 0.00000 | 1.0000 | 0 | 0 | 0.0000 | 0.00000 | 0.00000 |
| 17 | clean/jpeg92 | 0.99407 | 0.00524 | **0.8655** | **0.013557** | 0 | 0.0000 | 0.00592 | 0.00592 |
| 18 | clean/jpeg75 | **0.98730** | 0.00783 | **0.8033** | **0.026242** | 0 | 0.0004 | 0.00885 | 0.00885 |
| 19 | clean/webp80 | 0.99535 | 0.00551 | **0.8938** | **0.014002** | 0 | 0.0000 | 0.00624 | 0.00624 |

Bold = the value that matters for a false pass or a false alarm.

### 3.2 Rule-by-rule: detection vs false alarms

Each rule was evaluated on all 15 defects and all 4 controls.

| Rule | Defects caught | Defects missed | Controls falsely flagged |
|---|---:|---:|---|
| R1 `global_ssim < 0.99` | **7 / 15** | ghost mild+strong, speck mild+strong, lost stroke full+partial, wrong colour mild+strong | **1 / 4** (`jpeg75`, SSIM 0.98730) |
| R2 `global_rmse > 0.01` | 12 / 15 | ghost mild (0.00652), speck mild (0.00334), speck strong (0.00918) | 0 / 4 |
| R3 `tile_min_ssim < 0.95` | 13 / 15 | speck mild (0.9810), speck strong (0.9632) | **3 / 4** (jpeg92 0.8655, jpeg75 0.8033, webp80 0.8938) |
| R4 `diff>8 area > 0.1 %` | 11 / 15 | speck mild, speck strong, lost stroke full, lost stroke partial | **3 / 4** (jpeg92 1.36 %, jpeg75 2.62 %, webp80 1.40 %) |
| R5 `edge_specks > 0` | 2 / 15 | all other classes | 0 / 4 |
| R6 `white_residual > 0.002` | **1 / 15** | everything except strong fringe | 0 / 4 |
| R7 `composite_black_rmse > 0.01` | 11 / 15 | halo mild (0.00641), ghost mild (0.00753), speck mild, speck strong | 0 / 4 |
| R8 `region_rmse_ratio > 4` | 12 / 15 | ghost mild (3.79), speck mild (0.64), speck strong (1.75) | 0 / 4 |
| R9 composite (see §5) | **15 / 15** | — | **0 / 4** |

---

## 4. False-pass findings (the measurements that matter)

**F1. Global SSIM ≥ 0.99 is not an acceptance criterion.**
Eight of fifteen defects pass it, including every ghost-text case (0.99788 / 0.99567), a fully
missing 2 px rule (0.99803), a partial missing rule (0.99921), a magenta swapped into a brand
triangle (0.99769), and a near-identical colour swap (0.99857). It also **fails the wrong way**:
a benign JPEG q75 re-encode scores 0.98730 and would be rejected as a defect. A critic that accepts
at 0.99 has both false negatives and (on real exports) false positives.

**F2. Global RMSE ≤ 0.01 is the best single global metric — and still blind to two classes.**
It catches 12/15 with zero false alarms on four controls. It misses ghost_text/mild (0.00652),
speck/mild (0.00334) and speck/strong (0.00918). Note that a defect can be both *visually obvious*
(24 white specks on a navy badge) and numerically negligible globally.

**F3. Tile-wise SSIM cannot separate a mild speck from benign compression.**
The min-tile rule catches 13/15 but flags 3/4 controls. Worse, the ordering is inverted:
`jpeg75` control tile-min **0.8033** < `ghost_text/mild` **0.8508** ≈ `jpeg92` control **0.8655**,
while `speck/mild` (a real defect) sits at **0.9810**, above a 0.95 threshold. **No tile-min
threshold separates real mild specks from encoder noise**, because JPEG noise is locally large too.

**F4. Raw diff-area is a false-alarm machine on real exports.**
`diff>8` area: jpeg92 control **1.36 %**, jpeg75 **2.62 %**, webp80 **1.40 %** — all larger than the
mild speck (**0.0013 %**), the lost stroke (**0.05 %**) and the strong speck (**0.012 %**). A pixel
diff must be thresholded far above compression noise, and even then it ranks benign re-encodes above
genuine defects of the "small but crucial" kind.

**F5. `white_residual_ratio` has an effective alpha cutoff of 127 and misses mild fringe.**
Re-implementing `craft_trace`'s formula exactly: mild fringe → **0.0000** (its rim alpha is 90, so
the `alpha > 127` term excludes it), strong fringe → **0.0140** (caught). The gate therefore sees
only fringe at ≥50 % opacity. This is a concrete reason to parameterise the gate rather than reuse
it verbatim for a critic.

**F6. `edge_specks` is narrow but perfect for its class.**
Only the two speck cases fire (4 and 10 specks), every other case and all four controls report 0.
Reusing `craft_trace`'s component rule is the right move for specks — and the wrong move for
everything else (2/15 recall).

**F7. White fringe is completely invisible on a white background.**
Composite RMSE on black vs white: mild **0.01307 vs 0.00000**, strong **0.04828 vs 0.00000**.
Halos show the same asymmetry (0.00641 vs 0.00101). **A critic that renders on one background
cannot see white-edge defects**; `craft_trace` already writes black *and* white previews — the critic
must evaluate both and take the worse.

**F8. Localization is good for area defects, poor for text ghosts.**
Diff-bbox IoU vs the injected box: fringe 1.00, speck 1.00, flat recolour 1.00, margin shift 1.00,
overflow 0.997, wrong-colour triangle 0.980, halo 0.89–0.96, lost stroke 0.66, **ghost text 0.55–0.67**
— and its single largest component covers only **0.11** of the ghost box, because a displaced faint
wordmark fragments into many small disconnected components. A critic that reports "one region" will
misreport ghosting.

**F9. Geometry checks must be de-speckled first.**
A raw alpha bbox moved by **20–70 px** on the speck cases — a margin/centring check would call that a
layout error. After dropping alpha components <150 px (the same rule `craft_trace` uses), all speck
shifts collapse to 0 and only the two genuine margin cases shift (40 px, ±29 px).

**F10. A flat recolour is fully visible to SSIM — no constant-region blind spot.**
This hypothesis was tested explicitly and **rejected**: on the 600 px flat-disc recolour, zero tiles
had `SSIM ≥ 0.9999` while `RMSE ≥ 0.05`; the region SSIM dropped to 0.8416 against a 0.9791 control.
Flat-region colour changes are not an SSIM blind spot at 64 px tiles. (Recorded because the opposite
is commonly assumed.)

---

## 5. The critic that the data supports

No single scalar separates these classes. The measured design is **five independent checks, each
matched to a defect signature**, all calibrated against a benign re-encode of the *same* reference:

| Check | Signal | Threshold | Measured recall | Measured false alarms |
|---|---|---|---:|---:|
| C1 geometry | de-speckled content bbox shift vs reference | > 2 px any edge | 2 / 15 (both margin cases) | 0 / 4 |
| C2 specks | alpha components < 150 px | > 0 | 2 / 15 (both speck cases) | 0 / 4 |
| C3 region RMSE | `region_rmse / benign_control_region_rmse` | > 4.0 | 12 / 15 | 0 / 4 |
| C4 region SSIM | `control_region_ssim − case_region_ssim` | > 0.05 | 11 / 15 | 0 / 4 |
| C5 white key | `white_residual_ratio` (gate formula) | > 0.002 | 1 / 15 | 0 / 4 |
| **Union** | **any check fires** | — | **15 / 15** | **0 / 4** |

Union per case (which checks fired):

| Case | Fired | Case | Fired |
|---|---|---|---|
| 01 white_fringe/mild | C3 | 09 lost_stroke/full | C3, C4 |
| 02 white_fringe/strong | C3, C5 | 10 lost_stroke/partial | C3, C4 |
| 03 halo/mild | C3, C4 | 11 wrong_colour/mild | C3, C4 |
| 04 halo/strong | C3, C4 | 12 wrong_colour/strong | C3, C4 |
| 05 ghost_text/mild | **C4 only** | 13 wrong_colour/flat | C3, C4 |
| 06 ghost_text/strong | C3, C4 | 14 margin/shift | C1, C3, C4 |
| 07 speck/mild | **C2 only** | 15 margin/overflow | C1, C3, C4 |
| 08 speck/strong | **C2 only** | 16–19 controls | none |

**Why the thresholds are where they are (measured margins):**

- C3 `ratio > 4`: the three benign controls sit at **1.00, 1.50, 1.05**; the smallest *defect* ratio
  is ghost_text/mild at **3.79**. A 4.0 cut leaves a 2.7× margin over encoder noise and deliberately
  does **not** try to catch ghost/mild on its own — C4 does (its region SSIM drop is 0.0739, well
  over 0.05, while the controls are 0.000, 0.0221, −0.0042).
- C4 `drop > 0.05`: control maximum is **0.0221** (jpeg75); smallest defect drop is **0.0214**
  (fringe/mild) — so C3, not C4, is the fringe detector. The pair is complementary, which is why
  the union works.
- C1 `2 px`: margin defects shift content by 29–40 px after de-speckling; benign re-encoding shifts
  it by 0.
- C2 `150 px`: identical to `craft_trace`'s speck rule, and the controls produce zero qualifying
  components.
- C5 `0.002`: verbatim from `craft_trace`; only catches ≥50 %-opacity white rim.

---

## 6. Critic test criteria (acceptance tests for the harness)

A hosted visual critic is **accepted** only when it passes all of the following on this corpus, and
the run record carries the corpus + threshold hashes.

1. **Recall.** Each of the 15 labelled defects is reported as defective, and the label matches the
   class (`white_fringe`, `halo`, `ghost_text`, `speck`, `lost_stroke`, `wrong_colour`, `margin`).
   Minimum: 15/15 class-correct.
2. **Specificity.** All four controls are reported clean. The three lossy-encode controls are the
   important ones; a critic that flags jpeg75 is unusable on real exports.
3. **Localization.** For the 13 area-shaped defects, reported region IoU with the injected bbox
   ≥ **0.50** (measured achievable: 0.66–1.00). For ghosting, the report must be allowed to return
   **multiple** regions (largest-component IoU was only 0.11).
4. **Calibration.** Thresholds are computed against a benign re-encode of the *same* reference at
   run time; absolute constants are recorded per corpus, not hard-coded globally.
5. **Dual background.** Evaluation renders on both black and white and uses the worse-case signal;
   a white-edge defect must not be able to hide by being invisible on white.
6. **De-speckled geometry.** Layout/margin checks run on an alpha mask with components <150 px
   removed, so dust cannot masquerade as a layout shift.
7. **Determinism.** Two runs on the same inputs produce identical verdicts and identical metric
   values (the corpus is deterministic; the metric code is pure numpy/skimage).
8. **No silent pass.** If a required metric is missing from the report, the verdict is `UNVERIFIED`,
   never `pass` (this mirrors the evaluation protocol in `craft-agent-operator/references/evaluation.md`).
9. **Regression gate.** A change to the critic must re-run this corpus; any newly-missed defect or
   newly-flagged control blocks promotion.
10. **Human review stays.** The critic triages and localizes; a human still signs off print/publish.
    A green critic is not evidence that the design meets the brief.

Negative tests the critic must also survive (from the same data): a benign q75 re-encode must pass
(F1/R1); a mild speck must not be dismissed because the global RMSE is 0.003 (F3); a missing 1.5–2 px
rule must not be dismissed because global SSIM is 0.998 (F1).

---

## 7. Limits of this study

- **One reference, one art style.** All defects are injected into a single 1200×1500 badge. The
  thresholds are calibrated for it; they have not been shown to transfer to other layouts, scales,
  or photographic art.
- **Synthetic injection.** Fringes/halos/ghosts are modelled, not sampled from a real exporter or a
  real AI artefact. The jpeg/webp controls are real encoder output; the defects are not.
- **Two severities per class.** Enough to see the metric/defect interaction, not enough to estimate a
  detection curve across severity.
- **No VLM leg.** The study measures numerical metrics only; whether a vision model notices these
  artefacts is a separate experiment (and the corpus is a good fixture set for one).
- **Calibration control is in-family.** The benign control is a re-encode of the same reference; a
  critic comparing renders from *different* renderers should calibrate with that renderer's own
  control.
- **Not tested:** CMYK/press conversion, gradient banding, blend-mode flattening, text kerning drift,
  multi-artboard documents.

---

## 8. Operational note (recorded because it broke the first run)

Running the generator as `/tmp/vd_build.py` failed with
`AttributeError: module 'numbers' has no attribute 'Integral'` — another process on the host had left
`/tmp/numbers.py`, and a script executed from `/tmp` puts `/tmp` first on `sys.path`, so stdlib
`numbers` was shadowed. Fixed by running from a dedicated directory (`/tmp/vd/`). A hosted harness
must never execute job scripts straight out of a shared `/tmp`; give each run its own scratch
directory.

---

## 9. Artefacts

`execution-wave/fixtures/` — 20 PNGs, `metrics.json` (per-pair raw metrics), `analysis.json` (region
statistics + rule table), `critique.json` (composite verdicts), `manifest.json` (SHA-256 of all 26
artefacts), and the three scripts (`build_corpus.py`, `analyze_regions.py`, `evaluate_critic.py`).
