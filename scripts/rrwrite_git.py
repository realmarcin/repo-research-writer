#!/usr/bin/env python3
"""
RRWrite Git Manager

Manages Git operations for RRWrite manuscript repositories with comprehensive safety features.
Ensures manuscript git operations NEVER affect the tool repository.

Safety Features:
1. Remote URL validation - Prevents operations on rrwrite tool repo
2. Pre-commit hooks - Reject commits containing manuscript/ files in tool repo
3. Explicit --git-dir usage - Always specify exact git directory
4. Warning messages - Loud alerts when operating near tool repo
"""

import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any


class GitSafetyError(Exception):
    """Raised when a git operation would be unsafe."""
    pass


class GitManager:
    """Manage Git operations for RRWrite manuscripts with safety guarantees."""

    # Known RRWrite repository remotes (add more as needed)
    RRWRITE_REMOTE_PATTERNS = [
        "github.com/anthropics/rrwrite",
        "github.com/*/rrwrite",
        "rrwrite.git",
    ]

    def __init__(self, manuscript_dir: Path, auto_commit: bool = True, verbose: bool = True):
        """Initialize Git manager.

        Args:
            manuscript_dir: Path to manuscript directory (must contain .rrwrite/)
            auto_commit: Enable automatic commits after stages
            verbose: Enable warning messages

        Raises:
            GitSafetyError: If manuscript_dir is unsafe
        """
        self.manuscript_dir = Path(manuscript_dir).resolve()
        self.auto_commit = auto_commit
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)

        # SAFETY CHECK 1: Validate this is a manuscript directory
        self._validate_manuscript_directory()

        # SAFETY CHECK 2: Ensure not operating on tool repo
        self._check_not_tool_repo()

        # Git directory path (explicit)
        self.git_dir = self.manuscript_dir / ".git"

    def _validate_manuscript_directory(self):
        """Ensure we're operating on a manuscript directory, not tool repo.

        Raises:
            GitSafetyError: If directory is not a valid manuscript directory
        """
        state_file = self.manuscript_dir / ".rrwrite" / "state.json"

        if not self.manuscript_dir.exists():
            raise GitSafetyError(
                f"Manuscript directory does not exist: {self.manuscript_dir}"
            )

        # Allow initialization if .rrwrite doesn't exist yet (will be created)
        # But must not be the tool directory
        if (self.manuscript_dir / "scripts" / "rrwrite_state_manager.py").exists():
            raise GitSafetyError(
                f"SAFETY VIOLATION: Cannot operate on rrwrite tool directory!\n"
                f"Manuscript directory: {self.manuscript_dir}\n"
                f"This appears to be the RRWrite tool repository.\n"
                f"Manuscripts must be in manuscript/ subdirectory or use --output-dir"
            )

    def _check_not_tool_repo(self):
        """Check if we're about to operate on the tool repository.

        SAFETY FEATURE 4: Warning messages

        Raises:
            GitSafetyError: If this appears to be the tool repo
        """
        # Check for tool repo markers
        tool_markers = [
            "scripts/rrwrite_state_manager.py",
            "scripts/rrwrite-analyze-repo.py",
            ".claude/skills/rrwrite.md"
        ]

        for marker in tool_markers:
            if (self.manuscript_dir / marker).exists():
                raise GitSafetyError(
                    f"\n{'='*70}\n"
                    f"🚨 SAFETY VIOLATION: RRWRITE TOOL REPOSITORY DETECTED 🚨\n"
                    f"{'='*70}\n"
                    f"Directory: {self.manuscript_dir}\n"
                    f"This is the RRWrite tool repository, NOT a manuscript directory!\n\n"
                    f"Manuscripts must be created in:\n"
                    f"  - manuscript/ subdirectory (default), OR\n"
                    f"  - Custom location via --output-dir\n\n"
                    f"Refusing to initialize Git to prevent pollution of tool repo.\n"
                    f"{'='*70}\n"
                )

        if self.verbose:
            self.logger.info(f"✓ Safety check passed: {self.manuscript_dir}")

    def _check_remote_url(self, git_dir: Path) -> None:
        """Check if git remote URL matches RRWrite tool repository.

        SAFETY FEATURE 1: Remote URL validation

        Args:
            git_dir: Path to .git directory to check

        Raises:
            GitSafetyError: If remote URL matches tool repo patterns
        """
        try:
            result = subprocess.run(
                ["git", f"--git-dir={git_dir}", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                remote_url = result.stdout.strip().lower()

                # Check if remote matches tool repo patterns
                for pattern in self.RRWRITE_REMOTE_PATTERNS:
                    if pattern.lower() in remote_url:
                        raise GitSafetyError(
                            f"\n{'='*70}\n"
                            f"🚨 SAFETY VIOLATION: RRWRITE TOOL REMOTE DETECTED 🚨\n"
                            f"{'='*70}\n"
                            f"Git directory: {git_dir}\n"
                            f"Remote URL: {remote_url}\n\n"
                            f"This git repository has the RRWrite tool as its remote!\n"
                            f"Refusing to commit to prevent pollution of tool repository.\n\n"
                            f"If this is a manuscript, remove the rrwrite remote:\n"
                            f"  cd {self.manuscript_dir}\n"
                            f"  git remote remove origin\n"
                            f"{'='*70}\n"
                        )
        except FileNotFoundError:
            # Git not available, skip check
            pass

    def initialize_repository(self) -> bool:
        """Initialize Git repository in manuscript directory.

        SAFETY FEATURE 3: Use explicit --git-dir

        Returns:
            True if initialized, False if already exists

        Raises:
            GitSafetyError: If initialization would be unsafe
        """
        if self.git_dir.exists():
            if self.verbose:
                self.logger.info(f"Git already initialized: {self.manuscript_dir}")

            # SAFETY CHECK: Verify remote is not rrwrite tool
            self._check_remote_url(self.git_dir)
            return False

        # SAFETY: Ensure parent directory exists and is valid
        self.manuscript_dir.mkdir(parents=True, exist_ok=True)

        # Initialize git with explicit directory
        subprocess.run(
            ["git", "init", str(self.manuscript_dir)],
            check=True,
            capture_output=True
        )

        if self.verbose:
            print(f"\n✓ Git initialized in manuscript directory: {self.manuscript_dir}")

        # Create manuscript-specific .gitignore
        self._create_manuscript_gitignore()

        # SAFETY FEATURE 2: Install pre-commit hook to reject manuscript/ files
        # (This applies to the manuscript repo itself, warning against nested repos)
        self._install_safety_hooks()

        # Initial commit using explicit git-dir
        self._git_add([".gitignore"], "Add .gitignore for manuscript artifacts")
        self.commit(
            files=[".gitignore"],
            stage="initialization",
            description="Initialize RRWrite manuscript repository",
            metadata={"safety_checks": "enabled", "rrwrite_managed": "true"}
        )

        return True

    def _create_manuscript_gitignore(self):
        """Create .gitignore for manuscript artifacts."""
        gitignore_content = """# Large binary outputs
*.pdf
*.docx
*.doc
*.pptx

# Temporary caches
.rrwrite/cache/
.rrwrite/tmp/
__pycache__/

# OS files
.DS_Store
Thumbs.db
.DS_Store?
._*
.Spotlight-V100
.Trashes

# Editor files
*.swp
*.swo
*~
.vscode/
.idea/

# Build artifacts
build/
dist/
*.egg-info/
"""
        gitignore_path = self.manuscript_dir / ".gitignore"
        gitignore_path.write_text(gitignore_content)

    def _install_safety_hooks(self):
        """Install git hooks for additional safety.

        SAFETY FEATURE 2: Pre-commit hook
        """
        hooks_dir = self.git_dir / "hooks"
        hooks_dir.mkdir(exist_ok=True)

        pre_commit_hook = hooks_dir / "pre-commit"

        # Hook warns if committing nested .git directories (safety measure)
        hook_content = """#!/bin/bash
# RRWrite Safety Hook
# Warns about potentially problematic commits

# Check for nested .git directories
if git diff --cached --name-only | grep -q ".git/"; then
    echo "⚠️  WARNING: You are committing .git/ directory contents"
    echo "This is unusual and may indicate a mistake."
    echo ""
    echo "Press Enter to continue anyway, or Ctrl+C to cancel"
    read
fi

# Check for very large files (>10MB)
large_files=$(git diff --cached --name-only | while read file; do
    if [ -f "$file" ]; then
        size=$(wc -c < "$file")
        if [ $size -gt 10485760 ]; then
            echo "$file ($size bytes)"
        fi
    fi
done)

if [ -n "$large_files" ]; then
    echo "⚠️  WARNING: Large files detected:"
    echo "$large_files"
    echo ""
    echo "Consider adding to .gitignore or using Git LFS"
    echo "Press Enter to continue anyway, or Ctrl+C to cancel"
    read
fi

exit 0
"""
        pre_commit_hook.write_text(hook_content)
        pre_commit_hook.chmod(0o755)  # Make executable

    def _git_add(self, files: List[str], context: str = ""):
        """Add files to git staging area using explicit git-dir.

        SAFETY FEATURE 3: Explicit --git-dir usage

        Args:
            files: List of file paths relative to manuscript_dir
            context: Context for logging
        """
        # SAFETY CHECK: Verify remote before staging
        if self.git_dir.exists():
            self._check_remote_url(self.git_dir)

        subprocess.run(
            ["git", f"--git-dir={self.git_dir}", f"--work-tree={self.manuscript_dir}", "add"] + files,
            cwd=self.manuscript_dir,
            check=True,
            capture_output=True
        )

        if self.verbose and context:
            self.logger.debug(f"Staged files: {files} ({context})")

    def commit(
        self,
        files: List[str],
        stage: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Commit files with structured message and safety checks.

        SAFETY FEATURES: All 4 safety features applied

        Args:
            files: List of files to commit (relative to manuscript_dir)
            stage: Workflow stage name
            description: Commit description
            metadata: Optional metadata for commit message

        Returns:
            Commit hash if successful, None if auto_commit disabled

        Raises:
            GitSafetyError: If safety checks fail
        """
        if not self.auto_commit:
            return None

        # SAFETY CHECK 1: Verify remote URL
        if self.git_dir.exists():
            self._check_remote_url(self.git_dir)
        else:
            raise GitSafetyError(
                f"Git repository not initialized in {self.manuscript_dir}\n"
                f"Run initialize_repository() first"
            )

        # SAFETY CHECK 2: Pre-commit hook already installed
        # SAFETY FEATURE 4: Warning message
        if self.verbose:
            print(f"\n📝 Committing to manuscript repository: {self.manuscript_dir.name}")

        # Stage files using explicit git-dir (SAFETY FEATURE 3)
        self._git_add(files, f"stage={stage}")

        # Format commit message
        msg = f"[RRWrite] Complete {stage}: {description}\n\n"
        msg += f"Stage: {stage}\n"
        if metadata:
            for key, value in metadata.items():
                msg += f"{key.replace('_', ' ').title()}: {value}\n"
        msg += f"Timestamp: {datetime.now().isoformat()}\n"
        msg += "\nCo-Authored-By: RRWrite <rrwrite@research.ai>"

        # Commit using explicit git-dir (SAFETY FEATURE 3)
        subprocess.run(
            ["git", f"--git-dir={self.git_dir}", f"--work-tree={self.manuscript_dir}", "commit", "-m", msg],
            cwd=self.manuscript_dir,
            check=True,
            capture_output=True
        )

        # Get commit hash using explicit git-dir
        result = subprocess.run(
            ["git", f"--git-dir={self.git_dir}", "rev-parse", "HEAD"],
            cwd=self.manuscript_dir,
            capture_output=True,
            text=True,
            check=True
        )
        commit_hash = result.stdout.strip()

        if self.verbose:
            print(f"✓ Committed: {commit_hash[:7]} - {description}")

        return commit_hash

    def get_current_commit(self) -> Optional[str]:
        """Get current commit hash.

        Returns:
            Commit hash or None if not a git repo
        """
        if not self.git_dir.exists():
            return None

        try:
            result = subprocess.run(
                ["git", f"--git-dir={self.git_dir}", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def get_status(self) -> str:
        """Get git status output.

        Returns:
            Git status string
        """
        if not self.git_dir.exists():
            return "Not a git repository"

        result = subprocess.run(
            ["git", f"--git-dir={self.git_dir}", f"--work-tree={self.manuscript_dir}", "status"],
            capture_output=True,
            text=True,
            check=False
        )
        return result.stdout


def install_tool_repo_protection(tool_repo_path: Path):
    """Install pre-commit hook in the RRWrite tool repository.

    SAFETY FEATURE 2: Pre-commit hook for tool repo

    This hook rejects commits that include manuscript/ files,
    preventing accidental pollution of the tool repository.

    Args:
        tool_repo_path: Path to rrwrite tool repository root
    """
    git_dir = tool_repo_path / ".git"
    if not git_dir.exists():
        print("⚠️  Tool repository is not a git repository - skipping hook installation")
        return

    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)

    pre_commit_hook = hooks_dir / "pre-commit"

    hook_content = """#!/bin/bash
# RRWrite Tool Repository Protection Hook
# Prevents accidental commits of manuscript files to tool repository

# Check if any manuscript/ files are being committed
manuscript_files=$(git diff --cached --name-only | grep "^manuscript/")

if [ -n "$manuscript_files" ]; then
    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    echo "🚨 COMMIT REJECTED: manuscript/ files detected"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
    echo "You are attempting to commit files in manuscript/ to the tool repo:"
    echo "$manuscript_files"
    echo ""
    echo "Manuscripts should have their own git repositories!"
    echo ""
    echo "To fix this:"
    echo "  1. Unstage manuscript files: git reset HEAD manuscript/"
    echo "  2. Commit from manuscript directory: cd manuscript/yourproject/"
    echo "  3. Or verify .gitignore contains: manuscript/"
    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
    exit 1
fi

exit 0
"""

    pre_commit_hook.write_text(hook_content)
    pre_commit_hook.chmod(0o755)  # Make executable

    print(f"✓ Installed tool repository protection hook: {pre_commit_hook}")


def main():
    """CLI interface for Git manager."""
    import argparse

    parser = argparse.ArgumentParser(description="RRWrite Git Manager")
    parser.add_argument("--manuscript-dir", required=True, help="Manuscript directory")
    parser.add_argument("--initialize", action="store_true", help="Initialize git repository")
    parser.add_argument("--status", action="store_true", help="Show git status")
    parser.add_argument("--install-tool-hook", help="Install protection hook in tool repo")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.install_tool_hook:
        install_tool_repo_protection(Path(args.install_tool_hook))
        return

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(message)s'
    )

    try:
        manager = GitManager(
            manuscript_dir=Path(args.manuscript_dir),
            verbose=args.verbose
        )

        if args.initialize:
            manager.initialize_repository()

        if args.status:
            print(manager.get_status())

    except GitSafetyError as e:
        print(f"\n{e}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    import sys
    main()
