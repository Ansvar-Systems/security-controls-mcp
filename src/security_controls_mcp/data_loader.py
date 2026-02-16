"""Data loader for SCF controls and framework mappings."""

import json
from pathlib import Path
from typing import Any


class SCFData:
    """Loads and provides access to SCF control data."""

    def __init__(self):
        self.controls: list[dict[str, Any]] = []
        self.controls_by_id: dict[str, dict[str, Any]] = {}
        self.framework_to_scf: dict[str, dict[str, list[str]]] = {}
        self.frameworks: dict[str, dict[str, Any]] = {}
        self.framework_categories: dict[str, list[str]] = {}
        self._load_data()

    def _load_data(self):
        """Load SCF controls and reverse index from JSON files."""
        data_dir = Path(__file__).parent / "data"

        # Load controls
        with open(data_dir / "scf-controls.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            self.controls = data["controls"]

        # Build ID index
        self.controls_by_id = {ctrl["id"]: ctrl for ctrl in self.controls}

        # Load reverse index
        with open(data_dir / "framework-to-scf.json", "r", encoding="utf-8") as f:
            self.framework_to_scf = json.load(f)

        # Build framework metadata
        self._build_framework_metadata()

    def _build_framework_metadata(self):
        """Build framework metadata from controls."""
        # Complete framework display names for all 261 frameworks in SCF 2025.4
        framework_names = {
            # === TIER 0: AI GOVERNANCE ===
            "iso_42001_2023": "ISO/IEC 42001:2023 (AI Management System)",
            "nist_ai_rmf_1.0": "NIST AI 100-1 (AI Risk Management Framework) 1.0",
            "nist_ai_600_1": "NIST AI 600-1 (Generative AI Profile)",
            "eu_ai_act": "EU AI Act (Regulation 2024/1689)",
            "eu_cyber_resilience_act": "EU Cyber Resilience Act",
            "eu_cra_annexes": "EU Cyber Resilience Act Annexes",
            # === CORE FRAMEWORKS ===
            # SOC 2 / Audit
            "soc_2_tsc": "AICPA TSC 2017:2022 (SOC 2)",
            # CIS Controls
            "cis_csc_8.1": "CIS Critical Security Controls v8.1",
            "cis_csc_8.1_ig1": "CIS CSC v8.1 Implementation Group 1",
            "cis_csc_8.1_ig2": "CIS CSC v8.1 Implementation Group 2",
            "cis_csc_8.1_ig3": "CIS CSC v8.1 Implementation Group 3",
            # Governance
            "cobit_2019": "COBIT 2019",
            "coso_2017": "COSO 2017",
            # === CLOUD SECURITY ===
            "csa_ccm_4": "CSA Cloud Controls Matrix v4",
            "csa_iot_scf_2": "CSA IoT Security Controls Framework 2",
            "germany_c5_2020": "Germany C5:2020 (Cloud)",
            # === ISO STANDARDS ===
            "iso_27001_2022": "ISO/IEC 27001:2022",
            "iso_27002_2022": "ISO/IEC 27002:2022",
            "iso_27017_2015": "ISO/IEC 27017:2015 (Cloud Security)",
            "iso_27018_2014": "ISO/IEC 27018:2014 (Cloud Privacy)",
            "iso_27701_2025": "ISO/IEC 27701:2025 (Privacy Extension)",
            "iso_22301_2019": "ISO/IEC 22301:2019 (Business Continuity)",
            "iso_29100_2024": "ISO/IEC 29100:2024 (Privacy Framework)",
            "iso_31000_2009": "ISO 31000:2009 (Risk Management)",
            "iso_31010_2009": "ISO 31010:2009 (Risk Assessment)",
            "iso_sae_21434_2021": "ISO/SAE 21434:2021 (Automotive Cybersecurity)",
            # === INDUSTRIAL / OT ===
            "iec_62443_4_2_2019": "IEC 62443-4-2:2019 (Industrial Security)",
            "iec_tr_60601_4_5_2021": "IEC TR 60601-4-5:2021 (Medical IT)",
            "nerc_cip_2024": "NERC CIP 2024",
            "nist_800_82_r3_low": "NIST SP 800-82 R3 OT Overlay (Low)",
            "nist_800_82_r3_moderate": "NIST SP 800-82 R3 OT Overlay (Moderate)",
            "nist_800_82_r3_high": "NIST SP 800-82 R3 OT Overlay (High)",
            "imo_maritime_cyber": "IMO Maritime Cyber Risk Management",
            # === PRIVACY FRAMEWORKS ===
            "gdpr": "General Data Protection Regulation (GDPR)",
            "nist_privacy_framework_1.0": "NIST Privacy Framework 1.0",
            "apec_privacy_2015": "APEC Privacy Framework 2015",
            "gapp": "Generally Accepted Privacy Principles (GAPP)",
            "oecd_privacy": "OECD Privacy Principles",
            "us_dpf": "US Data Privacy Framework",
            # === NIST FRAMEWORKS ===
            "nist_csf_2.0": "NIST Cybersecurity Framework 2.0",
            "nist_800_37_r2": "NIST SP 800-37 R2 (Risk Management Framework)",
            "nist_800_39": "NIST SP 800-39 (Risk Management)",
            "nist_800_53_r4": "NIST SP 800-53 R4",
            "nist_800_53_r4_low": "NIST SP 800-53 R4 (Low)",
            "nist_800_53_r4_moderate": "NIST SP 800-53 R4 (Moderate)",
            "nist_800_53_r4_high": "NIST SP 800-53 R4 (High)",
            "nist_800_53_r5": "NIST SP 800-53 R5",
            "nist_800_53b_r5_privacy": "NIST SP 800-53B R5 (Privacy)",
            "nist_800_53b_r5_low": "NIST SP 800-53B R5 (Low)",
            "nist_800_53b_r5_moderate": "NIST SP 800-53B R5 (Moderate)",
            "nist_800_53b_r5_high": "NIST SP 800-53B R5 (High)",
            "nist_800_53_r5_noc": "NIST SP 800-53 R5 (NOC)",
            "nist_800_63b": "NIST SP 800-63B (Digital Identity)",
            "nist_800_160": "NIST SP 800-160 (Systems Security Engineering)",
            "nist_800_161_r1": "NIST SP 800-161 R1 (Supply Chain)",
            "nist_800_161_r1_baseline": "NIST SP 800-161 R1 C-SCRM Baseline",
            "nist_800_161_r1_flowdown": "NIST SP 800-161 R1 Flow Down",
            "nist_800_161_r1_level1": "NIST SP 800-161 R1 Level 1",
            "nist_800_161_r1_level2": "NIST SP 800-161 R1 Level 2",
            "nist_800_161_r1_level3": "NIST SP 800-161 R1 Level 3",
            "nist_800_171_r2": "NIST SP 800-171 R2 (CUI)",
            "nist_800_171a": "NIST SP 800-171A (Assessment)",
            "nist_800_171_r3": "NIST SP 800-171 R3 (CUI)",
            "nist_800_171a_r3": "NIST SP 800-171A R3 (Assessment)",
            "nist_800_172": "NIST SP 800-172 (Enhanced CUI)",
            "nist_800_207": "NIST SP 800-207 (Zero Trust)",
            "nist_800_218": "NIST SP 800-218 (SSDF)",
            # === FEDRAMP ===
            "fedramp_r4": "FedRAMP R4",
            "fedramp_r4_low": "FedRAMP R4 (Low)",
            "fedramp_r4_moderate": "FedRAMP R4 (Moderate)",
            "fedramp_r4_high": "FedRAMP R4 (High)",
            "fedramp_r4_lisaas": "FedRAMP R4 (LI-SaaS)",
            "fedramp_r5": "FedRAMP R5",
            "fedramp_r5_low": "FedRAMP R5 (Low)",
            "fedramp_r5_moderate": "FedRAMP R5 (Moderate)",
            "fedramp_r5_high": "FedRAMP R5 (High)",
            "fedramp_r5_lisaas": "FedRAMP R5 (LI-SaaS)",
            # === GOVRAMP / STATERAMP ===
            "govramp_core": "GovRAMP Core",
            "govramp_low": "GovRAMP Low",
            "govramp_low_plus": "GovRAMP Low+",
            "govramp_moderate": "GovRAMP Moderate",
            "govramp_high": "GovRAMP High",
            # === CMMC ===
            "cmmc_2.0_level_1": "CMMC 2.0 Level 1",
            "cmmc_2.0_level_1_aos": "CMMC 2.0 Level 1 AOs",
            "cmmc_2.0_level_2": "CMMC 2.0 Level 2",
            "cmmc_2.0_level_3": "CMMC 2.0 Level 3",
            # === PCI DSS ===
            "pci_dss_4.0.1": "PCI DSS v4.0.1",
            "pci_dss_4.0.1_saq_a": "PCI DSS v4.0.1 SAQ A",
            "pci_dss_4.0.1_saq_a_ep": "PCI DSS v4.0.1 SAQ A-EP",
            "pci_dss_4.0.1_saq_b": "PCI DSS v4.0.1 SAQ B",
            "pci_dss_4.0.1_saq_b_ip": "PCI DSS v4.0.1 SAQ B-IP",
            "pci_dss_4.0.1_saq_c": "PCI DSS v4.0.1 SAQ C",
            "pci_dss_4.0.1_saq_c_vt": "PCI DSS v4.0.1 SAQ C-VT",
            "pci_dss_4.0.1_saq_d_merchant": "PCI DSS v4.0.1 SAQ D (Merchant)",
            "pci_dss_4.0.1_saq_d_sp": "PCI DSS v4.0.1 SAQ D (Service Provider)",
            "pci_dss_4.0.1_saq_p2pe": "PCI DSS v4.0.1 SAQ P2PE",
            # === HEALTHCARE ===
            "hipaa_security_rule": "HIPAA Security Rule / NIST SP 800-66 R2",
            "hipaa_admin_2013": "HIPAA Administrative Simplification 2013",
            "hipaa_hicp_small": "HIPAA HICP Small Practice",
            "hipaa_hicp_medium": "HIPAA HICP Medium Practice",
            "hipaa_hicp_large": "HIPAA HICP Large Practice",
            "cms_mars_e_2.0": "CMS MARS-E 2.0 (Healthcare Exchanges)",
            "hhs_45_cfr_155_260": "HHS 45 CFR 155.260",
            # === US FINANCIAL ===
            "sox": "Sarbanes-Oxley Act (SOX)",
            "glba_cfr_314_2023": "GLBA CFR 314 (Dec 2023)",
            "ffiec": "FFIEC Cybersecurity Assessment",
            "us_finra": "US FINRA",
            "sec_cybersecurity_rule": "SEC Cybersecurity Rule",
            "us_facta": "US FACTA",
            "ftc_act": "FTC Act",
            "naic_mdl_668": "NAIC Insurance Data Security Model Law (MDL-668)",
            "fca_crm": "FCA CRM",
            # === US FEDERAL / DEFENSE ===
            "cjis_5.9.3": "CJIS Security Policy v5.9.3",
            "irs_1075": "IRS Publication 1075",
            "dfars_252_204_70xx": "DFARS 252.204-70xx (Cybersecurity)",
            "far_52_204_21": "FAR 52.204-21 (Basic Safeguarding)",
            "far_52_204_25": "FAR 52.204-25 (NDAA Section 889)",
            "far_52_204_27": "FAR 52.204-27",
            "itar_part_120": "ITAR Part 120",
            "nispom_2020": "NISPOM 2020",
            "us_nnpi": "US NNPI (Unclassified)",
            "nstc_nspm_33": "NSTC NSPM-33",
            "eo_14028": "EO 14028 (Improving Cybersecurity)",
            "dod_zt_roadmap": "DoD Zero Trust Execution Roadmap",
            "dod_ztra_2.0": "DoD Zero Trust Reference Architecture 2.0",
            "dhs_cisa_ssdaf": "DHS CISA SSDAF",
            "dhs_cisa_tic_3.0": "DHS CISA TIC 3.0",
            "dhs_ztcf": "DHS Zero Trust Capability Framework",
            "us_cisa_cpg_2022": "CISA Cross-Sector CPG 2022",
            "us_c2m2_2.1": "US C2M2 2.1 (Capability Maturity)",
            "us_cert_rmm_1.2": "US CERT RMM 1.2 (Resilience)",
            "us_ferpa": "US FERPA (Education Privacy)",
            "us_fipps": "US FIPPs (Fair Information Practice)",
            "us_coppa": "US COPPA (Children's Privacy)",
            "fda_21_cfr_part_11": "FDA 21 CFR Part 11 (Electronic Records)",
            "tsa_dhs_1580_82_2022": "TSA/DHS 1580/82-2022-01",
            "ssa_eiesr_8.0": "SSA EIESR 8.0",
            # === US STATE LAWS ===
            "us_ca_ccpa_2025": "California CCPA/CPRA 2025",
            "us_ca_sb327": "California SB327 (IoT)",
            "us_ca_sb1386": "California SB1386",
            "nydfs_500_2023": "NY DFS 23 NYCRR 500 (2023 Amendment)",
            "us_ny_shield": "New York SHIELD Act",
            "us_co_cpa": "Colorado Privacy Act",
            "us_va_cdpa_2025": "Virginia CDPA 2025",
            "us_or_cpa": "Oregon Consumer Privacy Act",
            "us_or_646a": "Oregon 646A",
            "us_tn_tipa": "Tennessee TIPA",
            "tx_ramp_level_1": "TX-RAMP Level 1",
            "tx_ramp_level_2": "TX-RAMP Level 2",
            "us_tx_cdpa": "Texas CDPA",
            "us_tx_dir_2.0": "Texas DIR Control Standards 2.0",
            "us_tx_bc521": "Texas BC521",
            "us_tx_sb820": "Texas SB 820",
            "us_tx_sb2610": "Texas SB 2610",
            "us_ma_201_cmr_17": "Massachusetts 201 CMR 17.00",
            "us_il_bipa": "Illinois BIPA (Biometric)",
            "us_il_ipa": "Illinois IPA",
            "us_il_pipa": "Illinois PIPA",
            "us_nv_noge_reg_5": "Nevada NOGE Reg 5",
            "us_nv_sb220": "Nevada SB220",
            "us_ak_pipa": "Alaska PIPA",
            "us_vt_act_171": "Vermont Act 171 of 2018",
            # === EU REGULATIONS ===
            "dora": "Digital Operational Resilience Act (DORA)",
            "nis2": "NIS2 Directive",
            "nis2_annex": "NIS2 Directive Annex",
            "psd2": "PSD2 (Payment Services Directive)",
            "eu_eba_gl_2019_04": "EU EBA GL/2019/04",
            # === EMEA NATIONAL ===
            "uk_caf_4.0": "UK Cyber Assessment Framework 4.0",
            "uk_cyber_essentials": "UK Cyber Essentials",
            "uk_dpa": "UK Data Protection Act",
            "uk_defstan_05_138": "UK DEFSTAN 05-138",
            "uk_cap_1850": "UK CAP 1850",
            "germany": "Germany Cybersecurity",
            "germany_bait": "Germany BAIT (Banking IT)",
            "bsi_200_1": "BSI Standard 200-1",
            "netherlands": "Netherlands Cybersecurity",
            "norway": "Norway Cybersecurity",
            "sweden": "Sweden Cybersecurity",
            "austria": "Austria Cybersecurity",
            "belgium": "Belgium Cybersecurity",
            "ireland": "Ireland Cybersecurity",
            "italy": "Italy Cybersecurity",
            "greece": "Greece Cybersecurity",
            "hungary": "Hungary Cybersecurity",
            "poland": "Poland Cybersecurity",
            "spain_boe_a_2022_7191": "Spain BOE-A-2022-7191",
            "spain_1720_2007": "Spain 1720/2007",
            "spain_311_2022": "Spain 311/2022",
            "spain_ccn_stic_825": "Spain CCN-STIC 825",
            "switzerland": "Switzerland Cybersecurity",
            "turkey": "Turkey Cybersecurity",
            "russia": "Russia Cybersecurity",
            "serbia_87_2018": "Serbia 87/2018",
            "enisa_2.0": "ENISA 2.0",
            # === MIDDLE EAST / AFRICA ===
            "israel": "Israel Cybersecurity",
            "israel_cdmo_1.0": "Israel CDMO 1.0",
            "saudi_sama_csf_1.0": "Saudi Arabia SAMA CSF 1.0",
            "saudi_cscc_1_2019": "Saudi Arabia CSCC-1 2019",
            "saudi_ecc_1_2018": "Saudi Arabia ECC-1 2018",
            "saudi_otcc_1_2022": "Saudi Arabia OTCC-1 2022",
            "saudi_cgiot_1_2024": "Saudi Arabia IoT CGIoT-1 2024",
            "saudi_pdpl": "Saudi Arabia PDPL",
            "saudi_sacs_002": "Saudi Arabia SACS-002",
            "uae_niaf": "UAE NIAF",
            "qatar_pdppl": "Qatar PDPPL",
            "south_africa": "South Africa (POPIA)",
            "kenya_dpa_2019": "Kenya DPA 2019",
            "nigeria_dpr_2019": "Nigeria DPR 2019",
            # === APAC ===
            "australia_essential_8": "Australian Essential Eight",
            "australia_ism_2024": "Australian ISM (June 2024)",
            "australia_privacy_act": "Australian Privacy Act",
            "australia_privacy_principles": "Australian Privacy Principles",
            "australia_iot_cop": "Australia IoT Code of Practice",
            "australia_cps_230": "Australia Prudential Standard CPS 230",
            "australia_cps_234": "Australia Prudential Standard CPS 234",
            "singapore": "Singapore Cybersecurity",
            "singapore_cyber_hygiene": "Singapore Cyber Hygiene Practice",
            "singapore_mas_trm_2021": "Singapore MAS TRM 2021",
            "japan_appi": "Japan APPI",
            "japan_ismap": "Japan ISMAP",
            "china_cybersecurity_law": "China Cybersecurity Law",
            "china_data_security_law": "China Data Security Law",
            "china_privacy_law": "China Privacy Law (PIPL)",
            "china_dnsip": "China DNSIP",
            "hong_kong": "Hong Kong Cybersecurity",
            "india_dpdpa_2023": "India DPDPA 2023",
            "india_itr": "India ITR",
            "india_sebi_cscrf": "India SEBI CSCRF",
            "south_korea": "South Korea Cybersecurity",
            "taiwan": "Taiwan Cybersecurity",
            "malaysia": "Malaysia Cybersecurity",
            "philippines": "Philippines Cybersecurity",
            "nz_hisf_2022": "New Zealand HISF 2022",
            "nz_hisf_suppliers_2023": "New Zealand HISF Suppliers 2023",
            "nz_nzism_3.6": "New Zealand NZISM 3.6",
            "nz_privacy_act_2020": "New Zealand Privacy Act 2020",
            # === AMERICAS (non-US) ===
            "canada_pipeda": "Canada PIPEDA",
            "canada_csag": "Canada CSAG",
            "canada_osfi_b13": "Canada OSFI B-13",
            "canada_itsp_10_171": "Canada ITSP-10-171",
            "brazil_lgpd": "Brazil LGPD",
            "argentina_ppl": "Argentina PPL",
            "argentina_reg_132_2018": "Argentina Reg 132-2018",
            "mexico": "Mexico Cybersecurity",
            "chile": "Chile Cybersecurity",
            "colombia": "Colombia Cybersecurity",
            "peru": "Peru Cybersecurity",
            "costa_rica": "Costa Rica Cybersecurity",
            "uruguay": "Uruguay Cybersecurity",
            "bahamas": "Bahamas Cybersecurity",
            "bermuda_bmaccc": "Bermuda BMACCC",
            # === AUTOMOTIVE ===
            "tisax_isa_6": "TISAX ISA 6 (Automotive)",
            "un_r155": "UN R155 (Vehicle Cybersecurity)",
            "un_ece_wp29": "UN ECE WP.29 (Automotive)",
            "ul_2900_1_2017": "UL 2900-1:2017 (Software Cybersecurity)",
            # === OTHER INDUSTRY ===
            "swift_cscf_2023": "SWIFT Customer Security Framework 2023",
            "shared_assessments_sig_2025": "Shared Assessments SIG 2025",
            "sparta": "SPARTA (Space Attack Research)",
            "mpa_csp_5.1": "MPA Content Security Program 5.1",
            "owasp_top_10_2021": "OWASP Top 10 2021",
            "mitre_attack_10": "MITRE ATT&CK v10",
        }

        # Framework categories for filtering
        # Every framework MUST be in at least one category for discoverability.
        # A framework may appear in multiple categories where appropriate.
        self.framework_categories = {
            # === AI & EMERGING TECHNOLOGY ===
            "ai_governance": [
                "iso_42001_2023",
                "nist_ai_rmf_1.0",
                "nist_ai_600_1",
                "eu_ai_act",
                "eu_cyber_resilience_act",
                "eu_cra_annexes",
            ],
            # === CORE SECURITY FRAMEWORKS ===
            "iso_standards": [
                "iso_27001_2022",
                "iso_27002_2022",
                "iso_27017_2015",
                "iso_27018_2014",
                "iso_27701_2025",
                "iso_22301_2019",
                "iso_29100_2024",
                "iso_31000_2009",
                "iso_31010_2009",
                "iso_sae_21434_2021",
                "iso_42001_2023",
            ],
            "nist_frameworks": [
                "nist_csf_2.0",
                "nist_800_37_r2",
                "nist_800_39",
                "nist_800_53_r4",
                "nist_800_53_r4_low",
                "nist_800_53_r4_moderate",
                "nist_800_53_r4_high",
                "nist_800_53_r5",
                "nist_800_53b_r5_privacy",
                "nist_800_53b_r5_low",
                "nist_800_53b_r5_moderate",
                "nist_800_53b_r5_high",
                "nist_800_53_r5_noc",
                "nist_800_63b",
                "nist_800_160",
                "nist_800_171_r2",
                "nist_800_171a",
                "nist_800_171_r3",
                "nist_800_171a_r3",
                "nist_800_172",
                "nist_800_207",
                "nist_800_218",
                "nist_privacy_framework_1.0",
                "nist_ai_rmf_1.0",
                "nist_ai_600_1",
            ],
            "cis_controls": [
                "cis_csc_8.1",
                "cis_csc_8.1_ig1",
                "cis_csc_8.1_ig2",
                "cis_csc_8.1_ig3",
            ],
            "cloud_security": [
                "iso_27017_2015",
                "iso_27018_2014",
                "csa_ccm_4",
                "csa_iot_scf_2",
                "germany_c5_2020",
            ],
            "governance": [
                "cobit_2019",
                "coso_2017",
                "enisa_2.0",
            ],
            # === PRIVACY ===
            "privacy": [
                "gdpr",
                "iso_27701_2025",
                "iso_29100_2024",
                "nist_privacy_framework_1.0",
                "nist_800_53b_r5_privacy",
                "apec_privacy_2015",
                "gapp",
                "oecd_privacy",
                "us_dpf",
                "us_ca_ccpa_2025",
                "us_co_cpa",
                "us_va_cdpa_2025",
                "us_or_cpa",
                "us_tn_tipa",
                "us_tx_cdpa",
                "us_coppa",
                "us_ferpa",
                "us_fipps",
                "us_il_bipa",
                "us_il_ipa",
                "us_il_pipa",
                "brazil_lgpd",
                "india_dpdpa_2023",
                "china_privacy_law",
                "china_data_security_law",
                "japan_appi",
                "canada_pipeda",
                "south_africa",
                "saudi_pdpl",
                "qatar_pdppl",
                "kenya_dpa_2019",
                "nigeria_dpr_2019",
                "nz_privacy_act_2020",
                "australia_privacy_act",
                "australia_privacy_principles",
                "uk_dpa",
                "argentina_ppl",
            ],
            # === US GOVERNMENT & DEFENSE ===
            "us_federal": [
                "nist_csf_2.0",
                "nist_800_53_r5",
                "nist_800_53b_r5_low",
                "nist_800_53b_r5_moderate",
                "nist_800_53b_r5_high",
                "nist_800_53_r5_noc",
                "nist_800_53_r4",
                "nist_800_53_r4_low",
                "nist_800_53_r4_moderate",
                "nist_800_53_r4_high",
                "nist_800_171_r2",
                "nist_800_171a",
                "nist_800_171_r3",
                "nist_800_171a_r3",
                "nist_800_172",
                "cjis_5.9.3",
                "irs_1075",
                "dfars_252_204_70xx",
                "far_52_204_21",
                "far_52_204_25",
                "far_52_204_27",
                "itar_part_120",
                "nispom_2020",
                "us_nnpi",
                "nstc_nspm_33",
                "eo_14028",
                "dhs_cisa_ssdaf",
                "dhs_cisa_tic_3.0",
                "us_cisa_cpg_2022",
                "us_c2m2_2.1",
                "us_cert_rmm_1.2",
                "tsa_dhs_1580_82_2022",
                "ssa_eiesr_8.0",
                "fda_21_cfr_part_11",
                "hhs_45_cfr_155_260",
            ],
            "fedramp": [
                "fedramp_r4",
                "fedramp_r4_low",
                "fedramp_r4_moderate",
                "fedramp_r4_high",
                "fedramp_r4_lisaas",
                "fedramp_r5",
                "fedramp_r5_low",
                "fedramp_r5_moderate",
                "fedramp_r5_high",
                "fedramp_r5_lisaas",
            ],
            "govramp": [
                "govramp_core",
                "govramp_low",
                "govramp_low_plus",
                "govramp_moderate",
                "govramp_high",
            ],
            "cmmc": [
                "cmmc_2.0_level_1",
                "cmmc_2.0_level_1_aos",
                "cmmc_2.0_level_2",
                "cmmc_2.0_level_3",
            ],
            "zero_trust": [
                "nist_800_207",
                "dod_zt_roadmap",
                "dod_ztra_2.0",
                "dhs_ztcf",
            ],
            # === US STATE LAWS ===
            "us_state_laws": [
                "us_ca_ccpa_2025",
                "us_ca_sb327",
                "us_ca_sb1386",
                "nydfs_500_2023",
                "us_ny_shield",
                "us_co_cpa",
                "us_va_cdpa_2025",
                "us_or_cpa",
                "us_or_646a",
                "us_tn_tipa",
                "us_tx_cdpa",
                "us_tx_dir_2.0",
                "us_tx_bc521",
                "us_tx_sb820",
                "us_tx_sb2610",
                "tx_ramp_level_1",
                "tx_ramp_level_2",
                "us_ma_201_cmr_17",
                "us_il_bipa",
                "us_il_ipa",
                "us_il_pipa",
                "us_nv_noge_reg_5",
                "us_nv_sb220",
                "us_ak_pipa",
                "us_vt_act_171",
            ],
            # === FINANCIAL SERVICES ===
            "financial": [
                "soc_2_tsc",
                "pci_dss_4.0.1",
                "pci_dss_4.0.1_saq_a",
                "pci_dss_4.0.1_saq_a_ep",
                "pci_dss_4.0.1_saq_b",
                "pci_dss_4.0.1_saq_b_ip",
                "pci_dss_4.0.1_saq_c",
                "pci_dss_4.0.1_saq_c_vt",
                "pci_dss_4.0.1_saq_d_merchant",
                "pci_dss_4.0.1_saq_d_sp",
                "pci_dss_4.0.1_saq_p2pe",
                "sox",
                "glba_cfr_314_2023",
                "ffiec",
                "us_finra",
                "sec_cybersecurity_rule",
                "us_facta",
                "ftc_act",
                "naic_mdl_668",
                "fca_crm",
                "dora",
                "psd2",
                "eu_eba_gl_2019_04",
                "swift_cscf_2023",
                "shared_assessments_sig_2025",
                "singapore_mas_trm_2021",
                "saudi_sama_csf_1.0",
                "canada_osfi_b13",
                "australia_cps_230",
                "australia_cps_234",
                "india_sebi_cscrf",
                "germany_bait",
            ],
            # === HEALTHCARE ===
            "healthcare": [
                "hipaa_security_rule",
                "hipaa_admin_2013",
                "hipaa_hicp_small",
                "hipaa_hicp_medium",
                "hipaa_hicp_large",
                "cms_mars_e_2.0",
                "hhs_45_cfr_155_260",
                "fda_21_cfr_part_11",
                "iec_tr_60601_4_5_2021",
            ],
            # === INDUSTRIAL / OT / CRITICAL INFRASTRUCTURE ===
            "industrial_ot": [
                "iec_62443_4_2_2019",
                "nerc_cip_2024",
                "nist_800_82_r3_low",
                "nist_800_82_r3_moderate",
                "nist_800_82_r3_high",
                "imo_maritime_cyber",
                "tsa_dhs_1580_82_2022",
            ],
            # === AUTOMOTIVE ===
            "automotive": [
                "iso_sae_21434_2021",
                "tisax_isa_6",
                "un_r155",
                "un_ece_wp29",
                "ul_2900_1_2017",
            ],
            # === SUPPLY CHAIN ===
            "supply_chain": [
                "nist_800_161_r1",
                "nist_800_161_r1_baseline",
                "nist_800_161_r1_flowdown",
                "nist_800_161_r1_level1",
                "nist_800_161_r1_level2",
                "nist_800_161_r1_level3",
                "nist_800_218",
                "dfars_252_204_70xx",
            ],
            # === THREAT INTELLIGENCE & APPSEC ===
            "threat_intel_appsec": [
                "mitre_attack_10",
                "owasp_top_10_2021",
                "sparta",
            ],
            # === UK ===
            "uk_cybersecurity": [
                "uk_caf_4.0",
                "uk_cyber_essentials",
                "uk_dpa",
                "uk_defstan_05_138",
                "uk_cap_1850",
                "fca_crm",
            ],
            # === EU REGULATIONS ===
            "eu_regulations": [
                "gdpr",
                "dora",
                "nis2",
                "nis2_annex",
                "psd2",
                "eu_ai_act",
                "eu_cyber_resilience_act",
                "eu_cra_annexes",
                "eu_eba_gl_2019_04",
                "enisa_2.0",
            ],
            # === EUROPE NATIONAL ===
            "europe_national": [
                "uk_caf_4.0",
                "uk_cyber_essentials",
                "uk_dpa",
                "uk_defstan_05_138",
                "uk_cap_1850",
                "germany",
                "germany_bait",
                "germany_c5_2020",
                "bsi_200_1",
                "austria",
                "belgium",
                "ireland",
                "italy",
                "greece",
                "hungary",
                "netherlands",
                "norway",
                "poland",
                "sweden",
                "spain_boe_a_2022_7191",
                "spain_1720_2007",
                "spain_311_2022",
                "spain_ccn_stic_825",
                "switzerland",
                "turkey",
                "russia",
                "serbia_87_2018",
                "fca_crm",
            ],
            # === MIDDLE EAST & AFRICA ===
            "middle_east_africa": [
                "israel",
                "israel_cdmo_1.0",
                "saudi_sama_csf_1.0",
                "saudi_cscc_1_2019",
                "saudi_ecc_1_2018",
                "saudi_otcc_1_2022",
                "saudi_cgiot_1_2024",
                "saudi_pdpl",
                "saudi_sacs_002",
                "uae_niaf",
                "qatar_pdppl",
                "south_africa",
                "kenya_dpa_2019",
                "nigeria_dpr_2019",
            ],
            # === ASIA-PACIFIC ===
            "asia_pacific": [
                "australia_essential_8",
                "australia_ism_2024",
                "australia_privacy_act",
                "australia_privacy_principles",
                "australia_iot_cop",
                "australia_cps_230",
                "australia_cps_234",
                "singapore",
                "singapore_cyber_hygiene",
                "singapore_mas_trm_2021",
                "japan_appi",
                "japan_ismap",
                "china_cybersecurity_law",
                "china_data_security_law",
                "china_privacy_law",
                "china_dnsip",
                "hong_kong",
                "india_dpdpa_2023",
                "india_itr",
                "india_sebi_cscrf",
                "south_korea",
                "taiwan",
                "malaysia",
                "philippines",
                "nz_hisf_2022",
                "nz_hisf_suppliers_2023",
                "nz_nzism_3.6",
                "nz_privacy_act_2020",
            ],
            # === AMERICAS (NON-US) ===
            "americas": [
                "canada_pipeda",
                "canada_csag",
                "canada_osfi_b13",
                "canada_itsp_10_171",
                "brazil_lgpd",
                "argentina_ppl",
                "argentina_reg_132_2018",
                "mexico",
                "chile",
                "colombia",
                "peru",
                "costa_rica",
                "uruguay",
                "bahamas",
                "bermuda_bmaccc",
            ],
            # === MEDIA & ENTERTAINMENT ===
            "media_entertainment": [
                "mpa_csp_5.1",
            ],
        }

        # Count controls per framework (only for frameworks that have mappings)
        for fw_key, fw_name in framework_names.items():
            count = sum(1 for ctrl in self.controls if ctrl["framework_mappings"].get(fw_key))
            if count > 0:  # Only include frameworks with actual mappings
                self.frameworks[fw_key] = {
                    "key": fw_key,
                    "name": fw_name,
                    "controls_mapped": count,
                }

    def get_control(self, control_id: str) -> dict[str, Any] | None:
        """Get control by SCF ID."""
        return self.controls_by_id.get(control_id)

    def search_controls(
        self, query: str, frameworks: list[str] | None = None, limit: int = 10
    ) -> list[dict[str, Any]]:
        """Search controls by description. Case-insensitive string matching for v1."""
        query_lower = query.lower()
        results = []

        for ctrl in self.controls:
            # Check if query matches name or description (case-insensitive)
            name_lower = ctrl["name"].lower() if ctrl["name"] else ""
            desc_lower = ctrl["description"].lower() if ctrl["description"] else ""

            if query_lower in name_lower or query_lower in desc_lower:
                # Filter by frameworks if specified
                if frameworks:
                    has_mapping = any(ctrl["framework_mappings"].get(fw) for fw in frameworks)
                    if not has_mapping:
                        continue

                # Get mapped frameworks for response
                mapped_frameworks = [
                    fw for fw, mappings in ctrl["framework_mappings"].items() if mappings
                ]

                # Create snippet (simple version - first 150 chars with highlight)
                desc = ctrl["description"]
                idx = desc.lower().find(query_lower)
                if idx >= 0:
                    start = max(0, idx - 50)
                    end = min(len(desc), idx + len(query) + 100)
                    snippet = desc[start:end]
                    if start > 0:
                        snippet = "..." + snippet
                    if end < len(desc):
                        snippet = snippet + "..."
                else:
                    snippet = desc[:150] + "..." if len(desc) > 150 else desc

                results.append(
                    {
                        "control_id": ctrl["id"],
                        "name": ctrl["name"],
                        "snippet": snippet,
                        "relevance": 1.0,  # Simple scoring for v1
                        "mapped_frameworks": mapped_frameworks,
                    }
                )

                if len(results) >= limit:
                    break

        return results

    def get_framework_controls(
        self, framework: str, include_descriptions: bool = False
    ) -> list[dict[str, Any]]:
        """Get all controls that map to a framework."""
        results = []

        for ctrl in self.controls:
            fw_mappings = ctrl["framework_mappings"].get(framework)
            if fw_mappings:
                result = {
                    "scf_id": ctrl["id"],
                    "scf_name": ctrl["name"],
                    "framework_control_ids": fw_mappings,
                    "weight": ctrl["weight"],
                }

                if include_descriptions:
                    result["description"] = ctrl["description"]

                results.append(result)

        return results

    def map_frameworks(
        self,
        source_framework: str,
        target_framework: str,
        source_control: str | None = None,
    ) -> list[dict[str, Any]]:
        """Map controls between two frameworks via SCF."""
        results = []

        # If source_control specified, filter to only controls with that mapping
        for ctrl in self.controls:
            source_mappings = ctrl["framework_mappings"].get(source_framework)
            target_mappings = ctrl["framework_mappings"].get(target_framework)

            # Skip if no source mapping
            if not source_mappings:
                continue

            # Filter by source_control if specified
            if source_control and source_control not in source_mappings:
                continue

            results.append(
                {
                    "scf_id": ctrl["id"],
                    "scf_name": ctrl["name"],
                    "source_controls": source_mappings,
                    "target_controls": target_mappings or [],
                    "weight": ctrl["weight"],
                }
            )

        return results
