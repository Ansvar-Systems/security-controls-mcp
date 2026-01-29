# SCF Security Controls MCP - Technical Handover

**Date:** 2026-01-29
**Subject:** security-controls-mcp implementation plan based on SCF analysis
**Status:** Ready for implementation

---

## Executive Summary

Investigation of the Secure Controls Framework (SCF) confirms that **PDF parsing is unnecessary for major frameworks**. The SCF Excel file (`secure-controls-framework-scf-2025-4.xlsx`) contains **1,451 controls with built-in mappings to 180+ frameworks**. All frameworks requested by SwagVonYolo (Reddit r/cybersecurity commenter) are already mapped in the Excel.

**Key Finding:** Use the SCF Excel as your primary data source. STRM PDFs are only needed for newer/niche frameworks not in the Excel.

---

## SCF Repository Structure

**Location:** `/tmp/scf-repo/`
**Git URL:** https://github.com/securecontrolsframework/securecontrolsframework
**Version:** SCF 2025.4 (released Dec 29, 2025)
**License:** Creative Commons

### Key Files

```
/tmp/scf-repo/
├── secure-controls-framework-scf-2025-4.xlsx    # Main database (5.3M)
│   ├── SCF 2025.4                               # 1,451 controls, 379 columns
│   ├── Authoritative Sources                    # Framework metadata
│   ├── Assessment Objectives 2025.4             # Testing criteria
│   ├── Evidence Request List 2025.4             # Audit evidence
│   ├── Risk Catalog                             # Risk mappings
│   └── Threat Catalog                           # Threat mappings
│
├── Set Theory Relationship Mapping (STRM)/      # 64 framework PDFs
│   ├── scf-strm-emea-eu-dora.pdf
│   ├── scf-strm-emea-eu-nis2.pdf
│   ├── scf-strm-general-iso-27001-2022.pdf
│   ├── scf-strm-general-nist-csf-2-0.pdf
│   └── ... (60 more)
│
└── SCF 2025.4 Errata.txt                        # Version notes
```

---

## Excel Data Structure

### SCF 2025.4 Sheet

**Total Rows:** 1,451 controls
**Total Columns:** 379

#### Core Columns

| Column | Name | Description |
|--------|------|-------------|
| 1 | SCF Domain | Control category (GOV, IAC, CFG, etc.) |
| 2 | SCF Control | Control name |
| 3 | SCF # | Control ID (e.g., GOV-01, IAC-02) |
| 4 | Control Description | Full text description |
| 5 | Conformity Validation Cadence | Testing frequency |
| 13 | Relative Control Weighting | Importance (0-10 scale) |
| 14 | PPTDF Applicability | People/Process/Tech/Data/Facility |

#### Framework Mapping Columns (180+ frameworks)

**Format:** Newline-separated list of framework control IDs
**Example:** `GOV-01` → ISO 27001:2022 → `"4.4\n5.1\n5.1(a)\n5.1(b)"...`

##### Key Framework Columns & Statistics

| Framework | Column | SCF Controls Mapped |
|-----------|--------|---------------------|
| **NIST CSF 2.0** | 93 | 253 controls |
| **NIST 800-53 R5** | 69 | 777 controls |
| **ISO 27001:2022** | 48 | 51 controls |
| **ISO 27002:2022** | 49 | (derived from 27001) |
| **CIS CSC 8.1** | 28 | 234 controls |
| **PCI DSS 4.0.1** | 96 | 364 controls |
| **CMMC 2.0 Level 2** | 119 | 198 controls |
| **SOC 2 (TSC)** | 25 | 412 controls |
| **DORA** | 198 | 103 controls |
| **NIS2** | 200 | 68 controls |
| **GDPR** | 199 | 42 controls |
| **NCSC CAF 4.0** | 238 | 67 controls |
| **UK Cyber Essentials** | 240 | 26 controls |

**Coverage:** ALL frameworks requested by SwagVonYolo are in the Excel ✓

---

## Data Model Design

### Primary Structure

