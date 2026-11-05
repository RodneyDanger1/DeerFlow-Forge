from __future__ import annotations

import asyncio
import dataclasses
import json
import os
import re
import stat
import sys
from pathlib import Path
from typing import Any, Callable

import asyncpg
import httpx
import pytest
import pytest_asyncio
from PIL import Image

from pod_pipeline import db, orchestrator
from pod_pipeline.config import Settings
from pod_pipeline.fourthwall import FourthwallClient

ROOT = Path(__file__).resolve().parent.parent
TEST_DB_URL = os.environ.get("TEST_DATABASE_URL", "postgresql://pod_app:devpass@127.0.0.1:5432/pod_test")
CRED_KEY = "test-credential-key-0123456789abcdef"
CRAFT_TOOLS = ("photocraft-cli", "vectorcraft-cli", "designcraft-cli", "effectcraft-cli", "filmcraft-cli")
DB_RE = re.compile(r"^postgresql://([^:]+):([^@]+)@([^:/]+):(\d+)/(\w+)$")


def _dsn(user: str, pw: str, host: str, port: str, name: str) -> str:
    return f"postgresql://{user}:{pw}@{host}:{port}/{name}"


async def _create_schema() -> None:
    """Create a throwaway database and apply sql/schema.sql through asyncpg.

    Earlier this shelled out to `su postgres` + `psql`, which only works on a
    host-installed PostgreSQL — the deployment runs Postgres in Docker, where no
    `postgres` OS user exists. The configured user owns the test database and is
    a superuser inside that container, so an asyncpg admin connection is enough.
    """
    match = DB_RE.match(TEST_DB_URL)
    if not match:
        raise pytest.UsageError(f"TEST_DATABASE_URL is not a plain postgresql:// URL: {TEST_DB_URL!r}")
    user, pw, host, port, name = match.groups()
    admin = await asyncpg.connect(_dsn(user, pw, host, port, "postgres"))
    try:
        await admin.execute(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)')
        await admin.execute(f'CREATE DATABASE "{name}" OWNER "{user}"')
    finally:
        await admin.close()
    conn = await asyncpg.connect(TEST_DB_URL)
    try:
        await conn.execute((ROOT / "sql" / "schema.sql").read_text(encoding="utf-8"))
    finally:
        await conn.close()


@pytest.fixture(scope="session")
def _database() -> None:
    try:
        asyncio.run(_create_schema())
    except (OSError, asyncpg.PostgresError) as exc:
        pytest.skip(f"test database unavailable at {TEST_DB_URL}: {exc}")


