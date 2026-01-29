# Installation Guide

## Prerequisites

- Python 3.10 or higher
- pip or pipx

---

## Quick Install (Recommended)

### Option 1: Using pipx (Isolated, Recommended)

```bash
# Install pipx if you don't have it
pip install pipx

# Install security-controls-mcp
pipx install security-controls-mcp

# With PDF import support for purchased standards
pipx install security-controls-mcp[import-tools]
```

### Option 2: Using pip

```bash
# Basic installation
pip install security-controls-mcp

# With PDF import support for purchased standards
pip install security-controls-mcp[import-tools]
```

### Option 3: From Source (For Development)

```bash
# Clone repository
git clone https://github.com/Ansvar-Systems/security-controls-mcp.git
cd security-controls-mcp

# Install in editable mode
pip install -e .

# Or with import tools
pip install -e '.[import-tools]'
```

**Import Tools** add support for importing purchased standards (ISO 27001, NIST SP 800-53, etc.). See [PAID_STANDARDS_GUIDE.md](PAID_STANDARDS_GUIDE.md) for details.

---

## Verify Installation

```bash
python test_server.py
```

You should see:
```
✓ Loaded 1451 controls
✓ Loaded 28 frameworks
✓ All tests passed!
```

---

## Configure for Claude

### Claude Desktop (Recommended for GUI)

1. **Locate your config file:**
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

2. **Create or edit the file:**

```json
{
  "mcpServers": {
    "security-controls": {
      "command": "/absolute/path/to/security-controls-mcp/venv/bin/python",
      "args": ["-m", "security_controls_mcp"]
    }
  }
}
```

**⚠️ Important:** Use the ABSOLUTE path to your venv Python:

```bash
# Get the absolute path:
cd /path/to/security-controls-mcp
source venv/bin/activate
which python
# Copy this path to the config
```

3. **Restart Claude Desktop**

4. **Verify it's loaded:**
   - Start a new conversation
   - Type: "List available frameworks"
   - You should see 16 security frameworks

---

### Claude Code (CLI)

Claude Code doesn't currently support adding custom MCP servers via config. Instead:

1. **Test locally:**
   ```bash
   source venv/bin/activate
   python test_mcp_integration.py
   ```

2. **Or start a new Claude Code session after installation** (servers may auto-discover)

---

## Troubleshooting

### "Module not found" error

Make sure you're using the venv Python:
```bash
source venv/bin/activate
which python  # Should show venv/bin/python
```

### "No such file or directory: python"

Use the full absolute path in your Claude config:
```json
{
  "command": "/Users/yourname/Projects/security-controls-mcp/venv/bin/python"
}
```

### Claude Desktop doesn't show the MCP server

1. Check the config file location (macOS vs Windows)
2. Restart Claude Desktop completely (quit and reopen)
3. Check for JSON syntax errors in config file
4. Look at Claude Desktop logs (if available)

### Data files missing

The data files should be in `src/security_controls_mcp/data/`. If missing:
```bash
# Re-run extraction
cd /tmp
source scf-venv/bin/activate
python3 /path/to/scf-extract-starter.py /tmp/scf-repo/secure-controls-framework-scf-2025-4.xlsx

# Copy to project
cp scf-controls.json framework-to-scf.json /path/to/security-controls-mcp/src/security_controls_mcp/data/
```

---

## Next Steps

See [TESTING.md](TESTING.md) for test queries and validation steps.
