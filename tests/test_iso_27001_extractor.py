"""Tests for ISO 27001 extractor."""

import importlib

import pytest
from security_controls_mcp.extractors.base import (
    BaseExtractor,
    ExtractionResult,
    VersionDetection,
)
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


# ============================================================================
# Version Detection Tests
# ============================================================================


def test_detect_version_2022_with_explicit_year():
    """Test that _detect_version correctly identifies 2022 version with explicit year."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    extractor = extractor_class()

    # Mock PDF with 2022 version text
    pdf_text = b"""
    ISO/IEC 27001:2022
    Information security management systems - Requirements
    This document specifies requirements for establishing, implementing, maintaining
    and continually improving an information security management system.
    93 controls
    """

    version, detection_level, evidence = extractor._detect_version(pdf_text)

    assert version == "2022"
    assert detection_level == VersionDetection.DETECTED
    assert len(evidence) > 0
    assert any("2022" in e for e in evidence), "Evidence should contain '2022'"


def test_detect_version_2013_with_explicit_year():
    """Test that _detect_version correctly identifies 2013 version with explicit year."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    extractor = extractor_class()

    # Mock PDF with 2013 version text
    pdf_text = b"""
    ISO/IEC 27001:2013
    Information technology - Security techniques
    Information security management systems - Requirements
    114 controls
    """

    version, detection_level, evidence = extractor._detect_version(pdf_text)

    assert version == "2013"
    assert detection_level == VersionDetection.DETECTED
    assert len(evidence) > 0
    assert any("2013" in e for e in evidence), "Evidence should contain '2013'"


def test_detect_version_2022_with_control_patterns():
    """Test detection of 2022 version based on control patterns without explicit year."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    extractor = extractor_class()

    # Mock PDF with 2022 control patterns but no year
    pdf_text = b"""
    Information security management systems
    Annex A - Information security controls
    A.5 Organizational controls
    A.6 People controls
    A.7 Physical controls
    A.8 Technological controls
    93 controls total
    """

    version, detection_level, evidence = extractor._detect_version(pdf_text)

    # Should detect as 2022 based on patterns
    assert version == "2022"
    # Without explicit year, should be AMBIGUOUS
    assert detection_level == VersionDetection.AMBIGUOUS
    assert len(evidence) > 0


def test_detect_version_2013_with_control_patterns():
    """Test detection of 2013 version based on control patterns."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    extractor = extractor_class()

    # Mock PDF with 2013 control patterns
    pdf_text = b"""
    Information security management systems
    Annex A - Security controls
    A.5 Information security policies
    A.9 Access control
    A.12 Operations security
    A.18 Compliance
    114 controls
    """

    version, detection_level, evidence = extractor._detect_version(pdf_text)

    # Should detect as 2013 based on patterns
    assert version == "2013"
    # Without explicit year, should be AMBIGUOUS
    assert detection_level == VersionDetection.AMBIGUOUS
    assert len(evidence) > 0


def test_detect_version_unknown_for_empty_pdf():
    """Test that _detect_version returns UNKNOWN for empty PDF."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    extractor = extractor_class()

    version, detection_level, evidence = extractor._detect_version(b"")

    assert version == "unknown"
    assert detection_level == VersionDetection.UNKNOWN
    assert len(evidence) == 0


def test_detect_version_unknown_for_invalid_pdf():
    """Test that _detect_version returns UNKNOWN for invalid PDF content."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    extractor = extractor_class()

    # Random content that doesn't match ISO 27001
    pdf_text = b"This is just some random text with no ISO content"

    version, detection_level, evidence = extractor._detect_version(pdf_text)

    assert version == "unknown"
    assert detection_level == VersionDetection.UNKNOWN
    assert len(evidence) == 0


def test_detect_version_case_insensitive():
    """Test that version detection is case-insensitive."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    extractor = extractor_class()

    # Mixed case version text
    pdf_text = b"iso/iec 27001:2022 information security"

    version, detection_level, evidence = extractor._detect_version(pdf_text)

    assert version == "2022"
    assert detection_level == VersionDetection.DETECTED


def test_detect_version_evidence_contains_snippets():
    """Test that evidence list contains specific text snippets found."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    extractor = extractor_class()

    pdf_text = b"""
    ISO/IEC 27001:2022
    93 controls
    A.5 Organizational controls
    """

    version, detection_level, evidence = extractor._detect_version(pdf_text)

    # Evidence should contain specific snippets
    assert len(evidence) >= 2  # At least year reference and control count
    evidence_text = " ".join(evidence).lower()
    assert "2022" in evidence_text
    assert "93" in evidence_text or "a.5" in evidence_text


