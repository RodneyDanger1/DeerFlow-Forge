# Example 4 — Visual critic: artifact + rendered images + diagnostics + rubric

> Extracted from `wave2/07-EXAMPLES.md` (task-7). Original code/design, validated as recorded there; not production code.

## 4. Example 4 — Visual critic: artifact + rendered images + diagnostics + rubric

### 4.1 What it demonstrates

A critic that is **blind, grounded and bounded**:

- blind: it receives brief, rubric lines and rendered images — never the exit code, gate report,
  operator claim or prior verdict;
- grounded: every scored dimension must cite a crop region that exists in the supplied render
  bundle, with an observation of at least 12 characters; a dimension without evidence is
  rejected by the schema, not tolerated;
- bounded: confidence is model-reported, recorded with an explicit semantics string, capped by
  the amount of grounding, and never presented as a probability that the artifact is correct.

Deterministic diagnostics (coverage, specks, alpha, edge hardness, centring, SSIM) are accepted
as **input data and stored as diagnostics**, but they are deliberately not placed in the prompt
and cannot set the verdict. Metrics measure geometry; the critic judges the brief. Conflating
them is how a harness invents "quality" it cannot see.

### 4.2 Contract

```jsonc
// Critique input (assembled by the verifier; 04 §7.3–7.4)
{
  "episode_id": "uuid",
  "artifact_sha256": "sha256:…",
  "brief_text": "…",
  "renders": [
    {"kind": "thumb_256",  "path": "build/ep/thumb_256.png",  "sha256": "sha256:…", "width": 256,  "height": 320},
    {"kind": "view_1024",  "path": "build/ep/view_1024.png",  "sha256": "sha256:…", "width": 1024, "height": 1280},
    {"kind": "crop_100",   "path": "build/ep/crop_100_3_2.png","sha256": "sha256:…", "width": 600,  "height": 750}
  ],
  "metrics": {"coverage": 0.41, "white_residual": 0.0, "edge_hardness": 0.93},
  "rubric": [
    {"dimension": "brief_fit",  "text": "subject matches the brief", "anchors": ["1=wrong subject", "5=exact subject"]},
    {"dimension": "hierarchy", "text": "wordmark dominates, tagline secondary"},
    {"dimension": "typography", "text": "no clipped or semi-transparent glyphs"},
    {"dimension": "colour",     "text": "palette matches brand facts"},
    {"dimension": "print_safety", "text": "no content in the provider safe-zone margin"}
  ]
}
```

```jsonc
// Stored report (forge_critique; schema-enforced)
{
  "episode_id": "uuid",
  "artifact_sha256": "sha256:…",
  "prompt_version": "critic-v0.3",
  "model_id": "deepseek-flash",
  "blinded_to": ["exit_code", "gate_report", "operator_claims", "prior_verdict"],
  "dimensions": {"brief_fit": {"score": 4, "evidence": [{"region": [0.0,0.0,1.0,1.0],
                  "crop_path": "build/ep/view_1024.png", "observation": "subject centred, wordmark legible"}]}},
  "defects": [{"severity": "minor", "where": "tagline", "issue": "tracking tight", "fix_hint": "+2% tracking"}],
  "confidence_reported": 0.72,
  "confidence_effective": 0.72,
  "confidence_semantics": "model self-report, not calibrated accuracy; never present as certainty",
  "unseen": ["no reference artwork supplied"],
  "verdict": "pass_with_notes",
  "image_hashes": ["sha256:…"],
  "diagnostics": {"coverage": 0.41, "white_residual": 0.0}
}
```

### 4.3 Confidence rules (no fake confidence)

| Rule | Enforcement |
|---|---|
| Confidence is reported, not computed as accuracy | `confidence_reported` stored verbatim; no conversion to "probability correct" |
| Grounding caps confidence | `effective = min(reported, 0.40 + 0.12 × evidence_count)`; a single crop cannot justify 0.95 |
| Low confidence cannot pass | `effective < 0.5` → `unverifiable` → `needs_human` |
| Unknowns are explicit | `unseen` is required; non-empty downgrades `pass` to `pass_with_notes` |
| Stability is measured, not assumed | Repeat calls on identical hashes are recorded; verdict flips become `forge_conflict` (04 §7.4) |
| No gate anchoring | Forbidden keys are rejected; any gate/exit mention in the critique is a schema violation |

