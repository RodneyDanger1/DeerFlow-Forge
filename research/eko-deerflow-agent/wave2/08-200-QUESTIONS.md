# Wave 2 — 200 Questions on Harness Engineering, Learning, and the Forge Conductor

**Date:** 2026-11-05 · **Owner:** Riley · **Status:** `VERIFIED SAMPLE` for cited facts; design items are
`PROPOSED`. This is a **new** 200, distinct from the first dossier's 200; together they are 400.

**Evidence source IDs**

| ID | Source |
|---|---|
| S1 | `wave2/01-STACK-VPS.md` / `01-VPS-FACTS.json` — read-only VPS audit |
| S2 | `wave2/02-AGENT-REPOS.md` / `02-REPOS.json` — primary-source harness verification |
| S3 | `wave2/03-CRAFT-SURFACE.md` / `03-SURFACE.json` — read-only Craft CLI/MCP probes |
| S4 | `wave2/04-HARNESS-DESIGN.md` / `04-DESIGN.json` — Forge Conductor design |
| S5 | `wave2/05-HARNESS-CODE.md` / `05-CODE.json` — harness code archaeology |
| S6 | `wave2/06-LEARNING-LOOPS.md` / `06-LEARNING.json` — learning/memory/RL research |
| S7 | `wave2/07-EXAMPLES.md` / `07-SKILL-SPECS.md` — original examples and skill specs |
| P1 | `../REPORT.md` — first 200-question Eko/Craft/DeerFlow dossier |

**Labels:** `[V]` executed/observed this wave · `[R]` read from a file/source · `[D]` design decision ·
`[U]` unverified/not documented · `[E]` estimate. Answers are deliberately short; the source file has
the full evidence. No claim here is a substitute for the named probe.

---

## Part A — Hosting, VPS, and the DeepSeek key (Q1–Q20)

**Q1. What host is the stack actually running on?**
`srv2108523` at `179.197.88.181`: Ubuntu 26.04.1, kernel 7.0.0-38, KVM, AMD EPYC 9354P, **2 vCPU**,
**7,935 MB RAM**, **96 GB disk / 36 GB free**, Docker 29.9.2. `[V: S1]`

**Q2. What services are active?**
`deerflow-forge-console.service` (127.0.0.1:8091), `pod-mcp.service` (0.0.0.0:8765),
`pod-worker.timer` (every 60 s), Docker, and the separate `ridgeboundia-*` app/Caddy stack. `[V: S1]`

**Q3. Is DeerFlow actually running?**
Yes: `/opt/deer-flow`, backend **2.2.0**, containers `deer-flow-gateway`, frontend, nginx, redis; it is
the real agent runtime, not the console. `[V: S1]`

**Q4. What model is configured?**
`deepseek-flash`, display name **“DeepSeek V4.1 Flash”**, context window **1,048,576**, output
`max_tokens: 8,192`, vision/thinking enabled, timeout 600 s, subagent `max_running: 3`. `[V: S1,S4]`

**Q5. Where does the DeepSeek key live?**
`DEEPSEEK_API_KEY` is present by **name only** in the DeerFlow environment; `config.yaml` references
`$DEEPSEEK_API_KEY`; no base URL is configured. No secret was printed. `[V: S1,S4]`

**Q6. Is the key valid / has a live call succeeded?**
**UNVERIFIED.** Evidence for past turns: 1,163 LangGraph checkpoints; counter-evidence: `runs = 0`, no
`deepseek` line in the gateway log. A live completion was deliberately not made (spends owner quota).
`[V/U: S1]`

**Q7. Does the pipeline use the DeepSeek key?**
No. `pipeline.env` has zero `DEEPSEEK*` names; `pod_pipeline` has no LLM client; the console has no AI
dependency. Only DeerFlow calls the model. `[V: S1]`

**Q8. Can the pipeline run a Craft step today?**
**No.** `/opt/pod-pipeline/bin/{vectorcraft,photocraft,designcraft,effectcraft,filmcraft}-cli` are
122–124-byte `sh` stubs that exit **127**. `[V: S1,S3]`

**Q9. Which real Craft binaries exist?**
VectorCraft **0.21.1** and PhotoCraft **0.20.2** under `/opt/craft/.../bin/`; DesignCraft, EffectCraft
and FilmCraft are **absent host-wide**. `[V: S1,S3]`

**Q10. Why does the pipeline fail even with real binaries?**
`routes.py` invents argv contracts marked `ASSUMPTION`: `vectorcraft-cli trace` is not a subcommand and
`photocraft-cli --input` is not accepted. Real surfaces are `run --in/--cmd/--commands/--export`,
`convert`, `commands`, `mcp`, etc. `[V: S1,S3]`

**Q11. Is the craft MCP registered in DeerFlow?**
No. Only `mcpServers.forge` (`http://172.17.0.1:8765/`) is registered; VectorCraft/PhotoCraft MCP
stdio servers are not. `[V: S1]`

**Q12. Do the Craft apps expose MCP at all?**
Yes: VectorCraft `mcp` exposes **33 tools**, PhotoCraft `mcp` **26** (probed handshake); headless
`render_preview`/`doc_inspect` are available, GUI-only tools refuse. `[V: S3]`

**Q13. Is there a display/GPU for GUI automation?**
No: `DISPLAY` unset, no X sockets, no `/dev/dri`, no GPU. `Xvfb` exists but `glxinfo` is absent.
Headless MCP/run is the viable path. `[V: S1,S3]`

**Q14. What is the database state?**
`pod` Postgres 16.15 is **empty**: 0 rows in all five tables (accounts, assets, jobs, products, sync
logs), 8,127 kB schema-only. There are no episode/skill/eval tables. `[V: S1]`

