# DeerFlow Forge

An architecture console and deployable reference package for a **print-on-demand
asset pipeline**: ingest → vector trace → raster/composite → grid + typography →
effects → motion. It is designed to be orchestrated by **DeerFlow 2.2** and synced to a
**Fourthwall** storefront; the local checkout and this session run the console/Forge code
under **DeepSeek Harness**, and **DeerFlow registration is not applied**.

The repository has two halves:

| Path | What it is |
|---|---|
| `src/`, `public/`, `scripts/`, `server/` | The **console** — a TanStack Start + Vite + React 19 app that renders the blueprint: board, routes, sandbox, playbook, and source browser. |
| `blueprint/files/` | The **deployable package** — Python `pod_pipeline`, Postgres schema, Docker Compose, systemd units, MCP bridge, craft CLI shims, and the real test suite (some integration tests require their named services). |
| `attachments/` | The original provided pipeline modules the blueprint was fitted to (`config.py`, `db.py`, `fourthwall.py`, `orchestrator.py`, `routes.py`, `runner.py`, `worker.py`, `validators.py`, `logfilter.py`, `ingest.py`, `craft_stub.py`, `conftest.py`). |
| `migrations/` | SQL migrations applied by `npm run build` when `DATABASE_URL` is set. |
| `.grok/references/` | Workspace contract captured from the original sandbox — kept for traceability. |

## Console

```bash
npm ci
npm run dev        # http://localhost:8080
```

Gates (run individually; current result):

```bash
npm run typecheck  # exit 0
npm run lint       # exit 0, 0 errors / 5 pre-existing warnings
npm run test       # 65/65
npm run build      # vite build, then db:migrate (skips without DATABASE_URL)
```

The console is a **pure viewer**: `src/lib/blueprint/sources.ts` imports the
pipeline files with Vite's `?raw`, so the built app has no runtime filesystem
dependency. That makes it cheap to host anywhere Node runs.

### Self-hosting on a VPS (not Vercel)

The build defaults to Nitro's `vercel` preset. For a plain Node host:

```bash
NITRO_PRESET=node-server npm run build
PORT=8090 HOST=127.0.0.1 node .output/server/index.mjs
```

Put Caddy/nginx in front of it, or reach it through an SSH tunnel. No secrets
are required to serve the console; `VITE_AUTH_ENABLED` is a build-time flag
(`.grok/app-env.json`) and stays `false` outside the Grok platform.


## Pipeline (VPS)

`blueprint/files/` is the deployable unit. Required configuration lives in
`blueprint/files/config/pipeline.env.example`:

| Variable | Meaning |
|---|---|
| `DATABASE_URL`, `POD_DB_PASS` | Postgres connection (Compose file provisions `postgres:16`) |
| `POD_CREDENTIAL_KEY` | At-rest credential encryption key |
| `FW_API_USER`, `FW_API_SECRET` | Fourthwall Open API credentials |
| `POD_USE_DOCKER`, `POD_DOCKER_IMAGE` | Run craft steps in the sandboxed runner image |
| `POD_MCP_HOST`, `POD_MCP_PORT` | MCP server bind address (default `127.0.0.1:8765`) |

Deploy:

```bash
cd blueprint/files/deploy
./setup-pipeline.sh          # validates env, applies schema, installs units
docker compose up -d postgres
```

### Craft binaries

`deploy/craft-launchers/vectorcraft-cli` and `photocraft-cli` are pinned absolute launchers for the
installed 0.21.1 / 0.20.2 binaries; `setup-pipeline.sh` installs them. `deploy/craft-bin/*-cli` are
named refusals for the absent DesignCraft/EffectCraft/FilmCraft engines. The pipeline fails with
`E_TOOL_NOT_INSTALLED` rather than fabricating output. `tests/stubs/craft_stub.py` is the contract
double, not a production tool.

## MCP integration with DeerFlow

`deploy/mcp-stdio.mjs` bridges DeerFlow's stdio MCP transport to the pipeline's
HTTP MCP server. It exposes three tools:

