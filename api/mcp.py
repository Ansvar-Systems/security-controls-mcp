"""Vercel serverless handler for Security Controls MCP.

Returns JSON responses (not SSE) for serverless compatibility.
Imports tool logic from the existing http_server module.
"""

import asyncio
import json
import os
import sys
from http.server import BaseHTTPRequestHandler

# Add src to path so security_controls_mcp is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from security_controls_mcp.http_server import (  # noqa: E402
    SERVER_VERSION,
    call_tool,
    list_tools,
)


def _cors_headers(handler):
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
    handler.send_header('Access-Control-Allow-Headers', 'Content-Type, mcp-session-id')
    handler.send_header('Access-Control-Expose-Headers', 'mcp-session-id')


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        _cors_headers(self)
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        _cors_headers(self)
        self.end_headers()
        self.wfile.write(json.dumps({
            'name': 'security-controls-mcp',
            'version': SERVER_VERSION,
            'protocol': 'mcp-streamable-http',
        }).encode())

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(content_length))

        method = body.get('method')
        params = body.get('params', {})
        request_id = body.get('id', 1)

        try:
            response = asyncio.run(_handle_method(method, params, request_id))
        except Exception as e:
            response = {
                'jsonrpc': '2.0',
                'id': request_id,
                'error': {'code': -32603, 'message': str(e)},
            }

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        _cors_headers(self)
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())


async def _handle_method(method, params, request_id):
    if method == 'initialize':
        return {
            'jsonrpc': '2.0',
            'id': request_id,
            'result': {
                'protocolVersion': '2024-11-05',
                'capabilities': {'tools': {}},
                'serverInfo': {
                    'name': 'security-controls-mcp',
                    'version': SERVER_VERSION,
                },
            },
        }

    if method == 'notifications/initialized':
        return {'jsonrpc': '2.0', 'id': request_id, 'result': {}}

    if method == 'ping':
        return {'jsonrpc': '2.0', 'id': request_id, 'result': {}}

    if method == 'tools/list':
        tools = await list_tools()
        return {
            'jsonrpc': '2.0',
            'id': request_id,
            'result': {
                'tools': [
                    {
                        'name': t.name,
                        'description': t.description,
                        'inputSchema': t.inputSchema,
                    }
                    for t in tools
                ]
            },
        }

    if method == 'tools/call':
        result = await call_tool(params.get('name'), params.get('arguments', {}))
        return {
            'jsonrpc': '2.0',
            'id': request_id,
            'result': {
                'content': [{'type': 'text', 'text': item.text} for item in result]
            },
        }

    return {
        'jsonrpc': '2.0',
        'id': request_id,
        'error': {'code': -32601, 'message': f'Method not found: {method}'},
    }