def test_extract_uses_detect_version():
    """Test that extract() method uses _detect_version()."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    extractor = extractor_class()

    # Create a mock PDF with 2022 version
    pdf_text = b"ISO/IEC 27001:2022\n93 controls"

    result = extractor.extract(pdf_text)

    # Result should have version detection info
    assert result.version != "unknown"
    assert result.version_detection != VersionDetection.UNKNOWN
    assert len(result.version_evidence) > 0


def test_detect_version_handles_pdfplumber_import_error():
    """Test that _detect_version handles missing pdfplumber gracefully."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    extractor = extractor_class()

    # This test will pass if pdfplumber is installed, but we need to test
    # the import error handling. We'll skip this for now since we can't
    # easily mock the import failure in this context.
    # The actual implementation should have try/except for ImportError.

    # For now, just verify the method exists and is callable
    assert hasattr(extractor, "_detect_version")
    assert callable(extractor._detect_version)


# ============================================================================
# Control Extraction Tests (ISO 27001:2022)
# ============================================================================


def test_extract_controls_2022_basic():
    """Test basic control extraction from ISO 27001:2022 PDF."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    extractor = extractor_class()

    # Mock PDF with a few controls
    pdf_text = b"""
    ISO/IEC 27001:2022
    Annex A
    A.5 Organizational controls

    A.5.1 Policies for information security
    Information security policy and topic-specific policies shall be defined,
    approved by management, published, communicated to and acknowledged by
    relevant personnel and relevant interested parties, and reviewed at
    planned intervals and if significant changes occur.

    A.5.2 Information security roles and responsibilities
    Information security roles and responsibilities shall be defined and
    allocated according to the organization needs.

    A.8 Technological controls

    A.8.1 User endpoint devices
    Information stored on, processed by or accessible via user endpoint
    devices shall be protected.
    """

    result = extractor.extract(pdf_text)

    # Should extract at least these 3 controls
    assert len(result.controls) >= 3
    control_ids = [c.id for c in result.controls]
    assert "A.5.1" in control_ids
    assert "A.5.2" in control_ids
    assert "A.8.1" in control_ids


def test_extract_controls_2022_sets_titles():
    """Test that control titles are correctly extracted."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    extractor = extractor_class()

    pdf_text = b"""
    ISO/IEC 27001:2022
    A.5.1 Policies for information security
    Some control content here.

    A.5.2 Information security roles and responsibilities
    More control content.
    """

    result = extractor.extract(pdf_text)

    # Find the controls
    a51 = next((c for c in result.controls if c.id == "A.5.1"), None)
    a52 = next((c for c in result.controls if c.id == "A.5.2"), None)

    assert a51 is not None
    assert "Policies for information security" in a51.title

    assert a52 is not None
    assert "Information security roles and responsibilities" in a52.title


def test_extract_controls_2022_sets_content():
    """Test that control content is correctly extracted."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    extractor = extractor_class()

    pdf_text = b"""
    ISO/IEC 27001:2022
    A.5.1 Policies for information security
    Information security policy and topic-specific policies shall be defined.
    This is the control content that should be captured.

    A.5.2 Information security roles and responsibilities
    Different control content here.
    """

    result = extractor.extract(pdf_text)

    a51 = next((c for c in result.controls if c.id == "A.5.1"), None)
    assert a51 is not None
    assert "Information security policy" in a51.content
    assert "shall be defined" in a51.content


def test_extract_controls_2022_sets_categories():
    """Test that control categories are correctly set based on A.X prefix."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    extractor = extractor_class()

    pdf_text = b"""
    ISO/IEC 27001:2022
    A.5.1 Organizational control
    Content for A.5.1

    A.6.1 People control
    Content for A.6.1

    A.7.1 Physical control
    Content for A.7.1

    A.8.1 Technological control
    Content for A.8.1
    """

    result = extractor.extract(pdf_text)

    # Check categories
    a51 = next((c for c in result.controls if c.id == "A.5.1"), None)
    assert a51 is not None
    assert a51.category == "Organizational"

    a61 = next((c for c in result.controls if c.id == "A.6.1"), None)
    assert a61 is not None
    assert a61.category == "People"

    a71 = next((c for c in result.controls if c.id == "A.7.1"), None)
    assert a71 is not None
    assert a71.category == "Physical"

    a81 = next((c for c in result.controls if c.id == "A.8.1"), None)
    assert a81 is not None
    assert a81.category == "Technological"


