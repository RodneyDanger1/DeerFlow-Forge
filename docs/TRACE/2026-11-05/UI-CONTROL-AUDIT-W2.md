# UI / control verification — wave 2 (task-27) — **PARTIAL**

**Date:** 2026-11-05 · **Seat:** UI/control trace · **Repo:** `C:\Users\Riley\Desktop\DeerFlow Forge`
**Mode:** read-only on source. No source/docs edited, no commit, no deploy, no production access.
**Stop condition:** hard timebox expired mid-run. This report records exactly what was executed and
what was not. **No UI claim below is a pass** — every unexercised control is `UNVERIFIED`.

---

## 1. Outcome at a glance

| Item | State |
|---|---|
| `NITRO_PRESET=node-server` rebuild | **COMPLETED** — first attempt blocked by host policy; `cmd.exe` path produced `✓ built in 5.56s` and regenerated `.output/nitro.json`; `db:migrate` then skipped (`DATABASE_URL` unset) and the composite npm exit was 1 |
| Fresh `.output` served | **NO** — regenerated but **not served** before the stop (so still no UI evidence) |
| `scripts/visual-console-smoke.mjs` run | **NO** — not executed (blocked by 1–2) |
| Playwright control probes (tabs, keyboard/focus, copy/download, mobile 390×844) | **SCRIPTED, NOT RUN** (written to `%TEMP%\uiw2\probe.mjs`) |
| Defects reproduced | **NONE** (no probe reached a UI) |
| Gate/fix performed | **NONE** — correctly, since no defect reproduced |
| Source changes | **NONE** |
| Files written in repo | this report only |

**No pass/fail verdict about the console UI is issued by this wave.** Wave 1's partial audit was not
reused as evidence; it is superseded by this run's own facts.

---

## 2. What was actually executed (evidence)

| # | Command | Result | Label |
|---|---|---|---|
| E1 | `$env:NITRO_PRESET='node-server'; npm run build` | **FAILED before build**: `npm.ps1 cannot be loaded because running scripts is disabled on this system` (PowerShell `ExecutionPolicy`). Exit 1. | VERIFIED |
| E2 | `cmd /c "set NITRO_PRESET=node-server&& npm run build"` | **Build completed**: `✓ built in 5.56s` → `Generated .output/nitro.json`; then `db:migrate` → `[migrate] DATABASE_URL not set — skipping`; composite npm exit 1 came from that tail, not from vite. `.output/server/index.mjs` mtime updated to `16:27:02`. | VERIFIED |
| E3 | `Get-Item .output/server/index.mjs` → `LastWriteTime 11/05/2026 14:39:27`; clock at check `16:25:57` | **The pre-existing `.output` was ~1 h 46 m stale**, i.e. built before the current HEAD (`a2a7bc7`). Any probe against it would have described an old UI. Not served. | VERIFIED |
| E4 | `git status --porcelain` on audited paths (wave-1 run) + no edits this wave | Working tree unchanged by this seat; source read-only honoured. | VERIFIED |
| E5 | Probe harness authored at `C:\Users\Riley\AppData\Local\Temp\uiw2\probe.mjs` (outside the repo) covering: 5 tabs × desktop/mobile, console/page/request-failure capture, horizontal-overflow check, 12-step Tab focus order, Enter-activated tab switch, Copy terminal-state + clipboard read, Download event + saved bytes. | Written; **never executed**. | VERIFIED (authored) / UNVERIFIED (behaviour) |

### Why the smoke script was not run as-is
`scripts/visual-console-smoke.mjs` hardcodes its output to `<repo>/screenshots` (line 21:
`const SHOTS = join(ROOT, "screenshots")`). Writing there would breach this task's write scope
("write only `UI-CONTROL-AUDIT-W2.md` plus screenshots outside repo"), so the equivalent probe was
re-implemented outside the repo instead. This is a **scope constraint, not a smoke-script defect** —
but it is worth fixing in wave 3 by accepting an output directory argument.

---

## 3. Environmental blocker (must be resolved before wave 3)

PowerShell cannot run `npm` because `npm.ps1` is blocked by ExecutionPolicy:
`File C:\Program Files\nodejs\npm.ps1 cannot be loaded because running scripts is disabled on this system.`
Workarounds that work here: `cmd /c "…&& npm run build"`, `npm.cmd`, or
`node node_modules/vite/bin/vite.js build` with `NITRO_PRESET=node-server` set in the environment.
This is a host setting, not a repo defect — do not "fix" it in code.

---

## 4. UNVERIFIED (all of it — wave 3 backlog)

1. That the `cmd.exe` rebuild (E2) completed and that `.output` is now current with `src/` + HEAD.
2. That `.output` was produced with `NITRO_PRESET=node-server` (not Vercel preset) — check
   `.output/nitro.json` and serve `node .output/server/index.mjs` on a local port.
3. All five tabs render on desktop 1280×800 and mobile 390×844, with zero console/page/request errors.
4. No horizontal overflow at 390×844.
5. Keyboard reachability and focus order; Enter/Space activation of tab buttons; visible focus ring.
6. Copy control terminal state (`Copied` / `Copy failed`) under granted and denied clipboard permission,
   including the documented hang case when `navigator.clipboard.writeText` never settles.
7. Download produces complete bytes (the "URL revoked too early" seam).
8. Sources: 34 file buttons, mobile select present and usable.
9. Routes accordion single-open behaviour (intentional vs defect).
10. Empty/error states (only if inducible without touching source or production).

---

## 5. Next wave — exact order (no new code)

```bash
cmd /c "set NITRO_PRESET=node-server&& npm run build"
node .output/server/index.mjs            # PORT=8092 in the environment
node scripts/visual-console-smoke.mjs http://127.0.0.1:8092
node "%TEMP%\uiw2\probe.mjs" http://127.0.0.1:8092
```

Then compare `screenshots/` output against the probe JSON. Only if a control *fails* in a fresh build
does wave 3 gate and patch; otherwise the console reports PASS with the probe artefact as evidence.

---

## 6. Honest summary

This wave produced **no UI evidence** — it produced the *means* to get it and discovered that the
build path is environment-blocked and the checked-in `.output` is stale. Claiming a pass here would
be exactly the false-verified failure the wave-1 report warned about. Status: **PARTIAL, no defect
asserted, nothing fixed, nothing deployed.**
