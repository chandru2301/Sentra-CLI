# Sentra CLI

A CLI tool that analyzes git diffs and decides whether a PR is safe to merge.

## Installation

```bash
pip install -e .
```

Or install directly:

```bash
python -m pip install .
```

## Usage

### Basic Scan

```bash
sentra scan
```

This compares your current branch against `main` (default base branch).

### Custom Base Branch

```bash
sentra scan --base develop
```

### Show Banner

Display the optional ASCII banner (enterprise users prefer clean by default):

```bash
sentra scan --banner
```

### Generate PR Comment

Generate a formatted PR comment (markdown) for posting to pull requests:

```bash
sentra scan --pr-comment
```

This outputs a professional, human-readable comment that satisfies three audiences:
- **Developer**: Clear action items
- **Lead/Manager**: Risk assessment
- **CI**: Deterministic signal

The comment includes confidence breakdowns when confidence < 80%, making Sentra defensible in audits.

## Theming

Sentra uses a professional purple theme (#9D4EDD) for brand identity. Colors are applied semantically:
- **Purple**: Headers, decisions, highlights (brand identity)
- **Green**: ALLOW decisions (success)
- **Yellow**: WARN decisions (warning)
- **Red**: BLOCK decisions (error)
- **Grey**: Secondary text (muted)

### Color Control

Sentra respects enterprise standards:
- **NO_COLOR**: Automatically disables colors when `NO_COLOR=1` is set
- **JSON output**: No colors, no emojis (`--json` flag)
- **CI-safe**: Clean output for automation

```bash
# Disable colors
NO_COLOR=1 sentra scan

# JSON output (always no colors)
sentra scan --json
```

## Exit Codes

| Decision | Exit Code | Meaning |
|----------|-----------|---------|
| ALLOW | 0 | Safe to merge |
| WARN | 0 | Review recommended (allowed to merge) |
| BLOCK | 1 | Merge blocked (requires manual review) |

CI/CD pipelines can use these exit codes to automatically block or warn on PRs. This makes Sentra predictable for enterprises.

## Safety Rules

The tool checks for:

1. **Sensitive File Detection** - Flags changes to security, auth, gateway, config files (MEDIUM → HIGH risk)
2. **Cross-Service Changes** - Detects changes across multiple services or shared modules (MEDIUM risk)
3. **Infrastructure Changes** - Flags port, Eureka, env var, Docker, CI file changes (HIGH risk)
4. **Large AI-Style Diffs** - Detects many files, large blocks, repeated patterns (MEDIUM risk)
5. **Test Coverage** - Warns if production code changed without tests (MEDIUM risk)

## Policy Packs

Create a `policy.yaml` file in your repo root to customize enforcement:

```yaml
version: 1

defaults:
  allow_severity: LOW
  block_severity: HIGH

paths:
  auth/:
    block_severity: MEDIUM

rules:
  INFRA_CHANGE:
    always_block: true
```

## AI Escalation (Optional)

Enable AI escalation via environment variables:

```bash
export OPENROUTER_API_KEY=sk-xxxx
export AI_ESCALATOR_ENABLED=true
export AI_ESCALATOR_MODEL=mistralai/devstral-2-2512:free
```

AI can only escalate MEDIUM → HIGH/CRITICAL. It never downgrades or decides.

## Example Output

```json
{
  "decision": "BLOCK",
  "confidence": 0.9,
  "reasons": [
    {
      "rule_id": "INFRA_CHANGE",
      "severity": "HIGH",
      "message": "Infrastructure configuration modified",
      "files": ["test_config/application.yml"]
    }
  ],
  "metadata": {
    "changed_files": 2,
    "affected_areas": ["auth", "config"],
    "base_branch": "main",
    "ai_escalation": "enabled",
    "policy_applied": true,
    "policy_file": "policy.yaml",
    "policy_version": 1
  }
}
```

## CI Integration

### GitHub Actions

See `.github/workflows/sentra.yml` for a complete example.

```yaml
- uses: ./.github/actions/sentra
  with:
    base_branch: main
```

### GitLab CI

See `.gitlab-ci.yml` for configuration.

### Jenkins

See `Jenkinsfile` for pipeline configuration.

### Docker

Build and run:

```bash
docker build -t sentra .
docker run \
  -e OPENROUTER_API_KEY=$OPENROUTER_API_KEY \
  -e AI_ESCALATOR_ENABLED=true \
  -v $(pwd):/scan \
  sentra scan --base main
```

Or use docker-compose:

```bash
docker-compose run sentra
```

## Development

```bash
# Run locally
python cli.py scan

# Run with custom base
python cli.py scan --base develop
```

## Failure Scenarios

| Scenario | Result |
|----------|--------|
| No policy.yaml | Defaults apply |
| No AI key | AI skipped |
| Git missing | BLOCK (exit 1) |
| AI timeout | AI skipped |
| Network down | AI skipped |
| Policy syntax error | Defaults apply |

CI must never hang.
