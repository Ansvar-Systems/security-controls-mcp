"""Tests for paid standards functionality."""

import json
import tempfile
from pathlib import Path

import pytest

from security_controls_mcp.config import Config
from security_controls_mcp.providers import PaidStandardProvider, StandardMetadata
from security_controls_mcp.registry import StandardRegistry


class TestConfig:
    """Test configuration management."""

    def test_config_creates_directories(self):
        """Test that config creates necessary directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(Path(tmpdir) / "test-config")
            assert config.config_dir.exists()
            assert config.standards_dir.exists()
            assert config.config_file.exists()

    def test_config_default_structure(self):
        """Test default config structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(Path(tmpdir) / "test-config")
            assert "standards" in config.data
            assert "query_settings" in config.data
            assert "legal" in config.data

    def test_add_and_get_standard(self):
        """Test adding and retrieving standards."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(Path(tmpdir) / "test-config")

            config.add_standard(
                standard_id="test_standard",
                path="test_standard",
                enabled=True,
            )

            enabled = config.get_enabled_standards()
            assert "test_standard" in enabled
            assert enabled["test_standard"]["enabled"] is True

    def test_disable_standard(self):
        """Test disabling a standard."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(Path(tmpdir) / "test-config")

            config.add_standard("test_standard", "test_standard", enabled=True)
            config.add_standard("test_standard", "test_standard", enabled=False)

            enabled = config.get_enabled_standards()
            assert "test_standard" not in enabled

    def test_remove_standard(self):
        """Test removing a standard."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(Path(tmpdir) / "test-config")

            config.add_standard("test_standard", "test_standard")
            assert "test_standard" in config.data["standards"]

            config.remove_standard("test_standard")
            assert "test_standard" not in config.data["standards"]


class TestPaidStandardProvider:
    """Test paid standard provider."""

    @pytest.fixture
    def mock_standard_dir(self):
        """Create a mock standard directory with test data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            standard_dir = Path(tmpdir) / "mock_standard"
            standard_dir.mkdir()

            # Create metadata
            metadata = {
                "standard_id": "mock_std",
                "title": "Mock Standard",
                "version": "1.0",
                "purchased_from": "Test Vendor",
                "purchase_date": "2026-01-29",
                "imported_date": "2026-01-29T12:00:00",
                "license": "Proprietary",
                "pages": 10,
                "restrictions": ["Personal use only"],
            }

            with open(standard_dir / "metadata.json", "w") as f:
                json.dump(metadata, f)

            # Create full text - structure is what gets loaded
            full_text = {
                "structure": {
                    "sections": [
                        {
                            "id": "1",
                            "title": "Introduction",
                            "page": 1,
                            "content": "This is the introduction section.",
                            "subsections": [
                                {
                                    "id": "1.1",
                                    "title": "Purpose",
                                    "page": 1,
                                    "content": "The purpose of this standard is...",
                                    "subsections": [],
                                }
                            ],
                        },
                        {
                            "id": "2",
                            "title": "Requirements",
                            "page": 5,
                            "content": "The requirements are...",
                            "subsections": [],
                        },
                    ],
                    "annexes": [
                        {
                            "id": "A",
                            "title": "Controls",
                            "page": 8,
                            "controls": [
                                {
                                    "id": "A.1",
                                    "title": "Access Control",
                                    "content": "Access control requirements...",
                                    "page": 8,
                                    "category": "Annex A",
                                    "type": "normative",
                                }
                            ],
                        }
                    ],
                }
            }

            with open(standard_dir / "full_text.json", "w") as f:
                json.dump(full_text, f)

            yield standard_dir

    def test_provider_loads_metadata(self, mock_standard_dir):
        """Test that provider loads metadata correctly."""
        provider = PaidStandardProvider(mock_standard_dir)
        metadata = provider.get_metadata()

        assert isinstance(metadata, StandardMetadata)
        assert metadata.standard_id == "mock_std"
        assert metadata.title == "Mock Standard"
        assert metadata.version == "1.0"

    def test_provider_search(self, mock_standard_dir):
        """Test searching within a standard."""
        provider = PaidStandardProvider(mock_standard_dir)

        # Search for content in sections
        results = provider.search("introduction", limit=10)
        assert len(results) > 0
        assert any("Introduction" in r.title for r in results)

        # Search for content in annexes
        results = provider.search("access control", limit=10)
        assert len(results) > 0
        assert any("Access Control" in r.title for r in results)

    def test_provider_get_clause(self, mock_standard_dir):
        """Test getting a specific clause."""
        provider = PaidStandardProvider(mock_standard_dir)

        # Get a section
        clause = provider.get_clause("1.1")
        assert clause is not None
        assert clause.clause_id == "1.1"
        assert clause.title == "Purpose"
        assert "purpose" in clause.content.lower()

        # Get an annex control
        clause = provider.get_clause("A.1")
        assert clause is not None
        assert clause.clause_id == "A.1"
        assert clause.title == "Access Control"

        # Non-existent clause
        clause = provider.get_clause("99.99")
        assert clause is None

    def test_provider_get_all_clauses(self, mock_standard_dir):
        """Test getting all clauses."""
        provider = PaidStandardProvider(mock_standard_dir)
        clauses = provider.get_all_clauses()

        # Should have sections + annex controls
        assert len(clauses) >= 4  # 1, 1.1, 2, A.1


class TestStandardRegistry:
    """Test standard registry."""

    def test_registry_with_no_standards(self):
        """Test registry with no paid standards."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(Path(tmpdir) / "test-config")
            registry = StandardRegistry(config)

            assert not registry.has_paid_standards()
            standards = registry.list_standards()
            assert len(standards) == 1  # Just SCF
            assert standards[0]["type"] == "built-in"

    def test_registry_list_standards(self):
        """Test listing all standards."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(Path(tmpdir) / "test-config")
            registry = StandardRegistry(config)

            standards = registry.list_standards()
            assert len(standards) >= 1
            assert standards[0]["standard_id"] == "scf"
            assert standards[0]["type"] == "built-in"

    def test_registry_get_provider_not_found(self):
        """Test getting a non-existent provider."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(Path(tmpdir) / "test-config")
            registry = StandardRegistry(config)

            provider = registry.get_provider("nonexistent")
            assert provider is None
