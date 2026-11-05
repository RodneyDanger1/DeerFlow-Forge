# Live VPS verification — 2026-11-05

**Source:** local `09b20e5` (UI truth fix on top of `3b3b65b`) pushed to
`https://github.com/RodneyDanger1/DeerFlow-Forge` before deployment.
**VPS:** `srv2108523` / `179.197.88.181`, `/opt/deerflow-forge`, user `forge`.
**Built runtime source:** `09b20e5` · **VPS checkout after evidence sync:** `b747939` (docs/evidence only; no app-code change) · **console unit:** `deerflow-forge-console.service` **active**
· **bind:** `127.0.0.1:8091` · **served HTML:** 14,253 bytes.
**Built output mtime on VPS:** `2026-11-05 23:48:00 UTC`.
**Access:** local SSH tunnel `127.0.0.1:18091 -> 127.0.0.1:8091`; CUA + Playwright both target
the tunnel.

## Deployment

1. Local `npm run build` with `NITRO_PRESET=node-server` → success.
2. Commit pushed to GitHub main (`09b20e5`).
3. VPS `git fetch` + `git reset --hard origin/main`; ownership repaired to `forge:forge` after
   root-owned skill files blocked the reset.
4. VPS `npm run build:vps` → `✓ built`, `.output` regenerated.
5. `systemctl restart deerflow-forge-console` → active; `curl /` → 200.

## CUA native pass

`cua-driver doctor` exit 0 · driver **0.28.2** · Windows UIA + interactive desktop available.

| Action | Result |
|---|---|
| `launch_app` Chrome new window on `http://127.0.0.1:18091` | window created, title `DeerFlow Forge` |
| `get_window_state` | 57 UIA elements; heading, nav, and all 10 route steps present |
| CUA `click` Routes (background) | earlier window rendered `Fourthwall routes` |
| CUA foreground Sandbox click | rendered `Sandbox and faults` with tree/limits/fault content |
| CUA foreground Board + Run route | after 5 s button `Run again`, `trace_state traced.` |
| CUA foreground Sources + Copy | system clipboard contained `routes.py` text (11,395 CRLF chars; raw file is 11,150 LF bytes + 245 line breaks) |
| screenshots | `screenshots/live-vps-2026-11-05/` |

**CUA note:** background synthetic clicks on the Chrome surface returned
`effect:"unverifiable"` and did not always land; `delivery_mode:"foreground"` landed and was verified
by fresh snapshots. This is a browser/transport constraint, not a product defect.

**One stale-window false negative:** after the deployment reload, the original background Chrome
window rendered a blank content area. A fresh CUA window and a Playwright page both rendered the app,
and Playwright reloaded the live page three times successfully. The old renderer was discarded as a
stale browser session; it is not treated as an app failure.

## Live console black-box suite — 22/22

URL: `http://127.0.0.1:18091` (VPS build), Chrome via Playwright, 1440×900 + 390×844.

| Check | Result |
|---|---|
| truth copy | header `Static blueprint · no live services`; body `Simulation of the documented route — no Craft process runs.` |
| tabs | Board, Routes, Sandbox, Playbook, Sources all non-empty; headings correct |
| five product routes | Apparel 10 steps; Knitwear 9; Accessories 9; Odd/3D 10; Stationery 10; `aria-checked` true |
| fault path | trace-exit-1 toggle → `FAIL` + `trace_state raster_fallback.` |
| normal path | toggle off + run → `trace_state traced.` |
| sandbox deep-link | `Open runner.py` → `pod_pipeline/runner.py` |
| all source files | 34/34 selectable on desktop; every heading/content non-empty |
| copy | clipboard normalized-equals rendered source (7,135 CRLF chars) |
| download | 6,967-byte file normalized-equals rendered source |
| playbook deep-link | `products.json` opens under Sources |
| keyboard/a11y | 3 landmarks; 0 unnamed controls; 10/10 Tab stops visible |
| console | 0 errors |
| reload | 3 consecutive reloads stable |
| mobile | 390×844 overflow 0; source select 34 options; no page errors |

## Live Forge service — real PostgreSQL

Temporary PostgreSQL 16 + `sql/schema_forge.sql`; service started with
`python -m forge_service --dsn … --port 8092` on the VPS.

| Probe | Observed |
|---|---|
| `GET /healthz` | `200 {"ok":true,"service":"forge","repo":{"ok":true,"tables":13}}` |
| `POST /v1/episodes` unique | `201`, episode `bf8013ef-…`, key `live-1793922706` |
| duplicate POST same key | `200`, same episode id, `"replayed":true` |
| `GET /v1/episodes/{id}` | `200` |
| `POST` with `account_id:true` | `400 E_REQUEST_INVALID`, detail `account_id must be a positive integer` |
| unknown episode | `404 E_EPISODE_NOT_FOUND` |
| service log | `forge service listening on http://127.0.0.1:8092 (loopback)` |

## Live worker — real PostgreSQL

One real job inserted through SQL; handler wrote its payload to `/tmp`:

```text
WORKER={"claimed":1,"finished":1,"job_id":1,"job_ok":true,"ok":true}
HANDLED={"n":1}
EMPTY={"claimed":0,"finished":0,"job_id":null,"ok":true}
```

This proves claim → handler → guarded finish → empty-queue behavior on the VPS with the real
repository, not an injected test repo.

## Findings

1. **FIXED — UI truth:** header previously claimed `Fourthwall Open API · DeepSeek V4.1-Flash`;
   no such live connection exists. Now `Static blueprint · no live services`.
2. **FIXED — misleading run affordance:** “Run route” now carries
   `Simulation of the documented route — no Craft process runs.`
3. **No app defect confirmed** in tabs, routes, toggles, run animation, sandbox/playbook deep-links,
   sources, copy/download, keyboard, mobile, reload, service, or worker.
4. Browser-session blank after deploy and background CUA click drops are **tooling false negatives**
   with fresh-window/foreground counter-evidence.

## Not verified

- Production `forge` database/service/TLS/auth; this used a temporary scratch PostgreSQL and a
  temporary service process.
- Craft execution through the gateway/service; no executor seam exists.
- DeerFlow MCP registration; no Fourthwall publish.
- Native GUI claim beyond Chrome window driving; no other desktop app was exercised.
