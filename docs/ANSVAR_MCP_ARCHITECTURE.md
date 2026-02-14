# Ansvar MCP Architecture - Complete Suite

**Central documentation for all Ansvar Systems MCP servers**

Last Updated: 2026-01-30

---

## Overview

Ansvar Systems maintains a suite of 5 interconnected MCP servers for comprehensive compliance, security, and risk management. These servers work together to provide end-to-end regulatory compliance and security control implementation.

### The Five Servers

| Server | Purpose | Tech Stack | Package Registry | Status |
|--------|---------|------------|------------------|--------|
| **Security Controls MCP** | 1,451 controls across 28 frameworks | Python + SQLite | PyPI | ✅ v0.2.1 Published |
| **EU Regulations MCP** | 47 EU regulations (GDPR, DORA, etc.) | TypeScript + SQLite | npm | ✅ Published |
| **US Regulations MCP** | 15 US federal & state laws | TypeScript + SQLite | npm | ✅ Published |
| **OT Security MCP** | IEC 62443, NIST 800-82/53, MITRE ICS | TypeScript + SQLite | npm | ✅ v0.2.0 Published |
| **Sanctions MCP** | OFAC/EU/UN sanctions + PEP checks | Python + SQLite | PyPI | 🟡 Ready (Not Published) |

---

## Architecture Principles

### 1. Local-First Design
- **Offline-capable**: All servers work without internet (except initial data ingestion)
- **SQLite databases**: Fast, embedded, zero-configuration
- **FTS5 full-text search**: Sub-millisecond search across thousands of entries
- **No API dependencies**: Run entirely on user's machine

### 2. MCP Protocol Integration
- **Model Context Protocol**: Anthropic's standard for AI tool integration
- **Claude Desktop**: Primary deployment target
- **Cursor/VS Code**: Full compatibility via MCP
- **Unified interface**: All servers expose consistent tool patterns

### 3. Data Quality & Freshness
- **Official sources only**: EUR-Lex, NIST, MITRE, ISO, OpenSanctions
- **Daily update checks**: Automated GitHub Actions workflows
- **Version tracking**: All data sources tracked with timestamps
- **Staleness protection**: Warnings when data is >7 days old

### 4. Cross-Server Integration
- **Bidirectional mappings**: Regulations ↔ Controls ↔ Frameworks
- **Consistent IDs**: Control IDs work across all servers
- **Workflow examples**: Documentation shows multi-server use cases

---

## Server Details

### 1. Security Controls MCP

**Repository**: https://github.com/Ansvar-Systems/security-controls-mcp

**Purpose**: Query and map security controls across 28 frameworks including ISO 27001, NIST CSF, DORA, PCI DSS, SOC 2, and more.

**Tech Stack**:
- **Language**: Python 3.11+
- **Database**: SQLite with FTS5
- **Data Source**: SCF (Secure Controls Framework) as rosetta stone
- **Package Manager**: Poetry
- **Distribution**: PyPI (`pipx install security-controls-mcp`)

**Key Features**:
- 1,451 security controls
- 28 frameworks (16→28 in v0.2.1 expansion)
- Bidirectional framework mapping
- Gap analysis between frameworks
- Official text import for purchased standards

**Deployment**:
```bash
# Installation
pipx install security-controls-mcp

# Claude Desktop config
{
  "mcpServers": {
    "security-controls": {
      "command": "security-controls-mcp"
    }
  }
}
```

**Data Updates**: Manual - requires re-ingesting SCF data and republishing

**Current Version**: v0.2.1 (Published 2026-01-29)

---

### 2. EU Regulations MCP

**Repository**: https://github.com/Ansvar-Systems/EU_compliance_MCP

**Purpose**: Query 47 EU regulations with full article text, recitals, definitions, and control mappings.

**Tech Stack**:
- **Language**: TypeScript
- **Database**: SQLite with FTS5
- **Data Source**: EUR-Lex official publications + UNECE
- **Package Manager**: npm
- **Distribution**: npm (`npx @ansvar/eu-regulations-mcp`)

**Key Features**:
- 47 regulations (GDPR, DORA, NIS2, AI Act, etc.)
- 2,438 articles + 3,712 recitals
- 1,138 official definitions
- 685 ISO 27001 & NIST CSF mappings
- 305 sector applicability rules

