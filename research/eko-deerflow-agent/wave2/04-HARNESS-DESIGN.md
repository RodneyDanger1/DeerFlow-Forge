# Forge Conductor — Hosted Harness Design

**Wave 2 · Task 04 · Design only · 2026-11-05**
Owner: Riley · Author: harness-architect (delegated) · Scope: DeerFlow Forge / Craft family

> **Status: DESIGN, NOT IMPLEMENTATION.** No service, unit, migration, table, prompt or code was
> created by this task. Nothing here is deployed. The only host actions taken were **read-only
> probes** over SSH (Appendix A). Production code, the pipeline, and the skills were not modified.
>
> **Evidence labels used throughout**
> `[V]` verified this session by a read-only command on the host (exact command + output in Appendix A)
> `[R]` read from a local repository file, with path (and line where useful)
> `[D]` verified in the prior dossier (`research/eko-deerflow-agent/REPORT.md`) and **not** re-executed
> `[I]` inference or design decision — not yet tested
> `[U]` unverified; becomes policy only after the named check is run
>
> The dossier's V/R/I/U taxonomy is reused, but `[V]` here means *this session on this host*, which is
> stricter than the dossier's `[V]` (a source read on 2026-11-05). Where they differ, this file's label wins.

---

## 0. The problem in one paragraph

Existing agents can already operate the Craft tools through typed commands, and DeerFlow 2.2 is
already installed on the host with a working model configuration. What does not exist is the layer
that makes an agent *trustworthy* on production art: a typed tool gateway with roots and refusals, a
verifier that refuses to believe exit codes or screenshots, a critic grounded in rendered evidence, a
durable episode ledger, and a promotion loop that can be rolled back. The Forge Conductor is that
layer. It is deliberately **not** a new agent framework, **not** a pixel-first computer-use agent, and
**not** a fine-tuning program.

---

## 1. Decision summary

| # | Decision | Why | Confidence |
|---|---|---|---|
| D1 | **Build a third plane** (`forge-*`) next to the existing console plane and pipeline plane. Do not embed an LLM loop in `pod_pipeline` or in the console. | Preserves the deterministic pipeline's reproducibility; the agent stays replaceable; existing units keep working if forge is stopped. `[R] deploy/vps/*.service, blueprint/files/deploy/systemd/*` | High |
| D2 | **Conductor + 6 capability-scoped specialists**, with typed handoffs over a queue table — not freeform chat between agents. | Every handoff is auditable and replayable; no context soup; roles enforce separation of duties. `[I]` | High |
| D3 | **Native CLI/MCP first, Playwright GUI only as a declared, logged fallback**, and a GUI success never counts as verification. | The Craft apps expose the same command registry to CLI/JSON/MCP `[D: A1–A3]`; GUI-only paths are slower and unverifiable. `[I]` | High |
| D4 | **Five-rung evidence ladder**: process → artifact → domain gates → rendered perception → visual critic, plus human rubric for taste/publish. A verdict is `pass` only if all rungs agree. | Exit 0 and screenshots are both forgeable/stale; the Orca/OpenAdapt lesson is verify the effect, not the screen. `[D: B4]` | High |
| D5 | **Blind critic**: the Visual Critic never sees exit codes, gate results, or the operator's success claim. It must cite crop evidence per rubric dimension or the schema rejects it. | Prevents confirmation bias and "looks good" verdicts. `[I]` | Medium |
| D6 | **Four memory stores**: episode ledger (append-only, hash-chained), case retrieval, semantic brand facts (temporal validity), procedural skill library (versioned, executable, pinned). "Learning" = context/policy change, **not** weight change. | Retrieval + skills give most early gain at low risk; fine-tuning needs a corpus and eval that do not exist. `[D: Q107, Q109–Q115]` | High |
| D7 | **Promotion is statistical and reversible**: draft → candidate → active requires ≥3 independent successes + golden regression + human sign-off, and any failure demotes/rolls back by pointer flip. | Prevents one lucky demo from becoming policy. `[I]` | High |
| D8 | **Postgres-native orchestration** (job table with `FOR UPDATE SKIP LOCKED` + explicit state machine). Do **not** add a broker; do **not** make DeerFlow or LangGraph own durable state. | One database, transactional with the ledger, 2 vCPU host, and the existing pod-postgres instance is already running. `[V]` postgres container + 5-table check | High |
| D9 | **Two-kilobyte discipline on the model**: `deepseek-flash` (`DeepSeek V4.1 Flash`) with `max_tokens: 8192` is treated as a bounded-output planner/drafter only; long artifacts live on disk and are referenced by hash. | Config-verified output cap `[V]`, 1,048,576-token context `[V]` but output is the constraint. `[I]` | High |
| D10 | **No fine-tuning, no RL, no autonomous publish** in Phases 0–2. Phase 3 is optional and gated on retrieval plateau + frozen goldens. | Gate-optimised RL produces gate-passing art; rights-cleared trajectory corpus does not exist. `[D: Q108, Q116]` | High |

**Explicit non-claims:** not implemented; not measured; not "better than a human designer"; no FilmCraft
or design-quality result (only VectorCraft 0.21.1 and PhotoCraft 0.20.2 are installed — see §2).

---

## 2. Verified environment baseline

Everything in this table was observed read-only on `srv2108523` this session unless labelled otherwise.
Full commands and raw output: Appendix A.

### 2.1 Host and services `[V]`

| Fact | Observed |
|---|---|
| Host | `srv2108523`, Linux `7.0.0-38-generic`, **2 vCPU** |
| Memory | 7,935 MB total; ~4,835 MB available at probe; load average `1.37, 1.12, 0.84` |
| Disk | `/` 96 G, 63 % used, **36 G free** |
| Uptime | 7 days |
| Active units | `deerflow-forge-console.service`, `pod-mcp.service`, `pod-worker.timer`, `docker` |
| Timers | `pod-worker.timer` every 60 s, `Persistent=true` (last trigger 16:11:01 UTC) |
| Listeners | `127.0.0.1:8091` console (node), `127.0.0.1:5432` pod-postgres (docker-proxy), **`0.0.0.0:8765`** pod MCP (python) |
| Directories | `/opt/{deer-flow, deerflow-forge, pod-pipeline, node22, uv-python, craft}` |
| Containers | `deer-flow-gateway`, `deer-flow-frontend`, `deer-flow-nginx` (127.0.0.1:2026), `deer-flow-redis` (not published), `pod-postgres`, `ridgeboundia-app`, `ridgeboundia-caddy` (**0.0.0.0:80,443**), `ridgeboundia-postgres`, `ridgeboundia-dev-pg` (127.0.0.1:5433) |
| Firewall | `ufw` active; 22/80/443 open; 8765 allowed only from `172.16.0.0/12` and `192.168.200.0/24` |

**Consequences for design:** the host is already loaded and shared with an unrelated shop app and the
DeerFlow stack. Forge must be a polite neighbour: loopback binds only, ≤2 concurrent episodes, a
global single-craft-step semaphore, disk quota, and no new public ports. `80/443` are already owned by
Caddy, so Forge gets its own loopback port and is reached by SSH tunnel (same pattern as the console).

### 2.2 Model configuration `[V]`

`/opt/deer-flow/config.yaml` (api_key value redacted at source; only the **name** `DEEPSEEK_API_KEY`
appears in the container environment):

```yaml
models:
- name: deepseek-flash
  display_name: DeepSeek V4.1 Flash
  model: deepseek-flash
  context_window: 1048576
  max_tokens: 8192
  timeout: 600.0
  max_retries: 2
  supports_vision: true
  supports_thinking: true
subagent_runtime:
  max_running: 3
  max_queued: 64
  admission_policy: queue
  queue_timeout_seconds: 300
recursion_limit: 100
token_budget:
  enabled: false
```

`docker exec deer-flow-gateway env | cut -d= -f1` shows `DEEPSEEK_API_KEY` — **the key exists in the
running DeerFlow gateway by name only; its value was neither read nor logged by this task.**

**Consequences:** (a) vision calls are plausible but **not** yet proven on print defects `[U]`;
(b) 8,192 output tokens forces structured, short specialist outputs; (c) "DeepSeek V4.1 Flash" is the
config's `display_name`, not an independently verified product version `[U]`; (d) a 600 s timeout and
2 retries set the per-call failure budget.

### 2.3 Craft installation `[V]`

| Surface | Reality |
|---|---|
| VectorCraft | `/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli`, `--version` → `vectorcraft-cli 0.21.1` |
| PhotoCraft | `/opt/craft/photocraft/photocraft-0.20.2-linux-x86_64/bin/photocraft-cli` |
| Catalogues | `/opt/craft/catalogues/{vectorcraft,photocraft}-commands.json` (552 KB / 84 KB) |
| FilmCraft / DesignCraft / EffectCraft | **not installed** (absent from `/opt/craft`) |
| CLI resolution | `command -v vectorcraft-cli` → **MISSING**; `/opt/pod-pipeline/bin/*-cli` are the shipped **placeholder shims** that print "vendor binary not installed" and `exit 127` |

**This is a material finding.** The README's live end-to-end claim (trace → trim → effect → PNG) is
**not reproducible in the current host state**: `runner.py` prepends `/opt/pod-pipeline/bin` to `PATH`
`[R: pod_pipeline/runner.py _env()]`, so the bare argv `vectorcraft-cli` resolves to the 127 shim, while
the real binaries under `/opt/craft` are not on any service `PATH` `[V]`. Forge must therefore resolve
tools by **absolute path + version probe**, and the deployment must replace the shims (an ops task, not
a design assumption). No Craft command was executed by this task.

### 2.4 Existing pipeline / DB / MCP `[V]`

- `pod-postgres` public tables: `agent_sync_logs, fourthwall_products, ingested_assets, processing_jobs,
  users_saas_accounts` — **no episode, action, artifact, eval, lesson or skill tables**.
- `pod-mcp` on `0.0.0.0:8765`, three tools only (`list_pending_assets`, `trigger_pipeline_job`,
  `get_fourthwall_status`), JSON-RPC `2024-11-05` `[R: pod_pipeline/mcp_server.py:34,51-108]`.
- Repo deploy path `/opt/deerflow-forge` at commit `32fc71f` (2026-11-05 02:39 -0600); DeerFlow at
  commit `58fc5bd5` (2026-11-04) with `CHANGELOG.md` `[2.2.0] — 2026-10-29` `[V]`.
