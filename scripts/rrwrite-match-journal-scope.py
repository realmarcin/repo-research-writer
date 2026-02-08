#!/usr/bin/env python3
"""
RRWrite Journal Scope Matcher

Analyzes manuscript outline compatibility with journal scope and requirements.
Scores journals based on keyword matching and structural alignment.

Usage:
    rrwrite-match-journal-scope.py --outline OUTLINE --journal JOURNAL --guidelines YAML [--verbose]

Arguments:
    --outline PATH      Path to outline file or workflow state
    --journal NAME      Journal identifier (e.g., 'bioinformatics')
    --guidelines PATH   Path to journal_guidelines.yaml
    --verbose          Enable detailed scoring output

Output:
    JSON with compatibility score, missing sections, and recommendations
"""

import argparse
import json
import re
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Set


def load_outline(outline_path: str) -> Dict:
    """Load outline from markdown or workflow state file."""
    path = Path(outline_path)

    if not path.exists():
        raise FileNotFoundError(f"Outline file not found: {outline_path}")

    content = path.read_text()

    # Extract outline text (handle both standalone and workflow state)
    if "## OUTLINE" in content:
        # Extract from workflow state
        outline_section = re.search(r'## OUTLINE\s*\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
        if outline_section:
            outline_text = outline_section.group(1)
        else:
            outline_text = content
    else:
        outline_text = content

    return {
        "text": outline_text,
        "path": str(path)
    }


def load_journal_guidelines(guidelines_path: str, journal: str) -> Dict:
    """Load journal guidelines from YAML file."""
    path = Path(guidelines_path)

    if not path.exists():
        raise FileNotFoundError(f"Guidelines file not found: {guidelines_path}")

    with open(path, 'r') as f:
        data = yaml.safe_load(f)

    if journal not in data['journals']:
        available = ', '.join(data['journals'].keys())
        raise ValueError(f"Journal '{journal}' not found. Available: {available}")

    return data['journals'][journal]


def extract_keywords(text: str) -> Set[str]:
    """Extract meaningful keywords from text using regex patterns."""
    # Convert to lowercase for matching
    text_lower = text.lower()

    # Extract words, keeping hyphenated terms and phrases
    words = re.findall(r'\b[\w-]+\b', text_lower)

    # Extract key phrases (2-3 word combinations)
    phrases = []
    for match in re.finditer(r'\b([\w-]+\s+[\w-]+(?:\s+[\w-]+)?)\b', text_lower):
        phrase = match.group(1)
        # Keep phrases that might be meaningful
        if len(phrase.split()) >= 2:
            phrases.append(phrase)

    # Combine words and phrases
    keywords = set(words + phrases)

    # Remove common stop words
    stop_words = {
        'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
        'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
        'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
        'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
        'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go',
        'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
        'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them',
        'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over',
        'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first',
        'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day',
        'most', 'us', 'is', 'was', 'are', 'been', 'has', 'had', 'were', 'said', 'did',
        'having', 'may', 'should', 'could', 'would', 'might', 'must', 'shall', 'can'
    }

    keywords = {kw for kw in keywords if kw not in stop_words and len(kw) > 2}

    return keywords


def score_keyword_match(outline_keywords: Set[str], journal_keywords: Dict[str, List[str]]) -> Tuple[float, Dict]:
    """Score outline keywords against journal's positive and negative keywords."""
    positive_keywords = set(kw.lower() for kw in journal_keywords.get('positive', []))
    negative_keywords = set(kw.lower() for kw in journal_keywords.get('negative', []))

    # Find matches
    positive_matches = outline_keywords & positive_keywords
    negative_matches = outline_keywords & negative_keywords

    # Calculate score
    # Positive matches increase score, negative matches decrease it
    if not positive_keywords:
        keyword_score = 0.5  # Neutral if no keywords defined
    else:
        positive_ratio = len(positive_matches) / len(positive_keywords)
        negative_penalty = len(negative_matches) * 0.1  # Each negative match reduces score by 10%
        keyword_score = max(0.0, min(1.0, positive_ratio - negative_penalty))

    details = {
        "positive_matches": sorted(list(positive_matches)),
        "negative_matches": sorted(list(negative_matches)),
        "positive_ratio": len(positive_matches) / len(positive_keywords) if positive_keywords else 0,
        "negative_count": len(negative_matches)
    }

    return keyword_score, details


def analyze_structure(outline_text: str, required_sections: List[str]) -> Tuple[float, Dict]:
    """Analyze if outline contains required sections."""
    outline_lower = outline_text.lower()

    present = []
    missing = []

    for section in required_sections:
        # Look for section headers in various formats
        patterns = [
            rf'^#+\s*{re.escape(section)}\s*$',  # Markdown header
            rf'^\*\*{re.escape(section)}\*\*\s*$',  # Bold
            rf'^{re.escape(section)}:\s*$',  # With colon
            rf'\b{re.escape(section)}\b'  # Anywhere in text
        ]

        found = False
        for pattern in patterns:
            if re.search(pattern, outline_lower, re.MULTILINE | re.IGNORECASE):
                found = True
                break

        if found:
            present.append(section)
        else:
            missing.append(section)

    # Calculate structural score
    if required_sections:
        structure_score = len(present) / len(required_sections)
    else:
        structure_score = 1.0

    details = {
        "present_sections": present,
        "missing_sections": missing,
        "coverage": structure_score
    }

    return structure_score, details


def calculate_compatibility_score(keyword_score: float, structure_score: float) -> float:
    """Calculate overall compatibility score (weighted average)."""
    # Weight: 60% keywords, 40% structure
    return 0.6 * keyword_score + 0.4 * structure_score


def generate_recommendations(score: float, keyword_details: Dict, structure_details: Dict,
                            journal_name: str) -> List[str]:
    """Generate recommendations based on analysis."""
    recommendations = []

    if score < 0.7:
        recommendations.append(f"Compatibility score ({score:.2f}) is below recommended threshold (0.70)")
        recommendations.append(f"Consider alternative journals or adjust manuscript scope")

    if keyword_details['negative_count'] > 0:
        recommendations.append(
            f"Warning: {keyword_details['negative_count']} negative keywords detected: "
            f"{', '.join(keyword_details['negative_matches'][:3])}"
        )

    if keyword_details['positive_ratio'] < 0.3:
        recommendations.append(
            f"Low positive keyword match ({keyword_details['positive_ratio']:.2%}). "
            f"Consider emphasizing relevant technical aspects"
        )

    if structure_details['missing_sections']:
        missing = ', '.join(structure_details['missing_sections'][:3])
        recommendations.append(f"Missing required sections: {missing}")

    if score >= 0.7 and not recommendations:
        recommendations.append(f"Good compatibility with {journal_name}")
        if keyword_details['positive_matches']:
            top_matches = ', '.join(keyword_details['positive_matches'][:5])
            recommendations.append(f"Strong matches: {top_matches}")

    return recommendations


def main():
    parser = argparse.ArgumentParser(
        description="Analyze manuscript outline compatibility with journal scope"
    )
    parser.add_argument(
        "--outline",
        required=True,
        help="Path to outline file or workflow state"
    )
    parser.add_argument(
        "--journal",
        required=True,
        help="Journal identifier (e.g., 'bioinformatics')"
    )
    parser.add_argument(
        "--guidelines",
        required=True,
        help="Path to journal_guidelines.yaml"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable detailed scoring output"
    )

    args = parser.parse_args()

    try:
        # Load data
        outline = load_outline(args.outline)
        guidelines = load_journal_guidelines(args.guidelines, args.journal)

        # Extract keywords from outline
        outline_keywords = extract_keywords(outline['text'])

        # Score keyword match
        keyword_score, keyword_details = score_keyword_match(
            outline_keywords,
            guidelines.get('suitability_keywords', {})
        )

        # Analyze structure
        structure_score, structure_details = analyze_structure(
            outline['text'],
            guidelines['structure'].get('required_sections', [])
        )

        # Calculate overall compatibility
        compatibility_score = calculate_compatibility_score(keyword_score, structure_score)

        # Generate recommendations
        recommendations = generate_recommendations(
            compatibility_score,
            keyword_details,
            structure_details,
            guidelines['name']
        )

        # Prepare output
        result = {
            "journal": args.journal,
            "journal_name": guidelines['name'],
            "compatibility_score": round(compatibility_score, 3),
            "keyword_score": round(keyword_score, 3),
            "structure_score": round(structure_score, 3),
            "recommendations": recommendations,
            "analysis": {
                "keywords": keyword_details,
                "structure": structure_details
            }
        }

        if args.verbose:
            result["debug"] = {
                "outline_path": outline['path'],
                "outline_keywords_count": len(outline_keywords),
                "outline_keywords_sample": sorted(list(outline_keywords))[:20]
            }

        # Output JSON
        print(json.dumps(result, indent=2))

        # Exit code based on compatibility
        sys.exit(0 if compatibility_score >= 0.7 else 1)

    except Exception as e:
        error_result = {
            "error": str(e),
            "journal": args.journal,
            "compatibility_score": 0.0
        }
        print(json.dumps(error_result, indent=2), file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
