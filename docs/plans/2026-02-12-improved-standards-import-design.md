# Improved Standards Import - Design Document

**Date:** 2026-02-12
**Status:** Approved
**Author:** Claude Code + Jeffrey von Rotz

## Executive Summary

Transform the security-controls-mcp from a CLI-based PDF importer into a **strategic compliance planning tool** for GRC analysts. The current import process is functional but not user-friendly - it requires command-line expertise and produces hit-or-miss extraction quality. This design addresses both issues with specialized extractors and a web UI.

## Problem Statement

### Current Pain Points

1. **Extraction Quality (Critical)**: Generic regex extractor fails too often (71/93 controls = loss of trust)
2. **User Experience**: CLI-only interface blocks adoption by business users (GRC analysts, compliance officers)
3. **No Validation**: Users don't know if extraction succeeded until they query
4. **Limited Visibility**: No dashboard showing what's imported or gap analysis
5. **No Recovery**: Bad extraction = manual JSON editing or give up

### Success Criteria

- **ISO 27001:2022**: 100% of 93 controls extracted (no failures accepted)
- **NIST 800-53 R5**: 99%+ of 777 controls extracted
- **Self-Service**: Business users can import standards without CLI knowledge
- **Strategic Value**: Gap analysis drives purchasing decisions ("which standard should I buy next?")

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Primary User** | Business users (GRC analysts/compliance officers) | CLI is a barrier to adoption for non-technical users |
| **Scope** | Production-ready UI with coverage dashboard (Option C) | Provides strategic value beyond just "PDF uploader" |
| **Authentication** | None (localhost + copyright warnings) | Simpler, faster to build; good enough for local/trusted network use |
| **Processing Model** | Synchronous (3-minute timeout) | "Super stable and simple" - no job queues, no background workers, no state management |
| **Architecture** | Extend existing `http_server.py` | One process, one port; reuse existing uvicorn/starlette infrastructure |
| **Frontend** | Pure HTML/CSS/Vanilla JS | No React, no build step, no npm - dead simple and rock solid |
| **Critical Path** | Specialized extractors FIRST | Foundation for everything else - bad extraction breaks the whole product |

## Architecture

### System Overview

```
security-controls-mcp/
├── src/security_controls_mcp/
│   ├── http_server.py          # EXTEND: Add web UI endpoints
│   ├── extractors/
│   │   ├── base.py             # NEW: Base extractor interface
│   │   ├── registry.py         # NEW: Auto-discovery of extractors
│   │   ├── version_detector.py # NEW: Detect standard version
│   │   ├── specialized/        # NEW: High-quality extractors
│   │   │   ├── __init__.py     # Auto-import all extractors
│   │   │   ├── iso_27001.py    # ISO 27001:2022 + 2013
│   │   │   ├── nist_800_53.py  # NIST 800-53 R5
│   │   │   ├── soc2_tsc.py     # SOC 2 TSC
│   │   │   ├── pci_dss.py      # PCI DSS v4.0.1
│   │   │   └── iso_27002.py    # ISO 27002:2022
│   │   └── pdf_extractor.py    # KEEP: Generic fallback
│   └── static/                 # NEW: Web UI
│       ├── index.html          # Dashboard
│       ├── import.html         # Upload form
│       ├── standard.html       # Detail + comparison view
│       ├── gap-analysis.html   # Strategic insights
│       ├── app.js              # Shared API client
│       └── styles.css          # Global styles
```

### Data Flow

```
Upload PDF → Validate → Detect Version → Try Specialized Extractor
                                              ↓
                                    Quality Score ≥ 90%?
                                    ↓ Yes          ↓ No
                                Use specialized   Try generic too
                                    ↓                 ↓
                                Return result    Show both → User chooses
```

## Core Components

### 1. Extractor Contract (Foundation)

All extractors implement a strict interface for consistency:

