# Paid Standards Import Guide

Import your purchased security standards (ISO 27001, NIST SP 800-53, etc.) to get official text alongside SCF descriptions.

## Overview

The Security Controls MCP Server includes 1,451 free SCF controls that map across **261 frameworks**. When you add purchased standards:

- Get official text from your licensed copies
- See full clauses with page numbers
- Enhanced queries showing both SCF descriptions and official requirements
- Framework mapping with real standard text on both sides

Your paid content stays private in `~/.security-controls-mcp/` (never committed to git).

## Quick Start

### 1. Install Import Tools

```bash
pip install security-controls-mcp[import-tools]
```

Installs PDF extraction dependencies (pdfplumber, Pillow, Click).

### 2. Purchase a Standard

Buy from official source:

- **ISO 27001**: [iso.org](https://www.iso.org/standard/27001)
- **NIST SP 800-53**: [csrc.nist.gov](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final)
- **PCI DSS**: [pcisecuritystandards.org](https://www.pcisecuritystandards.org/)

Download the PDF.

### 3. Import the Standard

```bash
scf-mcp-import import-standard \
  --file ~/Downloads/ISO-IEC-27001-2022.pdf \
  --type iso_27001_2022 \
  --title "ISO/IEC 27001:2022" \
  --purchased-from "ISO.org" \
  --purchase-date "2026-01-29"
```

What happens:
- Extracts text from PDF
- Detects sections and clauses (e.g., "5.1.2 Cryptographic controls")
- Saves to `~/.security-controls-mcp/standards/iso_27001_2022/`
- Adds to your config

### 4. Restart MCP Server

Restart to load the new content.

### 5. Query Your Standards

```
list_available_standards()
get_control("GOV-01")
query_standard("iso_27001_2022", "encryption key management")
get_clause("iso_27001_2022", "5.1.2")
```

## Supported Standards

**Works best with:**
- **ISO 27001/27002** - Numbered clauses, Annex A controls
- **NIST SP 800-53** - Control families (AC-1, SC-7, etc.)
- **PCI DSS** - Numbered requirements
- **CIS Controls** - Numbered controls and safeguards

**May need adjustments:**
- Scanned PDFs (poor text extraction)
- Image-heavy documents
- Non-standard numbering schemes

The generic extractor uses heuristics for numbered sections. Extraction quality varies by PDF.

## Standard IDs

Use these IDs for the `--type` parameter:

| Standard | ID | Example Control |
|----------|-----|-----------------|
| ISO/IEC 27001:2022 | `iso_27001_2022` | A.5.15 |
| ISO/IEC 27002:2022 | `iso_27002_2022` | 5.1 |
| ISO/IEC 27017:2015 | `iso_27017_2015` | CLD.6.3 |
| ISO/IEC 27018:2014 | `iso_27018_2014` | A.1.1 |
| ISO/IEC 27701:2025 | `iso_27701_2025` | 5.2.1 |
| ISO/IEC 42001:2023 | `iso_42001_2023` | 6.1.1 |
| ISO/IEC 22301:2019 | `iso_22301_2019` | 8.4.1 |
| NIST SP 800-53 Rev 5 | `nist_800_53_r5` | AC-1, SC-7 |
| NIST AI RMF 1.0 | `nist_ai_rmf_1.0` | GOVERN 1.1 |
| PCI DSS v4.0.1 | `pci_dss_4.0.1` | Req 3.4 |
| NIST CSF 2.0 | `nist_csf_2.0` | PR.DS-2 |
| SOC 2 (TSC) | `soc_2_tsc` | CC6.1 |

IDs should match SCF framework keys for automatic integration. See [docs/coverage.md](docs/coverage.md) for the complete list of 261 framework IDs.

## Directory Structure

```
~/.security-controls-mcp/
├── config.json                     # Which standards are enabled
└── standards/
    ├── iso_27001_2022/
    │   ├── metadata.json           # Purchase info, license
    │   └── full_text.json          # Extracted content
    └── nist_800_53_r5/
        ├── metadata.json
        └── full_text.json
```

**Important:** This directory is gitignored by default. Never commit it.

## Advanced Usage

**List imported standards:**
```bash
scf-mcp-import list-standards
```

**Re-import (overwrite):**
```bash
scf-mcp-import import-standard --file new-version.pdf --type iso_27001_2022 --force
```

**Disable a standard:**
Edit `~/.security-controls-mcp/config.json`:
```json
{
  "standards": {
    "iso_27001_2022": {
      "enabled": false,
      "path": "iso_27001_2022"
    }
  }
}
```

**Remove a standard:**
```bash
rm -rf ~/.security-controls-mcp/standards/iso_27001_2022
```
Then edit `config.json` to remove the entry.

## License Compliance

**Your purchased standards are licensed for PERSONAL USE ONLY.**

**You MAY:**
- Import standards you've purchased
- Query them via MCP for your own compliance research
- Reference them in your work (with attribution)
- Use get_control() to see official text alongside SCF

**You MAY NOT:**
- Share extracted JSON files with others
- Redistribute PDFs or extracted content
- Use AI to generate policies/procedures from SCF (SCF license restriction)
- Create derivative frameworks for distribution

**Automatic safeguards:**
- Git safety checks warn if standards directory isn't gitignored
- Attribution on every response shows source and license info
- Startup warnings list loaded paid standards and restrictions
- Local-only storage - content never leaves your machine

**Your responsibility:**
- Purchase standards from authorized sources
- Comply with your purchase agreement
- Don't redistribute content
- Consult legal counsel for compliance questions

This tool facilitates querying - it doesn't grant licenses.

## Troubleshooting

**"No text extracted from PDF"**
- PDF is scanned or image-based
- Check if PDF has selectable text
- Use OCR software to create searchable version
- Purchase different format (Word, HTML) if available

**"Warning: standards directory not gitignored"**
```bash
echo ".security-controls-mcp/" >> .gitignore
git add .gitignore
git commit -m "Gitignore paid standards directory"
```

**"Section detection found 0 sections"**
- PDF doesn't match expected numbering patterns
- Check if PDF uses standard numbering (1, 1.2, 1.2.3)
- Extractor looks for patterns like "5.1.2 Title"
- Contact us for help with specific standard formats

**"Standard 'xyz' not found" after import**
- MCP server hasn't reloaded
- Restart your MCP server to load new standards

## Examples

**Complete workflow:**
```bash
# 1. Buy ISO 27001 from ISO.org (download PDF)

# 2. Install import tools
pip install security-controls-mcp[import-tools]

# 3. Import the PDF
scf-mcp-import import-standard \
  --file ~/Downloads/ISO-IEC-27001-2022.pdf \
  --type iso_27001_2022 \
  --title "ISO/IEC 27001:2022" \
  --purchased-from "ISO.org" \
  --purchase-date "2026-01-29"

# 4. Restart MCP server

# 5. Ask Claude:
#    "Show me GOV-01 with official ISO 27001 text"
#    "What does ISO 27001 clause 5.1.2 say?"
#    "Map ISO 27001 to DORA with official text"
```

## FAQ

**Q: How many standards can I import?**
A: Unlimited. Each standard you purchase can be imported.

**Q: Do I need to keep the original PDF?**
A: No, after import you can delete it.

**Q: Can I share my imported standards with my team?**
A: No. Each person must purchase and import their own licensed copy.

**Q: Will this work with my company's custom framework?**
A: Maybe. If it's in PDF with numbered sections, the generic extractor might work. Contact us for custom extractors.

**Q: What if extraction quality is poor?**
A: You can manually edit `~/.security-controls-mcp/standards/xyz/full_text.json`.

**Q: Does this replace the official standard document?**
A: No. This tool is for research. Always refer to the official published standard for authoritative guidance.

## Getting Help

- **Issues:** [GitHub Issues](https://github.com/Ansvar-Systems/security-controls-mcp/issues)
- **Email:** hello@ansvar.eu

---

**Built by [Ansvar Systems](https://ansvar.eu) — Stockholm, Sweden**
