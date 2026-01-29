# SCF Security Controls MCP - Quick Start Guide

## What You Have

1. **SCF Repository** (cloned)
   - Location: `/tmp/scf-repo/`
   - Contains: SCF 2025.4 Excel + 64 STRM PDFs
   - Size: 5.3MB Excel, 1,451 controls, 180+ framework mappings

2. **Analysis Complete**
   - ✅ ALL requested frameworks found in Excel (no PDF parsing needed)
   - ✅ Data structure documented
   - ✅ Implementation plan ready

3. **Working Code**
   - `scf-extract-starter.py` - Data extraction script (ready to run)
   - `SCF-MCP-HANDOVER.md` - Full technical specification

## 5-Minute Test Run

### Step 1: Set up environment

```bash
cd /tmp
source scf-venv/bin/activate  # Virtual env already exists from our analysis
```

### Step 2: Run extraction script

```bash
python3 ~/Projects/Ansvar_business_strategy/scf-extract-starter.py \
  /tmp/scf-repo/secure-controls-framework-scf-2025-4.xlsx
```

**Output:**
- `scf-controls.json` (15-20 MB) - Full control database
- `framework-to-scf.json` (2-5 MB) - Reverse index
- `extraction-stats.txt` - Statistics report

**Expected time:** 30-60 seconds

### Step 3: Inspect the data

```bash
# See statistics
cat extraction-stats.txt

# Check file sizes
ls -lh scf-controls.json framework-to-scf.json

# Peek at first control
head -n 50 scf-controls.json
```

### Step 4: Test a query (manual)

```bash
# Find all controls that map to DORA
jq '.controls[] | select(.framework_mappings.dora != null) | {id, name, dora: .framework_mappings.dora}' scf-controls.json | head -n 20

# Cross-reference: DORA 16.1(a) → ISO 27001
# (requires reverse index lookup - this is what MCP will do)
```

## What's Next?

### Option A: Build MCP Server Now (2-3 weeks)

Follow the implementation plan in `SCF-MCP-HANDOVER.md`:
1. Week 1-2: Data extraction ✅ (you just did this!)
2. Week 3: MCP server implementation
3. Week 4: Testing & documentation
4. Week 5: Launch

**Start here:** Create `security-controls-mcp/` repo and set up MCP Python package

### Option B: Explore the Data First

Use the extracted JSON to test queries manually:

```bash
# Count DORA controls
jq '.controls[] | select(.framework_mappings.dora != null)' scf-controls.json | jq -s length

# Find high-weight controls (>= 8)
jq '.controls[] | select(.weight >= 8) | {id, name, weight}' scf-controls.json

# Get all UK Cyber Essentials controls
jq '.controls[] | select(.framework_mappings.uk_cyber_essentials != null)' scf-controls.json
```

### Option C: Test Cross-References

The reverse index enables framework → framework queries:

```bash
# Example: Find SCF controls for DORA Article 16.1(a)
jq '.dora["16.1(a)"]' framework-to-scf.json

# Then look up those SCF controls to see their ISO 27001 mappings
# (This is the core MCP query pattern)
```

## Key Insights from Analysis

### 1. NO PDF PARSING NEEDED (for major frameworks)

The SCF Excel has built-in mappings for:
- NIST CSF 2.0 (253 controls)
- NIST 800-53 R5 (777 controls)
- ISO 27001:2022 (51 controls)
- PCI DSS 4.0.1 (364 controls)
- CMMC 2.0 L2 (198 controls)
- SOC 2 (412 controls)
- DORA (103 controls)
- NIS2 (68 controls)
- GDPR (42 controls)
- NCSC CAF 4.0 (67 controls)
- UK Cyber Essentials (26 controls)
- CIS CSC 8.1 (234 controls)

**ALL frameworks SwagVonYolo requested are in the Excel.**

### 2. Data Format

Framework mappings are **newline-separated lists**:

