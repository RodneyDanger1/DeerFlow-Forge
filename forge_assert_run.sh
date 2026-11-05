#!/bin/bash
set -u
cd /opt/pod-pipeline-staging
FORGE_TEST_DSN='postgresql://postgres:scratch@127.0.0.1:55439/postgres' .venv/bin/python tests/forge_schema_assertions.py 2>&1
echo "assert=$?"