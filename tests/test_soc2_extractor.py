"""Tests for SOC 2 specialized extractor."""

import importlib

import pytest
from security_controls_mcp.extractors.base import (
    BaseExtractor,
    ExtractionResult,
    VersionDetection,
    Control,
)
from security_controls_mcp.extractors.specialized import get_extractor
from security_controls_mcp.extractors.registry import SPECIALIZED_EXTRACTORS


def _ensure_soc2_registered():
    """Ensure SOC2Extractor is registered."""
    if "soc2" not in SPECIALIZED_EXTRACTORS:
        import sys
        mod_name = "security_controls_mcp.extractors.specialized.soc2"
        if mod_name in sys.modules:
            importlib.reload(sys.modules[mod_name])
        else:
            importlib.import_module(mod_name)


def test_soc2_extractor_registered():
    _ensure_soc2_registered()
    """Test that SOC2Extractor is registered."""
    extractor_class = get_extractor("soc2")
    assert extractor_class is not None
    assert issubclass(extractor_class, BaseExtractor)


def test_soc2_version_detection_2017():
    _ensure_soc2_registered()
    """Test version detection for SOC 2 2017."""
    extractor_class = get_extractor("soc2")
    extractor = extractor_class()

    mock_pdf = b"%PDF-1.4\nSOC 2\nTrust Services Criteria\n2017"
    result = extractor.extract(mock_pdf)

    assert result.version in ["2017", "2017_tsc"]
    assert result.version_detection in [VersionDetection.DETECTED, VersionDetection.AMBIGUOUS]


def test_soc2_trust_services_categories():
    _ensure_soc2_registered()
    """Test that SOC 2 Trust Services Categories are recognized."""
    extractor_class = get_extractor("soc2")
    extractor = extractor_class()

    # SOC 2 has 5 Trust Services Categories
    expected_categories = [
        "Security",
        "Availability",
        "Processing Integrity",
        "Confidentiality",
        "Privacy"
    ]

    mock_pdf = b"%PDF-1.4\nSOC 2\nCC1.1 Security\nA1.1 Availability"
    result = extractor.extract(mock_pdf)

    # Check categories are assigned
    for control in result.controls:
        assert control.category in expected_categories or control.category == "Common Criteria"


def test_soc2_control_id_format():
    _ensure_soc2_registered()
    """Test that extracted controls follow SOC 2 format (CC1.1, A1.2, etc.)."""
    extractor_class = get_extractor("soc2")
    extractor = extractor_class()

    mock_pdf = b"%PDF-1.4\nSOC 2\nCC1.1 Control environment\nCC2.1 Communication"
    result = extractor.extract(mock_pdf)

    # SOC 2 format: PREFIX + NUMBER.NUMBER (e.g., CC1.1, A1.2)
    for control in result.controls:
        assert len(control.id) >= 4  # Minimum CC1.1
        # Should have letter prefix and numeric suffix
        parts = control.id.split(".")
        assert len(parts) >= 2


def test_soc2_common_criteria():
    _ensure_soc2_registered()
    """Test that Common Criteria (CC) controls are extracted."""
    extractor_class = get_extractor("soc2")
    extractor = extractor_class()

    mock_pdf = b"%PDF-1.4\nSOC 2 2017\nCC1.1 COSO Principle 1\nCC6.1 Logical access"
    result = extractor.extract(mock_pdf)

    # Should extract CC controls
    cc_controls = [c for c in result.controls if c.id.startswith("CC")]
    assert len(cc_controls) > 0


def test_soc2_extraction_result_structure():
    _ensure_soc2_registered()
    """Test that ExtractionResult has correct structure."""
    extractor_class = get_extractor("soc2")
    extractor = extractor_class()

    mock_pdf = b"%PDF-1.4\nSOC 2"
    result = extractor.extract(mock_pdf)

    assert result.standard_id == "soc2"
    assert isinstance(result.version, str)
    assert isinstance(result.confidence_score, float)
    assert result.extraction_method == "specialized"


def test_soc2_confidence_score():
    _ensure_soc2_registered()
    """Test confidence score calculation."""
    extractor_class = get_extractor("soc2")
    extractor = extractor_class()

    good_pdf = b"%PDF-1.4\nSOC 2 2017\nCC1.1 Control\nCC2.1 Communication"
    result_good = extractor.extract(good_pdf)

    bad_pdf = b"%PDF-1.4\nSome document"
    result_bad = extractor.extract(bad_pdf)

    assert result_good.confidence_score > result_bad.confidence_score


def test_soc2_invalid_pdf():
    _ensure_soc2_registered()
    """Test handling of invalid PDF."""
    extractor_class = get_extractor("soc2")
    extractor = extractor_class()

    invalid_pdf = b"Not a PDF"
    result = extractor.extract(invalid_pdf)

    assert result.confidence_score < 0.5
    assert len(result.warnings) > 0
