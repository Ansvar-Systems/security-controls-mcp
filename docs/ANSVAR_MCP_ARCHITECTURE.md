# Ansvar MCP Architecture - Complete Suite

**Central documentation for all Ansvar Systems MCP servers**

Last Updated: 2026-02-14

---

## Overview

Ansvar Systems maintains a suite of interconnected MCP servers for comprehensive compliance, security, and risk management. These servers work together to provide end-to-end regulatory compliance and security control implementation.

### Server Inventory

| Server | Purpose | Tech Stack | Package Registry | Status |
|--------|---------|------------|------------------|--------|
| **Security Controls MCP** | 1,451 controls across 261 frameworks | Python + JSON | PyPI | ✅ v1.0.0 Published |
| **EU Regulations MCP** | 49 EU regulations (GDPR, DORA, etc.) | TypeScript + SQLite | npm | ✅ Published |
| **US Regulations MCP** | 15 US federal & state laws | TypeScript + SQLite | npm | ✅ Published |
| **Automotive MCP** | UNECE R155/R156 + ISO 21434 | TypeScript + SQLite | npm | ✅ v1.0.1 Published |
| **Swedish Law MCP** | Swedish statutes, case law, EU cross-refs | TypeScript + SQLite | npm | ✅ v1.2.1 Published |
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

### 5. Standardized `about()` Tool

Every server exposes an `about` tool returning structured JSON with four sections. This enables orchestration layers to discover server capabilities, verify data freshness, and display provenance without hardcoded knowledge of each server.

**Schema** (all servers return this exact shape):

```jsonc
{
  "server": {
    "name": "Human-readable name",
    "package": "@ansvar/package-name",
    "version": "1.0.0",               // from package.json / pyproject.toml
    "suite": "Ansvar Compliance Suite",
    "repository": "https://github.com/Ansvar-Systems/..."
  },
  "dataset": {
    "fingerprint": "a1b2c3d4e5f6",    // first 12 hex chars of SHA-256 of data file
    "built": "2026-02-14T10:00:00Z",   // mtime of database / data file
    "jurisdiction": "EU | US | SE | International (UNECE) + ISO | International",
    "content_basis": "Free-text describing source, consolidation status, caveats",
    "counts": { /* server-specific table counts */ },
    "freshness": {
      "last_checked": null,            // or ISO timestamp
      "check_method": "Daily EUR-Lex RSS | Manual review | ..."
    }
  },
  "provenance": {
    "sources": ["EUR-Lex", "NIST", "..."],
    "license": "Apache-2.0 (server code). Data license details...",
    "authenticity_note": "Not an official legal publication. Verify against..."
  },
  "security": {
    "access_model": "read-only",
    "network_access": false,
    "filesystem_access": false,
    "arbitrary_execution": false
  }
}
```

**Implementation pattern** (TypeScript servers):

```typescript
// src/tools/about.ts — pure function, no side effects
export interface AboutContext { version: string; fingerprint: string; dbBuilt: string; }
export function getAbout(db, context: AboutContext): AboutResult { /* ... */ }

// Entry point (index.ts / http-server.ts) — computed once at startup
const fingerprint = createHash('sha256').update(readFileSync(DB_PATH)).digest('hex').slice(0, 12);
const aboutContext: AboutContext = { version: pkgVersion, fingerprint, dbBuilt: stat.mtime.toISOString() };
registerTools(server, db, aboutContext);

// registry.ts — factory closure keeps handler signature consistent
function createAboutTool(context: AboutContext): ToolDefinition { /* ... */ }
export function buildTools(context: AboutContext): ToolDefinition[] {
  return [...TOOLS, createAboutTool(context)];
}
```

**Implementation pattern** (Python servers):

```python
# server.py — computed at module load
DATA_FINGERPRINT = hashlib.sha256(Path("data/controls.json").read_bytes()).hexdigest()[:12]
DATA_BUILT = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# In call_tool handler
about_data = { "server": {...}, "dataset": {...}, "provenance": {...}, "security": {...} }
return [TextContent(type="text", text=json.dumps(about_data, indent=2))]
```

### 6. Tool Annotations

All servers annotate their tools with MCP tool annotations for client-side UX hints:

