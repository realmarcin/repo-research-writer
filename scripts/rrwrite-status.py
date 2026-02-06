#!/usr/bin/env python3
"""
Display RRWrite workflow status and progress.

Usage:
    python scripts/rrwrite-status.py
    python scripts/rrwrite-status.py --detailed
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from rrwrite_state_manager import StateManager
except ImportError:
    # Try alternative import
    import rrwrite_state_manager
    StateManager = rrwrite_state_manager.StateManager


def format_timestamp(iso_timestamp: str) -> str:
    """Format ISO timestamp to readable string.

    Args:
        iso_timestamp: ISO format timestamp

    Returns:
        Human-readable timestamp
    """
    if not iso_timestamp:
        return "N/A"

    try:
        dt = datetime.fromisoformat(iso_timestamp)
        return dt.strftime("%Y-%m-%d %H:%M")
    except (ValueError, AttributeError):
        return iso_timestamp


def get_status_symbol(status: str) -> str:
    """Get symbol for status.

    Args:
        status: Status string

    Returns:
        Status symbol
    """
    symbols = {
        "completed": "✓",
        "in_progress": "⚠",
        "not_started": "○",
    }
    return symbols.get(status, "?")


def display_status(state: dict, detailed: bool = False, manager: StateManager = None) -> None:
    """Display workflow status.

    Args:
        state: State dictionary
        detailed: Show detailed information
        manager: StateManager instance (for detailed mode)
    """
    print("=" * 60)
    print("RRWrite Project Status")
    print("=" * 60)
    print()

    # Project info
    print(f"Project: {state.get('project_name', 'Unknown')}")
    if state.get('target_journal'):
        print(f"Target Journal: {state['target_journal']}")
    print(f"Last Updated: {format_timestamp(state.get('last_updated'))}")
    print()

    # Workflow progress
    print("Workflow Progress:")
    print("-" * 60)

    workflow = state.get("workflow_status", {})

    # Plan
    plan = workflow.get("plan", {})
    symbol = get_status_symbol(plan.get("status"))
    print(f"  {symbol} Planning")
    if plan.get("file") and detailed:
        print(f"      File: {plan['file']}")
        print(f"      Completed: {format_timestamp(plan.get('completed_at'))}")

    # Research
    research = workflow.get("research", {})
    symbol = get_status_symbol(research.get("status"))
    papers = research.get("papers_found", 0)
    if papers > 0:
        print(f"  {symbol} Literature Research ({papers} papers)")
    else:
        print(f"  {symbol} Literature Research")
    if research.get("file") and detailed:
        print(f"      File: {research['file']}")
        print(f"      Completed: {format_timestamp(research.get('completed_at'))}")

    # Draft
    draft = workflow.get("draft", {})
    symbol = get_status_symbol(draft.get("status"))
    sections_done = draft.get("sections_completed", [])
    sections_pending = draft.get("sections_pending", [])
    total = len(sections_done) + len(sections_pending)

    if total > 0:
        print(f"  {symbol} Drafting ({len(sections_done)}/{total} sections)")
    else:
        print(f"  {symbol} Drafting")

    if detailed and sections_done:
        print(f"      Completed: {', '.join(sections_done)}")
        if sections_pending:
            print(f"      Pending: {', '.join(sections_pending)}")
        print(f"      Last section: {draft.get('last_section')}")

    # Critique
    critique = workflow.get("critique", {})
    iterations = critique.get("iterations", [])
    symbol = get_status_symbol(critique.get("status"))

    if iterations:
        latest = iterations[-1]
        version = latest.get("version", 1)
        recommendation = latest.get("recommendation", "Unknown")
        print(f"  {symbol} Critique (v{version} - {recommendation})")

        if detailed:
            major = latest.get("major_issues", 0)
            minor = latest.get("minor_issues", 0)
            print(f"      Issues: {major} major, {minor} minor")
            print(f"      File: {latest.get('file')}")

            if len(iterations) > 1:
                print(f"      Total iterations: {len(iterations)}")
    else:
        print(f"  {symbol} Critique")

    # Assembly
    assembly = workflow.get("assembly", {})
    symbol = get_status_symbol(assembly.get("status"))
    print(f"  {symbol} Final Assembly")
    if assembly.get("file") and detailed:
        print(f"      File: {assembly['file']}")

    print()

    # Next steps
    next_steps = get_next_steps(workflow)
    if next_steps:
        print("Next Steps:")
        print("-" * 60)
        for i, step in enumerate(next_steps, 1):
            print(f"  {i}. {step}")
        print()

    # Runs
    runs = state.get("runs", [])
    if runs and detailed:
        print("Workflow Runs:")
        print("-" * 60)
        for run in runs[-3:]:  # Show last 3 runs
            run_id = run.get("run_id", "Unknown")
            journal = run.get("target_journal", "N/A")
            started = format_timestamp(run.get("started_at"))
            print(f"  • {run_id}")
            print(f"    Journal: {journal}, Started: {started}")
        if len(runs) > 3:
            print(f"  ... and {len(runs) - 3} more")
        print()

    # Provenance
    if detailed:
        provenance = state.get("provenance", {})
        verifications = provenance.get("verification_runs", [])
        if verifications:
            print("Recent Verifications:")
            print("-" * 60)
            for ver in verifications[-3:]:
                script = Path(ver.get("script", "")).name
                timestamp = format_timestamp(ver.get("timestamp"))
                print(f"  • {script} ({timestamp})")
                print(f"    File: {ver.get('file')}, Result: {ver.get('result')}")
            print()

    # File history (if detailed and Git available)
    if detailed and manager:
        key_files = ["outline.md", "literature.md", "abstract.md", "methods.md", "results.md"]

        has_history = False
        for filename in key_files:
            file_path = f"manuscript/{filename}"
            history = manager.get_file_history(file_path, limit=1)
            if history:
                if not has_history:
                    print("Recent File Changes:")
                    print("-" * 60)
                    has_history = True
                h = history[0]
                print(f"  • {filename}: {h['date']} - {h['message'][:50]}")

        if has_history:
            print()

    # Uncommitted changes warning
    if manager and manager.check_uncommitted_changes():
        print("⚠️  Uncommitted Changes Detected")
        print("-" * 60)
        print("You have uncommitted changes in manuscript/")
        print()
        print("Recommendation: Commit before running skills")
        print("  git add manuscript/")
        print('  git commit -m "Work in progress"')
        print()


def get_next_steps(workflow: dict) -> list:
    """Determine next steps based on workflow status.

    Args:
        workflow: Workflow status dictionary

    Returns:
        List of next step descriptions
    """
    steps = []

    plan_status = workflow.get("plan", {}).get("status")
    research_status = workflow.get("research", {}).get("status")
    draft_status = workflow.get("draft", {}).get("status")
    critique_status = workflow.get("critique", {}).get("status")
    assembly_status = workflow.get("assembly", {}).get("status")

    # Plan
    if plan_status == "not_started":
        steps.append("Create manuscript outline with /rrwrite-plan-manuscript")
        return steps  # Can't proceed without plan

    # Research
    if research_status == "not_started":
        steps.append("Research literature with /rrwrite-research-literature")

    # Draft
    draft = workflow.get("draft", {})
    sections_done = draft.get("sections_completed", [])
    sections_pending = draft.get("sections_pending", [])

    if draft_status == "not_started":
        steps.append("Start drafting sections with /rrwrite-draft-section")
    elif sections_pending:
        steps.append(f"Draft remaining sections: {', '.join(sections_pending)}")

    # Critique
    if critique_status == "not_started" and sections_done:
        steps.append("Critique completed sections with /rrwrite-critique-manuscript")
    elif critique_status == "completed":
        iterations = workflow.get("critique", {}).get("iterations", [])
        if iterations:
            latest = iterations[-1]
            rec = latest.get("recommendation", "")
            if "REVISION" in rec.upper():
                steps.append("Address critique issues and revise sections")
                steps.append("Run /rrwrite-critique-manuscript again after revisions")

    # Assembly
    if assembly_status == "not_started" and sections_done and critique_status == "completed":
        iterations = workflow.get("critique", {}).get("iterations", [])
        if iterations:
            latest = iterations[-1]
            rec = latest.get("recommendation", "")
            if "ACCEPT" in rec.upper():
                steps.append("Assemble final manuscript with rrwrite-assemble-manuscript.py")

    # Validation
    if assembly_status == "completed":
        steps.append("Validate manuscript with rrwrite-validate-manuscript.py")

    return steps


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Display RRWrite workflow status"
    )
    parser.add_argument(
        "--detailed",
        "-d",
        action="store_true",
        help="Show detailed information"
    )
    parser.add_argument(
        "--project-dir",
        default=".",
        help="Project directory (default: current directory)"
    )

    args = parser.parse_args()

    # Initialize state manager
    manager = StateManager(args.project_dir)

    # Read state
    state = manager.read_state()

    if state is None:
        print("=" * 60)
        print("RRWrite Project Status")
        print("=" * 60)
        print()
        print("No state file found.")
        print()
        print("This project hasn't been initialized with RRWrite state tracking.")
        print()
        print("To initialize:")
        print("  python scripts/rrwrite-state-manager.py init")
        print()
        print("Or run the setup script:")
        print("  ~/repo-research-writer/install.sh setup-project")
        print()
        sys.exit(1)

    # Display status
    display_status(state, detailed=args.detailed, manager=manager)


if __name__ == "__main__":
    main()