- `pod` DB is separate from the console's DB; both halves already run as independent systemd units `[R]`.

### 2.5 Repo facts used as constraints `[R]`

| Fact | Source |
|---|---|
| Orchestrator is a deterministic state machine; retries only transient exits, `max_attempts` 2; trace fallback only on exit 1; sha256 staging; publish idempotent via existing `fw_product_id` | `blueprint/files/pod_pipeline/orchestrator.py:30,58-94,133-165,173-200,225-285` |
| Exactly 3 MCP tools; boundary validation before DB access; detached `Popen` spawns (a deliberate anti-zombie fix) | `pod_pipeline/mcp_server.py:51-108,148-160,171-208` |
| 4 validators (PNG/alpha, knit BMP, PDF, MP4); decompression-bomb cap 400 MP | `pod_pipeline/validators.py` |
| Schema enforces states/budgets; one live run per (asset, product_type) | `sql/schema.sql:136-138` |
| Console is a pure viewer; systemd unit on `127.0.0.1:8091`, `ProtectSystem=full` | `deploy/vps/deerflow-forge-console.service`, `src/lib/blueprint/sources.ts` |
| `package.json` has **no** LLM/agent SDK | `package.json` dependencies |
| `craft-agent-operator` already defines a proposed ledger + evaluation protocol, explicitly marked **not deployed** | `blueprint/files/skills/craft-agent-operator/references/{memory-ledger,evaluation}.md` |
| Print gates exist as tools: `craft_trace` (10 gates, retype mapping, upscale boundary) and `prep_print_art` | `blueprint/files/tools/craft_trace.py`, `prep_print_art.py`; `[D: C3]` |

---

## 3. Architecture

```
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│  OPERATOR / OWNER                                                                            │
│  brief + rights + approval token        replies on Telegram/CLI/console                      │
└───────────────────────────────┬──────────────────────────────────────────────────────────────┘
                                │  HTTPS/stdio (loopback or SSH tunnel)
┌───────────────────────────────▼──────────────────────────────────────────────────────────────┐
│  FORGE CONDUCTOR  (new; systemd `forge-conductor`, 127.0.0.1:8092)                            │
│  intake → brief → plan DAG → dispatch handoffs → arbitrate verdicts → record → learn         │
│  Budgets: tokens / wall-clock / attempts / spend     Locks: 1 craft step, 1 writer per doc    │
└───┬───────────────┬───────────────┬───────────────┬───────────────┬───────────────┬───────────┘
    │               │               │               │               │               │
    ▼               ▼               ▼               ▼               ▼               ▼
┌────────┐   ┌────────────┐  ┌────────────┐  ┌─────────────┐  ┌────────────┐  ┌──────────────┐
│ ART    │   │ VECTOR     │  │ RASTER     │  │ PRINT       │  │ VISUAL     │  │ MEMORY       │
│ DIR.   │   │ OPERATOR   │  │ OPERATOR   │  │ VERIFIER    │  │ CRITIC     │  │ CURATOR      │
│ brief→ │   │ VC/Design  │  │ PC/Motion  │  │ gates+geom  │  │ blind,     │  │ lessons,     │
│ ArtSpec│   │ commands   │  │ commands   │  │ read-back   │  │ crop-cited │  │ skills, facts│
└───┬────┘   └─────┬──────┘  └─────┬──────┘  └──────┬──────┘  └─────┬──────┘  └──────┬───────┘
    │              │               │                │               │                │
    └──────────────┴───────────────┴───────┬────────┴───────────────┴────────────────┘
                                            │ typed handoffs (queue table `forge_handoff`)
┌───────────────────────────────────────────▼──────────────────────────────────────────────────┐
│  TOOL GATEWAY  (`forge_gateway`)                                                              │
│  registry · absolute-path + version probe · allowlist · roots · idempotency keys · refusals   │
│  native plane: Craft CLI/JSON/MCP   │   fallback plane: Playwright MCP (a11y snapshot)       │
└───────┬───────────────────────┬───────────────────────────────┬──────────────────────────────┘
        │                       │                               │
┌───────▼─────────┐   ┌─────────▼──────────┐   ┌───────────────▼──────────────────────────────┐
│ CRAFT APPS      │   │ EXISTING PIPELINE  │   │ POSTGRES 16  `pod` (untouched) + `forge` (new)│
│ /opt/craft      │   │ pod_pipeline       │   │ ledger · jobs · handoffs · skills · facts     │
│ VC 0.21.1 / PC  │   │ MCP @8765, worker  │   │ retrieval · eval · retrieval receipts         │
│ 0.20.2 (2 of 5) │   │ timer, validators  │   │ (same instance, separate DB + role)           │
└─────────────────┘   └────────────────────┘   └──────────────────────────────────────────────┘

VERIFICATION LADDER (each rung writes evidence; later rungs cannot overrule missing earlier ones)
 1 process   exit/argv/timeout/pid/env-hash        ── necessary, never sufficient
 2 artifact  exists, size>0, sha256, dims/DPI/alpha, openable, source unchanged
 3 domain    craft_trace 10 gates / prep_print_art / provider geometry, non-vacuous counters
 4 render    thumbnail + 1024 + 100% tiles on light/mid/dark, metrics as diagnostics only
 5 critic    BLIND vision critique, crop-cited per dimension, schema-grounded
 6 human     rubric (taste), publish approval, skill promotion sign-off
```

The conductor never calls a Craft binary directly; specialists never write to another specialist's
artifact; the verifier never authors art; the critic never sees gates; the curator is the only role
allowed to mutate memory.

---

## 4. Components, roles and handoffs

### 4.1 Role table

| Role | Owns | Must not | Model use | Handoff in → out |
|---|---|---|---|---|
| **Conductor** (supervisor) | episode lifecycle, plan DAG, budgets, locks, arbitration, refusals, final verdict assembly | execute tools; approve taste; mutate memory | `deepseek-flash`, thinking **on**, temp ≤0.2 | `TaskEnvelope` → `ArtSpec` plan + `Handoff` fan-out; `VerificationVerdict` → episode transition |
| **Art Director** | translating brief into an executable art spec; brand-fact citation; success criteria | touch CLI; approve its own spec; redefine the brief | thinking on, temp 0.4 | brief + brand facts + retrieved cases → `ArtSpec` |
| **Vector Operator** | vector commands (trace, paths, type outlines, export), vector document state | write outside `work/`, `build/`; run gates; publish | thinking off, temp 0.1, forced tool calls | `CommandBatch` → `ArtifactRecord[]` |
| **Raster Operator** | raster commands (crop, adjust, mask, upscale ≤2.5×, export), frame extraction | trace AI text; upscale past 2.5×; touch masters | thinking off, temp 0.1 | `CommandBatch` → `ArtifactRecord[]` |
| **Print Verifier** | gate execution, geometry/DPI/white/alpha/colour checks, source-mutation check, read-back from system of record | author or edit art; see the operator's success claim | deterministic tool calls only; model only to summarise | `ArtifactRecord[]` → `GateReport` |
| **Visual Critic** | blind visual assessment against brief, per-dimension crop evidence, confidence + unseen list | see exit codes/gates/operator claims; score taste for promotion alone | vision on, temp 0.2, schema-constrained | rendered images + brief → `CritiqueReport` |
| **Memory Curator** | lessons, skill versions, brand facts, promotion/rollback, contradiction records | promote without evidence; edit in place; delete evidence | thinking on, temp 0.1 | episode evidence → `LessonCandidate`/`SkillDraft` |

**Separation of duties (enforced by the gateway, not by prompt):** the agent token of the operator
cannot call `verify.*`; the verifier token cannot call `craft.*`; the critic token can only call
`render.*` and `vision.*`; only the curator token can write `memory.*`. This is an allowlist per role.

**Planned 7th role:** `Motion Operator` for FilmCraft — **deferred** because no FilmCraft binary is
installed `[V]`. Do not claim FilmCraft capability before §2.3 changes and a catalogue snapshot exists.

### 4.2 Context budget per role (why handoffs are typed)

Config allows 1,048,576 input tokens but only 8,192 output `[V]`. The design does not use the long
context as a dumping ground; it uses it for *bounded* retrieval and image references:

| Role | Injected context | Hard cap |
|---|---|---|
| Conductor | brief, brand facts, retrieved case *summaries*, last 5 episode events | 6,000 tokens |
| Art Director | brief + brand facts + ≤5 retrieved cases + reference crops | 8,000 tokens |
| Operators | `ArtSpec` slice + command schema for ≤40 commands + document state | 6,000 tokens |
| Verifier | gate definitions + artifact metadata (never images) | 3,000 tokens |
| Critic | brief rubric lines + 3–6 rendered images (downscaled) + reference (if any) | 10,000 tokens |
| Curator | episode digest + candidate + contradiction candidates | 6,000 tokens |

All images are passed as **files with sha256**, not base64 in prompts; every prompt records
`prompt_version`, `model_id`, `input_hashes[]`.

### 4.3 Handoff protocol