```python
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

class VersionDetection(Enum):
    DETECTED = "detected"      # Clear match
    AMBIGUOUS = "ambiguous"    # Multiple possibilities
    UNKNOWN = "unknown"        # No version found

@dataclass
class Control:
    id: str                    # "A.5.15"
    title: str                 # "Access control"
    content: str               # Full text
    page: int                  # Page number
    category: str              # "Annex A"
    parent: Optional[str]      # "A.5" (for hierarchy)

@dataclass
class ExtractionResult:
    # Identification
    standard_id: str           # "iso_27001_2022"
    version: str               # "2022"
    version_detection: VersionDetection
    version_evidence: List[str]  # ["Found in metadata", "Page 1 confirms"]

    # Extraction results
    controls: List[Control]
    expected_control_ids: List[str]  # Known IDs for validation
    missing_control_ids: List[str]   # Expected but not found

    # Quality metrics
    confidence_score: float          # 0.0 to 1.0
    extraction_method: str           # "specialized" or "generic"
    extraction_duration_seconds: float
    warnings: List[str]

@dataclass
class ExtractionComparison:
    """When both extractors run and differ."""
    specialized: ExtractionResult
    generic: ExtractionResult

    controls_in_both: List[str]
    unique_to_specialized: List[str]
    unique_to_generic: List[str]

    recommendation: str  # Data-driven: consider coverage + confidence
```

### 2. Registry Pattern (Auto-Discovery)

New extractors are automatically discovered when dropped into `specialized/`:

```python
# extractors/registry.py
SPECIALIZED_EXTRACTORS = {}

def register_extractor(standard_pattern: str):
    def decorator(cls):
        SPECIALIZED_EXTRACTORS[standard_pattern] = cls
        return cls
    return decorator

# extractors/specialized/__init__.py
from pathlib import Path
import importlib

# Auto-import all extractor modules
for f in Path(__file__).parent.glob("*.py"):
    if f.name != "__init__.py":
        importlib.import_module(f".{f.stem}", __package__)

# extractors/specialized/iso_27001.py
@register_extractor("iso_27001")
class ISO27001Extractor(BaseExtractor):
    VERSIONS = {
        "2022": {"controls": 93, "themes": 4},
        "2013": {"controls": 114, "domains": 14}
    }
    # ... implementation ...
```

### 3. Version Detection (Three States)

```python
def detect_version(self, pdf) -> tuple[str, VersionDetection, List[str]]:
    evidence = []

    # Signal 1: PDF metadata
    if "2022" in pdf.metadata.get("title", ""):
        evidence.append("Found '2022' in PDF metadata")
        return "2022", VersionDetection.DETECTED, evidence

    # Signal 2: First 5 pages
    early_text = self._extract_pages(pdf, 0, 5)
    if "ISO/IEC 27001:2022" in early_text:
        evidence.append("Found 'ISO/IEC 27001:2022' on page 1")
        return "2022", VersionDetection.DETECTED, evidence

    # Signal 3: Control structure (ambiguous)
    control_count = self._count_annex_controls(pdf)
    if 90 <= control_count <= 95:
        evidence.append(f"Control count ({control_count}) suggests 2022")
        return "2022", VersionDetection.AMBIGUOUS, evidence

    # Unknown - default with evidence
    evidence.append("No version found in metadata or first 5 pages")
    return "2022", VersionDetection.UNKNOWN, evidence
```

### 4. Specialized Extractors (Top 5)

**Tier 1: Must work perfectly**
- ISO 27001:2022 (93 controls) + 2013 (114 controls)
- NIST SP 800-53 R5 (777 controls in families: AC-*, AU-*, SC-*, etc.)
- SOC 2 TSC (412 controls)
- PCI DSS v4.0.1 (364 requirements)
- ISO 27002:2022 (316 controls - companion to 27001)

**Key insight:** Specialized extractors have **structural knowledge**, not just better regex:
- ISO 27001 Annex A starts at known page, uses A.5-A.8 numbering, has 4 themes
- NIST 800-53 uses unambiguous family prefixes (AC-, AU-) with enhancements (AC-2(1))
- PCI DSS uses dotted requirement numbering (1.2.1, 3.4.1)

**Example: ISO 27001 Extractor**

