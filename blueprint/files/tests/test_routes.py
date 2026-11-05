"""Route/config contract: what products.json may say and what the pipeline does with it.

These are pure tests (no database, no subprocesses) so they run on any machine,
including a developer box that has no Postgres.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from pod_pipeline.config import ConfigError
from pod_pipeline.routes import DEFAULT_CFG, PRODUCT_TYPES, ROUTES, merged_cfg, render, render_argv

FILES_ROOT = Path(__file__).resolve().parent.parent
PRODUCTS_FILE = FILES_ROOT / "config" / "products.json"


def test_products_json_covers_exactly_the_supported_product_types() -> None:
    shipped = set(json.loads(PRODUCTS_FILE.read_text(encoding="utf-8")))
    assert shipped == set(PRODUCT_TYPES), (
        f"products.json keys {sorted(shipped)} drifted from PRODUCT_TYPES {sorted(PRODUCT_TYPES)}"
    )


def test_every_product_type_has_a_route_and_a_default_config() -> None:
    assert set(ROUTES) == set(PRODUCT_TYPES)
    assert set(DEFAULT_CFG) == set(PRODUCT_TYPES)


def test_route_upload_is_none_or_a_rendered_path() -> None:
    variables = {"src": "/s", "art": "/a", "work": "/w", "build": "/b", "run_id": "r", "asset_id": 1,
                 "fallback_dpi": 600, "cfg": {}}
    for name, route in ROUTES.items():
        assert route.upload is not None, f"{name} has no upload target"
        assert render(route.upload, variables, where=name).startswith("/")


def test_knitwear_without_a_grid_refuses_by_name() -> None:
    """knit_grid has no default on purpose: the factory grid is per-product."""
    cfg = merged_cfg("knitwear", {})
    step = ROUTES["knitwear"].steps[0]
    variables = {"src": "/s", "art": "/a", "work": "/w", "build": "/b", "cfg": cfg}
    with pytest.raises(ConfigError) as exc:
        render_argv(step, variables)
    assert "rendered empty" in str(exc.value)


def test_products_json_override_wins_over_the_default() -> None:
    cfg = merged_cfg("knitwear", {"knitwear": {"knit_grid": "112x140", "palette_limit": 8}})
    assert cfg["knit_grid"] == "112x140"
    assert cfg["palette_limit"] == 8
    # Unset keys fall back to the shipped default rather than disappearing.
    assert cfg["regions"] == DEFAULT_CFG["knitwear"]["regions"]


def test_unknown_product_type_refuses_by_name() -> None:
    with pytest.raises(ConfigError) as exc:
        merged_cfg("posters", {})
    assert "unknown product_type" in str(exc.value)
    for name in PRODUCT_TYPES:
        assert name in str(exc.value)


def test_missing_placeholder_names_the_template() -> None:
    with pytest.raises(ConfigError) as exc:
        render("{cfg[does_not_exist]}", {"cfg": {}}, where="test route")
    assert "test route" in str(exc.value)
