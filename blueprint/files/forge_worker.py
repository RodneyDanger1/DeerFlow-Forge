"""Forge worker loop: one claim, one handler, one truthful finish.

Local source only; the handler is injected so the worker can be tested without
Craft, a network, or a production database.

Bounded-error contract: every failure leaving this module is a `WorkerError`
subclass carrying a stable `E_*` code. The CLI prints one JSON object to stderr
and exits non-zero; it never prints a traceback as its contract.
"""
from __future__ import annotations

import argparse
import asyncio
import importlib
import json
import logging
import os
import sys
from typing import Any, Awaitable, Callable, Protocol

log = logging.getLogger("forge.worker")
Handler = Callable[[dict[str, Any]], Awaitable[None]]

# Codes a repo may use to refuse a finish; anything else becomes E_REPO.
FINISH_REFUSAL_CODES = frozenset({"E_JOB_STATE", "E_PARAM_REJECTED", "E_TIMEOUT"})
CLI_CONFIG_CODES = frozenset({"E_INVALID_ARG", "E_DSN_MISSING", "E_HANDLER_MISSING",
                              "E_HANDLER_INVALID"})
EXIT_OK, EXIT_RUNTIME, EXIT_CONFIG = 0, 1, 2


class WorkerError(RuntimeError):
    """A bounded worker/CLI failure with a stable E_* code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code, self.message = code, message


class FinishRefused(WorkerError):
    """The repo refused the finish; the job state is not what the worker assumed."""


def _error_code(exc: BaseException) -> str:
    """Extract a bounded E_* code from a repo/driver exception, else E_REPO."""
    code = getattr(exc, "code", None)
    if isinstance(code, str) and code.startswith("E_"):
        return code
    text = str(exc)
    for candidate in sorted(FINISH_REFUSAL_CODES, key=len, reverse=True):
        if candidate in text:
            return candidate
    return "E_REPO"


class WorkerRepo(Protocol):
    async def claim_job(self, worker: str, *, lease_s: int = 300) -> dict[str, Any] | None: ...
    async def finish_job(self, job_id: int, *, ok: bool, error: str | None = None) -> dict[str, Any]: ...
    async def reap_expired_jobs(self) -> int: ...


class LeaseReaper:
    """Periodic, cancellable expired-lease requeue. No Craft, no unbounded loop."""
    def __init__(self, repo: WorkerRepo, *, interval_s: float = 30.0) -> None:
        if interval_s <= 0:
            raise ValueError("interval_s must be positive")
        self.repo, self.interval_s = repo, interval_s

    async def run_once(self) -> int:
        return await self.repo.reap_expired_jobs()

    async def run(self, stop: asyncio.Event) -> int:
        requeued = 0
        while not stop.is_set():
            try:
                requeued += await self.run_once()
            except Exception:
                log.exception("lease reaper iteration failed")
            try:
                await asyncio.wait_for(stop.wait(), timeout=self.interval_s)
            except asyncio.TimeoutError:
                continue
        return requeued


class ForgeWorker:
    def __init__(self, repo: WorkerRepo, handler: Handler, *, worker_id: str = "worker-1",
                 lease_s: int = 300, kind: str | None = None) -> None:
        self.repo, self.handler = repo, handler
        self.worker_id, self.lease_s = worker_id, lease_s
        self.kind = kind

    async def _finish(self, job_id: int, *, ok: bool, error: str | None = None) -> dict[str, Any]:
        """Guarded finish (D3): a refused finish is a named, bounded failure."""
        try:
            return await self.repo.finish_job(job_id, ok=ok, error=error)
        except Exception as exc:
            code = _error_code(exc)
            raise FinishRefused(code, f"finish refused for job {job_id}: {exc}") from exc

    async def run_once(self) -> dict[str, Any] | None:
        job = await self.repo.claim_job(self.worker_id, lease_s=self.lease_s)
        if job is None:
            return None
        if self.kind is not None and job.get("kind") != self.kind:
            detail = f"E_JOB_KIND: expected {self.kind!r}, got {job.get('kind')!r}"
            await self._finish(job["id"], ok=False, error=detail)
            return {**job, "ok": False, "error": detail}
        try:
            await self.handler(dict(job.get("payload") or {}))
        except Exception as exc:  # boundary: record the failure, then re-raise nothing
            log.exception("job %s failed", job["id"])
            detail = f"{type(exc).__name__}: {exc}"
            await self._finish(job["id"], ok=False, error=detail)   # may raise FinishRefused
            return {**job, "ok": False, "error": detail}
        await self._finish(job["id"], ok=True)                      # may raise FinishRefused
        return {**job, "ok": True, "error": None}

    async def drain(self, *, max_jobs: int = 1) -> list[dict[str, Any]]:
        results = []
        for _ in range(max_jobs):
            result = await self.run_once()
            if result is None:
                break
            results.append(result)
        return results


# --------------------------------------------------------------------------- CLI
def _load_handler(spec: str) -> Handler:
    """Load a handler from 'module:callable'. Missing/invalid names are bounded errors."""
    if ":" not in spec:
        raise WorkerError("E_HANDLER_INVALID", "handler must look like module:callable")
    module_name, _, attr = spec.partition(":")
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:
        raise WorkerError("E_HANDLER_INVALID", f"cannot import {module_name}: {exc}") from exc
    handler = getattr(module, attr, None)
    if handler is None or not callable(handler):
        raise WorkerError("E_HANDLER_INVALID", f"{module_name}:{attr} is not callable")
    if not asyncio.iscoroutinefunction(handler):
        raise WorkerError("E_HANDLER_INVALID", f"{module_name}:{attr} must be async")
    return handler


def _resolve_dsn(args: argparse.Namespace) -> str:
    dsn = args.dsn or os.environ.get("FORGE_DSN") or os.environ.get("FORGE_TEST_DSN") \
        or os.environ.get("DATABASE_URL") or ""
    if not dsn.strip():
        raise WorkerError("E_DSN_MISSING",
                          "no DSN: pass --dsn or set FORGE_DSN / FORGE_TEST_DSN / DATABASE_URL")
    return dsn


def _make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m forge_worker",
        description="Claim at most one job and finish it truthfully. One-shot only.")
    parser.add_argument("--once", action="store_true",
                        help="required: drain one job and exit")
    parser.add_argument("--lease-s", type=int, default=300, help="claim lease seconds (1..86400)")
    parser.add_argument("--worker-id", default="worker-cli", help="worker identity for the claim")
    parser.add_argument("--dsn", default=None, help="Postgres DSN (or use FORGE_DSN)")
    parser.add_argument("--handler", default=os.environ.get("FORGE_HANDLER"),
                        help="module:async_callable that processes one job payload")
    parser.add_argument("--kind", default=None,
                        help="optional claimed job kind guard (e.g. forge.tool_call)")
    return parser


async def _run_once(*, dsn: str, worker_id: str, lease_s: int, handler: Handler,
                    repo_factory: Callable[[str], Awaitable[Any]] | None = None,
                    kind: str | None = None) -> dict[str, Any]:
    if repo_factory is None:
        from forge_repo import ForgeRepo  # lazy: tests need no asyncpg
        async def repo_factory(dsn_: str):
            return await ForgeRepo.connect(dsn_)
    repo = await repo_factory(dsn)
    try:
        worker = ForgeWorker(repo, handler, worker_id=worker_id, lease_s=lease_s,
                             kind=kind)
        result = await worker.run_once()
        if result is None:
            return {"ok": True, "claimed": 0, "finished": 0, "job_id": None}
        return {"ok": bool(result["ok"]), "claimed": 1, "finished": 1,
                "job_id": result["id"], "job_ok": bool(result["ok"])}
    finally:
        close = getattr(repo, "close", None)
        if close is not None:
            await close()


def main(argv: list[str] | None = None, *, repo_factory=None, handler: Handler | None = None) -> int:
    """CLI entry point. Returns the process exit code; prints one JSON object."""
    args = _make_parser().parse_args(argv)
    try:
        if not args.once:
            raise WorkerError("E_INVALID_ARG", "only --once is supported; no daemon mode")
        if not (1 <= args.lease_s <= 86400):
            raise WorkerError("E_INVALID_ARG", f"--lease-s out of range 1..86400: {args.lease_s}")
        dsn = _resolve_dsn(args)
        resolved = handler if handler is not None else (
            _load_handler(args.handler) if args.handler else None)
        if resolved is None:
            raise WorkerError("E_HANDLER_MISSING", "no handler: pass --handler module:callable")
        summary = asyncio.run(_run_once(dsn=dsn, worker_id=args.worker_id,
                                        lease_s=args.lease_s, handler=resolved,
                                        repo_factory=repo_factory, kind=args.kind))
    except WorkerError as exc:
        print(json.dumps({"ok": False, "code": exc.code, "message": exc.message}),
              file=sys.stderr)
        return EXIT_CONFIG if exc.code in CLI_CONFIG_CODES else EXIT_RUNTIME
    except Exception as exc:  # bounded: never leak a traceback as the contract
        print(json.dumps({"ok": False, "code": "E_WORKER", "message": f"{type(exc).__name__}: {exc}"}),
              file=sys.stderr)
        return EXIT_RUNTIME
    print(json.dumps(summary, sort_keys=True))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
