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
    # Check that version configs exist and have count
    assert 2022 in versions
    assert 2013 in versions
    assert versions[2022]["count"] == 93
    assert versions[2013]["count"] == 114


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


def test_iso27001_2022_has_expected_ids():
    """Test that VERSIONS[2022] contains expected_ids list with all 93 control IDs."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]

    # Check structure
    assert 2022 in extractor_class.VERSIONS
    version_config = extractor_class.VERSIONS[2022]
    assert isinstance(version_config, dict), "VERSIONS[2022] should be a dict"
    assert "expected_ids" in version_config, "VERSIONS[2022] should have expected_ids"

    # Check expected_ids is a list
    expected_ids = version_config["expected_ids"]
    assert isinstance(expected_ids, list), "expected_ids should be a list"

    # Check count
    assert len(expected_ids) == 93, f"Expected 93 control IDs, got {len(expected_ids)}"

    # Check all IDs follow the pattern A.X.Y
    for control_id in expected_ids:
        assert isinstance(control_id, str), f"Control ID should be string: {control_id}"
        assert control_id.startswith("A."), f"Control ID should start with A.: {control_id}"

    # Check specific categories are present
    organizational = [cid for cid in expected_ids if cid.startswith("A.5.")]
    people = [cid for cid in expected_ids if cid.startswith("A.6.")]
    physical = [cid for cid in expected_ids if cid.startswith("A.7.")]
    technological = [cid for cid in expected_ids if cid.startswith("A.8.")]

    assert len(organizational) == 37, f"Expected 37 A.5.x controls, got {len(organizational)}"
    assert len(people) == 8, f"Expected 8 A.6.x controls, got {len(people)}"
    assert len(physical) == 14, f"Expected 14 A.7.x controls, got {len(physical)}"
    assert len(technological) == 34, f"Expected 34 A.8.x controls, got {len(technological)}"

    # Check that all IDs are unique
    assert len(expected_ids) == len(set(expected_ids)), "All control IDs should be unique"
