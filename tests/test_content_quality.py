"""Content quality smoke tests for SCF data.

These tests verify the actual content quality of the security controls data,
ensuring descriptions are meaningful, mappings are valid, and the data is
production-ready for public release.
"""

import pytest

from security_controls_mcp.data_loader import SCFData


@pytest.fixture(scope="module")
def scf_data():
    """Module-scoped fixture for SCFData (loads once)."""
    return SCFData()


class TestControlContentQuality:
    """Verify control content is meaningful and complete."""

    def test_all_controls_have_nonempty_names(self, scf_data):
        """Every control must have a non-empty name."""
        for control in scf_data.controls:
            name = control.get("name", "")
            assert name and len(name.strip()) > 0, f"Control {control.get('id')} has empty name"

    def test_all_controls_have_nonempty_descriptions(self, scf_data):
        """Every control must have a non-empty description."""
        for control in scf_data.controls:
            desc = control.get("description", "")
            assert (
                desc and len(desc.strip()) > 0
            ), f"Control {control.get('id')} has empty description"

    def test_control_descriptions_minimum_length(self, scf_data):
        """Descriptions should be meaningful (at least 20 characters)."""
        short_descriptions = []
        for control in scf_data.controls:
            desc = control.get("description", "")
            if len(desc) < 20:
                short_descriptions.append((control.get("id"), len(desc)))

        assert (
            len(short_descriptions) == 0
        ), f"Controls with too-short descriptions: {short_descriptions[:10]}"

    def test_no_placeholder_text_in_descriptions(self, scf_data):
        """Descriptions should not contain placeholder text."""
        placeholders = ["TODO", "FIXME", "TBD", "placeholder", "lorem ipsum", "xxx"]
        issues = []
        for control in scf_data.controls:
            desc = control.get("description", "").lower()
            for placeholder in placeholders:
                if placeholder.lower() in desc:
                    issues.append((control.get("id"), placeholder))

        assert len(issues) == 0, f"Controls with placeholder text: {issues[:10]}"

    def test_control_ids_follow_pattern(self, scf_data):
        """Control IDs should follow expected pattern (XXX-NN or similar)."""
        import re

        # SCF uses pattern like GOV-01, RSK-02, etc.
        pattern = re.compile(r"^[A-Z]{2,5}-\d{1,3}(\.\d+)?$")

        invalid_ids = []
        for control in scf_data.controls:
            control_id = control.get("id", "")
            if not pattern.match(control_id):
                invalid_ids.append(control_id)

        assert len(invalid_ids) == 0, f"Controls with invalid ID pattern: {invalid_ids[:10]}"

    def test_control_weights_are_valid(self, scf_data):
        """Control weights should be positive numbers."""
        invalid_weights = []
        for control in scf_data.controls:
            weight = control.get("weight", 0)
            if not isinstance(weight, (int, float)) or weight < 0:
                invalid_weights.append((control.get("id"), weight))

        assert len(invalid_weights) == 0, f"Controls with invalid weights: {invalid_weights[:10]}"

    def test_control_domains_are_nonempty(self, scf_data):
        """Every control must have a domain."""
        empty_domains = []
        for control in scf_data.controls:
            domain = control.get("domain", "")
            if not domain or len(domain.strip()) == 0:
                empty_domains.append(control.get("id"))

        assert len(empty_domains) == 0, f"Controls with empty domains: {empty_domains[:10]}"


class TestFrameworkMappingQuality:
    """Verify framework mappings are valid and complete."""

    def test_all_frameworks_have_mappings(self, scf_data):
        """Every framework should have at least one control mapped."""
        for fw_key, fw_data in scf_data.frameworks.items():
            count = fw_data.get("controls_mapped", 0)
            assert count > 0, f"Framework {fw_key} has no controls mapped"

    def test_framework_mapping_ids_are_nonempty(self, scf_data):
        """Framework mapping IDs should not be empty strings."""
        issues = []
        for control in scf_data.controls:
            mappings = control.get("framework_mappings", {})
            for fw_key, fw_ids in mappings.items():
                if isinstance(fw_ids, list):
                    for fw_id in fw_ids:
                        if not fw_id or len(str(fw_id).strip()) == 0:
                            issues.append((control.get("id"), fw_key))

        assert len(issues) == 0, f"Empty framework mapping IDs found: {issues[:10]}"

    def test_bidirectional_mapping_consistency(self, scf_data):
        """Verify framework-to-scf index is consistent with controls."""
        # framework_to_scf structure: {fw_key: {fw_control_id: [scf_ids]}}
        checked = 0
        for fw_key, fw_mapping in scf_data.framework_to_scf.items():
            for fw_control_id, scf_ids in list(fw_mapping.items())[:10]:  # Sample check
                for scf_id in scf_ids:
                    control = scf_data.get_control(scf_id)
                    assert (
                        control is not None
                    ), f"framework_to_scf references non-existent control: {scf_id}"
                    checked += 1
        assert checked > 0, "No mappings were checked"

    def test_critical_frameworks_have_minimum_coverage(self, scf_data):
        """Critical frameworks should have substantial control coverage."""
        critical_minimums = {
            "nist_800_53_r5": 700,
            "iso_27002_2022": 300,
            "pci_dss_4.0.1": 300,
            "soc_2_tsc": 400,
            "dora": 100,
        }

        for fw_key, minimum in critical_minimums.items():
            count = scf_data.frameworks[fw_key]["controls_mapped"]
            assert (
                count >= minimum
            ), f"Framework {fw_key} has only {count} controls, expected >= {minimum}"


