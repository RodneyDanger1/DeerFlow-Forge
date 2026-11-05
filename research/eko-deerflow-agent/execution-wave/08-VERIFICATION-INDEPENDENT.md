# 08 — Independent Verification (fresh seat, execution wave)

**Task:** `task-16` · **Verifier:** `wave2-verifier` (fresh context; did not write any execution-wave deliverable)
**Date:** 2026-11-05 · **Workspace:** `C:\Users\Riley\Desktop` · **Repo:** `DeerFlow Forge`
**Write scope:** this file + `08-VERIFICATION-INDEPENDENT.json` only. No production edit, no fix applied.

**Independence rule applied:** no execution-wave receipt was accepted as proof. Every status below is
from a command run by this seat or a file read by this seat. Where the VPS was required and no SSH
access existed, the claim is `UNVERIFIED (independent)` even if another file labels it `VERIFIED`.

**Status vocabulary:** `VERIFIED` = executed/read this session, output quoted · `READ` = source read by
this seat, not executed · `INFERRED` = follows from verified data but not itself observed ·
`U` = unverified/unavailable · `UNVERIFIED` = could not reproduce independently.

---

## 1. Commands run and observed output

| # | Command (cwd) | Observed output | Exit | Status |
|---|---|---|---|---|
| T1 | `python -m unittest -v test_promotion` (`execution-wave/sim`) | `Ran 23 tests in 0.002s` / `OK` | **0** | VERIFIED |
| T2 | `python simulate.py --out <temp>` (`execution-wave/sim`) | all S1–S8 tables; `Wrote …` | **0** | VERIFIED |
| T2b | same run, `results` object canonically hashed | regen `sha256 890bedb6df6e8fe74182b8b6c8782b4216c57dbd5ce96be7ebac827b5d5bd138` == committed `04-PROMOTION.json`; findings identical; second run identical | — | VERIFIED |
| T3 | `node --test "test/*.test.mjs"` (`execution-wave/adapter`) | `tests 30  pass 30  fail 0  cancelled 0  skipped 0  todo 0`; `duration_ms 638.2` | **0** | VERIFIED |
| T4 | `python -m py_compile sim\promotion.py sim\simulate.py sim\test_promotion.py fixtures\build_corpus.py fixtures\analyze_regions.py fixtures\evaluate_critic.py` | no output | **0** | VERIFIED |
| T5 | parse every `execution-wave/*.json` + `fixtures/*.json` with Python `json` | 10/11 parse as UTF-8; **1 fails: `fixtures\manifest.json` — `Unexpected UTF-8 BOM`** (parses with `utf-8-sig`) | 1 | VERIFIED (1 defect) |
| T6 | `fixtures/manifest.json` SHA-256 re-computation | `manifest files=26 ok=26 bad=0`; 20 PNGs on disk | 0 | VERIFIED |
| T7 | doc `03` master table vs `fixtures/metrics.json` (19 rows) | `MASTER_TABLE_MISMATCHES 0` | 0 | VERIFIED |
| T8 | doc `03` rule table vs `fixtures/analysis.json` (9 rules) | all R1–R8 counts match (`R1 7/15·1/4`, `R3 13/15·3/4`, `R8 12/15·0/4`) | 0 | VERIFIED |
| T9 | `fixtures/critique.json` composite | `composite: 15/15 controls 0/4`; per-check C1 2, C2 2, C3 12, C4 11, C5 1, all 0/4 | 0 | VERIFIED |
| T10 | `python validate_skills.py` (`blueprint/files/skills/_meta`) | `39 skills checked \| 39 passed \| 0 failed`; `Runtime: DSH current=39 missing=0 differs=0 \| Hermes current=39 missing=0 differs=0` | **0** | VERIFIED |
| T11 | `python check_skill_commands.py` | `62 files scanned (39 SKILL.md + 23 references); 0 with unknown command ids` | **0** | VERIFIED |
| T12 | `python check_atlas.py` | `atlas check OK: VC 918 ids / 64 groups; PC 965 ids / 38 groups` | **0** | VERIFIED |
| T13 | five new skill dirs in `~/.dsh/skills` and `~/.hermes/skills` | all five `PRESENT` in both | — | VERIFIED |
| T14 | `git status --porcelain` (repo) | 17 lines: **5 ` M` + 12 `??`**; none under `pod_pipeline/`, `deploy/`, `src/`, `forge/` | — | VERIFIED |
| T15 | Lead package `Ridgeboundia-Agent-Research` | `files=129 bytes=4499906` — matches `07-PACKAGE.md` §2 exactly | — | VERIFIED |
| T16 | 400 answers | `REPORT.md` 200 `**Q` markers + `wave2/08-200-QUESTIONS.md` 200 = **400** | — | VERIFIED |
| T17 | `ssh -o BatchMode=yes -o ConnectTimeout=8 root@179.197.88.181 'echo SSH_OK; hostname'` | `root@179.197.88.181: Permission denied (publickey,password).` | **255** | U (no access) |

