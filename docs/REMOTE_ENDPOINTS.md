# Ansvar MCP Suite - Remote Endpoints

**For website builder: All public remote access details for the Ansvar MCP servers.**

Last verified: 2026-02-14 (all endpoints healthy)

---

## Public Endpoints

All servers are live and publicly accessible. No authentication required.

| Server | Endpoint | Health Check |
|--------|----------|--------------|
| **EU Regulations MCP** | `https://eu-regulations-mcp.vercel.app/mcp` | [/health](https://eu-regulations-mcp.vercel.app/health) |
| **US Regulations MCP** | `https://us-regulations-mcp.vercel.app/mcp` | [/health](https://us-regulations-mcp.vercel.app/health) |
| **Security Controls MCP** | `https://security-controls-mcp.vercel.app/mcp` | [/health](https://security-controls-mcp.vercel.app/health) |
| **Automotive Cybersecurity MCP** | `https://automotive-cybersecurity-mcp.vercel.app/mcp` | [/health](https://automotive-cybersecurity-mcp.vercel.app/health) |
| **Swedish Law MCP** | `https://swedish-law-mcp.vercel.app/mcp` | [/health](https://swedish-law-mcp.vercel.app/health) |

**Protocol:** MCP (Model Context Protocol) over Streamable HTTP
**Authentication:** None (public access)
**Hosting:** Vercel serverless functions
**Cold start:** ~2-3 seconds on first request, then instant

---

## Server Descriptions

### EU Regulations MCP
49 EU regulations including GDPR, NIS2, DORA, AI Act, Cyber Resilience Act, and all 10 DORA RTS/ITS technical standards. Full-text search across 2,500+ articles, cross-regulation comparison with synonym expansion, ISO 27001 and NIST CSF 2.0 control mappings, sector applicability analysis, official definitions, and audit evidence requirements.

### US Regulations MCP
15 US federal and state compliance laws including HIPAA, CCPA/CPRA, SOX, GLBA, FISMA, and FedRAMP. Federal and state privacy law comparison, breach notification timeline mapping, and cross-regulation search.

### Security Controls MCP
1,451 security controls across 28 frameworks including ISO 27001, NIST CSF 2.0, SOC 2, PCI DSS, CIS Controls, DORA, and more. Bidirectional framework mapping, gap analysis between any two frameworks, and control search.

### Automotive Cybersecurity MCP
Automotive cybersecurity standards including UN R155 (Vehicle Cybersecurity), UN R156 (Software Updates), and ISO/SAE 21434. Type approval requirements, threat analysis and risk assessment (TARA) guidance, and cybersecurity management system (CSMS) requirements.

### Swedish Law MCP
Swedish legislation in Swedish, sourced directly from Riksdagen (Swedish Parliament). Full-text search across Swedish laws and regulations.

---

## How Users Can Connect

### Claude Web (claude.ai)
1. Go to **Settings > Connectors**
2. Click **"Add custom connector"**
3. Enter the server name and URL from the table above
4. Click **"Add"**

### Claude Desktop / Claude Code
Add to MCP config file:

**Claude Code** (`~/.claude/mcp.json`):
```json
{
  "mcpServers": {
    "eu-regulations": {
      "type": "url",
      "url": "https://eu-regulations-mcp.vercel.app/mcp"
    },
    "us-regulations": {
      "type": "url",
      "url": "https://us-regulations-mcp.vercel.app/mcp"
    },
    "security-controls": {
      "type": "url",
      "url": "https://security-controls-mcp.vercel.app/mcp"
    },
    "automotive-cybersecurity": {
      "type": "url",
      "url": "https://automotive-cybersecurity-mcp.vercel.app/mcp"
    },
    "swedish-law": {
      "type": "url",
      "url": "https://swedish-law-mcp.vercel.app/mcp"
    }
  }
}
```

**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):
Same format as above.

### ChatGPT
Available as MCP apps in developer mode (not yet in GPT Store).

### Any MCP-Compatible Client
Connect via Streamable HTTP transport to the `/mcp` endpoint URLs.

---

## npm Packages (Local/CLI Alternative)

Users can also install and run locally for offline use:

| Package | Install Command |
|---------|----------------|
| EU Regulations | `npx @ansvar/eu-regulations-mcp` |
| US Regulations | `npx @ansvar/us-regulations-mcp` |
| Security Controls | `pipx install security-controls-mcp` |
| Automotive Cybersecurity | `npx @ansvar/automotive-cybersecurity-mcp` |
| Swedish Law | `npx @ansvar/swedish-law-mcp` |

---

## App Store / Marketplace Status

| Platform | Status |
|----------|--------|
| ChatGPT GPT Store | Not submitted (DEV drafts only) |
| Claude Connectors marketplace | No public marketplace exists yet |
| npm | Published (all TypeScript servers) |
| PyPI | Published (Security Controls) |

---

## Not Deployed Remotely

| Server | Reason |
|--------|--------|
| OT Security MCP | Not yet deployed to Vercel |
| Sanctions MCP | Not yet published |
| Dutch Law MCP | Database too large (919MB) for Vercel's 250MB limit |
