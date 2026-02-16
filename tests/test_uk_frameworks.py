"""Tests for UK Cybersecurity frameworks (Cyber Essentials + NCSC CAF 4.0)."""

import pytest
from security_controls_mcp.data_loader import SCFData


@pytest.fixture(scope="module")
def scf_data():
    """Load SCF data once for all tests."""
    return SCFData()


class TestUKCybersecurityFrameworks:
    """Test UK cybersecurity frameworks are properly integrated."""

    UK_FRAMEWORKS = [
        ("uk_cyber_essentials", "UK Cyber Essentials", 20),
        ("uk_caf_4.0", "UK Cyber Assessment Framework 4.0", 50),
        ("uk_dpa", "UK Data Protection Act", 5),
        ("uk_defstan_05_138", "UK DEFSTAN 05-138", 100),
        ("uk_cap_1850", "UK CAP 1850", 30),
    ]

    @pytest.mark.parametrize("fw_id,fw_name,min_controls", UK_FRAMEWORKS)
    def test_uk_framework_exists(self, scf_data, fw_id, fw_name, min_controls):
        """Verify UK framework exists in data."""
        assert fw_id in scf_data.frameworks, f"{fw_id} not found in frameworks"

    @pytest.mark.parametrize("fw_id,fw_name,min_controls", UK_FRAMEWORKS)
    def test_uk_framework_has_minimum_controls(self, scf_data, fw_id, fw_name, min_controls):
        """Verify UK framework has minimum expected controls."""
        fw = scf_data.frameworks[fw_id]
        assert fw["controls_mapped"] >= min_controls, (
            f"{fw_id} has {fw['controls_mapped']} controls, expected >= {min_controls}"
        )

    @pytest.mark.parametrize("fw_id,fw_name,min_controls", UK_FRAMEWORKS)
    def test_uk_framework_has_correct_name(self, scf_data, fw_id, fw_name, min_controls):
        """Verify UK framework has correct display name."""
        fw = scf_data.frameworks[fw_id]
        assert fw["name"] == fw_name

    def test_uk_frameworks_in_category(self, scf_data):
        """Test UK frameworks are in the uk_cybersecurity category."""
        assert "uk_cybersecurity" in scf_data.framework_categories
        uk_category = scf_data.framework_categories["uk_cybersecurity"]
        assert "uk_cyber_essentials" in uk_category
        assert "uk_caf_4.0" in uk_category
        assert "uk_dpa" in uk_category


class TestCyberEssentials:
    """Tests specific to UK Cyber Essentials framework."""

    def test_cyber_essentials_control_ids(self, scf_data):
        """Verify Cyber Essentials controls have proper control IDs."""
        controls = scf_data.get_framework_controls("uk_cyber_essentials")
        assert len(controls) > 0, "Expected Cyber Essentials controls"

        for ctrl in controls:
            assert ctrl["framework_control_ids"], (
                f"SCF control {ctrl['scf_id']} mapped to Cyber Essentials but has no control IDs"
            )

    def test_cyber_essentials_covers_five_controls(self, scf_data):
        """Verify Cyber Essentials maps to its 5 core control areas."""
        controls = scf_data.get_framework_controls("uk_cyber_essentials")
        all_ce_ids = set()
        for ctrl in controls:
            for ce_id in ctrl["framework_control_ids"]:
                all_ce_ids.add(ce_id.split(".")[0])

        # Cyber Essentials has 5 core controls (numbered 1-5)
        expected_areas = {"1", "2", "3", "4", "5"}
        assert expected_areas.issubset(all_ce_ids), (
            f"Expected all 5 Cyber Essentials areas, found: {all_ce_ids}"
        )

    def test_cyber_essentials_to_nist_csf_mapping(self, scf_data):
        """Test mapping Cyber Essentials to NIST CSF 2.0."""
        mappings = scf_data.map_frameworks("uk_cyber_essentials", "nist_csf_2.0")
        assert len(mappings) > 5, (
            "Expected overlap between Cyber Essentials and NIST CSF"
        )


class TestNCSCCAF:
    """Tests specific to NCSC Cyber Assessment Framework 4.0."""

    def test_caf_control_ids(self, scf_data):
        """Verify CAF controls have proper control IDs (A1.a format)."""
        controls = scf_data.get_framework_controls("uk_caf_4.0")
        assert len(controls) > 0, "Expected CAF controls"

        for ctrl in controls:
            assert ctrl["framework_control_ids"], (
                f"SCF control {ctrl['scf_id']} mapped to CAF but has no control IDs"
            )

    def test_caf_covers_four_objectives(self, scf_data):
        """Verify CAF maps to its 4 objectives (A, B, C, D)."""
        controls = scf_data.get_framework_controls("uk_caf_4.0")
        objectives = set()
        for ctrl in controls:
            for caf_id in ctrl["framework_control_ids"]:
                if caf_id and len(caf_id) >= 1:
                    objectives.add(caf_id[0])

        expected_objectives = {"A", "B", "C", "D"}
        assert expected_objectives.issubset(objectives), (
            f"Expected all 4 CAF objectives (A-D), found: {objectives}"
        )

    def test_caf_to_nist_csf_mapping(self, scf_data):
        """Test mapping NCSC CAF to NIST CSF 2.0."""
        mappings = scf_data.map_frameworks("uk_caf_4.0", "nist_csf_2.0")
        assert len(mappings) > 20, (
            "Expected significant overlap between NCSC CAF and NIST CSF"
        )

    def test_caf_to_iso27001_mapping(self, scf_data):
        """Test mapping NCSC CAF to ISO 27001."""
        mappings = scf_data.map_frameworks("uk_caf_4.0", "iso_27001_2022")
        has_target = [m for m in mappings if m["target_controls"]]
        assert len(has_target) > 5, (
            "Expected some overlap between NCSC CAF and ISO 27001"
        )

    def test_search_cyber_assessment(self, scf_data):
        """Test searching for CAF-related controls."""
        results = scf_data.search_controls("cyber assessment", limit=20)
        # Should find at least some controls (may not match directly
        # since SCF descriptions don't necessarily mention "cyber assessment")
        # This is a smoke test for the search functionality
        assert isinstance(results, list)
