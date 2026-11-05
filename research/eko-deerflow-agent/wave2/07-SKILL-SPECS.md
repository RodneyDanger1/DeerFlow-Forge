# 07 — Five Skill Specifications for the Forge Research Corpus

**Wave 2 · Task 07 · Skill specifications (draft, not installed) · 2026-11-05**
Owner: Riley · Author: `examples-skills-packager` (delegated) · Scope: using the Eko/Craft/DeerFlow research corpus

> **Status: SPECIFICATIONS, NOT PRODUCTION SKILLS.** Nothing here is installed in `~/.dsh/skills`.
> No production file, migration, unit or prompt was created. Each skill is specified as a
> `draft` version (`0.1.0-draft`), with trigger text, section plan, references, dependencies and a
> concise `SKILL.md` skeleton. Installation is a separate, reviewed action.
>
> These skills are the **usage layer** for the research corpus. They do not contain the research;
> they route to it, constrain how it is read, and turn it into design, adaptation, learning and
> verification work. `07-EXAMPLES.md` supplies the mechanism examples they cite.

---

## 0. Purpose, boundaries and conventions

### 0.1 Why five skills

The corpus is now **two 200-question sets** (`REPORT.md` Q1–Q200 and `wave2/08-200-QUESTIONS.md`
Q1–Q200), six mechanism examples and five skill specifications, on top of the wave2 source files.
Reading it ad hoc causes two failures: **context flooding** (dumping whole reports into the prompt) and
**evidence drift** (quoting an unverified claim as policy). Each skill below owns one recurring job and
one narrow contract:

| # | Skill | Job | Primary corpus | Depends on |
|---|---|---|---|---|
| 1 | `research-corpus-navigator` | answer from the corpus with bounded, labelled citations | `README.md`, `REPORT.md`, `wave2/01–08` | — |
| 2 | `agent-harness-architect` | design/build a harness from verified constraints | `04-HARNESS-DESIGN.md`, `07-EXAMPLES.md`, `01` | 1, 3 |
| 3 | `harness-code-adapter` | source mechanisms from donor repos safely | `05-HARNESS-CODE.md`, `02-AGENT-REPOS.md` | 1 |
| 4 | `agent-learning-loop` | memory, evaluation, skill promotion and rollback | `06-LEARNING-LOOPS.md`, `04 §8–9`, `07` ex. 3/5/6 | 1, 2 |
| 5 | `visual-computer-use-verifier` | verify screens, artifacts and rendered evidence | `04 §7`, `03-CRAFT-SURFACE.md`, `07` ex. 4 | 1, `craft-mcp-drive` |

### 0.2 What these skills must not do

- Do not duplicate installed skills. `craft-agent-operator` already owns the Craft execution loop
  and its ledger/evaluation references; `artcraft-command-atlas` owns command lookup;
  `craft-mcp-drive` owns MCP transport; `deep-research`, `evidence-gap-audit`, `source-verification`,
  `claim-register-builder` and `capability-auditor` own research discipline. The five skills below
  also have installed or adjacent counterparts — see §0.5 before installing any of them.
- Do not copy research text into a skill. Cite `path:line` and return an evidence packet.
- Do not install anything, run unpinned code, or touch production.
- Do not claim "learning", "verified", "measured" or "better than human" without the specific
  evidence named in the corpus.
- Do not put secrets in prompts, logs, examples or skill files; read credentials at runtime by name.

### 0.3 Shared format

Every SKILL.md follows the installed convention (`~/.dsh/skills/craft-agent-operator/SKILL.md`):
YAML frontmatter (`name`, `description` with trigger words, `version`, `author`, `license`,
`platforms`, `metadata.hermes.tags` and `related_skills`), then bounded sections, then
`references/` for depth. Target size ≤ 250 lines; progressive disclosure into `references/` when a
topic needs more. `description` must say **when** to use the skill, because that is what routing
sees.

### 0.4 Shared acceptance rule

A skill is ready to install only when: (a) trigger tests route the intended prompts to it and not
to a sibling skill; (b) a dry run on three real corpus questions produces the stated output shape
within the token budget; (c) it contains no secrets and no unpinned commands; (d) the author can
point to the file and line of every claim it makes about the corpus.

### 0.5 Relationship to installed skills (read before installing)

Five related skills are already installed at v1.0.0 under `~/.dsh/skills` (also copied in the repo
under `blueprint/files/skills/`). These five specifications are drafts for the **research-corpus
usage layer**, not accidental replacements. Installation must be a reviewed update/merge, not an
overwrite:

| This spec | Installed v1.0.0 | Relationship and install rule |
|---|---|---|
| `research-corpus-navigator` | same name (101 lines) | Draft update: adds `wave2/08`, the evidence-packet contract and explicit budgets; diff before replacing |
| `agent-harness-architect` | `forge-harness-architect` (142 lines) | Adjacent generic version; triggers overlap. Prefer the installed skill for Forge-specific work until the two are merged; never install both without a routing test |
| `harness-code-adapter` | same name (114 lines) | Draft update: corpus references and licence gate; diff before replacing |
| `agent-learning-loop` | same name (118 lines) | Draft update: adds `07` Examples 3/5/6 as mechanism references; diff before replacing |
| `visual-computer-use-verifier` | `visual-verification-critic` (121 lines) | Adjacent: this draft adds GUI fallback and system-of-record read-back; merge into the installed skill or keep one, with a routing test |

The names above are the task's names. The Lead owns the naming/merge decision; nothing here installs,
overwrites or edits an existing skill.

---

## 1. `research-corpus-navigator`

### 1.1 Identity

| Field | Value |
|---|---|
| **Name** | `research-corpus-navigator` |
| **Version** | `0.1.0-draft` |
| **Description** | "Use when a question must be answered from the Eko/Craft/DeerFlow research corpus (`REPORT.md` and `wave2/01–07`): route to the narrowest source, read it in bounded slices, and return labelled evidence with exact citations instead of pasting whole reports. Triggers: what did we verify, corpus question, dossier, research report, wave2, evidence lookup, claim check, unverified." |
| **License** | original (DeerFlow Forge) |
| **Writes** | none — read-only skill |