### 4.4 Sketch

<!-- Example 4 sketch — validated with py_compile + 9 scratch-harness checks -->
```python
"""Example 4 - visual critic: artifact + rendered images + diagnostics + rubric.

Forge Conductor mechanism sketch (Python 3.11+). Design-only: no model call is
made here. Confidence is model-reported and is never presented as a probability
that the artifact is correct.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Mapping, Protocol, Sequence

CRITIC_PROMPT_VERSION = "critic-v0.3"
DIMENSIONS = ("brief_fit", "hierarchy", "typography", "colour", "print_safety")
VERDICTS = ("pass", "pass_with_notes", "reject", "unverifiable")
SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
FORBIDDEN_INPUT_KEYS = frozenset(
    {"gate_report", "gates", "exit_code", "operator_claims", "prior_verdict", "argv", "stderr"}
)
GATE_MENTION_RE = re.compile(r"(gate_report|exit[_ ]code|gate\s*=|gates?\s*:|white_residual\s*=)", re.I)
MIN_OBSERVATION_CHARS = 12


class CritiqueRefused(Exception):
    def __init__(self, code: str, message: str, how_to_fix: str, evidence: Sequence[str] = ()) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.how_to_fix = how_to_fix
        self.evidence = tuple(evidence)


@dataclass(frozen=True)
class RenderView:
    kind: str
    path: str
    sha256: str
    width: int
    height: int

    def __post_init__(self) -> None:
        if not SHA256_RE.match(self.sha256):
            raise ValueError(f"render hash must be sha256:<64 hex>: {self.sha256!r}")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("render dimensions must be positive")


@dataclass(frozen=True)
class Diagnostics:
    """Deterministic measurements. Diagnostics never certify an artifact."""

    values: Mapping[str, float]

    def __post_init__(self) -> None:
        for key, value in self.values.items():
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValueError(f"diagnostic {key!r} must be numeric")


@dataclass(frozen=True)
class RubricLine:
    dimension: str
    text: str
    anchors: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.dimension not in DIMENSIONS:
            raise ValueError(f"unknown rubric dimension {self.dimension!r}")


@dataclass(frozen=True)
class CritiqueInput:
    episode_id: str
    artifact_sha256: str
    brief_text: str
    renders: tuple[RenderView, ...]
    metrics: Diagnostics
    rubric: tuple[RubricLine, ...]

    def __post_init__(self) -> None:
        if not SHA256_RE.match(self.artifact_sha256):
            raise ValueError("artifact_sha256 must be sha256:<64 hex>")
        if not self.renders:
            raise ValueError("the critic needs at least one rendered view")
        if not self.rubric:
            raise ValueError("the critic needs the rubric lines it must score")
        for line in self.rubric:
            if line.dimension not in DIMENSIONS:
                raise ValueError(f"rubric dimension {line.dimension!r} is not scoreable")


class VisionClient(Protocol):
    model_id: str

    def complete(self, prompt: str, image_paths: Sequence[str], *, timeout_s: int) -> str:
        """Return the raw model text. Raising is a vision failure, not a verdict."""
        ...


@dataclass(frozen=True)
class Defect:
    severity: str
    where: str
    issue: str
    fix_hint: str

    def __post_init__(self) -> None:
        if self.severity not in {"minor", "major"}:
            raise ValueError("severity must be minor or major")


@dataclass(frozen=True)
class CritiqueReport:
    episode_id: str
    artifact_sha256: str
    prompt_version: str
    model_id: str
    blinded_to: tuple[str, ...]
    dimensions: Mapping[str, Mapping[str, Any]]
    defects: tuple[Defect, ...]
    confidence_reported: float
    confidence_effective: float
    confidence_semantics: str
    unseen: tuple[str, ...]
    verdict: str
    decision_reason: str
    image_hashes: tuple[str, ...]
    raw_response_sha256: str
    diagnostics: Mapping[str, float]


def assert_input_blinded(extra: Mapping[str, Any]) -> None:
    leaked = sorted(FORBIDDEN_INPUT_KEYS.intersection(extra))
    if leaked:
        raise CritiqueRefused(
            "E_CRITIQUE_UNBLINDED",
            f"critic input carries forbidden keys: {', '.join(leaked)}",
            "pass only brief, rubric and rendered images; gate results stay in the verifier",
            leaked,
        )


def build_prompt(critique: CritiqueInput, *, retry_note: str | None = None) -> str:
    """Deterministic, versioned prompt. Diagnostics and gates are deliberately absent."""
    rubric = "\n".join(
        f"- {line.dimension}: {line.text}"
        + (f" (anchors: {', '.join(line.anchors)})" if line.anchors else "")
        for line in critique.rubric
    )
    views = "\n".join(f"- {view.kind}: {view.path} ({view.width}x{view.height})" for view in critique.renders)
    retry = f"\nYour previous answer was rejected: {retry_note}. Fix exactly that.\n" if retry_note else ""
    return (
        f"PROMPT_VERSION={CRITIC_PROMPT_VERSION}\n"
        "You are a blind art critic. You do not see exit codes, gate reports or operator claims.\n"
        "Score the rendered artifact against the brief. Every dimension needs quoted crop evidence:\n"
        '{"region":[x0,y0,x1,y1],"crop_path":"<one of the rendered paths>",'
        '"observation":"what you see (>=12 chars)"}.\n'
        f"{retry}\nBRIEF:\n{critique.brief_text}\n\nRUBRIC:\n{rubric}\n\nRENDERED VIEWS:\n{views}\n\n"
        "Reply with one JSON object only. Required keys: dimensions (all five), defects[], "
        "confidence (0..1), unseen[], verdict (pass|pass_with_notes|reject|unverifiable). "
        "Do not mention gate values. If you cannot evaluate a dimension, use verdict unverifiable."
    )


def strip_code_fence(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return stripped


def parse_critique(raw: str) -> dict[str, Any]:
    try:
        parsed = json.loads(strip_code_fence(raw))
    except json.JSONDecodeError as error:
        raise ValueError(f"critique is not JSON: {error.msg} at char {error.pos}") from error
    if not isinstance(parsed, dict):
        raise ValueError("critique must be a JSON object")
    return parsed


def validate_critique(
    payload: Mapping[str, Any], critique: CritiqueInput
) -> list[str]:
    """Return schema violations. An empty list means the report is admissible."""
    violations: list[str] = []
    known_paths = {view.path for view in critique.renders}

    dimensions = payload.get("dimensions")
    if not isinstance(dimensions, dict):
        violations.append("dimensions must be an object")
    else:
        missing = [name for name in DIMENSIONS if name not in dimensions]
        if missing:
            violations.append(f"dimensions missing: {', '.join(missing)}")
        for name in DIMENSIONS:
            entry = dimensions.get(name)
            if not isinstance(entry, dict):
                violations.append(f"dimensions.{name} must be an object")
                continue
            score = entry.get("score")
            if not isinstance(score, int) or isinstance(score, bool) or not 1 <= score <= 5:
                violations.append(f"dimensions.{name}.score must be an int 1..5")
            evidence = entry.get("evidence")
            if not isinstance(evidence, list) or not evidence:
                violations.append(f"dimensions.{name} has no crop evidence")
                continue
            for index, item in enumerate(evidence):
                where = f"dimensions.{name}.evidence[{index}]"
                if not isinstance(item, dict):
                    violations.append(f"{where} must be an object")
                    continue
                region = item.get("region")
                if (
                    not isinstance(region, list)
                    or len(region) != 4
                    or not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in region)
                ):
                    violations.append(f"{where}.region must be four numbers")
                elif not (0.0 <= region[0] < region[2] <= 1.0 and 0.0 <= region[1] < region[3] <= 1.0):
                    violations.append(f"{where}.region is not an ascending box inside [0,1]")
                elif (region[2] - region[0]) * (region[3] - region[1]) <= 0:
                    violations.append(f"{where}.region has zero area")
                crop = item.get("crop_path")
                if crop not in known_paths:
                    violations.append(f"{where}.crop_path is not one of the rendered views")
                observation = item.get("observation")
                if not isinstance(observation, str) or len(observation.strip()) < MIN_OBSERVATION_CHARS:
                    violations.append(f"{where}.observation must be at least {MIN_OBSERVATION_CHARS} chars")

    defects_raw = payload.get("defects")
    defects: list[Defect] = []
    if not isinstance(defects_raw, list):
        violations.append("defects must be a list")
    else:
        for index, item in enumerate(defects_raw):
            if not isinstance(item, dict):
                violations.append(f"defects[{index}] must be an object")
                continue
            try:
                defects.append(
                    Defect(
                        severity=str(item.get("severity", "")),
                        where=str(item.get("where", "")),
                        issue=str(item.get("issue", "")),
                        fix_hint=str(item.get("fix_hint", "")),
                    )
                )
            except ValueError as error:
                violations.append(f"defects[{index}]: {error}")

    verdict = payload.get("verdict")
    if verdict not in VERDICTS:
        violations.append(f"verdict must be one of {', '.join(VERDICTS)}")
    elif verdict == "pass" and any(defect.severity == "major" for defect in defects):
        violations.append("verdict pass is invalid with a major defect")

    unseen = payload.get("unseen")
    if not isinstance(unseen, list) or not all(isinstance(item, str) for item in unseen):
        violations.append("unseen must be a list of strings (may be empty)")

    confidence = payload.get("confidence")
    if (
        not isinstance(confidence, (int, float))
        or isinstance(confidence, bool)
        or not 0.0 <= float(confidence) <= 1.0
    ):
        violations.append("confidence must be a number in [0,1]")

    serialized = json.dumps(payload, sort_keys=True).lower()
    if GATE_MENTION_RE.search(serialized):
        violations.append("critique mentions a gate/exit value; the critic must stay blind")
    return violations


def effective_confidence(reported: float, evidence_count: int) -> float:
    """Cap model confidence by grounding: one crop cannot justify near-certainty."""
    cap = 0.40 + 0.12 * min(evidence_count, 5)
    return round(min(reported, cap), 3)


def decide(payload: Mapping[str, Any], confidence: float) -> tuple[str, str]:
    verdict = str(payload.get("verdict", "unverifiable"))
    major = any(
        isinstance(item, Mapping) and item.get("severity") == "major"
        for item in payload.get("defects", [])
    )
    if verdict == "reject" or major:
        return "reject", "E_CRITIQUE_REJECT"
    if verdict == "unverifiable":
        return "unverifiable", "E_CRITIQUE_UNVERIFIABLE"
    if confidence < 0.5:
        return "unverifiable", "E_CRITIQUE_LOW_CONFIDENCE"
    if verdict == "pass" and payload.get("unseen"):
        return "pass_with_notes", "PASS_DOWNGRADED_BY_UNSEEN"
    return "pass", "OK"


def evaluate(
    client: VisionClient,
    critique: CritiqueInput,
    *,
    timeout_s: int = 120,
) -> CritiqueReport:
    """Two attempts maximum. A refused critique is a refusal, never a pass."""
    prompt = build_prompt(critique)
    last_violations: list[str] = []
    for attempt in (1, 2):
        try:
            raw = client.complete(prompt, [view.path for view in critique.renders], timeout_s=timeout_s)
        except Exception as error:
            raise CritiqueRefused(
                "E_VISION_UNAVAILABLE",
                f"vision call failed: {type(error).__name__}",
                "retry once with the same prompt version; then route to needs_human",
            ) from error
        if not raw.strip():
            last_violations = ["vision returned empty text"]
        else:
            try:
                payload = parse_critique(raw)
            except ValueError as error:
                last_violations = [str(error)]
                payload = {}
            if payload:
                last_violations = validate_critique(payload, critique)
                if not last_violations:
                    evidence_count = sum(
                        len(entry.get("evidence", []))
                        for entry in payload.get("dimensions", {}).values()
                        if isinstance(entry, Mapping) and isinstance(entry.get("evidence"), list)
                    )
                    reported = float(payload["confidence"])
                    confidence = effective_confidence(reported, evidence_count)
                    verdict, reason = decide(payload, confidence)
                    dimensions = {
                        name: payload["dimensions"][name] for name in DIMENSIONS
                    }
                    return CritiqueReport(
                        episode_id=critique.episode_id,
                        artifact_sha256=critique.artifact_sha256,
                        prompt_version=CRITIC_PROMPT_VERSION,
                        model_id=client.model_id,
                        blinded_to=("exit_code", "gate_report", "operator_claims", "prior_verdict"),
                        dimensions=dimensions,
                        defects=tuple(
                            Defect(
                                severity=str(item["severity"]),
                                where=str(item["where"]),
                                issue=str(item["issue"]),
                                fix_hint=str(item.get("fix_hint", "")),
                            )
                            for item in payload.get("defects", [])
                        ),
                        confidence_reported=reported,
                        confidence_effective=confidence,
                        confidence_semantics="model self-report, not calibrated accuracy; never present as certainty",
                        unseen=tuple(str(item) for item in payload.get("unseen", [])),
                        verdict=verdict,
                        decision_reason=reason,
                        image_hashes=tuple(view.sha256 for view in critique.renders),
                        raw_response_sha256="sha256:" + sha256(raw.encode("utf-8")).hexdigest(),
                        diagnostics=dict(critique.metrics.values),
                    )
        if attempt == 1:
            prompt = build_prompt(critique, retry_note="; ".join(last_violations)[:400])
    raise CritiqueRefused(
        "E_CRITIQUE_UNGROUNDED",
        "critique failed schema/grounding validation after one retry",
        "fix the critic prompt or schema; do not accept an ungrounded critique",
        last_violations[:10],
    )
```

