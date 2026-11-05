# Wave 2 / 01 — Local Stack + Hostinger VPS Audit (DeerFlow Forge)

**Auditor:** `stack-vps-auditor` (read-only systems auditor)
**Shared task:** `task-1` (claimed, revision 2)
**Audit date/time:** 2026-11-05, 10:06–10:20 America/Chicago = 16:06–16:20 UTC (clock read on host: `date -u` → `2026-11-05T16:06:44Z`)
**Scope:** local repo `C:\Users\Riley\Desktop\DeerFlow Forge`, blueprint/pipeline, deploy units, config; Hostinger VPS `root@179.197.88.181` (`srv2108523`) over SSH with `~/.ssh/id_ed25519_hostinger`, `BatchMode=yes`.
**Mutation policy:** none. Only `read`, `grep`, `ls`, `cat`, `sha256sum`, `diff -rq`, `git rev-parse/log/status`, `systemctl is-enabled/is-active/cat/show`, `docker ps/images/inspect/network`, `ss`, `df`, `free`, `nproc`, `du`, `psql SELECT`, `sqlite3 mode=ro`, `curl` to loopback, `--version/--help` probes. No writes, restarts, installs, publishes, prunes. Nothing outside `/tmp` (transient probe files) was written on the host; nothing in the repo was modified.

## Evidence labels

| Label | Meaning |
|---|---|
| `VERIFIED` | Observed in this session's own command output (quoted below). |
| `READ` | Read from a file in the repo or on the host, at the cited path/line. |
| `INFERRED` | Logical consequence of verified/read facts, not directly observed. |
| `UNVERIFIED` | Not provable with the access available; stated as a gap. |

---

## 1. Ten headline facts

1. `VERIFIED` Pipeline and console are **deployed and running** on the VPS: `pod-mcp.service` active since 2026-11-05 06:00:19 UTC listening on `0.0.0.0:8765`; `pod-worker.timer` firing every 60 s (`drained 0 run(s)`); `deerflow-forge-console.service` answering HTTP 200 on `127.0.0.1:8091`.
2. `VERIFIED` The pipeline **cannot execute any in-system craft step**. `/opt/pod-pipeline/bin/{vectorcraft,photocraft,designcraft,effectcraft,filmcraft}-cli` are 122–124-byte `/bin/sh` stubs that `exit 127`; the last real run (`a7e58e17-…`, 2026-11-05 05:30) died at its first step with exactly that stub message in its 94-byte log.
3. `VERIFIED` Real vendor binaries exist only for **two of five** tools: `/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli` (`vectorcraft-cli 0.21.1`) and `/opt/craft/photocraft/photocraft-0.20.2-linux-x86_64/bin/photocraft-cli` (`photocraft-cli 0.20.2 (7c12f6471, 2026-11-05)`). `designcraft*`, `effectcraft*`, `filmcraft*` are **absent host-wide** (`find / -xdev -maxdepth 4`).
4. `VERIFIED` The pipeline's craft argv contract **does not match the installed CLIs**: `vectorcraft-cli trace …` → `vectorcraft-cli: unknown subcommand 'trace'`; `photocraft-cli --input …` → `error: unexpected argument '--input' found`. `routes.py` marks these exact contracts `ASSUMPTION` (READ `blueprint/files/pod_pipeline/routes.py:63-70, 88-96`).
5. `VERIFIED` Both installed craft CLIs ship **their own MCP server** (`vectorcraft-cli mcp [--headless]`, `photocraft-cli mcp [--bridge]`). A live handshake from `vectorcraft-cli mcp --headless` returned `protocolVersion 2024-11-05`, `serverInfo{name:"vectorcraft", version:"0.21.1"}`, tools for `command_list/command_run/command_batch/draw_shape/draw_path/set_paint/render_preview/doc_inspect`. This is the real agent surface — and it is **not registered** in DeerFlow.
6. `VERIFIED` Exactly **one** MCP server is registered in DeerFlow: `mcpServers.forge` → `http://172.17.0.1:8765/`, and it is reachable from inside the gateway container (`curl` 200 `{"ok":true}`, `tools/list` returns the three Forge tools).
7. `VERIFIED` The pod database is **empty**: `users_saas_accounts=0, ingested_assets=0, processing_jobs=0, fourthwall_products=0, agent_sync_logs=0`; DB size 8127 kB (schema only). Any claim of a live end-to-end run is now a claim about a **reset** database, not current state.
8. `VERIFIED` `/opt/pod-pipeline` is **not a git repository**. Deployment sync was established by sha256 instead: **26/26** compared files (all `pod_pipeline/*.py`, `sql/schema.sql`, `deploy/*`, `config/*`, `requirements*.txt`, `pytest.ini`) are byte-identical to the local working tree. The console repo `/opt/deerflow-forge` is at `32fc71f` and is **9 commits behind** local `d9dc2fe`.
9. `VERIFIED` Host capacity is small: **2 vCPU** (AMD EPYC 9354P), **7.9 GB RAM** with **2.5 GB swap already used**, **36 GB free** of 96 GB (63 % used). Docker reclaimables: **24.55 GB** images + **10.06 GB** build cache (76 % of 32.26 GB).
10. `VERIFIED` **No LLM code exists in the pipeline or the console.** `pipeline.env` contains zero `DEEPSEEK*` names; the console's only DeepSeek mention is a label string (`src/components/forge/console.tsx:43`). Every model call belongs to the separate `deer-flow` deployment (backend 2.2.0, `deepseek-flash` = "DeepSeek V4.1 Flash").

---

## 2. Local repository map (console vs pipeline)

| Area | Path | Nature | Evidence |
|---|---|---|---|
| Console (viewer) | `src/`, `public/`, `scripts/`, `server/` | TanStack Start + Vite + React 19 app, Nitro `node-server` build | `READ` `README.md:12-49`, `package.json` |
| Deployable pipeline | `blueprint/files/` | Python `pod_pipeline`, `sql/schema.sql`, Compose, systemd, MCP bridge, craft CLI stubs, tests | `READ` `README.md:13` |
| VPS console deploy | `deploy/vps/install-console.sh`, `deploy/vps/deerflow-forge-console.service` | Node 22 prefix `/opt/node22`, loopback `127.0.0.1:8091` | `READ` |
| Provided originals | `attachments/` | Pre-blueprint modules the package was fitted to | `READ` `README.md:14` |
| Migrations | `migrations/` | Applied by `npm run build` when `DATABASE_URL` set | `READ` `README.md:15` |
| Skills (installed, not code) | `blueprint/files/skills/**` | 30+ `SKILL.md` operator docs incl. `craft-agent-operator`, `artcraft-command-atlas`, `craft-mcp-drive` | `READ` listing |
| Console contract | `AGENTS.md` (19 005 B) | **Not a DeerFlow Forge contract** — it is the *Grok App Builder sandbox* contract ("You are Grok Build, in an isolated Linux sandbox at `/workspace`"). Project guidance here is stale/foreign to the VPS stack. | `READ` `AGENTS.md:1-20` |

Local git: `HEAD = d9dc2fe8163fe7796aa4acad1e6f75ae78df889b`, `2026-11-05T10:03:18-06:00`, "Research: Eko/Craft agent dossier, 200 Q&A, operator skill"; working tree **clean**. `VERIFIED`