@pytest.fixture
def stubs_env(tmp_path: Path) -> Path:
    """<root>/bin with launcher scripts for every Craft CLI -> tests/stubs/craft_stub.py."""
    bin_dir = tmp_path / "root" / "bin"
    bin_dir.mkdir(parents=True)
    for tool in CRAFT_TOOLS:
        launcher = bin_dir / tool
        launcher.write_text(f"#!{sys.executable}\nimport runpy,sys\nsys.path.insert(0, {str(ROOT / 'tests' / 'stubs')!r})\n"
                            f"import craft_stub\ncraft_stub.main()\n")
        launcher.chmod(launcher.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return tmp_path / "root"


@pytest.fixture
def settings(stubs_env: Path) -> Settings:
    products = {
        "apparel": {"fourthwall_template_id": "pro_apparel"},
        "knitwear": {"fourthwall_template_id": "pro_knit", "knit_grid": "40x50", "palette_limit": 6},
        "accessories": {"fourthwall_template_id": "pro_acc"},
        "odd_3d": {"fourthwall_template_id": "pro_odd"},
        "stationery": {"fourthwall_template_id": "pro_stat"},
    }
    return Settings(root=stubs_env, database_url=TEST_DB_URL, credential_key=CRED_KEY, flush_poll_s=0.02,
                    inbox_settle_s=0, step_timeout_s=30, max_log_bytes=2 * 1024 * 1024, products=products)


@pytest_asyncio.fixture
async def pool(_database, settings: Settings):
    p = await asyncpg.create_pool(TEST_DB_URL, min_size=1, max_size=6)
    await p.execute("TRUNCATE users_saas_accounts, ingested_assets, processing_jobs, fourthwall_products, "
                    "agent_sync_logs RESTART IDENTITY CASCADE")
    yield p
    await p.close()


@pytest_asyncio.fixture
async def account(pool: asyncpg.Pool) -> int:
    return await pool.fetchval(
        """INSERT INTO users_saas_accounts (display_name, tenant_token_hash, fourthwall_api_user, fourthwall_api_secret_enc)
           VALUES ('Test shop', repeat('a',64), 'apiuser', pgp_sym_encrypt('apisecret', $1)) RETURNING id""", CRED_KEY)


@pytest.fixture
def make_asset(settings: Settings, pool: asyncpg.Pool, account: int) -> Callable[..., Any]:
    from pod_pipeline.ingest import scan_inbox

    async def _make(name: str = "Cool_Design.png", size: tuple[int, int] = (200, 160), account_id: int | None = None) -> int:
        acct = account_id or account
        d = settings.inbox / str(acct)
        d.mkdir(parents=True, exist_ok=True)
        Image.new("RGBA", size, (255, 0, 0, 255)).save(d / name, "PNG")
        await scan_inbox(settings, pool)
        return await pool.fetchval("SELECT id FROM ingested_assets WHERE source_path=$1", str(d / name))

    return _make


class FakeFourthwall:
    """In-memory Fourthwall: api transport (Fourthwall host) + gcs transport (storage host), with call recording."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []
        self.gcs_puts: list[dict[str, Any]] = []
        self.auth_headers: list[str] = []
        self.reject_media_type = False
        self.fail_create_with: int | None = None
        self.products: dict[str, dict[str, Any]] = {}
        self._n = 0
        self.api = httpx.MockTransport(self._api)
        self.gcs = httpx.MockTransport(self._gcs)

    def count(self, method: str, path_prefix: str) -> int:
        return sum(1 for m, p in self.calls if m == method and p.startswith(path_prefix))

    def _api(self, req: httpx.Request) -> httpx.Response:
        path, method = req.url.path, req.method
        self.calls.append((method, path))
        self.auth_headers.append(req.headers.get("authorization", ""))
        body = json.loads(req.content) if req.content else None
        if path == "/open-api/v1.0/media/upload-url":
            if self.reject_media_type:
                return httpx.Response(406, json={"code": "UNSUPPORTED_MEDIA_TYPE_ERROR", "mediaType": body["contentType"],
                                                 "supportedMediaTypes": ["image/png", "image/jpeg"]})
            assert body["size"] > 0 and body["fileName"] and body["contentType"]
            self._n += 1
            return httpx.Response(201, json={"uploadUrl": f"https://storage.fake.test/up/{self._n}?sig=abc",
                                             "fileUrl": f"https://cdn.fake.test/media/{self._n}/{body['fileName']}"})
        if path == "/open-api/v1.0/media/images":
            return httpx.Response(200, json={"id": f"img_{self._n}", "uri": body["fileUrl"],
                                             "width": body["width"], "height": body["height"]})
        if path == "/open-api/v1.0/products" and method == "POST":
            if self.fail_create_with:
                return httpx.Response(self.fail_create_with, json={"code": "SOMETHING_BROKE"})
            assert body["type"] == "design" and body["regions"][0]["imageId"].startswith("img_")
            pid = f"off_{len(self.products) + 1}"
            self.products[pid] = {"id": pid, "name": body["name"], "slug": body["name"].lower().replace(" ", "-"),
                                  "access": {"type": "HIDDEN"}, "state": {"type": "AVAILABLE"},
                                  "variants": [{"id": "v1", "sku": f"SKU-{pid}-S"}, {"id": "v2", "sku": f"SKU-{pid}-M"}],
                                  "images": [{"id": "i"}], "updatedAt": "2026-11-04T10:00:00Z"}
            return httpx.Response(201, json={"productId": pid, "customizationId": "cus_1", "images": []})
        m = re.fullmatch(r"/open-api/v1.0/products/([^/]+)(/state)?", path)
        if m and m.group(1) in self.products:
            prod = self.products[m.group(1)]
            if method == "GET":
                return httpx.Response(200, json=prod)
            if method == "PUT" and m.group(2):
                prod["access"] = {"type": body["state"]}
                return httpx.Response(200, json=prod)
        return httpx.Response(404, json={"code": "NOT_FOUND"})

    def _gcs(self, req: httpx.Request) -> httpx.Response:
        self.gcs_puts.append({"headers": dict(req.headers), "len": len(req.content), "url": str(req.url)})
        return httpx.Response(200)


@pytest.fixture
def fake_fw(monkeypatch: pytest.MonkeyPatch) -> FakeFourthwall:
    fw = FakeFourthwall()

    class Patched(FourthwallClient):
        def __init__(self, base_url: str, user: str, secret: str, **kw: Any) -> None:
            super().__init__(base_url, user, secret, transport=fw.api, gcs_transport=fw.gcs, **kw)

    monkeypatch.setattr(orchestrator, "FourthwallClient", Patched)
    from pod_pipeline import mcp_server
    monkeypatch.setattr(mcp_server, "FourthwallClient", Patched)
    return fw


@pytest.fixture
def with_state(settings: Settings, pool: asyncpg.Pool, monkeypatch: pytest.MonkeyPatch):
    """Point the MCP module's lazy state at the test settings/pool."""
    from pod_pipeline import mcp_server
    monkeypatch.setattr(mcp_server.STATE, "settings", settings)
    monkeypatch.setattr(mcp_server.STATE, "pool", pool)
    monkeypatch.setattr(mcp_server.STATE, "lock", None)
    return mcp_server


def replace(settings: Settings, **kw: Any) -> Settings:
    return dataclasses.replace(settings, **kw)
