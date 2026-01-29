# Framework Expansion Design
**Date:** 2026-01-29
**Status:** Ready for Implementation

## Executive Summary

Add 11 high-value frameworks from SCF 2025.4 to expand geographic coverage (APAC, Europe) and add industry-specific frameworks (SWIFT, CSA STAR). All frameworks use official SCF mappings (no custom mappings).

## Frameworks to Add

### Tier 1: High Regulatory/Market Value (5 frameworks)

| Framework | SCF Column | Key | Justification |
|-----------|------------|-----|---------------|
| **Australian Essential Eight** | 242 | `australia_essential_8` | Mandatory for Australian gov/critical infrastructure |
| **Australian ISM June 2024** | 245 | `australia_ism_2024` | Comprehensive Australian gov security standard |
| **Singapore MAS TRM 2021** | 267 | `singapore_mas_trm_2021` | Mandatory for Singapore financial institutions |
| **SWIFT CSF 2023** | 107 | `swift_cscf_2023` | Mandatory for SWIFT financial messaging participants |
| **NIST Privacy Framework 1.0** | 61 | `nist_privacy_framework_1_0` | US privacy standard (complements existing GDPR) |

### Tier 2: European National Frameworks (6 frameworks)

| Framework | SCF Column | Key | Justification |
|-----------|------------|-----|---------------|
| **Netherlands** | 214 | `netherlands` | Dutch national cybersecurity regulations |
| **Norway** | 216 | `norway` | Norwegian national cybersecurity regulations |
| **Sweden** | 233 | `sweden` | Swedish national cybersecurity regulations |
| **Germany** | 204 | `germany` | German national cybersecurity regulations (general) |
| **Germany BAIT** | 205 | `germany_bait` | Banking Supervisory Requirements for IT |
| **Germany C5 2020** | 206 | `germany_c5_2020` | Cloud Computing Compliance Criteria Catalogue |

**Note:** European country columns contain mappings to national laws/regulations (article numbers). These are NOT the same as BIO, KATAKRI, NSM, etc. (which are security frameworks). SCF doesn't have those specific security frameworks.

### Tier 3: Cloud/Industry Standards (1 framework)

| Framework | SCF Column | Key | Justification |
|-----------|------------|-----|---------------|
| **CSA CCM 4** | 33 | `csa_ccm_4` | Cloud Security Alliance Cloud Controls Matrix (CSA STAR basis) |

## Implementation Plan

### Phase 1: Update Extraction Script
Update `scf-extract-starter.py` to include new framework column mappings:

```python
framework_columns = {
    # ... existing 16 frameworks ...

    # TIER 1: APAC
    "australia_essential_8": "APAC\nAustralia\nEssential 8",
    "australia_ism_2024": "APAC\nAustralia\nISM\nJune 2024",
    "singapore_mas_trm_2021": "APAC\nSingapore MAS\nTRM 2021",

    # TIER 1: Industry
    "swift_cscf_2023": "SWIFT\nCSF\n2023",
    "nist_privacy_framework_1_0": "NIST Privacy Framework\n1.0",

    # TIER 2: European National
    "netherlands": "EMEA\nNetherlands",
    "norway": "EMEA\nNorway",
    "sweden": "EMEA\nSweden",
    "germany": "EMEA\nGermany",
    "germany_bait": "EMEA\nGermany\nBanking Supervisory Requirements for IT (BAIT)",
    "germany_c5_2020": "EMEA\nGermany\nC5\n2020",

    # TIER 3: Cloud
    "csa_ccm_4": "CSA\nCCM\n4",
}
```

**Note:** Column headers use `\n` for line breaks in the Excel file.

### Phase 2: Extract New Data
Run extraction script if SCF Excel file is available:
```bash
python scf-extract-starter.py /path/to/secure-controls-framework-scf-2025-4.xlsx
```

This generates:
- `scf-controls.json` (updated with all mappings)
- `framework-to-scf.json` (reverse index with 27 frameworks)

### Phase 3: Update Framework Metadata
Update `src/security_controls_mcp/data_loader.py` with new framework display names:

```python
framework_names = {
    # ... existing 16 ...

    # Tier 1: APAC
    "australia_essential_8": "Australian Essential Eight",
    "australia_ism_2024": "Australian ISM (June 2024)",
    "singapore_mas_trm_2021": "Singapore MAS TRM 2021",

    # Tier 1: Industry
    "swift_cscf_2023": "SWIFT Customer Security Framework 2023",
    "nist_privacy_framework_1_0": "NIST Privacy Framework 1.0",

    # Tier 2: European National
    "netherlands": "Netherlands Cybersecurity Regulations",
    "norway": "Norway Cybersecurity Regulations",
    "sweden": "Sweden Cybersecurity Regulations",
    "germany": "Germany Cybersecurity Regulations",
    "germany_bait": "Germany BAIT (Banking IT Requirements)",
    "germany_c5_2020": "Germany C5:2020 (Cloud Controls)",

    # Tier 3: Cloud
    "csa_ccm_4": "CSA Cloud Controls Matrix v4",
}
```

