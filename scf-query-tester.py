#!/usr/bin/env python3
"""
SCF Query Tester - Demonstrates MCP query patterns
Tests the extracted JSON data with sample queries

Usage:
    python scf-query-tester.py
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


class SCFQueryTester:
    """Demonstrates the query patterns that will be in the MCP server."""

    def __init__(self, controls_file: Path, reverse_index_file: Path):
        print("📂 Loading SCF data...")
        with open(controls_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.controls = {c["id"]: c for c in data["controls"]}

        with open(reverse_index_file, "r", encoding="utf-8") as f:
            self.reverse_index = json.load(f)

        print(f"✅ Loaded {len(self.controls)} controls")
        print(f"✅ Indexed {len(self.reverse_index)} frameworks\n")

    def query_control(self, scf_id: str) -> Optional[Dict]:
        """Query a single SCF control by ID."""
        return self.controls.get(scf_id)

    def query_framework_controls(self, framework_key: str) -> List[Dict]:
        """Get all SCF controls that map to a framework."""
        controls = []
        for control in self.controls.values():
            mapping = control["framework_mappings"].get(framework_key)
            if mapping:
                controls.append(control)
        return controls

    def cross_reference_frameworks(
        self, source_fw: str, source_control: str, target_fw: str
    ) -> List[str]:
        """
        Cross-reference: Find target framework controls that map to source framework control.

        Example: DORA 16.1(a) → ISO 27001 controls
        """
        # Step 1: Find SCF controls for source framework control
        scf_controls = self.reverse_index.get(source_fw, {}).get(source_control, [])

        if not scf_controls:
            return []

        # Step 2: Get target framework mappings for those SCF controls
        target_controls = set()
        for scf_id in scf_controls:
            control = self.controls.get(scf_id)
            if control:
                target_mapping = control["framework_mappings"].get(target_fw)
                if target_mapping:
                    target_controls.update(target_mapping)

        return sorted(target_controls)

    def gap_analysis(self, baseline_fw: str, target_fw: str) -> Dict:
        """
        Compare two frameworks: find controls in target NOT covered by baseline.
        """
        baseline_controls = set()
        target_controls = set()

        for control in self.controls.values():
            if control["framework_mappings"].get(baseline_fw):
                baseline_controls.add(control["id"])
            if control["framework_mappings"].get(target_fw):
                target_controls.add(control["id"])

        gap = target_controls - baseline_controls
        overlap = baseline_controls & target_controls

        return {
            "baseline_controls": len(baseline_controls),
            "target_controls": len(target_controls),
            "overlap": len(overlap),
            "gap": len(gap),
            "gap_controls": sorted(gap),
        }


def print_control(control: Dict):
    """Pretty print a control."""
    print(f"\n{'=' * 80}")
    print(f"Control: {control['id']} - {control['name']}")
    print(f"{'=' * 80}")
    print(f"Domain: {control['domain']}")
    print(f"Weight: {control['weight']}/10")
    print(f"PPTDF: {control['pptdf']}")
    print(f"Validation: {control['validation_cadence']}")
    print("\nDescription:")
    print(f"  {control['description'][:200]}...")
    print("\nFramework Mappings:")

    for fw, mappings in control["framework_mappings"].items():
        if mappings:
            fw_display = fw.replace("_", " ").upper()
            print(f"  {fw_display}:")
            print(f"    {', '.join(mappings[:10])}")
            if len(mappings) > 10:
                print(f"    ... and {len(mappings) - 10} more")


def main():
    # Check if data files exist
    controls_file = Path("scf-controls.json")
    reverse_file = Path("framework-to-scf.json")

    if not controls_file.exists() or not reverse_file.exists():
        print("❌ Error: Data files not found!")
        print("\nRun the extraction script first:")
        print(
            "  python scf-extract-starter.py /tmp/scf-repo/secure-controls-framework-scf-2025-4.xlsx"
        )
        return

    print("🚀 SCF Query Tester - Demonstrating MCP Query Patterns")
    print("=" * 80)

    tester = SCFQueryTester(controls_file, reverse_file)

    # Test 1: Control Lookup
    print("\n📋 TEST 1: Control Lookup")
    print("-" * 80)
    print("Query: What does GOV-01 require?")

    control = tester.query_control("GOV-01")
    if control:
        print_control(control)

    # Test 2: Framework Coverage
    print("\n\n📋 TEST 2: Framework Coverage")
    print("-" * 80)
    print("Query: What controls are needed for DORA compliance?")

    dora_controls = tester.query_framework_controls("dora")
    print(f"\n✅ Found {len(dora_controls)} SCF controls that map to DORA")

    # Group by domain
    by_domain = {}
    for c in dora_controls:
        domain = c["domain"]
        if domain not in by_domain:
            by_domain[domain] = []
        by_domain[domain].append(c)

    print("\nControls by domain:")
    for domain in sorted(by_domain.keys()):
        controls = by_domain[domain]
        print(f"\n  {domain} ({len(controls)} controls):")
        for c in controls[:3]:  # Show first 3
            print(f"    - {c['id']}: {c['name']}")
        if len(controls) > 3:
            print(f"    ... and {len(controls) - 3} more")

    # Test 3: Cross-Framework Mapping
    print("\n\n📋 TEST 3: Cross-Framework Mapping")
    print("-" * 80)
    print("Query: What ISO 27001 controls cover DORA Article 16.1(a)?")

    iso_controls = tester.cross_reference_frameworks("dora", "16.1(a)", "iso_27001_2022")
    print("\n✅ DORA 16.1(a) maps to these ISO 27001 controls:")
    for iso_ctrl in iso_controls:
        print(f"  - {iso_ctrl}")

    # Show the SCF controls that bridge them
    scf_bridge = tester.reverse_index.get("dora", {}).get("16.1(a)", [])
    print(f"\n(Via SCF controls: {', '.join(scf_bridge)})")

    # Test 4: Gap Analysis
    print("\n\n📋 TEST 4: Gap Analysis")
    print("-" * 80)
    print("Query: I have ISO 27001. What additional controls does DORA require?")

    gap = tester.gap_analysis("iso_27001_2022", "dora")
    print(f"\nISO 27001 covers:        {gap['baseline_controls']} SCF controls")
    print(f"DORA requires:           {gap['target_controls']} SCF controls")
    print(f"Overlap:                 {gap['overlap']} SCF controls")
    print(f"Gap (DORA only):         {gap['gap']} SCF controls")

    print("\nSample gap controls (first 10):")
    for scf_id in gap["gap_controls"][:10]:
        control = tester.query_control(scf_id)
        if control:
            print(f"  - {scf_id}: {control['name']}")

    # Test 5: UK Cyber Essentials
    print("\n\n📋 TEST 5: UK Cyber Essentials")
    print("-" * 80)
    print("Query: What controls are needed for UK Cyber Essentials?")

    ce_controls = tester.query_framework_controls("uk_cyber_essentials")
    print(f"\n✅ Found {len(ce_controls)} SCF controls that map to UK Cyber Essentials")

    # Group by CE requirement number
    by_ce_req = {}
    for c in ce_controls:
        ce_mapping = c["framework_mappings"]["uk_cyber_essentials"]
        for ce_req in ce_mapping:
            if ce_req not in by_ce_req:
                by_ce_req[ce_req] = []
            by_ce_req[ce_req].append(c)

    print("\nControls by Cyber Essentials requirement:")
    for ce_req in sorted(by_ce_req.keys()):
        controls = by_ce_req[ce_req]
        print(f"\n  Requirement {ce_req} ({len(controls)} controls):")
        for c in controls[:3]:
            print(f"    - {c['id']}: {c['name']}")
        if len(controls) > 3:
            print(f"    ... and {len(controls) - 3} more")

    # Summary
    print("\n\n" + "=" * 80)
    print("✅ Query Tests Complete!")
    print("=" * 80)
    print("\nThese query patterns will be implemented as MCP tools:")
    print("  1. query_scf_control(scf_id)")
    print("  2. query_framework_controls(framework)")
    print("  3. cross_reference_frameworks(source_fw, source_ctrl, target_fw)")
    print("  4. gap_analysis(baseline_fw, target_fw)")
    print("  5. search_controls(text_query)")
    print("\nNext step: Build the MCP server to expose these as Claude tools!")


if __name__ == "__main__":
    main()
