"""Loopback-only Forge HTTP service (stdlib; local source, not deployed).

The service is a thin HTTP seam over a repository. It never calls Craft, never
publishes, and binds loopback by default. Tests may inject a fake repo.
"""
from __future__ import annotations

import asyncio
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Protocol
from urllib.parse import urlparse


class ServiceRepo(Protocol):
    async def create_episode(self, *, idempotency_key: str, account_id: int, brief: str,
                             task_family: str, budget: dict[str, Any] | None = None) -> dict[str, Any]: ...
    async def get_episode(self, episode_id: str) -> dict[str, Any] | None: ...


class _Loop:
    """One event loop for the service thread; repo pools must be created on it."""
    def __init__(self) -> None:
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.loop.run_forever, daemon=True)
        self.thread.start()

    def run(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, self.loop).result(timeout=30)


def _json(handler: BaseHTTPRequestHandler, status: int, body: dict[str, Any]) -> None:
    data = json.dumps(body, separators=(",", ":")).encode()
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def make_handler(repo: ServiceRepo, loop: _Loop):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: Any) -> None:  # keep test output clean
            return

        def do_GET(self) -> None:
            path = urlparse(self.path).path
            if path == "/healthz":
                return _json(self, 200, {"ok": True, "service": "forge"})
            prefix = "/v1/episodes/"
            if path.startswith(prefix):
                episode_id = path[len(prefix):]
                if not episode_id or "/" in episode_id:
                    return _json(self, 404, {"error": {"code": "E_EPISODE_NOT_FOUND"}})
                row = loop.run(repo.get_episode(episode_id))
                if row is None:
                    return _json(self, 404, {"error": {"code": "E_EPISODE_NOT_FOUND"}})
                return _json(self, 200, {"episode": row})
            return _json(self, 404, {"error": {"code": "E_NOT_FOUND"}})

        def do_POST(self) -> None:
            if urlparse(self.path).path != "/v1/episodes":
                return _json(self, 404, {"error": {"code": "E_NOT_FOUND"}})
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > 1_048_576:
                    raise ValueError("body size")
                body = json.loads(self.rfile.read(length))
                key = body["idempotency_key"]
                account = body["account_id"]
                brief = body["brief"]
                family = body["task_family"]
                if not isinstance(key, str) or not key or not isinstance(account, int):
                    raise ValueError("idempotency_key/account_id")
            except (ValueError, KeyError, json.JSONDecodeError) as exc:
                return _json(self, 400, {"error": {"code": "E_REQUEST_INVALID", "detail": str(exc)}})
            row = loop.run(repo.create_episode(
                idempotency_key=key, account_id=account, brief=str(brief),
                task_family=str(family), budget=body.get("budget")))
            return _json(self, 201, {"episode": row})

    return Handler


def asyncio_run(awaitable):
    import asyncio
    return asyncio.run(awaitable)


def make_server(repo: ServiceRepo, *, host: str = "127.0.0.1", port: int = 8092) -> ThreadingHTTPServer:
    if host not in ("127.0.0.1", "::1", "localhost"):
        raise ValueError("Forge service must bind loopback")
    loop = _Loop()
    server = ThreadingHTTPServer((host, port), make_handler(repo, loop))
    server.forge_loop = loop  # type: ignore[attr-defined]
    return server


def serve(repo: ServiceRepo, *, host: str = "127.0.0.1", port: int = 8092) -> None:
    server = make_server(repo, host=host, port=port)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server
