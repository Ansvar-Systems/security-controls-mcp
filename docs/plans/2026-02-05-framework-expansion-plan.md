# Framework Expansion Plan: 28 → 255 Frameworks

**Date**: 2026-02-05
**Goal**: Make security-controls-mcp THE definitive plugin for security framework mapping
**Scope**: Add all 255 SCF 2025.2 frameworks in phased rollout

---

## Executive Summary

Expand from 28 frameworks to full SCF 2025.2 coverage (255 frameworks), starting with AI governance frameworks (Tier 0) for immediate market differentiation.

## Current State

- **Frameworks exposed**: 28
- **SCF version**: 2025.4 (December 2025)
- **Architecture**: Framework-agnostic (data-driven)
- **Technical lift**: Low - primarily data extraction work

## Implementation Tiers

### Tier 0: AI & Emerging (4 frameworks) - IMMEDIATE PRIORITY

| Framework ID | Full Name | Why Critical |
|-------------|-----------|--------------|
| `iso_42001_2023` | ISO/IEC 42001:2023 AI Management System | THE AI governance standard |
| `nist_ai_rmf` | NIST AI 100-1 AI Risk Management Framework | US federal AI requirements |
| `eu_ai_act` | EU AI Act (Regulation 2024/1689) | Mandatory EU AI compliance 2025-2026 |
| `eu_cyber_resilience_act` | EU Cyber Resilience Act | IoT/connected product security |

### Tier 1: Enterprise Core (12 frameworks)

| Framework ID | Full Name | Category |
|-------------|-----------|----------|
| `iso_27017_2015` | ISO/IEC 27017:2015 | Cloud Security |
| `iso_27018_2014` | ISO/IEC 27018:2014 | Cloud Privacy (PII) |
| `iso_27701_2019` | ISO/IEC 27701:2019 | Privacy Extension to 27001 |
| `iso_22301_2019` | ISO/IEC 22301:2019 | Business Continuity |
| `iso_27001_2013` | ISO/IEC 27001:2013 | Legacy support |
| `iso_27002_2013` | ISO/IEC 27002:2013 | Legacy support |
| `cobit_2019` | COBIT 2019 | IT Governance |
| `sox` | Sarbanes-Oxley Act | Financial compliance |
| `nist_csf_1_1` | NIST CSF v1.1 | Legacy support |
| `nist_800_53_r4` | NIST SP 800-53 R4 | Legacy support |
| `pci_dss_saq_a` | PCI DSS v4.0.1 SAQ A | E-commerce |
| `pci_dss_saq_d` | PCI DSS v4.0.1 SAQ D | Full merchants |

### Tier 2: US Deep Compliance (20 frameworks)

| Framework ID | Full Name | Sector |
|-------------|-----------|--------|
| `stateramp_cat1` | StateRAMP Category 1 | US State Gov (Low) |
| `stateramp_cat2` | StateRAMP Category 2 | US State Gov (Moderate) |
| `stateramp_cat3` | StateRAMP Category 3 | US State Gov (High) |
| `cjis_5_9_3` | CJIS Security Policy v5.9.3 | Law Enforcement |
| `ffiec_cat` | FFIEC Cybersecurity Assessment | Banking |
| `glba_cfr_314` | GLBA CFR 314 (Dec 2023) | Financial Privacy |
| `nerc_cip_2024` | NERC CIP 2024 | Energy/Utilities |
| `fedramp_r5_low` | FedRAMP R5 Low | Federal (Low) |
| `fedramp_r5_high` | FedRAMP R5 High | Federal (High) |
| `fedramp_r5_lisaas` | FedRAMP R5 Li-SaaS | Federal (SaaS) |
| `fedramp_r4_moderate` | FedRAMP R4 Moderate | Federal (Legacy) |
| `nist_800_171_r2` | NIST SP 800-171 R2 | CUI Protection |
| `nist_800_171_r3` | NIST SP 800-171 R3 | CUI Protection (New) |
| `nist_800_172` | NIST SP 800-172 | Enhanced CUI |
| `nist_800_161_r1` | NIST SP 800-161 R1 | Supply Chain |
| `cmmc_2_0_level_3` | CMMC 2.0 Level 3 | Defense (Expert) |
| `dfars_252_204_7012` | DFARS 252.204-7012 | Defense Contractors |
| `irs_1075` | IRS Publication 1075 | Tax Data |
| `ccpa_cpra` | CCPA/CPRA | California Privacy |
| `nydfs_500` | NY DFS 500 | NY Financial |

### Tier 3: Global Regional (45 frameworks)

