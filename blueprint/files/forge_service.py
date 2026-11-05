"""Loopback-only Forge HTTP service (stdlib; local source, not deployed).

The service is a thin HTTP seam over a repository. It never calls Craft, never
publishes, and binds loopback by default. Tests may inject a fake repo.

Wave-2 contract (see docs/TRACE/2026-11-05/RUNTIME-FIXES-W2.md):
  D1  a slow repo call is cancelled and answered ``504 E_SERVICE_TIMEOUT``;
  D2  a replayed idempotency key returns the existing episode (``200``,
      ``replayed: true``) instead of ``409`` with no body;
  D6  a mapped row that violates the service contract is ``500 E_REPO_SHAPE``,
      never a silent ``404``;
  D7  every request field is validated at the boundary (``400`` before any
      write, no ``str()`` coercion of untrusted input).
"""
from __future__ import annotations

import asyncio
import concurrent.futures
import json
import logging
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Protocol
from urllib.parse import urlparse

log = logging.getLogger("forge.service")

BRIEF_MAX_CHARS = 8192
IDEMPOTENCY_KEY_MAX_CHARS = 200
MAX_BODY_BYTES = 1_048_576
TASK_FAMILY_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
SHAPE_ERROR_CODE = "E_REPO_SHAPE"


class ServiceTimeout(RuntimeError):
    """The repo call exceeded the service deadline and was cancelled."""

    code = "E_SERVICE_TIMEOUT"


class RequestInvalid(ValueError):
    """A request field failed boundary validation."""

    code = "E_REQUEST_INVALID"


class ServiceRepo(Protocol):
    async def create_episode(self, *, idempotency_key: str, account_id: int, brief: str,
                             task_family: str, budget: dict[str, Any] | None = None) -> dict[str, Any]: ...
    async def get_episode(self, episode_id: str) -> dict[str, Any] | None: ...
    async def health(self) -> dict[str, Any]: ...


class _Loop:
    """One event loop for the service thread; repo pools must be created on it."""
    def __init__(self, timeout_s: float = 30.0) -> None:
        if timeout_s <= 0:
            raise ValueError("timeout_s must be positive")
        self.timeout_s = float(timeout_s)
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.loop.run_forever, daemon=True)
        self.thread.start()

    def run(self, coro):
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        try:
            return future.result(timeout=self.timeout_s)
        except concurrent.futures.TimeoutError as exc:
            # Best effort: stop the in-flight coroutine so a timed-out request
            # does not keep writing after the client got its answer.
            future.cancel()
            raise ServiceTimeout(
                f"repo call exceeded {self.timeout_s:g}s and was cancelled") from exc

    def stop(self) -> None:
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join(timeout=5)
        self.loop.close()


def _json(handler: BaseHTTPRequestHandler, status: int, body: dict[str, Any]) -> None:
    data = json.dumps(body, separators=(",", ":"), default=str).encode()
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def _error(handler: BaseHTTPRequestHandler, status: int, code: str,
           detail: str | None = None) -> None:
    payload: dict[str, Any] = {"error": {"code": code}}
    if detail is not None:
        payload["error"]["detail"] = detail
    _json(handler, status, payload)


def _validate_create(body: Any) -> dict[str, Any]:
    """D7: reject malformed input before it can reach persistence."""
    if not isinstance(body, dict):
        raise RequestInvalid("body must be a JSON object")
    key = body.get("idempotency_key")
    if not isinstance(key, str) or not key.strip() or len(key) > IDEMPOTENCY_KEY_MAX_CHARS:
        raise RequestInvalid(
            f"idempotency_key must be a non-empty string of at most {IDEMPOTENCY_KEY_MAX_CHARS} chars")
    account = body.get("account_id")
    if isinstance(account, bool) or not isinstance(account, int) or account <= 0:
        raise RequestInvalid("account_id must be a positive integer")
    brief = body.get("brief")
    if not isinstance(brief, str) or not brief.strip() or len(brief) > BRIEF_MAX_CHARS:
        raise RequestInvalid(f"brief must be a non-empty string of at most {BRIEF_MAX_CHARS} chars")
    family = body.get("task_family")
    if not isinstance(family, str) or not TASK_FAMILY_RE.match(family):
        raise RequestInvalid("task_family must match ^[a-z0-9][a-z0-9_-]{0,63}$")
    budget = body.get("budget")
    if budget is not None and not isinstance(budget, dict):
        raise RequestInvalid("budget must be a JSON object when present")
    return {"idempotency_key": key.strip(), "account_id": account, "brief": brief,
            "task_family": family, "budget": budget}


def _lookup_by_key(repo: ServiceRepo, key: str, loop: _Loop) -> dict[str, Any] | None:
    """D2: the replay lookup. Repos without it keep the named 409 fallback."""
    lookup = getattr(repo, "get_episode_by_idempotency_key", None)
    if not callable(lookup):
        return None
    return loop.run(lookup(key))


