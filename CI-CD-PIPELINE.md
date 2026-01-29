# CI/CD Pipeline Documentation

Complete continuous integration and deployment pipeline with 11 automated workflows.

## Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      CI/CD Pipeline Flow                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Code Push                                                      │
│       ↓                                                         │
│  ┌────────────────────────────────────────────┐               │
│  │  Layer 1: Code Quality & Testing           │               │
│  ├────────────────────────────────────────────┤               │
│  │  • Tests (3 OS × 3 Python versions)        │               │
│  │  • Linting (ruff + black)                  │               │
│  │  • Pre-commit hooks                        │               │
│  │  • Code coverage (with reports)            │               │
│  └────────────────────────────────────────────┘               │
│       ↓                                                         │
│  ┌────────────────────────────────────────────┐               │
│  │  Layer 2: Security Scanning                │               │
│  ├────────────────────────────────────────────┤               │
│  │  • Gitleaks (secrets)                      │               │
│  │  • Semgrep (SAST)                          │               │
│  │  • Trivy (vulnerabilities)                 │               │
│  │  • CodeQL (semantic analysis)              │               │
│  │  • Socket Security (supply chain)          │               │
│  └────────────────────────────────────────────┘               │
│       ↓                                                         │
│  ┌────────────────────────────────────────────┐               │
│  │  Layer 3: Build & Package                  │               │
│  ├────────────────────────────────────────────┤               │
│  │  • Python package build                    │               │
│  │  • Manifest check                          │               │
│  │  • Installation validation (3 OS)          │               │
│  │  • Docker image build                      │               │
│  │  • Multi-arch support (amd64, arm64)       │               │
│  └────────────────────────────────────────────┘               │
│       ↓                                                         │
│  ┌────────────────────────────────────────────┐               │
│  │  Layer 4: Deployment                       │               │
│  ├────────────────────────────────────────────┤               │
│  │  • PyPI publishing (on release)            │               │
│  │  • Docker image push (GHCR)                │               │
│  │  • GitHub release automation               │               │
│  │  • Changelog generation                    │               │
│  └────────────────────────────────────────────┘               │
│       ↓                                                         │
│  ┌────────────────────────────────────────────┐               │
│  │  Layer 5: Scheduled Maintenance            │               │
│  ├────────────────────────────────────────────┤               │
│  │  • Dependabot (weekly Mon 6 AM)            │               │
│  │  • OSSF Scorecard (weekly Mon 2 AM)        │               │
│  │  • Trivy scan (daily 3 AM)                 │               │
│  └────────────────────────────────────────────┘               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Workflow Summary

| Workflow | Trigger | Duration | Purpose |
|----------|---------|----------|---------|
| **Tests** | Push, PR | ~5 min | Cross-platform testing (3 OS × 3 Python) |
| **Pre-commit** | Push, PR | ~1 min | Pre-commit hook validation |
| **Coverage** | Push, PR | ~3 min | Code coverage reporting |
| **Gitleaks** | Push, PR | ~30 sec | Secret detection |
| **Semgrep** | Push, PR | ~2 min | SAST analysis |
| **Trivy** | Push, PR, Daily | ~1 min | Vulnerability scanning |
| **OSSF Scorecard** | Weekly | ~1 min | Security best practices |
| **Build** | Push, PR, Release | ~3 min | Package build & validation |
| **Docker** | Push, PR, Release | ~5 min | Container image build |
| **Publish** | Release | ~2 min | PyPI publishing |
| **Release** | Tag push | ~1 min | GitHub release automation |

**Total time per push:** ~15 minutes (parallel execution)
**Monthly GitHub Actions usage:** ~800 minutes (well within free tier)

---

## Detailed Workflow Documentation

### 1. Tests Workflow (`tests.yml`)

**Purpose:** Comprehensive cross-platform testing and linting

**Triggers:**
- Every push to main
- Every pull request
- Manual dispatch

**Matrix Testing:**
- **Operating Systems:** Ubuntu, macOS, Windows
- **Python Versions:** 3.10, 3.11, 3.12
- **Total Combinations:** 9 test runs

**Test Stages:**
1. Unit tests (`pytest tests/ -v`)
2. Smoke tests (`verify_production_ready.py`)
3. Server startup test (`test_server.py`)
4. Linting (ruff + black)

**Artifacts:** None (test results in logs)

**Failure Handling:** Blocks merge if any test fails

---

### 2. Pre-commit Workflow (`pre-commit.yml`)

**Purpose:** Validate pre-commit hooks in CI

**Triggers:**
- Every push to main
- Every pull request
- Manual dispatch

**Checks:**
- Pre-commit hook execution on all files
- Hook configuration validation
- Diff display on failure

**Cache:** Pre-commit hooks cached for faster runs

**Features:**
- Shows diffs when checks fail
- Uses same hooks as local development
- Ensures consistency across environments

---

### 3. Code Coverage Workflow (`coverage.yml`)

**Purpose:** Track and report code coverage

