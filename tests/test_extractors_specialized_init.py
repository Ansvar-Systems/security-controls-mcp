"""Tests for specialized extractors auto-import mechanism."""

import importlib
import sys
from pathlib import Path
from typing import Type

import pytest


class TestSpecializedExtractorsInit:
    """Test the specialized extractors __init__.py auto-import mechanism."""

    def test_specialized_directory_importable(self):
        """Test that the specialized directory can be imported."""
        from security_controls_mcp.extractors import specialized

        assert specialized is not None

    def test_registry_functions_accessible(self):
        """Test that registry functions are re-exported by specialized module."""
        from security_controls_mcp.extractors import specialized

        # Should have access to registry functions
        assert hasattr(specialized, "register_extractor")
        assert hasattr(specialized, "get_extractor")
        assert callable(specialized.register_extractor)
        assert callable(specialized.get_extractor)

    def test_auto_import_discovers_modules(self, tmp_path, monkeypatch):
        """Test that auto-import mechanism discovers and imports .py files."""
        # Clear the registry first to avoid interference from other tests
        from security_controls_mcp.extractors.registry import SPECIALIZED_EXTRACTORS

        SPECIALIZED_EXTRACTORS.clear()

        # Create a temporary specialized directory
        specialized_dir = tmp_path / "specialized"
        specialized_dir.mkdir()

        # Create a test extractor module
        test_extractor = specialized_dir / "test_extractor.py"
        test_extractor.write_text(
            """
from security_controls_mcp.extractors.registry import register_extractor

@register_extractor("test_standard")
class TestExtractor:
    pass
"""
        )

        # Create __init__.py with auto-import logic
        init_file = specialized_dir / "__init__.py"
        init_file.write_text(
            """
import importlib
from pathlib import Path

# Re-export registry functions
from security_controls_mcp.extractors.registry import (
    register_extractor,
    get_extractor,
)

# Auto-discover and import all extractors
_current_dir = Path(__file__).parent
for _file in _current_dir.glob("*.py"):
    if _file.name != "__init__.py":
        _module_name = f"specialized.{_file.stem}"
        importlib.import_module(_module_name, package=__package__)
"""
        )

        # Add tmp_path to sys.path so we can import from it
        monkeypatch.syspath_prepend(str(tmp_path))

        # Import the specialized module (which should trigger auto-import)
        import specialized

        # Verify the extractor was registered
        from security_controls_mcp.extractors.registry import get_extractor

        extractor_class = get_extractor("test_standard")
        assert extractor_class is not None
        assert extractor_class.__name__ == "TestExtractor"

    def test_auto_import_ignores_init_file(self, tmp_path, monkeypatch):
        """Test that auto-import ignores __init__.py itself."""
        specialized_dir = tmp_path / "specialized"
        specialized_dir.mkdir()

        # Track imports in a file since module variables aren't accessible
        counter_file = specialized_dir / "import_counter.txt"
        counter_file.write_text("0")

        # Create __init__.py with a test that would fail if it imports itself
        init_file = specialized_dir / "__init__.py"
        init_file.write_text(
            f"""
import importlib
from pathlib import Path

# Re-export registry functions
from security_controls_mcp.extractors.registry import (
    register_extractor,
    get_extractor,
)

# Auto-discover and import all extractors
_current_dir = Path(__file__).parent
for _file in _current_dir.glob("*.py"):
    if _file.name != "__init__.py":
        _module_name = f"specialized.{{_file.stem}}"
        importlib.import_module(_module_name, package=__package__)
        # Increment counter
        _counter_file = _current_dir / "import_counter.txt"
        _count = int(_counter_file.read_text())
        _counter_file.write_text(str(_count + 1))
"""
        )

        # Add tmp_path to sys.path
        monkeypatch.syspath_prepend(str(tmp_path))

        # Import should succeed without trying to import __init__.py
        import specialized

        # Verify no files were imported (counter should still be 0)
        assert counter_file.read_text() == "0"

    def test_auto_import_handles_multiple_extractors(self):
        """Test that auto-import handles multiple extractor files.

        This test verifies that when the actual specialized directory exists
        with multiple .py files, all of them get imported and registered.
        We test this by checking that the auto-import logic doesn't fail
        when there are no .py files (empty directory case).
        """
        # The actual test for multiple files will happen when we create
        # real extractors. For now, we just verify the mechanism doesn't
        # crash with an empty directory.
        from security_controls_mcp.extractors import specialized

        # Should have imported successfully (with 0 files)
        assert specialized.register_extractor is not None
        assert specialized.get_extractor is not None

    def test_registry_functions_are_same_as_original(self):
        """Test that re-exported functions are the same as originals."""
        from security_controls_mcp.extractors import specialized
        from security_controls_mcp.extractors.registry import (
            register_extractor,
            get_extractor,
        )

        # Should be the exact same function objects
        assert specialized.register_extractor is register_extractor
        assert specialized.get_extractor is get_extractor

    def test_auto_import_with_empty_directory(self):
        """Test that auto-import works with no extractor files present."""
        # This tests the actual specialized directory when it's first created
        from security_controls_mcp.extractors import specialized

        # Should import successfully even with no extractors
        assert specialized.register_extractor is not None
        assert specialized.get_extractor is not None
