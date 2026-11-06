# DeerFlow Forge

**A local architecture console + a local Forge control plane + a deployable print-on-demand pipeline package.**

DeerFlow Forge is three related things in one repository. It is **not** a production service today, and
it does **not** currently execute Craft commands through its agent loop.

| Part | What it is | What it is not |
|---|---|---|
| **Console** (`src/`, `public/`, `scripts/`, `server/`) | TanStack Start + Vite + React 19 viewer for the blueprint: Board, Routes, Sandbox, Playbook, Sources | No backend, no agent loop, no Craft execution. “Run route” is an animation. |
| **Blueprint package** (`blueprint/files/`) | Python `pod_pipeline`, Postgres schemas, Docker/systemd/MCP assets, Craft CLI shims, tests | Not deployed; production Craft binaries and argv are not proven end-to-end |
| **Forge local core** (`blueprint/files/forge_*.py`) | Gateway policy, Postgres DDL/repository, queue worker/reaper, loopback service, verifier, blind critic, eval/promotion contract | No production DB/service, no real executor wiring, no learning loop |

**Date:** 2026-11-05 · **Production:** untouched · **DeerFlow MCP registration:** not applied.

---

## 1. Verified state

These are commands that were run in this checkout/staging, not architectural intentions.

| Gate | Result |
|---|---|
| Console tests | **65 passed, 0 failed, 0 skipped** (18 suites) |
| `tsc --noEmit` | exit 0 |
| Lint | **0 errors / 5 warnings** |
| Console build | Vite `node-server` build succeeded; `.output/server/index.mjs` serves HTTP 200 |
| Visual smoke | `ok:true`, zero failures; all five sections non-empty |
| Playwright controls | **18/18** (tabs, five model radios, route run completes, sandbox `runner.py`, Copy→`Copied`, Download event, mobile 390×844, 34 source options, zero overflow, zero console errors) |
| Keyboard/a11y | **8/8** (one h1, all controls named, 3 landmarks, 12/12 visible Tab stops, ≥40 px tap targets, zero runtime errors) |
| Forge local tests | **141 passed, 16 skipped**, 7.56 s |
| Forge staging suite | **194 passed, 5 skipped**, scratch PostgreSQL 16 + G0 bundle, 16.30 s |
| Forge gateway | 36/36; policy + async idempotency + replay |
| Persisted tool calls | **5 real-PostgreSQL tests**: success→replay, in-flight duplicate refusal, executor-crash failed row, stale recovery→replay, fresh in-flight untouched |
| Process executor | **8/8 tests**: absolute binary, artifact hash, timeout kill, missing artifact, typed params/work-root expansion, `--version` probe |
| Craft registry | VectorCraft **0.21.1** and PhotoCraft **0.20.2** bound to absolute paths; VPS version probe passes |
| Live Craft trace | Real VectorCraft trace through gateway → PostgreSQL: exit 0, 2 artifacts (SVG 6,051 B; PDF 13,610 B), persisted and replayed without re-execution |
| Eval persistence | **real-PostgreSQL test**: baseline+memory rows, duplicate→`E_EVAL_EXISTS`, missing episode→`E_EPISODE_NOT_FOUND` |
| Forge SQL | 18/18 assertions + `SKIP LOCKED`; real Postgres |
| G0 provenance | independently reproduced byte-identically; 22/22 hashes; 9/9 applicable gates |
| **Live VPS console** | `09b20e5` built/deployed at `/opt/deerflow-forge`; unit active on `127.0.0.1:8091`; **22/22** live black-box checks (tabs, five routes, fault path, deep-links, 34 sources, copy/download, keyboard, reload×3, mobile) |
| **Live CUA** | Chrome driven natively via CUA 0.28.2: window launch, Sandbox, Run route→`Run again`, Sources+Copy verified on the system clipboard |
| **Live Forge HTTP** | VPS service on scratch PostgreSQL: health 13 tables; create `201`; replay `200 replayed:true`; bad input `400`; unknown `404` |
| **Live worker** | VPS worker claimed/finished a real job, handler received payload; empty second run `claimed:0` |

Evidence: [`docs/TRACE/2026-11-05/GATE-FINAL-W2.md`](docs/TRACE/2026-11-05/GATE-FINAL-W2.md),
[`docs/TRACE/2026-11-05/LIVE-VPS-VERIFICATION.md`](docs/TRACE/2026-11-05/LIVE-VPS-VERIFICATION.md)
and [`docs/CAPABILITY-MATRIX.md`](docs/CAPABILITY-MATRIX.md).

---

## 2. Architecture and real wiring