**Triggers:**
- Every push to main
- Every pull request
- Manual dispatch

**Coverage Tools:**
- pytest-cov for collection
- Codecov for tracking
- HTML reports for detailed analysis

**Reports Generated:**
- XML (for Codecov)
- HTML (artifact download)
- Terminal (in logs)
- PR comments (when applicable)

**Thresholds:**
- 🟢 Green: ≥90%
- 🟡 Yellow: 75-89%
- 🟠 Orange: 60-74%
- 🔴 Red: <60%

**Artifacts:** HTML coverage report (30-day retention)

---

### 4. Build Workflow (`build.yml`)

**Purpose:** Build and validate Python package

**Triggers:**
- Every push to main
- Every pull request
- Release creation
- Manual dispatch

**Build Process:**
1. Install build tools (build, twine, check-manifest)
2. Validate manifest completeness
3. Build source distribution and wheel
4. Check package metadata with twine
5. Test installation from wheel

**Validation Matrix:**
- **Operating Systems:** Ubuntu, macOS, Windows
- **Python Versions:** 3.10, 3.11, 3.12
- **Total Validations:** 9 installation tests

**Tests:**
- Import validation
- Server startup test (5-second timeout)
- Platform-specific startup commands

**Artifacts:** Python package (dist/) - 7-day retention

---

### 5. Docker Workflow (`docker.yml`)

**Purpose:** Build and publish container images

**Triggers:**
- Push to main
- Version tags (v*)
- Pull requests (build only)
- Release publication
- Manual dispatch

**Build Features:**
- Multi-architecture builds (amd64, arm64)
- Layer caching for faster builds
- Metadata extraction for tagging
- Vulnerability scanning with Trivy

**Registries:**
- GitHub Container Registry (ghcr.io)

**Tags Generated:**
- `latest` (main branch)
- `v1.2.3` (semver)
- `v1.2` (major.minor)
- `v1` (major)
- `main-abc123` (branch-sha)
- `pr-123` (pull request)

**Security:**
- Trivy scan on built images
- Results uploaded to Security tab
- SARIF format for integration

**Artifacts:** Docker images in GHCR

---

### 6. Publish Workflow (`publish.yml`)

**Purpose:** Publish Python package to PyPI

**Triggers:**
- Release publication (PyPI)
- Manual dispatch (Test PyPI option)

**Publishing Process:**
1. Build package
2. Validate with twine check
3. Publish to PyPI or Test PyPI
4. Update release notes

**Authentication:**
- Uses trusted publishing (OIDC)
- No API tokens required
- Environment protection

**Environments:**
- `pypi` - Production PyPI
- `testpypi` - Test PyPI

**Safety:**
- Draft release support
- Pre-release detection
- Skip existing packages

---

### 7. Release Workflow (`release.yml`)

**Purpose:** Automate GitHub release creation

**Triggers:**
- Version tag push (v*)
- Manual dispatch

**Release Process:**
1. Checkout full history
2. Generate changelog from commits
3. Create GitHub release
4. Update release notes
5. Trigger downstream workflows

**Changelog:**
- Automatic from git log
- Commit messages formatted
- Full changelog link

**Release Types:**
- Standard (stable)
- Pre-release (alpha, beta, rc)
- Draft (manual approval)

**Notifications:**
- GitHub release created
- PyPI publish triggered
- Docker build triggered

---

### 8. Gitleaks Workflow (`gitleaks.yml`)

**Purpose:** Prevent secrets from entering repository

**Triggers:**
- Every push to main
- Every pull request
- Manual dispatch

**Scanning:**
- Full repository history
- All branches
- Common secret patterns

**Secret Types Detected:**
- AWS keys
- API tokens
- Private keys
- Database credentials
- OAuth tokens
- Generic secrets

**Configuration:** `.gitleaks.toml` for custom rules

**Artifacts:** Report on failure (30-day retention)

---

### 9. Semgrep Workflow (`semgrep.yml`)

**Purpose:** Static application security testing

**Triggers:**
- Every push to main
- Every pull request
- Manual dispatch

**Rulesets:**
- `p/security-audit` - Security patterns
- `p/secrets` - Secret detection
- `p/owasp-top-ten` - OWASP vulnerabilities
- `p/python` - Python-specific issues

**Analysis:**
- Semantic code understanding
- Low false positive rate
- SARIF output to Security tab

**Container:** Uses official Semgrep container

---

### 10. Trivy Workflow (`trivy.yml`)

**Purpose:** Comprehensive vulnerability scanning

**Triggers:**
- Every push to main
- Every pull request
- Daily at 3 AM UTC
- Manual dispatch

**Scanning:**
- Filesystem dependencies
- Python packages
- Known CVEs

**Severity Levels:**
- CRITICAL
- HIGH
- MEDIUM

**Outputs:**
- SARIF to Security tab
- Table format for PRs
- Blocking on CRITICAL/HIGH/MEDIUM vulnerabilities

**Scheduled:**
- Daily 3 AM scan for continuous monitoring

---

