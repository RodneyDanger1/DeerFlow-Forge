# Capability Matrix and Truth Audit — 2026-11-05

**Scope:** DeerFlow Forge local workspace + staging evidence. **No production deploy is claimed.**
Evidence labels: VERIFIED (executed here), READ (source/docs), HISTORICAL (dated, not current),
UNVERIFIED. This file is the current capability answer; dated `execution-wave/*` files remain history.

## 1. What the system can do now

| Capability | Status | Evidence | Limit |
|---|---|---|---|
| Console navigation/controls | **CAN** | 5 tabs, **18/18** Playwright control checks, **8/8** keyboard/a11y checks, desktop + 390×844 | static viewer; “Run route” is a simulation, not Craft execution |
| Console copy/download | **CAN** | Copy → `Copied`; Download event fires | real browser permission prompt unverified |
| Console build | **CAN** | `vite build` with `node-server`; smoke `ok:true` | console only; no production Forge DB/service |
| Live VPS console | **CAN** | HEAD `09b20e5` at `/opt/deerflow-forge`, unit active on 8091, 22/22 live black-box checks; CUA native launch/nav/run/copy | no production Forge service |
| Forge gateway policy | **CAN** | 36/36 tests: allowlist, roots, replay, refusals, verdict ladder; async execute | executor is injected |
| Persisted tool calls | **CAN** | 3 real-PG tests: in_flight before execution, terminal replay, in-flight duplicate refusal, executor-crash failed row | no stale in-flight expiry/recovery |
| Forge DDL | **CAN** | 13 tables/36 edges; apply-twice on scratch PostgreSQL 16 | scratch only; no migration/rollback drill |
| SQL invariants | **CAN** | 18/18 assertions; `SKIP LOCKED` 9 ms | 4 DB-dependent tests remain skipped without DSN |
| Repository | **CAN** | real-Postgres tests; episodes, jobs, lease abandon, exactly-one transition event, eval rows; expired lease requeues or abandons | no production DB/role |
| Worker/lease reaper | **CAN** | 10/10 local worker/service tests; abandoned-at-max test | no supervised daemon |
| Loopback service | **CAN** | 5/5 tests; real HTTP→repo→worker→reaper 2/2; health 200/503; cancellable timeout → `504 E_SERVICE_TIMEOUT`; idempotent replay `200 replayed:true`; strict POST validation; runnable `python -m forge_service` daemon | no TLS/auth; loopback only |
| Artifact verifier | **CAN** | 8/8 tests; real G0 pair passes; PNG-format and both-DPI checks; tamper/vacuous/failed/malformed refuse | no independent render/tile metrics |
| Blind-critic contract | **CAN** | 14/14 tests; gate authoritative; invalid `human`/non-bool `gate_ok` refuse; disagreement→needs_human | **no vision model or accuracy measurement** |
| Evaluation/promotion contract | **CAN** | 13/13 tests; Wilson LB; 3/3 refused; 8/8 candidate only with human; regressions refuse; `record_eval` persists one row per episode/arm | proposal only; **no consumer/route and no activation/learning claim** |
| G0 real trace/retouch | **CAN** | independent staging reproduction; 22/22 hashes; 9/9 applicable | no production publish |
| Skill guidance | **CAN** | 39 skills, prior 39/39 validation; W1-C guidance only | not runtime enforcement |
| Research corpus | **CAN** | 179 source files, 400 answers, 6 examples, 8 system diagrams + integration map | 189-file desktop package includes **6 skills** (`agent-learning-loop`, `craft-agent-operator`, `forge-harness-architect`, `harness-code-adapter`, `research-corpus-navigator`, `visual-verification-critic`) |
| Live Forge HTTP/worker | **CAN** | VPS service against scratch PostgreSQL: health 13 tables, `201`, `200 replayed:true`, `400`, `404`; live worker claimed/finished one job, empty queue `claimed:0` | temporary scratch DB/process, not production |
| Local Forge e2e | **CAN** | full staging suite **177 pass/4 skip** with scratch PG + G0 (14.42 s); local Forge-only **123 pass/13 skip** | not production |

