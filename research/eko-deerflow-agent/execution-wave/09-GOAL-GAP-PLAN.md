# 09 — Goal-to-Code Gap Audit and Decision-Complete Plan

**Date:** 2026-11-05 · **Status:** PLAN, not implementation. No production file/DB/service changed.
**Inputs:** `GOALS.md`, first `REPORT.md`, `wave2/08-200-QUESTIONS.md`, `wave2/01`–`07`, execution-wave
plan, live VPS probes, local source. **Lens:** goal → research → code → product → operations.

## 1. Outcome

A hosted **Forge Conductor** on the existing DeerFlow 2.2/DeepSeek runtime that can execute a brief on
VectorCraft/PhotoCraft through exact CLI/MCP commands, verify the artifact and gates, record an
evidence-grade episode, propose only verified lessons, and require human approval to publish. The
first release is a **production operator**, not an autonomous artist and not a new generic harness.

**What users can do after Phase 1 that they cannot do now:** submit a brief, watch a real trace/retouch
run end-to-end, inspect the artifact hash + gates + blind critique, and reproduce the run from the
ledger — with no stub, no invented argv and no fake success.

## 2. Current behavior (evidence, no assumptions)

| # | Current behavior | Evidence | Status |
|---|---|---|---|
| C1 | Pipeline cannot execute any Craft step | `/opt/pod-pipeline/bin/*-cli` 122–127 B shims exit 127; last run failed there | `VERIFIED` |
| C2 | The argv contract is invented | `routes.py:73-80` (`trace`, `--input`, `--svg-out`) and `:88-96` (`--input` for PhotoCraft); real CLIs reject them | `VERIFIED` |
| C3 | Only two Craft apps are installed | VectorCraft 0.21.1 / PhotoCraft 0.20.2; Film/Design/Effect absent host-wide | `VERIFIED` |
| C4 | Craft MCP is not registered in DeerFlow | only `mcpServers.forge` exists; craft MCP handshakes work standalone | `VERIFIED` |
| C5 | DeerFlow 2.2 + DeepSeek run on the VPS | backend 2.2.0; `deepseek-flash`/“V4.1 Flash”, 1M ctx, 8k output; key by env name | `VERIFIED` config; key validity `UNVERIFIED` |
| C6 | No learning/eval ledger exists | `pod` has 5 tables, no episode/action/skill/eval; DB empty | `VERIFIED` |
| C7 | Console is a viewer | pure viewer at 127.0.0.1:8091; no job controls/auth | `VERIFIED` |
| C8 | README's live E2E claim is not reproducible now | `README.md:191–194`; DB empty and stub failure; it may be historical | `HISTORICAL/UNREPRODUCIBLE` |
| C9 | Gates can lie if read naively | `craft_trace:344` saves before gates; `:250` vacuous retype gate; `prep_print_art:356` `ok:True` with warning-only upscale | `READ` + prior probes |
| C10 | MCP endpoint is host-sensitive | `pod-mcp` 0.0.0.0:8765, unauthenticated, pod in Docker group | `VERIFIED` |
| C11 | 39 skills/400 answers are instructions, not runtime | installed skills; pipeline has no LLM/loader | `VERIFIED` |
| C12 | Foreign `AGENTS.md` | Grok App Builder contract (`/workspace`, port 8080) not this VPS | `READ` |

### 2.1 Measured Phase 0 contracts (do not revert to the old ASSUMPTIONs)

