# Wave 2 / 02 — Agent Harnesses: Primary-Source Verification and Terminology

**Task:** `task-2` — verify the real state of candidate agent harnesses and the user's terminology.
**Owner:** `agent-repos-scout` (delegated subagent).
**Date:** 2026-11-05 (America/Chicago). All live fetches were performed on this date; GitHub API timestamps are UTC.
**Scope:** read-only research. No production file was modified. Files written by this task are only this document and `02-REPOS.json`.

---

## 0. Method, source hierarchy, evidence labels

### 0.1 Method

1. **Repository metadata** was read from the GitHub REST API (`/repos/{owner}/{repo}`, `/releases`, `/tags`, `/commits`, `/contents`, `/readme`, `/license`, `/search/repositories`) with no token — the public, canonical record for stars, forks, license, push date, and release tags.
2. **Project claims** were checked against repository source files fetched from `raw.githubusercontent.com` at each repo's default branch: `README.md`, `package.json`, `pyproject.toml`, `setup.py`, `server.json`, `CHANGELOG.md`, and selected source files. README marketing was **not** accepted as standalone proof; where possible the same claim was confirmed in a manifest or in code (e.g. Eko's `pauseTask`/`abortTask` in `packages/eko-core/src/agent/eko.ts`, DeerFlow's LangGraph dependency in `backend/pyproject.toml`).
3. **Papers and official product sites** were fetched directly (`arxiv.org/abs/2610.14224`, `harness2.github.io`, `hermes-agent.nousresearch.com`, `hyperagent.com`, `deepseek.com/en/harness/`).
4. **Search** used GitHub's repository search API and two general web searches, strictly as *discovery* for terminology. Any project surfaced that way was then verified by opening its own repository record or site.
5. Every number below is a point-in-time snapshot. Stars/forks/push dates change daily and must be re-fetched when an exact value matters.

### 0.2 Evidence labels used in this document and in `02-REPOS.json`

| Label | Meaning |
|---|---|
| `E1` | GitHub REST API record (official repository metadata: stars, forks, license, push, release tag). |
| `E2` | Repository source file at `main` (README/manifest/code) — fetched raw. Official project text, but still self-reported. |
| `E3` | Official paper or official product website fetched directly. |
| `E4` | Secondary source (blog/press/community repo) — used only to locate a project, never as proof of a claim. |
| `INFERRED` | A conclusion drawn by this task from two or more verified observations; not stated verbatim by a source. |
| `UNVERIFIED` | A claim in a README that this task could not independently confirm in code, manifest, or official docs. |
| `NOT FOUND` | Exhaustive enough search did not locate a primary source; no project is invented to fill the gap. |

**Rule applied:** if a term could not be tied to an official repository, package, paper, or product page, it is reported as `NOT FOUND` with the search evidence — never replaced by a plausible-sounding project.

### 0.3 Coverage note

`bytedance/deer-flow`'s README is 380,614 bytes and `config.example.yaml` is 194,493 bytes. They were read selectively (headings, architecture, subagent, sandbox, memory, deployment, security, and provider sections), not end-to-end. `CHANGELOG.md` (1,024,197 bytes) was read only as its head (current `2.3.0` milestone). Every claim attributed to those files below comes from a quoted or near-quoted section that was actually read.

---

## 1. Ten verified headline facts

1. `E1` **bytedance/deer-flow** is real and current: latest release **v2.2.0 (2026-11-04)**, backend manifest version `2.3.0-dev`, **85,028 stars / 11,947 forks**, **MIT**, Python backend `>=3.12`, last push **2026-11-05**. It self-describes as an "open-source **super agent harness**" (README line 12) — the phrase is DeerFlow's own, not a separate product.
2. `E1` **FellouAI/eko** (canonical repo casing) is real but **stale**: npm/package version **4.1.3**, latest GitHub release tag **v4.1.0 (2025-12-29)**, **4,960 stars / 446 forks**, **MIT**, last commit **2026-03-03** (~8 months before this report), TypeScript.
3. `E2` Eko's advertised controls are visible in code: `pauseTask()`, `abortTask()`, a `task_snapshot` recovery tool, an `McpTool` wrapper, `HumanInteractTool`, and plan/replan/chain agents. Its "memory" is a token-managed message store, **not** durable long-term memory; README makes **no** memory or learning claim.
4. `E1`+`E3` **"Harness 2" exists**: `google-research/harness2` = **Harness²**, *Recursive Agent Harnessing for an Open World* (**arXiv:2610.14224**, submitted 2026-10-09), **22,790 stars / 2,267 forks**, **Apache-2.0**, Python 3.12, created 2026-10-06, last push 2026-11-02.
5. `E1` **"superagent" is ambiguous**: (a) DeerFlow's self-description; (b) `deepseek-ai/dsh-superagent-prototype` — **19,342 stars**, **MIT**, TypeScript, "research prototype for reference only, **not an official DeepSeek product**"; (c) name collisions `forwardemail/superagent` (HTTP client) and `superagent-ai/superagent` (AI security).
6. `E1`+`E3` **"Hermes" is real**: `NousResearch/hermes-agent` — **260,789 stars / 57,574 forks**, **MIT**, Python, **v0.22.7 (2026-11-03)**, official site `hermes-agent.nousresearch.com`, "self-improving AI agent" with a built-in learning loop.
7. `NOT FOUND` **"Hermes hyperagent"** as an exact project or official phrase. Hermes Agent and Hyperagent(s) are two distinct real things; one 3-star community repo (`yurekami/ultragent`) describes combining "HyperAgents + AutoResearch + Hermes Agent + Anthropic harness design", which shows the conflation happens in the wild.
8. `NOT FOUND` **"metas hyperagent"** as an exact project name. Closest primary sources: Meta's **HyperAgents** (`facebookresearch/HyperAgents`, **CC BY-NC-SA 4.0**, arXiv 2603.19461) and the **Meta-Harness** artifact (`stanford-iris-lab/meta-harness-tbench2-artifact`, "76.4% on Terminal-Bench 2.0"). The Harness² results table itself lists "Meta-Harness" as a baseline.
9. `NOT FOUND` a single official "hyperagent". The term maps to at least four things: commercial hosted **Hyperagent** (`hyperagent.com`, closed source, verified), `hyperbrowserai/HyperAgent` (**AGPL-3.0**), `facebookresearch/HyperAgents` (**CC BY-NC-SA 4.0**), and the older ICML-2024 HyperAgent bandit algorithm.
10. `INFERRED` For a Craft-driving harness on this VPS, the decisive constraint is **not** which GUI agent is best — it is that the Craft CLIs on this host expose **headless MCP stdio servers and there is no display/GPU** (reported by sibling audit `task-1`; not independently re-verified here). Browser/GUI agents (browser-use, Agent-S, UI-TARS) are therefore not viable as the execution base, while DeerFlow is already deployed at 2.2.0 with the DeepSeek key configured.

---

## 2. Per-project verified profiles

### 2.1 FellouAI/eko (Eko)

