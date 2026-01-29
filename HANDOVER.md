# Security Controls MCP - Development Handover

**Date:** 2026-01-29
**Status:** v0.1.0 - Ready for Real-World Testing
**Developer:** Claude Sonnet 4.5
**For:** Jeffrey von Rotz / Ansvar Systems

---

## Executive Summary

Built a fully functional MCP server that provides AI agents access to 1,451 security controls across 16 compliance frameworks (ISO 27001, NIST CSF, DORA, PCI DSS, etc.). The server enables cross-framework mapping, compliance queries, and control lookups.

**All local tests pass ✅** — ready for Claude Desktop/Code integration testing.

---

## What Was Built

### Core Functionality (5 MCP Tools)

1. **`get_control`** - Get detailed information about a specific SCF control
   - Input: SCF control ID (e.g., "GOV-01")
   - Output: Full control details + framework mappings
   - Status: ✅ Working

2. **`search_controls`** - Full-text search across control descriptions
   - Input: Search query, optional framework filter, limit
   - Output: Relevant controls with snippets
   - Status: ✅ Working (case-insensitive)

3. **`list_frameworks`** - List all available security frameworks
   - Input: None (optional: detailed flag)
   - Output: 16 frameworks with control counts
   - Status: ✅ Working

4. **`get_framework_controls`** - Get all controls for a specific framework
   - Input: Framework key (e.g., "dora", "iso_27001_2022")
   - Output: All SCF controls that map to that framework
   - Status: ✅ Working

5. **`map_frameworks`** - Cross-reference controls between two frameworks
   - Input: Source framework, target framework, optional source control ID
   - Output: SCF controls showing source → target mappings
   - Status: ✅ Working

### Data Coverage

- **1,451 SCF controls** (Secure Controls Framework v2025.4)
- **16 frameworks mapped:**
  - NIST SP 800-53 R5: 777 controls
  - SOC 2 (TSC): 412 controls
  - PCI DSS v4.0.1: 364 controls
  - FedRAMP R5 Moderate: 343 controls
  - ISO 27002:2022: 316 controls
  - NIST CSF 2.0: 253 controls
  - CIS CSC v8.1: 234 controls
  - CMMC 2.0 Level 2: 198 controls
  - HIPAA Security Rule: 136 controls
  - DORA: 103 controls
  - NIS2: 68 controls
  - ISO 27001:2022: 51 controls
  - GDPR: 42 controls
  - UK Cyber Essentials: 26 controls
  - CMMC 2.0 Level 1: 52 controls
  - NCSC CAF 4.0: 67 controls

### Framework Keys (Normalized)

**Important:** Framework keys use dots in version numbers (matching source data):
- `nist_csf_2.0` (not `nist_csf_2_0`)
- `pci_dss_4.0.1` (not `pci_dss_4_0_1`)
- `cis_csc_8.1` (not `cis_csc_8_1`)
- `cmmc_2.0_level_1` and `cmmc_2.0_level_2`
- `ncsc_caf_4.0`

All other framework keys use underscores: `iso_27001_2022`, `dora`, `nis2`, `gdpr`, etc.

---

## Architecture

### Technology Stack

- **Language:** Python 3.10+
- **MCP SDK:** `mcp>=0.9.0`
- **Data Format:** JSON (pre-extracted from SCF Excel)
- **Package Manager:** pip
- **License:** Apache 2.0

### File Structure

```
security-controls-mcp/
├── src/
│   └── security_controls_mcp/
│       ├── __init__.py
│       ├── __main__.py          # Entry point
│       ├── server.py            # MCP server & tool handlers
│       ├── data_loader.py       # Data loading & query logic
│       └── data/
│           ├── scf-controls.json         # 1.5 MB - main database
│           └── framework-to-scf.json     # 0.2 MB - reverse index
│
├── tests/
│   ├── test_server.py           # Basic functionality tests
│   └── test_mcp_integration.py  # Full MCP tool integration tests
│
├── docs/
│   ├── README.md                # Overview
│   ├── INSTALL.md               # Installation guide
│   ├── TESTING.md               # Test queries & validation
│   └── HANDOVER.md              # This file
│
├── planning/ (from initial investigation)
│   ├── SCF-MCP-HANDOVER.md      # Original technical spec
│   ├── SCF-QUICKSTART.md        # Quick start guide
│   ├── scf-extract-starter.py   # Excel to JSON extractor
│   └── scf-query-tester.py      # Query pattern tester
│
├── pyproject.toml               # Package configuration
├── LICENSE                      # Apache 2.0
├── .gitignore                   # Python, venv, IDE files
└── venv/                        # Virtual environment (not in git)
```

