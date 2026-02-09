#!/usr/bin/env python3
"""Match manuscript outline to journal scope.

This script analyzes a manuscript outline and calculates its compatibility
with a target journal by comparing keywords, scope, and research focus.
"""

import argparse
import yaml
from pathlib import Path
import re
import sys


def extract_keywords(outline_text):
    """Extract domain-specific keywords from outline text.

    Args:
        outline_text: Content of the outline markdown file

    Returns:
        Set of lowercase keywords found in the outline
    """
    keywords = set()

    # Convert to lowercase for case-insensitive matching
    text_lower = outline_text.lower()

    # Method-related patterns
    method_patterns = [
        r'\b(algorithm|computational method|pipeline|workflow|software|tool|database)\b',
        r'\b(experimental|wet lab|clinical|imaging|sequencing)\b',
        r'\b(modeling|modelling|simulation|analysis|prediction|classification)\b',
        r'\b(machine learning|deep learning|neural network|artificial intelligence)\b',
        r'\b(genome|genomics|transcriptome|transcriptomics|proteome|proteomics)\b',
        r'\b(network analysis|pathway|systems biology|multi-scale)\b',
        r'\b(sequence alignment|genome annotation|gene prediction)\b',
        r'\b(single-cell|high-throughput|next-generation sequencing|rna-seq)\b',
        r'\b(evolutionary|population genetics|comparative genomics)\b',
        r'\b(structural biology|protein structure|molecular dynamics)\b',
        r'\b(data integration|meta-analysis|benchmark|validation)\b',
        r'\b(open source|reproducible|fair data|code availability)\b'
    ]

    for pattern in method_patterns:
        matches = re.findall(pattern, text_lower)
        keywords.update(matches)

    # Look for specific tool/method mentions (preserve as-is)
    tool_pattern = r'\b([A-Z][a-zA-Z0-9]+(?:-[A-Za-z0-9]+)*)\b'
    tools = re.findall(tool_pattern, outline_text)
    # Only include if mentioned multiple times (likely important)
    from collections import Counter
    tool_counts = Counter(tools)
    important_tools = {tool.lower() for tool, count in tool_counts.items() if count >= 2}
    keywords.update(important_tools)

    return keywords


def score_journal_match(outline_keywords, journal_data):
    """Calculate compatibility score (0.0-1.0) between outline and journal.

    Args:
        outline_keywords: Set of keywords extracted from outline
        journal_data: Journal configuration from guidelines YAML

    Returns:
        Float score between 0.0 (no match) and 1.0 (perfect match)
    """
    positive_keywords = set([
        k.lower() for k in journal_data.get('suitability_keywords', {}).get('positive', [])
    ])
    negative_keywords = set([
        k.lower() for k in journal_data.get('suitability_keywords', {}).get('negative', [])
    ])

    if len(positive_keywords) == 0:
        # No keywords defined for this journal
        return 0.5  # Neutral score

    # Count matches
    positive_matches = len(outline_keywords & positive_keywords)
    negative_matches = len(outline_keywords & negative_keywords)

    # Calculate positive ratio (what fraction of positive keywords are present)
    positive_ratio = positive_matches / len(positive_keywords)

    # Penalty for negative keywords (each reduces score)
    negative_penalty = negative_matches * 0.15

    # Bonus for multiple positive matches (indicates strong fit)
    if positive_matches >= 5:
        bonus = 0.1
    elif positive_matches >= 3:
        bonus = 0.05
    else:
        bonus = 0.0

    # Final score
    score = max(0.0, min(1.0, positive_ratio + bonus - negative_penalty))

    return score


