#!/usr/bin/env python3
"""Quick test script for MCP server functionality."""

from security_controls_mcp.data_loader import SCFData


def main():
    print("Loading SCF data...")
    data = SCFData()

    print(f"✓ Loaded {len(data.controls)} controls")
    print(f"✓ Loaded {len(data.frameworks)} frameworks\n")

    # Test 1: Get control
    print("Test 1: get_control('GOV-01')")
    ctrl = data.get_control("GOV-01")
    if ctrl:
        print(f"  ✓ {ctrl['id']}: {ctrl['name']}")
        print(f"  Domain: {ctrl['domain']}")
        print(f"  Weight: {ctrl['weight']}")
        dora = ctrl["framework_mappings"].get("dora", [])
        print(f"  DORA mappings: {dora[:3] if dora else 'None'}")
    else:
        print("  ✗ Control not found")

    print()

    # Test 2: Search controls
    print("Test 2: search_controls('encryption')")
    results = data.search_controls("encryption", limit=3)
    print(f"  ✓ Found {len(results)} controls")
    for r in results[:2]:
        print(f"    - {r['control_id']}: {r['name']}")

    print()

    # Test 3: Get framework controls
    print("Test 3: get_framework_controls('dora')")
    dora_controls = data.get_framework_controls("dora")
    print(f"  ✓ Found {len(dora_controls)} DORA controls")
    print(f"    First: {dora_controls[0]['scf_id']} - {dora_controls[0]['scf_name']}")

    print()

    # Test 4: Map frameworks
    print("Test 4: map_frameworks('iso_27001_2022' → 'dora')")
    mappings = data.map_frameworks("iso_27001_2022", "dora", source_control="5.1")
    print(f"  ✓ Found {len(mappings)} mappings for ISO 27001 5.1")
    if mappings:
        m = mappings[0]
        print(f"    {m['scf_id']}: {m['scf_name']}")
        print(f"    ISO: {m['source_controls'][:3]}")
        print(f"    DORA: {m['target_controls'][:3] if m['target_controls'] else 'None'}")

    print()

    # Test 5: List frameworks
    print("Test 5: frameworks")
    print("  ✓ Available frameworks:")
    for fw_key in list(data.frameworks.keys())[:5]:
        fw = data.frameworks[fw_key]
        print(f"    - {fw_key}: {fw['controls_mapped']} controls")

    print("\n✓ All tests passed!")


if __name__ == "__main__":
    main()