### 1.2 When to use / not use

| Use | Do not use |
|---|---|
| Any question answerable by the corpus ("what did we verify about X?", "which file covers Y?") | Live host facts — probe the host and read `01-STACK-VPS.md`; the corpus is a 2026-11-05 snapshot |
| Before designing or building from the research (feed the other four skills) | A single command/param lookup — use `artcraft-command-atlas` |
| Checking whether a claim exists, what label it carries, and what contradicts it | Production implementation — use the relevant engineering workflow |
| Preparing a decision summary for the owner | Open-ended new research — use `deep-research` first, then file the result into the corpus |
| Deciding whether a planned number/capability is `[V]`, `[R]`, `[I]` or `[U]` | Quoting a dossier claim as verified when the corpus already says it is not |

### 1.3 Sections (8)

| § | Section | Content |
|---|---|---|
| 1 | Corpus map | `REPORT.md` parts Q1–Q200; `08-200-QUESTIONS.md` Parts A–J with short answers mapped to source IDs S1–S7; wave2 files 01–07 for depth; JSON companions; which file answers which class of question |
| 2 | Question routing | Classify as fact / design / donor-code / learning / verification / unknown; pick the narrowest file and section; only widen when the narrow read is insufficient |
| 3 | Bounded reading protocol | Headings first (`^## `), then one section; ≤200 lines per read step; grep for terms; never load a whole 70 KB report into context |
| 4 | Evidence labels and precedence | `[V]` / `[R]` / `[D]` / `[I]` / `[U]`; stricter session label wins; a later unverified claim never overrides a verified one; contradictions are reported, not averaged |
| 5 | Evidence packet contract | ≤1,200 tokens: answer ≤5 sentences, citations `path:line`, labels, confidence `high/medium/low`, `contradicts[]`, `next_check[]`, `not_in_corpus[]` |
| 6 | Context budget and progressive disclosure | Return ids and one-line summaries; open a file only when its section is load-bearing; use JSON companions for structured facts |
| 7 | Freshness and gaps | Corpus date; host facts expire; wave2 files may be in flight; `[U]` items remain open until the named check exists |
| 8 | Refusals | Missing file, conflicting claims, question outside corpus, stale host fact → say so; never fill a gap with plausible text |

### 1.4 References needed

| Path | Use |
|---|---|
| `research/eko-deerflow-agent/README.md` | reading order and the short answer |
| `research/eko-deerflow-agent/REPORT.md` | 200 questions, Parts 1–10, bibliography, claim register, UNVERIFIED list |
| `research/eko-deerflow-agent/wave2/08-200-QUESTIONS.md` | second 200 questions (Parts A–J) with short answers and source IDs S1–S7; fastest route for a direct question |
| `research/eko-deerflow-agent/wave2/01-STACK-VPS.md` + `01-VPS-FACTS.json` | host, repo, deploy, MCP, Craft install, tests |
| `research/eko-deerflow-agent/wave2/02-AGENT-REPOS.md` + `02-REPOS.json` | Eko/DeerFlow/browser-use/Agent-S/UI-TARS/OpenAdapt/Playwright MCP verification |
| `research/eko-deerflow-agent/wave2/03-CRAFT-SURFACE.md` + `03-SURFACE.json` | command/MCP/visual surfaces, gates, GUI feasibility |
| `research/eko-deerflow-agent/wave2/04-HARNESS-DESIGN.md` + `04-DESIGN.json` | Forge Conductor design, contracts, ledger, eval |
| `research/eko-deerflow-agent/wave2/05-HARNESS-CODE.md` + `05-CODE.json` | donor mechanisms, code pointers, what not to copy |
| `research/eko-deerflow-agent/wave2/06-LEARNING-LOOPS.md` + `06-LEARNING.json` | memory/learning/RL research |
| `research/eko-deerflow-agent/wave2/07-EXAMPLES.md` + `07-EXAMPLES.json` + `07-SKILL-SPECS.md` | mechanism examples and these skills |
| `~/.dsh/skills/craft-agent-operator/references/{memory-ledger,evaluation}.md` | installed ledger/eval memory contracts |

### 1.5 Dependencies

| Kind | Value |
|---|---|
| Required | none (read-only) |
| Consumes | the corpus files above; JSON companions when machine-readable facts are needed |
| Related skills | `deep-research`, `evidence-gap-audit`, `source-verification`, `claim-register-builder`, `capability-auditor` |
| Used by | `agent-harness-architect`, `harness-code-adapter`, `agent-learning-loop`, `visual-computer-use-verifier` |

### 1.6 SKILL.md skeleton

```markdown
---
name: research-corpus-navigator
description: "Use when a question must be answered from the Eko/Craft/DeerFlow research corpus (REPORT.md + wave2 01–07): route to the narrowest source, read it in bounded slices, return labelled evidence with citations. Triggers: what did we verify, corpus, dossier, research report, wave2, evidence lookup, claim check, unverified."
version: 0.1.0-draft
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [research, evidence, citations, corpus, deerflow, craft]
    related_skills: [deep-research, evidence-gap-audit, source-verification, claim-register-builder, craft-agent-operator]
---

# Research corpus navigator

## When to use / not use
- Use for corpus questions, claim checks, decision summaries, and pre-design evidence.
- Not for live host facts, single command lookups, or new research.

## 1. Corpus map
- REPORT.md: Parts 1–10, Q1–Q200; bibliography; claim register; UNVERIFIED.
- wave2/01 host+repo+deploy · 02 donor repos · 03 Craft surfaces · 04 harness design ·
  05 donor mechanisms · 06 learning loops · 07 examples + skill specs · 08 the wave2 200 answers.
- 08: short answers (Parts A–J) with source IDs S1–S7; use it for a direct question, then follow
  the source ID into the depth file.
- JSON companions mirror the facts; prefer them for structured values.
- Installed skills: craft-agent-operator (loop), artcraft-command-atlas (commands),
  craft-mcp-drive (MCP).

## 2. Question routing
- Classify: host fact | repo fact | design decision | donor mechanism | learning/eval |
  verification | unknown.
- Pick the narrowest file; read its headings, then one section.
- Widen only if the narrow read lacks the answer; record why you widened.

## 3. Bounded reading protocol
- `^## ` headings first; then read one 100–200 line window.
- Grep the term; quote ≤3 lines per citation.
- Never inject a whole file >8k tokens; never open two large files at once.
- Prefer the JSON companion for numbers, paths, versions.