```python
@register_extractor("iso_27001")
class ISO27001Extractor(BaseExtractor):
    VERSIONS = {
        "2022": {
            "controls": 93,
            "themes": ["Organizational", "People", "Physical", "Technological"],
            "pattern": r"A\.[5-8]\.\d+",
            "expected_ids": ["A.5.1", "A.5.2", ..., "A.8.34"]
        },
        "2013": {
            "controls": 114,
            "domains": 14,
            "pattern": r"A\.\d+\.\d+\.\d+",
            "expected_ids": ["A.5.1.1", "A.5.1.2", ..., "A.18.2.3"]
        }
    }

    def extract(self, pdf_path: Path) -> ExtractionResult:
        # Detect version first
        version, detection, evidence = self.detect_version(pdf)
        config = self.VERSIONS[version]

        # Extract using known structure
        controls = []
        for page in pdf.pages[20:]:  # Annex A typically starts ~page 20
            matches = re.finditer(config["pattern"], page.text)
            for match in matches:
                control = self._parse_control(match, page)
                controls.append(control)

        # Validate against expected
        found_ids = [c.id for c in controls]
        missing_ids = [id for id in config["expected_ids"] if id not in found_ids]

        # Calculate confidence
        coverage = len(found_ids) / len(config["expected_ids"])
        confidence = coverage * 0.95  # Penalize slightly for any missing

        return ExtractionResult(
            standard_id=f"iso_27001_{version}",
            version=version,
            version_detection=detection,
            version_evidence=evidence,
            controls=controls,
            expected_control_ids=config["expected_ids"],
            missing_control_ids=missing_ids,
            confidence_score=confidence,
            extraction_method="specialized",
            warnings=[] if coverage == 1.0 else [f"Missing {len(missing_ids)} controls"]
        )
```

## API Endpoints

### HTTP Server Extensions

Extend existing `http_server.py` (reuse uvicorn/starlette):

```python
from starlette.staticfiles import StaticFiles

# NEW: Serve static files (web UI)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# NEW: Import endpoint
@app.post("/api/import", timeout=180)  # 3-minute timeout
async def import_standard(
    file: UploadFile,
    standard_type: str,
    title: str,
    purchased_from: str = "unknown",
    purchase_date: str = "unknown"
) -> ImportResponse:
    """Upload PDF and extract controls (synchronous)."""

    # Validate upload
    await validate_upload(file, standard_type)

    # Try specialized extractor
    result = await extract_with_fallback(file, standard_type)

    # Save to config
    config.add_standard(result.standard_id, ...)

    return ImportResponse(
        standard_id=result.standard_id,
        extraction_result=result,
        comparison=result.comparison if result.needs_comparison else None,
        next_url=f"/standard.html?id={result.standard_id}"
    )

# NEW: List standards
@app.get("/api/standards")
async def list_standards() -> List[StandardSummary]:
    """All imported standards with coverage metrics."""
    return [
        {
            "standard_id": "iso_27001_2022",
            "title": "ISO/IEC 27001:2022",
            "controls_extracted": 93,
            "controls_expected": 93,
            "coverage": 1.0,
            "quality_score": 0.98,
            "scf_mappings": 847,  # How many SCF controls it maps to
            "import_date": "2026-02-12T15:30:00"
        }
    ]

# NEW: Standard detail
@app.get("/api/standards/{standard_id}")
async def get_standard_detail(standard_id: str) -> StandardDetail:
    """Full details including hierarchy and comparison (if needed)."""
    return {
        "metadata": {...},
        "controls": [...],
        "hierarchy": {...},  # Tree structure
        "missing_controls": [...],
        "scf_mapping": {...},
        "comparison": {...} if comparison_exists else None
    }

# NEW: Delete standard
@app.delete("/api/standards/{standard_id}")
async def delete_standard(standard_id: str):
    """Remove imported standard (enables re-import workflow)."""
    config.remove_standard(standard_id)
    # Delete files from ~/.security-controls-mcp/standards/{id}/
    return {"status": "deleted"}

# NEW: Gap analysis
@app.get("/api/gap-analysis")
async def gap_analysis() -> GapAnalysis:
    """Strategic insights across all imported standards."""
    return {
        "total_scf_coverage": 0.58,
        "coverage_by_domain": [
            {"domain": "Asset Management", "percentage": 0.45, "status": "gaps"},
            {"domain": "Cryptography", "percentage": 0.38, "status": "gaps"},
            ...
        ],
        "suggested_standards": [
            {
                "standard_id": "iso_27002_2022",
                "title": "ISO/IEC 27002:2022",
                "rationale": "Implementation guidance for ISO 27001",
                "additional_coverage_pct": 0.15,
                "fills_gaps_in": [
                    {"domain": "Asset Management", "current": 0.45, "with_standard": 0.82},
                    {"domain": "Cryptography", "current": 0.38, "with_standard": 0.71}
                ]
            }
        ],
        "missing_critical_controls": [
            {
                "scf_id": "IAM-03",
                "title": "Multi-Factor Authentication",
                "criticality": "high",  # Based on framework count
                "required_by": ["pci_dss_4.0.1", "nist_800_53_r5", "cmmc_2.0"],
                "action": "Import NIST 800-53 R5 or PCI DSS v4.0.1"
            }
        ]
    }
```

