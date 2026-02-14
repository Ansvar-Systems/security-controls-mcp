"""Tests for the about tool."""

import json

import pytest
from security_controls_mcp.server import call_tool


class TestAbout:
    """Test the about tool returns structured Ansvar schema JSON."""

    @pytest.mark.asyncio
    async def test_about_returns_structured_json(self):
        """Test about returns valid structured JSON with expected fields."""
        result = await call_tool("about", {})
        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["server"]["name"] == "Security Controls MCP"
        assert data["dataset"]["jurisdiction"] == "International"
        assert data["dataset"]["counts"]["controls"] > 0
        assert data["dataset"]["counts"]["frameworks"] > 0
        assert data["security"]["access_model"] == "read-only"
        assert data["security"]["network_access"] is False

    @pytest.mark.asyncio
    async def test_about_has_provenance(self):
        """Test about includes provenance with SCF source and Apache license."""
        result = await call_tool("about", {})
        data = json.loads(result[0].text)
        assert "SCF" in data["provenance"]["sources"][0]
        assert "Apache-2.0" in data["provenance"]["license"]

    @pytest.mark.asyncio
    async def test_about_has_fingerprint(self):
        """Test about includes a 12-char data fingerprint."""
        result = await call_tool("about", {})
        data = json.loads(result[0].text)
        assert len(data["dataset"]["fingerprint"]) == 12
        assert data["dataset"]["fingerprint"] != "unknown"

    @pytest.mark.asyncio
    async def test_about_has_server_metadata(self):
        """Test about includes complete server metadata."""
        result = await call_tool("about", {})
        data = json.loads(result[0].text)
        assert data["server"]["package"] == "security-controls-mcp"
        assert data["server"]["suite"] == "Ansvar Compliance Suite"
        assert "github.com" in data["server"]["repository"]
        assert data["server"]["version"] is not None

    @pytest.mark.asyncio
    async def test_about_has_freshness_info(self):
        """Test about includes dataset freshness information."""
        result = await call_tool("about", {})
        data = json.loads(result[0].text)
        assert data["dataset"]["freshness"]["scf_version"] == "2025.4"
        assert data["dataset"]["freshness"]["check_method"] is not None

    @pytest.mark.asyncio
    async def test_about_security_flags(self):
        """Test about reports correct security posture."""
        result = await call_tool("about", {})
        data = json.loads(result[0].text)
        assert data["security"]["access_model"] == "read-only"
        assert data["security"]["network_access"] is False
        assert data["security"]["filesystem_access"] is False
        assert data["security"]["arbitrary_execution"] is False

    @pytest.mark.asyncio
    async def test_about_built_timestamp(self):
        """Test about includes a valid built timestamp."""
        result = await call_tool("about", {})
        data = json.loads(result[0].text)
        built = data["dataset"]["built"]
        assert built != "unknown"
        assert built.endswith("Z")
