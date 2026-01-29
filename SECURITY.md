# Security Policy

## Supported Versions

We release security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| 0.1.x   | :white_check_mark: |

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
   - Only add this server to your Claude Desktop/Code configuration
   - Do not expose the server over a network
   - The server uses stdio communication only (local only)

### Known Safe Operations

The following are **intentionally designed** and safe:
- Reading bundled JSON data files
- In-memory data indexing
- Local stdio communication with MCP clients
- No file writes (read-only operation)
- No network requests
- No subprocess execution
- No dynamic code evaluation

## Security Considerations

### Data Source

This project bundles data from the [Secure Controls Framework (SCF)](https://securecontrolsframework.com/) by ComplianceForge:
- Data is static (bundled at release time)
- Data is read-only (no modifications)
- Data source is publicly available
- Data is licensed under Creative Commons

### Dependencies

Runtime dependencies are minimal:
- `mcp>=0.9.0` (Model Context Protocol SDK)

Development dependencies:
- `pytest`, `pytest-asyncio` (testing only)
- `black`, `ruff` (code quality only)

### Attack Surface

**Minimal attack surface:**
- No network exposure (stdio only)
- No external API calls
- No file system writes
- No user authentication
- No dynamic code execution
- No subprocess spawning

**Potential risks (and mitigations):**
1. **Malicious data files** → Verified checksums, read-only access
2. **Dependency vulnerabilities** → Dependabot monitoring, minimal deps
3. **MCP protocol issues** → Uses official MCP SDK, stdio isolation

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

**Last Updated**: 2026-01-29
**Policy Version**: 1.0
