"""Unit tests for SCFData loader."""

import pytest

from security_controls_mcp.data_loader import SCFData


@pytest.fixture
def scf_data():
    """Fixture providing SCFData instance."""
    return SCFData()


class TestDataLoading:
    """Test data loading and integrity."""

    def test_data_loads_successfully(self, scf_data):
        """Smoke test: Data files load without errors."""
        assert scf_data is not None
        assert scf_data.controls is not None
        assert scf_data.frameworks is not None

    def test_expected_control_count(self, scf_data):
        """Verify expected number of controls loaded."""
        assert len(scf_data.controls) == 1451

    def test_expected_framework_count(self, scf_data):
        """Verify expected number of frameworks loaded."""
        assert len(scf_data.frameworks) == 28

    def test_controls_have_required_fields(self, scf_data):
        """Verify all controls have required fields."""
        required_fields = ["id", "name", "description", "domain", "weight", "framework_mappings"]
        for control in scf_data.controls[:10]:  # Sample check
            for field in required_fields:
                assert field in control, f"Control {control.get('id')} missing field: {field}"

    def test_frameworks_have_correct_structure(self, scf_data):
        """Verify framework metadata structure."""
        for fw_key, fw_data in scf_data.frameworks.items():
            assert "key" in fw_data
            assert "name" in fw_data
            assert "controls_mapped" in fw_data
            assert fw_data["controls_mapped"] > 0


class TestGetControl:
    """Test get_control method."""

    def test_get_existing_control(self, scf_data):
        """Get a control that exists."""
        control = scf_data.get_control("GOV-01")
        assert control is not None
        assert control["id"] == "GOV-01"
        assert "name" in control
        assert "description" in control

    def test_get_nonexistent_control(self, scf_data):
        """Get a control that doesn't exist."""
        control = scf_data.get_control("FAKE-999")
        assert control is None

    def test_control_has_framework_mappings(self, scf_data):
        """Verify control has framework mappings."""
        control = scf_data.get_control("GOV-01")
        assert "framework_mappings" in control
        assert isinstance(control["framework_mappings"], dict)


class TestSearchControls:
    """Test search_controls method."""

    def test_search_returns_results(self, scf_data):
        """Search returns results for common term."""
        results = scf_data.search_controls("encryption", limit=10)
        assert len(results) > 0
        assert len(results) <= 10

    def test_search_case_insensitive(self, scf_data):
        """Search is case insensitive."""
        lower_results = scf_data.search_controls("encryption", limit=5)
        upper_results = scf_data.search_controls("ENCRYPTION", limit=5)
        assert len(lower_results) == len(upper_results)

    def test_search_limit_respected(self, scf_data):
        """Search respects limit parameter."""
        results = scf_data.search_controls("access", limit=3)
        assert len(results) <= 3

    def test_search_with_framework_filter(self, scf_data):
        """Search with framework filter returns only matching controls."""
        results = scf_data.search_controls("encryption", frameworks=["dora"], limit=10)
        for result in results:
            assert "dora" in result["mapped_frameworks"]

    def test_search_no_results(self, scf_data):
        """Search with no matches returns empty list."""
        results = scf_data.search_controls("zzzzznonexistent", limit=10)
        assert results == []


class TestGetFrameworkControls:
    """Test get_framework_controls method."""

    def test_get_dora_controls(self, scf_data):
        """Get DORA framework controls."""
        controls = scf_data.get_framework_controls("dora")
        assert len(controls) == 103

    def test_get_iso27001_controls(self, scf_data):
        """Get ISO 27001 framework controls."""
        controls = scf_data.get_framework_controls("iso_27001_2022")
        assert len(controls) == 51

    def test_framework_controls_structure(self, scf_data):
        """Verify framework controls have correct structure."""
        controls = scf_data.get_framework_controls("dora", include_descriptions=False)
        for control in controls[:5]:  # Sample check
            assert "scf_id" in control
            assert "scf_name" in control
            assert "framework_control_ids" in control
            assert "weight" in control
            assert "description" not in control

    def test_framework_controls_with_descriptions(self, scf_data):
        """Verify descriptions included when requested."""
        controls = scf_data.get_framework_controls("dora", include_descriptions=True)
        for control in controls[:5]:  # Sample check
            assert "description" in control


class TestMapFrameworks:
    """Test map_frameworks method."""

    def test_map_iso_to_dora(self, scf_data):
        """Map ISO 27001 to DORA."""
        mappings = scf_data.map_frameworks("iso_27001_2022", "dora")
        assert len(mappings) > 0

    def test_map_with_source_control_filter(self, scf_data):
        """Map with source control filter."""
        mappings = scf_data.map_frameworks("iso_27001_2022", "dora", "5.1")
        assert len(mappings) >= 1
        for mapping in mappings:
            assert "5.1" in mapping["source_controls"]

    def test_mapping_structure(self, scf_data):
        """Verify mapping result structure."""
        mappings = scf_data.map_frameworks("iso_27001_2022", "dora", "5.1")
        for mapping in mappings:
            assert "scf_id" in mapping
            assert "scf_name" in mapping
            assert "source_controls" in mapping
            assert "target_controls" in mapping
            assert "weight" in mapping

    def test_map_nonexistent_source_framework(self, scf_data):
        """Map with non-existent source framework returns empty."""
        # This should return empty since no controls map to fake framework
        mappings = scf_data.map_frameworks("fake_framework", "dora")
        assert mappings == []


class TestCriticalFrameworks:
    """Test critical framework data integrity."""

    @pytest.mark.parametrize(
        "framework_key,expected_count",
        [
            ("nist_800_53_r5", 777),
            ("soc_2_tsc", 412),
            ("pci_dss_4.0.1", 364),
            ("dora", 103),
            ("iso_27001_2022", 51),
            ("nist_csf_2.0", 253),
        ],
    )
    def test_critical_framework_counts(self, scf_data, framework_key, expected_count):
        """Verify critical frameworks have expected control counts."""
        controls = scf_data.get_framework_controls(framework_key)
        assert (
            len(controls) == expected_count
        ), f"{framework_key} should have {expected_count} controls, got {len(controls)}"
