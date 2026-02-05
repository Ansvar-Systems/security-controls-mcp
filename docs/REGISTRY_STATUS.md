# Registry & Distribution Status

**Last Updated:** 2026-02-05
**Current Version:** v0.4.0

---

## Distribution Status

| Registry | Status | Link |
|----------|--------|------|
| **PyPI** | ✅ Published | [security-controls-mcp](https://pypi.org/project/security-controls-mcp/) |
| **GitHub Release** | ✅ Published | [v0.4.0](https://github.com/Ansvar-Systems/security-controls-mcp/releases/tag/v0.4.0) |
| **Docker Hub** | ✅ Published | [ansvar/security-controls-mcp](https://hub.docker.com/r/ansvar/security-controls-mcp) |
| **MCP Registry** | ⏳ Pending submission | See below |
| **awesome-mcp-servers** | ⏳ Pending PR | See below |

---

## Action Items: Registry Submissions

### 1. Official MCP Registry

**Namespace:** `io.github.Ansvar-Systems/security-controls`

**Steps to submit:**

```bash
# 1. Clone the registry repo
git clone https://github.com/modelcontextprotocol/registry
cd registry

# 2. Build the publisher CLI
make publisher

# 3. Authenticate with GitHub
./bin/mcp-publisher login

# 4. Publish using the server.json in this repo
./bin/mcp-publisher publish ../security-controls-mcp/server.json
```

**Alternative: Manual submission**
- Open issue at https://github.com/modelcontextprotocol/registry/issues
- Request indexing of `security-controls-mcp` from PyPI

---

### 2. awesome-mcp-servers List

**Repository:** https://github.com/wong2/awesome-mcp-servers

**Steps to submit:**

1. Fork the repository
2. Add entry under appropriate category (Security/Compliance):

```markdown
### Security & Compliance

- [security-controls-mcp](https://github.com/Ansvar-Systems/security-controls-mcp) - 1,451 security controls across 261 frameworks (ISO 27001, NIST, DORA, ISO 42001, EU AI Act) with bidirectional mapping. `Python` `Apache-2.0`
```

3. Submit PR with title: "Add security-controls-mcp (261 framework coverage)"

---

## Package Metadata

### PyPI Keywords
```
mcp, model-context-protocol, security, compliance, ISO-27001, NIST,
DORA, PCI-DSS, SOC-2, HIPAA, GDPR, ISO-42001, AI-governance,
NIST-AI-RMF, EU-AI-Act, SCF, framework-mapping
```

### server.json (MCP Registry)
- **Name:** `io.github.Ansvar-Systems/security-controls`
- **Version:** `0.4.0`
- **Tags:** security, compliance, governance, ISO-27001, ISO-42001, NIST, NIST-AI-RMF, DORA, PCI-DSS, SOC-2, HIPAA, GDPR, EU-AI-Act, AI-governance, framework-mapping, SCF

---

## Cross-Promotion

### Related Ansvar MCP Servers

| Server | Registry | Status |
|--------|----------|--------|
| EU Regulations MCP | npm | ✅ `@ansvar/eu-regulations-mcp` |
| US Regulations MCP | npm | ✅ `@ansvar/us-regulations-mcp` |
| OT Security MCP | npm | ✅ `@ansvar/ot-security-mcp` |
| Automotive MCP | npm | ✅ `@ansvar/automotive-cybersecurity-mcp` |
| Sanctions MCP | PyPI | ✅ `ansvar-sanctions-mcp` |

---

## Verification Checklist

After submission, verify:

- [ ] Package appears on https://registry.modelcontextprotocol.io/
- [ ] Search for "security-controls" returns the package
- [ ] Package metadata shows 261 frameworks
- [ ] Install command works: `pipx install security-controls-mcp`
- [ ] Listed on awesome-mcp-servers README

---

## Support

- **Issues:** https://github.com/Ansvar-Systems/security-controls-mcp/issues
- **Website:** https://ansvar.eu
- **Email:** hello@ansvar.eu