---

## 2. Claim → status table (decision-critical claims)

| # | Claim (source) | Independent check | Status |
|---|---|---|---|
| 1 | `sim` has 23 tests, all pass (04) | T1: `Ran 23 tests … OK` | **VERIFIED** |
| 2 | `simulate.py` deterministic, 20,000 trials, seed 20261105, reproduces committed results (04) | T2/T2b: results sha256 identical to committed; two regens identical | **VERIFIED** |
| 3 | 3/3 → Wilson LB 0.4385; `N=3 + LB>0.60` cannot promote (04, claim 14) | T2 S1/S2: `3 3 1.000 0.4385 False`; k_min None at n=3,4,5 | **VERIFIED** |
| 4 | `2 failures in last 20` false-demotes a 95% skill 41.22% (claim 15) | T2 S5: `window_2_of_20 0.4122` | **VERIFIED** |
| 5 | Human gate cuts gate-optimiser promotion 85.73% → 0.01% (claim 16) | T2 S6: `promote_without 0.8573`, `promote_with 0.0001` | **VERIFIED** |
| 6 | Promotion-rule correction landed in active guidance (ERRATA) | `ERRATA.md:3-26`; `agent-learning-loop/SKILL.md:67-75`; `memory-ledger.md:127-131` all state 0.4385 / n=8 / 41.22% | **VERIFIED** |
| 7 | Adapter: 30 tests, all pass; crash/resume/duplicate/approval/compaction covered (06) | T3: `tests 30 pass 30 fail 0`; output lists the named cases incl. "crash after the effect…" | **VERIFIED** |
| 8 | Adapter code is Python-free / Node only; `py_compile` N/A | Inspected `adapter/src/*.mjs`; T4 covers the six `.py` files that exist | **VERIFIED** |
| 9 | Visual: global SSIM catches 7/15; tile-min 13/15 with 3/4 false alarms; region 11/15 with 0/4 (claim 12) | T8/T9: R1 `7/15, 1/4`; R3 `13/15, 3/4`; C4 region-SSIM `11/15, 0/4` | **VERIFIED** |
| 10 | Visual: composite union catches 15/15 defects, 0/4 controls (03 §5) | T9: `composite 15/15 controls 0/4`; per-case fired map matches 03 §5 exactly | **VERIFIED** |
| 11 | Visual master table and rule table are consistent with the fixture JSON (03) | T7/T8: 0 metric mismatches; all rule counts match | **VERIFIED** |
| 12 | `fixtures/manifest.json` = SHA-256 of all artefacts (03 §9) | T6: 26/26 hashes and byte lengths match the files on disk | **VERIFIED** |
| 13 | 39 skills validate; DSH & Hermes both current (claim 13) | T10: `39 passed`; DSH `current=39 missing=0 differs=0`; Hermes same | **VERIFIED** |
| 14 | Command ids quoted in skills all exist in the 918/965 catalogues | T11/T12: 0 unknown ids; `VC 918 / PC 965` | **VERIFIED** |
| 15 | The five new skills are installed (claim 38) | T13: all five present in both runtimes; repo has 5 new dirs | **VERIFIED** |
| 16 | 39 skills / 400 answers exist (claim 13, GOALS) | T10 + T16: 39 SKILL.md; 400 Q markers (200 + 200) | **VERIFIED** |
| 17 | No production file changed this wave (claim 23) | T14: no diff under `pod_pipeline/`, `deploy/`, `src/`, `forge/`; 12 untracked dirs are research/skills. **Caveat: 5 skill files are modified, not "new"** | **VERIFIED (with caveat)** |
| 18 | Lead final package is 129 files / 4,499,906 bytes (07-PACKAGE) | T15: exactly 129 files / 4,499,906 bytes, same top level | **VERIFIED** |
| 19 | `routes.py` argv is invented (`trace`, `--input`, `--svg-out`, `--pdf-out`, PhotoCraft `--input`) (claim 6 / C2) | Local read: `routes.py:73-82` trace argv; `:84-93` and `:105-107` PhotoCraft `--input`/`--out-dir`; docstrings self-label "ASSUMPTION … invented" | **READ (local) / VERIFIED local file** |
| 20 | `deploy/craft-bin/*-cli` are 127-exit stubs (claim 4) | Local read: all five files `echo "…vendor binary not installed…" >&2; exit 127`; `setup-pipeline.sh:88-92` installs them only when `bin/$tool` absent | **READ (local source of shims)** |
| 21 | Only VectorCraft 0.21.1 + PhotoCraft 0.20.2 installed (claim 5) | Host-only; T17 SSH denied. Evidence files (`wave2/01`, `wave2/03`) not re-executed | **U (independent)** |
| 22 | `/opt/pod-pipeline/bin/*-cli` deployed stubs exit 127 (claim 4, deployed host) | Host-only; T17 denied | **U (independent)** |
| 23 | Craft MCP works standalone but is unregistered in DeerFlow (claim 8) | Host-only; T17 denied. Not re-derived from a live `extensions_config.json` | **U (independent)** |
| 24 | DeepSeek key validity (claim 3) | No live call anywhere; docs propose zero-spend `/user/balance` + `/models` | **U** — consistent with claim register |
| 25 | VPS 2 vCPU/7.9 GB, DeerFlow 2.2.0 running (claims 1–2) | Host-only; T17 denied | **U (independent)** |
| 26 | Visual corpus generated and measured on the VPS (`03` §1, manifest `generatedOn`) | Fixture data is internally consistent (T6–T9); generator not re-run (needs `/opt/pod-pipeline/.venv`, PIL/skimage) | **READ/INFERRED (data) + U (reproduction)** |
| 27 | `07-PACKAGE.md` is the executed packaging record | By its own text it is **SUPERSEDED**; task board shows task-14 completed; Lead package exists and matches its counts | **READ (self-declared historical)** |

