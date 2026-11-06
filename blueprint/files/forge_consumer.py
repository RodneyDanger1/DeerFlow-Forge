"""Worker-callable consumer: job payload -> ToolCall -> gateway -> persisted result.

The worker treats a raised exception as a failed job. A refused or failed tool
result is therefore converted to a named ``ConsumerError``; it must never look
like a successful job.
"""
from __future__ import annotations

from typing import Any, Protocol

from forge_gateway import PolicyError, ToolCall, ToolResult


class ConsumerError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


class GatewayLike(Protocol):
    async def execute(self, call: ToolCall, token: str) -> ToolResult: ...


REQUIRED = ("episode_id", "tool_id")


def payload_to_call(payload: Any) -> ToolCall:
    """Validate the job payload at the boundary; no silent string coercion."""
    if not isinstance(payload, dict):
        raise ConsumerError("E_REQUEST_INVALID", "job payload must be an object")
    for field in REQUIRED:
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ConsumerError("E_REQUEST_INVALID",
                                f"{field} must be a non-empty string")
    tool_id = payload["tool_id"]
    cmd_id = payload.get("cmd_id")
    if cmd_id is not None and (not isinstance(cmd_id, str) or not cmd_id.strip()):
        raise ConsumerError("E_REQUEST_INVALID", "cmd_id must be a string or null")
    params = payload.get("params", {})
    if not isinstance(params, dict):
        raise ConsumerError("E_REQUEST_INVALID", "params must be an object")
    paths = payload.get("paths", [])
    if not isinstance(paths, list) or not all(isinstance(p, str) and p for p in paths):
        raise ConsumerError("E_REQUEST_INVALID", "paths must be an array of non-empty strings")
    hashes = payload.get("input_hashes", [])
    if not isinstance(hashes, list) or not all(isinstance(h, str) for h in hashes):
        raise ConsumerError("E_REQUEST_INVALID", "input_hashes must be an array of strings")
    return ToolCall(episode_id=payload["episode_id"].strip(), tool_id=tool_id,
                    cmd_id=cmd_id, params=params, paths=tuple(paths),
                    input_hashes=tuple(hashes))


class ToolCallConsumer:
    """Async worker handler; returns the persisted ToolResult on success."""

    def __init__(self, gateway: GatewayLike, token: str) -> None:
        if not isinstance(token, str) or not token:
            raise ValueError("E_PARAM_REJECTED: token is required")
        self.gateway = gateway
        self.token = token

    async def __call__(self, payload: dict[str, Any]) -> ToolResult:
        call = payload_to_call(payload)
        try:
            result = await self.gateway.execute(call, self.token)
        except PolicyError as exc:
            raise ConsumerError(exc.code, exc.message) from exc
        if result.state == "in_flight":
            raise ConsumerError("E_IDEMPOTENCY_IN_FLIGHT", result.idempotency_key)
        if result.state == "refused":
            raise ConsumerError(result.refusal_code or "E_TOOL_REFUSED", result.message)
        if result.state == "failed":
            raise ConsumerError(result.refusal_code or "E_TOOL_FAILED", result.message)
        if result.state != "succeeded":
            raise ConsumerError("E_TOOL_STATE_UNKNOWN", result.state)
        return result
