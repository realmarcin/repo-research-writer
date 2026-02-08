#!/usr/bin/env python3
"""
RRWrite Status Dashboard

Displays current status of the RRWrite manuscript generation workflow.
Shows progress through planning, assessment, research, drafting, and critique phases.

Usage:
    rrwrite-status.py [--output-dir DIR] [--verbose] [--json]
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any

# Import state manager from same directory
try:
    from rrwrite_state_manager import StateManager
except ImportError:
    # If running as script, add to path
    script_dir = Path(__file__).parent
    sys.path.insert(0, str(script_dir))
    from rrwrite_state_manager import StateManager


def get_status_icon(status: str) -> str:
    """Get icon for status."""
    icons = {
        "not_started": "⏹",
        "in_progress": "▶",
        "completed": "✓",
        "failed": "✗"
    }
    return icons.get(status, "?")


def get_status_color(status: str) -> str:
    """Get ANSI color code for status (for terminal display)."""
    colors = {
        "not_started": "\033[90m",  # Gray
        "in_progress": "\033[93m",  # Yellow
        "completed": "\033[92m",    # Green
        "failed": "\033[91m"         # Red
    }
    reset = "\033[0m"
    return colors.get(status, "") + status.upper() + reset


def format_progress_bar(completed: int, total: int, width: int = 30) -> str:
    """Format a progress bar."""
    if total == 0:
        return "[" + " " * width + "] 0%"

    progress = completed / total
    filled = int(width * progress)
    bar = "=" * filled + " " * (width - filled)

    return f"[{bar}] {progress * 100:.0f}%"


def display_workflow_status(manager: StateManager, verbose: bool = False):
    """Display workflow status in human-readable format."""
    state = manager.export_state()
    workflow = state["workflow_status"]

    print("\n" + "=" * 70)
    print("  RRWrite Manuscript Generation - Workflow Status")
    print("=" * 70)

    # Header information
    print(f"\nManuscript Directory: {state['manuscript_dir']}")
    print(f"Target Journal: {state.get('target_journal') or 'Not set'}")
    print(f"Last Updated: {state['last_updated']}")

    # Overall progress
    progress = manager.get_progress_summary()
    print(f"\nOverall Progress: {format_progress_bar(progress['completed_stages'], progress['total_stages'])}")
    print(f"Current Stage: {progress['current_stage'].replace('_', ' ').title()}")

    print("\n" + "-" * 70)
    print("Workflow Stages:")
    print("-" * 70)

    # 1. Repository Analysis
    stage = workflow["repository_analysis"]
    icon = get_status_icon(stage["status"])
    print(f"\n{icon} Repository Analysis: {get_status_color(stage['status'])}")
    if verbose and stage["file"]:
        print(f"   File: {stage['file']}")
        if stage["completed_at"]:
            print(f"   Completed: {stage['completed_at']}")

    # 2. Planning
    stage = workflow["plan"]
    icon = get_status_icon(stage["status"])
    print(f"\n{icon} Planning: {get_status_color(stage['status'])}")
    if stage["target_journal"]:
        print(f"   Initial Journal: {stage['target_journal']}")
    if verbose and stage["file"]:
        print(f"   Outline: {stage['file']}")
        if stage["completed_at"]:
            print(f"   Completed: {stage['completed_at']}")

    # 3. Journal Assessment (NEW)
    stage = workflow["assessment"]
    icon = get_status_icon(stage["status"])
    print(f"\n{icon} Journal Assessment: {get_status_color(stage['status'])}")

    if stage["status"] == "completed":
        print(f"   Initial Journal: {stage.get('journal_initial', 'N/A')}")
        print(f"   Confirmed Journal: {stage.get('journal_confirmed', 'N/A')}")

        score = stage.get("compatibility_score")
        if score is not None:
            score_pct = score * 100
            score_icon = "✓" if score >= 0.7 else "⚠"
            print(f"   Compatibility: {score_icon} {score_pct:.0f}% ({score:.2f}/1.00)")

        adjustments = stage.get("required_adjustments", 0)
        if adjustments > 0:
            print(f"   ⚠ Required Adjustments: {adjustments}")

        if stage.get("guidelines_path"):
            print(f"   ✓ Guidelines: {stage['guidelines_path']}")

        if verbose:
            if stage["file"]:
                print(f"   Assessment Report: {stage['file']}")
            if stage["completed_at"]:
                print(f"   Completed: {stage['completed_at']}")

    elif stage["status"] == "in_progress":
        print(f"   Analyzing compatibility with initial journal...")

    # 4. Literature Research
    stage = workflow["research"]
    icon = get_status_icon(stage["status"])
    print(f"\n{icon} Literature Research: {get_status_color(stage['status'])}")
    if stage["status"] == "completed":
        print(f"   Topics: {stage.get('topics_count', 0)}")
        print(f"   Papers Found: {stage.get('papers_found', 0)}")
        if verbose and stage["file"]:
            print(f"   File: {stage['file']}")

    # 5. Drafting
    stage = workflow["drafting"]
    icon = get_status_icon(stage["status"])
    sections_done = stage["completed_sections"]
    sections_total = stage["total_sections"]

    print(f"\n{icon} Drafting: {get_status_color(stage['status'])}")
    print(f"   Progress: {format_progress_bar(sections_done, sections_total, width=20)}")
    print(f"   Sections: {sections_done}/{sections_total} completed")

    if verbose or stage["status"] != "not_started":
        print(f"\n   Section Status:")
        for section_name, section_data in stage["sections"].items():
            section_icon = get_status_icon(section_data["status"])
            section_display = section_name.replace("_", " ").title()
            print(f"     {section_icon} {section_display}: {section_data['status']}")
            if verbose and section_data["file"]:
                print(f"        File: {section_data['file']}")

    # 5.5. Assembly
    stage = workflow.get("assembly", {})
    if stage:
        icon = get_status_icon(stage.get("status", "not_started"))
        print(f"\n{icon} Assembly: {get_status_color(stage.get('status', 'not_started'))}")

        if stage.get("status") == "completed":
            sections_included = stage.get("sections_included", 0)
            sections_missing = stage.get("sections_missing", 0)
            total_words = stage.get("total_word_count", 0)
            warnings = stage.get("validation_warnings", 0)

            print(f"   Manuscript: {stage.get('file', 'manuscript.md')}")
            print(f"   Sections: {sections_included} included, {sections_missing} missing")
            print(f"   Total Words: {total_words:,}")

            if warnings > 0:
                print(f"   ⚠ Validation Warnings: {warnings}")

            if verbose:
                if stage.get("manifest_file"):
                    print(f"   Manifest: {stage['manifest_file']}")
                if stage.get("completed_at"):
                    print(f"   Completed: {stage['completed_at']}")

        elif stage.get("status") == "in_progress":
            print(f"   Assembling sections...")

    # 6. Critique
    stage = workflow["critique"]
    icon = get_status_icon(stage["status"])
    print(f"\n{icon} Critique: {get_status_color(stage['status'])}")
    if stage["status"] == "completed":
        issues = stage.get("issues_found", 0)
        major = stage.get("issues_major", 0)
        minor = stage.get("issues_minor", 0)
        print(f"   Issues Found: {issues} ({major} major, {minor} minor)")
        if verbose and stage["file"]:
            print(f"   Report: {stage['file']}")

    print("\n" + "=" * 70)

    # Files summary
    files = state["files"]
    generated_files = [f for f in files.values() if f is not None and isinstance(f, str)]
    if generated_files:
        print(f"\nGenerated Files: {len(generated_files)}")
        if verbose:
            print("\nFiles:")
            for file_type, file_path in files.items():
                if file_path and isinstance(file_path, str):
                    print(f"  - {file_type}: {file_path}")

    # Metadata
    metadata = state["metadata"]
    if any(metadata.values()):
        print(f"\nManuscript Statistics:")
        if metadata["total_word_count"] > 0:
            print(f"  Word Count: {metadata['total_word_count']}")
        if metadata["citations_count"] > 0:
            print(f"  Citations: {metadata['citations_count']}")
        if metadata["figures_count"] > 0:
            print(f"  Figures: {metadata['figures_count']}")
        if metadata["tables_count"] > 0:
            print(f"  Tables: {metadata['tables_count']}")

    print("\n" + "=" * 70 + "\n")


def display_json(manager: StateManager):
    """Display status as JSON."""
    state = manager.export_state()
    progress = manager.get_progress_summary()

    output = {
        "manuscript_dir": state["manuscript_dir"],
        "target_journal": state.get("target_journal"),
        "last_updated": state["last_updated"],
        "progress": progress,
        "workflow_status": state["workflow_status"],
        "files": state["files"],
        "metadata": state["metadata"]
    }

    print(json.dumps(output, indent=2))


def main():
    """CLI interface for status dashboard."""
    parser = argparse.ArgumentParser(
        description="Display RRWrite workflow status",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --output-dir manuscript/repo_v1
  %(prog)s --verbose
  %(prog)s --json
        """
    )
    parser.add_argument(
        "--output-dir",
        default="manuscript",
        help="Manuscript output directory (default: manuscript)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show verbose output with file paths and timestamps"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output status as JSON"
    )

    args = parser.parse_args()

    # Check if state exists
    state_file = Path(args.output_dir) / ".rrwrite" / "state.json"
    if not state_file.exists():
        print(f"Error: No workflow state found in {args.output_dir}", file=sys.stderr)
        print(f"Expected: {state_file}", file=sys.stderr)
        print("\nHave you initialized the workflow? Try running:", file=sys.stderr)
        print("  /rrwrite-plan-manuscript --target-dir <dir>", file=sys.stderr)
        sys.exit(1)

    try:
        manager = StateManager(output_dir=args.output_dir)

        if args.json:
            display_json(manager)
        else:
            display_workflow_status(manager, verbose=args.verbose)

        sys.exit(0)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
