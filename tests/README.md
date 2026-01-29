# Test Suite

Comprehensive test suite for security-controls-mcp.

## Test Structure

### Unit Tests (`test_data_loader.py`)
Tests for the `SCFData` class and all data loading/querying methods.

**Coverage:**
- Data loading and integrity
- `get_control()` method
- `search_controls()` method with filters
- `get_framework_controls()` method
- `map_frameworks()` method
- Critical framework counts verification

**Run:** `pytest tests/test_data_loader.py -v`

### Smoke Tests (`test_smoke.py`)
Quick validation that the package is properly installed and data files are present.

**Coverage:**
- Data files exist and are valid JSON
- All expected frameworks present
- Module imports work
- Package metadata correct
- Documentation files exist

**Run:** `pytest tests/test_smoke.py -v`

### Integration Tests (`test_integration.py`)
End-to-end tests for tool calls and MCP protocol communication.

**Coverage:**
- Direct tool calls (all 5 tools)
- Full MCP protocol lifecycle (marked as `slow`)
- Error handling for invalid inputs

**Run:** `pytest tests/test_integration.py -v`

**Run without slow tests:** `pytest tests/test_integration.py -v -m "not slow"`

## Running Tests

### All Tests
```bash
pytest tests/ -v
```

### Fast Tests Only (skip MCP protocol tests)
```bash
pytest tests/ -v -m "not slow"
```

### Specific Test File
```bash
pytest tests/test_data_loader.py -v
```

### Specific Test Class
```bash
pytest tests/test_data_loader.py::TestSearchControls -v
```

### Specific Test
```bash
pytest tests/test_data_loader.py::TestSearchControls::test_search_returns_results -v
```

### With Coverage
```bash
pytest tests/ --cov=security_controls_mcp --cov-report=html
```

## Test Statistics

- **Total Tests:** 51
- **Unit Tests:** 27
- **Smoke Tests:** 14
- **Integration Tests:** 10
- **Execution Time:** ~1 second (all tests)

## Test Markers

- `@pytest.mark.slow` - Tests that take >1 second (MCP protocol tests)
- `@pytest.mark.asyncio` - Async tests (integration tests)

## Continuous Integration

Tests run automatically on:
- Push to `main` branch
- Pull requests to `main` branch

See `.github/workflows/tests.yml` for CI configuration.

## Writing New Tests

### Unit Test Example
```python
def test_my_feature(scf_data):
    """Test description."""
    result = scf_data.my_method("param")
    assert result is not None
    assert result["expected_field"] == "expected_value"
```

### Async Integration Test Example
```python
@pytest.mark.asyncio
async def test_my_tool(self):
    """Test description."""
    result = await call_tool("tool_name", {"arg": "value"})
    assert len(result) == 1
    assert "expected" in result[0].text
```

## Test Data

All tests use the production data files:
- `src/security_controls_mcp/data/scf-controls.json`
- `src/security_controls_mcp/data/framework-to-scf.json`

No mocking or test fixtures - tests validate real data.
