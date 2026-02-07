# Security Policy

## Supported Versions

We release security updates for the following versions:

| Version | Supported |
| ------- | --------- |
| 0.4.x   | Yes       |
| 0.3.x   | Yes       |
| 0.2.x   | No        |
| 0.1.x   | No        |

## Reporting a Vulnerability

We take the security of security-controls-mcp seriously. If you discover a security vulnerability, please follow these steps:

### 1. Do NOT Open a Public Issue

Please do not report security vulnerabilities through public GitHub issues, discussions, or pull requests.

### 2. Report Privately

Send your report via email to: **hello@ansvar.eu**

Include the following information:
- Type of vulnerability
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the vulnerability (what an attacker could do)

### 3. Response Timeline

- **Initial Response**: Within 48 hours of report
- **Triage**: Within 7 days
- **Fix & Release**: Depends on severity
  - Critical: Within 7 days
  - High: Within 30 days
  - Medium: Within 90 days
  - Low: Next scheduled release

### 4. Disclosure Policy

- You'll receive acknowledgment of your report
- We'll keep you informed about the fix progress
- We'll notify you when the vulnerability is fixed
- We'll publicly disclose the vulnerability after a fix is released (with credit to you if desired)

## Security Best Practices for Users

### Data Privacy

This MCP server:
- **Does NOT collect or transmit** any user data
- **Does NOT make external API calls** (all data is local)
- **Does NOT require authentication** or API keys
- **Operates entirely offline** using bundled JSON data

### Deployment Modes

This server supports two deployment modes with different security profiles:

#### 1. Stdio Mode (Default - Local Only)

**Recommended for:** Claude Desktop, Claude Code, local development

**Security characteristics:**
- ✅ No network exposure (stdio transport only)
- ✅ Process isolation via operating system
- ✅ No authentication needed (local IPC)
- ✅ Minimal file writes (optional user config at `~/.security-controls-mcp/`)

**Usage:**
```bash
# Install with pipx
pipx install security-controls-mcp

# Add to Claude Desktop config
{
  "mcpServers": {
    "security-controls": {
      "command": "scf-mcp"
    }
  }
}
```

#### 2. HTTP Mode (Docker - Remote Access)

**Recommended for:** Ansvar AI platform, internal deployments, CI/CD integrations

**Security characteristics:**
- ⚠️ **Network exposed** (binds to `0.0.0.0:3000` in container)
- ⚠️ **No built-in authentication** (relies on network isolation)
- ⚠️ **Requires security controls:** firewall, VPN, reverse proxy, or private network
- ✅ Runs as non-root user (UID 1001)
- ✅ Alpine-based minimal container
- ✅ Health check endpoint (`/health`)

**Usage:**
```bash
# Run with Docker
docker run -p 3000:3000 security-controls-mcp

# IMPORTANT: Only expose on trusted networks
# Use with reverse proxy (nginx, Caddy) for TLS + auth
```

**Production deployment requirements:**
1. **Network Isolation:** Deploy behind firewall or VPN
2. **TLS Termination:** Use reverse proxy (nginx, Caddy, Traefik)
3. **Authentication:** Implement at reverse proxy level (OAuth, mTLS, API keys)
4. **Monitoring:** Enable container health checks and logging

### Safe Usage

1. **Verify Package Integrity**
   ```bash
   # Clone from official repository only
   git clone https://github.com/Ansvar-Systems/security-controls-mcp.git

   # Verify you're on the main branch
   git branch --show-current

   # Check the latest commit hash matches the official repo
   git log -1 --oneline
   ```

2. **Use Virtual Environments**
   ```bash
   # Always use a virtual environment
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .
   ```

3. **Keep Dependencies Updated**
   ```bash
   # Regularly update dependencies
   pip install --upgrade mcp
   ```

4. **Review Configuration**
   - For stdio mode: Only add to Claude Desktop/Code (local only)
   - For HTTP mode: Deploy behind firewall/VPN with authentication
   - Never expose HTTP mode directly to the public internet without authentication

### Known Safe Operations

The following are **intentionally designed** and safe:

**Both modes:**
- Reading bundled JSON data files (14 MB SCF controls)
- In-memory data indexing and full-text search
- No external API calls (fully offline)
- No subprocess execution
- No dynamic code evaluation

**Stdio mode specific:**
- Local stdio communication only
- Optional config file writes (`~/.security-controls-mcp/config.json`)
- No network exposure

**HTTP mode specific:**
- HTTP/SSE transport for MCP protocol
- Network binding (requires proper deployment security)
- Health check endpoint for monitoring

## Security Considerations

### Data Source

This project bundles data from the [Secure Controls Framework (SCF)](https://securecontrolsframework.com/) by ComplianceForge:
- Data is static (bundled at release time)
- Data is read-only (no modifications)
- Data source is publicly available
- Data is licensed under Creative Commons

### Dependencies

**Stdio mode (minimal):**
- `mcp>=0.9.0` (Model Context Protocol SDK)

**HTTP mode (adds):**
- `uvicorn` (ASGI server)
- `starlette` (web framework)

**Development only:**
- `pytest`, `pytest-asyncio` (testing)
- `black`, `ruff` (code quality)

### Attack Surface

**Stdio mode (minimal attack surface):**
- ✅ No network exposure
- ✅ Process isolation via OS
- ✅ Optional config file writes only
- ⚠️ Trusts local MCP client (Claude Desktop/Code)

**HTTP mode (expanded attack surface):**
- ⚠️ Network exposed (port 3000)
- ⚠️ No built-in authentication
- ⚠️ HTTP headers/cookies accepted
- ✅ No file uploads accepted
- ✅ Read-only data operations
- ✅ Runs as non-root in container

**Common to both modes:**
- ✅ No external API calls
- ✅ No dynamic code execution
- ✅ No subprocess spawning
- ✅ Bundled data only (14 MB SCF controls)

**Potential risks (and mitigations):**
1. **Malicious data files** → SHA256 verification, read-only bundled data
2. **Dependency vulnerabilities** → Dependabot monitoring, minimal dependencies
3. **HTTP mode exposure** → Deploy behind auth, use network isolation
4. **MCP protocol issues** → Uses official MCP SDK (v0.9.0+)

## Security Updates

Security updates are released as follows:

1. **Critical vulnerabilities**: Immediate patch release
2. **High severity**: Patch within 7 days
3. **Medium severity**: Patch within 30 days
4. **Low severity**: Bundled in next minor release

Updates are announced via:
- GitHub Security Advisories
- Release notes on GitHub
- README.md updates

## Acknowledgments

We appreciate the security research community's efforts to improve the security of open source software. Researchers who responsibly disclose vulnerabilities will be acknowledged in:
- Security advisories
- Release notes
- CHANGELOG.md (if desired)

## Contact

For security concerns, contact: **hello@ansvar.eu**

For general issues, use: [GitHub Issues](https://github.com/Ansvar-Systems/security-controls-mcp/issues)

---

**Last Updated**: 2026-02-07
**Policy Version**: 2.0