Notable `package.json` facts (`READ`): name is `app-builder-workspace` (not `deerflow-forge`); deps include `@tanstack/react-start ^1.168.60`, `vite ^8.2.0`, `nitro 3.0.260610-beta`, `react ^19.2.0`, `playwright ^1.62.0`. **No** `ai`, `@ai-sdk/*`, `openai`, `anthropic`, `langchain` or `deepseek` package. Scripts: `build:vps` (`scripts/build-vps.mjs`), `test` (node --test + 5 TS test files), `typecheck`, `lint`, `smoke:console`.

---

## 3. Architecture and call chain

```text
                        ┌──────────────────────────── VPS 179.197.88.181 (Ubuntu 26.04.1, KVM, 2 vCPU / 7.9 GB) ─────────────────────────────┐
 Browser (SSH tunnel) ──┤ 127.0.0.1:8091  deerflow-forge-console.service  (forge)  Nitro node-server  → pure viewer, imports .py as ?raw │
                        │                                                                                                          │
 caddy (80/443) ────────┤ ridgeboundia-caddy container  →  ridgeboundia.com (separate app, unrelated to this audit)                    │
                        │                                                                                                          │
 DeerFlow agent ────────┤ docker deer-flow-gateway (192.168.200.4) ──HTTP──► 172.17.0.1:8765  pod-mcp.service (pod)                     │
 (deepseek-flash)       │        │  langchain_mcp_adapters                                                     │                              │
                        │        └─ extensions_config.json → mcpServers.forge → 3 tools                             │                          │
                        │                                                                                                          │
                        │ pod-mcp: tools/list = [list_pending_assets, trigger_pipeline_job, get_fourthwall_status]                  │
                        │          trigger_pipeline_job → INSERT processing_jobs(status=queued)                                     │
                        │                              → subprocess.Popen(python -m pod_pipeline.worker --run-id <uuid>)              │
                        │                                                                                                          │
                        │ worker: claim_run (UPDATE … FOR UPDATE SKIP LOCKED) → run_pipeline                                        │
                        │   stage input (sha256 verified) → trace_step → route.steps → validators → publish → finish_run           │
                        │   each step: build_command() → native `nice -n 10 ionice -c3` or docker sandbox → run_step()              │
                        │   binaries resolved from <POD_ROOT>/bin (PATH) → ▶ stubs exit 127 today                                   │
                        │                                                                                                          │
                        │ pod-postgres container (postgres:16.15) 127.0.0.1:5432  ← pod-pipeline_default bridge 172.20.0.2          │
                        │ pod-worker.timer (60 s) → pod-worker.service --drain --scan (recover stale runs, scan inbox, drain queue)  │
                        └──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

Call chain, precisely (`READ blueprint/files/pod_pipeline/*`):

1. **MCP ingress** — `mcp_server.handle_rpc` speaks JSON-RPC 2.0 over HTTP (`_client`/`_read_http`) and stdio (`serve_stdio`, newline or `Content-Length` framing). Methods: `initialize`, `ping`, `tools/list`, `tools/call`. `POST /` only; `GET /health` → `{"ok":true}`. `READ mcp_server.py:_client, handle_rpc`.
2. **`trigger_pipeline_job`** — validates `asset_id`/`product_type` against `PRODUCT_TYPES`, loads the asset row, `db.enqueue_run` (unique partial index `processing_jobs_one_live_run` makes repeats idempotent), writes `agent_sync_logs(event_type="job.triggered")`, then `_spawn_worker` → `spawn_detached` (`subprocess.Popen`, `start_new_session=True`, stdout/stderr to `logs/jobs/mcp-spawn.log`). Idempotent repeat returns `created:false, spawned:false`.
3. **Worker** — `python -m pod_pipeline.worker --run-id <uuid>` → `run_pipeline` → `db.claim_run` with `FOR UPDATE SKIP LOCKED` (single-writer claim, safe against the timer drain racing an MCP spawn).
4. **Orchestration** — `_execute`: mkdir `sandbox|build|logs/<run_id>`, `set_asset(status=processing)`, `_stage_input` (sha256 must match ingest, else quarantine), `_trace_stage`, then each `route.steps` in order; `_collect_and_validate` enforces non-empty outputs + `flush_to_disk` (fsync file **and** directory) + named validators; `_publish`; `finish_run`; sandbox removed only on success.
5. **Run summary** — `run.finished` row in `agent_sync_logs` with `ok`, `product_state`, `artifact`, `error`.

---

## 4. LLM usage — actual state (a key corpus finding)

| Question | Answer | Evidence |
|---|---|---|
| Does the repo's pipeline call an LLM? | **No.** Zero `deepseek` occurrences in `config/pipeline.env` (`grep -c -i deepseek` → `0`), zero model/LLM client imports in `pod_pipeline/`. | `VERIFIED` |
| Does the console call an LLM? | **No.** No AI/LLM dependency in `package.json`; the only DeepSeek string in `src/` is a UI label. | `READ` `src/components/forge/console.tsx:43`, `VERIFIED` grep |
| Where does DeepSeek actually run? | A **separate** DeerFlow 2.2.0 deployment at `/opt/deer-flow` (container `deer-flow-gateway`), configured with `models[0].name: deepseek-flash`, `display_name: DeepSeek V4.1 Flash`, `use: deerflow.models.patched_deepseek:PatchedChatDeepSeek`, `model: deepseek-flash`, `context_window: 1048576`, `api_key: $DEEPSEEK_API_KEY`, `timeout: 600.0`, `max_retries: 2`, `max_tokens: 8192`, `supports_vision: true`, `supports_thinking: true`. | `READ` `/opt/deer-flow/config.yaml:18-37` |
| Base URL | **Not set anywhere readable.** `config.yaml` has no `base_url`; docker env has no `DEEPSEEK_BASE_URL`. Effective endpoint is therefore the `langchain_deepseek.ChatDeepSeek` default (api.deepseek.com). | `INFERRED` — `READ` `patched_deepseek.py:18` imports `langchain_deepseek.ChatDeepSeek` |
| Key source | Environment only: container env name `DEEPSEEK_API_KEY` = `<set>` (value never read/printed). Key file: none found; `/opt/deer-flow/.env` (mode 0600) and `config.yaml` reference `$DEEPSEEK_API_KEY`. | `VERIFIED` name presence, `READ` config |
| Is the key valid / has a live call succeeded? | **UNVERIFIED.** No proof either way. Supporting-but-not-conclusive evidence of real agent turns: `deerflow.db` has **1163 LangGraph checkpoints** (latest 2026-11-05T03:11:16Z) containing `langchain_core.messages` state, and 3+ thread dirs under `users/default/threads/`. Counter-evidence for "it works now": `runs` table is 0, `run_events` 0, gateway log contains **0** `deepseek` mentions. | `VERIFIED` counts; `UNVERIFIED` validity |
| Cost/token ledger | **None.** No token/usage/cost table in `deerflow.db` (45 tables; only `mcp_oauth_tokens`, `personal_access_tokens` match *token*). | `VERIFIED` |

**Consequence for the harness design:** the DeerFlow agent and the pipeline are decoupled by MCP only. Adding a Craft-driving agent means either (a) pointing an agent at craft's native MCP servers, or (b) extending the Forge MCP surface — neither exists today.

---

## 5. MCP surface inventory

| Server | Transport | Registered in DeerFlow? | Tools | Evidence |
|---|---|---|---|---|
| Forge pipeline (`pod_pipeline.mcp_server`) | HTTP `0.0.0.0:8765` + stdio | **Yes** — `mcpServers.forge` enabled, `type: http`, `url: http://172.17.0.1:8765/` | `list_pending_assets`, `trigger_pipeline_job`, `get_fourthwall_status` | `VERIFIED` live `tools/list`; `READ` `/opt/deer-flow/extensions_config.json` |
| VectorCraft | stdio (`mcp`, `--headless` or `--connect 127.0.0.1:7979`) | **No** | command/doc/draw family (`command_list`, `command_run`, `command_batch`, `draw_shape`, `draw_path`, `set_paint`, `render_preview`, `doc_inspect`, …) + resources `vectorcraft://object|command|effect|swatch` | `VERIFIED` handshake; `READ` `/opt/craft/artcraft-docs/mcp.md:1-40, 347+` |
| PhotoCraft | stdio (`mcp [--bridge 127.0.0.1:PORT]`, automation roots per direction) | **No** | engine command registry (965 entries on host) | `VERIFIED` `photocraft-cli mcp --help` |
| GitHub / parallel-search / openviking / postgres / long-running-reports | various | present but **`enabled: false`** | — | `READ` extensions_config |

Also present: `blueprint/files/deploy/mcp-stdio.mjs`, a Node stdio↔HTTP bridge that mirrors the client's framing (newline vs `Content-Length`). `READ`.

---

## 6. Job / run state machine, retries, persistence

**Schema** (`READ blueprint/files/sql/schema.sql`, 5 tables, applied identically on the VPS):

| Table | Role | Key constraints |
|---|---|---|
| `users_saas_accounts` | tenant, Fourthwall credential ciphertext + `auto_publish` | `tenant_token_hash` length 64 + unique; `fourthwall_api_secret_enc bytea` (pgp) |
| `ingested_assets` | one row per inbox file; sha256, dims, dpi | `status ∈ {pending,queued,processing,processed,failed,quarantined}`, `trace_state ∈ {pending,tracing,traced,raster_fallback,trace_failed}`, unique `(account_id, sha256)` |
| `processing_jobs` | both the **run** row (`module='orchestrator'`) and every **step** row | `status ∈ {queued,running,succeeded,failed}`; partial unique index `processing_jobs_one_live_run (asset_id, product_type) WHERE module='orchestrator' AND status IN ('queued','running')`; `error_digest ≤ 8000` |
| `fourthwall_products` | publish state per (account, asset, product_type) | natural unique `(account_id, asset_id, product_type)`; `publish_state ∈ {draft,processing,active,failed,needs_manual_upload}` |
| `agent_sync_logs` | audit log (inbound MCP, outbound Fourthwall) | `direction ∈ {inbound,outbound}`; unique `external_event_id`; payload ≤ 32 KiB |

**Run state machine** (`READ orchestrator.py, db.py`): `queued` → (`claim_run`, `FOR UPDATE SKIP LOCKED`) → `running` → `succeeded` | `failed`. Asset: `pending` → `queued` → `processing` → `processed` | `failed` (`quarantined` when sha mismatch / source vanished). Trace branch: `tracing` → `traced`, or `raster_fallback` when exit code ∈ {1}, or `trace_failed`.

**Retries.** `Settings.max_attempts = 2` (`POD_MAX_CONCURRENCY`/defaults in `config.py:66`). A step retries **only** when `outcome.transient` — `TRANSIENT_EXIT_CODES = {-9,-15,137,143,75}` or timeout (`runner.py:16`). Validation failures get `exit_code=0` and are **never retried** (deterministic re-run). Trace fallback is a separate tier-1 path, not a retry. Crash recovery: `recover_stale_runs` re-queues `running` runs whose PID is dead.

**Persistence details.** Per step: `start_step` row (argv captured), `finish_step` (status, exit, pid, digest, log_path, output_path). Artifacts: `flush_to_disk` = stable-size poll ×2 then `fsync(file)` + `fsync(dir)` (`runner.py:flush_to_disk`). Logs: `logs/jobs/<run_id>/<NN>-<step>-t<tier>-a<attempt>.log`, digest-filtered, capped by `max_log_bytes` (5 MiB). Inline credential decryption: `pgp_sym_decrypt(fourthwall_api_secret_enc, $POD_CREDENTIAL_KEY)` with env single-tenant fallback.

**Sandboxing.** Native mode (`POD_USE_DOCKER=0` on this host): `nice -n 10` + `ionice -c 3`, child env is a minimal allow-list (`PATH` prefixed with `<POD_ROOT>/bin`, `HOME`, `LANG=C.UTF-8`, `TMPDIR`, `QT_QPA_PLATFORM=offscreen`). Docker mode would add `--memory/--cpus/--cpu-shares/--pids-limit 256 --network none --cap-drop ALL --read-only`.

**Observed live state:** `drained 0 run(s), 0 failed` every minute; `inbox scan registered 0 new asset(s)`; all tables 0 rows. `VERIFIED`

---

## 7. Auth and publish path

- **Console auth:** none. `VITE_AUTH_ENABLED = "false"` in `.grok/app-env.json` (`READ`, via `git show HEAD:.grok/app-env.json`); served loopback-only on 8091, reached by SSH tunnel (`README.md:143-148`). No sessions, no middleware auth on the Nitro server.
- **MCP auth:** **none.** `mcp_server` has no token check; `POD_MCP_HOST=0.0.0.0`. Exposure is bounded only by `ufw` (`8765/tcp ALLOW IN 172.16.0.0/12`, `192.168.200.0/24`). Any container on the host's docker bridges can call `trigger_pipeline_job`.
- **Pipeline auth:** DB DSN inside `pipeline.env` (mode 0640, owner pod); no API auth on the pipeline itself.
- **Publish path (Fourthwall):** `_publish` → skip if `fw_product_id` already set → `route.upload is None` ⇒ `draft` → `get_fw_credentials` (per-tenant pgp decrypt, else env fallback) → **`None` ⇒ `publish_state=draft`, `last_error="no Fourthwall credentials configured"`, return without raising** → `fourthwall_template_id` missing ⇒ `publish_state=failed` + `PipelineError` → upload image → `create_design_product(publish_on_create=False)` → optional `set_state(PUBLIC)` when `auto_publish`. Honest-refusal design: no fabricated publish.
- **Current blocker on the publish path:** `config/products.json` still has `"fourthwall_template_id": "REPLACE_WITH_TEMPLATE_ID"` for all 5 product types, so every route would fail at `_publish` even with working craft steps. Download artefacts exist (`config/fourthwall-product-templates.json` 408 640 B, `fourthwall-template-details.json` 1 680 050 B, `fourthwall-template-details.csv` 1 077 318 B) but are not wired into `products.json`. `VERIFIED` (values printed from `products.json`; note the Fourthwall *credentials* env names are set, so the "no credentials" branch would not fire — the template-id branch would).

---

## 8. VPS capacity (VERIFIED, 2026-11-05T16:06:44Z)

| Resource | Value | Command |
|---|---|---|
| Host / virt | `srv2108523`, `kvm`, `Linux 7.0.0-38-generic #38-Ubuntu SMP PREEMPT_DYNAMIC Fri Sep 4 09:10:14 UTC 2026 x86_64` | `uname -a`, `systemd-detect-virt` |
| OS | `Ubuntu 26.04.1 LTS (Resolute Raccoon)`, `VERSION_ID=26.04` | `cat /etc/os-release` |
| CPU | **2 vCPU**, `AMD EPYC 9354P 32-Core Processor` (host model) | `nproc`, `/proc/cpuinfo` |
| Load | `0.26 0.61 0.60`, `1/444` procs | `uptime`, `/proc/loadavg` |
| RAM | total **7 935 MB**, used 3 076, free 2 373, buff/cache 2 860, **available 4 859** | `free -m` |
| Swap | total **4 095 MB**, **used 2 532**, free 1 563 | `free -m` |
| Disk `/` | `/dev/sda1` **96 G, 61 G used, 36 G avail, 63 %** | `df -h` |
| Inodes | 12 418 560 total, 1 177 053 used, **10 %** | `df -i` |
| Top RSS | `next-server` 19.5 % MEM / 24.4 % CPU, `dockerd` 8.2 % | `ps -eo pmem,pcpu,comm` |
| Uptime | `up 7 days, 1:26`, 2 users | `uptime` |
| Public IP | `179.197.88.181`; interfaces `172.17.0.1 172.18.0.1 172.19.0.1 172.20.0.1 192.168.200.1 + /64 IPv6` | `hostname -I`, ipify |

`/opt` footprint (VERIFIED `du -sh /opt/*`): `craft` **759 M**, `pod-pipeline` **451 M**, `deerflow-forge` **450 M**, `deer-flow` **235 M**, `node22` **203 M**, `uv-python` **110 M**, `containerd` 12 K.

**Free-capacity conclusion.** Headroom for an agent process is thin but real: ~4.8 GB available RAM against an already-swapped host, ~36 GB disk. Reclaimable today without touching live services: **24.55 GB** of images (71 images, only 8 active — 46 `ridgeboundia-app/migrate` tag pairs) + **10.06 GB** build cache. `INFERRED`.

---

## 9. Services and ports

| Unit / container | State (verified) | Bind | Notes |
|---|---|---|---|
| `pod-mcp.service` | `enabled` / `active` since 06:00:19 UTC, `NRestarts=0` | `0.0.0.0:8765` (python pid 74443) | `User=pod`, `SupplementaryGroups=docker`, `EnvironmentFile=/opt/pod-pipeline/config/pipeline.env` |
| `pod-worker.timer` | `enabled` / `active` | — | `OnBootSec=45`, `OnUnitActiveSec=60`; next run 27 s after probe |
| `pod-worker.service` | `static` / `oneshot` (`inactive` between runs) | — | `--drain --scan`; last: `drained 0 run(s), 0 failed` |
| `deerflow-forge-console.service` | `enabled` / `active` | `127.0.0.1:8091` (node pid 248604) | `User=forge`, `ProtectSystem=full`, `PrivateTmp=true` |
| `docker.service` / `containerd` | `enabled` / `active` | `0.0.0.0:22,80,443` + loopback | Docker 29.9.2, Compose v5.6.1 |
| `pod-postgres` (container) | `Up 11 hours (healthy)`, `restarts=0` | `127.0.0.1:5432` | `postgres:16` → server 16.15, DB `pod`, 8 127 kB, `mem_limit 1g`, `cpus 0.75`, volume `pgdata` |
| `deer-flow-gateway` | `Up 11 hours` | internal `8001`, net `192.168.200.4` | DeerFlow 2.2.0 backend, `DEEPSEEK_API_KEY` = `<set>` |
| `deer-flow-frontend` | `Up 14 hours` | internal `3000` | Next.js |
| `deer-flow-nginx` | `Up 14 hours` | `80/tcp`, `127.0.0.1:2026` | `nginx:1.31.2-alpine` |
| `deer-flow-redis` | `Up 14 hours (healthy)` | internal `6379` | `redis:7-alpine` |
| `ridgeboundia-app` / `-postgres` / `-caddy` / `-dev-pg` | running (app+caddy healthy) | `0.0.0.0:80,443` (caddy), `127.0.0.1:5433` (dev-pg) | separate product, `www.ridgeboundia.com` |
| `nginx` *systemd unit* | **not-found** | — | nginx runs only as the DeerFlow container |
| `postgresql@16-main` *systemd unit* | **not-found** | — | Postgres runs only as a container |
| `systemctl --failed` | **0 loaded units** | — | — |

Listening sockets (`ss -lntp`, VERIFIED): `127.0.0.1:65529` monarx-agent, `127.0.0.1:8091` node (console), `127.0.0.54:53`/`127.0.0.53:53` systemd-resolve, `127.0.0.1:2026` docker-proxy, `127.0.0.1:5433` docker-proxy, `127.0.0.1:5432` docker-proxy, `0.0.0.0:443` docker-proxy, `0.0.0.0:22` sshd, `0.0.0.0:80` docker-proxy, **`0.0.0.0:8765` python (pod MCP)**, `[::]:443/22/80`. UDP: `:53`, `127.0.0.1:323` chronyd, `127.0.0.1:1721` monarx-agent.

`ufw status verbose`: `active`, default **deny (incoming)**, `allow 22/80/443`, and only `172.16.0.0/12` + `192.168.200.0/24` → `8765/tcp` (`# DeerFlow Forge MCP from docker networks`).

Loopback health probes (`curl`): `http://127.0.0.1:8765/health` → **200** `{"ok":true}`; `POST /` `tools/list` → 3 tools; `http://127.0.0.1:8091/` → **200**; `http://127.0.0.1:80/` → **308** (caddy redirect). From inside the gateway: `curl http://172.17.0.1:8765/health` → **200**, `tools/list` → works.

---

## 10. Craft installation inventory

| Item | Value | Evidence |
|---|---|---|
| VectorCraft | `0.21.1`, extracted at `/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/` (271 M), binary `bin/vectorcraft-cli` + `bin/vectorcraft` | `VERIFIED` `--version` |
| PhotoCraft | `0.20.2 (7c12f6471, 2026-11-05)`, `/opt/craft/photocraft/photocraft-0.20.2-linux-x86_64/` (229 M) | `VERIFIED` `--version` |
| DesignCraft / EffectCraft / FilmCraft | **NOT INSTALLED** — no binary anywhere (`find / -xdev -maxdepth 4`, `find /opt /usr/local /root -maxdepth 6`) | `VERIFIED` |
| Archives | `/opt/craft/pkg/vectorcraft-0.21.1-linux-x86_64.tar.gz` 143 222 440 B, `photocraft-0.20.2-linux-x86_64.tar.gz` 126 621 245 B | `ls -la` |
| Command catalogues | `vectorcraft-commands.json` — JSON list, **918** entries, keys `enabled,id,label,menu,params,shortcut`; `photocraft-commands.json` — **965** lines of tab-separated text (despite `.json`; `json.load` fails) | `VERIFIED` |
| Rust source/docs | `/opt/craft/artcraft-docs/` (1 000 K): `mcp.md` 633 439 B, `image-trace-quality.md` 194 159 B, `development.md` 68 455 B, `architecture.md`, `src/{lib,logo,params,pipeline,quantize,smooth}.rs` | `ls -la` |
| Ownership | `/opt/craft` root:root 755; binaries `UNKNOWN:UNKNOWN` (uid 1001) 755 — **world-executable**, and `su pod -c '<vc> --version'` succeeds | `VERIFIED` |
| Catalogue freshness | live `vectorcraft-cli commands` → **918** entries (JSON list) and `photocraft-cli commands` → **965** lines — the archived catalogues are current, not stale copies | `VERIFIED` |
| Checksum manifest | **none** (`find /opt/craft -maxdepth 3` for `*.sha256|*.sha256sum|SHA256SUMS*|*.sig|checksums*` → empty) | `VERIFIED` |
| GPU | **none** — `/dev/dri` does not exist; no nvidia/amdgpu/i915 modules | `VERIFIED` |
| Java/py prerequisites | ffmpeg, ffprobe, convert (ImageMagick), identify, potrace, Xvfb, xvfb-run **present**; `glxinfo` absent; no GPU | `VERIFIED` `command -v` |

`vectorcraft-cli --help` (READ, live) documents three agent-relevant modes: `mcp [--connect ADDR | --headless] [--automation-read-root DIR] [--automation-write-root DIR]`, `run [--in FILE] [--cmd ID [--params JSON] | --commands FILE|-] [--export FILE] [--scale N]`, `commands` (prints the catalogue), `convert IN OUT …`. `photocraft-cli --help` documents `convert, info, run, batch, droplet, commands, mcp, serve, help` — note **no `--input`/`--out-dir`/`--trim-alpha` flags**.

---

## 11. Persistence and state audit

| Item | State | Evidence |
|---|---|---|
| `pod` DB rows | all five tables **0 rows** | `psql -Atc` union count |
| `pod` DB size / version | 8 127 kB / PostgreSQL **16.15** (Debian 16.15-1.pgdg13+2) | `psql` |
| `pod-postgres` health | `healthy`, `restarts=0` | `docker inspect` |
| Stale run artefacts | `sandbox/a7e58e17-…/input.png` 872 B (kept for a failed run), `build/a7e58e17-…/` empty, `logs/jobs/a7e58e17-…/01-vector_trace-t0-a1.log` 94 B = the stub's "vendor binary not installed" line | `find`, `ls -la`, `cat` |
| `mcp-spawn.log` | **absent** — no MCP-triggered spawn has happened since the last reset | `tail` → "No such file or directory" |
| `data/` | 119 M (inbox + ingested sources) | `du -sh` |
| DeerFlow state | `backend/.deer-flow/data/deerflow.db` 45 tables; **checkpoints 1163**, runs 0, run_events 0, agents 0, mcp_tasks 0, projects 0; `users/default/threads/{1f6fb8ef…,c4e9b80b…,6b471e9b…}` | sqlite `mode=ro` |
| DeerFlow memory index | `.retrieval/memory-fts5.sqlite3` (+ `-wal`, `-shm`) present | `ls` |
| Console build | `.output/server/index.mjs` 37 852 B, 2026-11-05 08:39; `.output/{nitro.json, public, server}` | `ls -la` |
| Job-log retention | no rotation policy found; only `logrotate.timer` system-wide | `systemctl list-timers` |

---

## 12. Deployment sync state

| Component | Installed | Deployed from | Sync proof | Drift |
|---|---|---|---|---|
| Pipeline | `/opt/pod-pipeline` (owner `forge:forge`; `.venv` `pod:pod` 3.12.16) | `cp -a /opt/deerflow-forge/blueprint/files/.` | **No `.git`** (`fatal: not a git repository`). 26/26 sha256 match local working tree, incl. `pod_pipeline/*.py` (12), `sql/schema.sql`, `deploy/*` (8), `config/{pipeline.env.example,products.json}`, `requirements*.txt`, `pytest.ini` | `diff -rq` found only `__pycache__`, `bin`, `skills` (not deployed), and `tools/artcraft.py` + `tools/craft_trace.py` **differ** (VPS copies are pre-`7ff65b5`/`bff0290` versions) |
| Console | `/opt/deerflow-forge` (owner `forge:forge`) | `git clone https://github.com/RodneyDanger1/DeerFlow-Forge` | `HEAD = 32fc71f1552bc623f4fc9636228c5cabd178be59`, `2026-11-05T02:39:38-06:00`, tree clean | **9 commits behind** local `d9dc2fe` (skills/docs/tools only — `git diff --stat 32fc71f..HEAD` touches `blueprint/files/skills/**`, `tools/artcraft.py`, `tools/craft_trace.py`, `research/**`, no `pod_pipeline/`) |
| Craft | `/opt/craft` (root, uid 1001 payloads) | manual extract of vendor tarballs | `--version` strings | vectorcraft 0.21.1 / photocraft 0.20.2 only |
| DeerFlow | `/opt/deer-flow` (root), containerised | `docker/docker-compose-dev.yaml` (compose project `deer-flow-dev`, running 4) | `git log -1 = 58fc5bd…`, tree has 2 untracked (`_audit_prompt.txt`, `extensions_config.json.bak-before-forge-mcp`) | backend `pyproject.toml version = "2.2.0"` |

Runtimes: system `Python 3.14.4`; pod venv `3.12.16` (via `uv` into `/opt/uv-python`, which is why root's `PATH` has no `uv`); `node v22.23.4` (`/opt/node22`); `git 2.53.0`; Docker Compose `v5.6.1`; **no `psql` client** on the host (use `docker exec pod-postgres psql`). Pod venv packages include `asyncpg 0.32.0, httpx 0.28.1, pillow 13.0.0, numpy 2.5.4, scipy 1.18.1, scikit-image 0.26.0, scour 0.38.2, pytest 9.2.0, pytest-asyncio 1.4.1.post1` — note `psycopg` is **not** installed (expected; the code uses asyncpg).

---

## 13. Environment variable names (NAMES ONLY — no values)

`/opt/pod-pipeline/config/pipeline.env` (mode 0640, `pod:pod`), 20 names, all non-empty:

`POD_ROOT`, `PYTHONPATH`, `DATABASE_URL`, `POD_DB_PASS`, `POD_CREDENTIAL_KEY`, `FW_BASE_URL`, `FW_API_USER`, `FW_API_SECRET`, `POD_USE_DOCKER`, `POD_DOCKER_IMAGE`, `POD_DOCKER_MEMORY`, `POD_DOCKER_CPUS`, `POD_DOCKER_CPU_SHARES`, `POD_NICE_LEVEL`, `POD_MAX_CONCURRENCY`, `POD_STEP_TIMEOUT_S`, `POD_FALLBACK_RASTER_DPI`, `POD_MCP_HOST`, `POD_MCP_PORT`, `POD_LOG_LEVEL`.

Non-secret values only (safe to publish): `POD_ROOT=/opt/pod-pipeline`, `FW_BASE_URL=https://api.fourthwall.com`, `POD_USE_DOCKER=0`, `POD_DOCKER_IMAGE=pod-craft-runner:latest`, `POD_MAX_CONCURRENCY=2`, `POD_MCP_HOST=0.0.0.0`, `POD_MCP_PORT=8765`.
`DATABASE_URL` shape only: `scheme=postgresql host=127.0.0.1 port=:5432 db=pod userinfo=<redacted>` (len 88).
Secrets, presence only: `POD_DB_PASS=<set>`, `POD_CREDENTIAL_KEY=<set>`, `FW_API_USER=<set>`, `FW_API_SECRET=<set>`.
**`DEEPSEEK*` names in this file: none** (`grep -c -i deepseek` → `0`).

`docker inspect deer-flow-gateway` env **names** (values never read): `AUTH_TRUSTED_PROXIES, CI, DEEPSEEK_API_KEY, DEER_FLOW_CHANNELS_GATEWAY_URL, DEER_FLOW_CHANNELS_LANGGRAPH_URL, DEER_FLOW_CONFIG_PATH, DEER_FLOW_CREDENTIALS_KEY, DEER_FLOW_EXTENSIONS_CONFIG_PATH, DEER_FLOW_HOME, DEER_FLOW_HOST_BASE_DIR, DEER_FLOW_INTERNAL_AUTH_TOKEN, DEER_FLOW_PROJECT_ROOT, DEER_FLOW_SANDBOX_HOST, DEER_FLOW_STREAM_BRIDGE_REDIS_URL, EXA_API_KEY, EXA_BASE_URL, GPG_KEY, INFOQUEST_API_KEY, JINA_API_KEY, LANG, LC_ALL, NO_PROXY, PATH, PROVISIONER_API_KEY, PYTHONIOENCODING, PYTHON_SHA256, PYTHON_VERSION, SERPER_API_KEY, SERPER_BASE_URL, SERPLY_API_KEY, SOFYA_API_KEY, TAVILY_API_KEY, UNBROWSE_API_KEY, no_proxy`.
Provider-key names present (all `<set>`, values never printed): `DEEPSEEK_API_KEY`, `TAVILY_API_KEY`, `INFOQUEST_API_KEY`, `EXA_API_KEY`, `SERPER_API_KEY`, `PROVISIONER_API_KEY`, `JINA_API_KEY`, `DEER_FLOW_CREDENTIALS_KEY`, `SOFYA_API_KEY`, `DEER_FLOW_INTERNAL_AUTH_TOKEN`, `UNBROWSE_API_KEY`, `SERPLY_API_KEY`.
Non-secret provider values that exist: only `EXA_BASE_URL` and `SERPER_BASE_URL` (URL endpoints, not keys). **No** `DEEPSEEK_MODEL` / `DEEPSEEK_BASE_URL` env name exists — the model comes from `config.yaml`.

---

## 14. Tests (counts read, not executed by me)

| Suite | Count | Status |
|---|---|---|
| Pipeline `blueprint/files/tests/` | **48** `test_*` functions across 8 files: `test_prep_print_art` 13, `test_mcp_jsonrpc` 11, `test_pipeline_integration` 4, `test_craft_trace` 5, `test_db_contracts` 5, `test_routes` 7, `test_mcp_spawn` 2, `test_artcraft_fixes` 1 | `READ` (regex count) |
| Pipeline cached result | `.pytest_cache/v/cache/lastfailed` = `{}` locally **and** on the VPS; `nodeids` 2 385 B (local) / 4 131 B (VPS) | `VERIFIED` file content |
| Console | `scripts/**/*.test.mjs` + 5 TS test files (`app-data`, `readiness-schedule`, `gate-identity`, `sign-in-gate`, `preview-path-prefix`) | `READ` `package.json` |
| README claim | "31 tests on the VPS against containerised PostgreSQL (27 pure, 4 integration)"; "207 JS tests (205 pass, 2 skipped)" | `READ` `README.md:184-190` — **not re-run here**; treat as `UNVERIFIED` for today's state |

I deliberately did **not** run `pytest`/`npm test`: both write caches (`.pytest_cache`, `node_modules/.vite`) and the integration suite `<redacted> DROP/CREATE DATABASE pod_test` on the live Postgres — outside a read-only mandate.

---

## 15. Exact gaps for hosting a Craft-driving agent on this VPS

Ordered by blocking severity. Each is a concrete, verifiable missing piece — not a wish.

1. **No executable craft step in the pipeline.** `GAP-BIN` — 5 stubs at `/opt/pod-pipeline/bin/*-cli` (122–124 B, `exit 127`). Fix requires real launchers; ownership is `pod:pod`, perms 755, so a root `install`/symlink is needed.
2. **Three of five craft tools do not exist on the host.** `GAP-TOOLS` — DesignCraft, EffectCraft, FilmCraft are absent. Routes `knitwear` (designcraft), `accessories` (designcraft), `odd_3d` (designcraft+effectcraft), `stationery` (designcraft+filmcraft), `apparel` (photocraft+effectcraft) are each blocked by at least one missing binary. Only the trace stage (vectorcraft) and the raster fallback (photocraft) could run today.
3. **The pipeline's argv contract is wrong for the real CLIs.** `GAP-ARGV` — `vectorcraft-cli trace` is not a subcommand; `photocraft-cli` accepts no `--input/--trim-alpha/--target-dpi/--out-dir`. Real surfaces are `run --in/--cmd/--commands/--export`, `convert IN OUT`, `commands`, `mcp`, `serve`, `batch`, `droplet`, `info`. `routes.py` needs rebuilding against `vectorcraft-commands.json` (918 ids) / photocraft's 965-entry registry.
4. **No agent has craft MCP registered.** `GAP-MCP` — DeerFlow's `extensions_config.json` has only `forge`. Both installed CLIs expose `mcp` (stdio). Registering requires a stdio-server entry (`command` + `args` + automation read/write roots) and a container-visible path, since the CLIs live on the **host**, not in the gateway image.
5. **Docker/host path isolation for craft.** `GAP-PATH` — craft binaries and `/opt/craft/artcraft-docs` are host paths; the gateway runs in a container with no bind mount for them (`docker inspect` shows no `/opt/craft` mount). `POD_USE_DOCKER=0` on this host, so craft runs as host processes under user `pod` (world-executable binaries — verified `su pod -c … --version` works).
6. **Headless-only, no GPU, no display.** `GAP-GUI` — `Xvfb`/`xvfb-run` installed but `glxinfo` absent and no GPU; `QT_QPA_PLATFORM=offscreen` is forced by `runner._env`. Any GUI-critic / screenshot-the-window workflow cannot run as-is; only the headless MCP/`run` modes are viable.
7. **No durable Craft-run state model.** `GAP-STATE` — `processing_jobs` has no craft-document, command-id, or revision columns; `agent_sync_logs` is the only agent-visible ledger and carries no artefact lineage. Craft's own MCP resources (`vectorcraft://object/{id}`) would need mirroring into Postgres for replay.
8. **No learning loop.** `GAP-LEARN` — no episode/skill/eval tables, no promotion or rollback path, no token ledger. The `craft-agent-operator` SKILL + `references/{memory-ledger,evaluation}.md` describe the loop; nothing implements it.
9. **No cost/usage control for the model.** `GAP-COST` — `deerflow.db` has no token/usage table; `config.yaml` has `token_budget`/`token_usage` keys but no evidence they persist per-call data.
10. **Console is a viewer only.** `GAP-CONSOLE` — no write API, no auth (`VITE_AUTH_ENABLED=false`), no job controls. Any operator UI for the agent must be new.
11. **Deployment is copy-based.** `GAP-SYNC` — `/opt/pod-pipeline` has no git remote or `.git`; refresh = `cp -a`, so "what is deployed" can only be answered by hashing. Two `tools/*.py` files already diverge from the deployed console checkout.
12. **Publish path cannot complete today.** `GAP-PUBLISH` — `products.json` template ids are `REPLACE_WITH_TEMPLATE_ID` (all 5). Fourthwall creds env names **are** set, so this is a config-data gap, not a credential gap.
13. **`AGENTS.md` at repo root is a foreign contract.** `GAP-DOC` — it documents a Grok `/workspace` sandbox (port 8080, `startup.sh`, Vercel), not this VPS. It will mislead any agent that reads it as project rule.

---

## 16. Security and operations risks

| # | Risk | Evidence | Severity |
|---|---|---|---|
| R1 | **Unauthenticated MCP on `0.0.0.0:8765`** — anyone able to reach the port can enqueue runs (`trigger_pipeline_job`) that later execute craft binaries as user `pod` (member of group `docker`). Only `ufw` source ranges limit it. | `ss -lntp`, `ufw status`, `mcp_server.py` (no auth) | High |
| R2 | `pod` user is in the **docker** group (`SupplementaryGroups=docker`) ⇒ effectively root-equivalent on the host if a craft binary or MCP call is compromised. | `systemctl cat pod-mcp`, `id pod` | High (structural) |
| R3 | **32.26 GB** of Docker images (76 % reclaimable) + **15.38 GB** build cache on a 96 GB disk; 63 % used. Disk pressure is the most likely outage vector. | `docker system df`, `df -h` | Medium |
| R4 | **Swap already at 2.5/4.0 GB** with only 7.9 GB RAM and a 19.5 %-RSS Next.js app. Adding an agent + headless DCC-style renderer risks OOM. | `free -m`, `ps` | Medium |
| R5 | Historical `pod-mcp` failure loop: `Failed to execute /opt/pod-pipeline/.venv/bin/python: Permission denied` (05:18) caused by `uv`-installed Python under `/root` (0700). Fixed via `UV_PYTHON_INSTALL_DIR=/opt/uv-python`; the same trap will recur on re-provision. | `journalctl -u pod-mcp`, `setup-pipeline.sh:78-90` | Medium |
| R6 | Historical console crash loop: `Cannot find module '/opt/deerflow-forge/.output/server/index.mjs'` (07:40) — unit starts before the build exists; `install-console.sh` installs the unit *before* building (`README.md` order) but the shipped unit has `Restart=on-failure` with no build guard. | `journalctl -u deerflow-forge-console` | Low |
| R7 | Three deployments share one host with overlapping bind ports: caddy owns `0.0.0.0:80/443`; `deer-flow-nginx` binds `80/tcp` only inside its bridge; `ridgeboundia-*` and `pod-*` both run Postgres (5432 vs internal 5433). A careless compose change can collide. | `docker ps`, `ss` | Medium |
| R8 | Secrets live in a 0640 `pipeline.env` plus container env (`DEEPSEEK_API_KEY`), i.e. readable by group `pod` and by any `docker inspect` caller. No vault, no rotation evidence. | `ls -la config/`, `docker inspect` names | Medium |
| R9 | Unauthenticated loopback console on 8091 leaks source of `pod_pipeline/*` and deploy units to anyone with an SSH tunnel — acceptable risk today, but it exposes infrastructure detail. | `curl 8091` 200, `sources.ts` `?raw` imports | Low |
| R10 | Craft binaries are owned by **uid 1001 (UNKNOWN)** — not mapped to any local account, so ownership/permission changes need root and the installer identity is untracked. | `stat -c '%U:%G'` | Low |
| R11 | `/opt/craft/pkg` keeps 258 M of tarballs and `/opt/craft` 759 M total without checksum manifest; reproducibility of the installed versions depends on those archives. | `du -sh`, no `.sha256` found | Low |
| R12 | `photocraft-commands.json` is **not JSON** despite the name (tab-separated text). Any agent parsing catalogues by extension will fail; the repo's own atlas (`references/catalogues/*.json`) should be preferred. | `file`, `json.load` error | Low (data-quality trap) |

---

## 17. Gaps in this audit (probe-level, stated honestly)

- **No failed probes.** SSH worked on the first attempt (`BatchMode` with `~/.ssh/id_ed25519_hostinger`); every listed probe returned data. `systemctl --failed` → 0 units.
- `UNVERIFIED` **Key validity / a live DeepSeek call.** I did not call the provider (would spend the owner's quota and is not read-only). Evidence for existence of agent turns is the 1 163 checkpoints; evidence for a current working call path is absent (`runs` 0, gateway log has no `deepseek` line).
- `UNVERIFIED` **Test results today.** Caches say `lastfailed = {}` but the suite was not executed; README numbers were not reproduced.
- `UNVERIFIED` **Console test counts** (207 / 205+2 skipped) — `npm test` not run (writes caches).
- `UNVERIFIED` **External reachability of 8765.** I verified the socket and the `ufw` rules but cannot prove closure from outside the host without an off-host probe. `README.md:173-174` claims it was verified previously.
- `UNVERIFIED` **Whether `designcraft/effectcraft/filmcraft` exist anywhere else** (e.g. a private artifact store) — only proven absent on this host filesystem.
- `UNVERIFIED` **The exact `langchain_deepseek` default base URL**; only inferred from the library import (`patched_deepseek.py:18`) since no `base_url` is configured anywhere readable.
- `INFERRED` (not directly measured): the "reclaimable disk = ~34.6 GB" figure combines `docker system df` image + build-cache reclaimables; I did not run `prune`.

---

## 18. Fifteen candidate questions for the 200-question corpus

Each is answerable from this audit's evidence and tests a distinct fact.

1. Which two systemd units keep the DeerFlow Forge pipeline alive on the VPS, and does the worker unit stay running between ticks? (`pod-mcp.service` active; `pod-worker.timer` every 60 s; `pod-worker.service` is `static`/`oneshot`.)
2. What exactly does a pipeline run do when `/opt/pod-pipeline/bin/vectorcraft-cli` exits 127 — does it retry, fall back, or fail? (Fails at the trace stage; `exit 127` is **not** in `TRANSIENT_EXIT_CODES`, so no retry; no raster fallback because fallback only triggers on exit code 1.)
3. Which of the five product routes could execute today if the stubs were replaced with the two installed CLIs? (`apparel` up to `effectcraft_distress`; all others need an absent binary.)
4. Why does `photocraft-cli: error: unexpected argument '--input' found` matter to the blueprint's correctness claim? (`routes.py` contracts are flagged `ASSUMPTION` and are verifiably wrong against 0.20.2.)
5. How is a pipeline job prevented from running twice if an agent calls `trigger_pipeline_job` twice? (Partial unique index `processing_jobs_one_live_run`; `enqueue_run` returns the existing `run_id` with `created:false`.)
6. What is the exact SQL claim mechanism that lets the MCP-spawned worker and the 60-second timer drain coexist? (`UPDATE … WHERE id = (SELECT … FOR UPDATE SKIP LOCKED LIMIT 1)`.)
7. Which failures are retried and which are not? (`transient` = timeout or exit ∈ {-9,-15,137,143,75}; validation failures carry `exit_code=0` and are never retried.)
8. How does the pipeline prove an output file is durable before publishing it? (`flush_to_disk`: stable signature ×2, `fsync(file)`, `fsync(parent dir)`.)
9. What is the database state of the deployed pipeline right now, and what does that imply about "verified end-to-end" claims? (All five tables 0 rows; 8 127 kB schema-only.)
10. Which craft tool exposes an MCP server that could replace the stubs, and what tool names does it advertise? (VectorCraft `mcp --headless`, `serverInfo{name:"vectorcraft",version:"0.21.1"}`; command/doc/draw tools.)
11. Which environment variable names does the pipeline use, and which DeepSeek variables are **absent** from it? (20 `POD_*`/`FW_*`/`DATABASE_URL` names; zero `DEEPSEEK*`.)
12. Where does the DeepSeek model actually get configured, and what are its declared limits? (`/opt/deer-flow/config.yaml:18-37` — `deepseek-flash`, 1 048 576 context, 8 192 max_tokens, 600 s timeout, `max_retries: 2`.)
13. Is the deployed pipeline a git checkout, and how was byte-equality proven? (No `.git`; 26/26 sha256 matches against the local working tree.)
14. What are the capacity numbers that bound an added agent process? (2 vCPU, 7.9 GB RAM / 2.5 GB swap used, 36 GB free, 0.26 load.)
15. What makes an unauthenticated `0.0.0.0:8765` MCP port materially risky here, beyond a missing token? (The `pod` service user is in the `docker` group, so a triggered craft binary runs with host-root-equivalent reach.)

---

## 19. Commands run (redacted, grouped)

Local (PowerShell, read-only):
`Get-ChildItem -Recurse` (repo/blueprint/deploy/research), `Get-Content` (README.md, AGENTS.md, package.json, blueprint/files/**, deploy/vps/*), `Select-String` (LLM refs, test defs), `Get-FileHash -Algorithm SHA256` (26 blueprint files), `git rev-parse HEAD`, `git log -1`, `git status --porcelain`, `git log --oneline 32fc71f..HEAD`, `git rev-list --count`, `git diff --stat`, `git show HEAD:.grok/app-env.json`.

Remote (SSH `root@179.197.88.181`, batch mode; scripts piped as base64-decoded bash to avoid CRLF mangling):
`uname -a`, `cat /etc/os-release`, `uptime`, `date -u`, `nproc`, `grep -m1 "model name" /proc/cpuinfo`, `free -m`, `df -h`, `df -i`, `cat /proc/loadavg`, `systemd-detect-virt`, `systemctl --failed`, `systemctl is-enabled/is-active <unit>`, `systemctl list-unit-files | grep -Ei 'pod|deer|craft|nginx|postgres|docker|caddy'`, `systemctl cat <unit>`, `systemctl show pod-mcp -p …`, `systemctl list-timers --all`, `journalctl -u <unit> --since '-7 days' [-n N]`, `journalctl --since '-7 days' | grep -Ei 'oom|out of memory|no space left'`, `docker ps/images/system df/version/network ls/network inspect/port/compose ls/inspect -f`, `ss -lntp`, `ss -lunp`, `ufw status verbose`, `ls -la /opt /opt/pod-pipeline /opt/craft /root`, `du -sh /opt/* /opt/pod-pipeline/{data,build,logs,sandbox,bin} /opt/craft/*`, `find` (craft binaries, deer-flow state, `-maxdepth`/`-xdev` guarded), `sha256sum` × 26 on `/opt/pod-pipeline`, `diff -rq` (blueprint vs deployed), `git -C /opt/{pod-pipeline,deerflow-forge,deer-flow} rev-parse HEAD|log -1|status --porcelain|remote -v`, `python3 -V`, `/opt/pod-pipeline/.venv/bin/python -V`, `pip list`, `npm/node --version`, `uv --version` (not found), `git --version`, `docker compose version`, `psql --version` (not found), `stat -c`, `id pod|forge`, `su -s /bin/sh pod -c …` (version + docs read), `systemd-analyze` — n/a, `curl -sS -m N [-o /dev/null -w …] http://127.0.0.1:{8765/health,8765/,8091/,80/}` and `curl -X POST … tools/list`, `docker exec postgres psql -U pod_app -d pod -Atc "select …"` (counts, version, size, group-bys, `left(last_error,90)`), `sqlite3` via `python3` with `file:…?mode=ro` (table list, counts, checkpoint columns), `head/sed/wc/file` on `/opt/deer-flow/config.yaml`, `extensions_config.json` (Python walk that redacts `*token*|*key*|*secret*|*pass*`), `artcraft-docs/mcp.md`, catalogues; `vectorcraft-cli --version|--help|mcp --headless` (JSON-RPC `initialize`+`tools/list` over stdio), `photocraft-cli --version|--help|mcp --help|commands|symbolic wrong-flag probe`, `command -v` for Xvfb/xvfb-run/glxinfo/ffmpeg/ffprobe/convert/identify/potrace.

Secret handling: every credential value was read as a **name only** (`cut -d= -f1`) or as length/`<set>` metadata; `DATABASE_URL` was reduced to `scheme/host/port/db` with `userinfo=<redacted>`; the only non-secret values printed are `POD_ROOT`, `FW_BASE_URL`, `POD_USE_DOCKER`, `POD_DOCKER_IMAGE`, `POD_MAX_CONCURRENCY`, `POD_MCP_HOST`, `POD_MCP_PORT`, plus `EXA_BASE_URL`/`SERPER_BASE_URL` names. No secret value appears in this document or in the companion JSON.

---

## 20. Source index

- Repo: `README.md`, `AGENTS.md`, `package.json`, `.grok/app-env.json`, `src/components/forge/console.tsx:43`, `src/lib/blueprint/sources.ts:1-5`
- Pipeline: `blueprint/files/pod_pipeline/{config,db,mcp_server,orchestrator,routes,runner,validators,worker}.py`, `blueprint/files/sql/schema.sql`
- Deploy: `blueprint/files/deploy/{compose.yml,setup-pipeline.sh,mcp-stdio.mjs,Dockerfile,craft-bin/*,systemd/*}`, `deploy/vps/{install-console.sh,deerflow-forge-console.service}`
- Config: `blueprint/files/config/{pipeline.env.example,products.json}`
- Host: `/opt/pod-pipeline/**`, `/opt/craft/**`, `/opt/deer-flow/{config.yaml,extensions_config.json,backend/pyproject.toml,logs/*}`, `/etc/systemd/system/{pod-mcp.service,pod-worker.service,pod-worker.timer,deerflow-forge-console.service}`
- Machine-readable companion: `research/eko-deerflow-agent/wave2/01-VPS-FACTS.json`