def analyze_structural_fit(outline_text, journal_data):
    """Analyze if outline structure matches journal requirements.

    Args:
        outline_text: Content of the outline markdown file
        journal_data: Journal configuration from guidelines YAML

    Returns:
        Dict with structural analysis results
    """
    results = {
        'required_sections_present': [],
        'required_sections_missing': [],
        'section_order_correct': True,
        'special_sections': []
    }

    # Extract section headers from outline (markdown ## headers)
    outline_sections = re.findall(r'^##\s+(.+)$', outline_text, re.MULTILINE)
    outline_sections_lower = [s.lower().strip() for s in outline_sections]

    # Check required sections
    required = journal_data.get('structure', {}).get('required_sections', [])
    for section in required:
        # Normalize section name for comparison
        section_variants = [
            section.lower(),
            section.replace('_', ' ').lower(),
            section.replace('_', ' and ').lower()
        ]

        found = any(
            any(variant in outline_sec for variant in section_variants)
            for outline_sec in outline_sections_lower
        )

        if found:
            results['required_sections_present'].append(section)
        else:
            results['required_sections_missing'].append(section)

    # Check for special sections
    if 'author_summary' in required and 'author_summary' not in results['required_sections_present']:
        results['special_sections'].append('Author Summary (PLOS requirement) - MISSING')

    return results


def main():
    parser = argparse.ArgumentParser(
        description='Match manuscript outline to journal scope',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--outline', required=True, help='Path to outline.md')
    parser.add_argument('--journal', required=True, help='Journal name (e.g., bioinformatics)')
    parser.add_argument('--guidelines', required=True, help='Path to journal_guidelines.yaml')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed analysis')
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

    # Load outline
    try:
        outline_text = outline_path.read_text()
    except Exception as e:
        print(f"Error reading outline: {e}", file=sys.stderr)
        return 1

    # Load guidelines
    try:
        with open(guidelines_path) as f:
            guidelines = yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading guidelines: {e}", file=sys.stderr)
        return 1

    # Get journal data
    journal_key = args.journal.lower().replace(' ', '_')
    journal_data = guidelines.get('journals', {}).get(journal_key)

    if not journal_data:
        print(f"Error: Journal '{args.journal}' not found in guidelines database", file=sys.stderr)
        available = ', '.join(guidelines.get('journals', {}).keys())
        print(f"Available journals: {available}", file=sys.stderr)
        return 1

    # Extract keywords and calculate score
    outline_keywords = extract_keywords(outline_text)
    compatibility_score = score_journal_match(outline_keywords, journal_data)

    # Structural analysis
    structural_analysis = analyze_structural_fit(outline_text, journal_data)

    # Output results
    print(f"Journal: {journal_data.get('full_name', args.journal)}")
    print(f"Compatibility Score: {compatibility_score:.2f}")
    print()

    # Interpretation
    if compatibility_score >= 0.75:
        print("✓ EXCELLENT MATCH - Outline aligns very well with journal scope")
    elif compatibility_score >= 0.6:
        print("✓ GOOD MATCH - Outline fits journal scope with minor adjustments")
    elif compatibility_score >= 0.45:
        print("⚠ MODERATE MATCH - Consider alternative journals or revise outline")
    else:
        print("✗ POOR MATCH - Outline does not fit journal scope well")

    print()

    if args.verbose:
        # Detailed keyword analysis
        positive_kw = set([k.lower() for k in journal_data.get('suitability_keywords', {}).get('positive', [])])
        negative_kw = set([k.lower() for k in journal_data.get('suitability_keywords', {}).get('negative', [])])

        matched_positive = outline_keywords & positive_kw
        matched_negative = outline_keywords & negative_kw

        print("Keyword Analysis:")
        print(f"  Outline keywords found: {len(outline_keywords)}")
        print(f"  Positive matches: {len(matched_positive)}/{len(positive_kw)}")
        if matched_positive:
            print(f"    → {', '.join(sorted(matched_positive))}")

        if matched_negative:
            print(f"  Negative matches: {len(matched_negative)} (red flags)")
            print(f"    → {', '.join(sorted(matched_negative))}")
        print()

        # Structural analysis
        print("Structural Analysis:")
        if structural_analysis['required_sections_present']:
            print(f"  ✓ Required sections present: {len(structural_analysis['required_sections_present'])}")
            for sec in structural_analysis['required_sections_present']:
                print(f"    - {sec}")

        if structural_analysis['required_sections_missing']:
            print(f"  ✗ Required sections missing: {len(structural_analysis['required_sections_missing'])}")
            for sec in structural_analysis['required_sections_missing']:
                print(f"    - {sec}")

        if structural_analysis['special_sections']:
            print(f"  ⚠ Special requirements:")
            for note in structural_analysis['special_sections']:
                print(f"    - {note}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
