# Eko, Craft Agents, and DeerFlow Forge

**A 200-question research and integration dossier**

Prepared: **2026-11-05** · Owner: Riley · Scope: FellouAI Eko, Devain Eko, Eko ecosystem,
agentic app-driving projects, the ArtCraft/Craft family, Adobe tutorial transfer, memory/learning,
and the real state of DeerFlow Forge.

> **Evidence labels:** `[V]` verified source · `[R]` local repository/catalogue · `[I]` inference ·
> `[U]` unverified/not found · `[H]` historical. Source IDs are in the bibliography.
>
> **This report does not claim** that any agent is better than a human designer, that Eko has durable
> learning, or that Adobe tutorials are 1:1 transferable. Those claims are examined and bounded.

---

## Executive answer (the decision)

**Do not build a new agent framework from scratch, and do not start with computer-use.** Build a
**Craft Conductor**: a thin, typed tool/verification layer around the existing ArtCraft CLI/MCP
surfaces, an **Experience Ledger** (episodes → actions → gate results → outcomes), and a
**retrieval/skill-promotion loop**. Use Eko or DeerFlow as the planner/orchestrator where they fit;
neither supplies the missing learning layer.

- **Eko** is a real MIT-licensed JavaScript agent framework: package **4.1.3**, latest GitHub release
  **v4.1.0** (2025-12-29), last commit 2026-03-03, **4,960 stars / 446 forks** at read time. It has a
  planner, dependency-aware multi-agent execution, pause/resume, MCP, custom agents/tools and
  streaming. Its “memory” is **in-process context compression plus a `task_snapshot` prompt** — not a
  durable cross-session store and not model training. `[V: E1–E5]`
- **Devain Eko** is a **different project with the same name**: a prompt-only “thinking companion”
  (MIT, one star, no server). It is useful as a reflection prompt, not an agent runtime. `[V: E6]`
- **eko-agent-github** is a third-party GitHub-discovery demo built with Eko (three stars, no license
  metadata). It is not official and not a design agent. `[V: E7]`
- The **Craft apps are not 1:1 copies** of Adobe apps. They are independent, mostly Rust,
  clean-room/reimplemented tools with familiar conventions; file compatibility varies by app. Adobe
  tutorials transfer **concepts and workflows**, not command IDs or exact UI behaviour. `[V: A1–A4]`
- **DeerFlow Forge, as this repository stands, does not learn.** It is a pure-viewer console plus a
  deterministic Python pipeline with three MCP tools; no LLM SDK, no episode memory, no skill
  induction and no reward/eval loop. The external **DeerFlow 2.x harness** has a real cross-session
  memory system (DeerMem facts/summaries), but that is fact/preference memory, not art-skill learning,
  and it is not vendored here. `[R: L1–L5; V: D1–D3]`
- **Existing agents can drive the tools** through the Craft CLI/MCP surfaces. The hard problem is not
  “can an agent click”; it is **reliable action selection, verification, memory and taste**. Build that
  layer; do not rebuild the apps or the harness.

**Recommendation:** Phase 1 is a Python-native **Craft Conductor** (LangGraph or equivalent durable
state) that calls the same command registry as the apps, writes an Experience Ledger, and promotes
only gate-verified procedures. Eko is a strong reference/optional TypeScript control plane; a full Eko
rewrite is not the first move. The success target is **reliable production output under human art
direction**, not “better than a human designer,” which has no supporting benchmark.

---

## Method and evidence bar

| Skill | Use here |
|---|---|
| `deep-research` | Question framing, source hierarchy, claim register, explicit gaps |
| `research` | Read local code/runtime first; separate confirmed from unknown |
| `evidence-check` | Every decision-critical claim carries a source or is labelled |
| `evidence-gap-audit` | Missing Eko docs, unexecuted tutorials, vendor benchmarks called out |
| `capability-auditor` | Claimed capability vs actual tool surface (Eko, DeerFlow, local repo) |
| `scientific-thinking` | Alternative explanations and boundary conditions for “learning” |
| `logic-debugger` | State machines, retries, snapshots, lost-state failure modes |
| `integration-logic` | Call-chain: console → MCP → pipeline → Craft → storefront |
| `logic-gatekeeper` | No production edit before architecture/data-flow/edge cases are stated |
| `agent-experience` / `agent-native-design` | Progressive disclosure, structured output, bounded tools |
| `artcraft-command-catalog` + atlas | Exact command IDs and parameter schemas for the Craft layer |
| `ai-art-vectorize-vectorcraft` / `artcraft-vector-trace` | Trace/retype/gate truth |
| `apparel-print-master` | Print-canvas and provider geometry |
| `artcraft-image-cleanup` | Retouch/upscale/colour boundaries |
| `craft-mcp-drive` | MCP transport, roots, tool inventory and refusal boundaries |

**Freshness rule:** current as of **2026-11-05**. Repository metadata/source read that date. Vendor
benchmark numbers are labelled as vendor claims, not independently reproduced. Eko’s documentation host
returned **HTTP 503** on 2026-11-05; README, package metadata, source and examples were used instead,
and that gap is recorded.

**Source hierarchy:** official repository/source > official docs > official learning hub >
peer-reviewed/preprint paper > vendor benchmark > secondary article. Forums and AI-generated pages were
not used as authoritative.

## Code pointers for the load-bearing claims

| Claim | Pointer |
|---|---|
| Eko constructs a task and plans/executes | `packages/eko-core/src/agent/eko.ts:18` (class), `:27` (`generate`), `:79` (`execute`), `:148` (`doRunWorkflow`), `:348` (`pauseTask`) |
| Eko planner is an LLM XML planner with retries | `packages/eko-core/src/agent/plan.ts:15`, `:80`, `:90` (8192 tokens), `:146` (3 retries) |
| Dependency tree/cycle handling | `packages/eko-core/src/common/tree.ts:8`, `:101`, `:146` |
| Eko memory compression/snapshot | `packages/eko-core/src/memory/memory.ts:7`, `:127`; `memory/snapshot.ts:6`, `:8` |
| Local pipeline is deterministic, not an LLM loop | `blueprint/files/pod_pipeline/orchestrator.py:58` (`run_pipeline`), `:147` (trace), `:167` (step), `:225` (publish) |
| Local MCP surface is exactly three tools | `blueprint/files/pod_pipeline/mcp_server.py:51`, `:53`, `:72`, `:92` |
| Local persistence has no memory/eval tables | `blueprint/files/sql/schema.sql:25`, `:49`, `:97`, `:147`, `:189` |
| Local `package.json` has no LLM/agent SDK | `package.json` dependencies (read 2026-11-05) |

## Call-chain / state audit (local, read-only)

| Hop | Evidence | Verdict |
|---|---|---|
| Console → pipeline | Console is a pure viewer; source strings imported at build time; no live agent calls | **viewer only** |
| External DeerFlow → MCP bridge | `deploy/mcp-stdio.mjs`; HTTP/stdio MCP; three tools | **wired**; external instance not inspected |
| MCP → DB/worker | `trigger_pipeline_job` inserts an orchestrator row and spawns a detached worker; repeats return the live run | **idempotent by live-run constraint** |
| Worker → orchestrator | claim run → stage/SHA-256 → trace → steps → validators → publish | **deterministic** |
| Orchestrator retries | transient exits only, `max_attempts` default 2; no parameter adaptation | **retry, not learning** |
| Publish | idempotent by existing Fourthwall product id; missing creds/template is a named refusal; `auto_publish` is config-driven | **real side effect; requires approval policy** |
| Failure state | `processing_jobs` records attempt/exit/digest/log/output; run/asset states change | **auditable, but no eval/lesson** |
| Agent trace | no `agent_episode`/`agent_action` schema | **missing** |
| Capability boundary | only pipeline controls are exposed over MCP, not Craft command tools | **missing direct action surface** |

This is the concrete integration gap: the pipe is reliable and idempotent, but it is not an agent
learning loop. The new `craft-agent-operator` skill and its proposed ledger close that gap.

---

## Part 1 — What Eko actually is (Q1–Q20)

**Q1. What is Eko?**
Eko (“Eko Keeps Operating”) is a production-oriented JavaScript/TypeScript framework for building
agentic workflows from natural language, with browser and Node environments. It is an agent
**framework**, not a design app. `[V: E1]`

**Q2. Who owns it and what is the license?**
FellouAI owns `FellouAI/eko`; the package is `@eko-ai/eko`; license is **MIT**. `[V: E1,E2]`

**Q3. What version is current?**
The package manifest is **4.1.3**; the newest GitHub release is **v4.1.0** (2025-12-29); the v4.1.3
commit is 2026-03-03. At read time: **4,960 stars, 446 forks, 14 open issues**. `[V: E2,E4]`

