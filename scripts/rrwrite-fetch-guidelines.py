#!/usr/bin/env python3
"""
RRWrite Guidelines Fetcher

Loads journal guidelines from YAML database and formats comprehensive markdown document.

Usage:
    rrwrite-fetch-guidelines.py --journal JOURNAL --guidelines YAML [--output PATH]

Arguments:
    --journal NAME      Journal identifier (e.g., 'bioinformatics')
    --guidelines PATH   Path to journal_guidelines.yaml
    --output PATH      Output path for markdown file (optional, prints to stdout if not provided)

Output:
    Markdown document with comprehensive journal guidelines and compliance checklist
"""

import argparse
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Any


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


def format_section_list(items: List[str], indent: int = 0) -> str:
    """Format a list of items as markdown."""
    prefix = "  " * indent
    return "\n".join([f"{prefix}- {item}" for item in items])


def format_word_limits(limits: Dict[str, Any]) -> str:
    """Format word limits section."""
    lines = []

    for section, limit in limits.items():
        if isinstance(limit, dict):
            min_words = limit.get('min', 'N/A')
            max_words = limit.get('max', 'N/A')
            lines.append(f"- **{section.replace('_', ' ').title()}**: {min_words}-{max_words} words")
        else:
            lines.append(f"- **{section.replace('_', ' ').title()}**: {limit}")

    return "\n".join(lines)


def format_citation_rules(rules: Dict[str, List[str]]) -> str:
    """Format citation rules by section."""
    lines = []

    for section, guidelines in rules.items():
        lines.append(f"\n**{section.title()}:**")
        lines.append(format_section_list(guidelines))

    return "\n".join(lines)


def generate_compliance_checklist(guidelines: Dict) -> str:
    """Generate a compliance checklist for the journal."""
    checklist = ["## Compliance Checklist", ""]

    # Structure requirements
    checklist.append("### Structure")
    required = guidelines['structure'].get('required_sections', [])
    for section in required:
        checklist.append(f"- [ ] {section} section included")
    checklist.append("")

    # Word limits
    checklist.append("### Word Limits")
    word_limits = guidelines.get('word_limits', {})
    for section, limit in word_limits.items():
        if isinstance(limit, dict):
            min_words = limit.get('min', 'N/A')
            max_words = limit.get('max', 'N/A')
            checklist.append(f"- [ ] {section.replace('_', ' ').title()}: {min_words}-{max_words} words")
    checklist.append("")

    # Formatting
    checklist.append("### Formatting")
    formatting = guidelines.get('formatting', {})
    if 'citation_style' in formatting:
        checklist.append(f"- [ ] Citations formatted as {formatting['citation_style']}")
    if 'reference_limit' in formatting:
        checklist.append(f"- [ ] References ≤ {formatting['reference_limit']}")
    if 'figure_limit' in formatting:
        checklist.append(f"- [ ] Figures ≤ {formatting['figure_limit']}")
    if 'table_limit' in formatting:
        checklist.append(f"- [ ] Tables ≤ {formatting['table_limit']}")
    checklist.append("")

    # Special requirements
    special_reqs = guidelines.get('special_requirements', [])
    if special_reqs:
        checklist.append("### Special Requirements")
        for req in special_reqs:
            checklist.append(f"- [ ] {req}")
        checklist.append("")

    # Citation rules
    citation_rules = guidelines.get('citation_rules', {})
    if citation_rules:
        checklist.append("### Citation Guidelines")
        for section in citation_rules.keys():
            checklist.append(f"- [ ] {section.title()} citations follow guidelines")
        checklist.append("")

    return "\n".join(checklist)


def generate_markdown(guidelines: Dict, journal_id: str) -> str:
    """Generate comprehensive markdown guidelines document."""
    lines = []

    # Title
    lines.append(f"# {guidelines['name']} - Author Guidelines")
    lines.append("")
    lines.append(f"**Publisher:** {guidelines['publisher']}")
    lines.append(f"**Journal ID:** {journal_id}")
    lines.append("")

    # Official guidelines link
    if 'author_guidelines_url' in guidelines:
        lines.append(f"**Official Guidelines:** {guidelines['author_guidelines_url']}")
        lines.append("")

    # Scope
    lines.append("## Scope")
    lines.append("")
    lines.append("This journal publishes research in:")
    lines.append(format_section_list(guidelines['scope']))
    lines.append("")

    # Structure
    lines.append("## Manuscript Structure")
    lines.append("")

    structure = guidelines['structure']

    if 'required_sections' in structure:
        lines.append("### Required Sections")
        lines.append(format_section_list(structure['required_sections']))
        lines.append("")

    if 'optional_sections' in structure:
        lines.append("### Optional Sections")
        lines.append(format_section_list(structure['optional_sections']))
        lines.append("")

    if 'section_order' in structure:
        lines.append("### Recommended Section Order")
        for i, section in enumerate(structure['section_order'], start=1):
            lines.append(f"{i}. {section}")
        lines.append("")

    # Word limits
    if 'word_limits' in guidelines:
        lines.append("## Word Limits")
        lines.append("")
        lines.append(format_word_limits(guidelines['word_limits']))
        lines.append("")

    # Formatting
    if 'formatting' in guidelines:
        lines.append("## Formatting Requirements")
        lines.append("")
        formatting = guidelines['formatting']

        if 'citation_style' in formatting:
            lines.append(f"- **Citation Style:** {formatting['citation_style']}")
        if 'reference_limit' in formatting:
            lines.append(f"- **Reference Limit:** {formatting['reference_limit']}")
        if 'figure_limit' in formatting:
            lines.append(f"- **Figure Limit:** {formatting['figure_limit']}")
        if 'table_limit' in formatting:
            lines.append(f"- **Table Limit:** {formatting['table_limit']}")
        if 'supplementary_limit' in formatting:
            lines.append(f"- **Supplementary Items Limit:** {formatting['supplementary_limit']}")
        lines.append("")

    # Special requirements
    if 'special_requirements' in guidelines:
        lines.append("## Special Requirements")
        lines.append("")
        lines.append(format_section_list(guidelines['special_requirements']))
        lines.append("")

    # Citation rules
    if 'citation_rules' in guidelines:
        lines.append("## Citation Guidelines by Section")
        lines.append("")
        lines.append(format_citation_rules(guidelines['citation_rules']))
        lines.append("")

    # Suitability keywords
    if 'suitability_keywords' in guidelines:
        lines.append("## Suitability Keywords")
        lines.append("")
        keywords = guidelines['suitability_keywords']

        if 'positive' in keywords:
            lines.append("### Positive Indicators")
            lines.append("Manuscripts focusing on these topics are typically suitable:")
            lines.append(format_section_list(keywords['positive']))
            lines.append("")

        if 'negative' in keywords:
            lines.append("### Negative Indicators")
            lines.append("Manuscripts primarily focused on these topics may not be suitable:")
            lines.append(format_section_list(keywords['negative']))
            lines.append("")

    # Compliance checklist
    lines.append(generate_compliance_checklist(guidelines))

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch and format journal author guidelines"
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
        "--output",
        help="Output path for markdown file (prints to stdout if not provided)"
    )

    args = parser.parse_args()

    try:
        # Load guidelines
        guidelines = load_journal_guidelines(args.guidelines, args.journal)

        # Generate markdown
        markdown = generate_markdown(guidelines, args.journal)

        # Output
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(markdown)
            print(f"Guidelines written to: {output_path}", file=sys.stderr)
        else:
            print(markdown)

        sys.exit(0)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
