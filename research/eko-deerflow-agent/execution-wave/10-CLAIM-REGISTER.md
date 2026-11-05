# Claim register — execution wave

**Scope:** decision-critical claims only. Labels: `VERIFIED` (executed/read this wave), `READ`,
`CORROBORATED`, `ESTIMATE`, `ASSUMPTION`, `HISTORICAL`, `UNVERIFIED`, `NOT DOCUMENTED`.

| # | Claim | Evidence | Status |
|---|---|---|---|
| 1 | VPS is 2 vCPU / ~7.9 GB / 36 GB free, no GPU | S1 §8; live probe | **VERIFIED** |
| 2 | DeerFlow 2.2.0 is running; model `deepseek-flash` displays “DeepSeek V4.1 Flash”, 1,048,576 ctx, 8,192 max output | S1 §4; `/opt/deer-flow/config.yaml` read; **no live call** | **VERIFIED (config)** |
| 3 | The DeepSeek key is valid | — | **UNVERIFIED**; zero-spend `/user/balance` + `/models` test proposed |
| 4 | `/opt/pod-pipeline/bin/*-cli` are stubs exiting 127 | S1 §1; direct `head`/run | **VERIFIED** |
| 5 | Only VectorCraft 0.21.1 + PhotoCraft 0.20.2 installed | S1 §10; S3 §2 | **VERIFIED** |
| 6 | Pipeline routes argv is invented and rejected | `routes.py:73–96`; S1 §1; S3 §3 | **VERIFIED** |
| 7 | README “live E2E trace/trim/effect exit 0” is current | `README.md:191–194`; DB empty, last run failed on stub | **HISTORICAL / UNREPRODUCIBLE** |
| 8 | Craft MCP works standalone but is not registered in DeerFlow | S3 §4; S1 §5 | **VERIFIED** |
| 9 | PhotoCraft MCP can interleave dependent calls | S3 §4.5 | **VERIFIED** |
| 10 | `craft_trace` writes artifact before gates; text gate vacuous at 0 boxes | `craft_trace.py:250,344`; S3 §5 | **READ + prior run** |
| 11 | `prep_print_art.ok` is hard-coded true and 2.5× is warning-only | `prep_print_art.py:356,339`; S3 §5 | **READ + prior run** |
| 12 | Global SSIM is insufficient for localized defects | S10 visual corpus: 7/15 global, 13/15 tile with 3/4 false alarms, region 11/15 with 0/4 | **VERIFIED (synthetic)** |
| 13 | 39 skills / 400 answers / 8 diagrams exist | repo + validation | **VERIFIED** |
| 14 | 3/3 successes give Wilson LB 0.4385, so N=3 + LB>0.60 cannot promote | task-11 simulation, 20k trials, 23 tests | **VERIFIED (simulation, assumed probabilities)** |
| 15 | “2 failures in last 20” false-demotes a 95% skill ~41% | task-11 | **VERIFIED (simulation)** |
| 16 | Human gate cuts gate-optimiser promotion 85.73% → 0.01% | task-11 | **VERIFIED (simulated strategy)** |
| 17 | `pod-mcp` is unauthenticated on 0.0.0.0:8765 | S1; S12 | **VERIFIED** |
| 18 | Off-host 8765/8091 closed from one workstation; 22 open | S12 | **VERIFIED (one vantage)** |
| 19 | DeepSeek can be validated with `/user/balance` + `/models`, no chat | S12 §3.4, official docs fetched | **VERIFIED (docs + inference on billing)** |
| 20 | The agent learns art direction | no episode ledger, no eval, no A/B | **NOT SUPPORTED** |
| 21 | The agent is better than a human designer | no blind study | **NOT SUPPORTED** |
| 22 | All Craft apps can be driven | Film/Design/Effect absent | **FALSE for current host** |
| 23 | Research/implementation seats did not modify production code | `git status`: 5 modified skill files + 12 new research/skill paths; no diff under `pod_pipeline/`, `deploy/`, `src/`, or `forge/` | **VERIFIED (no production code)** |

## Contradictions / resolutions

| Conflict | Resolution |
|---|---|
| README live E2E vs empty DB/stub failure | README claim is historical/unreproducible; current state verified by DB count + run log. Do not repeat the claim. |
| MCP protocol `2024-11-05` vs `2025-06-18` | Craft MCP server echoes the requested version; both observed. Record the requested version, not a hard-coded server version. |
| “39 skills current” vs runtime missing before install | After force install: DSH/Hermes 39 current; verify at use time. |
| `04` promotion rule N≥3 vs simulation | Simulation wins; rule corrected in `ERRATA.md` and `agent-learning-loop`; new horizon policy is a simulation suggestion, not adopted. |
| README says five craft CLIs; only two real | Scope is VC/PC until others are installed/catalogued; named refusal for absent apps. |

## Gaps (what would close them)

- Live key test via zero-spend metadata endpoints (owner-approved).
- Stdio MCP registration proof in the DeerFlow gateway.
- Film/Design/Effect binaries + catalogues.
- Real 10/50-golden run with gate/human outcomes.
- Human inter-rater agreement and real regression rates.
- Cost per accepted artifact.
- Written EULA/checksums for vendor binaries; LICENSE/NOTICE/SBOM for repo.

## Independent verification (fresh seat, task-16)

| Check | Result |
|---|---|
| Adapter `node --test "test/*.test.mjs"` | `tests 30 pass 30 fail 0`, exit 0 |
| Promotion `unittest` + `simulate.py` | `Ran 23 tests … OK`; results hash identical to committed `04-PROMOTION.json`; deterministic |
| Visual fixtures | 26/26 hashes, 19/19 table rows, R1 7/15·1/4, R3 13/15·3/4, R8 12/15·0/4, composite 15/15·0/4 |
| Skills / answers | 39/39 pass; DSH/Hermes 39 current; 62 files 0 unknown; 400 answers |
| Production diff | no diff under `pod_pipeline/`, `deploy/`, `src/`, `forge/` |
| VPS claims | **UNVERIFIED independently** — SSH denied `Permission denied (publickey,password)`; local `routes.py`/craft-bin stubs verified READ |

Verifier contradictions: X1 fixture manifest BOM (**fixed after verification**, UTF-8 no BOM); X2 claim 23 wording
(**fixed**); X3 stale task-8 status (**fixed**); X4 package superseded note (historical, expected); X5/X6
minor line-citation/“region 11/15” ambiguity (read the visual evidence files directly; not policy).
