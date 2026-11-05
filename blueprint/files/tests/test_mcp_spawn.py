"""The MCP trigger must spawn a worker that outlives its caller.

Defect this pins: `asyncio.create_subprocess_exec` binds the child to a
SubprocessTransport. When the calling interpreter exits - the one-shot
`--call` tool mode, or a Gateway restart - transport finalisation kills the
child. Measured on the VPS: the tool answered `spawned: true, pid: 45658`,
that pid was gone within a second, the spawn log stayed 0 bytes, and the run
stayed `queued`. The tool reported success for a worker that never started;
only the minute timer could rescue the row.

The fix is a detached `subprocess.Popen`, which has no loop or interpreter
ownership. These tests run the spawn inside a *separate* python process and
assert the grandchild produced its log entry after that process exited.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

FILES_ROOT = Path(__file__).resolve().parent.parent

# Runs in a child interpreter: Settings with a dead database URL, spawn from
# inside asyncio.run, then exit immediately. The worker cannot reach a database,
# but with a detached child it must still start and log its failure.
CALLER = """
import asyncio, sys, uuid
from pathlib import Path
from pod_pipeline.config import Settings
from pod_pipeline import mcp_server

root = Path(sys.argv[1])
settings = Settings(root=root, database_url="postgresql://nobody:nopass@127.0.0.1:1/none")
asyncio.run(mcp_server._spawn_worker(settings, uuid.uuid4()))
"""


def _invoke_caller(root: Path) -> None:
    env = {**os.environ, "PYTHONPATH": str(FILES_ROOT)}
    result = subprocess.run(
        [sys.executable, "-c", CALLER, str(root)], env=env, capture_output=True, text=True, timeout=90
    )
    assert result.returncode == 0, f"caller failed: {result.stderr[-800:]}"


def _wait_for_log(log: Path, timeout_s: float = 20.0) -> int:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if log.exists() and log.stat().st_size > 0:
            return log.stat().st_size
        time.sleep(0.05)
    return log.stat().st_size if log.exists() else 0


def test_worker_survives_the_calling_interpreter_exiting(tmp_path: Path) -> None:
    root = tmp_path / "root"
    (root / "logs" / "jobs").mkdir(parents=True)
    _invoke_caller(root)
    log = root / "logs" / "jobs" / "mcp-spawn.log"
    size = _wait_for_log(log)
    assert size > 0, (
        "the worker was killed when its caller's interpreter exited: nothing was written to the spawn log"
    )
    text = log.read_text(encoding="utf-8", errors="replace")
    assert "pod.worker" in text or "Traceback" in text or "configuration error" in text, text[:400]


def test_spawn_detached_is_not_owned_by_an_event_loop(tmp_path: Path) -> None:
    """Two callers can spawn concurrently; finished handles are reaped."""
    from pod_pipeline import mcp_server

    mcp_server._WORKER_PROCS.clear()
    log = tmp_path / "spawn.log"
    argv = [sys.executable, "-c", "import time; time.sleep(20)"]
    first = mcp_server.spawn_detached(argv, cwd=str(tmp_path), log_path=log)
    second = mcp_server.spawn_detached(argv, cwd=str(tmp_path), log_path=log)
    try:
        assert first != second
        assert len(mcp_server._WORKER_PROCS) == 2
        mcp_server._reap_workers()
        assert len(mcp_server._WORKER_PROCS) == 2
    finally:
        for proc in mcp_server._WORKER_PROCS:
            proc.kill()
            proc.wait(timeout=10)
        mcp_server._WORKER_PROCS.clear()