# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-02-16

### Added
- **100% framework categorization** — all 261 frameworks now in 26 categories for discoverability
- **`list_frameworks` category support** — optional `category` parameter filters by category; without it, frameworks are grouped by category instead of a flat dump
- **UK Cybersecurity category** — UK Cyber Essentials, NCSC CAF 4.0, UK DPA, DEFSTAN 05-138, CAP 1850, FCA CRM
- **17 new categories** — governance, fedramp, govramp, cmmc, zero_trust, us_state_laws, europe_national, middle_east_africa, asia_pacific, americas, media_entertainment, threat_intel_appsec, and more
- **Weekly update monitoring** — GitHub Actions workflow checks SCF releases + 14 framework source pages every Monday
- **Guardrail tests** — `TestCategoryCompleteness` ensures no framework goes uncategorized in future SCF updates
- **UK framework tests** — 24 tests covering Cyber Essentials (5 core areas), NCSC CAF (4 objectives A-D), cross-framework mappings

### Changed
- `list_frameworks` tool now groups output by category (was flat list of 261 items)
- Categories expanded from 9 (49 frameworks) to 26 (261 frameworks, 100% coverage)
- Test count increased from 242 to 277

## [1.0.0] - 2026-02-12

### 🎉 Production Release!

This is the first production-ready release with comprehensive standards import capabilities.

### Added
- **Standards Import Feature** - Web UI and API for uploading purchased standards (ISO, NIST, etc.)
- **12 Specialized Extractors** with automatic control extraction:
  - **IT/Cloud:** ISO 27001 (2022 & 2013), NIST 800-53 R5, SOC 2, PCI DSS (4.0/3.2.1), CIS Controls v8
  - **OT/ICS:** IEC 62443 (industrial cybersecurity)
  - **Automotive:** ISO/SAE 21434:2021
  - **Privacy:** ISO 27701, GDPR (EU 2016/679), CCPA/CPRA
  - **AI Governance:** ISO 42001:2023, NIST AI RMF 1.0
- **Web Upload Interface** at `/standards/upload` with:
  - Drag-and-drop PDF upload
  - Real-time extraction with confidence scoring
  - Control categorization and validation
  - Missing control detection
- **Auto-Discovery Registry** - New extractors self-register via decorator pattern
- **Version Detection** - Automatic identification of standard versions with evidence
- **Hierarchical Extraction** - Parent-child relationships preserved
- **Multi-Version Support** - ISO 27001 (2022: 93 controls, 2013: 114 controls), PCI DSS (4.0/3.2.1)

### Technical
- Added `extractors/` framework with base classes and registry pattern
- 115 new tests for extractors (242 total, 100% pass rate)
- Security hardening: File size limits, magic byte validation, CSP headers
- Evidence-based confidence scoring for extraction quality
- TDD approach throughout implementation

### Changed
- HTTP server now includes standards import web UI
- Test count increased from 127 to 242
- Enhanced project structure with extractors module

## [0.4.0] - 2026-02-05

### Added
- **Major framework expansion: 28 → 261 frameworks** (+832% increase)
- **AI Governance frameworks:** ISO 42001:2023, NIST AI RMF 1.0, NIST AI 600-1, EU AI Act, EU Cyber Resilience Act
- **Cloud security:** CSA STAR, StateRAMP, GovRAMP, TX-RAMP
- **Industrial/OT:** IEC 62443, NERC CIP, NIST 800-82 R3 overlays
- **Automotive:** ISO/SAE 21434, TISAX, UN R155/R156
- **Privacy:** 20+ national privacy frameworks worldwide
- **Regional:** 50+ country-specific frameworks (APAC, EU, Middle East, Americas)
- New `version_info` tool for agents to discover server capabilities
- HTTP server (`http_server.py`) with REST API and MCP-over-SSE transport
- Framework categories for filtering (ai_governance, cloud_security, privacy, etc.)

### Changed
- Tool count increased from 8 to 9 (added `version_info`)
- Updated framework metadata with 261 display names
- HTTP server version corrected to 0.4.0
- Added `notifications/initialized` and `ping` handlers to HTTP MCP endpoint

### Technical
- All 127 tests passing
- HTTP server supports both MCP JSON-RPC and REST API endpoints
- Proper `datetime.now(timezone.utc)` usage (replaces deprecated `utcnow()`)

## [0.3.5] - 2026-02-01

### Fixed
- **Critical:** Fixed entry point so `scf-mcp` runs the MCP server (was incorrectly pointing to CLI tools)
- macOS users: Added documentation about using full path since GUI apps don't inherit shell PATH

### Changed
- Split commands: `scf-mcp` runs MCP server, `scf-mcp-import` runs import CLI
- Updated all docs to reflect new command structure
- Fixed install instructions to use `pip install security-controls-mcp[import-tools]` instead of editable install

## [0.3.3] - 2026-01-31

### Changed
- Repository cleanup: Removed LLM-generated documentation bloat
- Simplified documentation from 18 to 6 essential files
- Cleaned up README (524→256 lines), removed excessive emojis and verbosity
- Simplified PAID_STANDARDS_GUIDE (342→251 lines)
- Updated .gitignore to exclude Claude artifacts (.claude/, .serena/, test_venv/)

### Removed
- 11 redundant documentation files (CLAUDE_CODE_SETUP.md, DEPLOYMENT_CHECKLIST.md, CI-CD-PIPELINE.md, QUICK_START.md, INSTALL.md, TESTING.md, SECURITY-TOOLS.md, LEGAL_COMPLIANCE.md, RELEASE_NOTES_v0.3.1.md)
- 7 development files from root (duplicate data files, test scripts)

### Technical
- No functional changes to MCP server or controls data
- All 103 tests passing
- Production readiness: 7/7 checks passed

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
