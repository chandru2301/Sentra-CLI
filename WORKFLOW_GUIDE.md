# Sentra Workflow Guide - When & Where to Use

This guide explains **exactly when and where** you can use Sentra in your development workflow.

## 🎯 Quick Answer

**Sentra can be used at ANY of these stages:**
1. ✅ **After `git add .`** (staged changes)
2. ✅ **After `git commit`** (committed changes)
3. ✅ **Before/After creating PR** (branch comparison)
4. ✅ **In CI/CD pipelines** (automated enforcement)

---

## 📊 Visual Workflow

```
Developer Workflow:
┌─────────────────────────────────────────────────────────────┐
│ 1. Make Changes                                              │
│    $ git add .                                               │
│    ✅ sentra scan  ← WORKS HERE (staged changes)             │
└─────────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Commit Changes                                            │
│    $ git commit -m "feat: add feature"                       │
│    ✅ sentra scan  ← WORKS HERE (committed vs base)         │
└─────────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Push to Branch                                            │
│    $ git push origin feature-branch                         │
│    ✅ sentra scan  ← WORKS HERE (branch vs main)             │
└─────────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Create Pull Request                                       │
│    GitHub/GitLab UI                                          │
│    ✅ CI runs sentra scan  ← AUTOMATIC (enforced)            │
└─────────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Merge Decision                                            │
│    ✅ CI blocks if BLOCK decision                           │
│    ✅ Merge allowed if ALLOW/WARN                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 Detailed Usage Scenarios

### Scenario 1: After `git add .` (Staged Changes)

**When:** You've staged changes but haven't committed yet.

**How it works:**
- Sentra tries to compare `main..HEAD` first
- If that fails (no commits yet), it falls back to `git diff --cached`
- Analyzes your **staged changes**

**Example:**
```bash
# Make some changes
echo "code" > new_file.py
git add .

# Check before committing
sentra scan
# ✅ Works! Analyzes staged changes
```

**Use case:** Quick check before committing to catch issues early.

---

### Scenario 2: After `git commit` (Committed Changes)

**When:** You've committed changes to your branch.

**How it works:**
- Compares your branch (`HEAD`) against base branch (`main` by default)
- Uses: `git diff main..HEAD`
- Analyzes **all committed changes** in your branch

**Example:**
```bash
# Commit your changes
git commit -m "feat: add authentication"

# Check what will be in PR
sentra scan
# ✅ Works! Analyzes committed changes vs main
```

**Use case:** Verify what will be included when you create a PR.

---

### Scenario 3: Before Creating PR (Pre-PR Check)

**When:** You want to check before opening a PR.

**How it works:**
- Compares your feature branch against target branch
- Shows what Sentra will evaluate in CI

**Example:**
```bash
# On feature branch
git checkout feature/auth
sentra scan --base main
# ✅ Shows decision that CI will see
```

**Use case:** Fix issues before PR to avoid CI failures.

---

### Scenario 4: In CI/CD (Automated Enforcement)

**When:** PR is created or updated.

**How it works:**
- CI automatically runs `sentra scan`
- Compares PR branch against base branch
- **BLOCK decision = CI fails = Merge blocked**

**Example (GitHub Actions):**
```yaml
- name: Run Sentra scan
  run: sentra scan --json
```

**Use case:** **Enforcement** - prevents risky code from merging.

---

## 🛠️ How Sentra Detects Changes

### Method 1: Branch Comparison (Primary)
```bash
git diff main..HEAD
```
- Used when you have commits on your branch
- Compares entire branch against base
- **Most common in PRs and CI**

### Method 2: Staged Changes (Fallback)
```bash
git diff --cached
```
- Used when branch comparison fails
- Shows only staged (uncommitted) changes
- **Useful for pre-commit checks**

---

## 📋 Complete Usage Matrix

| Stage | Command | What It Analyzes | Exit Code | Use Case |
|-------|---------|------------------|-----------|----------|
| **After `git add`** | `sentra scan` | Staged changes | 0/1 | Pre-commit check |
| **After `git commit`** | `sentra scan` | Committed changes | 0/1 | Pre-PR check |
| **Before PR** | `sentra scan --base main` | Branch vs base | 0/1 | Verify before PR |
| **In CI (PR)** | `sentra scan --json` | PR changes | 0/1 | **Enforcement** |
| **In CI (Push)** | `sentra scan --json` | Push changes | 0/1 | **Enforcement** |

---

## 🎯 Recommended Workflow

### For Developers (Local)

```bash
# 1. Make changes
git add .

# 2. Quick check (optional but recommended)
sentra scan
# If BLOCK, fix issues before committing

# 3. Commit
git commit -m "feat: add feature"

# 4. Verify before pushing
sentra scan
# Ensure it's safe to push

# 5. Push and create PR
git push origin feature-branch
```

### For CI/CD (Automated)

```yaml
# .github/workflows/sentra.yml
- name: Run Sentra
  run: |
    sentra scan --json > result.json
    # CI fails if BLOCK (exit code 1)
```

---

## 🔒 Enforcement Levels

### Level 1: Local (Developer)
- **When:** After `git add` or `git commit`
- **Enforcement:** Manual (developer sees output)
- **Can bypass:** ✅ Yes (developer can ignore)
- **Use case:** Early feedback

### Level 2: Pre-Push Hook (Optional)
- **When:** Before `git push`
- **Enforcement:** Blocks push if BLOCK
- **Can bypass:** ⚠️ Yes (with `--no-verify`)
- **Use case:** Catch issues before PR

### Level 3: CI/CD (Recommended)
- **When:** On PR creation/update
- **Enforcement:** Blocks merge if BLOCK
- **Can bypass:** ❌ No (with branch protection)
- **Use case:** **Real enforcement**

---

## 💡 Best Practices

### ✅ DO:
1. **Run locally before committing** - Catch issues early
2. **Run before creating PR** - Avoid CI failures
3. **Use in CI** - Enforce policies automatically
4. **Use `--json` in CI** - Machine-readable output

### ❌ DON'T:
1. **Don't rely only on local checks** - Can be bypassed
2. **Don't skip CI integration** - This is where enforcement happens
3. **Don't ignore BLOCK decisions** - They indicate real risks

---

## 🚀 Quick Examples

### Example 1: Pre-Commit Check
```bash
# Stage changes
git add src/auth/service.py

# Check before committing
sentra scan
# Output: BLOCK - Sensitive file detected
# → Fix issues, then commit
```

### Example 2: Pre-PR Check
```bash
# On feature branch with commits
git checkout feature/new-api
sentra scan --base main
# Output: WARN - Cross-service changes detected
# → Review, then create PR
```

### Example 3: CI Enforcement
```yaml
# GitHub Actions
- name: Sentra Check
  run: sentra scan --json
  # If BLOCK → CI fails → Merge blocked
```

---

## 📝 Summary

**Sentra works at ANY stage:**
- ✅ Staged changes (`git add`)
- ✅ Committed changes (`git commit`)
- ✅ Branch comparison (PR)
- ✅ CI/CD (automated)

**But enforcement only happens in CI with branch protection.**

**Recommendation:**
- Use locally for **feedback**
- Use in CI for **enforcement**

---

## 🔗 Related Files

- `.github/workflows/sentra.yml` - GitHub Actions workflow
- `.gitlab-ci.yml` - GitLab CI configuration
- `Jenkinsfile` - Jenkins pipeline
- `GITHUB_SETUP.md` - Complete CI setup guide