**Q4. Is Eko an agent or a framework?**
A framework/library: you construct `new Eko({ llms, agents })`, then `generate`/`execute`/`run`.
There is no turnkey product UI in the core package. `[V: E3]`

**Q5. What is Eko’s top-level architecture?**
`Eko.generate()` builds a `TaskContext`, invokes a `Planner`, parses an XML workflow, and
`execute()` walks the resulting agent dependency tree. `[V: E3]`

**Q6. How does planning work?**
A system prompt tells an LLM to select only available agents, emit a `<root>` XML workflow with
`<agent id dependsOn>`, `<node>`, `<forEach>`, `<watch>`, and variable inputs/outputs; the planner
streams the result and parses it. `[V: E3]`

**Q7. What are the planner parameters?**
`maxOutputTokens: 8192`, `temperature: 0.7`, streaming, up to three retries on planner failure.
`[V: E3]`

**Q8. How does an agent execute?**
A ReAct-style loop (default max 100 iterations) builds a system/user prompt, converts tools, calls
the model, handles text or tool calls, and optionally runs a task-result check in “expert” mode.
`[V: E3]`

**Q9. How does multi-agent dependency work?**
`dependsOn` edges are topologically processed into a tree; independent agents can run in parallel;
`buildAgentTree` detects cycles and **disconnects** them with a warning rather than hanging.
`[V: E3]`

**Q10. Does Eko persist tasks across process restarts?**
The core keeps tasks in an **in-memory `global.taskMap`**; pause/resume works in the same process.
There is no database/checkpoint store in the core for task state. `[V: E3; I]`

**Q11. What is `task_snapshot`?**
A tool used during context compression. It asks the model to write a textual snapshot plus completed
node IDs, then replaces older messages with that snapshot. It is a **prompt/context** mechanism, not a
durable memory service. `[V: E3]`

**Q12. What is `EkoMemory`?**
An in-process message buffer with token estimation, max-message/max-token caps, truncation and
simple compression; used for chat/session messages. It is not a vector store or fact database.
`[V: E3]`

**Q13. Does Eko support MCP?**
Yes. It has an MCP client interface, lists tools dynamically, and can add them to an agent’s tool
set; the README calls this “Native MCP.” `[V: E1,E3]`

**Q14. What are Eko’s built-in computer/browser agents?**
The core exports `BaseBrowserAgent`, `BaseBrowserLabelsAgent`, `BaseBrowserScreenAgent`; the Node
example adds a Playwright-backed browser agent and a `FileAgent`. A generic OS-level desktop agent is
not in the core export surface; verify per package before claiming one. `[V: E1,E3,E5]`

**Q15. Can I add a custom agent/tool?**
Yes. Extend `Agent` or supply `AgentParams`, and implement `Tool`/function tools; the README
advertises one-line customization. `[V: E1,E3]`

**Q16. Does Eko support human-in-the-loop?**
Yes: callbacks include workflow confirmation and human input/select/help/login paths; task controls
include pause/abort. `[V: E3]`

**Q17. Does Eko stream plans and results?**
Yes: planner stream callbacks and agent/tool stream events are part of the callback model. `[V: E3]`

**Q18. Does Eko have native A2A and observability?**
The README lists “Observable Chain” and “Native A2A” as **coming soon**; there is an `a2aClient`
interface in the core, so A2A is partial/experimental, not a finished feature. `[V: E1,E3]`

**Q19. What are Eko’s main failure modes?**
Unknown agent names throw; missing workflow throws; planner retries then throws; aborts are surfaced;
in-memory task state is lost on process exit; long context can lose detail through snapshot
compression. `[V: E3; I]`

**Q20. Were Eko’s official docs usable?**
The documentation host returned **HTTP 503** on 2026-11-05. The repository README, `package.json`,
source tree and examples were readable and are the basis here; docs-only claims remain unverified.
`[V: E4]`

---

## Part 2 — Eko demos, Devain, and the ecosystem (Q21–Q40)

**Q21. Is there an official “Eko Demos” catalog?**
The repository ships three example projects (`example/extension`, `example/nodejs`, `example/web`).
I did not verify a separate official demo gallery; treat the examples as the demos. `[V: E5; U]`

**Q22. What does the Node demo do?**
It wires an OpenAI-compatible LLM, a local-cookie browser agent and a file agent, then asks Eko to
open GitHub, search `FellouAI/eko`, star it, summarize it and save a Markdown file to the desktop.
`[V: E5]`

**Q23. What do the web and extension demos do?**
The web demo is a simple React login flow; the extension is a Chrome extension with chat and
browser automation wiring. They demonstrate deployment surfaces, not a production product. `[V: E5]`

**Q24. Does the extension demo have memory?**
It has a `memoryRecall(chatId, prompt)` hook and a chat memory object; this is application-level
chat memory, not evidence of a durable scored/learned memory system. `[V: E5]`

**Q25. Did Fellou publish an official Eko demo site?**
`eko.fellou.ai` / `fellou.ai/eko` is referenced; the docs path returned 503. No separate demo catalog
was verified. `[V: E1; U]`

**Q26. What is “Devain Eko Thinking Companion”?**
A **separate** open-source project (`devain/eko`) described as “an open-source AI Thinking
Companion”; it is a prompt plus a static site, MIT, one star, no server/account. `[V: E6]`

**Q27. Is Devain Eko the same as FellouAI Eko?**
No. Different owner, different mechanics: one is a JavaScript agent framework; the other is a
thinking-companion prompt. The shared name is a collision, not a fork relationship. `[V: E1,E6]`

**Q28. What does the Devain Eko prompt actually instruct?**
Four principles: remember *why*; push back; prefer simple; leave the person stronger. It asks one
good question, separates known/assumed/unknown, and reflects the clearest version of the user’s
thinking. `[V: E6]`

**Q29. Does Devain Eko have persistent memory?**
No store or server. “Remember” is an instruction to hold the thread in the conversation; there is no
database, retrieval or cross-session persistence. `[V: E6]`

**Q30. What is `eko-agent-github`?**
A third-party GitHub project-discovery tool that uses Eko to find trending repos and enrich them with
AI analysis (Python + TypeScript + Gradio). `[V: E7]`

**Q31. Is `eko-agent-github` official?**
No. It is authored by `1692775560`, not FellouAI; README links to Eko but the repository is
independent. `[V: E7]`

**Q32. Is `eko-agent-github` a design agent or a Craft driver?**
No. It searches/analyzes GitHub repositories; it does not draw, edit images, or drive ArtCraft. `[V: E7]`

**Q33. What does `eko-agent-github` prove?**
That Eko can be used to wrap APIs and an analysis workflow; it does not prove production reliability,
memory, or design capability. `[V: E7; I]`

**Q34. Are there other Eko forks/tools worth using?**
The GitHub search returned 37 repos matching “eko agent”; most are unrelated or small demos. Do not
adopt one without reviewing its license, maintenance and security; none is a canonical Craft driver.
`[V: E4; U]`

**Q35. What packages make up the Eko workspace?**
`@eko-ai/eko` (core), `eko-nodejs`, `eko-web`, `eko-extension`; each targets a runtime. `[V: E2]`

**Q36. Which LLM providers does Eko show?**
Anthropic, Google Gemini, OpenAI, and OpenAI-compatible endpoints (Qwen/Doubao examples), configured
through an `LLMs` map. `[V: E1]`

**Q37. Does Eko require an API key?**
For hosted models, yes. Browser/front-end code must not hold secrets; route through a backend proxy.
`[V: E1]`

**Q38. Can Eko run with a local model?**
The framework can point at an OpenAI-compatible local endpoint in principle; its examples use hosted
providers. Local-model quality and tool-calling reliability were not tested here. `[V: E1; U]`

**Q39. Does Eko ship a user interface?**
No product UI in core; examples provide web/extension shells. `[V: E1,E5]`

**Q40. What are Eko’s license obligations?**
Core is MIT; dependencies and model providers have their own licenses/terms. Pin versions and audit
supply chain before production. `[V: E2]`

<!-- PART2 -->
## Part 3 — Agentic app-driving projects (Q41–Q60)

**Q41. What is `browser-use`?**
An open-source Python/TypeScript browser agent (MIT) that gives an LLM browser actions; it can drive a
local or cloud browser and exposes 31 browser actions plus integrations. `[V: B1]`

**Q42. What is `Agent-S`?**
An open-source computer-use agent framework from Simular that operates desktop/web GUIs. Its README
claims Agent S3 was “first to surpass human performance on OSWorld” at 72.60%, and Agent S4 targets
evolving interfaces from experience. Those are author claims, not independently reproduced here.
`[V: B2]`

