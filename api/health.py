"""Health check endpoint."""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler
from pathlib import Path

# Add src to path so security_controls_mcp is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from security_controls_mcp.http_server import (  # noqa: E402
    SERVER_VERSION,
    scf_data,
    DATA_FINGERPRINT,
    DATA_BUILT,
)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            'status': 'ok',
            'server': 'security-controls-mcp',
            'version': SERVER_VERSION,
            'controls_count': len(scf_data.controls),
            'frameworks_count': len(scf_data.frameworks),
            'data_fingerprint': DATA_FINGERPRINT,
            'data_built': DATA_BUILT,
        }).encode())
