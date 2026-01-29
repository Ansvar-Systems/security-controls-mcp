# Claude Code Setup Guide

**Get security-controls-mcp working in Claude Code (this CLI).**

---

## ✅ Configuration Already Complete

The `.claude/.mcp.json` file is already configured in this project:

```json
{
  "security-controls": {
    "command": "/absolute/path/to/security-controls-mcp/venv/bin/python",
    "args": ["-m", "security_controls_mcp"]
  }
}
```

**Note:** Replace `/absolute/path/to/security-controls-mcp` with your actual project path.

---

## 🔄 Activate the MCP Server

### Option 1: Restart This Session

Type this in Claude Code:
```
/clear
```

This will start a fresh session that loads the MCP server.

### Option 2: Start New Session

```bash
# Exit current Claude Code session
exit

# Start a new session in this directory
cd /path/to/security-controls-mcp
claude
```

---

## 🧪 Test It's Working

After restarting, try these queries:

### 1. List Frameworks
```
List all available security frameworks
```

**Expected:** See 16 frameworks (NIST, ISO, DORA, PCI DSS, etc.)

### 2. Search Controls
```
Find all controls related to "encryption"
```

**Expected:** See CRY-05.3, CRY-07, etc.

### 3. Get Control Details
```
Show me details for control GOV-01
```

**Expected:** Full control information with framework mappings

### 4. Map Frameworks
```
Map ISO 27001 control 5.1 to DORA requirements
```

**Expected:** See SCF controls that bridge ISO→DORA

---

## 🔍 Verify MCP Server Loaded

Look for the MCP server in the startup messages when you start a new session. You should see something like:

```
Connected to MCP servers:
  - security-controls (5 tools)
```

Or check available tools:
```
What tools do you have available?
```

You should see:
- `mcp__security-controls__get_control`
- `mcp__security-controls__search_controls`
- `mcp__security-controls__list_frameworks`
- `mcp__security-controls__get_framework_controls`
- `mcp__security-controls__map_frameworks`

---

## 🐛 Troubleshooting

### MCP Server Not Loading

**Check 1: Verify .mcp.json exists**
```bash
cat .claude/.mcp.json
```

**Check 2: Verify Python path is correct**
```bash
# Replace with your actual project path
ls -la /absolute/path/to/security-controls-mcp/venv/bin/python
```

**Check 3: Test server manually**
```bash
source venv/bin/activate
python -m security_controls_mcp
# Should start and wait for JSON-RPC input
# Press Ctrl+C to exit
```

**Check 4: Verify package is installed**
```bash
source venv/bin/activate
python -c "import security_controls_mcp; print('✅ Installed')"
```

### MCP Server Crashes on Startup

Check Claude Code debug logs:
```bash
tail -50 ~/.claude/debug/$(ls -t ~/.claude/debug/ | head -1)
```

Look for errors related to "security-controls" MCP server.

### Tools Not Appearing

The MCP server might be loaded but Claude may not be calling it. Try being explicit:
```
Use the security-controls MCP server to list all frameworks
```

---

## 📝 Using Different Python Paths

If you clone this repo to a different location, update `.claude/.mcp.json`:

```json
{
  "security-controls": {
    "command": "/YOUR/NEW/PATH/venv/bin/python",
    "args": ["-m", "security_controls_mcp"]
  }
}
```

Or use a relative path (less reliable):
```json
{
  "security-controls": {
    "command": "python",
    "args": ["-m", "security_controls_mcp"],
    "env": {
      "VIRTUAL_ENV": "/absolute/path/to/venv"
    }
  }
}
```

---

## 🎯 Example Session

```
User: List all available security frameworks

Claude: [Uses security-controls MCP server]
**Available Frameworks (28 total)**

- **nist_800_53_r5**: NIST SP 800-53 Revision 5 (777 controls)
- **soc_2_tsc**: SOC 2 (TSC 2017:2022) (412 controls)
...

User: Find controls about "access control"

Claude: [Uses search_controls tool]
**Found 10 control(s) matching 'access control'**

**IAC-01: User Access Management**
...
```

---

## 🔗 Related Docs

- **QUICK_START.md** - Setup for Claude Desktop (GUI)
- **INSTALL.md** - Detailed installation guide
- **TESTING.md** - Test queries and examples
- **README.md** - Complete project overview and status

---

## 💡 Tips

1. **Be explicit in queries:** "Use the security-controls MCP server to..."
2. **Check tool names:** Tools are prefixed with `mcp__security-controls__`
3. **Restart when needed:** If MCP not responding, `/clear` to restart session
4. **Check logs:** Debug logs in `~/.claude/debug/` for troubleshooting

---

**MCP Server Status:** ✅ Configured and ready
**Next Step:** Type `/clear` to restart and test!
