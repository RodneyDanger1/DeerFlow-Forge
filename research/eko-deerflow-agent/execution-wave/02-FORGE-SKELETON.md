# Forge Conductor — Executable Skeleton Contract

**Execution Wave · Task 09 · Design → DDL → tested skeleton · 2026-11-05**
Owner: Riley · Author: harness-architect · Input: `wave2/04-HARNESS-DESIGN.md` · Status: **skeleton contract, not a deployed service**

> **What this is.** The Wave 2 design converted into three artefacts that actually execute:
> a Postgres schema that applies and enforces the invariants, a reference tool gateway that
> compiles and passes tests, and shared TypeScript contracts that type-check. Everything was run
> during this task; nothing was installed, migrated or edited in production.
>
> **What this is not.** Not a service, not a deployment, not a migration, and not a claim that any
> Craft command was executed. The `pod` database, `pod_pipeline`, the console and the Craft apps
> were not touched. No production file was modified. The skeleton runs only against a throwaway
> database that was created and dropped for this task.

**Evidence labels:** `[RUN]` executed in this task with output quoted in §10 · `[READ]` read from the
repo and cited by path · `[DESIGN]` carried over from `wave2/04` as an unexecuted design statement ·
`[GAP]` unresolved; listed in §11.

---

## 1. What "executable" means here

| Artefact | Form | Proof it runs | Lines |
|---|---|---|---|
| Postgres DDL (`forge` schema) | `forge_schema.sql` embedded in §3 | Applied twice to a real PostgreSQL 16.15 scratch DB; second apply is clean; 18 assertions pass; two-worker `SKIP LOCKED` claim does not block | 663 |
| Tool gateway reference | Python 3.14, stdlib only, embedded in §7 | `py_compile` clean; **33/33** unit tests pass | 310 |
| Gateway tests | `unittest`, embedded in §8.5 | same run as above | 255 |
| Wire contracts | TypeScript declarations embedded in §9 | `tsc --noEmit --strict` exit 0; a negative check (required field removed) fails with `TS2741` | 217 + 132 |

Three properties are *proved by test*, not asserted: illegal state changes are refused, a duplicate
idempotency key never executes twice, and every transition is appended to a hash-chained log that
detects forgery.

---

## 2. Scope and deltas from the Wave 1 design

The design proposed 18 tables. The skeleton ships **13 that execute today**, chosen so that the
ledger, queue, handoff, evidence and promotion-guard invariants are all enforceable:

| Shipped | Deferred to a later task | Why deferred |
|---|---|---|
| `forge_transition`, `forge_episode`, `forge_event`, `forge_handoff`, `forge_tool_call`, `forge_artifact`, `forge_gate`, `forge_critique`, `forge_eval`, `forge_job`, `forge_skill`, `forge_budget_ledger`, `forge_approval` | `forge_brand_fact`, `forge_episode_case`, `forge_retrieval`, `forge_lesson`, `forge_conflict`, `forge_role_token` | Retrieval/facts/lessons are Phase 2–3 per `04` §8; the role token table belongs to the auth task and is out of scope for a schema skeleton |
| Arbitration outcome as `forge_episode.verdict` + `reason_codes` | separate `forge_resolution` table | Two columns express the same fact without a join; promote only if resolution history is needed per artifact |
| `forge_approval` added | — | The design named approval tokens but had no table; single-use approval must be enforced by the database, not by convention |

**Corrections found by making it executable** (each would have been a silent design defect):

1. **`quarantined` is terminal.** The design sketch allowed `quarantined → cancelled`, which
   contradicts "terminal state" semantics. The Python test `test_terminal_states_have_no_outgoing_edges`
   failed on the first run; the edge was removed and the seeded table corrected to **36 edges**.
2. **Every transition must append an event.** The design said transitions write evidence; the first
   executable version of `forge_transition_episode` did not, and `T02` caught it (`expected 1 event,
   got 0`). The function now appends `episode.transition` inside the same transaction.
3. **Accepted episodes require a positive verdict.** Enforced twice: a table `CHECK` and a guarded
   function, so `accepted` can never exist without `pass`/`pass_with_notes`.

**Explicit non-claims:** the guard *labels* in `forge_transition` are documentation of conductor
preconditions; the database enforces **topology**, not their truth. Semantic guards (brief complete,
retrieval receipt present, locks held) are the conductor's job and are tested only as pure functions
in §8. This is recorded as `[GAP]` G-03.

---

## 3. DDL — exact schema, apply order and invariants

Apply with a role that owns the database:

```bash
psql -v ON_ERROR_STOP=1 -d <scratch_db> -f forge_schema.sql
```

Properties, all exercised in §10:

- **Idempotent re-apply.** `CREATE TABLE IF NOT EXISTS`, `CREATE OR REPLACE FUNCTION`, `DROP TRIGGER
  IF EXISTS` + `CREATE TRIGGER`; seeding uses `ON CONFLICT DO NOTHING`. Second apply exits 0.
- **Requires `pgcrypto`** for `digest()` (hash chain) and `gen_random_uuid()`.
- **Append-only evidence.** `forge_event`, `forge_artifact`, `forge_gate`, `forge_critique`,
  `forge_eval` carry a `BEFORE UPDATE OR DELETE` trigger raising SQLSTATE `42501`
  (`E_APPEND_ONLY`). A report query (`forge_immutability_report()`) proves coverage.
- **One writer per episode chain.** `forge_append_event()` takes
  `pg_advisory_xact_lock(hashtext('forge_event:'||episode))` and computes `prev_hash`/`hash` from
  `(episode_id, seq, kind, payload::text, prev_hash)`; `forge_verify_event_chain()` recomputes it.
- **No duplicate execution.** `forge_tool_call.idempotency_key` is `UNIQUE` with a shape check
  (`^sha256:[0-9a-f]{64}$`); `forge_replay_tool_call(key)` returns the stored row.
- **No duplicate promotion.** Partial unique index `forge_skill_one_active ON forge_skill(skill_id)
  WHERE status='active'`, plus `PRIMARY KEY (skill_id, version)`.
- **Queue correctness.** `forge_claim_job()` uses `FOR UPDATE SKIP LOCKED`, sets `lease_until` and
  increments `attempts`; empty queue returns `NULL` (never an error).
- **Human approval is single-use and hash-bound.** `forge_consume_approval()` updates only an unused,
  unexpired row for the exact `(episode, artifact_sha256, scope)` and raises
  `E_PUBLISH_NOT_APPROVED` otherwise.
- **Budget cap aborts the transaction.** `forge_charge()` raises `E_BUDGET_EXCEEDED` after the update,
  so the charge rolls back with the transaction (proved by `T12`).

Grants are **commented**, not applied: the role must be created by the database owner, and creating
cluster roles on a shared production cluster was deliberately not done. That is `[GAP]` G-04.

**File: ```forge_schema.sql```**