## 4. Evidence labels
- `[V]` verified this session; `[R]` read from repo; `[D]` dossier (not re-run);
  `[I]` inference/design; `[U]` unverified.
- Precedence: V > R > D > I > U. Never upgrade a label.
- Conflicting claims are reported side by side; never averaged.

## 5. Evidence packet
Return ≤1,200 tokens:
- answer (≤5 sentences)
- citations: `path:line` per claim
- labels per claim
- confidence: high | medium | low
- contradicts[] (paths + labels)
- next_check[] (the exact test/probe that would close a gap)
- not_in_corpus[] (what the corpus does not answer)

## 6. Context budget
- One-line summaries + ids, not transcripts.
- Progressive disclosure: open `references/` only when needed.
- For multi-file synthesis, write a small index first and cite it.

## 7. Freshness and gaps
- Corpus snapshot 2026-11-05; host facts expire.
- Wave2 files may be in flight; check for existence and last write time.
- `[U]` stays open until the named check is run.

## 8. Refusals
- Missing file or section → say which, do not substitute.
- Outside corpus → say so, recommend deep-research.
- Stale host fact → re-probe or mark stale.

## Anti-patterns
- Pasting a 50 KB report; citing a dossier claim as verified; inventing a source;
  answering from memory; ignoring the UNVERIFIED list.

## Sources & verification
- Corpus paths above; evidence labels and rules from REPORT.md and 04 § evidence registers.
```

### 1.7 Acceptance tests

1. "What did we verify about the installed Craft apps?" → ≤800 tokens, cites `04 §2.3` and
   `01 §10`, marks FilmCraft/DesignCraft absent `[V]`, does not read the full design file.
2. "Is the 393,216 output-token figure real?" → returns `[U]`/absent from corpus, points to the
   global contract's claims register, does not adopt the number.
3. "Which mechanisms should we copy from OpenHands?" → routes to `05` and
   `harness-code-adapter`, refuses to answer from the dossier alone if 05 is missing.

---

## 2. `agent-harness-architect`

### 2.1 Identity

| Field | Value |
|---|---|
| **Name** | `agent-harness-architect` |
| **Version** | `0.1.0-draft` |
| **Description** | "Use when designing or building an agent harness (supervisor, specialists, typed tool gateway, ledger, verification, memory, evaluation) from verified constraints: produce architecture, contracts, failure taxonomy and a phased plan before code. Triggers: harness design, agent architecture, Forge Conductor, build vs integrate, supervisor loop, tool gateway, design an agent, eval plan." |
| **License** | original (DeerFlow Forge) |
| **Writes** | design documents and contracts only; no production code without a separate build task |

### 2.2 When to use / not use

| Use | Do not use |
|---|---|
| Designing the Forge Conductor or any agent harness around the Craft tools | A single feature/bug fix in an existing harness |
| Deciding build vs integrate vs reuse from verified repo facts | When the corpus has not been read (use skill 1 first) |
| Writing contracts, state machines and refusal taxonomies | As a substitute for implementation; this skill ends at a gated plan |
| Reviewing a proposed architecture for missing verification/memory | When the owner wants "an agent that just does X" with no system around it — scope it first |
| Planning phases, gates and ops for a hosted harness | Claims of measured performance; those belong to the eval loop |

### 2.3 Sections (8)

| § | Section | Content |
|---|---|---|
| 1 | Intake and requirement map | Brief, deliverables, roles, surfaces, constraints, non-goals; flag requirements the corpus cannot support |
| 2 | Constraint baseline | Host capacity, model id/limits, installed app versions, ports, DB, budgets; every value labelled and dated |
| 3 | Architecture options | Build vs reuse table; three-plane separation; conductor + specialists; queue; tool gateway; GUI fallback boundary |
| 4 | Contracts | Versioned JSON shapes for envelope, handoff, tool result, gate report, critique, skill, eval; schema first, code second |
| 5 | State, failure and refusals | Episode state machine; transient vs terminal; named `E_*` codes; arbitration matrix |
| 6 | Memory, verification and evaluation | Evidence ladder; four stores; promotion/rollback; golden set and A/B; honest "learning" definition |
| 7 | Phased plan with gates | Phase 0 baseline → gateway → ledger/critic → retrieval → skills → hardening; each gate is evidence, not a date |
| 8 | Ops and security | Units, least privilege, loopback-only, secrets by name, backup/restore, rollback drill, cost caps |

### 2.4 References needed

| Path | Use |
|---|---|
| `wave2/04-HARNESS-DESIGN.md` | primary design: decisions, roles, contracts, ledger, tool layer, ladder, eval, ops |
| `wave2/01-STACK-VPS.md` + `01-VPS-FACTS.json` | verified host/repo/model/app facts; traps (127 shims) |
| `wave2/07-EXAMPLES.md` | mechanisms for supervisor, gateway, ledger, critic, promotion, eval |
| `wave2/05-HARNESS-CODE.md` | donor mechanisms and what not to copy (for the adapter decision) |
| `wave2/06-LEARNING-LOOPS.md` | memory/learning design constraints |
| `wave2/02-AGENT-REPOS.md`, `03-CRAFT-SURFACE.md` | verified donor repos and Craft surfaces |
| `~/.dsh/skills/craft-agent-operator/SKILL.md` | execution loop the harness must support |
| `~/.dsh/skills/craft-mcp-drive/SKILL.md` | MCP transport, roots, tool inventory |

### 2.5 Dependencies

| Kind | Value |
|---|---|
| Required | `research-corpus-navigator` (evidence), `harness-code-adapter` (donor code) |
| Optional | `agent-learning-loop` (memory/eval contracts, once installed), `visual-computer-use-verifier` (verification design), `craft-mcp-drive` (tool surface) |
| Produces for | build tasks, migration plans, eval plans |
| Related | `capability-auditor`, `integration-logic`, `logic-gatekeeper`, `forgewright-plan` |

### 2.6 SKILL.md skeleton

```markdown
---
name: agent-harness-architect
description: "Use when designing or building an agent harness (supervisor, specialists, typed tool gateway, ledger, verification, memory, evaluation) from verified constraints: architecture, contracts, failure taxonomy, phased plan. Triggers: harness design, agent architecture, Forge Conductor, build vs integrate, supervisor loop, tool gateway."
version: 0.1.0-draft
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [agent, architecture, harness, orchestration, contracts, deerflow, craft]
    related_skills: [research-corpus-navigator, harness-code-adapter, agent-learning-loop, visual-computer-use-verifier, craft-mcp-drive]
