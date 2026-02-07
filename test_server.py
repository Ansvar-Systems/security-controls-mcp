#!/usr/bin/env python3
"""Test server startup to verify all imports and initialization work correctly."""

import sys


def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")

    try:
        import security_controls_mcp
        print(f"  - security_controls_mcp: OK (v{security_controls_mcp.__version__})")
    except ImportError as e:
        print(f"  - security_controls_mcp: FAILED ({e})")
        return False

    try:
        from security_controls_mcp.server import app, registry
        print("  - server module: OK")
    except ImportError as e:
        print(f"  - server module: FAILED ({e})")
        return False

    try:
        from security_controls_mcp.data_loader import SCFData
        print("  - data_loader module: OK")
    except ImportError as e:
        print(f"  - data_loader module: FAILED ({e})")
        return False

    return True


def test_data_loading():
    """Test that SCF data loads correctly."""
    print("Testing data loading...")

    try:
        from security_controls_mcp.data_loader import SCFData

        data = SCFData()
        controls_count = len(data.controls)
        frameworks_count = len(data.frameworks)

        print(f"  - Controls loaded: {controls_count}")
        print(f"  - Frameworks loaded: {frameworks_count}")

        if controls_count < 1000:
            print("  - WARNING: Expected 1451 controls")
            return False

        if frameworks_count < 100:
            print("  - WARNING: Expected 261 frameworks")
            return False

        print("  - Data loading: OK")
        return True

    except Exception as e:
        print(f"  - Data loading: FAILED ({e})")
        return False


def test_server_initialization():
    """Test that the server can be initialized."""
    print("Testing server initialization...")

    try:
        from security_controls_mcp.server import app, registry

        # Check that registry has tools
        if not registry:
            print("  - WARNING: Registry is empty")
            return False

        print(f"  - Registry loaded with tools")
        print("  - Server initialization: OK")
        return True

    except Exception as e:
        print(f"  - Server initialization: FAILED ({e})")
        return False


def main():
    """Run all startup tests."""
    print("=" * 60)
    print("Security Controls MCP - Server Startup Test")
    print("=" * 60)

    results = []
    results.append(("Imports", test_imports()))
    results.append(("Data Loading", test_data_loading()))
    results.append(("Server Initialization", test_server_initialization()))

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\nAll tests passed! Server is ready.")
        return 0
    else:
        print("\nSome tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
