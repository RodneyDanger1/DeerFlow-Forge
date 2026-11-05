# UX / Accessibility / Native-Surface Audit — Wave 2 (real pass, partial)

**Task:** `task-31` · **Seat:** agent-repos-scout · **Date:** 2026-11-05 (America/Chicago)
**Mode:** read-only; only this file written. No source edit, no commit, no deploy, no production access.
**Status: PARTIAL — hard stop before the browser pass executed.** No probe result is claimed.

## 1. What was actually done `[V]`

| # | Action | Observed output |
|---|---|---|
| 1 | Claimed task-31 | board revision 2, owner agent-repos-scout |
| 2 | Checked built console artifact | `.output/server/index.mjs` — **present** (Nitro build exists) |
| 3 | Probed local ports | `8080` **closed**, `8081` **closed** (no server was running) |
| 4 | Checked Playwright runtime | `playwright 1.64.0`; chromium executable `C:\Users\Riley\AppData\Local\ms-playwright\chromium-1248\chrome-win64\chrome.exe`; browser cache contains chromium-1234/1248 + headless shells |
| 5 | Inventoried screenshot corpus | 18 image files: `app-builder-{built,preview}{,-mobile}.png`, `console-{board,playbook,routes,sandbox,sources}-{desktop,mobile}.png`, `sources-desktop.png`; plus `app-builder-{built,preview}.json` |
| 6 | Attempted preview server | `npm run preview:restart` **failed**: `npm.ps1 cannot be loaded because running scripts is disabled on this system` (PowerShell execution policy). Server never started. |

## 2. What was NOT run — `UNVERIFIED`

Because the server never came up, none of the required interaction probes executed:

| # | Probe | Status |
|---|---|---|
| A1 | Boot + console render in Chromium | `UNVERIFIED` |
| A2 | Tab order, focus visibility (`:focus-visible`) | `UNVERIFIED` |
| A3 | Labels / accessible names (buttons, inputs, images `alt`) | `UNVERIFIED` |
| A4 | Headings (`h1` count/order) and landmarks (`main`/`nav`) | `UNVERIFIED` |
| A5 | Loading state | `UNVERIFIED` |
| A6 | Empty state | `UNVERIFIED` |
| A7 | Error state | `UNVERIFIED` |
| A8 | Mobile 390×844 (overflow, touch targets) | `UNVERIFIED` |
| A9 | Screenshot read-back (18 images) | `UNVERIFIED` |

**Confirmed defects: 0. Confirmed passes: 0.** Neither is reported as a finding.

## 3. Exact blocker and the command that should work next `[V]`

`npm` is blocked only through the PowerShell shim (`npm.ps1`), not by Node or the repo:

```powershell
# bypass the blocked shim:
cmd /c npm run preview:restart
# or call the script directly:
node scripts/preview.mjs restart
# verify, then probe:
#   Invoke-WebRequest http://127.0.0.1:8081/ -UseBasicParsing  -> expect 200
node -e "const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();const r=await p.goto('http://127.0.0.1:8081/');console.log(r.status(),await p.title());await p.screenshot({path:process.env.TEMP+'/w2.png'});await b.close();})()"
```

The screenshot read-back can also proceed independently of the server: the 18 images in `screenshots/` exist and were not opened due to the timebox.

## 4. Native GUI / CUA — `UNAVAILABLE` (unchanged)

No CUA/MCP screen bridge is proven in this seat; no window snapshot or accessibility tree exists; no native claim is made. A browser screenshot of the web console is not native evidence.

## 5. Handoff

- This file is **PARTIAL**: environment and blocker verified; interaction pass not executed.
- Re-run with `cmd /c npm run preview:restart` (or `node scripts/preview.mjs restart`), then run A1–A9 against `http://127.0.0.1:8081/` (or 8080 for the dev server).
- Risks from the wave-1 partial remain untested: error path (`src/lib/error-component.tsx`), auth gate UX (`src/lib/auth/gates.tsx`), mobile overflow on dense views, loading states.
