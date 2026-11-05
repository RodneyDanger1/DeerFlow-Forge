# Execution Wave / 05 — Security, Dependency and Key Hardening Plan

**Task:** `task-12` (execution wave, WP-5). **Owner:** `agent-repos-scout`.
**Date:** 2026-11-05 (America/Chicago). **Inputs:** `wave2/01-STACK-VPS.md` (stack/VPS audit), `wave2/02-AGENT-REPOS.md` (repo verification), `wave2/05-HARNESS-CODE.md` (donor mechanisms), `execution-wave/00-WAVE-2-PLAN.md` (WP-5 + differential questions 8/9).
**Mutation policy:** **read-only. No production change was made.** Every hardening item below is a proposal with a change site, a rollback, and a test; the change window is executed later by the named owner.
**New work in this task (not a re-audit):** the DeepSeek zero-spend validation procedure was verified against the official API docs; donor and runtime licences were assembled into a NOTICE plan; an **off-host TCP reachability probe** was run from this workstation to resolve one item the stack audit left `UNVERIFIED`.

---

## 0. Evidence labels and scope boundaries

| Label | Meaning |
|---|---|
| `[V]` | Verified in this task (own command output, fetched official doc, or file read). |
| `[R]` | Read from an existing artifact: the VPS audit `01-STACK-VPS.md`, the repo verification `02-AGENT-REPOS.md`, the donor survey `05-HARNESS-CODE.md`, or a repo file at the cited path/line. |
| `[I]` | Inferred by this task from two or more verified observations; not directly observed. |
| `[U]` | Unverified — cannot be proven with the access used; stated as a residual gap. |

**Not done here:** no SSH session, no VPS service restarts, no config edits, no DeepSeek chat completion (would spend quota), no repo re-verification. VPS facts are `[R]` from `01-STACK-VPS.md`; if the host has changed since that audit, the preflight in §6 must be run before any change window.

---

## 1. Headline result — ten decisions in priority order

1. **Critical, cheapest first fix:** `pod-mcp` listens on `0.0.0.0:8765` **only because `pipeline.env` sets `POD_MCP_HOST=0.0.0.0`**. The code default is already `127.0.0.1` (`pod_pipeline/config.py:60,115`), and the HTTP server has **no authentication** (`pod_pipeline/mcp_server.py:301-415`). Rebinding is a one-value change with a restart; adding a bearer token is a small code change in the same file. `[R]` `[V]`
2. **New verified fact:** from this workstation, ports **8765 and 8091 are not reachable off-host** (TCP timeout), while **22 is open**. This closes the stack audit's "external reachability of 8765 `UNVERIFIED`" for this vantage point: the immediate internet exposure is currently *closed*, but one probe is not a guarantee for every network, and the internal blast radius (any docker-network peer, plus a compromised `pod` process) is unchanged. `[V]`
3. **The docker-group membership is the real root-equivalence risk:** `pod-mcp.service` runs `User=pod` with `SupplementaryGroups=docker` while `POD_USE_DOCKER=0`. If Docker is not needed by the pipeline (verified config says it is not), that supplementary group should be removed and systemd confinement added; otherwise any code path that can execute as `pod` is effectively host-root. `[R]`
4. **DeepSeek validation without spend is solved:** `GET https://api.deepseek.com/user/balance` and `GET https://api.deepseek.com/models` with `Authorization: Bearer $DEEPSEEK_API_KEY` return **200** for a valid key, **401** for an invalid/revoked key, **402** for a valid key with no balance — **without generating a single token**. A chat completion must never be used as a key test. `[V]` (docs) + `[I]` (no billing on metadata endpoints; see §4.3)
5. **Rotation is a 8-step, spend-free runbook** (§4.4): create key B → store root-only → restart gateway only → validate B against the metadata endpoints → revoke A → confirm A returns 401 → record fingerprint → re-run preflight. Never print or log the key; never put it in `ps`-visible argv (§4.2).
6. **DeerFlow must be pinned by tuple, not by tag:** deployed HEAD `58fc5bd`, backend `pyproject` `2.2.0`, compose project `deer-flow-dev`, two untracked files. Pin = commit SHA + image digests + `uv.lock` hash + compose/config/`extensions_config.json` hashes, recorded in a repo `deploy/pins.lock`. Do **not** follow `main` (`2.3.0-dev`, moving daily) or floating image tags (`postgres:16`, `redis:7-alpine`, `nginx:1.31.2-alpine`). `[R]`
7. **Licences are clean if donor choice stays as planned:** every adopted donor mechanism is MIT or Apache-2.0 (Goose, OpenHands, SWE-agent, Aider, Cline, Continue, Playwright MCP, DeerFlow). The non-permissive candidates from `02-AGENT-REPOS.md` remain excluded: HyperAgent (AGPL-3.0), Meta HyperAgents (CC BY-NC-SA 4.0), hyperagent.com (proprietary), unlicensed artifacts. `[R]`
8. **Two licence gaps need action:** the repo has **no `LICENSE` and no `NOTICE`** `[V]`, and the vendor Craft binaries have **no checksum manifest** and unknown EULA `[R]`, `[U]`. Ship `THIRD-PARTY-NOTICES.md` + generated SBOMs; record vendor version/hash/EULA before executing them as a service.
9. **Two image-licence questions must be resolved at pin time:** `redis:7-alpine` is a floating tag — Redis changed its licence terms in 2024 for versions ≥ 7.4 (RSALv2/SSPLv1) `[I — verify against the resolved image]`, and `postgres:16` resolves to 16.15 (PostgreSQL Licence) `[R]`. If the resolved Redis is ≥ 7.4 and policy forbids RSALv2/SSPL, switch to Valkey (BSD) or pin a 7.2 digest.
10. **Spend is not provider-limited at the key level:** DeepSeek's documented limits are account-level concurrency (2500 for `deepseek-flash`) and a balance (`402`), **not a per-key budget** `[U — no per-key limit documented]`. Budgets must therefore be enforced client-side (an episode cost ledger + `max_tokens`/wall-clock caps + `user_id` attribution, per the Wave 2 design). `[V]` `[R]`

