# SOURCE AUDIT — Wave 1 (read-only research integrity)

**Task:** `task-25` (claimed rev 2) · **Seat:** source/research freshness · **Repo:** `DeerFlow Forge` · **Report date:** 2026-11-05 (`America/Chicago`)
**Skills applied:** `/deep-research` (evidence bar, claim labels, mandatory citation gate), `/source-freshness-checker` (type rule → FRESH / RECHECK-DUE / STALE / UNKNOWN).
**Mode:** READ-ONLY. No source, doc, README, config, commit, deploy or production object was modified. The only write is this file.
**Disclosure — fetches this pass: 0.** No `web_fetch`/`web_search` call was issued in this pass; a 3-minute timebox stopped the program after Step 1 (frame questions) and Step 2 (evidence bar). Every external claim below is therefore `UNVERIFIED` **by construction**, not by refutation. Nothing was invented to fill a gap.

---

## 1. Question list (written before research — frozen)

Each question names the evidence that would settle it. None were researched this pass.

| # | Question | Evidence that settles it |
|---|---|---|
| Q1 | Does every external repo named in the corpus exist at the claimed URL, under the claimed licence, at the claimed version, with a recorded last-push date? | GitHub API `repos/{owner}/{repo}` + `releases/latest` fetched on the audit date |
| Q2 | Are the corpus's headline claims about Eko (FellouAI), DeerFlow 2.x, browser-use, Agent-S, UI-TARS, OpenAdapt and Playwright MCP current as of 2026-11-05? | Each project's official README/release page fetched today; version + date quoted |
| Q3 | Do the corpus's cited URLs resolve (HTTP 200) and serve the content attributed to them? | Fetch each URL; record status code, final URL, date |
| Q4 | Is the model identity "DeepSeek V4.1 Flash / `deepseek-flash` / 1017" documented by a first-party (DeepSeek) source? | Vendor model catalogue / API docs page fetched today |
| Q5 | Are Craft app claims (VectorCraft 0.21.1, PhotoCraft 0.20.2, DesignCraft, EffectCraft, FilmCraft) backed by an identifiable vendor source, or only by local binaries/docs? | Vendor site or release artefacts; otherwise `NOT DOCUMENTED` externally |
| Q6 | Do "Harness 2", "superagent", "metas hyperagent", "Hermes hyperagent" correspond to any first-party project? | Vendor/registry search; absence → `NOT DOCUMENTED` |
| Q7 | Which claims are time-sensitive (stars, latest release, default branch, "current") and what is their snapshot date? | Each claim carries an explicit "as of" date; undated → `RECHECK-DUE`/`UNKNOWN` |
| Q8 | Which citations are primary vs secondary (aggregator/blog/AI page)? | Source type per `/source-freshness-checker`; secondary never used as authority |
| Q9 | Do the corpus's internal numbers (test counts, simulation probabilities, benchmark figures) reproduce from the artefacts they cite? | Re-run or re-read the cited artefact (`04-PROMOTION-SIM.md`, pytest logs) |
| Q10 | Which claims are unfalsifiable as written (no version, no date, no URL)? | Rewrite or downgrade to `NOT DOCUMENTED` |

---

## 2. Evidence bar declared (before searching)

- **Freshness rule:** "current" = fetched within 2026-11-03…2026-11-05 (2-day window); older = `HISTORICAL`; undated = `UNKNOWN`. Version pins (e.g. "0.21.1") are `STALE` when a newer release exists on the primary source.
- **Source hierarchy:** vendor/primary docs > official registry/API > named analyst > reputable journalism > blogs/aggregators (`NOT AUTHORITATIVE`) > AI-generated pages (`NOT DOCUMENTED`).
- **Labels:** `VERIFIED` (source fetched and read this pass) · `CORROBORATED` (≥2 independent in-workspace sources agree, or one workspace source confirmed by an independent probe) · `HISTORICAL` (true-when-written, not current) · `UNVERIFIED` (no primary source fetched) · `NOT DOCUMENTED` (no primary source appears to exist / claim is unfalsifiable).
- **Gate:** a claim is promotable only when a URL fetched on 2026-11-05 is quoted next to it. **Zero claims passed that gate this pass.**

