# Pre-Commit Hooks Design

**Date:** 2026-01-29
**Status:** Approved
**Goal:** Prevent pushing broken code by enforcing strict local validation before commits

---

## Overview

Implement pre-commit hooks using the `pre-commit` framework to mirror CI/CD checks locally, providing fast feedback (15-35 seconds) and catching 90% of CI failures before push.

**Key Principles:**
- **Strict validation** - All tests, smoke tests, and formatting must pass
- **Bypassable** - Allow `--no-verify` for emergencies/WIP commits
- **Fast feedback** - Incremental checks on changed files only
- **CI mirror** - Local hooks match GitHub Actions checks

---

## Architecture

### Tool Choice: Pre-commit Framework

Use `pre-commit` (https://pre-commit.com/) instead of custom bash scripts:

✅ **Benefits:**
- Industry standard for Python projects
- Built-in caching (runs only on changed files)
- Auto-update capability for hook versions
- Language-agnostic (Python, shell, YAML, JSON)
- Built-in `--no-verify` support

### Hook Execution Flow

```yaml
.pre-commit-config.yaml
├── Stage 1: Formatting (auto-fix, ~1-2s)
│   ├── black - Auto-format Python code
│   └── ruff --fix - Auto-fix imports, unused vars
├── Stage 2: Linting (check-only, ~2-3s)
│   ├── ruff check - Strict validation
│   ├── check-yaml - GitHub Actions configs
│   ├── check-json - Data file validation
│   ├── trailing-whitespace
│   └── end-of-file-fixer
└── Stage 3: Testing (validation, ~10-30s)
    ├── pytest tests/ - Unit tests
    ├── verify_production_ready.py - Smoke test
    └── test_server.py - Server startup test
```

**Total Runtime:** 15-35 seconds per commit

---

## Detailed Hook Configuration

### Stage 1: Fast Formatting (Auto-fix)

**black**
- Auto-formats all Python files
- Excludes: `http_server.py` (Windows Unicode compatibility)
- Config: 100 char line length from `pyproject.toml`
- Runs only on changed `.py` files

**ruff (with --fix)**
- Auto-fixes: import sorting, unused variables, simple errors
- Uses existing config: E, F, I rules, ignore E501
- Runs only on changed `.py` files

### Stage 2: Linting (Check Only)

**ruff check**
- Strict validation, fails on unfixable issues
- Same config as CI: select E, F, I; ignore E501

**File validation**
- `check-yaml` - Validates `.github/workflows/*.yml`
- `check-json` - Validates `src/security_controls_mcp/data/*.json`
- `trailing-whitespace` - Removes trailing spaces
- `end-of-file-fixer` - Ensures newline at EOF

### Stage 3: Testing (Validation)

**pytest**
- Runs: `pytest tests/ -v --tb=short`
- Uses `pyproject.toml` config (asyncio_mode=auto, markers)
- Covers: data loader, integration, paid standards, smoke, content quality, security

**verify_production_ready.py**
- Comprehensive smoke test covering:
  - Data file existence and validity
  - MCP server functionality
  - Framework mapping integrity
  - Control data quality
- Environment: `PYTHONIOENCODING=utf-8` for Windows

**test_server.py**
- Validates MCP server startup
- Ensures server responds to basic requests
- Environment: `PYTHONIOENCODING=utf-8` for Windows

---

## Performance Optimizations

1. **Incremental Execution**
   - Formatters/linters run only on changed files
   - Full test suite runs (necessary for correctness)

2. **Parallel Processing**
   - Multiple hooks execute concurrently where possible
   - Pre-commit manages parallelization automatically

3. **Smart Caching**
   - Pre-commit caches hook virtualenvs
   - Avoids re-installing dependencies on each run

4. **Fail Fast**
   - Formatting runs first (fastest, auto-fixes)
   - Tests run last (slowest, only if formatting passes)

---

## Developer Workflow

### Normal Commit Flow
```bash
git add .
git commit -m "Add new feature"

# Hooks execute automatically:
# ✓ black (auto-formatted 3 files)
# ✓ ruff --fix (sorted imports in 2 files)
# ✓ ruff check (passed)
# ✓ check-json (passed)
# ✓ pytest (25 tests passed)
# ✓ verify_production_ready.py (all checks passed)
# ✓ test_server.py (server started successfully)
#
# [main abc1234] Add new feature
```

### Emergency Bypass
```bash
# WIP commits, debugging, hotfixes
git commit -m "WIP: debugging issue" --no-verify

# Skips all hooks, instant commit
# CI will still validate before merge
```

### Manual Hook Testing
```bash
# Run all hooks on all files (pre-commit check)
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
pre-commit run pytest --all-files
```

### First-Time Setup
```bash
# Install dev dependencies (includes pre-commit)
pip install -e ".[dev]"

# Activate hooks
pre-commit install

# Done! Hooks run automatically on next commit
```

---

## CI/CD Integration

### Local vs CI Comparison

| Check | Local Pre-commit | GitHub Actions CI |
|-------|-----------------|-------------------|
| **Formatting** | black (auto-fix) | black --check |
| **Linting** | ruff check | ruff check |
| **Unit Tests** | pytest tests/ | pytest (3 OS × 3 Python) |
| **Smoke Test** | verify_production_ready.py | verify_production_ready.py |
| **Server Test** | test_server.py | test_server.py |
| **Security** | ❌ (CI only) | CodeQL, Semgrep, Gitleaks, Trivy |
| **Coverage** | ❌ (CI only) | Coverage reporting |
| **Multi-version** | ❌ (CI only) | Python 3.10, 3.11, 3.12 |
| **Multi-OS** | ❌ (CI only) | Ubuntu, macOS, Windows |

### Value Proposition

**Local pre-commit:**
- Catches 90% of CI failures in ~20 seconds
- Fast feedback loop for developers
- Reduces "fix CI" commits in history

**GitHub Actions CI:**
- Validates across multiple environments
- Runs security scans (too slow for local)
- Final gate before merge
- Matrix testing (OS × Python versions)

### Workflow Benefits

```
Without Hooks:                With Hooks:
┌─────────────┐              ┌─────────────┐
│ Write code  │              │ Write code  │
└──────┬──────┘              └──────┬──────┘
       │                            │
┌──────▼──────┐              ┌──────▼──────┐
│ git commit  │              │ git commit  │
└──────┬──────┘              └──────┬──────┘
       │                            │
┌──────▼──────┐              ┌──────▼──────────────┐
│  git push   │              │ Pre-commit (20s)    │
└──────┬──────┘              │ ✓ Format            │
       │                     │ ✓ Lint              │
┌──────▼──────┐              │ ✓ Test              │
│ CI runs     │              └──────┬──────────────┘
│ (5-10 min)  │                     │
└──────┬──────┘              ┌──────▼──────┐
       │                     │  git push   │
┌──────▼──────┐              └──────┬──────┘
│ ❌ CI fails │                     │
│ (linting)   │              ┌──────▼──────┐
└──────┬──────┘              │ ✓ CI passes │
       │                     │ (5 min)     │
┌──────▼──────┐              └──────┬──────┘
│ Fix & push  │                     │
└──────┬──────┘              ┌──────▼──────┐
       │                     │ ✓ Merge     │
┌──────▼──────┐              └─────────────┘
│ CI runs     │
│ (5-10 min)  │
└──────┬──────┘
       │
┌──────▼──────┐
│ ✓ CI passes │
└──────┬──────┘
       │
┌──────▼──────┐
│    Merge    │
└─────────────┘

Total: 10-20 min          Total: 5-7 min
```

---

## Error Handling & User Feedback

### Success Output
```bash
$ git commit -m "Update control mappings"

black....................................Passed
ruff.....................................Passed
ruff-check...............................Passed
check-json...............................Passed
pytest...................................Passed
smoke-test...............................Passed
server-test..............................Passed

[main def5678] Update control mappings
 2 files changed, 45 insertions(+), 12 deletions(-)
```

### Formatting Failure (Auto-fixed)
```bash
$ git commit -m "Add new feature"

black....................................Failed
- hook id: black
- files were modified by this hook

reformatted src/security_controls_mcp/new_feature.py
1 file reformatted

# Fix: Files were auto-formatted, just re-commit
$ git add .
$ git commit -m "Add new feature"
# → Hooks pass, commit succeeds
```

### Test Failure
```bash
$ git commit -m "Add broken feature"

black....................................Passed
ruff.....................................Passed
ruff-check...............................Passed
pytest...................................Failed
- hook id: pytest
- exit code: 1

tests/test_integration.py::test_search_controls FAILED
AssertionError: Expected 5 results, got 3

# Fix: Correct the test or implementation
$ # ... fix code ...
$ git commit -m "Add feature (fixed tests)"
# → Hooks pass, commit succeeds
```

### Emergency Bypass
```bash
$ git commit -m "WIP: debugging" --no-verify

[main 9abc123] WIP: debugging
 1 file changed, 5 insertions(+)

# Skipped all hooks
# CI will still run on push
```

---

## Implementation Checklist

- [ ] Add `pre-commit>=3.0.0` to `pyproject.toml` dev dependencies
- [ ] Create `.pre-commit-config.yaml` with hook definitions
- [ ] Update `.gitignore` to exclude `.pre-commit-cache/`
- [ ] Update `README.md` with setup instructions
- [ ] Add troubleshooting guide for common hook issues
- [ ] Document `--no-verify` escape hatch
- [ ] Test hooks on clean checkout
- [ ] Verify hooks work on macOS, Linux, Windows
- [ ] Commit and push configuration
- [ ] Update team documentation

---

## Documentation Updates

### README.md Addition

```markdown
## Development Setup

### Install Dependencies
```bash
pip install -e ".[dev]"
```

### Activate Pre-commit Hooks
```bash
pre-commit install
```

This installs git hooks that automatically run before each commit:
- Code formatting (black, ruff)
- Linting (ruff check)
- Tests (pytest, smoke tests, server startup)

**Bypass hooks (emergencies only):**
```bash
git commit --no-verify
```

### Run Hooks Manually
```bash
# All hooks on all files
pre-commit run --all-files

# Specific hook
pre-commit run black --all-files
```
```

### Troubleshooting Guide

**Problem:** Hooks run slowly (>60 seconds)

**Solution:** Tests are running on every commit. This is expected for strict validation. Use `--no-verify` for WIP commits.

---

**Problem:** `pre-commit: command not found`

**Solution:** Install dev dependencies: `pip install -e ".[dev]"`

---

**Problem:** Black keeps reformatting my code

**Solution:** Let black auto-format, then re-commit. Your code will match project style.

---

**Problem:** I need to commit broken code temporarily

**Solution:** Use `git commit --no-verify` to bypass hooks. Fix before pushing.

---

## Future Enhancements

**Potential additions (not in initial scope):**
- Type checking with `mypy` (if type hints are added)
- Security scanning with `bandit` (if not too slow)
- Dependency checking with `safety` (monthly, not per-commit)
- Commit message linting with `commitlint`
- Branch name validation

**Performance monitoring:**
- Track hook execution time
- Consider skipping slow tests for small commits
- Add `--no-verify` guidance for WIP workflows

---

## Success Criteria

✅ **Pre-commit hooks prevent broken commits:**
- Formatting issues caught before commit
- Test failures caught before commit
- Linting issues caught before commit

✅ **Developer experience is smooth:**
- Setup takes <2 minutes
- Hook runtime is <35 seconds for typical commits
- Clear error messages with actionable fixes
- Bypass available for emergencies

✅ **CI/CD integration is seamless:**
- Local hooks mirror CI checks
- CI still validates across environments
- Reduced "fix CI" commits in history

✅ **Team adoption is successful:**
- Documentation is clear and accessible
- Troubleshooting guide covers common issues
- Developers understand when to use `--no-verify`
