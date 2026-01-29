"""MCP server for security controls framework queries."""

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .data_loader import SCFData


# Initialize data loader
scf_data = SCFData()

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
            description="Search for controls by keyword in name or description. Returns relevant controls with snippets.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'encryption', 'access control', 'incident response')",
                    },
                    "frameworks": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional: filter to controls that map to specific frameworks",
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
                        "description": "Include control descriptions (increases token usage, default: false)",
                        "default": False,
                    },
                },
                "required": ["framework"],
            },
        ),
        Tool(
            name="map_frameworks",
            description="Map controls between two frameworks via SCF. Shows which target framework requirements are satisfied by source framework controls.",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_framework": {
                        "type": "string",
                        "description": "Source framework key (what you HAVE, e.g., iso_27001_2022)",
                    },
                    "source_control": {
                        "type": "string",
                        "description": "Optional: specific source control ID (e.g., A.5.15) to filter results",
                    },
                    "target_framework": {
                        "type": "string",
                        "description": "Target framework key (what you want to SATISFY, e.g., dora)",
                    },
                },
                "required": ["source_framework", "target_framework"],
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

        mappings = scf_data.map_frameworks(
            source_framework, target_framework, source_control
        )

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
            text += f"**{mapping['scf_id']}: {mapping['scf_name']}** (weight: {mapping['weight']})\n"
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

        return [TextContent(type="text", text=text)]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Main entry point for the server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
