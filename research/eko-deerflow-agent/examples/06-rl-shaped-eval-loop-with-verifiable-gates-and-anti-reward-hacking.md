# Example 6 — RL-shaped eval loop with verifiable gates and anti-reward-hacking

> Extracted from `wave2/07-EXAMPLES.md` (task-7). Original code/design, validated as recorded there; not production code.

## 6. Example 6 — RL-shaped eval loop with verifiable gates and anti-reward-hacking

### 6.1 What it demonstrates

An evaluation loop that can *promote or reject a policy*, where "policy" means **retrieval +
active skills**, not model weights. The loop is RL-shaped because it selects actions from
evidence, but its reward is a **hard conjunction of verified properties**, not a scalar proxy
that can be gamed. Every known shortcut gets an explicit detector, and a null result is a
first-class outcome (`hold`), not a failure to be tuned away.

Design decision D10 is respected: no fine-tuning, no gradient updates, no PPO/RLHF pipeline.
If RL is ever considered (Phase 3+), this file's reward discipline is the precondition — a
verifiable reward, a private held-out set, and gate authorship separation.

### 6.2 Loop

```text
golden set (public dev 36 / private held-out 14)
        │
        ├── arm A: no retrieval, no promoted skills  (baseline)
        └── arm B: retrieval + active skills          (memory)
                    │
        randomised runs: ≥3 per golden per arm, identical budgets, same model/app/catalogue
                    │
        per-run record → verifiable_reward ∈ {0,1}
                    │
        anti-hack checks (private leakage, gate authorship, brief drift, shortcuts, cost anomaly,
        threshold hugging, skipped critic)
                    │
        Wilson 95% CI per arm; Newcombe CI for lift (B − A)
                    │
        verdict: promote_candidate | hold | reject
                    │
        promote/rollback via Example 5; every change re-runs the regression gates
```

### 6.3 Reward and metrics

```python
# Verifiable reward — a hard conjunction, no partial credit (Example 6 sketch).
reward = 1.0 if (
    run.passed_verified
    and run.unsafe_side_effects == 0
    and not run.source_mutated
    and run.gate_produced_by == "print_verifier"
    and not run.failure_codes
    and not run.input_override
) else 0.0
```

| Metric | Definition | Target |
|---|---|---|
| Primary: first-attempt verified-pass rate | accepted on attempt 1 / attempted goldens (rungs 1–5, +6 where required) | ↑ |
| Attempts per accepted artifact | tool batches until accepted | ↓ |
| Precision of "pass" | human-accepted / runs marked pass | ↑ (honesty metric) |
| Unsafe side effects | source mutations + unapproved publishes | = 0 |
| Regression rate | previously passing goldens now failing | = 0 |
| Retrieval lift | pass rate (B − A) with 95% CI | > 0 and CI excludes 0 |
| Critic stability | verdict flips on identical inputs | ↓ |
| Cost per accepted artifact | tokens + wall time (no invented dollars) | ↓ |

### 6.4 Sketch