```text
Operator / browser
      │
      ▼
Console (static React viewer) ── no HTTP calls ──► blueprint data in src/lib/blueprint/model.ts
      │
      │  (nothing)
      ▼
┌─────────────────────── Forge local core ───────────────────────┐
│ forge_service.py  loopback HTTP: /healthz, /v1/episodes*      │
│        │ repo factory (runnable: python -m forge_service)     │
│        ▼                                                       │
│ forge_repo.py  asyncpg: episodes, jobs, transitions, events    │
│        ▲                                                       │
│ forge_worker.py  python -m forge_worker --once (queue/reaper)  │
│                                                                │
│ forge_gateway.py  async policy + persisted Repo + injected Executor │
│        │ ForgeGatewayRepo: in_flight/terminal/replay   │
│        │ NO real Craft executor                          │
│        ▼                                                       │
│ forge_verifier.py / forge_critic.py / forge_eval.py            │
│        └── pure contract libraries; no route/worker consumer   │
└────────────────────────────────────────────────────────────────┘

blueprint pod_pipeline / Craft CLIs ── separate from Forge service; production not wired
DeerFlow runtime ── designed front door; MCP registration not applied
```

### Wired

- **Console → static model:** tabs/controls render from `src/lib/blueprint/model.ts` and `sources.ts`.
- **Service → repository:** `make_server(repo_factory=…)` and `python -m forge_service` construct
  `ForgeRepo` on the service event loop; the daemon refuses non-loopback binds.
- **Worker → repository:** `python -m forge_worker --once` claims jobs, runs a handler, finishes
  guarded, and reaps expired leases through `ForgeRepo`.
- **Gateway → policy:** registry, role allowlist, root containment, idempotency key, verdict ladder and
  `InMemoryRepo` are tested as a unit.
- **Gateway → PostgreSQL:** `ForgeGatewayRepo` writes `forge_tool_call` atomically: an `in_flight`
  row before execution, a terminal row after, and duplicate keys replay the persisted result without
  calling the executor. A concurrent in-flight duplicate raises `E_IDEMPOTENCY_IN_FLIGHT`.
- **Verifier/critic/eval → tests:** artifact hash/format/dimensions/DPI, blind-critic schema, and Wilson
  promotion decisions are covered by tests.
- **G0 artifacts → local evidence:** trace/retouch artifacts and gate reports are verified locally.

### Not wired

| Seam | Evidence | Consequence |
|---|---|---|
| Gateway → service/worker caller | no route or job calls `Gateway.execute` | gateway is library-level; not an automated pipeline |
| Gateway → real Craft executor | `Executor` is injected; no production executor module | gateway cannot execute Craft commands |
| Verifier/critic/eval → service/worker | contract modules have no route, queue consumer or repo writer | verification/critique/eval are callable libraries, not an automated pipeline |
| Console → agent/service | console has no API client or agent loop | UI is a viewer only |
| `pod_pipeline` → real Craft CLI | `/opt/pod-pipeline/bin/*-cli` may be stubs; real binaries live under `/opt/craft` | production pipeline is not proven end-to-end |
| DeerFlow → Forge | registration not applied | no DeerFlow-hosted Forge tools |
| Eval → learning loop | no retrieval/A-B/promotion activation/rollback | learning claim remains **L0** |

---

## 3. Repository map

| Path | Purpose |
|---|---|
| `src/components/forge/` | Seven console components: shell, board, routes, sandbox, playbook, sources, copy/download |
| `src/lib/blueprint/` | Model, sources registry, clipboard fallback; the console’s only data source |
| `scripts/` | Build/test/visual smoke helpers (`visual-console-smoke.mjs`, `browser-smoke.mjs`) |
| `blueprint/files/pod_pipeline/` | Existing deterministic print pipeline |
| `blueprint/files/forge_gateway.py` | Typed tool gateway, policy checks, idempotency key, verdict helpers |
| `blueprint/files/forge_repo.py` | Async PostgreSQL repository; episodes, jobs, transitions, events |
| `blueprint/files/forge_worker.py` | Queue worker, `LeaseReaper`, `--once` CLI |
| `blueprint/files/forge_service.py` | Loopback HTTP service + daemon entry point |
| `blueprint/files/forge_verifier.py` | Artifact existence/SHA-256/PNG/dimensions/DPI + gate-report verification |
| `blueprint/files/forge_critic.py` | Blind-critic schema, evidence combination, gate/critic/human resolver |
| `blueprint/files/forge_eval.py` | Wilson lower bound, golden evaluation, promotion proposal (inactive) |
| `blueprint/files/sql/schema_forge.sql` | 13-table Forge DDL, state functions, hash-chained events |
| `blueprint/files/tests/` | Unit, real-Postgres, gateway, service, worker, verifier, critic, eval tests |
| `docs/` | Current capability matrix, plan continuation, TRACE evidence |
| `research/eko-deerflow-agent/` | Research corpus, G0 evidence, historical execution waves (do not read as current state) |

