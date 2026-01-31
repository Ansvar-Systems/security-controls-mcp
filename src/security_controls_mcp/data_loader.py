"""Data loader for SCF controls and framework mappings."""

import json
from pathlib import Path
from typing import Any


class SCFData:
    """Loads and provides access to SCF control data."""

    def __init__(self):
        self.controls: list[dict[str, Any]] = []
        self.controls_by_id: dict[str, dict[str, Any]] = {}
        self.framework_to_scf: dict[str, dict[str, list[str]]] = {}
        self.frameworks: dict[str, dict[str, Any]] = {}
        self._load_data()

    def _load_data(self):
        """Load SCF controls and reverse index from JSON files."""
        data_dir = Path(__file__).parent / "data"

        # Load controls
        with open(data_dir / "scf-controls.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            self.controls = data["controls"]

        # Build ID index
        self.controls_by_id = {ctrl["id"]: ctrl for ctrl in self.controls}

        # Load reverse index
        with open(data_dir / "framework-to-scf.json", "r", encoding="utf-8") as f:
            self.framework_to_scf = json.load(f)

        # Build framework metadata
        self._build_framework_metadata()

    def _build_framework_metadata(self):
        """Build framework metadata from controls."""
        # Framework display names (keys must match actual data which uses dots in version numbers)
        framework_names = {
            # Original 16 frameworks
            "nist_csf_2.0": "NIST Cybersecurity Framework 2.0",
            "nist_800_53_r5": "NIST SP 800-53 Revision 5",
            "iso_27001_2022": "ISO/IEC 27001:2022",
            "iso_27002_2022": "ISO/IEC 27002:2022",
            "cis_csc_8.1": "CIS Critical Security Controls v8.1",
            "pci_dss_4.0.1": "PCI DSS v4.0.1",
            "cmmc_2.0_level_1": "CMMC 2.0 Level 1",
            "cmmc_2.0_level_2": "CMMC 2.0 Level 2",
            "soc_2_tsc": "SOC 2 (TSC 2017:2022)",
            "dora": "Digital Operational Resilience Act (DORA)",
            "nis2": "Network and Information Security Directive (NIS2)",
            "gdpr": "General Data Protection Regulation (GDPR)",
            "ncsc_caf_4.0": "NCSC Cyber Assessment Framework 4.0",
            "uk_cyber_essentials": "UK Cyber Essentials",
            "fedramp_r5_moderate": "FedRAMP Revision 5 (Moderate)",
            "hipaa_security_rule": "HIPAA Security Rule",
            # Tier 1: APAC (3 frameworks)
            "australia_essential_8": "Australian Essential Eight",
            "australia_ism_2024": "Australian ISM (June 2024)",
            "singapore_mas_trm_2021": "Singapore MAS TRM 2021",
            # Tier 1: Industry/Privacy (2 frameworks)
            "swift_cscf_2023": "SWIFT Customer Security Framework 2023",
            "nist_privacy_framework_1_0": "NIST Privacy Framework 1.0",
            # Tier 2: European National (6 frameworks)
            "netherlands": "Netherlands Cybersecurity Regulations",
            "norway": "Norway Cybersecurity Regulations",
            "sweden": "Sweden Cybersecurity Regulations",
            "germany": "Germany Cybersecurity Regulations",
            "germany_bait": "Germany BAIT (Banking IT Requirements)",
            "germany_c5_2020": "Germany C5:2020 (Cloud Controls)",
            # Tier 3: Cloud (1 framework)
            "csa_ccm_4": "CSA Cloud Controls Matrix v4",
        }

        # Count controls per framework
        for fw_key, fw_name in framework_names.items():
            count = sum(1 for ctrl in self.controls if ctrl["framework_mappings"].get(fw_key))
            self.frameworks[fw_key] = {
                "key": fw_key,
                "name": fw_name,
                "controls_mapped": count,
            }

    def get_control(self, control_id: str) -> dict[str, Any] | None:
        """Get control by SCF ID."""
        return self.controls_by_id.get(control_id)

    def search_controls(
        self, query: str, frameworks: list[str] | None = None, limit: int = 10
    ) -> list[dict[str, Any]]:
        """Search controls by description. Case-insensitive string matching for v1."""
        query_lower = query.lower()
        results = []

        for ctrl in self.controls:
            # Check if query matches name or description (case-insensitive)
            name_lower = ctrl["name"].lower() if ctrl["name"] else ""
            desc_lower = ctrl["description"].lower() if ctrl["description"] else ""

            if query_lower in name_lower or query_lower in desc_lower:
                # Filter by frameworks if specified
                if frameworks:
                    has_mapping = any(ctrl["framework_mappings"].get(fw) for fw in frameworks)
                    if not has_mapping:
                        continue

                # Get mapped frameworks for response
                mapped_frameworks = [
                    fw for fw, mappings in ctrl["framework_mappings"].items() if mappings
                ]

                # Create snippet (simple version - first 150 chars with highlight)
                desc = ctrl["description"]
                idx = desc.lower().find(query_lower)
                if idx >= 0:
                    start = max(0, idx - 50)
                    end = min(len(desc), idx + len(query) + 100)
                    snippet = desc[start:end]
                    if start > 0:
                        snippet = "..." + snippet
                    if end < len(desc):
                        snippet = snippet + "..."
                else:
                    snippet = desc[:150] + "..." if len(desc) > 150 else desc

                results.append(
                    {
                        "control_id": ctrl["id"],
                        "name": ctrl["name"],
                        "snippet": snippet,
                        "relevance": 1.0,  # Simple scoring for v1
                        "mapped_frameworks": mapped_frameworks,
                    }
                )

                if len(results) >= limit:
                    break

        return results

    def get_framework_controls(
        self, framework: str, include_descriptions: bool = False
    ) -> list[dict[str, Any]]:
        """Get all controls that map to a framework."""
        results = []

        for ctrl in self.controls:
            fw_mappings = ctrl["framework_mappings"].get(framework)
            if fw_mappings:
                result = {
                    "scf_id": ctrl["id"],
                    "scf_name": ctrl["name"],
                    "framework_control_ids": fw_mappings,
                    "weight": ctrl["weight"],
                }

                if include_descriptions:
                    result["description"] = ctrl["description"]

                results.append(result)

        return results

    def map_frameworks(
        self,
        source_framework: str,
        target_framework: str,
        source_control: str | None = None,
    ) -> list[dict[str, Any]]:
        """Map controls between two frameworks via SCF."""
        results = []

        # If source_control specified, filter to only controls with that mapping
        for ctrl in self.controls:
            source_mappings = ctrl["framework_mappings"].get(source_framework)
            target_mappings = ctrl["framework_mappings"].get(target_framework)

            # Skip if no source mapping
            if not source_mappings:
                continue

            # Filter by source_control if specified
            if source_control and source_control not in source_mappings:
                continue

            results.append(
                {
                    "scf_id": ctrl["id"],
                    "scf_name": ctrl["name"],
                    "source_controls": source_mappings,
                    "target_controls": target_mappings or [],
                    "weight": ctrl["weight"],
                }
            )

        return results