### Design Decisions

#### 1. **JSON Instead of SQLite**
- **Why:** Simpler deployment, no database setup, fast loading
- **Trade-off:** 1.7 MB in memory (acceptable for MCP use case)
- **Result:** <1 second load time

#### 2. **Pre-Extracted Data**
- **Why:** Avoid parsing 5.3 MB Excel file on every startup
- **Trade-off:** Manual data update process (run extraction script)
- **Result:** Fast startup, simpler dependencies

#### 3. **Simple String Search (v1)**
- **Why:** Get to market faster, no ML dependencies
- **Trade-off:** Less sophisticated than vector/embeddings search
- **Future:** Can add BM25 or embeddings in v1.1

#### 4. **Reverse Index for Cross-Framework Queries**
- **Why:** Enables fast framework → SCF → framework lookups
- **Trade-off:** Additional 200 KB in memory
- **Result:** Instant cross-framework mapping

#### 5. **Match eu-regulations-mcp Patterns**
- **Why:** Consistency across Ansvar MCP servers
- **Result:** Agents can use both servers without learning different patterns

---

## Testing Results

### Local Tests: ✅ All Pass

**test_server.py:**
```
✓ Loaded 1451 controls
✓ Loaded 16 frameworks
✓ get_control('GOV-01') - Returns full details
✓ search_controls('encryption') - Finds 3 controls
✓ get_framework_controls('dora') - Returns 103 controls
✓ map_frameworks(iso_27001 → dora) - Returns mappings
```

**test_mcp_integration.py:**
```
10/10 tests passed:
✓ get_control (valid ID)
✓ get_control (invalid ID - error handling)
✓ search_controls (basic query)
✓ search_controls (with framework filter)
✓ list_frameworks
✓ get_framework_controls (valid)
✓ get_framework_controls (invalid - error handling)
✓ map_frameworks (with source control filter)
✓ map_frameworks (all mappings)
✓ map_frameworks (invalid source - error handling)
```

### Claude Desktop: ⚠️ Needs Testing

**Cannot test from within this Claude Code session.** Requires:
1. Configure `claude_desktop_config.json`
2. Restart Claude Desktop
3. Verify tools are available
4. Run test queries from TESTING.md

### Claude Code: ⚠️ Needs Testing in New Session

**Cannot test in current session.** Requires:
1. Exit current session
2. Start new `claude` session
3. Verify MCP server loads
4. Run test queries

---

## Known Issues & Limitations

### Current Limitations