### Upload Validation (Fail Fast)

```python
async def validate_upload(file: UploadFile, standard_type: str):
    """Catch issues before extraction (save time, better UX)."""

    # Size check
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > 50 * 1024 * 1024:  # 50 MB
        raise HTTPException(413, "File too large (max 50MB)")

    # MIME type
    if file.content_type != "application/pdf":
        raise HTTPException(400, "Must be PDF")

    # Magic bytes
    header = await file.read(4)
    await file.seek(0)
    if header != b"%PDF":
        raise HTTPException(400, "Invalid PDF file")

    # NEW: Scanned PDF detection (upfront, not after extraction)
    first_5_pages = extract_text_from_pages(file, 0, 5)
    char_density = len(first_5_pages) / 5
    if char_density < 100:
        raise ScannedPDFError(
            "This appears to be a scanned PDF (images, not text). "
            "Please use a digital/native PDF or run OCR first."
        )

    # NEW: Wrong standard detection (keyword scan)
    if standard_type == "iso_27001":
        if "NIST" in first_5_pages and "800-53" in first_5_pages:
            raise WrongStandardError(
                "This appears to be NIST 800-53, not ISO 27001. "
                "Did you select the wrong standard type?"
            )

    # NEW: Duplicate handling
    if registry.has_standard(standard_id):
        raise DuplicateStandardError(
            f"{standard_id} already imported. Delete first to re-import.",
            allow_overwrite=True
        )
```

## Web UI

### Technology Stack

- **Pure HTML + Vanilla JS** (no React, no build step)
- **CSS Variables** for theming
- **Starlette StaticFiles** serving (zero config)

### Pages

#### 1. Dashboard (`index.html`)

**Purpose:** Overview of imported standards + quick actions

**Key Features:**
- Card for each imported standard (93/93 controls, 100% coverage)
- Real coverage metrics (not vague percentages)
- Warnings for incomplete extractions (770/777 controls ⚠️)
- Total SCF coverage (58% - 847/1,451)
- Delete button per standard (enables re-import)
- Link to Gap Analysis

#### 2. Import Form (`import.html`)

**Purpose:** Upload PDF with metadata

**Key Features:**
- **Copyright warning** (only import what YOU purchased)
- Standard type dropdown (auto-detect version):
  - ISO 27001 (detects 2022 vs 2013)
  - NIST SP 800-53 R5
  - SOC 2 TSC
  - PCI DSS v4.0.1
  - ISO 27002
  - Other (generic - shows warning + requires standard_id field)
- Drag-drop file upload
- Pre-fill metadata based on standard type
- Processing feedback: "Processing... may take 1-2 minutes"
- Update after 30s: "Still processing... large PDFs may take up to 2 minutes"

#### 3. Standard Detail (`standard.html`)

**Purpose:** View extracted controls + comparison (if needed)

**Layout (Clean Extraction):**
- Tree view with expand/collapse (default)
- Flat list with sort options (page, category, control ID)
- Search/filter controls
- Click control → Show full text
- SCF mapping visualization

**Layout (Comparison Needed):**
- Side-by-side: Specialized vs Generic
- Controls in both: 85
- Unique to specialized: 6 controls
- Unique to generic: 3 controls
- Recommendation with reasoning
- **Three choices:**
  - Use Specialized
  - Use Generic
  - **Use Best of Both** (union: 91 + 3 = 94 total)

#### 4. Gap Analysis (`gap-analysis.html`)

**Purpose:** Strategic insights - THE differentiator

**Key Features:**
- Overall SCF coverage progress bar (color-coded: green/yellow/red)
- Coverage by domain (from SCF data, not hardcoded):
  - Asset Management: 45% (gaps) ⚠️
  - Cryptography: 38% (gaps) ⚠️
  - Governance: 78% (strong) ✓
- Suggested standards with impact:
  - "ISO 27002 → +15% coverage, fills gaps in Asset Mgmt (45%→82%)"
  - "Mark as purchased" → Navigate to import with pre-select
- Framework overlap matrix (cap at 5-6, then list format)
- Missing critical controls:
  - Criticality = number of frameworks requiring it
  - IAM-03: MFA (required by 5 frameworks) → high
  - Shows exactly which standard to import for coverage
- **Export button:** Download Gap Report (CSV)

### Persistent Navigation

All pages include:
```html
<nav>
  <a href="/index.html">Dashboard</a>
  <a href="/import.html">Import</a>
  <a href="/gap-analysis.html">Gap Analysis</a>
</nav>
```