**Deployment**:
```bash
# Installation
npm install -g @ansvar/eu-regulations-mcp

# Claude Desktop config
{
  "mcpServers": {
    "eu-regulations": {
      "command": "npx",
      "args": ["-y", "@ansvar/eu-regulations-mcp"]
    }
  }
}
```

**Data Updates**:
- **Automated**: Daily GitHub Actions check EUR-Lex for updates
- **Auto-update mode**: Manual trigger to re-ingest all regulations
- **Publishes**: Automatically to npm when version tagged

**Current Version**: Published (check npm for latest)

**Special Notes**:
- Pre-built database (~18MB) shipped in npm package
- Puppeteer required for maintainer ingestion (EUR-Lex WAF bypass)
- End users never rebuild database

---

### 3. US Regulations MCP

**Repository**: https://github.com/Ansvar-Systems/US_Compliance_MCP

**Purpose**: Query 15 US federal and state compliance laws with full text and cross-references.

**Tech Stack**:
- **Language**: TypeScript
- **Database**: SQLite with FTS5
- **Data Source**: GPO, state government sites, official sources
- **Package Manager**: npm
- **Distribution**: npm (`npm install @ansvar/us-regulations-mcp`)

**Key Features**:
- 15 US regulations (HIPAA, CCPA, SOX, GLBA, etc.)
- Federal and state privacy law comparison
- Breach notification timeline mapping
- Cross-regulation search

**Deployment**:
```bash
# Installation
npm install -g @ansvar/us-regulations-mcp

# Claude Desktop config
{
  "mcpServers": {
    "us-regulations": {
      "command": "npx",
      "args": ["-y", "@ansvar/us-regulations-mcp"]
    }
  }
}
```

**Data Updates**: Manual - requires re-ingesting from official sources

**Current Version**: Published (check npm for latest)

---

### 4. OT Security MCP

**Repository**: https://github.com/Ansvar-Systems/ot-security-mcp

**Purpose**: Query IEC 62443, NIST 800-82/53, and MITRE ATT&CK for ICS to secure operational technology environments.

**Tech Stack**:
- **Language**: TypeScript
- **Database**: SQLite with FTS5
- **Data Sources**:
  - NIST 800-53 (OSCAL format from official GitHub)
  - MITRE ATT&CK for ICS (STIX 2.0 format)
  - IEC 62443 (user-supplied licensed data)
  - NIST 800-82 (curated from official PDF)
- **Package Manager**: npm
- **Distribution**: npm (`npm install @ansvar/ot-security-mcp`)

**Key Features**:
- 238 IEC 62443 requirements (3-3, 4-2, 3-2)
- 228 NIST 800-53 OT-relevant controls
- 83 MITRE ATT&CK for ICS techniques
- Security level mapping (SL-1 through SL-4)
- Zone/conduit architecture guidance (Purdue Model)
- 16 cross-standard mappings

**Deployment**:
```bash
# Installation
npm install -g @ansvar/ot-security-mcp

# Claude Desktop config
{
  "mcpServers": {
    "ot-security": {
      "command": "npx",
      "args": ["-y", "@ansvar/ot-security-mcp"]
    }
  }
}
```

**Data Updates**:
- **NIST 800-53**: Automated OSCAL ingestion from official GitHub
- **MITRE ATT&CK**: Automated STIX 2.0 ingestion
- **IEC 62443**: Manual (requires licensed standards)
- **Daily checks**: Automated workflow monitors NIST/MITRE sources

**Current Version**: v0.2.0 (Published 2026-01-29)

**Special Notes**:
- IEC 62443 content NOT included (copyrighted)
- Users provide their own licensed IEC standards
- Ingestion tools and schemas provided
- Sample data included for demonstration

---

### 5. Sanctions MCP

**Repository**: https://github.com/Ansvar-Systems/Sanctions-MCP

**Purpose**: Offline-capable sanctions screening for third-party risk management (DORA Article 28, AML/KYC compliance).

**Tech Stack**:
- **Language**: Python 3.11+
- **Database**: SQLite with FTS5
- **Data Source**: OpenSanctions (OFAC, EU, UN, etc.)
- **Package Manager**: Poetry
- **Distribution**: PyPI (`pip install ansvar-sanctions-mcp`)

