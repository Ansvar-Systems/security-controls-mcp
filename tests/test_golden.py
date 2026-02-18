"""Golden tests - regression tests for data accuracy across releases.

These tests validate that tool outputs match expected patterns defined in
fixtures/golden-tests.json. They serve as a contract between releases to
ensure data accuracy is maintained.
"""

import json
from pathlib import Path

import pytest

from security_controls_mcp.server import call_tool


FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
GOLDEN_TESTS_FILE = FIXTURES_DIR / "golden-tests.json"


def load_golden_tests():
    """Load golden test definitions from fixtures."""
    with open(GOLDEN_TESTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["tests"]


GOLDEN_TESTS = load_golden_tests()


@pytest.mark.parametrize(
    "test_case",
    GOLDEN_TESTS,
    ids=[t["id"] for t in GOLDEN_TESTS],
)
@pytest.mark.asyncio
async def test_golden(test_case):
    """Run a golden test case against the MCP server."""
    tool_name = test_case["tool"]
    arguments = test_case["arguments"]
    expected = test_case["expected"]

    # Call the tool
    result = await call_tool(tool_name, arguments)

    # Extract text from result
    assert len(result) > 0, f"Golden test {test_case['id']}: empty result"
    text = result[0].text.lower()

    # Check expected contains
    if "contains" in expected:
        for phrase in expected["contains"]:
            assert phrase.lower() in text, (
                f"Golden test {test_case['id']}: "
                f"expected '{phrase}' in output but not found.\n"
                f"Output preview: {text[:500]}"
            )

    # Check expected not_contains
    if "not_contains" in expected:
        for phrase in expected["not_contains"]:
            assert phrase.lower() not in text, (
                f"Golden test {test_case['id']}: "
                f"expected '{phrase}' NOT in output but it was found.\n"
                f"Output preview: {text[:500]}"
            )
