# Plan & Wiring Consistency Audit — 2026-11-05

**Task:** task-26 (Wave 1, read-only) · **Seat:** harness-architect (plan/wiring consistency)
**Mode:** audit + decision-complete plan. **No source, docs, tests, git, deploy or production were modified.**
**Evidence labels:** `VERIFIED` = read this session with `path:line`; `READ` = quote from a file read this session;
`INFERRED` = follows from symbols but body not read; `UNVERIFIED` = not checked this session; `CONFLICT` = two
sources disagree.

---

## 1. Recon ledger

- **Target behaviour:** the Forge Conductor (gateway → repo → worker → verifier/critic/eval → service) is
  claimed complete *locally* and is described by two governance docs that must agree on its gate state and
  on what an implementer may do next.
- **Entry points:** `docs/PLAN-CONTINUATION.md:1` (status/decision), `docs/AGENT-SKILL-MATRIX.md:1`
  (when-to-use + current gate), `blueprint/files/forge_*.py` (7 runtime modules),
  `blueprint/files/tests/test_forge_*.py` (8 modules) and
  `blueprint/files/tests/forge_schema_{assertions,skiplock}.py` (2 out-of-band scripts).
- **Callers:** `forge_service.py:121` injects `repo` into the server object; the tests are the only wiring
  harness read (bodies not read → `UNVERIFIED`). No production caller of any `forge_*` module exists in
  this repo (`VERIFIED` by symbol/cross-import scan: only `forge_service.py:121` mentions `forge_repo`).
- **Tests + command:** `blueprint/files/pytest.ini:1-6` → `testpaths = tests`, `asyncio_mode = auto`.
  Command: `cd blueprint/files && python -m pytest tests -q`. The two `forge_schema_*.py` scripts are **not**
  `test_*.py` and need `FORGE_TEST_DSN` (`forge_schema_assertions.py:17-20`), so `pytest` does not collect them.
- **Data flow (one path):** HTTP route (`forge_service.py:51,80`) → `ServiceRepo` protocol (`:19`) →
  `ForgeRepo` asyncpg methods (`forge_repo.py:46-106`) → SQL functions → Postgres. One failure path:
  malformed body → JSON 4xx (body not read → `UNVERIFIED`).
- **Unknowns:** bodies of service/repo/worker/tests; `requirements.txt` asyncpg/Pillow presence; whether a
  Makefile/CI runs the SQL scripts; `execution-wave/09-GOAL-GAP-PLAN.md` §5.2 content.
- **Files I would touch (future waves only):** the two docs, `forge_repo.py`, `forge_service.py`,
  `forge_worker.py`, `tests/forge_schema_*.py` (+ test invocation), `tests/test_forge_repo.py`.

---

## 2. Document consistency findings

| # | Claim | Source A | Source B | Class |
|---|---|---|---|---|
| D1 | G0 execution provenance | **CLOSED independently** (`16-G0-PROVENANCE.md`, byte-identical staging run) `PLAN-CONTINUATION.md:19` | **"execution provenance U"** and W2 may proceed **only if the owner accepts the caveat, otherwise wait for verifier VPS access** `AGENT-SKILL-MATRIX.md:34-36` | **CONFLICT** |
| D2 | W2 state | **local gate PASS**, 139 pass/4 skip, 18/18 SQL, SKIP LOCKED, e2e `PLAN-CONTINUATION.md:20` | gate section still conditions W2 on the provenance caveat `AGENT-SKILL-MATRIX.md:34-36` | **CONFLICT** (stale gate) |
| D3 | Historical "do not start W2" | superseded and retained only in history `PLAN-CONTINUATION.md:34-36` | matrix never records the supersession | **WEAK** |
| D4 | "Read first" set | `README.md, GOALS.md, ARCHITECTURE.md, execution-wave/09, 11-G0-EVIDENCE.md, docs/TRACE/03-fixes.md` `PLAN-CONTINUATION.md:3-4` | all five exist (`VERIFIED` this session) | OK |
| D5 | W2 recon inputs | `execution-wave/02-FORGE-SKELETON.md`, `ARCHITECTURE.md`, **`04-HARNESS-DESIGN.md`**, `execution-wave/09 §5.2`, `pod_pipeline` DB patterns `AGENT-SKILL-MATRIX.md:25` | `04-HARNESS-DESIGN.md` actually lives at `wave2/04-HARNESS-DESIGN.md` (`VERIFIED`); `09 §5.2` section not read | **WEAK path** |
| D6 | DeerFlow registration | **not applied** `PLAN-CONTINUATION.md:13` | matrix's gate section does not carry this blocker | **MISSING** |
| D7 | Learning claim | W4-A contract only, no learning claim; W4-B not started `PLAN-CONTINUATION.md:24-25` | matrix: "W2 is not a learning claim" `:28` | OK |

**Root cause of D1/D2:** the matrix's gate paragraph was written before `16-G0-PROVENANCE.md` closed the
caveat; `PLAN-CONTINUATION` was updated, the matrix was not. One of the two must become the single source of
truth for gate state.

---

## 3. Wiring audit (code-level)