| Contract | Measured behavior |
|---|---|
| VectorCraft trace | `run --in F --cmd select.all --cmd imageTrace.make --params '{"params":{...}}' --cmd imageTrace.expand --export out.svg` → exit 0, `{"result":{"bytes":334,"format":"svg"},"step":"export"}`; PDF export also works; **export does not create parent dirs** (`os error 2`) |
| PhotoCraft run | `run <FILE|--new> --cmd ID --params J --out F`; opens traced SVG with a benign flatten warning; `image.trim` 161×121; `image.imageSize` at 300 ppi; creates parent dirs |
| VectorCraft MCP | `mcp --headless --automation-read-root … --automation-write-root …` |
| PhotoCraft MCP | `mcp` **without `--headless`**, same roots; dependent calls must be awaited (server can interleave) |
| Gateway/binary | gateway uid 0, glibc 2.36 ≥ binaries’ max GLIBC_2.35; bind mount is viable |
| Security | `POD_MCP_HOST=0.0.0.0` in `pipeline.env` overrides code default `127.0.0.1`; rebind is one value. Key validation: `GET /user/balance` + `GET /models` with Bearer; 200 valid, 401 invalid, 402 no balance; **never** use a chat completion as a key test |
| Visual defect | global SSIM catches 7/15; tile-min catches 13/15 but flags 3/4 clean controls; region SSIM catches 11/15 with 0/4 false alarms — combine region + tile + crop, not one threshold |

## 3. Goal→code gap matrix

| Goal | Research says | Code/runtime reality | Gap | Severity | Owner |
|---|---|---|---|---|---|
| G1 execute Craft | real 918/965 registries, MCP works | stubs, wrong argv, MCP unregistered | execution path broken | **P0** | task-8 |
| G2 native tools | use CLI/MCP, not GUI | no gateway; GUI bridge broken | no typed tool surface | **P0** | task-9/13 |
| G3 verify | six-rung evidence ladder | gates exist but can be vacuous/pre-artifact; no critic | no verifier/critic integration | **P0** | task-10 |
| G4 learn | L1/L2 buildable, L3/L4 not | no ledger/eval/retrieval/skill tables | no learner | **P1** | task-11 |
| G5 host | VPS capacity, model exists | 2 vCPU/7.9 GB; key unverified; no GPU | capacity/key risk | **P1** | task-12 |
| G6 approval | human gate | no approval table/queue; publish config unset | no safe publish | **P0** | task-9/12 |
| G7 truth | labels/evidence | README claim drift; foreign AGENTS | documentation must be corrected | **P1** | Lead |
| All apps | only VC/PC installed | Film/Design/Effect absent | scope must exclude | **P1** | Lead |
| Better-than-human | no benchmark | no eval | claim must be dropped | **P0** | Lead |

## 4. Decisions (rejected alternatives)

| # | Decision | Rejected | Why |
|---|---|---|---|
| D1 | DeerFlow 2.2 is the runtime/front door | build a new harness; use Eko as core | already hosted, MIT, memory/subagents/checkpoints; Eko is dormant/JS/in-memory |
| D2 | Build a **third `forge-*` plane** | embed LLM in pipeline/console | preserves deterministic pipeline and replaceable agent |
| D3 | Phase 0 fixes execution first | build ledger/agent first | without real commands, every downstream test is fake |
| D4 | VC + PC only for MVP | all Craft apps | others absent; claiming otherwise is false |
| D5 | Native CLI/MCP only in MVP | GUI/computer-use first | no display/GPU; bridge panics; commands are deterministic |
| D6 | Postgres `forge` DB + queue | new broker; reuse `pod` DB | one DB, no new service, `pod` untouched |
| D7 | L1/L2 memory + skills; promotion calibrated (no 3/3 shortcut) | fine-tune/RL now | API model, no GPU, no corpus/eval; simulation shows 3/3 LB 0.4385, so horizon + baseline required; claim discipline |
| D8 | Human-approved publish | autonomous publish | irreversible external side effect; template ids missing |
| D9 | Blind critic + crop evidence | one global SSIM/screenshot | measured 4% defect changes SSIM only 0.99994→0.9787 |
| D10 | Use donor mechanisms, original adapters | copy/vendor whole repos | maintenance/licence/verifiability; no verbatim code |

## 5. File-by-file change (planned; no production edit in this task)

### 5.1 Phase 0 — execution repair

