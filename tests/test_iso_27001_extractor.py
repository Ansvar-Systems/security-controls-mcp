"""Tests for ISO 27001 extractor."""

import importlib

import pytest
from security_controls_mcp.extractors.base import BaseExtractor, ExtractionResult
from security_controls_mcp.extractors.registry import SPECIALIZED_EXTRACTORS


def _ensure_iso27001_registered():
    """Ensure ISO27001Extractor is registered.

    This helper is needed because other tests may clear the registry.
    We re-import the module each time to ensure registration.
    """
    if "iso_27001" not in SPECIALIZED_EXTRACTORS:
        # Import and reload to trigger decorator registration
        import sys

        mod_name = "security_controls_mcp.extractors.specialized.iso_27001"
        if mod_name in sys.modules:
            importlib.reload(sys.modules[mod_name])
        else:
            importlib.import_module(mod_name)


def test_iso27001_extractor_is_registered():
    """Test that ISO27001Extractor is registered in SPECIALIZED_EXTRACTORS."""
    _ensure_iso27001_registered()

    assert "iso_27001" in SPECIALIZED_EXTRACTORS, (
        f"iso_27001 not found in registry. "
        f"Available: {list(SPECIALIZED_EXTRACTORS.keys())}"
    )
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    assert extractor_class is not None


def test_iso27001_extractor_inherits_from_base():
    """Test that ISO27001Extractor inherits from BaseExtractor."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    assert issubclass(extractor_class, BaseExtractor)


def test_iso27001_extractor_has_versions():
    """Test that ISO27001Extractor has VERSIONS config."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    assert hasattr(extractor_class, "VERSIONS")
    versions = extractor_class.VERSIONS
    assert isinstance(versions, dict)
    assert versions.get(2022) == 93
    assert versions.get(2013) == 114


def test_iso27001_extractor_has_extract_method():
    """Test that ISO27001Extractor has extract method with correct signature."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    extractor = extractor_class()
    assert hasattr(extractor, "extract")
    assert callable(extractor.extract)


def test_iso27001_extractor_extract_returns_extraction_result():
    """Test that extract method returns ExtractionResult."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    extractor = extractor_class()

    # Call with dummy PDF bytes
    result = extractor.extract(pdf_bytes=b"dummy pdf content")

    assert isinstance(result, ExtractionResult)
    assert hasattr(result, "controls")
    assert hasattr(result, "standard_id")
    assert hasattr(result, "version")
    assert hasattr(result, "version_detection")
    assert hasattr(result, "warnings")