**Q43. What is `UI-TARS-desktop`?**
ByteDance’s multimodal GUI-agent stack (Agent TARS + UI-TARS Desktop), using vision-language models
to control a local or remote computer/browser; Apache-2.0. `[V: B3]`

**Q44. What is `OpenAdapt`?**
A record → compile → verify → replay layer for computer-use agents. It records a successful run,
compiles a program, reads the system of record back after writes, and can halt rather than claim a
false success. MIT. `[V: B4]`

**Q45. What is `Playwright MCP`?**
An MCP server that drives a browser through structured accessibility snapshots rather than pixels;
deterministic, no vision model required, with file-root and security controls. `[V: B5]`

**Q46. What is `Agentic` (ghua8088)?**
A local-first desktop assistant with 70+ tools, LangChain/Ollama/Gemini, and a closed-source product
binary; its open engine is Pytron-Kit. The product itself was not audited. `[V: B6]`

**Q47. Where does Eko fit among these?**
Eko is an **orchestration framework** (planner, multi-agent dependencies, MCP, pause/resume), not a
finished GUI agent. It can host custom browser/file tools; it does not natively provide the robust
desktop perception of Agent-S/UI-TARS. `[V: E1,E3]`

**Q48. Do Claude and OpenAI computer-use agents exist?**
Yes, official computer-use APIs/agent patterns exist and are widely used; their exact current tools
and reliability on the Craft apps were **not** tested in this program. Treat vendor docs as the source
at build time. `[U]`

**Q49. What is the core difference between a computer-use agent and an app-native agent?**
A computer-use agent perceives pixels/screens and chooses clicks; an app-native agent calls typed
commands and reads structured results. The latter is faster, more deterministic and easier to verify
when the app exposes a command API. `[V: B4,B5; I]`

**Q50. Which approach should drive ArtCraft/VectorCraft/PhotoCraft/FilmCraft?**
**App-native first** (CLI/JSON/MCP command registry); use computer-use only for UI-only gaps or a
human-like demo. The Craft apps explicitly expose command surfaces for agents. `[R: L1,C1; V: A1–A3]`

**Q51. Can existing agents drive the Craft apps today?**
Yes. Craft apps expose CLI, JSON control channels and MCP servers; any MCP-capable client or agent can
call them, subject to the app’s tool surface and file roots. `[V: A1–A3]`

**Q52. Why is screen-based driving risky for paid production art?**
The screen can say “saved” while the underlying write failed or landed on the wrong record; OpenAdapt’s
fault-injection results show screen checks reporting many bad saves as successful. Read-back/gates are
required. `[V: B4]`

**Q53. What is a computer-use agent, precisely?**
A loop that observes a UI state, selects an action (click/type/scroll), executes it, observes again,
and stops on a goal or budget; reliability depends on perception, action grounding and recovery.
`[V: B2,B3; I]`

**Q54. What is an app-native agent, precisely?**
A loop that selects typed commands or workflows, passes validated parameters, reads structured results
and verifies artifacts; the app owns semantics and validation. `[R: C1; V: A3]`

**Q55. What is MCP?**
The Model Context Protocol: a JSON-RPC interface for exposing tools/resources to agents. It standardises
discovery and calls; it does not by itself provide memory, learning or quality. `[V: B5; R: L4]`

**Q56. What are MCP’s practical limits?**
Tool schema/context cost, transport/lifecycle complexity, per-server auth/roots, and the fact that
tools can be listed but not callable in a given state; the agent must verify state and errors.
`[V: B5; R: C4]`

**Q57. What is OpenAdapt’s most important lesson for Craft?**
**Verify the effect, not the screen.** For a design pipeline: read back the actual file, dimensions,
gate report and product state; never accept a success message alone. `[V: B4; I]`

**Q58. What is Agent-S4’s “interface evolution” idea?**
It evolves the interfaces/tools an agent uses from task experience, rather than retraining the base
model for every app. It is research evidence that tool/interface adaptation matters; its benchmark
numbers are author-reported. `[V: B2]`

**Q59. Is browser-use’s “90.5% Stealth Bench V2” a reason to choose it?**
No. It is a vendor benchmark on a specific task set; independent reproduction and Craft-specific
success rates are what matter. Use it for browser-only fallback, not as proof of design competence.
`[V: B1; I]`

**Q60. Build or integrate?**
**Integrate** the orchestration and tool protocols; **build** the Craft-specific tool layer,
verification, experience ledger and promotion policy. Building a generic agent framework from scratch
would duplicate mature work. `[I]`

---

## Part 4 — What the Craft apps actually are (Q61–Q80)

**Q61. What are the ArtCraft/Craft apps?**
A family of free, open-source creative tools from the ArtCraft team, mostly written in pure Rust,
covering image editing, vector illustration, video, motion graphics, page layout, PDFs, audio,
presentations, CAD, spreadsheets and more. `[V: A1–A4]`

**Q62. Are they 1:1 copies of Adobe apps?**
**No.** They are independent implementations with familiar conventions and similar purposes; the
repositories describe clean-room/independent code and public-spec implementations. Some formats
round-trip; others do not. `[V: A1–A4]`

**Q63. What is PhotoCraft’s real status?**
Early alpha. The README says much of Photoshop’s surface exists but it is **not yet a daily
professional replacement**; 500+ commands are exposed, PSD round-trip rendering matches 307/309 corpus
files, and 15 tools are still missing. `[V: A2]`

**Q64. What is VectorCraft’s real status?**
Alpha. README reports ~88% of core menu items, ~92.5% of menu items doing something, ~75% feature
depth and ~65% “ready for real work”; the installed catalogue has **918 commands / 64 groups**.
`[V: A1; R: C1]`

**Q65. What is FilmCraft’s real status?**
Alpha. README reports ~86% feature breadth and ~56% “ready for real work”; **650+ engine commands**,
with CLI, JSON control channel and MCP; it does not open `.prproj` natively. `[V: A3]`

**Q66. Which other Craft apps exist?**
PhotoCraft, VectorCraft, FilmCraft, LightCraft, PdfCraft/PrintCraft, EffectCraft, DesignCraft,
FigCraft, WordCraft, SoundCraft, DeckCraft, CADCraft, GridCraft, TextureCraft, Craft Anything,
SolidCraft (community). Many are alpha/in-development. `[V: A1–A4]`

**Q67. How compatible are Adobe project files?**
PhotoCraft reads/writes PSD/PSB; VectorCraft handles SVG/PDF and partial `.ai`; FilmCraft imports FCP
XML/AAF/OTIO but not `.prproj`; EffectCraft does not open `.aep`; DesignCraft uses IDML/interchange.
Compatibility is app-specific, not a blanket “1:1.” `[V: A1–A4]`

**Q68. What surfaces do Craft apps expose for agents?**
Each app’s engine is command-based; the UI, CLI, JSON control channel and MCP server dispatch the same
commands. VectorCraft/PhotoCraft/FilmCraft READMEs explicitly document this. `[V: A1–A3]`

**Q69. How many VectorCraft commands are in the local snapshot?**
**918 commands in 64 groups** (snapshot 2026-11-05), asserted by the atlas builder. `[R: C1,C2]`

**Q70. How many PhotoCraft commands?**
**965 rows in 38 groups** in the local snapshot; the README’s “500+” is a product-level count, not the
same as the full engine registry. `[R: C1,C2]`

**Q71. How many FilmCraft commands?**
The README states **more than 650 engine commands**; they are discoverable with
`filmcraft-cli commands` and exposed over its control channel/MCP. `[V: A3]`

**Q72. How should an agent find the right command ID?**
Use the atlas intent map and `command_lookup.py`; read the full parameter schema for the chosen ID;
never guess an ID from a menu label. `[R: C2]`

**Q73. What are the atlas’s intent mappings?**
A curated intent → exact command ID table plus family indexes, group index, aliases and command tips;
the map is checked against the catalogue so IDs exist. `[R: C2]`

**Q74. What are the Craft verification gates?**
`craft_trace` enforces ten gates (white residual, specks, coverage, DPI, canvas, fill colours, edge
definition, hard alpha, transparent corners, retyped text); `prep_print_art` has coverage/subject/
upscale rules; print masters add 300 DPI and transparency. `[R: C3]`

**Q75. What makes a valid apparel print master?**
Provider geometry at 300 DPI, a transparent background, every neutral white removed, art centred at
the print width, and all gates passing; an `ok:false` report is not shippable. `[R: C3]`

**Q76. What is the AI-art vector pipeline?**
Strict white cutout → erase AI text bands → `imageTrace.make` with limited palette → `imageTrace.expand`
→ SVG export → render at print pixels → retype at mapped boxes → ten gates. `[R: C3]`