---

## 3. What this pass actually accessed (in-workspace, read-only)

| Source | Access | Freshness |
|---|---|---|
| `research/eko-deerflow-agent/ERRATA.md` (44 lines, full read) | READ this pass | FRESH (read 2026-11-05) |
| `research/eko-deerflow-agent/` inventory (file list + sizes, 120 files) | LISTED this pass | FRESH |
| `research/eko-deerflow-agent/README.md` | **NOT read at current revision** — a 2 113-byte revision was read in an earlier session; the file is now 15 085 bytes | STALE (must re-read) |
| `research/eko-deerflow-agent/REPORT.md` (71 088 B), `wave2/02-AGENT-REPOS.md` (61 253 B), `wave2/08-200-QUESTIONS.md` (43 847 B), `execution-wave/10-CLAIM-REGISTER.md`, `docs/**` | **NOT read this pass** | UNKNOWN |
| Root `README.md` (8 877 B, 213 lines) | READ in an earlier session of today | RECHECK-DUE (verify it has not changed) |
| `wave2/01-STACK-VPS.md` / `01-VPS-FACTS.json` (own prior audit) | READ (authored by this seat) | FRESH (2026-11-05) |
| External network (any URL) | **0 fetches** | — |
| Production (`root@179.197.88.181`) | **not touched this pass** (per scope) | — |

---

## 4. Claim audit (labels applied to what can be evidenced)

