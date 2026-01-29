#!/usr/bin/env python3
"""
Integration test for security-controls-mcp server.
Simulates MCP tool calls like Claude would make.
"""

import asyncio
import sys

# Import the tool handler function directly
from security_controls_mcp.server import call_tool as tool_handler


async def test_tool(tool_name: str, arguments: dict) -> None:
    """Test a single tool call."""
    print(f"\n{'='*80}")
    print(f"Testing: {tool_name}")
    print(f"Arguments: {arguments}")
    print('='*80)

    try:
        result = await tool_handler(tool_name, arguments)
        for content in result:
            print(content.text)
        print("\n✅ Success")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all integration tests."""
    print("="*80)
    print("Security Controls MCP - Integration Tests")
    print("="*80)

    # Test 1: get_control
    await test_tool(
        "get_control",
        {"control_id": "GOV-01", "include_mappings": True}
    )

    # Test 2: get_control (control not found)
    await test_tool(
        "get_control",
        {"control_id": "FAKE-999", "include_mappings": True}
    )

    # Test 3: search_controls
    await test_tool(
        "search_controls",
        {"query": "encryption key management", "limit": 5}
    )

    # Test 4: search_controls with framework filter
    await test_tool(
        "search_controls",
        {"query": "access control", "frameworks": ["dora"], "limit": 3}
    )

    # Test 5: list_frameworks
    await test_tool(
        "list_frameworks",
        {"detailed": False}
    )

    # Test 6: get_framework_controls
    await test_tool(
        "get_framework_controls",
        {"framework": "dora", "include_descriptions": False}
    )

    # Test 7: get_framework_controls (invalid framework)
    await test_tool(
        "get_framework_controls",
        {"framework": "fake_framework", "include_descriptions": False}
    )

    # Test 8: map_frameworks (ISO 27001 → DORA)
    await test_tool(
        "map_frameworks",
        {
            "source_framework": "iso_27001_2022",
            "target_framework": "dora",
            "source_control": "5.1"
        }
    )

    # Test 9: map_frameworks (all mappings, no filter)
    await test_tool(
        "map_frameworks",
        {
            "source_framework": "iso_27001_2022",
            "target_framework": "nist_csf_2_0"
        }
    )

    # Test 10: map_frameworks (invalid source framework)
    await test_tool(
        "map_frameworks",
        {
            "source_framework": "fake_framework",
            "target_framework": "dora"
        }
    )

    print("\n" + "="*80)
    print("Integration Testing Complete")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
