"""Auto-discovery and import of specialized extractors.

This module automatically discovers and imports all .py files in the
specialized/ directory to trigger their @register_extractor decorators.
"""

import importlib
from pathlib import Path

# Re-export registry functions for convenience
from security_controls_mcp.extractors.registry import (
    get_extractor,
    register_extractor,
)

# Auto-discover and import all extractor modules
_current_dir = Path(__file__).parent
for _file in _current_dir.glob("*.py"):
    if _file.name != "__init__.py":
        _module_name = f"{__package__}.{_file.stem}"
        importlib.import_module(_module_name)

__all__ = ["register_extractor", "get_extractor"]