| # | Claim (as written) | Where | Label | Freshness | Basis / what is missing |
|---|---|---|---|---|---|
| C1 | "Eko (FellouAI) is a real MIT JavaScript agent framework" | research README (earlier rev) | `UNVERIFIED` | UNKNOWN | No primary fetch. Eko's own docs host recorded as down: `eko.fellou.ai` / `fellou.ai/eko` returned **HTTP 503 on 2026-11-05** (`ERRATA.md:41-44`). Licence and language are unconfirmed here. |
| C2 | "Devain Eko is an unrelated prompt-only thinking companion; `eko-agent-github` is a third-party GitHub-discovery demo" | research README (earlier rev) | `UNVERIFIED` | UNKNOWN | Distinguishing claims about near-name projects **must** be fetched; name-collision claims are the highest-risk class and were not verified. |
| C3 | "Eko's memory is in-process context compression/snapshot, not durable learning" | research README / REPORT | `UNVERIFIED` | UNKNOWN | Requires reading Eko source/docs; none fetched. |
| C4 | "DeerFlow Forge is a console + deterministic Python pipeline with three MCP tools; it does not learn" | research README | `CORROBORATED` | FRESH | Three tools confirmed live (`tools/list` → `list_pending_assets`, `trigger_pipeline_job`, `get_fourthwall_status`) in `wave2/01-STACK-VPS.md` §5; no learning tables exist (5-table schema). |
| C5 | "Craft apps are independent Rust implementations, not 1:1 Adobe copies; Adobe tutorials transfer concepts, not exact commands" | research README | `UNVERIFIED` | UNKNOWN | Locally: both installed CLIs are Rust ELF binaries and expose distinct command registries (918 / 965) — consistent, but "independent of Adobe" is a legal/origin claim needing vendor sources. |
| C6 | README live-E2E claim: trace/trim/effect exited 0, `apparel_final.png` written, product row `draft`, run `succeeded` | root `README.md:191-194` | `HISTORICAL` | STALE | Repo's own errata downgrades it to `HISTORICAL/UNREPRODUCIBLE` (`ERRATA.md:28-33`). Independently corroborated by this seat: `pod` DB 0 rows in all tables, `bin/*-cli` stubs exit 127, last run log = stub message. |
| C7 | "31 pipeline tests (27 pure, 4 integration); 207 JS tests (205 pass, 2 skipped)" | root `README.md:184-190` | `UNVERIFIED` | RECHECK-DUE | Suite deliberately not executed in either audit (writes caches / DROP-CREATEs DB). Only `lastfailed = {}` seen. Counts never reproduced. |
| C8 | Boot/service claims: console, `pod-mcp`, `pod-worker.timer`, `docker` enabled; Postgres and nginx `unless-stopped` | root `README.md:196-200` | `CORROBORATED` (partly) | FRESH | Units verified `enabled/active` in `wave2/01` §9. The "nginx" wording is **imprecise**: no `nginx` systemd unit exists; nginx runs as the `deer-flow-nginx` container. |
| C9 | "DeerFlow's `langchain_mcp_adapters` client loads the three Forge tools and successfully calls `list_pending_assets`" | root `README.md:195-197` | `CORROBORATED` | FRESH | Confirmed from inside the gateway container: `curl http://172.17.0.1:8765/health` 200 and `tools/list` returns 3 tools (`wave2/01` §9). The *agent-call* half is not re-proven (no live run). |
| C10 | Promotion-rule numbers: Wilson LB 0.4385 at 3/3; 3.51 % null promotions / 81.14 % retention at n=8,k≥7,p=0.90; 41.22 % false-demote for "2 of last 20"; alternatives 15.10 % / 6.88 % / 22.98 % | `ERRATA.md:3-26` (citing `execution-wave/04-PROMOTION-SIM.md`, 23 tests, 20 000 trials, seed 20261105) | `UNVERIFIED` (primary artefact not re-read); repo-scoped label `HISTORICAL/ASSUMED` | RECHECK-DUE | These are **simulation outputs, not measurements**. The repo itself says the probabilities are `ASSUMED`, not observed on Craft episodes. Arithmetic must be recomputed from `sim/simulate.py` before any number is reused externally. |
| C11 | "Error rate claims / benchmark figures" elsewhere in REPORT.md | `REPORT.md` | `NOT DOCUMENTED` (this pass) | UNKNOWN | Not read this pass; any undated or unlinked figure must be treated as `NOT DOCUMENTED` until quoted with its source. |
| C12 | Repo URL `https://github.com/RodneyDanger1/DeerFlow-Forge` is the deployment source | root `README.md:131-136` | `VERIFIED` (as configured) / `UNVERIFIED` (as remote state) | RECHECK-DUE | The URL string is in the repo and the VPS checkout's `origin` matches it (verified on host). Whether the remote is public/current was **not** fetched. |
| C13 | Model identity "DeepSeek V4.1 Flash` / `deepseek-flash` / 1017" | README, `config.yaml` (host), corpus | `UNVERIFIED` (externally) / `VERIFIED` (as configured) | RECHECK-DUE | Configuration is locally verified (`models[0].name: deepseek-flash`, `display_name: DeepSeek V4.1 Flash`). No first-party model-catalogue fetch → the market-facing name and the "1017" build tag are unconfirmed. |
| C14 | "Eko docs at `eko.fellou.ai` / `fellou.ai/eko`" | `ERRATA.md:43` | `HISTORICAL` (observation) | STALE (transient host failure) | Recorded HTTP 503 on 2026-11-05. A 503 is a transient/edge failure, not proof the docs do not exist — retry before concluding `NOT DOCUMENTED`. |
| C15 | "Harness 2 / superagent / metas hyperagent / Hermes hyperagent" | corpus (per task naming) | `NOT DOCUMENTED` (provisional) | UNKNOWN | No first-party source located or fetched; provisional until a registry/vendor search is run. |

---

## 5. URL inventory (every external URL visible in the material actually read this pass)

| URL | Appears in | Fetch status | Freshness |
|---|---|---|---|
| `eko.fellou.ai` | `ERRATA.md:43` | **HTTP 503 on 2026-11-05** (recorded, not re-tried) | STALE / transient |
| `fellou.ai/eko` | `ERRATA.md:43` | **HTTP 503 on 2026-11-05** (recorded, not re-tried) | STALE / transient |
| `https://github.com/RodneyDanger1/DeerFlow-Forge` | `README.md:131-136`; VPS `origin` | not fetched | UNKNOWN |
| `https://api.fourthwall.com` | `config/pipeline.env` value (host) | not fetched | UNKNOWN |
| `https://search.parallel.ai/mcp` | `extensions_config.json` (host, disabled entry) | not fetched | UNKNOWN |
| `https://nodejs.org/dist/index.json` | `deploy/vps/install-console.sh` | not fetched | UNKNOWN |