| Field | Verified value | Evidence |
|---|---|---|
| What it is | "Production-ready JavaScript framework" for agents/workflows in computer + browser environments; multi-agent, native MCP, human-in-the-loop | `E2` README 16, 48–59 |
| Canonical repo | `FellouAI/eko` (API `full_name`; user-supplied `FellouAI/Eko` is the same repo, case-insensitive) | `E1` |
| License | **MIT** | `E1` (`license.spdx_id`), `E2` `package.json` |
| Version | **4.1.3** (root `package.json` + `packages/eko-core/package.json` + npm `dist-tags.latest`); latest GitHub release **v4.1.0 (2025-12-29)**; npm modified **2026-03-03** | `E1` releases; `E2` manifests; npm registry |
| Stars / forks | **4,960 / 446** | `E1` |
| Last push / last commit | **2026-03-03T10:22:49Z**; last commit `c3de315af2`, 2026-03-03, message "v4.1.3" | `E1` repo + commits |
| Runtime / language | TypeScript, ESM, pnpm monorepo; runs as browser extension, web app, or Node.js; LLM access through Vercel AI SDK providers (`@ai-sdk/*`), incl. `openai-compatible` for DeepSeek-style gateways | `E2` `package.json`, `packages/eko-core/package.json` |
| Tool interface | npm package `@eko-ai/eko` (library API); native MCP client (`src/mcp/http.ts`, `sse.ts`, `McpTool`); no standalone CLI | `E2` source tree, `tools/index.ts` |
| Engine surfaces | Multi-agent: `agent/chain.ts`, `plan.ts`, `replan.ts`, `a2a.ts`, `browser/`; services: browser, chat; tools: `foreach-task`, `human-interact`, `task-node-status`, `task-result-check`, `todo-list-manager`, `variable-storage`, `watch-trigger`, `task_snapshot` | `E2` `src/` listings |
| Pause/resume | **Confirmed in code**: `pauseTask(taskId, pause, abortCurrentStep?, reason?)`, `abortTask()`, `onTaskStatus` events `pause` / `resume-pause` / `abort`; `task_snapshot` tool archives progress for continuation | `E2` `agent/eko.ts`, `memory/snapshot.ts` |
| Human-in-the-loop | `HumanInteractTool` shipped | `E2` `tools/human-interact.ts` |
| Memory | `EkoMemory`: message history, capacity management, import/export, system prompt; **no vector store, no cross-session persistence claimed** | `E2` `memory/memory.ts` |
| Learning / training | **No claim anywhere in README** (grep for memory/learn/train/eval → 0 hits). No training code | `E2`, `UNVERIFIED`-as-absent |
| Deployment | Embed in a Node/browser/extension app; examples: extension, Node.js (Playwright), web | `E2` README 121–176 |
| Eval harness | None found | `E2` |
| Strengths | Small dependency surface, native MCP, code-level pause/resume/abort + snapshot recovery, parallel dependency-aware agent execution (v3), browser+file agents, MIT | `E2` |
| Limits | **No commits since 2026-03-03** (near-dormant); release tag lags package version; memory is conversation-scoped; no evaluation or learning loop; JS/TS only (awkward for a Python/DeepSeek VPS stack); no desktop-native creative-app tooling | `E1`, `E2`, `INFERRED` |
| Evidence URIs | https://api.github.com/repos/FellouAI/eko · https://api.github.com/repos/FellouAI/eko/releases · https://raw.githubusercontent.com/FellouAI/eko/main/package.json · https://raw.githubusercontent.com/FellouAI/eko/main/packages/eko-core/package.json · https://raw.githubusercontent.com/FellouAI/eko/main/packages/eko-core/src/agent/eko.ts · https://raw.githubusercontent.com/FellouAI/eko/main/packages/eko-core/src/memory/memory.ts · https://raw.githubusercontent.com/FellouAI/eko/main/packages/eko-core/src/memory/snapshot.ts · https://registry.npmjs.org/@eko-ai%2Feko (all accessed 2026-11-05) |

**Verdict:** real, MIT, but a dormant framework. Do not use as the base for a new production harness in 2026-11.

### 2.2 bytedance/deer-flow (DeerFlow 2.x)