```json
{
  "scf_controls": [
    {
      "id": "GOV-01",
      "domain": "Governance (GOV)",
      "name": "Cybersecurity & Data Protection Governance Program",
      "description": "Mechanisms exist to facilitate...",
      "weight": 8,
      "pptdf": "People, Process",
      "validation_cadence": "Annual",
      "framework_mappings": {
        "nist_csf_2.0": ["GV", "GV.RM-01", "GV.RM-03", "GV.RR-01"],
        "iso_27001_2022": ["4.4", "5.1", "5.1(a)", "5.1(b)"],
        "pci_dss_4.0.1": ["12.4", "A3.1.2"],
        "dora": ["16.1(a)", "16.1(b)", "16.1(c)"],
        "ncsc_caf_4.0": null,
        "uk_cyber_essentials": null,
        "cmmc_2.0_l2": null
      }
    }
  ],
  "frameworks": {
    "nist_csf_2.0": {
      "name": "NIST Cybersecurity Framework 2.0",
      "version": "2.0",
      "geography": "US Federal",
      "controls_mapped": 253,
      "url": "https://www.nist.gov/cyberframework"
    }
  }
}
```

### Reverse Index (for cross-framework queries)

```json
{
  "framework_to_scf": {
    "dora": {
      "16.1(a)": ["GOV-01", "GOV-02", "RSK-01"],
      "5.1": ["GOV-01", "IAC-01"]
    },
    "iso_27001_2022": {
      "4.4": ["GOV-01", "GOV-01.1"],
      "5.1": ["GOV-01", "GOV-02"]
    }
  }
}
```

---

## Query Patterns

### 1. Lookup SCF Control

```
User: "What does GOV-01 require?"
Response:
- Control ID & name
- Description
- Weight, PPTDF, validation cadence
- Mapped frameworks (NIST CSF, ISO 27001, DORA, etc.)
```

### 2. Cross-Framework Mapping

```
User: "What ISO 27001 controls map to DORA Article 16.1(a)?"
Process:
1. Find SCF controls that map to DORA 16.1(a) → [GOV-01, GOV-02]
2. Look up ISO 27001 mappings for those SCF controls → [4.4, 5.1, 6.1.1]
3. Return cross-reference
```

### 3. Compliance Query

```
User: "What controls do I need for UK Cyber Essentials?"
Response:
- 26 SCF controls that map to UK Cyber Essentials
- Grouped by Cyber Essentials requirement (1-5)
- Show SCF control details + implementation guidance
```

### 4. Gap Analysis

```
User: "I have ISO 27001. What else do I need for DORA?"
Process:
1. Get SCF controls for ISO 27001 → 51 controls
2. Get SCF controls for DORA → 103 controls
3. Find DORA controls NOT covered by ISO 27001 → gap list
4. Return gap controls with descriptions
```

---

## Implementation Plan

### Phase 1: Data Extraction (Week 1-2)

**Task:** Parse SCF Excel and build JSON database

**Code Approach:**
```python
import openpyxl
import json

wb = openpyxl.load_workbook('secure-controls-framework-scf-2025-4.xlsx', read_only=True)
ws = wb['SCF 2025.4']

# Get headers
headers = [cell.value for cell in ws[1]]

# Map framework columns
framework_map = {
    'nist_csf_2.0': headers.index('NIST\nCSF\n2.0'),
    'iso_27001_2022': headers.index('ISO\n27001\n2022'),
    'pci_dss_4.0.1': headers.index('PCI DSS\n4.0.1'),
    # ... all 180 frameworks
}

# Extract controls
controls = []
for row in ws.iter_rows(min_row=2, values_only=True):
    control = {
        'id': row[headers.index('SCF #')],
        'domain': row[headers.index('SCF Domain')],
        'name': row[headers.index('SCF Control')],
        'description': row[headers.index('Secure Controls Framework (SCF)\nControl Description')],
        'weight': row[headers.index('Relative Control Weighting')],
        'pptdf': row[headers.index('PPTDF\nApplicability')],
        'framework_mappings': {}
    }

    # Extract framework mappings
    for fw_key, fw_idx in framework_map.items():
        mapping = row[fw_idx]
        if mapping and mapping != 'None':
            # Split newline-separated values
            control['framework_mappings'][fw_key] = mapping.split('\n')
        else:
            control['framework_mappings'][fw_key] = None

    controls.append(control)

# Save to JSON
with open('scf-controls.json', 'w') as f:
    json.dump(controls, f, indent=2)
```