No other URL was read from the corpus this pass. **No URL in this table is cited here as support for a claim.**

---

## 6. Freshness summary (`/source-freshness-checker` status set)

| Status | Count | Sources |
|---|---|---|
| FRESH | 3 | `ERRATA.md`, `wave2/01-STACK-VPS.md`, `01-VPS-FACTS.json` (read 2026-11-05) |
| RECHECK-DUE | 5 | root `README.md` (earlier rev), test-count claims, model-name claim, repo remote state, `04-PROMOTION-SIM` numbers |
| STALE | 3 | research `README.md` (revision drift 2 113 → 15 085 B), README live-E2E claim, Eko docs hosts (503) |
| UNKNOWN | all external sources | 0 fetches this pass |

---

## 7. Verdict

**The corpus is externally unaudited.** Internal traceability is good — claims carry paths, errata are append-only and honest, and two of the README's operational claims were independently corroborated by the stack audit. But **zero external claims were verified in this pass**, and at least one high-risk class (near-name projects: Eko vs Devain Eko vs `eko-agent-github`; "Harness 2" vs "Hermes") is exactly where fabricated citations hide.

**No external claim from `research/eko-deerflow-agent/**` or `README.md` should be promoted into a deliverable until it carries a URL fetched on the audit date.** Treat C1–C3, C5, C11, C13 (external half), C14 and C15 as `UNVERIFIED`/`NOT DOCUMENTED`.

---

## 8. Recheck list (exact next actions, with due dates)

| Due | Action | Target |
|---|---|---|
| 2026-11-06 | Read the corpus bibliography first (`wave2/02-AGENT-REPOS.md`, `wave2/08-200-QUESTIONS.md`, `REPORT.md`) and extract every URL **as written**; freeze the corpus (byte size + mtime) before fetching | corpus |
| 2026-11-06 | Retry the two Eko hosts once; if still failing, record the status code and keep Eko claims `UNVERIFIED` (do not convert a 503 into "does not exist") | `eko.fellou.ai`, `fellou.ai/eko` |
| 2026-11-06 | Fetch the primary repo metadata (licence, latest release, last push) for each project named in Q1–Q2, quoting the API payload and date | per corpus bibliography |
| 2026-11-06 | Fetch a first-party DeepSeek model catalogue / API docs page for the model name and any "1017" tag | DeepSeek vendor docs |
| 2026-11-07 | Re-read the current `research/eko-deerflow-agent/README.md` (15 085 B) and re-label C1–C5 against what it now says | repo |
| 2026-11-07 | Recompute C10 from `execution-wave/sim/simulate.py` (seed 20261105) before any number leaves the repo | repo |
| 2026-11-12 | Re-run the pipeline suite and console suite to settle C7 (counts vs README) | repo (staging) |

---

## 9. Honest limits of this pass

- **0 external fetches**: a network outage, block, or my omission would look identical from inside this file. The `UNVERIFIED` labels are the truthful state either way; nothing was upgraded by assumption.
- **Timeboxed**: `/deep-research` steps 3–7 (researcher briefs, synthesis, independent verification pass, packaging) did not run. Steps 1–2 did, and are recorded above so the next pass does not restart from zero.
- **Not reviewed this pass**: `REPORT.md`, `wave2/02-AGENT-REPOS.md`, `wave2/08-200-QUESTIONS.md`, `execution-wave/10-CLAIM-REGISTER.md`, `docs/**`. Their citations are unaudited here by omission, not by clearance.
- **Rate-limit risk for the next pass**: unauthenticated GitHub API calls are capped (~60/hour); budget ~15 repo lookups and record the quota headers.