| # | Expected wiring | Evidence | Class | Impact |
|---|---|---|---|---|
| W1 | Gateway persists tool calls through a `Repo` (`find`/`store`) | `forge_gateway.py:237-243` defines the protocol; `forge_gateway.py:246-258` ships only `InMemoryRepo`; `forge_repo.py:46-106` has **no `find`/`store`** | **GAP (VERIFIED)** | Idempotency is proven in-memory only; the HTTP/repo path has **no tool-call replay store**. W2's "e2e" cannot cover duplicate-call safety |
| W2 | Worker is runnable | `forge_worker.py:46-74` has `ForgeWorker`/`drain` but the symbol scan finds **no `__main__`, no argparse, no CLI** (contrast `forge_verifier.py:109,136`) | **GAP (VERIFIED)** | The worker is library-only; any "service loop" claim needs an entry point or an explicit invocation recipe |
| W3 | One transition = one event | `forge_repo.py:63` `transition()` and `forge_repo.py:73` `append_event()` both exist; the SQL transition function already appends an event (execution-wave/02 §3) | **INFERRED risk** | If `transition()` also calls `append_event()`, every transition double-writes. Body not read this session → `UNVERIFIED` |
| W4 | Verifier/critic are on the execution path | `forge_verifier.py:109` is a standalone CLI; `forge_critic.py:30,82` are pure functions; cross-import scan shows only `forge_service.py:121` referencing another module | **GAP (VERIFIED)** | W3-A/W3-B are **contract-tested libraries**; no route/queue consumer wires them into a run. Docs say "DONE (contract)" — accurate, but a reader may over-read it |
| W5 | Eval/promotion persists | `forge_eval.py:12,24,56` are pure; `ForgeRepo` has no eval/promotion methods (`forge_repo.py:46-106`) | **GAP (VERIFIED)** | W4-A is a decision function, not a persisted decision; `10-CLAIM-REGISTER` must not claim promotion history |
| W6 | SQL invariants run in CI | `pytest.ini:1-2` collects `tests`; scripts are `forge_schema_assertions.py` / `forge_schema_skiplock.py` (`:17`, `:12` need `FORGE_TEST_DSN`) → **not collected** | **GAP (VERIFIED)** | "18/18 SQL" and SKIP LOCKED are manual; a green `pytest` run does not prove them |
| W7 | Clean-env test deps | `requirements-test.txt` lists only `-r requirements.txt`, pytest, pytest-asyncio; `asyncpg` (`forge_repo.py:12`) and `Pillow` (`forge_verifier.py:15`) must come from `requirements.txt` | **UNVERIFIED** | If absent, forge repo/verifier tests fail on a clean environment |
| W8 | Service auth/limits | `forge_service.py:19-35,46-110` shows a loopback-style HTTP service; no token/auth symbol visible in the scan | **UNVERIFIED** | Security posture unproven; `05-SECURITY` plan already exists as the owning task |

No production caller exists for any `forge_*` module, so **W1–W8 are the complete wiring surface inside this
repo** (`VERIFIED` by the cross-import scan).

---

## 4. Decision-complete next-step plan

Ordered, each step independently verifiable. No step is allowed to edit source in Wave 1; steps are for the
next wave. Every step names its rollback.

**P0 — Make the gate state single-sourced (docs only).**
- Change: rewrite `AGENT-SKILL-MATRIX.md:32-36` to reference `PLAN-CONTINUATION.md:19-31` as authoritative,
  replacing the stale "provenance U" paragraph with the closed state and the remaining real blockers
  (DeerFlow registration not applied `PLAN-CONTINUATION.md:13`; W4-B not started `:25`; no production cutover).
- Fix `AGENT-SKILL-MATRIX.md:25` path to `wave2/04-HARNESS-DESIGN.md`.
- Acceptance: `grep -n "provenance" docs/*.md` returns no "U" claim for G0; both docs name the same three
  blockers. Command: `rg -n "provenance|blocker" docs/PLAN-CONTINUATION.md docs/AGENT-SKILL-MATRIX.md`.
- Rollback: `git checkout -- docs/AGENT-SKILL-MATRIX.md`.

**P1 — Close the idempotency wiring gap (W1).**
- Change: add `ForgeRepo.find_tool_call(key)` / `store_tool_call(...)` using `forge_tool_call` (DDL in
  `execution-wave/02-FORGE-SKELETON.md` §3); add `PgRepo` adapter satisfying `forge_gateway.Repo`; test
  duplicate call returns stored result with **executor call count 1** against a real scratch DB.
- Acceptance: new `tests/test_forge_repo_toolcall.py` passes on `FORGE_TEST_DSN`; existing
  `tests/test_forge_gateway.py` still green. Command: `python -m pytest tests/test_forge_repo_toolcall.py -q`.
- Rollback: delete new file + adapter method (no schema change; table already exists).

**P2 — Remove the double-append risk (W3).**
- Change: read `forge_repo.py:63-79`; make **one** owner of event append (either the SQL function or the repo,
  not both); add a test asserting exactly one `episode.transition` event per transition.
