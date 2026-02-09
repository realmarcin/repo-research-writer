# RRWrite Git Architecture

## Overview

RRWrite uses a **clean separation architecture** to enable safe Git version control for manuscripts while keeping the tool repository unpolluted.

### Key Principle
**Tool and manuscripts use completely separate Git repositories.**

```
rrwrite/                          # Tool repository
├── .git/                         # ← Tool's git (for rrwrite code)
├── scripts/
├── templates/
├── example/                      # Example manuscripts (committed to tool repo)
└── manuscript/                   # User workspace (IGNORED by tool git)
    └── myproject_v1/             # User's manuscript
        └── .git/                 # ← Manuscript's git (separate repository)
```

---

## The Problem We Solve

**User Workflow:**
1. Clone rrwrite tool: `git clone https://github.com/user/rrwrite.git`
2. Run rrwrite from within that clone: `cd rrwrite && ./scripts/rrwrite.py ...`
3. Output goes to `manuscript/` directory inside the clone
4. **Risk:** User accidentally commits manuscripts to the tool repository

**Our Solution:**
- `manuscript/` is gitignored in tool repo
- Each manuscript gets its own `.git/` repository
- Four layers of safety checks prevent pollution

---

## Architecture Components

### 1. Directory Structure

```
rrwrite/                                  # Tool repo (users clone this)
├── .git/                                 # Tool repository's git
│   └── hooks/
│       └── pre-commit                    # Rejects manuscript/ commits
├── .gitignore                            # Ignores manuscript/
├── scripts/
│   ├── rrwrite_state_manager.py          # Initializes manuscript git
│   └── rrwrite_git.py                    # Git manager with safety checks
├── example/                              # Example manuscripts (tracked)
│   └── data_sheets_schema_v1/
└── manuscript/                           # User workspace (UNTRACKED)
    ├── project_v1/                       # Manuscript 1
    │   ├── .git/                         # Separate git repo
    │   ├── .rrwrite/
    │   │   └── state.json
    │   └── sections/
    └── project_v2/                       # Manuscript 2
        └── .git/                         # Another separate repo
```

### 2. Git Repository Separation

**Tool Repository (`rrwrite/.git/`):**
- Managed by RRWrite developers
- Users pull updates: `git pull`
- Contains: scripts, templates, documentation
- **Does NOT contain** user manuscripts

**Manuscript Repositories (`manuscript/project_v1/.git/`):**
- Managed by individual users
- One `.git/` per manuscript project
- Contains: manuscript sections, literature, evidence
- Completely independent history
- Users can push to their own remotes

**How Git Knows Which Repo:**
Git searches upward from your current directory for the first `.git/` folder:
- In `rrwrite/`: Uses `rrwrite/.git/` → tool repo
- In `manuscript/project_v1/`: Uses `manuscript/project_v1/.git/` → manuscript repo

---

## Four Layers of Safety

### Layer 1: Remote URL Validation

**What:** Check if git remote URL matches RRWrite tool repository patterns
**When:** Before every commit operation
**Protection:** Prevents committing if repository has rrwrite as remote

```python
# In rrwrite_git.py
RRWRITE_REMOTE_PATTERNS = [
    "github.com/anthropics/rrwrite",
    "github.com/*/rrwrite",
    "rrwrite.git",
]
```

**Error Example:**
```
🚨 SAFETY VIOLATION: RRWRITE TOOL REMOTE DETECTED 🚨
Remote URL: https://github.com/user/rrwrite.git
Refusing to commit to prevent pollution of tool repository.
```

### Layer 2: Pre-Commit Hooks

**Tool Repository Hook:**
Installed in `rrwrite/.git/hooks/pre-commit`

```bash
# Install with:
python scripts/rrwrite_state_manager.py --install-tool-protection
```

**What it does:**
- Rejects commits containing `manuscript/` files
- Alerts user if manuscript files are staged
- Provides instructions to fix

**Error Example:**
```
🚨 COMMIT REJECTED: manuscript/ files detected
You are attempting to commit files in manuscript/ to the tool repo

To fix this:
  1. Unstage manuscript files: git reset HEAD manuscript/
  2. Commit from manuscript directory: cd manuscript/yourproject/
```

**Manuscript Repository Hook:**
Installed automatically in each manuscript's `.git/hooks/pre-commit`

**What it does:**
- Warns about nested `.git/` directories
- Alerts about large files (>10MB)
- Suggests using Git LFS for large files

### Layer 3: Explicit --git-dir Usage

**What:** All git commands explicitly specify which repository to operate on
**Why:** Prevents accidents if current directory is ambiguous