```sql
-- Forge Conductor skeleton DDL - executable contract (PostgreSQL 16)
-- Section map: 0 extensions, 1 schema, 2 reference transitions, 3 helpers,
-- 4 episode, 5 handoff, 6 tool_call, 7 artifact/gate/critique/eval,
-- 8 job queue, 9 skill, 10 budget, 11 approval, 12 verification hooks.
--
-- Design rules encoded here:
--   * append-only evidence tables refuse UPDATE/DELETE (SQLSTATE 42501)
--   * no side effect without an idempotency key and a unique index
--   * every state change goes through a guarded function, never a bare UPDATE
--   * all refusals are named E_* errors raised by the database, not by callers
--
-- Re-applying this file is safe (IF NOT EXISTS / OR REPLACE / DROP TRIGGER IF EXISTS).

-- ---------------------------------------------------------------- 0 extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;   -- digest(), gen_random_uuid()

-- ------------------------------------------------------------------- 1 schema
CREATE SCHEMA IF NOT EXISTS forge;
SET search_path = forge, public;

-- ------------------------------------------------- 2 state reference data
CREATE TABLE IF NOT EXISTS forge_transition (
    from_state text NOT NULL,
    to_state   text NOT NULL,
    guard      text NOT NULL,
    terminal   boolean NOT NULL DEFAULT false,
    PRIMARY KEY (from_state, to_state),
    CONSTRAINT forge_transition_states CHECK (
        from_state IN ('intake','briefed','planned','context_ready','executing',
                       'verifying','critiquing','needs_human','paused','accepted',
                       'rejected','refused','failed','cancelled','quarantined')
        AND to_state IN ('intake','briefed','planned','context_ready','executing',
                         'verifying','critiquing','needs_human','paused','accepted',
                         'rejected','refused','failed','cancelled','quarantined')
    )
);

INSERT INTO forge_transition (from_state, to_state, guard, terminal) VALUES
  ('intake',        'briefed',        'deliverable_target_rights', false),
  ('intake',        'refused',        'brief_missing',             true),
  ('intake',        'cancelled',      'owner_cancelled',           true),
  ('briefed',       'planned',        'artspec_cited',             false),
  ('briefed',       'needs_human',    'brief_ambiguous',           false),
  ('briefed',       'refused',        'rights_missing',            true),
  ('briefed',       'cancelled',      'owner_cancelled',           true),
  ('planned',       'context_ready',  'retrieval_receipt',         false),
  ('planned',       'needs_human',    'spec_disputed',             false),
  ('planned',       'failed',         'planning_failed',           true),
  ('planned',       'refused',        'unsupported_surface',       true),
  ('context_ready', 'executing',      'locks_budget',              false),
  ('context_ready', 'needs_human',    'context_insufficient',      false),
  ('context_ready', 'refused',        'budget_exceeded',           true),
  ('context_ready', 'cancelled',      'owner_cancelled',           true),
  ('executing',     'verifying',      'handoff_artifacts',         false),
  ('executing',     'paused',         'human_pause',               false),
  ('executing',     'failed',         'execution_failed',          true),
  ('executing',     'needs_human',    'tool_refused_human',        false),
  ('executing',     'quarantined',    'source_mutated',            true),
  ('executing',     'cancelled',      'owner_cancelled',           true),
  ('verifying',     'critiquing',     'rungs_1_4_green',           false),
  ('verifying',     'rejected',       'gate_failed',               true),
  ('verifying',     'needs_human',    'gate_missing',              false),
  ('verifying',     'failed',         'verify_crashed',            true),
  ('critiquing',    'accepted',       'verdict_rules_human',       true),
  ('critiquing',    'rejected',       'critic_reject',             true),
  ('critiquing',    'needs_human',    'critic_disagrees',          false),
  ('critiquing',    'failed',         'critic_unavailable',        true),
  ('needs_human',   'accepted',       'human_approved',            true),
  ('needs_human',   'rejected',       'human_rejected',            true),
  ('needs_human',   'paused',         'human_paused',              false),
  ('needs_human',   'cancelled',      'owner_cancelled',           true),
  ('paused',        'executing',      'human_resumed',             false),
  ('paused',        'needs_human',    'human_escalated',           false),
  ('paused',        'cancelled',      'owner_cancelled',           true)
ON CONFLICT (from_state, to_state) DO NOTHING;

-- ---------------------------------------------------------------- 3 helpers
CREATE OR REPLACE FUNCTION forge_touch_updated_at() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at := now();
    RETURN NEW;
END;
$$;

-- Append-only guard: evidence rows are never rewritten or deleted.
CREATE OR REPLACE FUNCTION forge_refuse_mutation() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'E_APPEND_ONLY: % refused on %', TG_OP, TG_TABLE_NAME
        USING ERRCODE = '42501', HINT = 'evidence is immutable; append a new row instead';
END;
$$;

CREATE OR REPLACE FUNCTION forge_can_transition(p_from text, p_to text)
RETURNS boolean LANGUAGE sql STABLE AS $$
    SELECT EXISTS (SELECT 1 FROM forge_transition
                   WHERE from_state = p_from AND to_state = p_to);
$$;

-- ---------------------------------------------------------------- 4 episode
CREATE TABLE IF NOT EXISTS forge_episode (
    id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    idempotency_key   text UNIQUE,
    account_id        bigint NOT NULL,
    brief             text NOT NULL,
    task_family       text NOT NULL,
    mode              text NOT NULL DEFAULT 'assisted'
                      CHECK (mode IN ('assisted','replay','draft')),
    status            text NOT NULL DEFAULT 'intake'
                      CHECK (status IN ('intake','briefed','planned','context_ready','executing',
                                        'verifying','critiquing','needs_human','paused','accepted',
                                        'rejected','refused','failed','cancelled','quarantined')),
    verdict           text
                      CHECK (verdict IS NULL OR verdict IN ('pass','pass_with_notes','reject',
                                                            'needs_human','unverified')),
    reason_codes      text[] NOT NULL DEFAULT '{}',
    apps              jsonb  NOT NULL DEFAULT '[]'::jsonb,
    rights            jsonb  NOT NULL DEFAULT '{}'::jsonb,
    plan              jsonb  NOT NULL DEFAULT '{}'::jsonb,
    budget            jsonb  NOT NULL DEFAULT '{}'::jsonb,
    cost              jsonb  NOT NULL DEFAULT '{}'::jsonb,
    skill_pin         jsonb,
    catalogue_hash    text CHECK (catalogue_hash IS NULL OR catalogue_hash ~ '^sha256:[0-9a-f]{64}$'),
    human_required    boolean NOT NULL DEFAULT false,
    created_at        timestamptz NOT NULL DEFAULT now(),
    updated_at        timestamptz NOT NULL DEFAULT now(),
    finished_at       timestamptz,
    CONSTRAINT forge_episode_brief CHECK (char_length(brief) BETWEEN 1 AND 32768),
    CONSTRAINT forge_episode_reasons CHECK (array_length(reason_codes, 1) IS NULL
                                            OR array_length(reason_codes, 1) <= 32),
    CONSTRAINT forge_episode_accepted_verdict CHECK (
        status <> 'accepted' OR verdict IN ('pass','pass_with_notes')
    ),
    CONSTRAINT forge_episode_finished CHECK (
        finished_at IS NULL OR finished_at >= created_at
    )
);

CREATE INDEX IF NOT EXISTS forge_episode_lookup
    ON forge_episode (task_family, status, created_at DESC);
CREATE INDEX IF NOT EXISTS forge_episode_account
    ON forge_episode (account_id, created_at DESC);

DROP TRIGGER IF EXISTS forge_episode_touch ON forge_episode;
CREATE TRIGGER forge_episode_touch BEFORE UPDATE ON forge_episode
    FOR EACH ROW EXECUTE FUNCTION forge_touch_updated_at();

-- Guarded transition. The only legal way to change episode status.
CREATE OR REPLACE FUNCTION forge_transition_episode(
    p_episode uuid,
    p_to      text,
    p_verdict text DEFAULT NULL,
    p_reason  text[] DEFAULT '{}'
) RETURNS forge_episode
LANGUAGE plpgsql AS $$
DECLARE
    v_old  forge_episode;
    v_new  forge_episode;
    v_term boolean;
BEGIN
    SELECT * INTO v_old FROM forge_episode WHERE id = p_episode FOR UPDATE;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'E_EPISODE_NOT_FOUND: %', p_episode USING ERRCODE = 'P0002';
    END IF;
    IF NOT forge_can_transition(v_old.status, p_to) THEN
        RAISE EXCEPTION 'E_TRANSITION_ILLEGAL: % -> %', v_old.status, p_to
            USING ERRCODE = 'P0001';
    END IF;
    IF p_to = 'accepted'
       AND coalesce(p_verdict, v_old.verdict) IS NULL THEN
        RAISE EXCEPTION 'E_VERDICT_MISSING: accepted requires a verdict'
            USING ERRCODE = 'P0001';
    END IF;
    IF p_to = 'accepted'
       AND coalesce(p_verdict, v_old.verdict) NOT IN ('pass','pass_with_notes') THEN
        RAISE EXCEPTION 'E_VERDICT_INVALID: % cannot be accepted', coalesce(p_verdict, v_old.verdict)
            USING ERRCODE = 'P0001';
    END IF;

    SELECT terminal INTO v_term FROM forge_transition
     WHERE from_state = v_old.status AND to_state = p_to;

    UPDATE forge_episode
       SET status       = p_to,
           verdict      = coalesce(p_verdict, verdict),
           reason_codes = CASE WHEN array_length(p_reason,1) IS NULL
                               THEN reason_codes ELSE p_reason END,
           finished_at  = CASE WHEN v_term THEN now() ELSE finished_at END,
           updated_at   = now()
     WHERE id = p_episode
     RETURNING * INTO v_new;

    -- every transition is evidence; the chain records from/to/verdict/reasons
    PERFORM forge_append_event(
        p_episode, 'episode.transition',
        jsonb_build_object(
            'from',    v_old.status,
            'to',      p_to,
            'verdict', coalesce(p_verdict, v_old.verdict),
            'reasons', to_jsonb(coalesce(p_reason, '{}'::text[]))
        )
    );

    RETURN v_new;
END;
$$;

-- Hash-chained append-only event log. canonicalisation = PostgreSQL 16 jsonb text.
CREATE TABLE IF NOT EXISTS forge_event (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    episode_id  uuid NOT NULL REFERENCES forge_episode(id) ON DELETE RESTRICT,
    seq         integer NOT NULL CHECK (seq >= 1),
    kind        text NOT NULL CHECK (char_length(kind) BETWEEN 1 AND 64),
    payload     jsonb NOT NULL DEFAULT '{}'::jsonb,
    prev_hash   text NOT NULL CHECK (prev_hash ~ '^[0-9a-f]{64}$'),
    hash        text NOT NULL CHECK (hash ~ '^[0-9a-f]{64}$'),
    created_at  timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT forge_event_seq UNIQUE (episode_id, seq),
    CONSTRAINT forge_event_payload_size CHECK (octet_length(payload::text) <= 32768)
);

CREATE INDEX IF NOT EXISTS forge_event_episode ON forge_event (episode_id, seq);

DROP TRIGGER IF EXISTS forge_event_append_only ON forge_event;
CREATE TRIGGER forge_event_append_only BEFORE UPDATE OR DELETE ON forge_event
    FOR EACH ROW EXECUTE FUNCTION forge_refuse_mutation();

CREATE OR REPLACE FUNCTION forge_append_event(
    p_episode uuid,
    p_kind    text,
    p_payload jsonb
) RETURNS forge_event
LANGUAGE plpgsql AS $$
DECLARE
    v_seq  integer;
    v_prev text;
    v_row  forge_event;
BEGIN
    -- one writer per episode chain; avoids seq races inside a transaction boundary
    PERFORM pg_advisory_xact_lock(hashtext('forge_event:' || p_episode::text));

    SELECT coalesce(max(seq), 0), coalesce(max(hash), repeat('0', 64))
      INTO v_seq, v_prev
      FROM forge_event WHERE episode_id = p_episode;

    v_seq := v_seq + 1;

    INSERT INTO forge_event (episode_id, seq, kind, payload, prev_hash, hash)
    VALUES (
        p_episode, v_seq, p_kind, p_payload, v_prev,
        encode(digest(p_episode::text || ':' || v_seq::text || ':' || p_kind || ':'
                      || p_payload::text || ':' || v_prev, 'sha256'), 'hex')
    )
    RETURNING * INTO v_row;

    RETURN v_row;
END;
$$;

-- ---------------------------------------------------------------- 5 handoff
CREATE TABLE IF NOT EXISTS forge_handoff (
    id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    episode_id   uuid NOT NULL REFERENCES forge_episode(id) ON DELETE RESTRICT,
    parent_id    uuid REFERENCES forge_handoff(id) ON DELETE RESTRICT,
    kind         text NOT NULL CHECK (kind IN ('artspec','command_batch','gate_report',
                                               'critique','lesson_candidate','skill_draft')),
    produced_by  text NOT NULL,
    consumed_by  text NOT NULL,
    payload      jsonb NOT NULL DEFAULT '{}'::jsonb,
    input_hashes jsonb NOT NULL DEFAULT '[]'::jsonb,
    refusal_code text,
    state        text NOT NULL DEFAULT 'created'
                 CHECK (state IN ('created','claimed','completed','failed','expired')),
    lease_until  timestamptz,
    attempts     integer NOT NULL DEFAULT 0 CHECK (attempts >= 0),
    max_attempts integer NOT NULL DEFAULT 2 CHECK (max_attempts BETWEEN 1 AND 5),
    created_at   timestamptz NOT NULL DEFAULT now(),
    updated_at   timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT forge_handoff_payload_size CHECK (octet_length(payload::text) <= 32768),
    CONSTRAINT forge_handoff_failure CHECK (
        (state = 'failed') = (refusal_code IS NOT NULL)
    )
);

CREATE INDEX IF NOT EXISTS forge_handoff_ready
    ON forge_handoff (state, lease_until, created_at);
CREATE INDEX IF NOT EXISTS forge_handoff_episode
    ON forge_handoff (episode_id, created_at);

DROP TRIGGER IF EXISTS forge_handoff_touch ON forge_handoff;
CREATE TRIGGER forge_handoff_touch BEFORE UPDATE ON forge_handoff
    FOR EACH ROW EXECUTE FUNCTION forge_touch_updated_at();

CREATE OR REPLACE FUNCTION forge_claim_handoff(p_role text, p_lease_s integer DEFAULT 900)
RETURNS forge_handoff
LANGUAGE plpgsql AS $$
DECLARE v forge_handoff;
BEGIN
    IF p_lease_s < 1 OR p_lease_s > 86400 THEN
        RAISE EXCEPTION 'E_PARAM_REJECTED: lease_s' USING ERRCODE = '22023';
    END IF;
    UPDATE forge_handoff h
       SET state = 'claimed',
           attempts = h.attempts + 1,
           lease_until = now() + make_interval(secs => p_lease_s)
     WHERE h.id = (
         SELECT id FROM forge_handoff
          WHERE state = 'created' AND consumed_by = p_role
          ORDER BY created_at
          FOR UPDATE SKIP LOCKED
          LIMIT 1
     )
     RETURNING * INTO v;
    RETURN v;   -- NULL when nothing is ready; never an error
END;
$$;

-- --------------------------------------------------------------- 6 tool_call
CREATE TABLE IF NOT EXISTS forge_tool_call (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    episode_id      uuid NOT NULL REFERENCES forge_episode(id) ON DELETE RESTRICT,
    handoff_id      uuid REFERENCES forge_handoff(id) ON DELETE RESTRICT,
    tool_id         text NOT NULL,
    cmd_id          text,
    params          jsonb NOT NULL DEFAULT '{}'::jsonb,
    idempotency_key text NOT NULL,
    state           text NOT NULL DEFAULT 'in_flight'
                    CHECK (state IN ('in_flight','succeeded','failed','refused')),
    refusal_code    text,
    result          jsonb,
    exit_code       integer,
    duration_ms     integer CHECK (duration_ms IS NULL OR duration_ms >= 0),
    argv            text[],
    replayed        boolean NOT NULL DEFAULT false,
    created_at      timestamptz NOT NULL DEFAULT now(),
    finished_at     timestamptz,
    CONSTRAINT forge_tool_call_key UNIQUE (idempotency_key),
    CONSTRAINT forge_tool_call_key_shape CHECK (idempotency_key ~ '^sha256:[0-9a-f]{64}$'),
    CONSTRAINT forge_tool_call_refusal CHECK (
        (state = 'refused') = (refusal_code IS NOT NULL)
    ),
    CONSTRAINT forge_tool_call_exit CHECK (
        state <> 'succeeded' OR exit_code = 0
    ),
    CONSTRAINT forge_tool_call_params_size CHECK (octet_length(params::text) <= 65536)
);

CREATE INDEX IF NOT EXISTS forge_tool_call_episode
    ON forge_tool_call (episode_id, created_at);
CREATE INDEX IF NOT EXISTS forge_tool_call_handoff
    ON forge_tool_call (handoff_id);

-- Idempotent replay: a caller that lost its response reads the stored result.
CREATE OR REPLACE FUNCTION forge_replay_tool_call(p_key text)
RETURNS forge_tool_call
LANGUAGE sql STABLE AS $$
    SELECT * FROM forge_tool_call WHERE idempotency_key = p_key;
$$;

-- ------------------------------------------------- 7 artifact / gate / critique / eval
CREATE TABLE IF NOT EXISTS forge_artifact (
    id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    episode_id   uuid NOT NULL REFERENCES forge_episode(id) ON DELETE RESTRICT,
    handoff_id   uuid REFERENCES forge_handoff(id) ON DELETE RESTRICT,
    kind         text NOT NULL CHECK (kind IN ('input','svg','raster','pdf','report','preview','video')),
    path         text NOT NULL CHECK (char_length(path) BETWEEN 1 AND 2048),
    sha256       text NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    bytes        bigint NOT NULL CHECK (bytes > 0),
    width        integer CHECK (width IS NULL OR width > 0),
    height       integer CHECK (height IS NULL OR height > 0),
    dpi          integer CHECK (dpi IS NULL OR dpi > 0),
    format       text,
    created_at   timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT forge_artifact_unique UNIQUE (episode_id, sha256, kind)
);

CREATE INDEX IF NOT EXISTS forge_artifact_sha ON forge_artifact (sha256);

CREATE TABLE IF NOT EXISTS forge_gate (
    id               bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    episode_id       uuid NOT NULL REFERENCES forge_episode(id) ON DELETE RESTRICT,
    artifact_sha256  text NOT NULL CHECK (artifact_sha256 ~ '^[0-9a-f]{64}$'),
    runner           text NOT NULL,
    runner_version   text NOT NULL,
    ok               boolean NOT NULL,
    checks           jsonb NOT NULL DEFAULT '{}'::jsonb,
    non_vacuous      jsonb NOT NULL DEFAULT '{}'::jsonb,
    source_mutation  jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at       timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS forge_gate_artifact ON forge_gate (artifact_sha256, created_at DESC);

CREATE TABLE IF NOT EXISTS forge_critique (
    id                   bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    episode_id           uuid NOT NULL REFERENCES forge_episode(id) ON DELETE RESTRICT,
    artifact_sha256      text NOT NULL CHECK (artifact_sha256 ~ '^[0-9a-f]{64}$'),
    prompt_version       text NOT NULL,
    model_id             text NOT NULL,
    blinded_to           jsonb NOT NULL DEFAULT '[]'::jsonb,
    dimensions           jsonb NOT NULL,
    defects              jsonb NOT NULL DEFAULT '[]'::jsonb,
    confidence           numeric(4,3) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    unseen               jsonb NOT NULL DEFAULT '[]'::jsonb,
    verdict              text NOT NULL CHECK (verdict IN ('pass','pass_with_notes','reject','unverifiable')),
    created_at           timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS forge_eval (
    id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    episode_id   uuid NOT NULL REFERENCES forge_episode(id) ON DELETE RESTRICT,
    arm          text NOT NULL CHECK (arm IN ('baseline','memory')),
    technical    jsonb NOT NULL DEFAULT '{}'::jsonb,
    human        jsonb,
    verdict      text NOT NULL CHECK (verdict IN ('pass','fail','needs_human','unverified')),
    reviewer     text,
    created_at   timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT forge_eval_one_per_arm UNIQUE (episode_id, arm)
);

DROP TRIGGER IF EXISTS forge_artifact_append_only ON forge_artifact;
CREATE TRIGGER forge_artifact_append_only BEFORE UPDATE OR DELETE ON forge_artifact
    FOR EACH ROW EXECUTE FUNCTION forge_refuse_mutation();
DROP TRIGGER IF EXISTS forge_gate_append_only ON forge_gate;
CREATE TRIGGER forge_gate_append_only BEFORE UPDATE OR DELETE ON forge_gate
    FOR EACH ROW EXECUTE FUNCTION forge_refuse_mutation();
DROP TRIGGER IF EXISTS forge_critique_append_only ON forge_critique;
CREATE TRIGGER forge_critique_append_only BEFORE UPDATE OR DELETE ON forge_critique
    FOR EACH ROW EXECUTE FUNCTION forge_refuse_mutation();
DROP TRIGGER IF EXISTS forge_eval_append_only ON forge_eval;
CREATE TRIGGER forge_eval_append_only BEFORE UPDATE OR DELETE ON forge_eval
    FOR EACH ROW EXECUTE FUNCTION forge_refuse_mutation();

-- ------------------------------------------------------------- 8 job queue
CREATE TABLE IF NOT EXISTS forge_job (
    id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    kind         text NOT NULL CHECK (char_length(kind) BETWEEN 1 AND 64),
    payload      jsonb NOT NULL DEFAULT '{}'::jsonb,
    dedupe_key   text UNIQUE,
    priority     integer NOT NULL DEFAULT 100,
    state        text NOT NULL DEFAULT 'queued'
                 CHECK (state IN ('queued','claimed','running','succeeded','failed','abandoned')),
    lease_until  timestamptz,
    attempts     integer NOT NULL DEFAULT 0 CHECK (attempts >= 0),
    max_attempts integer NOT NULL DEFAULT 3 CHECK (max_attempts BETWEEN 1 AND 10),
    run_after    timestamptz NOT NULL DEFAULT now(),
    last_error   text,
    created_at   timestamptz NOT NULL DEFAULT now(),
    updated_at   timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS forge_job_ready ON forge_job (state, priority, run_after);
CREATE INDEX IF NOT EXISTS forge_job_lease ON forge_job (lease_until);

DROP TRIGGER IF EXISTS forge_job_touch ON forge_job;
CREATE TRIGGER forge_job_touch BEFORE UPDATE ON forge_job
    FOR EACH ROW EXECUTE FUNCTION forge_touch_updated_at();

CREATE OR REPLACE FUNCTION forge_claim_job(p_worker text, p_lease_s integer DEFAULT 300)
RETURNS forge_job
LANGUAGE plpgsql AS $$
DECLARE v forge_job;
BEGIN
    IF p_lease_s < 1 OR p_lease_s > 86400 THEN
        RAISE EXCEPTION 'E_PARAM_REJECTED: lease_s' USING ERRCODE = '22023';
    END IF;
    UPDATE forge_job j
       SET state = 'claimed',
           attempts = j.attempts + 1,
           lease_until = now() + make_interval(secs => p_lease_s)
     WHERE j.id = (
         SELECT id FROM forge_job
          WHERE state = 'queued' AND run_after <= now()
          ORDER BY priority, id
          FOR UPDATE SKIP LOCKED
          LIMIT 1
     )
     RETURNING * INTO v;
    RETURN v;   -- NULL when the queue is empty; never an error
END;
$$;

CREATE OR REPLACE FUNCTION forge_finish_job(p_job bigint, p_ok boolean, p_error text DEFAULT NULL)
RETURNS forge_job
LANGUAGE plpgsql AS $$
DECLARE v forge_job;
BEGIN
    UPDATE forge_job
       SET state = CASE WHEN p_ok THEN 'succeeded' ELSE 'failed' END,
           last_error = CASE WHEN p_ok THEN NULL ELSE left(coalesce(p_error,'unknown'), 2000) END,
           lease_until = NULL
     WHERE id = p_job AND state IN ('claimed','running')
     RETURNING * INTO v;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'E_JOB_STATE: job % is not claimed/running', p_job USING ERRCODE = 'P0001';
    END IF;
    RETURN v;
END;
$$;

-- ------------------------------------------------------------------- 9 skill
CREATE TABLE IF NOT EXISTS forge_skill (
    skill_id        text NOT NULL,
    version         integer NOT NULL CHECK (version >= 1),
    name            text NOT NULL,
    app             text NOT NULL,
    catalogue_hash  text NOT NULL CHECK (catalogue_hash ~ '^sha256:[0-9a-f]{64}$'),
    preconditions   jsonb NOT NULL,
    steps           jsonb NOT NULL,
    gates           jsonb NOT NULL,
    recovery        jsonb NOT NULL DEFAULT '[]'::jsonb,
    stats           jsonb NOT NULL DEFAULT '{}'::jsonb,
    status          text NOT NULL DEFAULT 'draft'
                    CHECK (status IN ('draft','candidate','active','superseded','rolled_back')),
    evidence        uuid[] NOT NULL DEFAULT '{}',
    promoted_at     timestamptz,
    superseded_by   text,
    created_at      timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (skill_id, version),
    CONSTRAINT forge_skill_active_promoted CHECK (
        status <> 'active' OR promoted_at IS NOT NULL
    )
);

-- At most one active version per skill. This is the anti-double-promotion guard.
CREATE UNIQUE INDEX IF NOT EXISTS forge_skill_one_active
    ON forge_skill (skill_id) WHERE status = 'active';

-- ---------------------------------------------------------------- 10 budget
CREATE TABLE IF NOT EXISTS forge_budget_ledger (
    day            date NOT NULL,
    account_id     bigint NOT NULL,
    tokens_in      bigint NOT NULL DEFAULT 0 CHECK (tokens_in >= 0),
    tokens_out     bigint NOT NULL DEFAULT 0 CHECK (tokens_out >= 0),
    calls          integer NOT NULL DEFAULT 0 CHECK (calls >= 0),
    cents          numeric(12,4) NOT NULL DEFAULT 0 CHECK (cents >= 0),
    hard_cap_cents numeric(12,4) NOT NULL DEFAULT 0 CHECK (hard_cap_cents >= 0),
    updated_at     timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (day, account_id)
);

CREATE OR REPLACE FUNCTION forge_charge(
    p_account    bigint,
    p_day        date,
    p_tokens_in  bigint,
    p_tokens_out bigint,
    p_cents      numeric,
    p_cap_cents  numeric DEFAULT NULL
) RETURNS forge_budget_ledger
LANGUAGE plpgsql AS $$
DECLARE v forge_budget_ledger;
BEGIN
    IF p_tokens_in < 0 OR p_tokens_out < 0 OR p_cents < 0 THEN
        RAISE EXCEPTION 'E_PARAM_REJECTED: negative usage' USING ERRCODE = '22023';
    END IF;
    INSERT INTO forge_budget_ledger AS b
        (day, account_id, tokens_in, tokens_out, calls, cents, hard_cap_cents)
    VALUES (p_day, p_account, p_tokens_in, p_tokens_out, 1, p_cents,
            coalesce(p_cap_cents, 0))
    ON CONFLICT (day, account_id) DO UPDATE
       SET tokens_in    = b.tokens_in + EXCLUDED.tokens_in,
           tokens_out   = b.tokens_out + EXCLUDED.tokens_out,
           calls        = b.calls + 1,
           cents        = b.cents + EXCLUDED.cents,
           hard_cap_cents = coalesce(p_cap_cents, b.hard_cap_cents),
           updated_at   = now()
    RETURNING * INTO v;

    IF v.hard_cap_cents > 0 AND v.cents > v.hard_cap_cents THEN
        RAISE EXCEPTION 'E_BUDGET_EXCEEDED: % > % cents', v.cents, v.hard_cap_cents
            USING ERRCODE = 'P0001';
    END IF;
    RETURN v;
END;
$$;

-- -------------------------------------------------------------- 11 approval
CREATE TABLE IF NOT EXISTS forge_approval (
    id               bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    episode_id       uuid NOT NULL REFERENCES forge_episode(id) ON DELETE RESTRICT,
    artifact_sha256  text NOT NULL CHECK (artifact_sha256 ~ '^[0-9a-f]{64}$'),
    scope            text NOT NULL CHECK (scope IN ('publish','promotion')),
    token_hash       text NOT NULL CHECK (token_hash ~ '^[0-9a-f]{64}$'),
    issued_by        text NOT NULL,
    issued_at        timestamptz NOT NULL DEFAULT now(),
    expires_at       timestamptz,
    used_at          timestamptz,
    CONSTRAINT forge_approval_unique UNIQUE (artifact_sha256, scope, token_hash),
    CONSTRAINT forge_approval_expiry CHECK (expires_at IS NULL OR expires_at > issued_at)
);

CREATE OR REPLACE FUNCTION forge_consume_approval(
    p_episode uuid,
    p_sha     text,
    p_scope   text
) RETURNS forge_approval
LANGUAGE plpgsql AS $$
DECLARE v forge_approval;
BEGIN
    UPDATE forge_approval
       SET used_at = now()
     WHERE episode_id = p_episode
       AND artifact_sha256 = p_sha
       AND scope = p_scope
       AND used_at IS NULL
       AND (expires_at IS NULL OR expires_at > now())
     RETURNING * INTO v;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'E_PUBLISH_NOT_APPROVED: % scope % has no live approval', p_sha, p_scope
            USING ERRCODE = 'P0001';
    END IF;
    RETURN v;
END;
$$;

-- --------------------------------------------------------- 12 verification hooks
-- Chain verifier: recompute every hash and the prev_hash link.
CREATE OR REPLACE FUNCTION forge_verify_event_chain(p_episode uuid)
RETURNS table(checked integer, broken integer)
LANGUAGE plpgsql AS $$
DECLARE
    r      record;
    n      integer := 0;
    bad    integer := 0;
    expect text := repeat('0', 64);
    want   text;
BEGIN
    FOR r IN SELECT * FROM forge_event WHERE episode_id = p_episode ORDER BY seq LOOP
        n := n + 1;
        want := encode(digest(r.episode_id::text || ':' || r.seq::text || ':' || r.kind || ':'
                              || r.payload::text || ':' || r.prev_hash, 'sha256'), 'hex');
        IF r.hash <> want OR r.prev_hash <> expect THEN
            bad := bad + 1;
        END IF;
        expect := r.hash;
    END LOOP;
    RETURN QUERY SELECT n, bad;
END;
$$;

-- Append-only coverage report: every immutable table must have its trigger.
CREATE OR REPLACE FUNCTION forge_immutability_report()
RETURNS table(table_name text, has_trigger boolean)
LANGUAGE sql STABLE AS $$
    SELECT t.name,
           EXISTS (SELECT 1 FROM pg_trigger g
                    WHERE g.tgrelid = ('forge.' || t.name)::regclass
                      AND g.tgname = t.name || '_append_only'
                      AND NOT g.tgisinternal)
      FROM (VALUES ('forge_event'), ('forge_artifact'), ('forge_gate'),
                   ('forge_critique'), ('forge_eval')) AS t(name);
$$;

-- Grants template (run separately as the database owner; not part of table DDL):
--   CREATE ROLE forge_app LOGIN PASSWORD :'pw';
--   GRANT USAGE ON SCHEMA forge TO forge_app;
--   GRANT SELECT, INSERT, UPDATE ON forge_episode, forge_handoff, forge_tool_call,
--         forge_job, forge_skill, forge_approval TO forge_app;
--   GRANT SELECT, INSERT ON forge_event, forge_artifact, forge_gate,
--         forge_critique, forge_eval, forge_budget_ledger TO forge_app;
--   GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA forge TO forge_app;
--   REVOKE ALL ON SCHEMA pod FROM forge_app;
```
---