**Q77. What is the rule for AI-rendered text?**
Never trace it; erase and retype with a real font at boxes measured on the original image, then verify
the retype gate. A pass with `retype_boxes: 0` is vacuous. `[R: C3]`

**Q78. What is the white rule?**
Every neutral white should become transparent for print/trace; cream/tan must survive. If there is no
white background, `--mode white` refuses; use `--mode none` deliberately or `--mode alpha` only with a
real alpha channel. `[R: C3]`

**Q79. What is the upscale boundary?**
Refuse more than **2.5×** upscale from the crop/subject baseline; regenerate instead. The ratio is
measured on the subject bbox, not the source canvas. `[R: C3]`

**Q80. Do Adobe tutorials transfer directly?**
They transfer **concepts, task intent, visual conventions and workflow order**, not exact command IDs,
menus, plugins or proprietary features. Treat them as a curriculum to translate and test, not a
guarantee. `[V: A1–A4, AD1; I]`

---

## Part 5 — Adobe tutorials as a training corpus (Q81–Q100)

**Q81. Which Adobe products map to which Craft apps?**
Photoshop → PhotoCraft; Illustrator → VectorCraft; Premiere Pro → FilmCraft; After Effects →
EffectCraft; InDesign → DesignCraft; Lightroom → LightCraft; Acrobat → PdfCraft/PrintCraft; Figma-like
→ FigCraft. `[V: A1–A4]`

**Q82. What are the official tutorial hubs?**
Adobe Learn hubs: `adobe.com/learn/photoshop`, `/illustrator`, `/premiere-pro`, `/after-effects` (and
equivalent InDesign/Lightroom hubs). These are the canonical starting points; helpx tutorial URLs may
redirect to Creative Cloud. `[V: AD1]`

**Q83. Can we bulk-scrape every Adobe tutorial?**
No. Do not bulk-copy copyrighted pages or assets without permission; use official public URLs, your
own capture notes, public-domain assets, and a curated task list. `[I]`

**Q84. What does a tutorial actually provide for an agent?**
A task intent, an ordered procedure, parameter examples, a visual target, and common mistakes. It does
not provide the Craft command IDs or a machine-checkable acceptance test. `[V: AD1; I]`

**Q85. What does not transfer from Adobe?**
Exact menu paths/shortcuts, proprietary file/edit data, plugins, cloud services, generative features,
and UI states that the Craft apps have not implemented. `[V: A1–A4]`

**Q86. How do we translate a tutorial step into a Craft action?**
Normalise the step to an intent → query the atlas/lookup → read the full parameter schema → probe one
step on a copy → verify the artifact → record the translation. `[R: C2; I]`

**Q87. Example: Photoshop “remove background.”**
Map to PhotoCraft subject/selection commands, then `layer.layerMask.revealSelection` (or the available
subject command), and verify the mask on black/white; do not assume a generative remove exists.
`[R: C1,C2; I]`

**Q88. Example: Illustrator “Image Trace.”**
Map to `imageTrace.make` with panel settings under `params.params`, then `imageTrace.expand`; select
all first; verify paths/fills and the rendered result. `[R: C3]`

**Q89. Example: Illustrator Pen tool.**
Map to VectorCraft path/pen command IDs from the atlas; do not use `path.simplify` (absent) or menu
guesses. Verify anchors and handles. `[R: C1,C2]`

**Q90. Example: Photoshop Curves.**
Map to `image.adjustments.curves` with `points`; for a live master prefer an adjustment layer/command
if available; verify on a copy. `[R: C1]`

**Q91. Example: Premiere Lumetri colour.**
FilmCraft exposes an effects/parameter command path (`effects.setParam` with a Lumetri-style effect in
its control example); verify the exact command/effect name in the installed build, not from memory.
`[V: A3; U]`

**Q92. Example: After Effects expressions.**
EffectCraft’s README claims JavaScript expressions and 259 effects; map concepts, but verify the actual
expression/runtime surface before relying on it. `[V: A4; U]`

**Q93. Example: InDesign paragraph styles.**
DesignCraft’s README describes paragraph/character styles, parent pages and print PDF; map the tutorial
concept to its command registry after installation. `[V: A4; U]`

**Q94. How many tasks should the first curriculum have?**
A practical first corpus: **5 apps × 10 tasks = 50 goldens**, each with input, intended steps, gate
criteria and accepted artifact. Quality matters more than volume. `[I]`

**Q95. What is a “golden” task?**
A frozen input plus a reference procedure, expected outputs and pass/fail gates; it must be runnable
against a pinned app version and produce evidence, not just a screenshot. `[I]`

**Q96. How do we score artistry?**
With a human rubric (brief fit, hierarchy, typography, colour, originality, print safety) and blind
comparison; automated gates score technical correctness only. `[I]`

**Q97. How do we score technical correctness?**
Command success, artifact existence, dimensions/DPI/colourspace, gate reports, provider geometry and
no source mutation; quote the exact evidence. `[R: C3]`

**Q98. What assets can we use for tutorials?**
Public-domain art (e.g., NASA/archival), your own work, or licensed assets with recorded rights; never
redistribute Adobe tutorial media. `[V: A2,A3; I]`

**Q99. How do we handle tutorial/app version drift?**
Record the Adobe page date, the Craft app version and command snapshot; re-run goldens on upgrades and
label stale results `HISTORICAL`. `[R: C2; I]`

**Q100. What are the first ten high-value tasks?**
(1) flat logo trace, (2) AI badge cleanup/trace, (3) photo crop/retouch/export, (4) print master at
300 DPI, (5) type/outline/retype, (6) mask/cutout, (7) smart-object/filter round trip, (8) ad layout
with safe zones, (9) short film cut/grade/export, (10) multi-page layout/PDF. `[R: C3; I]`

## Part 6 — Memory, learning, and what “learns from what it does” means (Q101–Q120)

**Q101. What kinds of memory matter for a design agent?**
Four layers: working/context (this run), episodic (what happened), semantic (brand rules, preferences,
facts), and procedural (skills/workflows). A production agent needs all four; a chat log is not enough.
`[I]`

**Q102. Does Eko learn from experience?**
No weight updates and no durable experience store. It compresses context and can snapshot a task into
a prompt; that is within-run continuity, not cross-run learning. `[V: E3]`

**Q103. Does DeerFlow learn?**
The external DeerFlow harness persists facts and summaries across sessions through DeerMem (and
optional mem0/honcho/OpenViking backends), injects them under a token budget, and can consolidate/
deduplicate facts. It does **not** train model weights. `[V: D2,D3]`

**Q104. Does DeerFlow Forge (this repo) learn?**
No. The local repo records processing jobs/logs and retries transient failures; it has no memory table,
no retrieval, no skill induction, no evaluation and no feedback into planning. `[R: L1–L3]`

**Q105. What would “truly learns” mean operationally?**
A statistically measurable improvement on held-out tasks: higher gate-pass rate, fewer attempts,
less human rework, lower cost, with no regression on old tasks. Without a baseline and eval set,
“learning” is only a story. `[I]`

**Q106. Does experience-based retrieval actually improve agents?**
Research supports it: Reflexion uses verbal feedback in an episodic buffer; ExpeL extracts insights
from experience without weight updates; Voyager grows a skill library; AWM induces reusable workflows.
Gains are task-dependent. `[V: M5–M8]`

**Q107. Should we fine-tune the model?**
Not first. Fine-tuning needs a large, labelled, rights-cleared trajectory corpus and an eval harness;
art-quality labels are expensive. Retrieval/skills give most of the early gain at lower risk. `[I]`

**Q108. Could RL work?**
Yes in principle: the Craft gates provide verifiable rewards, but they measure technical correctness,
not taste; optimizing them can produce “gate-passing” art. Use only with human/visual evals and a
reward-hacking review. `[I]`

**Q109. What is a skill library?**
Versioned executable procedures with preconditions, typed parameters, expected artifacts, gate results
and success statistics. Voyager’s evidence shows compositional reuse; the Craft equivalent is a
command/workflow library, not a folder of prompts. `[V: M5; I]`

**Q110. What is case memory?**
A retrievable record of a past brief, inputs, plan, actions, parameters, artifacts, gate results and
human rating. It lets a new run say “this resembles a case that needed more margin / different trace
settings.” `[I]`

**Q111. What is semantic memory here?**
Brand palette, logo rules, type licences, print widths, provider templates, owner preferences and
approved claims — durable facts injected into every relevant run. `[R: C3; I]`

**Q112. What is procedural memory here?**
The ordered command sequence for a task family (trace, retouch, print master), including parameter
ranges and failure recovery. This is what a “skill” should store. `[R: C3; I]`

**Q113. What is forgetting, and why is it required?**
Stale/contradictory facts and superseded skills must be invalidated or versioned. Graphiti’s temporal
validity and DeerFlow’s staleness/consolidation are examples; without it memory becomes a liability.
`[V: D2,M3]`