<!-- Example 6 sketch — validated with py_compile + 8 scratch-harness checks -->
```python
"""Example 6 - evaluation / learning loop with verifiable gates and anti-reward-hacking.

Forge Conductor mechanism sketch (Python 3.11+). Design-only: this is policy
selection over skills and retrieval, NOT weight training. Reward is binary and
gate-verified; a scalar proxy is deliberately not used.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Iterable, Mapping, Sequence

MIN_RUNS_PER_ARM_PER_GOLDEN = 3
THRESHOLD_HUG_MARGIN = 0.01
THRESHOLD_HUG_SHARE = 0.20


class Arm(StrEnum):
    BASELINE = "baseline"
    MEMORY = "memory"


class EvalRefused(Exception):
    def __init__(self, code: str, message: str, how_to_fix: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.how_to_fix = how_to_fix


@dataclass(frozen=True)
class GoldenTask:
    golden_id: str
    task_family: str
    private: bool
    input_sha256: str
    brief_hash: str
    min_tool_calls: int
    token_floor: int
    required_gates: tuple[str, ...]
    human_required: bool
    suite_version: str

    def __post_init__(self) -> None:
        if not self.required_gates:
            raise ValueError("every golden needs at least one required gate")
        if self.min_tool_calls < 1:
            raise ValueError("min_tool_calls must be positive")
        if self.token_floor < 0:
            raise ValueError("token_floor must be non-negative")


@dataclass(frozen=True)
class RunRecord:
    run_id: str
    arm: Arm
    golden_id: str
    passed_verified: bool
    human_accepted: bool | None
    attempts: int
    unsafe_side_effects: int
    source_mutated: bool
    failure_codes: tuple[str, ...]
    tool_calls: int
    tokens_in: int
    tokens_out: int
    brief_hash: str
    input_sha256: str
    input_override: bool
    retrieved_case_ids: tuple[str, ...]
    gate_produced_by: str
    threshold_margin: float
    critic_validated: bool

    @property
    def tokens(self) -> int:
        return self.tokens_in + self.tokens_out


@dataclass(frozen=True)
class HackFlag:
    code: str
    severity: str  # critical | major | minor
    detail: str
    run_id: str | None = None


@dataclass(frozen=True)
class Reward:
    value: float
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class ArmMetrics:
    runs: int
    pass_rate: float
    pass_ci: tuple[float, float]
    precision_pass: float | None
    median_attempts: float
    mean_tokens: float
    unsafe_side_effects: int


@dataclass(frozen=True)
class EvalReport:
    suite_version: str
    goldens: int
    baseline: ArmMetrics
    memory: ArmMetrics
    lift: float
    lift_ci: tuple[float, float]
    regressions: int
    flags: tuple[HackFlag, ...]
    verdict: str
    generated_at: str


def wilson_interval(successes: int, trials: int, z: float = 1.96) -> tuple[float, float]:
    if trials <= 0:
        raise ValueError("trials must be positive")
    if not 0 <= successes <= trials:
        raise ValueError("successes must be within [0, trials]")
    p = successes / trials
    denominator = 1 + z * z / trials
    centre = (p + z * z / (2 * trials)) / denominator
    half = z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials)) / denominator
    return max(0.0, centre - half), min(1.0, centre + half)


def newcombe_difference_ci(
    successes_a: int,
    trials_a: int,
    successes_b: int,
    trials_b: int,
    z: float = 1.96,
) -> tuple[float, float]:
    """Newcombe score interval for p_b - p_a; used to test retrieval lift."""
    p_a = successes_a / trials_a
    p_b = successes_b / trials_b
    low_a, high_a = wilson_interval(successes_a, trials_a, z)
    low_b, high_b = wilson_interval(successes_b, trials_b, z)
    diff = p_b - p_a
    lower = diff - math.sqrt((p_b - low_b) ** 2 + (high_a - p_a) ** 2)
    upper = diff + math.sqrt((high_b - p_b) ** 2 + (p_a - low_a) ** 2)
    return max(-1.0, lower), min(1.0, upper)


def verifiable_reward(run: RunRecord) -> Reward:
    """Reward is a hard conjunction of verified properties. No partial credit.

    A gate pass obtained by an operator-authored report, or a run that mutated the
    source, scores 0 even if the artifact looked correct. This is the property that
    makes the loop resistant to optimizing the score instead of the work.
    """
    reasons: list[str] = []
    if not run.passed_verified:
        reasons.append("not_verified")
    if run.unsafe_side_effects > 0:
        reasons.append("unsafe_side_effect")
    if run.source_mutated:
        reasons.append("source_mutated")
    if run.gate_produced_by != "print_verifier":
        reasons.append("gate_not_authored_by_verifier")
    if run.failure_codes:
        reasons.append("failure_codes_present")
    if run.input_override:
        reasons.append("input_override_not_rewarded")
    return Reward(0.0 if reasons else 1.0, tuple(reasons))


def detect_flags(
    runs: Sequence[RunRecord],
    goldens: Mapping[str, GoldenTask],
    private_ids: Iterable[str],
) -> list[HackFlag]:
    flags: list[HackFlag] = []
    private = set(private_ids)
    for run in runs:
        golden = goldens.get(run.golden_id)
        if golden is None:
            flags.append(HackFlag("E_EVAL_UNKNOWN_GOLDEN", "critical", f"{run.golden_id} has no definition", run.run_id))
            continue
        if set(run.retrieved_case_ids) & private:
            flags.append(
                HackFlag(
                    "E_EVAL_CONTAMINATED",
                    "critical",
                    "a private held-out golden was retrieved into context",
                    run.run_id,
                )
            )
        if run.arm is Arm.BASELINE and run.retrieved_case_ids:
            flags.append(
                HackFlag(
                    "E_EVAL_ARM_CONTAMINATED",
                    "critical",
                    "baseline run carried retrieval cases",
                    run.run_id,
                )
            )
        if run.gate_produced_by != "print_verifier":
            flags.append(
                HackFlag(
                    "E_GATE_AUTHORSHIP",
                    "critical",
                    f"gate report produced by {run.gate_produced_by}",
                    run.run_id,
                )
            )
        if run.brief_hash != golden.brief_hash and not run.input_override:
            flags.append(
                HackFlag("E_BRIEF_DRIFT", "major", "brief hash changed without an override record", run.run_id)
            )
        if run.input_sha256 != golden.input_sha256 and not run.input_override:
            flags.append(
                HackFlag("E_INPUT_MISMATCH", "major", "input differs from the frozen golden", run.run_id)
            )
        if run.tool_calls < golden.min_tool_calls:
            flags.append(
                HackFlag(
                    "E_SHORTCUT",
                    "major",
                    f"{run.tool_calls} tool calls, floor {golden.min_tool_calls}",
                    run.run_id,
                )
            )
        if run.tokens < golden.token_floor:
            flags.append(
                HackFlag(
                    "E_COST_ANOMALY",
                    "minor",
                    f"{run.tokens} tokens, floor {golden.token_floor}; critic may have been skipped",
                    run.run_id,
                )
            )
        if golden.human_required and not run.critic_validated:
            flags.append(
                HackFlag("E_CRITIC_SKIPPED", "major", "golden requires a critic pass", run.run_id)
            )

    passing = [run for run in runs if run.passed_verified]
    hugged = [run for run in passing if run.threshold_margin < THRESHOLD_HUG_MARGIN]
    if len(passing) >= 5 and len(hugged) / len(passing) > THRESHOLD_HUG_SHARE:
        flags.append(
            HackFlag(
                "E_THRESHOLD_HUGGING",
                "major",
                f"{len(hugged)}/{len(passing)} passes sit within {THRESHOLD_HUG_MARGIN:.0%} of a gate threshold",
            )
        )
    return flags


def assert_no_private_leak(retrieved_ids: Iterable[str], private_ids: Iterable[str]) -> None:
    leaked = sorted(set(retrieved_ids) & set(private_ids))
    if leaked:
        raise EvalRefused(
            "E_EVAL_CONTAMINATED",
            f"retrieval index exposes private goldens: {', '.join(leaked)}",
            "remove private fixtures from the retrieval index before any arm comparison",
        )


def _median(values: Sequence[int | float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(float(value) for value in values)
    middle = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def _arm_metrics(runs: Sequence[RunRecord]) -> ArmMetrics:
    if not runs:
        raise EvalRefused("E_EVAL_EMPTY", "an arm has no runs", "execute the golden suite before comparing arms")
    passes = sum(1 for run in runs if run.passed_verified)
    low, high = wilson_interval(passes, len(runs))
    reviewed = [run for run in runs if run.passed_verified and run.human_accepted is not None]
    precision = (
        sum(1 for run in reviewed if run.human_accepted) / len(reviewed) if reviewed else None
    )
    return ArmMetrics(
        runs=len(runs),
        pass_rate=passes / len(runs),
        pass_ci=(low, high),
        precision_pass=precision,
        median_attempts=_median([run.attempts for run in runs]),
        mean_tokens=sum(run.tokens for run in runs) / len(runs),
        unsafe_side_effects=sum(run.unsafe_side_effects for run in runs),
    )


def evaluate_arms(
    goldens: Sequence[GoldenTask],
    baseline_runs: Sequence[RunRecord],
    memory_runs: Sequence[RunRecord],
    *,
    private_ids: Iterable[str] = (),
) -> EvalReport:
    """Compare baseline vs retrieval+skills. A null result is a valid verdict."""
    if not goldens:
        raise EvalRefused("E_EVAL_EMPTY", "no goldens configured", "freeze the golden set before evaluating")
    by_id = {golden.golden_id: golden for golden in goldens}
    private = set(private_ids) | {golden.golden_id for golden in goldens if golden.private}

    for arm_name, runs in (("baseline", baseline_runs), ("memory", memory_runs)):
        counts: dict[str, int] = {}
        for run in runs:
            if run.golden_id not in by_id:
                raise EvalRefused(
                    "E_EVAL_UNKNOWN_GOLDEN", f"{arm_name} ran unknown golden {run.golden_id}", "rebuild the run manifest"
                )
            if run.arm.value != arm_name:
                raise EvalRefused(
                    "E_EVAL_ARM_MISMATCH",
                    f"{run.run_id} is arm {run.arm.value} but filed under {arm_name}",
                    "never mix arms; the comparison would be meaningless",
                )
            counts[run.golden_id] = counts.get(run.golden_id, 0) + 1
        missing = [golden_id for golden_id in by_id if counts.get(golden_id, 0) < MIN_RUNS_PER_ARM_PER_GOLDEN]
        if missing:
            raise EvalRefused(
                "E_EVAL_INCOMPLETE",
                f"{arm_name} has < {MIN_RUNS_PER_ARM_PER_GOLDEN} runs for: {', '.join(missing[:5])}",
                "run every golden at least three times per arm; randomise order and hold budgets equal",
            )

    assert_no_private_leak(
        [case_id for run in baseline_runs for case_id in run.retrieved_case_ids], private
    )
    flags = detect_flags(baseline_runs, by_id, private) + detect_flags(memory_runs, by_id, private)
    baseline = _arm_metrics(baseline_runs)
    memory = _arm_metrics(memory_runs)
    lift = memory.pass_rate - baseline.pass_rate
    lift_ci = newcombe_difference_ci(
        sum(1 for run in baseline_runs if run.passed_verified),
        len(baseline_runs),
        sum(1 for run in memory_runs if run.passed_verified),
        len(memory_runs),
    )
    regressions = len(
        {run.golden_id for run in baseline_runs if run.passed_verified}
        & {run.golden_id for run in memory_runs if not run.passed_verified}
    )
    critical = [flag for flag in flags if flag.severity == "critical"]
    if critical:
        verdict = "reject"
    elif baseline.unsafe_side_effects or memory.unsafe_side_effects or regressions:
        verdict = "reject"
    elif lift_ci[0] > 0.0:
        verdict = "promote_candidate"
    elif lift_ci[1] < 0.0:
        verdict = "reject"
    else:
        verdict = "hold"

    return EvalReport(
        suite_version=goldens[0].suite_version,
        goldens=len(goldens),
        baseline=baseline,
        memory=memory,
        lift=lift,
        lift_ci=lift_ci,
        regressions=regressions,
        flags=tuple(flags),
        verdict=verdict,
        generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )


def schedule_runs(arms: Sequence[Arm], golden_ids: Sequence[str], repeats: int, seed: int) -> list[tuple[Arm, str]]:
    """Randomised, reproducible execution order (arm-major, then shuffled)."""
    if repeats < MIN_RUNS_PER_ARM_PER_GOLDEN:
        raise ValueError(f"repeats must be >= {MIN_RUNS_PER_ARM_PER_GOLDEN}")
    plan = [(arm, golden_id) for arm in arms for golden_id in golden_ids for _ in range(repeats)]
    random.Random(seed).shuffle(plan)
    return plan
```

