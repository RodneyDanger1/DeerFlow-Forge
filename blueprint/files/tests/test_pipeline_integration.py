"""End-to-end orchestration against a real PostgreSQL schema and the Craft CLI stubs.

Requires a reachable test database (``TEST_DATABASE_URL``, default
postgresql://pod_app:devpass@127.0.0.1:5432/pod_test). Skipped, not failed,
when no database is reachable — see conftest._database.

Each test drives the same entry point the MCP tool uses (enqueue -> claim ->
run_pipeline) and then asserts on durable rows, so a green test means the
pipeline really wrote the artifact, the product row, and the sync log.
"""
from __future__ import annotations

import os
import stat
import sys
from pathlib import Path

import pytest

from pod_pipeline import db, orchestrator

STUBS = Path(__file__).resolve().parent / "stubs"
CRAFT_TOOLS = ("photocraft-cli", "vectorcraft-cli", "designcraft-cli", "effectcraft-cli", "filmcraft-cli")


@pytest.fixture
def stub_env(settings):
    """Rewrite the stub launchers so they run with extra env switches baked in.

    runner._env deliberately builds a minimal child environment, so the stub's
    documented STUB_* switches cannot arrive through the parent process. Baking
    them into the launcher keeps production code free of test-only plumbing.
    """

    def _apply(**kv: object) -> None:
        for tool in CRAFT_TOOLS:
            p = settings.bin_dir / tool
            p.write_text(
                f"#!{sys.executable}\n"
                "import os, sys\n"
                f"os.environ.update({kv!r})\n"
                f"sys.path.insert(0, {str(STUBS)!r})\n"
                "import craft_stub\n"
                "craft_stub.main()\n"
            )
            p.chmod(p.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    return _apply


async def _product_row(pool, run_id):
    return await pool.fetchrow("SELECT * FROM fourthwall_products WHERE run_id=$1", run_id)


async def test_apparel_run_produces_artifact_and_fourthwall_product(settings, pool, account, make_asset, fake_fw) -> None:
    asset_id = await make_asset()
    run_id, created = await db.enqueue_run(pool, account_id=account, asset_id=asset_id, product_type="apparel")
    assert created is True

    summary = await orchestrator.run_pipeline(settings, pool, run_id, pid=os.getpid())

    assert summary is not None and summary["ok"] is True, summary
    artifact = Path(summary["artifact"])
    assert artifact.is_file() and artifact.stat().st_size > 0
    assert summary["product_state"] == "draft"

    row = await _product_row(pool, run_id)
    assert row is not None
    assert row["fw_product_id"], "a Fourthwall product id was not persisted"
    assert row["media_id"], "the uploaded media id was not persisted"
    assert row["publish_state"] == "draft"

    asset = await db.get_asset(pool, asset_id)
    assert asset["status"] == "processed"
    assert asset["trace_state"] == "traced"

    assert fake_fw.count("POST", "/open-api/v1.0/media/upload-url") == 1
    assert fake_fw.count("POST", "/open-api/v1.0/products") == 1
    # Every step is recorded per job, so the run has an audit trail.
    steps = await pool.fetch("SELECT step_name, status FROM processing_jobs WHERE run_id=$1 ORDER BY step_index", run_id)
    names = [r["step_name"] for r in steps]
    assert "vector_trace" in names and "effectcraft_distress" in names
    assert all(r["status"] in ("succeeded", "failed") for r in steps)


async def test_trace_exit_one_switches_to_the_raster_fallback(settings, pool, account, make_asset, fake_fw, stub_env) -> None:
    stub_env(STUB_VECTOR_EXIT="1")
    asset_id = await make_asset()
    run_id, _ = await db.enqueue_run(pool, account_id=account, asset_id=asset_id, product_type="apparel")

    summary = await orchestrator.run_pipeline(settings, pool, run_id, pid=os.getpid())

    assert summary is not None and summary["ok"] is True, summary
    asset = await db.get_asset(pool, asset_id)
    assert asset["trace_state"] == "raster_fallback"
    steps = await pool.fetch("SELECT step_name FROM processing_jobs WHERE run_id=$1", run_id)
    assert "raster_fallback" in {r["step_name"] for r in steps}


async def test_anti_aliased_knitwear_fails_validation_and_marks_the_asset_failed(
    settings, pool, account, make_asset, fake_fw, stub_env
) -> None:
    stub_env(STUB_KNIT="antialias")
    asset_id = await make_asset()
    run_id, _ = await db.enqueue_run(pool, account_id=account, asset_id=asset_id, product_type="knitwear")

    summary = await orchestrator.run_pipeline(settings, pool, run_id, pid=os.getpid())

    assert summary is not None and summary["ok"] is False
    assert "distinct colors" in (summary["error"] or "")
    asset = await db.get_asset(pool, asset_id)
    assert asset["status"] == "failed"
    run = await db.get_run(pool, run_id)
    # RUN_SELECT exposes the orchestrator row's status as job_status (it is a
    # processing_jobs row, not a separate runs table) plus the failure digest.
    assert run["job_status"] == "failed"
    assert "distinct colors" in (run["error_digest"] or "")


async def test_missing_fourthwall_credentials_refuse_without_faking_a_publish(
    settings, pool, account, make_asset, fake_fw
) -> None:
    """No credentials: the artifact is real, the publish is not — and the row says why."""
    bare = await pool.fetchval(
        """INSERT INTO users_saas_accounts (display_name, tenant_token_hash)
           VALUES ('No creds', repeat('b',64)) RETURNING id""")
    settings = dataclasses_replace(settings, fw_api_user=None, fw_api_secret=None)
    asset_id = await make_asset(account_id=bare)
    run_id, _ = await db.enqueue_run(pool, account_id=bare, asset_id=asset_id, product_type="apparel")

    summary = await orchestrator.run_pipeline(settings, pool, run_id, pid=os.getpid())

    assert summary is not None
    assert summary["artifact"] and Path(summary["artifact"]).is_file()
    assert summary["product_state"] == "draft"
    row = await _product_row(pool, run_id)
    assert row is not None
    assert row["fw_product_id"] is None
    assert "credentials" in (row["last_error"] or "")
    # Nothing was uploaded: no fake success on the wire.
    assert fake_fw.count("POST", "/open-api/v1.0/products") == 0


def dataclasses_replace(settings, **kw):
    import dataclasses

    return dataclasses.replace(settings, **kw)
