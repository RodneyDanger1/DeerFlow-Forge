# UX / Accessibility / Native-Surface Audit — Wave 1

**Task:** `task-24` · **Seat:** agent-repos-scout (UX/accessibility/native-surface) · **Date:** 2026-11-05 (America/Chicago)
**Mode:** read-only. No source/docs/commit/deploy/production change. This file is the only write.
**Timebox notice:** the Lead timeboxed this report to 3 minutes of remaining work. Interactive Playwright inspection, screenshot reading, and component-level code review were **not executed**. Everything not directly observed below is marked `UNVERIFIED` — this file records verified recon, an explicit probe backlog, and the native-surface classification; it does **not** claim a pass.

## Evidence labels

| Label | Meaning |
|---|---|
| `[V]` | Verified in this session by a command or file listing I actually ran. |
| `[U]` | Unverified — probe not run (timebox), or no access. Not a pass, not a defect. |
| `UNAVAILABLE` | No tool/bridge exists in this seat to perform the check; classified, not faked. |

## 1. Verified recon `[V]`

- Console source inventory (`src/`): `routes/index.tsx`, `routes/__root.tsx`, `router.tsx`, `routeTree.gen.ts`, `styles.css`; forge UI components `components/forge/{console,board,routes-view,sandbox-view,playbook-view,sources-view,copy-button}.tsx`; error surface `lib/error-component.tsx`; auth gates `lib/auth/gates.tsx`; blueprint model `lib/blueprint/model.ts`; preview bridge `components/preview-host-bridge.tsx` + `lib/preview-host-bridge.ts`.
- Scripts available for a UI probe: `dev` (`vite dev --host 0.0.0.0 --port 8080`), `build`, `build:dev`, `preview`, `preview:restart`, `smoke:console` (`scripts/visual-console-smoke.mjs`), `test`, `typecheck`.
- Existing trace corpus: `docs/TRACE/01-controls.md`, `02-traces.md`, `03-fixes.md`, `AGENT-INSTRUCTIONS.md` (read-not — left for the full pass).
- `screenshots/` exists with **18 image files** (sizes 1,197–124,219 bytes). Filenames were not captured before the timebox; no image was read, so **no visual claim** is made.
- `docs/TRACE/2026-11-05/` did **not** exist; this report created it.

## 2. Checks NOT run — `UNVERIFIED` (probe backlog)

None of the task's required interaction checks were executed. Each is a first-class wave-1 probe, not a suggestion:

| # | Check | Method | Status |
|---|---|---|---|
| A1 | Server boots and console renders | `npm run preview:restart` (or `npm run dev`), Playwright to `http://127.0.0.1:8080` / `:8081` | `[U]` |
| A2 | Keyboard order + visible focus | Tab/Shift-Tab through the page, assert `:focus-visible` on every interactive element | `[U]` |
| A3 | Labels / accessible names | Axe-core or manual: every button/input has a name; images have `alt`; forms have `<label>` | `[U]` |
| A4 | Headings/landmarks | Assert one `h1`, ordered `h2..h6`, `main`/`nav`/`header` landmarks | `[U]` |
| A5 | Loading states | Trigger slow/failed data, screenshot and assert a visible busy/status state | `[U]` |
| A6 | Empty states | Fresh/empty project list: assert explanatory copy + next action | `[U]` |
| A7 | Error states | Force a server/data error; assert readable error + recovery path (see `lib/error-component.tsx`) | `[U]` |
| A8 | Mobile 390×844 | Playwright viewport; no horizontal overflow; touch-target ≥44 px; usable nav | `[U]` |
| A9 | Contrast / motion | Compute token contrast from `styles.css`; check `prefers-reduced-motion` | `[U]` |
| A10 | Screenshot read-back | Read the 18 `screenshots/` images and map visible defects to `file:line` | `[U]` |
| A11 | Source review | Read the seven forge components + `error-component` + `gates` for ARIA and error-path gaps | `[U]` |

**Consequence:** `0` confirmed defects and `0` confirmed passes. Reporting either without A1–A8 would be a fabricated result.

## 3. Native GUI / CUA — `UNAVAILABLE` + `UNVERIFIED`

- The specialty `/visuals-gui` protocol requires a computer-use driver (CUA CLI/MCP) that can launch, focus, snapshot and act on a real window.
- **No bridge is proven in this seat:** no CUA/MCP screen driver was mounted or contacted, no accessibility snapshot or window screenshot was captured, and the host is a Windows workstation while the web console is the only reachable surface (local dev/preview server).
- Therefore **no native snapshot exists and none is claimed.** Native findings (menu, dialog, focus path, state restoration, cross-app handoff) are `UNAVAILABLE` for this seat and `UNVERIFIED` for the product. Any future claim about the native/Craft GUI must cite a fresh snapshot + accessibility tree from a real bridge; a browser screenshot of the web console is **not** evidence about the native app.

## 4. Defects

| ID | Severity | Screen/control | Repro | Proposed fix | Status |
|---|---|---|---|---|---|
| — | — | — | — | — | **No defect is confirmed.** None is listed, because no reproducible interaction was run. |

## 5. Risks to test first in the full pass (hypotheses only, not defects)

1. Error path: `lib/error-component.tsx` exists, but whether a failed route surfaces a readable message plus a retry link is unverified (A7).
2. Auth gates: `lib/auth/gates.tsx` + sign-in gate logic exist; whether a signed-out viewer gets a labelled, keyboard-reachable gate — unverified (A2/A3/A7).
3. Mobile: the console is data-dense (`board`, `routes-view`, tables); horizontal overflow at 390×844 is the most likely mobile failure (A8) — unverified.
4. Loading: viewers that fetch jobs/assets need an explicit busy state; spinner-never-resolves is a silent failure (A5) — unverified.

## 6. Exact commands for the full wave-1 pass

```bash
npm run preview:restart          # or: npm run dev  (0.0.0.0:8080)
npx playwright --version         # confirm driver + browser availability
npm run smoke:console            # existing smoke script, read its JSON output
```
Then a Playwright script that, per screen: assert `h1`/landmarks, tab through all controls recording focus ring, run axe-core, resize to 390×844, force empty/error/loading states, and save screenshots under `/tmp` (not the repo). Read each screenshot back with an image reader before writing any defect.

## 7. Handoff

- **Report status: PARTIAL (timeboxed).** Verified: recon inventory + native classification. Unverified: every interaction/a11y/mobile check (A1–A11).
- **Do not treat this file as an audit pass.** Wave 1 evidence requires A1–A8 outputs quoted per screen; without them, severity and fix recommendations would be invented.
- **Native surfaces:** explicitly `UNAVAILABLE` for this seat; no fake snapshot was produced.
