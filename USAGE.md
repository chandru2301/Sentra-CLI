# Sentra - Complete Usage Guide

A comprehensive guide to using the Sentra tool for analyzing git diffs and enforcing PR safety policies.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Basic Usage](#basic-usage)
4. [Configuration](#configuration)
5. [Policy Packs](#policy-packs)
6. [AI Escalation](#ai-escalation)
7. [CI/CD Integration](#cicd-integration)
8. [Exit Codes](#exit-codes)
9. [Examples](#examples)
10. [Troubleshooting](#troubleshooting)
11. [Best Practices](#best-practices)

---

## Installation

### From Source

```bash
# Clone the repository
git clone <repository-url>
cd CI-manager

# Install in development mode
pip install -e .
```

### From PyPI (when published)

```bash
pip install sentra
```

### Verify Installation

**Linux/macOS:**
```bash
sentra scan --help
```

**Windows (PowerShell):**
If the command is not found, try:
```powershell
# Refresh PATH
$env:PATH = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Or use Python module directly
python -m cli scan --help

# Or use full path
& "$env:LOCALAPPDATA\Programs\Python\Python311\Scripts\sentra.exe" scan --help
```

**Alternative (Windows):**
```powershell
# Use Python module directly (always works)
python cli.py scan --help
```

---

## Quick Start

### 1. Basic Scan

Run a scan comparing your current branch against `main`:

```bash
sentra scan
```

### 2. Custom Base Branch

Compare against a different base branch:

```bash
sentra scan --base develop
```

### 3. View Output

The tool outputs JSON to stdout:

```json
{
  "decision": "ALLOW",
  "confidence": 0.95,
  "reasons": [],
  "metadata": {
    "changed_files": 0,
    "affected_areas": [],
    "base_branch": "main",
    "ai_escalation": "disabled",
    "policy_applied": false
  }
}
```

---

## Basic Usage

### Command Syntax

```bash
sentra scan [--base BRANCH]
```

**Arguments:**
- `scan` - The only command (required)
- `--base BRANCH` - Base branch to compare against (default: `main`)

### Common Workflows

#### Pre-commit Check

```bash
# Before pushing, check your changes
git add .
sentra scan --base main
```

#### Pre-merge Check

```bash
# Check if your feature branch is safe to merge
git checkout feature-branch
sentra scan --base main
```

#### Compare Against Specific Branch

```bash
# Compare against release branch
sentra scan --base release/v1.0
```

---

## Configuration

### Environment Variables

sentra uses environment variables for optional features:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENROUTER_API_KEY` | API key for AI escalation | - | No (AI optional) |
| `AI_ESCALATOR_ENABLED` | Enable AI escalation | `false` | No |
| `AI_ESCALATOR_MODEL` | AI model to use | - | No |
| `AI_ESCALATOR_TIMEOUT` | AI request timeout (seconds) | `5` | No |

### Setting Environment Variables

**Linux/macOS:**
```bash
export OPENROUTER_API_KEY=sk-xxxx
export AI_ESCALATOR_ENABLED=true
export AI_ESCALATOR_MODEL=mistralai/devstral-2-2512:free
```

**Windows (PowerShell):**
```powershell
$env:OPENROUTER_API_KEY="sk-xxxx"
$env:AI_ESCALATOR_ENABLED="true"
$env:AI_ESCALATOR_MODEL="mistralai/devstral-2-2512:free"
```

**Windows (CMD):**
```cmd
set OPENROUTER_API_KEY=sk-xxxx
set AI_ESCALATOR_ENABLED=true
set AI_ESCALATOR_MODEL=mistralai/devstral-2-2512:free
```

---

## Policy Packs

Policy packs allow you to customize enforcement rules without changing code.

### Creating a Policy File

Create `policy.yaml` in your repository root:

```yaml
version: 1

defaults:
  allow_severity: LOW
  block_severity: HIGH

paths:
  auth/:
    block_severity: MEDIUM

  config/:
    block_severity: MEDIUM

  infra/:
    block_severity: LOW

branches:
  protected:
    - main
    - release/*

rules:
  INFRA_CHANGE:
    always_block: true

  TEST_COVERAGE:
    max_allowed_severity: MEDIUM
```

### Policy Configuration Options

#### Defaults

```yaml
defaults:
  allow_severity: LOW    # Severity level for ALLOW decision
  block_severity: HIGH   # Severity level for BLOCK decision
```

#### Path-Based Policies

Make specific directories stricter:

```yaml
paths:
  auth/:
    block_severity: MEDIUM  # Block on MEDIUM or higher in auth/
  
  config/:
    block_severity: MEDIUM  # Block on MEDIUM or higher in config/
```

#### Branch Protection

Apply stricter rules to protected branches:

```yaml
branches:
  protected:
    - main           # Exact match
    - release/*      # Pattern match (all release branches)
```

#### Rule-Specific Policies

```yaml
rules:
  INFRA_CHANGE:
    always_block: true  # Always block infrastructure changes
  
  TEST_COVERAGE:
    max_allowed_severity: MEDIUM  # Allow up to MEDIUM severity
```

### Policy Examples

#### Strict Production Policy

```yaml
version: 1

defaults:
  allow_severity: LOW
  block_severity: MEDIUM  # Block on MEDIUM (stricter)

paths:
  auth/:
    block_severity: LOW  # Very strict for auth
  
  infra/:
    block_severity: LOW  # Very strict for infra

branches:
  protected:
    - main
    - production

rules:
  INFRA_CHANGE:
    always_block: true
  
  SENSITIVE_FILES:
    always_block: true
```

#### Relaxed Development Policy

```yaml
version: 1

defaults:
  allow_severity: LOW
  block_severity: HIGH  # Only block on HIGH

paths:
  # No path-specific rules

branches:
  protected:
    - main  # Only protect main

rules:
  # No rule-specific overrides
```

---

## AI Escalation

AI escalation is an optional feature that can escalate MEDIUM severity findings to HIGH or CRITICAL.

### How It Works

1. **Only affects MEDIUM rules** - AI never touches LOW, HIGH, or CRITICAL
2. **Only escalates** - AI can only increase severity, never decrease
3. **Fails silently** - If AI is unavailable, tool continues without it
4. **Rate limited** - Maximum 5 escalations per scan

### Enabling AI Escalation

1. Get an OpenRouter API key from https://openrouter.ai
2. Set environment variables:

```bash
export OPENROUTER_API_KEY=sk-xxxx
export AI_ESCALATOR_ENABLED=true
export AI_ESCALATOR_MODEL=mistralai/devstral-2-2512:free
export AI_ESCALATOR_TIMEOUT=5
```

3. Run scan normally:

```bash
sentra scan
```

### AI Escalation Output

When AI escalates a rule, the output includes an `ai_escalated` flag:

```json
{
  "decision": "BLOCK",
  "confidence": 0.9,
  "reasons": [
    {
      "rule_id": "CROSS_SERVICE",
      "severity": "HIGH",
      "message": "Touches multiple services",
      "files": ["src/auth/service.py"],
      "ai_escalated": true
    }
  ],
  "metadata": {
    "ai_escalation": "enabled"
  }
}
```

### AI Escalation Behavior

| Scenario | Result |
|----------|--------|
| AI enabled, MEDIUM rule | AI evaluates, may escalate |
| AI enabled, HIGH rule | AI not called (already high) |
| AI enabled, timeout | AI skipped, original severity kept |
| AI disabled | AI skipped, original severity kept |
| No API key | AI skipped, original severity kept |

---

## CI/CD Integration

### GitHub Actions

#### Using the Provided Action

Add to `.github/workflows/sentra.yml`:

```yaml
name: sentra Gate

on:
  pull_request:
    branches:
      - main
      - develop

jobs:
  sentra:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: ./.github/actions/sentra
        with:
          base_branch: ${{ github.base_ref || 'main' }}
```

#### Setting Secrets

1. Go to repository Settings → Secrets and variables → Actions
2. Add secret: `OPENROUTER_API_KEY` (optional, for AI escalation)
3. Add secret: `AI_ESCALATOR_ENABLED` (optional, set to `"true"` to enable)
4. Add secret: `AI_ESCALATOR_MODEL` (optional, e.g., `"mistralai/devstral-2-2512:free"`)

### GitLab CI

Add to `.gitlab-ci.yml`:

```yaml
ai_safety_scan:
  image: python:3.10
  stage: test
  variables:
    AI_ESCALATOR_ENABLED: "true"
    AI_ESCALATOR_MODEL: "mistralai/devstral-2-2512:free"
  before_script:
    - pip install sentra
  script:
    - sentra scan --base ${CI_MERGE_REQUEST_TARGET_BRANCH_NAME:-main}
  only:
    - merge_requests
```

#### Setting Variables

1. Go to Settings → CI/CD → Variables
2. Add variable: `OPENROUTER_API_KEY` (optional, for AI escalation)
3. Mark as "Masked" and "Protected" if sensitive

### Jenkins

Add to `Jenkinsfile`:

```groovy
pipeline {
  agent any
  
  environment {
    AI_ESCALATOR_ENABLED = "true"
    AI_ESCALATOR_MODEL = "mistralai/devstral-2-2512:free"
    OPENROUTER_API_KEY = credentials('openrouter-key')
  }
  
  stages {
    stage('sentra Gate') {
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

#### Setting Credentials

1. Go to Jenkins → Manage Jenkins → Credentials
2. Add credential: `openrouter-key` (Secret text)
3. Store your OpenRouter API key

### Docker

#### Build Image

```bash
docker build -t sentra .
```

#### Run Locally

```bash
docker run \
  -e OPENROUTER_API_KEY=$OPENROUTER_API_KEY \
  -e AI_ESCALATOR_ENABLED=true \
  -e AI_ESCALATOR_MODEL=mistralai/devstral-2-2512:free \
  -v $(pwd):/scan \
  -w /scan \
  sentra scan --base main
```

#### Using Docker Compose

```bash
# Set environment variables
export OPENROUTER_API_KEY=sk-xxxx
export AI_ESCALATOR_ENABLED=true

# Run scan
docker-compose run sentra
```

---

## Exit Codes

The tool uses exit codes to communicate results to CI/CD systems:

| Exit Code | Meaning | Decision | CI Behavior |
|-----------|---------|----------|-------------|
| 0 | Safe | ALLOW or WARN | PR allowed, pipeline passes |
| 2 | Block | BLOCK | PR blocked, pipeline fails |

### Understanding Exit Codes

- **Exit 0 (Safe)**: Changes are safe to merge or require manual review
- **Exit 2 (Block)**: Changes are blocked and must be fixed before merging

### CI Integration

CI systems automatically interpret exit codes:

- **GitHub Actions**: Exit 2 → PR check fails → PR cannot be merged
- **GitLab CI**: Exit 2 → Pipeline fails → Merge request blocked
- **Jenkins**: Exit 2 → Stage fails → Pipeline stops

---

## Examples

### Example 1: Safe Change

**Scenario**: Adding a new utility function

```bash
$ sentra scan
```

**Output:**
```json
{
  "decision": "ALLOW",
  "confidence": 0.95,
  "reasons": [],
  "metadata": {
    "changed_files": 1,
    "affected_areas": [],
    "base_branch": "main"
  }
}
```

**Result**: Exit code 0 → Safe to merge

---

### Example 2: High Risk Change

**Scenario**: Modifying authentication and infrastructure config

```bash
$ sentra scan
```

**Output:**
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
    },
    {
      "rule_id": "INFRA_CHANGE",
      "severity": "HIGH",
      "message": "Modified infrastructure files: config/application.yml",
      "files": ["config/application.yml"]
    }
  ],
  "metadata": {
    "changed_files": 2,
    "affected_areas": ["auth", "config"],
    "base_branch": "main"
  }
}
```

**Result**: Exit code 2 → Blocked, requires review

---

### Example 3: AI Escalated Change

**Scenario**: MEDIUM severity rule escalated by AI

```bash
$ export AI_ESCALATOR_ENABLED=true
$ export OPENROUTER_API_KEY=sk-xxxx
$ sentra scan
```

**Output:**
```json
{
  "decision": "BLOCK",
  "confidence": 0.9,
  "reasons": [
    {
      "rule_id": "CROSS_SERVICE",
      "severity": "HIGH",
      "message": "Touches multiple services",
      "files": ["src/auth/service.py", "src/payment/service.py"],
      "ai_escalated": true
    }
  ],
  "metadata": {
    "changed_files": 2,
    "affected_areas": ["auth", "payment"],
    "base_branch": "main",
    "ai_escalation": "enabled"
  }
}
```

**Result**: Exit code 2 → Blocked (AI escalated MEDIUM → HIGH)

---

### Example 4: Policy-Enforced Block

**Scenario**: Policy requires blocking all infra changes

**policy.yaml:**
```yaml
version: 1

rules:
  INFRA_CHANGE:
    always_block: true
```

**Output:**
```json
{
  "decision": "BLOCK",
  "confidence": 0.9,
  "reasons": [
    {
      "rule_id": "INFRA_CHANGE",
      "severity": "HIGH",
      "message": "Modified infrastructure files: docker-compose.yml",
      "files": ["docker-compose.yml"]
    }
  ],
  "metadata": {
    "changed_files": 1,
    "affected_areas": ["infra"],
    "base_branch": "main",
    "policy_applied": true,
    "policy_file": "policy.yaml",
    "policy_version": 1
  }
}
```

**Result**: Exit code 2 → Blocked by policy

---

## Troubleshooting

### Issue: "sentra: command not found" (Windows)

**Error:**
```
sentra : The term 'sentra' is not recognized as the name of a cmdlet
```

**Solution 1: Refresh PATH**
```powershell
# Refresh PATH in current session
$env:PATH = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Try again
sentra scan --help
```

**Solution 2: Use Python module directly**
```powershell
# This always works, no PATH issues
python cli.py scan --help
```

**Solution 3: Use full path**
```powershell
# Find your Python Scripts directory
python -c "import sys; print(sys.executable.replace('python.exe', 'Scripts'))"

# Use full path
& "C:\Users\YourUser\AppData\Local\Programs\Python\Python311\Scripts\sentra.exe" scan --help
```

**Solution 4: Restart PowerShell**
- Close and reopen PowerShell to refresh PATH
- Or restart your terminal/IDE

**Solution 5: Verify installation**
```powershell
# Check if installed
python -m pip show sentra

# Reinstall if needed
pip install -e .
```

---

### Issue: "Not a git repository"

**Error:**
```
Error: Not a git repository. Please run this command from a git repository.
```

**Solution:**
- Ensure you're in a git repository
- Run `git init` if starting a new project
- Check that `.git` directory exists

---

### Issue: "git command not found"

**Error:**
```
Error: git command not found. Please ensure git is installed.
```

**Solution:**
- Install git: `sudo apt-get install git` (Linux) or download from git-scm.com
- Verify: `git --version`
- Ensure git is in your PATH

---

### Issue: No changes detected

**Output:**
```json
{
  "decision": "ALLOW",
  "reasons": [],
  "metadata": {
    "changed_files": 0
  }
}
```

**Possible Causes:**
- No differences between branches
- All changes are already committed
- Comparing against wrong branch

**Solution:**
- Check: `git diff main..HEAD`
- Verify base branch: `sentra scan --base <correct-branch>`

---

### Issue: AI escalation not working

**Symptoms:**
- `ai_escalation: "disabled"` in output
- No `ai_escalated` flags in reasons

**Checklist:**
1. Verify environment variables are set:
   ```bash
   echo $AI_ESCALATOR_ENABLED
   echo $OPENROUTER_API_KEY
   echo $AI_ESCALATOR_MODEL
   ```
2. Check API key is valid
3. Verify network connectivity
4. Check timeout settings (increase if needed)

**Solution:**
- AI is optional - tool works without it
- If AI fails, tool continues with original severities
- Check logs for AI errors (if any)

---

### Issue: Policy not applied

**Symptoms:**
- `policy_applied: false` in output

**Checklist:**
1. Verify `policy.yaml` exists in repo root
2. Check YAML syntax is valid
3. Ensure `version` field is set

**Solution:**
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('policy.yaml'))"

# Check file location
ls -la policy.yaml
```

---

### Issue: Exit code always 0

**Symptoms:**
- Tool always exits with code 0, even for HIGH severity

**Possible Causes:**
- Policy configured to allow HIGH severity
- Default `block_severity` is too high

**Solution:**
- Check `policy.yaml` defaults
- Verify `block_severity` setting
- Check if policy is overriding decision

---

## Best Practices

### 1. Policy Management

- **Version control policies**: Commit `policy.yaml` to repository
- **Review policy changes**: Treat policy changes like code changes
- **Test policies**: Test policy changes in feature branches first
- **Document policies**: Add comments explaining why rules exist

### 2. CI/CD Integration

- **Run early**: Add to PR checks, not just merge
- **Fail fast**: Block early in pipeline
- **Clear messaging**: Use JSON output for clear error messages
- **Monitor**: Track decision patterns over time

### 3. AI Escalation

- **Start disabled**: Enable AI only after validating rules
- **Monitor costs**: Track API usage and costs
- **Set timeouts**: Use reasonable timeout values (5-10 seconds)
- **Have fallback**: Tool works perfectly without AI

### 4. Branch Strategy

- **Protect main**: Always use strict policies for main branch
- **Relax for dev**: Use relaxed policies for development branches
- **Branch-specific**: Use branch protection in policies

### 5. Rule Tuning

- **Start strict**: Begin with strict rules, relax as needed
- **Measure impact**: Track how often rules trigger
- **Iterate**: Adjust rules based on team feedback
- **Document**: Explain why each rule exists

### 6. Team Adoption

- **Educate team**: Explain what each rule checks
- **Provide examples**: Show examples of blocked vs allowed changes
- **Gather feedback**: Adjust based on team needs
- **Celebrate safety**: Recognize when rules catch issues

---

## Advanced Usage

### Parsing JSON Output

**Python:**
```python
import json
import subprocess

result = subprocess.run(
    ["sentra", "scan"],
    capture_output=True,
    text=True
)

data = json.loads(result.stdout)
print(f"Decision: {data['decision']}")
print(f"Confidence: {data['confidence']}")
```

**Bash:**
```bash
output=$(sentra scan)
decision=$(echo $output | jq -r '.decision')
echo "Decision: $decision"
```

**PowerShell:**
```powershell
$output = sentra scan | ConvertFrom-Json
Write-Host "Decision: $($output.decision)"
```

### Custom Scripts

**Pre-commit Hook:**
```bash
#!/bin/bash
sentra scan --base main
if [ $? -eq 2 ]; then
    echo "sentra check failed. Please review the output above."
    exit 1
fi
```

**Git Hook:**
```bash
# .git/hooks/pre-push
#!/bin/bash
sentra scan --base origin/main
exit $?
```

---

## Support

For issues, questions, or contributions:

1. Check this documentation
2. Review troubleshooting section
3. Check repository issues
4. Review code and policy examples

---

## License

[Add your license information here]

---

**Last Updated**: 2024