---

# Agent harness architect

## When to use / not use
- Use for architecture, contracts, failure taxonomy and phased plans.
- Not for single features, and not before the corpus evidence is read.

## 1. Intake and requirement map
- State deliverable, roles, surfaces, constraints, non-goals.
- Map each requirement to a capability and a gate; list gaps explicitly.

## 2. Constraint baseline
- Host, model, apps, ports, DB, budgets — labelled `[V]/[R]/[D]/[U]` and dated.
- Name the traps (PATH shims, absent apps, output-token cap, shared 2-vCPU host).

## 3. Architecture options
- Default: three planes (console, deterministic pipeline, new forge plane), not one monolith.
- Conductor + capability-scoped specialists; typed handoffs over a queue, not chat.
- Native CLI/MCP first; GUI only as a declared fallback with read-back.
- Decide build vs reuse per component; write the decision down.

## 4. Contracts
- Version every shape: TaskEnvelope, ArtSpec, CommandBatch, GateReport,
  CritiqueReport, Skill, EvalReport.
- Schema first; add `schema_version`; reject unknown fields at boundaries.

## 5. State, failure and refusals
- Episode state machine with guards; every transition writes an event.
- Transient vs terminal; named `E_*` codes with how_to_fix.
- Arbitration matrix: gate fail ≠ critic pass; missing rung → unverified.

## 6. Memory, verification and evaluation
- Evidence ladder (process → artifact → gates → render → critic → human).
- Four stores: ledger, cases, brand facts, skills; append-only ledger.
- Golden set with private held-out; promotion needs independent successes + goldens +
  human sign-off; rollback is a pointer flip.
- "Learning" means retrieval/skills unless a measured held-out gain exists.

## 7. Phased plan with gates
- Each phase has an evidence gate; no schedule confidence without measurement.
- Baseline first (honest pass/fail), then gateway, ledger/critic, retrieval,
  skills, hardening.

## 8. Ops and security
- Loopback binds, least-privilege users, secrets by name, no new public ports.
- Backup/restore and rollback drills are part of done.
- Cost caps and concurrency sized to the measured host.

## Refusals
- No fabricated numbers; no "better than human" claim; no autonomous publish;
  no fine-tuning/RL before the eval harness exists.

## Sources & verification
- 04 (primary), 01 (host facts), 05 (donor mechanisms), 06 (learning), 07 (examples),
  craft-agent-operator, craft-mcp-drive.
```

### 2.7 Acceptance tests

1. "Design a harness for the Craft apps." → produces architecture + contracts + failure
   taxonomy + phased gates, cites `04` decisions, names the 127-shim trap and absent apps,
   and does not propose a new framework.
2. "Should we fork DeerFlow or build our own?" → answers from `04 §11` with a build-vs-reuse
   table, labels confidence, and names what must be built either way.
3. "Write the supervisor code." → refuses to jump to code; emits contracts and points to
   `07` Example 1 as the mechanism, then a build task.

---

## 3. `harness-code-adapter`

### 3.1 Identity

| Field | Value |
|---|---|
| **Name** | `harness-code-adapter` |
| **Version** | `0.1.0-draft` |
| **Description** | "Use when sourcing or adapting mechanisms from donor agent repositories (OpenHands, SWE-agent, Aider, Cline, Goose, Open Interpreter, Codex/Claude-style harnesses, Playwright MCP, UI-TARS/Agent-S, Eko, DeerFlow): verify licence and provenance, extract the mechanism, reimplement it originally, and record attribution and a removal path. Triggers: borrow mechanism, adapt code, donor repo, fork vs reimplement, code donation, port from OpenHands, adapter." |
| **License** | original (DeerFlow Forge) |
| **Writes** | adaptation notes, provenance records, original code; never verbatim proprietary code |

### 3.2 When to use / not use

| Use | Do not use |
|---|---|
| A donor repo has a mechanism the harness needs (loop, gateway, compaction, checkpoints, sandbox, eval) | The mechanism can be specified from `04`/`07` without a donor — do that first |
| Deciding adapter vs fork vs vendor vs reimplement | Licence is unknown or restricts use; stop at the licence gate |
| Recording source commit, licence, attribution and removal path | Copying code into production without a reviewed, original implementation |
| Building parity/failure tests for an adapted mechanism | Treating a donor's benchmark or star count as evidence it works here |

### 3.3 Sections (8)

| § | Section | Content |
|---|---|---|
| 1 | Donor intake | Repo, commit SHA, language/runtime, last activity, licence file, maintenance signals, exact file:line pointers |
| 2 | Licence and provenance gate | Licence compatibility, attribution duties, copyleft boundaries, no code without a recorded licence and commit |
| 3 | Mechanism extraction | Describe behaviour, invariants, state, failure modes and dependencies in prose before touching code |
| 4 | Integration decision | Adapter (call it), fork (own it), vendor (pin it), or reimplement (rewrite); weigh maintenance, licence, runtime, coupling |
| 5 | Original implementation and parity tests | Reimplement the mechanism in this repo's language/contracts; parity cases + failure injection; no copied bodies |
| 6 | Attribution record | `references/donors.md`: repo, URL, commit, licence, files read, what was extracted, what was changed |
| 7 | Removal and rollback | Removal steps, dependency prune, data migration if any, test that the harness still runs without it |
| 8 | Refusal boundaries | No unpinned git installs, no install scripts without approval, no secrets, no proprietary/copied code, no "inspired by" without attribution |

### 3.4 References needed

| Path | Use |
|---|---|
| `wave2/05-HARNESS-CODE.md` + `05-CODE.json` | donor mechanisms, code pointers, "what not to copy", 12 candidate mechanisms |
| `wave2/02-AGENT-REPOS.md` + `02-REPOS.json` | verified repo metadata, licences, versions, build-vs-integrate |
| `wave2/04-HARNESS-DESIGN.md` §11 | build vs buy decisions to respect |
| Donor repositories' `LICENSE`, `pyproject.toml`/`package.json`, commit page | authoritative licence, version, runtime |
| `REPORT.md` bibliography and evidence labels | source hierarchy and what was actually read |

### 3.5 Dependencies

| Kind | Value |
|---|---|
| Required | `research-corpus-navigator` |
| Recommended | `source-verification`, `hallucination-redteam` (for "this is verified" claims) |
| Feeds | `agent-harness-architect` (build-vs-reuse decisions) |
| Related | `capability-auditor`, `integration-logic` |

### 3.6 SKILL.md skeleton

```markdown
---
name: harness-code-adapter
description: "Use when sourcing or adapting mechanisms from donor agent repositories: verify licence/provenance, extract the mechanism, reimplement it originally, record attribution and a removal path. Triggers: borrow mechanism, adapt code, donor repo, fork vs reimplement, code donation, port from OpenHands, adapter."
version: 0.1.0-draft
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [agent, harness, licence, provenance, adaptation, donors]
    related_skills: [research-corpus-navigator, source-verification, agent-harness-architect, capability-auditor]