def _is_shape_error(exc: BaseException) -> bool:
    return getattr(exc, "code", None) == SHAPE_ERROR_CODE


def _valid_episode_row(row: Any) -> bool:
    """D6 defence in depth: a repo row without an id is a contract violation."""
    return isinstance(row, dict) and bool(row.get("id"))


def make_handler(repo: ServiceRepo, loop: _Loop):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: Any) -> None:  # keep test output clean
            return

        def do_GET(self) -> None:
            path = urlparse(self.path).path
            if path == "/healthz":
                try:
                    health = loop.run(repo.health())
                except ServiceTimeout as exc:
                    return _json(self, 504, {"ok": False, "service": "forge",
                                             "error": {"code": exc.code, "detail": str(exc)}})
                except Exception:
                    log.exception("health check failed")
                    return _json(self, 503, {"ok": False, "service": "forge",
                                             "error": {"code": "E_SERVICE_UNAVAILABLE"}})
                if not isinstance(health, dict) or health.get("ok") is not True:
                    return _json(self, 503, {"ok": False, "service": "forge",
                                             "error": {"code": "E_SERVICE_UNHEALTHY"},
                                             "detail": health})
                return _json(self, 200, {"ok": True, "service": "forge", "repo": health})
            prefix = "/v1/episodes/"
            if path.startswith(prefix):
                episode_id = path[len(prefix):]
                if not episode_id or "/" in episode_id:
                    return _error(self, 404, "E_EPISODE_NOT_FOUND")
                try:
                    row = loop.run(repo.get_episode(episode_id))
                except ServiceTimeout as exc:
                    return _error(self, 504, exc.code, str(exc))
                except Exception as exc:
                    if _is_shape_error(exc):
                        log.exception("episode row violated the service contract")
                        return _error(self, 500, SHAPE_ERROR_CODE, str(exc))
                    log.exception("episode read failed")
                    return _error(self, 503, "E_SERVICE_UNAVAILABLE")
                if row is None:
                    return _error(self, 404, "E_EPISODE_NOT_FOUND")
                if not _valid_episode_row(row):
                    log.error("episode row violated the service contract: keys=%s",
                              sorted(row) if isinstance(row, dict) else type(row).__name__)
                    return _error(self, 500, SHAPE_ERROR_CODE, "episode row is missing id")
                return _json(self, 200, {"episode": row})
            return _error(self, 404, "E_NOT_FOUND")

        def do_POST(self) -> None:
            if urlparse(self.path).path != "/v1/episodes":
                return _error(self, 404, "E_NOT_FOUND")
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > MAX_BODY_BYTES:
                    raise RequestInvalid(f"body size must be 1..{MAX_BODY_BYTES} bytes")
                body = json.loads(self.rfile.read(length))
                fields = _validate_create(body)
            except (RequestInvalid, ValueError, KeyError, json.JSONDecodeError) as exc:
                return _error(self, 400, "E_REQUEST_INVALID", str(exc))
            try:
                row = loop.run(repo.create_episode(**fields))
            except ServiceTimeout as exc:
                return _error(self, 504, exc.code, str(exc))
            except Exception as exc:
                if getattr(exc, "sqlstate", None) == "23505":
                    existing = _lookup_by_key(repo, fields["idempotency_key"], loop)
                    if existing is not None:
                        return _json(self, 200, {"episode": existing, "replayed": True})
                    return _error(self, 409, "E_EPISODE_EXISTS")
                if _is_shape_error(exc):
                    log.exception("episode row violated the service contract")
                    return _error(self, 500, SHAPE_ERROR_CODE, str(exc))
                log.exception("episode create failed")
                return _error(self, 503, "E_SERVICE_UNAVAILABLE")
            return _json(self, 201, {"episode": row})

    return Handler


def make_server(repo: ServiceRepo | None = None, *, repo_factory=None,
                host: str = "127.0.0.1", port: int = 8092,
                call_timeout_s: float = 30.0) -> ThreadingHTTPServer:
    if host not in ("127.0.0.1", "::1", "localhost"):
        raise ValueError("Forge service must bind loopback")
    if (repo is None) == (repo_factory is None):
        raise ValueError("pass exactly one of repo or repo_factory")
    loop = _Loop(call_timeout_s)
    try:
        if repo_factory is not None:
            repo = loop.run(repo_factory())
        server = ThreadingHTTPServer((host, port), make_handler(repo, loop))
    except BaseException:
        loop.stop()
        raise
    server.forge_loop = loop  # type: ignore[attr-defined]
    server.forge_repo = repo  # type: ignore[attr-defined]
    return server


def serve(repo: ServiceRepo | None = None, *, repo_factory=None,
          host: str = "127.0.0.1", port: int = 8092,
          call_timeout_s: float = 30.0) -> ThreadingHTTPServer:
    server = make_server(repo, repo_factory=repo_factory, host=host, port=port,
                         call_timeout_s=call_timeout_s)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server
