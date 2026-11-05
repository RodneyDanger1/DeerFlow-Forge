# Docs fixes — Wave 2 (task-30)

**Status: PARTIAL — hard stop reached after the first authoritative-doc corrections.**
**Date:** 2026-11-05 · **Seat:** examples-skills-packager · **Code edits:** none · **Production:** none

## Changed files

| File | Change | Evidence |
|---|---|---|
| `docs/AGENT-SKILL-MATRIX.md:25` | Fixed wrong docs path: `04-HARNESS-DESIGN.md` → `research/eko-deerflow-agent/wave2/04-HARNESS-DESIGN.md`; qualified `02-FORGE-SKELETON.md`, `ARCHITECTURE.md`, `09-GOAL-GAP-PLAN.md` with the research root | `research/eko-deerflow-agent/wave2/04-HARNESS-DESIGN.md` exists; no repo-root `04-HARNESS-DESIGN.md` |
| `docs/AGENT-SKILL-MATRIX.md:34` | Gate status: `execution provenance U` → **PASS**, citing `execution-wave/16-G0-PROVENANCE.md` (independent fresh staging run reproduced artifacts byte-identically) | `docs/PLAN-CONTINUATION.md:19`; `CAPABILITY-MATRIX.md:64` |
| `docs/CAPABILITY-MATRIX.md:25` | "189-file desktop package includes 10 skills" → **6 skills**, names listed | `C:\Users\Riley\Desktop\Ridgeboundia-Agent-Research\skills`: `agent-learning-loop`, `craft-agent-operator`, `forge-harness-architect`, `harness-code-adapter`, `research-corpus-navigator`, `visual-verification-critic` |

## Recomputed counts (commands, this pass)

| Count | Value | Command / scope |
|---|---|---|
| JS tests | **65 pass / 0 fail / 0 skip** | `npm.cmd test` (node:test; 18 suites, 65 tests, 2.5 s) |
| Desktop package files | **189** | recursive file count of `C:\Users\Riley\Desktop\Ridgeboundia-Agent-Research` |
| Package skills | **6** | `Get-ChildItem <package>\skills -Directory` (names above) |
| Corpus source files | **179** | recursive count of `research/eko-deerflow-agent`, excluding `__pycache__` |
| Answers | **400** | 200 `**Qn.` in `REPORT.md` + 200 in `wave2/08-200-QUESTIONS.md` |
| Diagram sources | **8** (+ `INTEGRATIONS.mmd`) | `research/eko-deerflow-agent/diagrams/*.mmd` |
| Forge tables | **13** | `CREATE TABLE` in `blueprint/files/sql/schema_forge.sql` |

## Not changed / still stale

- **`docs/PLAN-CONTINUATION.md` not edited** — plan seat owns it, per Lead instruction (task text allowed it; Lead message takes precedence).
- Test counts in `README.md:206` and `CAPABILITY-MATRIX.md:26` (**139 pass / 4 skip**) were **not re-run**; static `def test_` count is 141. Label remains runner-qualified and must not be quoted as re-verified.
- `CAPABILITY-MATRIX.md:15` **36 transitions/edges** not recomputed.
- `README.md:205` Playwright **15/15**, `CAPABILITY-MATRIX.md:23` G0 **22/22 hashes / 9/9 gates**, MCP **33/26** tools: not re-executed this pass.
- `README.md:5` "orchestrated by DeerFlow 2.2" and `README.md:13` "stub tests" remain to correct (audit §2); no time before hard stop.
- Historical claims in `README.md:215–218` are already labelled HISTORICAL; no change needed.

## Verification

No code, migration, service or production file was touched. Only the two docs above plus this report were written.