---

# Harness code adapter

## When to use / not use
- Use when a donor mechanism is actually needed and its licence is verifiable.
- Not to copy code, and not before the mechanism is specified in prose.

## 1. Donor intake
- Record repo, commit SHA, licence, runtime, activity, exact file:line pointers.
- Read the donor's tests; they describe the real contract.

## 2. Licence and provenance gate
- No licence or incompatible licence → stop.
- Record attribution duties and copyleft boundaries.
- Never copy a file without a commit and licence in the record.

## 3. Mechanism extraction
- Describe behaviour, invariants, state, failure modes, dependencies.
- Separate the mechanism from the donor's framework and naming.

## 4. Integration decision
- Adapter (call), fork (own), vendor (pin), or reimplement (rewrite).
- Default to reimplementing small typed mechanisms; vendor only pinned releases.
- State maintenance cost and exit path for each choice.

## 5. Original implementation and parity tests
- Write original code against this repo's contracts.
- Parity cases for the happy path; failure injection for the error path.
- No verbatim copied bodies, no renamed-only copies.

## 6. Attribution record
- Update references/donors.md: repo, URL, commit, licence, files read,
  mechanism extracted, changes made, date.
- Keep the record with the code, not in chat.

## 7. Removal and rollback
- Document removal steps and dependency prune.
- Exercise the inverse once: remove, run the harness, confirm behaviour.

## 8. Refusal boundaries
- No unpinned git install; no install script without approval.
- No secrets; no proprietary code; no attribution-free lifting.
- No benchmark claim from the donor's own numbers.

## Sources & verification
- 05 (donor mechanisms), 02 (verified repo facts), 04 §11 (build vs buy),
  donor LICENSE + commit, REPORT bibliography.