---

## 2. Threat model (one page)

**Assets.** (a) Craft vendor binaries and the `/opt/craft` toolchain; (b) the `pod` Postgres DB and the DeerFlow state DB; (c) provider credentials in container env (`DEEPSEEK_API_KEY` plus Tavily/Exa/Serper/Jina/InfoQuest/Provisional/Sofya/Unbrowse/Serply keys) and the Fourthwall credentials; (d) the publish path (Fourthwall products); (e) model spend on the owner's DeepSeek account.

**Adversaries / accident sources.**
- A network peer that can reach an exposed port and call MCP tools that spawn host processes (`trigger_pipeline_job` → craft binaries as `pod`). `[R]`
- A compromised or malicious ArtCraft/vendor binary or an unverified binary substitution (no checksums today). `[R]`
- A compromised dependency pulled by a floating image tag or an unpinned `uv`/`npm` environment. `[R]` `[V]`
- A model-induced damaging action: a hallucinated or over-broad command that deletes/overwrites project files or publishes an unfinished product. `[R]`
- An operator accident: key pasted into a command line, log, or commit; wrong container restarted; wrong DB targeted.

**Blast radius today.** `pod` is in the `docker` group, so code-execution as `pod` is host-root-equivalent (mount the host FS, read every container env, including `DEEPSEEK_API_KEY`). `[R]` The MCP server is unauthenticated; the only boundary is `ufw` source ranges (`172.16.0.0/12`, `192.168.200.0/24`) `[R]`, corroborated for the internet by the off-host probe `[V]`.

**Design principle for this plan.** *Fail closed, least privilege, verify without spend.* No control here depends on trusting a README, an exit code, or a "saved" toast; each has an independent observable (TCP result, HTTP status, hash, `id`, licence scan, balance check).

---

## 3. Hardening plan (finding → change → rollback → test)

### 3.1 pod MCP: loopback bind + token authentication

**Current state `[R]` `[V]`**

| Fact | Evidence |
|---|---|
| Listens `0.0.0.0:8765`, `User=pod`, `SupplementaryGroups=docker` | `01-STACK-VPS.md` §9; `blueprint/files/deploy/systemd/pod-mcp.service` |
| No auth anywhere in the MCP server | `blueprint/files/pod_pipeline/mcp_server.py:301-415` (`handle_rpc`, `_client`, `serve_http`); no `Authorization`/token check |
| Code default is loopback; deployment overrides it | `pod_pipeline/config.py:60,115` (`mcp_host = "127.0.0.1"`); `01` §13 `POD_MCP_HOST=0.0.0.0` |
| Three tools exposed, one spawns workers | `mcp_server.py:281-291` dispatch; `01` §3/§26 (`trigger_pipeline_job`) |
| Internet reachability from one off-host vantage | **closed** — `[V]` probe 2026-11-05 (timeout on 8765/8091; 22 open) |
| In-network reachability | open to `172.16.0.0/12` and `192.168.200.0/24` via `ufw` `[R]` |

**Option A (minimum, no code): rebind to the docker bridge and keep it internal.**
Change `/opt/pod-pipeline/config/pipeline.env`: `POD_MCP_HOST=0.0.0.0` → `POD_MCP_HOST=172.17.0.1` (the address the DeerFlow gateway already uses: `01` §9 verifies `curl http://172.17.0.1:8765/health` from inside the gateway). Restart `pod-mcp.service`. This removes every non-docker interface while preserving the exact consumer path. Rollback: set the value back and restart. Test: `ss -lntp | grep 8765` shows `172.17.0.1:8765` only; the off-host probe still times out; the gateway health call still returns 200.

**Option B (recommended, small code change): bearer token in the MCP server.**
Add to `mcp_server.py`: read `POD_MCP_TOKEN` from the environment; in `_client` (or a wrapper around `_read_http`/`handle_rpc`) require `Authorization: Bearer <token>` with a constant-time compare (`hmac.compare_digest`); return HTTP **401** with a JSON-RPC error for missing/invalid tokens; log only `remote_addr`, method and allow/deny. Configure the consumer (`/opt/deer-flow/extensions_config.json` `mcpServers.forge`) to send a static header — **first verify DeerFlow's MCP client supports static headers** for HTTP servers (its MCP guide is `backend/docs/MCP_SERVER.md`; not fetched in this task `[U]`). If headers are not supported, keep Option A and reach the server through the existing host-side stdio bridge (`blueprint/files/deploy/mcp-stdio.mjs`) with the token injected in the bridge.
Rollback: token becomes optional when `POD_MCP_TOKEN` is unset (fail-open only for local dev); or revert the file and restart.
Test: unauthenticated `curl -s -o /dev/null -w '%{http_code}' -X POST http://127.0.0.1:8765/` → **401**; authenticated → **200/result**; `tools/list` still returns the 3 tools; gateway smoke call succeeds.