## 4. State machine — 36 edges, 15 states, terminal rules

States: `intake → briefed → planned → context_ready → executing → verifying → critiquing` with
`needs_human` and `paused` as re-entrant branches, and terminal
`accepted · rejected · refused · failed · cancelled · quarantined`.

| From | To (guard label) |
|---|---|
| `intake` | `briefed` (deliverable_target_rights), `refused` (brief_missing), `cancelled` |
| `briefed` | `planned` (artspec_cited), `needs_human`, `refused` (rights_missing), `cancelled` |
| `planned` | `context_ready` (retrieval_receipt), `needs_human`, `failed`, `refused` |
| `context_ready` | `executing` (locks_budget), `needs_human`, `refused` (budget_exceeded), `cancelled` |
| `executing` | `verifying` (handoff_artifacts), `paused`, `failed`, `needs_human`, `quarantined` (source_mutated), `cancelled` |
| `verifying` | `critiquing` (rungs_1_4_green), `rejected` (gate_failed), `needs_human` (gate_missing), `failed` |
| `critiquing` | `accepted` (verdict_rules_human), `rejected` (critic_reject), `needs_human`, `failed` |
| `needs_human` | `accepted` (human_approved), `rejected`, `paused`, `cancelled` |
| `paused` | `executing` (human_resumed), `needs_human`, `cancelled` |
| `quarantined` | — terminal (security review closes out of band) |

