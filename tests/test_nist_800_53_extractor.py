"""Tests for NIST 800-53 specialized extractor."""

import importlib

import pytest
from io import BytesIO
from security_controls_mcp.extractors.base import (
    BaseExtractor,
    ExtractionResult,
    VersionDetection,
    Control,
)
from security_controls_mcp.extractors.specialized import get_extractor
from security_controls_mcp.extractors.registry import SPECIALIZED_EXTRACTORS


def _ensure_nist_800_53_registered():
    """Ensure NIST80053Extractor is registered.

    This helper is needed because other tests may clear the registry.
    We re-import the module each time to ensure registration.
    """
    if "nist_800_53" not in SPECIALIZED_EXTRACTORS:
        # Import and reload to trigger decorator registration
        import sys

        mod_name = "security_controls_mcp.extractors.specialized.nist_800_53"
        if mod_name in sys.modules:
            importlib.reload(sys.modules[mod_name])
        else:
            importlib.import_module(mod_name)


def test_nist_800_53_extractor_registered():
    _ensure_nist_800_53_registered()
    """Test that NIST800_53Extractor is registered."""
    extractor_class = get_extractor("nist_800_53")
    assert extractor_class is not None
    assert issubclass(extractor_class, BaseExtractor)


def test_nist_800_53_extractor_instantiation():
    _ensure_nist_800_53_registered()
    """Test that NIST800_53Extractor can be instantiated."""
    extractor_class = get_extractor("nist_800_53")
    extractor = extractor_class()
    assert isinstance(extractor, BaseExtractor)


def test_nist_800_53_version_detection_r5():
    _ensure_nist_800_53_registered()
    """Test version detection for NIST 800-53 Revision 5."""
    extractor_class = get_extractor("nist_800_53")
    extractor = extractor_class()

    # Mock PDF with R5 indicators
    mock_pdf = b"%PDF-1.4\nNIST Special Publication 800-53\nRevision 5\n320 controls"

    result = extractor.extract(mock_pdf)
    assert result.version == "r5"
    assert result.version_detection in [VersionDetection.DETECTED, VersionDetection.AMBIGUOUS]


def test_nist_800_53_control_id_format():
    _ensure_nist_800_53_registered()
    """Test that extracted controls follow NIST format (e.g., AC-1, AU-2)."""
    extractor_class = get_extractor("nist_800_53")
    extractor = extractor_class()

    mock_pdf = b"%PDF-1.4\nNIST SP 800-53 Rev. 5\nAC-1 Policy and Procedures\nAU-2 Event Logging"

    result = extractor.extract(mock_pdf)

    # Check that extracted controls follow NIST pattern
    for control in result.controls:
        assert "-" in control.id, f"Control ID {control.id} doesn't follow NIST format"
        parts = control.id.split("-")
        assert len(parts) == 2, f"Control ID {control.id} should be FAMILY-NUMBER"


def test_nist_800_53_control_families():
    _ensure_nist_800_53_registered()
    """Test that NIST 800-53 control families are recognized."""
    extractor_class = get_extractor("nist_800_53")
    extractor = extractor_class()

    # NIST 800-53 R5 has 20 control families
    expected_families = [
        "AC",  # Access Control
        "AU",  # Audit and Accountability
        "AT",  # Awareness and Training
        "CM",  # Configuration Management
        "CP",  # Contingency Planning
        "IA",  # Identification and Authentication
        "IR",  # Incident Response
        "MA",  # Maintenance
        "MP",  # Media Protection
        "PS",  # Personnel Security
        "PE",  # Physical and Environmental Protection
        "PL",  # Planning
        "PM",  # Program Management
        "RA",  # Risk Assessment
        "CA",  # Assessment, Authorization, and Monitoring
        "SC",  # System and Communications Protection
        "SI",  # System and Information Integrity
        "SA",  # System and Services Acquisition
        "SR",  # Supply Chain Risk Management
        "PT",  # PII Processing and Transparency
    ]

    # Mock PDF with multiple control families
    mock_pdf = b"%PDF-1.4\nNIST SP 800-53 Rev. 5\nAC-1 Policy\nAU-1 Policy\nSC-1 Policy"

    result = extractor.extract(mock_pdf)

    # Check that extracted controls have valid family prefixes
    for control in result.controls:
        family = control.id.split("-")[0]
        assert family in expected_families, f"Unknown family: {family}"


