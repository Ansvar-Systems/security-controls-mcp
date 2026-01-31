"""MCP server for security controls framework queries."""

import asyncio

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


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_control",
            description="Get details about a specific SCF control by its ID (e.g., GOV-01, IAC-05)",
            inputSchema={
                "type": "object",
                "properties": {
                    "control_id": {
                        "type": "string",
                        "description": "SCF control ID (e.g., GOV-01)",
                    },
                    "include_mappings": {
                        "type": "boolean",
                        "description": "Include framework mappings (default: true)",
                        "default": True,
                    },
                },
                "required": ["control_id"],
            },
        ),
        Tool(
            name="search_controls",
            description=(
                "Search for controls by keyword in name or description. "
                "Returns relevant controls with snippets."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Search query (e.g., 'encryption', 'access control', "
                            "'incident response')"
                        ),
                    },
                    "frameworks": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "Optional: filter to controls that map to specific frameworks"
                        ),
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 10)",
                        "default": 10,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="list_frameworks",
            description="List all available security frameworks with metadata",
            inputSchema={
                "type": "object",
                "properties": {
                    "detailed": {
                        "type": "boolean",
                        "description": "Include detailed information (default: false)",
                        "default": False,
                    },
                },
            },
        ),
        Tool(
            name="get_framework_controls",
            description="Get all SCF controls that map to a specific framework",
            inputSchema={
                "type": "object",
                "properties": {
                    "framework": {
                        "type": "string",
                        "description": "Framework key (e.g., dora, iso_27001_2022, nist_csf_2_0)",
                    },
                    "include_descriptions": {
                        "type": "boolean",
                        "description": (
                            "Include control descriptions "
                            "(increases token usage, default: false)"
                        ),
                        "default": False,
                    },
                },
                "required": ["framework"],
            },
        ),
        Tool(
            name="map_frameworks",
            description=(
                "Map controls between two frameworks via SCF. Shows which target "
                "framework requirements are satisfied by source framework controls."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "source_framework": {
                        "type": "string",
                        "description": (
                            "Source framework key (what you HAVE, e.g., iso_27001_2022)"
                        ),
                    },
                    "source_control": {
                        "type": "string",
                        "description": (
                            "Optional: specific source control ID (e.g., A.5.15) "
                            "to filter results"
                        ),
                    },
                    "target_framework": {
                        "type": "string",
                        "description": (
                            "Target framework key (what you want to SATISFY, e.g., dora)"
                        ),
                    },
                },
                "required": ["source_framework", "target_framework"],
            },
        ),
        Tool(
            name="list_available_standards",
            description=(
                "List all available standards including SCF (built-in) and any "
                "purchased standards the user has imported"
            ),
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="query_standard",
            description=(
                "Search for content within a specific purchased standard. "
                "Requires the standard to be imported first."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "standard": {
                        "type": "string",
                        "description": (
                            "Standard identifier (e.g., iso_27001_2022). "
                            "Use list_available_standards to see what's available."
                        ),
                    },
                    "query": {
                        "type": "string",
                        "description": (
                            "Search query (e.g., 'encryption key management', "
                            "'access control policy')"
                        ),
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 10)",
                        "default": 10,
                    },
                },
                "required": ["standard", "query"],
            },
        ),
        Tool(
            name="get_clause",
            description=(
                "Get the full text of a specific clause/section from a purchased standard"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "standard": {
                        "type": "string",
                        "description": "Standard identifier (e.g., iso_27001_2022)",
                    },
                    "clause_id": {
                        "type": "string",
                        "description": ("Clause/section identifier (e.g., '5.1.2', 'A.5.15')"),
                    },
                },
                "required": ["standard", "clause_id"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""

    if name == "get_control":
        control_id = arguments["control_id"]
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
        query = arguments["query"]
        frameworks = arguments.get("frameworks")
        limit = arguments.get("limit", 10)

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
        frameworks = list(scf_data.frameworks.values())
        frameworks.sort(key=lambda x: x["controls_mapped"], reverse=True)

        text = f"**Available Frameworks ({len(frameworks)} total)**\n\n"
        for fw in frameworks:
            text += f"- **{fw['key']}**: {fw['name']} ({fw['controls_mapped']} controls)\n"

        return [TextContent(type="text", text=text)]

    elif name == "get_framework_controls":
        framework = arguments["framework"]
        include_descriptions = arguments.get("include_descriptions", False)

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
        source_framework = arguments["source_framework"]
        target_framework = arguments["target_framework"]
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
        standard = arguments["standard"]
        query = arguments["query"]
        limit = arguments.get("limit", 10)

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
        standard = arguments["standard"]
        clause_id = arguments["clause_id"]

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
