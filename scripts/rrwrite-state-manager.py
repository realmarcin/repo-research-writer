#!/usr/bin/env python3
"""
State management library for RRWrite workflow tracking.

Provides functions to initialize, read, and update the workflow state file
stored in manuscript/.rrwrite/state.json.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
import subprocess


class StateManager:
    """Manages the RRWrite workflow state file."""

    def __init__(self, project_root: str = "."):
        """Initialize state manager.

        Args:
            project_root: Root directory of the research project
        """
        self.project_root = Path(project_root).resolve()
        self.manuscript_dir = self.project_root / "manuscript"
        self.state_dir = self.manuscript_dir / ".rrwrite"
        self.state_file = self.state_dir / "state.json"

    def initialize_state(self, project_name: Optional[str] = None,
                        target_journal: Optional[str] = None) -> Dict[str, Any]:
        """Initialize a new state file.

        Args:
            project_name: Name of the research project
            target_journal: Target journal for submission

        Returns:
            Initial state dictionary
        """
        # Create .rrwrite directory if it doesn't exist
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # Get git info if available
        git_info = self._get_git_info()

        # Create initial state structure
        state = {
            "version": "1.0",
            "project_name": project_name or self.project_root.name,
            "target_journal": target_journal,
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),

            "workflow_status": {
                "plan": {
                    "status": "not_started",
                    "file": None,
                    "completed_at": None,
                    "git_commit": None
                },
                "research": {
                    "status": "not_started",
                    "file": None,
                    "completed_at": None,
                    "git_commit": None,
                    "papers_found": 0
                },
                "draft": {
                    "status": "not_started",
                    "sections_completed": [],
                    "sections_pending": [],
                    "last_section": None,
                    "completed_at": None
                },
                "critique": {
                    "status": "not_started",
                    "iterations": []
                },
                "assembly": {
                    "status": "not_started",
                    "file": None,
                    "completed_at": None
                }
            },

            "runs": [],

            "provenance": {
                "input_files": [],
                "verification_runs": []
            },

            "metadata": {
                "rrwrite_version": "1.0.0",
                "git_repo": git_info.get("remote_url"),
                "git_branch": git_info.get("branch")
            }
        }

        # Write state file
        self._write_state(state)
        return state

    def read_state(self) -> Optional[Dict[str, Any]]:
        """Read the current state file.

        Returns:
            State dictionary or None if file doesn't exist
        """
        if not self.state_file.exists():
            return None

        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading state file: {e}")
            return None

    def _write_state(self, state: Dict[str, Any]) -> None:
        """Write state to file.

        Args:
            state: State dictionary to write
        """
        state["last_updated"] = datetime.now().isoformat()

        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def update_workflow_stage(self, stage: str, status: str = "completed",
                            file_path: Optional[str] = None,
                            **kwargs) -> None:
        """Update the status of a workflow stage.

        Args:
            stage: Workflow stage (plan, research, draft, critique, assembly)
            status: Status (not_started, in_progress, completed)
            file_path: Path to output file (relative to project root)
            **kwargs: Additional stage-specific fields
        """
        state = self.read_state()
        if state is None:
            # Initialize if state doesn't exist
            state = self.initialize_state()

        if stage not in state["workflow_status"]:
            raise ValueError(f"Unknown workflow stage: {stage}")

        # Get current git commit
        git_commit = self._get_current_commit()

        # Update stage status
        stage_data = state["workflow_status"][stage]
        stage_data["status"] = status

        if file_path:
            stage_data["file"] = file_path

        if status == "completed":
            stage_data["completed_at"] = datetime.now().isoformat()
            if git_commit:
                stage_data["git_commit"] = git_commit

        # Update stage-specific fields
        for key, value in kwargs.items():
            stage_data[key] = value

        self._write_state(state)

    def add_critique_iteration(self, critique_type: str, version: int,
                              file_path: str, recommendation: str,
                              major_issues: int = 0, minor_issues: int = 0) -> None:
        """Add a critique iteration to the state.

        Args:
            critique_type: Type of critique (outline, literature, section, manuscript)
            version: Critique version number
            file_path: Path to critique file
            recommendation: Critique recommendation
            major_issues: Number of major issues
            minor_issues: Number of minor issues
        """
        state = self.read_state()
        if state is None:
            state = self.initialize_state()

        iteration = {
            "type": critique_type,
            "version": version,
            "file": file_path,
            "completed_at": datetime.now().isoformat(),
            "recommendation": recommendation,
            "major_issues": major_issues,
            "minor_issues": minor_issues
        }

        state["workflow_status"]["critique"]["iterations"].append(iteration)
        state["workflow_status"]["critique"]["status"] = "completed"

        self._write_state(state)

    def add_section_completed(self, section_name: str) -> None:
        """Mark a manuscript section as completed.

        Args:
            section_name: Name of the section (e.g., 'abstract', 'methods')
        """
        state = self.read_state()
        if state is None:
            state = self.initialize_state()

        draft_status = state["workflow_status"]["draft"]

        if section_name not in draft_status["sections_completed"]:
            draft_status["sections_completed"].append(section_name)

        # Remove from pending if present
        if section_name in draft_status["sections_pending"]:
            draft_status["sections_pending"].remove(section_name)

        draft_status["last_section"] = section_name
        draft_status["completed_at"] = datetime.now().isoformat()

        # Update status
        if len(draft_status["sections_completed"]) > 0:
            draft_status["status"] = "in_progress"

        self._write_state(state)

    def add_run(self, run_id: str, target_journal: Optional[str] = None,
                outputs: Optional[Dict[str, str]] = None) -> None:
        """Record a workflow run.

        Args:
            run_id: Unique run identifier (e.g., timestamped directory name)
            target_journal: Target journal for this run
            outputs: Dictionary of output file paths
        """
        state = self.read_state()
        if state is None:
            state = self.initialize_state()

        run = {
            "run_id": run_id,
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "target_journal": target_journal or state.get("target_journal"),
            "git_commit": self._get_current_commit(),
            "outputs": outputs or {}
        }

        state["runs"].append(run)
        self._write_state(state)

    def complete_run(self, run_id: str, outputs: Optional[Dict[str, str]] = None) -> None:
        """Mark a workflow run as completed.

        Args:
            run_id: Run identifier
            outputs: Final output file paths
        """
        state = self.read_state()
        if state is None:
            return

        for run in state["runs"]:
            if run["run_id"] == run_id:
                run["completed_at"] = datetime.now().isoformat()
                if outputs:
                    run["outputs"].update(outputs)
                break

        self._write_state(state)

    def record_verification(self, script: str, file_path: str,
                          column: str, operation: str, result: Any) -> None:
        """Record a verification/validation run.

        Args:
            script: Name of verification script
            file_path: Path to file that was verified
            column: Column name (for data files)
            operation: Operation performed (mean, count, etc.)
            result: Result of verification
        """
        state = self.read_state()
        if state is None:
            state = self.initialize_state()

        verification = {
            "timestamp": datetime.now().isoformat(),
            "script": script,
            "file": file_path,
            "column": column,
            "operation": operation,
            "result": result
        }

        state["provenance"]["verification_runs"].append(verification)
        self._write_state(state)

    def get_next_critique_version(self, critique_type: str) -> int:
        """Get the next version number for a critique.

        Args:
            critique_type: Type of critique

        Returns:
            Next version number
        """
        state = self.read_state()
        if state is None:
            return 1

        iterations = state["workflow_status"]["critique"]["iterations"]
        matching = [it for it in iterations if it["type"] == critique_type]

        if not matching:
            return 1

        return max(it["version"] for it in matching) + 1

    def _get_git_info(self) -> Dict[str, Optional[str]]:
        """Get git repository information.

        Returns:
            Dictionary with branch and remote_url
        """
        info = {"branch": None, "remote_url": None}

        try:
            # Get current branch
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                info["branch"] = result.stdout.strip()

            # Get remote URL
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                info["remote_url"] = result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return info

    def _get_current_commit(self) -> Optional[str]:
        """Get current git commit hash.

        Returns:
            Short commit hash or None
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return None

    def check_uncommitted_changes(self) -> bool:
        """Check if there are uncommitted changes in the manuscript directory.

        Returns:
            True if there are uncommitted changes, False otherwise
        """
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain", "manuscript/"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return bool(result.stdout.strip())
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return False

    def warn_uncommitted_changes(self, file_path: str) -> None:
        """Warn user if there are uncommitted changes before overwriting.

        Args:
            file_path: File that will be overwritten
        """
        if not self.check_uncommitted_changes():
            return

        file_rel_path = Path(file_path).relative_to(self.project_root)
        print()
        print("⚠️  Warning: Uncommitted changes detected")
        print()
        print(f"You have uncommitted changes in manuscript/")
        print(f"About to overwrite/modify: {file_rel_path}")
        print()
        print("Recommendation:")
        print("  git add manuscript/")
        print(f'  git commit -m "Save before regenerating {file_rel_path.name}"')
        print()
        print("Or create an automatic checkpoint:")
        print("  (Previous versions can be recovered from Git history)")
        print()

    def create_checkpoint(self, message: str) -> bool:
        """Create a Git checkpoint commit.

        Args:
            message: Commit message

        Returns:
            True if checkpoint created successfully
        """
        try:
            # Check if there are changes to commit
            result = subprocess.run(
                ["git", "status", "--porcelain", "manuscript/"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0 or not result.stdout.strip():
                # No changes to commit
                return False

            # Stage manuscript directory changes
            subprocess.run(
                ["git", "add", "manuscript/"],
                cwd=self.project_root,
                check=True,
                timeout=5
            )

            # Create commit
            subprocess.run(
                ["git", "commit", "-m", f"[RRWrite Checkpoint] {message}"],
                cwd=self.project_root,
                check=True,
                capture_output=True,
                timeout=5
            )

            print(f"✓ Created Git checkpoint: {message}")
            return True

        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return False

    def get_file_history(self, file_path: str, limit: int = 5) -> list:
        """Get Git history for a file.

        Args:
            file_path: Path to file (relative to project root)
            limit: Number of commits to retrieve

        Returns:
            List of commit dictionaries with hash, date, message
        """
        history = []
        try:
            result = subprocess.run(
                ["git", "log", f"-{limit}", "--pretty=format:%h|%ai|%s", "--", file_path],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0 and result.stdout:
                for line in result.stdout.strip().split('\n'):
                    parts = line.split('|', 2)
                    if len(parts) == 3:
                        history.append({
                            "hash": parts[0],
                            "date": parts[1][:16],  # YYYY-MM-DD HH:MM
                            "message": parts[2]
                        })
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return history


def main():
    """Command-line interface for state manager."""
    import argparse

    parser = argparse.ArgumentParser(
        description="RRWrite state management utility"
    )
    parser.add_argument(
        "action",
        choices=["init", "show"],
        help="Action to perform"
    )
    parser.add_argument(
        "--project-name",
        help="Project name (for init)"
    )
    parser.add_argument(
        "--journal",
        help="Target journal (for init)"
    )

    args = parser.parse_args()

    manager = StateManager()

    if args.action == "init":
        state = manager.initialize_state(
            project_name=args.project_name,
            target_journal=args.journal
        )
        print(f"✓ State file initialized: {manager.state_file}")
        print(f"  Project: {state['project_name']}")
        if state['target_journal']:
            print(f"  Journal: {state['target_journal']}")

    elif args.action == "show":
        state = manager.read_state()
        if state is None:
            print("No state file found. Run 'rrwrite-state-manager.py init' first.")
        else:
            print(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()
