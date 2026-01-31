# MCP Registry Status & Submission Plan

## Current Status

### ✅ Already Published Packages

**1. EU Regulations MCP**
- **npm:** `@ansvar/eu-regulations-mcp` ✅ Published
- **mcpName:** `io.github.Ansvar-Systems/eu-regulations-mcp` ✅ Configured
- **Keywords:** Includes "mcp" ✅
- **README:** Mentions MCP ✅
- **Auto-Discovery:** Should be discoverable by registry

**2. US Regulations MCP**
- **npm:** `@ansvar/us-regulations-mcp` ✅ Published
- **mcpName:** `us.ansvar/us-regulations-mcp` ✅ Configured
- **Keywords:** Includes "mcp" ✅
- **README:** Mentions MCP ✅
- **Auto-Discovery:** Should be discoverable by registry

**3. Security Controls MCP**
- **PyPI:** `security-controls-mcp` v0.2.1 ✅ Published
- **Keywords:** Includes "mcp" ✅
- **README:** Mentions MCP ✅
- **Auto-Discovery:** Should be discoverable by registry (Python packages don't support mcpName field)

---

## Registry Discovery

The MCP Registry at https://registry.modelcontextprotocol.io/ **auto-discovers** packages from npm and PyPI that meet these criteria:

1. ✅ Package contains "mcp" in keywords
2. ✅ README mentions Model Context Protocol
3. ✅ (Optional) Has mcpName field for namespacing

**All three packages meet these criteria!**

---

## What Happens Next

### Automatic Discovery (Current Approach)

The registry should automatically discover all three servers within 24-48 hours of publication. No manual submission needed.

**Check if they're live:**
1. Visit https://registry.modelcontextprotocol.io/
2. Search for "ansvar" or "eu-regulations" or "us-regulations" or "security-controls"
3. If not found after 48 hours, proceed to manual submission

### Manual Submission (If Needed)

If auto-discovery doesn't work after 48 hours:

**Option 1: Contact MCP Team**
- Open issue: https://github.com/modelcontextprotocol/registry/issues
- Provide package URLs and metadata
- Request manual indexing

**Option 2: GitHub MCP Registry (Community)**
- Some community registries track MCP servers
- Submit via PR to community lists

---

## Cross-Promotion Strategy

### 1. Link All Three Repos

**Update each README with a "Related Projects" section:**

```markdown
## Related Projects by Ansvar Systems

**Complete Compliance Suite:**

1. **[EU Regulations MCP](https://github.com/Ansvar-Systems/EU_compliance_MCP)** - Query 47 EU regulations (GDPR, AI Act, DORA, NIS2, etc.)
2. **[US Regulations MCP](https://github.com/Ansvar-Systems/US_Compliance_MCP)** - Query US federal and state compliance laws (HIPAA, CCPA, SOX, etc.)
3. **[Security Controls MCP](https://github.com/Ansvar-Systems/security-controls-mcp)** - Query 1,451 security controls across 28 frameworks (ISO 27001, NIST, DORA, etc.)

**How They Work Together:**
- EU/US MCPs tell you WHAT compliance requirements you must meet
- Security Controls MCP tells you HOW to implement controls that satisfy those requirements
```

### 2. Social Media Announcement

**Draft Announcement:**

```
🚀 Launched: Compliance Suite for Claude

Three MCP servers that work together for complete compliance coverage:

🇪🇺 EU Regulations MCP - 47 EU regulations (GDPR, AI Act, DORA, NIS2...)
📦 npm: @ansvar/eu-regulations-mcp

🇺🇸 US Regulations MCP - 15 US laws (HIPAA, CCPA, SOX, GLBA...)
📦 npm: @ansvar/us-regulations-mcp

🔐 Security Controls MCP - 1,451 controls across 28 frameworks
📦 pypi: security-controls-mcp

Ask Claude: "What DORA requirements apply?" → Get exact article → Map to ISO 27001 controls

All open source (Apache 2.0) | Built by @Ansvar-Systems

#MCP #Compliance #AI #GDPR #HIPAA #ISO27001
```

**Post to:**
- Reddit: r/cybersecurity, r/netsec, r/compliance
- Hacker News: "Show HN: Compliance Suite for Claude - Query EU regs, US laws, and security controls"
- LinkedIn: Tag #Compliance #Cybersecurity #AI #MCP
- X/Twitter: Tag @AnthropicAI, use #MCP hashtag

### 3. Documentation Cross-Links

Add to each project's README:

**Example workflow across all three:**
```
User: "What are DORA's ICT risk management requirements?"
→ EU Regulations MCP: Returns DORA Article 6 full text

User: "What security controls satisfy DORA Article 6?"
→ Security Controls MCP: Maps to ISO 27001, NIST CSF, and SCF controls

User: "Show me ISO 27001 A.8.1 requirements"
→ Security Controls MCP: Returns control details and framework mappings
```

---

## Action Items

### Immediate (Next 24 Hours)

- [ ] **Wait for auto-discovery** - Check registry.modelcontextprotocol.io in 24-48 hours
- [ ] **Cross-link READMEs** - Add "Related Projects" section to all three repos
- [ ] **Prepare social announcement** - Draft posts for Reddit, HN, LinkedIn, Twitter

### Follow-Up (48 Hours)

- [ ] **Verify registry listing** - Confirm all three appear on https://registry.modelcontextprotocol.io/
- [ ] **If not listed:** Submit manual request to registry team
- [ ] **Post announcements** - Share on social media channels

### Long-Term

- [ ] **Monitor GitHub stars/usage** - Track community adoption
- [ ] **Respond to issues** - Engage with users and add requested features
- [ ] **Consider Docker registry** - Submit to Docker MCP Registry for container-based deployment

---

## Success Metrics

**Week 1:**
- All three servers appear on MCP Registry
- 50+ GitHub stars combined
- 10+ social media mentions

**Month 1:**
- 500+ PyPI downloads for security-controls-mcp
- 1,000+ npm downloads for EU/US regulation servers
- Featured in at least one compliance/security blog

---

## Contact & Support

- **Website:** https://ansvar.eu
- **GitHub:** https://github.com/Ansvar-Systems
- **Issues:** Open on respective repos

---

**Last Updated:** 2026-01-29
**Status:** ✅ All packages published, awaiting registry auto-discovery