**Q15. Is the deployed pipeline a git checkout?**
No `/opt/pod-pipeline/.git`; sync was proven by **26/26 sha256-identical** files versus local. The console
checkout is at `32fc71f`, 9 commits behind local `d9dc2fe`. `[V: S1]`

**Q16. Can the console control the agent?**
No. It is a pure viewer at `127.0.0.1:8091`; no write API, no job controls, no auth in this environment.
`[V: S1]`

**Q17. What is the biggest security issue found?**
`pod-mcp` listens on **0.0.0.0:8765** unauthenticated; ufw restricts it to Docker ranges, but the `pod`
user is in the Docker group, so a triggered job can reach host-root-equivalent Docker access. `[V: S1]`

**Q18. What are the capacity constraints for a new agent?**
2 vCPU / 7.9 GB with **2.5 GB swap already used**; 24.55 GB reclaimable Docker images + 10.06 GB build
cache; no GPU. Design for **≤2 episodes**, one global Craft semaphore, loopback-only ports. `[V: S1,S4]`

**Q19. What is the publish blocker?**
`products.json` has `fourthwall_template_id: REPLACE_WITH_TEMPLATE_ID` for all five product types, so
publish would refuse even with working Craft steps. `[V: S1]`

**Q20. What is the single biggest blocker to the user's goal?**
The **Craft execution path is not wired**: stub binaries + wrong argv + unregistered MCP. The model and
harness are already hosted; the missing piece is the typed Craft tool gateway and verification plane.
`[V: S1,S3; D: S4]`

---

## Part B — Existing harnesses and terminology (Q21–Q40)

**Q21. Is Eko a viable base today?**
No. It is MIT and real, but **4.1.3**, release v4.1.0, **last commit 2026-03-03**, no durable
memory/eval/learning, JS-only; treat as reference/optional control plane. `[V: S2]`

**Q22. What does Eko give us?**
Planner, dependency-aware multi-agent execution, pause/resume/abort, `task_snapshot`, MCP, human tools,
stream callbacks. Use the **patterns**, not the runtime. `[V: S2]`

**Q23. Does Eko learn or remember across sessions?**
No. `EkoMemory` is a token-managed message buffer; no vector store or durable cross-session memory
claim. `[V: S2]`

**Q24. What does DeerFlow 2.2 provide?**
LangGraph runtime/checkpoints, subagents, sandbox, skills, durable DeerMem memory (FTS5 facts +
summaries + write gates), MCP both ways, channels/cron, DeepSeek adapter. MIT, active daily. `[V: S2]`

**Q25. Does DeerFlow learn design?**
No. It stores facts/preferences and can stage skills, but its own docs say the learning strategy,
candidate generation and quality evaluation are **not included**. `[V: S6]`

**Q26. What is “Harness 2”?**
`google-research/harness2` = **Harness²**, arXiv 2610.14224, Apache-2.0, ~22.8k stars; a research
blueprint with 8 editable components and a Propose–Probe–Compose loop, not a production server. `[V: S2]`

**Q27. What is “superagent”?**
Ambiguous: (a) DeerFlow's own category name; (b) `deepseek-ai/dsh-superagent-prototype`, MIT research
prototype explicitly “not an official DeepSeek product”; (c) an HTTP client / security product. Qualify
the term. `[V: S2]`

**Q28. What is “Hermes”?**
`NousResearch/hermes-agent`, MIT, ~260k stars, v0.22.7, Python; self-described self-improving agent with
auto-skills/FTS5 memory, subagents, gateway, “$5 VPS” claim. Not deployed here. `[V: S2]`

**Q29. What is a “hyperagent”?**
Also ambiguous: Meta `facebookresearch/HyperAgents` (CC BY-NC-SA), `hyperbrowserai/HyperAgent` (AGPL),
`hyperagent.com` (closed), and an older bandit algorithm. There is no single official product. `[V: S2]`

**Q30. What about “metas hyperagent”?**
**NOT FOUND** as an exact project. The plausible referents are Meta HyperAgents or the Stanford
Meta-Harness Terminal-Bench artifact; neither should be named as the user's project without clarification.
`[V: S2]`

**Q31. What about “Hermes hyperagent”?**
**NOT FOUND** as an official project/phrase. It is a conflation of Hermes Agent and Hyperagent(s); do not
invent a merged product. `[V: S2]`

**Q32. Is browser-use relevant?**
Only for browser-only research/admin. MIT, 120k stars, browser actions, MCP, replay; no memory,
orchestration or approval. Not a Craft base. `[V: S2]`

**Q33. Is Agent-S relevant?**
It is a real GUI agent with strong OSWorld claims, but needs a display and has no orchestration/memory/
approval; not viable on this headless 2 vCPU host. `[V: S2]`

**Q34. Is UI-TARS-desktop relevant?**
GUI/vision-first, Apache-2.0, MCP kernel, no memory/eval; same display constraint. `[V: S2]`

**Q35. Is Playwright MCP relevant?**
Yes as a deterministic **web fallback**: accessibility snapshots, read-only hints, no vision. Use it only
where no native Craft command exists and read back the result. `[V: S2]`

**Q36. Which projects should not be used?**
Meta HyperAgents (CC BY-NC-SA), `hyperbrowserai/HyperAgent` (AGPL), hyperagent.com (closed), Eko as base
(dormant), dsh-superagent-prototype (self-declared non-prod), Harness² as runtime, unlicensed artifacts.
`[V: S2]`

**Q37. Can we reuse code from donor repos?**
Reuse **mechanisms and interfaces** with attribution; do not copy large proprietary/verbatim blocks.
Write original adapters. License metadata matters for redistribution, but the architectural ideas are what
we need. `[D: S7]`

**Q38. What is the build-vs-buy decision?**
Integrate **DeerFlow 2.2** as the runtime; build the **Forge Conductor** control plane; borrow Harness²’s
method and OpenAdapt’s verification; do not build a new planner. `[V: S2,S4]`

