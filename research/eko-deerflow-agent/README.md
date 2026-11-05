# Ridgeboundia / DeerFlow Forge Agent Program

**Status:** research + execution evidence + implementation plan. **No production repair or deploy has
been applied.** Phase 0 staging gate passed for one real VectorCraft trace and one real PhotoCraft
retouch; a **local** Forge core (gateway/DDL/repo/worker/service/verifier/critic) is implemented and
tested on scratch infrastructure; DeerFlow MCP registration remains unapplied. Date: 2026-11-05.
Owner: Riley.

This is the master entry point for the agent-harness work. It explains what exists, what is broken,
what we are building, the six integrations, eight Python changes, eight agent/tool/skill changes, the
goal evaluation, and how to read the evidence without drowning in it.

> **Read next:** [`GOALS.md`](GOALS.md) → [`ARCHITECTURE.md`](ARCHITECTURE.md) →
> [`execution-wave/09-GOAL-GAP-PLAN.md`](execution-wave/09-GOAL-GAP-PLAN.md) → [`PLAIN-ENGLISH.md`](PLAIN-ENGLISH.md).
> Diagrams: [`diagrams/index.html`](diagrams/index.html).

---

## 1. The outcome we are building

A hosted **Forge Conductor** designed for the DeerFlow 2.2 + DeepSeek V4.1 Flash runtime that can:

1. take a print/vector brief;
2. choose exact Craft command ids from a pinned catalogue;
3. run on copies through a typed CLI/MCP gateway;
4. verify artifact hashes, dimensions/DPI, domain gates, an independent render and a blind visual
   critic;
5. record a hash-chained episode with evidence;
6. propose a lesson/skill only after repeated verified success and human approval;
7. never publish to the storefront without explicit human approval.

The first release is a **production operator under human art direction**, not an autonomous artist,
not a new generic superagent, and not a claim of “better than human.”

## 2. What we know now (the short truth)

| Area | Finding |
|---|---|
| VPS | 2 vCPU / 7.9 GB / 36 GB free, no GPU/display; DeerFlow 2.2 is the designed host, but Forge MCP registration is **not applied** and current runtime ownership is unverified |
| Model | `deepseek-flash` (“DeepSeek V4.1 Flash”), 1,048,576 ctx, 8,192 output; key validity unverified |
| Craft apps | VectorCraft 0.21.1 + PhotoCraft 0.20.2 installed; Film/Design/Effect **absent** |
| Execution | Production `/opt/pod-pipeline/bin/*-cli` may still be stubs; `deploy/craft-launchers` are pinned; `routes.py` argv was corrected and staging-proven. Production deploy not applied |
| MCP | Craft MCP works standalone (33/26 tools) but is **not registered** in DeerFlow |
| Persistence | `pod` untouched; local `forge` DDL + repo/worker/service exist and are scratch-Postgres tested; no production `forge` DB |
| Verification | local verifier/critic contracts are implemented and tested (8/8, 14/14); **no vision-model accuracy claim** |
| Learning | DeerMem facts + skill-evolution host exist; **no full learner or quality evaluation**; current level **L0** |
| Publish | `fourthwall_template_id` unset for all five products; no approval queue |
| Evidence | README’s live-E2E claim is historical/unreproducible in the current state |
| Assets | 39 skills, 400 answers, 6 examples, 8 validated system diagrams + integration map, **179-file source corpus**, **189-file desktop package** |

The key sentence: **the model/harness is present; the Craft execution path and learning evidence are
not.** Phase 0 starts there.

## 3. Six integrations

