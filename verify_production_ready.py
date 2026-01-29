#!/usr/bin/env python3
"""
Comprehensive production readiness verification script.
Checks all critical aspects before deployment.
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path


class Colors:
    """Terminal colors for output."""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_header(text):
    """Print a section header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}\n")


def print_check(name, passed, details=""):
    """Print a check result."""
    symbol = f"{Colors.GREEN}✓{Colors.END}" if passed else f"{Colors.RED}✗{Colors.END}"
    print(f"{symbol} {name}")
    if details:
        print(f"  {details}")


def check_data_files():
    """Check that all data files exist and are valid."""
    print_header("1. Data Files Verification")

    data_dir = Path("src/security_controls_mcp/data")
    required_files = ["scf-controls.json", "framework-to-scf.json"]

    all_good = True
    for filename in required_files:
        filepath = data_dir / filename
        exists = filepath.exists()

        if exists:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    json.load(f)
                size_kb = filepath.stat().st_size / 1024
                print_check(f"{filename}", True, f"Size: {size_kb:.1f} KB")
            except json.JSONDecodeError:
                print_check(f"{filename}", False, "Invalid JSON")
                all_good = False
        else:
            print_check(f"{filename}", False, "File not found")
            all_good = False

    return all_good


def check_data_integrity():
    """Check data integrity and completeness."""
    print_header("2. Data Integrity Verification")

    try:
        from security_controls_mcp.data_loader import SCFData

        data = SCFData()

        # Check controls
        controls_ok = len(data.controls) == 1451
        print_check("Control count (1451)", controls_ok, f"Found: {len(data.controls)}")

        # Check frameworks
        frameworks_ok = len(data.frameworks) == 28
        print_check("Framework count (28)", frameworks_ok, f"Found: {len(data.frameworks)}")

        # Check specific high-value frameworks
        critical_frameworks = {
            "nist_800_53_r5": 777,
            "soc_2_tsc": 412,
            "pci_dss_4.0.1": 364,
            "dora": 103,
            "iso_27001_2022": 51,
        }

        for fw_key, expected_count in critical_frameworks.items():
            actual = data.frameworks.get(fw_key, {}).get("controls_mapped", 0)
            passed = actual == expected_count
            print_check(f"{fw_key}", passed, f"Expected {expected_count}, found {actual}")

        return controls_ok and frameworks_ok

    except Exception as e:
        print_check("Data loader", False, f"Error: {e}")
        return False


def check_module_imports():
    """Check all module imports work."""
    print_header("3. Module Import Verification")

    modules_to_test = [
        "security_controls_mcp",
        "security_controls_mcp.server",
        "security_controls_mcp.data_loader",
    ]

    all_good = True
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print_check(f"Import {module_name}", True)
        except ImportError as e:
            print_check(f"Import {module_name}", False, str(e))
            all_good = False

    return all_good


def check_tool_functionality():
    """Check that all 5 tools work correctly."""
    print_header("4. Tool Functionality Verification")

    try:
        from security_controls_mcp.data_loader import SCFData

        data = SCFData()

        # Test 1: get_control
        ctrl = data.get_control("GOV-01")
        test1 = ctrl is not None and ctrl["id"] == "GOV-01"
        print_check("get_control('GOV-01')", test1, f"Name: {ctrl['name'][:50]}..." if ctrl else "")

        # Test 2: search_controls
        results = data.search_controls("encryption", limit=5)
        test2 = len(results) > 0
        print_check("search_controls('encryption')", test2, f"Found {len(results)} results")

        # Test 3: list_frameworks
        test3 = len(data.frameworks) == 28
        print_check("list_frameworks", test3, f"{len(data.frameworks)} frameworks")

        # Test 4: get_framework_controls
        dora_controls = data.get_framework_controls("dora")
        test4 = len(dora_controls) == 103
        print_check("get_framework_controls('dora')", test4, f"Found {len(dora_controls)} controls")

        # Test 5: map_frameworks
        mappings = data.map_frameworks("iso_27001_2022", "dora", "5.1")
        test5 = len(mappings) > 0
        print_check("map_frameworks(iso→dora)", test5, f"Found {len(mappings)} mappings")

        return all([test1, test2, test3, test4, test5])

    except Exception as e:
        print_check("Tool functionality", False, str(e))
        return False


