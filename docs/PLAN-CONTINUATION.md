# Plan continuation — 2026-11-05

**Read first:** `research/eko-deerflow-agent/README.md`, `GOALS.md`, `ARCHITECTURE.md`,
`execution-wave/09-GOAL-GAP-PLAN.md`, `execution-wave/11-G0-EVIDENCE.md`, `docs/TRACE/03-fixes.md`.

## Status

| Step | Status |
|---|---|
| W0 docs integrity | done |
| W1-A launcher/argv/preflight/mutation/gate truth | done on staging; 53 pass/4 skip |
| W1-B Craft MCP direct proof | done: 33/26 tools + PhotoCraft `command_batch` |
| W1-B DeerFlow registration | not applied |
| G0 real trace/retouch | passed on staging; Lead-run |
| W1-C skill guidance | **DONE** — 39/39, both runtimes; guidance only |
| Independent W1-C/console review | **PASS** (`13-INDEPENDENT-REVIEW`) |
| Independent G0 artifact review | **PASS (artifact consistency)**; execution provenance **U** (`14-G0-ARTIFACT-REVIEW`) |
| G0 artifact bundle | copied to `execution-wave/g0/` + 22-entry MANIFEST; D2 vacuous retype gate fixed; report regenerated as 9/9 applicable |
| G0 provenance | **CLOSED independently** (`16-G0-PROVENANCE.md`): fresh staging-only run reproduced artifacts byte-identically |
| W2 Forge service/DDL/queue | **W2 local gate PASS**: 97 pass/9 skip; 18/18 SQL; 9 ms SKIP LOCKED; real HTTP→repo→worker→reaper e2e. No production deploy |
| UI/agent bug audit | **DONE for tested surfaces**: copy fallback, health 503, verifier malformed check, reaper abandoned; UI 15/15 checks, 112 pass/4 skip |
| W3-A verifier | **DONE**: 8/8 tests; real G0 pair passes; tamper/vacuous/failed/malformed checks refuse; staging 112 pass/4 skip |
| W3-B critic | **DONE (contract)**: 14/14 blind-critic tests; gate authoritative; disagreement → needs_human; no model claim |
| W4 learning/eval | not started |

## Decision

G0 is closed: artifact consistency PASS, independent provenance PASS. W2 may begin as **local source**
(new `forge` gateway/schema/tests), but no production `forge` DB, service, or cutover until W2 gate G1.
The `--print-width-in 5.0` recipe is now recorded; the old 8.0 default produces a different PNG by design.

## Decision

Do **not** start W2 yet. The independent reviewer confirmed the artifacts are internally consistent but
cannot confirm they came from the VPS. Starting a durable ledger on that basis would violate the
plan's gate. The honest next action is either:

1. owner grants the verifier read-only VPS access so it can rerun G0, or
2. owner explicitly accepts a **conditional G0** based on Lead-run artifacts + independent artifact
   consistency, with W2 still local-only until production is separately approved.

No production cutover is proposed either way.

## W1-C scope and non-goals

**Goal:** patch only skills whose guidance still contradicts Phase 0 or omits a safety boundary.

**Files:**
- `blueprint/files/skills/forge-harness-architect/SKILL.md` — promotion rule is stale (3/3).
- `blueprint/files/skills/craft-mcp-drive/SKILL.md` — await dependent MCP calls; interleaving.
- `blueprint/files/skills/apparel-print-master/SKILL.md` — bind approval to artifact SHA-256.
- `blueprint/files/skills/craft-agent-operator/SKILL.md` — already has evidence/preflight; no rewrite.
- `blueprint/files/skills/harness-code-adapter/SKILL.md` — already has donor provenance; no rewrite.

**Not goal:** runtime code, new skills, renaming installed skills, claiming behavior is enforced.

**Verify:** `validate_skills.py` → 39/39; `check_skill_commands.py` → 0 unknown; install both runtimes;
then run a fresh verifier on local tests and G0 evidence (VPS access is a known verifier limitation).