**Q39. Why is DeerFlow the best substrate?**
Already hosted with the DeepSeek key, MIT, Python/LangGraph, subagents, memory, MCP, sandbox; the only
candidate that is self-hostable and already running. `[V: S1,S2]`

**Q40. What must be added on day one?**
Craft MCP registration, absolute-path/version pinning, a typed command gateway, artifact/read-back
verification, episode ledger, and an operator approval queue. `[V: S3; D: S4]`

## Part C — Harness internals and code donation (Q41–Q60)

**Q41. What is an agent harness, precisely?**
The runtime around a model: prompts, tool registry/schemas, execution loop, context management,
subagents, sandbox, approval, checkpoints, telemetry and evaluation. The model is one component; the
harness determines what it can reliably do. `[D: S4,S5]`

**Q42. What is the minimal agent loop?**
Observe → decide → call tool → observe result → update context → repeat until a terminal verdict or
budget. A tool result must be validated, not merely appended. `[D: S4]`

**Q43. Why use an explicit state machine?**
Crash/retry/approval need legal transitions. A free loop cannot answer “is this run resumable?” or
“did this side effect already happen?” Forge uses `planned → executing → verifying → resolved` plus
`needs_human/failed/rolled_back`. `[D: S4,S6]`

**Q44. What belongs in a tool registry entry?**
Tool id, app/version probe, absolute binary path, surface (CLI/MCP), read/write roots, allowed roles,
command schema reference, timeout, idempotency, expected outputs and refusal codes. `[D: S4]`

**Q45. How do we keep context bounded?**
Typed handoffs and artifacts-by-hash: the model gets a brief, ≤40 command schemas, document state and
bounded summaries; full files stay on disk. Do not paste whole logs or all 918 commands. `[D: S4]`

**Q46. Should we use subagents?**
Yes, but capability-scoped: conductor, art director, vector operator, raster operator, print verifier,
blind critic, memory curator. Handoffs are structured records, not freeform chat. `[D: S4]`

**Q47. What do checkpoints buy?**
Resume after a crash and an audit of what the agent believed at each step. DeerFlow/LangGraph already
provides checkpoints; Forge’s ledger is the durable source of truth for Craft artifacts. `[D: S4]`

**Q48. Where does human approval fit?**
Destructive operations, print/publish, new task families, and skill promotion. The approval is bound to
an artifact hash/version, not a vague “yes.” `[D: S4]`

**Q49. How should the sandbox work?**
Container with no network, read-only inputs, writable run dir, CPU/memory/process caps. The current host
has no GPU and limited RAM, so one global Craft semaphore is required. `[D: S4; V: S1]`

**Q50. What does MCP add and not add?**
Adds a standard tool interface and discovery. It does **not** add memory, evaluation, approval, or
protection from a tool that lies. Those are harness responsibilities. `[D: S4]`

**Q51. How should the model adapter work?**
Treat model id/context/output cap as configuration; surface provider errors; never assume a model can
see images or call tools just because the name says so. Verify capabilities. `[V: S1,S4]`

**Q52. What retry policy is defensible?**
Retry only named transient failures (timeout, 429, 5xx, killed process); never retry a gate failure or
an unknown write. The current pipeline retries only transient exits, max 2. `[R: S1]`

**Q53. How do we make tool calls idempotent?**
A content hash of tool + normalized params + target + episode, persisted before the call; duplicate calls
return the prior result. Publishing needs a natural-key dedupe (product/template/asset). `[D: S4]`

**Q54. What telemetry is required?**
Each tool call/params/result/exit/duration, artifact hashes, gate values, critic output, tokens/cost,
approval, and final verdict. Without this the ledger is fiction. `[D: S4]`

**Q55. What does “code donation” mean here?**
Borrowing a mechanism/interface pattern from an open-source harness and writing an original adapter for
our contracts. It is not copy-pasting a file into production. `[D: S7]`

**Q56. Is vendoring/forking a donor repo safe?**
Only with a pinned commit, review, tests and license compliance; for a 2 vCPU host, prefer small adapters
over a second runtime. A fork creates a maintenance liability. `[D: S2,S7]`

**Q57. What is the adapter interface?**
`Probe()` version/capabilities → `Plan()` typed spec → `Execute()` idempotent tool call → `Verify()`
artifact/read-back → `Normalize()` result/refusal. The donor’s internals do not leak into the conductor.
`[D: S7]`

**Q58. What is the biggest stitching risk?**
Two sources of truth (DeerFlow state vs Forge ledger) and mismatched error semantics. Pick one durable
owner (Forge ledger) and treat the other as a cache. `[D: S4]`

**Q59. Which donor patterns are worth borrowing?**
OpenAdapt: read-back/stop-on-uncertainty. Harness²: eight editable components + Propose–Probe–Compose.
DeerFlow: durable runtime, subagents, memory substrate. Eko: dependency graph/pause. OpenHands/SWE-agent:
tool loop and test-driven verification. `[V: S2; D: S4]`

**Q60. What must not be copied?**
Verbatim proprietary code, license-incompatible components, fake “success” wrappers, a GUI automation
stack with no read-back, and any memory that treats retrieved text as instructions. `[D: S4,S7]`

---

## Part D — Learning, memory and RL (Q61–Q80)

**Q61. What are the five distinct “learning” claims?**
In-context reflection, retrieval memory, procedural skill/lesson libraries, supervised fine-tuning, and
reinforcement learning. They have different evidence and costs. `[V: S6]`

**Q62. What level is the current stack?**
**L0**: no episode/skill/eval tables, no token ledger, no Craft MCP registered, no learning loop.
`[V: S1,S6]`

**Q63. What is L1 and can we build it?**
L1 = episodic/reflective memory: store verified/failed episodes and retrieve lessons. Buildable now with
Postgres + text retrieval; no GPU. `[D: S6]`

