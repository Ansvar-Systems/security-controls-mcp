# Quick Start Guide

**Get security-controls-mcp running in Claude Desktop in 2 minutes.**

## 📦 Step 1: Install

**Option 1: Using pipx (Recommended)**
```bash
pipx install security-controls-mcp
```

**Option 2: Using pip**
```bash
pip install security-controls-mcp
```

**Requirements:** Python 3.10+ and pip/pipx

---

## 🚀 Step 2: Configure Claude Desktop

**macOS:**
```bash
open ~/Library/Application\ Support/Claude/
```

**Windows:**
```cmd
explorer %APPDATA%\Claude\
```

### Step 3: Edit `claude_desktop_config.json`

If the file doesn't exist, create it. Add this configuration:

```json
{
  "mcpServers": {
    "security-controls": {
      "command": "scf-mcp"
    }
  }
}
```

**That's it!** The `scf-mcp` command is available globally after pip/pipx installation.

---

## 🔄 Step 3: Restart Claude Desktop

1. Quit Claude Desktop completely (Cmd+Q on Mac, right-click taskbar icon on Windows)
2. Reopen Claude Desktop

### Step 5: Verify It Works

Start a new conversation and try:

```
List all available security frameworks
```

You should see output like:
```
**Available Frameworks (28 total)**

- **nist_800_53_r5**: NIST SP 800-53 Revision 5 (777 controls)
- **soc_2_tsc**: SOC 2 (TSC 2017:2022) (412 controls)
- **pci_dss_4.0.1**: PCI DSS v4.0.1 (364 controls)
...
```

---

## 🧪 Test Queries

Try these queries to explore what the MCP server can do:

### 1. Explore Frameworks
```
What security frameworks are available?
```

### 2. Search for Controls
```
Find all controls related to "encryption"
```

### 3. Get Control Details
```
Show me details for control GOV-01
```

### 4. Framework Mapping
```
Map ISO 27001 control 5.1 to DORA requirements
```

### 5. Get All Controls for a Framework
```
Show me all controls that map to DORA
```

---

## 🔧 Troubleshooting

### Server Not Loading

**Check 1: Config file location**
```bash
# macOS
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Windows
type %APPDATA%\Claude\claude_desktop_config.json
```

**Check 2: Python path is absolute**
```json
✅ GOOD: "/Users/jeff/Projects/security-controls-mcp/venv/bin/python"
❌ BAD:  "venv/bin/python"
❌ BAD:  "python"
```

**Check 3: JSON syntax is valid**
Use https://jsonlint.com to validate your config file.

**Check 4: Restart Claude Desktop**
Make sure you fully quit (Cmd+Q / Exit), not just close the window.

### "Module not found" Error

Your virtual environment might not be activated. Reinstall:
```bash
cd /path/to/security-controls-mcp
python3 -m venv venv
source venv/bin/activate
pip install -e .
which python  # Copy this exact path to config
```

### Still Not Working?

Run the diagnostic:
```bash
source venv/bin/activate
python test_mcp_client.py
```

If this shows `✅ All MCP protocol tests passed!`, the server works. The issue is with Claude Desktop config.

---

## 📚 What's Next?

Once it's working, see [TESTING.md](TESTING.md) for:
- Example queries
- Use cases
- Advanced features

---

## 🆘 Need Help?

1. Check [INSTALL.md](INSTALL.md) for detailed installation instructions
2. Check [README.md](README.md) for technical architecture and features
3. Report issues: https://github.com/Ansvar-Systems/security-controls-mcp/issues
