# Security Controls MCP Server

<!-- mcp-name: io.github.Ansvar-Systems/security-controls -->

[![MCP](https://img.shields.io/badge/MCP-0.9.0+-blue.svg)](https://modelcontextprotocol.io)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![SCF](https://img.shields.io/badge/SCF-2025.4-orange.svg)](https://securecontrolsframework.com/)

## Overview

Universal translator for security frameworks. Makes 1,451 security controls across 28 frameworks searchable and AI-accessible through Claude, Cursor, or any MCP-compatible client.

Built on the [Secure Controls Framework (SCF)](https://securecontrolsframework.com/) by ComplianceForge.

**Key capabilities:**
- 1,451 security controls across governance, risk, compliance, and technical domains
- 28 major frameworks including ISO 27001, NIST CSF, DORA, PCI DSS, CMMC, and more
- Bidirectional mapping between frameworks via SCF rosetta stone
- Optional integration with purchased standards (ISO, NIST 800-53) for official text
- Full-text search across all control descriptions
- Natural language queries instead of framework-specific IDs

## Why This Exists

Different frameworks describe the same security measures in different ways. ISO 27001 has one control ID, NIST CSF has another, PCI DSS has yet another — but they're all talking about the same thing.

This MCP server provides instant bidirectional mapping between any two frameworks via the SCF rosetta stone. Ask Claude "What DORA controls does ISO 27001 A.5.15 map to?" and get an immediate answer backed by ComplianceForge's framework database.

## Installation

```bash
# Using pipx (recommended)
pipx install security-controls-mcp

# Using pip
pip install security-controls-mcp

# From source
git clone https://github.com/Ansvar-Systems/security-controls-mcp.git
cd security-controls-mcp
pip install -e .
```

**Requirements:** Python 3.10+

### Claude Desktop Configuration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "security-controls": {
      "command": "scf-mcp"
    }
  }
}
```

**macOS users:** GUI apps don't inherit your shell's PATH. Use the full path instead:
```json
{
  "mcpServers": {
    "security-controls": {
      "command": "/Users/YOUR_USERNAME/.local/bin/scf-mcp"
    }
  }
}
```
Find your path with: `which scf-mcp`

**Config location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

### Cursor / VS Code

Same configuration under `"mcp.servers"` in your settings.

## Example Queries

- "What does GOV-01 require?"
- "Search for controls about encryption key management"
- "What ISO 27001 controls map to DORA?"
- "List all controls needed for PCI DSS compliance"
- "Which DORA requirements does ISO 27001 A.5.15 satisfy?"
- "Show me all NIST CSF 2.0 controls related to incident response"

## Available Frameworks (28)

- **US Government:** NIST 800-53 (777), NIST CSF 2.0 (253), FedRAMP (343), CMMC 2.0 (198/52)
- **International Standards:** ISO 27001 (51), ISO 27002 (316), CIS CSC v8.1 (234)
- **US Industry:** PCI DSS v4.0.1 (364), SOC 2 (412), HIPAA (136)
- **APAC:** Australia Essential Eight (37), Australia ISM (336), Singapore MAS TRM (214)
- **EU Regulations:** GDPR (42), DORA (103), NIS2 (68)
- **UK Standards:** NCSC CAF 4.0 (67), Cyber Essentials (26)
- **European National:** Netherlands (27), Norway (23), Sweden (25), Germany (18/91/239)
- **Financial:** SWIFT CSCF 2023 (127)
- **Cloud:** CSA CCM v4 (334)

## Tools

### Core Tools

**`list_frameworks()`** - List all 28 frameworks with control counts

**`get_control(control_id)`** - Get full details for a specific SCF control
- Returns description, domain, weight, PPTDF category, and mappings to all 28 frameworks

**`search_controls(query, frameworks=[], limit=10)`** - Search controls by keyword
- Optional framework filtering
- Full-text search across names and descriptions

**`get_framework_controls(framework)`** - Get all controls for a specific framework
- Returns controls organized by domain

**`map_frameworks(source_framework, target_framework, source_control=None)`** - Map between frameworks
- Bidirectional mapping via SCF
- Optional filtering to specific source control

### Purchased Standards Tools

**`list_available_standards()`** - List all available standards (SCF + imported)

**`query_standard(standard, query, limit=10)`** - Search within purchased standard
- Requires import first
- Returns clauses with page numbers

**`get_clause(standard, clause_id)`** - Get full text of specific clause
- Requires import first

See [PAID_STANDARDS_GUIDE.md](PAID_STANDARDS_GUIDE.md) for import instructions.

## Add Purchased Standards (Optional)

Import your purchased ISO 27001, NIST SP 800-53, or other standards to get official text alongside SCF descriptions:

```bash
# Install import tools
pip install -e '.[import-tools]'

# Import purchased PDF
scf-mcp import-standard \
  --file ~/Downloads/ISO-27001-2022.pdf \
  --type iso_27001_2022 \
  --title "ISO/IEC 27001:2022"

