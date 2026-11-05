# Recon ledger — Forge Conductor

Per `forgewright-recon`. Read-only; no edit authorized by this ledger.

## Target behavior

Take a print/vector brief, run the installed Craft apps through native CLI/MCP, verify the artifact and
gates, record an evidence episode, and require human approval before publish.

## Entry points (current)

| Entry | Path:line | Role |
|---|---|---|
| Pipeline orchestrator | `blueprint/files/pod_pipeline/orchestrator.py:58` | claim → execute → publish |
| Trace stage | `orchestrator.py:147` | VectorCraft/raster trace |
| Step runner | `orchestrator.py:167` | argv, timeout, retry |
| Publish | `orchestrator.py:225` | Fourthwall product state |
| Pipeline MCP | `pod_pipeline/mcp_server.py:51` | three tools |
| Console | `src/components/forge/console.tsx` | viewer only |
| DeerFlow integration | `deploy/mcp-stdio.mjs` + `extensions_config.json` | external harness → Forge MCP |
| Craft CLIs | `/opt/craft/*/bin/*-cli` | real command engines |
| Craft MCP | `vectorcraft-cli mcp`, `photocraft-cli mcp` | 33/26 tools |
| Stub shims | `/opt/pod-pipeline/bin/*-cli` | exit 127 (blocker) |

## Callers / data flow

`console/MCP → pod_mcp → DB run row → detached worker → run_pipeline → routes → Craft CLI → artifact →
validators → publish → DB state`.

Failure path: missing stub → exit 127 → step failed → run failed → no artifact; `README.md` live-E2E
claim is historical/unreproducible now.

## Tests (current)

| Test | Command | State |
|---|---|---|
| Console type/lint/test | `npm run typecheck`, `npm run lint`, `npm test` | not run in this audit |
| Pipeline pure/integration | `cd blueprint/files && uv run ... pytest` | cached `lastfailed={}`, not re-run |
| Craft trace | VPS/gate tool | prior runs exist; no current Craft CLI path |
| Promotion sim | `cd execution-wave/sim && python -m unittest -v test_promotion` | 23/23 pass; `python simulate.py` deterministic |
| Adapter | `node --test`/package script | in progress |
| Diagram validation | Kroki HTTP 200 for 8/8 | validated |

## Unknowns / evidence missing

- DeepSeek key validity (zero-spend metadata endpoints proposed; no live call).
- Film/Design/Effect availability (absent on host; private store unknown).
- DeerFlow stdio MCP path (working servers are HTTP; not yet registered).
- PhotoCraft MCP concurrency under load; SVG flatten fidelity; post-change test counts.
- Human inter-rater agreement; real gate/human rates; cost per accepted artifact.
- Whether README's earlier E2E can be reproduced after repair.

## Files expected to change (planned, not done)

See `09-GOAL-GAP-PLAN.md` §5. No production file is touched by this wave.

## Recon verdict

**Recon complete for Phase 0.** The execution path is the first broken link; the model/harness is not.