**Which invariants are enforced where:**

| Invariant | Enforced by | Proof |
|---|---|---|
| Only listed edges are traversable | seeded `forge_transition` + `forge_transition_episode()` | SQL `T03`, `T15`; Python `TransitionTests` |
| Unknown state is refused | Python `next_state`; SQL CHECK on both columns | Python `test_unknown_state_refused` |
| `accepted` needs `pass`/`pass_with_notes` | SQL table CHECK + guarded function | SQL `T04` |
| Terminal states are final | no outgoing edges; Python set equality test | Python `test_terminal_states_have_no_outgoing_edges` |
| Every transition is evidence | `forge_append_event` inside the transition transaction | SQL `T02`, `T05`; chain verifier |
| Handoff lifecycles | CHECK `(state='failed') = (refusal_code IS NOT NULL)` + claim function | SQL `T10` |
| Job lifecycles | state CHECK + `forge_finish_job` only from claimed/running | SQL `T09`, `T17` |
| Skill lifecycles | `draft/candidate/active/superseded/rolled_back` + one-active index | SQL `T11` |

**Verdict assembly** (Python `build_verdict`) is total and order-independent: mutation → reject;
missing process/artifact/render evidence → unverified; failed or vacuous gate → reject; missing gate →
unverified; missing/rejecting critic → `needs_human`; human-required without human → `needs_human`;
otherwise pass/pass_with_notes. A missing rung can never become a pass.

---

## 5. Idempotency — exact algorithm

```
key = "sha256:" + sha256( canonical_json({
        "episode_id", "tool_id", "params", "input_hashes", "schema": "forge-idem/1" }) )
canonical_json = JSON, keys sorted, separators ("," ":"), UTF-8, no NaN/Infinity
```

Guarantees and their mechanisms:

| Guarantee | Mechanism |
|---|---|
| Same logical call → same key | canonical JSON (dict order irrelevant); tested |
| Different episode/params/inputs → different key | key material includes all four; tested |
| Key shape is checkable | `validate_key` + SQL CHECK; tested |
| A key executes at most once | `UNIQUE (idempotency_key)`; tested |
| A lost response is recoverable | `forge_replay_tool_call(key)` / `Repo.find` returns stored result; tested (executor call count stays 1) |
| Refusals are also idempotent | refused outcomes are stored, replays return them; tested |
| Publish/promotion cannot be replayed for free | `forge_approval` consumed once per `(artifact, scope)`; tested |

The Python gateway checks **all policy before any side effect** — spec, role, command allowlist, roots,
key shape, replay — and only then calls the executor. A root or allowlist violation therefore leaves
zero rows and zero executor calls (tested).

**Known race (`[GAP]` G-01):** `find → execute → insert` is not atomic across two processes. The
database unique index is the real guard; a production `Repo` must catch `unique_violation` and re-read
the winning row instead of failing. The skeleton documents the required catch; it does not pretend the
Python find-then-insert is race-free.

---

## 6. Refusal handling

The skeleton carries **35 codes: the 27 from `04` section 6.6 plus 8 raised by the executable layer** (`E_TRANSITION_ILLEGAL`, `E_VERDICT_MISSING`, `E_VERDICT_INVALID`, `E_EPISODE_NOT_FOUND`, `E_APPEND_ONLY`, `E_JOB_STATE`, `E_ROLE_DENIED`, `E_IDEMPOTENCY_CONFLICT`). Rules: every refusal is a named `E_*` code; **unknown codes fail closed as terminal**; retry is a
property of the code, never of the caller's optimism; refusals raised before a side effect produce no
rows.

| Code | Terminal | Raised by | Notes |
|---|---|---|---|
| `E_TRANSITION_ILLEGAL`, `E_VERDICT_MISSING`, `E_VERDICT_INVALID` | yes | SQL function | state machine integrity |
| `E_EPISODE_NOT_FOUND`, `E_APPEND_ONLY` | yes | SQL | evidence integrity |
| `E_BUDGET_EXCEEDED`, `E_PUBLISH_NOT_APPROVED`, `E_JOB_STATE` | yes | SQL function | side-effect control |
| `E_ROOT_DENIED`, `E_INPLACE_WRITE`, `E_COMMAND_UNKNOWN`, `E_ROLE_DENIED`, `E_IDEMPOTENCY_CONFLICT` | yes | Python gateway | policy, before execution |
| `E_APP_DRIFT`, `E_CATALOGUE_STALE`, `E_SOURCE_MUTATED`, `E_RIGHTS_MISSING`, `E_BRIEF_MISSING`, `E_UPSCALE_LIMIT`, `E_TEXT_TRACE_FORBIDDEN`, `E_WHITE_MODE_REFUSED`, `E_SURFACE_UNVERIFIABLE`, `E_UNSUPPORTED_SURFACE`, `E_EVAL_EMPTY` | yes | gateway/verifier | design taxonomy from `04` §6.6 |
| `E_ARTIFACT_MISSING`, `E_ARTIFACT_EMPTY`, `E_DOCUMENT_STATE`, `E_GATE_FAILED`, `E_GATE_MISSING`, `E_GATE_VACUOUS`, `E_VISION_UNAVAILABLE`, `E_CRITIQUE_UNGROUNDED`, `E_PARAM_REJECTED`, `E_TIMEOUT`, `E_MEMORY_CONFLICT` | **no** | verifier/executor | retry within `max_attempts` |

Terminal codes are never retried (`is_terminal_refusal` + `may_retry`; tested for five terminal and one
retryable code, plus unknown-code fail-closed).

---

## 7. Tool-gateway interface (minimal)

| Symbol | Signature | Purpose |
|---|---|---|
| `ToolSpec` | `tool_id, allowed_roles, allowed_cmds, roots, writes, timeout_s` | registry entry; the allowlist is exact command IDs, never a prefix wildcard |
| `ToolCall` | `episode_id, tool_id, cmd_id, params, paths, input_hashes` | one bounded invocation |
| `ExecutionOutcome` | `exit_code, duration_ms, argv, artifacts, refusal_code, message` | what an executor may return |
| `ToolResult` | `idempotency_key, state, replayed, exit_code, refusal_code, artifacts, message` | stored, replayable result |
| `Gateway.execute(call, token) -> ToolResult` | ordered checks → execute → classify → store | the single entry point |
| `Executor.run(spec, call) -> ExecutionOutcome` | protocol | real CLI adapter (task-08) or a test double; no production branch fabricates data |
| `Repo.find/store` | protocol | the `forge_tool_call` table in production; in-memory for tests |
| `canonical_json`, `idempotency_key`, `validate_key` | pure functions | key contract |
| `resolve_within(path, roots) -> Path` | pure function | realpath first, then root comparison |
| `can_transition`, `next_state` | pure functions | 36-edge mirror of the SQL seed |
| `is_terminal_refusal`, `may_retry` | pure functions | refusal policy |
| `build_verdict(Evidence) -> (verdict, reasons)` | pure function | evidence ladder, total |

Execution order is fixed and tested: **spec → role → cmd allowlist → roots → key shape → replay →
execute → classify → store**. Any policy failure raises `PolicyError` (or returns a refused
`ToolResult` for role denial) *before* the executor is called.

**File: ```forge_gateway.py```**

