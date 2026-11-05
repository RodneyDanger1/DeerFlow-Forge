---
name: craft-agent-operator
description: "Use when an AI agent must plan, execute, verify and learn from a real ArtCraft/Craft production job: retrieve similar cases, choose exact command ids, run on copies, verify artifacts and gates, record an experience episode, and propose only evidence-backed lessons. Triggers: Craft agent, design agent, autonomous design, agent memory, experience ledger, learn from run, improve design workflow, Eko/DeerFlow operator, design agent protocol."
version: 1.0.0
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [agent, craft, vectorcraft, photocraft, filmcraft, memory, evaluation, orchestration, eko, deerflow]
    related_skills: [artcraft-command-atlas, craft-mcp-drive, apparel-print-master, ai-art-vectorize-vectorcraft, artcraft-vector-trace, artcraft-image-cleanup, artcraft-photocraft-layers]
---

# Craft agent operator

The operating protocol for an AI agent doing real Craft production work: **plan from evidence, execute
exact commands, verify the artifact, record the episode, and promote a lesson only after repeated
success**. This is not a claim that the agent is trained; it is the loop that makes improvement
measurable.

## When to use / not use

- Use when an agent must complete a design job end-to-end (vector, raster, print master, layout, film).
- Use when adding memory/learning to DeerFlow Forge or an Eko/DeerFlow orchestrator.
- Use when deciding whether a past run's lesson should become a reusable skill.
- Not for a single command lookup (`artcraft-command-atlas`), MCP transport only (`craft-mcp-drive`), or
  autonomous storefront publishing (requires explicit owner approval).

## Non-negotiable boundaries

1. **No source overwrite.** Work on a copy; write a new output path.
2. **No invented ids/params.** Query the catalogue; read the full schema.
3. **No success without evidence.** Exit 0 is not proof; verify the artifact and gates.
4. **No autonomous publish.** Prepare, verify, then request human approval.
5. **No self-promoting memory.** A lesson/skill is a draft until evaluated and approved.
6. **No training claim.** Retrieval/skills are not weight training; say which one is being used.
7. **No pixel-only shortcut** when a typed command exists; use computer-use only for UI-only gaps.
8. **No rights violations.** Record asset licences/provenance before use.

## Preflight (every run)

Record in the episode envelope:

- Brief: one sentence of intent, audience, deliverable, owner-approved claims.
- Rights: source asset licence/provenance; customer-art confidentiality.
- App + version: VectorCraft 0.21.1, PhotoCraft 0.20.2, FilmCraft build, etc.
- Output contract: path, format, dimensions, DPI, colourspace, provider template/area.
- Verification: which gates apply (`craft_trace`, `prep_print_art`, print master, custom PDF checks).
- Budget: max steps, max retries, max wall-clock, cost ceiling.
- Approval: who signs off print/publish/store changes.

If a field is missing, ask; do not invent. Name the missing field in the refusal.

## Loop

`brief → retrieve → plan → execute → verify → record → reflect → propose → (human) promote`

### 1. Retrieve

Use the narrowest source that answers the question:

- Exact command/param: `artcraft-command-atlas` `references/command_lookup.py`.
- Similar past job: episode index by app + task family + brand + product.
- Constraints: brand kit, provider template, printer/DTG rules, prior gate failures.
- Known traps: `command-tips.md`, skill pitfalls, prior episode `failure_code`.

Return bounded evidence (ids, paths, gate values), not whole logs. If no case is similar, say so.

### 2. Plan

- Choose the **task family** and the app(s); state why.
- List the command ids and parameter ranges from the catalogue.
- State the verification for each step and the stop condition.
- Prefer deterministic commands over browser/computer-use.
- For a multi-app job, define the artifact contract at each handoff (SVG → print PNG → mockup).
- If the plan needs a capability that does not exist, stop and escalate; do not fake it.

### 3. Execute

- Run one step at a time on a copy; parse the JSON envelope/result.
- For CLI: use the exact command from `artcraft-command-catalog`/atlas.
- For MCP: use `craft-mcp-drive`; pass both read/write roots; never run unconfined.
- After each destructive step, re-inspect the artifact; do not chain blindly.
- On a named refusal, stop and classify; retry only a proven transient failure.

### 4. Verify

Minimum evidence per run:

- Command exit + JSON result (not just stdout prose).
- Artifact exists, non-zero, expected format.
- Dimensions/DPI/colourspace (`identify` or equivalent).
- The applicable gate report (`craft_trace` ten gates, `prep_print_art` coverage/upscale, print geometry).
- Visual check at 100% and thumbnail; compare against the brief.
- For writes/publish: read back the actual record/product state.
- For text: retype evidence (boxes > 0, font resolves, overlay covers).

If any check fails, mark the episode failed and preserve the evidence. Never edit a report to pass.