**Q114. What is a promotion gate?**
A rule that a candidate lesson/skill is promoted only after N independent successful runs, gate
evidence, no regression, and human approval. Otherwise it stays a draft. `[I]`

**Q115. What is catastrophic interference?**
Fine-tuning on new tasks can degrade old capabilities; memory/retrieval avoids overwriting weights.
This is one reason to prefer an external skill/case store first. `[V: M5; I]`

**Q116. What is reward hacking in this domain?**
Optimizing proxy metrics (path count, coverage, speed) while producing worse art or unsafe print
output. The ten gates are necessary but not sufficient; a human/visual rubric is required. `[R: C3; I]`

**Q117. What data-rights constraints apply?**
Only train/retrieve on assets with recorded rights; Adobe tutorial media and customer art are not a
free training corpus. Keep provenance and deletion paths. `[I]`

**Q118. How should we evaluate memory?**
A/B the same held-out tasks with and without memory/skills; measure gate pass, attempts, cost, latency,
and blind human ratings. Report confidence intervals, not anecdotes. `[I]`

**Q119. What is the smallest useful learning loop?**
Log every run with actions/gates → retrieve similar past runs → propose parameters/skills → verify on
a copy → record outcome → promote only after repeated success. `[I]`

**Q120. Can this become “better than a human designer”?**
There is no verified benchmark for that claim. It can be faster and more consistent at production
tasks; creativity, taste, brief interpretation and accountability remain human-led. `[I]`

---

## Part 7 — DeerFlow Forge and DeerFlow: the actual state (Q121–Q140)

**Q121. What is DeerFlow Forge in this repository?**
A TanStack Start/Vite console plus a deployable Python `pod_pipeline` package (orchestrator, DB, MCP,
Fourthwall client, Craft tool wrappers) and skills; the console is a pure viewer that imports pipeline
files at build time. `[R: L1]`

**Q122. Does the repo contain an LLM/agent runtime?**
No. `package.json` has no OpenAI/Anthropic/LangChain/agent SDK; the pipeline is deterministic Python.
The README’s “orchestrated by DeerFlow 2.2” is an external integration claim, not code in this repo.
`[R: L1,L2]`

**Q123. What is the local MCP surface?**
Exactly three tools: `list_pending_assets`, `trigger_pipeline_job`, `get_fourthwall_status`. `[R: L4]`

**Q124. What does the orchestrator actually do?**
Claim a run → stage/verify SHA-256 → trace (raster fallback on exit 1) → route steps with validators and
fsync → publish to Fourthwall → mark the run. It is a deterministic state machine, not an LLM planner.
`[R: L2]`

**Q125. Does it retry and learn from failures?**
It retries only transient exits, up to `max_attempts` (default 2); it records the failure but does not
change parameters or future plans. `[R: L2]`

**Q126. What does it persist?**
Tenant, assets, processing jobs (step/attempt/params/log/output), Fourthwall products, and sync logs;
schema constraints enforce states and budgets. `[R: L3]`

**Q127. Does it persist artifacts and gate reports?**
It persists artifact paths and step logs; Craft gate reports are files on disk, not a first-class
evaluation table. `[R: L2,L3]`

**Q128. Does it remember brand rules?**
Only as static config/skills; no learned or updated brand memory. `[R: L3]`

**Q129. Does it use the 33 installed Craft skills?**
The skills are for external agents (DSH/Hermes); the deployed Python pipeline does not load them as
agent instructions. `[R: L1]`

**Q130. Is “DeerFlow 2.2 / DeepSeek V4.1-Flash” verified?**
No. The local README claims it; the public bytedance/deer-flow README describes **DeerFlow 2.0** as a
super-agent harness. Version/model naming must be checked against the deployed instance, not assumed.
`[R: L1; V: D1]`

**Q131. What is the public DeerFlow 2.0 architecture?**
Gateway-embedded LangGraph runtime, middleware chain, subagents, sandbox, skills, MCP, checkpoints,
SSE streaming, artifacts, and a pluggable memory manager. `[V: D1,D4]`

**Q132. Does public DeerFlow have cross-session memory?**
Yes: DeerMem’s default backend stores summaries and per-agent facts, injects them under
`max_injection_tokens`, and has staleness/consolidation/dedup controls. `[V: D2,D3]`

**Q133. Does DeerFlow’s memory make it a design learner?**
No. It stores user/project facts and preferences; it does not learn from visual outcomes, gates or
design quality unless you add such a memory/eval loop. `[V: D3; I]`

**Q134. Does public DeerFlow train models?**
No evidence of training in the memory docs; it is an inference harness with memory. Fine-tuning/RL is
a separate program. `[V: D2,D3]`

**Q135. What does the local repo lack for an agent?**
Direct Craft command tools (only pipeline controls), episode/action schema, gate-result table,
retrieval, skill versioning, eval corpus, promotion policy and human rating loop. `[R: L1–L4]`

**Q136. Can an external DeerFlow call the local pipeline?**
Yes, via the HTTP/stdio MCP bridge; the README reports a verified MCP load and `list_pending_assets`
call. That does not give the external agent direct command-level control of VectorCraft/PhotoCraft.
`[R: L1,L4]`

**Q137. What is the biggest integration gap?**
The step from “trigger a fixed route” to “choose and verify an original design procedure” — the
command-level tools, feedback and learning loop. `[I]`

**Q138. What is the biggest safety gap?**
Publishing is a real external side effect; the repo requires owner approval/credentials and honest
refusals, but an autonomous agent must not be allowed to publish without a gate. `[R: L2]`

**Q139. What is the verdict on “does the agent in DeerFlow Forge learn”?**
This repo: **no**. External DeerFlow: **yes for facts/preferences across sessions; no for artistic
skill/quality unless extended**. `[R: L1–L4; V: D3]`

**Q140. What should be built first?**
The Experience Ledger + direct command gateway + eval harness; then retrieval; then skill promotion.
Training comes last, if ever. `[I]`

---

## Part 8 — Integration architecture (Q141–Q160)

**Q141. Where should the agent live?**
As a separate **control plane** that calls the existing pipeline and Craft command surfaces; do not
embed an LLM loop inside the deterministic worker. This preserves reproducibility and makes the agent
replaceable. `[I]`

**Q142. Eko or LangGraph?**
Eko: JS/TS, planner/multi-agent/MCP, MIT; strong for a Node control plane, but in-memory task state and
a stale docs/repo cadence. LangGraph: Python, durable checkpoints, fits the existing Python pipeline
and Postgres. `[V: E1–E3; V: D4; I]`

**Q143. What is the recommended choice?**
Phase 1: **Python Craft Conductor** using the existing pipeline + a durable graph/state store; expose
Eko-compatible tool contracts. Evaluate Eko as an optional TypeScript front-end/orchestrator for
interactive browser work. `[I]`

**Q144. Why not make Eko the core?**
It adds a second runtime and its task memory is process-local; you would still build the durable
ledger, Craft tools and eval. Its planner/dependency design is worth copying. `[V: E3; I]`

**Q145. Where does browser-use fit?**
A fallback for web-only surfaces (storefront/admin) and for UI-only gaps; not the primary art path. Its
benchmark is vendor-reported. `[V: B1; I]`

**Q146. Where does OpenAdapt fit?**
As a pattern for compiled, repeatable, verified procedures, especially for storefront/admin tasks with
read-back. It is not a generative design system. `[V: B4]`

**Q147. What tools must the agent have?**
`command_lookup`, `craft_run` (single/batch), `craft_inspect`, `verify_artifact`, `print_master`,
`pipeline_trigger`, `publish_status`, `memory_search`, `memory_write_candidate`, `eval_run`. `[R:
C2,C3,L4; I]`

**Q148. How do we constrain the tools?**
Allowlist command families/groups; read/write roots; no network; no secrets in prompts; owner approval
for publish; per-run budgets; reject paths outside roots. `[V: B5; R: C3]`

**Q149. How do we verify a run?**
Command exit + JSON envelope + artifact exists/nonzero + dimensions/DPI/format + Craft gate report +
visual review; for writes, read back the record. Never trust a success message alone. `[R: C3; V: B4]`

**Q150. What is the minimum durable schema?**
`agent_episode` (brief, inputs, plan, status), `agent_action` (tool, params, result, error, duration),
`agent_artifact` (path/hash/dimensions), `agent_eval` (gates, human score), `agent_lesson` (scope,
evidence, version, status). `[I]`

**Q151. How do we retrieve a relevant case?**
Hybrid: metadata filters (app, task family, brand, product), BM25/lexical over brief/notes, embeddings
over text/art descriptions, then rerank by gate success and recency; return bounded snippets + IDs.
`[I]`