```typescript
const READ_ONLY_ANNOTATIONS = { readOnlyHint: true, destructiveHint: false } as const;

function annotateTools(tools: Tool[]): Tool[] {
  return tools.map((tool) => ({
    ...tool,
    annotations: {
      title: tool.annotations?.title ?? toTitle(tool.name),
      readOnlyHint: true,
      destructiveHint: false,
    },
  }));
}
```

Since all Ansvar servers are read-only data retrieval tools, every tool gets `readOnlyHint: true` and `destructiveHint: false`. The `title` is auto-generated from the tool name (e.g., `search_legislation` → `Search Legislation`) unless explicitly overridden.

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
- 261 frameworks (SCF 2025.4)
- Bidirectional framework mapping
- Gap analysis between frameworks
- Official text import for purchased standards
- `about` tool with structured metadata (see Architecture Principles §5)

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

**Current Version**: v1.0.0 (Published)

---

### 2. EU Regulations MCP

**Repository**: https://github.com/Ansvar-Systems/EU_compliance_MCP

**Purpose**: Query 49 EU regulations with full article text, recitals, definitions, and control mappings.

**Tech Stack**:
- **Language**: TypeScript
- **Database**: SQLite with FTS5
- **Data Source**: EUR-Lex official publications + UNECE
- **Package Manager**: npm
- **Distribution**: npm (`npx @ansvar/eu-regulations-mcp`)

**Key Features**:
- 49 regulations (GDPR, DORA, NIS2, AI Act, CRA, 10 DORA RTS/ITS, etc.)
- 2,528 articles + 3,869 recitals
- 1,226 official definitions
- 709 ISO 27001 & NIST CSF 2.0 mappings
- 323 sector applicability rules
- 407 evidence requirements (all 49 regulations)
- `about` tool with structured metadata (see Architecture Principles §5)

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

### 5. Automotive Cybersecurity MCP

**Repository**: https://github.com/Ansvar-Systems/Automotive-MCP

**Purpose**: Query UNECE R155/R156 regulation text and ISO/SAE 21434 clause structure for automotive cybersecurity compliance.

**Tech Stack**:
- **Language**: TypeScript
- **Database**: SQLite with FTS5
- **Data Sources**: EUR-Lex (UNECE regulations), ISO (clause structure only)
- **Package Manager**: npm
- **Distribution**: npm (`npm install @ansvar/automotive-cybersecurity-mcp`)

**Key Features**:
- UNECE R155 (Cybersecurity) + R156 (Software Updates) full regulation text
- ISO/SAE 21434 clause structure and work products (full text requires license)
- Cross-framework mappings (regulation ↔ standard)
- Compliance traceability matrix export (Markdown/CSV)
- FTS5 full-text search across all sources
- `about` tool with structured metadata (see Architecture Principles §5)

**Deployment**:
```bash
# Claude Desktop config
{
  "mcpServers": {
    "automotive-cybersecurity": {
      "command": "npx",
      "args": ["-y", "@ansvar/automotive-cybersecurity-mcp"]
    }
  }
}
```

**Data Updates**: Manual — requires re-ingesting from EUR-Lex

**Current Version**: v1.0.1 (Published)

**Special Notes**:
- ISO 21434 full text NOT included (copyrighted) — only clause titles and mappings
- UNECE regulation text is freely reusable under EUR-Lex policy

---

### 6. Swedish Law MCP

**Repository**: https://github.com/Ansvar-Systems/swedish-law-mcp

**Purpose**: Query Swedish statutes (SFS), case law, preparatory works, and EU law cross-references for legal research.

**Tech Stack**:
- **Language**: TypeScript
- **Database**: SQLite with FTS5
- **Data Sources**: riksdagen.se (statutes), lagen.nu (case law, CC-BY)
- **Package Manager**: npm
- **Distribution**: npm (`npm install @ansvar/swedish-law-mcp`)

**Key Features**:
- 10,286 legal documents (statutes)
- 31,198 legal provisions with historical versions
- 5,944 court decisions (HD, HFD, AD, etc.)
- 6,735 preparatory works (Prop., SOU, Ds)
- 228 EU directives/regulations with Swedish implementation mappings
- Citation validation and formatting
- Time-aware queries (as-of-date for historical law)
- `about` tool with structured metadata (see Architecture Principles §5)

**Deployment**:
```bash
# Claude Desktop config
{
  "mcpServers": {
    "swedish-law": {
      "command": "npx",
      "args": ["-y", "@ansvar/swedish-law-mcp"]
    }
  }
}
```