## Error Handling

**Philosophy:** Business users give up at first cryptic error. Every failure needs:
1. Clear explanation (what went wrong)
2. Why it happened (context)
3. How to fix it (actionable steps)

### Error Categories

#### 1. Upload Validation Failures

- **File too large** → "73 MB, max 50 MB. Try compressed version."
- **Not a PDF** → "This is .docx. Convert to PDF first."
- **Corrupt PDF** → "Invalid file header. Re-download from source."
- **Scanned PDF** → "Images, not text. Use digital PDF or run OCR."

#### 2. Extraction Failures

- **Zero controls found** → Show debug info, offer "View Raw Text", link to GitHub Issues
- **Partial extraction (67/93)** → List missing controls, offer comparison with generic
- **Version mismatch** → "You said 2022, we detected 2013. Evidence: [...]. Switch?"

#### 3. Processing Timeouts

- **3-minute timeout** → "Exceeded limit at page 187/215. Retry or use compressed version."
- **Retry with fallback:** Try `extractFirstNPages(100)` if full extraction times out

#### 4. Comparison Edge Cases

- **Both fail** → "0 controls from both extractors. Verify this is the official standard. View raw text."
- **Wildly different** → "Specialized: 93, Generic: 147. Generic treated sub-clauses as controls. Use specialized."

#### 5. System Errors

- **Disk full** → "No space. Current: 847 MB, need: 25 MB. Delete unused standards."
- **Permission denied** → "Fix: chmod 755 ~/.security-controls-mcp/"

#### 6. Duplicate Import

- **Already exists** → "iso_27001_2022 imported on Feb 12. Delete first to re-import. [Overwrite] [Cancel]"

#### 7. Wrong Standard

- **Mismatch detected** → "Selected ISO 27001 but PDF mentions NIST 800-53. Wrong type?"

### Recovery Mechanisms

- **Manual override:** Let user specify version when detection is ambiguous
- **"View Raw Text"** button (first 5,000 chars + Show More)
- **"Report Issue on GitHub"** with auto-populated debug template
- **Retry with degraded mode:** extractFirstNPages(100) if timeout

## Implementation Priorities

### Phase 1: Foundation (Week 1)

1. **Extractor contract & registry**
   - `base.py`: ExtractionResult, Control dataclasses
   - `registry.py`: @register_extractor decorator + auto-discovery
   - Update `extractors/specialized/__init__.py` for auto-import

2. **Version detection**
   - `version_detector.py`: Three states (detected/ambiguous/unknown)
   - Evidence list (multiple signals)
   - Tests for ISO 27001:2022 vs 2013

3. **Top 5 specialized extractors**
   - ISO 27001 (2022 + 2013)
   - NIST 800-53 R5
   - SOC 2 TSC
   - PCI DSS v4.0.1
   - ISO 27002:2022

### Phase 2: API (Week 1-2)

4. **HTTP endpoints** (extend `http_server.py`)
   - POST /api/import
   - GET /api/standards
   - GET /api/standards/{id}
   - DELETE /api/standards/{id}
   - GET /api/gap-analysis

5. **Upload validation**
   - Size, MIME, magic bytes
   - Scanned PDF detection (upfront)
   - Wrong standard detection
   - Duplicate handling

### Phase 3: Web UI (Week 2)

6. **Core pages**
   - Dashboard (standards library)
   - Import form (with copyright warnings)
   - Standard detail (tree + flat + comparison)
   - Gap analysis (strategic insights)

7. **Error handling**
   - Error templates for all scenarios
   - "Report Issue on GitHub" integration
   - Manual override UIs

### Phase 4: Polish (Week 3)

8. **Coverage dashboard**
   - Pull domain taxonomy from SCF data
   - Smart suggestions with fills_gaps_in
   - Missing critical controls (criticality by framework count)
   - Overlap matrix (cap at 5-6 standards)

9. **Export functionality**
   - CSV export of gap report
   - Include: coverage by domain, missing controls, suggestions

10. **Testing & docs**
    - Test all 5 extractors with real PDFs
    - Test error scenarios
    - Update README, PAID_STANDARDS_GUIDE
    - Add screenshots to docs

## Success Metrics

### Extraction Quality (Make or Break)

- **ISO 27001:2022**: 100% of 93 controls (no failures accepted)
- **NIST 800-53 R5**: 99%+ of 777 controls
- **SOC 2 TSC**: 100% of 412 controls
- **PCI DSS v4.0.1**: 100% of 364 requirements
- **ISO 27002:2022**: 99%+ of 316 controls
- **Generic fallback**: 80%+ for known standards

