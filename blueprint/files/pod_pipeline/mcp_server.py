"""MCP server for the pod pipeline.

Speaks JSON-RPC 2.0 (MCP tools/list + tools/call) on stdio and on
POD_MCP_HOST:POD_MCP_PORT. The three tools are the agent contract:

    list_pending_assets(account_id?)
    trigger_pipeline_job(asset_id, product_type)
    get_fourthwall_status(product_id)

trigger_pipeline_job inserts the orchestrator row and spawns
`python -m pod_pipeline.worker --run-id`. It does not run the craft steps
inside this process. STATE is the lazy handle tests patch.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
import uuid
from typing import Any

from . import db
from .config import ConfigError, Settings
from .fourthwall import FourthwallClient, FourthwallError
from .routes import PRODUCT_TYPES

log = logging.getLogger("pod.mcp")

PROTOCOL = "2024-11-05"


class State:
    def __init__(self) -> None:
        self.settings: Settings | None = None
        self.pool: db.Pool | None = None
        self.lock: asyncio.Lock | None = None


STATE = State()


class ToolError(Exception):
    pass


TOOLS: list[dict[str, Any]] = [
    {
        "name": "list_pending_assets",
        "description": "Assets sitting in the inbox or stuck in queued/processing past POD stuck_after_s.",
        "inputSchema": {
            "type": "object",
            "properties": {"account_id": {"type": "integer"}},
            "additionalProperties": False,
        },
    },
    {
        "name": "trigger_pipeline_job",
        "description": "Enqueue one asset onto one product route and spawn an isolated worker process.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "asset_id": {"type": "integer"},
                "product_type": {"type": "string", "enum": list(PRODUCT_TYPES)},
            },
            "required": ["asset_id", "product_type"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_fourthwall_status",
        "description": "Local fourthwall_products row plus the live product, if Fourthwall has an id. product_id is our row id or the Fourthwall product id.",
        "inputSchema": {
            "type": "object",
            "properties": {"product_id": {"type": "string"}},
            "required": ["product_id"],
            "additionalProperties": False,
        },
    },
]


def dumps(obj: Any) -> str:
    return json.dumps(obj, default=str, separators=(",", ":"))


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, (bytes, memoryview)):
        return None
    return value


def _settings() -> Settings:
    if STATE.settings is None:
        STATE.settings = Settings.from_env()
    return STATE.settings


async def _pool() -> db.Pool:
    if STATE.pool is None:
        STATE.pool = await db.create_pool(_settings())
    return STATE.pool


def _need_int(args: dict[str, Any], name: str, *, required: bool) -> int | None:
    if name not in args or args[name] is None:
        if required:
            raise ToolError(f"{name} is required")
        return None
    try:
        return int(args[name])
    except (TypeError, ValueError) as exc:
        raise ToolError(f"{name} must be an integer") from exc


async def list_pending_assets(arguments: dict[str, Any]) -> dict[str, Any]:
    settings = _settings()
    pool = await _pool()
    account_id = _need_int(arguments, "account_id", required=False)
    rows = await db.pending_assets(pool, stuck_after_s=settings.stuck_after_s, account_id=account_id)
    return {"assets": [_jsonable(r) for r in rows]}


async def _spawn_worker(settings: Settings, run_id: uuid.UUID) -> int:
    log_path = settings.job_logs / "mcp-spawn.log"
    await asyncio.to_thread(log_path.parent.mkdir, 0o750, True, True)
    handle = await asyncio.to_thread(open, log_path, "ab")
    try:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "pod_pipeline.worker", "--run-id", str(run_id),
            cwd=str(settings.root),
            env=os.environ.copy(),
            stdin=asyncio.subprocess.DEVNULL,
            stdout=handle,
            stderr=asyncio.subprocess.STDOUT,
            start_new_session=True,
        )
    finally:
        handle.close()
    if proc.pid is None:
        raise ToolError(f"run {run_id} is queued but the worker pid was not assigned")
    return proc.pid


async def trigger_pipeline_job(arguments: dict[str, Any]) -> dict[str, Any]:
    asset_id = _need_int(arguments, "asset_id", required=True)
    product_type = str(arguments.get("product_type") or "")
    if product_type not in PRODUCT_TYPES:
        raise ToolError(f"product_type must be one of {', '.join(PRODUCT_TYPES)}")
    assert asset_id is not None
    settings = _settings()
    pool = await _pool()

    async def body() -> dict[str, Any]:
        asset = await db.get_asset(pool, asset_id)
        if asset is None:
            raise ToolError(f"asset {asset_id} does not exist")
        run_id, created = await db.enqueue_run(
            pool, account_id=asset["account_id"], asset_id=asset_id, product_type=product_type)
        await db.log_sync(
            pool, account_id=asset["account_id"], direction="inbound", channel="mcp",
            event_type="job.triggered", run_id=run_id,
            payload={"asset_id": asset_id, "product_type": product_type, "created": created})
        if not created:
            return {"run_id": str(run_id), "created": False, "spawned": False, "pid": None}
        try:
            pid = await _spawn_worker(settings, run_id)
        except OSError as exc:
            return {
                "run_id": str(run_id), "created": True, "spawned": False, "pid": None,
                "error": (
                    f"worker did not start ({exc}). The run stays queued; "
                    "pod-worker.timer will claim it."
                ),
            }
        return {"run_id": str(run_id), "created": True, "spawned": True, "pid": pid}

    if STATE.lock is None:
        return await body()
    async with STATE.lock:
        return await body()


async def get_fourthwall_status(arguments: dict[str, Any]) -> dict[str, Any]:
    product_id = str(arguments.get("product_id") or "").strip()
    if not product_id:
        raise ToolError("product_id is required")
    settings = _settings()
    pool = await _pool()
    row = await db.get_product_row(pool, product_id)
    if row is None:
        return {"found": False, "product_id": product_id}
    live: dict[str, Any] | None = None
    live_error: str | None = None
    fw_id = row.get("fw_product_id")
    if fw_id:
        creds = await db.get_fw_credentials(pool, settings, row["account_id"])
        if creds is None:
            live_error = "no Fourthwall credentials configured"
        else:
            try:
                async with FourthwallClient(settings.fw_base_url, creds[0], creds[1]) as fw:
                    live = await fw.get_product(fw_id)
            except FourthwallError as exc:
                live_error = str(exc)[:500]
    return {"found": True, "row": _jsonable(row), "live": live, "live_error": live_error}


async def _dispatch(name: str, arguments: Any) -> dict[str, Any]:
    if not isinstance(arguments, dict):
        raise ToolError("arguments must be an object")
    if name == "list_pending_assets":
        return await list_pending_assets(arguments)
    if name == "trigger_pipeline_job":
        return await trigger_pipeline_job(arguments)
    if name == "get_fourthwall_status":
        return await get_fourthwall_status(arguments)
    raise ToolError(f"unknown tool {name}")


def _ok(rid: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": rid, "result": result}


def _err(rid: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": code, "message": message}}


async def handle_rpc(msg: Any) -> dict[str, Any] | None:
    if not isinstance(msg, dict):
        return _err(None, -32600, "invalid request")
    if "id" not in msg:
        return None
    rid = msg.get("id")
    method = msg.get("method")
    params = msg.get("params") or {}
    if not isinstance(params, dict):
        return _err(rid, -32602, "params must be an object")
    if method == "initialize":
        return _ok(rid, {
            "protocolVersion": PROTOCOL,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "pod-pipeline", "version": "1.0.0"},
        })
    if method == "ping":
        return _ok(rid, {})
    if method == "tools/list":
        return _ok(rid, {"tools": TOOLS})
    if method == "tools/call":
        name = str(params.get("name") or "")
        try:
            result = await _dispatch(name, params.get("arguments") or {})
        except ToolError as exc:
            return _ok(rid, {"content": [{"type": "text", "text": str(exc)}], "isError": True})
        except Exception as exc:
            log.exception("tool %s failed", name)
            text = f"{type(exc).__name__}: {exc}"[:500]
            return _ok(rid, {"content": [{"type": "text", "text": text}], "isError": True})
        return _ok(rid, {"content": [{"type": "text", "text": dumps(result)}], "isError": False})
    return _err(rid, -32601, f"method not found: {method}")


def _http(status: int, body: bytes) -> bytes:
    reason = {200: "OK", 400: "Bad Request", 405: "Method Not Allowed", 500: "Internal Server Error"}[status]
    head = (
        f"HTTP/1.1 {status} {reason}\r\n"
        "Content-Type: application/json\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n\r\n"
    )
    return head.encode("ascii") + body


async def _read_http(reader: asyncio.StreamReader) -> dict[str, Any] | None:
    try:
        head = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), 15)
    except (asyncio.IncompleteReadError, asyncio.LimitOverrunError, asyncio.TimeoutError):
        return None
    if len(head) > 16384:
        return None
    lines = head.decode("iso-8859-1", "replace").split("\r\n")
    parts = lines[0].split(" ")
    if len(parts) < 2:
        return None
    headers: dict[str, str] = {}
    for line in lines[1:]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        headers[key.lower()] = value.strip()
    try:
        length = int(headers.get("content-length", "0") or 0)
    except ValueError:
        return None
    if length < 0 or length > 1_000_000:
        return None
    body = await reader.readexactly(length) if length else b""
    return {"method": parts[0], "path": parts[1].split("?", 1)[0], "body": body}


async def _client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        req = await _read_http(reader)
        if req is None:
            writer.write(_http(400, dumps(_err(None, -32700, "bad http")).encode()))
        elif req["method"] == "GET" and req["path"] == "/health":
            writer.write(_http(200, b'{"ok":true}'))
        elif req["method"] != "POST":
            writer.write(_http(405, b'{"error":"POST JSON-RPC only"}'))
        else:
            try:
                msg = json.loads(req["body"].decode("utf-8") if req["body"] else "null")
            except json.JSONDecodeError:
                writer.write(_http(400, dumps(_err(None, -32700, "parse error")).encode()))
            else:
                resp = await handle_rpc(msg)
                if resp is None:
                    writer.write(b"HTTP/1.1 204 No Content\r\nConnection: close\r\n\r\n")
                else:
                    writer.write(_http(200, dumps(resp).encode()))
        await writer.drain()
    except Exception as exc:
        log.exception("mcp connection failed")
        try:
            writer.write(_http(500, dumps(_err(None, -32603, str(exc)[:300])).encode()))
            await writer.drain()
        except Exception:
            pass
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass


async def serve_http() -> None:
    settings = _settings()
    server = await asyncio.start_server(_client, settings.mcp_host, settings.mcp_port)
    sockets = ", ".join(str(s.getsockname()) for s in server.sockets or [])
    log.info("mcp http listening on %s", sockets)
    async with server:
        await server.serve_forever()


def _frame(obj: dict[str, Any], framed: bool) -> bytes:
    data = dumps(obj).encode()
    if not framed:
        return data + b"\n"
    return f"Content-Length: {len(data)}\r\n\r\n".encode("ascii") + data


async def serve_stdio() -> None:
    loop = asyncio.get_running_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    framed: bool | None = None

    def write(data: bytes) -> None:
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()

    while True:
        peek = await reader.read(1)
        if not peek:
            return
        if peek == b"{":
            rest = await reader.readline()
            raw = peek + rest
            this_framed = False
        else:
            this_framed = True
            header = bytearray(peek)
            while b"\r\n\r\n" not in header and b"\n\n" not in header:
                more = await reader.read(1)
                if not more:
                    return
                header += more
                if len(header) > 16384:
                    return
            text = header.decode("iso-8859-1", "replace")
            sep = "\r\n\r\n" if "\r\n\r\n" in text else "\n\n"
            try:
                length = int(text.lower().split("content-length:", 1)[1].split("\n", 1)[0].strip())
            except (IndexError, ValueError):
                await loop.run_in_executor(None, write, _frame(_err(None, -32700, "missing Content-Length"), True))
                return
            raw = await reader.readexactly(length)
        if framed is None:
            framed = this_framed
        try:
            msg = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            await loop.run_in_executor(None, write, _frame(_err(None, -32700, "parse error"), bool(framed)))
            continue
        resp = await handle_rpc(msg)
        if resp is not None:
            await loop.run_in_executor(None, write, _frame(resp, bool(framed)))


def main() -> None:
    logging.basicConfig(
        level=os.environ.get("POD_LOG_LEVEL", "INFO"), stream=sys.stderr,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(prog="pod_pipeline.mcp_server")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--http", action="store_true")
    mode.add_argument("--stdio", action="store_true")
    mode.add_argument("--call", nargs=2, metavar=("TOOL", "JSON"))
    args = ap.parse_args()
    try:
        if args.call:
            name, raw = args.call
            result = asyncio.run(_dispatch(name, json.loads(raw)))
            print(dumps(result))
            return
        asyncio.run(serve_stdio() if args.stdio else serve_http())
    except ConfigError as exc:
        print(f"configuration error: {exc}", file=sys.stderr)
        sys.exit(2)
    except ToolError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