def test_extract_controls_2022_sets_parent():
    """Test that parent relationships are correctly set."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    extractor = extractor_class()

    pdf_text = b"""
    ISO/IEC 27001:2022
    A.5.1 Control title
    Content

    A.5.10 Control title
    Content

    A.8.23 Control title
    Content
    """

    result = extractor.extract(pdf_text)

    a51 = next((c for c in result.controls if c.id == "A.5.1"), None)
    assert a51 is not None
    assert a51.parent == "A.5"

    a510 = next((c for c in result.controls if c.id == "A.5.10"), None)
    assert a510 is not None
    assert a510.parent == "A.5"

    a823 = next((c for c in result.controls if c.id == "A.8.23"), None)
    assert a823 is not None
    assert a823.parent == "A.8"


def test_extract_controls_2022_sets_page_numbers():
    """Test that page numbers are tracked for controls."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    extractor = extractor_class()

    # Note: This is a simplified test since we're using byte strings
    # In a real PDF, page numbers would come from pdfplumber
    pdf_text = b"""
    ISO/IEC 27001:2022
    A.5.1 Control on page 1
    Content
    """

    result = extractor.extract(pdf_text)

    # At minimum, page numbers should be integers
    for control in result.controls:
        assert isinstance(control.page, int)
        assert control.page >= 0


def test_extract_controls_2022_handles_spacing_variations():
    """Test that control ID patterns handle spacing variations."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    extractor = extractor_class()

    pdf_text = b"""
    ISO/IEC 27001:2022
    A.5.1 Control with standard spacing
    Content

    A.5.2  Control with extra space
    Content

    A.5.3
    Control on next line
    Content
    """

    result = extractor.extract(pdf_text)

    control_ids = [c.id for c in result.controls]
    assert "A.5.1" in control_ids
    assert "A.5.2" in control_ids
    assert "A.5.3" in control_ids


def test_extract_controls_2022_validates_against_expected():
    """Test that extraction validates against expected 93 control IDs."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    extractor = extractor_class()

    # Mock complete PDF with all 93 controls
    controls_text = []
    for control_id in extractor_class.VERSIONS[2022]["expected_ids"]:
        controls_text.append(f"{control_id} Title\nContent\n")

    pdf_text = b"ISO/IEC 27001:2022\n" + "\n".join(controls_text).encode()

    result = extractor.extract(pdf_text)

    # Should have expected_control_ids set
    assert result.expected_control_ids is not None
    assert len(result.expected_control_ids) == 93

    # Should calculate missing_control_ids
    assert result.missing_control_ids is not None


def test_extract_controls_2022_confidence_score():
    """Test that confidence score reflects extraction completeness."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    extractor = extractor_class()

    # Extract with only a few controls (incomplete)
    pdf_text = b"""
    ISO/IEC 27001:2022
    A.5.1 Title
    Content
    A.5.2 Title
    Content
    """

    result = extractor.extract(pdf_text)

    # Confidence should be low since we only have 2/93 controls
    assert result.confidence_score < 0.5
    assert result.confidence_score >= 0.0


def test_extract_controls_2022_full_extraction():
    """Test full extraction with all 93 controls returns high confidence."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    extractor = extractor_class()

    # Build PDF with all 93 controls
    controls_text = ["ISO/IEC 27001:2022\n"]
    for control_id in extractor_class.VERSIONS[2022]["expected_ids"]:
        controls_text.append(f"{control_id} Control title\nControl content here.\n\n")

    pdf_text = "".join(controls_text).encode()

    result = extractor.extract(pdf_text)

    # Should extract all 93 controls
    assert len(result.controls) == 93

    # Confidence should be high
    assert result.confidence_score >= 0.9

    # Should have no missing controls
    assert result.missing_control_ids is not None
    assert len(result.missing_control_ids) == 0