**Data Updates**: Manual — riksdagen.se API for statutes, lagen.nu sync for case law

**Current Version**: v1.2.1 (Published)

**Special Notes**:
- Swedish law is not subject to copyright per 1 § upphovsrättslagen (1960:729)
- Case law from lagen.nu under CC-BY (Domstolsverket)
- Database is ~73MB (pre-built, shipped in npm package)

---

### 7. Sanctions MCP

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
    "automotive-cybersecurity": {
      "command": "npx",
      "args": ["-y", "@ansvar/automotive-cybersecurity-mcp"]
    },
    "swedish-law": {
      "command": "npx",
      "args": ["-y", "@ansvar/swedish-law-mcp"]
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
| Automotive MCP | EUR-Lex (UNECE R155/R156) | Public domain (UN) | Manual |
| Swedish Law MCP | riksdagen.se, lagen.nu | No copyright (1 § URL), CC-BY | Manual |
| OT Security (NIST) | NIST GitHub OSCAL | Public domain | Daily checks |
| OT Security (MITRE) | MITRE GitHub STIX | Apache 2.0 | Daily checks |
| Security Controls MCP | SCF Framework | CC BY 4.0 | Manual |
| Sanctions MCP | OpenSanctions | CC BY 4.0 | User-controlled |

### Licensed / User-Supplied

| Server | Data Source | License | Notes |
|--------|-------------|---------|-------|
| Security Controls MCP | ISO standards text | Purchased from ISO | Optional import |
| Automotive MCP | ISO/SAE 21434 | Purchased from ISO | Clause titles only; full text not included |
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
| Security Controls | v1.0.0 | 2026-02-14 | 261 frameworks, `about` tool |
| EU Regulations | Latest | 2026-02-14 | 49 regulations, `about` tool |
| US Regulations | Latest | 2026-02-14 | 15 regulations, `about` tool |
| Automotive | v1.0.1 | 2026-02-14 | R155/R156 + ISO 21434, `about` tool |
| Swedish Law | v1.2.1 | 2026-02-14 | 10K statutes, case law, `about` tool |
| OT Security | v0.2.0 | 2026-01-29 | MITRE ATT&CK, zone/conduit |
| Sanctions | v1.0.0 | Pending | Ready for PyPI |

---

## Architecture Diagrams

### Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Claude Desktop / Cursor / ChatGPT                     │
│                           (MCP Client)                                  │
│              calls about() on each server to discover capabilities      │
└───────────────────┬─────────────────────────────────────────────────────┘
                    │ MCP Protocol (stdio or Streamable HTTP)
    ┌───────┬───────┼───────┬───────┬───────┬───────┐
    │       │       │       │       │       │       │
┌───▼──┐ ┌─▼────┐ ┌▼─────┐ ┌▼─────┐ ┌▼─────┐ ┌▼────┐ ┌──────┐
│ Sec  │ │  EU  │ │  US  │ │Auto- │ │ SE   │ │ OT  │ │Sanc- │
│ Ctrl │ │ Regs │ │ Regs │ │motive│ │ Law  │ │ Sec │ │tions │
│ MCP  │ │ MCP  │ │ MCP  │ │ MCP  │ │ MCP  │ │ MCP │ │ MCP  │
└──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬──┘ └──┬───┘
   │        │        │        │        │        │       │
   │ JSON   │ SQLite │ SQLite │ SQLite │ SQLite │SQLite │SQLite
   │        │ FTS5   │ FTS5   │ FTS5   │ FTS5   │FTS5   │FTS5
   │        │        │        │        │        │       │
┌──▼───┐ ┌─▼────┐ ┌─▼────┐ ┌─▼────┐ ┌─▼────┐ ┌▼────┐ ┌▼─────┐
│ 261  │ │49 EU │ │15 US │ │R155  │ │10K   │ │IEC  │ │Open  │
│Framew│ │Regs  │ │Regs  │ │R156  │ │Stats │ │NIST │ │Sanc- │
│1451  │ │2528  │ │      │ │ISO   │ │6K    │ │MITRE│ │tions │
│Ctrls │ │Arts  │ │      │ │21434 │ │Cases │ │     │ │      │
└──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └─────┘ └──────┘
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

*Last updated: 2026-02-14*
*Document maintained by: Ansvar Systems*
*File location: security-controls-mcp/docs/ANSVAR_MCP_ARCHITECTURE.md*
