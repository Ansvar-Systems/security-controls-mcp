# Legal Compliance Review
**Date:** 2026-01-29
**Reviewed by:** Claude Code
**Status:** ⚠️ Action Required

## Summary

This project redistributes SCF (Secure Controls Framework) data under the Creative Commons Attribution-NoDerivatives 4.0 International (CC BY-ND 4.0) license. The codebase is generally compliant, but requires **immediate action** to address AI-generated derivative content risks.

---

## Critical Issue: AI-Generated Derivatives

### The Problem

The SCF End User License Agreement explicitly prohibits:

> "utilizing Artificial Intelligence (AI) (or similar technologies) to leverage SCF content to generate policies, standards, procedures, metrics, risks, threats or other derivative content"

**Source:** [SCF Terms & Conditions](https://securecontrolsframework.com/terms-conditions/)

### Why This Matters

This MCP server:
1. Provides SCF control data to Claude (an AI system)
2. Enables users to query and analyze controls
3. **Could be used** by users to generate derivative content (policies, procedures, etc.)

Even though the MCP server itself doesn't create derivatives, **users could violate the license** by asking Claude to generate derivative content based on SCF data.

### Required Action

**Add prominent disclaimers** warning users about the AI derivative content restriction.

---

## Compliance Checklist

### ✅ Currently Compliant

- [x] Separate licenses for code (Apache 2.0) and data (CC license)
- [x] Attribution to ComplianceForge in README
- [x] Link to source (securecontrolsframework.com)
- [x] General disclaimer about not being legal advice (README:182)
- [x] No modification of SCF control data (read-only redistribution)
- [x] No commercial licensing of derivative works
- [x] Open source Apache 2.0 for code components

### ⚠️ Needs Improvement

- [ ] **Explicit CC BY-ND 4.0 specification** (README says "Creative Commons" but not the specific license version)
- [ ] **Copyright notice in data files** (JSON files lack ComplianceForge copyright headers)
- [ ] **AI derivative content warning** (critical - see above)
- [ ] **License file for data** (Consider adding a separate LICENSE-DATA.md)

---

## Recommended Changes

### 1. Update README.md License Section

**Current (lines 192-195):**
```markdown
## License

- **Code:** Apache License 2.0 (see [LICENSE](LICENSE))
- **Data:** Creative Commons (SCF by ComplianceForge)
```

**Recommended:**
```markdown
## License

### Code License
The source code in this repository is licensed under the **Apache License 2.0** (see [LICENSE](LICENSE)).

### Data License
The SCF control data (`scf-controls.json`, `framework-to-scf.json`) is licensed under the **Creative Commons Attribution-NoDerivatives 4.0 International (CC BY-ND 4.0)** by ComplianceForge.

- **Source:** [Secure Controls Framework (SCF)](https://securecontrolsframework.com/)
- **License:** [CC BY-ND 4.0](https://creativecommons.org/licenses/by-nd/4.0/)
- **Copyright:** ComplianceForge
- **Version:** SCF 2025.4 (Released December 29, 2025)

#### Data Usage Restrictions

⚠️ **IMPORTANT:** The SCF license explicitly prohibits using AI systems to generate derivative content (policies, standards, procedures, metrics, risks, threats) based on SCF data.

**You may:**
- Query and analyze SCF controls
- Map between frameworks
- Reference controls in your own work (with attribution)

**You may NOT:**
- Ask Claude (or any AI) to generate policies/procedures based on SCF controls
- Create derivative frameworks or modified versions for distribution
- Remove or modify control definitions

For questions about permitted uses, see: [SCF Terms & Conditions](https://securecontrolsframework.com/terms-conditions/)
```

### 2. Add Startup Warning

Create a new file to display when the server starts:

**File:** `src/security_controls_mcp/legal_notice.py`

```python
"""Legal compliance notices for SCF data usage."""

LEGAL_NOTICE = """
╔════════════════════════════════════════════════════════════════════════════╗
║                         IMPORTANT LEGAL NOTICE                             ║
╚════════════════════════════════════════════════════════════════════════════╝

This MCP server provides access to Secure Controls Framework (SCF) data,
which is licensed under CC BY-ND 4.0 by ComplianceForge.

⚠️  AI DERIVATIVE CONTENT RESTRICTION:

    The SCF license PROHIBITS using AI systems (including Claude) to generate
    derivative content such as policies, standards, procedures, or metrics
    based on SCF controls.

✓  PERMITTED USES:
    • Query and analyze control mappings
    • Map between frameworks (e.g., ISO 27001 → DORA)
    • Reference controls in your work (with attribution)

✗  PROHIBITED USES:
    • Asking Claude to write policies/procedures based on SCF controls
    • Creating derivative frameworks for distribution
    • Removing or modifying control definitions

For full terms, see: https://securecontrolsframework.com/terms-conditions/

This is not legal advice. Consult a legal professional for compliance guidance.
"""

def print_legal_notice():
    """Print legal notice on server startup."""
    print(LEGAL_NOTICE)
```

Then update `server.py` to display this on startup.

### 3. Add Copyright Headers to Data Files

Consider adding a metadata section to the JSON files (requires regeneration):

```json
{
  "_metadata": {
    "source": "Secure Controls Framework (SCF)",
    "copyright": "Copyright © ComplianceForge",
    "license": "Creative Commons Attribution-NoDerivatives 4.0 International (CC BY-ND 4.0)",
    "license_url": "https://creativecommons.org/licenses/by-nd/4.0/",
    "version": "SCF 2025.4",
    "release_date": "2025-12-29",
    "source_url": "https://securecontrolsframework.com/",
    "terms_url": "https://securecontrolsframework.com/terms-conditions/"
  },
  "controls": [
    ...
  ]
}
```

### 4. Create LICENSE-DATA.md

Create a separate license file for the data:

**File:** `LICENSE-DATA.md`

```markdown
# Data License

The SCF control data files in this repository (`scf-controls.json`, `framework-to-scf.json`) are licensed under:

**Creative Commons Attribution-NoDerivatives 4.0 International (CC BY-ND 4.0)**

**Copyright:** ComplianceForge
**Source:** [Secure Controls Framework (SCF)](https://securecontrolsframework.com/)
**Version:** SCF 2025.4 (Released December 29, 2025)

---

## License Summary

You are free to:

- **Share** — copy and redistribute the material in any medium or format for any purpose, even commercially

Under the following terms:

- **Attribution** — You must give appropriate credit to ComplianceForge, provide a link to the license, and indicate if changes were made
- **NoDerivatives** — If you remix, transform, or build upon the material, you may not distribute the modified material

---

## Important Restrictions

The SCF End User License Agreement specifically prohibits:

> "utilizing Artificial Intelligence (AI) (or similar technologies) to leverage SCF content to generate policies, standards, procedures, metrics, risks, threats or other derivative content"

This means you **may not** use AI systems (including Claude, ChatGPT, or similar) to generate derivative content based on SCF data.

---

## Full License

The complete CC BY-ND 4.0 license is available at:
https://creativecommons.org/licenses/by-nd/4.0/legalcode

For SCF-specific terms and conditions, see:
https://securecontrolsframework.com/terms-conditions/

---

## Questions?

For questions about permitted uses, contact ComplianceForge directly or consult a legal professional.
```

---

## Additional Recommendations

### Package Distribution (PyPI)

If you plan to publish to PyPI:

1. **Add license classifiers** to `pyproject.toml`:
   ```toml
   classifiers = [
       "License :: OSI Approved :: Apache Software License",
       "License :: Other/Proprietary License",  # For CC BY-ND data
       ...
   ]
   ```

2. **Include both LICENSE files** in the package manifest

### User Documentation

Update `INSTALL.md` and `TESTING.md` to reference the AI derivative content restriction.

---

## Ongoing Compliance

### What to Monitor

1. **SCF License Changes**: ComplianceForge may update terms
2. **Data Updates**: When updating to newer SCF versions, verify license hasn't changed
3. **User Feedback**: Watch for users attempting to generate derivative content
4. **Legal Precedents**: Monitor for any CC BY-ND AI-related case law

### Recommended Practices

1. **Attribution Verification**: Periodically verify all attribution remains intact
2. **License Audits**: Review license compliance before major releases
3. **User Education**: Clearly communicate permitted vs. prohibited uses
4. **Legal Review**: Consider professional legal review before commercial use

---

## Disclaimer

This compliance review is provided for informational purposes only and does not constitute legal advice. For legal guidance specific to your situation, consult a qualified attorney specializing in intellectual property and open source licensing.

---

## Sources

- [SCF Terms & Conditions](https://securecontrolsframework.com/terms-conditions/)
- [CC BY-ND 4.0 Legal Code](https://creativecommons.org/licenses/by-nd/4.0/legalcode)
- [ComplianceForge SCF Homepage](https://complianceforge.com/secure-controls-framework-scf/)
- [SCF FAQ](https://securecontrolsframework.com/faq/faq)

**Last Updated:** 2026-01-29
**Reviewer:** Automated compliance check via Claude Code
**Next Review:** Before next major release or SCF data update