# Restart MCP, then query
```

Your paid content stays private in `~/.security-controls-mcp/` (never committed to git).

Full guide: [PAID_STANDARDS_GUIDE.md](PAID_STANDARDS_GUIDE.md)

## Technical Architecture

**Data Pipeline:**
SCF JSON → In-memory index → MCP tools → AI response

**Key principles:**
- All control text returns verbatim from SCF source with zero LLM paraphrasing
- Framework mappings use ComplianceForge's authoritative crosswalks
- Optional purchased standards stored locally (never committed)
- Search results optimized for AI context windows

**Data integrity:**
- SCF version locked to 2025.4 for consistency
- All mappings sourced from official SCF framework crosswalks
- User-imported standards require valid licenses

## Data Source

Based on **SCF 2025.4** (released December 29, 2025)

- 1,451 controls across all domains
- 580+ framework mappings (28 frameworks)
- Licensed under Creative Commons (data)
- Source: [ComplianceForge SCF](https://securecontrolsframework.com/)

**Included data files:**
- `scf-controls.json` - All 1,451 controls with framework mappings
- `framework-to-scf.json` - Reverse index for framework-to-SCF lookups

## Related Projects

Part of **Ansvar's Compliance Suite** - MCP servers that work together for end-to-end compliance:

**EU Regulations MCP** - Query 47 EU regulations (GDPR, AI Act, DORA, NIS2, etc.)
- `npx @ansvar/eu-regulations-mcp`
- [github.com/Ansvar-Systems/EU_compliance_MCP](https://github.com/Ansvar-Systems/EU_compliance_MCP)

**US Regulations MCP** - Query US federal and state compliance laws (HIPAA, CCPA, SOX, etc.)
- `npm install @ansvar/us-regulations-mcp`
- [github.com/Ansvar-Systems/US_Compliance_MCP](https://github.com/Ansvar-Systems/US_Compliance_MCP)

**OT Security MCP** - Query IEC 62443, NIST 800-82/53, MITRE ATT&CK for ICS
- `npm install @ansvar/ot-security-mcp`
- [github.com/Ansvar-Systems/ot-security-mcp](https://github.com/Ansvar-Systems/ot-security-mcp)

### Workflow Example

```
1. "What DORA requirements apply to ICT risk management?"
   → EU Regulations MCP returns Article 6 full text

2. "What security controls satisfy DORA Article 6?"
   → Security Controls MCP maps to ISO 27001, NIST CSF controls

3. "Show me ISO 27001 A.8.1 implementation details"
   → Security Controls MCP returns control requirements
```

## Development

```bash
# Clone and install
git clone https://github.com/Ansvar-Systems/security-controls-mcp.git
cd security-controls-mcp
pip install -e '.[dev]'

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/ -v
```

Pre-commit hooks run automatically before each commit:
- Code formatting (black, ruff)
- Linting (ruff check, YAML/JSON validation)
- Tests (pytest, smoke tests, server startup)

Bypass hooks (emergencies only): `git commit --no-verify`

## Important Disclaimers

**Not Legal or Compliance Advice:** Control text is sourced directly from official SCF data, but this tool should not be used as the sole basis for compliance decisions. Always verify against official framework sources and consult qualified compliance professionals.

**AI Content Restrictions:** The SCF license explicitly prohibits using AI systems to generate derivative content such as policies, standards, procedures, metrics, risks, or threats based on SCF data. You may query and analyze controls, but not generate derivative compliance artifacts.

**Purchased Standards:** Optional standards imports require valid licenses. You must own legitimate copies and comply with copyright restrictions. This tool does not include or distribute any copyrighted standards text.

**Framework Coverage:** While SCF provides comprehensive mappings, not all controls map 1:1 across frameworks. Always review official framework documentation for authoritative requirements.

## License

**Code:** Apache License 2.0 (see [LICENSE](LICENSE))

**Data:** Creative Commons Attribution-NoDerivatives 4.0 International (CC BY-ND 4.0) by ComplianceForge
- Source: [Secure Controls Framework (SCF)](https://securecontrolsframework.com/)
- Version: SCF 2025.4 (December 29, 2025)

**What you MAY do:**
- Query and analyze SCF controls
- Map between frameworks
- Reference controls in your own work (with attribution)
- Use this MCP server to understand control requirements

**What you MAY NOT do:**
- Use AI to generate policies or procedures based on SCF controls
- Create derivative frameworks or modified versions for distribution
- Remove or modify control definitions

For complete terms: [SCF Terms & Conditions](https://securecontrolsframework.com/terms-conditions/)

---

## More Open Source from Ansvar

We maintain a family of MCP servers for compliance and security professionals:

| Server | Description | Install |
|--------|-------------|---------|
| **[EU Regulations](https://github.com/Ansvar-Systems/EU_compliance_MCP)** | 47 EU regulations (GDPR, AI Act, DORA, NIS2, MiFID II, eIDAS, MDR...) | `npx @ansvar/eu-regulations-mcp` |
| **[US Regulations](https://github.com/Ansvar-Systems/US_Compliance_MCP)** | HIPAA, CCPA, SOX, GLBA, FERPA, COPPA, FDA 21 CFR Part 11, state privacy laws | `npx @ansvar/us-regulations-mcp` |
| **[OT Security](https://github.com/Ansvar-Systems/ot-security-mcp)** | IEC 62443, NIST 800-82, MITRE ATT&CK for ICS | `npx @ansvar/ot-security-mcp` |
| **[Automotive](https://github.com/Ansvar-Systems/Automotive-MCP)** | UNECE R155/R156, ISO 21434 for automotive cybersecurity | `npx @ansvar/automotive-cybersecurity-mcp` |
| **[Sanctions](https://github.com/Ansvar-Systems/Sanctions-MCP)** | Offline sanctions screening with OpenSanctions (30+ lists) | `pip install ansvar-sanctions-mcp` |

Browse all projects: [ansvar.eu/open-source](https://ansvar.eu/open-source)

---

**Built by:** [Ansvar Systems](https://ansvar.eu) (Stockholm, Sweden)