### User Experience

- **Upload to results**: <60 seconds for typical PDFs
- **Zero cryptic errors**: Every failure has actionable fix
- **Re-import rate**: <10% (high extraction quality means few retries)

### Adoption Signals

- **Self-service**: Business users complete imports without help
- **Strategic use**: "View Gap Analysis" is most-clicked feature
- **Purchasing decisions**: Users buy suggested standards

## Out of Scope (v1)

- ❌ Authentication (localhost only)
- ❌ Multi-user/team features
- ❌ Background jobs (rejected - contradicts "simple and stable")
- ❌ Checkpoints/resume (contradicts synchronous design)
- ❌ OCR integration (user's responsibility)
- ❌ Custom framework creation (requires SCF mapping)
- ❌ Mobile UI (desktop-first)
- ❌ Real-time progress bars (spinner with timeout is sufficient)

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Specialized extractors still fail | Medium | High | Extensive testing with real PDFs; collect samples upfront |
| PDF formats vary widely | High | Medium | Generic fallback always available; document limitations |
| 3-minute timeout insufficient | Low | Medium | Retry with extractFirstNPages(100); recommend compressed PDFs |
| Users upload wrong standard | Medium | Low | Keyword detection catches most cases; clear error messages |
| Gap analysis domain names change | Low | Low | Pull from SCF data at runtime, not hardcoded |

## Future Enhancements (Post-v1)

- **Additional specialized extractors**: CIS Controls, CMMC, ISO 42001
- **API-based imports**: NIST publishes JSON/XML - use that directly
- **HTML/Word format support**: Expand beyond PDF
- **OCR integration**: Auto-detect scanned PDFs and offer OCR
- **Standard versioning**: Track multiple versions (ISO 27001:2022 v1 vs v2)
- **Batch import**: Upload multiple PDFs at once
- **Advanced gap analysis**: Suggest combinations ("ISO 27001 + ISO 27002 = 73% coverage")
- **Export to PDF**: Prettier gap reports
- **Authentication**: Add if deployed beyond localhost

## Appendix: Comparison Logic

When specialized and generic extractors both run and differ:

```python
def choose_recommendation(spec: ExtractionResult, gen: ExtractionResult) -> str:
    # Prioritize expected ID coverage over raw count
    spec_coverage = len(spec.controls) / len(spec.expected_control_ids)
    gen_matched = [c for c in gen.controls if c.id in spec.expected_control_ids]
    gen_coverage = len(gen_matched) / len(spec.expected_control_ids)

    if spec.confidence_score >= 0.90 and spec_coverage > gen_coverage:
        return f"Use specialized ({len(spec.controls)} controls, {spec_coverage:.0%} expected coverage)"
    elif gen_coverage > spec_coverage:
        return f"Review generic result ({len(gen.controls)} controls, but verify against expected IDs)"
    elif spec.confidence_score >= 0.85:
        return f"Use specialized (higher confidence: {spec.confidence_score:.0%})"
    else:
        return "Use Best of Both (merge unique controls from each)"
```

## Appendix: Domain Coverage Calculation

```python
def calculate_domain_coverage(imported_standards, scf_data):
    """Calculate coverage by SCF domain."""

    # Get all SCF domains dynamically
    all_domains = scf_data.get_domains()

    coverage_by_domain = []
    for domain in all_domains:
        scf_controls_in_domain = scf_data.get_controls_by_domain(domain.name)

        # Count how many are covered by imported standards
        covered = 0
        for scf_control in scf_controls_in_domain:
            if any(has_mapping(std, scf_control) for std in imported_standards):
                covered += 1

        percentage = covered / len(scf_controls_in_domain)
        status = "strong" if percentage > 0.70 else "moderate" if percentage > 0.50 else "gaps"

        coverage_by_domain.append({
            "domain": domain.name,
            "percentage": percentage,
            "status": status,
            "covered": covered,
            "total": len(scf_controls_in_domain)
        })

    return coverage_by_domain
```

## Appendix: Criticality Calculation

```python
def calculate_criticality(scf_control):
    """Criticality = number of frameworks requiring this control."""
    framework_count = len(scf_control.mappings)

    if framework_count >= 5:
        return "high"
    elif framework_count >= 3:
        return "medium"
    else:
        return "low"
```

---

**End of Design Document**