### 5. Record

Write one append-only episode record (JSON/DB row) with:

```json
{
  "episode_id": "uuid",
  "brief": "...",
  "task_family": "ai_badge_trace",
  "apps": [{"name": "VectorCraft", "version": "0.21.1"}],
  "rights": {"source": "...", "licence": "..."},
  "plan": {"steps": ["imageTrace.make", "imageTrace.expand"]},
  "actions": [{"seq": 1, "tool": "vectorcraft-cli run", "params": {}, "result": {}, "duration_ms": 0}],
  "artifacts": [{"path": "/tmp/art.svg", "sha256": "...", "w": 2400, "h": 3000, "dpi": 300}],
  "evaluation": {"ok": true, "gates": {}, "human": null},
  "outcome": "verified",
  "failure_code": null,
  "cost": {"model_tokens": 0, "wall_s": 0}
}
```

The full schema and promotion rule are in `references/memory-ledger.md`.

### 6. Reflect

Only after verification:

- What was the actual cause of any retry/failure?
- Which parameter range/ordering mattered?
- Was the quality issue technical (gate) or taste (human)?
- What would make the next run cheaper or more reliable?

Write a **candidate** lesson, not a fact. Include evidence episode ids and confidence.

### 7. Propose / promote

A candidate becomes active only when:

- at least **3 independent episodes** succeed with it (start N=3),
- the golden regression suite passes,
- a human/quality owner approves,
- it is versioned and has a rollback.

Never rewrite an active skill in place; create a new version. Demote on failure/regression. Record why.

## Tool selection

| Need | First tool | Fallback |
|---|---|---|
| Find command id/params | atlas lookup | catalogue `commands --json` |
| Run a command/batch | Craft CLI | MCP `command_batch` |
| Inspect document | app `info`/`document.inspect` | render preview |
| Verify print | `craft_trace`/`prep_print_art` report | `identify` + visual |
| Plan/execute multi-step | Craft Conductor / DeerFlow / Eko | scripted CLI |
| Web-only admin/storefront | Playwright MCP | browser-use |
| Repeat a stable UI task | compiled program (OpenAdapt pattern) | agent replay |
| Persist experience | Episode Ledger | JSONL files (temporary) |

## Evidence contract

Return, at minimum:

- brief and rights decision;
- app/version and command ids actually used;
- artifact paths, hashes, dimensions/DPI/format;
- gate table and pass/fail;
- human rating/approval state;
- `UNVERIFIED` list;
- episode id + lesson candidates (if any).

A mockup, a screen render, or an exit code is not print proof.

## Refusals / escalation

Stop and name the cause when:

- missing rights, brief, provider geometry, font, template, or approval;
- command id absent or parameter rejected;
- gate fails after one documented retry;
- upscale >2.5× or source below ~150 px per print inch;
- AI text without a retype path;
- batch collision without naming;
- publish/print would occur without human approval;
- a requested “lesson” lacks evidence;
- the model/harness cannot be verified.

## Anti-patterns

- “The command exited 0, so it worked.”
- Tracing AI lettering or reusing another design's retype boxes.
- Calling a screen render print proof.
- Writing a lesson from one lucky run.
- Editing the gate report or thresholds to pass.
- Loading the entire atlas into context instead of one lookup.
- Treating Eko's `task_snapshot` or DeerFlow facts as trained design skill.
- Letting a UI-only agent drive a command-capable app.

## Worked example (abbreviated)

1. Brief: 8 in AI badge on a 2400×3000 print canvas; rights confirmed.
2. Lookup: `craft_trace`, `imageTrace.make`, `type.createOutlines` via atlas.
3. Plan: cutout → trace limited palette → expand → SVG → render → retype → ten gates.
4. Execute on `/tmp/art.png`; stop if any gate fails.
5. Verify: `ok:true`, 2400×3000 at 118.11 px/cm, retype boxes >0.
6. Record episode; compare with prior `ai_badge_trace` cases.
7. Candidate lesson: “noise 12→20 fixed specks on this source family”; wait for 3 successes.
8. Human reviews the artifact; only then can the lesson become a skill version.

## Sources & verification

- **VERIFIED:** Craft command counts/gates from the local catalogue and `craft_trace` source; MCP
  roots/protocol from `craft-mcp-drive`; Eko architecture source (planner/tree/memory/snapshot);
  DeerFlow memory docs; OpenAdapt verify/read-back claims; Adobe/Craft compatibility docs.
- **PROPOSED:** ledger schema, promotion N=3, metrics and 90-day plan. These are design decisions, not
  deployed behaviour; mark them as such until a migration/tests exist.
- **DETAIL:** `references/memory-ledger.md`, `references/evaluation.md`; command depth in
  `artcraft-command-atlas`; transport in `craft-mcp-drive`.