---

## 4. What it can and cannot do

### Can

- Render a five-tab blueprint console, navigate keyboard-only, copy/download source text, switch five
  product models, and play the documented route animation.
- Validate Forge tool policy (unknown tool, role denial, root escape, duplicate idempotency key).
- Create/read episodes through a loopback service over real PostgreSQL; replay duplicate episode keys
  with `200 replayed:true`; return named 400/404/500/503/504 errors.
- Claim/finish jobs, requeue or abandon expired leases, and run the worker from a CLI.
- Verify PNG artifacts by SHA-256, format, dimensions and both DPI axes; combine gate/critic/human
  evidence into a named verdict; compute Wilson lower bounds and refuse unsupported promotion.
- Reproduce the G0 trace/retouch artifact evidence locally on scratch infrastructure.

### Cannot / do not claim

- Production Forge DB, service unit, TLS/auth, deploy, or restore drill.
- Full Craft execution through Forge or the service; no real executor is wired.
- DeerFlow MCP registration or a DeerFlow-hosted agent loop.
- Publish to Fourthwall; no approval queue or templates configured.
- DesignCraft/EffectCraft/FilmCraft; they are absent.
- Vision-critic accuracy (no model run) or learning L1/L2/L3/L4 (no retrieval/A-B/promotion/rollback).
- Native GUI/CUA capture; no desktop bridge is available.
- All 918 Craft commands; only measured VectorCraft/PhotoCraft contracts and 33/26 MCP tools are known.
- `pod_pipeline` production argv/CLI is proven; the real binaries and shims are separate.

---

## 5. Run it

```powershell
# console
npm.cmd test
npm.cmd run typecheck
npm.cmd run lint
$env:NITRO_PRESET='node-server'; cmd /c "npm.cmd run build"
node .output/server/index.mjs            # PORT defaults to 8092; serve locally
node scripts/visual-console-smoke.mjs http://127.0.0.1:8092

# Forge local tests (no DB)
cd blueprint/files
python -m unittest discover -s tests -p 'test_forge_*.py'

# real-DB staging (separate PostgreSQL 16; never point at production)
$env:FORGE_TEST_DSN='postgresql://postgres:scratch@127.0.0.1:55439/postgres'
pytest tests -q

# runnable Forge service (loopback only; real DB required)
$env:FORGE_DSN='postgresql://forge:...@127.0.0.1:5432/forge'
python -m forge_service --port 8092

# worker, once
python -m forge_worker --once --dsn $env:FORGE_DSN --handler my.module:handle
```

The service refuses non-loopback hosts. Secrets are read from `FORGE_DSN`/environment and are never
printed by the daemon.

---

## 6. Current plan and next steps

The decision-complete plan is [`docs/PLAN-CONTINUATION.md`](docs/PLAN-CONTINUATION.md). Short form:

1. **W1 — tool-call idempotency persistence (DONE).** `ToolResult` carries episode/tool/params/argv/
   duration; `Gateway.execute` and `Repo` are async; `ForgeGatewayRepo` writes an `in_flight` row
   before execution and replays terminal rows. Tested against real PostgreSQL.
2. **W5 — eval-row persistence (DONE at repository level).** `ForgeRepo.record_eval()` writes one
   immutable row per episode/arm and refuses duplicates; **no consumer/route calls it yet**.
3. **Executor + Craft registry (DONE).** `ProcessExecutor` validates absolute binaries, runs without a
   shell in an explicit work root, kills on timeout, captures bounded stderr and hashes artifacts.
   `forge_craft_registry` binds VectorCraft 0.21.1/PhotoCraft 0.20.2 and probes versions. A real
   VectorCraft trace through the gateway persisted 2 artifacts and replayed without re-execution.
4. **Consumer seam (next).** Wire gateway/verifier/critic/eval into a worker job or service route with evidence rows.
5. **Production hardening.** systemd, TLS/auth, migration/rollback, backup/restore drill, supervised
   reaper, DeerFlow registration.
6. **Learning.** Only after 1–5: episode retrieval, A/B, promotion/rollback; otherwise remain L0.

---

## 7. Evidence discipline

- `VERIFIED` = command/output or fetched primary source.
- `READ` = source/document inspected, not executed.
- `INFERRED` = reasoned from code; no run.
- `UNVERIFIED` = no evidence; say what would settle it.
- `HISTORICAL` = true earlier, not current.

Historical execution-wave files retain their original claims; the current-status answer is
`docs/CAPABILITY-MATRIX.md`, `docs/PLAN-CONTINUATION.md`, and the latest TRACE gate report.