| Path | Change | Test |
|---|---|---|
| `blueprint/files/deploy/craft-bin/*-cli` | replace 127 shims with launchers to `/opt/craft/*/bin` (absolute); keep refusal if absent | `--version` for VC/PC; absent app → named refusal |
| `blueprint/files/pod_pipeline/routes.py:73-80` | replace trace argv with `run --in {src} --commands {steps} --export {svg}` or dedicated wrapper | one real trace; artifact exists |
| `blueprint/files/pod_pipeline/routes.py:88-96` | replace PhotoCraft `--input` contract with `photocraft-cli run FILE ... --out` | one real retouch |
| DeerFlow `extensions_config.json` | register vectorcraft/photocraft MCP stdio with roots; no arbitrary host paths | `tools/list`, `command_batch` |
| `README.md:188-211` | relabel live-E2E as historical/unreproducible; state current blockers | doc read-back |
| `AGENTS.md` | replace foreign Grok contract with a DeerFlow Forge/VPS contract, or remove | no port-8080 claims |

### 5.2 Phase 1 — Forge skeleton

| Path | Change |
|---|---|
| `blueprint/files/forge/contracts.py` | TaskEnvelope, ArtSpec, Handoff, ToolCall, Artifact, Verdict (versioned) |
| `blueprint/files/forge/gateway.py` | absolute binary registry, allowlist/roots/idempotency/refusals |
| `blueprint/files/forge/verifier.py` | artifact hash/dimensions/DPI + gate-report parser + read-back |
| `blueprint/files/forge/jobs.py` | Postgres queue `FOR UPDATE SKIP LOCKED`, leases, attempts |
| `blueprint/files/sql/schema_forge.sql` | new `forge` DB tables: episode/event/handoff/tool_call/artifact/gate/critique/eval/skill/job/budget/role |
| `blueprint/files/forge/critic.py` | blind prompt/schema, crop grounding, cannot-assess path |
| `blueprint/files/forge/memory.py` | episode append, bounded retrieval, candidate lessons |
| `blueprint/files/forge/promotion.py` | Wilson bound, N≥3, regression, approve/rollback |
| `deploy/systemd/forge-conductor.service` | loopback 8092, `ProtectSystem=strict`, env file |
| `deploy/systemd/forge-worker.service` | queue worker, ≤2 concurrency, one craft semaphore |
| `deploy/systemd/forge-ui.service` | optional 8093 operator approval UI (loopback) |

### 5.3 Phase 2 — learning and evaluation

| Path | Change |
|---|---|
| `blueprint/files/forge/eval.py` | golden runner, A/B arms, metrics, JSON report |
| `blueprint/files/forge/evaluation/` | 10–50 golden fixtures (rights-cleared) |
| `blueprint/files/skills/*` | the five research skills + operator; loaded by agent, not pipeline |
| DeerFlow memory config | keep DeerMem for facts; Forge ledger for episodes/skills; do not duplicate |

### 5.4 Never change

`pod` schema, orchestrator determinism, console viewer contract, Craft app binaries/catalogues,
publish without approval, any secret value in repo/logs.

## 6. Failure modes and required behavior

| Failure | Required behavior |
|---|---|
| Missing/stub binary | named `E_APP_UNAVAILABLE`; no fallback that pretends success |
| Wrong argv/unknown id | `E_COMMAND_UNKNOWN`/`E_PARAM_REJECTED`; stop |
| No document/selection | open/select first; `enabled:false` is state, not absence |
| PhotoCraft concurrent MCP | await each reply; never pipe dependent calls |
| Artifact exists but gate failed | `failed`; preserve artifact for diagnosis; no ship |
| `prep_print_art.ok` true with warning | parse `warnings`; over-2.5× upscale is a refusal for print |
| Text gate with 0 boxes | `unverified`, not pass |
| Source mutated | fail episode; quarantine |
| Key missing/invalid | named refusal; no fake completion; owner-approved live test |
| Budget exceeded | stop before spend; `E_BUDGET` |
| Worker crash | lease expiry/requeue; idempotent tool key; no duplicate publish |
| Critic/gate disagree | `needs_human`; never critic override |
| Publish without approval | refuse; `E_PUBLISH_NOT_APPROVED` |
| App/catalogue drift | pin hash; skill expired until revalidated |

## 7. Tests (discriminating, including error paths)