---

## 3. Contradictions found (named, not fixed)

| # | Conflict | Evidence | Severity |
|---|---|---|---|
| X1 | **`fixtures/manifest.json` is not plain UTF-8 JSON** — it carries a UTF-8 BOM, so the standard `json.load(open(f))`/`json.loads(raw.decode('utf-8'))` fails (`Unexpected UTF-8 BOM`). It parses only with `utf-8-sig`. This contradicts the general "JSON parses/valid JSON" expectation for the fixture set. | T5 | Low (tooling hazard) |
| X2 | **Claim 23 wording vs `git status`**: "git status shows only **new** research/skills files" — actual status has **5 modified** tracked skill files (`M skills/README.md`, `M _meta/SKILLS-INDEX.md`, `M _meta/manifest.json`, `M craft-agent-operator/references/memory-ledger.md`, `M skills-index/SKILL.md`) plus 12 untracked. No production code is modified, so the substantive claim holds; the "only new" wording does not. | T14 | Low (wording) |
| X3 | **Stale task status inside a deliverable**: `01-EXECUTION-REPAIR.md:3` says task-8 "(in_progress, revision 2)"; the task board records task-8 **completed, revision 3**. | `01:3` vs `team_task_list` | Low (provenance) |
| X4 | **`07-PACKAGE.md` says "SUPERSEDED"** and "no file was copied … by this task", while task-14 is marked **completed** and the 00-plan WP-7 defines packaging as this seat's deliverable. The Lead package it describes does exist and matches its counts (T15), so the record is a historical freeze note, not an executed manifest. | `07-PACKAGE.md` §0/§5 vs board | Low (scope) |
| X5 | **Minor line-offset drift**: `09-GOAL-GAP-PLAN.md:23` cites `routes.py:88-96` for PhotoCraft `--input`; the actual invented PhotoCraft argv is at `:84-93` (raster fallback) and `:105-107` (apparel trim). The claim is directionally true; the range is approximate. Also `01` cites `setup-pipeline.sh:88-90`; the loop is `:88-92`. | local read of `routes.py`, `setup-pipeline.sh` | Low (citation precision) |
| X6 | **"region 11/15 with 0/4"** in the claim register is the **C4 region-SSIM** result; the `03` §3.2 table's **R8 region-ratio** rule is **12/15, 0/4**. Both are in the docs; the register's unqualified "region" label is ambiguous rather than wrong. | T8/T9 | Very low (labelling) |

