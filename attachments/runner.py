"""Async process runner: sandbox wrapping, streaming log digest, hard timeouts, durable flush."""
from __future__ import annotations

import asyncio
import hashlib
import os
import shutil
import signal
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

from .config import Settings
from .logfilter import StreamDigest

TRANSIENT_EXIT_CODES = {-9, -15, 137, 143, 75}   # SIGKILL/SIGTERM (OOM killer), docker 128+n, EX_TEMPFAIL


@dataclass
class StepOutcome:
    exit_code: int
    timed_out: bool
    pid: int | None
    duration_s: float
    digest: str
    executed_argv: list[str]

    @property
    def ok(self) -> bool:
        return self.exit_code == 0 and not self.timed_out

    @property
    def transient(self) -> bool:
        return self.timed_out or self.exit_code in TRANSIENT_EXIT_CODES


class FlushTimeout(RuntimeError):
    pass


def build_command(settings: Settings, argv: list[str], *, work: Path, build: Path, container_name: str) -> list[str]:
    """Wrap a Craft command line in the configured sandbox.

    docker mode: cgroup limits (--memory/--cpus/--cpu-shares) are what protect the web app. `nice` on the
    `docker run` client would not reach the container's processes (the daemon starts them), so it is not used.
    native mode: nice + ionice (idle class) on the process itself.
    """
    inner = [*settings.craft_prefix, *argv]
    if settings.use_docker:
        return [
            "docker", "run", "--rm", "--init", "--name", container_name,
            "--memory", settings.docker_memory, "--memory-swap", settings.docker_memory,   # no swap use
            "--cpus", settings.docker_cpus, "--cpu-shares", str(settings.docker_cpu_shares),
            "--pids-limit", "256", "--network", "none",
            "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
            "--read-only", "--tmpfs", "/tmp:rw,size=512m", "-e", "HOME=/tmp",
            "--user", f"{os.getuid()}:{os.getgid()}",
            "-v", f"{work}:{work}:rw", "-v", f"{build}:{build}:rw", "-w", str(work),
            settings.docker_image, *inner,
        ]
    prefix = ["nice", "-n", str(settings.nice_level)]
    if shutil.which("ionice"):
        prefix += ["ionice", "-c", "3"]
    return [*prefix, *inner]


def _env(settings: Settings, work: Path) -> dict[str, str]:
    path = f"{settings.bin_dir}{os.pathsep}{os.environ.get('PATH', '/usr/local/bin:/usr/bin:/bin')}"
    return {"PATH": path, "HOME": str(work), "LANG": "C.UTF-8", "TMPDIR": str(work),
            "QT_QPA_PLATFORM": "offscreen", "POD_RUN_WORKDIR": str(work)}


async def _terminate(proc: asyncio.subprocess.Process, container: str | None) -> None:
    if container:
        killer = await asyncio.create_subprocess_exec(
            "docker", "kill", container, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
        await killer.wait()
    for sig, grace in ((signal.SIGTERM, 5.0), (signal.SIGKILL, 5.0)):
        try:
            os.killpg(proc.pid, sig)
        except ProcessLookupError:
            return
        try:
            await asyncio.wait_for(proc.wait(), grace)
            return
        except asyncio.TimeoutError:
            continue


async def run_step(
    settings: Settings, argv: list[str], *, work: Path, build: Path, log_path: Path, timeout_s: int,
) -> StepOutcome:
    container = f"pod-{uuid.uuid4().hex[:12]}" if settings.use_docker else None
    cmd = build_command(settings, argv, work=work, build=build, container_name=container or "")
    digest = StreamDigest(log_path=log_path, max_log_bytes=settings.max_log_bytes)
    started = time.monotonic()
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdin=asyncio.subprocess.DEVNULL, stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT, cwd=work, env=_env(settings, work),
            start_new_session=True,                       # own process group -> killpg reaches helper processes
        )
    except FileNotFoundError as exc:
        digest.finish()
        return StepOutcome(127, False, None, 0.0, f"executable not found: {exc.filename}", cmd)

    reader = asyncio.create_task(digest.consume(proc.stdout))   # type: ignore[arg-type]
    timed_out = False
    try:
        await asyncio.wait_for(proc.wait(), timeout_s)
    except asyncio.TimeoutError:
        timed_out = True
        await _terminate(proc, container)
    try:
        await asyncio.wait_for(reader, 10)
    except asyncio.TimeoutError:
        # a grandchild still holds the pipe open after the main process exited: kill the leftovers
        reader.cancel()
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        digest.finish()
    code = proc.returncode if proc.returncode is not None else -1
    return StepOutcome(code, timed_out, proc.pid, time.monotonic() - started, digest.render(), cmd)


# ------------------------------------------------------------------------------ durable flush
def _fsync_and_hash(path: Path) -> tuple[int, str]:
    h = hashlib.sha256()
    size = 0
    fd = os.open(path, os.O_RDONLY)
    try:
        with os.fdopen(os.dup(fd), "rb") as fh:
            while chunk := fh.read(1024 * 1024):
                h.update(chunk)
                size += len(chunk)
        os.fsync(fd)                                      # file data + metadata to stable storage
    finally:
        os.close(fd)
    dfd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(dfd)                                     # directory entry (the file's name) too
    finally:
        os.close(dfd)
    return size, h.hexdigest()


async def flush_to_disk(path: Path, *, poll_s: float = 0.2, stable_polls: int = 2, max_wait_s: float = 30.0) -> tuple[int, str]:
    """Wait until `path` stops changing, then fsync it (and its directory) off the event loop.

    Returns (size, sha256). Only after this returns is it safe to stream the file to another host."""
    loop = asyncio.get_running_loop()
    deadline = loop.time() + max_wait_s
    last: tuple[int, int] | None = None
    stable = 0
    while True:
        try:
            st = await asyncio.to_thread(os.stat, path)
            sig: tuple[int, int] | None = (st.st_size, st.st_mtime_ns)
        except FileNotFoundError:
            sig = None
        stable = stable + 1 if (sig is not None and sig[0] > 0 and sig == last) else 0
        last = sig
        if stable >= stable_polls:
            return await asyncio.to_thread(_fsync_and_hash, path)
        if loop.time() > deadline:
            raise FlushTimeout(f"{path} did not settle within {max_wait_s}s (size/mtime still changing or file missing)")
        await asyncio.sleep(poll_s)