**Key Features**:
- 30+ sanctions lists (OFAC, EU, UN, etc.)
- Fuzzy name matching with confidence scoring
- PEP (Politically Exposed Person) checks
- Dataset staleness protection (7-day warnings, 30-day blocks)
- Offline-capable with local database (~500MB)

**Deployment**:
```bash
# Installation
pip install ansvar-sanctions-mcp

# Claude Desktop config
{
  "mcpServers": {
    "sanctions": {
      "command": "sanctions-mcp"
    }
  }
}
```

**Data Updates**:
- **Manual ingestion**: User runs `ingest_datasets` tool
- **Dataset size**: ~500MB (one-time download)
- **Refresh cycle**: User-controlled (recommended weekly)

**Current Status**:
- ✅ Package built and ready
- ✅ 37/37 tests passing
- ✅ Apache 2.0 licensed
- ✅ PyPI configuration complete
- 🟡 **Not yet published to PyPI** (awaiting publication command)

---

## Deployment Architecture

### MCP Registry Auto-Discovery

All servers are configured for MCP Registry auto-discovery:
- **Keywords**: "mcp", "model-context-protocol" in package metadata
- **Repository URLs**: Properly configured in package.json/pyproject.toml
- **mcpName field**: Format `io.github.Ansvar-Systems/<project>`
- **Discovery timeline**: 24-48 hours after PyPI/npm publication

### Claude Desktop Integration

**Config Location**:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**Example Multi-Server Config**:
```json
{
  "mcpServers": {
    "security-controls": {
      "command": "security-controls-mcp"
    },
    "eu-regulations": {
      "command": "npx",
      "args": ["-y", "@ansvar/eu-regulations-mcp"]
    },
    "us-regulations": {
      "command": "npx",
      "args": ["-y", "@ansvar/us-regulations-mcp"]
    },
    "ot-security": {
      "command": "npx",
      "args": ["-y", "@ansvar/ot-security-mcp"]
    },
    "sanctions": {
      "command": "sanctions-mcp"
    }
  }
}
```

### Cursor/VS Code Integration

Similar configuration in `.cursor/mcp.json` or VS Code settings.

### Remote Endpoints (Vercel Streamable HTTP)

The following servers are deployed as Vercel serverless functions for remote MCP access (ChatGPT, Claude Web, etc.):

| Server | Endpoint | Protocol |
|--------|----------|----------|
| **EU Regulations MCP** | `https://eu-regulations-mcp.vercel.app/mcp` | Streamable HTTP |
| **US Regulations MCP** | `https://us-regulations-mcp.vercel.app/mcp` | Streamable HTTP |
| **Security Controls MCP** | `https://security-controls-mcp.vercel.app/mcp` | Streamable HTTP |
| **Automotive MCP** | `https://automotive-cybersecurity-mcp.vercel.app/mcp` | Streamable HTTP |
| **Swedish Law MCP** | `https://swedish-law-mcp.vercel.app/mcp` | Streamable HTTP |

Health check endpoints are available at `/health` for each server.

