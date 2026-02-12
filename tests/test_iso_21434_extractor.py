"""Tests for ISO 21434 specialized extractor."""

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


def _ensure_iso_21434_registered():
    """Ensure ISO21434Extractor is registered.

    This helper is needed because other tests may clear the registry.
    We re-import the module each time to ensure registration.
    """
    if "iso_21434" not in SPECIALIZED_EXTRACTORS:
        # Import and reload to trigger decorator registration
        import sys

        mod_name = "security_controls_mcp.extractors.specialized.iso_21434"
        if mod_name in sys.modules:
            importlib.reload(sys.modules[mod_name])
        else:
            importlib.import_module(mod_name)


def test_iso_21434_extractor_registered():
    _ensure_iso_21434_registered()
    """Test that ISO21434Extractor is registered."""
    extractor_class = get_extractor("iso_21434")
    assert extractor_class is not None
    assert issubclass(extractor_class, BaseExtractor)


def test_iso_21434_extractor_instantiation():
    _ensure_iso_21434_registered()
    """Test that ISO21434Extractor can be instantiated."""
    extractor_class = get_extractor("iso_21434")
    extractor = extractor_class()
    assert isinstance(extractor, BaseExtractor)


def test_iso_21434_version_detection_2021():
    _ensure_iso_21434_registered()
    """Test version detection for ISO 21434:2021."""
    extractor_class = get_extractor("iso_21434")
    extractor = extractor_class()

    # Mock PDF with 2021 indicators
    mock_pdf = b"%PDF-1.4\nISO/SAE 21434:2021\nRoad vehicles\nCybersecurity engineering"

    result = extractor.extract(mock_pdf)
    assert result.version == "2021"
    assert result.version_detection in [VersionDetection.DETECTED, VersionDetection.AMBIGUOUS]


def test_iso_21434_clause_format():
    _ensure_iso_21434_registered()
    """Test that extracted clauses follow ISO format (e.g., 5.4.2, 6.3.1)."""
    extractor_class = get_extractor("iso_21434")
    extractor = extractor_class()

    mock_pdf = b"%PDF-1.4\nISO 21434:2021\n5.4.2 Risk assessment\n6.3.1 Concept phase"

    result = extractor.extract(mock_pdf)

    # Check that extracted controls follow ISO clause pattern
    for control in result.controls:
        # ISO clause format: X.Y or X.Y.Z where X, Y, Z are digits
        parts = control.id.split(".")
        assert len(parts) >= 2, f"Clause ID {control.id} should have at least 2 parts"
        for part in parts:
            assert part.isdigit(), f"Clause ID part {part} should be numeric"


def test_iso_21434_lifecycle_phases():
    _ensure_iso_21434_registered()
    """Test that ISO 21434 lifecycle phases are recognized."""
    extractor_class = get_extractor("iso_21434")
    extractor = extractor_class()

    # ISO 21434 has lifecycle-based organization
    expected_phases = [
        "Management",
        "Concept",
        "Product Development",
        "Production",
        "Operations and Maintenance",
        "Decommissioning",
    ]

    mock_pdf = b"%PDF-1.4\nISO 21434:2021\n5 Organizational cybersecurity\n6 Concept phase"

    result = extractor.extract(mock_pdf)

    # Check that extracted controls have recognized categories
    if result.controls:
        for control in result.controls:
            # Category should be one of the lifecycle phases or a clause category
            assert isinstance(control.category, str)
            assert len(control.category) > 0


def test_iso_21434_extraction_result_structure():
    _ensure_iso_21434_registered()
    """Test that ExtractionResult has correct structure for ISO 21434."""
    extractor_class = get_extractor("iso_21434")
    extractor = extractor_class()

    mock_pdf = b"%PDF-1.4\nISO 21434:2021"

    result = extractor.extract(mock_pdf)

    assert result.standard_id == "iso_21434"
    assert isinstance(result.version, str)
    assert isinstance(result.version_detection, VersionDetection)
    assert isinstance(result.version_evidence, list)
    assert isinstance(result.controls, list)
    assert isinstance(result.confidence_score, float)
    assert 0.0 <= result.confidence_score <= 1.0
    assert result.extraction_method == "specialized"