- Acceptance: `SELECT count(*) FROM forge_event WHERE kind='episode.transition'` equals transitions issued.
- Rollback: revert the repo edit; SQL function is unchanged.

**P3 — Give the worker an entry point (W2).**
- Change: add `python -m forge_worker` (argparse: `--once|--loop`, `--lease-s`, `--dsn-env`) matching
  `forge_verifier.py:109` conventions; no behavior change to `ForgeWorker`.
- Acceptance: `python -m forge_worker --once` with a scratch DB claims and finishes one queued job; exit 0.
- Rollback: delete `if __name__ == "__main__"` block; library API untouched.

**P4 — Put SQL invariants into the test suite (W6).**
- Change: add `tests/test_forge_schema.py` that runs the assertion bodies when `FORGE_TEST_DSN` is set and
  `pytest.skip("FORGE_TEST_DSN unset")` otherwise; reference the existing scripts, do not duplicate assertions.
- Acceptance: `pytest -q` shows 18 assertions as collected tests when DSN is set, and skips cleanly when not.
- Rollback: delete the wrapper file.

**P5 — Reconcile the claim register (evidence).**
- Change: update `execution-wave/10-CLAIM-REGISTER.md` with W1–W8 statuses from §3 of this audit.
- Acceptance: every W-row in this audit appears with a class; no claim of persisted idempotency, worker
  service, or wired verifier/critic/eval.
- Rollback: restore the previous register.

**Sequencing rationale:** P0 first because a contradictory gate doc can authorise scope the evidence does not
support; P1/P2 are correctness; P3/P4 are operability; P5 is the receipt. P1 and P2 must precede any claim of
"HTTP→repo→worker e2e idempotency".

---

## 5. Failure modes of this plan

| Mode | Handling |
|---|---|
| `FORGE_TEST_DSN` unavailable | P1/P4 tests skip explicitly with a named reason; SQL gaps stay `UNVERIFIED`, never silently green |
| Repo body already appends (P2) | Stop; do not delete the repo call until the SQL function ownership is confirmed; record as `CONFLICT` |
| Worker entry point conflicts with a deployment owner | Keep `--once` only; do not add supervision (no systemd/systemd unit in scope) |
| Doc rewrite loses history | Keep the historical note (`PLAN-CONTINUATION.md:34-36`) verbatim; add a dated supersession line |
| Scope creep into production | Blocked: no DB, no deploy, no DeerFlow registration; those are separate owners |

---

## 6. Out of scope / blockers (must not be claimed solved by this plan)

- **Production cutover, supervised service, PostgreSQL production DB** — `PLAN-CONTINUATION.md:29-32`.
- **DeerFlow MCP registration** — explicitly "not applied" `PLAN-CONTINUATION.md:13`; W1-B evidence is staging
  only.
- **W4-B learning loop** — "not started" `PLAN-CONTINUATION.md:25`; no learning claim is permitted.
- **VPS read-only verifier access** — `AGENT-SKILL-MATRIX.md:35`; provenance caveat closing depended on it.
- **Auth/security hardening** of `forge_service.py` — owned by `05-SECURITY` plan, not this audit.

---

## 7. UNVERIFIED (explicit)

1. Bodies of `forge_repo.py`, `forge_service.py`, `forge_worker.py`, `forge_critic.py`, `forge_verifier.py`,
   `forge_eval.py` and all `tests/test_forge_*.py` — not read this session; gaps W1–W8 are symbol-level.
2. Whether `transition()` double-appends events (W3) — `INFERRED` risk only.
3. `requirements.txt` containing `asyncpg`/`Pillow` (W7).
4. Whether any Makefile/CI invokes `forge_schema_assertions.py` / `forge_schema_skiplock.py`.
5. The claimed "139 pass/4 skip", "18/18 SQL", "9 ms SKIP LOCKED" — `READ` from
   `PLAN-CONTINUATION.md:20-24`, **not re-run** by this audit.
6. `execution-wave/09-GOAL-GAP-PLAN.md` §5.2 content referenced by `AGENT-SKILL-MATRIX.md:25`.
7. `forge_service.py` auth/route validation (W8).

---

## 8. Evidence appendix (commands run, read-only)

- `Get-ChildItem blueprint/files -Filter forge_*.py` → 7 modules (`VERIFIED`).
- `Select-String forge_*.py` for imports/classes/functions/`__main__` → symbol map in §3 (`VERIFIED`).
- `Get-ChildItem tests` → 8 `test_forge_*.py` + 2 `forge_schema_*.py` scripts (`VERIFIED`).
- `Get-Content docs/PLAN-CONTINUATION.md`, `docs/AGENT-SKILL-MATRIX.md`, `pytest.ini`,
  `requirements-test.txt` (`READ`; line anchors quoted above).
- `Test-Path` for the five "read first" files → all present (`VERIFIED`).
- **Not run:** pytest, SQL scripts, service, worker, any database (read-only audit; no DSN used).

---

*No files outside this report were created or modified. Next wave starts at P0; P1/P2 require a scratch
`FORGE_TEST_DSN` and must not touch production.*
