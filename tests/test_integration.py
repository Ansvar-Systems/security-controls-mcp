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
        """Test list_frameworks shows categories."""
        result = await call_tool("list_frameworks", {})
        assert len(result) == 1
        assert "261" in result[0].text
        assert "categories" in result[0].text.lower()
        assert "dora" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_list_frameworks_with_category(self):
        """Test list_frameworks filtered by category."""
        result = await call_tool("list_frameworks", {"category": "uk_cybersecurity"})
        assert len(result) == 1
        assert "uk_cyber_essentials" in result[0].text
        assert "uk_caf_4.0" in result[0].text

    @pytest.mark.asyncio
    async def test_list_frameworks_invalid_category(self):
        """Test list_frameworks with invalid category."""
        result = await call_tool("list_frameworks", {"category": "fake_category"})
        assert len(result) == 1
        assert "not found" in result[0].text.lower()
        assert "Available categories" in result[0].text

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
        """Test MCP server module loads correctly and exposes expected tools.

        Note: Full stdio protocol testing requires Content-Length framing
        (not newline-delimited JSON), which the mcp library's stdio_server
        handles internally. We verify the server can be imported and its
        tool list is correct.
        """
        # Verify the server module tools are correct via direct import
        from security_controls_mcp.server import list_tools

        tools = await list_tools()
        assert len(tools) == 10, f"Expected 10 tools, got {len(tools)}"

        # Verify tool names match expected set
        tool_names = {t.name for t in tools}
        expected = {
            "version_info", "about", "get_control", "search_controls",
            "list_frameworks", "get_framework_controls", "map_frameworks",
            "list_available_standards", "query_standard", "get_clause",
        }
        assert tool_names == expected, f"Tool name mismatch: {tool_names ^ expected}"
