# Security Tools Documentation

This repository implements a defense-in-depth security strategy using 9 free security tools across three layers of protection.

## Security Tools Overview

| Tool | Purpose | Frequency | Cost |
|------|---------|-----------|------|
| **Gitleaks** | Secret scanning | Every commit + PR | Free |
| **Dependabot** | Dependency updates | Weekly (Mon 6 AM) | Free |
| **Trivy** | Vulnerability scanner | Daily (3 AM) | Free |
| **Semgrep** | SAST (code analysis) | Every push | Free |
| **OSSF Scorecard** | Best practices | Weekly (Mon 2 AM) | Free |
| **pytest** | Unit/integration tests | Every test run | Free |
| **CodeQL** | Advanced SAST | Every push | Free (existing) |
| **Socket Security** | Supply chain | Every PR | Free (existing) |

## Defense-in-Depth Security Stack

### Layer 1: Pre-Commit
- ✅ **Gitleaks** (secrets) - Prevents secrets from entering the repository
- ✅ **Tests** - Ensures code quality and functionality

### Layer 2: Push/PR (Immediate)
- ✅ **Gitleaks** (secrets scan) - Scans full repository history
- ✅ **Semgrep** (SAST) - Static application security testing
- ✅ **Trivy** (vulnerabilities) - Scans dependencies and code
- ✅ **Socket Security** (supply chain) - Monitors npm packages
- ✅ **CodeQL** (advanced SAST) - Deep semantic analysis

### Layer 3: Scheduled (Background)
- ✅ **Dependabot** (weekly) - Automated dependency updates
- ✅ **OSSF Scorecard** (weekly) - Security best practices assessment
- ✅ **Trivy** (daily) - Continuous vulnerability monitoring

## Tool Details

### 1. Gitleaks - Secret Detection

**Purpose:** Prevents secrets (API keys, tokens, passwords) from being committed to the repository.

**Configuration:** `.github/workflows/gitleaks.yml`

**Runs:**
- On every push to main
- On every pull request
- Manual trigger via workflow_dispatch

**What it scans:**
- Full git history
- All branches
- Common secret patterns (AWS keys, GitHub tokens, private keys, etc.)

**Results:** Uploaded to GitHub Security tab and as artifacts for review.

---

### 2. Dependabot - Dependency Updates

**Purpose:** Automatically creates pull requests to update dependencies with known vulnerabilities.

**Configuration:** `.github/dependabot.yml`

**Runs:** Weekly on Mondays at 6:00 AM UTC

**Updates:**
- Python dependencies (pip)
- GitHub Actions workflows

**Settings:**
- Max 10 open PRs for pip dependencies
- Max 5 open PRs for GitHub Actions
- Auto-labeled with "dependencies" and "security"

---

### 3. Trivy - Vulnerability Scanner

**Purpose:** Comprehensive vulnerability scanning for dependencies, containers, and code.

**Configuration:** `.github/workflows/trivy.yml`

**Runs:**
- On every push to main
- On every pull request
- Daily at 3:00 AM UTC (scheduled)
- Manual trigger via workflow_dispatch

**Scans:**
- Filesystem dependencies
- Python packages
- Known CVEs (CRITICAL, HIGH, MEDIUM severity)

**Output:**
- SARIF format uploaded to GitHub Security tab
- Table format for PR comments

**Exit behavior:** Blocking on CRITICAL/HIGH/MEDIUM vulnerabilities (fails builds to enforce security standards)

---

### 4. Semgrep - SAST Analysis

**Purpose:** Static Application Security Testing using semantic code analysis.

**Configuration:** `.github/workflows/semgrep.yml`

**Runs:**
- On every push to main
- On every pull request
- Manual trigger via workflow_dispatch

**Rulesets:**
- `p/security-audit` - General security patterns
- `p/secrets` - Secret detection
- `p/owasp-top-ten` - OWASP Top 10 vulnerabilities
- `p/python` - Python-specific security issues

**Output:** SARIF format uploaded to GitHub Security tab

**Features:**
- Semantic code analysis (understands code meaning, not just patterns)
- Low false positive rate
- Custom rule support

---

### 5. OSSF Scorecard - Security Best Practices

**Purpose:** Evaluates repository security posture against OpenSSF best practices.

**Configuration:** `.github/workflows/ossf-scorecard.yml`

**Runs:**
- Weekly on Mondays at 2:00 AM UTC
- On branch protection rule changes
- On pushes to main
- Manual trigger via workflow_dispatch

**Checks:**
- Code review practices
- Branch protection
- Dependency update automation
- Vulnerability disclosure
- Security policy presence
- Token permissions
- And 10+ additional security checks

**Scoring:** 0-10 scale for each check, with detailed recommendations

**Output:**
- SARIF format uploaded to GitHub Security tab
- Artifacts retained for 5 days

---

### 6. CodeQL (Existing)

**Purpose:** GitHub's advanced semantic code analysis engine.

**Configuration:** GitHub's default CodeQL setup (if already configured)

**Runs:**
- On every push
- On pull requests

**Languages:** Python (auto-detected)

**Queries:**
- Security queries
- Code quality queries
- Extended query packs

---

### 7. Socket Security (Existing)

**Purpose:** Supply chain security for npm dependencies.

**Configuration:** GitHub App integration (if already configured)

**Runs:** On every pull request

**Monitors:**
- New dependencies
- Dependency updates
- Supply chain attacks
- Malicious packages
- License compliance

---

### 8. pytest - Testing Framework

**Purpose:** Unit and integration testing with coverage reporting.

**Configuration:** `pyproject.toml` and test files in `tests/`

**Runs:**
- Every test execution
- CI/CD pipeline
- Pre-commit hooks (optional)