```python
#!/usr/bin/env python3
"""Forge Conductor skeleton: reference implementation of the tool gateway.

Executable contract only. No network, no Craft CLI, no database driver: the
repository and the executor are protocols so the logic can be tested with a
permitted test double (see test_forge_gateway.py).

Design rules proven by tests:
  * one canonical idempotency key per (episode, tool, params, input hashes)
  * a replayed key returns the stored result and never calls the executor again
  * role allowlists and command allowlists fail closed with E_* refusals
  * paths are resolved before the root comparison (no traversal)
  * refusals are terminal or retryable by code, not by caller opinion
  * a verdict is assembled from evidence rungs; missing evidence is unverified
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Literal, Protocol, Sequence

# --------------------------------------------------------------------------- states
EPISODE_STATES: tuple[str, ...] = (
    "intake", "briefed", "planned", "context_ready", "executing", "verifying",
    "critiquing", "needs_human", "paused", "accepted", "rejected", "refused",
    "failed", "cancelled", "quarantined",
)

# Edges mirror the seeded `forge_transition` table exactly (36 rows).
TRANSITIONS: frozenset[tuple[str, str]] = frozenset({
    ("intake", "briefed"), ("intake", "refused"), ("intake", "cancelled"),
    ("briefed", "planned"), ("briefed", "needs_human"), ("briefed", "refused"),
    ("briefed", "cancelled"),
    ("planned", "context_ready"), ("planned", "needs_human"), ("planned", "failed"),
    ("planned", "refused"),
    ("context_ready", "executing"), ("context_ready", "needs_human"),
    ("context_ready", "refused"), ("context_ready", "cancelled"),
    ("executing", "verifying"), ("executing", "paused"), ("executing", "failed"),
    ("executing", "needs_human"), ("executing", "quarantined"), ("executing", "cancelled"),
    ("verifying", "critiquing"), ("verifying", "rejected"), ("verifying", "needs_human"),
    ("verifying", "failed"),
    ("critiquing", "accepted"), ("critiquing", "rejected"), ("critiquing", "needs_human"),
    ("critiquing", "failed"),
    ("needs_human", "accepted"), ("needs_human", "rejected"), ("needs_human", "paused"),
    ("needs_human", "cancelled"),
    ("paused", "executing"), ("paused", "needs_human"), ("paused", "cancelled"),
})

TERMINAL_STATES: frozenset[str] = frozenset(
    {"accepted", "rejected", "refused", "failed", "cancelled", "quarantined"})

# Refusal taxonomy: terminal codes are never retried by any agent.
TERMINAL_REFUSALS: frozenset[str] = frozenset({
    "E_BRIEF_MISSING", "E_RIGHTS_MISSING", "E_ROOT_DENIED", "E_INPLACE_WRITE",
    "E_COMMAND_UNKNOWN", "E_APP_DRIFT", "E_CATALOGUE_STALE", "E_SOURCE_MUTATED",
    "E_UPSCALE_LIMIT", "E_TEXT_TRACE_FORBIDDEN", "E_WHITE_MODE_REFUSED",
    "E_BUDGET_EXCEEDED", "E_PUBLISH_NOT_APPROVED", "E_SURFACE_UNVERIFIABLE",
    "E_EVAL_EMPTY", "E_UNSUPPORTED_SURFACE", "E_EPISODE_NOT_FOUND",
})
RETRYABLE_REFUSALS: frozenset[str] = frozenset({
    "E_ARTIFACT_MISSING", "E_ARTIFACT_EMPTY", "E_DOCUMENT_STATE",
    "E_GATE_FAILED", "E_GATE_MISSING", "E_GATE_VACUOUS", "E_VISION_UNAVAILABLE",
    "E_CRITIQUE_UNGROUNDED", "E_TIMEOUT", "E_PARAM_REJECTED", "E_MEMORY_CONFLICT",
})


class PolicyError(RuntimeError):
    """A refusal raised before any side effect. Carries a named code."""

    def __init__(self, code: str, message: str, *, terminal: bool = True) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
        self.terminal = terminal


# --------------------------------------------------------------------------- keys
def canonical_json(value: Any) -> str:
    """Deterministic JSON for hashing. Rejects NaN/inf and non-UTF-8-safe input."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)


def sha256_hex(data: str | bytes) -> str:
    raw = data.encode("utf-8") if isinstance(data, str) else data
    return hashlib.sha256(raw).hexdigest()


def idempotency_key(episode_id: str, tool_id: str, params: dict[str, Any],
                    input_hashes: Sequence[str] = ()) -> str:
    """Stable key. Same logical call -> same key, regardless of dict order."""
    material = canonical_json({
        "episode_id": episode_id,
        "tool_id": tool_id,
        "params": params,
        "input_hashes": list(input_hashes),
        "schema": "forge-idem/1",
    })
    return "sha256:" + sha256_hex(material)


def validate_key(key: str) -> bool:
    return len(key) == 71 and key.startswith("sha256:") and all(
        c in "0123456789abcdef" for c in key[7:])


# ----------------------------------------------------------------------- transitions
def can_transition(current: str, target: str) -> bool:
    return (current, target) in TRANSITIONS


def next_state(current: str, target: str) -> str:
    if current not in EPISODE_STATES:
        raise PolicyError("E_EPISODE_STATE_UNKNOWN", current)
    if not can_transition(current, target):
        raise PolicyError("E_TRANSITION_ILLEGAL", f"{current} -> {target}")
    return target


# --------------------------------------------------------------------------- paths
def resolve_within(path: str, roots: Iterable[str]) -> Path:
    """Resolve symlinks and '..' BEFORE the root check; fail closed."""
    candidate = Path(os.path.realpath(os.path.abspath(path)))
    for root in roots:
        resolved_root = Path(os.path.realpath(os.path.abspath(root)))
        if candidate == resolved_root or resolved_root in candidate.parents:
            return candidate
    raise PolicyError("E_ROOT_DENIED", f"{path} is outside the declared roots")


# ------------------------------------------------------------------------ refusals
def is_terminal_refusal(code: str) -> bool:
    if code in TERMINAL_REFUSALS:
        return True
    if code in RETRYABLE_REFUSALS:
        return False
    return True  # unknown codes fail closed: terminal


def may_retry(code: str, attempt: int, max_attempts: int) -> bool:
    if is_terminal_refusal(code):
        return False
    return 0 < attempt < max_attempts


# ------------------------------------------------------------------------- verdicts
@dataclass(frozen=True)
class Evidence:
    """Rungs 1-6. Missing evidence is None, never a default of 'ok'."""
    process_ok: bool | None = None
    artifact_ok: bool | None = None
    gate_ok: bool | None = None
    gate_vacuous: bool = False
    source_mutated: bool = False
    render_ok: bool | None = None
    critique: Literal["pass", "pass_with_notes", "reject", "unverifiable"] | None = None
    human: Literal["accept", "reject"] | None = None
    human_required: bool = False


def build_verdict(ev: Evidence) -> tuple[str, list[str]]:
    """Return (verdict, reason_codes). Rules are order-independent and total."""
    reasons: list[str] = []
    if ev.source_mutated:
        return "reject", ["E_SOURCE_MUTATED"]
    if ev.process_ok is not True:
        return "unverified", ["E_ARTIFACT_MISSING"]
    if ev.artifact_ok is not True:
        return "reject", ["E_ARTIFACT_EMPTY"]
    if ev.gate_ok is None:
        return "unverified", ["E_GATE_MISSING"]
    if ev.gate_vacuous:
        return "reject", ["E_GATE_VACUOUS"]
    if ev.gate_ok is not True:
        return "reject", ["E_GATE_FAILED"]
    if ev.render_ok is not True:
        return "unverified", ["E_ARTIFACT_MISSING"]
    if ev.critique is None or ev.critique == "unverifiable":
        return "needs_human", ["E_VISION_UNAVAILABLE"]
    if ev.critique == "reject":
        return "needs_human", ["E_CRITIQUE_REJECT"]
    if ev.human_required:
        if ev.human is None:
            return "needs_human", ["E_HUMAN_REQUIRED"]
        if ev.human == "reject":
            return "reject", ["E_HUMAN_REJECT"]
    if ev.critique == "pass_with_notes":
        return "pass_with_notes", ["E_CRITIQUE_NOTES"]
    return "pass", []


# ------------------------------------------------------------------------- gateway
@dataclass(frozen=True)
class ToolSpec:
    tool_id: str
    allowed_roles: tuple[str, ...]
    allowed_cmds: tuple[str, ...]
    roots: tuple[str, ...]
    writes: bool = False
    timeout_s: int = 900


@dataclass(frozen=True)
class ToolCall:
    episode_id: str
    tool_id: str
    cmd_id: str | None
    params: dict[str, Any]
    paths: tuple[str, ...] = ()
    input_hashes: tuple[str, ...] = ()


@dataclass(frozen=True)
class ExecutionOutcome:
    exit_code: int
    duration_ms: int
    argv: tuple[str, ...]
    artifacts: tuple[dict[str, Any], ...] = ()
    refusal_code: str | None = None
    message: str = ""


@dataclass
class ToolResult:
    idempotency_key: str
    state: Literal["succeeded", "failed", "refused"]
    replayed: bool = False
    exit_code: int | None = None
    refusal_code: str | None = None
    artifacts: tuple[dict[str, Any], ...] = ()
    message: str = ""


class Executor(Protocol):
    def run(self, spec: ToolSpec, call: ToolCall) -> ExecutionOutcome: ...


class Repo(Protocol):
    def find(self, key: str) -> ToolResult | None: ...
    def store(self, key: str, result: ToolResult) -> None: ...


class InMemoryRepo:
    """Test double for the forge_tool_call table (unique key semantics)."""

    def __init__(self) -> None:
        self.rows: dict[str, ToolResult] = {}

    def find(self, key: str) -> ToolResult | None:
        return self.rows.get(key)

    def store(self, key: str, result: ToolResult) -> None:
        if key in self.rows:
            raise PolicyError("E_IDEMPOTENCY_CONFLICT", key)
        self.rows[key] = result


class Gateway:
    def __init__(self, specs: Sequence[ToolSpec], executor: Executor, repo: Repo,
                 roles: dict[str, str]) -> None:
        self._specs = {s.tool_id: s for s in specs}
        self._executor = executor
        self._repo = repo
        self._roles = roles            # token -> role

    def spec(self, tool_id: str) -> ToolSpec:
        try:
            return self._specs[tool_id]
        except KeyError:
            raise PolicyError("E_COMMAND_UNKNOWN", f"tool {tool_id}") from None

    def execute(self, call: ToolCall, token: str) -> ToolResult:
        spec = self.spec(call.tool_id)
        role = self._roles.get(token)
        if role is None or role not in spec.allowed_roles:
            return ToolResult(
                idempotency_key=idempotency_key(call.episode_id, call.tool_id,
                                                call.params, call.input_hashes),
                state="refused", refusal_code="E_ROLE_DENIED",
                message=f"role {role!r} may not call {call.tool_id}")

        if call.cmd_id is not None and call.cmd_id not in spec.allowed_cmds:
            raise PolicyError("E_COMMAND_UNKNOWN", f"cmd {call.cmd_id}")

        for path in call.paths:
            resolve_within(path, spec.roots)   # raises E_ROOT_DENIED before any effect

        key = idempotency_key(call.episode_id, call.tool_id, call.params, call.input_hashes)
        if not validate_key(key):
            raise PolicyError("E_KEY_SHAPE", key)
        prior = self._repo.find(key)
        if prior is not None:
            return ToolResult(**{**prior.__dict__, "replayed": True})

        outcome = self._executor.run(spec, call)
        if outcome.refusal_code:
            result = ToolResult(idempotency_key=key, state="refused",
                                refusal_code=outcome.refusal_code,
                                message=outcome.message)
        elif outcome.exit_code == 0:
            result = ToolResult(idempotency_key=key, state="succeeded",
                                exit_code=0, artifacts=outcome.artifacts)
        else:
            result = ToolResult(idempotency_key=key, state="failed",
                                exit_code=outcome.exit_code, message=outcome.message)
        self._repo.store(key, result)
        return result
```
---

## 8. Tests — what is proven, and how to re-run

### 8.1 SQL assertion suite (18 assertions + 1 concurrency scenario)

Run against a throwaway database after the DDL. Every assertion raises on failure, so the exit status
is the verdict.

| ID | Proves |
|---|---|
| `T01` | 13 base tables and 36 seeded edges exist |
| `T02` | `intake→briefed` works, is non-terminal, and appends exactly one event |
| `T03` | illegal `intake→accepted` raises and leaves status unchanged |
| `T04` | accept requires a verdict; `reject` cannot be accepted; terminal sets `finished_at` |
| `T05` | event chain: seq monotonic, genesis `prev_hash` zeros, second hash links, verifier reports 0 broken |
| `T06` | `UPDATE` and `DELETE` on `forge_event` raise `42501` |
| `T07` | duplicate episode submission key violates unique |
| `T08` | duplicate tool-call key violates unique; replay returns stored result; refused row requires `refusal_code` |
| `T09` | job claim sets `claimed`/`attempts=1`/lease; second claim takes the next job; empty queue returns NULL |
| `T10` | handoff claim sets lease and attempts; nothing ready returns NULL |
| `T11` | second active skill version violates the partial index; duplicate `(skill_id,version)` violates PK |
| `T12` | budget accumulates; over-cap raises; aborted charge rolls back (balance unchanged) |
| `T13` | approval consumes once, wrong artifact hash consumes nothing |
| `T14` | malformed sha256 and zero-byte artifacts violate checks |
| `T15` | no transition out of a terminal state; `can_transition` false |
| `T16` | every append-only table actually has its trigger |
| `T17` | finishing a queued job raises; finishing a claimed job succeeds |
| `T18` | a directly forged event row is detected by the chain verifier |
| `T-SKIPLOCK` | with worker A holding a claim and sleeping, worker B claims a different job in <2000 ms (observed 592 ms) — `SKIP LOCKED` does not block |

### 8.2 Python suite — 33 tests in 6 groups

| Group | Tests | Covers |
|---|---|---|
| Key | 3 | canonical JSON order independence, key stability/shape, sensitivity to episode/params/inputs |
| Transition | 6 | 36-edge count, legal/illegal/unknown transitions, terminal-state closure, totality |
| Verdict | 9 | happy path, missing gate → unverified, gate beats critic, vacuous gate, source mutation, critic reject/missing, human required/reject |
| Path | 3 | inside root allowed, `..` traversal denied, sibling root denied |
| Refusal | 3 | terminal codes never retry, retryable codes respect budget, unknown code fails closed |
| Gateway | 9 | success + replay does not re-execute, param change → new call, role denial, unknown token, command allowlist, unknown tool, root violation before side effect, executor refusal stored/replayed, failed exit not success |

### 8.3 TypeScript checks

- Positive: `tsc --noEmit --strict` over `contracts.d.ts` + `check.ts` → exit 0.
- Negative: removing `runner_version` from the `GateReport` literal → `TS2741`, exit 2. The contracts
  are therefore load-bearing, not decoration.
- The check file also exhaustively enumerates all 15 `EpisodeStatus` values, so adding a state without
  updating the union fails compilation.

### 8.4 Exact re-run commands (as executed in §10)

```bash
# SQL: scratch DB (created and dropped for this task only)
psql -v ON_ERROR_STOP=1 -d forge_scratch -f forge_schema.sql   # apply twice
psql -v ON_ERROR_STOP=1 -d forge_scratch -f forge_tests.sql
# concurrency: two psql sessions, one holding a claim with pg_sleep(3)

# Python
python -m py_compile forge_gateway.py test_forge_gateway.py
python -m unittest -v test_forge_gateway.py

# TypeScript
node node_modules/typescript/bin/tsc --noEmit --strict \
  --target ES2022 --module ESNext --moduleResolution bundler contracts.d.ts check.ts
```