### 4.5 Inputs and outputs

| Direction | Value |
|---|---|
| In | `CritiqueInput` (artifact hash, brief, renders, diagnostics, rubric); a `VisionClient` |
| Out | `CritiqueReport` with per-dimension grounded evidence, defects, reported + effective confidence, unseen, verdict, image hashes, raw-response hash |
| Not sent to the model | diagnostics, gates, exit codes, operator claims, prior verdicts |
| On refusal | `CritiqueRefused(code, message, how_to_fix, evidence)` — never a fabricated pass |

### 4.6 Failure path

| Failure | Mechanic | Result |
|---|---|---|
| Input carries gate/exit/operator keys | `assert_input_blinded` | `E_CRITIQUE_UNBLINDED` |
| Vision call raises/times out/returns empty | first attempt retried once | `E_VISION_UNAVAILABLE` → `needs_human` |
| Malformed JSON | parse error becomes retry note | second failure → `E_CRITIQUE_UNGROUNDED` |
| Dimension missing evidence, crop path unknown, zero-area region, short observation | schema violations | retry once with violations; second failure → `E_CRITIQUE_UNGROUNDED` |
| `pass` with a major defect | schema violation | rejected, retried once |
| Critic mentions a gate/exit value | regex violation | `E_CRITIQUE_UNGROUNDED` |
| Confidence < 0.5 | decision rule | `unverifiable` (no silent pass) |
| `pass` with non-empty `unseen` | decision rule | `pass_with_notes` |
| Model returns `reject` / `unverifiable` | decision rule | propagate; conductor arbitrates |
| Two identical-input calls disagree | not handled here | recorded as conflict and measured; a single call is never treated as stable |

### 4.7 VERIFIED vs PROPOSED

| Claim | Label | Source / status |
|---|---|---|
| Render ladder, critic protocol, schema rejection rules, confidence < 0.5 → human | `[R]` | 04 §7.3–7.4 |
| `deepseek-flash` is configured with `supports_vision: true` | `[V]` | 04 §2.2 (host config) |
| Vision quality on print defects is not measured | `[U]` | 04 §15 lists this as an open unknown; no labelled defect corpus exists |
| The Python sketch compiles and its pass/retry/refusal/low-confidence paths ran in the scratch harness | `[V]` (this task) | `py_compile` exit 0; 9/9 Example-4 checks passed |
| `effective_confidence` cap constants | `[I]` | Proposed calibration guard; must be tested against the 50-defect corpus, not believed |
| Crop regions are semantically grounded (the model didn't hallucinate a box that happens to exist) | `[U]` | The schema checks existence and geometry only; semantic grounding needs a human-labelled audit |
| Multiple images per call and resolution limits for this model | `[U]` | Not probed; 04 §15 requires an API probe before the render ladder is final |
| Critic prompt version `critic-v0.3` | `[R]` | Named in 04; not executed |

---