```

### 3.7 Acceptance tests

1. "Port OpenHands' tool loop." → produces mechanism extraction + licence check + original
   implementation plan + parity tests, not copied source.
2. "Just clone repo X and use it." → checks licence, pinned version, install scripts and
   runtime cost before agreeing; records the decision.
3. "Which donor has the best loop?" → cites `05`/`02` with labels; refuses to rank on stars or
   native benchmarks alone.

---

## 4. `agent-learning-loop`

### 4.1 Identity

| Field | Value |
|---|---|
| **Name** | `agent-learning-loop` |
| **Version** | `0.1.0-draft` |
| **Description** | "Use when adding or operating memory, retrieval, skills, evaluation, promotion or rollback for an agent harness: record episodes, retrieve bounded cases, evaluate with goldens and A/B, promote only evidence-backed skills, detect reward hacking, and state honestly whether anything was learned. Triggers: agent memory, experience ledger, retrieval, skill promotion, evaluation loop, RL loop, reward hacking, golden set, learn from runs." |
| **License** | original (DeerFlow Forge) |
| **Writes** | ledger/eval design and records; not model weights; no production edits without a build task |

### 4.2 When to use / not use

| Use | Do not use |
|---|---|
| Designing or operating the four memory stores and the promotion loop | Fine-tuning or PPO/RLHF weight training — out of scope and not planned (`04` D10) |
| Adding retrieval and proving whether it helps | Claiming "learning" from a demo or a single run |
| Building a golden set, A/B arms and regression gates | Evaluating without fixtures (refuse: `E_EVAL_EMPTY`) |
| Auditing a claimed improvement for reward hacking | Treating the public dev set as a scoreboard |
| Deciding whether a lesson/skill is promotable or must roll back | Promoting on confidence alone; promotion requires samples + goldens + sign-off |

### 4.3 Sections (8)

| § | Section | Content |
|---|---|---|
| 1 | Stores and ownership | Ledger (append-only), cases, semantic facts, procedural skills; only the curator mutates memory |
| 2 | Episode recording | Event chain, handoffs, tool calls, artifacts, gates, critique, resolution; evidence ids, never bare prose |
| 3 | Retrieval and receipts | Hard filters → lexical/vector rank → rerank; ≤1,200 tokens; receipt per query; empty is honest |
| 4 | Skills and pins | Executable steps, parameter ranges, preconditions, gates, recovery; version + app/catalogue pin; replay/adapt only |
| 5 | Golden set and metrics | Public dev / private held-out; primary pass rate, attempts, precision of pass, unsafe = 0, regression = 0, cost, critic stability |
| 6 | A/B and statistics | Same model/apps/catalogue; ≥3 runs per golden per arm; randomised; Wilson CI per arm, Newcombe for lift; null result stands |
| 7 | Promotion and rollback | N=3 independent + goldens + human sign-off; monotonic versions; one active pointer; kill switch; rollback flip |
| 8 | Anti-reward-hacking and honest claims | Held-out, gate authorship, vacuity, brief drift, shortcuts, cost anomaly, threshold hugging; retrieval/skills ≠ training |

### 4.4 References needed

| Path | Use |
|---|---|
| `wave2/06-LEARNING-LOOPS.md` + `06-LEARNING.json` | memory systems, reflection, skill libraries, RL stacks, failure modes |
| `wave2/04-HARNESS-DESIGN.md` §8–9 | four stores, promotion policy, goldens, metrics, anti-hacking, regression gates |
| `wave2/07-EXAMPLES.md` Examples 3, 5, 6 + `07-EXAMPLES.json` | ledger/retrieval, promotion, eval mechanisms |
| `wave2/01-STACK-VPS.md` §11 | proof that no ledger/eval tables exist yet |
| `~/.dsh/skills/craft-agent-operator/references/memory-ledger.md` | proposed ledger tables, promotion policy, forgetting |
| `~/.dsh/skills/craft-agent-operator/references/evaluation.md` | rubric anchors, golden record shape |

### 4.5 Dependencies

| Kind | Value |
|---|---|
| Required | `research-corpus-navigator`, `agent-harness-architect` |
| Installed skills | `craft-agent-operator` (loop + ledger/eval references) |
| Optional | `auditor`, `capability-auditor` (independent review of claims) |
| Uses | `07` Examples 3, 5, 6 as mechanism references |

### 4.6 SKILL.md skeleton

```markdown
---
name: agent-learning-loop
description: "Use when adding or operating memory, retrieval, skills, evaluation, promotion or rollback for an agent harness: record episodes, retrieve bounded cases, evaluate with goldens and A/B, promote evidence-backed skills, detect reward hacking, state honestly whether anything was learned. Triggers: agent memory, experience ledger, retrieval, skill promotion, evaluation loop, RL loop, reward hacking, golden set."
version: 0.1.0-draft
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [agent, memory, evaluation, skills, rl, promotion, deerflow]
    related_skills: [research-corpus-navigator, agent-harness-architect, craft-agent-operator, auditor]
---

# Agent learning loop

## When to use / not use
- Use for ledger/retrieval/skills/eval/promotion work.
- Not for weight training; not to claim learning without held-out evidence.

## 1. Stores and ownership
- Ledger (append-only, hash-chained), cases, semantic facts, procedural skills.
- The curator is the only writer of memory; everyone else reads.

## 2. Episode recording
- Record what happened with evidence ids: handoffs, tool calls, artifacts,
  gates, critique, resolution, cost.
- No prose-only success; no missing gate recorded as pass.

## 3. Retrieval and receipts
- Hard metadata filters first; lexical/vector rank; rerank by outcome,
  quality, recency, failure-code affinity.
- ≤1,200 injected tokens; return ids + one-line summaries + why_retrieved.
- Write a retrieval receipt for every query; no case → empty, baseline arm.

## 4. Skills and pins
- Skill = exact command ids + bounded parameter ranges + preconditions + gates
  + recovery.
- Versioned; never edited in place; pin app version + catalogue hash + skill
  version into the episode.
- Replay with defaults; adapt only within declared ranges.

## 5. Golden set and metrics
- 36 dev / 14 private (start); freeze per app/model/catalogue version.
- Primary: first-attempt verified-pass rate.
- Always report: precision of pass, unsafe = 0, regressions = 0,
  cost per accepted artifact, critic stability.

## 6. A/B and statistics
- Same model/apps/catalogue/fixtures; ≥3 runs per golden per arm.
- Randomised order, identical budgets, reviewers blind to arm.
- Wilson CI per arm; Newcombe CI for lift; overlapping CI → hold.

## 7. Promotion and rollback
- candidate → active: ≥3 independent successes + golden pass + human sign-off.
- Monotonic versions; exactly one active per skill; evidence never deleted.
- Rollback flips the pointer and re-runs goldens; kill switch forces baseline.

## 8. Anti-reward-hacking and honest claims
- Detectors: private leakage, gate authorship, vacuity, brief drift,
  input override, shortcuts, cost anomaly, threshold hugging.
- Retrieval/skills are context/policy change, not model training.
- "Learns" requires a persistent held-out gain that survives rollback.

## Refusals
- E_EVAL_EMPTY / E_EVAL_INCOMPLETE: no score, no promotion.
- No invented goldens, no averaged contradictions, no deleted evidence.

## Sources & verification
- 06 (research), 04 §8–9 (design), 07 examples 3/5/6 (mechanisms),
  craft-agent-operator references.
