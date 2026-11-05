"""Runtime settings. Everything comes from environment variables (see .env.example)
plus an optional per-category config file at <root>/config/products.json."""
from __future__ import annotations

import json
import os
import shlex
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class ConfigError(RuntimeError):
    """Raised for missing or invalid configuration. Never retried."""


def _bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} must be an integer, got {raw!r}") from exc


@dataclass(frozen=True)
class Settings:
    root: Path
    database_url: str
    credential_key: str = ""
    fw_base_url: str = "https://api.fourthwall.com"
    fw_api_user: str | None = None
    fw_api_secret: str | None = None
    # --- sandboxing -------------------------------------------------------
    use_docker: bool = False
    docker_image: str = "pod-craft-runner:latest"
    docker_memory: str = "2g"
    docker_cpus: str = "1.5"
    docker_cpu_shares: int = 256          # relative weight vs. the web app (default 1024)
    nice_level: int = 10                  # native mode only; see BLUEPRINT.md section 6
    craft_prefix: tuple[str, ...] = ()    # e.g. ("xvfb-run", "-a") for GUI toolkits
    # --- execution --------------------------------------------------------
    max_concurrency: int = 2
    step_timeout_s: int = 900
    max_attempts: int = 2
    fallback_raster_dpi: int = 600
    max_log_bytes: int = 5 * 1024 * 1024
    flush_poll_s: float = 0.2
    inbox_settle_s: int = 5
    stuck_after_s: int = 1800
    # --- MCP server -------------------------------------------------------
    mcp_host: str = "127.0.0.1"
    mcp_port: int = 8765
    products: dict[str, dict[str, Any]] = field(default_factory=dict)

    # directory layout ------------------------------------------------------
    @property
    def inbox(self) -> Path:
        return self.root / "data" / "inbox"

    @property
    def sandbox(self) -> Path:
        return self.root / "sandbox"

    @property
    def build(self) -> Path:
        return self.root / "build"

    @property
    def job_logs(self) -> Path:
        return self.root / "logs" / "jobs"

    @property
    def bin_dir(self) -> Path:
        return self.root / "bin"

    @classmethod
    def from_env(cls) -> "Settings":
        root = Path(os.environ.get("POD_ROOT", "/opt/pod-pipeline")).resolve()
        db_url = os.environ.get("DATABASE_URL", "")
        if not db_url:
            raise ConfigError("DATABASE_URL is not set")
        products: dict[str, dict[str, Any]] = {}
        cfg_file = root / "config" / "products.json"
        if cfg_file.is_file():
            try:
                products = json.loads(cfg_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise ConfigError(f"{cfg_file} is not valid JSON: {exc}") from exc
        return cls(
            root=root,
            database_url=db_url,
            credential_key=os.environ.get("POD_CREDENTIAL_KEY", ""),
            fw_base_url=os.environ.get("FW_BASE_URL", "https://api.fourthwall.com").rstrip("/"),
            fw_api_user=os.environ.get("FW_API_USER") or None,
            fw_api_secret=os.environ.get("FW_API_SECRET") or None,
            use_docker=_bool("POD_USE_DOCKER", False),
            docker_image=os.environ.get("POD_DOCKER_IMAGE", "pod-craft-runner:latest"),
            docker_memory=os.environ.get("POD_DOCKER_MEMORY", "2g"),
            docker_cpus=os.environ.get("POD_DOCKER_CPUS", "1.5"),
            docker_cpu_shares=_int("POD_DOCKER_CPU_SHARES", 256),
            nice_level=_int("POD_NICE_LEVEL", 10),
            craft_prefix=tuple(shlex.split(os.environ.get("POD_CRAFT_PREFIX", ""))),
            max_concurrency=max(1, _int("POD_MAX_CONCURRENCY", 2)),
            step_timeout_s=_int("POD_STEP_TIMEOUT_S", 900),
            fallback_raster_dpi=_int("POD_FALLBACK_RASTER_DPI", 600),
            mcp_host=os.environ.get("POD_MCP_HOST", "127.0.0.1"),
            mcp_port=_int("POD_MCP_PORT", 8765),
            products=products,
        )
