#!/usr/bin/env python3
"""Recommend alternative journals based on outline analysis.

This script scores a manuscript outline against all journals in the
guidelines database and returns the top recommendations.
"""

import argparse
import yaml
from pathlib import Path
import sys

# Import from sibling module
try:
    from rrwrite_match_journal_scope import extract_keywords, score_journal_match, analyze_structural_fit
except ImportError:
    # If running standalone, try adding scripts dir to path
    scripts_dir = Path(__file__).parent
    sys.path.insert(0, str(scripts_dir))
    from rrwrite_match_journal_scope import extract_keywords, score_journal_match, analyze_structural_fit


def get_scope_summary(journal_data, max_items=2):
    """Get brief summary of journal scope.

    Args:
        journal_data: Journal configuration dict
        max_items: Maximum number of scope items to include

    Returns:
        String with comma-separated scope items
    """
    scope = journal_data.get('scope', [])[:max_items]
    return ', '.join(scope) if scope else 'No scope information available'


def explain_score(score, outline_keywords, journal_data):
    """Generate human-readable explanation for score.

    Args:
        score: Compatibility score (0.0-1.0)
        outline_keywords: Set of keywords from outline
        journal_data: Journal configuration dict

    Returns:
        String explaining why the score is what it is
    """
    positive_kw = set([k.lower() for k in journal_data.get('suitability_keywords', {}).get('positive', [])])
    negative_kw = set([k.lower() for k in journal_data.get('suitability_keywords', {}).get('negative', [])])

    matched_positive = outline_keywords & positive_kw
    matched_negative = outline_keywords & negative_kw

    reasons = []

    if score >= 0.75:
        reasons.append(f"Strong keyword alignment ({len(matched_positive)} positive matches)")
    elif score >= 0.6:
        reasons.append(f"Good keyword coverage ({len(matched_positive)} positive matches)")
    elif score >= 0.45:
        reasons.append(f"Moderate fit ({len(matched_positive)} positive matches)")
    else:
        reasons.append(f"Limited keyword overlap ({len(matched_positive)} positive matches)")

    if matched_negative:
        reasons.append(f"Contains {len(matched_negative)} scope mismatch keywords")

    # Check for special journal features
    if 'author_summary' in journal_data.get('structure', {}).get('required_sections', []):
        reasons.append("Requires non-technical Author Summary")

    word_limit = journal_data.get('word_limits', {}).get('total', 0)
    if word_limit > 0 and word_limit <= 3000:
        reasons.append(f"Strict {word_limit}-word limit")

    return '; '.join(reasons)


def recommend_journals(outline_text, guidelines, exclude=None, top_n=3):
    """Score all journals and return top recommendations.

    Args:
        outline_text: Content of outline.md
        guidelines: Full guidelines database dict
        exclude: Journal key to exclude from recommendations
        top_n: Number of top journals to return

    Returns:
        List of tuples: (journal_key, journal_data_with_score)
    """
    outline_keywords = extract_keywords(outline_text)

    scores = {}
    for journal_key, journal_data in guidelines.get('journals', {}).items():
        # Skip excluded journal
        if exclude and journal_key == exclude.lower().replace(' ', '_'):
            continue

        # Calculate compatibility score
        score = score_journal_match(outline_keywords, journal_data)

        # Get structural analysis
        structural = analyze_structural_fit(outline_text, journal_data)

        # Store results
        scores[journal_key] = {
            'score': score,
            'name': journal_data.get('full_name', journal_key),
            'scope_summary': get_scope_summary(journal_data),
            'explanation': explain_score(score, outline_keywords, journal_data),
            'missing_sections': len(structural.get('required_sections_missing', [])),
            'word_limit': journal_data.get('word_limits', {}).get('total', 0)
        }

    # Sort by score descending
    ranked = sorted(scores.items(), key=lambda x: x[1]['score'], reverse=True)

    return ranked[:top_n]


def main():
    parser = argparse.ArgumentParser(
        description='Recommend journals for manuscript outline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --outline manuscript/repo_v1/outline.md --guidelines templates/journal_guidelines.yaml
  %(prog)s --outline outline.md --guidelines guidelines.yaml --exclude bioinformatics --top 5
        """
    )
    parser.add_argument('--outline', required=True, help='Path to outline.md')
    parser.add_argument('--guidelines', required=True, help='Path to journal_guidelines.yaml')
    parser.add_argument('--exclude', help='Exclude this journal from recommendations')
    parser.add_argument('--top', type=int, default=3, help='Number of recommendations (default: 3)')
    parser.add_argument('--show-scores', action='store_true', help='Show detailed scoring breakdown')
    args = parser.parse_args()

    # Validate inputs
    outline_path = Path(args.outline)
    if not outline_path.exists():
        print(f"Error: Outline file not found: {args.outline}", file=sys.stderr)
        return 1

    guidelines_path = Path(args.guidelines)
    if not guidelines_path.exists():
        print(f"Error: Guidelines file not found: {args.guidelines}", file=sys.stderr)
        return 1

    # Load data
    try:
        outline_text = outline_path.read_text()
    except Exception as e:
        print(f"Error reading outline: {e}", file=sys.stderr)
        return 1

    try:
        with open(guidelines_path) as f:
            guidelines = yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading guidelines: {e}", file=sys.stderr)
        return 1

    # Get recommendations
    recommendations = recommend_journals(outline_text, guidelines, args.exclude, args.top)

    if not recommendations:
        print("No journal recommendations available.", file=sys.stderr)
        return 1

    # Print results
    print("Journal Recommendations")
    print("=" * 80)

    if args.exclude:
        print(f"(Excluding: {args.exclude})")
        print()

    for i, (journal_key, data) in enumerate(recommendations, 1):
        print(f"\n{i}. {data['name']}")
        print(f"   Compatibility Score: {data['score']:.2f}/1.00", end='')

        # Add visual indicator
        if data['score'] >= 0.75:
            print(" ✓ EXCELLENT")
        elif data['score'] >= 0.6:
            print(" ✓ GOOD")
        elif data['score'] >= 0.45:
            print(" ⚠ MODERATE")
        else:
            print(" ✗ POOR")

        print(f"   Scope: {data['scope_summary']}")
        print(f"   Reason: {data['explanation']}")

        if data['word_limit'] > 0:
            print(f"   Word Limit: {data['word_limit']} words")
        else:
            print(f"   Word Limit: No strict limit")

        if data['missing_sections'] > 0:
            print(f"   ⚠ {data['missing_sections']} required section(s) missing from outline")

    print()
    print("=" * 80)

    # Suggest action
    top_score = recommendations[0][1]['score']
    if top_score >= 0.75:
        print(f"Recommendation: Proceed with {recommendations[0][1]['name']} (excellent match)")
    elif top_score >= 0.6:
        print(f"Recommendation: {recommendations[0][1]['name']} is a good fit")
    else:
        print(f"Recommendation: Consider revising outline to better match target journal")

    return 0


if __name__ == '__main__':
    sys.exit(main())
