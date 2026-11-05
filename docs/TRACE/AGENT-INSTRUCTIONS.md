# TRACE agent instructions — DeerFlow Forge console

**Goal:** walk every console tab (`Board`, `Routes`, `Sandbox`, `Playbook`, `Sources`) in reading order;
inventory every control; trace each control from render → handler → shared model → rendered result;
fix only confirmed defects at the true source; prove RED→GREEN and re-run the suite after each fix.

**Current plan (read first):**
- `research/eko-deerflow-agent/README.md` — master plan/status.
- `research/eko-deerflow-agent/ARCHITECTURE.md` — system boundaries.
- `research/eko-deerflow-agent/execution-wave/09-GOAL-GAP-PLAN.md` — decisions/tests.
- `research/eko-deerflow-agent/execution-wave/11-G0-EVIDENCE.md` — actual staged Phase 0 truth.

**Console files:**
- `src/components/forge/console.tsx` — tab shell/nav and shared state.
- `src/components/forge/board.tsx` — Board tab controls and run animation.
- `src/components/forge/routes-view.tsx` — Routes tab family accordion.
- `src/components/forge/sandbox-view.tsx` — Sandbox tab limits/faults and `Open runner.py`.
- `src/components/forge/playbook-view.tsx` — Playbook content/links.
- `src/components/forge/sources-view.tsx` — Sources file browser/copy/download.
- `src/components/forge/copy-button.tsx` — copy/download controls.
- `src/lib/blueprint/model.ts` — **the shared truth** for Board/Routes commands and assumptions.
- `src/lib/blueprint/sources.ts` — the source-file registry for Sources.

**Rules:**
1. Do not edit until the broken hop is named with `path:line`.
2. One writer per file; Lead owns final integration.
3. No test weakening; no placeholder/mock in the product path.
4. A UI string that contradicts the actual `routes.py`/`model` is a defect, not cosmetic drift.
5. A disabled/unreachable control is a defect unless it is intentionally named/refused.
6. Record VERIFIED / READ / INFERRED / UNVERIFIED; do not claim a click/run not exercised.
7. After each fix: re-run typecheck/tests and re-trace the affected tab; report residual bounds.

**Evidence output:** `docs/TRACE/01-controls.md`, `docs/TRACE/02-traces.md`, `docs/TRACE/03-fixes.md`.