**Q64. What is L2?**
Procedural memory: versioned skills/workflows induced from verified episodes, with preconditions,
command ids, gates and rollback. Buildable after L1. `[D: S6]`

**Q65. What is L3?**
Supervised fine-tuning/preference optimization of weights on rights-cleared trajectories. Needs a large
corpus, GPU/compute, eval and safety; **not available** here. `[V: S6]`

**Q66. What is L4?**
RL on verifiable environment rewards (PPO/GRPO/RLOO). Needs open weights, GPU fleet, rollouts, a
deterministic verifier and reward-hacking defenses; **not available** here. `[V: S6]`

**Q67. What does Reflexion actually show?**
Verbal reflection in an episodic buffer improves later trials **without weight updates**; it is L1.
It does not prove reflection works without reliable external feedback. `[V: S6]`

**Q68. What does ExpeL show?**
An agent can extract natural-language insights from past tasks and recall them at inference without
parametric updates; the closest template for Forge’s lesson store. `[V: S6]`

**Q69. What does Voyager show?**
An ever-growing library of executable skills, composed over time, with environment feedback; L2, not
fine-tuning. `[V: S6]`

**Q70. What does Agent Workflow Memory show?**
Inducing reusable workflows from trajectories and injecting them improves web-navigation success
(paper reports 24.6%/51.1% relative gains); L2. `[V: S6]`

**Q71. What does DeerFlow’s memory actually do?**
DeerMem stores facts/summaries with confidence/token budgets/FTS recall and skill-evolution staging;
the host supplies evidence/staging/rollback but **not** learning strategy or quality evaluation. `[V: S6]`

**Q72. Are Mem0/Graphiti/Zep relevant?**
As external memory patterns: fact extraction, temporal validity, hybrid retrieval. Their benchmark
numbers are vendor/paper claims; none is installed or measured here. `[V: S6]`

**Q73. What is retrieval poisoning?**
A wrong/adversarial memory retrieved later and treated as guidance. Mitigation: memory is data, never
instructions; evidence ids; scope/version pins; rollback. `[V: S6]`

**Q74. What is staleness?**
A lesson pinned to VectorCraft 0.21.1 or an old catalogue becomes wrong after an upgrade. Pin app version
+ catalogue hash and expire/demote on drift. `[V: S6]`

**Q75. What is the promotion rule?**
Draft → candidate → active requires ≥3 independent successes, **Wilson lower bound** not just count, golden
regression pass, and human approval. At 3/3 the Wilson 95% lower bound is ≈0.44, so count alone is weak.
`[V: S6]`

**Q76. What is the acceptance function?**
Verifier-computed gates AND artifact contract/hash AND rights AND, for taste, a human score ≥3. A model’s
self-report is never the reward. `[D: S6]`

**Q77. Why is reward hacking a real risk?**
Proxy rewards (gates, path counts, speed) can be optimized while quality drops; RLVR can improve scores
with randomly assigned rewards; specification gaming can generalize to reward tampering. `[V: S6]`

**Q78. What does the random-reward result imply?**
A reported RL gain can be an artifact of the optimizer/model family; validate across ≥2 checkpoints and
keep a held-out, human-reviewed set. `[V: S6]`

**Q79. Can this VPS train the model?**
No. The model is an API, there is no GPU, 2 vCPU/7.9 GB, and no verifier/training stack. L3/L4 are out of
reach; do not promise them. `[V: S6]`

**Q80. Can the agent “learn with no direction”?**
Only in reset-able, verifiable simulators. Forge must be autonomous **within an approved brief**, with
supervised promotion; never autonomous publish, gate changes, reward changes or skill activation.
`[V: S6]`

---

## Part E — Craft command, MCP and visual surface (Q81–Q100)

**Q81. What are the exact registry counts?**
VectorCraft **918 commands / 64 groups**; PhotoCraft **965 / 38**; catalogues are current and the local
VectorCraft file is byte-identical to `/opt/craft`. `[V: S3]`

**Q82. What does `enabled:false` mean?**
It is **state**, not capability: 771/918 VectorCraft and 783/965 PhotoCraft rows appear disabled in the
no-document snapshot; `select.all` still ran successfully (count 3). Open/select a document first.
`[V: S3]`

**Q83. What are VectorCraft’s MCP tools?**
**33 tools** + 3 resources + 5 prompts + 4 templates; includes `command_list`, `command_run`,
`command_batch`, `doc_inspect`, `render_preview`, `open_file`, `export`, draw/select/paint tools.
`[V: S3]`

**Q84. What are PhotoCraft’s MCP tools?**
**26 tools** + 2 resources; includes `doc_open`, `doc_inspect`, `doc_export`, `doc_export_layers`,
`command_run`, `command_batch`, `render_preview`, `ui_*` (GUI-only). `[V: S3]`

**Q85. How do roots/refusals behave?**
Read/write roots are deny-by-default; exact refusals include `automation path rejected: outside the
read root` and `absolute paths must be inside the automation root`. `[V: S3]`

**Q86. What concurrency hazard was found?**
PhotoCraft’s MCP server **does not serialize `tools/call`**; piped dependent calls raced and returned
out of order (“no document open”). The harness must await each reply. `[V: S3]`

**Q87. What do Craft exit codes mean?**
`craft_trace`: 0 success, **1 gate failure**, **2 refusal**. PhotoCraft: 2 is argument-parser only;
semantic refusals use 1. Do not treat every non-zero as the same thing. `[V: S3]`

**Q88. Does an artifact exist only when gates pass?**
No. `craft_trace` writes the artifact **before** evaluating gates; a failed run still leaves a PNG. File
existence is not a pass. `[V: S3]`

