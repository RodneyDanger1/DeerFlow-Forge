# UI + agent bug audit — 2026-11-05

Scope: built console (desktop/mobile), real control handlers, Forge service/verifier/reaper seams.
Gate: `docs/UI-AUDIT-GATE.md`. No production change.

## UI control matrix

| Control family | Evidence | Result |
|---|---|---|
| 5 nav buttons | rebuilt bundle, desktop + mobile | WIRED-AND-WORKS |
| 5 route radios | every radio checked | WIRED-AND-WORKS |
| 2 toggles | `aria-pressed` true/false | WIRED-AND-WORKS |
| Run route / rerun | waits for `Run again`, then `Running` | WIRED-AND-WORKS |
| 5 route sections | expand Knitwear | WIRED-AND-WORKS |
| Sandbox → runner.py | Sources heading `pod_pipeline/runner.py` | WIRED-AND-WORKS |
| Playbook → MCP server | Sources heading `pod_pipeline/mcp_server.py` | WIRED-AND-WORKS |
| 34 source buttons | switch file | WIRED-AND-WORKS |
| Copy | real built bundle | **Copied** after stable-locator retest |
| Download | download event + bytes | **4456 bytes** |
| Mobile select | 34 options; switch file | WIRED-AND-WORKS |
| Mobile layout | 390×844 | no overflow, no errors |

The first copy probe used `getByRole(button, name="Copy")`; after the label changes to `Copied`, that
locator is no longer a stable identity. Re-querying `main button` with `/^(Copied|Copy failed)$/`
showed the correct state. This was a **probe false negative**, not a product failure. The clipboard
path was still hardened with a 700 ms timeout + selection fallback so a pending Clipboard API cannot
leave the button inert forever.

## Confirmed defects fixed

1. **`/healthz` always returned `ok:true`** even if the repository was down. It now calls
   `repo.health()`; unhealthy/raising repos return `503 E_SERVICE_UNHEALTHY` /
   `E_SERVICE_UNAVAILABLE`.
2. **Verifier crashed on a non-object check** with `AttributeError`. It now returns
   `E_REPORT_INVALID`; regression test added.
3. **Lease reaper requeued forever** after `max_attempts`. It now marks the job `abandoned` with
   `E_LEASE_EXPIRED_MAX_ATTEMPTS`; an abandoned job is never claimable. Scratch-Postgres test added.
4. **Clipboard could stay pending** in headless/denied contexts; `copyText` now races a 700 ms
   timeout and falls back to `execCommand`, with timer cleanup.

## Proof

```text
NITRO_PRESET=node-server npm.cmd exec vite build      # success
node scripts/visual-console-smoke.mjs http://127.0.0.1:8090
  desktop + mobile: ok:true; no overflow; no console/page/request errors

custom Playwright audit
  ok:true; 15 checks; copy status "Copied"; download 4456 bytes; 34 mobile options

npm.cmd test                   65 passed
npm.cmd run typecheck          exit 0
staging pytest                 112 passed, 4 skipped
  (scratch PostgreSQL + G0 bundle mounted)
repo tests                     4/4 (includes abandoned job)
service tests                  5/5 (includes 503 unhealthy repo)
verifier tests                 8/8 (includes malformed check)
```

## Not done / unverified

- Routes accordion stays open when its selected section is clicked again; recorded as UX behavior, not
  changed.
- Sources still lists only the pod package (34 files), not the new Forge Python modules.
- No production service/UI deployment; loopback console and scratch DB only.
- Copy success in a real user browser with a permission prompt is still browser-dependent; the
  timeout/fallback path is the tested safety net.
- W3-B critic remains not started.