### Phase 4: Update Documentation

**README.md updates:**
1. Update badge: "16 frameworks" → "27 frameworks"
2. Update framework list section
3. Add new "Framework Roadmap" section

**Framework Roadmap Section:**
```markdown
## Framework Roadmap

**Currently Supported (27 frameworks):**
- **International:** ISO 27001/27002, NIST CSF/800-53, CIS CSC, CSA CCM
- **US Federal/Industry:** FedRAMP, CMMC, PCI DSS, SOC 2, HIPAA
- **EU/UK:** GDPR, DORA, NIS2, NCSC CAF, Cyber Essentials
- **APAC:** Australia Essential Eight, Australia ISM, Singapore MAS TRM
- **European National:** Netherlands, Norway, Sweden, Germany (general/BAIT/C5)
- **Financial:** SWIFT CSCF
- **Privacy:** NIST Privacy Framework

**Not Yet Available (Waiting for SCF Coverage):**
- 🇳🇱 Netherlands BIO (Baseline Informatiebeveiliging Overheid)
- 🇫🇮 Finland KATAKRI
- 🇳🇴 Norway NSM Grunnprinsipper (specific security framework)
- 🇸🇪 Sweden MSB frameworks (specific security framework)
- 🇩🇰 Denmark CFCS guidelines
- 🇧🇪 Belgium CCB frameworks
- 🇫🇷 France ANSSI SecNumCloud

*These frameworks are not included because SCF doesn't provide official mappings. We maintain data quality by using only ComplianceForge-vetted mappings from SCF.*

**Want these frameworks?**
1. **Fork for private use:** Use our [paid standards import feature](PAID_STANDARDS_GUIDE.md)
2. **Contribute to SCF:** Help add mappings at https://securecontrolsframework.com/contact/
```

### Phase 5: Update Tests
Update test expectations in:
- `tests/test_smoke.py` - add new framework keys to expected list
- `tests/test_data_loader.py` - add new frameworks to critical framework tests if needed
- `verify_production_ready.py` - update framework count from 16 to 27

### Phase 6: Update CHANGELOG
Document the expansion:
```markdown
## [0.3.0] - 2026-01-29

### Added
- 11 new framework mappings from SCF 2025.4
  - APAC: Australian Essential Eight, Australian ISM 2024, Singapore MAS TRM 2021
  - Financial: SWIFT CSCF 2023
  - Privacy: NIST Privacy Framework 1.0
  - European: Netherlands, Norway, Sweden, Germany (general/BAIT/C5)
  - Cloud: CSA Cloud Controls Matrix v4
- Framework Roadmap section to README documenting available and unavailable frameworks

### Changed
- Total framework coverage: 16 → 27 frameworks
- Updated framework metadata and documentation
```

## Data Quality Considerations

### Why No Custom Mappings
For compliance consulting use case, maintaining **authoritative source integrity** is critical:
- ✅ All mappings from ComplianceForge SCF (vetted, defensible in audits)
- ❌ No community/custom mappings (creates confusion, liability)
- ✅ Clear documentation of what's NOT available (manages expectations)

### European Country Columns
The European country columns (Netherlands, Norway, Sweden, Germany) contain **national law/regulation article numbers**, NOT specific security frameworks like:
- ❌ BIO (Netherlands baseline security framework) - NOT in SCF
- ❌ KATAKRI (Finnish defense security framework) - NOT in SCF
- ❌ NSM Grunnprinsipper (Norwegian security principles) - NOT in SCF

Users wanting those specific frameworks should:
1. Fork repo and use paid standards import for their private use
2. Contribute mappings to SCF for public benefit

## Success Metrics

**Value Added:**
- +5 frameworks with regulatory mandate (Australia, Singapore, SWIFT)
- +6 European national regulations (compliance consulting value)
- +1 privacy framework (NIST Privacy complements GDPR)
- +1 cloud standard (CSA CCM/STAR)

**Total Coverage:** 27 frameworks spanning:
- 4 continents (Americas, Europe, Asia, Australia)
- 8 industries (gov, finance, healthcare, tech, cloud, etc.)
- 3 framework types (international standards, national regs, industry-specific)

## Next Steps After Implementation

1. Test with real compliance consulting scenarios
2. Gather user feedback on which "not available" frameworks are most requested
3. Consider contributing high-demand frameworks to SCF upstream
