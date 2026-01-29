"""Integration tests for MCP server."""

import asyncio
import json
import subprocess
import sys

import pytest

from security_controls_mcp.server import call_tool


class TestToolCalls:
    """Test tool calls directly (without MCP protocol overhead)."""

    @pytest.mark.asyncio
    async def test_get_control_success(self):
        """Test get_control with valid control ID."""
        result = await call_tool("get_control", {"control_id": "GOV-01", "include_mappings": True})
        assert len(result) == 1
        assert "GOV-01" in result[0].text
        assert "Cybersecurity" in result[0].text

    @pytest.mark.asyncio
    async def test_get_control_not_found(self):
        """Test get_control with invalid control ID."""
        result = await call_tool("get_control", {"control_id": "FAKE-999"})
        assert len(result) == 1
        assert "not found" in result[0].text

    @pytest.mark.asyncio
    async def test_search_controls(self):
        """Test search_controls."""
        result = await call_tool("search_controls", {"query": "encryption", "limit": 5})
        assert len(result) == 1
        assert "Found" in result[0].text
        assert "control" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_search_controls_with_framework_filter(self):
        """Test search with framework filter."""
        result = await call_tool(
            "search_controls", {"query": "access control", "frameworks": ["dora"], "limit": 3}
        )
        assert len(result) == 1
        # Should either find results or say no results
        assert len(result[0].text) > 0

    @pytest.mark.asyncio
    async def test_list_frameworks(self):
        """Test list_frameworks."""
        result = await call_tool("list_frameworks", {})
        assert len(result) == 1
        assert "28 total" in result[0].text
        assert "dora" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_get_framework_controls(self):
        """Test get_framework_controls for DORA."""
        result = await call_tool("get_framework_controls", {"framework": "dora"})
        assert len(result) == 1
        assert "103" in result[0].text or "Total Controls" in result[0].text

    @pytest.mark.asyncio
    async def test_get_framework_controls_invalid(self):
        """Test get_framework_controls with invalid framework."""
        result = await call_tool("get_framework_controls", {"framework": "fake_framework"})
        assert len(result) == 1
        assert "not found" in result[0].text

    @pytest.mark.asyncio
    async def test_map_frameworks(self):
        """Test map_frameworks between ISO and DORA."""
        result = await call_tool(
            "map_frameworks",
            {
                "source_framework": "iso_27001_2022",
                "target_framework": "dora",
                "source_control": "5.1",
            },
        )
        assert len(result) == 1
        assert "Mapping" in result[0].text

    @pytest.mark.asyncio
    async def test_map_frameworks_invalid_source(self):
        """Test map_frameworks with invalid source framework."""
        result = await call_tool(
            "map_frameworks", {"source_framework": "fake_framework", "target_framework": "dora"}
        )
        assert len(result) == 1
        assert "not found" in result[0].text


@pytest.mark.slow
class TestMCPProtocol:
    """Test full MCP protocol communication via stdio.

    Note: Uses asyncio.create_subprocess_exec (safe - no shell injection risk)
    as opposed to subprocess.exec() or shell=True variants.
    """

    @pytest.mark.asyncio
    async def test_mcp_server_lifecycle(self):
        """Test MCP server can start, respond, and shutdown cleanly."""
        # Start MCP server as subprocess using safe create_subprocess_exec
        # This does NOT use shell=True, preventing command injection
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            "-m",
            "security_controls_mcp",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        try:
            # Give server time to start
            await asyncio.sleep(0.5)

            # Test initialize
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"},
                },
            }

            process.stdin.write((json.dumps(init_request) + "\n").encode())
            await process.stdin.drain()

            response_line = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
            response = json.loads(response_line.decode())

            assert "result" in response
            assert response["result"]["serverInfo"]["name"] == "security-controls-mcp"

            # Test tools/list
            list_request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}

            process.stdin.write((json.dumps(list_request) + "\n").encode())
            await process.stdin.drain()

            response_line = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
            response = json.loads(response_line.decode())

            assert "result" in response
            assert len(response["result"]["tools"]) == 8  # 5 original + 3 new paid standards tools

            # Test tool call
            call_request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "get_control", "arguments": {"control_id": "GOV-01"}},
            }

            process.stdin.write((json.dumps(call_request) + "\n").encode())
            await process.stdin.drain()

            response_line = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
            response = json.loads(response_line.decode())

            assert "result" in response
            assert len(response["result"]["content"]) > 0

        finally:
            # Cleanup
            process.terminate()
            await process.wait()
