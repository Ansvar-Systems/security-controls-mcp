# Security Controls MCP Server

[![MCP](https://img.shields.io/badge/MCP-0.9.0+-blue.svg)](https://modelcontextprotocol.io)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![SCF](https://img.shields.io/badge/SCF-2025.4-orange.svg)](https://securecontrolsframework.com/)

Query **1,451 security controls** across **16 frameworks** — from ISO 27001 and NIST CSF to DORA, PCI DSS, and more — directly from Claude, Cursor, or any MCP-compatible client.

Built on the [Secure Controls Framework (SCF)](https://securecontrolsframework.com/) by ComplianceForge.

---

## Why This Exists

When you're implementing security controls, you face a common problem: different frameworks describe the same security measures in different ways. ISO 27001 has one control ID, NIST CSF has another, PCI DSS has yet another — but they're all talking about the same thing.

This MCP server solves that by giving you instant **bidirectional mapping** between any two frameworks via the SCF rosetta stone. Ask Claude "What DORA controls does ISO 27001 A.5.15 map to?" and get an immediate, authoritative answer backed by ComplianceForge's comprehensive framework database.

**Works with:** [EU Regulations MCP](https://github.com/Ansvar-Systems/eu-regulations-mcp) for complete EU compliance coverage (DORA + NIS2 + AI Act + GDPR + more).

---

## Quick Start

### Installation

See **[INSTALL.md](INSTALL.md)** for detailed setup instructions.

**Quick version:**
```bash
git clone https://github.com/Ansvar-Systems/security-controls-mcp.git
cd security-controls-mcp
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### Testing

See **[TESTING.md](TESTING.md)** for validation steps and example queries.

**Quick test:**
```bash
# Run all tests
pytest tests/ -v

# Or run quick validation
python test_server.py
```

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

## Available Frameworks (16 Total)

When you call `list_frameworks()`, you get:

```
Available Frameworks (16 total)

- nist_800_53_r5: NIST SP 800-53 Revision 5 (777 controls)
- soc_2_tsc: SOC 2 (TSC 2017:2022) (412 controls)
- pci_dss_4.0.1: PCI DSS v4.0.1 (364 controls)
- fedramp_r5_moderate: FedRAMP Revision 5 (Moderate) (343 controls)
- iso_27002_2022: ISO/IEC 27002:2022 (316 controls)
- nist_csf_2.0: NIST Cybersecurity Framework 2.0 (253 controls)
- cis_csc_8.1: CIS Critical Security Controls v8.1 (234 controls)
- cmmc_2.0_level_2: CMMC 2.0 Level 2 (198 controls)
- hipaa_security_rule: HIPAA Security Rule (136 controls)
- dora: Digital Operational Resilience Act (DORA) (103 controls)
- nis2: Network and Information Security Directive (NIS2) (68 controls)
- ncsc_caf_4.0: NCSC Cyber Assessment Framework 4.0 (67 controls)
- cmmc_2.0_level_1: CMMC 2.0 Level 1 (52 controls)
- iso_27001_2022: ISO/IEC 27001:2022 (51 controls)
- gdpr: General Data Protection Regulation (GDPR) (42 controls)
- uk_cyber_essentials: UK Cyber Essentials (26 controls)
```

**Framework categories:**
- **Government:** NIST 800-53, NIST CSF, FedRAMP, CMMC
- **International Standards:** ISO 27001, ISO 27002, CIS CSC
- **Industry:** PCI DSS, SOC 2, HIPAA
- **EU Regulations:** DORA, NIS2, GDPR
- **UK Standards:** NCSC CAF, Cyber Essentials

---

## Tools

### 1. `get_control`
Get details about a specific SCF control by ID.

```python
get_control(control_id="GOV-01")
```

**Returns:** Full control details including description, domain, weight, PPTDF category, and mappings to all 16 frameworks.

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

**Returns:** All 16 frameworks with display names and control counts.

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

## Data Source

Based on **SCF 2025.4** released December 29, 2025.

- **1,451 controls** across all domains
- **180+ framework mappings** (16 frameworks × 0-777 controls each)
- Licensed under **Creative Commons** (data)
- Source: [ComplianceForge SCF](https://securecontrolsframework.com/)

**Data files included in package:**
- `scf-controls.json` - All 1,451 controls with framework mappings
- `framework-to-scf.json` - Reverse index for framework-to-SCF lookups

---

## Disclaimer

This tool provides technical control mappings based on the SCF framework. It is **not legal advice** and should not be used as the sole basis for compliance decisions. Always consult with qualified compliance professionals and auditors for your specific regulatory requirements.

---

## Related Projects

- **[EU Regulations MCP](https://github.com/Ansvar-Systems/eu-regulations-mcp)** - Query EU AI Act, DORA, NIS2, DSA, DMA, and more alongside these security controls for complete EU compliance coverage.

---

## License

- **Code:** Apache License 2.0 (see [LICENSE](LICENSE))
- **Data:** Creative Commons (SCF by ComplianceForge)

---

Built by [Ansvar Systems](https://ansvar.eu) — Stockholm, Sweden