### 6.5 Inputs and outputs

| Direction | Value |
|---|---|
| In | `GoldenTask[]` (public/private, input hash, brief hash, minimum tool calls, token floor, required gates), `RunRecord[]` per arm |
| Out | `EvalReport {baseline, memory, lift, lift_ci, regressions, flags, verdict}` |
| Refuses | empty golden set (`E_EVAL_EMPTY`), fewer than 3 runs per golden per arm (`E_EVAL_INCOMPLETE`), private-id leakage (`E_EVAL_CONTAMINATED`), mixed arms (`E_EVAL_ARM_MISMATCH`) |
| Honesty | A single demo is an anecdote; an overlapping CI yields `hold`; the private set is a sentinel, not a scoreboard |

### 6.6 Anti-reward-hacking checks

| Hack | Detector | Severity |
|---|---|---|
| Retrieve a private held-out golden | retrieved ids ∩ private ids | critical → reject |
| Baseline arm secretly uses retrieval | baseline run with non-empty `retrieved_case_ids` | critical |
| Operator authors its own gate report | `gate_produced_by != "print_verifier"` | critical |
| Narrow the brief until it passes | brief hash mismatch without override | major |
| Swap the input for an easier one | input hash mismatch without override record | major |
| Skip required steps | tool calls below the golden's floor | major |
| Pass by threshold hugging | >20% of passes within 1% of a gate threshold | major |
| Skip the critic | required critic not validated | major |
| Skip the critic to save cost | tokens below the family floor | minor (review flag) |
| Game the private set by tuning on it | private ids not retrievable; evaluated separately | structural |

