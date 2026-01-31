# v0.3.1 - Production Readiness

## Production Readiness Improvements

This patch release improves package metadata and confirms production readiness after comprehensive testing and security audits.

### Changed
- ✅ **Fixed Poetry license format** - Updated to SPDX expression (removed deprecated table format)
- ✅ **Upgraded to Beta status** - Changed from Alpha to Beta (Development Status :: 4)
- ✅ **Removed deprecated license classifier** - Following Poetry best practices
- ✅ **Added poetry.lock** - Ensures reproducible builds

### Quality Assurance
- ✅ **104/104 tests passing** - Comprehensive test coverage including:
  - 21 content quality tests
  - 20 data loading tests
  - 10 integration tests
  - 27 security tests
  - 14 smoke tests
- ✅ **Security audit completed** - No credentials, PII, or sensitive data exposed
- ✅ **Build verification** - Clean PyPI distribution (238KB wheel, 279KB source)

### Technical Details
- No functional changes to MCP tools or data
- No breaking changes to API
- Fully backward compatible with 0.3.0

**Full Changelog:** https://github.com/Ansvar-Systems/security-controls-mcp/blob/main/CHANGELOG.md#031---2026-01-31

---

## Installation

```bash
pipx install security-controls-mcp
```

Or upgrade:
```bash
pipx upgrade security-controls-mcp
```

## What's Included

- **1,451 security controls** from SCF 2025.4
- **28 framework mappings** (ISO 27001, NIST CSF, DORA, PCI DSS, SOC 2, CMMC, and more)
- **Bidirectional framework mapping** - map any framework to any other framework
- **Full-text search** across all control descriptions
- **Optional paid standards integration** - import your purchased ISO/NIST standards

## Support

- 📚 **Documentation:** [README.md](https://github.com/Ansvar-Systems/security-controls-mcp/blob/main/README.md)
- 🐛 **Issues:** [GitHub Issues](https://github.com/Ansvar-Systems/security-controls-mcp/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/Ansvar-Systems/security-controls-mcp/discussions)
- 📧 **Email:** hello@ansvar.eu