**Q89. Is the text gate proof of retyping?**
No. `retyped_text_present` is vacuous when `retype_boxes == 0`; text-bearing art must provide a retype
spec and boxes. `[V: S3]`

**Q90. Is `prep_print_art.ok` trustworthy?**
No. `ok` is hard-coded true; the 2.5× upscale limit is a **warning**. It observed `ok:true` at 3.609×;
parse `warnings`, not only `ok`. `[V: S3]`

**Q91. What visual metrics were measured?**
Engine render vs rsvg gave SSIM 0.99994 / RMSE 0.0011 on the test; whitening a 120×100 block (~4% of
frame) only moved SSIM to 0.9787. Global metrics miss localized defects. `[V: S3]`

**Q92. What should the critic use instead?**
Tile-wise SSIM/diff bounding boxes, crop evidence, edge/white-residual checks and a blind rubric — not one
global score. `[D: S3,S4]`

**Q93. What are render preview limits?**
VectorCraft inline preview ≤4096 px, PhotoCraft ≤2048 px (per docs); previews are evidence, not final
proof. `[V: S3]`

**Q94. Can we fall back to GUI screenshots?**
Not today. Apps launch under Xvfb, but `--control` panics due to missing `libxkbcommon-x11.so`; the control
port never opens. Headless MCP/CLI is the only path. `[V: S3]`

**Q95. Which app should be first?**
**VectorCraft**: complete machine-checked catalogue, 33-tool semantic MCP, deterministic batch up to
100k steps, and gate tooling already implemented/run. PhotoCraft second. `[V: S3]`

**Q96. Why is FilmCraft not a target?**
No FilmCraft binary exists; `/opt/pod-pipeline/bin/filmcraft-cli` is a 122-byte stub exiting 127. Its
“650+” count is README-only. `[V: S1,S3]`

**Q97. Do Adobe tutorials transfer?**
Concepts/workflows only; not exact command ids or UI. The Craft apps are independent implementations and
some file formats differ. `[V: S3; P1]`

**Q98. What is the correct CLI form for a trace?**
Not `vectorcraft-cli trace`. Use `run --in FILE --commands steps.json --export OUT` with
`select.all`, `imageTrace.make`, `imageTrace.expand`, or the `craft_trace` wrapper. `[V: S3]`

**Q99. What is the first safe end-to-end task?**
A 1024² flat badge: cutout → trace → expand → SVG export → 2400 px render → gates, on copies, with all
tool calls and gate values recorded. `[D: S3,S4]`

**Q100. What is the biggest Craft blocker?**
The pipeline stubs/argv mismatch and unregistered Craft MCP; the real 918/965 command surfaces are
available and must be wired with absolute paths. `[V: S1,S3]`

## Part F — Computer use, visual verification and critics (Q101–Q120)

**Q101. What is a computer-use agent?**
A loop that observes a GUI (pixels/a11y), chooses an action, executes it and re-observes; it needs
grounding, recovery and a stop condition. It is a fallback, not the primary Craft path. `[D: S4]`

**Q102. Why prefer native commands for Craft?**
Typed commands are deterministic, cheaper, easier to validate and already expose the same engine as the
UI. Pixel actions cannot read the document model and are brittle on a headless host. `[V: S3; D: S4]`

**Q103. Can a screenshot prove success?**
No. A screen can show “saved” while the write failed; OpenAdapt’s fault study found 54/72 bad saves
reported as saved by screen checks. Always read back the artifact/system of record. `[V: S2]`

**Q104. What is the evidence ladder?**
Process result → artifact exists/hash → domain gates → render ladder → blind visual critique → human
rubric. A pass requires all applicable rungs; a missing rung is `unverified`. `[D: S4]`

**Q105. What is a blind critic?**
A visual critic that never sees exit codes, gate results or the operator’s success claim; it receives the
brief and rendered images only, and must cite crop evidence per dimension. `[D: S4]`

**Q106. Why crop evidence?**
Global SSIM/RMSE miss a 4% localized defect (measured 0.99994 → 0.9787 after a 120×100 white block).
Crop/tile evidence is the only way to localize a defect. `[V: S3]`

**Q107. How do we stop hallucinated critiques?**
Schema-constrained output: each dimension requires a crop box, observation and severity; missing/ungrounded
dimensions are rejected; the critic cannot override a failed deterministic gate. `[D: S4]`

**Q108. What is a false-pass rate?**
The fraction of bad artifacts the critic calls good. It is not measured for `deepseek-flash` vision; a
50-defect labelled corpus is required before trusting it. `[U: S4]`

**Q109. What should the human rubric cover?**
Brief fit, hierarchy, typography, colour/brand, print safety, originality; anchored 1–5 scores with two
reviewers for promotion/publish; disagreements recorded. `[D: S4]`

**Q110. Is rendering reproducible?**
Not guaranteed: fonts, rsvg/engine versions and exporters can drift. Record versions + artifact hashes and
use a tolerance policy for comparisons. `[D: S4]`

**Q111. What is the render ladder?**
Deterministic engine render → independent renderer (rsvg) → thumbnail/100% crops → metrics/diff → critic.
Disagreement between engine and independent render is a defect signal. `[D: S3,S4]`

**Q112. Why hash artifacts?**
A path can be overwritten; the hash binds the gate/critique/approval to exact bytes. Every artifact row
stores SHA-256 and dimensions/DPI. `[D: S4]`

**Q113. What can a headless run not verify?**
Window state, dialogs, live UI panels and GUI-only tools error headless. `ui_screenshot`/`type_text`
require bridge/control mode. `[V: S3]`

**Q114. Is Playwright a good fallback?**
For web-only surfaces (storefront/admin), yes: deterministic accessibility snapshots, read-only hints.
It still needs system-of-record read-back. `[V: S2]`

