"""Tests for extractor registry pattern."""

from security_controls_mcp.extractors.registry import (
    register_extractor,
    get_extractor,
    SPECIALIZED_EXTRACTORS,
)


def test_register_extractor_decorator():
    """Test that @register_extractor adds class to registry."""
    # Clear registry first
    SPECIALIZED_EXTRACTORS.clear()

    @register_extractor("test_standard")
    class TestExtractor:
        pass

    assert "test_standard" in SPECIALIZED_EXTRACTORS
    assert SPECIALIZED_EXTRACTORS["test_standard"] == TestExtractor


def test_get_extractor():
    """Test get_extractor retrieves registered class."""
    SPECIALIZED_EXTRACTORS.clear()

    @register_extractor("another_standard")
    class AnotherExtractor:
        pass

    extractor = get_extractor("another_standard")
    assert extractor == AnotherExtractor

    missing = get_extractor("nonexistent")
    assert missing is None