**Not deployed** (database too large for Vercel's 250MB limit):
- Dutch Law MCP (919MB database)

---

## Cross-Server Workflows

### Workflow 1: DORA Compliance Implementation

```
1. "What are DORA Article 6 ICT risk management requirements?"
   → EU Regulations MCP returns full article text

2. "Map DORA Article 6 to ISO 27001 controls"
   → Security Controls MCP shows mapped controls (A.5.1, A.8.1, etc.)

3. "Show me ISO 27001 A.8.1 implementation details"
   → Security Controls MCP returns control requirements

4. "Does my cloud provider have sanctions against them?"
   → Sanctions MCP screens vendor name against OFAC/EU/UN lists
```

### Workflow 2: NIS2 OT Operator Compliance

```
1. "What are NIS2 requirements for energy sector operators?"
   → EU Regulations MCP returns NIS2 Article 21 requirements

2. "What IEC 62443 security level satisfies NIS2 Article 21?"
   → OT Security MCP recommends Security Level 2-3

3. "Map IEC 62443 SR 1.1 to NIST 800-53 controls"
   → Security Controls MCP shows AC-2, IA-2 mappings

4. "What MITRE ATT&CK techniques target this configuration?"
   → OT Security MCP shows relevant ICS attack techniques
```

### Workflow 3: Third-Party Risk Management (TPRM)

```
1. "What are DORA Article 28 third-party risk requirements?"
   → EU Regulations MCP returns full article

2. "Screen vendor 'Acme Cloud Services' against sanctions"
   → Sanctions MCP checks OFAC/EU/UN lists + PEP database

3. "What security controls should I require from this vendor?"
   → Security Controls MCP maps DORA → ISO 27001 → NIST CSF

4. "Check if vendor processes health data under HIPAA"
   → US Regulations MCP shows HIPAA requirements
```

---

## Data Sources & Licenses

### Public Domain / Open Source

| Server | Data Source | License | Update Frequency |
|--------|-------------|---------|------------------|
| EU Regulations MCP | EUR-Lex, UNECE | Public domain (EU/UN) | Daily checks |
| US Regulations MCP | GPO, state sites | Public domain (US gov) | Manual |
| OT Security (NIST) | NIST GitHub OSCAL | Public domain | Daily checks |
| OT Security (MITRE) | MITRE GitHub STIX | Apache 2.0 | Daily checks |
| Security Controls MCP | SCF Framework | CC BY 4.0 | Manual |
| Sanctions MCP | OpenSanctions | CC BY 4.0 | User-controlled |

### Licensed / User-Supplied

| Server | Data Source | License | Notes |
|--------|-------------|---------|-------|
| Security Controls MCP | ISO standards text | Purchased from ISO | Optional import |
| OT Security MCP | IEC 62443 | Purchased from ISA/IEC | User provides JSON |

**Important**: No copyrighted standards are included in distributions. Tools and schemas provided for users who own licenses.

---

## CI/CD & Automation

### GitHub Actions Workflows

All repositories use GitHub Actions for:
- **Continuous Integration**: Tests on push/PR
- **Security Scanning**: npm audit, CodeQL, SBOM generation
- **Automated Publishing**: npm/PyPI on version tags
- **Daily Update Checks**: EUR-Lex, NIST, MITRE monitoring

### Update Notification Channels

- **GitHub Issues**: Auto-created when updates detected
- **Webhooks**: Optional Slack/Discord/generic webhooks
- **Auto-update Mode**: Manual trigger for full re-ingestion

### Release Process

**TypeScript/npm servers**:
```bash
npm run build
npm test
npm version patch  # or minor, major
git push && git push --tags
# GitHub Actions publishes to npm automatically
```

**Python/PyPI servers**:
```bash
poetry build
poetry run pytest
poetry version patch
git commit -am "bump version"
git push
poetry publish  # Manual for now
```

---

## Development Environment Setup

### Prerequisites

**All servers**:
- Git
- Modern terminal (iTerm2, Windows Terminal, etc.)

**TypeScript servers** (EU, US, OT):
- Node.js 18.x or 20.x
- npm or pnpm

**Python servers** (Security Controls, Sanctions):
- Python 3.11+
- Poetry or pipx

### Quick Start (Any Server)

```bash
# 1. Clone repository
git clone https://github.com/Ansvar-Systems/<repo-name>
cd <repo-name>

# 2. Install dependencies
npm install      # TypeScript
poetry install   # Python

# 3. Run tests
npm test         # TypeScript
poetry run pytest # Python

# 4. Run locally
npm run dev      # TypeScript (usually)
poetry run python -m src.server  # Python
```

---

## Maintenance Responsibilities

### Core Team (Ansvar Systems)

- **Data ingestion**: Add new regulations/standards
- **Framework expansion**: Add new security frameworks
- **Bug fixes**: Address reported issues
- **Security updates**: Dependency patches
- **Publishing**: Version bumps and releases

### Community Contributors

- **Bug reports**: Via GitHub Issues
- **Feature requests**: Via GitHub Discussions
- **Documentation improvements**: Via PRs
- **Data corrections**: Via GitHub Issues with sources

---

## Support & Contact

### Community Support
- **GitHub Issues**: Report bugs or request features
- **GitHub Discussions**: Ask questions or share use cases
- **README documentation**: Comprehensive guides in each repo

### Commercial Support
- **Email**: hello@ansvar.eu
- **Website**: https://ansvar.eu
- **Services**:
  - Custom framework mappings
  - Private deployments
  - Integration consulting
  - Compliance assessments

---

## Roadmap

### Near-Term (Q1-Q2 2026)

- [ ] **Sanctions MCP**: Publish v1.0.0 to PyPI
- [ ] **MCP Registry**: All 5 servers auto-discovered
- [ ] **Enhanced mappings**: More DORA ↔ ISO 27001 mappings
- [ ] **EU Regulations**: Add delegated acts for key regulations

### Medium-Term (Q2-Q3 2026)

- [ ] **Security Controls**: Framework expansion to 35+
- [ ] **OT Security**: Add NERC CIP for North American energy
- [ ] **US Regulations**: Add sector-specific regulations
- [ ] **Cross-server API**: Programmatic access for all servers

### Long-Term (Q3-Q4 2026)

- [ ] **Compliance Workflows**: Guided multi-server workflows
- [ ] **Assessment Tools**: Gap analysis automation
- [ ] **Reporting**: Export compliance evidence
- [ ] **Enterprise Features**: Team collaboration, audit trails

---

## Version History

| Server | Version | Date | Notes |
|--------|---------|------|-------|
| Security Controls | v0.2.1 | 2026-01-29 | 28 frameworks (16→28 expansion) |
| OT Security | v0.2.0 | 2026-01-29 | MITRE ATT&CK, zone/conduit |
| EU Regulations | Latest | 2026-01-xx | 47 regulations |
| US Regulations | Latest | 2026-01-xx | 15 regulations |
| Sanctions | v1.0.0 | Pending | Ready for PyPI |

---

## Architecture Diagrams

### Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Desktop / Cursor                    │
│                      (MCP Client)                            │
└───────────────────┬─────────────────────────────────────────┘
                    │ MCP Protocol (stdio)
        ┌───────────┼───────────┬───────────┬───────────┐
        │           │           │           │           │
┌───────▼─────┐ ┌──▼─────┐ ┌──▼─────┐ ┌──▼─────┐ ┌──▼─────┐
│ Security    │ │   EU   │ │   US   │ │   OT   │ │Sanctions│
│ Controls    │ │  Regs  │ │  Regs  │ │Security│ │   MCP  │
│    MCP      │ │  MCP   │ │  MCP   │ │  MCP   │ │        │
└──────┬──────┘ └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘
       │            │           │           │           │
       │ SQLite     │ SQLite    │ SQLite    │ SQLite    │ SQLite
       │ FTS5       │ FTS5      │ FTS5      │ FTS5      │ FTS5
       │            │           │           │           │
┌──────▼──────┐ ┌──▼─────┐ ┌──▼─────┐ ┌──▼─────┐ ┌──▼─────┐
│  28 Frameworks││47 Regs ││15 Regs ││IEC/NIST││OpenSanc-│
│1,451 Controls││2,438 Art││Articles││MITRE   ││tions    │
└─────────────┘ └────────┘ └────────┘ └────────┘ └────────┘
```

### Cross-Server Integration

```
┌──────────────────────────────────────────────────────────┐
│              Compliance Implementation Workflow           │
└──────────────────────────────────────────────────────────┘

 ┌─────────────┐      ┌──────────────┐     ┌──────────────┐
 │   EU/US     │──1──▶│  Security    │──2─▶│  OT Security │
 │Regulations  │      │  Controls    │     │      or      │
 │    MCPs     │      │     MCP      │     │  Sanctions   │
 └─────────────┘      └──────────────┘     └──────────────┘
       │                      │                     │
       │                      │                     │
 1. What must        2. What controls      3. How to implement
    I comply         satisfy this          (OT-specific) OR
    with?            requirement?          Are vendors safe?
                                          (Sanctions check)
```

---

## Contributing

See individual repository CONTRIBUTING.md files for contribution guidelines.

General principles:
- All regulation/standard content must come from official sources
- Data quality over quantity
- Comprehensive tests required
- Documentation updated with code changes
- Apache 2.0 license for all contributions

---

## About Ansvar Systems

We build AI-accelerated threat modeling and compliance tools for:
- **Automotive**: ISO 21434, UN R155/R156
- **Financial Services**: DORA, PSD2, MiFID II
- **Healthcare**: MDR, IVDR, HIPAA
- **Critical Infrastructure**: NIS2, IEC 62443, NERC CIP

**Location**: Stockholm, Sweden
**Website**: https://ansvar.eu
**Contact**: hello@ansvar.eu

---

*Last updated: 2026-01-30*
*Document maintained by: Ansvar Systems*
*File location: security-controls-mcp/docs/ANSVAR_MCP_ARCHITECTURE.md*
