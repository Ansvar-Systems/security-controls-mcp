# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.2] - 2026-01-31

### Changed
- Updated package metadata to use SPDX license format (removed deprecated table format)
- Upgraded PyPI classifier from "Development Status :: 3 - Alpha" to "4 - Beta"
- Removed deprecated license classifier per Poetry best practices

### Technical
- Production readiness verified: 104/104 tests passing, comprehensive security audit completed
- No functional changes to MCP tools or data

## [0.3.0] - 2026-01-29

### Added
- **12 new framework mappings** from SCF 2025.4 - expanded global coverage
  - **APAC:** Australian Essential Eight (37 controls), Australian ISM June 2024 (336 controls), Singapore MAS TRM 2021 (214 controls)
  - **Financial:** SWIFT Customer Security Framework 2023 (127 controls)
  - **Privacy:** NIST Privacy Framework 1.0 (187 controls)
  - **European National:** Netherlands (27 controls), Norway (23 controls), Sweden (25 controls), Germany general (18 controls), Germany BAIT (91 controls), Germany C5:2020 (239 controls)
  - **Cloud:** CSA Cloud Controls Matrix v4 (334 controls)
- **Framework Roadmap** section in README documenting:
  - All 28 available frameworks with control counts
  - Frameworks not yet available (BIO, KATAKRI, NSM, MSB, CFCS, CCB, ANSSI)
  - Clear guidance on maintaining data quality via SCF-only mappings

### Changed
- Total framework coverage: **16 → 28 frameworks** (+75% expansion)
- Updated all documentation to reflect new framework count
- Enhanced framework categories in README (added APAC, European National, Financial, Cloud)
- Updated tests to verify 28 frameworks
- Updated `scf-extract-starter.py` with 12 new framework column mappings

### Technical
- Re-extracted data from SCF 2025.4 Excel file with expanded framework coverage
- Updated `src/security_controls_mcp/data_loader.py` with new framework display names
- All existing tools automatically support new frameworks (no API changes)

## [0.2.0] - 2025-01-29

### Added
- **Paid Standards Support** - Import and query purchased security standards (ISO 27001, NIST SP 800-53, etc.)
- Three new MCP tools:
  - `list_available_standards` - Show all available standards (SCF + imported)
  - `query_standard` - Search within purchased standards
  - `get_clause` - Get full text of specific clauses
- CLI tool (`scf-mcp`) for importing standards from PDF:
  - `scf-mcp import-standard` - Extract and import PDF standards
  - `scf-mcp list-standards` - List all imported standards
- Enhanced existing tools with official text from purchased standards:
  - `get_control` now shows official text alongside SCF descriptions
  - `map_frameworks` displays official text from both source and target frameworks
- User-local storage (`~/.security-controls-mcp/`) - keeps paid content private
- PDF extraction pipeline with intelligent structure detection
- Comprehensive documentation: PAID_STANDARDS_GUIDE.md (341 lines)
- 12 new tests for paid standards functionality (63 total tests)
- License compliance features: startup warnings, attribution, git safety checks

### Changed
- Updated README.md with paid standards overview and quick start
- Enhanced legal notices to show loaded paid standards
- Tool count increased from 5 to 8

### Technical Details
- Provider abstraction for extensible standard support
- Config system for managing imported standards
- Registry pattern for unified standard access
- Optional dependencies: `pip install -e '.[import-tools]'` for PDF extraction

### Fixed
- Git safety check when standards directory is outside repository

## [0.1.0] - 2025-01-29

### Added
- Initial release of Security Controls MCP Server
- Support for 16 security frameworks with 1,451 controls mapped from SCF 2025.4
- Five MCP tools:
  - `get_control` - Retrieve detailed control information
  - `search_controls` - Search controls by keyword
  - `list_frameworks` - List all available frameworks
  - `get_framework_controls` - Get controls for a specific framework
  - `map_frameworks` - Map controls between any two frameworks
- Comprehensive documentation (README, INSTALL, TESTING)
- Test suite with MCP protocol integration tests
- Data files: scf-controls.json (1,451 controls), framework-to-scf.json (reverse mappings)

### Frameworks Supported
- NIST SP 800-53 R5 (777 controls)
- SOC 2 TSC (412 controls)
- PCI DSS v4.0.1 (364 controls)
- FedRAMP R5 Moderate (343 controls)
- ISO/IEC 27002:2022 (316 controls)
- NIST CSF 2.0 (253 controls)
- CIS CSC v8.1 (234 controls)
- CMMC 2.0 Level 2 (198 controls)
- HIPAA Security Rule (136 controls)
- DORA (103 controls)
- NIS2 (68 controls)
- NCSC CAF 4.0 (67 controls)
- CMMC 2.0 Level 1 (52 controls)
- ISO/IEC 27001:2022 (51 controls)
- GDPR (42 controls)
- UK Cyber Essentials (26 controls)

[0.2.0]: https://github.com/Ansvar-Systems/security-controls-mcp/releases/tag/v0.2.0
[0.1.0]: https://github.com/Ansvar-Systems/security-controls-mcp/releases/tag/v0.1.0