#### Europe (20)
| Framework ID | Full Name |
|-------------|-----------|
| `eba_ict_guidelines` | EBA ICT Guidelines |
| `psd2` | PSD2 Payment Services |
| `uk_caf_3_1` | UK CAF v3.1 |
| `uk_def_stan_05_138` | UK Defence Standard 05-138 |
| `france_anssi` | France ANSSI Guidelines |
| `spain_ens` | Spain ENS (BOE-A-2022-7191) |
| `italy_acn` | Italy ACN Framework |
| `belgium_ccb` | Belgium CCB Guidelines |
| `austria_nis` | Austria NIS Implementation |
| `switzerland_finma` | Switzerland FINMA |
| `poland_ksc` | Poland KSC Act |
| `czech_nukib` | Czech NUKIB |
| `hungary_nbsz` | Hungary NBSZ |
| `romania_dnsc` | Romania DNSC |
| `greece_nca` | Greece NCA |
| `portugal_cncs` | Portugal CNCS |
| `ireland_ncsc` | Ireland NCSC |
| `denmark_cfcs` | Denmark CFCS |
| `finland_traficom` | Finland Traficom |
| `eu_enisa_5g` | ENISA 5G Security |

#### Asia-Pacific (15)
| Framework ID | Full Name |
|-------------|-----------|
| `japan_ismap` | Japan ISMAP |
| `japan_pipa` | Japan PIPA (Privacy) |
| `korea_isms_p` | Korea ISMS-P |
| `korea_pipa` | Korea PIPA |
| `china_mlps_2_0` | China MLPS 2.0 |
| `china_dsl` | China Data Security Law |
| `china_pipl` | China PIPL |
| `india_dpdpa_2023` | India DPDPA 2023 |
| `india_cert_in` | India CERT-IN |
| `taiwan_pdpa` | Taiwan PDPA |
| `philippines_dpa` | Philippines DPA |
| `thailand_pdpa` | Thailand PDPA |
| `vietnam_cybersecurity` | Vietnam Cybersecurity Law |
| `indonesia_pp71` | Indonesia PP 71 |
| `malaysia_pdpa` | Malaysia PDPA |

#### Middle East & Africa (10)
| Framework ID | Full Name |
|-------------|-----------|
| `saudi_sama_csf` | Saudi SAMA CSF |
| `saudi_ndmo` | Saudi NDMO |
| `saudi_pdpl` | Saudi PDPL |
| `saudi_cgiot` | Saudi CGIoT-1 |
| `uae_niaf` | UAE NIAF |
| `uae_pdp` | UAE PDP Law |
| `qatar_nia` | Qatar NIA |
| `bahrain_pdpl` | Bahrain PDPL |
| `south_africa_popia` | South Africa POPIA |
| `kenya_dpa` | Kenya DPA |

### Tier 4: Specialized & OT (25 frameworks)

#### Industrial/OT (8)
| Framework ID | Full Name |
|-------------|-----------|
| `iec_62443_4_2` | IEC 62443-4-2:2019 Industrial Security |
| `iec_62443_3_3` | IEC 62443-3-3 System Security |
| `iec_62443_2_4` | IEC 62443-2-4 Service Providers |
| `nist_800_82_r3` | NIST SP 800-82 R3 OT Security |
| `api_1164` | API 1164 Pipeline Security |
| `awwa_cybersecurity` | AWWA Water Cybersecurity |
| `isa_99` | ISA-99 Industrial Automation |
| `enisa_smart_grid` | ENISA Smart Grid Security |

#### Healthcare (5)
| Framework ID | Full Name |
|-------------|-----------|
| `hitrust_csf_11` | HITRUST CSF v11 |
| `iec_80001` | IEC 80001 Medical IT Networks |
| `iec_62304` | IEC 62304 Medical Device Software |
| `fda_premarket` | FDA Premarket Cybersecurity |
| `nz_hisf` | NZ Health Info Security Framework |

#### Automotive & IoT (6)
| Framework ID | Full Name |
|-------------|-----------|
| `iso_sae_21434` | ISO/SAE 21434:2021 Automotive |
| `unece_wp29` | UNECE WP.29 R155/R156 |
| `iec_tr_60601_4_5` | IEC TR 60601-4-5:2021 Medical |
| `etsi_en_303_645` | ETSI EN 303 645 Consumer IoT |
| `nistir_8259` | NISTIR 8259 IoT Baseline |
| `csa_iot_baseline` | CSA IoT Security Baseline |

