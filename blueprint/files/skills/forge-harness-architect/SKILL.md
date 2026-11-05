---
name: forge-harness-architect
description: "Use when designing or changing the hosted Forge Conductor: a third plane beside the DeerFlow console and pod pipeline, with a supervisor, capability-scoped specialists, typed handoffs, a Craft tool gateway, evidence ladder, episode ledger, promotion and rollback. Turns research into a decision-complete build plan. Triggers: Forge Conductor, agent harness design, harness architecture, build an agent, supervisor, subagents, tool gateway, episode ledger."
version: 1.0.0
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [harness, architecture, conductor, subagents, ledger, vps, deepseek]
    related_skills: [research-corpus-navigator, harness-code-adapter, agent-learning-loop, visual-verification-critic, craft-agent-operator]
---

# Forge Conductor architect

Design the **third plane** that makes an agent trustworthy on production art. It is not a new model,
not a new planner, and not a pixel-first computer-use agent. It is the control plane around the existing
DeerFlow runtime and the Craft command engines.

## When to use / not use

- Use to design/implement the Forge Conductor, its roles, contracts, tables, phases or acceptance.
- Use when deciding whether a feature belongs in the conductor, DeerFlow, the pipeline or a Craft app.
- Not for a single command (`artcraft-command-atlas`), transport (`craft-mcp-drive`), or visual checks
  (`visual-verification-critic`).

## Verified baseline (read before designing)

- VPS: 2 vCPU, 7.9 GB RAM, 36 GB free, **no GPU/display**; load already shared with other services.
- DeerFlow **2.2.0** is running; model `deepseek-flash` = “DeepSeek V4.1 Flash”, 1,048,576 ctx,
  8,192 output, key via `DEEPSEEK_API_KEY` (value never assumed valid).
- VectorCraft 0.21.1 / PhotoCraft 0.20.2 are installed; Design/Effect/Film are **absent**.
- `/opt/pod-pipeline/bin/*-cli` are **stubs exiting 127**; real binaries are under `/opt/craft/*/bin`.
- Pipeline `routes.py` argv is invented and wrong (`vectorcraft-cli trace`, `photocraft-cli --input`).
- `pod` DB is empty schema-only; no episode/eval/skill tables; `pod-mcp` is unauthenticated on 0.0.0.0:8765.
- Full evidence: `wave2/01-STACK-VPS.md`, `wave2/03-CRAFT-SURFACE.md`.

## Decisions (bind these unless re-planned)

| # | Decision |
|---|---|
| D1 | New `forge-*` plane; never embed an LLM loop in `pod_pipeline` or the console. |
| D2 | Conductor + six specialists (art director, vector operator, raster operator, print verifier, blind critic, memory curator). |
| D3 | Native CLI/MCP first; Playwright/GUI only as declared fallback with read-back. |
| D4 | Six-rung evidence ladder: process → artifact → gates → render → blind critic → human. |
| D5 | Blind critic cannot see exit codes/gates/operator claims; schema requires crop evidence. |
| D6 | Four stores: hash-chained episode ledger, case retrieval, temporal brand facts, versioned skills. |
| D7 | Promotion uses a pre-declared evaluation horizon + Wilson lower bound above baseline + golden regression + human approval; ≥3 successes is only the minimum sample. **3/3 does not pass** (LB 0.4385); simulation suggests n=8/k≥7/LB>p0 as an input, not a policy. Demotion and suite size must be tested. |
| D8 | Postgres queue (`FOR UPDATE SKIP LOCKED`), no broker; new `forge` DB/role, `pod` untouched. |
| D9 | Model = bounded planner/drafter/critic; artifacts by hash on disk; never trust model-reported success. |
| D10 | No fine-tune/RL/autonomous publish in Phases 0–2. |

## Architecture