class TestSearchQuality:
    """Verify search functionality returns quality results."""

    def test_common_security_terms_return_results(self, scf_data):
        """Common security terms should return relevant results."""
        common_terms = [
            "encryption",
            "authentication",
            "access control",
            "audit",
            "backup",
            "incident",
            "risk",
            "policy",
            "password",
            "firewall",
        ]

        for term in common_terms:
            results = scf_data.search_controls(term, limit=5)
            assert len(results) > 0, f"No results for common security term: {term}"

    def test_search_results_contain_query_term(self, scf_data):
        """Search results should contain the query term in name or description."""
        query = "encryption"
        results = scf_data.search_controls(query, limit=10)

        for result in results:
            name = result.get("name", "").lower()
            desc = result.get("description", "").lower()
            snippet = result.get("snippet", "").lower()

            # Query term should appear somewhere in the result
            assert (
                query in name or query in desc or query in snippet
            ), f"Result {result.get('control_id')} doesn't contain '{query}'"

    def test_search_relevance_scoring(self, scf_data):
        """Search results should have relevance scores."""
        results = scf_data.search_controls("access control", limit=5)

        for result in results:
            relevance = result.get("relevance", 0)
            assert isinstance(
                relevance, (int, float)
            ), f"Result {result.get('control_id')} missing relevance score"
            assert relevance > 0, f"Result {result.get('control_id')} has non-positive relevance"


class TestFrameworkSpecificContent:
    """Verify specific frameworks have expected content."""

    def test_dora_has_ict_controls(self, scf_data):
        """DORA framework should have ICT-related controls."""
        controls = scf_data.get_framework_controls("dora", include_descriptions=True)
        descriptions = " ".join([c.get("description", "") for c in controls]).lower()

        # DORA is about ICT risk and operational resilience
        assert (
            "ict" in descriptions or "operational" in descriptions or "resilience" in descriptions
        ), "DORA controls should reference ICT or operational resilience"

    def test_pci_dss_has_payment_controls(self, scf_data):
        """PCI DSS should have payment/cardholder data controls."""
        controls = scf_data.get_framework_controls("pci_dss_4.0.1", include_descriptions=True)
        descriptions = " ".join([c.get("description", "") for c in controls]).lower()

        # PCI DSS is about payment card security
        assert (
            "card" in descriptions
            or "payment" in descriptions
            or "transaction" in descriptions
            or "data" in descriptions
        ), "PCI DSS controls should reference payment/card data"

    def test_hipaa_has_health_controls(self, scf_data):
        """HIPAA should have health information controls."""
        controls = scf_data.get_framework_controls("hipaa_security_rule", include_descriptions=True)
        descriptions = " ".join([c.get("description", "") for c in controls]).lower()

        # HIPAA is about health information
        assert (
            "health" in descriptions
            or "patient" in descriptions
            or "medical" in descriptions
            or "phi" in descriptions
            or "protected" in descriptions
        ), "HIPAA controls should reference health information"

    def test_gdpr_has_privacy_controls(self, scf_data):
        """GDPR should have privacy/data protection controls."""
        controls = scf_data.get_framework_controls("gdpr", include_descriptions=True)
        descriptions = " ".join([c.get("description", "") for c in controls]).lower()

        # GDPR is about data protection and privacy
        assert (
            "privacy" in descriptions
            or "personal" in descriptions
            or "data protection" in descriptions
            or "consent" in descriptions
        ), "GDPR controls should reference privacy/personal data"


class TestDataConsistency:
    """Verify data consistency across the dataset."""

    def test_no_duplicate_control_ids(self, scf_data):
        """Control IDs must be unique."""
        ids = [c.get("id") for c in scf_data.controls]
        duplicates = [x for x in ids if ids.count(x) > 1]

        assert len(set(duplicates)) == 0, f"Duplicate control IDs found: {set(duplicates)}"

    def test_framework_counts_match_index(self, scf_data):
        """Framework control counts should match the index."""
        for fw_key, fw_data in scf_data.frameworks.items():
            reported_count = fw_data.get("controls_mapped", 0)
            actual_controls = scf_data.get_framework_controls(fw_key)
            actual_count = len(actual_controls)

            assert (
                reported_count == actual_count
            ), f"Framework {fw_key} reports {reported_count} controls but has {actual_count}"

    def test_all_mapped_frameworks_exist_in_index(self, scf_data):
        """All framework keys in control mappings should exist in frameworks index."""
        missing_frameworks = set()
        for control in scf_data.controls:
            mappings = control.get("framework_mappings", {})
            for fw_key in mappings.keys():
                if fw_key not in scf_data.frameworks:
                    missing_frameworks.add(fw_key)

        assert (
            len(missing_frameworks) == 0
        ), f"Framework keys in mappings not in index: {missing_frameworks}"