**Q152. How does a lesson get promoted?**
Draft → N successful independent runs → regression against goldens → human approval → versioned skill;
any failure demotes/rolls back. `[I]`

**Q153. How do we roll back?**
Version every skill/lesson; pin the version in each run; keep the previous version and a kill switch;
re-run goldens after rollback. `[I]`

**Q154. How do we sandbox?**
Docker/container with no network, read-only source mounts, writable run dir, CPU/memory limits, process
timeouts, and a copy of the input. `[R: L2]`

**Q155. How do we handle secrets?**
Environment/credential store only; never the prompt or repo; redact logs; separate publish credentials.
`[R: L2; I]`

**Q156. How do we handle print/publish approval?**
Agent prepares and verifies; human approves the exact artifact and store state; no autonomous publish
in Phase 1. `[R: C3,L2]`

**Q157. How do we use Adobe tutorials?**
As a curated intent corpus with translation records, not a scraped training dump; every translated
step is probed and saved with evidence. `[V: AD1; I]`

**Q158. How do we integrate FilmCraft?**
Use its command registry + JSON control/MCP; record exact effect/parameter names from the installed
build; verify exported media and loudness/colour where relevant. `[V: A3]`

**Q159. How do we handle multiple apps in one job?**
A workflow graph with typed handoffs (SVG → print raster; raster → mockup; video → ad); each hop has an
artifact contract and a gate. `[I]`

**Q160. What is the MVP?**
One app family (VectorCraft or PhotoCraft) + ten goldens + direct command tool + ledger + eval +
retrieval, with no autonomous publish. `[I]`

## Part 9 — Safety, evaluation, and operations (Q161–Q180)

**Q161. What can go wrong in an autonomous Craft run?**
Destructive edits to a master, wrong crop/print size, tracing AI text, publishing an unapproved product,
rights violations, secret leakage, runaway cost, and a “success” that produced an unusable file.
`[R: C3; I]`

**Q162. What prevents those failures?**
Work on copies, write new paths, typed preflight, gate reports, read-back/verification, allowlists,
sandboxing, budgets, and human approval for print/publish. `[R: C3; V: B4]`

**Q163. How do we handle prompt injection in art/metadata?**
Treat all user/art/OCR/web text as data, never instructions; delimit it; do not let it change tool
policy; log untrusted content separately. `[I]`

**Q164. How do we handle malicious tool arguments?**
Validate IDs against the catalogue, validate parameter types/ranges, reject paths outside roots, and
fail closed on unknown tools/ids. `[V: B5; R: C2]`

**Q165. What is the supply-chain risk?**
Agent frameworks and MCP servers execute code; pin versions/lockfiles, review licenses, limit network,
and audit dependencies. Eko is MIT but its deps/providers are separate. `[V: E2; I]`

**Q166. What does a run cost?**
Model calls dominate (planning + retries + tool reasoning); Craft CLI work is local CPU/GPU. Cap tokens,
cache retrieval, and prefer deterministic commands for routine steps. `[I]`

**Q167. What about latency?**
Planning adds seconds to minutes; batch/serial Craft steps add more. Use async jobs, progress events,
and skip the LLM for known procedures after a skill is promoted. `[I]`

**Q168. What observability is required?**
Per-run trace: plan, retrieved cases, each tool call/params/result/error, gate values, artifacts,
model/token usage, human rating, and final state. `[I]`

**Q169. How do we prevent regressions?**
A golden suite per app/task family, run on every skill/prompt/model change; block promotion on any
regression. `[I]`

**Q170. How do we detect app drift?**
Pin app version + catalogue snapshot; hash the command registry; run a smoke task after upgrades; mark
stale skills. `[R: C2; I]`

**Q171. How much human review is needed?**
At least: approve the brief/claims, review the final artifact, approve print/publish; sample routine
runs; 100% review for new task families. `[I]`

**Q172. What is the failure taxonomy?**
Model/planning error, tool/schema error, state/selection error, quality/gate failure, rights/policy
failure, infrastructure failure, and evaluation error. Each needs a distinct response. `[I]`

**Q173. What is a named refusal?**
A specific error with context and a fix path (e.g., missing template, gate failed, path outside root),
never a silent fallback or success-shaped empty result. `[R: C3,L4; I]`

**Q174. How do we make runs idempotent?**
Stable run IDs, dedupe by input hash + task, no duplicate publish, and resume from checkpoints rather
than replaying side effects. `[R: L3; I]`

**Q175. How do we recover from a crash?**
Durable episode/action records + checkpoint; on restart, resume the last verified step; if a write may
have landed, reconcile before retrying. `[V: B4; I]`

**Q176. What privacy rules apply?**
Customer art and briefs are confidential; local processing, access control, retention limits, no
training on customer data without permission. `[I]`

**Q177. What licensing rules apply?**
Craft apps are MIT/Apache-2.0 with asset exceptions; fonts/stock/AI outputs need recorded rights; do not
strip attribution/trademarks. `[V: A1–A4]`

**Q178. Can we claim Adobe compatibility or legal clearance?**
No blanket claim. State per-app format support and require human trademark/legal review; “Adobe
alternative” is descriptive, not legal clearance. `[V: A1–A4; I]`

**Q179. Which model should the agent use?**
Use a strong tool-calling model for planning, a cheaper model for extraction/classification, and
evaluate on the golden suite; model names are volatile, so pin and re-test. `[I]`

**Q180. What is the release gate?**
Typecheck/lint/tests, golden eval, gate pass threshold, no regressions, security review, human sign-off,
and a rollback path. `[I]`

---

## Part 10 — Roadmap and final decision (Q181–Q200)

**Q181. Should we build now?**
Yes, but Phase 0 first: freeze the current state, define the golden set, and instrument a baseline.
Do not start with a fine-tune or a full computer-use agent. `[I]`

**Q182. What is Phase 0?**
Inventory apps/commands, choose 10 goldens, record baseline pass/attempts/cost, define the episode
schema and the human rating rubric. `[I]`

**Q183. What is Phase 1?**
Craft Conductor + direct command gateway + Experience Ledger + verifier; one app family; no autonomous
publish; 10 goldens running. `[I]`

**Q184. What is Phase 2?**
Retrieval of similar cases, skill drafts, promotion gate, regression suite; expand to PhotoCraft and
print masters. `[I]`

**Q185. What is Phase 3?**
Optional fine-tuning/RL on successful, rights-cleared trajectories with a frozen eval; only if
retrieval/skills plateau. `[I]`

**Q186. What staffing is realistic?**
One agent/backend engineer, one design/quality owner, part-time infra/security; a designer is not
optional for taste evaluation. `[I]`

**Q187. How long to a useful MVP?**
Estimate **6–10 weeks** for one app family and 10 goldens with a working ledger/eval; this is an
estimate, not a measured schedule. `[I, ESTIMATE]`

**Q188. What will it cost?**
Infrastructure is small (existing VPS/Postgres/containers); model calls and engineering time dominate.
Do not quote a dollar figure without a measured token/task baseline. `[U]`

**Q189. What is the primary success metric?**
Gate-pass rate on held-out goldens at first attempt, attempts per accepted artifact, human rework
minutes, cost per accepted artifact, and zero unsafe publishes. `[I]`

**Q190. What is the realistic target?**
A reliable junior-to-mid production designer with human art direction: it executes briefs, follows
brand rules, hits technical specs, and escalates taste decisions. `[I]`

**Q191. Will it be better than a human designer?**
No verified basis. It may be faster/cheaper on repetitive production and more consistent on gates;
creativity, originality, client judgement and accountability remain human. `[I]`

**Q192. What should we reuse?**
Eko’s planner/dependency/pause patterns; DeerFlow’s memory manager and LangGraph runtime; OpenAdapt’s
verify/read-back discipline; Playwright MCP’s structured browser access; the Craft CLI/MCP command
registry and 33 skills. `[V: E1–E7,D1–D4,B1–B5; R: C1–C4]`

**Q193. What should we avoid?**
Building a generic agent framework, starting with pixel-only computer use, fine-tuning before an eval
set, trusting a success screen, autonomous publishing, and claiming “learning” without a baseline.
`[I]`

**Q194. What is the biggest unknown?**
How to evaluate design quality reproducibly. Technical gates are measurable; taste/brief fit needs a
human rubric and inter-rater agreement. `[I]`

**Q195. What evidence is still needed?**
100+ instrumented episodes, a 50-task golden corpus, a blind human rating study, a cost/latency
baseline, and an independent security review. `[I]`

**Q196. What decision is requested now?**
Approve Phase 0/1: build the Craft Conductor + ledger + golden harness, with Eko/DeerFlow as optional
orchestration references, not a rewrite. `[I]`