Handoffs are rows, not messages. A handoff is `created` by the conductor, `claimed` by exactly one
specialist (lease, heartbeat), and `completed` with a typed payload or `failed` with a refusal code.
The supervisor may retry a handoff at most twice (matching the pipeline's `max_attempts` discipline)
and only for transient failures; a policy refusal is terminal.

```jsonc
// Handoff envelope (all handoffs)
{
  "handoff_id": "uuid",
  "episode_id": "uuid",
  "parent_handoff_id": "uuid|null",
  "kind": "artspec|command_batch|gate_report|critique|critique_verdict|lesson_candidate|skill_draft",
  "produced_by": "art_director",
  "consumed_by": "vector_operator",
  "schema_version": "1.0",
  "deadline_s": 900,
  "budget": {"tokens": 4000, "wall_s": 600},
  "input_hashes": ["sha256:…"],
  "payload": { },
  "refusal": null
}
```

### 4.4 Arbitration rules (conductor)

1. Gate pass + critic pass + human pass → `accepted`.
2. Gate pass + critic reject → `needs_human` (never silently override the critic).
3. Gate fail + critic pass → `rejected` (a beautiful artifact with a broken technical gate is not shippable).
4. Missing gate report → `unverified`, never `pass`.
5. Critic unavailable/unparseable → retry once, then `needs_human` with `E_VISION_UNAVAILABLE`.
6. Two specialists disagree on the same artifact → `conflict` record, human decides.
7. Any budget/lock/root violation → terminal refusal with a named code.

---

## 5. Data contracts

### 5.1 Canonical JSON shapes (`forge/contracts/*.json`, versioned)

**TaskEnvelope** (operator → conductor)

```jsonc
{
  "schema_version": "1.0",
  "episode_id": "uuid",
  "account_id": 1,
  "brief": {"text": "…", "deliverable": "dtg_front_print_master", "quantity": 1,
            "deadline_utc": "2026-11-08T00:00:00Z"},
  "task_family": "ai_badge_trace_v1",
  "target": {"app": "vectorcraft", "app_version": "0.21.1",
             "catalogue_hash": "sha256:…", "product_type": "apparel"},
  "inputs": [{"path": "inbox/badge.png", "sha256": "…", "rights_id": "rights_0007"}],
  "constraints": {"print_width_in": 8.0, "dpi": 300, "max_upscale": 2.5,
                  "background": "transparent", "provider": "fourthwall", "template_id": "…"},
  "budget": {"max_attempts": 3, "max_tokens": 80000, "max_wall_s": 5400, "max_cents": 0},
  "approval": {"publish_allowed": false, "approval_token": null},
  "mode": "assisted|replay|draft",
  "requested_by": "owner"
}
```

**ArtSpec** (art director → operators/verifier/critic)

```jsonc
{
  "schema_version": "1.0",
  "episode_id": "uuid",
  "deliverable": "dtg_front_print_master",
  "canvas": {"width_px": 2400, "height_px": 3000, "dpi": 300, "color_space": "sRGB"},
  "composition": {"subject_bbox_target": [0.5, 0.5, 0.62], "safe_margin_in": 0.5,
                  "hierarchy": ["wordmark", "tagline", "ornament"],
                  "background": "transparent"},
  "palette": [{"hex": "#1B2A41", "role": "primary", "brand_fact_id": "bf_012"}],
  "typography": [{"role": "wordmark", "family": "FONT-ABC", "licensed": true,
                  "treatment": "retype_outlined"}],
  "constraints": {"no_white_residual": true, "no_traced_text": true,
                  "min_edge_hardness": 0.9, "provider_safe_zone": [0.04, 0.04]},
  "success_criteria": [
    {"id": "gates_10_10", "type": "domain_gate", "runner": "craft_trace", "required": {"ok": true}},
    {"id": "brief_fit", "type": "rubric", "min": 4, "reviewers": "human"}
  ],
  "brand_fact_ids": ["bf_012", "bf_031"],
  "source_case_ids": ["ep_0193"],
  "open_questions": ["is the tagline copy approved?"],
  "commitments": {"vectors_only_for_marks": true}
}
```

**CommandBatch / CommandResult**

```jsonc
// request
{"handoff_id": "uuid", "commands": [
  {"cmd_id": "imageTrace.make", "app": "vectorcraft",
   "params": {"preset": "logo_limited_palette", "palette_limit": 6},
   "idempotency_key": "sha256:…", "expects": {"artifact": "svg"}}
], "workdir": "work/<episode>/", "stop_on_error": true}

// result
{"exit_code": 0, "duration_ms": 41332, "argv_executed": ["/opt/craft/.../vectorcraft-cli", "…"],
 "stdout_digest": "sha256:…", "stderr_digest": "sha256:…", "log_path": "logs/…",
 "artifacts": [{"path": "build/<episode>/traced.svg", "sha256": "…", "bytes": 90211,
                "width_px": null, "height_px": null, "format": "svg"}],
 "envelope_version": "2024-11-05", "error": null}
```

**GateReport** (print verifier; fields mirror `craft_trace`'s report shape `[R: tools/craft_trace.py]`)

```jsonc
{"episode_id": "uuid", "artifact_sha256": "…", "runner": "craft_trace", "runner_version": "1.0.0",
 "ok": true, "checks": {"white_residual": {"value": 0, "pass": true},
                        "specks": {"value": 3, "pass": true},
                        "coverage": {"value": 0.41, "pass": true},
                        "dpi": {"value": 300, "pass": true},
                        "canvas": {"value": [2400,3000], "pass": true},
                        "fill_colours": {"value": 7, "pass": true},
                        "edge_definition": {"value": 0.93, "pass": true},
                        "hard_alpha": {"value": true, "pass": true},
                        "transparent_corners": {"value": true, "pass": true},
                        "retyped_text": {"value": true, "pass": true}},
 "non_vacuous": {"retype_boxes": 2, "text_present": true},
 "source_mutation": {"input_sha256_before": "…", "after": "…", "mutated": false},
 "generated_at": "2026-11-05T16:20:00Z", "refusal": null}
```

**CritiqueReport** (visual critic — schema-enforced)

```jsonc
{"episode_id": "uuid", "artifact_sha256": "…", "critic_prompt_version": "critic-v0.3",
 "model_id": "deepseek-flash", "blinded_to": ["exit_code", "gate_report", "operator_claims"],
 "dimensions": {
   "brief_fit": {"score": 4, "evidence": [{"region": [0,0,1,1], "crop_path": "build/…/thumb.png",
                  "observation": "subject centred, wordmark legible at 256 px"}]},
   "hierarchy": {"score": 4, "evidence": [{"region": [0.08,0.10,0.92,0.38], "crop_path": "…"}]},
   "typography": {"score": 3, "evidence": [{"region": [0.30,0.55,0.70,0.62], "crop_path": "…",
                  "observation": "tagline letter-spacing tight at print scale"}]},
   "colour": {"score": 5, "evidence": [{"region": [0,0,1,1], "crop_path": "…"}]},
   "print_safety": {"score": 4, "evidence": [{"region": [0.0,0.0,0.06,0.06], "crop_path": "…"}]}
 },
 "defects": [{"severity": "minor", "where": "tagline", "issue": "tracking",
              "fix_hint": "increase tracking by 2%"}],
 "confidence": 0.72,
 "unseen": ["no reference artwork supplied", "reverse side not evaluated"],
 "verdict": "pass|pass_with_notes|reject|unverifiable"}
```

Validation rejects (a) any dimension without ≥1 `evidence` entry, (b) `observation` shorter than 12
characters, (c) `verdict: pass` when `defects[].severity == "major"`, (d) any mention of a gate value.
Rejection emits `E_CRITIQUE_UNGROUNDED` and the critic must retry once.

**Skill** (procedural memory; executable, versioned)

```jsonc
{"skill_id": "sk_vc_trace_retpye_v3", "name": "vc_ai_badge_trace", "version": 3,
 "app": {"name": "vectorcraft", "version": "0.21.1", "catalogue_hash": "sha256:…"},
 "task_family": "ai_badge_trace_v1",
 "preconditions": {"input": {"background": "white", "min_subject_px": 600},
                   "document": "new", "rights_required": true},
 "steps": [{"seq": 1, "cmd_id": "imageTrace.make",
            "params": {"palette_limit": {"range": [4, 8], "default": 6},
                       "mode": {"const": "colors"}}},
           {"seq": 2, "cmd_id": "imageTrace.expand", "params": {}},
           {"seq": 3, "tool": "document.export", "params": {"format": "svg"}}],
 "gates": [{"runner": "craft_trace", "required": {"ok": true, "retype_boxes": ">0 when text_present"}}],
 "recovery": [{"on": "E_GATE_FAILED:white_residual", "do": "step:prep_print_art --mode white"}],
 "stats": {"success": 0, "failure": 0, "attempts": 0},
 "status": "draft|candidate|active|superseded|rolled_back",
 "evidence_episode_ids": [], "promoted_at": null, "superseded_by": null}
```

### 5.2 Ledger tables (new DB `forge`; `pod` untouched)

All writes go through repository functions with explicit transactions; no ORM magic. Every episode
row carries `schema_version` and `prev_event_hash` chaining.

| Table | Key columns | Purpose |
|---|---|---|
| `forge_episode` | `id uuid pk, account_id, brief, task_family, apps jsonb, rights jsonb, plan jsonb, status, mode, budget jsonb, cost jsonb, skill_pin jsonb, catalogue_hash, started_at, finished_at` | one run, one row |
| `forge_event` | `id bigserial, episode_id, seq, kind, payload jsonb, prev_hash char(64), hash char(64), created_at` (unique `episode_id,seq`) | append-only hash-chained event log |
| `forge_handoff` | `id uuid pk, episode_id, parent_id, kind, produced_by, consumed_by, payload jsonb, refusal_code, state, lease_until, attempts, created_at` | typed handoffs |
| `forge_tool_call` | `id bigserial, episode_id, handoff_id, tool, cmd_id, params jsonb, idempotency_key char(64), result jsonb, exit_code, duration_ms, argv text[], refused bool` (unique `idempotency_key`) | tool audit + replay |
| `forge_artifact` | `id bigserial, episode_id, handoff_id, kind, path, sha256, bytes, width, height, dpi, format, gate_report jsonb, created_at` | artifact index (content-addressed store on disk) |
| `forge_gate` | `id bigserial, episode_id, artifact_sha256, runner, runner_version, ok, checks jsonb, non_vacuous jsonb, source_mutation jsonb` | gate evidence, separated from artifact |
| `forge_critique` | `id bigserial, episode_id, artifact_sha256, prompt_version, model_id, blinded_to jsonb, dimensions jsonb, defects jsonb, confidence, unseen jsonb, verdict` | critic evidence |
| `forge_eval` | `id bigserial, episode_id, arm text ('baseline'|'memory'), technical jsonb, human jsonb, verdict, reviewer, created_at` | evaluation record |
| `forge_resolution` | `id bigserial, episode_id, candidate_sha256, resolution text ('pass'|'fail'|'needs_human'|'unverified'), reason_codes text[]` | arbitration outcome |
| `forge_job` | `id bigserial, kind, payload jsonb, priority, state, lease_until, attempts, max_attempts, run_after, created_at` | Postgres queue (`FOR UPDATE SKIP LOCKED`) |
| `forge_episode_case` | `episode_id, task_family, brand, product_type, summary tsvector, embedding real[] null, outcome, accepted bool` | retrieval index + receipts |
| `forge_retrieval` | `id bigserial, episode_id, query_hash, returned_ids uuid[], scores real[], injected_tokens int` | retrieval receipt for A/B |
| `forge_brand_fact` | `id text pk ('bf_012'), scope, key, value jsonb, provenance text, confidence, valid_from, valid_to, superseded_by, status` | semantic memory |
| `forge_skill` | `skill_id text, version int, app, catalogue_hash, preconditions jsonb, steps jsonb, gates jsonb, recovery jsonb, stats jsonb, status, promoted_at, superseded_by` (unique `skill_id,version`) | procedural memory |
| `forge_lesson` | `id uuid, scope, task_family, content, evidence uuid[], success_count, failure_count, confidence, version, status, superseded_by, created_at` | candidate rules |
| `forge_conflict` | `id bigserial, kind, a_ref, b_ref, detail jsonb, resolved_by, resolution` | contradictions (never averaged away) |
| `forge_budget_ledger` | `day date, account_id, tokens_in, tokens_out, calls, cents, hard_cap_cents` | cost caps |
| `forge_role_token` | `role, token_hash, allowlist jsonb, active bool` | role-scoped tool permissions (§4.1) |

Indexes: `forge_episode(task_family,status,started_at desc)`, `forge_handoff(state,lease_until)`,
`forge_job(state,priority,run_after)`, `forge_artifact(sha256)`, `forge_skill(app,status)`,
`forge_brand_fact(key,scope,status)`. pgvector is **not** assumed: `postgres:16` (stock) may not ship
it, so vectors are `real[]` + in-process cosine until an image swap is approved `[U]`.

---

## 6. Tool layer

### 6.1 Two planes, one gateway

| Plane | Transport | When allowed | Verification requirement |
|---|---|---|---|
| **Native** (default) | Craft CLI under `/opt/craft/<app>/<version>/bin/`, app JSON control channel, app MCP server | always preferred; the only plane that may produce a shippable artifact | artifact ladder rungs 2–5 |
| **Fallback** (declared) | Playwright MCP, accessibility snapshot first, screenshot only as evidence | only when a `forge_tool_gap` row proves no native command exists, or for web-only surfaces (Fourthwall admin) | **must** read back from the system of record (file hash / DB row / REST GET); a GUI "saved" toast is never verification |

A fallback action that cannot be read back is refused with `E_SURFACE_UNVERIFIABLE`. GUI actions are
recorded with the a11y snapshot hash and, if used, screenshot hash — but a screenshot alone yields
`unverified` (see §7.2).

### 6.2 Tool registry entry (the only way a tool becomes callable)

```jsonc
{"tool_id": "craft.run", "app": "vectorcraft",
 "bin": "/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli",
 "version_probe": ["--version"], "version_regex": "^vectorcraft-cli (\\d+\\.\\d+\\.\\d+)$",
 "surface": "cli|json|mcp", "writes": true, "destructive": false,
 "roots": {"read": ["inbox:ro", "work/<episode>:rw", "build/<episode>:rw"],
           "write": ["work/<episode>", "build/<episode>"]},
 "allow_roles": ["vector_operator"],
 "param_schema_ref": "forge/contracts/commands/vectorcraft/<cmd_id>.json",
 "timeout_s": 900, "idempotency": "required", "requires_document": true,
 "outputs": [{"kind": "svg", "validate": ["magic_xml", "nonzero", "sha256"]}],
 "refusal_codes": ["E_COMMAND_UNKNOWN", "E_PARAM_REJECTED", "E_ROOT_DENIED", "E_APP_DRIFT"]}
```

**Resolution is by absolute path and version probe, never by bare name** — the host currently proves
why: `/opt/pod-pipeline/bin/*-cli` are 127-shims on `PATH`, while the real clients live under
`/opt/craft` and are not on any service `PATH` `[V]`. At startup the gateway probes every declared
binary, records `(path, version, sha256)`, and pins them into the episode. Any mismatch between the
episode pin and the probe is `E_APP_DRIFT` (terminal; a human must repin).

### 6.3 Allowlist

- **Per role** (§4.1): operators get `craft.*`, `render.*`, `inspect.*`; verifier gets `verify.*`,
  `readback.*`; critic gets `render.*`, `vision.*`; curator gets `memory.*`; conductor gets none.
- **Per command**: the allowlist is a set of exact `cmd_id`s drawn from the pinned catalogue
  (918 VectorCraft / 965 PhotoCraft `[D: C1,C2]`, snapshot `/opt/craft/catalogues/*.json` `[V]`), not a
  prefix wildcard. `imageTrace.*` as a wildcard is forbidden; `imageTrace.make` and `imageTrace.expand`
  are listed individually.
- **Denylist always wins**: file/overwrite/delete/publish commands are not in any operator allowlist.
  Publishing is a distinct tool (`publish.request`) requiring an approval token and a named human.
- Unknown command → `E_COMMAND_UNKNOWN` with up to 5 nearest catalogue matches and *no execution*.
  Guessing a command ID from a menu label is a defect, not a capability `[D: Q72]`.

### 6.4 Roots and path policy

Canonical layout on the host (new, under `/var/lib/forge` — not inside the repo):

```
/var/lib/forge/
  inbox/<account>/            read-only sources (sha256 recorded at intake; never written)
  work/<episode_id>/          scratch; deleted on success, kept on failure
  build/<episode_id>/         outputs; immutable after episode closes
  artifacts/<sha256>          content-addressed store (hardlink/copy from build)
  memory/                     exports for backup (not authoritative)
  logs/<episode_id>/
```

Rules: all paths are resolved with `realpath` before the root check (symlink escape → `E_ROOT_DENIED`);
a path outside the declared roots is refused, never clamped; the source file's hash is re-checked
immediately before and after the batch (`E_SOURCE_MUTATED`); writes must create new files, not modify
in place; a tool that cannot avoid in-place mutation is refused `E_INPLACE_WRITE`.

### 6.5 Idempotency

`idempotency_key = sha256(episode_id ‖ tool_id ‖ canonical_json(params) ‖ input_hashes)`.
Unique index on `forge_tool_call.idempotency_key`; a replayed call returns the stored result and sets
`replayed: true`. Side effects beyond file creation — publish, upload, state change — require a
second, human-issued key. The existing pipeline already follows this discipline for publishing
(`upsert_product` / existing `fw_product_id` short-circuit `[R: orchestrator.py:228-232]`); Forge
inherits the rule, not the code.

### 6.6 Refusal codes

| Code | Trigger | Resolver |
|---|---|---|
| `E_BRIEF_MISSING` | no deliverable, no target, or contradictory constraints | conductor asks owner; no placeholder |
| `E_RIGHTS_MISSING` | input/asset lacks a recorded rights id | owner supplies rights record |
| `E_ROOT_DENIED` | resolved path outside roots / symlink escape | developer/ops fix, not retry |
| `E_INPLACE_WRITE` | tool would overwrite a source or master | re-run on a copy |
| `E_COMMAND_UNKNOWN` | cmd_id not in pinned allowlist | atlas lookup + human review |
| `E_PARAM_REJECTED` | schema/range/type violation | operator re-derives params from schema |
| `E_APP_DRIFT` | version/catalogue/bin hash ≠ episode pin | repin + rerun goldens |
| `E_CATALOGUE_STALE` | catalogue hash older than app version | refresh catalogue |
| `E_DOCUMENT_STATE` | wrong/absent open document, wrong selection | operator resets state; never "try anyway" |
| `E_ARTIFACT_MISSING` | expected output absent | retry once, then fail |
| `E_ARTIFACT_EMPTY` | zero bytes / unopenable | retry once, then fail |
| `E_SOURCE_MUTATED` | input hash changed | quarantine episode; never reuse artifacts |
| `E_GATE_FAILED` | any required gate false | route to recovery step or escalate |
| `E_GATE_MISSING` | no gate report for a printed artifact | `unverified`; cannot ship |
| `E_GATE_VACUOUS` | pass with vacuous counters (`retype_boxes:0` while text present, `coverage` at threshold exactly) | verifier re-runs with reference masks |
| `E_UPSCALE_LIMIT` | >2.5× subject-relative upscale `[D: Q79]` | regenerate at higher native res |
| `E_TEXT_TRACE_FORBIDDEN` | text present but trace has no retype step `[D: Q77]` | erase + retype; never trace AI text |
| `E_WHITE_MODE_REFUSED` | `--mode white` on an image with no white background `[D: Q78]` | choose `none`/`alpha` deliberately |
| `E_VISION_UNAVAILABLE` | vision call failed/unparseable after retry | `needs_human` |
| `E_CRITIQUE_UNGROUNDED` | critique missing crop evidence / cites gate values | critic retry once |
| `E_BUDGET_EXCEEDED` | token/wall/spend cap hit | hard stop before next model call |
| `E_TIMEOUT` | step/handoff exceeded deadline | retry once if transient, else fail |
| `E_PUBLISH_NOT_APPROVED` | publish without approval token | request approval |
| `E_SURFACE_UNVERIFIABLE` | GUI path has no read-back | refuse; find a native path |
| `E_MEMORY_CONFLICT` | contradictory active facts/lessons | curator opens conflict; no silent overwrite |
| `E_EVAL_EMPTY` | golden set missing/fixtures absent | evaluation refuses; no fabricated score |
| `E_UNSUPPORTED_SURFACE` | app not installed/verified (e.g. FilmCraft today) | refuse; do not simulate |

Refusals are structured: `{code, message, how_to_fix, evidence_refs, terminal: bool}`. `terminal` refusals
must not be retried by any agent. This mirrors the existing tools' named-refusal behaviour
(`CraftTraceError(code, message, how_to_fix)` `[R: tools/craft_trace.py]`).

### 6.7 Concurrency and locks

- One global **craft-step semaphore** (default 1 on this 2-vCPU host) shared by Forge and the existing
  `pod-worker` path, implemented as a Postgres advisory lock keyed `craft:global`. Rationale: load
  average already 1.37 without any Forge work `[V]`.
- Per-document advisory lock `doc:<app>:<realpath>`; a second writer queues with `E_DOCUMENT_STATE`.
- ≤2 concurrent episodes; ≤3 concurrent model-calling subagents (mirrors the verified DeerFlow
  `subagent_runtime.max_running: 3` `[V]`), with queueing rather than rejection.
- Model calls are not pipelined per episode: one call at a time per specialist, so cost is attributable.

---

## 7. Perception and verification

### 7.1 The evidence ladder (no single rung may certify an artifact)

| Rung | Evidence | Produced by | Failure code if absent |
|---|---|---|---|
| 1 process | exit code, timeout flag, argv executed, duration, pid, stdout/stderr digests | gateway | `E_ARTIFACT_MISSING` (no artifact) / `E_TIMEOUT` |
| 2 artifact | exists, `bytes>0`, sha256, magic bytes, openable, dimensions, DPI, colour space, alpha bbox, page count | verifier (PIL/ffprobe) | `E_ARTIFACT_EMPTY` |
| 3 domain | `craft_trace` 10 gates, `prep_print_art` coverage/subject/upscale, provider geometry, retype non-vacuity | print verifier | `E_GATE_FAILED` / `E_GATE_MISSING` / `E_GATE_VACUOUS` |
| 4 rendered perception | render ladder + deterministic diagnostics | verifier (no model) | `E_ARTIFACT_MISSING` |
| 5 visual critic | blind rubric with crop evidence | visual critic | `E_VISION_UNAVAILABLE` / `E_CRITIQUE_UNGROUNDED` |
| 6 human rubric | anchored 1–5 scores, two reviewers for promotion/publish | owner/designer | `needs_human` |

Verdict assembly (conductor): `pass` requires rungs 1–5 green and, for print/publish or promotion,
rung 6. Any missing rung → `unverified`. Any disagreement between rung 3 and 5 → `needs_human`.

### 7.2 Why exit codes and screenshots are not trusted

- **Exit 0 is a claim about a process, not an effect.** The existing orchestrator already validates
  outputs after exit 0 (`_collect_and_validate` checks existence, size>0 and per-step validators
  `[R: orchestrator.py:203-221]`); Forge extends that with hashes, dimensions and gates.
- **Screenshots are stale by construction.** A preview can render from a cached document while the
  export is broken; the dossier records exactly this class of false success in computer-use systems
  `[D: Q52, B4]`. Therefore: a screenshot never upgrades a verdict; it can only *downgrade* one.
- **Vacuity is a real pass mode.** A gate report with `ok:true` but `retype_boxes:0` on an image that
  contains text is a pass that verified nothing `[D: Q77]`. The verifier asserts non-vacuous counters
  from an independent text-presence probe (OCR or the brief's own text) before accepting the report.
- **Source immutability is checked, not assumed.** Hash the input before and after every batch; a
  changed master is `E_SOURCE_MUTATED` and the episode is quarantined.
- **The export is re-rendered independently.** For vector work, render the SVG at print pixels with a
  second renderer and compare a perceptual hash with the delivered raster; a mismatch means the
  preview and the export disagree → `needs_human`.
- **The critic is blind.** It receives the brief, rubric lines, rendered images and (optionally) a
  reference — never the exit code, gate report, operator's claim, or prior critic verdict.

### 7.3 Render ladder (deterministic, cheap, no model)

| Render | Spec | Catches |
|---|---|---|
| `thumb_256` | longest side 256 px, on `#FFFFFF`, `#808080`, `#000000` | white fringes, halo, transparency misuse |
| `view_1024` | longest side 1024 px, sRGB | hierarchy, centring, legibility |
| `crop_100` | 4×4 tiles at 100 % of print pixels | edge definition, specks, aliasing |
| `print_sheet` | 1:1 print-size composite on the provider template | placement vs safe zone, scale |
| `contrast_sim` | deuteranopia/protanopia simulation | colour-only differentiation |
| `alpha_matte` | alpha over magenta/green | hard-alpha violations, semi-transparent junk |

Diagnostics computed and stored (not verdicts): alpha coverage, bbox and centring offsets, unique
colour count, connected components, edge-hardness ratio, white-pixel residual fraction, empty-margin
fraction, and SSIM against a golden reference when one exists. Metrics that drift beyond a golden's
tolerance are flagged for review but cannot alone fail an artifact.

### 7.4 Visual critic protocol

1. Prompt template is versioned (`critic-v0.3`), stored in the repo, and golden-tested against a small
   defect corpus (white fringe, ghost text, misplaced label, off-brand palette, clipped glyph).
2. Output is schema-constrained (§5.1). The schema rejects ungrounded dimensions, gate-value mentions,
   or `pass` with major defects.
3. The critic must fill `unseen` (what it could not evaluate) — a non-empty `unseen` list downgrades
   `pass` to `pass_with_notes`, never blocks.
4. Confidence < 0.5 → `needs_human` regardless of score.
5. Critic calls are logged with model id, prompt hash, image hashes, token counts and raw response.
   A critic result is reproducible: same prompt version + same image hashes should not flip verdicts;
   flips are recorded as `forge_conflict` and measured as critic instability.
6. Critic cannot be the same agent instance as the Art Director; role allowlists enforce it.

### 7.5 Human rubric

Anchored 1–5 dimensions (brief fit, hierarchy, typography, colour, print safety), with the anchors from
`evaluation.md` `[R]`, two reviewers where the skill/publish is promoted, blind arm assignment, and
inter-rater disagreement reported rather than averaged away. Human review is required for: every
publish, every skill promotion, every new task family's first 3 episodes, and a ≥10 % sample of
accepted artifacts thereafter.

---

## 8. Durable memory and what "learning" means here

### 8.1 Four stores, four jobs

| Store | Question it answers | Table(s) | Writable by |
|---|---|---|---|
| **Episode ledger** | what exactly happened, with evidence? | `forge_episode`, `forge_event`, `forge_tool_call`, `forge_artifact`, `forge_gate`, `forge_critique`, `forge_resolution` | system only (append-only) |
| **Case retrieval** | what similar work has succeeded/failed? | `forge_episode_case`, `forge_retrieval` | curator + system |
| **Semantic brand facts** | what is true about this brand/product now? | `forge_brand_fact` | curator only |
| **Procedural skills** | how do we execute this task family reliably? | `forge_skill`, `forge_lesson` | curator only, via promotion |

The ledger is hash-chained (`forge_event.prev_hash`). It is the source of truth; any derived view
(case summary, skill stats) is rebuildable from it.

### 8.2 Case retrieval (Phase 2)

Pipeline: hard metadata filter (`task_family`, `app`, `app_version`, `product_type`, `brand`, outcome)
→ lexical rank (BM25 over brief + critique defect terms; Postgres `tsvector`) → optional vector rank
over normalised descriptions (`real[]` + in-process cosine until pgvector is approved) → rerank by
(a) accepted outcome, (b) gate pass rate, (c) recency, (d) same failure code affinity → inject ≤1,200
tokens: case IDs, one-line summaries, parameters that mattered, failure codes, and a `why_retrieved`
line per case.

Every retrieval writes a `forge_retrieval` receipt: `query_hash`, `returned_ids`, scores, injected
tokens. A/B can therefore prove the memory arm really had memory. With no matching case, the run takes
the baseline arm and records `retrieval: empty` — it must not invent precedent.

### 8.3 Semantic facts

Typed keys, e.g. `brand.palette.primary`, `print.max_width_in`, `type.licensed_fonts`,
`provider.template_id`, `channel.safe_zone`, `owner.preference.background`. Each row:
`value jsonb, provenance (source path/URL/human), confidence, valid_from, valid_to, superseded_by,
status`. Facts are *read* by the Art Director (must cite `brand_fact_id`s in the ArtSpec); facts are
*written* only by the curator, with provenance. Contradiction opens `forge_conflict`; it never
overwrites. Expiry by `valid_to` or by app/version change.

### 8.4 Procedural skills

A skill is an executable program (steps = exact `cmd_id`s + bounded parameter ranges), with
preconditions, expected artifacts, gates, recovery branches, and trial statistics. Two execution modes:

- **replay**: run the stored steps with default parameters, no model except the critic/verifier; used
  once a skill is `active` and the brief matches preconditions.
- **adapt**: the operator may adjust parameters *within the declared ranges only*; out-of-range is
  `E_SKILL_PRECONDITION`.

Skills are selected by retrieval + precondition match, not regenerated from scratch each time. Pinned
into the episode (`skill_pin = {skill_id, version, catalogue_hash, app_version}`) so a later run is
reproducible after the skill changes.

### 8.5 Promotion and rollback

```
draft ──(1 verified episode + explicit scope/conditions)──► candidate
candidate ──(≥3 independent successes + golden regression pass + human sign-off)──► active
active ──(new version promoted)──► superseded   (old kept, replayable)
active ──(failure/regression/contradiction)──► rolled_back  (pointer flip + goldens re-run)
```

- "Independent" = different inputs/episodes, not three attempts on one file.
- A lesson/skill that improves one task and regresses another is rejected (dossier's A/B rule `[R]`).
- No in-place edits: every change is a new version; rollback flips the active pointer and re-runs the
  golden suite. A kill switch (`FORGE_SKILLS_ENABLED=0`) forces the baseline arm.
- Every promotion records evidence episode IDs; evidence rows are never deleted (supersede only).

### 8.6 What this is *not*: retrieval/skills vs fine-tuning vs RL

| Mechanism | What changes | Evidence needed | Status here |
|---|---|---|---|
| Retrieval | prompt context | retrieval receipts + A/B | Phase 2 |
| Skill library | selected/parameterised procedure | ≥3 verified episodes + goldens | Phase 2 |
| Semantic facts | typed, sourced values | provenance + human sign-off | Phase 1 (read-only facts first) |
| Fine-tuning weights | model parameters | large rights-cleared corpus + frozen eval + cost | **Not planned (Phase 3 optional)** |
| RL on gates | policy | verifiable reward + anti-hacking review | **Not planned**; gates measure correctness, not taste `[D: Q108]` |

"Learns" is only claimed when a held-out-task gain persists across briefs and survives rollback tests.
Until then the honest phrasing is "retrieves past cases and reuses vetted procedures".

---

## 9. Evaluation

### 9.1 Golden set

50 tasks = 5 task families × 10, frozen per app/version, each with fixtures, rights records, reference
procedure, required gates and accepted-artifact hash. Split **public dev (36)** / **private held-out
(14)**; the agent may retrieve from dev cases only, never from held-out. Held-out fixtures are stored
outside the retrieval index and are only used by the eval runner.

| Family | App | Required evidence | Human rubric? |
|---|---|---|---|
| `ai_badge_trace_v1` | VectorCraft | `craft_trace` 10 gates + retype non-vacuity | yes |
| `logo_flat_trace_v1` | VectorCraft | 10 gates + render/re-export hash match | yes |
| `photo_retouch_export_v1` | PhotoCraft | dims/DPI/colour space + mask edge audit | yes |
| `print_master_dtg_v1` | VectorCraft/PhotoCraft | 300 DPI, transparent white, provider geometry, safe zone | yes |
| `type_outline_retype_v1` | VectorCraft | font status + bounds + retype gate | yes |

Each golden record is the `evaluation.md` shape `[R]`, extended with `arm`, `runs`, `variance_policy`,
`rights`, `catalogue_hash`, `private: bool`.

### 9.2 Metrics

| Metric | Definition | Target direction |
|---|---|---|
| **Primary**: first-attempt verified-pass rate | accepted on attempt 1 / attempted goldens (pass = rungs 1–5, and 6 where required) | ↑ |
| Attempts per accepted artifact | tool batches until accepted | ↓ |
| Human rework minutes | reviewer time per accepted artifact | ↓ |
| Cost per accepted artifact | model tokens (in/out) × verified price + wall seconds (CPU value) | ↓, no invented $ |
| **Precision of "pass"** | human-accepted / runs the system marked pass | ↑ (this is the honesty metric) |
| Unsafe side effects | source mutations, unapproved publishes | **= 0** |
| Regression rate | previously passing goldens now failing | **= 0** |
| Refusal correctness | refusals matching the expected refusal for a negative fixture | ↑ |
| Retrieval lift | pass rate (arm B − arm A) with CI | > 0 and CI excludes 0 |
| Critic stability | verdict flips on identical inputs across prompt version | ↓ |

### 9.3 A/B protocol

Same model id, same app versions, same catalogue hash, same fixtures. Arm A = no retrieval/lessons
(baseline); Arm B = retrieval + active skills only. ≥3 runs per golden, randomised order, identical
budgets. Human reviewers blind to arm. Report per-task results, aggregate with Wilson 95 % CI, median
attempts, cost, human scores, and every failure code. A single demo is an anecdote.

### 9.4 Anti-reward-hacking

- **Held-out private set** the agent cannot retrieve; reported separately. A gain only on public
  goldens is memorisation.
- **Gate authorship separation**: the verifier emits gates, never the operator; a gate report from an
  operator's process is discarded (`E_GATE_MISSING`).
- **Vacuity checks** on pass counters (§7.2); reject threshold-hugging (e.g. coverage within ±1 % of
  the pass threshold on >20 % of runs) as a review flag.
- **Brief-drift check**: the conductor diffs the ArtSpec's deliverable/constraints against the original
  brief; narrowing the brief to something passable is `needs_human` and recorded.
- **Shortcut detection**: suspiciously short episodes (fewer tool calls than the skill's minimum) are
  reviewed; so are inputs that differ from the golden hash without an `input_override` record.
- **Rubric-anchor audit**: periodic re-scoring of a fixed sample by the design owner to detect rater
  drift; disagreement is reported, not smoothed.
- **Cost anomaly**: a run far below the expected token floor for its family is flagged — it may have
  skipped the critic.

### 9.5 Regression gates

Run on every change to skills, prompts, critic version, model id, app version or catalogue hash:

1. all public goldens execute (no crash), 2. verified-pass rate ≥ baseline − 2 pp, 3. zero unsafe side
effects, 4. zero `E_SOURCE_MUTATED`, 5. cost per accepted artifact within +20 % of baseline,
6. critic schema-validation rate = 100 %, 7. private-set results recorded (no threshold applied to a
14-item set; it is a sentinel, not a scoreboard). Any failure blocks promotion and, if already active,
triggers rollback.

Missing fixtures → `E_EVAL_EMPTY`; missing gate → `unverified`; changed app/model version invalidates
the baseline (new label, never a silent comparison).

---

## 10. Hosting and operations

### 10.1 Topology (proposed; nothing installed)

```
                     ssh tunnel / loopback only                     
 operator ──► 127.0.0.1:8092  forge-conductor.service (new, user forge)
                    │
                    ├── forge-worker.service (new, user forge)  ── queue: forge_job (SKIP LOCKED)
                    ├── forge-gateway.service (new, user forge-runner, no docker group)
                    │        └── spawns /opt/craft/<app>/<ver>/bin/<cli> with PATH pinned,
                    │            nice 10 + ionice idle, cwd work/<ep>, 900 s timeout, process group kill
                    ├── Postgres: existing `pod-postgres` container 127.0.0.1:5432
                    │        ├── DB `pod`     (existing, untouched, 5 tables)
                    │        └── DB `forge`   (new, role forge_app, least privilege, own schema)
                    └── existing planes, unchanged:
                           deerflow-forge-console 127.0.0.1:8091
                           pod-mcp 8765 (ufw-restricted) + pod-worker.timer (60 s)
                           DeerFlow 2.2 stack (gateway/frontend/nginx:2026/redis) — used as the
                           conversational front door only, never as ledger/verifier owner
```

| Unit | Type | User | Key hardening |
|---|---|---|---|
| `forge-conductor.service` | simple, Restart=on-failure | `forge` | `NoNewPrivileges`, `ProtectSystem=strict`, `PrivateTmp`, `ReadWritePaths=/var/lib/forge`, `MemoryMax=1G`, `CPUQuota=80%` |
| `forge-worker.service` | simple (queue consumer, long-lived) | `forge` | same + `TasksMax=64` |
| `forge-gateway.service` | simple | `forge-runner` (uid 10002) | no `docker` group, no network egress except loopback, `ReadOnlyPaths=/opt/craft` |
| `forge-eval.service` | oneshot, timer nightly | `forge` | runs goldens; writes `forge_eval`; no publish |
| `forge-backup.service` + timer | oneshot | `forge` | `pg_dump forge`, artifact manifest, restic/off-host |

**Ports:** new services bind `127.0.0.1:8092` (API), `127.0.0.1:8093` (metrics) only. `80/443` belong
to Caddy for the unrelated shop app `[V]`; Forge must not take them. Access is an SSH tunnel
(`ssh -N -L 8092:127.0.0.1:8092 root@<vps>`), exactly like the console on 8091 `[R: README.md]`.

### 10.2 Database and queues

- Reuse the running `postgres:16` instance; create DB `forge` with role `forge_app`
  (`CONNECT`, `USAGE`/`CREATE` on schema `forge`, no rights on `pod`). **Do not** grant superuser.
- Queue: `forge_job` with `SELECT … WHERE state='queued' AND run_after<=now() ORDER BY priority,id
  FOR UPDATE SKIP LOCKED LIMIT 1`, lease `lease_until`, `attempts/max_attempts`, exponential backoff
  on transient codes only; `attempts>max` → `abandoned` + alert. No Redis dependency: the existing
  `deer-flow-redis` is container-internal and belongs to another stack `[V]`.
- Postgres 16 is stock; **pgvector is not assumed** `[U]`. Vectors start as `real[]` with in-process
  cosine (fine at ≤10⁴ cases). Switching the image is a separate, reviewed ops change (it risks the
  existing `pod` volume — do not do it casually).

### 10.3 Model configuration (env names only — no values here)

`/opt/forge/config/forge.env` (root:forge 0640; never committed):

| Variable | Meaning / proposed default |
|---|---|
| `DEEPSEEK_API_KEY` | already present for DeerFlow by name `[V]`; Forge reads the same credential source, never logs it |
| `FORGE_MODEL_ID` | `deepseek-flash` (config-verified id `[V]`) |
| `FORGE_MODEL_BASE_URL` | must be copied from the working DeerFlow provider config — **not invented** `[U]` |
| `FORGE_MAX_OUTPUT_TOKENS` | `8192` (config-verified cap `[V]`); per-role caps are lower |
| `FORGE_THINKING` | `on` for conductor/art-director/curator, `off` for operators/extraction |
| `FORGE_VISION_MODEL_ID` | same model; **vision-on-print-art quality must be measured** `[U]` |
| `FORGE_DB_URL` | `postgresql://forge_app:…@127.0.0.1:5432/forge` |
| `FORGE_ROOTS` | `/var/lib/forge` |
| `FORGE_CRAFT_BIN_ROOT` | `/opt/craft` |
| `FORGE_MAX_EPISODES` | `2` |
| `FORGE_CRAFT_SEMAPHORE` | `1` |
| `FORGE_DAILY_TOKEN_CAP` / `FORGE_DAILY_CENTS_CAP` | set from a measured baseline; **no invented dollar figure** |
| `FORGE_SKILLS_ENABLED` | `1` (kill switch → `0` forces baseline arm) |
| `FORGE_CRITIC_PROMPT_VERSION` | `critic-v0.3` |
| `FORGE_PUBLISH_MODE` | `human_approval_required` (default; `off` in Phase 1) |

Secrets never appear in: prompts, logs, `argv`, `forge_tool_call.result`, error messages, or this
document. Log redaction is a gateway responsibility, tested with a fixture token.

### 10.4 Cost caps and concurrency

- Per episode: `max_tokens`, `max_wall_s`, `max_attempts`, `max_cents` in the envelope; the conductor
  checks before every model call and hard-stops with `E_BUDGET_EXCEEDED`.
- Per day: `forge_budget_ledger` row per account; a breach disables new episodes (existing work drains).
- Concurrency: ≤2 episodes, 1 craft step globally, ≤3 model-calling subagents, ≤1 vision call per
  artifact revision. Rationale: 2 vCPU / ~4.8 GB free / load 1.37 already `[V]`.
- Timeouts: CLI 900 s (matches `POD_STEP_TIMEOUT_S` `[R]`), handoff 900 s, model call 600 s (matches
  DeerFlow's configured timeout `[V]`), critic 120 s.

### 10.5 Observability

- Structured JSON logs per episode to journald (`journalctl -u forge-conductor`), plus the ledger as the
  queryable trace. Correlation: `episode_id`, `handoff_id`, `tool_call_id`.
- `/healthz` (liveness: DB + model credential presence, **not** a model call) and `/metrics`
  (Prometheus text): episodes by state, refusal codes, gate pass rate, cost, queue age, critic flips.
- Daily digest: episodes, verified-pass rate, refusals by code, spend, top failure family.
- Alerts (webhook): budget ≥80 %, queue age >10 min, `E_SOURCE_MUTATED`, skill rollback, backup failure,
  model auth failure. No alert on individual gate failures (noise); they are metrics.
- Log hygiene: bounded sizes (pipeline already caps at 5 MB `[R: config.py]`), digests not bodies for
  large stdout, redaction test in CI.

### 10.6 Backup, rollback, retention

- Nightly `pg_dump -Fc forge` + `pg_dump -Fc pod` (read-only copy of existing), artifacts manifest
  (sha256 list) and skills/facts export; encrypted, off-host, 14 daily + 8 weekly retention.
- Artifacts: content-addressed store; episode `build/` is immutable after close; GC only unreferenced
  blobs older than 90 days, with a dry-run report first (disk is 63 % full `[V]`; set a 10 GB quota).
- App rollback: release dirs `/opt/forge/releases/<ts>` + symlink swap; `systemctl restart
  forge-conductor`; migrations forward-only for append-only tables, with tested down-migration for
  facts/skills (pointer restore, never delete evidence).
- Skill/lesson rollback: pointer flip + golden re-run; kill switch for instant baseline behaviour.
- Restore drill is part of Definition of Done for Phase 3 (restore to a scratch DB and run 3 goldens).

### 10.7 Security

- Least-privilege users: `forge` (orchestrator), `forge-runner` (tool exec, no docker group), existing
  `pod`, `forge` console user. No service runs as root.
- systemd hardening per §10.1; `ReadOnlyPaths=/opt/craft`, `ReadWritePaths=/var/lib/forge` only.
- Network: forge services loopback-only; craft processes run with `--network none` in docker mode
  `[R: runner.py]` and no egress in native mode (verified by an egress test, not assumption `[U]`).
- Credentials: env file 0640 root:forge, no secrets in repo/console bundle; the console is a pure
  viewer and must never receive model or Fourthwall credentials `[R]`.
- Authorization: role-scoped tool tokens (§4.1); publish requires a separate human approval token;
  approval is per-artifact-hash, so a changed artifact invalidates it.
- Prompt injection: brief text, OCR, EXIF, filenames, web/API text are **data**; they are delimited,
  never inserted into tool-policy or system prompts; any instruction-like content is logged and
  ignored. A tool may not be invoked because text asked for it.
- Supply chain: pin framework versions; MCP servers and CLIs execute code — review before install;
  no unpinned Git sources (see dossier's install discipline).
- Audit: hash-chained events, append-only; local access logs retained 90 days; no customer PII in
  prompts beyond what the brief requires; rights records kept with artifacts.
- Firewall: add **no** new public ports; if a reverse proxy is later desired, it must be an explicit
  Caddy vhost with auth, not a default route (80/443 already owned).

---

## 11. Build vs buy (and what is actually verified)

| Candidate | What it gives | Verified state | Decision |
|---|---|---|---|
| **DeerFlow 2.2** (installed at `/opt/deer-flow`) | LangGraph runtime, middleware, subagents (max_running 3), MCP client, memory manager, conversational front door | **Installed and running**; `CHANGELOG 2.2.0`; model `deepseek-flash` configured `[V]` | **Reuse as front door / interactive agent only.** Do not let it own the ledger, gates or promotion. Its memory is facts/preferences, not art-skill learning `[D: Q133]`. Extending its memory backend is `[U]` until read. |
| **Eko 4.1.3** (MIT, TS) | planner, `dependsOn` DAG, pause/resume, MCP discovery | Source/README verified in dossier `[D: E1–E5]`; docs host 503 `[D]` | **Borrow patterns** (DAG semantics, pause/resume, MCP discovery). Optional TS sidecar later. Not the core: process-local task state, second runtime `[D: Q10, Q144]`. |
| **LangGraph** | durable graph + checkpointer, human-in-the-loop interrupts | Public surface known from dossier `[D: D4]`; not installed in this repo `[V: package.json]` | **Optional for the planner graph only.** The ledger-critical state machine is Postgres-native (§10.2) so it stays testable without a framework. |
| **OpenAdapt** | record → compile → verify → replay; read-back before claiming success | README/pattern `[D: B4]` | **Adopt the discipline**: verify effect from the system of record; compiled skills are programs; halt on uncertainty. Not a generative design system. |
| **Playwright MCP** | a11y-snapshot browser control, roots | `[D: B5]` | **Fallback plane only**, with mandatory read-back. |
| **Craft CLIs / JSON / MCP + atlas + `craft_trace` / `prep_print_art`** | domain commands, gates, recipes | VectorCraft 0.21.1 + PhotoCraft 0.20.2 installed `[V]`; catalogues on disk `[V]`; gates are repo tools `[R]`; **FilmCraft/DesignCraft/EffectCraft absent** `[V]` | **Reuse as the domain layer.** Resolve by absolute path + version probe; replace the 127-shims before any E2E claim. |
| **Existing `pod_pipeline`** | deterministic orchestration, validators, idempotent publish, MCP | `[R]` orchestrator/validators/mcp/schema | **Leave untouched.** Forge calls it through MCP for pipeline jobs; Forge does not fork it. |
| **Existing console** | read-only viewer | `[R]`, running on 8091 `[V]` | **Leave untouched.** Forge is headless; a later viewer can read `forge_*` tables. |

**Build from scratch (no framework supplies these):** tool gateway (registry, allowlist, roots,
idempotency, refusal codes, absolute-path/version pinning); the evidence ladder and verifier;
blind critic harness (render ladder, grounded schema, prompt versioning, stability metric); episode
ledger with hash chain and retrieval receipts; skill format/runner/promotion/rollback; eval harness
(goldens, arms, held-out set, CI); the ops units and caps.

**Explicitly not doing:** a generic agent framework; a pixel-first computer-use agent; fine-tuning or
RL now; autonomous publishing; any claim of measured learning before the eval harness exists.

---

## 12. State machine, failure and refusal modes

### 12.1 Episode state machine

```
intake ──► briefed ──► planned ──► context_ready ──► executing ──► verifying ──► critiquing
  │           │           │             │               │            │             │
  │           │           │             │               │            │             ├─► accepted
  │           │           │             │               │            │             ├─► needs_human ──► accepted|rejected
  │           │           │             │               │            │             ├─► unverified (missing rung)
  │           │           │             │               │            │             └─► rejected
  │           │           │             │               └─► failed ◄──┴─────────────┘
  └───────────┴───────────┴─────────────┴─► refused (terminal, named code)
                         paused ──► (resume from last verified step)
                     cancelled / quarantined (source mutation, security event)
```

Guards: `briefed` requires deliverable + target + rights; `planned` requires an ArtSpec with cited
brand facts and success criteria; `context_ready` requires a retrieval receipt (possibly empty);
`executing` requires locks and budget; `verifying` requires a completed handoff with artifacts;
`critiquing` requires rungs 1–4 green; `accepted` requires the arbitration rules (§4.4) and, for
print/publish, human approval. Every transition writes a `forge_event` (hash-chained).

### 12.2 Failure taxonomy → response

| Class | Example | Response |
|---|---|---|
| Planning failure | ArtSpec contradicts the brief | conductor rejects handoff; Art Director revises once; then `needs_human` |
| Tool/schema failure | `E_PARAM_REJECTED`, `E_COMMAND_UNKNOWN` | retry with corrected params only after schema re-read; unknown id → human |
| State failure | wrong document/selection, `E_DOCUMENT_STATE` | reset document state, re-run the batch on a copy |
| Quality failure | gate fail / critic reject | route to skill recovery branch; max 2 recovery loops; then `needs_human` |
| Policy/rights failure | `E_RIGHTS_MISSING`, `E_PUBLISH_NOT_APPROVED` | terminal refusal; owner action required |
| Infrastructure failure | OOM/timeout/model 5xx | transient retry with backoff; reschedule job; keep last verified state |
| Evaluation failure | `E_EVAL_EMPTY`, missing gate | evaluation refuses; no score; block promotion |
| Security event | root escape attempt, injection pattern, source mutation | quarantine episode, alert, no artifact import into memory |

### 12.3 Named refusal examples (operator-facing text)

```
E_GATE_FAILED: white residual 0.7% (max 0.0%) on build/<ep>/final.png
  how_to_fix: re-run step 1 with prep_print_art --mode white; see gate report lines 12-14
E_APP_DRIFT: vectorcraft-cli 0.22.0 found, episode pinned 0.21.1
  how_to_fix: refresh catalogue, re-run goldens, repin the episode
E_PUBLISH_NOT_APPROVED: artifact sha256:… has no approval token
  how_to_fix: owner approves this exact hash in the console; nothing was published
```

---

## 13. 90-day phased plan

| Phase / weeks | Deliverable | Gate to pass (evidence, not vibes) |
|---|---|---|
| **0 (0–1)** | Host baseline + repo inventory: forge DB/role, catalogue hashes, CLI probes, 10 goldens frozen, rights records, rubric v0, critic prompt v0.3, `forge_job` queue | 10 goldens execute **on the existing pipeline** and record honest pass/fail; no Forge run yet; shims replaced or the gap documented |
| **1 (2–3)** | Tool gateway: registry, absolute-path/version pinning, allowlist, roots, idempotency, refusals; verifier rungs 1–3; source-mutation check | One trace episode + one retouch episode end-to-end, every tool call in `forge_tool_call`, zero source mutations |
| **2 (4–5)** | Ledger + handoffs + conductor state machine + render ladder + blind critic; episode replay from ledger | One full episode reconstructed from the ledger alone; critic schema-validation 100 %; critic stability measured on 20 identical renders |
| **3 (6–7)** | Case retrieval + retrieval receipts + A/B harness; baseline vs memory arm on dev goldens | A/B report with CI; if no lift, retrieval is disabled by default (honest null result accepted) |
| **4 (8–9)** | Skills: draft/candidate/active, promotion gate, regression suite, kill switch, rollback drill | 3 skills promoted with ≥3 independent evidences; one deliberate rollback exercised and verified |
| **5 (10–11)** | Print masters + second app + 50-golden corpus; cost/latency baseline; observability dashboards | Zero unsafe publishes; cost per accepted artifact measured; private held-out set recorded |
| **6 (12)** | Hardening: backup/restore drill, security review, retention/GC, runbooks, ops handover | Restore drill passes; `systemd-analyze security` baseline recorded; incident runbook tested |

Staffing assumption: 1 engineer + design owner (taste/sign-off) + part-time infra/security. Timeline is
an **estimate** `[I]`, not a measured schedule. Do not plan Phase 3 (fine-tune/RL) inside 90 days.

---

## 14. Fifteen candidate questions for the 200-question corpus

1. Does `vectorcraft-cli` 0.21.1 emit a stable machine-readable envelope for every command, or do
   scripts have to parse human text? (blocks the JSON-control-channel assumption)
2. Do FilmCraft/DesignCraft/EffectCraft offer the same CLI/JSON/MCP parity as VectorCraft and
   PhotoCraft, and how many of their commands are catalogue-indexed today?
3. What is the measured wall-clock cost of a 2400×3000 trace + 10-gate cycle on a 2-vCPU host with one
   concurrent step, including render and export?
4. How reliable is `deepseek-flash` vision at detecting print-class defects (white fringe, halo, ghost
   text, sub-1 % specks) compared with a human rater — what is its false-pass rate?
5. Can a vision critic be constrained to cite real crop regions (no hallucinated boxes), and what
   prompt/schema enforces that with this model?
6. Which of the 918 VectorCraft / 965 PhotoCraft commands are actually exercised by the first five task
   families, and what is the smallest allowlist that covers them?
7. Does `craft_trace`'s retype gate detect a mis-mapped text box, or only count boxes and pass?
8. How does `prep_print_art --mode white` behave on cream/tan and soft AI shadows, and what is its
   measured false-removal rate?
9. Are repeated runs of the same trace/render bit-identical (fonts, rsvg-convert, library versions), or
   does output hash drift require a tolerance policy?
10. Does DeerFlow 2.2's memory manager accept a custom/external backend, or only its configured
    backends — and can it be pointed at a `forge` ledger view without forking the harness?
11. How much of a DeerFlow subagent's 300 s queue timeout / `max_running: 3` is consumed by the
    conductor's handoffs, and where does the bottleneck actually appear?
12. What human inter-rater agreement (e.g. Krippendorff's α) is achievable on the five-dimension
    rubric, and how many reviewers are needed per promotion to be defensible?
13. Does retrieval of past cases measurably raise first-attempt verified-pass rate on held-out goldens,
    or does it just add tokens (null result is a valid outcome)?
14. What is the measured token and cent cost per accepted artifact on `deepseek-flash` with thinking
    on vs off, and does thinking improve gate pass enough to justify the cost?
15. Can a Playwright fallback for Fourthwall admin be trusted if every action is followed by an API
    read-back (exact product id/state/dedupe), and what is its failure rate vs the API-only path?

---

## 15. Open unknowns (must be closed before they become policy)

| Unknown | Why it matters | Cheapest decisive evidence |
|---|---|---|
| Model pricing and real token usage for this workload | every cost cap and dollar figure is currently ungrounded | instrument 10 episodes, read provider usage, no estimates |
| Vision quality on print defects | the critic is load-bearing for taste; if it false-passes, the ladder is fake | labelled 50-defect corpus, measure precision/recall |
| Craft CLI JSON envelope stability | tool gateway parsing and error mapping depend on it | snapshot stdout/stderr for 20 commands on 0.21.1/0.20.2 |
| FilmCraft/DesignCraft/EffectCraft availability | multi-app supervision is claimed in the brief, only 2 of 5 apps exist on the host | install + `--version` + catalogue snapshot, then a smoke task |
| pgvector availability on `postgres:16` | retrieval design changes if vectors must be in-process | `CREATE EXTENSION vector` on a scratch DB |
| DeerFlow memory backend extensibility | decides whether facts live in DeerFlow or `forge` | read `/opt/deer-flow/backend` memory provider interfaces (not yet read) |
| Approximate cost of a full 50-golden eval run | gates the A/B cadence | measure once on 5 goldens × 3 arms |
| Human rater availability and agreement | taste claims are impossible without it | 2 reviewers × 20 artifacts, compute agreement |
| Exact refusal-code mapping for CLI stderr | a correct refusal vs a generic failure | 10 negative fixtures across both apps |
| Whether `deepseek-flash` vision accepts multiple images and at what resolution | render ladder + critic cost | one documented API probe (spends quota: needs owner approval) |

Also explicitly unverified: **this design was not implemented, not measured, and no model call was made
by this task**. The DeepSeek key was observed by **name only** and never read, echoed or logged.

---

## 16. Evidence register

| Claim | Label | Source |
|---|---|---|
| Host `srv2108523`, 2 vCPU, 7,935 MB RAM, 36 GB free, load 1.37 | **[V]** | Appendix A.1 |
| Console/pod-mcp/pod-worker.timer/docker active; listeners 8091/5432/8765 | **[V]** | Appendix A.1 |
| DeerFlow 2.2.0 checkout; `deepseek-flash` / "DeepSeek V4.1 Flash"; ctx 1,048,576; max_tokens 8,192; vision+thinking true | **[V]** | Appendix A.2 |
| `subagent_runtime.max_running: 3`, queue 300 s, recursion_limit 100 | **[V]** | Appendix A.2 |
| `DEEPSEEK_API_KEY` present in gateway env (name observed only) | **[V]** | Appendix A.2 |
| VectorCraft 0.21.1 / PhotoCraft 0.20.2 installed; Film/Design/Effect absent | **[V]** | Appendix A.3 |
| `*-cli` bare names MISSING on PATH; `/opt/pod-pipeline/bin` holds 127-shims | **[V]** | Appendix A.3 |
| `pod` DB has 5 tables, no agent/memory/eval tables | **[V]** | Appendix A.4 |
| Orchestrator deterministic; retries transient only; trace fallback exit 1; publish idempotent | **[R]** | `pod_pipeline/orchestrator.py` |
| 3 MCP tools; boundary validation; detached spawns | **[R]** | `pod_pipeline/mcp_server.py` |
| 4 validators; 400 MP bomb cap | **[R]** | `pod_pipeline/validators.py` |
| Unique live-run index, state constraints | **[R]** | `sql/schema.sql:136-138` |
| Console is pure viewer; 8091 systemd; SSH tunnel | **[R]** | `README.md`, `deploy/vps/*` |
| No LLM SDK in `package.json` | **[R]** | `package.json` |
| `craft-agent-operator` ledger + evaluation are **proposed**, not deployed | **[R]** | `skills/craft-agent-operator/references/*.md` |
| `craft_trace` 10 gates, retype mapping, named errors | **[R]** | `tools/craft_trace.py`; `[D: C3]` |
| Eko memory is in-process, not durable | **[D]** | `REPORT.md` Q10–Q13 |
| DeerFlow memory = facts/preferences, no art-skill learning | **[D]** | `REPORT.md` Q132–Q134 |
| Gates are technical, not taste; reward hacking risk | **[D]** | `REPORT.md` Q108, Q116 |
| Anything about model cost, vision accuracy, JSON envelopes, FilmCraft | **[U]** | §15 |

---

## Appendix A — read-only probe evidence (2026-11-05)

Commands were run over SSH as root, read-only; no writes, no service changes, no Craft execution.
Output abridged to the lines that support claims above.

### A.1 Host, units, listeners

```
$ ssh -i ~/.ssh/id_ed25519_hostinger root@179.197.88.181 'hostnamectl --static; nproc; free -m | head -2; df -h / | tail -1; systemctl is-active …; ss -ltnp | grep -E "8091|5432|8765"'
srv2108523
7.0.0-38-generic
2
Mem: 7935 total, 4835 available
/dev/sda1  96G  61G  36G  63% /
active / active / active / active
127.0.0.1:8091  node
127.0.0.1:5432  docker-proxy
0.0.0.0:8765    python
```

### A.2 Model configuration (values redacted at source)

```
$ sed -n '1,60p' /opt/deer-flow/config.yaml | sed -E 's/(api_key:).*/\1 <redacted>/'
models:
- name: deepseek-flash
  display_name: DeepSeek V4.1 Flash
  model: deepseek-flash
  context_window: 1048576
  api_key: <redacted>
  timeout: 600.0
  max_retries: 2
  max_tokens: 8192
  supports_vision: true
  supports_thinking: true

$ grep -nA5 'subagent_runtime' /opt/deer-flow/config.yaml
159:subagent_runtime:
160-  max_running: 3
161-  max_queued: 64
162-  admission_policy: queue
163-  queue_timeout_seconds: 300

$ docker exec deer-flow-gateway env | cut -d= -f1 | grep -i deepseek
DEEPSEEK_API_KEY
```

### A.3 Craft installation and CLI resolution

```
$ /opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli --version
vectorcraft-cli 0.21.1

$ for c in vectorcraft-cli photocraft-cli filmcraft-cli designcraft-cli effectcraft-cli; do command -v $c || echo MISSING; done
MISSING × 5

$ ls -1 /opt/craft
artcraft-docs catalogues photocraft pkg vectorcraft

$ head -5 /opt/pod-pipeline/deploy/craft-bin/vectorcraft-cli
#!/bin/sh
echo "vectorcraft-cli: vendor binary not installed. Replace this file and rebuild pod-craft-runner." >&2
exit 127
```

### A.4 Database and DeerFlow checkout

```
$ docker exec pod-postgres psql -U pod_app -d pod -tAc "select table_name from information_schema.tables …"
agent_sync_logs
fourthwall_products
ingested_assets
processing_jobs
users_saas_accounts

$ git -C /opt/deer-flow log -1 --format='%H %cd'
58fc5bd5b8e6ea46538e9481ba06ca2a46e14e2a Wed Nov 4 14:46:47 2026 +0800
$ head -12 /opt/deer-flow/CHANGELOG.md
## [2.2.0] — 2026-10-29
```

### A.5 Known discrepancy recorded honestly

`README.md` claims a live end-to-end run (trace → trim → effect → PNG). In the current host state the
bare CLI names resolve to the 127-shims in `/opt/pod-pipeline/bin`, so that claim is **not
reproducible now**; the real binaries exist under `/opt/craft` but are not wired. This design treats it
as an ops gap to close in Phase 0, not as evidence against the pipeline's design.

---

*End of design. Next action is Phase 0 approval and a measured baseline — not a claim that the Forge
Conductor exists. No model call, Craft command, migration or service was created by this task.*


