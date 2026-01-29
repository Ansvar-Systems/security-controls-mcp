# Paid Standards Guide

This guide explains how to add your purchased security standards (ISO 27001, NIST SP 800-53, etc.) to the Security Controls MCP Server for enhanced compliance research.

---

## Overview

The Security Controls MCP Server includes **1,451 free SCF controls** that map across 28 frameworks. When you add your **purchased standards**, you get:

- ✅ **Official text** from your licensed copies
- ✅ **Full clauses** with page numbers
- ✅ **Enhanced SCF queries** showing both SCF descriptions AND official requirements
- ✅ **Framework mapping** with real standard text on both sides

**Your paid content stays private** - it's stored locally in `~/.security-controls-mcp/` and never committed to git.

---

## Quick Start

### 1. Install Import Tools

```bash
pip install -e '.[import-tools]'
```

This installs PDF extraction dependencies (pdfplumber, Pillow, Click).

### 2. Purchase a Standard

Buy the standard from the official source:

- **ISO 27001**: [iso.org](https://www.iso.org/standard/27001)
- **NIST SP 800-53**: [csrc.nist.gov](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final)
- **PCI DSS**: [pcisecuritystandards.org](https://www.pcisecuritystandards.org/)

Download the PDF to your computer.

### 3. Import the Standard

```bash
scf-mcp import-standard \
  --file ~/Downloads/ISO-IEC-27001-2022.pdf \
  --type iso_27001_2022 \
  --title "ISO/IEC 27001:2022" \
  --purchased-from "ISO.org" \
  --purchase-date "2026-01-29"
```

**What happens:**
- Extracts text from PDF
- Detects sections and clauses (e.g., "5.1.2 Cryptographic controls")
- Saves to `~/.security-controls-mcp/standards/iso_27001_2022/`
- Adds to your config

### 4. Restart MCP Server

The server loads paid standards on startup. Restart it to see your new content.

### 5. Query Your Standards

Use the MCP tools in Claude:

```
list_available_standards()
→ Shows SCF + your ISO 27001

get_control("GOV-01")
→ Shows SCF description + ISO 27001 A.5.1 official text

query_standard("iso_27001_2022", "encryption key management")
→ Searches within your ISO 27001

get_clause("iso_27001_2022", "5.1.2")
→ Shows full text of clause 5.1.2 with page number
```

---

## Supported Standards

The import tool works best with:

### ✅ Well-Structured PDFs
- **ISO 27001/27002** - Numbered clauses, Annex A controls
- **NIST SP 800-53** - Control families (AC-1, SC-7, etc.)
- **PCI DSS** - Numbered requirements
- **CIS Controls** - Numbered controls and safeguards

### ⚠️ May Need Adjustments
- Scanned PDFs (poor text extraction)
- Image-heavy documents
- Non-standard numbering schemes

**Tip:** The generic extractor uses heuristics (numbered sections like "1.2.3 Title"). It handles most standards reasonably well, but extraction quality varies by PDF.

---

## Standard IDs

Use these IDs for the `--type` parameter:

| Standard | ID | Example Control |
|----------|-----|-----------------|
| ISO/IEC 27001:2022 | `iso_27001_2022` | A.5.15 |
| ISO/IEC 27002:2022 | `iso_27002_2022` | 5.1 |
| NIST SP 800-53 Rev 5 | `nist_800_53_r5` | AC-1, SC-7 |
| PCI DSS v4.0.1 | `pci_dss_4.0.1` | Req 3.4 |
| NIST CSF 2.0 | `nist_csf_2.0` | PR.DS-2 |
| SOC 2 (TSC) | `soc_2_tsc` | CC6.1 |

**Note:** IDs should match the SCF framework keys for automatic integration.

---

## Directory Structure

After importing, your files live here:

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

**Important:** This directory is gitignored by default. Never commit it!

---

## Advanced Usage

### List Imported Standards

```bash
scf-mcp list-standards
```

Shows all available standards (SCF + your imports).

### Re-Import (Overwrite)

```bash
scf-mcp import-standard --file new-version.pdf --type iso_27001_2022 --force
```

Overwrites existing import with new PDF.

### Disable a Standard

Edit `~/.security-controls-mcp/config.json`:

```json
{
  "standards": {
    "iso_27001_2022": {
      "enabled": false,  // Change to false
      "path": "iso_27001_2022"
    }
  }
}
```

Restart server to apply.

### Remove a Standard

```bash
rm -rf ~/.security-controls-mcp/standards/iso_27001_2022
```

Then edit `config.json` to remove the entry.

---

## License Compliance

### ⚠️ Important Restrictions

**Your purchased standards are licensed for PERSONAL USE ONLY.**

✅ **You MAY:**
- Import standards you've purchased
- Query them via MCP for your own compliance research
- Reference them in your work (with attribution)
- Use get_control() to see official text alongside SCF

✗ **You MAY NOT:**
- Share extracted JSON files with others
- Redistribute PDFs or extracted content
- Use AI to generate policies/procedures from SCF (SCF license restriction)
- Create derivative frameworks for distribution

### Automatic Safeguards

The tool includes:
- **Git safety checks** - Warns if standards directory isn't gitignored
- **Attribution on every response** - Shows source and license info
- **Startup warnings** - Lists loaded paid standards and restrictions
- **Local-only storage** - Content never leaves your machine

### Your Responsibility

**You are responsible for:**
- Purchasing standards from authorized sources
- Complying with your purchase agreement
- Not redistributing content
- Consulting legal counsel for compliance questions

**This tool facilitates querying - it doesn't grant licenses.**

---

## Troubleshooting

### "No text extracted from PDF"

**Cause:** PDF is scanned or image-based.

**Solution:** The PDF needs searchable text. Try:
1. Check if PDF has selectable text (not just images)
2. Use OCR software to create searchable version
3. Purchase a different format (Word, HTML) if available

### "Warning: standards directory not gitignored"

**Cause:** You're in a git repo and the standards directory could be committed.

**Solution:**
```bash
echo ".security-controls-mcp/" >> .gitignore
git add .gitignore
git commit -m "Gitignore paid standards directory"
```

### "Section detection found 0 sections"

**Cause:** PDF doesn't match expected numbering patterns.

**Solution:**
- Check if PDF uses standard numbering (1, 1.2, 1.2.3)
- The extractor looks for patterns like "5.1.2 Title"
- Contact us if you need help with a specific standard format

### "Standard 'xyz' not found" after import

**Cause:** MCP server hasn't reloaded.

**Solution:** Restart your MCP server to load new standards.

---

## Examples

### Complete Workflow: ISO 27001

```bash
# 1. Buy ISO 27001 from ISO.org (download PDF)

# 2. Install import tools
pip install -e '.[import-tools]'

# 3. Import the PDF
scf-mcp import-standard \
  --file ~/Downloads/ISO-IEC-27001-2022.pdf \
  --type iso_27001_2022 \
  --title "ISO/IEC 27001:2022" \
  --purchased-from "ISO.org" \
  --purchase-date "2026-01-29" \
  --version "2022"

# 4. Restart MCP server

# 5. Ask Claude:
#    "Show me GOV-01 with official ISO 27001 text"
#    "What does ISO 27001 clause 5.1.2 say?"
#    "Map ISO 27001 to DORA with official text"
```

### Query Examples

**Get SCF control with official text:**
```
User: Get control GOV-01
Claude: [Shows SCF description]
        [Shows ISO 27001 A.5.1 official text with page number]
```

**Search within your standard:**
```
User: Search for "encryption key management" in ISO 27001
Claude: [Shows matching clauses with page numbers]
```

**Framework mapping with official text:**
```
User: Map ISO 27001 to DORA
Claude: [Shows SCF mapping]
        [Shows ISO 27001 A.5.15 official text]
        [Shows DORA Article 9 official text if you have it]
```

---

## FAQ

**Q: How many standards can I import?**
A: Unlimited. Each standard you purchase can be imported.

**Q: Do I need to keep the original PDF?**
A: No, after import you can delete it. The extracted JSON has everything.

**Q: Can I share my imported standards with my team?**
A: No. Each person must purchase and import their own licensed copy.

**Q: Will this work with my company's custom framework?**
A: Maybe. If it's in PDF with numbered sections, the generic extractor might work. Contact us for custom extractors.

**Q: What if extraction quality is poor?**
A: You can manually edit `~/.security-controls-mcp/standards/xyz/full_text.json` to fix issues.

**Q: Does this replace the official standard document?**
A: No. This tool is for research and queries. Always refer to the official published standard for authoritative guidance.

---

## Getting Help

- **Issues:** [GitHub Issues](https://github.com/Ansvar-Systems/security-controls-mcp/issues)
- **Email:** hello@ansvar.eu
- **Documentation:** [README.md](README.md)

---

**Built by [Ansvar Systems](https://ansvar.eu) — Stockholm, Sweden**