### 6.7 Failure path

| Failure | Mechanic | Result |
|---|---|---|
| No goldens / fixtures missing | `E_EVAL_EMPTY` | no score is produced; promotion blocked |
| Missing runs | `E_EVAL_INCOMPLETE` | evaluation refuses; no partial comparison |
| Unknown golden id | `E_EVAL_UNKNOWN_GOLDEN` | refuses |
| Both arms mixed | `E_EVAL_ARM_MISMATCH` | refuses |
| Critical hack flag | verdict `reject` | promotion blocked; incident review |
| Unsafe effect or regression | verdict `reject` | if already active, Example 5 rollback |
| CI overlaps zero | verdict `hold` | honest null result; retrieval/skills stay off by default |
| App/model/catalogue changed | baseline label changes | never compared silently; new baseline required |

### 6.8 VERIFIED vs PROPOSED

| Claim | Label | Source / status |
|---|---|---|
| Golden split 36 public / 14 private, metrics, A/B protocol, anti-hack list, regression gates | `[R]` | 04 §9.1–9.5 |
| No fine-tuning/RL in Phases 0–2; gate-optimised RL produces gate-passing art | `[R]` | 04 D10, §8.6 |
| The Python sketch compiles; Wilson/Newcombe, reward, contamination and empty-set paths ran in the scratch harness | `[V]` (this task) | `py_compile` exit 0; 8/8 Example-6 checks passed |
| The 50-golden corpus exists | `[U]` | **It does not.** 04 §15/§9.1 specify it; no fixtures are frozen yet |
| Any measured lift from retrieval or skills | `[U]` | Not measured; null result is a valid and expected early outcome |
| Threshold-hugging constants (1%, 20%) | `[I]` | Proposed review flags; tune on real gate distributions |
| Newcombe interval assumptions (independent runs) | `[I]` | Runs are not strictly independent; treat CI as a diagnostic, not proof |
| RL on weights / reward models | `[U]` | Not planned; no corpus, no reward model, no training stack |