#### Supply Chain & Privacy (6)
| Framework ID | Full Name |
|-------------|-----------|
| `nist_800_161_r1_low` | NIST 800-161 R1 Low Baseline |
| `nist_800_161_r1_mod` | NIST 800-161 R1 Moderate |
| `nist_800_161_r1_high` | NIST 800-161 R1 High |
| `us_dpf` | US Data Privacy Framework |
| `apec_cbpr` | APEC CBPR |
| `iso_27036` | ISO/IEC 27036 Supplier Security |

### Tier 5: Remaining Frameworks (~149 frameworks)

All remaining SCF 2025.2 frameworks including:
- Legacy versions of standards
- Regional variations
- Sector-specific addendums
- Compliance questionnaire variants

---

## Technical Implementation

### Phase 1: Data Extraction (All Tiers)

**Step 1.1: Obtain SCF 2025.2 Full Dataset**
```bash
# Download from SCF website or GitHub
# File: SCF_2025.2.xlsx (full spreadsheet with all 255 frameworks)
```

**Step 1.2: Create Extraction Script**
```python
# scripts/extract_scf_frameworks.py
# - Parse SCF Excel/CSV
# - Extract all framework columns
# - Generate scf-controls.json with all 255 frameworks
# - Generate framework-to-scf.json reverse index
```

**Step 1.3: Update Data Files**
```
src/security_controls_mcp/data/
├── scf-controls.json        # Add all framework mappings
└── framework-to-scf.json    # Rebuild reverse index
```

### Phase 2: Framework Registry Update

**Step 2.1: Update `data_loader.py`**
```python
# Add all 255 framework display names to framework_names dict
framework_names = {
    # Tier 0: AI & Emerging
    "iso_42001_2023": "ISO/IEC 42001:2023 (AI Management System)",
    "nist_ai_rmf": "NIST AI 100-1 (AI Risk Management Framework)",
    "eu_ai_act": "EU AI Act (Regulation 2024/1689)",
    "eu_cyber_resilience_act": "EU Cyber Resilience Act",
    # ... all 255 frameworks
}
```

**Step 2.2: Add Framework Categories (New Feature)**
```python
# New: Organize frameworks by category for better UX
framework_categories = {
    "ai_governance": ["iso_42001_2023", "nist_ai_rmf", "eu_ai_act"],
    "cloud_security": ["iso_27017_2015", "iso_27018_2014", "csa_ccm_4"],
    "privacy": ["gdpr", "iso_27701_2019", "ccpa_cpra", ...],
    "us_federal": ["fedramp_r5_moderate", "nist_800_53_r5", ...],
    "financial": ["pci_dss_4.0.1", "sox", "glba_cfr_314", ...],
    "healthcare": ["hipaa_security_rule", "hitrust_csf_11", ...],
    "industrial_ot": ["iec_62443_4_2", "nerc_cip_2024", ...],
    # ... etc
}
```

### Phase 3: Enhanced Tools

**Step 3.1: Update `list_frameworks` Tool**
```python
# Add optional category filter
def list_frameworks(category: str | None = None) -> list[dict]:
    """
    List all supported frameworks.

    Args:
        category: Optional filter (ai_governance, cloud_security,
                  privacy, us_federal, financial, healthcare,
                  industrial_ot, regional_eu, regional_apac, etc.)
    """
```

**Step 3.2: Add `get_framework_info` Tool**
```python
def get_framework_info(framework_id: str) -> dict:
    """
    Get detailed info about a framework including:
    - Full name and version
    - Category
    - Issuing body
    - Applicability (sectors, regions)
    - Related frameworks
    - Total control count
    """
```

**Step 3.3: Add `find_related_frameworks` Tool**
```python
def find_related_frameworks(framework_id: str) -> list[dict]:
    """
    Find frameworks related to the given one.
    E.g., iso_27001_2022 → iso_27017, iso_27018, iso_27701
    """
```

### Phase 4: Testing

**Step 4.1: Unit Tests**
```python
# tests/test_all_frameworks.py
def test_all_frameworks_loadable():
    """Verify all 255 frameworks load correctly."""

def test_framework_control_counts():
    """Verify each framework has expected control count."""

def test_cross_framework_mapping():
    """Test mapping between various framework pairs."""
```

**Step 4.2: Integration Tests**
```python
# Test MCP tool responses for all frameworks
def test_list_frameworks_returns_255():
    result = list_frameworks()
    assert len(result) == 255

def test_tier0_frameworks_available():
    for fw in ["iso_42001_2023", "nist_ai_rmf", "eu_ai_act"]:
        assert fw in scf_data.frameworks
```

### Phase 5: Documentation

**Step 5.1: Update `docs/coverage.md`**
- Full list of 255 frameworks
- Control counts per framework
- Category organization
- Version information

**Step 5.2: Update `README.md`**
- Highlight 255 framework coverage
- Feature AI governance frameworks prominently
- Update quick start examples

