# GitHub Actions Setup for Sentra Enforcement

This guide explains how to set up Sentra with GitHub Actions to enforce policy checks that **cannot be bypassed**.

## ✅ What This Setup Provides

- **GitHub Desktop users** ❌ cannot bypass Sentra
- **CLI users** ❌ cannot bypass Sentra  
- **Force-push** ❌ does nothing (CI re-runs)
- **Only CI + Sentra** decides merge eligibility

## Step 1: GitHub Actions Workflow

The workflow file `.github/workflows/sentra.yml` is already created. It:

- Runs on every PR (opened, synchronized, reopened)
- Runs on every push to protected branches (`main`, `release/*`)
- Installs Sentra
- Runs `sentra scan --json`
- Enforces decision: **BLOCK = CI failure** (exit code 1)

## Step 2: Configure Branch Protection (REQUIRED)

This is the **critical step** that makes enforcement non-bypassable.

### Go to Repository Settings

1. Navigate to: **Repository → Settings → Branches → Branch protection rules**
2. Create or edit rule for `main` (and `release/*` if needed)

### Enable These Settings

✅ **Require a pull request before merging**
- Required number of approvals: 1 (or your preference)

✅ **Require status checks to pass before merging**
- ✅ Select **"Sentra Policy Check"** from the list
- ✅ **Require branches to be up to date before merging**

✅ **(Optional but recommended) Include administrators**
- This ensures even admins cannot bypass

### Disable These Settings

❌ **Allow force pushes**
❌ **Allow deletions**

## Step 3: Configure GitHub Secret

1. Go to: **Repository → Settings → Secrets and variables → Actions**
2. Click **"New repository secret"**
3. Name: `SENTRA_LICENSE_KEY`
4. Value: Your Sentra Pro license key (or leave empty for Free tier)
5. Click **"Add secret"**

### License Tiers

- **Free tier** (no `SENTRA_LICENSE_KEY`):
  - BLOCK decisions are downgraded to WARN
  - CI passes (exit code 0)
  - Merge allowed

- **Pro tier** (with `SENTRA_LICENSE_KEY`):
  - BLOCK decisions are enforced
  - CI fails (exit code 1)
  - Merge blocked

## Step 4: Verify Enforcement

Test the setup to ensure it works:

### Test Scenario 1: GitHub Desktop User
1. User commits risky code locally ✅ Allowed
2. User pushes to branch ✅ Allowed
3. User opens PR ✅ Allowed
4. Sentra runs ✅ Automatic
5. Decision = BLOCK (Pro tier) ❌ CI fails
6. Merge button 🔒 **Disabled** (cannot merge)

### Test Scenario 2: Force Push
1. User force-pushes ✅ Allowed (GitHub behavior)
2. CI re-runs ✅ Automatic
3. Sentra BLOCK ❌ Merge still blocked

### Test Scenario 3: CLI User
1. User pushes via CLI ✅ Allowed
2. Sentra runs ✅ Automatic
3. BLOCK decision ❌ CI fails, merge blocked

## How It Works

### Enforcement Flow

```
Developer Action
    ↓
GitHub Actions Triggered
    ↓
Sentra Workflow Runs
    ↓
sentra scan --json
    ↓
Decision Evaluation
    ↓
BLOCK? → Exit Code 1 → CI Fails
WARN/ALLOW? → Exit Code 0 → CI Passes
    ↓
Branch Protection Checks Status
    ↓
Status = Failed? → Merge Button Disabled
Status = Passed? → Merge Allowed
```

### Why This Cannot Be Bypassed

1. **GitHub Actions runs in GitHub's infrastructure** - not on developer machines
2. **Branch protection is enforced by GitHub** - not by local git hooks
3. **Status checks are required** - GitHub won't allow merge if check fails
4. **Force-push doesn't bypass** - CI re-runs automatically
5. **Admins included** - even repository admins cannot bypass (if enabled)

This is the same mechanism GitHub uses to enforce its own rules.

## Pro Tier vs Free Tier Behavior

### Free Tier (No License Key)

```json
{
  "decision": "WARN",  // BLOCK downgraded to WARN
  "metadata": {
    "license_tier": "free",
    "original_decision": "BLOCK"
  }
}
```

- Exit code: `0` (CI passes)
- Merge: ✅ Allowed
- PR comment shows upgrade notice

### Pro Tier (With License Key)

```json
{
  "decision": "BLOCK",
  "metadata": {
    "license_tier": "pro"
  }
}
```

- Exit code: `1` (CI fails)
- Merge: ❌ Blocked
- PR comment shows blocking message

## Troubleshooting

### Workflow Not Running

- Check that `.github/workflows/sentra.yml` exists
- Verify file is committed to the repository
- Check GitHub Actions tab for errors

### Status Check Not Appearing

- Ensure workflow runs successfully at least once
- Check that job name matches: `sentra`
- Verify branch protection rule is configured correctly

### CI Passes When It Should Fail

- Check `SENTRA_LICENSE_KEY` secret is set (for Pro tier)
- Verify `sentra scan` command is working
- Check workflow logs for Sentra output

### Merge Still Allowed After BLOCK

- Verify branch protection rule is active
- Check that "Require status checks" is enabled
- Ensure "Sentra Policy Check" is selected in required checks
- Verify workflow completed (not skipped)

## Next Steps

1. ✅ Workflow file created (`.github/workflows/sentra.yml`)
2. ⏳ Configure branch protection (manual step in GitHub UI)
3. ⏳ Add `SENTRA_LICENSE_KEY` secret (for Pro tier)
4. ⏳ Test with a PR to verify enforcement

## Summary

✅ **CI runs on PR + push**
✅ **Sentra evaluates decision**
✅ **BLOCK → CI fails (Pro tier)**
✅ **Branch protection blocks merge**
✅ **GitHub Desktop cannot bypass**
✅ **Force-push does nothing**

This is **real enforcement, not theater**.

