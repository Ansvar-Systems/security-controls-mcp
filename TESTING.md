# Testing Guide

## Quick Validation

After installation, verify the MCP server works:

### 1. Local Tests (No Claude Required)

```bash
cd /path/to/security-controls-mcp
source venv/bin/activate

# Basic functionality test
python test_server.py

# Full integration test (all 5 tools)
python test_mcp_integration.py
```

Expected output:
- ✅ All tests passed!
- No errors or tracebacks
- Data loads correctly (1,451 controls, 28 frameworks)

---

## 2. Test in Claude

Once configured in Claude Desktop, try these queries:

### Test 1: Get Control by ID

**Query:** "What does GOV-01 require?"

**Expected Response:**
- Control ID: GOV-01
- Name: Cybersecurity & Data Protection Governance Program
- Domain, description, weight (10/10)
- Framework mappings: NIST CSF, ISO 27001, DORA, NIS2, etc.

---

### Test 2: Search Controls

**Query:** "Search for encryption controls"

**Expected Response:**
- Found 3+ controls
- CRY-05.3: Database Encryption
- CRY-07: Wireless Access Authentication & Encryption
- Should show snippets and mapped frameworks

---

### Test 3: List Frameworks

**Query:** "List available frameworks"

**Expected Response:**
- 28 frameworks total
- NIST SP 800-53 R5: 777 controls
- SOC 2: 412 controls
- PCI DSS v4.0.1: 364 controls
- NIST CSF 2.0: 253 controls
- DORA: 103 controls
- ISO 27001:2022: 51 controls
- etc.

---

### Test 4: Get Framework Controls

**Query:** "What controls do I need for DORA compliance?"

**Expected Response:**
- Total: 103 controls
- Grouped by domain (Governance, Asset Management, Business Continuity, etc.)
- Each control shows SCF ID, name, and DORA article mappings

---

### Test 5: Cross-Framework Mapping

**Query:** "Map ISO 27001 control 5.1 to DORA"

**Expected Response:**
- Found 2 SCF controls
- GOV-01 maps ISO 5.1 → DORA 16.1(a), 16.1(b), 16.1(c), etc.
- GOV-02 also has mappings
- Shows weight/importance for each control

---

### Test 6: Cross-Framework (Full)

**Query:** "Which DORA requirements does ISO 27001 satisfy?"

**Expected Response:**
- 51 SCF controls that have both ISO 27001 and DORA mappings
- Shows source (ISO) and target (DORA) article IDs
- Grouped by domain

---

## Advanced Test Scenarios

### Compliance Gap Analysis (Manual)

**Query 1:** "What controls do I need for ISO 27001?"
**Query 2:** "What controls do I need for DORA?"
**Manual step:** Compare the two lists to find gaps

(Note: `compare_frameworks` tool is planned for v1.1)

---

### Multi-Framework Queries

**Query:** "Show me controls that satisfy both DORA and NIS2"

**Expected:** Agent should call `get_framework_controls` for both, then find intersection

---

### Integration with eu-regulations-mcp

If you have both MCP servers loaded:

**Query:** "What does DORA Article 16 require, and which ISO 27001 controls satisfy it?"

**Expected workflow:**
1. Agent → eu-regulations-mcp: Get DORA Article 16 text
2. Agent → security-controls-mcp: Map ISO 27001 to DORA
3. Agent combines both responses

---

## Error Handling Tests

### Test Invalid Control ID

**Query:** "What does FAKE-999 require?"

**Expected:** "Control FAKE-999 not found. Use search_controls to find controls."

---

### Test Invalid Framework

**Query:** "Get controls for fake_framework"

**Expected:** "Framework 'fake_framework' not found. Available: dora, iso_27001_2022, nist_csf_2.0, ..."

---

### Test Empty Search

**Query:** "Search for controls about xyzabc123nonexistent"

**Expected:** "No controls found matching 'xyzabc123nonexistent'. Try different keywords."

---

## Performance Validation

### Data Loading Speed

```bash
time python -c "from security_controls_mcp.data_loader import SCFData; SCFData()"
```

**Expected:** < 1 second (data files are pre-extracted)

---

### Search Performance

Large searches should still be fast:

```bash
time python -c "
from security_controls_mcp.data_loader import SCFData
data = SCFData()
data.search_controls('security', limit=100)
"
```

**Expected:** < 0.5 seconds

---

## Validation Checklist

Before considering v1 release-ready:

- [ ] All 5 tools work in Claude Desktop
- [ ] Search finds relevant controls (not empty results)
- [ ] Framework counts are correct (no "0 controls" for major frameworks)
- [ ] Cross-framework mapping works (ISO → DORA, NIST → PCI DSS, etc.)
- [ ] Error messages are helpful (invalid IDs, frameworks)
- [ ] No crashes or exceptions during normal use
- [ ] Data loads in < 1 second
- [ ] Works on both macOS and Windows (if applicable)

---

## Reporting Issues

If you find bugs:

1. **What query did you run?**
2. **What was the response?**
3. **What did you expect?**
4. **Which MCP client?** (Claude Desktop, Claude Code, other)

Include logs if available:
- Claude Desktop: Check application logs (location varies)
- Local tests: Copy terminal output

---

## Next Steps After Testing

Once validated:
- [ ] Create GitHub repository
- [ ] Publish to npm/PyPI (if distributing)
- [ ] Add to Smithery MCP registry
- [ ] Share on Reddit, LinkedIn, etc.
- [ ] Plan v1.1 features (gap analysis, better search, etc.)
