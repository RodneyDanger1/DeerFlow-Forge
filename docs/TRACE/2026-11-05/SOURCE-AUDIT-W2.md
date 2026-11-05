# SOURCE-AUDIT-W2 — frozen-question execution (primary fetch pass)

**Task:** `task-32` (claimed rev 2) · **Date:** 2026-11-05 (`America/Chicago`) · **Source of questions:** `docs/TRACE/2026-11-05/SOURCE-AUDIT.md` §1 (Q1–Q10, frozen).
**Mode:** READ-ONLY. No code, doc, README, config, commit or production access. Only this file was written.
**Hard-stop disclosure:** a 2-minute stop landed after **5 primary fetches**. Nothing below is inferred from memory; every fact carries its URL and fetch date. **10 of the 15 corpus repo URLs were NOT fetched** — those questions stay `UNVERIFIED`. No page was blocked (no 4xx/5xx); the gap is time, not access.

---

## 1. Fetch log (all HTTP 200, fetched 2026-11-05)

| # | URL | Status | Payload used |
|---|---|---|---|
| F1 | `https://api.github.com/repos/FellouAI/eko` | 200 | licence, language, stars/forks, created/pushed |
| F2 | `https://api.github.com/repos/bytedance/deer-flow` | 200 | same + description/topics/homepage |
| F3 | `https://api.github.com/repos/browser-use/browser-use` | 200 | same |
| F4 | `https://api.github.com/repos/simular-ai/Agent-S` | 200 | same |
| F5 | `https://api.github.com/repos/NousResearch/hermes-agent` | 200 | same |

All five are GitHub's own API — **primary** for repository metadata (source hierarchy tier 1–2). JSON treated as untrusted data; only descriptive fields recorded.

---

## 2. Verified facts (`VERIFIED` = fetched and read this pass)

| Fact | Value | Source | Fetch date |
|---|---|---|---|
| `FellouAI/eko` exists, public, not archived, default `main` | id 892974698 | F1 | 2026-11-05 |
| Eko licence | **MIT** (`spdx_id: MIT`) | F1 | 2026-11-05 |
| Eko primary language | **TypeScript** (`language: TypeScript`) | F1 | 2026-11-05 |
| Eko stars / forks / watchers | **4 960 / 447 / 4 960** (subscribers 99, open issues 15) | F1 | 2026-11-05 |
| Eko created / last push | created **2024-11-23T07:32:24Z**; **pushed_at 2026-03-03T10:22:49Z**; `updated_at` 2026-11-02T16:17:49Z | F1 | 2026-11-05 |
| Eko self-description / homepage | "Eko (Eko Keeps Operating) — Build Production-ready Agentic Workflow with Natural Language — eko.fellou.ai"; homepage **https://fellou.ai/eko** | F1 | 2026-11-05 |
| `bytedance/deer-flow` exists, public, `main` | id 979115477 | F2 | 2026-11-05 |
| DeerFlow licence / language | **MIT** / **Python** | F2 | 2026-11-05 |
| DeerFlow stars / forks | **85 029 / 11 949** (open issues 1 050, topics include `superagent`, `harness`, `langgraph`, `mcp`-adjacent `multi-agent`) | F2 | 2026-11-05 |
| DeerFlow created / last push | **2025-05-07T02:50:19Z** / **2026-11-05T13:40:33Z** (same day as audit) | F2 | 2026-11-05 |
| DeerFlow self-description | "An open-source long-horizon **SuperAgent harness** that researches, codes, and creates…" homepage `https://deerflow.tech` | F2 | 2026-11-05 |
| `browser-use/browser-use` | MIT / Python; **120 132 stars**, 13 403 forks; pushed **2026-11-05T22:25:47Z**; homepage `https://browser-use.com` | F3 | 2026-11-05 |
| `simular-ai/Agent-S` | **Apache-2.0** / Python; **12 886 stars**, 1 504 forks; pushed **2026-10-30T20:56:06Z**; homepage `https://www.simular.ai` | F4 | 2026-11-05 |
| `NousResearch/hermes-agent` | **MIT** / Python; **260 856 stars**, 57 596 forks; created **2025-07-22**; pushed **2026-11-05T22:25:50Z**; homepage `https://hermes-agent.nousresearch.com`; description "The agent that grows with you" | F5 | 2026-11-05 |

Snapshot instant: the five payloads carry `updated_at` between **2026-11-05T21:28Z and 2026-11-05T22:26Z**. Any star/fork figure quoted from this pass is **as of that instant** and decays daily.

---

## 3. Corrections and conflicts (evidence-based, nothing guessed)