### 8.5 Embedded test file (verbatim, as run)

**File: ```test_forge_gateway.py```**

```python
#!/usr/bin/env python3
"""Tests for the Forge gateway skeleton. Stdlib only: python -m unittest -v."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from forge_gateway import (
    EPISODE_STATES, TRANSITIONS, TERMINAL_STATES, Evidence, ExecutionOutcome, Gateway,
    InMemoryRepo, PolicyError, ToolCall, ToolSpec, build_verdict, can_transition,
    canonical_json, idempotency_key, is_terminal_refusal, may_retry, next_state,
    resolve_within, sha256_hex, validate_key,
)


class FakeExecutor:
    """Permitted test double for an external CLI (never a production branch)."""

    def __init__(self, outcome=None):
        self.calls = 0
        self.outcome = outcome or ExecutionOutcome(
            exit_code=0, duration_ms=12, argv=("fake-cli",),
            artifacts=({"path": "build/x.png", "sha256": "a" * 64, "bytes": 10},))

    def run(self, spec, call):
        self.calls += 1
        return self.outcome


SPEC = ToolSpec(
    tool_id="craft.run",
    allowed_roles=("vector_operator",),
    allowed_cmds=("imageTrace.make", "imageTrace.expand"),
    roots=("/tmp/forge-work",),
    writes=True,
)


class KeyTests(unittest.TestCase):
    def test_canonical_json_is_order_independent(self):
        self.assertEqual(canonical_json({"b": 1, "a": [2, {"d": 4, "c": 3}]}),
                         canonical_json({"a": [2, {"c": 3, "d": 4}], "b": 1}))

    def test_key_is_stable_and_well_formed(self):
        k1 = idempotency_key("ep", "craft.run", {"b": 2, "a": 1}, ["sha256:" + "f" * 64])
        k2 = idempotency_key("ep", "craft.run", {"a": 1, "b": 2}, ["sha256:" + "f" * 64])
        self.assertEqual(k1, k2)
        self.assertTrue(validate_key(k1))
        self.assertEqual(len(k1), 71)

    def test_key_changes_with_params_episode_and_inputs(self):
        base = idempotency_key("ep1", "t", {"a": 1})
        self.assertNotEqual(base, idempotency_key("ep2", "t", {"a": 1}))
        self.assertNotEqual(base, idempotency_key("ep1", "t", {"a": 2}))
        self.assertNotEqual(base, idempotency_key("ep1", "t", {"a": 1}, ["sha256:" + "1" * 64]))


class TransitionTests(unittest.TestCase):
    def test_transition_table_matches_design_count(self):
        self.assertEqual(len(TRANSITIONS), 36)
        self.assertTrue(set(EPISODE_STATES) >= {s for pair in TRANSITIONS for s in pair})

    def test_legal_transition(self):
        self.assertEqual(next_state("intake", "briefed"), "briefed")

    def test_illegal_transition_refused(self):
        for src, dst in (("intake", "accepted"), ("refused", "executing"),
                         ("accepted", "paused"), ("quarantined", "executing")):
            with self.assertRaises(PolicyError) as caught:
                next_state(src, dst)
            self.assertEqual(caught.exception.code, "E_TRANSITION_ILLEGAL")

    def test_unknown_state_refused(self):
        with self.assertRaises(PolicyError) as caught:
            next_state("not-a-state", "briefed")
        self.assertEqual(caught.exception.code, "E_EPISODE_STATE_UNKNOWN")

    def test_terminal_states_have_no_outgoing_edges(self):
        for state in TERMINAL_STATES:
            outgoing = {dst for src, dst in TRANSITIONS if src == state}
            self.assertEqual(outgoing, set(), f"{state} has outgoing edges")

    def test_can_transition_is_total(self):
        self.assertFalse(can_transition("intake", "accepted"))
        self.assertTrue(can_transition("critiquing", "accepted"))


class VerdictTests(unittest.TestCase):
    def full_pass(self, **overrides):
        base = dict(process_ok=True, artifact_ok=True, gate_ok=True, render_ok=True,
                    critique="pass", human=None, human_required=False)
        base.update(overrides)
        return build_verdict(Evidence(**base))

    def test_happy_path_passes(self):
        self.assertEqual(self.full_pass(), ("pass", []))

    def test_missing_gate_is_unverified_not_pass(self):
        verdict, reasons = self.full_pass(gate_ok=None)
        self.assertEqual(verdict, "unverified")
        self.assertIn("E_GATE_MISSING", reasons)

    def test_gate_failure_dominates_positive_critic(self):
        verdict, _ = self.full_pass(gate_ok=False)
        self.assertEqual(verdict, "reject")

    def test_vacuous_gate_is_reject(self):
        verdict, reasons = self.full_pass(gate_vacuous=True)
        self.assertEqual(verdict, "reject")
        self.assertIn("E_GATE_VACUOUS", reasons)

    def test_source_mutation_is_reject_before_everything(self):
        verdict, reasons = self.full_pass(source_mutated=True)
        self.assertEqual((verdict, reasons[0]), ("reject", "E_SOURCE_MUTATED"))

    def test_critic_reject_goes_to_human(self):
        verdict, _ = self.full_pass(critique="reject")
        self.assertEqual(verdict, "needs_human")

    def test_missing_critic_goes_to_human(self):
        verdict, _ = self.full_pass(critique=None)
        self.assertEqual(verdict, "needs_human")

    def test_human_required_blocks_acceptance(self):
        verdict, _ = self.full_pass(human_required=True)
        self.assertEqual(verdict, "needs_human")

    def test_human_reject_overrides_critic_pass(self):
        verdict, _ = self.full_pass(human_required=True, human="reject")
        self.assertEqual(verdict, "reject")


class PathTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="forge-root-")
        self.outside = tempfile.mkdtemp(prefix="forge-outside-")
        Path(self.root, "work").mkdir()

    def test_path_inside_root_resolves(self):
        target = str(Path(self.root, "work", "a.png"))
        self.assertEqual(resolve_within(target, [self.root]), Path(target))

    def test_traversal_is_denied(self):
        target = str(Path(self.root, "..", "escape.png"))
        with self.assertRaises(PolicyError) as caught:
            resolve_within(target, [self.root])
        self.assertEqual(caught.exception.code, "E_ROOT_DENIED")

    def test_sibling_root_is_denied(self):
        target = str(Path(self.outside, "a.png"))
        with self.assertRaises(PolicyError) as caught:
            resolve_within(target, [self.root])
        self.assertEqual(caught.exception.code, "E_ROOT_DENIED")


class RefusalTests(unittest.TestCase):
    def test_terminal_codes_never_retry(self):
        for code in ("E_SOURCE_MUTATED", "E_ROOT_DENIED", "E_PUBLISH_NOT_APPROVED",
                     "E_BUDGET_EXCEEDED", "E_COMMAND_UNKNOWN"):
            self.assertTrue(is_terminal_refusal(code))
            self.assertFalse(may_retry(code, 1, 3))

    def test_retryable_codes_retry_until_budget(self):
        self.assertFalse(is_terminal_refusal("E_ARTIFACT_MISSING"))
        self.assertTrue(may_retry("E_ARTIFACT_MISSING", 1, 2))
        self.assertFalse(may_retry("E_ARTIFACT_MISSING", 2, 2))

    def test_unknown_code_fails_closed(self):
        self.assertTrue(is_terminal_refusal("E_SOMETHING_NEW"))


class GatewayTests(unittest.TestCase):
    def setUp(self):
        self.repo = InMemoryRepo()
        self.executor = FakeExecutor()
        self.gw = Gateway([SPEC], self.executor, self.repo,
                          roles={"tok-op": "vector_operator", "tok-critic": "visual_critic"})
        self.call = ToolCall(episode_id="ep1", tool_id="craft.run",
                             cmd_id="imageTrace.make", params={"palette": 6},
                             paths=("/tmp/forge-work/out.svg",))

    def test_success_then_replay_does_not_reexecute(self):
        r1 = self.gw.execute(self.call, "tok-op")
        r2 = self.gw.execute(self.call, "tok-op")
        self.assertEqual(r1.state, "succeeded")
        self.assertFalse(r1.replayed)
        self.assertTrue(r2.replayed)
        self.assertEqual(r1.idempotency_key, r2.idempotency_key)
        self.assertEqual(self.executor.calls, 1)

    def test_different_params_produce_new_call(self):
        self.gw.execute(self.call, "tok-op")
        other = ToolCall(episode_id="ep1", tool_id="craft.run",
                         cmd_id="imageTrace.make", params={"palette": 8})
        self.gw.execute(other, "tok-op")
        self.assertEqual(self.executor.calls, 2)

    def test_role_denied_is_refusal_not_exception(self):
        result = self.gw.execute(self.call, "tok-critic")
        self.assertEqual(result.state, "refused")
        self.assertEqual(result.refusal_code, "E_ROLE_DENIED")
        self.assertEqual(self.executor.calls, 0)

    def test_unknown_token_denied(self):
        result = self.gw.execute(self.call, "nope")
        self.assertEqual(result.refusal_code, "E_ROLE_DENIED")

    def test_cmd_not_allowlisted_fails_closed(self):
        bad = ToolCall(episode_id="ep1", tool_id="craft.run",
                       cmd_id="file.delete", params={})
        with self.assertRaises(PolicyError) as caught:
            self.gw.execute(bad, "tok-op")
        self.assertEqual(caught.exception.code, "E_COMMAND_UNKNOWN")
        self.assertEqual(self.executor.calls, 0)

    def test_unknown_tool_fails_closed(self):
        bad = ToolCall(episode_id="ep1", tool_id="craft.rm", cmd_id=None, params={})
        with self.assertRaises(PolicyError) as caught:
            self.gw.execute(bad, "tok-op")
        self.assertEqual(caught.exception.code, "E_COMMAND_UNKNOWN")

    def test_root_violation_refused_before_side_effect(self):
        bad = ToolCall(episode_id="ep1", tool_id="craft.run",
                       cmd_id="imageTrace.make", params={},
                       paths=("/etc/passwd",))
        with self.assertRaises(PolicyError) as caught:
            self.gw.execute(bad, "tok-op")
        self.assertEqual(caught.exception.code, "E_ROOT_DENIED")
        self.assertEqual(self.executor.calls, 0)
        self.assertEqual(self.repo.rows, {})

    def test_executor_refusal_is_stored_and_replayed(self):
        refusing = FakeExecutor(ExecutionOutcome(exit_code=127, duration_ms=1,
                                                 argv=("fake-cli",),
                                                 refusal_code="E_COMMAND_UNKNOWN",
                                                 message="vendor binary not installed"))
        gw = Gateway([SPEC], refusing, self.repo, roles={"tok-op": "vector_operator"})
        r1 = gw.execute(self.call, "tok-op")
        r2 = gw.execute(self.call, "tok-op")
        self.assertEqual((r1.state, r1.refusal_code), ("refused", "E_COMMAND_UNKNOWN"))
        self.assertTrue(r2.replayed)
        self.assertEqual(refusing.calls, 1)

    def test_failed_exit_is_failed_not_succeeded(self):
        failing = FakeExecutor(ExecutionOutcome(exit_code=1, duration_ms=2,
                                                argv=("fake-cli",), message="boom"))
        gw = Gateway([SPEC], failing, self.repo, roles={"tok-op": "vector_operator"})
        result = gw.execute(self.call, "tok-op")
        self.assertEqual(result.state, "failed")
        self.assertEqual(result.exit_code, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
```

---

## 9. TypeScript wire contracts

The declarations mirror the SQL and Python boundaries so a console/CLI can consume the conductor
without re-deriving shapes: `EpisodeStatus`, `Verdict`, `RefusalCode`, `Role`, `App`, `TaskEnvelope`,
`ArtSpec`, `Handoff`, `ToolCall`, `ToolResult`, `ArtifactRecord`, `GateReport`, `CritiqueReport`,
`VerificationVerdict`, `EpisodeView`, `HttpApi`. `check.ts` is a compile-only fixture: it constructs
one valid value of each shape and an exhaustive state map. It has no runtime and imports nothing but
types, so it cannot drift into a second source of truth.

**File: ```contracts.d.ts```**