**Step 5.3: Create `docs/frameworks/` Directory**
```
docs/frameworks/
├── ai-governance.md      # ISO 42001, NIST AI RMF, EU AI Act
├── cloud-security.md     # ISO 27017/27018, CSA CCM
├── privacy.md            # GDPR, ISO 27701, CCPA
├── us-federal.md         # FedRAMP, NIST, CMMC
├── financial.md          # PCI, SOX, GLBA, FFIEC
├── healthcare.md         # HIPAA, HITRUST
├── industrial-ot.md      # IEC 62443, NERC CIP
└── regional/
    ├── europe.md
    ├── asia-pacific.md
    └── middle-east-africa.md
```

---

## Implementation Sequence

### Week 1: Tier 0 - AI & Emerging (Immediate)

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | Download SCF 2025.2 full dataset | `scf-2025.2.xlsx` |
| 1 | Create extraction script | `scripts/extract_scf_frameworks.py` |
| 2 | Extract Tier 0 frameworks | Updated `scf-controls.json` |
| 2 | Update `data_loader.py` | 4 new frameworks in registry |
| 3 | Write tests for Tier 0 | `tests/test_tier0_frameworks.py` |
| 3 | Update documentation | README, coverage.md |
| 4 | Release v0.4.0 | PyPI publish |

### Week 2: Tier 1 + 2 - Enterprise & US Deep

| Day | Task | Deliverable |
|-----|------|-------------|
| 1-2 | Extract Tier 1 frameworks (12) | Data files updated |
| 2-3 | Extract Tier 2 frameworks (20) | Data files updated |
| 4 | Add framework categories feature | New tool enhancement |
| 5 | Testing + documentation | Full test coverage |
| 5 | Release v0.5.0 | PyPI publish |

### Week 3: Tier 3 - Global Regional

| Day | Task | Deliverable |
|-----|------|-------------|
| 1-2 | Extract Europe frameworks (20) | Data files updated |
| 2-3 | Extract APAC frameworks (15) | Data files updated |
| 3-4 | Extract MEA frameworks (10) | Data files updated |
| 5 | Testing + documentation | Regional docs |
| 5 | Release v0.6.0 | PyPI publish |

### Week 4: Tier 4 + 5 - Specialized & Complete

| Day | Task | Deliverable |
|-----|------|-------------|
| 1-2 | Extract OT/Industrial (8) | Data files updated |
| 2-3 | Extract Healthcare/Auto/IoT (17) | Data files updated |
| 3-4 | Extract remaining Tier 5 (~149) | Complete coverage |
| 5 | Final testing + documentation | All 255 frameworks |
| 5 | Release v1.0.0 | Major version - complete coverage |

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Frameworks supported | 28 | 255 |
| AI governance frameworks | 0 | 4 |
| Regional coverage | 8 countries | 50+ countries |
| OT/Industrial frameworks | 0 | 8 |
| Healthcare frameworks | 1 (HIPAA) | 5 |

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| SCF data format changes | Pin to SCF 2025.2, document extraction process |
| Large data file size | Lazy loading, optional framework packs |
| Framework ID conflicts | Strict naming convention with version numbers |
| Missing mappings in SCF | Document gaps, contribute upstream to SCF |

## Version Strategy

| Version | Content | Marketing |
|---------|---------|-----------|
| v0.4.0 | Tier 0 (AI) | "First MCP with ISO 42001 + EU AI Act" |
| v0.5.0 | Tier 1+2 | "Enterprise-ready with 60+ frameworks" |
| v0.6.0 | Tier 3 | "Global compliance across 50+ countries" |
| v1.0.0 | All tiers | "THE definitive security framework MCP - 255 frameworks" |

---

## Files to Create/Modify

### New Files
- `scripts/extract_scf_frameworks.py` - Data extraction script
- `docs/frameworks/*.md` - Framework category documentation
- `tests/test_all_frameworks.py` - Comprehensive framework tests

### Modified Files
- `src/security_controls_mcp/data/scf-controls.json` - Add all framework mappings
- `src/security_controls_mcp/data/framework-to-scf.json` - Rebuild reverse index
- `src/security_controls_mcp/data_loader.py` - Add 255 framework names + categories
- `src/security_controls_mcp/tools/list_frameworks.py` - Add category filter
- `docs/coverage.md` - Full framework documentation
- `README.md` - Update marketing copy
- `pyproject.toml` - Version bumps

---

## Appendix: Complete Framework ID List

See attached `framework-ids-complete.csv` for the full list of 255 framework IDs with:
- Framework ID (snake_case)
- Full display name
- Category
- Tier
- SCF column reference