| C# | Corpus formulation | Primary finding | Label |
|---|---|---|---|
| X1 | "Eko (FellouAI) is a real **MIT JavaScript** agent framework" | MIT **VERIFIED**; but the API's `language` field is **TypeScript**, not JavaScript. The project is a TS SDK over a JS runtime; the "JavaScript" descriptor is unsupported by the metadata I fetched. | CORRECTION (descriptor), repo existence VERIFIED |
| X2 | Eko presented as a **current/active** framework | `pushed_at` **2026-03-03**, **247 days before** the audit date; `updated_at` (2026-11-02) reflects stars/visibility, not code. Under the freshness rule this source is **STALE** for "current"; "active development in 2026 H2" is **contradicted**. | CORRECTION (currency) / STALE |
| X3 | "Harness 2 / superagent harness" as an ambiguous term | DeerFlow's own repository description uses the exact phrase **"SuperAgent harness"** (F2). This is primary evidence that *one* project self-describes with that term; it does **not** establish a product called "Harness 2". | CORROBORATED (term), NOT DOCUMENTED ("Harness 2") |
| X4 | "Hermes hyperagent" | A repo `NousResearch/hermes-agent` **does exist** (MIT, Python, 260 856 stars) — the *named project* is real. Its description is "The agent that grows with you" and **does not use "hyperagent"**; `google-research/harness2` was **not fetched**. The compound phrase remains undecided. | CORROBORATED (repo), NOT DOCUMENTED (phrase) |
| X5 | Star/version figures anywhere in the corpus | Cannot be compared: the corpus's own numbers were not re-read this pass, and I will not "correct" numbers I did not see. Any corpus figure must be re-checked against the payloads above before use. | OPEN |

---

## 4. Frozen questions — status after this pass

| Q | Status | What the 5 fetches settled / what is still missing |
|---|---|---|
| Q1 repo exists/licence/version/last-push | **PARTIAL (5/15 repos)** | Existence, licence, language, last push: settled for eko, deer-flow, browser-use, Agent-S, hermes-agent. **Versions/releases and the other 10 repos: `UNVERIFIED`** (never fetched). |
| Q2 headline currency | **PARTIAL (5/7)** | Eko **STALE** (247 d); deer-flow, browser-use, hermes-agent **FRESH** (same-day push); Agent-S **FRESH** (6 d). UI-TARS-desktop, OpenAdapt, playwright-mcp **`UNVERIFIED`**. |
| Q3 URLs resolve / serve attributed content | **PARTIAL (5/5 fetched = 200)** | Five API URLs resolve and serve repo metadata. The corpus's 150 other URLs (arxiv, blogs, docs) **`UNVERIFIED`**. |
| Q4 DeepSeek "V4.1 Flash / 1017" first-party | **`UNVERIFIED`** | No DeepSeek vendor page fetched. |
| Q5 Craft vendor sourcing | **`UNVERIFIED` / likely `NOT DOCUMENTED`** | No vendor site fetched; vendor-source existence cannot be asserted or denied. |
| Q6 "Harness 2 / superagent / metas hyperagent / Hermes hyperagent" | **PARTIAL** | "SuperAgent harness" verified as deer-flow's own description; `NousResearch/hermes-agent` exists; "Harness 2" and "metas hyperagent" **`NOT DOCUMENTED`** in what was fetched. |
| Q7 Time-sensitive claims with snapshot date | **SETTLED (method)** | Every figure above carries instant 2026-11-05T21:28–22:26Z. Corpus figures without such a stamp remain `RECHECK-DUE`. |
| Q8 Primary vs secondary citations | **PARTIAL** | All 5 fetches are primary. The corpus also stores a **secondary** citation (`arize.com/blog/how-hermes-implements-open-source-agent-harness-architecture`) — `NOT AUTHORITATIVE` under the declared hierarchy, and **unfetched**. |
| Q9 Internal numbers reproduce | **`UNVERIFIED`** | Promotion-sim numbers (ERRATA §) not recomputed. |
| Q10 Unfalsifiable claims | **`UNVERIFIED`** | Not enumerated in the timeboxed window. |

---

## 5. Freshness table (`/source-freshness-checker` statuses)

| Source | Type | Last push / read | Status |
|---|---|---|---|
| F2 deer-flow | official repo | 2026-11-05 | **FRESH** |
| F3 browser-use | official repo | 2026-11-05 | **FRESH** |
| F5 hermes-agent | official repo | 2026-11-05 | **FRESH** |
| F4 Agent-S | official repo | 2026-10-30 | **FRESH** (6 d) |
| F1 eko | official repo | 2026-03-03 | **STALE** (247 d) for "current"; still valid for identity/licence |
| 10 unfetched corpus repos | official repo | — | **UNKNOWN** |
| arxiv citations (21) | papers | — | **UNKNOWN** (not fetched) |

---

## 6. What remains `UNVERIFIED`, exactly

Not fetched for lack of time (not blocked — every attempted fetch returned 200): `bytedance/UI-TARS-desktop`, `OpenAdaptAI/OpenAdapt`, `microsoft/playwright-mcp`, `google-research/harness2`, `alex-hyperagent/hyperagent-public-skills`, `facebookresearch/HyperAgents`, `hyperbrowserai/HyperAgent`, `deepseek-ai/dsh-superagent-prototype`, `stanford-iris-lab/meta-harness-tbench2-artifact`, releases/tags endpoints for all five fetched repos, `https://api.github.com/rate_limit`, all 21 `arxiv.org/abs/*` pages, DeepSeek vendor docs, Craft vendor sources, `arize.com` blog.

**No invented citation appears in this document.** Every URL above was fetched at the stated status; every claim not backed by a 200 fetch is labelled `UNVERIFIED`/`NOT DOCUMENTED`/`OPEN`.

### Next-fetch order (same-day, cheapest first)
1. `/repos/{owner}/{repo}/releases/latest` + `/tags` for the five fetched repos (version claims).
2. The 10 remaining corpus repo URLs in the order the corpus cites them.
3. `api.github.com/rate_limit` before the batch (unauthenticated ~60/h; 5 used).
4. DeepSeek vendor model page, then Craft vendor sources, then arxiv spot-check of the 5 most-cited papers.
