# Security Controls MCP Server

Query **1,451 security controls** across **16 frameworks** — from ISO 27001 and NIST CSF to DORA, PCI DSS, and more — directly from Claude, Cursor, or any MCP-compatible client.

Built on the [Secure Controls Framework (SCF)](https://securecontrolsframework.com/) by ComplianceForge.

---

## Quick Start

### Installation

See **[INSTALL.md](INSTALL.md)** for detailed setup instructions.

**Quick version:**
```bash
git clone https://github.com/Ansvar-Systems/security-controls-mcp.git
cd security-controls-mcp
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### Testing

See **[TESTING.md](TESTING.md)** for validation steps and example queries.

**Quick test:**
```bash
python test_server.py
```

---

## Example Queries

- *"What does GOV-01 require?"*
- *"Search for controls about encryption key management"*
- *"What ISO 27001 controls map to DORA?"*
- *"List all controls needed for PCI DSS compliance"*
- *"Which DORA requirements does ISO 27001 A.5.15 satisfy?"*

---

## Available Frameworks

- **ISO 27001:2022** (51 controls)
- **NIST CSF 2.0** (253 controls)
- **NIST SP 800-53 R5** (777 controls)
- **DORA** (103 controls)
- **NIS2** (68 controls)
- **GDPR** (42 controls)
- **PCI DSS v4.0.1** (364 controls)
- **SOC 2 (TSC)** (412 controls)
- **CMMC 2.0** (198 controls L2, 52 controls L1)
- **CIS CSC v8.1** (234 controls)
- **UK Cyber Essentials** (26 controls)
- **NCSC CAF 4.0** (67 controls)
- **FedRAMP R5 Moderate** (343 controls)
- **HIPAA Security Rule** (136 controls)

---

## Tools

### 1. `get_control`
Get details about a specific SCF control by ID.

```
get_control(control_id="GOV-01")
```

### 2. `search_controls`
Search for controls by keyword.

```
search_controls(query="encryption", limit=10)
```

### 3. `list_frameworks`
List all available frameworks.

```
list_frameworks()
```

### 4. `get_framework_controls`
Get all controls for a specific framework.

```
get_framework_controls(framework="dora")
```

### 5. `map_frameworks`
Map controls between frameworks.

```
map_frameworks(
  source_framework="iso_27001_2022",
  source_control="A.5.15",
  target_framework="dora"
)
```

---

## Data Source

Based on **SCF 2025.4** released December 29, 2025.

- 1,451 controls
- 180+ framework mappings
- Licensed under Creative Commons

---

## License

Apache License 2.0

---

Built by [Ansvar Systems](https://ansvar.eu) — Stockholm, Sweden