**Option C (defence in depth, later): socket activation / Unix domain socket** mounted into the gateway, or an authenticated reverse proxy on `172.17.0.1`. Do not expose `8765` on any public interface in any option.

**Priority: A today, B this week, C if a second consumer appears.**

### 3.2 Docker group → root equivalence

**Current state `[R]`:** `pod-mcp.service` has `User=pod`, `Group=pod`, **`SupplementaryGroups=docker`**, `NoNewPrivileges=true`, `Restart=on-failure`. `POD_USE_DOCKER=0` in `pipeline.env`. `[R]` `[V]`

**Change (staged):**
1. Confirm Docker is not needed: `grep -rn "docker" /opt/pod-pipeline/pod_pipeline/ | grep -v __pycache__` (expect only config/optional runner paths) `[R` partially checked by `01` §13 `POD_USE_DOCKER=0`]`.
2. Remove `SupplementaryGroups=docker` from the unit (repo `blueprint/files/deploy/systemd/pod-mcp.service` + host `/etc/systemd/system/pod-mcp.service`), `systemctl daemon-reload && systemctl restart pod-mcp`.
3. Add confinement: `ProtectSystem=strict`, `ProtectHome=true`, `PrivateTmp=true`, `ReadWritePaths=/opt/pod-pipeline/data /opt/pod-pipeline/build /opt/pod-pipeline/logs /opt/pod-pipeline/sandbox`, `RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX`, `MemoryMax=1500M`, `TasksMax=512`.
4. Verify both the negative and the positive: `su -s /bin/sh pod -c 'docker ps'` **fails**, and a pipeline craft step still runs.
Rollback: restore the previous unit file (keep a copy) and `daemon-reload`; the group can be re-added in one line if a verified Docker path emerges.
Test: `systemctl show pod-mcp -p SupplementaryGroups` empty; `docker ps` as `pod` → permission denied; one MCP-triggered run completes.

**If Docker is ever required again:** use rootless Docker or a socket proxy with an explicit allow-list, never the raw `docker` group.

### 3.3 Secret inventory and handling

**Current state `[R]` `[V]`:** `/opt/pod-pipeline/config/pipeline.env` is `0640 pod:pod` and holds `POD_DB_PASS`, `POD_CREDENTIAL_KEY`, `FW_API_USER`, `FW_API_SECRET`, `DATABASE_URL`; the DeerFlow gateway carries `DEEPSEEK_API_KEY` + 10 more provider keys + `DEER_FLOW_CREDENTIALS_KEY` + `DEER_FLOW_INTERNAL_AUTH_TOKEN` in container env; no vault; no rotation evidence. `pipeline.env` has **no** `DEEPSEEK*` names — the model key is gateway-only. `[R]` `[V]` (`.gitignore` excludes `.env*`; no secret-like file is tracked `[V]`).

**Change:**
1. Secret register (names + location + owner + rotation date + fingerprint hash — **never values**). Fingerprint: `printf %s "$VALUE" | sha256sum | cut -c1-12`.
2. Tighten file modes: `chmod 600` root-owned for gateway env file; `chmod 640 root:pod` for `pipeline.env` only if `pod` truly needs each value (prefer 600 + systemd `EnvironmentFile=-` read as root is not possible; systemd reads as root before dropping privileges, so **0600 root:root is compatible** with `EnvironmentFile` — verify on the host `[U]`).
3. Remove `pod` from the docker group (§3.2) — this is the single biggest reduction in who can read container env.
4. Add a leak scan to the preflight: count occurrences of key-shaped strings in journals and logs without printing them (§6 P9).
5. Provider keys that are not used by the Craft harness (Tavily/Exa/Serper/Jina/InfoQuest/Sofya/Unbrowse/Serply) should be scoped or removed from the gateway env; each is an independent credential with its own spend/abuse surface. Decide per key `[U]`.

### 3.4 DeepSeek key validation without spend — **differential question 8**

**Verdict `[V]`:** validate with **metadata endpoints only**. Never use `/chat/completions` as a key test.

**Official API facts (fetched 2026-11-05):**

| Fact | Source |
|---|---|
| Base URL `https://api.deepseek.com` (OpenAI-compatible); Anthropic base `https://api.deepseek.com/anthropic` | `api-docs.deepseek.com` (Your First API Call) |
| Auth header `Authorization: Bearer ${DEEPSEEK_API_KEY}` | same |
| Model `deepseek-flash` is served by **DeepSeek-V4.1-Flash-1017** (`deepseek-v4-flash*` legacy names retired) | same |
| `GET /models` returns the model list with context/output/modality metadata | `api-docs.deepseek.com/api/list-models` |
| `GET /user/balance` returns `is_available` and `balance_infos` | `api-docs.deepseek.com/api/get-user-balance` |
| Error semantics: **401** = authentication fails (wrong key), **402** = insufficient balance, **429** = rate limit, **500/503** = server | `api-docs.deepseek.com/quick_start/error_codes` |
| Account-level concurrency: `deepseek-flash` **2500**, `deepseek-v4-pro` **500**; `user_id` parameter gives content/KVCache/scheduling isolation | `api-docs.deepseek.com/quick_start/rate_limit` |

