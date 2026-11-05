"""MCP JSON-RPC surface: the agent contract must be correct without a database.

Covers initialize, tools/list, unknown tools/methods, bad arguments, and the
notification rule (no id -> no reply).
"""
from __future__ import annotations

import pytest

from pod_pipeline import mcp_server

EXPECTED_TOOLS = {"list_pending_assets", "trigger_pipeline_job", "get_fourthwall_status"}


async def test_initialize_reports_protocol_and_tools_capability() -> None:
    resp = await mcp_server.handle_rpc({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
    assert resp["id"] == 1
    result = resp["result"]
    assert result["protocolVersion"] == mcp_server.PROTOCOL
    assert "tools" in result["capabilities"]
    assert result["serverInfo"]["name"] == "pod-pipeline"


async def test_tools_list_publishes_a_closed_schema_per_tool() -> None:
    resp = await mcp_server.handle_rpc({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    tools = {t["name"]: t for t in resp["result"]["tools"]}
    assert set(tools) == EXPECTED_TOOLS
    for name, tool in tools.items():
        schema = tool["inputSchema"]
        assert schema["type"] == "object", name
        assert schema["additionalProperties"] is False, f"{name} accepts unknown arguments"
        assert tool.get("description"), f"{name} has no description"


async def test_tools_declare_read_only_versus_mutating_annotations() -> None:
    """An agent client uses these hints for policy; a wrong hint is a capability lie."""
    resp = await mcp_server.handle_rpc({"jsonrpc": "2.0", "id": 20, "method": "tools/list"})
    tools = {t["name"]: t for t in resp["result"]["tools"]}
    for name, tool in tools.items():
        annotations = tool.get("annotations")
        assert annotations, f"{name} declares no annotations"
        assert annotations.get("title"), f"{name} has no annotation title"
        assert isinstance(annotations.get("readOnlyHint"), bool), name
        assert isinstance(annotations.get("destructiveHint"), bool), name
        assert isinstance(annotations.get("idempotentHint"), bool), name
        assert isinstance(annotations.get("openWorldHint"), bool), name
    assert tools["list_pending_assets"]["annotations"]["readOnlyHint"] is True
    assert tools["get_fourthwall_status"]["annotations"]["readOnlyHint"] is True
    assert tools["trigger_pipeline_job"]["annotations"]["readOnlyHint"] is False
    # Trigger queues work and spawns a process; it never deletes anything.
    assert tools["trigger_pipeline_job"]["annotations"]["destructiveHint"] is False
    # Repeating it while a live run exists returns that run (unique live-run index).
    assert tools["trigger_pipeline_job"]["annotations"]["idempotentHint"] is True


async def test_trigger_requires_both_arguments() -> None:
    for args, expected in (({}, "required"), ({"asset_id": 1}, "product_type must be one of")):
        resp = await mcp_server.handle_rpc(
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
             "params": {"name": "trigger_pipeline_job", "arguments": args}})
        result = resp["result"]
        assert result["isError"] is True, f"missing arguments were accepted: {args}"
        assert expected in result["content"][0]["text"]


async def test_trigger_rejects_an_unknown_product_type_by_name() -> None:
    resp = await mcp_server.handle_rpc(
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
         "params": {"name": "trigger_pipeline_job",
                    "arguments": {"asset_id": 1, "product_type": "posters"}}})
    text = resp["result"]["content"][0]["text"]
    assert resp["result"]["isError"] is True
    assert "product_type must be one of" in text
    for name in ("apparel", "knitwear", "accessories", "odd_3d", "stationery"):
        assert name in text


async def test_unknown_tool_is_a_named_error() -> None:
    resp = await mcp_server.handle_rpc(
        {"jsonrpc": "2.0", "id": 5, "method": "tools/call",
         "params": {"name": "drop_tables", "arguments": {}}})
    assert resp["result"]["isError"] is True
    assert "unknown tool drop_tables" in resp["result"]["content"][0]["text"]


async def test_unknown_method_returns_method_not_found() -> None:
    resp = await mcp_server.handle_rpc({"jsonrpc": "2.0", "id": 6, "method": "resources/list"})
    assert resp["error"]["code"] == -32601


async def test_notifications_are_never_answered() -> None:
    """MCP notifications carry no id; a reply would desynchronise the client."""
    assert await mcp_server.handle_rpc({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None


async def test_non_object_params_is_rejected() -> None:
    resp = await mcp_server.handle_rpc(
        {"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": ["tools/list"]})
    assert resp["error"]["code"] == -32602


async def test_ping_is_supported() -> None:
    resp = await mcp_server.handle_rpc({"jsonrpc": "2.0", "id": 8, "method": "ping"})
    assert resp == {"jsonrpc": "2.0", "id": 8, "result": {}}


@pytest.mark.parametrize("limit", [0, 201, -5])
async def test_list_pending_assets_bounds_the_page_size(limit: int) -> None:
    """The tool refuses an out-of-range page size before touching the database."""
    resp = await mcp_server.handle_rpc(
        {"jsonrpc": "2.0", "id": 9, "method": "tools/call",
         "params": {"name": "list_pending_assets", "arguments": {"limit": limit}}})
    result = resp["result"]
    assert result["isError"] is True
    assert "limit must be between 1 and 200" in result["content"][0]["text"]
