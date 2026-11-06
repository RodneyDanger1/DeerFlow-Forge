"""Production worker job: one payload -> one persisted, registered Craft call.

Configure with:
  FORGE_DSN / FORGE_TEST_DSN / DATABASE_URL
  FORGE_WORK_ROOT (absolute existing directory for the run's artifacts)
  FORGE_VECTORCRAFT_BIN / FORGE_PHOTOCRAFT_BIN (optional absolute overrides)
"""
from __future__ import annotations

import os
from pathlib import Path

from forge_consumer import ConsumerError, ToolCallConsumer
from forge_craft_registry import build_registry, load_verified_registry
from forge_gateway import Gateway, ToolSpec
from forge_repo import ForgeGatewayRepo, ForgeRepo


def _dsn() -> str:
    value = (os.environ.get("FORGE_DSN") or os.environ.get("FORGE_TEST_DSN")
             or os.environ.get("DATABASE_URL") or "").strip()
    if not value:
        raise ConsumerError("E_DSN_MISSING",
                            "no DSN: set FORGE_DSN / FORGE_TEST_DSN / DATABASE_URL")
    return value


def _work_root() -> Path:
    raw = os.environ.get("FORGE_WORK_ROOT", "").strip()
    if not raw:
        raise ConsumerError("E_WORK_ROOT_MISSING", "set FORGE_WORK_ROOT to an absolute directory")
    root = Path(raw)
    if not root.is_absolute() or not root.is_dir():
        raise ConsumerError("E_WORK_ROOT_INVALID",
                            f"FORGE_WORK_ROOT must be an absolute directory: {raw}")
    return root.resolve()


def build_specs(work_root: Path) -> list[ToolSpec]:
    registry = build_registry()
    return [ToolSpec(tool_id=tool_id, allowed_roles=("operator",),
                     allowed_cmds=(cmd_id,), roots=(str(work_root),))
            for (tool_id, cmd_id) in registry]


async def make_consumer(dsn: str, work_root: Path) -> tuple[ToolCallConsumer, ForgeRepo]:
    """Build the real gateway/consumer and return them with the open repo."""
    executor, _probes = load_verified_registry(work_root=work_root)
    repo = await ForgeRepo.connect(dsn)
    try:
        gateway = Gateway(build_specs(work_root), executor,
                          ForgeGatewayRepo(repo.pool),
                          roles={"worker": "operator"})
        return ToolCallConsumer(gateway, "worker"), repo
    except BaseException:
        await repo.close()
        raise


async def handle(payload: dict) -> object:
    """Worker handler: validate, execute one registered Craft call, persist it."""
    consumer, repo = await make_consumer(_dsn(), _work_root())
    try:
        return await consumer(payload)
    finally:
        await repo.close()