**Q115. Is browser-use needed?**
Only for browser research/admin tasks that a skill cannot do via API; not for Craft art. `[V: S2]`

**Q116. Does DeepSeek V4.1 Flash support vision?**
The deployed config reports vision enabled; actual accuracy on print defects is **not measured**. Do not
assume capability from the config alone. `[V: S1; U]`

**Q117. What is the vision critic’s largest risk?**
Confident false passes on subtle defects (fringe/halo/ghost text). Mitigate with labelled tests, human
review, deterministic gates and a “cannot assess” verdict. `[D: S4]`

**Q118. What should the critic return?**
`verdict`, per-dimension score, defects with crop boxes/severity, confidence, unseen regions, and an
explicit “cannot assess” list; no prose-only approval. `[D: S4]`

**Q119. How do we validate the critic?**
A labelled defect set (white fringe, halo, ghost text, speck, wrong colour, bad margin), measure precision/
recall/false-pass, and re-test on every model/prompt change. `[D: S4]`

**Q120. Can the critic overrule a gate?**
No. A failed gate is terminal for shipping; critic-vs-gate disagreement becomes `needs_human`, not a pass.
`[D: S4]`

---

## Part G — Data, state, security and cost (Q121–Q140)

**Q121. Where should Forge state live?**
A new `forge` Postgres DB/role, separate from `pod`; same Postgres instance is fine on this host. `[D: S4]`

**Q122. What tables are required?**
Episode, event, handoff, tool_call, artifact, gate, critique, eval, resolution, job, case/retrieval,
brand_fact, skill, lesson, conflict, budget, role token. `[D: S4]`

**Q123. Why hash-chain events?**
It makes tampering/accidental mutation detectable and gives replayable evidence. Each event stores
`prev_hash`/`hash`. `[D: S4]`

**Q124. How are writes made idempotent?**
Content-addressed idempotency keys on tool calls; unique constraints; duplicate publish blocked by
product/template natural key. `[D: S4]`

**Q125. How do we detect source mutation?**
Hash inputs before/after the episode and record `source_mutation`; any mutation fails the episode. `[D: S4]`

**Q126. How strict are roots?**
Read/write roots are explicit per role and episode; absolute paths outside them are refused, not
normalized silently. `[V: S3; D: S4]`

**Q127. Does the console have auth?**
No in this deployment (`VITE_AUTH_ENABLED=false`), and it is loopback-only. Any operator UI needs auth or
an SSH tunnel. `[V: S1]`

**Q128. Is the MCP endpoint safe?**
`pod-mcp` is unauthenticated on `0.0.0.0:8765`, restricted by ufw; the pod user has Docker-group access.
Treat it as host-sensitive and move to loopback/auth before exposing. `[V: S1]`

**Q129. Where should secrets live?**
Environment/credential store only; never in prompts, repo, ledger or logs. The DeepSeek key exists only as
an env name/value in the DeerFlow deployment. `[V: S1]`

**Q130. What must gate publish?**
A verified artifact, correct provider template/area, credentials, approval, and a product-state read-back;
no autonomous publish in Phases 0–2. `[D: S4]`

**Q131. Is there a token/cost ledger today?**
No token/usage/cost table in `deerflow.db`; only run/thread metadata. Forge must record per-call and
per-episode cost. `[V: S1]`

**Q132. How should budgets work?**
Per-episode token/time/attempt caps + daily account cap + hard kill switch; a capped call returns a named
refusal, not a silently truncated success. `[D: S4]`

**Q133. How many concurrent episodes?**
At most 2 on this host, with one global Craft-step semaphore; the box already runs other services and
2.5 GB swap is used. `[V: S1; D: S4]`

**Q134. What is the backup plan?**
Nightly `pg_dump` of `forge`, artifact-store checksums, and a restore drill; the ledger/artifacts are the
only source of truth. `[D: S4]`

**Q135. How do we roll back?**
Pointer flip to the previous skill version; restore artifact/episode references; keep superseded rows;
never delete evidence. `[D: S4]`

**Q136. What is retention?**
Keep episodes/evidence for audit; expire large previews/caches; keep rights/provenance as long as the
asset exists. `[D: S4]`

**Q137. What audit does an operator need?**
Who approved what, which model/version, which app/catalogue, which artifact hash, which gate/critic
results, and the cost. `[D: S4]`

**Q138. What refusal codes are needed?**
`E_COMMAND_UNKNOWN`, `E_PARAM_REJECTED`, `E_ROOT_DENIED`, `E_APP_DRIFT`, `E_GATE_MISSING`,
`E_GATE_FAILED`, `E_SURFACE_UNVERIFIABLE`, `E_PUBLISH_NOT_APPROVED`, `E_BUDGET`. `[D: S4]`

**Q139. What observability is required?**
Per-episode trace, tool calls, retries, gate values, critic output, token/cost, queue depth, lease expiry,
and a dashboard that distinguishes “not configured” from “failed.” `[D: S4]`

**Q140. What rights/provenance must be stored?**
Source, licence, permitted uses, attribution, AI generation source/model where relevant, and expiry; a
missing rights record blocks production. `[D: S4]`

---

## Part H — Build plan and architecture (Q141–Q160)

**Q141. What is the “third plane”?**
A new `forge-*` control plane beside the existing console and pipeline, owning the agent/ledger/verifier;
it calls the pipeline/Craft, but does not live inside them. `[D: S4]`

**Q142. What roles does the conductor have?**
Conductor, art director, vector operator, raster operator, print verifier, blind visual critic, memory
curator. Six specialists + supervisor. `[D: S4]`

**Q143. Why typed handoffs?**
They bound context, encode intent, and make every delegation auditable/replayable. Freeform chat between
agents loses state and cannot be verified. `[D: S4]`

**Q144. What is the tool gateway?**
One registry/entry point for exact CLI/MCP commands, with absolute paths, version probe, roots, role
allowlist, schema, timeout, idempotency and refusal mapping. `[D: S4]`