```python
# Instead of:
subprocess.run(["git", "commit", "-m", "message"], cwd=manuscript_dir)

# We use:
subprocess.run([
    "git",
    f"--git-dir={manuscript_dir}/.git",
    f"--work-tree={manuscript_dir}",
    "commit", "-m", "message"
], cwd=manuscript_dir)
```

**Protection:** Even if code is run from wrong directory, git operations target correct repo

### Layer 4: Warning Messages

**What:** Loud, visible warnings when operating near boundaries
**When:** Git initialization, commits, safety check failures

**Example:**
```
🚨 SAFETY VIOLATION: RRWRITE TOOL REPOSITORY DETECTED 🚨
Directory: /Users/you/rrwrite
This is the RRWrite tool repository, NOT a manuscript directory!

Manuscripts must be created in:
  - manuscript/ subdirectory (default), OR
  - Custom location via --output-dir
```

---

## User Workflows

### Workflow 1: Default Usage

```bash
# Clone rrwrite tool (ONE TIME)
git clone https://github.com/user/rrwrite.git
cd rrwrite

# Install tool protection hook (RECOMMENDED)
python scripts/rrwrite_state_manager.py --install-tool-protection

# Run rrwrite (creates manuscript/repo_v1/ with its own .git/)
./scripts/rrwrite.py --repo /path/to/research-repo

# Manuscript now has version control
cd manuscript/repo_v1
git log  # Shows manuscript-specific commits

# Push manuscript to your own repository
git remote add origin https://github.com/you/my-manuscript.git
git push -u origin main

# Pull tool updates (from rrwrite directory)
cd ../..
git pull  # Updates RRWrite tool only, not manuscripts
```

### Workflow 2: Custom Output Location

```bash
# Clone rrwrite
git clone https://github.com/user/rrwrite.git

# Run rrwrite with custom output (outside rrwrite directory)
./rrwrite/scripts/rrwrite.py \
    --repo /path/to/research-repo \
    --output-dir ~/my-manuscripts/project_v1

# Manuscript is completely separate from tool
cd ~/my-manuscripts/project_v1
git log  # Independent repository
git remote add origin https://github.com/you/manuscript.git
git push
```

### Workflow 3: Multiple Manuscripts

```bash
# Create first manuscript
./scripts/rrwrite.py --repo /path/to/repo1
# Creates: manuscript/repo1_v1/.git/

# Create second manuscript
./scripts/rrwrite.py --repo /path/to/repo2
# Creates: manuscript/repo2_v1/.git/

# Each has independent git history
cd manuscript/repo1_v1 && git log  # Shows repo1 history
cd ../repo2_v1 && git log          # Shows repo2 history
```

---

## Safety Verification

### Test 1: Tool Repository Protection

```bash
cd rrwrite

# Verify manuscript/ is ignored
git status | grep manuscript
# Should show nothing

# Try to add manuscript files (should fail with hook)
git add manuscript/
git commit -m "Test"
# Should be rejected by pre-commit hook
```

### Test 2: Separate Histories

```bash
# Check tool repo history
cd rrwrite
git log --oneline
# Shows: rrwrite tool commits

# Check manuscript repo history
cd manuscript/myproject_v1
git log --oneline
# Shows: manuscript commits (completely different)
```

### Test 3: Remote URL Safety

```bash
# In manuscript directory
cd manuscript/myproject_v1

# Try to add rrwrite remote (should fail)
git remote add origin https://github.com/user/rrwrite.git
git commit -m "Test"
# Should be rejected: "RRWRITE TOOL REMOTE DETECTED"
```

---

## Troubleshooting

### "Git repository not initialized"

**Cause:** Git initialization failed or was disabled
**Fix:**
```bash
cd manuscript/yourproject
python ../../scripts/rrwrite_git.py \
    --manuscript-dir . \
    --initialize \
    --verbose
```

### "SAFETY VIOLATION: RRWRITE TOOL REPOSITORY DETECTED"

**Cause:** Trying to initialize git in tool directory
**Fix:**
```bash
# Don't run rrwrite from tool root with output="."
# Instead:
./scripts/rrwrite.py --repo /path/to/research --output-dir manuscript/myproject
```

### "Commit rejected: manuscript/ files detected"

**Cause:** Pre-commit hook detected manuscript files in tool repo commit
**Fix:**
```bash
# Unstage manuscript files
git reset HEAD manuscript/

# Commit from manuscript directory instead
cd manuscript/yourproject
git add .
git commit -m "Your manuscript changes"
```