```text
DeerFlow gateway (front door / chat / checkpoints)
        │ typed TaskEnvelope
┌───────▼─────────────────────────────────────────────┐
│ Forge Conductor (systemd, 127.0.0.1:8092)            │
│  plan DAG · budgets · arbitration · verdict assembly │
└───┬──────────────┬──────────────┬────────────────────┘
    │ handoffs      │              │
┌───▼─────┐  ┌──────▼──────┐  ┌───▼───────────────┐
│ Craft   │  │ Verifier    │  │ Memory Curator    │
│ operators│ │ + critic   │  │ ledger/skills     │
└───┬─────┘  └──────┬──────┘  └───┬───────────────┘
    │               │              │
/opt/craft CLI/MCP  gates/render   Postgres `forge`
    │               │              │
    └──── /opt/pod-pipeline (unchanged) / Fourthwall ────┘
```

## Required contracts

- `TaskEnvelope`: brief, rights, apps/versions, output contract, gates, budget, approval.
- `ArtSpec`: task family, command ids, parameter ranges, artifacts, stop rules.
- `Handoff`: parent, kind, produced_by, consumed_by, payload, state, lease, attempts.
- `ToolCall`: tool/cmd, normalized params, idempotency key, result, exit, duration, refusal.
- `Artifact`: kind, path, sha256, bytes, dimensions, DPI, format, gate report.
- `VerificationVerdict`: rungs, pass/fail/unverified, reason codes, evidence hashes.
- `CritiqueReport`: blinded_to, per-dimension crop/observation/severity, confidence, unseen, verdict.
- `Skill`: preconditions, exact steps, gates, recovery, stats, version, status.

## Tool gateway rules

1. Resolve binaries by **absolute path** and `--version` probe; never by bare name (`PATH` currently
   resolves the 127-shims first).
2. One registry entry per tool; only registered tools are callable.
3. Per-role allowlist; command ids from the pinned catalogue hash.
4. Read/write roots are explicit; reject outside them.
5. Idempotency key persisted before the call; duplicate returns prior result.
6. Timeout, max attempts, named refusal codes, no silent fallback.
7. A command that writes before gating is still not a pass; verify artifacts.

## State machine

`planned → retrieving → executing → verifying → resolved` with `needs_human`, `failed`, `rolled_back`
and `refused` terminal-ish states. A retry is only for a named transient; a gate failure is not retried
with the same parameters. Promotion is a separate state transition with evidence and human approval.

## Hosting

- Loopback only: 8092 conductor, 8093 operator UI; reach via SSH tunnel.
- ≤2 episodes, one global craft-step semaphore, per-day token/cost cap, kill switch.
- Postgres `forge` role least privilege; nightly dump + restore drill.
- No secrets in prompts/logs/ledger; key names only in docs.
- Move `pod-mcp` to auth/loopback; do not expose 8765.

## Phase gates

| Phase | Deliverable | Must pass |
|---|---|---|
| 0 | fix shims, freeze 10 goldens, catalogue/version hashes, rubric | 10 goldens run honestly |
| 1 | gateway + verifier rungs 1–3 | one trace + one retouch, zero source mutation |
| 2 | ledger + handoffs + blind critic | replay episode from ledger; critic schema 100% |
| 3 | retrieval + A/B | CI report; null result disables retrieval |
| 4 | skill promotion + rollback | 3 skills with evidence; rollback drill |
| 5 | print + second app + 50 goldens | zero unsafe publishes; measured cost |
| 6 | hardening/backup/security | restore drill + runbook |

## Failure modes to design for

Stub shadowing; app/catalogue drift; missing document (`enabled:false` is state); PhotoCraft concurrent
MCP replies; gate-before-artifact; vacuous retype gate; `prep_print_art.ok` warning-only; localized
defects invisible to global SSIM; missing display; unauthenticated MCP; no token ledger; publish template
ids unset.

## Anti-patterns

- New planner/runtime; GUI-first; model-reported success; writing a skill after one run; editing the
  verifier from the agent; autonomous publish; trusting `ok:true`; loading all 918 commands.

## Output contract

Deliver a decision-complete plan: outcome, current evidence with `path:line`, decisions/alternatives,
file-by-file changes, failure modes, tests (including an error path), rollback, out-of-scope, and the
phase gate. Do not claim implementation before it exists.

## Sources

`wave2/04-HARNESS-DESIGN.md` (primary), `01`, `02`, `03`, `06`; `craft-agent-operator`; local
`routes.py`/`mcp_server.py`; DeerFlow config read-only.
