# DeerFlow Forge

An architecture console and deployable reference package for a **print-on-demand
asset pipeline**: ingest → vector trace → raster/composite → grid + typography →
effects → motion, orchestrated by **DeerFlow 2.2** (DeepSeek V4.1-Flash) and
synced to a **Fourthwall** storefront.

The repository has two halves:

| Path | What it is |
|---|---|
| `src/`, `public/`, `scripts/`, `server/` | The **console** — a TanStack Start + Vite + React 19 app that renders the blueprint: board, routes, sandbox, playbook, and source browser. |
| `blueprint/files/` | The **deployable package** — Python `pod_pipeline`, Postgres schema, Docker Compose, systemd units, MCP bridge, craft CLI shims, and stub tests. |
| `attachments/` | The original provided pipeline modules the blueprint was fitted to (`config.py`, `db.py`, `fourthwall.py`, `orchestrator.py`, `routes.py`, `runner.py`, `worker.py`, `validators.py`, `logfilter.py`, `ingest.py`, `craft_stub.py`, `conftest.py`). |
| `migrations/` | SQL migrations applied by `npm run build` when `DATABASE_URL` is set. |
| `.grok/references/` | Workspace contract captured from the original sandbox — kept for traceability. |

## Console

```bash
npm ci
npm run dev        # http://localhost:8080
```

Gates (all green on Windows 11 / Node 26):

```bash
npm run typecheck  # tsc --noEmit
npm run lint       # eslint .
npm run test       # scripts/**/*.test.mjs + src/lib tests
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

`deploy/craft-bin/*-cli` are **placeholders** that exit 127 with a message. They
stand in for five vendor headless binaries (VectorCraft, PhotoCraft, DesignCraft,
EffectCraft, FilmCraft). Replace each file with the real executable (or point the
pipeline at `POD_USE_DOCKER=1` and a `pod-craft-runner` image). Until then the
pipeline starts and reports "vendor binary not installed" per step — it does not
fabricate output.

## MCP integration with DeerFlow

`deploy/mcp-stdio.mjs` bridges DeerFlow's stdio MCP transport to the pipeline's
HTTP MCP server. It exposes three tools:

- `list_pending_assets`
- `trigger_pipeline_job`
- `get_fourthwall_status`

Run the pipeline MCP server on the VPS, then register it in DeerFlow's
`extensions_config.json` as an MCP server (`type: "http"`, url
`http://host.docker.internal:8765/`) or use the stdio bridge inside the container.

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

Verified on Windows 11 / Node 26.7.0 and on the deployed VPS:

- Console: typecheck, lint, 207 JS tests (205 pass, 2 skipped), Vercel build,
  `node-server` build, and a Chrome visual pass over all five sections at
  desktop and phone widths against **the VPS build over an SSH tunnel** (0
  console errors, 0 failed requests, 0 horizontal overflow).
- Pipeline: 31 tests on the VPS against containerised PostgreSQL (27 pure, 4
  integration using the documented `craft_stub.py` double and a mocked
  Fourthwall transport).
- Live end-to-end on the VPS: `trigger_pipeline_job` → detached worker → trace,
  trim, effect steps all exit 0 → `apparel_final.png` written → product row
  `draft` with `last_error: "no Fourthwall credentials configured"` (honest
  refusal, no fake publish). The run is `succeeded`, the asset `processed`.
- DeerFlow integration: DeerFlow's own `langchain_mcp_adapters` client loads the
  three Forge tools from `http://172.17.0.1:8765/` and successfully calls
  `list_pending_assets`.
- Boot: `deerflow-forge-console.service`, `pod-mcp.service`, `pod-worker.timer`
  and `docker.service` are all `enabled`; Postgres and nginx restart policies
  are `unless-stopped`.

Windows-specific fixes in this tree: the Vite env-wrapper resolves npm `.cmd`
shims, the build script re-invokes npm through `npm_execpath`, the test script
globs correctly under `cmd`, and symlink-dependent tests skip when Developer
Mode is unavailable.

Known gaps before real pipeline traffic: vendor craft binaries (the shipped
`craft-bin/*-cli` files exit 127 by design), Fourthwall credentials, and the
`fourthwall_template_id` values in `config/products.json`. Until those exist the
pipeline refuses at the publish step with a named error rather than pretending
to publish.


