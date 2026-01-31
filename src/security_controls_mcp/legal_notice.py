"""Legal compliance notices for SCF data usage."""

import sys

LEGAL_NOTICE = """
╔════════════════════════════════════════════════════════════════════════════╗
║                    SECURITY CONTROLS MCP SERVER                            ║
║                         LEGAL USAGE NOTICE                                 ║
╚════════════════════════════════════════════════════════════════════════════╝

This server provides Secure Controls Framework (SCF) data licensed under
CC BY-ND 4.0 by ComplianceForge.

⚠️  AI DERIVATIVE CONTENT RESTRICTION:

    The SCF license PROHIBITS using AI systems (including Claude) to generate
    derivative content such as policies, standards, procedures, or metrics
    based on SCF controls.

✓  PERMITTED USES:
    • Query control details and mappings
    • Map between frameworks (ISO 27001 → DORA, etc.)
    • Reference controls in your work (with attribution)
    • Understand compliance requirements

✗  PROHIBITED USES:
    • Asking Claude to write policies/procedures from SCF controls
    • Creating derivative frameworks for distribution
    • Generating automated compliance content using AI

Full terms: https://securecontrolsframework.com/terms-conditions/

This is not legal advice. Consult legal professionals for compliance guidance.

════════════════════════════════════════════════════════════════════════════
"""


def print_legal_notice(registry=None):
    """Print legal notice to stderr on server startup.

    Args:
        registry: Optional StandardRegistry to show information about paid standards
    """
    print(LEGAL_NOTICE, file=sys.stderr)

    # If paid standards are loaded, show additional notice
    if registry and registry.has_paid_standards():
        paid_notice = (
            "\n╔════════════════════════════════════════════════════════════════════════════╗\n"
        )
        paid_notice += (
            "║                    PAID STANDARDS LOADED                                   ║\n"
        )
        paid_notice += (
            "╚════════════════════════════════════════════════════════════════════════════╝\n\n"
        )

        standards = registry.list_standards()
        paid_standards = [s for s in standards if s["type"] == "paid"]

        if paid_standards:
            paid_notice += "Loaded purchased standards:\n\n"
            for std in paid_standards:
                paid_notice += f"  ✓ {std['title']}\n"
                paid_notice += f"    License: {std['license']}\n"
                paid_notice += f"    Purchased: {std['purchase_date']}\n\n"

            paid_notice += "⚠️  IMPORTANT LICENSE RESTRICTIONS:\n\n"
            paid_notice += "    • Licensed for your personal use only\n"
            paid_notice += "    • No redistribution or sharing of content\n"
            paid_notice += (
                "    • Do not share extracted text or create derivatives for distribution\n"
            )
            paid_notice += "    • Consult your purchase agreement for full terms\n\n"
            paid_notice += "This tool provides query access only. Ensure your use complies with\n"
            paid_notice += "all applicable license agreements.\n\n"
            paid_notice += (
                "════════════════════════════════════════════════════════════════════════════\n"
            )

            print(paid_notice, file=sys.stderr)