### 11. OSSF Scorecard Workflow (`ossf-scorecard.yml`)

**Purpose:** Security best practices assessment

**Triggers:**
- Weekly on Mondays at 2 AM UTC
- Branch protection changes
- Push to main
- Manual dispatch

**Checks (18 total):**
- Binary artifacts
- Branch protection
- CI tests
- CII best practices
- Code review
- Contributors
- Dangerous workflow
- Dependency update tool
- Fuzzing
- License
- Maintained
- Packaging
- Pinned dependencies
- SAST
- Security policy
- Signed releases
- Token permissions
- Vulnerabilities

**Scoring:** 0-10 for each check

**Artifacts:** Results (5-day retention)

---

## Environment Variables & Secrets

### Required Secrets

| Secret | Purpose | Workflow |
|--------|---------|----------|
| `GITHUB_TOKEN` | Automatic, provided by GitHub | All |
| `CODECOV_TOKEN` | Optional, for Codecov uploads | Coverage |
| `GITLEAKS_LICENSE` | Optional, for Gitleaks Pro | Gitleaks |

### Optional Secrets

| Secret | Purpose | Workflow |
|--------|---------|----------|
| `PYPI_API_TOKEN` | PyPI publishing (if not using OIDC) | Publish |
| `TEST_PYPI_API_TOKEN` | Test PyPI publishing | Publish |

### Environment Setup

**PyPI Trusted Publishing (Recommended):**
1. Go to PyPI project settings
2. Add GitHub Actions publisher
3. Configure repository details
4. No API tokens needed!

---

## Workflow Dependencies

```
Release Tag Push
    ↓
    ├─→ Release (creates GitHub release)
    │       ↓
    │       ├─→ Publish (publishes to PyPI)
    │       └─→ Docker (builds & pushes image)
    │
    └─→ Build (validates package)
            ↓
            └─→ Tests (runs on all platforms)
```

---

## CI/CD Best Practices

### 1. Fast Feedback
- Parallel workflow execution
- Cached dependencies
- Matrix testing for coverage

### 2. Security First
- Multi-layer security scanning
- Secrets detection in every PR
- Vulnerability monitoring

### 3. Quality Gates
- Tests must pass before merge
- Linting enforced
- Coverage tracked

### 4. Automation
- Automated dependency updates
- Automatic changelog generation
- One-click releases

### 5. Transparency
- All results in Security tab
- PR comments for coverage
- Build artifacts available

---

## Monitoring & Debugging

### GitHub Actions Dashboard
- Repository → Actions tab
- View all workflow runs
- Filter by event, status, workflow

### Security Tab
- Repository → Security → Code scanning
- View all security findings
- Filter by tool, severity

### Artifacts
- Download from workflow runs
- Coverage reports
- Build packages
- Security scan results

### Logs
- Click any workflow run
- Expand job steps
- Download raw logs

---

## Maintenance Tasks

### Weekly
- Review Dependabot PRs
- Check OSSF Scorecard results
- Monitor scheduled scans

### Monthly
- Review workflow performance
- Update action versions
- Audit security findings

### Quarterly
- Review and optimize workflows
- Update documentation
- Security tools evaluation

---

## Cost Analysis

**GitHub Actions Free Tier:**
- Public repos: Unlimited minutes
- Private repos: 2,000 minutes/month

**Estimated Monthly Usage:**
- Push workflows: ~300 minutes
- PR workflows: ~300 minutes
- Scheduled workflows: ~200 minutes
- **Total: ~800 minutes/month**

**Well within free tier limits!**

---

## Troubleshooting

### Build Failures

**Manifest check fails:**
```bash
# Locally run
check-manifest
# Add missing files to MANIFEST.in
```

**Package installation fails:**
```bash
# Test locally
python -m build
pip install dist/*.whl
```

### Test Failures

**Platform-specific issues:**
- Check matrix OS in logs
- Review platform-specific code
- Add conditional tests if needed

**Version-specific issues:**
- Check Python version in logs
- Review version compatibility
- Update version requirements

### Docker Build Failures

**Multi-arch issues:**
- Check Dockerfile compatibility
- Test locally with buildx
- Review platform-specific dependencies

**Cache issues:**
```bash
# Clear cache in workflow
# Add cache-from: type=gha with mode=max
```

### Publishing Failures

**PyPI upload fails:**
- Check trusted publishing setup
- Verify package version
- Review PyPI project settings

**Docker push fails:**
- Check GHCR permissions
- Verify registry login
- Review package settings

---

## Future Enhancements

### Planned
- [ ] Performance benchmarking
- [ ] Integration testing
- [ ] E2E testing
- [ ] Canary deployments
- [ ] Rollback automation

### Under Consideration
- [ ] Nightly builds
- [ ] Beta channel releases
- [ ] Automated security patching
- [ ] Multi-region deployments

---

**Last Updated:** 2026-01-29
**Maintained By:** Ansvar Systems DevOps Team
**Questions?** Open an issue or contact devops@ansvar.eu
