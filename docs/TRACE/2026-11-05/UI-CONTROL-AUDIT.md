# UI / control trace audit — wave 1 (read-only)

**Date:** 2026-11-05 · **Seat:** UI/control trace · **Task:** `task-20`
**Scope:** `src/components/forge`, `src/lib/blueprint`, `scripts/visual-console-smoke.mjs`, built
`.output`, `screenshots/` · **Repo:** `C:\Users\Riley\Desktop\DeerFlow Forge`
**Mode:** read-only. No file outside this report was created or modified; no commit, deploy, or
production access.

> **Status banner — read first.** This pass was **timeboxed to a hard stop before the source reads
> and browser probes completed**. It therefore contains: (a) a verified file inventory, (b) the
> documented defect set from the committed TRACE record, (c) an explicit UNVERIFIED list. **No
> defect is asserted as confirmed by this pass**, because no defect was reproduced in the current
> build here. Everything that needs execution is marked UNVERIFIED with the exact command that
> would settle it.

---

## 1. Evidence gathered (what is actually verified)

| ID | Evidence | Label |
|---|---|---|
| E1 | `git log --oneline -3 -- docs/TRACE src/components/forge src/lib/blueprint scripts` → `a2a7bc7 Fix UI/agent seams: clipboard fallback, health 503, verifier malformed checks, abandoned leases`; `ecfb7db Trace: report copy failure, verify correct node-server build`; `3d95d13 Trace/fix console: measured board model, cross-step path, source registry, playbook truth; browser evidence` | VERIFIED |
| E2 | `git status --porcelain -- src/components/forge src/lib/blueprint scripts docs/TRACE .output` → **empty** (audited paths committed, clean working tree) | VERIFIED |
| E3 | File inventory recorded below (names + byte sizes via `Get-ChildItem`) | VERIFIED |
| E4 | `docs/TRACE/AGENT-INSTRUCTIONS.md` (33 lines): goal, console file map, 7 rules, evidence outputs | READ |
| E5 | `docs/TRACE/02-traces.md` (49 lines): T1–T5 defect table + trace ladders + negative paths tested | READ |
| E6 | `docs/TRACE/03-fixes.md` (33 lines): fix receipt, commands run (`typecheck` 0, `npm test` 65/65, build, smoke `ok:true` on `:8092`) | READ |
| E7 | `docs/UI-AUDIT-GATE.md` (34 lines): prior control-inventory verdicts + phase-1 gate naming four seams | READ |
| E8 | `screenshots/` holds 10 `console-*-{desktop,mobile}.png` captured 2026-11-05 14:42 (board, routes, sandbox, playbook, sources ×2 viewports) | VERIFIED (existence) |

**Not gathered (timebox):** source line-level reads of the seven Forge components and four
`src/lib/blueprint` modules; `.output` build inspection; any browser run; visual inspection of the
screenshots.

---

## 2. Inventory (verified by listing; line counts not captured)

### 2.1 Console components — `src/components/forge/`
| File | Bytes | Role per `docs/TRACE/AGENT-INSTRUCTIONS.md:14-20` |
|---|---:|---|
| `console.tsx` | 3,404 | tab shell/nav, shared state |
| `board.tsx` | 5,314 | Board controls + run animation |
| `routes-view.tsx` | 3,215 | Routes accordion |
| `sandbox-view.tsx` | 4,940 | Sandbox limits/faults, `Open runner.py` |
| `playbook-view.tsx` | 18,100 | Playbook content/links (largest static surface) |
| `sources-view.tsx` | 2,994 | Sources file browser/select/download |
| `copy-button.tsx` | 1,532 | copy/download control |

### 2.2 Shared model — `src/lib/blueprint/`
| File | Bytes | Role |
|---|---:|---|
| `model.ts` | 14,149 | shared truth for Board/Routes commands + assumptions (call it the highest-value file to audit) |
| `model.test.ts` | 2,966 | regression pins (trace/fallback/knit/trim/step-adjacency) |
| `sources.ts` | 6,053 | Sources registry (34 buttons per E5) |
| `clipboard.ts` | 1,340 | `copyText` used by CopyButton |

