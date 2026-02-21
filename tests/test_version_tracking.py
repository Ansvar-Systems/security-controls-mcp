"""Tests for premium version tracking tools."""

import json
import os

import pytest
from security_controls_mcp.server import call_tool
from security_controls_mcp.tools.version_tracking import (
    VersionHistory,
    is_premium_enabled,
    upgrade_response,
)


class TestPremiumGating:
    """Test premium env var gating."""

    @pytest.fixture(autouse=True)
    def _clear_premium(self):
        original = os.environ.get("PREMIUM_ENABLED")
        yield
        if original is None:
            os.environ.pop("PREMIUM_ENABLED", None)
        else:
            os.environ["PREMIUM_ENABLED"] = original

    def test_is_premium_enabled_false_when_unset(self):
        os.environ.pop("PREMIUM_ENABLED", None)
        assert is_premium_enabled() is False

    def test_is_premium_enabled_false_when_false(self):
        os.environ["PREMIUM_ENABLED"] = "false"
        assert is_premium_enabled() is False

    def test_is_premium_enabled_true_when_true(self):
        os.environ["PREMIUM_ENABLED"] = "true"
        assert is_premium_enabled() is True

    def test_upgrade_response_structure(self):
        resp = upgrade_response()
        assert resp["premium"] is False
        assert "Intelligence Portal" in resp["message"]
        assert "hello@ansvar.ai" in resp["message"]

    @pytest.mark.asyncio
    async def test_get_control_history_returns_upgrade_when_not_set(self):
        os.environ.pop("PREMIUM_ENABLED", None)
        result = await call_tool("get_control_history", {"control_id": "GOV-01"})
        data = json.loads(result[0].text)
        assert data["premium"] is False
        assert "Intelligence Portal" in data["message"]

    @pytest.mark.asyncio
    async def test_diff_control_returns_upgrade_when_not_set(self):
        os.environ.pop("PREMIUM_ENABLED", None)
        result = await call_tool(
            "diff_control", {"control_id": "GOV-01", "from_version": "2024.4"}
        )
        data = json.loads(result[0].text)
        assert data["premium"] is False

    @pytest.mark.asyncio
    async def test_get_framework_changes_returns_upgrade_when_not_set(self):
        os.environ.pop("PREMIUM_ENABLED", None)
        result = await call_tool(
            "get_framework_changes", {"framework": "iso_27001_2022"}
        )
        data = json.loads(result[0].text)
        assert data["premium"] is False


class TestGetControlHistory:
    """Test get_control_history with premium enabled."""

    @pytest.fixture(autouse=True)
    def _enable_premium(self):
        os.environ["PREMIUM_ENABLED"] = "true"
        yield
        os.environ.pop("PREMIUM_ENABLED", None)

    @pytest.mark.asyncio
    async def test_returns_empty_history_for_unknown_control(self):
        result = await call_tool("get_control_history", {"control_id": "ZZZ-99"})
        data = json.loads(result[0].text)
        assert data["control_id"] == "ZZZ-99"
        assert data["versions"] == []

    @pytest.mark.asyncio
    async def test_returns_valid_structure(self):
        result = await call_tool("get_control_history", {"control_id": "GOV-01"})
        data = json.loads(result[0].text)
        assert "control_id" in data
        assert "versions" in data

    @pytest.mark.asyncio
    async def test_empty_control_id_returns_error(self):
        result = await call_tool("get_control_history", {"control_id": ""})
        assert "Error" in result[0].text or "required" in result[0].text


class TestDiffControl:
    """Test diff_control with premium enabled."""

    @pytest.fixture(autouse=True)
    def _enable_premium(self):
        os.environ["PREMIUM_ENABLED"] = "true"
        yield
        os.environ.pop("PREMIUM_ENABLED", None)

    @pytest.mark.asyncio
    async def test_returns_valid_structure(self):
        result = await call_tool(
            "diff_control", {"control_id": "GOV-01", "from_version": "2024.4"}
        )
        data = json.loads(result[0].text)
        assert "control_id" in data
        assert "from_version" in data
        assert "to_version" in data

    @pytest.mark.asyncio
    async def test_no_data_returns_gracefully(self):
        result = await call_tool(
            "diff_control",
            {"control_id": "GOV-01", "from_version": "2024.4", "to_version": "2025.4"},
        )
        data = json.loads(result[0].text)
        # No version history data yet, should return gracefully
        assert (
            data.get("total_changes", 0) == 0
            or "No version data" in data.get("change_summary", "")
            or data.get("diff") is None
        )