**Q197. What can be built today?**
The direct command gateway, episode/eval tables, `command_lookup` integration, a verifier wrapper, and
10 goldens using the existing Craft CLI. `[R: C2,C3,L4]`

**Q198. What must not be claimed?**
That the current agent learns, that Eko is a durable learning system, that Craft apps are 1:1 Adobe
replacements, that Adobe tutorials transfer exactly, or that the system beats human designers. `[I]`

**Q199. Final recommendation?**
**Hybrid:** use existing harnesses for orchestration, build the Craft-specific tool/verification/
experience layer, and keep humans on taste and publish. `[I]`

**Q200. One-sentence answer?**
Existing agents can already operate the Craft tools through CLI/MCP, but none of them learns art
direction or verifies design effects; DeerFlow Forge must add the command gateway, experience ledger,
evaluation and promotion loop to become a genuinely improving design agent. `[I]`

---

## Command and tutorial coverage boundary

This program did **not** obtain or verify a complete command list for every Craft app. The honest
coverage is:

| Surface | Coverage here |
|---|---|
| VectorCraft | **918/918 commands, 64/64 groups** in the local snapshot, indexed by the atlas `[R: C1,C2]` |
| PhotoCraft | **965/965 rows, 38/38 groups** in the local snapshot, indexed by the atlas `[R: C1,C2]` |
| FilmCraft | README reports **650+ engine commands**; not enumerated in this dossier; its own `commands`/MCP registry must be snapshotted before claiming full coverage `[V: A3]` |
| EffectCraft / DesignCraft / LightCraft / others | Not installed or catalogued here; no full command claims `[U]` |
| Adobe tutorials | Official Learn hubs identified; **not all tutorials scraped or executed**; the 50-task curriculum is a proposal `[V: AD1; I]` |

Therefore, “all the commands from all the Craft apps” is **not** a verified statement yet. The atlas is
complete for VectorCraft/PhotoCraft; the next catalogue task is FilmCraft (and then the remaining apps)
using the same snapshot/extractor/checker pattern.

## What to borrow from each system

| Source | Mechanism worth borrowing | Do not copy blindly |
|---|---|---|
| **Eko** | Planner → dependency graph; `dependsOn` parallel branches; pause/resume controls; MCP tool discovery; streaming callbacks; human-in-the-loop callbacks | In-memory task state and `task_snapshot` are not a durable memory service; docs were 503 |
| **DeerFlow 2.x** | LangGraph durable runtime; `MemoryManager` contract; per-user/per-agent facts; injection budget; staleness/consolidation; middleware chain; sandbox/skills | Its memory is facts/preferences, not design-skill induction; the harness is heavy |
| **OpenAdapt** | Compile repeated work into a program; verify before/after writes; read-back from the system of record; halt on uncertainty | Replay-only; not for novel visual design |
| **Playwright MCP** | Accessibility snapshots over pixels; deterministic browser actions; workspace roots | Web-only; cannot edit a vector document |
| **browser-use / Agent-S / UI-TARS** | Perception/grounding fallback for UI-only surfaces; benchmark discipline | Pixel-only path is slower/fragile for command-capable apps; vendor scores need reproduction |
| **ArtCraft apps** | Typed command registry; CLI/JSON/MCP parity; gates and provider geometry; clean-room assets | Some apps alpha; format compatibility varies; do not call them 1:1 Adobe copies |

## Agent-native tool contract (required for the Craft Conductor)

Every tool exposed to the agent must:

1. **Return structured JSON** on stdout (or an MCP structured result): `ok`, `data`, `error_code`,
   `message`, `artifacts[]`, `gate_report?`, `next_actions?`.
2. **Use stable IDs** (command ids, run ids, artifact hashes), never prose-only success.
3. **Expose state** before mutation: document open, selection, app version, catalogue version, roots.
4. **Validate at the boundary**: unknown id, wrong type/range, path outside root, missing document.
5. **Be idempotent or carry an idempotency key**; publishing must dedupe.
6. **Declare destructive effects**; require approval for overwrite/publish.
7. **Bound outputs**: truncate logs and schemas, return paths/handles plus a retrieval command.
8. **Provide a probe/dry-run where possible**; where the CLI has none, require a copy and a new output.
9. **Fail closed** with a named `E_*` code and a fix hint; never return an empty success.
10. **Record evidence** automatically (artifact path/hash, dimensions/DPI, gate values).

This is the practical application of `agent-native-design` and `agent-experience`: progressive
disclosure, structured output, bounded context, delegated auth, safety boundaries.

## First curriculum extract (proposal)

| # | Adobe-derived task | Craft target | Command family | Verification |
|---|---|---|---|---|
| 1 | Flat logo to vector | VectorCraft | `imageTrace.*`, `object.path.*` | SVG paths/fills + 2400 px render |
| 2 | AI badge cleanup/trace | VectorCraft + pipeline | `prep_print_art`, `craft_trace` | ten gates, `ok:true` |
| 3 | Photo crop/retouch/export | PhotoCraft | `image.crop`, `filter.*`, `image.adjustments.*` | dimensions/DPI/colourspace |
| 4 | Print master | PhotoCraft/VectorCraft | `image.imageSize`, `document.export` | 300 DPI, transparent white, provider canvas |
| 5 | Type/outline/retype | VectorCraft | `type.createOutlines`, `text.*` | font status, bounds, gate |
| 6 | Mask/cutout | PhotoCraft | `select.*`, `layer.layerMask.*` | mask on black/white, edge audit |
| 7 | Smart object/filter | PhotoCraft | `layer.smartObjects.*`, `filter.*` | source/link status, non-destructive check |
| 8 | Ad layout | VectorCraft/DesignCraft | `file.new`, `file.place`, `text.create`, `document.export` | exact px, safe margins, contrast |
| 9 | Short film cut/grade | FilmCraft | command registry + `effects.setParam` | export playable, loudness/colour |
| 10 | Multi-page layout/PDF | DesignCraft | command registry | PDF pages/fonts/bleed |

## Reference architecture

```text
┌────────────────────────────────────────────────────────────────────┐
│  Brief / operator UI / DeerFlow or Eko orchestrator                │
│  (plan, clarify, choose task family, request approval)             │
└──────────────────────────────┬─────────────────────────────────────┘
                               │ typed task envelope
┌──────────────────────────────▼─────────────────────────────────────┐
│  Craft Conductor                                                   │
│  plan → retrieve cases/skills → execute → verify → reflect → record│
└───────┬──────────────────────┬──────────────────────┬──────────────┘
        │                      │                      │
┌───────▼────────┐   ┌─────────▼──────────┐   ┌───────▼──────────────┐
│ Tool Gateway   │   │ Verifier           │   │ Experience Ledger    │
│ command_lookup │   │ exit + JSON        │   │ episodes/actions/    │
│ craft_run      │   │ artifact/dim/DPI   │   │ artifacts/evals/     │
│ inspect/batch  │   │ Craft gate report  │   │ lessons/skills       │
│ print/publish  │   │ read-back/visual   │   │ (Postgres)           │
└───────┬────────┘   └─────────┬──────────┘   └───────┬──────────────┘
        │                      │                      │
┌───────▼──────────────────────▼──────────────────────▼──────────────┐
│  Existing Craft apps / pod_pipeline / Fourthwall / MCP             │
│  VectorCraft · PhotoCraft · FilmCraft · EffectCraft · DesignCraft  │
└────────────────────────────────────────────────────────────────────┘
```

**Optional Eko sidecar:** a Node process for interactive/planning experiments, calling the same Tool
Gateway over HTTP/MCP. It must not own durable state; the ledger is the source of truth.

### Minimum ledger schema (proposal, not yet migrated)

```sql
agent_episode(id, account_id, brief, task_family, app_versions jsonb,
              plan jsonb, status, started_at, finished_at, cost jsonb)
agent_action(id, episode_id, seq, tool, params jsonb, result jsonb,
             error jsonb, duration_ms, created_at)
agent_artifact(id, episode_id, kind, path, sha256, width, height, dpi,
               format, gate_report jsonb)
agent_eval(id, episode_id, technical jsonb, human jsonb, verdict,
           reviewer, created_at)
agent_lesson(id, scope, task_family, content, evidence_episode_ids,
             version, status, promoted_at, superseded_by)
agent_skill(id, name, version, preconditions, steps jsonb, gates jsonb,
            success_count, failure_count, status)
```

### Learning loop states

`brief → planned → retrieved → executing → verified → rated → archived`
with side states `refused`, `needs_human`, `failed`, `rolled_back`.

Promotion rule: a lesson/skill moves `draft → candidate → active` only after **N independent
successes** (start N=3), a golden regression pass, and human approval. Every active version is pinned
into the episode; a failure creates a new version, not an in-place edit.