### "I want to disable Git for manuscripts"

**Solution:**
```bash
./scripts/rrwrite.py --repo /path/to/research --no-git
```

---

## Advanced Usage

### Manual Git Initialization

```bash
cd manuscript/myproject_v1
python ../../scripts/rrwrite_git.py --manuscript-dir . --initialize
```

### Check Git Status

```bash
python ../../scripts/rrwrite_git.py --manuscript-dir manuscript/myproject_v1 --status
```

### Custom Commit from Python

```python
from pathlib import Path
from rrwrite_git import GitManager

manager = GitManager(manuscript_dir=Path("manuscript/myproject_v1"))
manager.commit(
    files=["introduction.md", "methods.md"],
    stage="drafting",
    description="Complete introduction and methods sections",
    metadata={"word_count": 3500, "sections": 2}
)
```

---

## Design Rationale

### Why Not Git Worktrees?

**Considered:** Use git worktrees to manage manuscripts
**Rejected:** Too complex for users, requires advanced Git knowledge

### Why Not Separate Output Directory by Default?

**Considered:** Make users specify output directory outside rrwrite
**Rejected:** Adds friction, breaks "works out of the box" principle

### Why Not Forks?

**Considered:** Users fork rrwrite, commit manuscripts to their fork
**Rejected:**
- Pollutes fork history with unrelated manuscript commits
- Makes pulling tool updates difficult
- Confuses tool updates with manuscript updates

### Why This Architecture?

**Chosen:** Separate `.git/` repositories with safety layers
**Benefits:**
- ✅ Works out of the box (default `manuscript/` location)
- ✅ Clear separation (tool vs manuscript repos)
- ✅ Easy updates (pull tool updates without affecting manuscripts)
- ✅ Flexible (supports custom output locations)
- ✅ Safe (four layers prevent accidents)
- ✅ Standard Git (no advanced features required)

---

## Implementation Details

### Files Modified

1. **`.gitignore`** - Ignore `manuscript/` in tool repo
2. **`scripts/rrwrite_git.py`** - Git manager with safety features
3. **`scripts/rrwrite_state_manager.py`** - Initialize manuscript git, integrate GitManager
4. **`docs/GIT_ARCHITECTURE.md`** - This file

### Safety Features Implementation

| Feature | Location | Code |
|---------|----------|------|
| Remote URL validation | `rrwrite_git.py:_check_remote_url()` | Checks remote against patterns |
| Pre-commit hook (tool) | `rrwrite_git.py:install_tool_repo_protection()` | Bash hook rejecting manuscript/ |
| Pre-commit hook (manuscript) | `rrwrite_git.py:_install_safety_hooks()` | Bash hook warning about issues |
| Explicit --git-dir | `rrwrite_git.py:commit()`, `_git_add()` | Uses `--git-dir` flag |
| Warning messages | `rrwrite_git.py:_check_not_tool_repo()` | Prints loud warnings |

---

## FAQ

**Q: Can I commit manuscripts to the tool repository?**
A: Technically yes if you deliberately circumvent safety features, but you really shouldn't. Manuscripts should have their own repos.

**Q: What if I want to contribute an example manuscript to rrwrite?**
A: Put it in `example/` directory, not `manuscript/`. The `example/` directory is tracked by tool git.

**Q: Can I use my existing git repository for manuscripts?**
A: Yes! Use `--output-dir` to point to your existing repo. RRWrite will detect the existing `.git/` and use it.

**Q: Do I need to fork rrwrite?**
A: No! Clone the main rrwrite repo directly. Manuscripts get their own separate git repos.

**Q: How do I share my manuscript with collaborators?**
A: Push your manuscript repo to GitHub:
```bash
cd manuscript/myproject_v1
git remote add origin https://github.com/you/manuscript.git
git push -u origin main
```

**Q: What happens when I update rrwrite?**
A: Pull updates in the tool directory:
```bash
cd rrwrite
git pull
```
Your manuscripts in `manuscript/` are unaffected (they're gitignored).

---

## Summary

RRWrite's Git architecture provides:
- ✅ **Safety:** Four layers prevent accidental commits to tool repo
- ✅ **Separation:** Tool and manuscripts have independent histories
- ✅ **Simplicity:** Works out of the box with default settings
- ✅ **Flexibility:** Custom output locations supported
- ✅ **Version Control:** Every manuscript gets automatic git tracking
- ✅ **Collaboration:** Push manuscripts to your own remotes

The architecture ensures users can safely version control their manuscripts while working from within a clone of the rrwrite tool repository.
