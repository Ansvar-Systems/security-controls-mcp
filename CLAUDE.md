# Security Controls MCP - Development Guide

**Part of the Ansvar MCP Suite** → See [ANSVAR_MCP_ARCHITECTURE.md](./docs/ANSVAR_MCP_ARCHITECTURE.md) for complete suite documentation

## Project Overview

MCP server providing access to 1,451 security controls across **261 frameworks**. Uses SCF (Secure Controls Framework) as a rosetta stone for bidirectional framework mapping.

## Key Features

- **261 Frameworks**: ISO 27001, NIST CSF, DORA, PCI DSS, SOC 2, CMMC, FedRAMP, and 254 more
- **AI Governance**: ISO 42001, NIST AI RMF, EU AI Act, Cyber Resilience Act
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
scf-mcp --version

# Claude Desktop config (use full path for GUI apps)
{
  "mcpServers": {
    "security-controls": {
      "command": "/full/path/to/scf-mcp"
    }
  }
}
# Find your path with: which scf-mcp
```

## Project Structure

```
security-controls-mcp/
├── src/security_controls_mcp/
│   ├── __main__.py            # Entry point (stdio transport)
│   ├── server.py              # MCP server with 9 tools (stdio)
│   ├── http_server.py         # HTTP/SSE server with web UI for standards import
│   ├── data_loader.py         # SCF data loading & search logic
│   ├── config.py              # User config & paid standards paths
│   ├── registry.py            # Standard provider registry
│   ├── providers.py           # Paid standard providers
│   ├── legal_notice.py        # License compliance notices
│   ├── cli.py                 # PDF import CLI (optional)
│   ├── extractors/            # **NEW: Standards extraction framework**
│   │   ├── base.py            # Base classes & data structures
│   │   ├── registry.py        # Extractor registry & auto-discovery
│   │   └── specialized/       # 12 specialized extractors
│   │       ├── iso_27001.py   # ISO 27001 (2022 & 2013)
│   │       ├── nist_800_53.py # NIST 800-53 R5
│   │       ├── iso_21434.py   # Automotive cybersecurity
│   │       ├── soc2.py        # SOC 2 Trust Services
│   │       ├── pci_dss.py     # PCI DSS 4.0/3.2.1
│   │       ├── iec_62443.py   # Industrial/OT security
│   │       ├── cis_controls.py# CIS Controls v8
│   │       ├── iso_27701.py   # Privacy management
│   │       ├── iso_42001.py   # AI management
│   │       ├── nist_ai_rmf.py # NIST AI RMF
│   │       ├── gdpr.py        # EU GDPR
│   │       └── ccpa.py        # California CCPA/CPRA
│   └── data/
│       ├── scf-controls.json      # 1,451 controls with mappings
│       └── framework-to-scf.json  # Framework → SCF reverse index
├── tests/                     # 242 tests (all passing)
├── docs/
│   ├── ANSVAR_MCP_ARCHITECTURE.md  # **Central architecture doc**
│   ├── coverage.md            # Framework coverage details
│   └── plans/                 # Implementation plans
└── pyproject.toml             # Package configuration
```

## Standards Import Feature (NEW in v1.0.0)

### Web UI for Standards Upload
Business users can upload purchased standards (ISO, NIST, etc.) via a web interface:

```bash
# Start HTTP server with web UI
python -m security_controls_mcp.http_server --port 8000

# Open browser to http://localhost:8000/standards/upload
# Upload PDF → See extracted controls with confidence scoring
```

### 12 Specialized Extractors

Automatically extracts controls from diverse standard types:

**IT/Cloud Security:**
- ISO 27001 (2022: 93 controls, 2013: 114 controls)
- NIST 800-53 (R5: 320 controls across 20 families)
- SOC 2 (Trust Services Criteria with 5 categories)
- PCI DSS (v4.0/v3.2.1 with 12 requirements)
- CIS Controls (v8: 18 controls, 153 safeguards)

**OT/ICS:** IEC 62443 (Industrial cybersecurity)

**Automotive:** ISO 21434 (Automotive cybersecurity)

**Privacy:**
- ISO 27701 (Privacy management system)
- GDPR (EU Regulation 2016/679, 99 articles)
- CCPA/CPRA (California privacy law)

**AI Governance:**
- ISO 42001 (AI management system)
- NIST AI RMF (AI Risk Management Framework)

### Extractor Features
- **Version Detection**: Automatic version identification with confidence scoring
- **Hierarchical Structure**: Parent-child relationships preserved
- **Category Assignment**: Automatic categorization by standard structure
- **Missing Control Detection**: Validates extraction completeness
- **Evidence-Based Confidence**: Clear indicators of extraction quality

### Adding New Extractors
Create a new file in `src/security_controls_mcp/extractors/specialized/`:

```python
from ..base import BaseExtractor, Control, ExtractionResult, VersionDetection
from ..registry import register_extractor

@register_extractor("my_standard")
class MyStandardExtractor(BaseExtractor):
    def extract(self, pdf_bytes: bytes) -> ExtractionResult:
        # Implement extraction logic
        pass
```

The extractor auto-registers and becomes available immediately.

## Available Tools

### 1. `version_info`
Get MCP server version, statistics, and database info

### 2. `get_control`
Retrieve a specific control by ID (e.g., GOV-01)

### 3. `search_controls`
Full-text search across all controls by keyword

### 4. `list_frameworks`
List all 261 supported frameworks with control counts

### 5. `get_framework_controls`
Get all controls for a specific framework

### 6. `map_frameworks`
Map controls between any two frameworks (bidirectional)

### 7. `list_available_standards`
List all available standards (SCF built-in + purchased)

### 8. `query_standard`
Search within a purchased standard's official text

### 9. `get_clause`
Get full text of a specific clause from a purchased standard

## Framework IDs

```python
# Use these IDs with the tools
FRAMEWORKS = [
    "iso_27001_2022", "iso_27002_2022", "nist_csf_2.0",
    "nist_800_53_r5", "dora", "pci_dss_4.0.1", "soc_2_tsc",
    "cmmc_2.0_level_2", "fedramp_r5_high", "cis_csc_8.1",
    # ... 251 more (use list_frameworks tool to see all)
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

- **Frameworks**: 261 (expanded from 28 in v0.4.0)
- **Controls**: 1,451 unique controls
- **Mappings**: 50,000+ bidirectional relationships
- **Database Size**: ~7MB (JSON)
- **Tools**: 9 (6 core + 3 paid standards)
- **Tests**: 242 passing (100% pass rate)
- **Specialized Extractors**: 12 (NEW in v1.0.0)
  - IT/Cloud: ISO 27001, NIST 800-53, SOC 2, PCI DSS, CIS Controls
  - OT/ICS: IEC 62443
  - Automotive: ISO 21434
  - Privacy: ISO 27701, GDPR, CCPA
  - AI: ISO 42001, NIST AI RMF

## Version History

- **v1.0.0** (2026-02-12): 🎉 **Production Release!** Standards import feature with 12 specialized extractors, web UI, auto-discovery registry, 242 tests
- **v0.4.0** (2026-02-05): Major framework expansion (28→261), AI governance support
- **v0.3.5** (2026-02-01): Entry point fix
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
