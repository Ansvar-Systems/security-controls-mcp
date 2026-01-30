# MCP Servers Registry Submission

## Compliance Suite by Ansvar Systems

We're submitting **three complementary MCP servers** that together provide comprehensive compliance coverage for organizations building regulated products:

---

## 1. EU Regulations MCP

**Query 47 EU regulations directly from Claude**

- **Package:** `@ansvar/eu-regulations-mcp` (npm)
- **Repository:** https://github.com/Ansvar-Systems/EU_compliance_MCP
- **License:** Apache 2.0
- **Coverage:** GDPR, AI Act, DORA, NIS2, MiFID II, PSD2, eIDAS, Medical Device Regulation, IVDR, and 38+ more
- **Use Case:** European market compliance - data protection, financial services, healthcare, AI, cybersecurity

**Installation:**
```bash
npx @ansvar/eu-regulations-mcp
```

**Key Features:**
- 47 EU regulations with full text
- 3,500+ recitals and articles
- Cross-regulation search and reference
- Daily EUR-Lex synchronization
- Article-level precision with context

---

## 2. US Regulations MCP

**Query US federal and state compliance laws directly from Claude**

- **Package:** `@ansvar/us-regulations-mcp` (npm)
- **Repository:** https://github.com/Ansvar-Systems/US_Compliance_MCP
- **License:** Apache 2.0
- **Coverage:** HIPAA, CCPA, SOX, GLBA, FERPA, COPPA, FDA 21 CFR Part 11, EPA RMP, FFIEC, NYDFS 500, + 4 state privacy laws (VA, CO, CT, UT)
- **Use Case:** US market compliance - healthcare, finance, consumer privacy, environmental, education

**Installation:**
```bash
npm install @ansvar/us-regulations-mcp
```

**Key Features:**
- 15 major US federal and state regulations
- Full regulatory text with section-level search
- Cross-regulation comparison
- State vs. federal requirement mapping
- Breach notification timeline comparison

---

## 3. Security Controls MCP

**Query 1,451 security controls across 28 frameworks directly from Claude**

- **Package:** `security-controls-mcp` (PyPI)
- **Repository:** https://github.com/Ansvar-Systems/security-controls-mcp
- **License:** Apache 2.0 (code) / CC BY-ND 4.0 (data)
- **Coverage:** ISO 27001, NIST CSF 2.0, NIST 800-53, DORA, NIS2, PCI DSS, SOC 2, CMMC, FedRAMP, HIPAA Security Rule, CIS Controls, and 17 more
- **Use Case:** Implementing security controls to meet compliance requirements from EU/US regulations

**Installation:**
```bash
pipx install security-controls-mcp
```

**Key Features:**
- 1,451 SCF (Secure Controls Framework) controls
- 28 framework mappings (ISO, NIST, PCI, SOC 2, HIPAA, DORA, NIS2, etc.)
- Bidirectional framework mapping (e.g., "What DORA controls satisfy ISO 27001 A.5.15?")
- Natural language search across control descriptions
- Gap analysis and control coverage reports

---

## Why These Three Work Together

**The Compliance Stack:**

1. **EU/US Regulations MCP** → Know WHAT compliance requirements you must meet
2. **Security Controls MCP** → Know HOW to implement controls that satisfy those requirements

**Example Workflow:**
```
User: "What are DORA's ICT risk management requirements?"
EU Regulations MCP: Returns Article 6 of DORA with full text

User: "What security controls satisfy DORA Article 6?"
Security Controls MCP: Maps to specific ISO 27001, NIST CSF, and SCF controls

User: "Show me ISO 27001 A.8.1 full text"
[If user has purchased ISO 27001]: Returns official standard text
[Otherwise]: Returns SCF description with framework mapping
```

**Real-World Use Cases:**
- **Startups:** "We're launching in the EU - what GDPR, AI Act, and DORA requirements apply?"
- **Healthcare:** "Map HIPAA Security Rule to NIST 800-53 controls for our cloud deployment"
- **Finance:** "What controls satisfy both MiFID II and SOX Section 404?"
- **Multi-National:** "Compare GDPR vs. CCPA data subject rights and implement unified controls"

---

## Submission JSON

```json
{
  "servers": [
    {
      "name": "eu-regulations-mcp",
      "displayName": "EU Regulations MCP",
      "description": "Query 47 EU regulations (GDPR, AI Act, DORA, NIS2, MiFID II, eIDAS, MDR, and more) directly from Claude for European market compliance",
      "repository": "https://github.com/Ansvar-Systems/EU_compliance_MCP",
      "package": "@ansvar/eu-regulations-mcp",
      "packageType": "npm",
      "author": "Ansvar Systems",
      "license": "Apache-2.0",
      "homepage": "https://github.com/Ansvar-Systems/EU_compliance_MCP",
      "tags": ["compliance", "regulations", "eu", "gdpr", "dora", "nis2", "ai-act", "legal"],
      "category": "compliance"
    },
    {
      "name": "us-regulations-mcp",
      "displayName": "US Regulations MCP",
      "description": "Query US federal and state compliance laws (HIPAA, CCPA, SOX, GLBA, FERPA, COPPA, FDA, and more) directly from Claude for US market compliance",
      "repository": "https://github.com/Ansvar-Systems/US_Compliance_MCP",
      "package": "@ansvar/us-regulations-mcp",
      "packageType": "npm",
      "author": "Ansvar Systems",
      "license": "Apache-2.0",
      "homepage": "https://github.com/Ansvar-Systems/US_Compliance_MCP",
      "tags": ["compliance", "regulations", "us", "hipaa", "ccpa", "sox", "privacy", "legal"],
      "category": "compliance"
    },
    {
      "name": "security-controls-mcp",
      "displayName": "Security Controls MCP",
      "description": "Query 1,451 security controls across 28 frameworks (ISO 27001, NIST CSF, DORA, PCI DSS, SOC 2, CMMC, and more) for compliance gap analysis and framework mapping",
      "repository": "https://github.com/Ansvar-Systems/security-controls-mcp",
      "package": "security-controls-mcp",
      "packageType": "pypi",
      "author": "Ansvar Systems",
      "license": "Apache-2.0",
      "homepage": "https://github.com/Ansvar-Systems/security-controls-mcp",
      "tags": ["security", "compliance", "iso27001", "nist", "dora", "pci-dss", "soc2", "framework-mapping"],
      "category": "compliance"
    }
  ]
}
```

---

## About Ansvar Systems

**Ansvar Systems** (Stockholm, Sweden) specializes in AI-accelerated compliance and security tools.

- **Website:** https://ansvar.eu
- **GitHub:** https://github.com/Ansvar-Systems
- **Focus:** Making compliance accessible through AI-native tooling

All three servers are:
- Open source (Apache 2.0)
- Production-ready and actively maintained
- Already published to npm/PyPI
- Used by organizations building regulated products

---

## Additional Resources

- **EU Regulations MCP:** [README](https://github.com/Ansvar-Systems/EU_compliance_MCP/blob/main/README.md)
- **US Regulations MCP:** [README](https://github.com/Ansvar-Systems/US_Compliance_MCP/blob/main/README.md)
- **Security Controls MCP:** [README](https://github.com/Ansvar-Systems/security-controls-mcp/blob/main/README.md)

All three servers have comprehensive documentation, installation guides, and example queries.