1. **Search Quality (v1)**
   - Simple substring matching (case-insensitive)
   - No ranking/relevance scoring beyond exact matches
   - No synonym handling (search "crypto" won't find "cryptographic")
   - **Future:** Add BM25 or vector search in v1.1

2. **Framework Keys Use Mixed Notation**
   - Some have dots: `nist_csf_2.0`, `pci_dss_4.0.1`
   - Others use underscores: `iso_27001_2022`
   - **Why:** Matches source data exactly
   - **Impact:** Users need to know correct key format
   - **Mitigation:** Error messages show available keys

3. **No Gap Analysis Tool (v1)**
   - Agents must call `get_framework_controls` twice and compare manually
   - **Deferred to v1.1:** `compare_frameworks` tool for gap analysis

4. **No Framework-Native ID Lookup (v1)**
   - Must know SCF ID (e.g., "GOV-01") or search first
   - Can't query directly by ISO 27001 A.5.15 and get SCF controls
   - **Workaround:** Use `map_frameworks` or `search_controls`
   - **Deferred to v1.1:** `lookup_control` tool

5. **Only 16 Frameworks**
   - SCF has 180+ frameworks, but extraction script only configured for 16
   - **Why:** Top frameworks requested by users (DORA, ISO, NIST, PCI, etc.)
   - **Future:** Add more frameworks on demand

### Fixed Issues

✅ **Framework key mismatch** - Fixed in commit 703c098
- Problem: Metadata used underscores, data had dots
- Fix: Updated framework names dict to match source data

✅ **Case-sensitive search** - Fixed in commit 703c098
- Problem: Search for "encryption" didn't find "Encryption"
- Fix: Made search case-insensitive

---

## Integration with eu-regulations-mcp

### Designed for Cross-MCP Workflows

**Example: DORA Compliance Query**

```
User: "What does DORA Article 16 require, and which ISO 27001 controls satisfy it?"

Agent workflow:
1. eu-regulations-mcp.get_article(regulation="DORA", article="16")
   → Returns: Article 16 text (ICT risk management framework)

2. security-controls-mcp.map_frameworks(
     source_framework="iso_27001_2022",
     target_framework="dora"
   )
   → Returns: GOV-01, GOV-02, RSK-01 map ISO 5.1 → DORA 16.1(a), etc.

3. Agent combines both responses for user
```

### Interface Consistency

Both MCPs use the same patterns:
- Simple, focused tools (get, search, list, map)
- Structured JSON responses
- Helpful error messages with suggestions
- Token-conscious design (snippets for search, full text on demand)

---

## Next Steps

### Immediate (Before v1.0 Release)

1. **Test in Claude Desktop** ⚠️ Critical
   - Configure MCP server in `claude_desktop_config.json`
   - Restart Claude Desktop
   - Verify all 5 tools work
   - Run test queries from TESTING.md
   - Document any issues found

2. **Test in Fresh Claude Code Session** ⚠️ Critical
   - Exit current session
   - Start new session
   - Verify MCP server loads
   - Run test queries

3. **Fix Any Issues Found**
   - If tools don't load: check config paths, permissions
   - If queries fail: debug with local tests first
   - If responses are wrong: check data extraction

### v1.0 Release Checklist

- [ ] All tests pass in Claude Desktop
- [ ] All tests pass in Claude Code (new session)
- [ ] No crashes or exceptions during normal use
- [ ] Error messages are helpful
- [ ] Documentation is accurate (INSTALL.md, TESTING.md)
- [ ] Create GitHub repository
- [ ] Add topics/tags for discoverability
- [ ] Create release notes

### v1.1 Enhancement Ideas

**High Priority:**
- [ ] `compare_frameworks` - Gap analysis between two frameworks
- [ ] `lookup_control` - Find SCF controls by framework-native ID
- [ ] Better search - BM25 scoring or basic relevance ranking
- [ ] Token estimates in responses (like eu-regulations-mcp)

**Medium Priority:**
- [ ] Add more frameworks (user-driven: request → add)
- [ ] Include Assessment Objectives (testing criteria for controls)
- [ ] Response formatting improvements (better grouping, tables)
- [ ] Performance optimization for large queries

**Low Priority:**
- [ ] Vector search with embeddings
- [ ] Control relationships/dependencies
- [ ] STRM PDF parsing for niche frameworks
- [ ] Web UI for browsing controls

---

## File Locations

### Critical Files

**Production code:**
- `/Users/jeffreyvonrotz/Projects/security-controls-mcp/src/security_controls_mcp/`

**Data files (1.7 MB total):**
- `/Users/jeffreyvonrotz/Projects/security-controls-mcp/src/security_controls_mcp/data/scf-controls.json`
- `/Users/jeffreyvonrotz/Projects/security-controls-mcp/src/security_controls_mcp/data/framework-to-scf.json`

**Virtual environment:**
- `/Users/jeffreyvonrotz/Projects/security-controls-mcp/venv/`
- Python path: `/Users/jeffreyvonrotz/Projects/security-controls-mcp/venv/bin/python`

**Source data (for updates):**
- `/tmp/scf-repo/secure-controls-framework-scf-2025-4.xlsx` (5.3 MB)
- Extraction script: `scf-extract-starter.py`

### Git Repository

**Local:** `/Users/jeffreyvonrotz/Projects/security-controls-mcp/`
**Commits:** 5 total (planning → implementation → bugfixes → docs)
**Status:** Clean working tree, ready to push

**Remote:** Not yet created (pending testing & v1.0 release)

---

## Configuration Reference

### Claude Desktop Config

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "security-controls": {
      "command": "/Users/jeffreyvonrotz/Projects/security-controls-mcp/venv/bin/python",
      "args": ["-m", "security_controls_mcp"]
    }
  }
}
```

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "security-controls": {
      "command": "C:\\Users\\YourName\\Projects\\security-controls-mcp\\venv\\Scripts\\python.exe",
      "args": ["-m", "security_controls_mcp"]
    }
  }
}
```

---

## Troubleshooting Guide

### "Module not found" Error

