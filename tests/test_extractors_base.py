"""Tests for base extractor dataclasses."""

from dataclasses import dataclass
from typing import Optional

import pytest

from security_controls_mcp.extractors.base import (
    Control,
    ExtractionComparison,
    ExtractionResult,
    VersionDetection,
)


def test_control_creation():
    """Test creating a Control instance."""
    control = Control(
        id="A.5.1",
        title="Policies for information security",
        content="Information security policy and topic-specific policies shall be defined...",
        page=15,
        category="Organizational controls",
        parent=None,
    )

    assert control.id == "A.5.1"
    assert control.title == "Policies for information security"
    assert "Information security policy" in control.content
    assert control.page == 15
    assert control.category == "Organizational controls"
    assert control.parent is None


def test_control_with_parent():
    """Test Control with parent reference."""
    control = Control(
        id="A.5.1.1",
        title="Sub-control example",
        content="Some content",
        page=16,
        category="Organizational controls",
        parent="A.5.1",
    )

    assert control.parent == "A.5.1"


def test_version_detection_enum():
    """Test VersionDetection enum values."""
    assert VersionDetection.DETECTED.value == "detected"
    assert VersionDetection.AMBIGUOUS.value == "ambiguous"
    assert VersionDetection.UNKNOWN.value == "unknown"

    # Test that we can create from string
    assert VersionDetection("detected") == VersionDetection.DETECTED
    assert VersionDetection("ambiguous") == VersionDetection.AMBIGUOUS
    assert VersionDetection("unknown") == VersionDetection.UNKNOWN


def test_extraction_result_creation():
    """Test creating an ExtractionResult instance."""
    control1 = Control(
        id="A.5.1",
        title="Policies for information security",
        content="Information security policy...",
        page=15,
        category="Organizational controls",
    )
    control2 = Control(
        id="A.5.2",
        title="Information security roles and responsibilities",
        content="Roles and responsibilities...",
        page=16,
        category="Organizational controls",
    )

    result = ExtractionResult(
        standard_id="iso_27001_2022",
        version="2022",
        version_detection=VersionDetection.DETECTED,
        version_evidence=["Found '2022' in title", "Document metadata shows 2022"],
        controls=[control1, control2],
        expected_control_ids=["A.5.1", "A.5.2", "A.5.3"],
        missing_control_ids=["A.5.3"],
        confidence_score=0.95,
        extraction_method="specialized_iso27001",
        extraction_duration_seconds=2.5,
        warnings=["Could not extract control A.5.3"],
    )

    assert result.standard_id == "iso_27001_2022"
    assert result.version == "2022"
    assert result.version_detection == VersionDetection.DETECTED
    assert len(result.version_evidence) == 2
    assert len(result.controls) == 2
    assert len(result.expected_control_ids) == 3
    assert result.missing_control_ids == ["A.5.3"]
    assert result.confidence_score == 0.95
    assert result.extraction_method == "specialized_iso27001"
    assert result.extraction_duration_seconds == 2.5
    assert len(result.warnings) == 1


def test_extraction_result_optional_fields():
    """Test ExtractionResult with optional fields as None."""
    result = ExtractionResult(
        standard_id="nist_800_53_r5",
        version="Rev 5",
        version_detection=VersionDetection.DETECTED,
        version_evidence=["Revision 5 found in header"],
        controls=[],
        expected_control_ids=None,
        missing_control_ids=None,
        confidence_score=0.8,
        extraction_method="generic",
        extraction_duration_seconds=1.0,
        warnings=[],
    )

    assert result.expected_control_ids is None
    assert result.missing_control_ids is None
    assert len(result.warnings) == 0


def test_extraction_comparison_creation():
    """Test creating an ExtractionComparison instance."""
    control1 = Control(
        id="A.5.1",
        title="Policies for information security",
        content="Information security policy...",
        page=15,
        category="Organizational controls",
    )
    control2 = Control(
        id="A.5.2",
        title="Information security roles and responsibilities",
        content="Roles and responsibilities...",
        page=16,
        category="Organizational controls",
    )
    control3 = Control(
        id="A.5.3",
        title="Segregation of duties",
        content="Segregation...",
        page=17,
        category="Organizational controls",
    )

    specialized_result = ExtractionResult(
        standard_id="iso_27001_2022",
        version="2022",
        version_detection=VersionDetection.DETECTED,
        version_evidence=["Found '2022' in title"],
        controls=[control1, control2, control3],
        expected_control_ids=["A.5.1", "A.5.2", "A.5.3"],
        missing_control_ids=[],
        confidence_score=0.95,
        extraction_method="specialized_iso27001",
        extraction_duration_seconds=2.5,
        warnings=[],
    )

    generic_result = ExtractionResult(
        standard_id="iso_27001_2022",
        version="2022",
        version_detection=VersionDetection.DETECTED,
        version_evidence=["Found '2022' in title"],
        controls=[control1, control2],
        expected_control_ids=None,
        missing_control_ids=None,
        confidence_score=0.70,
        extraction_method="generic",
        extraction_duration_seconds=1.5,
        warnings=["Could not extract A.5.3"],
    )

    comparison = ExtractionComparison(
        specialized=specialized_result,
        generic=generic_result,
        controls_in_both=["A.5.1", "A.5.2"],
        unique_to_specialized=["A.5.3"],
        unique_to_generic=[],
        recommendation="use_specialized",
    )

    assert comparison.specialized == specialized_result
    assert comparison.generic == generic_result
    assert len(comparison.controls_in_both) == 2
    assert comparison.unique_to_specialized == ["A.5.3"]
    assert comparison.unique_to_generic == []
    assert comparison.recommendation == "use_specialized"


def test_extraction_comparison_generic_better():
    """Test ExtractionComparison when generic extractor is better."""
    specialized_result = ExtractionResult(
        standard_id="unknown_standard",
        version="unknown",
        version_detection=VersionDetection.UNKNOWN,
        version_evidence=[],
        controls=[],
        expected_control_ids=["A.1", "A.2"],
        missing_control_ids=["A.1", "A.2"],
        confidence_score=0.0,
        extraction_method="specialized_unknown",
        extraction_duration_seconds=3.0,
        warnings=["Failed to extract controls"],
    )

    control1 = Control(
        id="A.1", title="Control 1", content="Content", page=1, category="Cat"
    )

    generic_result = ExtractionResult(
        standard_id="unknown_standard",
        version="1.0",
        version_detection=VersionDetection.DETECTED,
        version_evidence=["Version 1.0 in header"],
        controls=[control1],
        expected_control_ids=None,
        missing_control_ids=None,
        confidence_score=0.75,
        extraction_method="generic",
        extraction_duration_seconds=1.0,
        warnings=[],
    )

    comparison = ExtractionComparison(
        specialized=specialized_result,
        generic=generic_result,
        controls_in_both=[],
        unique_to_specialized=[],
        unique_to_generic=["A.1"],
        recommendation="use_generic",
    )

    assert comparison.recommendation == "use_generic"
    assert len(comparison.unique_to_generic) == 1
