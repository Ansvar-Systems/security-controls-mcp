"""Tests for extractor registry pattern."""

import pytest

from security_controls_mcp.extractors.registry import (
    register_extractor,
    get_extractor,
    SPECIALIZED_EXTRACTORS,
)


@pytest.fixture(autouse=True)
def clear_registry():
    """Clear registry before and after each test."""
    SPECIALIZED_EXTRACTORS.clear()
    yield
    SPECIALIZED_EXTRACTORS.clear()


def test_register_extractor_decorator():
    """Test that @register_extractor adds class to registry."""
    @register_extractor("test_standard")
    class TestExtractor:
        pass

    assert "test_standard" in SPECIALIZED_EXTRACTORS
    assert SPECIALIZED_EXTRACTORS["test_standard"] == TestExtractor


def test_get_extractor():
    """Test get_extractor retrieves registered class."""
    @register_extractor("another_standard")
    class AnotherExtractor:
        pass

    extractor = get_extractor("another_standard")
    assert extractor == AnotherExtractor

    missing = get_extractor("nonexistent")
    assert missing is None


def test_register_extractor_duplicate_overwrites():
    """Test that re-registering a pattern overwrites previous."""
    @register_extractor("duplicate")
    class FirstExtractor:
        pass

    @register_extractor("duplicate")
    class SecondExtractor:
        pass

    assert get_extractor("duplicate") == SecondExtractor


def test_register_extractor_empty_pattern():
    """Test behavior with empty pattern."""
    @register_extractor("")
    class EmptyExtractor:
        pass

    assert get_extractor("") == EmptyExtractor


def test_get_extractor_case_sensitive():
    """Test that pattern matching is case-sensitive."""
    @register_extractor("ISO_27001")
    class UpperExtractor:
        pass

    assert get_extractor("ISO_27001") == UpperExtractor
    assert get_extractor("iso_27001") is None
