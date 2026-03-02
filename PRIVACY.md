# Privacy Policy

## Data Collection

**This MCP server collects no data.**

- No user data is stored
- No telemetry is sent
- No tracking or analytics
- No cookies or session data
- No network calls at runtime

## Architecture

This MCP server is a **read-only knowledge base**. It serves pre-built data from a local SQLite database. No user queries, inputs, or interactions are logged or persisted by the MCP server itself.

## Data Sources

All data in this knowledge base is sourced from **publicly available** Security Controls government and legislative publications.

## Host Environment

When this MCP server runs inside a host application (Claude Desktop, Cursor, VS Code, etc.), the **host application's** privacy policy governs how your interactions are processed. This MCP server itself has no visibility into or control over the host's data practices.

## npm Package

The published npm package contains only:
- Static SQLite database (legislation text)
- Server code (TypeScript/JavaScript)
- Configuration files

No user data is included in or collected by the package.

## Contact

For privacy questions about this MCP server: [Ansvar Systems](https://ansvar.eu)