```ts
/**
 * Forge Conductor skeleton — shared wire contracts (types only, no runtime).
 * Generated as an executable-skeleton artefact for execution-wave task-09.
 * These declarations mirror the SQLite-free Postgres DDL in 02-FORGE-SKELETON.md
 * and the Python gateway in the same document; they are the boundary between
 * the conductor (Python) and any TypeScript surface (console/CLI/SSE).
 */

export type EpisodeStatus =
  | "intake" | "briefed" | "planned" | "context_ready" | "executing"
  | "verifying" | "critiquing" | "needs_human" | "paused" | "accepted"
  | "rejected" | "refused" | "failed" | "cancelled" | "quarantined";

export type Verdict = "pass" | "pass_with_notes" | "reject" | "needs_human" | "unverified";

export type RefusalCode =
  | "E_BRIEF_MISSING" | "E_RIGHTS_MISSING" | "E_ROOT_DENIED" | "E_INPLACE_WRITE"
  | "E_COMMAND_UNKNOWN" | "E_PARAM_REJECTED" | "E_APP_DRIFT" | "E_CATALOGUE_STALE"
  | "E_DOCUMENT_STATE" | "E_ARTIFACT_MISSING" | "E_ARTIFACT_EMPTY" | "E_SOURCE_MUTATED"
  | "E_GATE_FAILED" | "E_GATE_MISSING" | "E_GATE_VACUOUS" | "E_UPSCALE_LIMIT"
  | "E_TEXT_TRACE_FORBIDDEN" | "E_WHITE_MODE_REFUSED" | "E_VISION_UNAVAILABLE"
  | "E_CRITIQUE_UNGROUNDED" | "E_BUDGET_EXCEEDED" | "E_TIMEOUT"
  | "E_PUBLISH_NOT_APPROVED" | "E_SURFACE_UNVERIFIABLE" | "E_MEMORY_CONFLICT"
  | "E_EVAL_EMPTY" | "E_UNSUPPORTED_SURFACE";

export type Role =
  | "conductor" | "art_director" | "vector_operator" | "raster_operator"
  | "print_verifier" | "visual_critic" | "memory_curator";

export type App = "vectorcraft" | "photocraft" | "designcraft" | "effectcraft" | "filmcraft";

export interface TaskEnvelope {
  readonly schema_version: "1.0";
  readonly episode_id: string;
  readonly account_id: number;
  readonly brief: {
    readonly text: string;
    readonly deliverable: string;
    readonly quantity: number;
    readonly deadline_utc: string | null;
  };
  readonly task_family: string;
  readonly target: {
    readonly app: App;
    readonly app_version: string;
    readonly catalogue_hash: `sha256:${string}`;
    readonly product_type: string;
  };
  readonly inputs: ReadonlyArray<{
    readonly path: string;
    readonly sha256: string;
    readonly rights_id: string;
  }>;
  readonly constraints: {
    readonly print_width_in: number;
    readonly dpi: number;
    readonly max_upscale: number;
    readonly background: "transparent" | "solid";
    readonly provider: string;
    readonly template_id: string | null;
  };
  readonly budget: {
    readonly max_attempts: number;
    readonly max_tokens: number;
    readonly max_wall_s: number;
    readonly max_cents: number;
  };
  readonly approval: { readonly publish_allowed: boolean; readonly approval_token: string | null };
  readonly mode: "assisted" | "replay" | "draft";
}

export interface ArtSpec {
  readonly schema_version: "1.0";
  readonly episode_id: string;
  readonly deliverable: string;
  readonly canvas: { readonly width_px: number; readonly height_px: number; readonly dpi: number; readonly color_space: "sRGB" | "CMYK" };
  readonly composition: {
    readonly subject_bbox_target: readonly [number, number, number];
    readonly safe_margin_in: number;
    readonly hierarchy: ReadonlyArray<string>;
    readonly background: "transparent" | "solid";
  };
  readonly palette: ReadonlyArray<{ readonly hex: string; readonly role: string; readonly brand_fact_id: string }>;
  readonly typography: ReadonlyArray<{ readonly role: string; readonly family: string; readonly licensed: boolean; readonly treatment: string }>;
  readonly constraints: {
    readonly no_white_residual: boolean;
    readonly no_traced_text: boolean;
    readonly min_edge_hardness: number;
    readonly provider_safe_zone: readonly [number, number];
  };
  readonly success_criteria: ReadonlyArray<
    | { readonly id: string; readonly type: "domain_gate"; readonly runner: string; readonly required: Record<string, boolean | number> }
    | { readonly id: string; readonly type: "rubric"; readonly min: number; readonly reviewers: "human" }
  >;
  readonly brand_fact_ids: ReadonlyArray<string>;
  readonly source_case_ids: ReadonlyArray<string>;
}

export interface Handoff<TKind extends string, TPayload> {
  readonly handoff_id: string;
  readonly episode_id: string;
  readonly parent_handoff_id: string | null;
  readonly kind: TKind;
  readonly produced_by: Role;
  readonly consumed_by: Role;
  readonly schema_version: "1.0";
  readonly deadline_s: number;
  readonly budget: { readonly tokens: number; readonly wall_s: number };
  readonly input_hashes: ReadonlyArray<string>;
  readonly payload: TPayload;
  readonly refusal: RefusalCode | null;
}

export interface ToolCall {
  readonly episode_id: string;
  readonly tool_id: string;
  readonly cmd_id: string | null;
  readonly params: Readonly<Record<string, unknown>>;
  readonly paths: ReadonlyArray<string>;
  readonly input_hashes: ReadonlyArray<string>;
}

export interface ToolResult {
  readonly idempotency_key: `sha256:${string}`;
  readonly state: "succeeded" | "failed" | "refused";
  readonly replayed: boolean;
  readonly exit_code: number | null;
  readonly refusal_code: RefusalCode | null;
  readonly artifacts: ReadonlyArray<ArtifactRecord>;
  readonly message: string;
}

export interface ArtifactRecord {
  readonly episode_id: string;
  readonly kind: "input" | "svg" | "raster" | "pdf" | "report" | "preview" | "video";
  readonly path: string;
  readonly sha256: string;
  readonly bytes: number;
  readonly width: number | null;
  readonly height: number | null;
  readonly dpi: number | null;
  readonly format: string | null;
}

export interface GateReport {
  readonly episode_id: string;
  readonly artifact_sha256: string;
  readonly runner: string;
  readonly runner_version: string;
  readonly ok: boolean;
  readonly checks: Readonly<Record<string, { readonly value: unknown; readonly pass: boolean }>>;
  readonly non_vacuous: Readonly<Record<string, number | boolean>>;
  readonly source_mutation: {
    readonly input_sha256_before: string;
    readonly input_sha256_after: string;
    readonly mutated: boolean;
  };
}

export interface CritiqueReport {
  readonly episode_id: string;
  readonly artifact_sha256: string;
  readonly critic_prompt_version: string;
  readonly model_id: string;
  readonly blinded_to: ReadonlyArray<"exit_code" | "gate_report" | "operator_claims">;
  readonly dimensions: Readonly<Record<
    "brief_fit" | "hierarchy" | "typography" | "colour" | "print_safety",
    {
      readonly score: 1 | 2 | 3 | 4 | 5;
      readonly evidence: ReadonlyArray<{
        readonly region: readonly [number, number, number, number];
        readonly crop_path: string;
        readonly observation: string;
      }>;
    }
  >>;
  readonly defects: ReadonlyArray<{ readonly severity: "minor" | "major"; readonly where: string; readonly issue: string; readonly fix_hint: string }>;
  readonly confidence: number;
  readonly unseen: ReadonlyArray<string>;
  readonly verdict: "pass" | "pass_with_notes" | "reject" | "unverifiable";
}

export interface VerificationVerdict {
  readonly episode_id: string;
  readonly artifact_sha256: string;
  readonly verdict: Verdict;
  readonly rungs: {
    readonly process: boolean | null;
    readonly artifact: boolean | null;
    readonly domain: boolean | null;
    readonly render: boolean | null;
    readonly critic: "pass" | "pass_with_notes" | "reject" | "unverifiable" | null;
    readonly human: "accept" | "reject" | null;
  };
  readonly reason_codes: ReadonlyArray<RefusalCode | string>;
  readonly human_required: boolean;
}

export interface EpisodeView {
  readonly id: string;
  readonly status: EpisodeStatus;
  readonly verdict: Verdict | null;
  readonly task_family: string;
  readonly mode: "assisted" | "replay" | "draft";
  readonly created_at: string;
  readonly finished_at: string | null;
  readonly reason_codes: ReadonlyArray<string>;
}

/** Minimal HTTP surface of the skeleton (loopback only). */
export interface HttpApi {
  readonly "POST /v1/episodes": { request: TaskEnvelope; response: { episode_id: string; status: EpisodeStatus } };
  readonly "GET /v1/episodes/:id": { response: EpisodeView };
  readonly "POST /v1/tool-calls": { request: ToolCall; response: ToolResult };
  readonly "POST /v1/episodes/:id/approve": { request: { artifact_sha256: string; scope: "publish" | "promotion"; token: string }; response: { approved: boolean } };
  readonly "GET /healthz": { response: { ok: boolean; db: boolean; model_credential: boolean } };
}
```

**File: ```check.ts```**

```ts
/**
 * Compile-only check for the Forge skeleton wire contracts.
 * Run: tsc --noEmit --strict contracts.d.ts check.ts
 * It must fail compilation if a required field disappears or a union drifts.
 */
import type {
  ArtSpec, CritiqueReport, EpisodeStatus, EpisodeView, GateReport, Handoff,
  RefusalCode, TaskEnvelope, ToolCall, ToolResult, Verdict, VerificationVerdict,
} from "./contracts";

const allStates: Record<EpisodeStatus, true> = {
  intake: true, briefed: true, planned: true, context_ready: true, executing: true,
  verifying: true, critiquing: true, needs_human: true, paused: true, accepted: true,
  rejected: true, refused: true, failed: true, cancelled: true, quarantined: true,
};

const terminal: ReadonlyArray<EpisodeStatus> = ["accepted", "rejected", "refused", "failed", "cancelled", "quarantined"];

const envelope: TaskEnvelope = {
  schema_version: "1.0",
  episode_id: "2f1c6a6e-0d3a-4f7f-9d8e-1b2c3d4e5f60",
  account_id: 1,
  brief: { text: "8in front print, transparent white", deliverable: "dtg_front_print_master", quantity: 1, deadline_utc: null },
  task_family: "ai_badge_trace_v1",
  target: { app: "vectorcraft", app_version: "0.21.1", catalogue_hash: `sha256:${"a".repeat(64)}`, product_type: "apparel" },
  inputs: [{ path: "inbox/badge.png", sha256: "b".repeat(64), rights_id: "rights_0007" }],
  constraints: { print_width_in: 8, dpi: 300, max_upscale: 2.5, background: "transparent", provider: "fourthwall", template_id: null },
  budget: { max_attempts: 3, max_tokens: 80000, max_wall_s: 5400, max_cents: 0 },
  approval: { publish_allowed: false, approval_token: null },
  mode: "assisted",
};

const spec: ArtSpec = {
  schema_version: "1.0",
  episode_id: envelope.episode_id,
  deliverable: envelope.brief.deliverable,
  canvas: { width_px: 2400, height_px: 3000, dpi: 300, color_space: "sRGB" },
  composition: { subject_bbox_target: [0.5, 0.5, 0.62], safe_margin_in: 0.5, hierarchy: ["wordmark", "tagline"], background: "transparent" },
  palette: [{ hex: "#1B2A41", role: "primary", brand_fact_id: "bf_012" }],
  typography: [{ role: "wordmark", family: "FONT-ABC", licensed: true, treatment: "retype_outlined" }],
  constraints: { no_white_residual: true, no_traced_text: true, min_edge_hardness: 0.9, provider_safe_zone: [0.04, 0.04] },
  success_criteria: [
    { id: "gates", type: "domain_gate", runner: "craft_trace", required: { ok: true } },
    { id: "fit", type: "rubric", min: 4, reviewers: "human" },
  ],
  brand_fact_ids: ["bf_012"],
  source_case_ids: [],
};

const gate: GateReport = {
  episode_id: envelope.episode_id,
  artifact_sha256: "c".repeat(64),
  runner: "craft_trace",
  runner_version: "1.0.0",
  ok: true,
  checks: { dpi: { value: 300, pass: true } },
  non_vacuous: { retype_boxes: 2 },
  source_mutation: { input_sha256_before: "b".repeat(64), input_sha256_after: "b".repeat(64), mutated: false },
};

const critique: CritiqueReport = {
  episode_id: envelope.episode_id,
  artifact_sha256: gate.artifact_sha256,
  critic_prompt_version: "critic-v0.3",
  model_id: "deepseek-flash",
  blinded_to: ["exit_code", "gate_report", "operator_claims"],
  dimensions: {
    brief_fit: { score: 4, evidence: [{ region: [0, 0, 1, 1], crop_path: "build/thumb.png", observation: "subject centred, wordmark legible" }] },
    hierarchy: { score: 4, evidence: [{ region: [0.08, 0.1, 0.92, 0.38], crop_path: "build/h.png", observation: "wordmark first, tagline second" }] },
    typography: { score: 3, evidence: [{ region: [0.3, 0.55, 0.7, 0.62], crop_path: "build/t.png", observation: "tracking tight at print scale" }] },
    colour: { score: 5, evidence: [{ region: [0, 0, 1, 1], crop_path: "build/c.png", observation: "palette matches brand facts" }] },
    print_safety: { score: 4, evidence: [{ region: [0, 0, 0.06, 0.06], crop_path: "build/m.png", observation: "subject inside safe margin" }] },
  },
  defects: [{ severity: "minor", where: "tagline", issue: "tracking", fix_hint: "increase 2%" }],
  confidence: 0.72,
  unseen: ["no reference artwork"],
  verdict: "pass_with_notes",
};

const verdict: VerificationVerdict = {
  episode_id: envelope.episode_id,
  artifact_sha256: gate.artifact_sha256,
  verdict: "pass_with_notes",
  rungs: { process: true, artifact: true, domain: true, render: true, critic: "pass_with_notes", human: null },
  reason_codes: ["E_CRITIQUE_NOTES"],
  human_required: false,
};

const handoff: Handoff<"command_batch", ToolCall> = {
  handoff_id: "a".repeat(8),
  episode_id: envelope.episode_id,
  parent_handoff_id: null,
  kind: "command_batch",
  produced_by: "art_director",
  consumed_by: "vector_operator",
  schema_version: "1.0",
  deadline_s: 900,
  budget: { tokens: 4000, wall_s: 600 },
  input_hashes: [],
  payload: { episode_id: envelope.episode_id, tool_id: "craft.run", cmd_id: "imageTrace.make", params: { palette: 6 }, paths: [], input_hashes: [] },
  refusal: null,
};

const result: ToolResult = {
  idempotency_key: `sha256:${"d".repeat(64)}`,
  state: "succeeded",
  replayed: false,
  exit_code: 0,
  refusal_code: null,
  artifacts: [],
  message: "",
};

const view: EpisodeView = {
  id: envelope.episode_id,
  status: "accepted",
  verdict: "pass",
  task_family: envelope.task_family,
  mode: "assisted",
  created_at: new Date(0).toISOString(),
  finished_at: null,
  reason_codes: [],
};

const refusals: ReadonlyArray<RefusalCode> = [
  "E_ROOT_DENIED", "E_COMMAND_UNKNOWN", "E_GATE_MISSING", "E_SOURCE_MUTATED",
  "E_PUBLISH_NOT_APPROVED", "E_BUDGET_EXCEEDED",
];

// Touch every binding so noUnusedLocals does not erase the check.
export const checked = { allStates, terminal, envelope, spec, gate, critique, verdict, handoff, result, view, refusals } as const;
export const verdictType: Verdict = verdict.verdict;
```
---