**Procedure (run inside the gateway container so the env is the real one):**

```bash
# 0. presence only — no value printed
docker exec deer-flow-gateway sh -lc 'test -n "$DEEPSEEK_API_KEY" && echo present || echo MISSING'

# 1. balance (auth + balance state, zero tokens generated)
docker exec deer-flow-gateway sh -lc '
  printf "header = \"Authorization: Bearer %s\"\n" "$DEEPSEEK_API_KEY" \
  | curl -K - -sS -o /dev/null -w "balance_http=%{http_code}\n" https://api.deepseek.com/user/balance'

# 2. model list (auth + egress + exact model ids available)
docker exec deer-flow-gateway sh -lc '
  printf "header = \"Authorization: Bearer %s\"\n" "$DEEPSEEK_API_KEY" \
  | curl -K - -sS -o /dev/null -w "models_http=%{http_code}\n" https://api.deepseek.com/models'
```

**Result matrix:**

| Observed | Meaning | Action |
|---|---|---|
| `balance_http=200`, `models_http=200` | Key valid, egress works, balance readable | Proceed; record `is_available` |
| `401` on either | Key invalid, revoked, or wrong environment | Rotate (§4.4); never retry with another value found on disk |
| `402` | Auth succeeded, account balance insufficient | Top up or reduce budget; key itself is valid |
| `429` | Rate/concurrency limit | Back off; unrelated to validity |
| `5xx` / timeout / DNS error | Provider or network, not the key | Re-test later; check egress |