| # | Integration | What it connects | Why it is needed | Acceptance gate |
|---|---|---|---|---|
| **I1** | **Craft launcher + argv contract** | `/opt/craft/*/bin` → `deploy/craft-bin` → `routes.py` | The pipeline cannot execute a Craft command today | one real VectorCraft trace + one real PhotoCraft retouch |
| **I2** | **Craft MCP bridge** | VectorCraft/PhotoCraft stdio MCP → DeerFlow `mcpServers` | Gives the agent native 33/26-tool surfaces without shell guessing | `tools/list` + `command_batch`; dependent PhotoCraft calls awaited |
| **I3** | **Forge Conductor service** | Console/DeerFlow → `forge-conductor:8092` → queue/ledger | Owns planning, budgets, episode state and recovery | replay one episode from ledger; no source mutation |
| **I4** | **Evidence verifier + blind critic** | artifacts → gates → render → tile metrics → critic | Exit 0/`ok:true`/screenshots are not proof | 5-check composite + human rubric; missing evidence = UNVERIFIED |
| **I5** | **Human approval + publish** | Forge approval → Fourthwall product state | Publishing is irreversible and currently misconfigured | approval bound to artifact hash; template ids set; no auto-publish |
| **I6** | **Learning + evaluation loop** | episodes → retrieval → candidate skill → regression → active | “Learns” must mean a measured, reversible change | calibrated promotion + A/B; null result disables memory |

### I1 — Launcher + argv contract (P0)

- **Files:** `blueprint/files/deploy/craft-bin/*-cli`, `blueprint/files/pod_pipeline/routes.py`,
  `deploy/setup-pipeline.sh`.
- **Measured contract (do not revert to the old ASSUMPTION):**
  - VectorCraft: `run --in F --cmd select.all --cmd imageTrace.make --params '{"params":{…}}'
    --cmd imageTrace.expand --export out.svg`; export does **not** create parent dirs.
  - PhotoCraft: `run FILE|--new --cmd ID --params J --out F`; creates parent dirs.
- **Refusal:** absent app → `E_TOOL_NOT_INSTALLED`, not a fake trace.
- **Rollback:** restore the original launchers and `routes.py` from backup.

### I2 — Craft MCP bridge (P0)

- **Files:** DeerFlow `extensions_config.json`; optional stdio bridge; read/write roots.
- **Rules:** VectorCraft `mcp --headless --automation-read/write-root`; PhotoCraft `mcp` without
  `--headless` + roots; await each `tools/call` (PhotoCraft can interleave).
- **Gate:** `tools/list` returns 33/26; a real batch produces an artifact.

### I3 — Forge Conductor service (P1, local core only)

- **Files:** `blueprint/files/forge_gateway.py`, `forge_repo.py`, `forge_worker.py`,
  `forge_service.py`, `sql/schema_forge.sql`; deployment units are not installed.
- **DB:** 13 tables (episode, event, handoff, tool_call, artifact, gate, critique, eval, job, skill,
  budget, approval, transition), 36 seeded edges; scratch PostgreSQL only.
- **Gate:** **18/18 SQL assertions**, **33/33 gateway tests**, two-worker `SKIP LOCKED`, 4/4 repository,
  5/5 service, 2/2 real HTTP→repo→worker→reaper tests. No production DB/service.

### I4 — Evidence verifier + blind critic (P1, contract only)

- **Files:** `blueprint/files/forge_verifier.py`, `forge_critic.py`, tests.
- **Ladder:** artifact hash/PNG/DPI + gate-report parser; blind-critic schema + gate/critic/human
  resolver. Missing evidence → `UNVERIFIED`; critic cannot override a failed gate.
- **Measured locally:** verifier 8/8; critic 14/14. No vision model was run; earlier synthetic
  recall/false-alarm figures are **not current evidence** and must not be quoted as measured.
- **Gate:** real G0 pair passes; tampered/vacuous/failed/malformed inputs refuse by name.

### I5 — Human approval + publish (P1)

- **Files:** `forge/approval`/`forge_publish.py`, `config/products.json`, Fourthwall client.
- **Rules:** approval table binds to artifact hash + scope; template/area validated; no autonomous
  publish; product state read back.
- **Gate:** approval reused → blocked; missing template → named refusal; no store mutation in tests.

### I6 — Learning + evaluation (P2/P3, contract only)

- **Files:** `forge_eval.py`, `forge_critic.py`, `forge_verifier.py`; no learner/activation.
- **Rule:** L1/L2 only (retrieval/skills), no fine-tune/RL. Promotion requires a declared horizon,
  Wilson lower bound above baseline, golden regression and human approval. **3/3 is not enough**
  (Wilson LB 0.4385; the old rule was rejected by simulation).
