-- DeerFlow pod pipeline. Matches the SQL in pod_pipeline/db.py and tests/conftest.py.
-- Apply as the database owner (docker image user pod_app, a superuser inside that container):
--   docker exec -i pod-postgres psql -U pod_app -d pod -v ON_ERROR_STOP=1 < sql/schema.sql
--
-- Tenant insert (POD_CREDENTIAL_KEY is the pgp passphrase, never the Fourthwall secret):
--   INSERT INTO users_saas_accounts
--     (display_name, tenant_token_hash, sync_domain, fourthwall_api_user, fourthwall_api_secret_enc)
--   VALUES (
--     'Shop', encode(sha256('rotate-me'), 'hex'), 'shop.example',
--     'api-user', pgp_sym_encrypt('api-secret', 'the POD_CREDENTIAL_KEY value')
--   );

BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE OR REPLACE FUNCTION pod_touch_updated_at() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at := now();
    RETURN NEW;
END;
$$;

CREATE TABLE IF NOT EXISTS users_saas_accounts (
    id                          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    display_name                text NOT NULL,
    tenant_token_hash           text NOT NULL,
    sync_domain                 text,
    fourthwall_api_user         text,
    fourthwall_api_secret_enc   bytea,
    auto_publish                boolean NOT NULL DEFAULT false,
    status                      text NOT NULL DEFAULT 'active',
    created_at                  timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT users_saas_accounts_token_len CHECK (char_length(tenant_token_hash) = 64),
    CONSTRAINT users_saas_accounts_status CHECK (status IN ('active', 'revoked')),
    CONSTRAINT users_saas_accounts_domain CHECK (
        sync_domain IS NULL OR sync_domain ~ '^[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS users_saas_accounts_token_idx
    ON users_saas_accounts (tenant_token_hash);

CREATE UNIQUE INDEX IF NOT EXISTS users_saas_accounts_domain_idx
    ON users_saas_accounts (sync_domain)
    WHERE sync_domain IS NOT NULL AND status = 'active';

CREATE TABLE IF NOT EXISTS ingested_assets (
    id                  bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    account_id          bigint NOT NULL REFERENCES users_saas_accounts (id) ON DELETE RESTRICT,
    source_kind         text NOT NULL DEFAULT 'directory',
    source_path         text NOT NULL,
    original_filename   text NOT NULL,
    sha256              text NOT NULL,
    byte_size           bigint NOT NULL,
    mime_type           text,
    width_px            integer,
    height_px           integer,
    source_dpi          integer,
    color_space         text NOT NULL DEFAULT 'unknown',
    has_alpha           boolean,
    status              text NOT NULL DEFAULT 'pending',
    trace_state         text NOT NULL DEFAULT 'pending',
    trace_bounds        jsonb,
    created_at          timestamptz NOT NULL DEFAULT now(),
    updated_at          timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT ingested_assets_sha CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    CONSTRAINT ingested_assets_size CHECK (byte_size > 0),
    CONSTRAINT ingested_assets_kind CHECK (source_kind IN ('directory', 'webhook')),
    CONSTRAINT ingested_assets_dims CHECK (
        (width_px IS NULL OR width_px > 0) AND (height_px IS NULL OR height_px > 0)
    ),
    CONSTRAINT ingested_assets_dpi CHECK (source_dpi IS NULL OR source_dpi > 0),
    CONSTRAINT ingested_assets_status CHECK (
        status IN ('pending', 'queued', 'processing', 'processed', 'failed', 'quarantined')
    ),
    CONSTRAINT ingested_assets_trace CHECK (
        trace_state IN ('pending', 'tracing', 'traced', 'raster_fallback', 'trace_failed')
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS ingested_assets_account_sha_idx
    ON ingested_assets (account_id, sha256);

CREATE INDEX IF NOT EXISTS ingested_assets_status_updated_idx
    ON ingested_assets (status, updated_at);

CREATE INDEX IF NOT EXISTS ingested_assets_source_path_idx
    ON ingested_assets (source_path);

DROP TRIGGER IF EXISTS ingested_assets_touch ON ingested_assets;
CREATE TRIGGER ingested_assets_touch
    BEFORE UPDATE ON ingested_assets
    FOR EACH ROW EXECUTE FUNCTION pod_touch_updated_at();

CREATE TABLE IF NOT EXISTS processing_jobs (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_id          uuid NOT NULL,
    account_id      bigint NOT NULL REFERENCES users_saas_accounts (id) ON DELETE RESTRICT,
    asset_id        bigint NOT NULL REFERENCES ingested_assets (id) ON DELETE RESTRICT,
    product_type    text NOT NULL,
    module          text NOT NULL,
    step_name       text NOT NULL,
    step_index      integer NOT NULL,
    attempt         integer NOT NULL DEFAULT 1,
    fallback_tier   integer NOT NULL DEFAULT 0,
    status          text NOT NULL,
    pid             integer,
    argv            text[],
    exit_code       integer,
    error_digest    text,
    log_path        text,
    output_path     text,
    started_at      timestamptz,
    finished_at     timestamptz,
    CONSTRAINT processing_jobs_product CHECK (
        product_type IN ('apparel', 'knitwear', 'accessories', 'odd_3d', 'stationery')
    ),
    CONSTRAINT processing_jobs_module CHECK (
        module IN ('orchestrator', 'vectorcraft', 'photocraft', 'designcraft', 'effectcraft', 'filmcraft')
    ),
    CONSTRAINT processing_jobs_status CHECK (status IN ('queued', 'running', 'succeeded', 'failed')),
    CONSTRAINT processing_jobs_attempt CHECK (attempt >= 1),
    CONSTRAINT processing_jobs_tier CHECK (fallback_tier >= 0),
    CONSTRAINT processing_jobs_step CHECK (step_index >= 0),
    CONSTRAINT processing_jobs_time_order CHECK (
        finished_at IS NULL OR started_at IS NULL OR finished_at >= started_at
    ),
    CONSTRAINT processing_jobs_digest_budget CHECK (
        error_digest IS NULL OR char_length(error_digest) <= 8000
    )
);

-- One live orchestrator run per asset + product. enqueue_run depends on this raising unique_violation.
CREATE UNIQUE INDEX IF NOT EXISTS processing_jobs_one_live_run
    ON processing_jobs (asset_id, product_type)
    WHERE module = 'orchestrator' AND status IN ('queued', 'running');

CREATE INDEX IF NOT EXISTS processing_jobs_run_idx
    ON processing_jobs (run_id);

CREATE INDEX IF NOT EXISTS processing_jobs_queued_idx
    ON processing_jobs (id)
    WHERE module = 'orchestrator' AND status = 'queued';

CREATE TABLE IF NOT EXISTS fourthwall_products (
    id                  bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    account_id          bigint NOT NULL REFERENCES users_saas_accounts (id) ON DELETE RESTRICT,
    asset_id            bigint NOT NULL REFERENCES ingested_assets (id) ON DELETE RESTRICT,
    run_id              uuid,
    product_type        text NOT NULL,
    fw_template_id      text,
    media_id            text,
    media_file_url      text,
    fw_product_id       text,
    fw_slug             text,
    variants            jsonb NOT NULL DEFAULT '[]'::jsonb,
    skus                text[] NOT NULL DEFAULT '{}',
    publish_state       text NOT NULL DEFAULT 'draft',
    last_error          text,
    published_at        timestamptz,
    updated_at          timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT fourthwall_products_natural UNIQUE (account_id, asset_id, product_type),
    CONSTRAINT fourthwall_products_type CHECK (
        product_type IN ('apparel', 'knitwear', 'accessories', 'odd_3d', 'stationery')
    ),
    CONSTRAINT fourthwall_products_state CHECK (
        publish_state IN ('draft', 'processing', 'active', 'failed', 'needs_manual_upload')
    )
);

CREATE INDEX IF NOT EXISTS fourthwall_products_fw_product_idx
    ON fourthwall_products (fw_product_id)
    WHERE fw_product_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS fourthwall_products_media_idx
    ON fourthwall_products (media_id)
    WHERE media_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS fourthwall_products_state_idx
    ON fourthwall_products (publish_state);

DROP TRIGGER IF EXISTS fourthwall_products_touch ON fourthwall_products;
CREATE TRIGGER fourthwall_products_touch
    BEFORE UPDATE ON fourthwall_products
    FOR EACH ROW EXECUTE FUNCTION pod_touch_updated_at();

CREATE TABLE IF NOT EXISTS agent_sync_logs (
    id                  bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    account_id          bigint REFERENCES users_saas_accounts (id) ON DELETE RESTRICT,
    direction           text NOT NULL,
    channel             text NOT NULL,
    event_type          text NOT NULL,
    external_event_id   text,
    http_method         text,
    url                 text,
    status_code         integer,
    success             boolean,
    duration_ms         integer,
    payload             jsonb,
    run_id              uuid,
    fw_product_row_id   bigint REFERENCES fourthwall_products (id) ON DELETE RESTRICT,
    created_at          timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT agent_sync_logs_direction CHECK (direction IN ('inbound', 'outbound')),
    CONSTRAINT agent_sync_logs_duration CHECK (duration_ms IS NULL OR duration_ms >= 0),
    CONSTRAINT agent_sync_logs_payload_budget CHECK (
        payload IS NULL OR octet_length(payload::text) <= 32768
    )
);

-- log_sync uses ON CONFLICT DO NOTHING. Webhook retries share external_event_id; null ids never collide.
CREATE UNIQUE INDEX IF NOT EXISTS agent_sync_logs_external_event_idx
    ON agent_sync_logs (external_event_id)
    WHERE external_event_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS agent_sync_logs_account_idx
    ON agent_sync_logs (account_id, id DESC);

CREATE INDEX IF NOT EXISTS agent_sync_logs_run_idx
    ON agent_sync_logs (run_id)
    WHERE run_id IS NOT NULL;

COMMIT;
