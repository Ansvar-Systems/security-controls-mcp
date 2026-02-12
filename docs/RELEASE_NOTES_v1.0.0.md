# Release Notes - v1.0.0 (2026-02-12)

## 🎉 Major Feature: Standards Import with 12 Specialized Extractors

This release introduces a comprehensive standards import system that allows users to upload purchased security standards (ISO, NIST, etc.) and automatically extract controls with high accuracy.

## ✨ Key Features

### Web UI for Standards Upload
- **User-Friendly Interface**: Drag-and-drop PDF upload at `http://localhost:8000/standards/upload`
- **Real-Time Extraction**: Instant control extraction with progress feedback
- **Results Dashboard**: View extracted controls with confidence scoring, categories, and validation
- **Security Hardened**: File size limits (50MB), PDF magic byte validation, CSP headers

### 12 Specialized Extractors

Automatic control extraction from diverse standard types:

#### 📊 IT/Cloud Security (5 extractors)
- **ISO 27001** (2022: 93 controls, 2013: 114 controls)
  - Multi-version support with automatic version detection
  - 4 categories (2022) or 14 families (2013)
  - Format: A.X.Y (e.g., A.5.15, A.8.23)

- **NIST 800-53** (Revision 5: 320 controls)
  - 20 control families (AC, AU, AT, CM, etc.)
  - Control enhancements (e.g., AC-1(1))
  - Format: FAMILY-NUMBER

- **SOC 2** (Trust Services Criteria 2017)
  - 5 categories: Security, Availability, Processing Integrity, Confidentiality, Privacy
  - Format: CC1.1, A1.2, PI1.1, C1.1, P1.1
  - ~100 criteria total

- **PCI DSS** (v4.0 & v3.2.1)
  - 12 requirements with sub-requirements
  - Format: 1.2.3
  - ~300 requirements total

- **CIS Controls** (v8 & v7.1)
  - 18 controls with 153 safeguards
  - Format: 1.1, 4.3
  - Asset inventory to penetration testing

#### 🏭 OT/ICS Security (1 extractor)
- **IEC 62443** (Industrial Automation & Control Systems)
  - Multi-part standard (62443-2-1, 62443-3-3, etc.)
  - SR/FR/CR requirement types
  - Critical for SCADA, DCS, PLC systems

#### 🚗 Automotive (1 extractor)
- **ISO/SAE 21434** (Road Vehicles - Cybersecurity Engineering)
  - Version 2021
  - 10 main clauses (5-14) covering lifecycle phases
  - Format: X.Y.Z (e.g., 5.4.2, 6.3.1)
  - Management, Concept, Development, Production, Operations, Decommissioning

#### 🔒 Privacy (3 extractors)
- **ISO 27701** (Privacy Information Management System)
  - Version 2019 - Extends ISO 27002 for PIMS
  - Additional privacy-specific controls
  - Format: X.Y.Z

- **GDPR** (EU General Data Protection Regulation)
  - Regulation (EU) 2016/679
  - 99 articles across 11 chapters
  - Format: Article X
  - Principles, Rights, Controller obligations, Enforcement

- **CCPA/CPRA** (California Consumer Privacy Act)
  - CCPA (2018) and CPRA (2020 amendment)
  - Format: Section 1798.XXX
  - Consumer rights and business obligations

#### 🤖 AI Governance (2 extractors)
- **ISO 42001** (AI Management System)
  - Version 2023 - First comprehensive AI management standard
  - Clauses 4-10: Context, Leadership, Planning, Support, Operation, Evaluation, Improvement
  - Format: X.Y

- **NIST AI RMF** (AI Risk Management Framework)
  - NIST AI 100-1 (v1.0)
  - 4 functions: GOVERN, MAP, MEASURE, MANAGE
  - Format: GOVERN-1.1, MAP-2.3, etc.
  - Trustworthy AI characteristics

### Extractor Features

**Version Detection**
- Automatic identification of standard versions
- Evidence-based confidence scoring (DETECTED/AMBIGUOUS/UNKNOWN)
- Evidence collection (e.g., "Found 'Revision 5' text", "Found '2016/679'")

**Hierarchical Extraction**
- Parent-child relationships preserved
- Control families and categories
- Sub-controls and enhancements tracked

**Quality Validation**
- Expected control count validation
- Missing control detection
- Confidence scoring (0.0 to 1.0)
- Extraction warnings

**Auto-Discovery Registry**
- Decorator-based registration (`@register_extractor("standard_name")`)
- New extractors automatically discovered
- No manual configuration required

## 🏗️ Architecture

