#!/usr/bin/env python3
"""
Compare two workflow runs.

Usage:
    python scripts/rrwrite-compare-runs.py run1 run2
    python scripts/rrwrite-compare-runs.py \
        manuscript/runs/2026-02-05_143022_nature-methods \
        manuscript/runs/2026-02-08_091530_plos-revised
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime
import difflib

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))


def read_metadata(run_dir: Path) -> dict:
    """Read run metadata.

    Args:
        run_dir: Run directory path

    Returns:
        Metadata dictionary or empty dict
    """
    metadata_file = run_dir / "run_metadata.json"
    if not metadata_file.exists():
        return {}

    try:
        with open(metadata_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def count_words(file_path: Path) -> int:
    """Count words in a file.

    Args:
        file_path: Path to file

    Returns:
        Word count
    """
    if not file_path.exists():
        return 0

    try:
        with open(file_path, 'r') as f:
            content = f.read()
            return len(content.split())
    except IOError:
        return 0


def count_lines(file_path: Path) -> int:
    """Count lines in a file.

    Args:
        file_path: Path to file

    Returns:
        Line count
    """
    if not file_path.exists():
        return 0

    try:
        with open(file_path, 'r') as f:
            return len(f.readlines())
    except IOError:
        return 0


def count_citations(run_dir: Path) -> int:
    """Count citations in a run.

    Args:
        run_dir: Run directory path

    Returns:
        Number of citations
    """
    # Check for .bib files
    bib_files = list(run_dir.glob("*.bib"))
    if not bib_files:
        return 0

    total = 0
    for bib_file in bib_files:
        try:
            with open(bib_file, 'r') as f:
                content = f.read()
                # Count @article, @book, etc.
                total += content.count('@')
        except IOError:
            pass

    return total


def get_file_stats(run_dir: Path, filename: str) -> dict:
    """Get statistics for a file.

    Args:
        run_dir: Run directory path
        filename: File name

    Returns:
        Dictionary with words, lines, exists
    """
    file_path = run_dir / filename
    return {
        "exists": file_path.exists(),
        "words": count_words(file_path),
        "lines": count_lines(file_path)
    }


def compare_files(run1_dir: Path, run2_dir: Path, filename: str) -> str:
    """Compare a file between two runs.

    Args:
        run1_dir: First run directory
        run2_dir: Second run directory
        filename: File name to compare

    Returns:
        Comparison summary string
    """
    stats1 = get_file_stats(run1_dir, filename)
    stats2 = get_file_stats(run2_dir, filename)

    if not stats1["exists"] and not stats2["exists"]:
        return f"  {filename}: Not present in either run"

    if not stats1["exists"]:
        return f"  A {filename}: Added ({stats2['words']} words, {stats2['lines']} lines)"

    if not stats2["exists"]:
        return f"  D {filename}: Deleted ({stats1['words']} words)"

    # Both exist - compare
    word_diff = stats2["words"] - stats1["words"]
    line_diff = stats2["lines"] - stats1["lines"]

    if word_diff == 0 and line_diff == 0:
        return f"  = {filename}: Unchanged"

    word_pct = (word_diff / stats1["words"] * 100) if stats1["words"] > 0 else 0
    sign = "+" if word_diff > 0 else ""

    return f"  M {filename}: {stats1['lines']} → {stats2['lines']} lines ({sign}{word_diff} words, {sign}{word_pct:.0f}%)"


def compare_runs(run1_path: str, run2_path: str) -> None:
    """Compare two workflow runs.

    Args:
        run1_path: Path to first run directory
        run2_path: Path to second run directory
    """
    run1_dir = Path(run1_path).resolve()
    run2_dir = Path(run2_path).resolve()

    # Validate directories exist
    if not run1_dir.exists():
        print(f"Error: Run 1 not found: {run1_dir}")
        sys.exit(1)

    if not run2_dir.exists():
        print(f"Error: Run 2 not found: {run2_dir}")
        sys.exit(1)

    # Read metadata
    meta1 = read_metadata(run1_dir)
    meta2 = read_metadata(run2_dir)

    # Display comparison
    print("=" * 60)
    print("Run Comparison")
    print("=" * 60)
    print()

    # Run 1 info
    print(f"Run 1: {run1_dir.name}")
    print(f"  Location: {run1_dir}")
    if meta1.get("target_journal"):
        print(f"  Target: {meta1['target_journal']}")
    if meta1.get("created_at"):
        print(f"  Created: {meta1['created_at'][:16]}")
    if meta1.get("git_commit"):
        print(f"  Git commit: {meta1['git_commit']}")

    # Count stats for run 1
    total_words1 = sum(count_words(run1_dir / f) for f in ["abstract.md", "introduction.md", "methods.md", "results.md", "discussion.md"] if (run1_dir / f).exists())
    sections1 = sum(1 for f in ["abstract.md", "introduction.md", "methods.md", "results.md", "discussion.md"] if (run1_dir / f).exists())
    citations1 = count_citations(run1_dir)

    print(f"  Word count: {total_words1:,}")
    print(f"  Sections: {sections1}")
    print(f"  Citations: {citations1}")

    print()

    # Run 2 info
    print(f"Run 2: {run2_dir.name}")
    print(f"  Location: {run2_dir}")
    if meta2.get("target_journal"):
        print(f"  Target: {meta2['target_journal']}")
    if meta2.get("created_at"):
        print(f"  Created: {meta2['created_at'][:16]}")
    if meta2.get("git_commit"):
        print(f"  Git commit: {meta2['git_commit']}")

    # Count stats for run 2
    total_words2 = sum(count_words(run2_dir / f) for f in ["abstract.md", "introduction.md", "methods.md", "results.md", "discussion.md"] if (run2_dir / f).exists())
    sections2 = sum(1 for f in ["abstract.md", "introduction.md", "methods.md", "results.md", "discussion.md"] if (run2_dir / f).exists())
    citations2 = count_citations(run2_dir)

    word_diff = total_words2 - total_words1
    word_diff_pct = (word_diff / total_words1 * 100) if total_words1 > 0 else 0
    section_diff = sections2 - sections1
    citation_diff = citations2 - citations1

    print(f"  Word count: {total_words2:,} ({word_diff:+,}, {word_diff_pct:+.0f}%)")
    print(f"  Sections: {sections2} ({section_diff:+})")
    print(f"  Citations: {citations2} ({citation_diff:+})")

    print()

    # File-by-file comparison
    print("File Changes:")
    print("-" * 60)

    # Get all markdown files from both runs
    all_files = set()
    for run_dir in [run1_dir, run2_dir]:
        for md_file in run_dir.glob("*.md"):
            if md_file.name != "run_metadata.json":
                all_files.add(md_file.name)

    # Sort files in logical order
    file_order = ["outline.md", "literature.md", "abstract.md", "introduction.md",
                  "methods.md", "results.md", "discussion.md", "conclusion.md",
                  "full_manuscript.md"]

    sorted_files = []
    for f in file_order:
        if f in all_files:
            sorted_files.append(f)
            all_files.remove(f)

    # Add remaining files
    sorted_files.extend(sorted(all_files))

    # Compare each file
    changes = []
    for filename in sorted_files:
        comparison = compare_files(run1_dir, run2_dir, filename)
        print(comparison)
        if not comparison.startswith("  ="):
            changes.append(filename)

    print()

    if changes:
        print(f"Summary: {len(changes)} file(s) changed")
    else:
        print("Summary: Runs are identical")

    print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Compare two workflow runs"
    )
    parser.add_argument(
        "run1",
        help="First run directory path"
    )
    parser.add_argument(
        "run2",
        help="Second run directory path"
    )

    args = parser.parse_args()

    compare_runs(args.run1, args.run2)


if __name__ == "__main__":
    main()
