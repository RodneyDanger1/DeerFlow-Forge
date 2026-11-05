---
name: research-corpus-navigator
description: "Use when planning, coding or answering from the Ridgeboundia/DeerFlow research corpus: routes an agent to the right file/question without flooding context, enforces evidence labels and claim conflicts, and points to the 400 already-answered questions. Triggers: research corpus, what do we know, read the research, 200 questions, evidence label, claim register, prior findings, harness research."
version: 1.0.0
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [research, corpus, evidence, navigation, claims, agent]
    related_skills: [forge-harness-architect, harness-code-adapter, agent-learning-loop, visual-verification-critic, craft-agent-operator]
---

# Research corpus navigator

Read the research without drowning in it. The corpus is deliberately split so an agent loads **one
decision area**, not 400 answers. This skill is the map and the evidence discipline.

## When to use / not use

- Use before planning a harness, changing the Craft agent, or claiming what the stack supports.
- Use when someone asks “didn't we research this?” or “what did the 200 questions conclude?”
- Use when a claim needs a source label or conflicts with another report.
- Not for executing Craft commands (`artcraft-command-catalog`), MCP transport (`craft-mcp-drive`), or
  writing production code (`forge-harness-architect`).

## Corpus map

Repo root: `C:\Users\Riley\Desktop\DeerFlow Forge\research\eko-deerflow-agent\`.

| File | Load when | What it answers |
|---|---|---|
| `REPORT.md` | Eko/Craft/DeerFlow background; first 200 | Eko vs Devain vs eko-agent, Craft-vs-Adobe, memory/learning, first architecture |
| `wave2/00-START-HERE.md` | start of any wave-2 task | decision map, file map, reading orders |
| `wave2/01-STACK-VPS.md` | hosting, key, services, blockers | actual VPS state, model, stubs, argv mismatch, DB, security |
| `wave2/02-AGENT-REPOS.md` | choosing/building a harness | verified Eko/DeerFlow/Harness²/Hermes/OpenAdapt; terminology |
| `wave2/03-CRAFT-SURFACE.md` | Craft commands, MCP, gates, visual | exact counts, state semantics, roots, exit codes, critic limits |
| `wave2/04-HARNESS-DESIGN.md` | design/build Forge Conductor | roles, contracts, ledger, verifier, phases |
| `wave2/05-HARNESS-CODE.md` | donor code mechanisms | what advanced harnesses actually implement; what not to copy |
| `wave2/06-LEARNING-LOOPS.md` | memory/RL/promotion | L0–L4, evidence, reward hacking, Wilson rule |
| `wave2/07-EXAMPLES.md` | implementing a mechanism | original supervisor/tool/ledger/critic/promotion snippets |
| `wave2/08-200-QUESTIONS.md` | a specific answer | second 200, short answers + source IDs |
| `wave2/BIBLIOGRAPHY.md` | citation/source check | every URL fetched, failed retrievals |

**Do not read the entire corpus into context.** Start with `00-START-HERE.md`; then one file or one
question range. Use `grep` for `**Q123.` to fetch a single answer.

## Read order by task

| Task | Order |
|---|---|
| “Can the VPS run this?” | 01 → 03 §3–4 → 04 §2/§10 |
| “Which harness should we use?” | 02 §2–5 → 04 §1/§11 → 06 §7 |
| “Why doesn't the pipeline run?” | 01 §1/§15 → 03 §3 → local `routes.py` |
| “How do we learn from runs?” | 06 §1–3/§8–10 → 04 §8–9 → 07 example 3/5 |
| “How do we judge art?” | 03 §5–6 → 04 §7 → 05/07 visual example |
| “What did the 400 questions say?” | first `REPORT.md` Q1–200, then `08-200-QUESTIONS.md` Q1–200 |

## Evidence rules

Use the corpus labels, never invent a fifth:

- `[V]` / `VERIFIED` — command executed or source read this wave.
- `[R]` / `READ` — file read, not executed.
- `[D]` / `PROPOSED` — design decision; not implemented.
- `[U]` / `UNVERIFIED` — could not prove; name what would.
- `NOT FOUND` / `NOT DOCUMENTED` — official sources silent; do not fill.

Rules:
1. A claim that changes a decision needs a source/path and a label.
2. If two files disagree, prefer the live primary source and record the conflict; do not average.
3. A design item is not a capability; never say “implemented” because a design file exists.
4. A vendor/paper number is not an independent reproduction.
5. Anything older than the freshness rule is `HISTORICAL`, not current.

## Claim-register protocol

For each material claim record: `claim_id`, verbatim claim, location, type, source/path, fetched date,
status (`VERIFIED`/`VAULT-RECORDED`/`UNVERIFIED`/`CONTRADICTED`), and what would settle it. The corpus
already has a claim register in `REPORT.md` and evidence sections in each wave-2 file; append, do not
rewrite.

## Maintenance

- Add a new wave/file for new research; **never delete an old answer** or silently change a conclusion.
- Put corrections in `wave2/ERRATA.md` with date and replacing source.
- Re-fetch before changing a policy (model/app/DeerFlow version).
- Update `INDEX.json` and the START-HERE map whenever a file is added.

## Anti-patterns

- Pasting all 400 questions into the prompt.
- Quoting a README as proof of runtime behaviour.
- Treating `[D]` design as `[V]` implementation.
- Hiding a contradiction by choosing the convenient source.
- Citing a URL you did not fetch.

## Output contract

Return: the one file/question you used, the claim(s) with labels, conflicts found, gaps, and the
implication for the task. Point to exact paths; do not paraphrase a whole report.