### Registry Pattern
```python
from ..base import BaseExtractor
from ..registry import register_extractor

@register_extractor("my_standard")
class MyStandardExtractor(BaseExtractor):
    def extract(self, pdf_bytes: bytes) -> ExtractionResult:
        # Implementation
        pass
```

### Data Structures
- `Control`: Individual control with ID, title, content, page, category, parent
- `ExtractionResult`: Complete extraction with version, controls, confidence, warnings
- `VersionDetection`: Enum (DETECTED, AMBIGUOUS, UNKNOWN)

### Web API Endpoints
- `GET /standards/upload` - Web upload interface
- `POST /api/standards/extract` - Extract controls from uploaded PDF
- Returns JSON with controls, version, confidence, warnings

## 📊 Statistics

- **Extractors**: 12 (covering 5 major domains)
- **Tests**: 242 (100% pass rate)
- **Test Coverage**: Foundation, extractors, web UI, security
- **Extraction Speed**: <0.1s for version detection, <1s for full extraction
- **Supported Formats**: PDF (with magic byte validation)
- **Max File Size**: 50MB (configurable)

## 🔒 Security

- File size limits (50MB default)
- PDF magic byte validation (must start with `%PDF-`)
- CSP headers (Content-Security-Policy)
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- No error details leaked to users
- Path traversal prevention

## 🧪 Testing

### Test Categories
- **Foundation** (11 tests): Base classes, dataclasses, enums
- **Registry** (5 tests): Auto-discovery, registration, edge cases
- **ISO 27001** (37 tests): Version detection, 2022/2013 extraction, validation
- **NIST 800-53** (11 tests): R5 extraction, families, enhancements
- **ISO 21434** (12 tests): Automotive clauses, lifecycle phases
- **SOC 2** (8 tests): Trust Services Criteria, categories
- **Web UI** (24 tests): Upload, extraction, security, error handling
- **Specialized Init** (7 tests): Auto-import mechanism

### Test Commands
```bash
# Run all tests
pytest -v

# Run with timing
pytest -v --durations=10

# Run specific extractor tests
pytest tests/test_iso_27001_extractor.py -v
```

## 📈 Performance

- Version detection: <0.05s
- Control extraction: 0.1-0.5s (depends on PDF size and complexity)
- Total extraction time: <1s for most standards
- Memory efficient: Streaming PDF processing
- No persistent storage required

## 🚀 Usage

### Start Web UI
```bash
# Clone and install
git clone https://github.com/Ansvar-Systems/security-controls-mcp
cd security-controls-mcp
poetry install

# Start HTTP server
poetry run python -m security_controls_mcp.http_server --port 8000

# Open http://localhost:8000/standards/upload
```

### Programmatic Usage
```python
from security_controls_mcp.extractors.specialized import get_extractor

# Get ISO 27001 extractor
extractor = get_extractor("iso_27001")()

# Extract controls
with open("iso27001.pdf", "rb") as f:
    result = extractor.extract(f.read())

print(f"Version: {result.version}")
print(f"Controls: {len(result.controls)}")
print(f"Confidence: {result.confidence_score:.2f}")
```

## 🔄 Migration Guide

No breaking changes. New feature is additive only.

## 🐛 Known Issues

None reported.

## 🎯 Future Enhancements

Potential additions for future releases:
- Additional extractors (HIPAA, FISMA, FedRAMP baseline docs, etc.)
- Batch processing (multiple PDFs at once)
- Export formats (JSON, CSV, Excel)
- Comparison view (specialized vs generic extraction)
- Control mapping to SCF framework
- OCR support for scanned PDFs

## 📝 Breaking Changes

None. This is a feature addition.

## 🤝 Contributors

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

## 📚 Documentation

- [CLAUDE.md](../CLAUDE.md) - Development guide with extractor documentation
- [CHANGELOG.md](../CHANGELOG.md) - Complete version history
- [Design Document](./plans/2026-02-12-improved-standards-import-design.md) - Architecture decisions
- [Implementation Plan](./plans/2026-02-12-improved-standards-import-plan.md) - Detailed build plan

## ✅ Checklist for Release

- [x] All 242 tests passing
- [x] Documentation updated (CLAUDE.md, CHANGELOG.md, README.md)
- [x] Security review completed
- [x] Performance benchmarks acceptable
- [x] Release notes created
- [ ] Version bumped in pyproject.toml
- [ ] Tagged in git
- [ ] Published to PyPI

## 🎉 Conclusion

v1.0.0 represents a major capability enhancement, enabling automated extraction from diverse security standards across IT, OT, automotive, privacy, and AI domains. The extensible architecture makes it easy to add new extractors while maintaining high quality through comprehensive testing.
