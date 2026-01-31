# Security Controls MCP - Development Guide

**Part of the Ansvar MCP Suite** → See [ANSVAR_MCP_ARCHITECTURE.md](./docs/ANSVAR_MCP_ARCHITECTURE.md) for complete suite documentation

## Project Overview

MCP server providing access to 1,451 security controls across 28 frameworks. Uses SCF (Secure Controls Framework) as a rosetta stone for bidirectional framework mapping.

## Key Features

- **28 Frameworks**: ISO 27001, NIST CSF, DORA, PCI DSS, SOC 2, CMMC, FedRAMP, and 21 more
- **1,451 Controls**: Complete control catalog with descriptions
- **Bidirectional Mapping**: Map any framework to any other framework
- **Gap Analysis**: Compare control coverage between frameworks
- **Official Text Import**: Support for purchased ISO/NIST standards

## Tech Stack

- **Language**: Python 3.11+
- **Database**: SQLite with FTS5 full-text search
- **Package Manager**: Poetry
- **Distribution**: PyPI (`pipx install security-controls-mcp`)
- **Data Source**: SCF Framework (Creative Commons BY 4.0)

## Quick Start

```bash
# Install
pipx install security-controls-mcp

# Verify
security-controls-mcp --version

# Claude Desktop config
{
  "mcpServers": {
    "security-controls": {
      "command": "security-controls-mcp"
    }
  }
}
```

## Project Structure

```
security-controls-mcp/
├── src/security_controls_mcp/
│   ├── server.py              # MCP server entry point
│   ├── data/
│   │   ├── scf-controls.json      # 1,451 controls with mappings
│   │   └── framework-to-scf.json  # Framework → SCF mappings
│   ├── data_loader.py         # SCF data loading logic
│   └── tools/                 # MCP tool implementations
│       ├── version_info.py
│       ├── list_frameworks.py
│       ├── get_control.py
│       ├── search_controls.py
│       ├── get_framework_controls.py
│       └── map_frameworks.py
├── tests/                     # Comprehensive test suite
├── docs/
│   ├── ANSVAR_MCP_ARCHITECTURE.md  # **Central architecture doc**
│   └── coverage.md            # Framework coverage details
└── pyproject.toml             # Poetry configuration
```

## Available Tools

### 1. `version_info`
Get MCP server version and statistics

### 2. `list_frameworks`
List all 28 supported frameworks with control counts

### 3. `get_control`
Retrieve a specific control by ID from any framework

### 4. `search_controls`
Full-text search across all controls

### 5. `get_framework_controls`
Get all controls for a specific framework

### 6. `map_frameworks`
Map controls between any two frameworks (bidirectional)

## Framework IDs

```python
# Use these IDs with the tools
FRAMEWORKS = [
    "iso_27001_2022", "iso_27002_2022", "nist_csf_2_0",
    "nist_800_53_r5", "dora", "pci_dss_4_0", "soc_2",
    "cmmc_2_0", "fedramp_high", "cis_controls_v8",
    # ... 18 more (see docs/coverage.md)
]
```

## Development

```bash
# Clone and install
git clone https://github.com/Ansvar-Systems/security-controls-mcp
cd security-controls-mcp
poetry install

# Run tests
poetry run pytest

# Run locally
poetry run python -m src.security_controls_mcp.server

# Build for PyPI
poetry build
```

## Data Updates

### SCF Framework Updates

When SCF releases new versions:

```bash
# 1. Download new scf-controls.json from SCF repo
# 2. Update src/security_controls_mcp/data/scf-controls.json
# 3. Run tests to validate
poetry run pytest

# 4. Update version
poetry version patch

# 5. Build and publish
poetry build
poetry publish
```

### Adding New Frameworks

1. Check if SCF includes the framework
2. If yes, it's automatically available (SCF is the mapper)
3. If no, request SCF team add it OR create manual mapping in `framework-to-scf.json`

## Testing

```bash
# Run all tests
poetry run pytest

# With coverage
poetry run pytest --cov=src --cov-report=html

# Specific test
poetry run pytest tests/test_map_frameworks.py -v
```

## Current Statistics

- **Frameworks**: 28 (expanded from 16 in v0.2.1)
- **Controls**: 1,451 unique controls
- **Mappings**: 15,000+ bidirectional relationships
- **Database Size**: ~8MB (SQLite)
- **Tests**: 100% passing

## Version History

- **v0.2.1** (2026-01-29): Framework expansion (16→28 frameworks)
- **v0.2.0**: Initial public release with 16 frameworks
- **v0.1.0**: Internal beta

## Integration with Other Ansvar MCPs

This server works seamlessly with:
- **EU Regulations MCP**: Map DORA/GDPR requirements to ISO 27001
- **US Regulations MCP**: Map HIPAA/SOX to NIST controls
- **OT Security MCP**: Bridge IT security controls to OT standards
- **Sanctions MCP**: Security controls for vendor assessments

See [ANSVAR_MCP_ARCHITECTURE.md](./docs/ANSVAR_MCP_ARCHITECTURE.md) for complete workflow examples.

## Coding Guidelines

- Python 3.11+ with type hints
- Pydantic for data validation
- SQLite for data storage
- Black for formatting
- Ruff for linting
- pytest for testing

## Support

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and use cases
- **Commercial**: hello@ansvar.eu

## License

Apache License 2.0 - See [LICENSE](./LICENSE)

---

**For complete Ansvar MCP suite documentation, see:**
📖 [docs/ANSVAR_MCP_ARCHITECTURE.md](./docs/ANSVAR_MCP_ARCHITECTURE.md)