```

### 4.7 Acceptance tests

1. "Did retrieval improve the agent?" → demands arms, runs per golden, CI; reports null if
   overlapping; refuses to answer from one demo.
2. "Promote this lesson." → checks 3 independent evidence ids, goldens, sign-off, pin;
   refuses if any missing.
3. "The agent learns from every run — confirm." → distinguishes ledger recording from learning;
   cites `04 §8.6`; says retrieval/skills only, no weights.

---

## 5. `visual-computer-use-verifier`

### 5.1 Identity

| Field | Value |
|---|---|
| **Name** | `visual-computer-use-verifier` |
| **Version** | `0.1.0-draft` |
| **Description** | "Use when verifying a visual artifact, screenshot, print master or GUI-only surface: build rendered evidence, read back from the system of record, run a blind crop-cited critic, and refuse to treat exit codes, screenshots or 'saved' toasts as proof. Triggers: verify design, visual critic, screenshot verification, computer use fallback, render ladder, print proof, screen evidence, GUI read-back." |
| **License** | original (DeerFlow Forge) |
| **Writes** | verification records (render bundle, diagnostics, critique, read-back), never art authorship |

### 5.2 When to use / not use

| Use | Do not use |
|---|---|
| Verifying any visual artifact before acceptance/publish | As the primary action path when a typed CLI/MCP command exists |
| Print masters, DPI/transparency/safe-zone checks | Authoring or editing art — the verifier must not author |
| GUI-only surfaces (web admin, UI-only gap) with mandatory read-back | Pixel-only automation of a command-capable app |
| Blind critic review with rubric and crop evidence | Accepting a critic verdict without evidence, or letting metrics decide taste |
| Explaining why a screenshot/exit code is insufficient | Claiming a screenshot proves a print file |

### 5.3 Sections (8)

| § | Section | Content |
|---|---|---|
| 1 | Evidence ladder | Process → artifact → domain gates → rendered perception → blind critic → human rubric; missing rung = unverified |
| 2 | Artifact read-back | Exists, non-zero, magic, dimensions/DPI/colour/alpha, hash before/after; read back the system of record for writes |
| 3 | Render ladder | thumb 256 on light/mid/dark; view 1024; 100% crops; print sheet; contrast sim; alpha matte; diagnostics as data |
| 4 | Blind critic | Inputs (brief, rubric, renders), forbidden inputs (gates/exit/claims), crop-cited schema, unseen list, confidence rules |
| 5 | GUI fallback | When permitted (tool-gap proof), accessibility snapshot first, screenshot as evidence only, read-back or `E_SURFACE_UNVERIFIABLE` |
| 6 | Refusal codes | `E_ARTIFACT_MISSING/EMPTY`, `E_GATE_MISSING/VACUOUS/FAILED`, `E_VISION_UNAVAILABLE`, `E_CRITIQUE_UNGROUNDED/UNBLINDED`, `E_SURFACE_UNVERIFIABLE`, `E_SOURCE_MUTATED` |
| 7 | Precision and honest reporting | Pass precision, critic flips, false-pass audit; screenshots can only downgrade, never upgrade |
| 8 | Human rubric | Anchored 1–5 dimensions, blind reviewers, disagreement reported, required for publish/promotion/first episodes |

### 5.4 References needed

| Path | Use |
|---|---|
| `wave2/04-HARNESS-DESIGN.md` §7 | evidence ladder, render ladder, critic protocol, human rubric |
| `wave2/03-CRAFT-SURFACE.md` + `03-SURFACE.json` | actual command/MCP/visual surfaces, gate tools, GUI feasibility |
| `wave2/07-EXAMPLES.md` Example 4 + `07-EXAMPLES.json` | critic mechanism, confidence rules, failure paths |
| `wave2/01-STACK-VPS.md` §10 | installed apps, shims, missing FilmCraft/DesignCraft |
| `~/.dsh/skills/craft-mcp-drive/SKILL.md` | MCP transport, roots, tool inventory |
| `~/.dsh/skills/artcraft-command-atlas/SKILL.md` | exact command/gate lookup (read-only) |
| `~/.dsh/skills/visuals-gui/SKILL.md`, `~/.dsh/skills/forgewright-evidence-check/SKILL.md` | existing visual/evidence-check discipline to compose with |

### 5.5 Dependencies

| Kind | Value |
|---|---|
| Required | `research-corpus-navigator`, `craft-mcp-drive` |
| Optional | `artcraft-command-atlas` (lookup), `visuals-gui`, `forgewright-evidence-check` |
| Related | `apparel-print-master`, `ai-art-vectorize-vectorcraft`, `artcraft-vector-trace` (domain gates) |

### 5.6 SKILL.md skeleton

```markdown
---
name: visual-computer-use-verifier
description: "Use when verifying a visual artifact, screenshot, print master or GUI-only surface: render evidence, read back from the system of record, run a blind crop-cited critic, never treat exit codes or screenshots as proof. Triggers: verify design, visual critic, screenshot verification, computer use fallback, render ladder, print proof, screen evidence, GUI read-back."
version: 0.1.0-draft
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [verification, vision, critic, screenshots, gui, print, craft]
    related_skills: [research-corpus-navigator, craft-mcp-drive, artcraft-command-atlas, apparel-print-master, forgewright-evidence-check]
---

# Visual / computer-use verifier

## When to use / not use
- Use to verify visual artifacts and GUI-only surfaces.
- Not to author art; not as the primary path when a typed command exists.

## 1. Evidence ladder
- process → artifact → domain gates → render → blind critic → human rubric.
- Missing rung = unverified; no later rung upgrades a missing earlier one.
- Exit 0 is a claim about a process, not an effect.

## 2. Artifact read-back
- exists, non-zero, magic bytes, openable, dimensions, DPI, colour, alpha bbox.
- Hash inputs before/after; a changed source is E_SOURCE_MUTATED.
- For writes: read the system of record (file/DB/API), not the UI toast.

## 3. Render ladder
- thumb 256 on #FFFFFF/#808080/#000000; view 1024; 100% crops; print sheet;
  contrast simulation; alpha matte.
- Store diagnostics (coverage, bbox, components, edge hardness, white residual,
  SSIM) as data; diagnostics cannot certify an artifact.

## 4. Blind critic
- Inputs: brief, rubric lines, rendered images (files + hashes).
- Forbidden: gates, exit codes, operator claims, prior verdicts.
- Every dimension cites a real crop path + region + observation ≥12 chars.
- No reference → list it in unseen; unseen downgrades pass to pass_with_notes.
- Confidence is model self-report; low confidence → needs_human; never "certainty".