**Coverage:**
- Tracks code coverage
- Identifies untested code paths
- Enforces minimum coverage thresholds

---

## Security Workflow Integration

### For Developers

**Before committing:**
1. Run tests locally: `pytest tests/ -v`
2. Ensure no secrets in code
3. Review security warnings in IDE

**On pull request:**
- Wait for all security checks to pass
- Review Trivy vulnerability reports
- Address Semgrep findings
- Check CodeQL analysis results
- Verify Socket Security approval

**Merge requirements:**
- All CI checks must pass
- Security findings addressed or documented
- Code review approved

### For Security Team

**Weekly reviews:**
- Check OSSF Scorecard results
- Review Dependabot PRs
- Audit Trivy daily scans

**Incident response:**
- Gitleaks findings = immediate action required
- Critical/High Trivy CVEs = patch within 7 days
- Semgrep security issues = assess and remediate

---

## Security Findings Workflow

### Critical Severity (Immediate Action)
1. **Secrets detected (Gitleaks)**
   - Rotate compromised credentials immediately
   - Review git history
   - Update secret management practices

2. **Critical CVEs (Trivy)**
   - Assess exploitability
   - Apply patches or mitigations within 24 hours
   - Document in security log

### High Severity (7-Day SLA)
1. **High-severity vulnerabilities**
   - Review impact assessment
   - Apply patches within 7 days
   - Test thoroughly before deployment

2. **SAST findings (Semgrep/CodeQL)**
   - Validate finding
   - Fix or document false positive
   - Update rules if needed

### Medium/Low Severity (30-Day SLA)
- Review during sprint planning
- Batch similar fixes
- Consider technical debt tradeoffs

---

## Tool Comparison Matrix

| Feature | Gitleaks | Trivy | Semgrep | CodeQL | OSSF |
|---------|----------|-------|---------|--------|------|
| Secret Detection | ✅ Primary | ❌ | ✅ Secondary | ❌ | ❌ |
| CVE Detection | ❌ | ✅ Primary | ❌ | ✅ Secondary | ❌ |
| Code Analysis | ❌ | ❌ | ✅ Primary | ✅ Primary | ❌ |
| Best Practices | ❌ | ❌ | ❌ | ❌ | ✅ Primary |
| Speed | Fast | Fast | Medium | Slow | Fast |
| False Positives | Low | Low | Low | Very Low | N/A |

---

## Configuration Files

### Created Files
1. `.github/dependabot.yml` - Automated dependency updates
2. `.github/workflows/trivy.yml` - Vulnerability scanning
3. `.github/workflows/semgrep.yml` - SAST scanning
4. `.github/workflows/ossf-scorecard.yml` - Best practices assessment
5. `.github/workflows/gitleaks.yml` - Secret detection
6. `SECURITY-TOOLS.md` - This documentation

### Existing Files (Modified or Referenced)
- `.github/workflows/` - May include existing CodeQL/Socket workflows
- `pyproject.toml` - Test configuration
- `.gitignore` - Excludes security artifacts

---

## Monitoring & Alerts

### GitHub Security Tab
All SARIF results are automatically uploaded to:
- Repository → Security → Code scanning alerts

**Alert categories:**
- `gitleaks` - Secret detection
- `trivy` - Vulnerability scanning
- `semgrep` - SAST findings
- `codeql` - Advanced SAST
- `ossf-scorecard` - Best practices

### Notifications
Configure in repository settings:
- Security → Dependabot alerts
- Security → Code scanning alerts
- Actions → Workflow failures

---

## Troubleshooting

### Gitleaks Finding False Positives
```bash
# Add to .gitleaks.toml
[allowlist]
paths = [
  "tests/fixtures/sample_secrets.py"  # Test data
]
```

### Trivy Reporting Known Issues
```yaml
# Add to .trivyignore
CVE-2023-12345  # False positive - not exploitable in our use case
```

### Semgrep Custom Rules
```yaml
# Add to .semgrep.yml for custom rules
rules:
  - id: custom-security-check
    pattern: dangerous_function(...)
    message: "Avoid using dangerous_function"
    severity: WARNING
```

### OSSF Scorecard Low Score
- Review recommendations in Security tab
- Enable branch protection
- Add SECURITY.md
- Enable vulnerability disclosure
- Configure automated updates

---

## Cost Analysis

**Total monthly cost:** $0

All tools used are free for public repositories and offer free tiers for private repositories:

- **Gitleaks:** Free forever
- **Trivy:** Free forever
- **Semgrep:** Free tier (up to 10 contributors for private repos)
- **Dependabot:** Free on GitHub
- **OSSF Scorecard:** Free forever
- **CodeQL:** Free for public repos
- **Socket Security:** Free tier available

**GitHub Actions minutes:**
- Free tier: 2,000 minutes/month (public repos: unlimited)
- Estimated usage: ~400 minutes/month
- Well within free tier limits

---

## Further Reading

- [Gitleaks Documentation](https://github.com/gitleaks/gitleaks)
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [Semgrep Documentation](https://semgrep.dev/docs/)
- [OSSF Scorecard Documentation](https://github.com/ossf/scorecard)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

---

## Maintenance

### Monthly Tasks
- Review OSSF Scorecard trends
- Merge Dependabot PRs
- Update security tool versions

### Quarterly Tasks
- Audit security findings backlog
- Review and update security policies
- Assess tool effectiveness

### Annual Tasks
- Security tools evaluation
- Threat model review
- Security training updates

---

**Last Updated:** 2026-01-29
**Maintained By:** Ansvar Systems Security Team
**Questions?** Open an issue or contact security@ansvar.eu
