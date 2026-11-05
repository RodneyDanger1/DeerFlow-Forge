#!/usr/bin/env bash
# Install/refresh the DeerFlow Forge console on a Debian/Ubuntu VPS.
#
#   sudo PREVIEW=1 bash deploy/vps/install-console.sh
#
# Serves the built console on 127.0.0.1:8091 (loopback only — reach it through
# an SSH tunnel, or put your own reverse proxy in front). Does not touch Docker,
# Caddy, or any other service on the host.
#
# Re-running is safe: dependencies are installed from the lockfile, the build
# directory is rebuilt from scratch (see scripts/build-vps.mjs for why the build
# caches must be cleared), and the unit is only restarted when it changed.
set -euo pipefail
trap 'echo "install-console.sh failed at line $LINENO" >&2' ERR

REPO="${REPO:-/opt/deerflow-forge}"
NODE_PREFIX="${NODE_PREFIX:-/opt/node22}"
APP_USER="${APP_USER:-forge}"
PORT="${PORT:-8091}"
NODE_MAJOR=22

if [[ "$(id -u)" -ne 0 ]]; then
  echo "install-console.sh must run as root" >&2
  exit 1
fi
if [[ ! -f "$REPO/package.json" || ! -f "$REPO/scripts/build-vps.mjs" ]]; then
  echo "expected the repo at $REPO (clone it there first)" >&2
  exit 1
fi
if ! command -v curl >/dev/null 2>&1; then
  apt-get update && apt-get install -y --no-install-recommends curl ca-certificates
fi

# --- Node: install a private copy, never replace the host's node/npm ---------
if [[ ! -x "$NODE_PREFIX/bin/node" ]]; then
  ver="$(curl -fsSL https://nodejs.org/dist/index.json |
    python3 -c "import json,sys; print(next(r['version'] for r in json.load(sys.stdin) if r['version'].startswith('v${NODE_MAJOR}.') and r.get('lts')))")"
  echo "installing Node $ver into $NODE_PREFIX"
  tmp="$(mktemp -d)"
  curl -fsSL "https://nodejs.org/dist/${ver}/node-${ver}-linux-x64.tar.xz" -o "$tmp/node.tar.xz"
  tar -xJf "$tmp/node.tar.xz" -C "$tmp"
  install -d "$NODE_PREFIX"
  cp -a "$tmp/node-${ver}-linux-x64/." "$NODE_PREFIX/"
  rm -rf "$tmp"
fi
NODE="$NODE_PREFIX/bin/node"
NPM="$NODE_PREFIX/bin/npm"
"$NODE" --version

# --- account -----------------------------------------------------------------
if ! id -u "$APP_USER" >/dev/null 2>&1; then
  useradd --system --create-home --home-dir "$REPO" --shell /usr/sbin/nologin "$APP_USER"
fi

# --- dependencies + build ----------------------------------------------------
# Run as root, then hand the tree to the service user: the clone is root-owned at
# this point, so building as forge would fail with EACCES on node_modules.
cd "$REPO"
"$NPM" ci --no-audit --no-fund
"$NODE" scripts/build-vps.mjs

if [[ ! -f "$REPO/.output/server/index.mjs" ]]; then
  echo "build produced no .output/server/index.mjs" >&2
  exit 1
fi

# --- unit --------------------------------------------------------------------
install -d /etc/systemd/system
sed -e "s#/opt/deerflow-forge#$REPO#g" -e "s#/opt/node22#$NODE_PREFIX#g" -e "s#Environment=PORT=8091#Environment=PORT=$PORT#" \
  "$REPO/deploy/vps/deerflow-forge-console.service" > /etc/systemd/system/deerflow-forge-console.service
chown -R "$APP_USER:$APP_USER" "$REPO"
systemctl daemon-reload
systemctl enable deerflow-forge-console.service
systemctl restart deerflow-forge-console.service

# --- verify (the unit is up only when it actually answers) -------------------
for _ in $(seq 1 40); do
  if curl -fsS -o /dev/null --max-time 2 "http://127.0.0.1:${PORT}/"; then
    echo "console ready on http://127.0.0.1:${PORT}/"
    exit 0
  fi
  sleep 1
done
echo "console did not answer on 127.0.0.1:${PORT}" >&2
journalctl -u deerflow-forge-console.service --no-pager -n 60 >&2 || true
exit 1