## 5. GUI fallback
- Only when a tool-gap row proves no native command (or web-only admin).
- Accessibility snapshot first; screenshots as evidence only.
- Every write must be read back; unreadable → E_SURFACE_UNVERIFIABLE.
- Record a11y snapshot hash (and screenshot hash if used).

## 6. Refusal codes
- E_ARTIFACT_MISSING / E_ARTIFACT_EMPTY / E_ARTIFACT_MISMATCH
- E_GATE_MISSING / E_GATE_VACUOUS / E_GATE_FAILED
- E_VISION_UNAVAILABLE / E_CRITIQUE_UNGROUNDED / E_CRITIQUE_UNBLINDED
- E_SURFACE_UNVERIFIABLE / E_SOURCE_MUTATED
- Refusals are named, structured and terminal where marked.

## 7. Precision and honest reporting
- Track pass precision (human-accepted / marked pass), critic flip rate,
  false-pass audit sample.
- A screenshot can only downgrade a verdict, never upgrade it.
- Do not report "print proof" for a screen render or mockup.

## 8. Human rubric
- Anchored 1–5: brief fit, hierarchy, typography, colour, print safety.
- Two blind reviewers for publish/promotion; disagreement reported, not averaged.
- Required for publish, promotion, and the first episodes of a new family.

## Anti-patterns
- "Command exited 0, so it worked." "The screenshot looks right." "The gate passed."
  "The vision model said pass." "Saved toast means saved."

## Sources & verification
- 04 §7 (ladder, render, critic, rubric), 03 (surfaces), 07 Example 4,
  craft-mcp-drive (transport/roots), domain gate skills.
```

### 5.7 Acceptance tests

1. "Is this PNG print-ready?" → asks for dimensions/DPI/alpha/gate report, requires rungs 1–4,
   marks `unverified` if any missing; does not accept a screenshot.
2. "The GUI said 'saved' — done?" → refuses; requires read-back from the system of record;
   explains `E_SURFACE_UNVERIFIABLE`.
3. "Review this render with the critic." → checks critic inputs are blind, requires crop-cited
   evidence per dimension, applies unseen/low-confidence rules, never outputs fake certainty.

---

## 6. Dependency graph and rollout order

```text
research-corpus-navigator  (no dependencies; read-only)
   ├── harness-code-adapter      (needs corpus + licence discipline)
   ├── visual-computer-use-verifier  (needs craft-mcp-drive + corpus)
   └── agent-harness-architect   (needs navigator + adapter; uses verifier for §6/7)
             └── agent-learning-loop  (needs architect's contracts + 07 examples)

Rollout (install in this order, validate each before the next):
  1. research-corpus-navigator   → trigger + packet tests on 3 questions
  2. harness-code-adapter        → licence-gate dry run on one donor
  3. visual-computer-use-verifier→ blind-critic dry run on one render bundle
  4. agent-harness-architect     → design dry run on the Forge Conductor brief
  5. agent-learning-loop         → eval dry run with synthetic run records
```

The graph is intentionally acyclic: `agent-harness-architect` depends on
`harness-code-adapter` for donor decisions, and `agent-learning-loop` depends on the architect
for the contracts it evaluates. Neither requires the other to be installed first; the corpus
supplies the contracts in the meantime.

## 7. Validation plan for all five

| Check | Method | Pass condition |
|---|---|---|
| Trigger routing | 5 positive + 3 negative prompts per skill | Positive prompts route to the skill; negatives route to the named sibling |
| Output shape | Dry run on three real corpus questions | Stated sections/fields present; no whole-file dumps |
| Token budget | Measure injected context and output | Within the skill's budget (≤1,200 tokens for navigator; bounded elsewhere) |
| Citation quality | Spot-check 5 claims per dry run | Each claim has a real `path:line` or is labelled `[I]/[U]` |
| Size | `SKILL.md` line count | ≤250 lines, or depth moved to `references/` |
| Safety | Scan for secrets, unpinned installs, production writes | Zero hits; no install scripts |
| Non-duplication | Compare with installed skills | No overlap that would steal routing from `craft-agent-operator`, `artcraft-command-atlas`, `craft-mcp-drive` |
| Removal | Remove the skill and re-run its trigger tests | Requests route to the intended fallback; no orphan references |

## 8. What these skills must not become

- A second copy of the research dossier (they cite it, they do not restate it).
- An auto-loader that opens all wave2 files for every question.
- An orchestrator that replaces `craft-agent-operator`, the console, or the Forge Conductor.
- A deployment tool: nothing here installs services or touches production.
- A claim engine: no number, capability or benchmark becomes "verified" through repetition.

## 9. Limitations and unverified items

| Item | Status | What would prove it |
|---|---|---|
| Skills installed or routed by the runtime | **Not installed** | Install as drafts in a test profile; run the trigger suite |
| Trigger wording and overlap with existing skills | **Unverified** | 8-prompt routing test per skill against the installed catalogue |
| Token budgets and reading slices | **Unverified estimates** | Measure on real questions; adjust limits |
| Corpus references to `02`–`08` and their JSON companions | **Wave 2 was still being written while these specs were authored** | Re-check paths, section numbers and `08` at install; update citations |
| Claims the skills repeat from the corpus | **Not re-verified here** | Follow each citation to its source and label |
| Skill effectiveness | **Unmeasured** | A/B on dry-run tasks (time, citations, errors) |
| Name collisions in `~/.dsh/skills` | **Unchecked** (looks distinct) | Search the installed skills index before install |
| `07-EXAMPLES.md` code sketches | Compile/typecheck and scratch-harness checked, **not production** | Build tasks, integration tests, real DB/CLI/model probes |
| Relationship to installed counterparts (§0.5) | **Unverified** | Diff each draft against `~/.dsh/skills` v1.0.0; routing test for the two adjacent names |

No skill in this file is presented as installed, tested in routing, or measured. They are
specifications ready for review.

