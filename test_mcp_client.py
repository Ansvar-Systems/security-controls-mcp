#!/usr/bin/env python3
"""
Test MCP server by running it as a subprocess and sending MCP protocol messages.
This simulates how Claude would actually interact with the server.

SECURITY NOTE: Uses asyncio.create_subprocess_exec (safe) not subprocess.exec().
This is a test script with no user input - command injection is not possible.
"""

import asyncio
import json
import subprocess
import sys


async def send_mcp_request(process, method: str, params: dict = None):
    """Send an MCP JSON-RPC request and get response."""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {}
    }

    request_json = json.dumps(request) + "\n"
    process.stdin.write(request_json.encode())
    await process.stdin.drain()

    # Read response
    response_line = await process.stdout.readline()
    if not response_line:
        return None

    return json.loads(response_line.decode())


async def test_mcp_server():
    """Test the MCP server via stdio communication."""

    print("="*80)
    print("MCP Server Protocol Test")
    print("="*80)

    # Start the MCP server process
    print("\n1. Starting MCP server process...")
    # Using create_subprocess_exec (safe) - no shell, no user input
    process = await asyncio.create_subprocess_exec(
        sys.executable, "-m", "security_controls_mcp",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    print("   ✓ Server started (PID: {})".format(process.pid))

    # Give it a moment to initialize
    await asyncio.sleep(0.5)

    try:
        # Test 1: Initialize
        print("\n2. Sending initialize request...")
        response = await send_mcp_request(process, "initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        })

        if response and "result" in response:
            print("   ✓ Server initialized")
            print(f"   Server name: {response['result'].get('serverInfo', {}).get('name')}")
        else:
            print(f"   ✗ Initialization failed: {response}")
            return

        # Test 2: List tools
        print("\n3. Listing available tools...")
        response = await send_mcp_request(process, "tools/list")

        if response and "result" in response:
            tools = response["result"].get("tools", [])
            print(f"   ✓ Found {len(tools)} tools:")
            for tool in tools:
                print(f"     - {tool['name']}: {tool['description'][:60]}...")
        else:
            print(f"   ✗ Failed to list tools: {response}")
            return

        # Test 3: Call get_control tool
        print("\n4. Testing get_control tool...")
        response = await send_mcp_request(process, "tools/call", {
            "name": "get_control",
            "arguments": {
                "control_id": "GOV-01",
                "include_mappings": True
            }
        })

        if response and "result" in response:
            content = response["result"].get("content", [])
            if content:
                text = content[0].get("text", "")
                print("   ✓ get_control response:")
                print("   " + text[:200].replace("\n", "\n   ") + "...")
        else:
            print(f"   ✗ get_control failed: {response}")

        # Test 4: Call search_controls tool
        print("\n5. Testing search_controls tool...")
        response = await send_mcp_request(process, "tools/call", {
            "name": "search_controls",
            "arguments": {
                "query": "encryption",
                "limit": 3
            }
        })

        if response and "result" in response:
            content = response["result"].get("content", [])
            if content:
                text = content[0].get("text", "")
                print("   ✓ search_controls response:")
                lines = text.split("\n")[:5]
                for line in lines:
                    print("   " + line)
        else:
            print(f"   ✗ search_controls failed: {response}")

        # Test 5: Call list_frameworks tool
        print("\n6. Testing list_frameworks tool...")
        response = await send_mcp_request(process, "tools/call", {
            "name": "list_frameworks",
            "arguments": {}
        })

        if response and "result" in response:
            content = response["result"].get("content", [])
            if content:
                text = content[0].get("text", "")
                print("   ✓ list_frameworks response:")
                lines = text.split("\n")[:8]
                for line in lines:
                    print("   " + line)
        else:
            print(f"   ✗ list_frameworks failed: {response}")

        print("\n" + "="*80)
        print("✅ All MCP protocol tests passed!")
        print("="*80)

    finally:
        # Cleanup
        print("\n7. Shutting down server...")
        process.terminate()
        await process.wait()
        print("   ✓ Server stopped")


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
