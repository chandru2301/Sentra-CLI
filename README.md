# AI Safety

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
ai-safety scan
```

This compares your current branch against `main` (default base branch).

### Custom Base Branch

```bash
ai-safety scan --base develop
```

### Fail on Specific Risk Level

```bash
ai-safety scan --fail-on high
```

This will exit with code 2 if risk is HIGH or above.

## Exit Codes

| Exit Code | Meaning |
|-----------|---------|
| 0 | Safe (LOW risk) |
| 1 | Warning (MEDIUM risk) |
| 2 | Block (HIGH risk) |

CI/CD pipelines can use these exit codes to automatically block or warn on PRs.

## Safety Rules

The tool checks for:

1. **Sensitive File Detection** - Flags changes to security, auth, gateway, config files (MEDIUM → HIGH risk)
2. **Cross-Service Changes** - Detects changes across multiple services or shared modules (MEDIUM risk)
3. **Infrastructure Changes** - Flags port, Eureka, env var, Docker, CI file changes (HIGH risk)
4. **Large AI-Style Diffs** - Detects many files, large blocks, repeated patterns (MEDIUM risk)
5. **Test Coverage** - Warns if production code changed without tests (MEDIUM risk)

## Example Output

```
AI SAFETY REPORT
================

Overall Risk: HIGH

Reasons:
- Modified gateway routing configuration
- Changed identity authentication flow
- No test files updated

Affected Areas:
- gateway
- identity
- config

Recommendation:
❌ Block merge
Manual review required.
```

## Development

```bash
# Run locally
python cli.py scan

# Run with custom base
python cli.py scan --base develop
```

## CI Integration

### GitHub Actions

```yaml
- name: AI Safety Check
  run: |
    pip install ai-safety
    ai-safety scan --fail-on high
```

If exit code = 2, the PR will be blocked.