## 2. What it cannot do (do not claim)

| Capability | Status | Blocking fact |
|---|---|---|
| Production Forge service/DB | **CANNOT** | no service unit, production `forge` DB/role, TLS/auth, or deploy |
| Full Craft execution through service | **CANNOT** | gateway/service do not invoke Craft; separate seam |
| DeerFlow MCP registration | **CANNOT** | config not applied; standalone MCP proof only |
| DesignCraft/EffectCraft/FilmCraft | **CANNOT** | apps absent; named refusals only |
| Publish to Fourthwall | **CANNOT** | approval/template/credentials not configured; no publish path |
| Vision critic accuracy | **CANNOT CLAIM** | model never run; ≥50 labelled defect set not executed |
| Learning L1/L2 | **CANNOT CLAIM** | verifier/critic/eval contracts exist, but no episode retrieval/promotion loop, live corpus, or A/B |
| Learning L3/L4 | **CANNOT** | no corpus/GPU/RL fleet |
| Native GUI/CUA | **CANNOT CLAIM** | no working desktop GUI bridge; headless browser only |
| All 918 Craft commands | **CANNOT** | only measured VC/PC contracts and 33/26 MCP tools proven |

## 3. Conditional / unverified

| Item | Why unverified | What would prove it |
|---|---|---|
| 4 skipped staging tests | DB/DSN-specific setup | run with their required staging service |
| Clipboard under real permission prompt | headless API stayed pending; fallback tested | manual browser permission test |
| Service under crash/restart | loopback tests only | systemd + kill/restart + lease recovery |
| Critic visual precision/recall | no model/corpus | held-out labelled defect run |
| Production `/opt/pod-pipeline` state | not inspected this pass | read-only VPS inventory + deploy gate |
| DeepSeek key validity | not exercised | owner-approved live call |
| Full publish | templates/credentials absent | template IDs + approval + read-back |

## 4. Truth corrections applied

| Old claim | Current truth | Evidence |
|---|---|---|
| 207 JS tests (205/2) | **65/65** | `npm.cmd test` |
| 31 pipeline tests | **177 pass/4 skip** current staging suite; **123 pass/13 skip** local Forge-only | scratch PG + G0 + `pytest`; see `GATE-FINAL-W2.md` |
| 131-file package | **179 source / 189 desktop package** | filesystem count |
| Live VPS effect/publish E2E | **HISTORICAL, not reproducible** | EffectCraft absent; no production deploy/publish |
| DeerFlow loads Forge tools | **UNVERIFIED/HISTORICAL** | registration not applied |
| “Do not start W2” | **superseded** | G0 provenance closed; W2 local gate PASS |
| “No critic integration” | **local contract only** | verifier 8/8, critic 14/14; no model |
| 8 diagrams | **8 system diagrams + 1 integration map** | corpus |
| 3/3 promotion rule | **rejected; Wilson LB 0.4385**; n=8 suggestion is simulation only | promotion evidence |

## 5. Algorithm/data accuracy checks

- Promotion: 3/3 Wilson 95% lower bound = **0.4385**; no k passes threshold at n=3–5. The n=8/k≥7
  variant is a **simulation suggestion**, not an adopted policy.
- G0 trace report: **9/9 applicable**, retype `applicable:false`, actual trace hash
  `ab64aad7”¦`, output 1500×1800 at 299.9994 DPI.
- Forge SQL: **13 tables / 36 transitions**, 18 assertions, no vacuous counts.
- Test counts are environment-qualified: “4 skipped” is **not** four passes.
- UI Copy: the first probe was a **stateful-locator false negative**; stable locator shows `Copied`.

## 6. Authoritative docs updated

`README.md`, `docs/PLAN-CONTINUATION.md`, `research/eko-deerflow-agent/README.md`,
`00-START-HERE.md`, `ARCHITECTURE.md`, plus this matrix. Dated `execution-wave/*` evidence files were
not rewritten; their historical counts remain historical.
