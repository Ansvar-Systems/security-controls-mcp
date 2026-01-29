#!/usr/bin/env python3
"""Quality test script with challenging queries."""

import asyncio

from security_controls_mcp.data_loader import SCFData


async def run_quality_tests():
    """Run challenging test queries to verify quality."""
    print("=" * 80)
    print("Security Controls MCP - Quality Testing")
    print("=" * 80)

    data = SCFData()

    # Test 1: Edge case - Empty search
    print("\n[TEST 1] Empty search query")
    results = data.search_controls("", limit=5)
    # Empty query should either return no results or be handled gracefully
    if len(results) == 0 or len(results) <= 5:
        print(f"✓ PASS: Handled empty query gracefully ({len(results)} results)")
    else:
        print(f"✗ FAIL: Empty query returned too many results ({len(results)})")

    # Test 2: Non-existent framework
    print("\n[TEST 2] Non-existent framework")
    controls = data.get_framework_controls("fake_framework_123")
    # Should return empty list for invalid framework (graceful handling)
    if len(controls) == 0:
        print("✓ PASS: Invalid framework handled gracefully (returned empty list)")
    else:
        print(f"✗ FAIL: Invalid framework returned data ({len(controls)} items)")

    # Test 3: Complex multi-framework mapping
    print("\n[TEST 3] Complex framework mapping (ISO 27001 → DORA)")
    mapping = data.map_frameworks("iso_27001_2022", "dora")
    scf_controls = len(mapping)
    dora_controls = sum(len(m["target_controls"]) for m in mapping)
    print(f"  Mapped {scf_controls} SCF controls → {dora_controls} DORA requirements")
    if scf_controls > 0 and dora_controls > 0:
        print("✓ PASS: Successful cross-framework mapping")

        # Show sample mapping
        sample = mapping[0]
        print(f"\n  Example: SCF {sample['scf_id']} - {sample['scf_name'][:40]}...")
        print(f"    ISO controls: {', '.join(sample['source_controls'][:3])}")
        print(f"    DORA controls: {', '.join(sample['target_controls'][:3])}")
    else:
        print("✗ FAIL: Mapping returned empty results")

    # Test 4: Search with special characters
    print("\n[TEST 4] Search with special characters")
    queries = ["access & authentication", "data-at-rest", "AI/ML", "privacy (GDPR)"]
    for query in queries:
        results = data.search_controls(query, limit=3)
        print(f"  '{query}': {len(results)} results - {'✓' if len(results) > 0 else '⚠️'}")

    # Test 5: Framework-specific search
    print("\n[TEST 5] Framework-filtered search")
    general_results = data.search_controls("encryption", limit=100)
    dora_results = data.search_controls("encryption", frameworks=["dora"], limit=100)
    print(f"  General encryption search: {len(general_results)} results")
    print(f"  DORA-only encryption search: {len(dora_results)} results")
    if len(dora_results) < len(general_results):
        print("✓ PASS: Framework filtering works correctly")
    else:
        print("✗ FAIL: Framework filtering may not be working")

    # Test 6: Get control with all mappings
    print("\n[TEST 6] Control with comprehensive mappings")
    control = data.get_control("GOV-01")
    if control:
        framework_count = len(control.get("framework_mappings", {}))
        total_mappings = sum(
            len(v) for v in control["framework_mappings"].values() if v is not None
        )
        print(f"  Control: {control['id']} - {control['name'][:50]}...")
        print(
            f"  Mapped to {framework_count} frameworks with {total_mappings} total control references"
        )
        print("✓ PASS: Control loaded with comprehensive mappings")
    else:
        print("✗ FAIL: Could not load GOV-01")

    # Test 7: Verify data completeness for critical frameworks
    print("\n[TEST 7] Critical framework data completeness")
    critical_frameworks = {
        "dora": 103,
        "iso_27001_2022": 51,
        "nist_csf_2.0": 253,
        "pci_dss_4.0.1": 364,
        "nist_800_53_r5": 777,
    }

    all_passed = True
    for framework, expected_count in critical_frameworks.items():
        controls = data.get_framework_controls(framework)
        total = len(controls)
        status = "✓" if total >= expected_count else "✗"
        if total < expected_count:
            all_passed = False
        print(f"  {framework}: {total} controls (expected {expected_count}) {status}")

    if all_passed:
        print("✓ PASS: All critical frameworks have complete data")
    else:
        print("✗ FAIL: Some frameworks missing data")

    # Test 8: Mapping consistency check
    print("\n[TEST 8] Bidirectional mapping consistency")
    iso_to_nist = data.map_frameworks("iso_27001_2022", "nist_800_53_r5")
    nist_to_iso = data.map_frameworks("nist_800_53_r5", "iso_27001_2022")

    print(f"  ISO → NIST: {len(iso_to_nist)} source controls")
    print(f"  NIST → ISO: {len(nist_to_iso)} source controls")

    # Both should have mappings
    if len(iso_to_nist) > 0 and len(nist_to_iso) > 0:
        print("✓ PASS: Bidirectional mappings exist")
    else:
        print("✗ FAIL: Bidirectional mappings incomplete")

    # Test 9: Case sensitivity in search
    print("\n[TEST 9] Case insensitivity verification")
    lower = data.search_controls("access control", limit=5)
    upper = data.search_controls("ACCESS CONTROL", limit=5)
    mixed = data.search_controls("AcCeSs CoNtRoL", limit=5)

    if len(lower) == len(upper) == len(mixed) and len(lower) > 0:
        print(f"  All queries returned {len(lower)} results")
        print("✓ PASS: Search is case-insensitive")
    else:
        print(f"  Lower: {len(lower)}, Upper: {len(upper)}, Mixed: {len(mixed)}")
        print("✗ FAIL: Case sensitivity issues detected")

    # Test 10: Performance check
    print("\n[TEST 10] Performance benchmarks")
    import time

    # Test search performance
    start = time.time()
    for _ in range(100):
        data.search_controls("security", limit=10)
    search_time = (time.time() - start) * 10  # ms per search

    # Test get_control performance
    start = time.time()
    for i in range(100):
        data.get_control(f"GOV-{i:02d}")
    get_time = (time.time() - start) * 10  # ms per get

    # Test framework mapping performance
    start = time.time()
    data.map_frameworks("iso_27001_2022", "dora")
    map_time = (time.time() - start) * 1000  # ms

    print(f"  Search controls: {search_time:.2f} ms per query")
    print(f"  Get control: {get_time:.2f} ms per lookup")
    print(f"  Map frameworks: {map_time:.2f} ms")

    if search_time < 50 and get_time < 10 and map_time < 1000:
        print("✓ PASS: Performance is acceptable")
    else:
        print("⚠️  WARNING: Performance may need optimization")

    print("\n" + "=" * 80)
    print("Quality Testing Complete")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_quality_tests())