- **Current gate:** eval contract **13/13**; 3/3 refused, 8/8 only a candidate with human approval,
  regressions refuse. No real corpus/A-B/activation; current level remains **L0**.

## 4. Eight small Python enhancements

These are **planned**, not applied. Each is written to be independently testable.

| # | File / function | Change | Test |
|---|---|---|---|
| **P1** | `pod_pipeline/routes.py` `trace_step` / `raster_fallback_step` | replace invented `trace`/`--input` argv with measured `run` contracts | `test_routes.py` + one live trace/retouch |
| **P2** | `pod_pipeline/orchestrator.py` `_run_step` / preflight | check binary exists, app version, catalogue hash; `E_TOOL_NOT_INSTALLED` | missing-binary error path |
| **P3** | `tools/craft_trace.py` gate assembly | make `retyped_text_present` non-vacuous; record artifact path/hash; gate status before/after save | 0-box text fixture must fail; text fixture must pass |
| **P4** | `tools/prep_print_art.py` report | stop treating `ok:true` as a pass; expose warning-only upscale and coverage; add `verdict` | 3.6× upscale test must be `refused_for_print` |
| **P5** | `pod_pipeline/runner.py` / orchestrator | hash inputs before/after; flag source mutation; atomic artifact copy | mutate a fixture; episode must fail |
| **P6** | `pod_pipeline/db.py` / new `forge/repo.py` | idempotency key, duplicate replay, unique constraints, queue lease | duplicate call = one effect; crash/requeue |
| **P7** | `pod_pipeline/worker.py` | lease expiry/reaper/recovery with bounded scans | kill worker mid-run; reclaim once |
| **P8** | `pod_pipeline/orchestrator.py` / new `forge/cost.py` | persist token/cost per step/episode; enforce caps | cap exceeded returns named refusal, no silent truncation |

## 5. Eight agent/tool/skill enhancements

These are changes to how agents use the stack; most are documentation/protocol now, code/tooling later.

| # | Skill/tool | Enhancement | Why |
|---|---|---|---|
| **A1** | `craft-agent-operator` | mandatory evidence contract + no screenshot/exit-code proof + episode record | prevents “it looked good” shipping |
| **A2** | `agent-learning-loop` | calibrated promotion/demotion/regression, corrected 3/3 rule | simulation showed the original rule cannot promote |
| **A3** | `visual-verification-critic` | 5-check composite, black+white render, region/tile evidence | global SSIM misses 4% defects |
| **A4** | `forge-harness-architect` | Phase 0 app/binary preflight; VC/PC-only scope | prevents designing for absent apps |
| **A5** | `harness-code-adapter` | donor provenance/pin, adapter contract, no verbatim code | code stitching without a fork |
| **A6** | `research-corpus-navigator` | map 400 answers + claim/errata; one-slice loading | stops context flooding |
| **A7** | `craft-mcp-drive` | await dependent calls; auth/loopback; stdio vs HTTP gap | PhotoCraft interleaving + exposed MCP |
| **A8** | `apparel-print-master` / publish skills | bind approval to artifact hash; template/rights preflight | no irreversible publish on a stale master |

## 6. Phase plan and gates

| Phase | Deliverable | Gate |
|---|---|---|
| **0** | launchers, argv, MCP registration, 10 goldens, README/AGENTS correction | one real trace + retouch; no stub; expected artifacts |
| **1** | Forge skeleton, verifier, approval, queue | replay from ledger; duplicate/refusal/crash tests |
| **2** | blind critic, tile metrics, human rubric | 15/15 synthetic recall / 0/4 false alarms; missing → UNVERIFIED |
| **3** | retrieval + A/B | measured gain or null; memory disabled on null |
| **4** | skill promotion/rollback | calibrated horizon + regression + human; rollback drill |
| **5** | print + second app + 50 goldens | no unsafe publish; measured cost |
| **6** | security/backup/hardening | restore drill; key metadata check; MCP auth |

Estimate: 6–10 weeks for Phase 0–2; this is an `ESTIMATE`, not a measured schedule.

## 7. Goal evaluation (summary)