**Q145. What does the verifier check?**
Exit/result shape, artifact existence/hash/dimensions/DPI, gate report, source mutation, and read-back;
missing evidence is `unverified`, never pass. `[D: S4]`

**Q146. Why a separate visual critic?**
To avoid the actor grading its own work; blind input and crop-cited output reduce confirmation bias. `[D: S4]`

**Q147. What is the memory curator?**
The only role allowed to write lessons/skill candidates after evidence review; it cannot promote without
the gate/human approval. `[D: S4]`

**Q148. Why a Postgres queue instead of a broker?**
The host is small and already runs Postgres; `FOR UPDATE SKIP LOCKED` gives transactional leasing with no
new service. `[D: S4]`

**Q149. What is the model’s job?**
Planning, drafting, classification and critique — bounded, schema-constrained calls. It is not the source
of truth for success or reward. `[D: S4]`

**Q150. What are the phases?**
0 baseline/goldens; 1 tool gateway+verifier; 2 ledger+critic; 3 retrieval; 4 skills; 5 print/second app;
6 hardening. `[D: S4]`

**Q151. What is Phase 0 exactly?**
Fix/replace the Craft CLI shims; freeze 10 goldens; capture catalogue/version hashes; define rights/rubric;
record current pass/fail honestly. `[D: S4; V: S1]`

**Q152. What is the Phase 1 acceptance test?**
One VectorCraft trace and one PhotoCraft retouch end-to-end, every call in the ledger, zero source
mutations, gate/artifact evidence present. `[D: S4]`

**Q153. What is the Phase 2 acceptance test?**
A full episode can be reconstructed from the ledger alone; critic schema validation is 100%; a 20-render
stability test is recorded. `[D: S4]`

**Q154. What is Phase 3?**
Optional retrieval/skill promotion after Phase 2; A/B with a null-result option. Fine-tune/RL is not in the
90-day plan. `[D: S4]`

**Q155. What should be reused?**
DeerFlow runtime/checkpoints/memory; OpenAdapt read-back; Harness² improvement method; Eko dependency/
pause patterns; Craft CLI/MCP; the existing 33 skills. `[V: S2; D: S4]`

**Q156. What should not be built?**
A new planner/runtime, a browser/GUI base, a second memory product, a fine-tuning stack, or an autonomous
publisher. `[D: S4]`

**Q157. What staffing is realistic?**
One engineer + design owner + part-time infra/security; the design owner is mandatory for taste/approval.
`[D: S4]`

**Q158. How long is the MVP?**
90-day plan: Phase 0–2 in 5–6 weeks, skills by ~9 weeks, print/second app by ~11. Estimate only. `[E: S4]`

**Q159. What will it cost?**
Infrastructure is small (existing VPS), but model calls + engineering time dominate. Measure tokens/cent
per accepted artifact before quoting a dollar figure. `[D: S4]`

**Q160. What is the final acceptance?**
A held-out golden suite with first-attempt pass, zero unsafe publishes, source-mutation zero, cost/log
complete, and a human-approved artifact. `[D: S4]`

---

## Part I — Evaluation, truth and claim discipline (Q161–Q180)

**Q161. What do the labels mean?**
`VERIFIED` executed/read this wave; `READ` source read but not run; `INFERRED`; `UNVERIFIED`; `NOT
DOCUMENTED`. Never promote a lower label without evidence. `[D: S1–S7]`

**Q162. Can we claim “100% truth”?**
Only for observed facts with a source/probe. Designs, estimates and future behaviour are `PROPOSED`; the
honest answer is a labelled corpus, not an absolutist claim. `[D]`

**Q163. Which claims are unsupported?**
“Better than a human designer,” “the agent learns art,” “FilmCraft is installed,” “the key is valid,”
“the pipeline runs end-to-end today,” “GUI screenshots prove print quality.” `[V: S1,S3,S6]`

**Q164. What would prove “better than human”?**
A blind, representative study on held-out briefs with expert raters, inter-rater agreement and a baseline;
none exists. `[D: S4]`

**Q165. What is the benchmark today?**
A 10-golden smoke set + gate metrics; 50-golden corpus is proposed. No design-quality benchmark has been
run. `[D: S4]`

**Q166. What is a golden task?**
Frozen input/rights, brief, reference plan, required gates, human rubric, accepted artifact hash. `[D: S4]`

**Q167. What is the A/B design?**
Same model/app/catalogue, arm A baseline vs arm B retrieval/skills, ≥3 runs, blind human review, CI and
cost/latency reported. `[D: S4]`

**Q168. How do we measure human agreement?**
Two reviewers on the five-dimension rubric; report disagreement/α; do not average it away. `[D: S4]`

**Q169. Is a null result acceptable?**
Yes. If retrieval/skills do not improve held-out pass rate, disable them; that is a valid scientific
result, not a failure to hide. `[D: S4]`

**Q170. How is reward hacking prevented?**
Verifier outside agent writes, gate config hash, held-out set, evidence diversity, human review, no
self-reported reward. `[V: S6]`

**Q171. How is the model evaluated?**
Compare models/prompts on the same goldens, measure gate pass/attempts/cost/visual false-pass; do not
assume the newest model wins. `[D: S4]`

**Q172. Who verifies the verifier?**
A separate reviewer/agent re-fetches key claims and re-runs a sample; the author cannot self-certify. `[D: S4]`

**Q173. What citation rule applies?**
Every decision-critical claim has a fetched source/path; no invented URL, id or number. `[D: S1–S7]`

**Q174. How are conflicts handled?**
Name both sources, prefer the live primary source, record in `ERRATA.md`/conflict table; never silently
average. `[D]`

