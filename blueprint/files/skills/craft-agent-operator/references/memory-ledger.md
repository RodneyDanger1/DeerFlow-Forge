# Experience Ledger and promotion rules

**Status:** proposed schema and policy. It is not deployed in `pod_pipeline` yet. Do not claim that
these tables exist until a migration, tests and a read-back are present.

## Why it exists

The current pipeline records runs and steps but does not answer: *what did the agent learn from this
run, and should it be reused?* The ledger makes experience explicit, auditable and reversible.

## Tables

```sql
CREATE TABLE agent_episode (
  id                uuid PRIMARY KEY,
  account_id        bigint NOT NULL,
  brief             text NOT NULL,
  task_family       text NOT NULL,
  apps              jsonb NOT NULL,          -- [{name, version}]
  rights            jsonb NOT NULL,          -- source, licence, notes
  plan              jsonb NOT NULL,
  status            text NOT NULL,           -- planned|executing|verified|failed|refused
  failure_code      text,
  cost              jsonb NOT NULL DEFAULT '{}'::jsonb,
  started_at        timestamptz NOT NULL DEFAULT now(),
  finished_at       timestamptz
);

CREATE TABLE agent_action (
  id                bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  episode_id        uuid NOT NULL REFERENCES agent_episode(id) ON DELETE CASCADE,
  seq               integer NOT NULL,
  tool              text NOT NULL,
  params            jsonb NOT NULL,
  result            jsonb,
  error             jsonb,
  duration_ms       integer,
  UNIQUE (episode_id, seq)
);

CREATE TABLE agent_artifact (
  id                bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  episode_id        uuid NOT NULL REFERENCES agent_episode(id) ON DELETE CASCADE,
  kind              text NOT NULL,           -- input|svg|raster|pdf|report|preview
  path              text NOT NULL,
  sha256            text NOT NULL,
  width             integer,
  height            integer,
  dpi               integer,
  format            text,
  gate_report       jsonb
);

CREATE TABLE agent_eval (
  id                bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  episode_id        uuid NOT NULL REFERENCES agent_episode(id) ON DELETE CASCADE,
  technical         jsonb NOT NULL,          -- gates, dimensions, colourspace
  human             jsonb,                   -- rubric scores, reviewer, notes
  verdict           text NOT NULL,           -- pass|fail|needs_human
  created_at        timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE agent_lesson (
  id                uuid PRIMARY KEY,
  scope             text NOT NULL,           -- app/task_family/brand/global
  task_family       text NOT NULL,
  content           text NOT NULL,           -- the candidate rule, with conditions
  evidence          uuid[] NOT NULL,         -- episode ids
  success_count     integer NOT NULL DEFAULT 0,
  failure_count     integer NOT NULL DEFAULT 0,
  confidence        numeric(4,3) NOT NULL DEFAULT 0,
  version           integer NOT NULL DEFAULT 1,
  status            text NOT NULL,           -- draft|candidate|active|superseded|rejected
  superseded_by     uuid,
  created_at        timestamptz NOT NULL DEFAULT now(),
  promoted_at       timestamptz
);

CREATE TABLE agent_skill (
  id                uuid PRIMARY KEY,
  name              text NOT NULL,
  version           integer NOT NULL,
  app               text NOT NULL,
  preconditions     jsonb NOT NULL,
  steps             jsonb NOT NULL,
  gates             jsonb NOT NULL,
  success_count     integer NOT NULL DEFAULT 0,
  failure_count     integer NOT NULL DEFAULT 0,
  status            text NOT NULL,           -- draft|candidate|active|rolled_back
  created_at        timestamptz NOT NULL DEFAULT now(),
  UNIQUE (name, version)
);
```

## Indexes / retrieval

```sql
CREATE INDEX agent_episode_lookup ON agent_episode (task_family, status, started_at DESC);
CREATE INDEX agent_action_episode ON agent_action (episode_id, seq);
CREATE INDEX agent_lesson_lookup ON agent_lesson (task_family, status, confidence DESC);
```

Initial retrieval can be lexical/metadata; add embeddings only after a measured baseline. Suggested
query shape:

```sql
SELECT id, brief, task_family, status, finished_at
FROM agent_episode
WHERE task_family = $1
  AND status IN ('verified','failed')
ORDER BY finished_at DESC
LIMIT 20;
```

Then rank by: same app/version, same brand/template, similar failure code, gate success, recency.
Return a bounded summary plus episode IDs, not the whole trace.

## Promotion policy

| Transition | Requirement |
|---|---|
| `draft → candidate` | One verified episode with the lesson; explicit conditions |
| `candidate → active` | Calibrated evaluation horizon + Wilson lower bound above baseline, no golden regression, human approval; ≥3 independent successes is only the minimum sample, not a rule |
| `active → superseded` | New version active; old kept for replay |
| `active → rolled_back` | Failure/regression; notify owner; pin old version |

> **Correction (2026-11-05, execution-wave task-11):** 3/3 successes give a Wilson 95% lower bound of
> **0.4385**, so a `LB > 0.60` rule cannot promote at N=3. The rule must declare a horizon. A simulation
> suggests `n=8, k≥7, LB>p0` as a starting point (3.51% synthetic null promotions, 81.14% retention at
> p=0.90), but this is **not adopted** until the owner picks p0/n and real episodes test it. “2 failures
> in last 20” also false-demoted a 95%-reliable skill 41.22% of the time; choose 2-consecutive/3-in-20
> and test. A 40-golden suite misses ~19.5% of risky skills at 5% regression/golden; size the suite.
> The human gate is load-bearing: a gate-optimising strategy was promoted 85.73% without it vs 0.01%
> with it.

- "Independent" means different inputs/runs, not three attempts of the same file.
- A lesson must state its **scope** and **failure conditions**; a global rule from one brand is invalid.
- Confidence is not a substitute for sample count; store both.
- Human ratings are required for taste claims; gates alone cannot promote “better design.”
- Every promoted skill pins the app/version and command-snapshot hash it was validated against.

## Forgetting / contradiction

- If a newer episode contradicts an active lesson, create a contradiction record; do not silently
  average.
- Expire lessons when the app version changes or the catalogue no longer contains the command.
- Keep deleted/superseded rows for audit; do not hard-delete evidence.

## Failure codes (suggested)

`E_BRIEF_MISSING`, `E_RIGHTS_MISSING`, `E_APP_VERSION`, `E_COMMAND_UNKNOWN`, `E_PARAM_REJECTED`,
`E_ARTIFACT_MISSING`, `E_GATE_FAILED`, `E_UPSCALE_LIMIT`, `E_PUBLISH_NOT_APPROVED`, `E_BUDGET`.

## Honest status

- Tables: **proposed**.
- Retrieval: **proposed**.
- Promotion: **proposed policy**.
- No claim of learned weights or measured improvement until the evaluation harness exists.