---

## 7. How the six examples compose

| Example | Consumes | Produces | Used by |
|---|---|---|---|
| 1 Supervisor | `PlanNode`, `Budget`, specialists | `Handoff` rows, `EpisodeResult`, verdict codes | operator/console; ledger close |
| 2 Gateway | registry, pinned catalogue, role token | `ToolSuccess` / `Refusal`, `forge_tool_call` | operators, verifier, critic render calls |
| 3 Ledger | episode close, retrieval query | chained events, case index, retrieval receipt | 1 (events), 5 (promotion evidence), 6 (run records) |
| 4 Critic | renders, brief, rubric, diagnostics | grounded `CritiqueReport` | 1 (verdict), 3 (evidence), 5 (quality evidence) |
| 5 Promotion | evidence, goldens, sign-off, pin | active skill version / rollback | 1 (skill_pin), 6 (policy arm) |
| 6 Eval | goldens, run records | `EvalReport`, promote/hold/reject | 5 (promotion gate), 2 (regression fixtures) |

Traced once end to end:

```text
brief → TaskEnvelope → [1] plan/dispatch → [2] gateway executes craft CLI
      → [3] events + artifacts + gate report → [4] blind critique
      → [1] arbitration → [3] close episode/case
      → [6] evaluate arms → [5] promote/rollback → next episode retrieves the case/skill
```

