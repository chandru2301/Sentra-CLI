# Sentra CLI - Functionalities Documentation

A comprehensive guide to all features and capabilities of Sentra, an AI safety gate for code.

## Table of Contents

1. [Core Functionality](#core-functionality)
2. [Safety Rules](#safety-rules)
3. [Policy Engine](#policy-engine)
4. [AI Escalation](#ai-escalation)
5. [CLI Commands](#cli-commands)
6. [Output Formats](#output-formats)
7. [Decision System](#decision-system)
8. [License Tiers](#license-tiers)
9. [CI/CD Integration](#cicd-integration)
10. [Git Integration](#git-integration)

---

## Core Functionality

### Purpose

Sentra analyzes git diffs to determine if code changes are safe to merge. It evaluates the **intent** behind changes, not just syntax, making it a safety gate for AI-written code.

### Key Capabilities

- **Git Diff Analysis**: Reads and parses git diffs between branches
- **Risk Assessment**: Evaluates changes using multiple safety rules
- **Decision Making**: Produces deterministic decisions (ALLOW/WARN/BLOCK)
- **Policy Enforcement**: Applies custom policies via `policy.yaml`
- **CI Integration**: Designed for automated CI/CD pipelines
- **Exit Codes**: Uses standard exit codes for CI automation

### Workflow

1. Read git diff between current branch and base branch
2. Parse diff into structured format (files, chunks, lines)
3. Run all safety rules against the changes
4. Apply policy rules (if configured)
5. Apply AI escalation (if enabled, optional)
6. Map rule results to decision and confidence
7. Apply license tier restrictions (Free tier downgrades BLOCK to WARN)
8. Output result in requested format (JSON, PR comment, or pretty)

---

## Safety Rules

Sentra includes five built-in safety rules that evaluate different aspects of code changes:

### 1. Sensitive Files Detection (`SENSITIVE_FILES`)

**Purpose**: Flags changes to security-critical files and configurations.

**Detection**:
- Files matching patterns: `security`, `auth`, `gateway`, `config`
- Configuration files: `application.yml`, `application.yaml`, `.properties`
- Files containing sensitive keywords in path

**Severity**:
- Single sensitive file: **MEDIUM**
- Multiple sensitive files: **HIGH**
- Configuration files: **HIGH**

**Example Triggers**:
- `src/auth/service.py`
- `config/application.yml`
- `src/security/gateway.py`

---

### 2. Cross-Service Changes (`CROSS_SERVICE`)

**Purpose**: Detects changes that span multiple services or touch shared modules.

**Detection**:
- Multiple services touched in single PR
- Shared modules modified (common, shared, lib, utils)
- Multiple top-level directories changed

**Severity**: **MEDIUM**

**Example Triggers**:
- Changes to both `auth/service.py` and `payment/service.py`
- Modifications to `common/utils.py` and `shared/lib.py`
- Changes across multiple service directories

---

### 3. Infrastructure Changes (`INFRA_CHANGE`)

**Purpose**: Flags infrastructure and deployment configuration changes.

**Detection**:
- **Files**: Dockerfile, docker-compose, .env, Jenkinsfile, CI configs, Kubernetes, Helm
- **Content**: Port changes, Eureka URLs, environment variables, server.port

**Severity**: **HIGH**

**Example Triggers**:
- `Dockerfile` modifications
- `.github/workflows/deploy.yml` changes
- Port configuration changes in `application.yml`
- Environment variable additions/removals

---

### 4. Large Diffs (`LARGE_DIFF`)

**Purpose**: Detects large-scale changes that might indicate AI-generated code.

**Detection**:
- Many files changed (> 10 files)
- Large total diff (> 500 lines added/removed)
- Multiple large files (> 3 files with > 200 lines changed)
- Repeated patterns (similar-sized chunks, AI-style patterns)

**Severity**: **MEDIUM**

**Example Triggers**:
- 15 files changed in single PR
- 800 lines added across multiple files
- 5 files with > 200 lines changed each
- Repeated similar chunk patterns

---

### 5. Test Coverage (`TEST_COVERAGE`)

**Purpose**: Warns when production code changes without corresponding test updates.

**Detection**:
- Production code files changed (`.py`, `.java`, `.js`, `.ts`, etc.)
- No test files updated (no `test`, `spec`, `__tests__` patterns)
- Excludes config, docs, and non-code files

**Severity**: **MEDIUM**

**Example Triggers**:
- `src/service.py` modified but no `test_service.py` updated
- Production code changes without test coverage
- Business logic changes without tests

---

## Policy Engine

### Overview

The policy engine allows customization of enforcement rules without changing code. Policies are defined in `policy.yaml` in the repository root.

### Policy Structure

```yaml
version: 1

defaults:
  allow_severity: LOW    # Severity level for ALLOW decision
  block_severity: HIGH   # Severity level for BLOCK decision

paths:
  auth/:
    block_severity: MEDIUM  # Stricter rules for auth/ directory

branches:
  protected:
    - main
    - release/*  # Pattern matching for release branches

rules:
  INFRA_CHANGE:
    always_block: true  # Always block infrastructure changes
  
  TEST_COVERAGE:
    max_allowed_severity: MEDIUM  # Allow up to MEDIUM severity
```

### Policy Capabilities

**What Policies Can Do**:
- ✅ Force BLOCK on specific rules (`always_block`)
- ✅ Lower tolerance for specific paths (`block_severity` per path)
- ✅ Override default thresholds (`allow_severity`, `block_severity`)
- ✅ Apply stricter rules to protected branches
- ✅ Set maximum allowed severity per rule

**What Policies Cannot Do**:
- ❌ Change rule logic
- ❌ Modify AI behavior
- ❌ Downgrade detected severity (only escalate)
- ❌ Silence a triggered rule

### Path-Based Policies

Apply stricter rules to specific directories:

```yaml
paths:
  auth/:
    block_severity: MEDIUM  # Block on MEDIUM or higher in auth/
  
  config/:
    block_severity: LOW     # Very strict for config/
```

### Branch Protection

Apply stricter rules to protected branches:

```yaml
branches:
  protected:
    - main           # Exact match
    - release/*      # Pattern match (all release branches)
    - production     # Exact match
```

### Rule-Specific Policies

Override behavior for specific rules:

```yaml
rules:
  INFRA_CHANGE:
    always_block: true  # Always block, regardless of severity
  
  TEST_COVERAGE:
    max_allowed_severity: MEDIUM  # Allow up to MEDIUM
```

---

## AI Escalation

### Overview

AI escalation is an **optional** feature that can escalate MEDIUM severity findings to HIGH or CRITICAL. AI never downgrades or decides—it only escalates.

### How It Works

1. **Only affects MEDIUM rules**: AI never touches LOW, HIGH, or CRITICAL
2. **Only escalates**: AI can only increase severity (MEDIUM → HIGH/CRITICAL)
3. **Fails silently**: If AI is unavailable, tool continues without it
4. **Rate limited**: Maximum 5 escalations per scan (prevents cost explosions)

### Configuration

Set environment variables:

```bash
export OPENROUTER_API_KEY=sk-xxxx
export AI_ESCALATOR_ENABLED=true
export AI_ESCALATOR_MODEL=mistralai/devstral-2-2512:free
export AI_ESCALATOR_TIMEOUT=5  # seconds
```

### AI Behavior

| Scenario | Result |
|----------|--------|
| AI enabled, MEDIUM rule | AI evaluates, may escalate to HIGH/CRITICAL |
| AI enabled, HIGH rule | AI not called (already high) |
| AI enabled, timeout | AI skipped, original severity kept |
| AI disabled | AI skipped, original severity kept |
| No API key | AI skipped, original severity kept |

### AI Escalation Output

When AI escalates a rule, the output includes an `ai_escalated` flag:

```json
{
  "reasons": [
    {
      "rule_id": "CROSS_SERVICE",
      "severity": "HIGH",
      "message": "Touches multiple services",
      "ai_escalated": true
    }
  ],
  "metadata": {
    "ai_escalation": "enabled"
  }
}
```

---

## CLI Commands

### Basic Scan

```bash
sentra scan
```

Compares current branch against `main` (default base branch).

### Custom Base Branch

```bash
sentra scan --base develop
```

Compare against a different base branch.

### JSON Output

```bash
sentra scan --json
```

Output machine-readable JSON format (no colors, no emojis).

### PR Comment Format

```bash
sentra scan --pr-comment
```

Generate formatted PR comment (markdown) for posting to pull requests.

### Show Banner

```bash
sentra scan --banner
```

Display optional ASCII banner (enterprise users prefer clean by default).

### Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `--base BRANCH` | Base branch to compare against | `main` |
| `--json` | Output JSON format | Pretty format |
| `--pr-comment` | Output PR comment format | Pretty format |
| `--banner` | Show ASCII banner | No banner |

---

## Output Formats

### Pretty Format (Default)

Human-readable output with colors and formatting:

```
Sentra Policy Scan · v1.0.0

Decision: ❌ BLOCK
Confidence: 90%
Base branch: main
Files changed: 2

Policy Findings (2)
• SENSITIVE_FILES · HIGH
  Modified sensitive files: src/auth/service.py
  • src/auth/service.py

• INFRA_CHANGE · HIGH
  Modified infrastructure files: config/application.yml
  • config/application.yml

────────────────────────────────────────
Result: Merge blocked
Policy requires manual review
```

### JSON Format

Machine-readable JSON output:

```json
{
  "decision": "BLOCK",
  "confidence": 0.9,
  "reasons": [
    {
      "rule_id": "SENSITIVE_FILES",
      "severity": "HIGH",
      "message": "Modified sensitive files: src/auth/service.py",
      "files": ["src/auth/service.py"]
    }
  ],
  "metadata": {
    "changed_files": 2,
    "affected_areas": ["auth", "config"],
    "base_branch": "main",
    "ai_escalation": "disabled",
    "policy_applied": true,
    "policy_file": "policy.yaml",
    "policy_version": 1,
    "license_tier": "free"
  }
}
```

### PR Comment Format

Markdown formatted for PR comments:

```markdown
## Sentra Policy Scan

**Decision**: ❌ BLOCK  
**Confidence**: 90%

### Policy Findings

- **SENSITIVE_FILES** (HIGH): Modified sensitive files: src/auth/service.py
- **INFRA_CHANGE** (HIGH): Modified infrastructure files: config/application.yml

**Result**: Merge blocked. Policy requires manual review.
```

---

## Decision System

### Decision Types

| Decision | Meaning | Exit Code | CI Behavior |
|----------|---------|-----------|-------------|
| **ALLOW** | Safe to merge | 0 | PR allowed, pipeline passes |
| **WARN** | Review recommended | 0 | PR allowed, pipeline passes |
| **BLOCK** | Merge blocked | 1 | PR blocked, pipeline fails |

### Decision Logic

**Default (No Policy)**:
- CRITICAL or HIGH severity → **BLOCK**
- MEDIUM severity → **WARN**
- LOW severity or no rules → **ALLOW**

**With Policy**:
- Policy rules take precedence
- Path-based policies apply
- Branch protection rules apply
- Rule-specific overrides apply

### Confidence Scores

| Decision | Confidence Range | Meaning |
|----------|------------------|---------|
| ALLOW | ≤ 0.95 | High confidence in safety |
| WARN | ≤ 0.75 | Moderate confidence, review needed |
| BLOCK | ≤ 0.90 | High confidence in risk |

### Confidence Breakdown

When confidence < 0.8, Sentra provides a breakdown:

- ✔ Deterministic rule evaluation
- ✔ Test files updated
- ✔ Change limited to a single module
- ✖ No test coverage changes detected
- ✖ Core module touched
- ✖ AI-generated code escalation

---

## License Tiers

### Free Tier

**Capabilities**:
- ✅ Local scans
- ✅ Basic policy rules
- ✅ All safety rules
- ✅ JSON output
- ✅ PR comment format

**Limitations**:
- ❌ BLOCK decisions downgraded to WARN
- ❌ Exit code always 0 (never blocks CI)
- ❌ No CI enforcement

### Pro Tier

**Capabilities**:
- ✅ Everything in Free tier
- ✅ CI enforcement (BLOCK = exit code 1)
- ✅ Custom policies
- ✅ Team management
- ✅ Audit logs

### Enterprise Tier

**Capabilities**:
- ✅ Everything in Pro tier
- ✅ Policy customization
- ✅ Full audit logs
- ✅ SLA
- ✅ Support

---

## CI/CD Integration

### GitHub Actions

```yaml
name: Sentra Gate

on:
  pull_request:
    branches: [main, develop]

jobs:
  sentra:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Run Sentra
        run: |
          pip install sentra
          sentra scan --base ${{ github.base_ref || 'main' }} --json
```

### GitLab CI

```yaml
ai_safety_scan:
  image: python:3.10
  stage: test
  script:
    - pip install sentra
    - sentra scan --base ${CI_MERGE_REQUEST_TARGET_BRANCH_NAME:-main}
  only:
    - merge_requests
```

### Jenkins

```groovy
pipeline {
  agent any
  
  stages {
    stage('Sentra Gate') {
      steps {
        sh '''
          pip install sentra
          sentra scan --base ${CHANGE_TARGET:-main}
        '''
      }
    }
  }
}
```

### Docker

```bash
docker build -t sentra .
docker run \
  -e OPENROUTER_API_KEY=$OPENROUTER_API_KEY \
  -e AI_ESCALATOR_ENABLED=true \
  -v $(pwd):/scan \
  -w /scan \
  sentra scan --base main
```

---

## Git Integration

### Diff Reading

Sentra reads git diffs using:

1. **Branch comparison**: `git diff base_branch..HEAD`
2. **Fallback to staged**: If branch comparison fails, uses `git diff --cached`
3. **Error handling**: Validates git repository and git availability

### Base Branch Resolution

- Default: `main`
- Custom: `--base BRANCH` flag
- CI-aware: Uses `github.base_ref` or `CI_MERGE_REQUEST_TARGET_BRANCH_NAME`

### Diff Parsing

Parses git diff format into structured data:

```python
{
  "path/to/file.py": {
    "added_lines": 10,
    "removed_lines": 5,
    "chunks": [
      {
        "old_start": 1,
        "old_count": 5,
        "new_start": 1,
        "new_count": 10,
        "lines": [
          ("added", "new line content"),
          ("removed", "old line content"),
          ("context", "unchanged line")
        ]
      }
    ]
  }
}
```

### Pre-flight Checks

- ✅ Validates git is installed
- ✅ Validates git repository exists
- ✅ Handles missing base branch gracefully
- ✅ Falls back to staged changes if needed

---

## Exit Codes

| Exit Code | Decision | Meaning | CI Behavior |
|-----------|----------|---------|-------------|
| 0 | ALLOW or WARN | Safe to merge or review recommended | Pipeline passes |
| 1 | BLOCK | Merge blocked | Pipeline fails |

**Note**: Free tier always exits with code 0 (BLOCK downgraded to WARN).

---

## Error Handling

### Failure Scenarios

| Scenario | Result | Exit Code |
|----------|--------|-----------|
| No policy.yaml | Defaults apply | 0 or 1 |
| No AI key | AI skipped | 0 or 1 |
| Git missing | BLOCK (exit 1) | 1 |
| AI timeout | AI skipped | 0 or 1 |
| Network down | AI skipped | 0 or 1 |
| Policy syntax error | Defaults apply | 0 or 1 |

**Principle**: CI must never hang. All failures are handled gracefully.

---

## Summary

Sentra provides:

- ✅ **5 built-in safety rules** for comprehensive risk assessment
- ✅ **Policy engine** for customizable enforcement
- ✅ **AI escalation** (optional) for intelligent risk assessment
- ✅ **Multiple output formats** (pretty, JSON, PR comment)
- ✅ **CI/CD integration** (GitHub Actions, GitLab CI, Jenkins, Docker)
- ✅ **License tiers** (Free, Pro, Enterprise)
- ✅ **Deterministic decisions** with confidence scores
- ✅ **Git-native** diff analysis
- ✅ **Enterprise-grade** error handling

All features work together to provide a non-bypassable safety gate for AI-written code, enforced locally and in CI.

