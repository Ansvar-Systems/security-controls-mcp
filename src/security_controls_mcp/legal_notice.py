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


def print_legal_notice():
    """Print legal notice to stderr on server startup."""
    print(LEGAL_NOTICE, file=sys.stderr)