| Test | Command / evidence | Pass |
|---|---|---|
| T0 versions | `vectorcraft-cli --version`, `photocraft-cli --version` | expected versions |
| T1 trace | real 1024² badge via `craft_trace`/run | SVG/PNG + report, `ok:true`, 10 gates |
| T2 retouch | PhotoCraft crop→filters→imageSize on copy | 2400×3000, 118.11 px/cm |
| T3 MCP | initialize → tools/list → command_batch | 33/26 tools; batch result |
| T4 refusals | unknown id/outside root/missing doc | named codes; no write |
| T5 duplicate | same idempotency key twice | one effect, same result |
| T6 crash/resume | kill worker mid-episode | lease requeue; no duplicate |
| T7 verifier | fixture with failed gate | `failed`, not ship |
| T8 critic | labelled defect set | precision/recall + false-pass reported |
| T9 promotion | calibrated horizon (e.g. n=8, k≥7, LB>p0) + regression + human | simulation shows null-promotion rate and retention; 3/3 rule rejected; no overclaim |
| T10 packaging | copy corpus/skills | links/JSON/validation clean |
| T11 docs | README claims | no unreproducible “live E2E” |

## 8. Rollback

- **Phase 0:** restore original `deploy/craft-bin` shims, `routes.py`, DeerFlow MCP config from backup;
  no DB migration.
- **Phase 1:** stop/disable `forge-*` units; `DROP DATABASE forge`; artifacts remain content-addressed;
  `pod` untouched.
- **Phase 2:** feature flag `FORGE_MEMORY=off`; retrieval/skills disabled; prior skill versions retained.
- Every file change has a pre-change SHA-256; rollback is a pointer/file restore, not a rewrite.
- If a live key test was approved, record spend; rotate the key if exposed.

## 9. Out of scope / blockers

- FilmCraft/DesignCraft/EffectCraft not installed; no command claims.
- GUI/computer-use blocked by missing display and broken control bridge.
- No fine-tune/RL (API model, no GPU/open weights/corpus).
- No autonomous publish; template ids missing.
- DeepSeek key validity not proven without an owner-approved live call.
- No “better than human designer” claim; no blind study.
- Adobe tutorials not executed; 50-task corpus is a proposal.
- Production migration/implementation is **not** authorized by this plan.

## 10. Diagram index (validated via Kroki)

| Diagram | Purpose | Source |
|---|---|---|
| `01-goal-gap` | goals → code gaps → phases | `diagrams/01-goal-gap.mmd` |
| `02-runtime-topology` | VPS services/ports/planes | `02-runtime-topology.mmd` |
| `03-craft-command-path` | operator → gateway → CLI → verifier → critic | `03-craft-command-path.mmd` |
| `04-forge-architecture` | roles, memory, tools, data | `04-forge-architecture.mmd` |
| `05-learning-state` | episode/skill/rollback state machine | `05-learning-state.mmd` |
| `06-evidence-ladder` | why each proof rung matters | `06-evidence-ladder.mmd` |
| `07-decision-tree` | build-vs-buy / scope choices | `07-decision-tree.mmd` |
| `08-roadmap` | phase gates/time | `08-roadmap.mmd` |

## 11. Open questions only the owner can answer

1. Is the live DeepSeek key valid, and may we spend a minimal completion to prove it? **Preferred:
   use the zero-spend metadata check first** (`GET /user/balance`, `GET /models`); a chat completion is
   not a key test.
2. Which Craft app is the first commercial target: VectorCraft or PhotoCraft?
3. Are FilmCraft/DesignCraft/EffectCraft available from a private artifact store, or out of scope?
4. Who is the human approver for print/publish and skill promotion?
5. What are the rights for the first 10/50 golden assets?
6. Is “Harness 2” the Google Harness² project, or an internal second harness? (terminology)
7. Is the desired interface chat-only, or an operator UI with approvals?
8. What is the cost ceiling per artifact/day?

## Verdict

**The product is buildable now only as a narrow, evidence-gated operator (VectorCraft + PhotoCraft).**
The model and harness already exist; the blockers are execution wiring, verification, ledger/approval,
and scope honesty. Phase 0 must fix the execution path before any “learning” work is meaningful.