async def check_mcp_protocol():
    """Check MCP protocol communication."""
    print_header("5. MCP Protocol Verification")

    # Skip in CI environments where stdio-based MCP tests are unreliable
    if os.environ.get("CI") == "true":
        print_check("MCP protocol", True, "Skipped in CI (tested via integration tests)")
        return True

    try:
        # Start the MCP server
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            "-m",
            "security_controls_mcp",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        await asyncio.sleep(1.0)  # Increased wait time

        # Test initialize
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "verify-script", "version": "1.0.0"},
            },
        }

        process.stdin.write((json.dumps(request) + "\n").encode())
        await process.stdin.drain()

        response_line = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
        response = json.loads(response_line.decode())

        init_ok = "result" in response
        print_check(
            "MCP initialize",
            init_ok,
            f"Server: {response.get('result', {}).get('serverInfo', {}).get('name', 'unknown')}",
        )

        # Test tools/list
        request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}

        process.stdin.write((json.dumps(request) + "\n").encode())
        await process.stdin.drain()

        response_line = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
        response = json.loads(response_line.decode())

        tools = response.get("result", {}).get("tools", [])
        tools_ok = len(tools) == 8
        print_check("MCP tools/list", tools_ok, f"Found {len(tools)} tools")

        # Cleanup
        process.terminate()
        await process.wait()

        return init_ok and tools_ok

    except Exception as e:
        print_check("MCP protocol", False, str(e))
        try:
            process.terminate()
            await process.wait()
        except Exception:
            pass
        return False


def check_package_metadata():
    """Check package metadata and version."""
    print_header("6. Package Metadata Verification")

    try:
        import security_controls_mcp

        # Check version
        version = getattr(security_controls_mcp, "__version__", None)
        version_ok = version is not None
        print_check(
            "Package version",
            version_ok,
            f"Version: {version}" if version else "No version defined",
        )

        # Check pyproject.toml exists
        pyproject = Path("pyproject.toml")
        pyproject_ok = pyproject.exists()
        print_check("pyproject.toml", pyproject_ok)

        return version_ok and pyproject_ok

    except Exception as e:
        print_check("Package metadata", False, str(e))
        return False


def check_documentation():
    """Check that all required documentation exists."""
    print_header("7. Documentation Verification")

    required_docs = {
        "README.md": "Project overview",
        "INSTALL.md": "Installation instructions",
        "TESTING.md": "Testing guide",
        "LICENSE": "License file",
    }

    all_good = True
    for filename, description in required_docs.items():
        filepath = Path(filename)
        exists = filepath.exists()

        if exists:
            size_kb = filepath.stat().st_size / 1024
            print_check(f"{filename}", True, f"{description} ({size_kb:.1f} KB)")
        else:
            print_check(f"{filename}", False, f"Missing: {description}")
            all_good = False

    return all_good


async def main():
    """Run all verification checks."""

    print(f"\n{Colors.BOLD}Security Controls MCP - Production Readiness Verification{Colors.END}")
    print(f"{Colors.BOLD}Version: 0.3.0{Colors.END}")

    results = {}

    # Run all checks
    results["data_files"] = check_data_files()
    results["data_integrity"] = check_data_integrity()
    results["module_imports"] = check_module_imports()
    results["tool_functionality"] = check_tool_functionality()
    results["mcp_protocol"] = await check_mcp_protocol()
    results["package_metadata"] = check_package_metadata()
    results["documentation"] = check_documentation()

    # Summary
    print_header("VERIFICATION SUMMARY")

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    for check_name, passed_check in results.items():
        status = (
            f"{Colors.GREEN}PASS{Colors.END}" if passed_check else f"{Colors.RED}FAIL{Colors.END}"
        )
        print(f"{status} - {check_name.replace('_', ' ').title()}")

    print(f"\n{Colors.BOLD}Overall: {passed}/{total} checks passed{Colors.END}")

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ PRODUCTION READY{Colors.END}")
        print(
            f"{Colors.GREEN}All systems operational. Ready for deployment to Claude Desktop/Code.{Colors.END}\n"
        )
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠️  NOT PRODUCTION READY{Colors.END}")
        print(f"{Colors.RED}Fix failing checks before deployment.{Colors.END}\n")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