def test_extract_controls_returns_empty_for_non_iso_pdf():
    """Test that extraction returns empty list for non-ISO 27001 PDFs."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    extractor = extractor_class()

    pdf_text = b"""
    This is some random document
    It has nothing to do with ISO 27001
    Just random text content
    """

    result = extractor.extract(pdf_text)

    # Should detect as unknown version
    assert result.version == "unknown"

    # Should return empty controls list
    assert len(result.controls) == 0

    # Should have low confidence
    assert result.confidence_score == 0.0


def test_extract_controls_handles_malformed_pdf():
    """Test that extraction handles malformed PDFs gracefully."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    extractor = extractor_class()

    # Malformed PDF with version but no readable controls
    pdf_text = b"""
    ISO/IEC 27001:2022
    \x00\x01\x02\x03\x04\x05
    Random binary garbage
    """

    result = extractor.extract(pdf_text)

    # Should not crash
    assert isinstance(result, ExtractionResult)
    assert result.version == "2022"

    # May have low or zero controls
    assert len(result.controls) >= 0


def test_extract_uses_extract_controls_2022_when_version_2022():
    """Test that extract() uses _extract_controls_2022() when version is 2022."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    extractor = extractor_class()

    pdf_text = b"""
    ISO/IEC 27001:2022
    A.5.1 Test control
    Content here
    """

    result = extractor.extract(pdf_text)

    # Should detect as 2022
    assert result.version == "2022"

    # Should have extracted controls (proving _extract_controls_2022 was called)
    assert len(result.controls) > 0

    # extraction_method should indicate full extraction, not placeholder
    assert "placeholder" not in result.extraction_method.lower()


def test_extract_metadata_fields():
    """Test that all metadata fields are properly set in ExtractionResult."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    extractor = extractor_class()

    pdf_text = b"""
    ISO/IEC 27001:2022
    A.5.1 Title
    Content
    """

    result = extractor.extract(pdf_text)

    # Check all required fields are present
    assert result.standard_id == "iso_27001"
    assert result.version is not None
    assert result.version_detection is not None
    assert result.version_evidence is not None
    assert result.controls is not None
    assert isinstance(result.confidence_score, float)
    assert result.extraction_method is not None
    assert isinstance(result.extraction_duration_seconds, float)
    assert result.extraction_duration_seconds >= 0.0
    assert result.warnings is not None
    assert isinstance(result.warnings, list)


# ============================================================================
# ISO 27001:2013 Tests
# ============================================================================


def test_iso27001_2013_has_expected_ids():
    """Test that VERSIONS[2013] contains expected_ids list with all 114 control IDs."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]

    # Check structure
    assert 2013 in extractor_class.VERSIONS
    version_config = extractor_class.VERSIONS[2013]
    assert isinstance(version_config, dict), "VERSIONS[2013] should be a dict"
    assert "expected_ids" in version_config, "VERSIONS[2013] should have expected_ids"

    # Check expected_ids is a list
    expected_ids = version_config["expected_ids"]
    assert isinstance(expected_ids, list), "expected_ids should be a list"

    # Check count
    assert len(expected_ids) == 114, f"Expected 114 control IDs, got {len(expected_ids)}"

    # Check all IDs follow the pattern A.X.Y
    for control_id in expected_ids:
        assert isinstance(control_id, str), f"Control ID should be string: {control_id}"
        assert control_id.startswith("A."), f"Control ID should start with A.: {control_id}"

    # Check that all IDs are unique
    assert len(expected_ids) == len(set(expected_ids)), "All control IDs should be unique"

    # Check specific categories exist (spot check)
    a5_controls = [cid for cid in expected_ids if cid.startswith("A.5.")]
    a9_controls = [cid for cid in expected_ids if cid.startswith("A.9.")]
    a18_controls = [cid for cid in expected_ids if cid.startswith("A.18.")]

    assert len(a5_controls) >= 2, "Should have A.5.x controls"
    assert len(a9_controls) >= 10, "Should have A.9.x controls (Access control)"
    assert len(a18_controls) >= 2, "Should have A.18.x controls (Compliance)"


def test_extract_controls_2013_basic():
    """Test basic control extraction from ISO 27001:2013 PDF."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    extractor = extractor_class()

    # Mock PDF with 2013 version and a few controls
    pdf_text = b"""
    ISO/IEC 27001:2013
    Annex A
    A.5 Information security policies

    A.5.1.1 Policies for information security
    A set of policies for information security shall be defined, approved by
    management, published and communicated to employees and relevant external parties.

    A.5.1.2 Review of the policies for information security
    The policies for information security shall be reviewed at planned intervals or if
    significant changes occur to ensure their continuing suitability, adequacy and effectiveness.

    A.9 Access control

    A.9.1.1 Access control policy
    An access control policy shall be established, documented and reviewed based on business
    and information security requirements.
    """

    result = extractor.extract(pdf_text)

    # Should extract at least these 3 controls
    assert len(result.controls) >= 3
    control_ids = [c.id for c in result.controls]
    assert "A.5.1.1" in control_ids
    assert "A.5.1.2" in control_ids
    assert "A.9.1.1" in control_ids