| Field | Verified value | Evidence |
|---|---|---|
| What it is | "An open-source **long-horizon SuperAgent harness** that researches, codes, and creates... sandboxes, memories, tools, skill, subagents and message gateway" (repo description); a ground-up rewrite of the v1 deep-research framework, "no longer a framework you wire together... a **super agent harness**... Built on LangGraph and LangChain" | `E1` description; `E2` README 12, 17, 1711–1719 |
| License | **MIT** | `E1`; README badge |
| Version | Latest release **v2.2.0 (2026-11-04)**; backend `pyproject.toml` version **2.3.0-dev**; CHANGELOG head accumulates the **2.3.0** milestone; tags v2.2.0 / v2.1.0 / v2.0.0 | `E1` releases/tags; `E2` `backend/pyproject.toml`, `CHANGELOG.md` |
| Stars / forks | **85,028 / 11,947** | `E1` |
| Last push | **2026-11-05T13:40:33Z**; last commit "fix(mcp): degrade a blob without mimeType instead of failing the tool call (#7800)" | `E1` |
| Runtime / language | Python **>=3.12** backend (FastAPI, LangGraph, LangChain, `langgraph-sdk`), Node.js **22+** frontend (`pnpm`), nginx entrypoint on port **2026**; Docker Compose v2.24+ | `E2` `backend/pyproject.toml`, README 5–6, 595–639 |
| Architecture | LangGraph graph runtime + Gateway service; LangGraph SSE protocol exposed through an **embedded Python client**; thread/checkpoint state with `interrupt_before` / `interrupt_after`; run cancellation and rollback; durable batch items; "Active Goals" continuation ownership | `E2` README 774, 789–848, 1700–1731, 3642+ |
| Subagents | Native `task` tool with `context_mode="isolated"` or `"snapshot"` (snapshot carries the parent's retained conversation + compaction summary at dispatch), `batch_task` durable batches, per-child role/model/tools/skills restrictions, child pause/resume | `E2` README 2740–2769, CHANGELOG head |
| Memory | **DeerMem** long-term memory as default local backend: user-global summaries in `memory.json`, facts as Markdown per agent under `agents/{agent_name}/facts/`, deterministic write gate (scope/durability/authority), SQLite FTS5/BM25 retrieval index under `.retrieval/`, `middleware` vs `tool` modes (`memory_search`, `memory_get`), optional `mem0` and OpenViking-style backends in config | `E2` README 3466–3620; `config.example.yaml` 2329–2493 |
| Skills | Bundled + user/imported skills, `.skill` archives, Capability Center, skill archives/scopes, sandbox-aware skill views | `E2` README 1755+, CHANGELOG head |
| Sandbox | Pluggable sandbox providers (e.g. `deerflow.community.aio_sandbox:AioSandboxProvider`), quarantine records under `{DEER_FLOW_HOME}/sandbox-quarantine`, provisioner/Kubernetes mode optional; a dedicated `backend/scripts/benchmark/sandbox/` suite exists | `E2` README 625–639, 1117–1160, 2991+ |
| MCP | Consumes HTTP/SSE + stdio MCP servers, OAuth flows, per-tool call timeouts, durable background-task adaptation, admin-managed shared servers; docs at `backend/docs/MCP_SERVER.md` | `E2` README 1157–1267 |
| Gateway / channels | Message gateway + channels: Telegram, Slack, Feishu/Lark, WeChat iLink, WeCom, DingTalk; scheduled tasks (cron) with stop conditions; TUI ("Terminal Workbench"); PATs for API access | `E2` README 1457–1476, 3853–4065, 1660–1710 |
| Deployment | Docker (`make docker-init/start/logs`), `make dev`, `make up`; local-trusted model: binds to **127.0.0.1** by default, `BIND_HOST` to expose, first-run `/setup` admin; sizing guidance 8 vCPU/16 GB for a long-running server | `E2` README 595–639, 4185–4204 |
| Model support | Explicit **DeepSeek** support via `deerflow.models.patched_deepseek:PatchedChatDeepSeek`; example "DeepSeek V4 (Thinking)" with `supports_vision: false`; guidance recommends Doubao-Seed-2.0-Code / DeepSeek v3.2 / Kimi 2.5 | `E2` `config.example.yaml` 163–211, 484–494; README 32, 337–389 |
| Eval / observability | Per-run trace file in `.monocle/` (VS Code extension), token-usage dashboard, benchmarks under `backend/scripts/benchmark/*` — **no task-quality eval/promotion loop** | `E2` README 1669, 1725–1743, 2776 |
| Human approval | Interrupt/checkpoint/resume mechanics exist, but there is **no first-class approval queue** in the README | `E2`, `UNVERIFIED` |
| Security posture | README warns the harness has system-command execution and is designed for a **trusted local** deployment; "Gateway admin is equivalent to code execution"; external system/developer role injection rejected with HTTP 400 | `E2` README 4132–4199 |
| Strengths | The most complete self-hostable agent harness among candidates: MIT, LangGraph, subagents (incl. durable batches), durable memory with write gates, skills, pluggable sandbox, MCP both ways, multi-channel gateway, cron, TUI, Python client, DeepSeek adapter, active daily development | `E1`, `E2` |
| Limits | Heavy for a 2 vCPU / 8 GB host (README recommends 8–16 vCPU for server use); loopback-trusted design means exposing it needs hardening; no native desktop/creative-app tools (only filesystem/shell/MCP, so Craft must arrive as MCP servers or skills); token/usage persistence is provider-metadata-based; no built-in task-quality evaluation; large surface to audit | `E2`, `INFERRED` |
| Evidence URIs | https://api.github.com/repos/bytedance/deer-flow · https://api.github.com/repos/bytedance/deer-flow/releases · https://raw.githubusercontent.com/bytedance/deer-flow/main/README.md · https://raw.githubusercontent.com/bytedance/deer-flow/main/backend/pyproject.toml · https://raw.githubusercontent.com/bytedance/deer-flow/main/config.example.yaml · https://raw.githubusercontent.com/bytedance/deer-flow/main/CHANGELOG.md (all accessed 2026-11-05) |

**Verdict:** primary integration candidate. Sibling audit `task-1` (not re-verified here) reports DeerFlow **2.2.0** already running on the target VPS as container `deer-flow-gateway` with `DEEPSEEK_API_KEY` set — that materially lowers integration cost.

### 2.3 browser-use/browser-use

| Field | Verified value | Evidence |
|---|---|---|
| What it is | Open-source Python library for AI browser agents + Browser Use Cloud (stealth browsers, hosted agent API) | `E1` description; `E2` README 50, 66 |
| License | **MIT** | `E1`; README FAQ 311–319 |
| Version | **0.13.14** (pyproject + release, 2026-10-26); latest commit 2026-10-30 | `E1`, `E2` `pyproject.toml` |
| Stars / forks | **120,107 / 13,399** | `E1` |
| Runtime / language | Python **>=3.11,<4.0**; CDP via `cdp-use==1.4.5`; Playwright-backed; MCP dependency `mcp==2.1.1` | `E2` `pyproject.toml` |
| Tool interface | Python library (`Agent`, `Tools`, `Browser`); **MCP server** registered as `com.browser-use/browser-use` (stdio: `uvx browser-use --cli-mcp`; remote streamable-HTTP: `https://api.browser-use.com/v3/mcp`); CLI skill install (`browser-use skill install`); "toolsets for Claude" integration | `E2` `server.json`, README 95–98, 178–219 |
| Deployment | Local Python + local browser; Browser Use Cloud browsers ($0.02/browser-hour); hosted agent API; Dockerfiles present | `E2` README 160–172, 339–348; root listing |
| Memory | No durable memory subsystem claimed; run history is per-run (save/load history for replay) | `E2` README 350–376 |
| Learning / training | No user-facing learning claim; rerun replays recorded clicks without per-step model calls (deterministic replay, not learning) | `E2` README 350–376 |
| Eval | Browser Use Benchmark v2 (60-task subset shown in README); separate `browser-use/benchmark` repo | `E2` README 223–228, 390 |
| Human approval | Not claimed | `UNVERIFIED` |
| Strengths | Very large ecosystem, best-in-class browser action surface (31 actions), cloud stealth browsers, MCP server both stdio and remote, replay/rerun, MIT library, active | `E2` |
| Limits | Browser-only — no native app/desktop tooling; a managed-vendor path (BU2 model/cloud) sits beside the OSS library; no orchestration of specialist subagents; no durable memory; approval/verification not first-class | `E2`, `INFERRED` |
| Evidence URIs | https://api.github.com/repos/browser-use/browser-use · https://raw.githubusercontent.com/browser-use/browser-use/main/README.md · https://raw.githubusercontent.com/browser-use/browser-use/main/pyproject.toml · https://raw.githubusercontent.com/browser-use/browser-use/main/server.json (accessed 2026-11-05) |

**Verdict:** excellent browser tool layer, wrong base for desktop creative apps.

### 2.4 simular-ai/Agent-S

| Field | Verified value | Evidence |
|---|---|---|
| What it is | Open-source computer-use agent framework (`gui-agents`) that operates a real GUI by clicking/typing/scrolling on macOS, Windows, Linux; plus Agent S4 research package | `E2` README 44, 74–82 |
| License | **Apache-2.0** | `E1`; `setup.py` classifier |
| Version | `gui-agents` **0.3.2** (setup.py; latest release v0.3.2, 2025-12-16); `agent_s4` is a separate distribution; last commit 2026-10-21 | `E1`, `E2` `setup.py`, `agent_s4/README.md` |
| Stars / forks | **12,882 / 1,502** | `E1` |
| Runtime / language | Python; GUI drivers `pyautogui`, `pyobjc` (macOS), `pywinauto`/`pywin32` (Windows), `selenium`; OCR `paddleocr`, `pytesseract`; FastAPI/uvicorn service bits | `E2` `setup.py` |
| Tool interface | Python library + console entry point `agent_s=gui_agents.s3.cli_app:main`; hosted Simular API/Sai alternative | `E2` `setup.py`, README 69–72 |
| Memory | "memory" and "retrieval-augmented-generation" are repo topics and paper themes (Agent S2 compositional memory); no durable store verified in code by this task | `E1` topics, `UNVERIFIED` |
| Learning / training | **Agent S4** (2026-10-20, arXiv 2610.28601): a Builder agent evolves a "shadow interface" Python tool library; population-based evolution selects variants by benchmark fitness; research pipeline needs AWS VMs and benchmarks | `E2` `agent_s4/README.md` 1–70 |
| Eval | Strong: OSWorld V2 (21.3% binary with Qwen3.8-27B; S3 72.60% on original OSWorld), ScienceBoard 41.4% → 58.6% | `E2` README 46–56, `agent_s4/README.md` 19–36 |
| Human approval | Not claimed | `UNVERIFIED` |
| Strengths | Real desktop GUI control, OSWorld-leading results, Apache-2.0, compositional S2 architecture, active research (S4), cross-platform | `E2` |
| Limits | Needs a live display/session — a headless VPS without GPU/display cannot run it as-is; heavy dependency set (paddle, OCR, pyautogui); benchmark-tuned rather than productized; learning is a research training loop, not in-product | `E2`, `INFERRED` |
| Evidence URIs | https://api.github.com/repos/simular-ai/Agent-S · https://raw.githubusercontent.com/simular-ai/Agent-S/main/README.md · https://raw.githubusercontent.com/simular-ai/Agent-S/main/setup.py · https://raw.githubusercontent.com/simular-ai/Agent-S/main/agent_s4/README.md (accessed 2026-11-05) |

### 2.5 bytedance/UI-TARS-desktop

| Field | Verified value | Evidence |
|---|---|---|
| What it is | "Multimodal AI Agent stack" shipping **Agent TARS** (general multimodal agent with CLI + Web UI) and **UI-TARS Desktop** (native GUI agent app driven by the UI-TARS model, local or remote computer/browser operators) | `E2` README 13–47 |
| License | **Apache-2.0** | `E1`; README 286 |
| Version | Release **v0.3.1 (2026-10-08)**; Agent TARS CLI v0.3.0 announced 2025-11-05 with AIO sandbox support; last commit 2026-10-09 "chore(all): release 0.3.1" | `E1`, `E2` README 72–79 |
| Stars / forks | **39,551 / 4,025** | `E1` |
| Runtime / language | TypeScript monorepo (pnpm 9, turbo, Node), Electron desktop app; npm `@agent-tars/cli` | `E2` root `package.json`, README 86–97 |
| Tool interface | Agent TARS CLI + Web UI; **MCP-based kernel** with ability to mount extra MCP servers; UI-TARS SDK for GUI automation | `E2` README 95–97, 143, 74 |
| Deployment | Local desktop app (macOS/Windows/Linux) or server/CLI; local or remote operators; optional AIO agent sandbox (`agent-infra/sandbox`) | `E2` README 74 |
| Memory | No durable memory claim in the repository README | `UNVERIFIED` |
| Learning / training | The UI-TARS model is trained by ByteDance, but this repo is the runtime/product; no user-trainable loop | `E2`, `INFERRED` |
| Eval | No benchmark harness in this repository | `E2` |
| Human approval | Not claimed | `UNVERIFIED` |
| Strengths | Polished desktop GUI agent, vision-first multimodal, MCP-native kernel, remote operators (no local install), Apache-2.0, sizable community | `E2` |
| Limits | GUI/vision-first, not an orchestration/learning harness; no memory/eval/approval; needs a graphical session; last commit ~1 month old vs DeerFlow's same-day cadence | `E1`, `E2` |
| Evidence URIs | https://api.github.com/repos/bytedance/UI-TARS-desktop · https://raw.githubusercontent.com/bytedance/UI-TARS-desktop/main/README.md · https://raw.githubusercontent.com/bytedance/UI-TARS-desktop/main/package.json (accessed 2026-11-05) |

### 2.6 OpenAdaptAI/OpenAdapt

| Field | Verified value | Evidence |
|---|---|---|
| What it is | "The open-source, **verified execution layer** for computer-use agents": a person or an agent demonstrates a task once; OpenAdapt **compiles the run into a program** that repeats it with **no model calls**, checks the record before each save and reads it back after, and halts when anything mismatches | `E2` README 5–22 |
| License | **MIT** | `E1`; `pyproject.toml` `license = "MIT"` |
| Version | **1.20.0** (release + pyproject, 2026-11-05 — same day as this report); also `openadapt-flow` 2.6.0 and `openadapt-desktop` 0.26.0 released 2026-11-04 | `E1`, `E2` `pyproject.toml` |
| Stars / forks | **1,863 / 279** | `E1` |
| Runtime / language | Python **>=3.10** (supports 3.10–3.12), local-first CLI (`uvx --python 3.12 openadapt quickstart --break-it`) | `E2` `pyproject.toml`, README 96–104 |
| Tool interface | CLI; **MCP server** (`claude mcp add openadapt -- uvx --python 3.12 openadapt-agent serve`); Agent Skills | `E2` README 160, 288, 322–328 |
| Modes | **Explore** (record a demonstration, read back the save) / **Run** (compiled program, no model calls, checked save + read-back) / **Repair** (stop before saving; agent proposes fix; a person approves) | `E2` README 60–66 |
| Memory | Compiled programs + run receipts + benchmark scoreboards are the durable artifacts; memory here is procedural, not conversational | `E2` README 268–296 |
| Learning | "Learns from any successful run, a person's demonstration or a computer-use agent's verified run, and compiles it into a program" — demonstration compilation, **no weight training** | `E2` README 280 |
| Eval / verification | Exceptional: fault-injection studies — model-built "success" screens reported 54/72 bad saves as saved vs 0/72 with a full read-back; an agent claimed all 30 bad saves in a broken-save test, and `openadapt-flow verify-run` flagged all 30 with no false alarms | `E2` README 68–92 |
| Human approval | Yes — approval gate; a person approves repairs before saving; "A person checks the record before anything is retried" | `E2` README 60–66, 121–130 |
| Deployment | Local process on Windows/macOS/Linux, with a hosted demo/Cloud dashboard for counts/digests/receipts | `E2` README 103, 322–345 |
| Strengths | The only candidate that treats **effect verification** (read the system of record) as a first-class gate; deterministic replay with zero model cost; approval workflow; MIT; very active; MCP + CLI + Skills | `E2` |
| Limits | Oriented to GUI/RPA + EHR-style record systems, not creative-app project files; compiling a program per task is an onboarding cost; small community; Windows-heavy automation heritage; not an orchestrator/multi-agent planner | `E1`, `E2`, `INFERRED` |
| Evidence URIs | https://api.github.com/repos/OpenAdaptAI/OpenAdapt · https://raw.githubusercontent.com/OpenAdaptAI/OpenAdapt/main/README.md · https://raw.githubusercontent.com/OpenAdaptAI/OpenAdapt/main/pyproject.toml · https://raw.githubusercontent.com/OpenAdaptAI/OpenAdapt/main/CAPABILITIES.md (accessed 2026-11-05) |

**Verdict:** not a base harness, but the best **verification/approval pattern** to copy for Craft mutations (read back the artifact, not the "Saved" toast).

### 2.7 microsoft/playwright-mcp

| Field | Verified value | Evidence |
|---|---|---|
| What it is | MCP server exposing Playwright browser automation to LLMs via **structured accessibility snapshots** (no screenshots, no vision model) | `E2` README 1–17 |
| License | **Apache-2.0** | `E1`; `package.json` |
| Version | **0.0.84** (release 2026-10-31; `package.json` 0.0.84); last commit 2026-11-04 | `E1`, `E2` `package.json` |
| Stars / forks | **39,216 / 3,384** | `E1` |
| Runtime / language | TypeScript, Node **>=18**; dependency `playwright` pinned to a date build | `E2` `package.json` |
| Tool interface | MCP only: `browser_click`, `browser_close`, `browser_console_messages`, `browser_drag`, `browser_drop`, `browser_emulate_media`, `browser_evaluate`, … each declares a **Read-only: true/false** hint; CLI options incl. `--init-page`, `--init-script`, user profile, config file, standalone server, Docker | `E2` README `### Tools`, Configuration |
| Deployment | `npx @playwright/mcp@latest` per MCP client; Docker (`docker run -p 8080:8080`); stdio or standalone HTTP | `E2` README 28–90, `package.json` scripts |
| Memory | None (browser profile persistence only) | `E2` |
| Learning / eval | None | `E2` |
| Human approval | Partial: read-only hints per tool + element description "used to obtain permission" — but the server does not itself gate approvals | `E2` README Tools |
| Strengths | Deterministic, token-efficient (a11y tree), first-party Microsoft, widely supported, Apache-2.0, per-tool read-only hints useful for policy engines; the README itself recommends **Playwright CLI + SKILLs** over MCP for high-throughput coding agents | `E2` README 5–11 |
| Limits | Browser-only; no vision; no orchestration/memory/eval; token cost of accessibility trees at scale | `E2` |
| Evidence URIs | https://api.github.com/repos/microsoft/playwright-mcp · https://raw.githubusercontent.com/microsoft/playwright-mcp/main/README.md · https://raw.githubusercontent.com/microsoft/playwright-mcp/main/package.json (accessed 2026-11-05) |

---

## 3. Terminology investigation (the part that prevents hallucinated projects)

Searches run on 2026-11-05: GitHub repository search API for `"harness 2" in:name`, `hyperagent in:name`, `hyperagent in:description`, `superagent in:name`, `hermes-agent in:name`, `hermes hyperagent`, `metas hyperagent`, plus `web_search` for the same phrases. Each hit below was then verified against its own GitHub API record, README, paper, or official site.

### 3.1 "Harness 2" — VERIFIED (real project)

- Canonical: **`google-research/harness2`**, product name **Harness²**, paper *Harness^2: Recursive Agent Harnessing for an Open World*.
- `E1` 22,790 stars / 2,267 forks, **Apache-2.0**, Python, created 2026-10-06, last push 2026-11-02, default branch `main`.
- `E3` Paper arXiv:2610.14224, submitted **9 Oct 2026**, CC-BY-4.0; official site `harness2.github.io` (Google Cloud AI Research + Northwestern).
- `E2` What it does: a harness = "prompts, tools, memory, skills, orchestration"; it exposes **eight editable components** (C1 system prompt, C2 guardrails, C3 memory, C4 tool guidance, C5 subagents, C6 skills, C7 scripts, C8 plugins) and optimizes them with a **Propose–Probe–Compose** loop plus a persistent *improvement harness* (`EXPERIENCE.md`), model weights frozen. Executors: OpenCode (default) and Codex. Benchmarks: JobBench, LAB, WorkBuddy-Bench. Install: Linux + Python 3.12 + `uv`; model-backed runs need Node 20+, gcloud/Vertex AI; a credential-free local demo exists.
- `E2` Explicitly **"not an officially supported Google product"**.
- Community ports to DeepSeek Harness already exist (`Xnmk029/dsh-plugin-harness2`, `Asiu-x/dsh-harness2`) — small, third-party, not official (`E1` search results).
- **Answer for the Lead:** "Harness 2" = Harness², and it is a design blueprint for a self-improving harness, not a production agent server.

### 3.2 "superagent" — AMBIGUOUS (three distinct referents; do not use unqualified)

| Referent | Evidence | Status |
|---|---|---|
| DeerFlow's own category name: "open-source **super agent harness**"; repo topics include `superagent` and `harness` | `E1` description+topics; `E2` README 1711–1719 | **Official self-description** |
| `deepseek-ai/dsh-superagent-prototype` — "dsh-superagent", proactive coding agent for one GitHub repo, packaged as a bundle **for DeepSeek Harness**; **MIT**, TypeScript, 19,342 stars / 2,205 forks, created **2026-10-31**, last push 2026-11-03 | `E1`; `E2` README 1–17 | **Official DeepSeek org, but the README states: "Research prototype for reference only, not an official DeepSeek product… not production-ready"** |
| Name collisions: `forwardemail/superagent` (16,633 stars — AJAX HTTP client for Node/browsers) and `superagent-ai/superagent` (6,837 stars — LLM prompt-injection security) | `E1` search results | Not agent harnesses |

### 3.3 "metas hyperagent" — NOT FOUND as an exact name (two credible referents, unresolved)

- `NOT FOUND` on GitHub repo search (`metas hyperagent` → 9 hits, all third-party experiments) and in web search as a project name.
- Closest primary sources:
  1. **Meta's HyperAgents** — `facebookresearch/HyperAgents`, description "Self-referential self-improving agents that can optimize for any computable task", **2,867 stars / 372 forks**, license **CC BY-NC-SA 4.0** (non-commercial), arXiv **2603.19461**, Python, last push 2026-07-31; `meta_agent.py` / `task_agent.py` / `generate_loop.py`; warns it executes model-generated code (`E1`, `E2`).
  2. **Meta-Harness** — `stanford-iris-lab/meta-harness-tbench2-artifact`, "Meta-Harness: 76.4% on Terminal-Bench 2.0 (Claude Opus 4.6)", 1,249 stars, no license file (`NONE`), Python, last push 2026-03-26 (`E1`, `E2`). Harness²'s own results table lists "Meta-Harness" (average 76.4) as a baseline method (`E3` harness2.github.io).
- **Answer for the Lead:** treat "metas hyperagent" as unresolved user shorthand. Ask which one is meant; do not write "Meta's Hyperagent" as if it were a product. Neither referent is usable as a production dependency (one non-commercial, one unlicensed research artifact).

### 3.4 "Hermes hyperagent" — NOT FOUND as an exact project (conflation of two real things)

- `NOT FOUND`: no official repo, package, paper, or product is named "Hermes hyperagent". GitHub search returned exactly **one** repo: `yurekami/ultragent` (3 stars), described as "Self-referential self-improving agent configuration for Claude Code. Combines HyperAgents + AutoResearch + **Hermes Agent** + Anthropic harness design" — evidence that the phrase circulates as a mashup, not a project (`E1`, `E4`).
- **Hermes** is real and huge: `NousResearch/hermes-agent` — **260,789 stars / 57,574 forks**, **MIT**, Python, **v0.22.7 (2026-11-03)**, last push 2026-11-05, official site `hermes-agent.nousresearch.com` (`E1`, `E3`). README: "The self-improving AI agent built by Nous Research… built-in learning loop — creates skills from experience, improves them during use, nudges itself to persist knowledge, searches its own past conversations"; agent-curated memory + FTS5 session search + Honcho user modeling; isolated subagents; MCP integration docs; six terminal backends (local, Docker, SSH, Modal, Daytona, Vercel Sandbox); gateway to Telegram/Discord/Slack/WhatsApp/Signal/Email/CLI; cron; "Run it on a $5 VPS" (`E2` README 19–31, 176–178).
- **Hyperagent** is separate (see 3.5).
- **Answer for the Lead:** "Hermes hyperagent" almost certainly means either *Hermes Agent* (Nous) or *Hyperagent* (commercial/hyperbrowser), possibly both at once. It is not a fourth project.

### 3.5 "hyperagent" — AMBIGUOUS (four referents, one of them commercial)

| Referent | Evidence | Status |
|---|---|---|
| **Hyperagent** hosted product — `hyperagent.com`: "Agents that ship real, powerful work", a fleet of agents with browsers/shells that deliver websites, video, slides, documents, dashboards; "Hyperagent learns as it goes and generates new memories and skills"; Slack/Telegram/webhook/schedule delivery | `E3` fetched `https://www.hyperagent.com/` | **Commercial, hosted — no source repo found. Not self-hostable** |
| `hyperbrowserai/HyperAgent` — "Hyperagent is Playwright supercharged with AI"; TypeScript, npm `@hyperbrowser/agent`, MCP client, action caching (record/replay without LLM), cloud via Hyperbrowser; 1,604 stars; last push 2026-05-11 | `E1`; `E2` README 24–38; LICENSE text = **GNU AGPL-3.0**, "Copyright (c) 2025 S2 Labs Inc." | **AGPL-3.0 (network copyleft)** |
| `facebookresearch/HyperAgents` — Meta research, self-referential self-improving agents | `E1`; `E2` README 6–8 | **CC BY-NC-SA 4.0 (non-commercial)** |
| `alex-hyperagent/hyperagent-public-skills` — "Free skills from the Hyperagent team", 1,155 stars, **no license**, no README (404) | `E1`, failed `/readme` | Unlicensed; provenance unclear |
| Older academic: `szrlee/HyperAgent` (ICML 2024 bandit algorithm) | `E1` search results | Different domain (not an agent harness) |

**Answer for the Lead:** never write "hyperagent" unqualified in the design doc. Specify *Hyperagent (hyperagent.com, closed)*, *HyperAgent (hyperbrowser, AGPL-3.0)*, or *Meta HyperAgents (CC BY-NC-SA)*.

---

## 4. Capability matrix

Ratings: **strong** = first-class, verified in source/docs; **partial** = exists but constrained or unverified; **none** = absent; **n/a** = not applicable. Evidence labels in parentheses refer to §0.2.

| Project | Orchestration (subagents/planning) | Native app tools (beyond browser) | Vision / computer-use | Durable memory | Eval harness | Human approval | Self-hostability | Fit for Craft apps on this VPS |
|---|---|---|---|---|---|---|---|---|
| **DeerFlow 2.2.x** | **strong** — `task`/`batch_task` subagents, isolated/snapshot context, goals, LangGraph planning (`E2`) | **partial** — filesystem + shell + sandbox + arbitrary MCP servers; no creative-app tools (`E2`) | **none** — no computer-use; DeepSeek V4 example sets `supports_vision: false` (`E2`) | **strong** — DeerMem facts+summaries, FTS5 index, write gate, mem0/OpenViking options (`E2`) | **partial** — traces (`monocle`), token dashboard, sandbox benchmarks; no task-quality promotion loop (`E2`) | **partial** — `interrupt_before/after`, resume, rollback; no approval queue documented (`E2`) | **strong** — MIT, Docker Compose, loopback default, already deployed per `task-1` (`E1`,`E2`) | **4/5** — best substrate; needs Craft MCP registration + verification/eval layer |
| **Harness²** (`google-research/harness2`) | **strong** (design) — subagents component + OpenCode/Codex executors (`E2`) | **none** — benchmark harness (`E2`) | **none** — text/code benchmarks (`E2`) | **strong** (design) — memory component + persistent improvement library/`EXPERIENCE.md` (`E2`) | **strong** — JobBench/LAB/WorkBuddy drivers, judge, report (`E2`) | **none** (`E2`) | **partial** — Linux+uv OK; model-backed runs need Vertex/Codex (`E2`) | **3/5** — blueprint to copy, not a runtime |
| **Hermes Agent** | **strong** — isolated subagents, provider/model routing (`E2`) | **partial** — terminal + browser + computer-use MCP servers (`E2` link) | **partial** — web search/browser/vision features claimed (`E3`) | **strong** — persistent memory, FTS5 recall, Honcho, auto-skills (`E2`,`E3`) | **partial** — `evals/` dir + batch trajectories; no promotion gate verified (`E2`,`UNVERIFIED`) | **partial** — Desktop approvals/settings; not verified for VPS (`UNVERIFIED`) | **strong** — MIT, Docker, `$5 VPS` claim (`E2`) | **3/5** — viable alternative substrate; heavy for 2 vCPU/8 GB |
| **browser-use** | **none** — single agent loop (`E2`) | **none** — browser only (`E2`) | **partial** — screenshots + DOM; no desktop (`E2`) | **none** — run history only (`E2`) | **partial** — BU Bench v2 (`E2`) | **none** (`E2`) | **strong** — MIT library; cloud optional (`E1`,`E2`) | **2/5** — browser surface only |
| **Agent-S** | **none** — one CUA (S2 compositional internally) (`E2`) | **strong** — real desktop GUI (`E2`) | **strong** — OSWorld SOTA (`E2`) | **partial** — topic/paper claim, not verified in code (`E1`,`UNVERIFIED`) | **strong** — OSWorld/ScienceBoard (`E2`) | **none** (`E2`) | **partial** — needs display; desktop deps (`E2`) | **2/5** — infeasible headless on this VPS |
| **UI-TARS-desktop** | **none** — single TARS agent (`E2`) | **strong** — desktop operators (`E2`) | **strong** — UI-TARS VLM (`E2`) | **none** (`E2`) | **none** (`E2`) | **none** (`UNVERIFIED`) | **partial** — Node/Electron; remote operators (`E2`) | **2/5** — GUI-first; no headless path |
| **OpenAdapt** | **none** — no planner (`E2`) | **strong** — any GUI app + API step (`E2`) | **partial** — recording/OCR, no VLM required (`E2`) | **strong** (procedural) — compiled programs, receipts, scoreboards (`E2`) | **strong** — fault-injection + read-back verification (`E2`) | **strong** — approval gate, stop-before-save (`E2`) | **strong** — MIT, local-first (`E1`,`E2`) | **3/5** — copy the verification/approval pattern; not a base |
| **playwright-mcp** | **none** (`E2`) | **none** — browser only (`E2`) | **none** — a11y tree, no vision (`E2`) | **none** (`E2`) | **none** (`E2`) | **partial** — per-tool read-only hints (`E2`) | **strong** — Apache-2.0, npx/Docker (`E1`,`E2`) | **2/5** — only if a Craft surface is web |
| **Eko 4.1.x** | **strong** — chain/plan/replan, parallel agents, A2A (`E2`) | **partial** — browser + file agents, Node system access (`E2`) | **partial** — browser automation; desktop via extension (`E2`) | **none** — conversation memory only (`E2`) | **none** (`E2`) | **strong** — `HumanInteractTool` (`E2`) | **strong** — MIT, npm/Node (`E1`,`E2`) | **1/5** — dormant since 2026-03-03, no eval/memory, JS-only |

**Reading the matrix:** no candidate scores strong on both *orchestration+memory* and *native creative-app tools+verification*. That split is the actual build case: orchestration exists to be integrated; Craft-native tooling and verification must be built.

---

## 5. Build vs integrate

### 5.1 Decision

**Integrate DeerFlow 2.2.x as the agent runtime; build the Craft control plane around it.** Do not build a new orchestration engine, and do not adopt a GUI/browser agent as the base.

Rationale (all `INFERRED` from §2–§4 plus the sibling `task-1` audit, which is clearly attributed):
- DeerFlow is MIT, already runs on the VPS, already has a working DeepSeek adapter, and already provides the four primitives hardest to rebuild: LangGraph runtime + checkpoints, durable subagents, durable memory with write gates, and pluggable sandbox/MCP. It is the only candidate that is simultaneously self-hostable, actively developed, permissively licensed, and Python-native.
- The Craft CLIs expose **headless MCP stdio servers** (per `task-1`), which is exactly DeerFlow's extension mechanism — so the tool layer can be registered rather than reimplemented.
- No candidate has Craft-specific verification, eval/promotion, or an episode ledger. Those are the "unique" parts and must be built.

### 5.2 Ranked recommendation

| Rank | Action | Why | Effort | Risk |
|---|---|---|---|---|
| **1** | **Integrate DeerFlow 2.2.x** (pin to a tag/commit; today's tag v2.2.0) as the hosted runtime; register `vectorcraft-cli mcp` and `photocraft-cli mcp` as MCP servers; add Craft skills | MIT, DeepSeek adapter, subagents, DeerMem, MCP, already deployed; highest capability per integration hour | M | Version drift (2.3.0-dev moving daily); container/host path isolation for Craft binaries (`task-1` gap `GAP-PATH`); 2 vCPU/8 GB headroom |
| **2** | **Build "Forge Conductor" control plane** on top: episode ledger, artifact/hash lineage, verification gates, skill library, eval/promotion, rollback, token/cost ledger | Nothing on the market does this for Craft; it is the product's uniqueness | L | Scope creep; must stay additive to DeerFlow, not a fork |
| **3** | **Adopt Harness²'s design, not its code**: the eight editable components + Propose–Probe–Compose + `EXPERIENCE.md` improvement harness, adapted so "probe" runs Craft commands on disposable copies and "compose" promotes only if verification passes | Apache-2.0 blueprint with a published method and results; lets the harness improve without weight training | M | Its executors/benchmarks are OpenCode/Codex + Vertex; only the method transfers |
| **4** | **Copy OpenAdapt's verification discipline**: verify by reading back the artifact/system of record (file diff, project JSON, render hash), never by trusting a CLI "OK"; keep a stop-before-final-save repair path with human approval | Its fault-injection evidence (54/72 vs 0/72) shows screen/exit-code success is not proof | S–M | Craft has no "REST read-back" for every artifact; needs per-tool verifiers |
| **5** | **Use Hermes Agent only if the requirement shifts** to a personal always-on agent with a built-in learning loop, and only on a larger host | MIT, huge, memory+skills+subagents, `$5 VPS`; but duplicates DeerFlow and would not fit the current 2 vCPU/8 GB alongside the existing stack | L | Resource pressure; two gateways; redundant memory systems |
| **6** | **Optional browser tier**: `playwright-mcp` (deterministic, read-only hints) if a Craft surface or publishing flow becomes web-based; `browser-use` only for web research tasks that a skill needs | Both are strong at their niche; neither is an orchestrator | S | Tool sprawl; separate process to supervise |
| **7** | **GUI/vision fallback — defer**: Agent-S / UI-TARS-desktop only if a Craft operation has no CLI/MCP equivalent, and only with a virtual display on a bigger host | All three need a live GUI; this VPS has no display/GPU per `task-1` | XL | High OOM/brittleness risk; not a near-term path |

### 5.3 "Do not use" list (with the concrete reason)

| Do not use | Reason (verified) |
|---|---|
| **Meta `facebookresearch/HyperAgents`** as a dependency | **CC BY-NC-SA 4.0 — non-commercial, share-alike**; research code that executes model-generated code (`E1`,`E2`) |
| **`hyperbrowserai/HyperAgent`** in a closed VPS service | **AGPL-3.0** — network use triggers source-disclosure obligations; last push 2026-05-11 (`E1`,`E2` LICENSE) |
| **hyperagent.com** as a component | Closed hosted product; no source, cannot self-host, no on-prem story (`E3`) |
| **Eko** as the new base | Last commit 2026-03-03; package 4.1.3 vs release tag 4.1.0; no durable memory/eval/learning; JS-only (`E1`,`E2`) |
| **`deepseek-ai/dsh-superagent-prototype`** in production | Its own README: "Research prototype for reference only, **not an official DeepSeek product**… not production-ready software" (`E2`) |
| **Harness²** as a production runtime | It is a benchmark/experiment harness (Vertex AI + OpenCode/Codex, Linux, `uv`), "not an officially supported Google product"; no service, memory store, or approval API (`E2`) |
| **browser-use / Agent-S / UI-TARS** as the Craft execution base | Browser-only or GUI-only; no orchestration/memory/approval; GUI ones need a display this VPS lacks (`E2`, `task-1`) |
| **Unlicensed artifacts** (`alex-hyperagent/hyperagent-public-skills`, `stanford-iris-lab/meta-harness-tbench2-artifact`) | No license file found (`E1`); no default reuse rights |
| **Any "metas hyperagent" / "Hermes hyperagent" repo claimed as official** | `NOT FOUND` — see §3.3–3.4; naming them as products would be fabrication |

### 5.4 Integration sketch (for `task-4`, not a spec)

```
VPS 179.197.88.181 (2 vCPU / 7.9 GB — small)
├─ DeerFlow 2.2.x (already running, container deer-flow-gateway)
│   ├─ Gateway + LangGraph runtime + checkpoints
│   ├─ Subagents: supervisor (lead) → craft-runner / verifier / publisher
│   ├─ DeerMem: user + project facts, facts per agent, FTS5 recall
│   └─ MCP registry (extensions_config.json + config.yaml)
│        ├─ vectorcraft mcp (stdio, headless)
│        └─ photocraft mcp (stdio, --bridge)
├─ Forge Conductor (build; additive service, not a DeerFlow fork)
│   ├─ episode ledger (Postgres): episode → steps → artifact hashes → verdicts
│   ├─ verification gates: parse/validate project file, re-render hash, command exit + artifact diff
│   ├─ skill library + promotion (Propose–Probe–Compose adapted; EXPERIENCE.md analog)
│   ├─ rollback: artifact snapshots + DeerFlow thread checkpoint
│   └─ cost/usage ledger + approval queue for destructive steps
└─ Existing pipeline/console (unchanged; Conductor calls the same MCP surface)
```

**Hard constraints to design around** (from `task-1`, attributed, not re-verified here): 2 vCPU/7.9 GB with swap already in use; no display/GPU; Craft binaries live on the host while DeerFlow's gateway is containerized (needs a bind mount or a host-side MCP bridge); unauthenticated MCP currently bound on `0.0.0.0:8765`; no durable Craft-run state model yet.

---

## 6. Fifteen candidate questions (for the next wave / 200-question corpus)

Answered-by-whom tags: **USR** = only the user can answer; **SRC** = needs a primary-source fetch; **VPS** = needs the host; **DES** = design decision.

1. **USR** — When you wrote "Harness 2", did you mean Google's `google-research/harness2` (Harness², arXiv 2610.14224), or "the second version of our harness"? (Both are plausible; only the first has a primary source.)
2. **USR** — "metas hyperagent": Meta's `facebookresearch/HyperAgents` (CC BY-NC-SA), the Stanford "Meta-Harness" Terminal-Bench artifact, or something you saw elsewhere?
3. **USR** — "Hermes hyperagent": Hermes Agent (Nous, MIT, 260k stars) or Hyperagent (hyperagent.com, closed) — or was it "Hermes" the model family?
4. **USR** — "superagent": DeerFlow's category name, DeepSeek's `dsh-superagent-prototype`, or a different product?
5. **SRC** — DeerFlow: pin **v2.2.0** or track `main` (2.3.0-dev)? What breaks for us between the two? (Check CHANGELOG entries for memory/sandbox/MCP changes.)
6. **SRC** — DeerFlow: does `DeerMem` support a Postgres/retrieval backend that can share the pipeline's Postgres, or is Markdown+SQLite FTS5 the only durable path? (`config.example.yaml` memory backend section.)
7. **DES** — Are Craft operations exposed as **MCP tools**, **CLI commands run through a shell tool**, or **both**? The choice decides whether the supervisor needs a shell or an MCP-only tool policy.
8. **VPS** — Can the DeerFlow gateway container see `/opt/craft/**` today (bind mount), or must Craft MCP run host-side behind the existing stdio↔HTTP bridge?
9. **VPS** — What is the measured memory headroom after adding one concurrent DeerFlow run on 2 vCPU/7.9 GB (swap already used)? Is a second run safe?
10. **DES** — What is the artifact-of-record per Craft app (project file? rendered PNG? PDF?) and how do we read it back for verification, in the OpenAdapt sense?
11. **DES** — Which destructive Craft operations require a human approval, and where does that approval live (DeerFlow interrupt, web panel, CLI prompt)?
12. **DES** — What does "promotion" mean for a Craft skill: eval score threshold, N successful episodes, or human sign-off? Who can promote?
13. **SRC** — Eko: is there an actively maintained fork or a v5 announcement after 2026-03-03? If not, Eko should be treated as reference-only.
14. **SRC** — Hermes Agent: is there a first-party production deployment guide for a 2 vCPU/8 GB VPS with a non-Nous model (DeepSeek API), and what is its measured idle RSS?
15. **DES** — License policy: are AGPL (HyperAgent) and CC BY-NC-SA (Meta HyperAgents) acceptable anywhere in our stack, even as dev-time tooling? If not, the "do not use" list in §5.3 is permanent.

---

## 7. Bibliography (every URL below was fetched on 2026-11-05)

### 7.1 Repository records and release data (GitHub REST API, `E1`)

| URL | Used for |
|---|---|
| https://api.github.com/repos/FellouAI/eko | Eko metadata |
| https://api.github.com/repos/FellouAI/eko/releases | Eko release tags |
| https://api.github.com/repos/FellouAI/eko/tags | Eko tags |
| https://api.github.com/repos/FellouAI/eko/commits | Eko last commit |
| https://api.github.com/repos/FellouAI/eko/contents/ | Eko root tree |
| https://api.github.com/repos/bytedance/deer-flow | DeerFlow metadata |
| https://api.github.com/repos/bytedance/deer-flow/releases | DeerFlow releases |
| https://api.github.com/repos/bytedance/deer-flow/tags | DeerFlow tags |
| https://api.github.com/repos/bytedance/deer-flow/commits | DeerFlow last commit |
| https://api.github.com/repos/browser-use/browser-use | browser-use metadata |
| https://api.github.com/repos/browser-use/browser-use/releases | browser-use releases |
| https://api.github.com/repos/simular-ai/Agent-S | Agent-S metadata |
| https://api.github.com/repos/simular-ai/Agent-S/releases | Agent-S releases |
| https://api.github.com/repos/bytedance/UI-TARS-desktop | UI-TARS metadata |
| https://api.github.com/repos/bytedance/UI-TARS-desktop/releases | UI-TARS releases |
| https://api.github.com/repos/OpenAdaptAI/OpenAdapt | OpenAdapt metadata |
| https://api.github.com/repos/OpenAdaptAI/OpenAdapt/releases | OpenAdapt releases |
| https://api.github.com/repos/microsoft/playwright-mcp | playwright-mcp metadata |
| https://api.github.com/repos/microsoft/playwright-mcp/releases | playwright-mcp releases |
| https://api.github.com/repos/google-research/harness2 | Harness² metadata |
| https://api.github.com/repos/google-research/harness2/readme | Harness² README via API |
| https://api.github.com/repos/google-research/harness2/releases | no releases found (count 0) |
| https://api.github.com/repos/google-research/harness2/tags | no tags found (count 0) |
| https://api.github.com/repos/facebookresearch/HyperAgents | Meta HyperAgents metadata + README |
| https://api.github.com/repos/deepseek-ai/dsh-superagent-prototype | dsh-superagent metadata + README |
| https://api.github.com/repos/hyperbrowserai/HyperAgent | HyperAgent metadata + README |
| https://api.github.com/repos/hyperbrowserai/HyperAgent/license | AGPL-3.0 confirmation |
| https://api.github.com/repos/alex-hyperagent/hyperagent-public-skills | unlicensed skills repo metadata |
| https://api.github.com/repos/stanford-iris-lab/meta-harness-tbench2-artifact | Meta-Harness artifact metadata |
| https://api.github.com/repos/NousResearch/hermes-agent | Hermes metadata |
| https://api.github.com/repos/NousResearch/hermes-agent/readme | Hermes README via API |
| https://api.github.com/repos/NousResearch/hermes-agent/releases | Hermes releases |
| https://api.github.com/search/repositories?q=… | terminology discovery queries (harness 2, hyperagent, superagent, hermes-agent, hermes hyperagent, metas hyperagent) |
| https://api.github.com/rate_limit | rate-limit check |

### 7.2 Repository source files (`E2`)

| URL | Used for |
|---|---|
| https://raw.githubusercontent.com/FellouAI/eko/main/README.md | Eko features, news, licensing |
| https://raw.githubusercontent.com/FellouAI/eko/main/package.json | Eko version 4.1.3 |
| https://raw.githubusercontent.com/FellouAI/eko/main/packages/eko-core/package.json | Eko core deps/version |
| https://raw.githubusercontent.com/FellouAI/eko/main/packages/eko-core/src/memory/memory.ts | Eko memory implementation |
| https://raw.githubusercontent.com/FellouAI/eko/main/packages/eko-core/src/memory/snapshot.ts | task_snapshot tool |
| https://raw.githubusercontent.com/FellouAI/eko/main/packages/eko-core/src/agent/eko.ts | pause/resume/abort API |
| https://raw.githubusercontent.com/FellouAI/eko/main/packages/eko-core/src/tools/index.ts | HITL + MCP tool wrappers |
| https://raw.githubusercontent.com/bytedance/deer-flow/main/README.md | DeerFlow architecture, memory, subagents, sandbox, deployment |
| https://raw.githubusercontent.com/bytedance/deer-flow/main/backend/pyproject.toml | deer-flow 2.3.0-dev, LangGraph, Python ≥3.12 |
| https://raw.githubusercontent.com/bytedance/deer-flow/main/config.example.yaml | DeepSeek adapter examples, memory backends |
| https://raw.githubusercontent.com/bytedance/deer-flow/main/CHANGELOG.md | 2.3.0 milestone / 2.2.0 history |
| https://raw.githubusercontent.com/browser-use/browser-use/main/README.md | browser-use product paths, MCP, replay |
| https://raw.githubusercontent.com/browser-use/browser-use/main/pyproject.toml | browser-use 0.13.14 deps |
| https://raw.githubusercontent.com/browser-use/browser-use/main/server.json | browser-use MCP registry entry |
| https://raw.githubusercontent.com/simular-ai/Agent-S/main/README.md | Agent-S versions and results |
| https://raw.githubusercontent.com/simular-ai/Agent-S/main/setup.py | gui-agents 0.3.2, deps, entry point |
| https://raw.githubusercontent.com/simular-ai/Agent-S/main/agent_s4/README.md | Agent S4 evolution method |
| https://raw.githubusercontent.com/bytedance/UI-TARS-desktop/main/README.md | Agent TARS / UI-TARS Desktop features |
| https://raw.githubusercontent.com/bytedance/UI-TARS-desktop/main/package.json | monorepo/runtime |
| https://raw.githubusercontent.com/OpenAdaptAI/OpenAdapt/main/README.md | verified execution layer, modes, fault studies |
| https://raw.githubusercontent.com/OpenAdaptAI/OpenAdapt/main/CAPABILITIES.md | capability map |
| https://raw.githubusercontent.com/OpenAdaptAI/OpenAdapt/main/pyproject.toml | OpenAdapt 1.20.0, MIT, Python |
| https://raw.githubusercontent.com/microsoft/playwright-mcp/main/README.md | tool list, read-only hints, config |
| https://raw.githubusercontent.com/microsoft/playwright-mcp/main/package.json | 0.0.84, Node ≥18 |
| https://raw.githubusercontent.com/google-research/harness2/main/README.md | Harness² components, install, benchmarks |
| https://raw.githubusercontent.com/facebookresearch/HyperAgents/main/README.md | Meta HyperAgents setup and license badge |
| https://raw.githubusercontent.com/deepseek-ai/dsh-superagent-prototype/main/README.md | "research prototype… not an official DeepSeek product" |
| https://raw.githubusercontent.com/hyperbrowserai/HyperAgent/main/README.md | Hyperagent features |
| https://raw.githubusercontent.com/hyperbrowserai/HyperAgent/main/LICENSE | AGPL-3.0 text |
| https://raw.githubusercontent.com/NousResearch/hermes-agent/main/README.md | Hermes features, memory, learning loop |

### 7.3 Official papers / sites / registries (`E3`)

| URL | Used for |
|---|---|
| https://arxiv.org/abs/2610.14224 | Harness² paper abstract, submission date, CC-BY-4.0 |
| https://harness2.github.io/ | Harness² official site: two-level recursion, C1–C8 components, results table (incl. "Meta-Harness 76.4") |
| https://www.deepseek.com/en/harness/ | Official DeepSeek Harness description: open-source, Cordis plugin architecture, DeepSeek-V41-Flash surfaced in UI |
| https://hermes-agent.nousresearch.com/ | Official Hermes Agent site: features, install, cloud hosting plans |
| https://www.hyperagent.com/ | Official Hyperagent product (commercial, hosted fleet, memories/skills) |
| https://registry.npmjs.org/@eko-ai%2Feko | npm `dist-tags.latest = 4.1.3`, modified 2026-03-03 |

### 7.4 Secondary leads (`E4` — not used as proof)

| URL | Note |
|---|---|
| https://arize.com/blog/how-hermes-implements-open-source-agent-harness-architecture/ | Fetched 200 but body truncated by the fetcher; used only as a lead that "Hermes" is discussed as a harness. Not cited for any fact. |

---

## 8. Failed retrievals and unresolved items (honest list)

| Attempt | Result | Consequence |
|---|---|---|
| `https://eko.fellou.ai/docs/release/versions/` | Fetcher refused the cross-origin redirect to `https://fellou.ai` | Eko version history was taken from GitHub releases + npm registry instead (both fetched). The docs site is **not** cited. |
| First run of `https://api.github.com/search/repositories` | HTTP 403 (transient; the same call succeeded seconds later; `rate_limit` showed search 10/10) | Terminology discovery was re-run with delays; final counts above are from successful calls. |
| `https://api.github.com/repos/alex-hyperagent/hyperagent-public-skills/readme` | HTTP 404 — repo has no README | Repo recorded as "unlicensed, README absent"; not used. |
| Full-text fetch of the Arize Hermes article | HTTP 200 but body truncated | Excluded from evidence. |
| Official docs sites not fetched | `docs.openadapt.ai`, `hermes-agent.nousresearch.com/docs`, `docs.browser-use.com`, `agent-tars.com`, `playwright.dev` were **not** opened | No claim in this report depends on them; only repository files and the fetched pages above are cited. |
| DeerFlow README/CHANGELOG/config full read | Not attempted end-to-end (380 KB / 1 MB / 194 KB) | Selective reads only; stated in §0.3. Any section not quoted remains unread. |
| GitHub API authentication | No token was available; 60 core requests/hour | All needed calls completed; a few duplicate calls were needed after the transient 403. |
| "metas hyperagent" / "Hermes hyperagent" exact projects | `NOT FOUND` | Not invented; reported as unresolved user terminology (§3.3–3.4) with the closest primary sources named. |
| Agent-S durable memory in code | Not confirmed (repo topic + paper claim only) | Marked `UNVERIFIED` in §2.4 and the matrix. |
| DeerFlow first-class human-approval queue | Not found in README | Marked `partial` / `UNVERIFIED` in the matrix. |
| Craft feasibility (display, paths, RAM) | Taken from sibling `task-1`, not re-probed here | Attributed wherever used; `task-2` did not touch the VPS. |

---

## 9. Hand-off summary

- **Terminology is now decidable:** Harness² is a real Apache-2.0 Google research project; superagent and hyperagent are ambiguous and must always be qualified; "metas hyperagent" and "Hermes hyperagent" are **not** official projects and should be raised with the user (§6 Q1–Q4).
- **The integration base is DeerFlow 2.2.x** — MIT, DeepSeek-capable, already deployed, with the primitives a Craft harness needs.
- **The build surface is small and unique:** Craft MCP registration, artifact verification by read-back, episode ledger, skill promotion with rollback, cost and approval gates. That is where the product's defensibility lives.
- **The tempting wrong turns are now documented:** non-commercial Meta research code, AGPL HyperAgent, the dormant Eko, and the explicitly non-production DeepSeek prototype.