## 10. Execution evidence (this task, 2026-11-05)

All database work ran against a throwaway database `forge_scratch` on the existing
`postgres:16` container (`PostgreSQL 16.15`), created and dropped inside this task. The `pod` database
was never connected to. Python ran locally (3.14.7); TypeScript ran with the repo's installed
compiler (5.9.3, `node_modules/typescript/bin/tsc`) read-only.

| # | Check | Command (abridged) | Observed |
|---|---|---|---|
| E1 | DDL applies | `psql -v ON_ERROR_STOP=1 -d forge_scratch -f forge_schema.sql` | `exit=0` |
| E2 | DDL re-applies (idempotent) | same command, second time | `exit=0`, no errors |
| E3 | SQL assertions | `psql -v ON_ERROR_STOP=1 -d forge_scratch -f forge_tests.sql` | `exit=0`; `T01 PASS tables=13 edges=36` … `T18 PASS detected forged event`; `ALL SQL ASSERTIONS PASSED` |
| E4 | Queue concurrency | worker A claims + `pg_sleep(3)`; worker B claims immediately | `A_job=4 B_job=5 elapsed_ms=592`; `T-SKIPLOCK PASS` |
| E5 | Python compiles | `python -m py_compile forge_gateway.py test_forge_gateway.py` | `exit=0` |
| E6 | Python tests | `python -m unittest -v test_forge_gateway.py` | `Ran 33 tests in 0.026s` — `OK` |
| E7 | TS contracts type-check | `tsc --noEmit --strict … contracts.d.ts check.ts` | `exit=0` |
| E8 | TS negative check | same with `runner_version` removed from `GateReport` literal | `error TS2741: Property 'runner_version' is missing …`; `exit=2` (expected) |
| E9 | Scratch cleanup | `DROP DATABASE forge_scratch` | `exit=0` |

**Failure modes exercised, not just the happy path:** illegal transition (twice), unknown state,
terminal re-entry, duplicate submission, duplicate tool key, duplicate promotion, tampered event,
forged event, refused row without code, malformed hash, zero-byte artifact, over-cap budget (and its
rollback), double-used approval, finish-before-claim, role denial, command deny, unknown tool, path
traversal, sibling-root escape, executor exit≠0, executor refusal, missing gate, vacuous gate, critic
absent/reject, human-required, and a negative TS compile.

**No production changes.** `git status` shows modifications/new files from *other* execution-wave seats
(skills, errata, diagrams, other research files); this task wrote only the two deliverables named in
the task. No file under `blueprint/`, `pod_pipeline/`, `deploy/`, `src/` or `server/` was edited by this
task, and no service, unit or database in production was changed.

---

## 11. Unresolved gaps

| ID | Gap | Impact | How to close |
|---|---|---|---|
| G-01 | `Gateway` does `find → execute → insert`; two concurrent identical calls can both reach the executor. The DB unique key is the real guard. | A crash between execute and insert, or a race, can double-execute a side effect. | Production `Repo.store` must catch `unique_violation`, re-read the winner and return it; add an integration test with two real connections. |
| G-02 | Event hashes use PostgreSQL 16 `jsonb::text` canonicalisation. | A PG major upgrade could change rendering and invalidate old chains. | Pin `server_version` in the chain record (or hash a canonical string produced in application code) before production. |
| G-03 | Guard *labels* in `forge_transition` are documentation; only topology and verdict rules are enforced. | A conductor bug can skip "retrieval_receipt present" and the DB will not notice. | Enforce guards at handoff creation (e.g. require a `forge_handoff` row per guard) or add guard validation to the transition function. |
| G-04 | Grants/roles are commented, never applied; no privilege test. Shared cluster roles were not created. | Least-privilege contract is unproven. | Apply grants on a dedicated database instance; test that `forge_app` cannot read `pod` and cannot UPDATE evidence tables. |
| G-05 | No migration tool or versioned schema (CREATE IF NOT EXISTS only). | First real ALTER is untested; drift is possible. | Add `schema_version` table + forward-only migrations; test upgrade from v1 to v2 and a failed-migration rollback. |
| G-06 | Python `Repo`/`Executor` protocols are not wired to psycopg or a real CLI. | Integration behaviour (types, transactions, connection loss) is unproven. | Implement the psycopg adapter in the next task and run the same 33 tests against it. |
| G-07 | No HTTP server implementation; the route table is a TS type only. | The conductor boundary is specified, not running. | FastAPI (or equivalent) with the four `/v1` routes + `/healthz`; contract tests. |
| G-08 | Approval token issuance/signing is unspecified; the DB consumes a hash. | Anyone who can insert an approval row can authorise a publish. | Define issuer, signature/expiry policy and an audit trail; keep DB insert permission curator/owner-only. |
| G-09 | Only two concurrent workers were tested, on one host, with `pg_sleep`. | Lease recovery, clock skew and long-running claims are untested. | Add lease-expiry, crash-without-release and clock-skew tests; consider `pg_stat_activity` reaping. |
| G-10 | Event payload cap 32 KB; large refusal context must be digested elsewhere. | Truncation could lose evidence if callers ignore the cap. | Store a `refusal_digest` + log path instead of large payloads; test the boundary. |
| G-11 | Python `build_verdict` does not look at human-required for `pass_with_notes` vs `needs_human` combinations exhaustively. | Some evidence combinations are unenumerated. | Property-based test over the cartesian product of rungs. |
| G-12 | Promotion *policy* (3 successes, regression, sign-off) is not implemented; only the one-active-version guard exists. | Promotion cannot be exercised end-to-end from SQL alone. | Implement `forge_promote_skill()` per `04` §8.5 / `06-LEARNING…`; simulation is task-11. |
| G-13 | Retrieval, brand facts, lessons, conflicts, role tokens are deferred tables. | Phase 2–3 memory is not covered by this skeleton. | Add when retrieval/eval work starts; reuse the same append-only/versioning patterns. |
| G-14 | TypeScript contracts are compile-checked but not generated from or against the Python code. | Two copies can drift. | Codegen from JSON Schema, or a contract test that serialises a Python object and validates it with the TS shape (e.g. `zod`). |
| G-15 | No Craft CLI was executed; `Executor` semantics (real stdout envelope) remain task-08's question. | The gateway is tested only with a fake executor. | Wire task-08's real CLI adapter and replay its negative fixtures through the gateway. |
| G-16 | `pgvector` and embeddings are not used (stock `postgres:16`). | Retrieval ranking is lexical-only if added now. | Test `CREATE EXTENSION vector` on a scratch DB, then decide. |

---

## 12. Traceability: design §, skeleton artefact, proof

| `04-HARNESS-DESIGN` | Skeleton artefact | Proof |
|---|---|---|
| §3 architecture, §4 roles/handoffs | `forge_handoff` + `forge_claim_handoff` | `T10` |
| §5 data contracts (episode/event/tool/artifact/gate/critique/eval/skill/job/budget/approval) | 13 tables in §3 | `T01`, `T07`–`T14` |
| §5.2 ledger tables | shipped subset + deferral table in §2 | `[GAP]` G-13 |
| §5.2 hash-chained ledger | `forge_event` + append/verify functions + append-only trigger | `T05`, `T06`, `T18` |
| §6 tool layer (allowlist, roots, idempotency, refusal codes) | Python `Gateway` + `ToolSpec`/`ToolCall` + 35-code taxonomy | 33 Python tests |
| §6.6 refusal codes | `TERMINAL_REFUSALS` / `RETRYABLE_REFUSALS` + SQL-raised codes | refusal tests + `T12`/`T13` |
| §7 evidence ladder / verdict rules | `build_verdict(Evidence)` | 9 verdict tests |
| §7.2 anti-trust (source mutation, vacuous gates) | verdict rules + `E_SOURCE_MUTATED`/`E_GATE_VACUOUS` | verdict tests |
| §8 memory/promotion/rollback | `forge_skill` states + one-active index | `T11`; policy deferred (G-12) |
| §9 evaluation | `forge_eval` one-per-arm | `T01` (table), `[GAP]` G-13 |
| §10 hosting/security | grants template + comments | `[GAP]` G-04 |
| §12 state machine | 36-edge seed + guarded transition + Python mirror | `T02`–`T05`, `T15`; Python transition tests |
| §14 questions | unchanged; this task answers only the "is the skeleton runnable" question | — |

---

## 13. How to reproduce from scratch

```bash
# 1. throwaway database (never the production pod DB)
psql -d postgres -c "CREATE DATABASE forge_scratch"
psql -v ON_ERROR_STOP=1 -d forge_scratch -f forge_schema.sql   # twice = idempotent proof
psql -v ON_ERROR_STOP=1 -d forge_scratch -f forge_tests.sql    # 18 assertions

# 2. python (stdlib only, any 3.11+)
python -m py_compile forge_gateway.py test_forge_gateway.py
python -m unittest -v test_forge_gateway.py

# 3. typescript (repo compiler)
node node_modules/typescript/bin/tsc --noEmit --strict \
  --target ES2022 --module ESNext --moduleResolution bundler contracts.d.ts check.ts

# 4. cleanup
psql -d postgres -c "DROP DATABASE forge_scratch"
```

The code lives **in this document** (no side files were committed, per the task's write scope). Copy
each fenced block to the filename named in its breadcrumb before running.

---

## 14. Non-goals of this task

- No service, daemon, systemd unit, container or HTTP listener was created.
- No production database, table, role or migration was changed.
- No Craft CLI was executed and no artifact was verified; `Executor` is exercised only by a test double
  (a permitted double: external process boundary, never the unit under test).
- No promotion/evaluation policy was implemented; only its database guard.
- No claim that the design is implemented: this is the smallest executable skeleton that makes the
  design's invariants testable.