- `list_pending_assets`
- `trigger_pipeline_job`
- `get_fourthwall_status`

Run the pipeline MCP server on the VPS, then register it in DeerFlow's
`extensions_config.json` as an MCP server (`type: "http"`, url
`http://host.docker.internal:8765/`) or use the stdio bridge inside the container.

## Forge local core (not deployed)

See `docs/CAPABILITY-MATRIX.md` for the current can/cannot/unverified matrix and the truth corrections.

`blueprint/files/` also contains the local Forge control-plane modules:

| Module | Current capability |
|---|---|
| `forge_gateway.py` | typed tool-call policy, role/cmd allowlist, roots, idempotency, refusal classification |
| `sql/schema_forge.sql` | 13 tables / 36 transitions; apply-twice + 18 SQL assertions on scratch PostgreSQL 16 |
| `forge_repo.py` | asyncpg repository, job lease/finish, abandoned-after-max-attempts requeue |
| `forge_worker.py` | one claim → handler → truthful finish; bounded `LeaseReaper` |
| `forge_service.py` | loopback HTTP `/healthz`, create/get episode; repository health is required |
| `forge_verifier.py` | artifact SHA/IHDR/DPI + gate-report parser; fail-closed verdicts |
| `forge_critic.py` | blind-critic schema + gate/critic/human resolver (gate authoritative) |
| `forge_eval.py` | Wilson lower bound + golden eval + promotion **proposal** (never activates) |

None of these are installed as services; there is no production `forge` database, systemd unit, TLS,
auth, or learning loop. The Run route in the console is a blueprint visualization, not execution.

## Verification

```bash
# Console (Node 22+)
npm run typecheck && npm run lint && npm test && npm run build

# Pipeline (pure tests: no database needed)
cd blueprint/files
uv run --python 3.12 --with pytest --with pytest-asyncio --with asyncpg \
  --with httpx --with pillow -- python -m pytest tests/ -q \
  -k "not integration"

# Pipeline (integration: real PostgreSQL + Craft CLI stubs)
TEST_DATABASE_URL=postgresql://pod_app:<pass>@127.0.0.1:5432/pod_test \
  .venv/bin/python -m pytest tests/ -q

# Visual/forensic smoke: real Chrome, both viewports, screenshots in screenshots/
npm run build:vps
PORT=8090 node .output/server/index.mjs &
node scripts/visual-console-smoke.mjs http://127.0.0.1:8090
```

`npm run build:vps` clears preset-sensitive build caches before building with
the `node-server` Nitro preset. Skipping that is a real defect: `node_modules/.nitro`
keeps the previous client manifest, so the SSR HTML can reference a CSS file the
build never wrote (observed as a 404 on `/assets/styles-*.css` and an unstyled
page). CSS now uses a deterministic `assets/styles.css` name because Vite's
client and SSR passes minify it differently and would otherwise hash it
inconsistently.

## Deployment (VPS)

Both halves run on one host and never touch each other's services.

```bash
# Console: loopback on 127.0.0.1:8091, systemd unit, private Node 22 install
sudo git clone https://github.com/RodneyDanger1/DeerFlow-Forge /opt/deerflow-forge
sudo bash /opt/deerflow-forge/deploy/vps/install-console.sh

# Pipeline: /opt/pod-pipeline + Postgres container + MCP + worker timer
sudo cp -a /opt/deerflow-forge/blueprint/files/. /opt/pod-pipeline/
sudo bash /opt/pod-pipeline/deploy/setup-pipeline.sh
```