class TestGetFrameworkChanges:
    """Test get_framework_changes with premium enabled."""

    @pytest.fixture(autouse=True)
    def _enable_premium(self):
        os.environ["PREMIUM_ENABLED"] = "true"
        yield
        os.environ.pop("PREMIUM_ENABLED", None)

    @pytest.mark.asyncio
    async def test_returns_valid_structure(self):
        result = await call_tool(
            "get_framework_changes", {"framework": "iso_27001_2022"}
        )
        data = json.loads(result[0].text)
        assert "framework" in data
        assert "changes" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_empty_changes_for_unknown_framework(self):
        result = await call_tool(
            "get_framework_changes", {"framework": "nonexistent_9999"}
        )
        data = json.loads(result[0].text)
        assert data["changes"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_respects_limit(self):
        result = await call_tool(
            "get_framework_changes",
            {"framework": "iso_27001_2022", "limit": 1},
        )
        data = json.loads(result[0].text)
        assert len(data["changes"]) <= 1

    @pytest.mark.asyncio
    async def test_empty_framework_returns_error(self):
        result = await call_tool("get_framework_changes", {"framework": ""})
        assert "Error" in result[0].text or "required" in result[0].text


class TestVersionHistoryLoader:
    """Test the VersionHistory data loader directly."""

    def test_loads_empty_history(self, tmp_path):
        data_dir = tmp_path
        history_file = data_dir / "version-history.json"
        history_file.write_text(json.dumps({"changes": []}))
        vh = VersionHistory(data_dir)
        assert vh.get_control_history("GOV-01") == []

    def test_loads_with_changes(self, tmp_path):
        data_dir = tmp_path
        history_file = data_dir / "version-history.json"
        history_file.write_text(
            json.dumps(
                {
                    "changes": [
                        {
                            "control_id": "GOV-01",
                            "scf_version": "2025.4",
                            "effective_date": "2025-01-15",
                            "change_type": "modified",
                            "summary": "Updated description",
                            "frameworks_affected": ["iso_27001_2022"],
                        }
                    ]
                }
            )
        )
        vh = VersionHistory(data_dir)
        history = vh.get_control_history("GOV-01")
        assert len(history) == 1
        assert history[0]["change_type"] == "modified"

    def test_get_recent_changes_filters_by_date(self, tmp_path):
        data_dir = tmp_path
        history_file = data_dir / "version-history.json"
        history_file.write_text(
            json.dumps(
                {
                    "changes": [
                        {
                            "control_id": "GOV-01",
                            "effective_date": "2024-06-01",
                            "frameworks_affected": ["iso_27001_2022"],
                        },
                        {
                            "control_id": "IAC-05",
                            "effective_date": "2025-03-01",
                            "frameworks_affected": ["nist_csf_2.0"],
                        },
                    ]
                }
            )
        )
        vh = VersionHistory(data_dir)
        recent = vh.get_recent_changes("2025-01-01")
        assert len(recent) == 1
        assert recent[0]["control_id"] == "IAC-05"

    def test_get_framework_changes_filters_by_framework(self, tmp_path):
        data_dir = tmp_path
        history_file = data_dir / "version-history.json"
        history_file.write_text(
            json.dumps(
                {
                    "changes": [
                        {
                            "control_id": "GOV-01",
                            "effective_date": "2025-01-15",
                            "frameworks_affected": ["iso_27001_2022"],
                        },
                        {
                            "control_id": "IAC-05",
                            "effective_date": "2025-03-01",
                            "frameworks_affected": ["nist_csf_2.0"],
                        },
                    ]
                }
            )
        )
        vh = VersionHistory(data_dir)
        changes = vh.get_framework_changes("iso_27001_2022")
        assert len(changes) == 1
        assert changes[0]["control_id"] == "GOV-01"

    def test_handles_missing_file_gracefully(self, tmp_path):
        vh = VersionHistory(tmp_path)
        assert vh.get_control_history("GOV-01") == []
        assert vh.get_recent_changes("2025-01-01") == []