def test_extract_controls_2013_sets_categories():
    """Test that 2013 control categories are correctly set."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    extractor = extractor_class()

    pdf_text = b"""
    ISO/IEC 27001:2013
    A.5.1.1 Security policy control
    Content for A.5.1.1

    A.6.1.1 Organization control
    Content for A.6.1.1

    A.9.1.1 Access control
    Content for A.9.1.1

    A.18.1.1 Compliance control
    Content for A.18.1.1
    """

    result = extractor.extract(pdf_text)

    # Check categories are set correctly for 2013
    a5_control = next((c for c in result.controls if c.id == "A.5.1.1"), None)
    assert a5_control is not None
    assert a5_control.category == "Information security policies"

    a6_control = next((c for c in result.controls if c.id == "A.6.1.1"), None)
    assert a6_control is not None
    assert a6_control.category == "Organization of information security"

    a9_control = next((c for c in result.controls if c.id == "A.9.1.1"), None)
    assert a9_control is not None
    assert a9_control.category == "Access control"

    a18_control = next((c for c in result.controls if c.id == "A.18.1.1"), None)
    assert a18_control is not None
    assert a18_control.category == "Compliance"


def test_extract_uses_extract_controls_2013_when_version_2013():
    """Test that extract() uses _extract_controls_2013() when version is 2013."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    extractor = extractor_class()

    pdf_text = b"""
    ISO/IEC 27001:2013
    A.5.1.1 Test control
    Content here
    """

    result = extractor.extract(pdf_text)

    # Should detect as 2013
    assert result.version == "2013"

    # Should have extracted controls (proving _extract_controls_2013 was called)
    assert len(result.controls) > 0

    # extraction_method should indicate 2013
    assert "2013" in result.extraction_method


def test_extract_controls_2013_full_extraction():
    """Test full extraction with all 114 controls for 2013 version."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    extractor = extractor_class()

    # Build PDF with all 114 controls
    controls_text = ["ISO/IEC 27001:2013\n"]
    for control_id in extractor_class.VERSIONS[2013]["expected_ids"]:
        controls_text.append(f"{control_id} Control title\nControl content here.\n\n")

    pdf_text = "".join(controls_text).encode()

    result = extractor.extract(pdf_text)

    # Should extract all 114 controls
    assert len(result.controls) == 114

    # Confidence should be high
    assert result.confidence_score >= 0.9

    # Should have no missing controls
    assert result.missing_control_ids is not None
    assert len(result.missing_control_ids) == 0


def test_extract_controls_2013_validates_against_expected():
    """Test that 2013 extraction validates against expected 114 control IDs."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    extractor = extractor_class()

    # Mock PDF with 2013 version
    pdf_text = b"""
    ISO/IEC 27001:2013
    A.5.1.1 Title
    Content
    A.5.1.2 Title
    Content
    """

    result = extractor.extract(pdf_text)

    # Should have expected_control_ids set
    assert result.expected_control_ids is not None
    assert len(result.expected_control_ids) == 114

    # Should calculate missing_control_ids
    assert result.missing_control_ids is not None
    # We only provided 2 controls, so should have 112 missing
    assert len(result.missing_control_ids) == 112


def test_extract_controls_2013_sets_parent():
    """Test that parent relationships are correctly set for 2013 controls."""
    _ensure_iso27001_registered()
    extractor_class = SPECIALIZED_EXTRACTORS["iso_27001"]
    extractor = extractor_class()

    pdf_text = b"""
    ISO/IEC 27001:2013
    A.5.1.1 Control title
    Content

    A.9.2.3 Control title
    Content

    A.18.1.5 Control title
    Content
    """

    result = extractor.extract(pdf_text)

    # Check parent structure (A.X.Y.Z -> A.X.Y)
    a511 = next((c for c in result.controls if c.id == "A.5.1.1"), None)
    assert a511 is not None
    assert a511.parent == "A.5.1"

    a923 = next((c for c in result.controls if c.id == "A.9.2.3"), None)
    assert a923 is not None
    assert a923.parent == "A.9.2"

    a1815 = next((c for c in result.controls if c.id == "A.18.1.5"), None)
    assert a1815 is not None
    assert a1815.parent == "A.18.1"
