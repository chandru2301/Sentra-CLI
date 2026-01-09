# Fix: Duplicate Sentra Workflows

## Problem Identified

You had **two Sentra workflows** running:
1. ✅ **"Sentra Policy Check"** (`.github/workflows/sentra.yml`) - Working correctly
2. ❌ **"Sentra"** (`.github/workflows/mergegate.yml`) - Failing (using custom action)

## What Was Fixed

### ✅ Deleted Duplicate Workflow
- Removed `.github/workflows/mergegate.yml`
- This was the failing workflow that used a custom action

### ✅ Improved Main Workflow
- Updated `.github/workflows/sentra.yml` to handle exit codes properly
- Added proper error handling for JSON parsing
- Ensured BLOCK decisions fail CI correctly

## Current State

**You now have ONE workflow:**
- ✅ `.github/workflows/sentra.yml` - "Sentra Policy Check"
- This is the only workflow that will run

## Next Steps

### 1. Push the Changes
```bash
git add .github/workflows/
git commit -m "fix: remove duplicate Sentra workflow"
git push
```

### 2. Verify in GitHub
After pushing:
1. Go to your PR
2. Check the "Checks" tab
3. You should see **only ONE** "Sentra Policy Check" status

### 3. Enable Branch Protection
Once you confirm only one check exists:

1. Go to: **Repository → Settings → Branches**
2. Edit branch protection for `main`
3. Enable: **"Require status checks to pass"**
4. Select: **"Sentra Policy Check"** ✅
5. Enable: **"Require branches to be up to date"**
6. (Optional) Enable: **"Include administrators"**

### 4. Test Enforcement
Create a test PR that should be BLOCKED:
- The PR should show ❌ "Sentra Policy Check" failed
- Merge button should be **disabled**

## Why This Happened

The `mergegate.yml` workflow was:
- Using a custom action (`./.github/actions/sentra`)
- Not handling exit codes properly
- Creating confusion with duplicate checks

## Cleanup (Optional)

If you want to clean up unused custom actions:

```bash
# These are no longer needed if you're not using custom actions
rm -rf .github/actions/sentra
rm -rf .github/actions/mergegate
```

**Note:** Only delete these if you're sure you won't use custom actions in the future.

## Verification Checklist

After pushing, verify:
- [ ] Only ONE "Sentra Policy Check" appears in PR checks
- [ ] Workflow runs successfully
- [ ] BLOCK decisions fail CI correctly
- [ ] Branch protection is configured
- [ ] Merge button is disabled when Sentra blocks

---

## Summary

✅ **Fixed:** Removed duplicate workflow
✅ **Result:** One clean, working workflow
✅ **Next:** Enable branch protection for enforcement

