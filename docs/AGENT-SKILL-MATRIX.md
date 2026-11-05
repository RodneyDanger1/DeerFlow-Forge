# Agent skill matrix — when, where, why

This file is part of the operating contract for the Forge plan. The plan is in
`research/eko-deerflow-agent/README.md`, `execution-wave/09-GOAL-GAP-PLAN.md`, and
`docs/PLAN-CONTINUATION.md`.

| Moment | Skill | Use it for | Do **not** use it for |
|---|---|---|---|
| Before any W2 edit | `forgewright-recon` | frame behavior, read entry/callers/tests, write a recon ledger | repository tours or guessing callers |
| Before any mutation | `logic-gatekeeper` | Phase 1 JSON: architecture, data flow, edge cases, root cause | after the patch, or for an explanation-only task |
| Any bug/failing gate | `logic-debugger` | invariants, deterministic RED, fault injection, replay/lease truth | cosmetic changes or test weakening |
| Runtime repair | `forge` | root-cause localization, minimal diff, RED→GREEN, error-path closure | writing the plan or the architecture |
| Lead integration | `forgewright-lead` | research → root cause → gate → implement → run → evidence-check | delegating ownership of the final test run |
| Capability claims | `capability-auditor` | agent/tool allowlist vs registry, manifest truth, routing/refusals | adding a tool just because a doc lists it |
| Tool contract | `agent-native-design` | stdout JSON, exit codes, schema/introspection, dry-run, delegated auth | designing business logic or GUI layout |
| Integration seams | `integration-logic` | UI/client → route → service → tool → store → response; refusal matrix | replacing a missing provider with a mock |
| Memory/learning | `agent-learning-loop` | L0–L4 claim, episode/retrieval/skill/promotion/rollback, A/B | claiming “it learns” from a single run or 3/3 |
| Agent-facing UI | `agent-experience` | minimal context, progressive disclosure, bounded outputs, locality | marketing copy or unverified capability claims |
| Evidence | `evidence-check`, `evidence-gap-audit` | every claim has a source; classify OK/WEAK/MISSING/CONFLICT/U | inventing proof or backfilling history |
| Visual/UI trace | `trace`, `visuals` | control inventory, render→handler→effect, screenshots/console/network | claiming a click when only source was read |
| Mermaid | `mermaid-skill` | diagrams-as-code, validation, export | pixel-precise art |

## W2 use

1. **Recon first:** target = add the Forge Conductor’s local skeleton (DDL, tool gateway, transition/refusal/idempotency tests); read `execution-wave/02-FORGE-SKELETON.md`, `ARCHITECTURE.md`, `04-HARNESS-DESIGN.md`, `execution-wave/09` §5.2, and the existing `pod_pipeline` DB patterns.
2. **Gate:** write `logic-gatekeeper` Phase 1; no schema/service write before it.
3. **Implementation order:** pure gateway + tests → DDL → queue/lease → service; no publish, no production.
4. **Learning:** use `agent-learning-loop` only for the evaluation/promotion part; W2 is not a learning claim.
5. **Capability:** every new tool/agent must appear in a generated registry/allowlist test; no “documented but uncallable” additions.
6. **Evidence:** update `10-CLAIM-REGISTER` and write a W2 receipt; no claim without a command/output.

## Current gate decision

G0: **artifact consistency PASS**, **execution provenance U**. W2 may proceed only as local,
non-deployed source if the owner accepts that provenance caveat; otherwise wait for verifier VPS
read-only access. No production change either way.