No contradiction was found between the **executed** results and the **documented** result tables:
promotion numbers, visual master/rule/composite tables, skill counts and the five-skill install all
reproduce exactly.

---

## 4. What this seat could not reproduce (residual `U`)

1. **All VPS-host observations** — SSH to `179.197.88.181` returns `Permission denied (publickey,password)`
   (exit 255). Therefore deployed stub behaviour, installed-app inventory (2 apps), live Craft MCP
   registration state in DeerFlow, DeerFlow version/uptime, and VPS capacity are `U (independent)`.
   The local repo *sources* for the shims and `routes.py` argv were read and match the descriptions.
2. **Visual corpus regeneration** — `build_corpus.py` / `analyze_regions.py` / `evaluate_critic.py` were
   not re-run (require the VPS venv with Pillow/numpy/scipy/scikit-image). Instead the emitted JSON was
   cross-checked against the document tables (T6–T9), which is consistency evidence, not re-measurement.
3. **Run of the adapter against a real Craft binary** — correctly out of scope (`06` §7, §10); no such
   run is claimed.
4. **DeepSeek key validity** — `U`; no zero-spend metadata call was made (owner approval required).
5. **`sim` probabilities against real Craft episodes** — `ASSUMED` by design; no real episode exists.

---

## 5. Verdict

The executable parts of the execution wave reproduce **as claimed**: 23/23 promotion tests, the
deterministic 20,000-trial simulation (results hash-identical), 30/30 adapter tests, Python compile
clean, visual fixture data fully consistent with the document tables (26/26 manifest hashes, 0 metric
mismatches, union 15/15 with 0/4 false alarms), 39/39 skills valid with DSH and Hermes parity, all
command ids known (918/965), the five new skills installed in both runtimes, and 400 answers present.
No production code was modified (`pod_pipeline/`, `deploy/`, `src/` clean); only skill metadata and new
research/skills directories differ.

Defects are minor and are **reported, not fixed**: the BOM on `fixtures/manifest.json` (X1), the
"only new files" wording in claim 23 (X2), stale in-document task status (X3), the superseded packaging
record (X4), and small line-citation drift (X5/X6). The decision-critical VPS and key claims remain
`U` from this seat because the host is not reachable.
