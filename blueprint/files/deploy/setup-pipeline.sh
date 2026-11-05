#!/usr/bin/env bash
# Install the DeerFlow pod pipeline onto a Debian/Ubuntu VPS.
# The tree must already be at /opt/pod-pipeline (this script lives in deploy/).
# Re-running is safe: env, products.json, and vendor CLIs already in bin/ are kept.
set -euo pipefail
trap 'echo "setup-pipeline.sh failed at line $LINENO" >&2' ERR
umask 027

ROOT="${POD_ROOT:-/opt/pod-pipeline}"
APP_USER="${POD_USER:-pod}"
APP_GROUP="${POD_GROUP:-pod}"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "setup-pipeline.sh must run as root" >&2
  exit 1
fi
if [[ ! -f "$ROOT/sql/schema.sql" || ! -f "$ROOT/deploy/compose.yml" ]]; then
  echo "expected the pipeline tree at $ROOT" >&2
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends \
  ca-certificates curl \
  python3 python3-venv \
  imagemagick potrace ghostscript ffmpeg

# Docker is required, but never installed over an existing engine: the distro
# docker.io package can replace the running Docker a live site depends on.
if ! command -v docker >/dev/null 2>&1; then
  apt-get install -y --no-install-recommends docker.io docker-compose-v2
fi
if command -v systemctl >/dev/null 2>&1 && [[ -d /run/systemd/system ]]; then
  systemctl enable --now docker 2>/dev/null || true
fi
if ! docker info >/dev/null 2>&1; then
  echo "the docker daemon is not reachable; start it (this script will not restart a running engine)" >&2
  exit 1
fi
if ! docker compose version >/dev/null 2>&1; then
  echo "docker compose v2 is required" >&2
  exit 1
fi

if ! getent group "$APP_GROUP" >/dev/null 2>&1; then
  groupadd --system "$APP_GROUP"
fi
if ! id -u "$APP_USER" >/dev/null 2>&1; then
  useradd --system --gid "$APP_GROUP" --create-home --home-dir "$ROOT" --shell /usr/sbin/nologin "$APP_USER"
fi
if getent group docker >/dev/null 2>&1; then
  usermod -aG docker "$APP_USER"
fi

install -d -o "$APP_USER" -g "$APP_GROUP" -m 0750 \
  "$ROOT/bin" \
  "$ROOT/config" \
  "$ROOT/data/inbox" \
  "$ROOT/sandbox" \
  "$ROOT/build" \
  "$ROOT/logs/jobs" \
  "$ROOT/sql" \
  "$ROOT/deploy"

if [[ ! -x "$ROOT/.venv/bin/python" ]]; then
  if command -v uv >/dev/null 2>&1; then
    # Ubuntu 26.04 ships Python 3.14; asyncpg/Pillow wheels lag it. uv pins 3.12.
    uv venv --python 3.12 "$ROOT/.venv"
  else
    python3 -m venv "$ROOT/.venv"
  fi
fi
if command -v uv >/dev/null 2>&1; then
  uv pip install --python "$ROOT/.venv/bin/python" --disable-pip-version-check -r "$ROOT/requirements-test.txt"
else
  "$ROOT/.venv/bin/pip" install --disable-pip-version-check -r "$ROOT/requirements-test.txt"
fi

for tool in vectorcraft-cli photocraft-cli designcraft-cli effectcraft-cli filmcraft-cli; do
  if [[ ! -e "$ROOT/bin/$tool" ]]; then
    install -m 0755 "$ROOT/deploy/craft-bin/$tool" "$ROOT/bin/$tool"
  fi
done

if [[ ! -f "$ROOT/config/products.json" ]]; then
  echo "missing $ROOT/config/products.json" >&2
  exit 1
fi

if [[ ! -f "$ROOT/config/pipeline.env" ]]; then
  db_pass="$(python3 -c 'import secrets; print(secrets.token_hex(24))')"
  cred_key="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
  sed -e "s/__DB_PASS__/${db_pass}/g" -e "s/__CRED_KEY__/${cred_key}/g" \
    "$ROOT/config/pipeline.env.example" > "$ROOT/config/pipeline.env"
  chmod 0640 "$ROOT/config/pipeline.env"
fi

set -a
# shellcheck disable=SC1091
. "$ROOT/config/pipeline.env"
set +a

if [[ -z "${POD_DB_PASS:-}" || -z "${DATABASE_URL:-}" ]]; then
  echo "pipeline.env is missing POD_DB_PASS or DATABASE_URL" >&2
  exit 1
fi

if python3 -c 'import socket,sys;s=socket.socket();s.settimeout(0.3);r=s.connect_ex(("127.0.0.1",5432));s.close();sys.exit(0 if r==0 else 1)' \
  && ! docker ps --format '{{.Names}}' | grep -qx pod-postgres; then
  echo "127.0.0.1:5432 is in use and pod-postgres is not the listener" >&2
  exit 1
fi

if [[ "${POD_USE_DOCKER:-0}" == "1" ]]; then
  docker build -t "${POD_DOCKER_IMAGE:-pod-craft-runner:latest}" -f "$ROOT/deploy/Dockerfile" "$ROOT"
else
  echo "POD_USE_DOCKER is not 1: skipping the craft-runner image (native mode uses \$ROOT/bin)"
fi
docker compose --env-file "$ROOT/config/pipeline.env" -f "$ROOT/deploy/compose.yml" up -d

ready=0
for _ in $(seq 1 40); do
  status="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{end}}' pod-postgres 2>/dev/null || true)"
  if [[ "$status" == "healthy" ]]; then
    ready=1
    break
  fi
  sleep 1
done
if [[ "$ready" -ne 1 ]]; then
  echo "pod-postgres did not become healthy" >&2
  docker logs --tail 80 pod-postgres >&2 || true
  exit 1
fi

docker exec -i pod-postgres psql -U pod_app -d pod -v ON_ERROR_STOP=1 < "$ROOT/sql/schema.sql"

if command -v systemctl >/dev/null 2>&1 && [[ -d /run/systemd/system ]]; then
  install -m 0644 "$ROOT/deploy/systemd/pod-mcp.service" /etc/systemd/system/pod-mcp.service
  install -m 0644 "$ROOT/deploy/systemd/pod-worker.service" /etc/systemd/system/pod-worker.service
  install -m 0644 "$ROOT/deploy/systemd/pod-worker.timer" /etc/systemd/system/pod-worker.timer
  systemctl daemon-reload
  systemctl enable --now pod-mcp.service pod-worker.timer
else
  echo "systemd is not running; start the MCP and the worker timer yourself" >&2
fi

chown -R "$APP_USER:$APP_GROUP" "$ROOT"
chmod 0640 "$ROOT/config/pipeline.env"

echo "pod pipeline ready at $ROOT"
echo "next: insert a users_saas_accounts row, then drop files in $ROOT/data/inbox/<account_id>/"