### 2.3 Smoke/probe harness — `scripts/`
`visual-console-smoke.mjs` (4,553 B) exists; adjacent `browser-smoke.mjs`, `browser-smoke-verdict.mjs`,
`browser-guard.mjs`, `blueprint-parity.test.mjs` also present. Only `visual-console-smoke.mjs` is in
scope for this wave.

### 2.4 Build output and screenshots
- `.output/` — **not inspected**. Prior record (`03-fixes.md:20-22`) states a plain build produced the
  **Vercel preset** while `.output` was a stale **node-server** build, fixed with
  `NITRO_PRESET=node-server`. Whether the current `.output` matches current `src/` is UNVERIFIED.
- `screenshots/` — 10 console PNGs + older app-builder captures; timestamps are prior to the latest
  commit `a2a7bc7`, so they may not depict the current UI (UNVERIFIED).

---

## 3. Control inventory under audit (status: not re-exercised)

Derived from `AGENT-INSTRUCTIONS.md:3-4` and `UI-AUDIT-GATE.md:5-13`. Current-build status is
**UNVERIFIED** for every row; the right-hand column is the prior record, not this pass.

| Tab | Controls | Prior verdict (E7) |
|---|---|---|
| Board | 5 route radios, 2 toggles, Run route, rerun | WIRED-AND-WORKS |
| Routes | 5 route sections, expansion | WIRED; open section does not collapse (recorded as maybe-intentional, not fixed) |
| Sandbox | `Open runner.py` → Sources | WIRED |
| Playbook | MCP server, products.json, compose.yml → Sources | WIRED |
| Sources | 34 file buttons, mobile select, Copy, Download | navigation/select/download WIRED; Copy status unobservable headless (Clipboard API stayed pending) |
| Mobile 390×844 | nav, source select, overflow | no overflow, no errors |

Two structural questions this audit could not settle: (1) Routes single-open accordion — intentional
or a defect per rule 5 (`disabled/unreachable control is a defect unless intentionally named`);
(2) CopyButton status when the Clipboard API never settles — the exact seam named in E7.

---

## 4. Documented defects (not re-confirmed in this pass)

These are **committed findings from the prior trace**, reproduced here with their recorded root and
fix. **Fix status is claimed, not proven, by this pass** (commit `a2a7bc7`/`ecfb7db`/`3d95d13`, E1).

| ID | Severity | Symptom (recorded) | Root (recorded, `02-traces.md`) | Proposed fix | Status |
|---|---|---|---|---|---|
| D1 (T1) | High | Board/Routes displayed `vectorcraft-cli trace --input/--svg-out/--out-dir` and knitwear `--palette-limit` while the repaired `routes.py` uses `run --cmd/--export` | `model.ts` hand-copied from the pre-repair route table | keep the parity test (`scripts/blueprint-parity.test.mjs`) comparing rendered `routes.py` argv to the rendered board plan; add a case per family | Fix claimed (3d95d13); **UNVERIFIED** |
| D2 (T2) | High | apparel distress step read `{work}/apparel/trimmed.png` after trim moved to `{work}/trimmed.png` | drifted edge contracts; parity passed because both sides were stale | assert `trim --out == distress --input` in `model.test.ts` (present per E6) | Fix claimed; **UNVERIFIED** |
| D3 (T3) | Medium | `deploy/craft-launchers/*` and DeerFlow MCP example absent from Sources | `sources.ts` imported only old `craft-bin` stubs | registry imports both launchers + MCP example (34 buttons) | Fix claimed; **UNVERIFIED** |
| D4 (T4) | Medium | Playbook image-trace example used old `--commands` JSON; skill count said 22 | static content not updated after Phase 0 | measured `run` example; count reconciled (39) | Fix claimed; **UNVERIFIED** |
| D5 (T5) | Medium | Copy stayed `Copy` when both clipboard paths were denied; no failure signal | `copy-button.tsx` reacted only to success, returned early on failure | explicit `Copied`/`Copy failed` state; bounded wait + fallback | Fix claimed (`ecfb7db`); **UNVERIFIED** |