**Cause:** Not using the venv Python
**Fix:**
```bash
cd /Users/jeffreyvonrotz/Projects/security-controls-mcp
source venv/bin/activate
which python  # Verify path
```

### "No such file or directory: python"

**Cause:** Wrong path in Claude config
**Fix:** Use absolute path from `which python` (inside venv)

### Framework Shows "0 controls"

**Cause:** Framework key doesn't match data
**Fix:** Use exact keys from data (dots in versions: `nist_csf_2.0`)

### Search Returns Empty

**Cause:** Query doesn't match any control names/descriptions
**Fix:** Try simpler terms (e.g., "encrypt" instead of "encryption key management")

### Claude Desktop Doesn't Show MCP Server

**Checklist:**
1. Config file in correct location? (macOS vs Windows)
2. JSON syntax valid? (no trailing commas, proper quotes)
3. Absolute path to venv Python?
4. Restarted Claude Desktop? (full quit and reopen)
5. Permissions correct? (read/execute on venv/bin/python)

---

## Data Update Process

When SCF releases new version (currently using 2025.4):

1. **Download new SCF Excel:**
   ```bash
   cd /tmp/scf-repo
   # Download new file from https://securecontrolsframework.com/scf-download/
   ```

2. **Run extraction:**
   ```bash
   cd /tmp
   source scf-venv/bin/activate
   python3 /path/to/scf-extract-starter.py /tmp/scf-repo/secure-controls-framework-scf-NEW.xlsx
   ```

3. **Copy to project:**
   ```bash
   cp scf-controls.json framework-to-scf.json \
      /Users/jeffreyvonrotz/Projects/security-controls-mcp/src/security_controls_mcp/data/
   ```

4. **Test:**
   ```bash
   cd /Users/jeffreyvonrotz/Projects/security-controls-mcp
   source venv/bin/activate
   python test_server.py
   ```

5. **Update version in pyproject.toml and commit**

---

## Contact & Support

**Developer:** Claude Sonnet 4.5
**Organization:** Ansvar Systems (https://ansvar.eu)
**Location:** Stockholm, Sweden
**Date:** 2026-01-29

**For issues:**
- Local testing: Check TESTING.md troubleshooting section
- Integration issues: See INSTALL.md troubleshooting
- Bugs: Create GitHub issue (once repo is public)

---

## Appendix: Example Queries

### Query 1: Get Control Details

```
User: "What does GOV-01 require?"

Response:
GOV-01: Cybersecurity & Data Protection Governance Program

Domain: Cybersecurity & Data Protection Governance
Description: Mechanisms exist to facilitate the implementation of
cybersecurity and data protection governance controls.

Weight: 10/10
PPTDF: Process
Validation Cadence: Annual

Framework Mappings:
- NIST CSF 2.0: GV, GV.RM-01, GV.RM-03, ...
- ISO 27001:2022: 4.4, 5.1, 5.1(a), 5.1(b), ...
- DORA: 16.1(a), 16.1(b), 16.1(c), ...
- NIS2: 21.1, 21.2, 21.2(a), ...
```

### Query 2: Cross-Framework Mapping

```
User: "Map ISO 27001 control 5.1 to DORA"

Response:
Mapping: ISO/IEC 27001:2022 → DORA
Filtered to source control: 5.1
Found 2 SCF controls

GOV-01: Cybersecurity & Data Protection Governance Program (weight: 10)
- Source (iso_27001_2022): 4.4, 5.1, 5.1(a), 5.1(b), ...
- Target (dora): 16.1(a), 16.1(b), 16.1(c), 16.1(d), ...

GOV-02: Publishing Cybersecurity Documentation (weight: 5)
- Source (iso_27001_2022): 5.1
- Target (dora): No direct mapping
```

### Query 3: Framework Coverage

```
User: "What controls do I need for DORA compliance?"

Response:
Digital Operational Resilience Act (DORA)
Total Controls: 103

Governance (GOV):
- GOV-01: Cybersecurity & Data Protection Governance Program
  Maps to: 16.1(a), 16.1(b), 16.1(c), 16.1(d), 16.1(e), ...
- GOV-02: Publishing Cybersecurity Documentation
  Maps to: 16.1(a)
...

Asset Management:
- AST-01.1: Asset-Service Dependencies
  Maps to: 8.5
...
```

---

**END OF HANDOVER**

*All local tests pass. Ready for Claude Desktop/Code integration testing.*
