#!/usr/bin/env python3
"""HTTP Server Entry Point for Security Controls MCP.

This provides HTTP transport (Server-Sent Events) for remote MCP clients.
Compatible with Ansvar platform's HTTP MCP client.
"""
import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict

import uvicorn
from mcp.server import Server
from mcp.types import TextContent, Tool
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, StreamingResponse
from starlette.routing import Route

from .data_loader import SCFData
from .legal_notice import print_legal_notice

logger = logging.getLogger(__name__)

SERVER_VERSION = "0.4.2"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB max upload size

# Initialize data loader
scf_data = SCFData()

# Create MCP server instance
mcp_server = Server("security-controls-mcp")

# HTML template for standards upload interface
UPLOAD_PAGE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Standards Import - Security Controls MCP</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #2d3748;
        }

        .container { max-width: 1200px; margin: 0 auto; }

        .header {
            background: white;
            border-radius: 12px;
            padding: 24px 32px;
            margin-bottom: 24px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }

        .header h1 { font-size: 28px; font-weight: 600; color: #1a202c; margin-bottom: 8px; }
        .header p { color: #718096; font-size: 15px; }

        .upload-card {
            background: white;
            border-radius: 12px;
            padding: 32px;
            margin-bottom: 24px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }

        .upload-area {
            border: 2px dashed #cbd5e0;
            border-radius: 8px;
            padding: 48px 24px;
            text-align: center;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .upload-area:hover { border-color: #4299e1; background: #ebf8ff; }
        .upload-area.dragging { border-color: #3182ce; background: #bee3f8; }

        .upload-icon { font-size: 48px; color: #4299e1; margin-bottom: 16px; }
        .upload-text { font-size: 16px; color: #4a5568; margin-bottom: 8px; }
        .upload-hint { font-size: 14px; color: #a0aec0; }

        input[type="file"] { display: none; }

        .btn {
            display: inline-block;
            padding: 12px 32px;
            font-size: 15px;
            font-weight: 500;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .btn-primary { background: #4299e1; color: white; }
        .btn-primary:hover { background: #3182ce; }
        .btn-primary:disabled { background: #cbd5e0; cursor: not-allowed; }

        .btn-container { margin-top: 24px; text-align: center; }

        .processing-indicator {
            display: none;
            text-align: center;
            padding: 24px;
            color: #4a5568;
        }

        .processing-indicator.active { display: block; }

        .spinner {
            border: 3px solid #e2e8f0;
            border-top: 3px solid #4299e1;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 16px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .results-container {
            display: none;
            background: white;
            border-radius: 12px;
            padding: 32px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }

        .results-container.active { display: block; }

        .results-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 2px solid #e2e8f0;
        }

        .results-title { font-size: 22px; font-weight: 600; color: #1a202c; }

        .badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
        }

        .badge-success { background: #c6f6d5; color: #22543d; }
        .badge-warning { background: #fef5e7; color: #744210; }
        .badge-error { background: #fed7d7; color: #742a2a; }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }

        .metric-card { background: #f7fafc; border-radius: 8px; padding: 20px; }

        .metric-label {
            font-size: 13px;
            color: #718096;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .metric-value { font-size: 28px; font-weight: 600; color: #2d3748; }
        .metric-subtext { font-size: 14px; color: #a0aec0; margin-top: 4px; }

        .section-title {
            font-size: 18px;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 16px;
        }

        .missing-controls { margin-bottom: 32px; }

        .control-chip {
            display: inline-block;
            background: #edf2f7;
            color: #4a5568;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
            margin: 4px;
        }

        .controls-table-container { overflow-x: auto; }

        table { width: 100%; border-collapse: collapse; }

        th {
            text-align: left;
            padding: 12px;
            background: #f7fafc;
            color: #4a5568;
            font-size: 13px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 2px solid #e2e8f0;
        }

        td {
            padding: 16px 12px;
            border-bottom: 1px solid #e2e8f0;
            font-size: 14px;
        }

        tr:hover { background: #f7fafc; }

        .control-id { font-weight: 600; color: #2d3748; }
        .control-title { color: #4a5568; }
        .control-category { color: #718096; font-size: 13px; }

        .error-message {
            background: #fed7d7;
            color: #742a2a;
            padding: 16px;
            border-radius: 8px;
            margin-bottom: 16px;
        }

        @media (max-width: 768px) {
            .header h1 { font-size: 22px; }
            .upload-card, .results-container { padding: 20px; }
            .metrics-grid { grid-template-columns: 1fr; }
            table { font-size: 13px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Standards Import</h1>
            <p>Upload a PDF standard to extract security controls and analyze coverage</p>
        </div>

        <div class="upload-card">
            <form id="uploadForm" method="POST" enctype="multipart/form-data">
                <div class="upload-area" id="uploadArea">
                    <div class="upload-icon">📄</div>
                    <div class="upload-text">Click to select a PDF file</div>
                    <div class="upload-hint">or drag and drop here</div>
                    <input type="file" id="fileInput" accept=".pdf,application/pdf" required>
                </div>
                <div class="btn-container">
                    <button type="submit" class="btn btn-primary" id="submitBtn" disabled>
                        Extract Controls
                    </button>
                </div>
            </form>

            <div class="processing-indicator" id="processingIndicator">
                <div class="spinner"></div>
                <div>Processing your PDF... This may take a moment.</div>
            </div>
        </div>

        <div class="results-container" id="resultsContainer">
            <div class="results-header">
                <div class="results-title">Extraction Results</div>
                <div id="confidenceBadge"></div>
            </div>

            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Version Detected</div>
                    <div class="metric-value" id="versionValue">-</div>
                    <div class="metric-subtext" id="versionDetection">-</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Coverage</div>
                    <div class="metric-value" id="coverageValue">-</div>
                    <div class="metric-subtext" id="coverageText">-</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Controls Extracted</div>
                    <div class="metric-value" id="controlsCount">-</div>
                    <div class="metric-subtext" id="expectedCount">-</div>
                </div>
            </div>

            <div class="missing-controls" id="missingControlsSection" style="display: none;">
                <div class="section-title">Missing Controls</div>
                <div id="missingControlsList"></div>
            </div>

            <div>
                <div class="section-title">Control Details</div>
                <div class="controls-table-container">
                    <table id="controlsTable">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Title</th>
                                <th>Category</th>
                                <th>Page</th>
                            </tr>
                        </thead>
                        <tbody id="controlsTableBody">
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const submitBtn = document.getElementById('submitBtn');
        const uploadForm = document.getElementById('uploadForm');
        const processingIndicator = document.getElementById('processingIndicator');
        const resultsContainer = document.getElementById('resultsContainer');

        uploadArea.addEventListener('click', () => fileInput.click());

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                const file = e.target.files[0];
                uploadArea.querySelector('.upload-text').textContent = file.name;
                submitBtn.disabled = false;
            }
        });

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragging');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragging');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragging');
            const files = e.dataTransfer.files;
            if (files.length > 0 && files[0].type === 'application/pdf') {
                fileInput.files = files;
                uploadArea.querySelector('.upload-text').textContent = files[0].name;
                submitBtn.disabled = false;
            }
        });

        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            processingIndicator.classList.add('active');
            submitBtn.disabled = true;
            resultsContainer.classList.remove('active');

            try {
                const response = await fetch('/api/standards/extract', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                if (response.ok) {
                    displayResults(data);
                } else {
                    displayError(data.message || data.error || 'An error occurred during extraction');
                }
            } catch (error) {
                displayError('Network error: ' + error.message);
            } finally {
                processingIndicator.classList.remove('active');
                submitBtn.disabled = false;
            }
        });

        function displayResults(data) {
            resultsContainer.classList.add('active');

            document.getElementById('versionValue').textContent = data.version || 'Unknown';
            document.getElementById('versionDetection').textContent =
                data.version_detection ? data.version_detection.replace('_', ' ') : '';

            const confidence = data.confidence_score || 0;
            const badgeEl = document.getElementById('confidenceBadge');
            let badgeClass = 'badge-error';
            let badgeText = 'Low Confidence';

            if (confidence >= 0.9) {
                badgeClass = 'badge-success';
                badgeText = 'High Confidence';
            } else if (confidence >= 0.7) {
                badgeClass = 'badge-warning';
                badgeText = 'Medium Confidence';
            }

            badgeEl.className = 'badge ' + badgeClass;
            badgeEl.textContent = badgeText + ' (' + Math.round(confidence * 100) + '%)';

            const extracted = data.controls ? data.controls.length : 0;
            const expected = data.expected_control_ids ? data.expected_control_ids.length : 0;
            const coveragePercent = expected > 0 ? Math.round((extracted / expected) * 100) : 0;

            document.getElementById('coverageValue').textContent = coveragePercent + '%';
            document.getElementById('coverageText').textContent =
                extracted + ' of ' + (expected || 'unknown') + ' expected controls';
            document.getElementById('controlsCount').textContent = extracted;
            document.getElementById('expectedCount').textContent =
                'Expected: ' + (expected || 'unknown');

            if (data.missing_control_ids && data.missing_control_ids.length > 0) {
                const section = document.getElementById('missingControlsSection');
                const list = document.getElementById('missingControlsList');
                section.style.display = 'block';
                list.textContent = '';
                data.missing_control_ids.forEach(id => {
                    const chip = document.createElement('span');
                    chip.className = 'control-chip';
                    chip.textContent = id;
                    list.appendChild(chip);
                });
            } else {
                document.getElementById('missingControlsSection').style.display = 'none';
            }

            const tbody = document.getElementById('controlsTableBody');
            tbody.textContent = '';

            if (data.controls && data.controls.length > 0) {
                data.controls.forEach(control => {
                    const row = document.createElement('tr');
                    const idCell = document.createElement('td');
                    idCell.className = 'control-id';
                    idCell.textContent = control.id || '-';
                    const titleCell = document.createElement('td');
                    titleCell.className = 'control-title';
                    titleCell.textContent = control.title || '-';
                    const catCell = document.createElement('td');
                    catCell.className = 'control-category';
                    catCell.textContent = control.category || '-';
                    const pageCell = document.createElement('td');
                    pageCell.textContent = control.page || '-';
                    row.appendChild(idCell);
                    row.appendChild(titleCell);
                    row.appendChild(catCell);
                    row.appendChild(pageCell);
                    tbody.appendChild(row);
                });
            } else {
                const row = document.createElement('tr');
                const cell = document.createElement('td');
                cell.colSpan = 4;
                cell.style.textAlign = 'center';
                cell.style.padding = '24px';
                cell.style.color = '#a0aec0';
                cell.textContent = 'No controls extracted';
                row.appendChild(cell);
                tbody.appendChild(row);
            }

            resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }

        function displayError(message) {
            resultsContainer.classList.add('active');
            resultsContainer.textContent = '';
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            const strongEl = document.createElement('strong');
            strongEl.textContent = 'Error: ';
            errorDiv.appendChild(strongEl);
            errorDiv.appendChild(document.createTextNode(message));
            resultsContainer.appendChild(errorDiv);
            const btnDiv = document.createElement('div');
            btnDiv.style.textAlign = 'center';
            btnDiv.style.marginTop = '16px';
            const btn = document.createElement('button');
            btn.className = 'btn btn-primary';
            btn.textContent = 'Try Again';
            btn.onclick = () => location.reload();
            btnDiv.appendChild(btn);
            resultsContainer.appendChild(btnDiv);
            resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    </script>
</body>
</html>
"""


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="version_info",
            description=(
                "Get server version, statistics, and database info. "
                "Call this first to understand what data is available."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
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
                        "description": "Framework key (e.g., dora, iso_27001_2022, nist_csf_2.0)",
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
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""

    if name == "version_info":
        # Collect framework categories for summary
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
        return [TextContent(type="text", text=text)]

    elif name == "get_control":
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
        by_domain: Dict[str, list] = {}
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

        return [TextContent(type="text", text=text)]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def health_check(request):
    """Health check endpoint."""
    return JSONResponse(
        {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": {"connected": True, "type": "json", "version": "SCF 2025.4"},
            "service": "security-controls-api",
            "controls_count": len(scf_data.controls),
            "frameworks_count": len(scf_data.frameworks),
        }
    )


# ============== REST API ENDPOINTS ==============

async def api_search_controls(request):
    """REST API: Search controls by keyword."""
    try:
        body = await request.json()
        query = body.get("query", "")
        frameworks = body.get("frameworks")
        limit = body.get("limit", 10)

        if not query:
            return JSONResponse({"error": "Bad Request", "message": "Query is required"}, status_code=400)

        results = scf_data.search_controls(query, frameworks, limit)
        return JSONResponse({
            "query": query,
            "count": len(results),
            "results": results
        })
    except Exception as e:
        logger.error(f"Error in api_search_controls: {e}", exc_info=True)
        return JSONResponse({"error": "Internal Server Error", "message": "An error occurred while processing your search"}, status_code=500)


async def api_get_control(request):
    """REST API: Get specific control by ID."""
    control_id = request.path_params["control_id"]
    include_mappings = request.query_params.get("include_mappings", "true").lower() == "true"

    control = scf_data.get_control(control_id)
    if not control:
        return JSONResponse({"error": "Not Found", "message": f"Control {control_id} not found"}, status_code=404)

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

    return JSONResponse(response)


async def api_list_frameworks(request):
    """REST API: List all frameworks."""
    frameworks = list(scf_data.frameworks.values())
    frameworks.sort(key=lambda x: x["controls_mapped"], reverse=True)
    return JSONResponse({
        "count": len(frameworks),
        "frameworks": frameworks
    })


async def api_map_frameworks(request):
    """REST API: Map controls between frameworks."""
    try:
        body = await request.json()
        source_framework = body.get("source_framework")
        target_framework = body.get("target_framework")
        source_control = body.get("source_control")

        if not source_framework or not target_framework:
            return JSONResponse({"error": "Bad Request", "message": "source_framework and target_framework required"}, status_code=400)

        if source_framework not in scf_data.frameworks:
            return JSONResponse({"error": "Not Found", "message": f"Framework {source_framework} not found"}, status_code=404)
        if target_framework not in scf_data.frameworks:
            return JSONResponse({"error": "Not Found", "message": f"Framework {target_framework} not found"}, status_code=404)

        mappings = scf_data.map_frameworks(source_framework, target_framework, source_control)
        return JSONResponse({
            "source_framework": source_framework,
            "target_framework": target_framework,
            "count": len(mappings),
            "mappings": mappings
        })
    except Exception as e:
        logger.error(f"Error in api_map_frameworks: {e}", exc_info=True)
        return JSONResponse({"error": "Internal Server Error", "message": "An error occurred while mapping frameworks"}, status_code=500)


async def api_root(request):
    """REST API: Root endpoint."""
    return JSONResponse({
        "service": "security-controls-api",
        "version": SERVER_VERSION,
        "database": "SCF 2025.4",
        "endpoints": {
            "health": "/health",
            "search": "POST /api/search",
            "control": "GET /api/controls/{control_id}",
            "frameworks": "GET /api/frameworks",
            "map": "POST /api/map",
            "extract": "POST /api/standards/extract",
            "upload": "GET /standards/upload"
        }
    })


# ============== STANDARDS IMPORT WEB UI ==============

async def standards_upload_page(request: Request):
    """Serve the standards upload HTML page."""
    return HTMLResponse(
        UPLOAD_PAGE_HTML,
        headers={
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Content-Security-Policy": "default-src 'self' 'unsafe-inline'"
        }
    )


async def api_standards_extract(request: Request):
    """Extract controls from uploaded PDF standard.

    Accepts multipart/form-data with a 'file' field containing the PDF.
    Returns ExtractionResult as JSON.
    """
    try:
        # Parse multipart form data
        form = await request.form()
        file_field = form.get("file")

        if not file_field:
            return JSONResponse(
                {"error": "Bad Request", "message": "No file provided"},
                status_code=400
            )

        # Check content length if available
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_FILE_SIZE:
            return JSONResponse(
                {"error": "Bad Request", "message": "File too large (max 50MB)"},
                status_code=413
            )

        # Read PDF bytes
        pdf_bytes = await file_field.read()

        if not pdf_bytes or len(pdf_bytes) == 0:
            return JSONResponse(
                {"error": "Bad Request", "message": "Empty file provided"},
                status_code=400
            )

        # Check file size after reading
        if len(pdf_bytes) > MAX_FILE_SIZE:
            return JSONResponse(
                {"error": "Bad Request", "message": "File too large (max 50MB)"},
                status_code=413
            )

        # Validate PDF magic bytes
        if not pdf_bytes.startswith(b'%PDF-'):
            return JSONResponse(
                {"error": "Bad Request", "message": "Invalid PDF file"},
                status_code=400
            )

        # Try to extract using ISO 27001 extractor (the only one currently available)
        try:
            # Import the extractor registry
            from .extractors.registry import get_extractor
            from .extractors.specialized.iso_27001 import ISO27001Extractor

            # Get the ISO 27001 extractor
            extractor_class = get_extractor("iso_27001")

            if not extractor_class:
                # If not registered, use the class directly
                extractor_class = ISO27001Extractor

            # Create extractor instance and extract
            extractor = extractor_class()
            result = extractor.extract(pdf_bytes)

            # Convert ExtractionResult to dict for JSON serialization
            result_dict = {
                "standard_id": result.standard_id,
                "version": result.version,
                "version_detection": result.version_detection.value,
                "version_evidence": result.version_evidence,
                "controls": [
                    {
                        "id": ctrl.id,
                        "title": ctrl.title,
                        "content": ctrl.content[:200] if ctrl.content else "",  # Truncate for UI
                        "page": ctrl.page,
                        "category": ctrl.category,
                        "parent": ctrl.parent
                    }
                    for ctrl in result.controls
                ],
                "expected_control_ids": result.expected_control_ids,
                "missing_control_ids": result.missing_control_ids,
                "confidence_score": result.confidence_score,
                "extraction_method": result.extraction_method,
                "extraction_duration_seconds": result.extraction_duration_seconds,
                "warnings": result.warnings
            }

            return JSONResponse(result_dict)

        except ImportError as e:
            logger.error(f"Import error in extraction: {e}", exc_info=True)
            return JSONResponse(
                {
                    "error": "Server Error",
                    "message": "Extraction tools not available. Install with: pip install -e '.[import-tools]'"
                },
                status_code=500
            )
        except Exception as e:
            logger.error(f"Extraction error: {e}", exc_info=True)
            return JSONResponse(
                {
                    "error": "Extraction Error",
                    "message": "Failed to extract controls. Please verify the PDF is a valid ISO 27001 standard.",
                    "warnings": ["Extraction failed. Check server logs for details."]
                },
                status_code=500
            )

    except Exception as e:
        logger.error(f"Error in api_standards_extract: {e}", exc_info=True)
        return JSONResponse(
            {"error": "Internal Server Error", "message": "An error occurred while processing the file"},
            status_code=500
        )


async def mcp_endpoint(request):
    """MCP endpoint - accepts JSON-RPC requests."""
    try:
        # Parse JSON-RPC request
        body = await request.json()
        method = body.get("method")
        params = body.get("params", {})
        request_id = body.get("id", 1)

        # Handle initialize
        if method == "initialize":
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "security-controls-mcp", "version": SERVER_VERSION},
                },
            }
            return StreamingResponse(
                iter([f"event: message\ndata: {json.dumps(response)}\n\n"]),
                media_type="text/event-stream",
            )

        # Handle notifications (no response needed per JSON-RPC)
        elif method == "notifications/initialized":
            response = {"jsonrpc": "2.0", "id": request_id, "result": {}}
            return StreamingResponse(
                iter([f"event: message\ndata: {json.dumps(response)}\n\n"]),
                media_type="text/event-stream",
            )

        # Handle ping
        elif method == "ping":
            return StreamingResponse(
                iter([f"event: message\ndata: {json.dumps({'jsonrpc': '2.0', 'id': request_id, 'result': {}})}\n\n"]),
                media_type="text/event-stream",
            )

        # Handle list tools
        elif method == "tools/list":
            tools = await list_tools()
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "inputSchema": tool.inputSchema,
                        }
                        for tool in tools
                    ]
                },
            }
            return StreamingResponse(
                iter([f"event: message\ndata: {json.dumps(response)}\n\n"]),
                media_type="text/event-stream",
            )

        # Handle tool call
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            # Call the tool
            result = await call_tool(tool_name, arguments)

            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"content": [{"type": "text", "text": item.text} for item in result]},
            }
            return StreamingResponse(
                iter([f"event: message\ndata: {json.dumps(response)}\n\n"]),
                media_type="text/event-stream",
            )

        else:
            # Unknown method
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }
            return StreamingResponse(
                iter([f"event: message\ndata: {json.dumps(response)}\n\n"]),
                media_type="text/event-stream",
            )

    except Exception as e:
        # Error response
        logger.error(f"Error in mcp_sse_endpoint: {e}", exc_info=True)
        response = {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {"code": -32603, "message": "Internal server error"},
        }
        return StreamingResponse(
            iter([f"event: message\ndata: {json.dumps(response)}\n\n"]),
            media_type="text/event-stream",
            status_code=500,
        )


# Starlette app - serves both MCP and REST API
app = Starlette(
    routes=[
        # Health & root
        Route("/health", health_check),
        Route("/", api_root),
        # MCP protocol endpoint
        Route("/mcp", mcp_endpoint, methods=["POST"]),
        # REST API endpoints
        Route("/api/search", api_search_controls, methods=["POST"]),
        Route("/api/controls/{control_id}", api_get_control),
        Route("/api/frameworks", api_list_frameworks),
        Route("/api/map", api_map_frameworks, methods=["POST"]),
        # Standards import web UI
        Route("/standards/upload", standards_upload_page),
        Route("/api/standards/extract", api_standards_extract, methods=["POST"]),
    ],
)


def main():
    """Start HTTP server."""
    # Display legal notice on startup
    print_legal_notice()

    # Get port from environment
    port = int(os.getenv("PORT", "3000"))

    print(f"\n✓ Security Controls MCP HTTP server starting on port {port}")
    print(
        f"✓ Loaded {len(scf_data.controls)} controls across {len(scf_data.frameworks)} frameworks\n"
    )

    # Run server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