**Q175. How do we handle stale sources?**
Pin versions/dates; re-fetch before policy; mark older than the freshness rule `HISTORICAL`. `[D]`

**Q176. What remains unverified?**
Key validity, model vision accuracy, vision cost, DeerFlow deployed memory internals, GUI capture, full
FilmCraft, human agreement, long-run cost, pgvector availability. `[V: S1–S6]`

**Q177. What does “Harness 2” mean?**
Most likely Google Harness²; confirmed as a real project. Ask the owner if they meant “our second harness”
instead. `[V: S2]`

**Q178. What about “metas hyperagent” / “Hermes hyperagent”?**
No exact official project found; closest are Meta HyperAgents/Meta-Harness and Hermes Agent + Hyperagent.
Do not claim a merged product. `[V: S2]`

**Q179. Is “DeerFlow 2.2” verified?**
The deployed backend is 2.2.0; the public repo reports v2.2.0/2.3.0-dev. The model display name says V4.1
Flash. The key’s live validity is still unverified. `[V: S1,S2]`

**Q180. What is the overall status?**
Research/design is substantially verified; implementation is **not started**; the first blocker is the
Craft execution path, not the model. `[V: S1–S6]`

---

## Part J — Skills, vault, operations and the next move (Q181–Q200)

**Q181. Which five skills are being added?**
`research-corpus-navigator`, `forge-harness-architect`, `harness-code-adapter`, `agent-learning-loop`,
`visual-verification-critic`. Together with `craft-agent-operator`, they cover reading, design, adaptation,
learning and visual proof. `[D: S7]`

**Q182. What does the corpus navigator do?**
Tells an agent which research file/question to read, how to load only the needed slice, and the evidence
labels/conflict rules; prevents dumping 400 questions into context. `[D: S7]`

**Q183. What does the harness architect do?**
Turns the Forge Conductor design into a decision-complete plan: roles, contracts, tables, phases, failure
modes, tests and rollback. `[D: S4,S7]`

**Q184. What does the code adapter do?**
Maps a donor mechanism to our interfaces, writes an original adapter, records provenance/license metadata,
and requires tests/verification; refuses verbatim proprietary copying. `[D: S7]`

**Q185. What does the learning loop skill do?**
Defines L0–L4, the episode/retrieval/promotion contract, Wilson-bound rule, reward design and anti-hacking
checks; prevents “it learns” claims without evidence. `[D: S6]`

**Q186. What does the visual verifier do?**
Runs the evidence ladder: artifact/hash → gates → independent render → tile metrics/crops → blind critic →
human rubric; refuses exit-code/screenshot-only proof. `[D: S3,S4]`

**Q187. How are the skills installed?**
Repo source of truth `blueprint/files/skills/`; installer mirrors `references/` to DSH and Hermes; validator
and semantic checker must pass. `[D: S7]`

**Q188. Where is the Desktop copy?**
`C:\Users\Riley\Desktop\Ridgeboundia-Agent-Research\` with `00-START-HERE.md`, `research/`, `skills/`,
`examples/`, `INDEX.json`; generated from the corpus after validation. `[D]`

**Q189. Where is the vault copy?**
`/srv/vaults/storefront/30-reference/art-learning/29-AGENT-HARNESS-RESEARCH/` plus an index entry in
`00-ART-LEARNING-INDEX.md`; same files, Obsidian-compatible markdown. `[D]`

**Q190. What does the index contain?**
File map, word/source counts, decisions, reading orders, evidence labels, gaps, maintenance protocol, and a
machine-readable `INDEX.json`. `[D: S7]`

**Q191. How is the corpus maintained?**
Append-only errata; re-fetch before changing a policy; version each report; never delete contradicting
evidence; add new questions as a new wave, not by rewriting old ones. `[D]`

**Q192. What triggers a re-verify?**
App/Craft version, model/config, DeerFlow version, host capacity, command catalogue, or a failed episode.
`[D]`

**Q193. What are the top security tasks?**
Move MCP to loopback/auth; restrict Docker-group access; rotate/validate the DeepSeek key; sandbox Craft;
no secrets in logs; no autonomous publish. `[V: S1; D: S4]`

**Q194. What is the next 90 days?**
Phase 0 fix shims/goldens; Phase 1 gateway/verifier; Phase 2 ledger/critic; Phase 3 retrieval; Phase 4
skills; Phase 5 print/second app; Phase 6 hardening. `[D: S4]`

**Q195. Is Phase 3 fine-tuning?**
No; Phase 3 in the 90-day plan is retrieval/skills. Fine-tuning/RL is optional later, only after a frozen
eval and rights-cleared corpus. `[D: S4,S6]`

**Q196. Can we fine-tune DeepSeek V4.1 Flash?**
No documented support in the sources reviewed; the model is an API. Treat as **NOT DOCUMENTED**. `[V: S6]`

**Q197. Can this host do RL?**
No. No GPU, 2 vCPU, API model, no rollouts/training stack; L4 is not available. `[V: S6]`

**Q198. Is “superagent” the future?**
DeerFlow already calls itself a super-agent harness; use its runtime, but the unique value is the Craft
control plane, not a new superagent. `[V: S2; D: S4]`

**Q199. What is the recommendation?**
Build the Forge Conductor on the existing DeerFlow 2.2 + DeepSeek runtime; fix the Craft tool path first;
add ledger/verifier/critic/promotion; defer GUI/RL/fine-tune. `[D: S4]`

**Q200. One-sentence answer?**
The VPS already hosts a capable super-agent harness and model, but its Craft execution path is stubbed and
unverified; the unique, buildable advance is a third Forge plane with a typed Craft gateway, artifact/read-
back verification, a blind visual critic, and an evidence-gated learning loop. `[V: S1–S4]`

---

*End of Wave 2 questions. Companion files: `01`–`07`; first-wave 200 in `../REPORT.md`.*