**Deliverable:** `scf-controls.json` (estimated 15-20MB)

### Phase 2: Reverse Index (Week 2)

**Task:** Build framework → SCF lookup table

```python
framework_to_scf = {}

for control in controls:
    for fw_key, fw_controls in control['framework_mappings'].items():
        if fw_controls:
            if fw_key not in framework_to_scf:
                framework_to_scf[fw_key] = {}

            for fw_control in fw_controls:
                if fw_control not in framework_to_scf[fw_key]:
                    framework_to_scf[fw_key][fw_control] = []
                framework_to_scf[fw_key][fw_control].append(control['id'])

# Save reverse index
with open('framework-to-scf.json', 'w') as f:
    json.dump(framework_to_scf, f, indent=2)
```

**Deliverable:** `framework-to-scf.json` (cross-reference index)

### Phase 3: MCP Server (Week 3-4)

**Task:** Build Python MCP server with query tools

**Tools to implement:**

1. `query_scf_control`
   - Input: SCF control ID (e.g., "GOV-01")
   - Output: Control details + framework mappings

2. `query_framework_controls`
   - Input: Framework key (e.g., "dora")
   - Output: All SCF controls that map to that framework

3. `cross_reference_frameworks`
   - Input: Source framework + control, Target framework
   - Output: Mapped controls in target framework

4. `gap_analysis`
   - Input: Baseline framework, Target framework
   - Output: Controls in target NOT covered by baseline

5. `search_controls`
   - Input: Text query (description search)
   - Output: Relevant SCF controls

**MCP Server Structure:**
```
security-controls-mcp/
├── pyproject.toml
├── README.md
├── src/
│   └── security_controls_mcp/
│       ├── __init__.py
│       ├── server.py              # MCP server entry point
│       ├── data/
│       │   ├── scf-controls.json
│       │   └── framework-to-scf.json
│       └── tools/
│           ├── query.py           # Query implementations
│           └── search.py          # Text search
└── tests/
    └── test_queries.py
```

### Phase 4: Testing & Documentation (Week 4-5)

**Tasks:**
- Test all query patterns
- Write usage examples
- Create README with sample queries
- Document framework coverage

**Test Cases:**
- Query GOV-01 → verify DORA, ISO 27001, NIST CSF mappings
- Cross-reference DORA 16.1(a) → ISO 27001 controls
- Gap analysis: ISO 27001 vs DORA
- Search "encryption" → find CRY-* controls
- Query UK Cyber Essentials → 26 controls returned

### Phase 5: Launch (Week 5)

**Launch Checklist:**
- [ ] Publish to GitHub
- [ ] Submit to Smithery MCP registry
- [ ] Create README with installation instructions
- [ ] Add to awesome-mcp-servers list
- [ ] LinkedIn announcement post
- [ ] Reddit r/ClaudeAI post

---

## Technical Decisions

### ✅ Use SCF Excel as Primary Source

**Rationale:**
- 180+ frameworks already mapped
- Covers all requested frameworks
- Structured data (no PDF parsing needed)
- Maintained by ComplianceForge

**Alternative (rejected):** Parse STRM PDFs individually

### ✅ JSON Database (not SQLite)

**Rationale:**
- Simpler deployment (no DB setup)
- Fast loading for MCP context
- Easy to version control
- 15-20MB file size is manageable

**Alternative (considered):** SQLite for complex queries, but JSON sufficient for MCP use case

### ✅ Build Reverse Index

**Rationale:**
- Enables bidirectional queries
- Critical for cross-framework mapping
- One-time build cost, fast lookups

### ⚠️ STRM PDFs: Optional Enhancement

**Use Case:** If user requests niche framework not in Excel (e.g., Saudi Arabia OTCC-1)

**Implementation:**
```python
import pdfplumber

def parse_strm_pdf(filepath):
    mappings = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table[1:]:  # skip header
                    mappings.append({
                        "article": row[0],
                        "scf_id": row[4],  # SCF # column
                        "strength": row[6]  # Strength of Relationship
                    })
    return mappings
```

**Priority:** Low (implement only if users request unmapped frameworks)

---

## Cross-Promotion Strategy

### Link with EU Regulations MCP

**Scenario:** User asking about DORA compliance