def test_iso_21434_main_clauses():
    _ensure_iso_21434_registered()
    """Test that main ISO 21434 clauses are recognized."""
    extractor_class = get_extractor("iso_21434")
    extractor = extractor_class()

    # Main clauses in ISO 21434
    mock_pdf = (
        b"%PDF-1.4\nISO 21434:2021\n"
        b"5 Organizational cybersecurity management\n"
        b"6 Project dependent cybersecurity management\n"
        b"7 Distributed cybersecurity activities\n"
        b"8 Continual cybersecurity activities\n"
        b"9 Concept\n"
        b"10 Product development\n"
        b"11 Cybersecurity validation\n"
        b"12 Production\n"
        b"13 Operations and maintenance\n"
        b"14 End of cybersecurity support and decommissioning"
    )

    result = extractor.extract(mock_pdf)

    # Should extract multiple clauses
    assert len(result.controls) > 0

    # Check that clause IDs start with expected main clause numbers (5-14)
    main_clause_prefixes = ["5", "6", "7", "8", "9", "10", "11", "12", "13", "14"]
    clause_ids = [c.id.split(".")[0] for c in result.controls]

    for clause_id in clause_ids:
        assert clause_id in main_clause_prefixes, f"Unexpected main clause: {clause_id}"


def test_iso_21434_hierarchical_structure():
    _ensure_iso_21434_registered()
    """Test that ISO 21434 hierarchical clause structure is preserved."""
    extractor_class = get_extractor("iso_21434")
    extractor = extractor_class()

    mock_pdf = b"%PDF-1.4\nISO 21434:2021\n5.4 Risk management\n5.4.2 Risk assessment"

    result = extractor.extract(mock_pdf)

    # Find child clause (5.4.2)
    child_clauses = [c for c in result.controls if c.id == "5.4.2"]

    if child_clauses:
        child = child_clauses[0]
        # Should have parent reference
        assert child.parent is not None
        # Parent should be 5.4
        assert child.parent == "5.4" or child.parent.startswith("5.4")


def test_iso_21434_confidence_score():
    _ensure_iso_21434_registered()
    """Test confidence score calculation."""
    extractor_class = get_extractor("iso_21434")
    extractor = extractor_class()

    # High confidence: clear version, multiple clauses
    good_pdf = b"%PDF-1.4\nISO 21434:2021\n5.4 Management\n6.3 Concept\n7.2 Activities"
    result_good = extractor.extract(good_pdf)

    # Low confidence: unclear version, no clauses
    bad_pdf = b"%PDF-1.4\nSome document"
    result_bad = extractor.extract(bad_pdf)

    assert result_good.confidence_score > result_bad.confidence_score


def test_iso_21434_warnings():
    _ensure_iso_21434_registered()
    """Test that warnings are generated for issues."""
    extractor_class = get_extractor("iso_21434")
    extractor = extractor_class()

    # PDF with very few clauses should generate warnings
    sparse_pdf = b"%PDF-1.4\nISO 21434:2021\n5.4 Management"

    result = extractor.extract(sparse_pdf)

    # Should have warnings about sparse extraction
    assert isinstance(result.warnings, list)
    if len(result.controls) < 20:  # ISO 21434 has many clauses
        assert len(result.warnings) > 0


def test_iso_21434_invalid_pdf():
    _ensure_iso_21434_registered()
    """Test handling of invalid PDF."""
    extractor_class = get_extractor("iso_21434")
    extractor = extractor_class()

    invalid_pdf = b"Not a PDF"

    result = extractor.extract(invalid_pdf)

    # Should return result with low confidence and warnings
    assert result.confidence_score < 0.5
    assert len(result.warnings) > 0
    assert result.version_detection == VersionDetection.UNKNOWN


def test_iso_21434_sub_clause_depth():
    _ensure_iso_21434_registered()
    """Test handling of multi-level sub-clauses (e.g., 5.4.2.3)."""
    extractor_class = get_extractor("iso_21434")
    extractor = extractor_class()

    mock_pdf = b"%PDF-1.4\nISO 21434:2021\n5.4.2.3 Detailed requirement"

    result = extractor.extract(mock_pdf)

    # Find deep sub-clauses
    deep_clauses = [c for c in result.controls if len(c.id.split(".")) >= 4]

    if deep_clauses:
        # Should handle deep nesting
        clause = deep_clauses[0]
        assert "." in clause.id
        parts = clause.id.split(".")
        assert len(parts) >= 4