| Goal | Status | Evidence | What moves it |
|---|---|---|---|
| G1 execute Craft | **PARTIAL** | staging launchers/argv proven; production deploy unverified | I1/P1/P2 |
| G2 native tools | **PARTIAL** | MCP works standalone, not registered | I2/P6 |
| G3 verify quality | **PARTIAL (local)** | verifier 8/8 + critic contract 14/14; no vision-model accuracy | I4/P3/P4 |
| G4 learn | **NOT STARTED (L0)** | no ledger/eval/retrieval claim | I3/I6/P6–P8 |
| G5 host on VPS | **FEASIBLE** | 2 vCPU, model running; no production Forge service | I3 + caps |
| G6 safe publish | **BLOCKED** | no approval, templates unset | I5/A8 |
| G7 truth | **IMPROVING** | claim register; README correction pending | docs/ERRATA |

Full detail: [`GOAL-EVALUATION.md`](GOAL-EVALUATION.md).

## 8. What is possible / what is best

**Possible now:** repair the execution path, run one real trace/retouch, record evidence, verify
dimensions/DPI/gates, build the ledger/queue, and prove replay/idempotency. **Best first move:** I1 +
I2 + I3, not GUI or training.

**Not possible now:** all Craft apps, autonomous publish, fine-tuning, RL, “better than human,” or a
production claim that the current agent learns.

**Best architecture:** DeerFlow 2.2 as front door/runtime + Forge Conductor as third plane + native
Craft CLI/MCP + Postgres ledger/queue + DeerMem facts + versioned skills. Do not build a new generic
harness or vendor a whole donor repo.

## 9. Evidence and files

| Item | Where |
|---|---|
| Goals/non-goals | [`GOALS.md`](GOALS.md) |
| Architecture | [`ARCHITECTURE.md`](ARCHITECTURE.md) |
| Integration map | [`INTEGRATIONS.mmd`](INTEGRATIONS.mmd) + SVG/PNG |
| Eight system diagrams | [`diagrams/`](diagrams/index.html) |
| Integration map (ninth) | [`INTEGRATIONS.mmd`](INTEGRATIONS.mmd) + SVG/PNG |
| PDF reading copies | [`PDF-CATALOGUE.md`](PDF-CATALOGUE.md) · 29-page binder in `docs/pdf/` |
| Goal→code gap + decision plan | [`execution-wave/09-GOAL-GAP-PLAN.md`](execution-wave/09-GOAL-GAP-PLAN.md) |
| Recon ledger | [`execution-wave/RECON-LEDGER.md`](execution-wave/RECON-LEDGER.md) |
| Claim register | [`execution-wave/10-CLAIM-REGISTER.md`](execution-wave/10-CLAIM-REGISTER.md) |
| Independent verification | [`execution-wave/08-VERIFICATION-INDEPENDENT.md`](execution-wave/08-VERIFICATION-INDEPENDENT.md) |
| First 200 | [`REPORT.md`](REPORT.md) |
| Second 200 | [`wave2/08-200-QUESTIONS.md`](wave2/08-200-QUESTIONS.md) |
| Six examples | [`examples/`](examples/README.md) |
| PDF catalogue | [`PDF-CATALOGUE.md`](PDF-CATALOGUE.md) |
| Plain English | [`PLAIN-ENGLISH.md`](PLAIN-ENGLISH.md) |

## 10. Truth rules

- A design is not an implementation; `PROPOSED` is not `VERIFIED`.
- Exit 0, `ok:true`, a screenshot or a README claim is not proof.
- The 400 answers are a fixed corpus; re-fetch before changing policy.
- No production file/DB/service has been changed by this research wave.
- “Better than human” is unsupported; no blind study exists.
- FilmCraft/DesignCraft/EffectCraft are absent and out of the current scope.
- The key is configured by name only; validity is unverified until the zero-spend metadata check.

## 11. Next action

Approve **Phase 0**. Apply I1/I2 on a staging copy, run one real trace and one real retouch, write
the evidence to the ledger, then decide whether Phase 1 is worth building. Do not start with
fine-tuning, GUI automation or autonomous publishing.
