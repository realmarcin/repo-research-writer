#!/usr/bin/env python3
"""
RRWrite Journal Recommender

Scores all journals in database against manuscript outline and returns ranked recommendations.

Usage:
    rrwrite-recommend-journal.py --outline OUTLINE --guidelines YAML [--exclude JOURNAL] [--top N] [--show-scores]

Arguments:
    --outline PATH      Path to outline file or workflow state
    --guidelines PATH   Path to journal_guidelines.yaml
    --exclude JOURNAL   Exclude specific journal from recommendations (can be used multiple times)
    --top N            Number of top recommendations to return (default: 3)
    --show-scores      Include detailed scoring information in output

Output:
    JSON with ranked journal recommendations and explanations
"""

import argparse
import json
import sys
import yaml
from pathlib import Path
from typing import Dict, List
import subprocess


def load_all_journals(guidelines_path: str) -> Dict:
    """Load all journals from guidelines YAML."""
    path = Path(guidelines_path)

    if not path.exists():
        raise FileNotFoundError(f"Guidelines file not found: {guidelines_path}")

    with open(path, 'r') as f:
        data = yaml.safe_load(f)

    return data['journals']


def score_journal(outline_path: str, journal_id: str, guidelines_path: str) -> Dict:
    """Score a single journal using the matcher script."""
    matcher_script = Path(__file__).parent / "rrwrite-match-journal-scope.py"

    if not matcher_script.exists():
        raise FileNotFoundError(f"Matcher script not found: {matcher_script}")

    try:
        result = subprocess.run(
            [
                sys.executable,
                str(matcher_script),
                "--outline", outline_path,
                "--journal", journal_id,
                "--guidelines", guidelines_path
            ],
            capture_output=True,
            text=True,
            check=False  # Don't raise exception on non-zero exit
        )

        # Parse output
        output = result.stdout.strip()
        if output:
            return json.loads(output)
        else:
            # Matcher failed, return minimal data
            return {
                "journal": journal_id,
                "compatibility_score": 0.0,
                "error": result.stderr or "Unknown error"
            }

    except Exception as e:
        return {
            "journal": journal_id,
            "compatibility_score": 0.0,
            "error": str(e)
        }


def generate_explanation(score_data: Dict) -> str:
    """Generate human-readable explanation for journal recommendation."""
    score = score_data.get('compatibility_score', 0.0)
    journal_name = score_data.get('journal_name', score_data.get('journal', 'Unknown'))

    explanation_parts = []

    # Score interpretation
    if score >= 0.9:
        explanation_parts.append("Excellent match")
    elif score >= 0.8:
        explanation_parts.append("Strong match")
    elif score >= 0.7:
        explanation_parts.append("Good match")
    elif score >= 0.5:
        explanation_parts.append("Moderate match")
    else:
        explanation_parts.append("Weak match")

    # Add specific reasons
    analysis = score_data.get('analysis', {})

    # Positive keywords
    keyword_analysis = analysis.get('keywords', {})
    positive_matches = keyword_analysis.get('positive_matches', [])
    if positive_matches:
        explanation_parts.append(
            f"aligns with scope ({', '.join(positive_matches[:3])})"
        )

    # Negative keywords warning
    negative_matches = keyword_analysis.get('negative_matches', [])
    if negative_matches:
        explanation_parts.append(
            f"but contains discouraged elements ({', '.join(negative_matches[:2])})"
        )

    # Structure
    structure_analysis = analysis.get('structure', {})
    missing = structure_analysis.get('missing_sections', [])
    if missing:
        if len(missing) == 1:
            explanation_parts.append(f"missing required section: {missing[0]}")
        elif len(missing) <= 3:
            explanation_parts.append(f"missing sections: {', '.join(missing)}")
        else:
            explanation_parts.append(f"missing {len(missing)} required sections")
    else:
        explanation_parts.append("has all required sections")

    return f"{journal_name}: {'; '.join(explanation_parts)}"


def rank_journals(scores: List[Dict], top_n: int) -> List[Dict]:
    """Rank journals by compatibility score."""
    # Sort by score (descending)
    sorted_scores = sorted(
        scores,
        key=lambda x: x.get('compatibility_score', 0.0),
        reverse=True
    )

    return sorted_scores[:top_n]


def format_recommendation(rank: int, score_data: Dict, show_scores: bool) -> Dict:
    """Format a single recommendation."""
    rec = {
        "rank": rank,
        "journal": score_data.get('journal'),
        "journal_name": score_data.get('journal_name', score_data.get('journal')),
        "explanation": generate_explanation(score_data)
    }

    if show_scores:
        rec["scores"] = {
            "compatibility": score_data.get('compatibility_score', 0.0),
            "keyword": score_data.get('keyword_score', 0.0),
            "structure": score_data.get('structure_score', 0.0)
        }
        rec["analysis"] = score_data.get('analysis', {})

    return rec


def main():
    parser = argparse.ArgumentParser(
        description="Recommend journals based on manuscript outline analysis"
    )
    parser.add_argument(
        "--outline",
        required=True,
        help="Path to outline file or workflow state"
    )
    parser.add_argument(
        "--guidelines",
        required=True,
        help="Path to journal_guidelines.yaml"
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Exclude specific journal from recommendations (can be repeated)"
    )
    parser.add_argument(
        "--top",
        type=int,
        default=3,
        help="Number of top recommendations to return (default: 3)"
    )
    parser.add_argument(
        "--show-scores",
        action="store_true",
        help="Include detailed scoring information"
    )

    args = parser.parse_args()

    try:
        # Load all journals
        journals = load_all_journals(args.guidelines)

        # Filter excluded journals
        journal_ids = [jid for jid in journals.keys() if jid not in args.exclude]

        if not journal_ids:
            raise ValueError("No journals available after exclusions")

        # Score all journals
        scores = []
        for journal_id in journal_ids:
            score_data = score_journal(args.outline, journal_id, args.guidelines)
            if 'error' not in score_data:
                scores.append(score_data)

        if not scores:
            raise ValueError("Failed to score any journals")

        # Rank journals
        ranked = rank_journals(scores, args.top)

        # Format recommendations
        recommendations = []
        for i, score_data in enumerate(ranked, start=1):
            recommendations.append(
                format_recommendation(i, score_data, args.show_scores)
            )

        # Prepare output
        result = {
            "total_journals_evaluated": len(scores),
            "recommendations": recommendations
        }

        # Output JSON
        print(json.dumps(result, indent=2))

        sys.exit(0)

    except Exception as e:
        error_result = {
            "error": str(e),
            "recommendations": []
        }
        print(json.dumps(error_result, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
