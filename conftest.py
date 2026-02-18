"""Root conftest.py - ensures src/ is on the Python path for all tests."""

import sys
from pathlib import Path

# Add src/ to the Python path so tests can import security_controls_mcp
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)
