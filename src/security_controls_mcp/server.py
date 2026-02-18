"""MCP server for security controls framework queries."""

import asyncio
import hashlib
import json as json_module
from datetime import datetime, timezone
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .config import Config
from .data_loader import SCFData
from .legal_notice import print_legal_notice
from .registry import StandardRegistry

# Initialize data loader
scf_data = SCFData()

# Initialize configuration and registry for paid standards
config = Config()
registry = StandardRegistry(config)

# Create server instance
app = Server("security-controls-mcp")


SERVER_VERSION = "1.1.0"

# Compute data fingerprint and build timestamp once at module load
_data_dir = Path(__file__).parent / "data"
_controls_file = _data_dir / "scf-controls.json"


def _compute_data_fingerprint() -> str:
    """Compute a short SHA-256 fingerprint of the controls data file."""
    try:
        content = _controls_file.read_bytes()
        return hashlib.sha256(content).hexdigest()[:12]
    except Exception:
        return "unknown"


def _get_data_built() -> str:
    """Get the modification time of the controls data file as ISO timestamp."""
    try:
        mtime = _controls_file.stat().st_mtime
        return datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return "unknown"


DATA_FINGERPRINT = _compute_data_fingerprint()
DATA_BUILT = _get_data_built()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="version_info",
            description=(
                "Get server version, control/framework counts, and top 10 frameworks by "
                "coverage. Use this as a quick overview of what data is available. "
                "For structured provenance metadata, use the 'about' tool instead. "
                "Returns ~500 tokens."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        ),
        Tool(
            name="about",
            description=(
                "Returns structured JSON with server metadata, dataset provenance, "
                "data fingerprint, freshness indicators, and security posture. "
                "Use this to verify data currency and coverage before relying on results. "
                "Prefer this over version_info when you need machine-readable metadata. "
                "Returns ~800 tokens."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        ),
        Tool(
            name="get_control",
            description=(
                "Retrieve a specific SCF control by its exact ID. Returns the control's "
                "domain, description, weight (1-10 criticality), PPTDF classification, "
                "validation cadence, and optionally all framework mappings. "
                "Use this when you already know the control ID (e.g., GOV-01, IAC-05, CRY-01). "
                "If you don't know the ID, use search_controls first. "
                "Returns 'not found' for invalid IDs. "
                "With include_mappings=true (default), returns ~1000-3000 tokens depending "
                "on how many frameworks map to this control. Set include_mappings=false "
                "to reduce to ~200 tokens."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "control_id": {
                        "type": "string",
                        "description": (
                            "SCF control ID in format DOMAIN-NN (e.g., GOV-01, IAC-05, "
                            "CRY-01, NET-01). Use search_controls to discover valid IDs."
                        ),
                        "pattern": "^[A-Z]{2,5}-\\d{2}(\\.\\d{1,2})?$",
                    },
                    "include_mappings": {
                        "type": "boolean",
                        "description": (
                            "Include cross-framework mappings in the response. "
                            "Set to false to reduce token usage when you only need "
                            "the control description. Default: true."
                        ),
                        "default": True,
                    },
                },
                "required": ["control_id"],
                "additionalProperties": False,
            },
        ),
        Tool(
            name="search_controls",
            description=(
                "Full-text search across all 1,451 SCF controls by keyword in name or "
                "description. Returns matching controls with text snippets and their "
                "top framework mappings. Use this to discover controls by topic "
                "(e.g., 'encryption', 'incident response', 'access control'). "
                "Optionally filter to controls that map to specific frameworks. "
                "Returns 'No controls found' when no matches exist. "
                "Each result is ~100 tokens; default limit of 10 returns ~1000 tokens."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Search keyword or phrase. Matches against control names and "
                            "descriptions. Examples: 'encryption', 'access control', "
                            "'incident response', 'data classification'. "
                            "Must not be empty."
                        ),
                        "minLength": 1,
                    },
                    "frameworks": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "Optional: filter results to controls that map to these "
                            "framework keys (e.g., ['iso_27001_2022', 'nist_csf_2.0']). "
                            "Use list_frameworks to discover valid keys."
                        ),
                    },
                    "limit": {
                        "type": "integer",
                        "description": (
                            "Maximum number of results to return. Default: 10. "
                            "Use lower values to save tokens."
                        ),
                        "default": 10,
                        "minimum": 1,
                        "maximum": 100,
                    },
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        ),
        Tool(
            name="list_frameworks",
            description=(
                "List all 261 supported security frameworks, optionally filtered by "
                "category. Without a category filter, returns all frameworks grouped "
                "by category (~3000 tokens). With a category filter, returns only that "
                "category's frameworks (~200-500 tokens). Use this to discover valid "
                "framework keys for get_framework_controls and map_frameworks. "
                "Returns an error listing valid categories if an invalid category is given."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": (
                            "Filter to a specific category. Omit to see all categories "
                            "with their frameworks."
                        ),
                        "enum": [
                            "ai_governance",
                            "americas",
                            "asia_pacific",
                            "automotive",
                            "cis_controls",
                            "cloud_security",
                            "cmmc",
                            "eu_regulations",
                            "europe_national",
                            "fedramp",
                            "financial",
                            "governance",
                            "govramp",
                            "healthcare",
                            "industrial_ot",
                            "iso_standards",
                            "media_entertainment",
                            "middle_east_africa",
                            "nist_frameworks",
                            "privacy",
                            "supply_chain",
                            "threat_intel_appsec",
                            "uk_cybersecurity",
                            "us_federal",
                            "us_state_laws",
                            "zero_trust",
                        ],
                    },
                },
                "additionalProperties": False,
            },
        ),
        Tool(
            name="get_framework_controls",
            description=(
                "Get all SCF controls that map to a specific framework, grouped by "
                "domain. WARNING: Large frameworks like NIST 800-53 can return 700+ "
                "controls (~5000 tokens with descriptions, ~2000 without). "
                "Set include_descriptions=false (default) to reduce token usage. "
                "Controls are capped at 10 per domain with overflow indicated. "
                "Returns 'not found' with a list of valid framework keys if the "
                "framework doesn't exist. Use list_frameworks to discover valid keys."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "framework": {
                        "type": "string",
                        "description": (
                            "Framework key (e.g., 'iso_27001_2022', 'nist_csf_2.0', "
                            "'dora', 'pci_dss_4.0.1'). Use list_frameworks to discover "
                            "valid keys."
                        ),
                    },
                    "include_descriptions": {
                        "type": "boolean",
                        "description": (
                            "Include control descriptions in the response. Significantly "
                            "increases token usage (~2.5x). Default: false."
                        ),
                        "default": False,
                    },
                },
                "required": ["framework"],
                "additionalProperties": False,
            },
        ),
        Tool(
            name="map_frameworks",
            description=(
                "Map controls between two frameworks via SCF as a rosetta stone. "
                "Shows which target framework requirements are satisfied by source "
                "framework controls, and identifies gaps where no mapping exists. "
                "Useful for gap analysis and compliance mapping. "
                "Results are capped at 20 mappings; use source_control to filter "
                "to a specific control for detailed mapping. "
                "Returns 'not found' if either framework key is invalid. "
                "Typical response: ~1500-3000 tokens."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "source_framework": {
                        "type": "string",
                        "description": (
                            "Source framework key - the framework you HAVE implemented "
                            "(e.g., 'iso_27001_2022'). Use list_frameworks to discover keys."
                        ),
                    },
                    "source_control": {
                        "type": "string",
                        "description": (
                            "Optional: filter to a specific source control ID "
                            "(e.g., 'A.5.15' for ISO 27001, 'PR.AC-1' for NIST CSF) "
                            "to see its specific mappings to the target framework."
                        ),
                    },
                    "target_framework": {
                        "type": "string",
                        "description": (
                            "Target framework key - the framework you want to SATISFY "
                            "(e.g., 'dora', 'nist_800_53_r5'). Use list_frameworks to "
                            "discover keys."
                        ),
                    },
                },
                "required": ["source_framework", "target_framework"],
                "additionalProperties": False,
            },
        ),
        Tool(
            name="list_available_standards",
            description=(
                "List all available standards: SCF (always built-in) plus any purchased "
                "standards the user has imported via PDF upload. Purchased standards "
                "provide official clause text for query_standard and get_clause tools. "
                "If no standards have been imported, only SCF is shown with a guidance "
                "message. Returns ~200-500 tokens."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        ),
        Tool(
            name="query_standard",
            description=(
                "Search within a purchased standard's official text by keyword. "
                "Requires the standard to have been imported first via PDF upload. "
                "Returns matching clauses with text snippets. "
                "If the standard is not found, returns available standard IDs. "
                "If no standards are imported, returns guidance to import first. "
                "Use list_available_standards to check what's available before calling. "
                "Returns ~500-2000 tokens depending on matches."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "standard": {
                        "type": "string",
                        "description": (
                            "Standard identifier (e.g., 'iso_27001_2022', 'nist_800_53_r5'). "
                            "Use list_available_standards to see imported standards."
                        ),
                    },
                    "query": {
                        "type": "string",
                        "description": (
                            "Search query for clause content (e.g., 'encryption key "
                            "management', 'access control policy'). Must not be empty."
                        ),
                        "minLength": 1,
                    },
                    "limit": {
                        "type": "integer",
                        "description": (
                            "Maximum number of results to return. Default: 10."
                        ),
                        "default": 10,
                        "minimum": 1,
                        "maximum": 50,
                    },
                },
                "required": ["standard", "query"],
                "additionalProperties": False,
            },
        ),
        Tool(
            name="get_clause",
            description=(
                "Get the full text of a specific clause or section from a purchased "
                "standard by its clause ID. Requires the standard to have been imported "
                "first via PDF upload. Returns the complete clause content with page "
                "reference and license notice. If the clause is not found, returns an "
                "error message. Use query_standard to discover clause IDs first."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "standard": {
                        "type": "string",
                        "description": (
                            "Standard identifier (e.g., 'iso_27001_2022'). "
                            "Use list_available_standards to see imported standards."
                        ),
                    },
                    "clause_id": {
                        "type": "string",
                        "description": (
                            "Clause or section identifier within the standard "
                            "(e.g., '5.1.2', 'A.5.15' for ISO 27001, 'AC-1' for "
                            "NIST 800-53). Use query_standard to discover valid IDs."
                        ),
                    },
                },
                "required": ["standard", "clause_id"],
                "additionalProperties": False,
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""

    if name == "version_info":
        top_frameworks = sorted(
            scf_data.frameworks.values(),
            key=lambda x: x["controls_mapped"],
            reverse=True,
        )[:10]

        text = f"**Security Controls MCP Server v{SERVER_VERSION}**\n\n"
        text += "**Database:** SCF 2025.4\n"
        text += f"**Controls:** {len(scf_data.controls)} unique controls\n"
        text += f"**Frameworks:** {len(scf_data.frameworks)} supported\n\n"
        text += "**Top 10 Frameworks by Coverage:**\n"
        for fw in top_frameworks:
            text += f"- `{fw['key']}`: {fw['name']} ({fw['controls_mapped']} controls)\n"
        text += (
            "\n*Use `list_frameworks` for the complete list, "
            "`search_controls` to find controls by keyword, "
            "and `map_frameworks` to map between any two frameworks.*"
        )

        if registry.has_paid_standards():
            standards = registry.list_standards()
            paid = [s for s in standards if s["type"] == "paid"]
            if paid:
                text += f"\n\n**Paid Standards Loaded:** {len(paid)}\n"
                for s in paid:
                    text += f"- {s['title']} (`{s['standard_id']}`)\n"

        return [TextContent(type="text", text=text)]

    elif name == "about":
        about_data = {
            "server": {
                "name": "Security Controls MCP",
                "package": "security-controls-mcp",
                "version": SERVER_VERSION,
                "suite": "Ansvar Compliance Suite",
                "repository": "https://github.com/Ansvar-Systems/security-controls-mcp",
            },
            "dataset": {
                "fingerprint": DATA_FINGERPRINT,
                "built": DATA_BUILT,
                "jurisdiction": "International",
                "content_basis": (
                    "Secure Controls Framework (SCF) 2025.4 control catalog with "
                    "cross-framework mappings. Framework identifiers and mapping "
                    "relationships only \u2014 no copyrighted standard text included."
                ),
                "counts": {
                    "controls": len(scf_data.controls),
                    "frameworks": len(scf_data.frameworks),
                },
                "freshness": {
                    "last_checked": "2026-02-17",
                    "check_method": "Manual SCF release monitoring",
                    "scf_version": "2025.4",
                },
            },
            "provenance": {
                "sources": ["Secure Controls Framework (SCF)"],
                "license": (
                    "Apache-2.0 (server code). SCF data used under SCF license terms. "
                    "Framework control IDs and mapping relationships are factual data."
                ),
                "authenticity_note": (
                    "Control mappings are derived from the Secure Controls Framework. "
                    "Individual framework standards (ISO 27001, NIST, etc.) are copyrighted "
                    "by their respective bodies. This server provides mapping relationships, "
                    "not standard text."
                ),
            },
            "security": {
                "access_model": "read-only",
                "network_access": False,
                "filesystem_access": False,
                "arbitrary_execution": False,
            },
        }

        # Include paid standards count if available
        if registry.has_paid_standards():
            standards = registry.list_standards()
            paid = [s for s in standards if s["type"] == "paid"]
            about_data["dataset"]["counts"]["paid_standards"] = len(paid)

        return [TextContent(type="text", text=json_module.dumps(about_data, indent=2))]

    elif name == "get_control":
        control_id = str(arguments.get("control_id") or "").strip()
        if not control_id:
            return [
                TextContent(
                    type="text",
                    text="Error: control_id is required and must not be empty. "
                    "Use search_controls to discover valid control IDs (e.g., GOV-01, IAC-05).",
                )
            ]
        include_mappings = arguments.get("include_mappings", True)

        control = scf_data.get_control(control_id)
        if not control:
            return [
                TextContent(
                    type="text",
                    text=f"Control {control_id} not found. Use search_controls to find controls.",
                )
            ]

        response = {
            "id": control["id"],
            "domain": control["domain"],
            "name": control["name"],
            "description": control["description"],
            "weight": control["weight"],
            "pptdf": control["pptdf"],
            "validation_cadence": control["validation_cadence"],
        }

        if include_mappings:
            response["framework_mappings"] = control["framework_mappings"]

        # Format response
        text = f"**{response['id']}: {response['name']}**\n\n"
        text += f"**Domain:** {response['domain']}\n"
        text += f"**Description:** {response['description']}\n\n"
        text += f"**Weight:** {response['weight']}/10\n"
        text += f"**PPTDF:** {response['pptdf']}\n"
        text += f"**Validation Cadence:** {response['validation_cadence']}\n"

        if include_mappings:
            text += "\n**Framework Mappings:**\n"
            for fw_key, mappings in response["framework_mappings"].items():
                if mappings:
                    fw_name = scf_data.frameworks.get(fw_key, {}).get("name", fw_key)
                    text += f"- **{fw_name}:** {', '.join(mappings)}\n"

        # Check if user has paid standards with official text for mapped frameworks
        if include_mappings and registry.has_paid_standards():
            official_texts = []

            for fw_key, control_ids in response["framework_mappings"].items():
                if not control_ids:
                    continue

                # Check if we have a paid standard for this framework
                provider = registry.get_provider(fw_key)
                if not provider:
                    continue

                # Try to get official text for the first mapped control ID
                for control_id in control_ids[:1]:  # Just show first mapping to avoid clutter
                    clause = provider.get_clause(control_id)
                    if clause:
                        metadata = provider.get_metadata()
                        official_texts.append(
                            {
                                "framework": fw_key,
                                "framework_name": scf_data.frameworks.get(fw_key, {}).get(
                                    "name", fw_key
                                ),
                                "control_id": control_id,
                                "clause": clause,
                                "metadata": metadata,
                            }
                        )
                        break

            # Display official texts if we found any
            if official_texts:
                text += "\n" + "=" * 80 + "\n"
                text += "**📜 Official Text from Your Purchased Standards**\n"
                text += "=" * 80 + "\n\n"

                for item in official_texts:
                    text += f"### {item['framework_name']} - {item['control_id']}\n\n"
                    text += f"**{item['clause'].title}**\n\n"

                    # Show content (truncate if very long)
                    content = item["clause"].content
                    if len(content) > 1000:
                        content = (
                            content[:1000]
                            + "...\n\n*[Content truncated - use get_clause for full text]*"
                        )
                    text += f"{content}\n\n"

                    if item["clause"].page:
                        text += f"📄 Page {item['clause'].page}\n"

                    text += f"**Source:** {item['metadata'].title} (your licensed copy)\n"
                    text += "⚠️ Licensed content - do not redistribute\n\n"

        return [TextContent(type="text", text=text)]

    elif name == "search_controls":
        query = str(arguments.get("query") or "").strip()
        if not query:
            return [
                TextContent(
                    type="text",
                    text="Error: query is required and must not be empty. "
                    "Provide a keyword or phrase (e.g., 'encryption', 'access control').",
                )
            ]
        frameworks = arguments.get("frameworks")
        try:
            limit = min(max(int(arguments.get("limit", 10) or 10), 1), 100)
        except (ValueError, TypeError):
            limit = 10

        results = scf_data.search_controls(query, frameworks, limit)

        if not results:
            return [
                TextContent(
                    type="text",
                    text=f"No controls found matching '{query}'. Try different keywords.",
                )
            ]

        text = f"**Found {len(results)} control(s) matching '{query}'**\n\n"
        for result in results:
            text += f"**{result['control_id']}: {result['name']}**\n"
            text += f"{result['snippet']}\n"
            text += f"*Mapped to: {', '.join(result['mapped_frameworks'][:5])}*\n\n"

        return [TextContent(type="text", text=text)]

    elif name == "list_frameworks":
        category = arguments.get("category")
        categories = scf_data.framework_categories

        if category:
            # Filter to a specific category
            if category not in categories:
                available = ", ".join(sorted(categories.keys()))
                return [
                    TextContent(
                        type="text",
                        text=f"Category '{category}' not found.\n\n**Available categories:** {available}",
                    )
                ]

            fw_keys = categories[category]
            text = f"**{category.replace('_', ' ').title()}** ({len(fw_keys)} frameworks)\n\n"
            for fw_key in sorted(fw_keys):
                fw = scf_data.frameworks.get(fw_key)
                if fw:
                    text += f"- **{fw['key']}**: {fw['name']} ({fw['controls_mapped']} controls)\n"
        else:
            # Show all frameworks grouped by category
            text = f"**Available Frameworks ({len(scf_data.frameworks)} total, {len(categories)} categories)**\n\n"
            for cat_name in sorted(categories.keys()):
                fw_keys = categories[cat_name]
                text += f"\n### {cat_name.replace('_', ' ').title()} ({len(fw_keys)})\n"
                for fw_key in sorted(fw_keys):
                    fw = scf_data.frameworks.get(fw_key)
                    if fw:
                        text += f"- `{fw['key']}`: {fw['name']} ({fw['controls_mapped']} controls)\n"

        return [TextContent(type="text", text=text)]

    elif name == "get_framework_controls":
        framework = str(arguments.get("framework") or "").strip()
        if not framework:
            return [
                TextContent(
                    type="text",
                    text="Error: framework is required and must not be empty. "
                    "Use list_frameworks to discover valid framework keys.",
                )
            ]
        include_descriptions = bool(arguments.get("include_descriptions", False))

        if framework not in scf_data.frameworks:
            available = ", ".join(scf_data.frameworks.keys())
            return [
                TextContent(
                    type="text",
                    text=f"Framework '{framework}' not found. Available: {available}",
                )
            ]

        controls = scf_data.get_framework_controls(framework, include_descriptions)

        fw_info = scf_data.frameworks[framework]
        text = f"**{fw_info['name']}**\n"
        text += f"**Total Controls:** {len(controls)}\n\n"

        # Group by domain for readability
        by_domain: dict[str, list] = {}
        for ctrl in controls:
            # Get full control to get domain
            full_ctrl = scf_data.get_control(ctrl["scf_id"])
            if full_ctrl:
                domain = full_ctrl["domain"]
                if domain not in by_domain:
                    by_domain[domain] = []
                by_domain[domain].append(ctrl)

        for domain, domain_ctrls in sorted(by_domain.items()):
            text += f"\n**{domain}**\n"
            for ctrl in domain_ctrls[:10]:  # Limit per domain for readability
                text += f"- **{ctrl['scf_id']}**: {ctrl['scf_name']}\n"
                text += f"  Maps to: {', '.join(ctrl['framework_control_ids'][:5])}\n"
                if include_descriptions:
                    text += f"  {ctrl['description'][:100]}...\n"

            if len(domain_ctrls) > 10:
                text += f"  *... and {len(domain_ctrls) - 10} more controls*\n"

        return [TextContent(type="text", text=text)]

    elif name == "map_frameworks":
        source_framework = str(arguments.get("source_framework") or "").strip()
        target_framework = str(arguments.get("target_framework") or "").strip()
        if not source_framework or not target_framework:
            return [
                TextContent(
                    type="text",
                    text="Error: both source_framework and target_framework are required. "
                    "Use list_frameworks to discover valid framework keys.",
                )
            ]
        source_control = arguments.get("source_control")

        # Validate frameworks exist
        if source_framework not in scf_data.frameworks:
            available = ", ".join(scf_data.frameworks.keys())
            return [
                TextContent(
                    type="text",
                    text=f"Source framework '{source_framework}' not found. Available: {available}",
                )
            ]

        if target_framework not in scf_data.frameworks:
            available = ", ".join(scf_data.frameworks.keys())
            return [
                TextContent(
                    type="text",
                    text=f"Target framework '{target_framework}' not found. Available: {available}",
                )
            ]

        mappings = scf_data.map_frameworks(source_framework, target_framework, source_control)

        if not mappings:
            return [
                TextContent(
                    type="text",
                    text=f"No mappings found between {source_framework} and {target_framework}",
                )
            ]

        source_name = scf_data.frameworks[source_framework]["name"]
        target_name = scf_data.frameworks[target_framework]["name"]

        text = f"**Mapping: {source_name} → {target_name}**\n"
        if source_control:
            text += f"**Filtered to source control: {source_control}**\n"
        text += f"**Found {len(mappings)} SCF controls**\n\n"

        for mapping in mappings[:20]:  # Limit for readability
            text += (
                f"**{mapping['scf_id']}: {mapping['scf_name']}** (weight: {mapping['weight']})\n"
            )
            text += f"- Source ({source_framework}): {', '.join(mapping['source_controls'][:5])}\n"
            if mapping["target_controls"]:
                text += (
                    f"- Target ({target_framework}): {', '.join(mapping['target_controls'][:5])}\n"
                )
            else:
                text += f"- Target ({target_framework}): *No direct mapping*\n"
            text += "\n"

        if len(mappings) > 20:
            text += f"\n*Showing first 20 of {len(mappings)} mappings*\n"

        # Check if user has paid standards for source or target frameworks
        if registry.has_paid_standards():
            source_provider = registry.get_provider(source_framework)
            target_provider = registry.get_provider(target_framework)

            if source_provider or target_provider:
                text += "\n" + "=" * 80 + "\n"
                text += "**📜 Official Text from Your Purchased Standards**\n"
                text += "=" * 80 + "\n\n"

                # Show example from first mapping
                if mappings:
                    example_mapping = mappings[0]

                    # Show source framework official text
                    if source_provider and example_mapping["source_controls"]:
                        for control_id in example_mapping["source_controls"][:1]:
                            clause = source_provider.get_clause(control_id)
                            if clause:
                                metadata = source_provider.get_metadata()
                                text += f"### {source_name} - {control_id}\n\n"
                                text += f"**{clause.title}**\n\n"

                                content = clause.content
                                if len(content) > 800:
                                    content = content[:800] + "...\n\n*[Truncated]*"
                                text += f"{content}\n\n"

                                if clause.page:
                                    text += f"📄 Page {clause.page} | "
                                text += f"**Source:** {metadata.title}\n\n"

                    # Show target framework official text
                    if target_provider and example_mapping["target_controls"]:
                        for control_id in example_mapping["target_controls"][:1]:
                            clause = target_provider.get_clause(control_id)
                            if clause:
                                metadata = target_provider.get_metadata()
                                text += f"### {target_name} - {control_id}\n\n"
                                text += f"**{clause.title}**\n\n"

                                content = clause.content
                                if len(content) > 800:
                                    content = content[:800] + "...\n\n*[Truncated]*"
                                text += f"{content}\n\n"

                                if clause.page:
                                    text += f"📄 Page {clause.page} | "
                                text += f"**Source:** {metadata.title}\n\n"

                text += "⚠️ Licensed content - do not redistribute\n"
                text += (
                    "\n*Showing example from first mapping. Use get_clause for specific clauses.*\n"
                )

        return [TextContent(type="text", text=text)]

    elif name == "list_available_standards":
        standards = registry.list_standards()

        text = f"**Available Standards ({len(standards)} total)**\n\n"

        for std in standards:
            if std["type"] == "built-in":
                text += f"### {std['title']} (Built-in)\n"
                text += f"- **License:** {std['license']}\n"
                text += f"- **Coverage:** {std['controls']}\n\n"
            else:
                text += f"### {std['title']} (Purchased)\n"
                text += f"- **ID:** `{std['standard_id']}`\n"
                text += f"- **Version:** {std['version']}\n"
                text += f"- **License:** {std['license']}\n"
                text += f"- **Purchased from:** {std['purchased_from']}\n"
                text += f"- **Purchase date:** {std['purchase_date']}\n\n"

        if not registry.has_paid_standards():
            text += "\n*No purchased standards imported yet. Purchase a standard "
            text += "(e.g., ISO 27001 from ISO.org) and use the import tool to add it.*\n"

        return [TextContent(type="text", text=text)]

    elif name == "query_standard":
        standard = str(arguments.get("standard") or "").strip()
        query = str(arguments.get("query") or "").strip()
        if not standard or not query:
            return [
                TextContent(
                    type="text",
                    text="Error: both standard and query are required and must not be empty. "
                    "Use list_available_standards to see available standard IDs.",
                )
            ]
        try:
            limit = min(max(int(arguments.get("limit", 10) or 10), 1), 50)
        except (ValueError, TypeError):
            limit = 10

        provider = registry.get_provider(standard)
        if not provider:
            available = [s["standard_id"] for s in registry.list_standards() if s["type"] == "paid"]
            if available:
                text = f"Standard '{standard}' not found. Available: {', '.join(available)}"
            else:
                text = "No purchased standards available. Import a standard first using the import tool."
            return [TextContent(type="text", text=text)]

        results = provider.search(query, limit=limit)

        if not results:
            return [TextContent(type="text", text=f"No results found for '{query}' in {standard}")]

        metadata = provider.get_metadata()
        text = f"**{metadata.title} - Search Results for '{query}'**\n\n"
        text += f"Found {len(results)} result(s)\n\n"

        for result in results:
            text += f"### {result.clause_id}: {result.title}\n"
            if result.section_type:
                text += f"*{result.section_type}*\n"
            text += f"{result.content[:300]}...\n"
            if result.page:
                text += f"📄 Page {result.page}\n"
            text += f"\n**Source:** {metadata.title} (your licensed copy)\n"
            text += "⚠️ Licensed content - do not redistribute\n\n"

        return [TextContent(type="text", text=text)]

    elif name == "get_clause":
        standard = str(arguments.get("standard") or "").strip()
        clause_id = str(arguments.get("clause_id") or "").strip()
        if not standard or not clause_id:
            return [
                TextContent(
                    type="text",
                    text="Error: both standard and clause_id are required and must not be empty. "
                    "Use query_standard to discover clause IDs.",
                )
            ]

        provider = registry.get_provider(standard)
        if not provider:
            available = [s["standard_id"] for s in registry.list_standards() if s["type"] == "paid"]
            if available:
                text = f"Standard '{standard}' not found. Available: {', '.join(available)}"
            else:
                text = "No purchased standards available. Import a standard first using the import tool."
            return [TextContent(type="text", text=text)]

        result = provider.get_clause(clause_id)

        if not result:
            return [TextContent(type="text", text=f"Clause '{clause_id}' not found in {standard}")]

        metadata = provider.get_metadata()
        text = f"**{metadata.title}**\n\n"
        text += f"## {result.clause_id}: {result.title}\n\n"
        if result.section_type:
            text += f"*{result.section_type}*\n\n"
        text += f"{result.content}\n\n"
        if result.page:
            text += f"📄 **Page:** {result.page}\n"
        text += f"\n**Source:** {metadata.title} (your licensed copy, purchased {metadata.purchase_date})\n"
        text += f"**License:** {metadata.license}\n"
        text += "⚠️ **This content is from your personally licensed copy. Do not share or redistribute.**\n"

        return [TextContent(type="text", text=text)]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Main entry point for the server."""
    # Display legal notice on startup
    print_legal_notice(registry)

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
