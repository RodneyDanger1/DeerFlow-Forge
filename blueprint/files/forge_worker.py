"""Forge worker loop: one claim, one handler, one truthful finish.

Local source only; the handler is injected so the worker can be tested without
Craft, a network, or a production database.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Awaitable, Callable, Protocol

log = logging.getLogger("forge.worker")
Handler = Callable[[dict[str, Any]], Awaitable[None]]


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
                 lease_s: int = 300) -> None:
        self.repo, self.handler = repo, handler
        self.worker_id, self.lease_s = worker_id, lease_s

    async def run_once(self) -> dict[str, Any] | None:
        job = await self.repo.claim_job(self.worker_id, lease_s=self.lease_s)
        if job is None:
            return None
        try:
            await self.handler(dict(job.get("payload") or {}))
        except Exception as exc:  # boundary: record the failure, then re-raise nothing
            log.exception("job %s failed", job["id"])
            await self.repo.finish_job(job["id"], ok=False, error=f"{type(exc).__name__}: {exc}")
            return {**job, "ok": False, "error": f"{type(exc).__name__}: {exc}"}
        await self.repo.finish_job(job["id"], ok=True)
        return {**job, "ok": True, "error": None}

    async def drain(self, *, max_jobs: int = 1) -> list[dict[str, Any]]:
        results = []
        for _ in range(max_jobs):
            result = await self.run_once()
            if result is None:
                break
            results.append(result)
        return results
