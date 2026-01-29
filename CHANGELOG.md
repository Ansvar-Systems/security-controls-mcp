# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.1.0]: https://github.com/Ansvar-Systems/security-controls-mcp/releases/tag/v0.1.0
