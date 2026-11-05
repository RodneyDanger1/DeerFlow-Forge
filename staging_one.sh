#!/bin/bash
set -u
docker rm -f forge-pg-test >/dev/null 2>&1 || true
docker run -d --rm --name forge-pg-test -e POSTGRES_PASSWORD=scratch -p 127.0.0.1:55439:5432 postgres:16-alpine >/dev/null
for i in $(seq 1 30); do docker exec forge-pg-test pg_isready -U postgres >/dev/null 2>&1 && break; sleep 1; done
docker cp /tmp/schema_forge.sql forge-pg-test:/tmp/schema_forge.sql
docker exec -i forge-pg-test psql -U postgres -v ON_ERROR_STOP=1 -f /tmp/schema_forge.sql >/dev/null 2>&1
cd /opt/pod-pipeline-staging
FORGE_TEST_DSN='postgresql://postgres:scratch@127.0.0.1:55439/postgres' .venv/bin/python -m pytest tests/test_forge_repo.py::RepoTests::test_transition_appends_exactly_one_event -vv 2>&1 | tail -35
docker rm -f forge-pg-test >/dev/null 2>&1 || true