**Repro pattern for all five (wave 2):** render the tab in the built console, read the control's
label/output, then compare against the rendered `blueprint/files/pod_pipeline/routes.py` contract
(`node --test scripts/blueprint-parity.test.mjs`). A UI string that contradicts `routes.py`/`model`
is a defect by rule 4 (`AGENT-INSTRUCTIONS.md:28`).

---

## 5. Open seams named by the prior gate, still needing proof
(`docs/UI-AUDIT-GATE.md:23-34` — listed here as the highest-value repro targets, not as confirmed defects.)

| Seam | Why it matters | Repro | Proposed fix |
|---|---|---|---|
| Clipboard promise never settles | button can stay `Copy` forever even after the failure-state fix | deny clipboard permission, click Copy, wait >2 s, assert label becomes `Copy failed` | bounded `Promise.race` timeout in `clipboard.ts` → throw a named error |
| `/healthz` could return `ok:true` when the repo is unhealthy | a viewer that lies about health | stub `repo.health` false/raise, assert HTTP 503 + `ok:false` | validate at the service entry; no hard-coded true |
| verifier given non-object `checks` raises instead of refusing | crash path in gate reporting | pass `{checks:"x"}` to the verifier, assert `E_REPORT_INVALID` | shape-validate, return named error |
| download URL revoked too early | truncated download | click Download, hash the blob, revoke early in a test double | revoke on `setTimeout(0)` after click / use `download` attribute lifecycle |

Commit `a2a7bc7` names three of these in its subject ("clipboard fallback, health 503, verifier
malformed checks"); **the fourth (early URL revoke) has no recorded fix and is UNVERIFIED either way.**

---

## 6. Build-artifact risk (UNVERIFIED, high consequence)

`03-fixes.md:20-22` records that `.output` was stale and used the wrong Nitro preset. A stale or
wrong-preset `.output` would make every browser probe describe an old UI — which is exactly how a
false "verified" audit happens. **No conclusion about the built console is valid until `.output` is
rebuilt from the current tree and its `server/index.mjs` served.**

---

## 7. Unverified — required before any wave-2 fix

1. Line-level read of `console.tsx`, `board.tsx`, `routes-view.tsx`, `sandbox-view.tsx`,
   `playbook-view.tsx`, `sources-view.tsx`, `copy-button.tsx`.
2. Line-level read of `model.ts`, `sources.ts`, `clipboard.ts`, `model.test.ts`.
3. `.output` freshness/preset vs `src/`; no stale-artifact check run.
4. Browser probe of all five tabs, desktop 1440×900 and mobile 390×844: console/page/request errors,
   overflow, disabled controls, aria labels.
5. Exercise of `visual-console-smoke.mjs` against a freshly built server (`ok:true` claim from E6 not
   reproduced here).
6. Copy success/failure and Download integrity probes (D5, §5).
7. Whether the Routes accordion's non-collapsing open section is intentional (rule 5).
8. Do the 10 `screenshots/console-*.png` still match the current UI? (timestamps predate `a2a7bc7`).

**Exact commands for the next pass** (no source changes):
```bash
npm run typecheck
node --experimental-strip-types --test src/lib/blueprint/model.test.ts
node --test scripts/blueprint-parity.test.mjs
NITRO_PRESET=node-server npm run build
node .output/server/index.mjs            # then serve on a local port
node scripts/visual-console-smoke.mjs http://127.0.0.1:<port>
```

---

## 8. Method notes

- Specialty skills: `/trace` and `/weaver` are **not installed** in this profile; the trace intent was
  executed against the repo's own committed procedure (`docs/TRACE/AGENT-INSTRUCTIONS.md`) and
  `visual-verification-critic` (`blueprint/files/skills/visual-verification-critic/SKILL.md`, read).
  Recorded as a substitution rather than silently skipped.
- `/forgewright-lead|plan|recon` and `/forge` are baseline procedures **for code changes**; this wave
  touched no code, so they were not invoked.
- Known-good facts used: audited paths are committed and clean (E2), so findings will be stable for
  wave 2 to reproduce.
