#!/bin/bash
set -u
docker cp /tmp/schema_forge.sql forge-pg-test:/tmp/schema_forge.sql
docker exec -i forge-pg-test psql -U postgres -v ON_ERROR_STOP=1 -f /tmp/schema_forge.sql >/tmp/forge_reapply.log 2>&1
echo "reapply=$?"
docker exec -i forge-pg-test psql -U postgres -Atc "select prosrc from pg_proc where proname='forge_claim_job';" | grep -n "v.id IS NULL" || true
cd /opt/pod-pipeline-staging
FORGE_TEST_DSN='postgresql://postgres:scratch@127.0.0.1:55439/postgres' .venv/bin/python tests/forge_schema_assertions.py 2>&1
echo "assert=$?"