`setup-pipeline.sh` refuses to install `docker.io` over a running engine, skips
the craft-runner image unless `POD_USE_DOCKER=1`, and pins Python 3.12 through
`uv` when available (Ubuntu 26.04's 3.14 has no asyncpg/Pillow wheels yet).

Reach the console through an SSH tunnel:

```bash
ssh -N -L 8091:127.0.0.1:8091 root@<vps>
# then open http://localhost:8091
```

To let DeerFlow drive the pipeline, register the MCP server in DeerFlow's
`extensions_config.json`:

```json
{"mcpServers": {"forge": {"enabled": true, "type": "http",
  "url": "http://172.17.0.1:8765/",
  "description": "DeerFlow Forge pod pipeline",
  "session_init_timeout": 30, "tool_call_timeout": 120}}}
```

Networking notes learned on a real host:

- The gateway container sits on its own bridge (e.g. `192.168.200.0/24`), so its
  gateway IP is reachable but a service bound only to `127.0.0.1` is not.
- With `ufw` active, container-to-host traffic is dropped unless the Docker
  source ranges are allowed explicitly (published ports bypass this via DNAT,
  host sockets do not):

  ```bash
  ufw allow from 172.16.0.0/12 to any port 8765 proto tcp
  ufw allow from 192.168.200.0/24 to any port 8765 proto tcp   # deer-flow-dev bridge
  ```

- Bind `POD_MCP_HOST=0.0.0.0` and rely on those rules; verify from **outside**
  the host that the port stays closed.

The pipeline exposes `list_pending_assets`, `trigger_pipeline_job`, and
`get_fourthwall_status`; `deploy/mcp-stdio.mjs` is a stdio bridge that mirrors
the client's framing (newline-delimited or Content-Length).

## Status

**Current verified state (2026-11-05, this checkout):**

- Console: `npm test` **65/65**, `tsc --noEmit` clean, lint **0 errors / 5 warnings**, rebuilt with the
  `node-server` preset; Chrome visual smoke passes all five sections at desktop and phone widths with
  **0 console errors, 0 failed requests, 0 horizontal overflow**. A Playwright control probe passes
  **18/18** checks (tabs, model radios, run completion, sandbox open, Copy→`Copied`, Download event,
  mobile select) and a keyboard/a11y probe passes **8/8** (one h1, named controls, landmarks,
  12/12 visible Tab stops, no overflow, ≥40 px tap targets, zero runtime errors).
- Pipeline/Forge staging suite: **165 passed, 4 skipped** on a throwaway PostgreSQL 16 container with
  the G0 bundle mounted (14.55 s). The 4 skips are DB-dependent tests outside the Forge scratch DSN.
  Local Forge-only discovery: **111 passed, 9 skipped**.
- Forge local: gateway **33/33**; SQL **18/18** plus `SKIP LOCKED`; repository **4/4**; service **5/5**;
  verifier **8/8**; blind-critic contract **14/14**; real HTTP→repo→worker→reaper **2/2**.
  Wave-2 fixes add cancellable service timeout (`504 E_SERVICE_TIMEOUT`), idempotent replay
  (`200 replayed:true`), `E_REPO_SHAPE` instead of silent 404, strict POST validation, guarded
  `finish_job`, and `python -m forge_worker --once`. Evidence: `docs/TRACE/2026-11-05/GATE-FINAL-W2.md`.
- G0: independent verifier reproduced trace/retouch artifacts byte-identically; **9/9 applicable**
  gates on the regenerated trace report.
- DeerFlow MCP registration: **not applied**. No production `forge` DB, service, or storefront
  publish exists.

**Historical claims corrected:** earlier revisions claimed 207 JS tests (205 pass/2 skipped), 31
pipeline tests, a live VPS effect/publish E2E, DeerFlow client loading the Forge tools, and enabled
systemd units. Those are **HISTORICAL and not current evidence**. EffectCraft is absent and publish
templates are unset, so a full effect→publish E2E cannot be claimed from this checkout.

Windows-specific fixes in this tree: the Vite env-wrapper resolves npm `.cmd`
shims, the build script re-invokes npm through `npm_execpath`, the test script
globs correctly under `cmd`, and symlink-dependent tests skip when Developer
Mode is unavailable.

Known gaps before real pipeline traffic: absent DesignCraft/EffectCraft/FilmCraft engines (named
refusals in `craft-bin/*-cli`), Fourthwall credentials, `fourthwall_template_id` values in
`config/products.json`, and no approved production deployment. Until those exist the pipeline
refuses at the publish step with a named error rather than pretending to publish.