```
User (via eu-regulations-mcp): "What does DORA Article 16 require?"
Response: "Article 16 covers ICT risk management framework.
For implementation guidance, use security-controls-mcp to see
mapped controls (GOV-01, RSK-01, etc.)"
```

**Scenario:** User asking about controls

```
User (via security-controls-mcp): "What controls do I need for DORA?"
Response: "103 SCF controls map to DORA. For the actual regulatory
text, use eu-regulations-mcp to read DORA Articles 5, 6, 9, 16..."
```

### Shared Data Files

**Option:** Create shared `control-mappings.json` that both MCPs reference:

```json
{
  "dora_article_16.1a": {
    "scf_controls": ["GOV-01", "GOV-02"],
    "iso_27001": ["4.4", "5.1"],
    "nist_csf": ["GV.RM-01", "GV.SC-01"]
  }
}
```

---

## Next Steps

### Immediate Actions

1. **Extract SCF Excel → JSON** (1-2 days)
   - Run extraction script
   - Validate 1,451 controls loaded
   - Verify framework mappings for DORA, ISO 27001, NIST CSF

2. **Build reverse index** (1 day)
   - Create framework → SCF lookup
   - Test cross-references

3. **Implement MCP server** (3-5 days)
   - Set up Python package structure
   - Implement 5 core tools
   - Write tests

4. **Documentation** (2 days)
   - README with examples
   - Framework coverage table
   - Installation guide

5. **Launch** (1 day)
   - Publish to GitHub
   - Submit to Smithery
   - Announce on LinkedIn, Reddit

### Timeline Estimate

**Total: 2-3 weeks for MVP**

| Week | Focus |
|------|-------|
| Week 1-2 | Data extraction, reverse index, validation |
| Week 3 | MCP server implementation, core tools |
| Week 4 | Testing, documentation, examples |
| Week 5 | Polish, launch prep, announcements |

---

## Open Questions

### 1. Should we include all 180 frameworks or subset?

**Options:**
- **Option A:** All 180 frameworks (comprehensive)
- **Option B:** Top 20-30 most-requested (lean)

**Recommendation:** Start with Option B (top frameworks), expand on demand

**Top Priority Frameworks:**
- NIST CSF 2.0, NIST 800-53 R5
- ISO 27001:2022, ISO 27002:2022
- PCI DSS 4.0.1
- SOC 2 (TSC)
- CMMC 2.0
- DORA, NIS2, GDPR
- NCSC CAF 4.0, UK Cyber Essentials
- CIS CSC 8.1

### 2. Text search implementation?

**Options:**
- **Option A:** Simple string matching in control descriptions
- **Option B:** Embeddings + vector search (requires embedding model)

**Recommendation:** Option A for MVP, Option B for v2

### 3. Include Assessment Objectives sheet?

The "Assessment Objectives 2025.4" sheet has testing criteria for each control.

**Value:** Helps users understand HOW to test/verify controls
**Cost:** Additional data extraction + tool complexity

**Recommendation:** Add in v1.1 after core queries validated

---

## Resources

### SCF Documentation
- **Website:** https://securecontrolsframework.com/
- **GitHub:** https://github.com/securecontrolsframework/securecontrolsframework
- **Download:** https://securecontrolsframework.com/scf-download/
- **Errata:** https://github.com/securecontrolsframework/securecontrolsframework/blob/main/SCF%202025.4%20Errata.txt

### MCP Development
- **MCP Spec:** https://modelcontextprotocol.io/
- **Python SDK:** https://github.com/anthropics/python-sdk
- **Smithery Registry:** https://smithery.ai/

### Related MCPs
- **eu-regulations-mcp:** (your existing tool)
- **Cross-reference opportunity:** Link DORA/NIS2 articles to SCF controls

---

## Contact & Handover

**Prepared by:** Claude Sonnet 4.5
**Prepared for:** Jeffrey von Rotz / Ansvar
**Date:** 2026-01-29

**Key Files Generated:**
- `/tmp/scf-repo/` - Cloned SCF repository
- This handover document

**Environment Setup:**
```bash
# Virtual environment for Excel parsing
cd /tmp
python3 -m venv scf-venv
source scf-venv/bin/activate
pip install openpyxl pdfplumber
```

**Ready to start:** Data extraction script in Phase 1 above
