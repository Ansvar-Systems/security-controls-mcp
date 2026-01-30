# Security Controls MCP Server

[![MCP](https://img.shields.io/badge/MCP-0.9.0+-blue.svg)](https://modelcontextprotocol.io)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![SCF](https://img.shields.io/badge/SCF-2025.4-orange.svg)](https://securecontrolsframework.com/)

## Overview

**The universal translator for security frameworks.**

The Security Controls MCP Server is an open-source tool that makes 1,451 security controls across 28 frameworks searchable and AI-accessible directly through Claude, Cursor, or any MCP-compatible client.

Built on the [Secure Controls Framework (SCF)](https://securecontrolsframework.com/) by ComplianceForge.

## Key Features

**Coverage:**
- 1,451 security controls spanning governance, risk, compliance, and technical domains
- 28 major frameworks including ISO 27001, NIST CSF, DORA, PCI DSS, CMMC, Australian Essential Eight, Singapore MAS TRM, SWIFT CSCF, and more
- Bidirectional mapping between any two frameworks via SCF rosetta stone
- Optional integration with purchased standards (ISO, NIST 800-53) for official text

**Capabilities:**
- Full-text search across all control descriptions and names
- Natural language queries instead of framework-specific control IDs
- Cross-framework requirement comparison (e.g., "What DORA controls does ISO 27001 A.5.15 map to?")
- Control filtering by framework, domain, or keyword
- SCF control metadata including PPTDF categories and security domain weights

---

## Why This Exists

When you're implementing security controls, you face a common problem: different frameworks describe the same security measures in different ways. ISO 27001 has one control ID, NIST CSF has another, PCI DSS has yet another — but they're all talking about the same thing.

This MCP server solves that by giving you instant **bidirectional mapping** between any two frameworks via the SCF rosetta stone. Ask Claude "What DORA controls does ISO 27001 A.5.15 map to?" and get an immediate, authoritative answer backed by ComplianceForge's comprehensive framework database.

---

## 🔒 Add Your Purchased Standards (Optional)

**NEW:** Import your purchased ISO 27001, NIST SP 800-53, or other standards to get:

✅ **Official text** from your licensed copies alongside SCF descriptions
✅ **Full clauses** with page numbers for compliance research
✅ **Enhanced queries** - see both SCF mappings AND official requirements

Your paid content stays private in `~/.security-controls-mcp/` (never committed to git).

**Quick example:**
```bash
# Install import tools
pip install -e '.[import-tools]'

# Import your purchased PDF
scf-mcp import-standard \
  --file ~/Downloads/ISO-27001-2022.pdf \
  --type iso_27001_2022 \
  --title "ISO/IEC 27001:2022"

# Restart MCP, then query:
# "Show me GOV-01 with official ISO 27001 text"
```

**📖 Full Guide:** [PAID_STANDARDS_GUIDE.md](PAID_STANDARDS_GUIDE.md) - Complete setup, troubleshooting, and license compliance information.

---

## Installation & Setup

### Quick Install (Recommended)

**Option 1: Using pipx (Recommended)**
```bash
pipx install security-controls-mcp
```

**Option 2: Using pip**
```bash
pip install security-controls-mcp
```

**Option 3: From Source**
```bash
git clone https://github.com/Ansvar-Systems/security-controls-mcp.git
cd security-controls-mcp
pip install -e .
```

**Requirements:**
- Python 3.10 or higher
- pip or pipx

### Development Setup (For Contributors)

If you're contributing to the project, install development tools and pre-commit hooks:

```bash
# Install development dependencies
pip install -e '.[dev]'

# Install pre-commit hooks (runs tests/linting before each commit)
pre-commit install
```

Pre-commit hooks automatically run before each commit:
- **Code formatting** - black, ruff (auto-fixes)
- **Linting** - ruff check, YAML/JSON validation
- **Tests** - pytest, smoke tests, server startup test

**Bypass hooks (emergencies only):**
```bash
git commit --no-verify
```

**Run hooks manually:**
```bash
# All hooks on all files
pre-commit run --all-files

# Specific hook
pre-commit run black --all-files
```

### Claude Desktop Configuration

After installation, add to `claude_desktop_config.json`:

**If installed via pip/pipx:**
```json
{
  "mcpServers": {
    "security-controls": {
      "command": "scf-mcp"
    }
  }
}
```

**If installed from source:**
```json
{
  "mcpServers": {
    "security-controls": {
      "command": "python",
      "args": ["-m", "security_controls_mcp"],
      "cwd": "/path/to/security-controls-mcp"
    }
  }
}
```

**Config file location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

### Cursor / VS Code Configuration

Same configuration under `"mcp.servers"` instead of `"mcpServers"` in your settings.

### Testing

```bash
# Run all tests
pytest tests/ -v

# Or run quick validation
python test_server.py
```

**📖 Full Documentation:**
- **[INSTALL.md](INSTALL.md)** - Detailed setup instructions
- **[TESTING.md](TESTING.md)** - Validation steps and example queries
- **[PAID_STANDARDS_GUIDE.md](PAID_STANDARDS_GUIDE.md)** - Import purchased standards for official text

---

## Example Queries

Ask Claude these natural language questions:

- *"What does GOV-01 require?"*
- *"Search for controls about encryption key management"*
- *"What ISO 27001 controls map to DORA?"*
- *"List all controls needed for PCI DSS compliance"*
- *"Which DORA requirements does ISO 27001 A.5.15 satisfy?"*
- *"Show me all NIST CSF 2.0 controls related to incident response"*
- *"Map CMMC Level 2 controls to FedRAMP requirements"*

---

## Available Frameworks (28 Total)

When you call `list_frameworks()`, you get:

```
Available Frameworks (28 total)

- nist_800_53_r5: NIST SP 800-53 Revision 5 (777 controls)
- soc_2_tsc: SOC 2 (TSC 2017:2022) (412 controls)
- pci_dss_4.0.1: PCI DSS v4.0.1 (364 controls)
- fedramp_r5_moderate: FedRAMP Revision 5 (Moderate) (343 controls)
- australia_ism_2024: Australian ISM (June 2024) (336 controls)
- csa_ccm_4: CSA Cloud Controls Matrix v4 (334 controls)
- iso_27002_2022: ISO/IEC 27002:2022 (316 controls)
- nist_csf_2.0: NIST Cybersecurity Framework 2.0 (253 controls)
- germany_c5_2020: Germany C5:2020 (Cloud Controls) (239 controls)
- cis_csc_8.1: CIS Critical Security Controls v8.1 (234 controls)
- singapore_mas_trm_2021: Singapore MAS TRM 2021 (214 controls)
- cmmc_2.0_level_2: CMMC 2.0 Level 2 (198 controls)
- nist_privacy_framework_1_0: NIST Privacy Framework 1.0 (187 controls)
- hipaa_security_rule: HIPAA Security Rule (136 controls)
- swift_cscf_2023: SWIFT Customer Security Framework 2023 (127 controls)
- dora: Digital Operational Resilience Act (DORA) (103 controls)
- germany_bait: Germany BAIT (Banking IT Requirements) (91 controls)
- nis2: Network and Information Security Directive (NIS2) (68 controls)
- ncsc_caf_4.0: NCSC Cyber Assessment Framework 4.0 (67 controls)
- cmmc_2.0_level_1: CMMC 2.0 Level 1 (52 controls)
- iso_27001_2022: ISO/IEC 27001:2022 (51 controls)
- gdpr: General Data Protection Regulation (GDPR) (42 controls)
- australia_essential_8: Australian Essential Eight (37 controls)
- netherlands: Netherlands Cybersecurity Regulations (27 controls)
- uk_cyber_essentials: UK Cyber Essentials (26 controls)
- sweden: Sweden Cybersecurity Regulations (25 controls)
- norway: Norway Cybersecurity Regulations (23 controls)
- germany: Germany Cybersecurity Regulations (18 controls)
```

**Framework categories:**
- **US Government:** NIST 800-53, NIST CSF, NIST Privacy, FedRAMP, CMMC
- **International Standards:** ISO 27001, ISO 27002, CIS CSC
- **US Industry:** PCI DSS, SOC 2, HIPAA
- **APAC:** Australia Essential Eight, Australia ISM, Singapore MAS TRM
- **EU Regulations:** GDPR, DORA, NIS2
- **UK Standards:** NCSC CAF, Cyber Essentials
- **European National:** Netherlands, Norway, Sweden, Germany (general/BAIT/C5)
- **Financial:** SWIFT CSCF
- **Cloud:** CSA CCM

---

## Framework Roadmap

**Not Yet Available (Waiting for SCF Coverage):**

These security frameworks are not currently included because the Secure Controls Framework (SCF) doesn't provide official mappings. We maintain data quality and compliance consulting credibility by using only ComplianceForge-vetted mappings.

- 🇳🇱 **Netherlands BIO** (Baseline Informatiebeveiliging Overheid) - Dutch government security baseline
- 🇫🇮 **Finland KATAKRI** - Finnish defense forces security audit criteria
- 🇳🇴 **Norway NSM** Grunnprinsipper - Norwegian NSA basic security principles
- 🇸🇪 **Sweden MSB** - Swedish Civil Contingencies Agency cybersecurity frameworks
- 🇩🇰 **Denmark CFCS** - Center for Cybersikkerhed guidelines
- 🇧🇪 **Belgium CCB** - Centre for Cybersecurity Belgium frameworks
- 🇫🇷 **France ANSSI** SecNumCloud - French cybersecurity agency cloud framework

**Note:** The European country frameworks we DO include (Netherlands, Norway, Sweden, Germany) map to national cybersecurity **laws and regulations** (article numbers from GDPR, NIS2, etc.), not the specific security baseline frameworks listed above.

**Want these frameworks?**

1. **For private use:** Fork this repository and use the [paid standards import feature](PAID_STANDARDS_GUIDE.md) to add your purchased frameworks
2. **For public benefit:** Contribute framework mappings to SCF at https://securecontrolsframework.com/contact/

---

## Tools

### 1. `get_control`
Get details about a specific SCF control by ID.

```python
get_control(control_id="GOV-01")
```

**Returns:** Full control details including description, domain, weight, PPTDF category, and mappings to all 28 frameworks.

---

### 2. `search_controls`
Search for controls by keyword in name or description.

```python
search_controls(query="encryption", limit=10)
```

**Optional parameters:**
- `frameworks` - Filter to specific frameworks (e.g., `["dora", "iso_27001_2022"]`)
- `limit` - Maximum results (default: 10)

---

### 3. `list_frameworks`
List all available frameworks with metadata.

```python
list_frameworks()
```

**Returns:** All 28 frameworks with display names and control counts.

---

### 4. `get_framework_controls`
Get all SCF controls that map to a specific framework.

```python
get_framework_controls(framework="dora")
```

**Returns:** All controls with mappings to the specified framework, organized by domain.

---

### 5. `map_frameworks`
Map controls between two frameworks via SCF.

```python
map_frameworks(
  source_framework="iso_27001_2022",
  source_control="A.5.15",  # Optional: filter to specific control
  target_framework="dora"
)
```

**Returns:** SCF controls that map to both frameworks, showing the connection between them.

---

### 6. `list_available_standards`
List all available standards including built-in SCF and any purchased standards you've imported.

```python
list_available_standards()
```

**Returns:** List of available standards with metadata (type, title, import date).

---

### 7. `query_standard`
Search within a specific purchased standard (requires import first).

```python
query_standard(
  standard="iso_27001_2022",
  query="access control",
  limit=10
)
```

**Returns:** Relevant clauses/sections from the purchased standard with page numbers.

---

### 8. `get_clause`
Get the full text of a specific clause from a purchased standard.

```python
get_clause(
  standard="iso_27001_2022",
  clause_id="5.15"
)
```

**Returns:** Complete clause text with metadata from your purchased standard.

**Note:** Tools 6-8 require purchased standards to be imported first. See [PAID_STANDARDS_GUIDE.md](PAID_STANDARDS_GUIDE.md) for setup.

---

## Technical Architecture

**Data Pipeline:**
SCF JSON → In-memory index → MCP tools → AI response

**Key Principles:**
- All control text returns verbatim from SCF source data with zero LLM paraphrasing
- Framework mappings use ComplianceForge's authoritative control crosswalks
- Optional purchased standards stored locally in `~/.security-controls-mcp/` (never committed)

**Context Management:**
- Search results optimized for AI context windows
- Full control retrieval includes all framework mappings
- Cross-framework queries use bidirectional SCF mapping indices

**Data Integrity:**
- SCF version locked to 2025.4 for consistency
- Optional standards imported from user-purchased PDFs (with license compliance)
- All mappings sourced from official SCF framework crosswalks

---

## Data Source

Based on **SCF 2025.4** released December 29, 2025.

- **1,451 controls** across all domains
- **580+ framework mappings** (28 frameworks × 18-777 controls each)
- Licensed under **Creative Commons** (data)
- Source: [ComplianceForge SCF](https://securecontrolsframework.com/)

**Data files included in package:**
- `scf-controls.json` - All 1,451 controls with framework mappings
- `framework-to-scf.json` - Reverse index for framework-to-SCF lookups

---

## Important Disclaimers

**Not Legal or Compliance Advice:** Control text is sourced directly from official SCF data, but framework mappings and control interpretations are provided for research purposes only. This tool should not be used as the sole basis for compliance decisions. Always verify against official framework sources and consult qualified compliance professionals and auditors for your specific regulatory requirements.

**AI Content Restrictions:** The SCF license explicitly prohibits using AI systems to generate derivative content such as policies, standards, procedures, metrics, risks, or threats based on SCF data. You may query and analyze controls, but not generate derivative compliance artifacts.

**Purchased Standards:** Optional standards imports (ISO, NIST) require valid licenses. You must own legitimate copies and comply with copyright restrictions. This tool does not include or distribute any copyrighted standards text.

**Framework Coverage:** While SCF provides comprehensive mappings, not all controls map 1:1 across frameworks. Some controls may be interpreted, consolidated, or split during mapping. Always review official framework documentation for authoritative requirements.

---

## Related Projects: Complete Compliance Suite

This server is part of **Ansvar's Compliance Suite** - three MCP servers that work together for end-to-end compliance coverage:

### 🇪🇺 [EU Regulations MCP](https://github.com/Ansvar-Systems/EU_compliance_MCP)
**Query 47 EU regulations directly from Claude**
- GDPR, AI Act, DORA, NIS2, MiFID II, PSD2, eIDAS, Medical Device Regulation, and 39 more
- Full regulatory text with article-level search
- Cross-regulation reference and comparison
- **Install:** `npx @ansvar/eu-regulations-mcp`

### 🇺🇸 [US Regulations MCP](https://github.com/Ansvar-Systems/US_Compliance_MCP)
**Query US federal and state compliance laws directly from Claude**
- HIPAA, CCPA, SOX, GLBA, FERPA, COPPA, FDA 21 CFR Part 11, and 8 more
- Federal and state privacy law comparison
- Breach notification timeline mapping
- **Install:** `npm install @ansvar/us-regulations-mcp`

### 🔐 Security Controls MCP (This Project)
**Query 1,451 security controls across 28 frameworks**
- ISO 27001, NIST CSF, DORA, PCI DSS, SOC 2, CMMC, FedRAMP, and 21 more
- Bidirectional framework mapping and gap analysis
- Import your purchased standards for official text
- **Install:** `pipx install security-controls-mcp`

### How They Work Together

**Regulations → Controls Implementation Workflow:**

```
1. "What DORA requirements apply to ICT risk management?"
   → EU Regulations MCP returns Article 6 full text

2. "What security controls satisfy DORA Article 6?"
   → Security Controls MCP maps to ISO 27001, NIST CSF, and SCF controls

3. "Show me ISO 27001 A.8.1 implementation details"
   → Security Controls MCP returns control requirements and framework mappings
```

**Complete compliance in one chat:**
- **EU/US Regulations MCPs** tell you WHAT compliance requirements you must meet
- **Security Controls MCP** tells you HOW to implement controls that satisfy those requirements

### Specialized: OT/ICS Security

### 🏭 [OT Security MCP](https://github.com/Ansvar-Systems/ot-security-mcp)
**Query IEC 62443, NIST 800-82/53, and MITRE ATT&CK for ICS**
- Specialized for OT/ICS environments (manufacturing, energy, critical infrastructure)
- Security levels, Purdue Model, zone/conduit architecture
- MITRE ATT&CK for ICS threat intelligence
- **Install:** `npm install @ansvar/ot-security-mcp`
- **Use case:** Industrial control systems, SCADA, PLCs, critical infrastructure

---

## Developer Information

**Built by:** [Ansvar Systems](https://ansvar.eu) (Stockholm, Sweden) — specializes in AI-accelerated threat modeling and compliance tools

**License:** Apache License 2.0 (code) / CC BY-ND 4.0 (data)

**Documentation:**
- [INSTALL.md](INSTALL.md) - Complete installation guide for all platforms
- [TESTING.md](TESTING.md) - Validation steps and example queries
- [PAID_STANDARDS_GUIDE.md](PAID_STANDARDS_GUIDE.md) - Import purchased standards
- [LEGAL_COMPLIANCE.md](LEGAL_COMPLIANCE.md) - License requirements and restrictions

**Related Projects:**
- **[EU Regulations MCP](https://github.com/Ansvar-Systems/eu-regulations-mcp)** - Query 37 EU regulations (AI Act, DORA, NIS2, GDPR, etc.) for complete EU compliance coverage

---

## License

### Code License

The source code in this repository is licensed under the **Apache License 2.0** (see [LICENSE](LICENSE)).

### Data License

The SCF control data (`scf-controls.json`, `framework-to-scf.json`) is licensed under the **Creative Commons Attribution-NoDerivatives 4.0 International (CC BY-ND 4.0)** by ComplianceForge.

- **Source:** [Secure Controls Framework (SCF)](https://securecontrolsframework.com/)
- **License:** [CC BY-ND 4.0](https://creativecommons.org/licenses/by-nd/4.0/)
- **Copyright:** ComplianceForge
- **Version:** SCF 2025.4 (Released December 29, 2025)

#### ⚠️ Important: AI Derivative Content Restriction

The SCF license **explicitly prohibits** using AI systems (including Claude) to generate derivative content such as policies, standards, procedures, metrics, risks, or threats based on SCF data.

**You MAY:**
- Query and analyze SCF controls
- Map between frameworks (e.g., "What DORA controls does ISO 27001 A.5.15 map to?")
- Reference controls in your own work (with proper attribution)
- Use this MCP server to understand control requirements

**You MAY NOT:**
- Ask Claude (or any AI) to generate policies or procedures based on SCF controls
- Create derivative frameworks or modified versions for distribution
- Remove or modify control definitions

For complete terms and conditions, see: [SCF Terms & Conditions](https://securecontrolsframework.com/terms-conditions/)