## Build vs integrate

| Option | Fit | Why |
|---|---|---|
| Build a new framework | Poor | duplicates planner/tool/MCP/checkpoint work; no Craft-specific advantage |
| Eko as core | Medium | MIT, planner/MCP/deps/pause; in-memory state and a second runtime; docs stale |
| DeerFlow as core | Medium–good | Python/LangGraph, memory, sandbox, subagents; heavier harness; art tools absent |
| LangGraph/own state machine | Good | fits Python/Postgres; durable; no second runtime; requires building tool/eval layer |
| browser-use / Agent-S / UI-TARS | Fallback | GUI-only; useful for web/admin gaps, not the primary command path |
| OpenAdapt | Pattern | compile/verify/read-back discipline; not generative design |
| **Craft Conductor + ledger** | **Best first move** | directly addresses the missing tools, evidence and improvement loop |

## 90-day plan (proposal)

| Week | Deliverable | Gate |
|---|---|---|
| 0–1 | Freeze baseline; 10 goldens; episode schema; human rubric | Goldens run on current pipeline |
| 2–3 | Tool gateway: lookup, run, inspect, verify; allowlist/roots | One trace + one retouch end-to-end |
| 4–5 | Ledger + eval recorder + run viewer | Every run has actions/gates/artifacts |
| 6–7 | Retrieval over past cases; parameter suggestions | A/B improves first-attempt gate rate or attempts |
| 8–9 | Skill drafts + promotion gate + regression | 3 skills promoted with evidence |
| 10–12 | Expand to print/vector + FilmCraft; human study | 50 goldens, no unsafe publish |

## Claim register

| Claim | Evidence | Status |
|---|---|---|
| Eko is a real MIT JS agent framework at 4.1.3 | package.json, GitHub API, source | **VERIFIED** |
| Eko’s memory is in-process/snapshot, not durable | `memory.ts`, `snapshot.ts`, `eko.ts` | **VERIFIED** |
| Devain Eko is a separate prompt-only project | `devain/eko` README/site | **VERIFIED** |
| eko-agent-github is third-party, not official | owner/repo metadata/README | **VERIFIED** |
| Craft apps are independent, not 1:1 Adobe copies | repo READMEs, ArtCraft article | **VERIFIED** |
| Adobe tutorials transfer only conceptually | app compatibility docs + missing formats | **VERIFIED / bounded** |
| Local DeerFlow Forge has no learning loop | package.json, orchestrator, schema, MCP | **VERIFIED (local)** |
| Public DeerFlow has cross-session facts memory | memory.mdx, MEMORY docs | **VERIFIED (public repo)** |
| Local repo runs “DeerFlow 2.2 / DeepSeek V4.1-Flash” | README only; no code/name verification | **UNVERIFIED** |
| Eko documentation details beyond source/README | docs host 503 | **UNVERIFIED** |
| Agent is “better than a human designer” | no benchmark | **NOT SUPPORTED** |
| Any current system learns art direction from gates | no evidence found | **NOT DOCUMENTED** |

## Evidence gaps / explicit UNVERIFIED

- **Eko docs host 503** (2026-11-05): architecture claims beyond source/README/examples are unverified.
- **No Eko benchmark** was reproduced; no claim about its planning reliability on Craft tasks.
- **No Adobe tutorial was executed** in this program; the curriculum is a design, not a measured result.
- **No Craft command was executed in this research program**; all counts and gates are from the
  existing local catalogues and prior verified runs, not re-run now.
- **No current agent was tested** on a blind design-quality benchmark; “better than human” is untested.
- **Vendor numbers** (browser-use 90.5%, Agent-S 72.60%, Mem0 92.5, Zep 94.8) are author/vendor claims,
  not independently reproduced.
- **Cost/time estimates** are `ESTIMATE`, not measured.
- **Public DeerFlow memory** was read from docs; the deployed instance’s config/version was not
  inspected, so “the deployed agent learns” remains unverified.

## Bibliography

| ID | Source | URL / local path | Read |
|---|---|---|---|
| E1 | FellouAI/Eko README | https://github.com/FellouAI/Eko | 2026-11-05 |
| E2 | Eko package manifest | https://raw.githubusercontent.com/FellouAI/Eko/main/package.json | 2026-11-05 |
| E3 | Eko core source (`eko.ts`, `plan.ts`, `tree.ts`, `memory/*`, `types`, `agent/base.ts`) | `C:\Users\Riley\Desktop\_research\eko\packages\eko-core\src` | 2026-11-05 |
| E4 | GitHub API metadata/releases/commits | https://api.github.com/repos/FellouAI/Eko | 2026-11-05 |
| E5 | Eko examples | https://github.com/FellouAI/Eko/tree/main/example | 2026-11-05 |
| E6 | Devain Eko | https://github.com/devain/eko · https://devain.github.io/eko/ | 2026-11-05 |
| E7 | eko-agent-github | https://github.com/1692775560/eko-agent-github | 2026-11-05 |
| A1 | VectorCraft README | https://github.com/storytold/vectorcraft | 2026-11-05 |
| A2 | PhotoCraft README | https://github.com/storytold/photocraft | 2026-11-05 |
| A3 | FilmCraft README | https://github.com/storytold/filmcraft | 2026-11-05 |
| A4 | ArtCraft Crafting Apps article | https://gigazine.net/gsc_news/en/20261005-artcraft-crafting-apps/ | 2026-11-05 |
| D1 | bytedance/deer-flow README | https://github.com/bytedance/deer-flow | 2026-11-05 |
| D2 | DeerFlow memory docs | https://github.com/bytedance/deer-flow/blob/main/frontend/src/content/en/harness/memory.mdx | 2026-11-05 |
| D3 | DeerFlow memory improvements/cognitive style | `backend/docs/MEMORY_IMPROVEMENTS.md`, `MEMORY_COGNITIVE_STYLE.md` | 2026-11-05 |
| D4 | DeerFlow architecture | `backend/docs/ARCHITECTURE.md` | 2026-11-05 |
| L1 | DeerFlow Forge README | `C:\Users\Riley\Desktop\DeerFlow Forge\README.md` | 2026-11-05 |
| L2 | `pod_pipeline/orchestrator.py`, `runner.py`, `config.py` | local repo | 2026-11-05 |
| L3 | `sql/schema.sql`, `pod_pipeline/db.py` | local repo | 2026-11-05 |
| L4 | `pod_pipeline/mcp_server.py` | local repo | 2026-11-05 |
| L5 | `AGENTS.md`, `package.json` | local repo | 2026-11-05 |
| B1 | browser-use README | https://github.com/browser-use/browser-use | 2026-11-05 |
| B2 | Agent-S README | https://github.com/simular-ai/Agent-S | 2026-11-05 |
| B3 | UI-TARS-desktop README | https://github.com/bytedance/UI-TARS-desktop | 2026-11-05 |
| B4 | OpenAdapt README | https://github.com/OpenAdaptAI/OpenAdapt | 2026-11-05 |
| B5 | Playwright MCP README | https://github.com/microsoft/playwright-mcp | 2026-11-05 |
| B6 | Agentic README | https://github.com/ghua8088/Agentic | 2026-11-05 |
| M1 | Mem0 README | https://github.com/mem0ai/mem0 | 2026-11-05 |
| M2 | Letta README | https://github.com/letta-ai/letta | 2026-11-05 |
| M3 | Graphiti README | https://github.com/getzep/graphiti | 2026-11-05 |
| M4 | Zep paper | https://arxiv.org/abs/2501.13956 | 2026-11-05 |
| M5 | Voyager README/paper | https://github.com/MineDojo/Voyager · arXiv:2305.16291 | 2026-11-05 |
| M6 | Reflexion paper | https://arxiv.org/abs/2303.11366 | 2026-11-05 |
| M7 | ExpeL paper | https://arxiv.org/abs/2308.10144 | 2026-11-05 |
| M8 | Agent Workflow Memory paper | https://arxiv.org/abs/2409.07429 | 2026-11-05 |
| C1 | Craft command atlas | `blueprint/files/skills/artcraft-command-atlas/` | 2026-11-05 |
| C2 | `command_lookup.py`, `group-index.md`, `check_atlas.py` | same | 2026-11-05 |
| C3 | `tools/craft_trace.py`, `prep_print_art.py`, skills | local repo | 2026-11-05 |
| C4 | `craft-mcp-drive` skill | installed/locally authored | 2026-11-05 |
| AD1 | Adobe Learn hubs | https://www.adobe.com/learn/photoshop · /illustrator · /premiere-pro · /after-effects | 2026-11-05 |

---

*End of dossier. The next action is Phase 0 approval, not a claim that the agent already learns.*