def test_nist_800_53_extraction_result_structure():
    _ensure_nist_800_53_registered()
    """Test that ExtractionResult has correct structure for NIST 800-53."""
    extractor_class = get_extractor("nist_800_53")
    extractor = extractor_class()

    mock_pdf = b"%PDF-1.4\nNIST SP 800-53 Rev. 5"

    result = extractor.extract(mock_pdf)

    assert result.standard_id == "nist_800_53"
    assert isinstance(result.version, str)
    assert isinstance(result.version_detection, VersionDetection)
    assert isinstance(result.version_evidence, list)
    assert isinstance(result.controls, list)
    assert isinstance(result.confidence_score, float)
    assert 0.0 <= result.confidence_score <= 1.0
    assert result.extraction_method == "specialized"


def test_nist_800_53_expected_control_count_r5():
    _ensure_nist_800_53_registered()
    """Test that NIST 800-53 R5 expects 320 controls."""
    extractor_class = get_extractor("nist_800_53")
    extractor = extractor_class()

    mock_pdf = b"%PDF-1.4\nNIST SP 800-53 Rev. 5"

    result = extractor.extract(mock_pdf)

    # R5 has 320 controls
    if result.expected_control_ids:
        assert len(result.expected_control_ids) == 320


def test_nist_800_53_control_enhancements():
    _ensure_nist_800_53_registered()
    """Test that control enhancements are handled (e.g., AC-1(1))."""
    extractor_class = get_extractor("nist_800_53")
    extractor = extractor_class()

    mock_pdf = b"%PDF-1.4\nNIST SP 800-53 Rev. 5\nAC-1(1) Enhancement One"

    result = extractor.extract(mock_pdf)

    # Check if enhancements are recognized
    enhancement_controls = [c for c in result.controls if "(" in c.id]

    # If enhancements are extracted, verify format
    for control in enhancement_controls:
        assert control.id.count("(") == 1
        assert control.id.count(")") == 1
        assert control.parent is not None, "Enhancement should have parent reference"


def test_nist_800_53_confidence_score():
    _ensure_nist_800_53_registered()
    """Test confidence score calculation."""
    extractor_class = get_extractor("nist_800_53")
    extractor = extractor_class()

    # High confidence: clear version, many controls
    good_pdf = b"%PDF-1.4\nNIST SP 800-53 Revision 5\nAC-1\nAC-2\nAU-1"
    result_good = extractor.extract(good_pdf)

    # Low confidence: unclear version, no controls
    bad_pdf = b"%PDF-1.4\nSome document"
    result_bad = extractor.extract(bad_pdf)

    assert result_good.confidence_score > result_bad.confidence_score


def test_nist_800_53_warnings():
    _ensure_nist_800_53_registered()
    """Test that warnings are generated for issues."""
    extractor_class = get_extractor("nist_800_53")
    extractor = extractor_class()

    # PDF with very few controls should generate warnings
    sparse_pdf = b"%PDF-1.4\nNIST SP 800-53 Rev. 5\nAC-1 Policy"

    result = extractor.extract(sparse_pdf)

    # Should have warnings about missing controls
    assert isinstance(result.warnings, list)
    if len(result.controls) < 100:  # R5 has 320 controls
        assert len(result.warnings) > 0


def test_nist_800_53_invalid_pdf():
    _ensure_nist_800_53_registered()
    """Test handling of invalid PDF."""
    extractor_class = get_extractor("nist_800_53")
    extractor = extractor_class()

    invalid_pdf = b"Not a PDF"

    result = extractor.extract(invalid_pdf)

    # Should return result with low confidence and warnings
    assert result.confidence_score < 0.5
    assert len(result.warnings) > 0
    assert result.version_detection == VersionDetection.UNKNOWN