Every arrow is a stored record with a hash, not a message in memory. That is the difference
between a loop that can be audited and one that can only be demoed.

---

## 8. What would make these production-ready

The sketches are mechanism examples. Turning them into production requires, in this order:

1. **Migrations + integration tests against PostgreSQL 16** — chain append/verify, queue
   claim/lease, unique indexes, transaction boundaries, rollback drill.
2. **Contract versioning + JSON Schema** for `Handoff`, `ToolSuccess/Refusal`, `GateReport`,
   `CritiqueReport`, `Skill`, `EvalReport`; a schema registry with backward-compatibility tests.
3. **Real CLI probes** — 20 commands per installed app; capture stdout/stderr envelopes; replace
   the sketch's assumed `{"artifact": …}` shape where it is wrong; replace 127-shims.
4. **Failure injection** — timeout, signal, partial write, disk full, DB restart, concurrent
   promotion, corrupted chain, private-set leakage; assert the named refusal, not a crash.
5. **AuthN/Z** — role tokens, approval tokens bound to artifact hashes, no secrets in logs/argv.
6. **Observability** — episode/handoff/tool_call correlation ids, refusal-code metrics, queue
   age, budget burn, critic flip rate.
7. **Human rubric + inter-rater study** — the taste rung cannot be fabricated from gates.
8. **Load/resource test on the 2-vCPU host** — global craft semaphore = 1, ≤2 episodes,
   model-call cap; measure wall time and memory before raising limits.
9. **Backup/restore + rollback exercise** — restore to a scratch DB and replay three episodes.
10. **Honest baseline** — run the 50 goldens once before any "learning" claim; publish the null
    result if that is what the data says.

---

## 9. Unverified items (must stay unverified until the named check is run)

| Item | Why it is unverified | Cheapest check |
|---|---|---|
| Real Craft CLI JSON envelope | Sketch assumes `{"artifact": …}` lines | Snapshot 20 commands on 0.21.1/0.20.2 |
| PostgreSQL SQL in Examples 3/5 | No Forge DB exists | Scratch DB + migrations + tests |
| Chain hashing across `jsonb` normalisation | Driver round-trip may change numbers | Store canonical text; property test |
| Vision quality on print defects | No labelled corpus | 50-defect corpus; precision/recall |
| Critic semantic grounding | Schema checks geometry, not meaning | Human audit of 100 crop citations |
| `effective_confidence` constants | Proposed guard | Calibration study on the defect corpus |
| Retrieval lift | No 50-golden corpus | Freeze goldens; A/B with CI |
| Promotion of real skills | No evidence exists | 3 independent accepted episodes |
| Lease/deadline values | Proposed | Load test on the host |
| Any "learning" claim | Not measured | Persistent held-out gain that survives rollback |

No number in this file is presented as measured unless it is in the VERIFIED column of its
section. Everything else is design.