```json
{
  "id": "GOV-01",
  "framework_mappings": {
    "dora": ["16.1(a)", "16.1(b)", "16.1(c)", "5.1", "9.4"],
    "iso_27001_2022": ["4.4", "5.1", "5.1(a)", "5.1(b)"],
    "uk_cyber_essentials": null
  }
}
```

### 3. Reverse Index Enables Cross-Framework Queries

```json
{
  "dora": {
    "16.1(a)": ["GOV-01", "GOV-02", "RSK-01"],
    "5.1": ["GOV-01", "IAC-01"]
  }
}
```

This is how you answer: "What ISO 27001 controls map to DORA 16.1(a)?"
1. Look up DORA 16.1(a) in reverse index → [GOV-01, GOV-02]
2. Look up those controls' ISO 27001 mappings → [4.4, 5.1, etc.]

## Files Overview

```
Ansvar_business_strategy/
├── SCF-MCP-HANDOVER.md          # Full technical spec (read this!)
├── SCF-QUICKSTART.md            # This file
└── scf-extract-starter.py       # Extraction script

/tmp/scf-repo/                   # SCF repository (cloned)
├── secure-controls-framework-scf-2025-4.xlsx
└── Set Theory Relationship Mapping (STRM)/
    └── ... (64 PDFs - only needed for niche frameworks)

/tmp/ (after running extraction)
├── scf-controls.json            # Main database
├── framework-to-scf.json        # Reverse index
└── extraction-stats.txt         # Statistics
```

## MCP Server Query Examples

Once you build the MCP server, users will be able to:

### Query 1: Control Lookup
```
User: "What does GOV-01 require?"

MCP Response:
Control: GOV-01 - Cybersecurity & Data Protection Governance Program
Description: Mechanisms exist to facilitate the implementation of
  cybersecurity and data protection controls...
Weight: 8/10
PPTDF: People, Process

Mapped Frameworks:
  - NIST CSF 2.0: GV, GV.RM-01, GV.RM-03, GV.RR-01
  - ISO 27001:2022: 4.4, 5.1, 5.1(a), 5.1(b)
  - DORA: 16.1(a), 16.1(b), 16.1(c), 5.1, 9.4
  - PCI DSS 4.0.1: 12.4, A3.1.2
```

### Query 2: Framework Coverage
```
User: "What controls do I need for DORA compliance?"

MCP Response:
103 SCF controls map to DORA:

Governance (GOV):
  - GOV-01: Cybersecurity & Data Protection Governance Program
  - GOV-02: Publishing Cybersecurity Documentation
  ...

Risk Management (RSK):
  - RSK-01: Risk Management Program
  - RSK-02: Risk Identification
  ...
```

### Query 3: Cross-Framework Mapping
```
User: "What ISO 27001 controls cover DORA Article 16.1(a)?"

MCP Response:
DORA Article 16.1(a) maps to these SCF controls:
  - GOV-01, GOV-02, RSK-01

Those SCF controls map to ISO 27001:
  - 4.4 (Context of the organization)
  - 5.1 (Leadership and commitment)
  - 5.2 (Policy)
  - 6.1.1 (Actions to address risks)
```

### Query 4: Gap Analysis
```
User: "I'm certified for ISO 27001. What additional controls does DORA require?"

MCP Response:
ISO 27001 covers 51 SCF controls.
DORA requires 103 SCF controls.

Gap: 52 SCF controls not covered by ISO 27001:
  - TRN-01: Security Awareness Training
  - TRN-02: Role-Based Security Training
  - THR-01: Threat Intelligence Program
  ...
```

## Ready to Build?

**Next step:** Read `SCF-MCP-HANDOVER.md` for the full implementation plan.

**Quick wins:**
1. ✅ Data extraction (you can do this in 5 minutes)
2. ✅ Test queries manually with `jq`
3. → Build MCP server (2-3 weeks, detailed plan in handover doc)

## Questions?

Check the handover document for:
- Detailed data model
- MCP server architecture
- Implementation timeline
- Testing strategy
- Launch checklist

All the technical decisions are documented there.