The `curl -K -` form keeps the secret out of `ps`/argv (it is written to curl's config on stdin; `printf` is a shell builtin). `[V]` procedure + `[I]` zero-spend: the docs price chat tokens and the metadata endpoints generate no tokens, so no charge is expected — this is an inference from endpoint semantics, not an explicit billing statement, and is labelled as such.

**Forbidden as validation:** `POST /chat/completions` with a 1-token prompt. It spends the owner's balance, creates a billable event, and proves nothing that `/models` does not already prove.

### 3.5 Key rotation runbook (spend-free, reversible)

| # | Step | Command / action | Verify |
|---|---|---|---|
| 0 | Record current fingerprint, no value | `printf %s "$K" \| sha256sum \| cut -c1-12` inside container | 12-hex fingerprint stored in the secret register |
| 1 | Create key **B** in the DeepSeek platform (UI, `platform.deepseek.com/api_keys` — linked by the official error-codes page) | label `deerflow-vps-<purpose>` | B exists; do not paste it into chat/logs |
| 2 | Store B in a root-only file | `install -m 600 -o root -g root /dev/stdin /etc/deerflow/deepseek.env` | `stat -c '%a %U:%G'` → `600 root:root` |
| 3 | Point the gateway at B (compose `env_file`/drop-in), restart **only** the gateway container | `docker compose -p deer-flow-dev up -d --no-deps <gateway-service>` | container healthy |
| 4 | Validate B (§3.4) | both metadata endpoints | `200` |
| 5 | Revoke key **A** in the platform | UI | A listed as revoked |
| 6 | Confirm A is dead (if its value is still in a secure file) | metadata endpoint with A | `401` |
| 7 | Record new fingerprint + date + operator in the secret register | — | register updated |
| 8 | Re-run preflight P5/P6/P9 | — | all pass |
| 9 | Schedule next rotation (90 days or on incident) | calendar/runbook | — |

Rollback: key B can be revoked and A re-enabled in the platform; the container can be restarted onto the previous env file. Never leave two active keys indefinitely.

### 3.6 Spend and safety controls (client-side, because key-level budget is not documented)

- **Episode budgets** (from the Wave 2 design): `max_tokens`, `max_wall_s`, `max_attempts`, and a per-episode cost cap; refuse before the first model call when the budget is absent or exceeded. `[R]`
- **Attribution:** pass `user_id` on model calls (documented isolation parameter) so a leaked or runaway episode can be attributed/isolated. `[V]`
- **Concurrency cap:** the VPS has 2 vCPU/7.9 GB; cap the harness at 1–2 concurrent runs regardless of the account's 2500-concurrency allowance. `[R]` `[V]`
- **Balance monitor:** scheduled zero-spend `GET /user/balance`; alert when `is_available` is false; treat `402` as a fail-closed stop. `[V]`
- **Cost ledger:** persist per-call token usage (DeerFlow records provider usage in its dashboard `[R]`); reconcile against the balance delta. A missing usage field must surface as `UNVERIFIED`, not be estimated into the ledger.
- **No autonomous spend:** the harness may not create paid provider accounts, top up, or change models without an approval token. `[R]` (design)

### 3.7 DeerFlow version pin and supply chain

**Current state `[R]` `[V]`:** `/opt/deer-flow` at git `58fc5bd…`, `backend/pyproject.toml` version `2.2.0`, compose project `deer-flow-dev` from `docker/docker-compose-dev.yaml`, two untracked files (`_audit_prompt.txt`, `extensions_config.json.bak-before-forge-mcp`); repo release **v2.2.0 (2026-11-04)**, while main is **2.3.0-dev** and moves daily. `[R]` `[V]`

**Pin tuple (record in `deploy/pins.lock`, generated by a read-only script):**
1. `git -C /opt/deer-flow rev-parse HEAD` → `58fc5bd…` (and `git describe --tags --always` to relate it to `v2.2.0`).
2. Image digests for every container: `docker inspect --format '{{.Config.Image}} {{index .RepoDigests 0}}' <container>` for gateway, frontend, nginx, redis, postgres.
3. `sha256sum` of `docker/docker-compose-dev.yaml`, `config.yaml`, `extensions_config.json`, `backend/uv.lock`.
4. Python: `uv sync --locked` semantics — `uv.lock` pins `https://pypi.org/simple`; do **not** set a mirror index (`UV_INDEX_URL` must stay the default or the locked build fails). `[R]`
5. Node/frontend and nginx/redis/postgres images: pin by digest, not tag.
6. Vendor Craft binaries: version + SHA256 + vendor checksum/EULA (see §3.8).

**Rules:**
- No `docker compose pull` of floating tags in production; deploy by digest.
- No upgrade to `2.3.0-dev` until: changelog review of subagent/memory/sandbox/MCP changes `[R]`, a staging clone with the same compose, a golden-set evaluation, and a tested rollback.
- The untracked `extensions_config.json.bak-before-forge-mcp` is a config-drift smell: keep a versioned copy of the active file in the pin manifest, and resolve the untracked state during the change window.
- `deer-flow.dev` style local overrides must not be silently edited on the host; changes go through a documented compose override recorded in the repo.

### 3.8 Vendor Craft binaries (proprietary, unverified provenance)

**Current state `[R]`:** binaries owned by `UNKNOWN` uid 1001, world-executable, extracted from tarballs in `/opt/craft/pkg` (258 MB) with **no checksum manifest, no signature**; docs tree `/opt/craft/artcraft-docs/` (1 MB); only vectorcraft 0.21.1 and photocraft 0.20.2 installed.

**Change:**
1. Record `sha256sum` of every executable and the tarballs in `deploy/vendor-craft.lock` (read-only `sha256sum`).
2. Request the vendor's published checksums/signature and EULA; until received, mark provenance `[U]` and treat the binaries as trusted-by-possession only.
3. Create a dedicated service account or numeric uid for Craft execution; do not run them as `pod` (which currently has broader file access and, until §3.2, docker).
4. Keep `/opt/craft/pkg` tarballs for reproducibility (they are the only originals), with hashes.
5. No redistribution of the binaries or docs in any packaged corpus (licence unknown) — relevant to the task-14 packaging output.

### 3.9 Licence / NOTICE inventory — **differential question 9**

**Gap `[V]`:** the repo root has **no `LICENSE`, no `NOTICE`, no `THIRD-PARTY-NOTICES`**. `.gitignore` excludes `.env*` and no secret-like file is tracked `[V]`.

**Donor mechanisms to be adapted (licences `[R]` from `02-AGENT-REPOS.md` and `05-HARNESS-CODE.md` §1.1):**

| Mechanism (05-HARNESS-CODE) | Donor | Licence | Obligation |
|---|---|---|---|
| M1 ordered re-entrant operation pipeline | block/goose | Apache-2.0 | retain licence + NOTICE, state changes |
| M2 single-step contract / append-only trajectory | SWE-agent/SWE-agent | MIT | retain copyright + permission notice |
| M3 repair-on-format vs abort-on-environment | SWE-agent + Aider-AI/aider | MIT + Apache-2.0 | both notices |
| M4 declarative tool records | SWE-agent + continuedev/continue | MIT + Apache-2.0 | both notices |
| M5 one tool namespace across transports | continuedev/continue + All-Hands-AI/OpenHands | Apache-2.0 + MIT | both notices |
| M6 capability-gated tool exposure | microsoft/playwright-mcp | Apache-2.0 | retain licence + NOTICE |
| M7 composable condenser pipeline | All-Hands-AI/OpenHands (0.60) | MIT | retain notice |
| M8 continuation-note compaction | cline/cline | Apache-2.0 | retain licence + NOTICE |
| M9 token-budget compaction | block/goose + cline/cline | Apache-2.0 | retain licences |
| M10 assertions as first-class tools | microsoft/playwright-mcp | Apache-2.0 | retain licence |
| M11 decidable acceptance + explicit UNVERIFIED | bytedance/deer-flow | MIT | retain notice |
| M12 fail-closed checkpoints + state-only rollback | OpenHands / DeerFlow (MIT) | MIT | retain notice |

All twelve donors are permissive `[R]`; no copyleft or non-commercial donor appears. **Still required:** check each donor repository for a `NOTICE` file and carry its text into our `NOTICE` (Apache-2.0 §4(d)); this is a per-repo file check at adoption time, not assumed `[U]`.

**Excluded by licence policy (unchanged from `02-AGENT-REPOS.md` §5.3):** hyperbrowserai/HyperAgent (**AGPL-3.0**), facebookresearch/HyperAgents (**CC BY-NC-SA 4.0**), hyperagent.com (**proprietary**), alex-hyperagent/hyperagent-public-skills and stanford-iris-lab/meta-harness-tbench2-artifact (**no licence**). Do not copy code, prompts, or assets from these into the product.

**Runtime dependencies (licence to be confirmed by SBOM, not assumed):**

| Layer | Items | Expected licence | Gate |
|---|---|---|---|
| Pipeline Python | asyncpg, httpx, Pillow | Apache-2.0 / BSD-3 / MIT-CMU-family | confirm with SBOM |
| DeerFlow Python | from `backend/pyproject.toml` + `uv.lock` (FastAPI, LangGraph/LangChain, pydantic, …) | MIT/BSD/Apache | confirm with SBOM |
| Console Node | React, Radix, TanStack, Tailwind, better-auth, kysely, pg, Playwright | MIT (Playwright Apache-2.0) | confirm with SBOM |
| Images | `postgres:16` (PostgreSQL Licence), `nginx:1.31.2-alpine` (BSD-2), `redis:7-alpine` (**verify version; ≥7.4 RSALv2/SSPLv1**) | mixed | pin digest + read image licence |
| Vendor | vectorcraft 0.21.1, photocraft 0.20.2, artcraft-docs | proprietary, EULA unknown | obtain EULA + checksums |

**Deliverables to build (proposal, not applied):**
1. `LICENSE` — decide the project licence (owner decision; internal-only vs source-available).
2. `NOTICE` + `THIRD-PARTY-NOTICES.md` — generated sections for Python/Node/images + hand-written donor attributions.
3. `deploy/sbom/` — CycloneDX JSON per deployment (tool choice verified at execution; candidates: `syft`, `trivy fs`, `pip-licenses`, `license-checker` — availability **not** assumed `[U]`).
4. `licenses/policy.json` — allow: MIT, BSD-2/3, Apache-2.0, ISC, PSF, PostgreSQL, MIT-CMU; review: MPL-2.0; deny in distributed code: AGPL, SSPL, RSALv2, CC-BY-NC*, unlicensed.
5. CI gate: fail the build on a denied licence or a missing donor notice.

### 3.10 Host and network surface

| Surface | State | Action |
|---|---|---|
| `0.0.0.0:22` SSH | open, `[V]`; config unread `[U]` | Preflight: `sshd -T \| grep -E 'permitrootlogin\|passwordauthentication'`; require key-only, no root password login; consider fail2ban |
| `0.0.0.0:80/443` | caddy for the separate Ridgeboundia app `[R]` | Out of scope; do not touch in this change window |
| `127.0.0.1:2026` | DeerFlow nginx `[R]` | keep loopback; never `BIND_HOST=0.0.0.0` for DeerFlow unless the security recommendations are implemented `[R]` |
| `0.0.0.0:8765` | pod MCP `[R]`; internet-closed from one vantage `[V]` | §3.1 |
| `127.0.0.1:8091` | console, no auth `[R]` | leave loopback; add auth before exposing; do not add a `BIND_HOST` for it |
| `127.0.0.1:65529` + UDP `:1721` | `monarx-agent` `[R]` | provenance check (`systemctl cat`, `dpkg -S`, package signature); remove if not required |
| Docker disk | 32.26 GB images (76 % reclaimable) + 15.38 GB build cache; 63 % used `[R]` | reclaim before change window; never prune during an incident without a pull plan |
| Swap / RAM | 2.5 GB swap used; ~4.8 GB available `[R]` | cap the agent process; OOM is the most likely outage vector |

### 3.11 Logging, audit and redaction

- MCP: log `remote_addr`, tool name, allow/deny, latency — **never** argument values that may contain paths or secrets. `[R]` (current server has no access log)
- DeepSeek: never log `Authorization` headers; scan logs for `sk-`-shaped strings (count-only scan, no print) and rotate on any hit. `[V]` (policy)
- Change window: every action logged to a change record (who, command, result, rollback point) — no secrets in the record.
- DeerFlow traces (`monocle`) and token dashboard are useful evidence; they must not be published with prompts containing credentials. `[R]`

### 3.12 Backups and rollback before any change

- Postgres: no `psql` client on the host; use `docker exec pod-postgres pg_dump` (read-only dump to `/tmp`, then copy off-host) — verify `pg_dump` exists in the image at execution `[U]`. The `pod` DB currently has 0 rows `[R]`, so the risk is low but the schema still matters.
- Config: back up `pipeline.env`, the systemd units, `extensions_config.json`, `config.yaml`, compose file with mode 600 and a hash.
- Images: know the pull/digest path *before* pruning; never prune the only copy of a running image.
- Rollback for every item is stated in §3.1–3.8; the change window (§5) is ordered so that each step can be reverted independently.

---

## 4. Preflight checklist (read-only, run before the change window)

All commands are read-only; no secret value is printed. Run from the workstation (off-host) and on the VPS (SSH, batch mode).

| # | Check | Command (representative) | Pass criteria | Sev |
|---|---|---|---|---|
| P0 | Host capacity | `free -m; df -h /; uptime` | ≥2 GB available RAM, ≥10 GB free disk | Med |
| P1 | MCP not internet-reachable (off-host) | `Test-NetConnection 179.197.88.181 -Port 8765` (Windows) / `nc -vz` (Linux) | `TcpTestSucceeded: False` | Crit |
| P2 | MCP bind address | `ss -lntp \| grep 8765` | expected bind only (today `0.0.0.0` — fails gate until §3.1) | Crit |
| P3 | Docker group membership | `systemctl show pod-mcp -p SupplementaryGroups; getent group docker; id pod` | `pod` not in `docker` | Crit |
| P4 | Docker socket perms | `stat -c '%a %U:%G' /var/run/docker.sock` | `660 root:docker` and group minimal | High |
| P5 | Key presence (names only) | `docker inspect --format '{{range .Config.Env}}{{println .}}{{end}}' deer-flow-gateway \| grep -c '^DEEPSEEK_API_KEY='` | `1` | High |
| P6 | Key validity, zero spend | §3.4 metadata calls | both `200` and `is_available=true` | High |
| P7 | Secret file modes | `stat -c '%a %U:%G' /opt/pod-pipeline/config/pipeline.env` | `640` or `600`, root-owned preferred | Med |
| P8 | DeerFlow pin manifest | §3.7 commands | matches `deploy/pins.lock` | High |
| P9 | Key-leak scan | `journalctl -u pod-mcp -u deer-flow-gateway --since -7d \| grep -c 'sk-'`; `docker logs … 2>&1 \| grep -c 'Bearer '` | `0` | High |
| P10 | Licence files / SBOM | `ls LICENSE NOTICE THIRD-PARTY-NOTICES.md deploy/sbom 2>/dev/null` | present after §3.9 | Med |
| P11 | Image versions/digests | `docker images --digests`; `docker exec deer-flow-redis redis-server --version` | digests recorded; Redis licence resolved | High |
| P12 | SSH posture | `sshd -T \| grep -E 'permitrootlogin\|passwordauthentication'` | `permitrootlogin no` (or `prohibit-password`), `passwordauthentication no` | Med |
| P13 | Console exposure | off-host `8091` + `ss -lntp \| grep 8091` | closed externally, loopback bind | Med |
| P14 | Vendor binary hashes | `sha256sum /opt/craft/*/…/bin/*-cli` | recorded in `deploy/vendor-craft.lock` | High |
| P15 | Unknown host agent | `systemctl cat monarx-agent; dpkg -S $(command -v monarx-agent)` | provenance known or removed | Low |

**Gate rule:** P1–P3, P5–P6, P8 must pass **before** any Craft-driving agent is enabled. P10/P11 can pass with an explicit, dated waiver.

---

## 5. Change window (ordered; execute later, not in this task)

| Order | Change | File / command | Rollback | Verification |
|---|---|---|---|---|
| 1 | Snapshot configs + hashes (§3.12) | `install -m600` copies; `sha256sum` | restore copies | hashes match |
| 2 | Rebind MCP to `172.17.0.1` (§3.1 A) | `pipeline.env` value; `systemctl restart pod-mcp` | revert value + restart | P2/P1; gateway health 200 |
| 3 | Drop `SupplementaryGroups=docker` + confinement (§3.2) | unit file; `daemon-reload`; restart | restore unit | P3/P4; `docker ps` as pod fails; one craft run OK |
| 4 | Tighten secret file modes (§3.3) | `chmod/chown`; verify systemd still starts | restore modes | P7; service up |
| 5 | Rotate DeepSeek key (§3.5) | platform + env file + gateway restart | re-enable A, revoke B | P5/P6/P9; old key 401 |
| 6 | Pin manifest + digest deploy (§3.7) | `deploy/pins.lock`; compose override | restore compose | P8/P11 |
| 7 | Vendor hash manifest + EULA request (§3.8) | `deploy/vendor-craft.lock` | n/a (record only) | P14 |
| 8 | NOTICE/SBOM policy (§3.9) | new repo files + CI gate | revert CI gate | P10 |
| 9 | MCP bearer token (§3.1 B) | `mcp_server.py` + `extensions_config.json` | unset token / revert | 401 unauth, 200 auth, 3 tools |
| 10 | Spend ledger + balance monitor (§3.6) | Forge Conductor service (task-9) | disable monitor | ledger row per call; `402` stops |

Window length estimate: 45–90 minutes for steps 1–6; steps 7–10 are follow-ups. No step requires a Craft run to be in flight; steps 2–6 restart services, so schedule when idle.

---

## 6. Verification matrix (control → test → expected)

| Control | Test | Expected |
|---|---|---|
| MCP not public | off-host TCP 8765 | timeout / refused |
| MCP auth | unauthenticated POST | 401 JSON-RPC error |
| MCP reachable by consumer | gateway health + `tools/list` | 200 + 3 tools |
| Least privilege | `id pod`, `docker ps` as pod | no docker group; permission denied |
| Key valid | `/user/balance`, `/models` | 200 + `is_available` |
| Key not leaked | log scan count | 0 |
| Old key dead | old key metadata call | 401 |
| Pinned build | manifest compare | all hashes/digests match |
| Licence policy | CI licence gate | no denied licences; NOTICE present |
| Spend stop | simulated `402` | fail-closed refusal, no retry storm |

---

## 7. Answers to the two differential questions (WP-5)

**Q8 — "What is the exact DeepSeek key validation that does not spend quota?"**
`GET https://api.deepseek.com/user/balance` and `GET https://api.deepseek.com/models` with `Authorization: Bearer $DEEPSEEK_API_KEY`, executed inside the gateway container with the header passed via `curl -K -` (stdin) so the secret never appears in `ps`. `200` = valid; `401` = invalid/revoked; `402` = valid but no balance; `429`/5xx/timeout = rate/provider/network, not key validity. A chat completion is explicitly forbidden as a validation step. `[V]` docs + `[I]` no-token billing.

**Q9 — "What is the licence/NOTICE delta for each borrowed mechanism?"**
Twelve mechanisms will be adapted from nine permissive donors: Goose (Apache-2.0), SWE-agent (MIT), Aider (Apache-2.0), Continue (Apache-2.0), OpenHands (MIT), Cline (Apache-2.0), Playwright MCP (Apache-2.0), DeerFlow (MIT), plus Playwright (Apache-2.0) for M6/M10 context. Delta to implement: add `LICENSE`, `NOTICE`, `THIRD-PARTY-NOTICES.md`, per-repo `NOTICE` file checks, CycloneDX SBOMs, and a CI deny-list. No non-permissive donor is used; the AGPL / CC-BY-NC / proprietary / unlicensed candidates stay excluded. `[R]`

---

## 8. Unverified and residual risks

| # | Item | Why | Resolution |
|---|---|---|---|
| U1 | External reachability of 8765 from *all* networks | one off-host vantage verified closed `[V]`; not proof for provider-internal or other peers | keep the P1 probe in CI/preflight; internal boundary is §3.1/§3.2 |
| U2 | Redis resolved version and licence (≥7.4 RSALv2/SSPL?) | floating `redis:7-alpine` tag; image not inspected in this task | `redis-server --version` + read image licence at pin time (P11) |
| U3 | DeerFlow MCP client support for static auth headers | `backend/docs/MCP_SERVER.md` not fetched | fetch and confirm before §3.1 Option B; else use Option A/bridge |
| U4 | Systemd `EnvironmentFile` readability at 0600 root | not tested on host | test in the change window; fallback 0640 root:pod |
| U5 | DeepSeek metadata endpoints are free | inferred from API semantics; docs do not state billing for metadata | treat as `[I]`; if ever billed, the cost is bounded and still avoids token generation |
| U6 | Docker socket perms / docker group members / SSH config / monarx provenance | not re-probed (read-only mandate; task-1 did not cover) | preflight P3/P4/P12/P15 |
| U7 | Per-key spend limit at DeepSeek | no per-key budget documented | client-side budgets (§3.6) |
| U8 | Vendor EULA and checksums | none on host | vendor request; hash manifest meanwhile |
| U9 | `pg_dump` availability for backup | no `psql` client on host; container image path only | verify in change window |
| U10 | VPS facts may have drifted since the audit | this task did not SSH | run the preflight; if it contradicts `01-STACK-VPS.md`, stop and update the audit |

---

## 9. Bibliography (accessed 2026-11-05)

**Official DeepSeek API documentation — fetched this task (`[V]`):**
- https://api-docs.deepseek.com/ — base URLs, `Authorization: Bearer`, `deepseek-flash` = DeepSeek-V4.1-Flash-1017
- https://api-docs.deepseek.com/api/list-models — `GET /models` response fields
- https://api-docs.deepseek.com/api/get-user-balance — `GET /user/balance`, `is_available`, balances
- https://api-docs.deepseek.com/quick_start/error_codes — 401/402/429/500/503 semantics
- https://api-docs.deepseek.com/quick_start/rate_limit — account concurrency (2500 flash / 500 pro), `user_id` isolation

**Repo files read this task (read-only, `[V]`):**
- `DeerFlow Forge/blueprint/files/deploy/systemd/pod-mcp.service` — `User=pod`, `SupplementaryGroups=docker`, `NoNewPrivileges=true`
- `DeerFlow Forge/blueprint/files/deploy/compose.yml` — `postgres:16` floating tag, port/mem/cpu lines
- `DeerFlow Forge/blueprint/files/pod_pipeline/mcp_server.py` — `handle_rpc` (301), `_http` (335), `_client` (373), `serve_http` (409): no auth
- `DeerFlow Forge/blueprint/files/pod_pipeline/config.py` — `mcp_host` default `127.0.0.1` (60, 115)
- `DeerFlow Forge/blueprint/files/requirements.txt` / `requirements-test.txt` — runtime/test Python deps
- `DeerFlow Forge/package.json` — console dependency names
- `DeerFlow Forge/.gitignore` — `.env*` excluded, no secret-like tracked file

**Sibling artifacts cited (`[R]`):**
- `research/eko-deerflow-agent/wave2/01-STACK-VPS.md` — VPS facts, services/ports, env names, risks R1–R12, gaps
- `research/eko-deerflow-agent/wave2/02-AGENT-REPOS.md` — licence/NOTICE source-of-truth for candidate harnesses and the do-not-use list
- `research/eko-deerflow-agent/wave2/05-HARNESS-CODE.md` — donor mechanism IDs and licences (`§1.1`, `§4`)
- `research/eko-deerflow-agent/execution-wave/00-WAVE-2-PLAN.md` — WP-5 definition, differential questions Q8/Q9

**Probes run this task (`[V]`):** TCP connect from the workstation to `179.197.88.181` ports 8765 (closed), 8091 (closed), 22 (open), 2026-11-05.

**Not fetched / not used:** any VPS shell, any DeepSeek chat completion, `backend/docs/MCP_SERVER.md`, vendor EULA, image licence texts.

---

## 10. Hand-off

- **Do first, today:** §3.1 Option A (rebind) and §3.2 (drop docker group) — both are reversible in under five minutes and remove the two critical structural risks.
- **Do before any agent is enabled:** §3.4 zero-spend validation, §3.5 rotation, §3.7 pin manifest, preflight gate.
- **Do before packaging/distribution:** §3.9 NOTICE/SBOM and the vendor licence record, or the packaged corpus would ship unattributed permissive code and unexplained proprietary binaries.
- **Do not do:** expose 8765 publicly, keep `pod` in `docker`, add a chat-completion key probe, follow `main`, prune images without a pull path, or copy code from the AGPL/CC-BY-NC/proprietary donors.
