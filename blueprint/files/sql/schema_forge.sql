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
    -- A null composite is not SQL NULL in every client; make empty explicit.
    IF v.id IS NULL THEN
        RETURN NULL;
    END IF;
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
    -- A null composite is not SQL NULL in every client; make empty explicit.
    IF v.id IS NULL THEN
        RETURN NULL;
    END IF;
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
