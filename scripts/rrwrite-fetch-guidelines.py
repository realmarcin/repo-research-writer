#!/usr/bin/env python3
"""Fetch comprehensive author guidelines for a journal.

This script extracts journal-specific requirements from the guidelines
database and formats them as a comprehensive markdown document.
"""

import argparse
import yaml
from pathlib import Path
from datetime import datetime
import sys


def format_word_limit(limit_value):
    """Format word limit for display.

    Args:
        limit_value: Int (specific limit) or 0 (no limit)

    Returns:
        Formatted string
    """
    if isinstance(limit_value, int):
        return f"{limit_value} words" if limit_value > 0 else "No strict limit"
    elif isinstance(limit_value, dict):
        min_val = limit_value.get('min', 0)
        max_val = limit_value.get('max', 'unlimited')
        if max_val == 'unlimited' or max_val == 0:
            return f"At least {min_val} words" if min_val > 0 else "No strict limit"
        return f"{min_val}-{max_val} words"
    return "Not specified"


def fetch_guidelines(journal_name, guidelines_yaml_path):
    """Fetch and format guidelines from YAML database.

    Args:
        journal_name: Name or key of the journal
        guidelines_yaml_path: Path to journal_guidelines.yaml

    Returns:
        Formatted markdown string with comprehensive guidelines

    Raises:
        ValueError: If journal not found in database
    """
    # Load guidelines database
    try:
        with open(guidelines_yaml_path) as f:
            all_guidelines = yaml.safe_load(f)
    except Exception as e:
        raise ValueError(f"Error loading guidelines database: {e}")

    # Find journal (case-insensitive, handle spaces/underscores)
    journal_key = journal_name.lower().replace(' ', '_')
    journal_data = all_guidelines.get('journals', {}).get(journal_key)

    if not journal_data:
        available = ', '.join(all_guidelines.get('journals', {}).keys())
        raise ValueError(
            f"Journal '{journal_name}' not found in guidelines database. "
            f"Available journals: {available}"
        )

    # Build markdown document
    md = f"""# Author Guidelines: {journal_data['full_name']}

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Source**: {journal_data.get('author_guidelines_url', 'Internal database')}

---

## Journal Scope

{journal_data.get('full_name')} publishes research in the following areas:

"""

    for scope_item in journal_data.get('scope', []):
        md += f"- {scope_item}\n"

    # Required Structure
    md += """

## Manuscript Structure

"""

    # Section order
    section_order = journal_data.get('structure', {}).get('section_order', [])
    if section_order:
        md += "### Required Section Order:\n\n"
        for i, section in enumerate(section_order, 1):
            section_display = section.replace('_', ' ').title()
            md += f"{i}. **{section_display}**\n"
        md += "\n"

    # Required vs optional sections
    required_sections = journal_data.get('structure', {}).get('required_sections', [])
    optional_sections = journal_data.get('structure', {}).get('optional_sections', [])

    if required_sections:
        md += "### Required Sections:\n\n"
        for section in required_sections:
            section_display = section.replace('_', ' ').title()
            md += f"- {section_display}\n"
        md += "\n"

    if optional_sections:
        md += "### Optional Sections:\n\n"
        for section in optional_sections:
            section_display = section.replace('_', ' ').title()
            md += f"- {section_display}\n"
        md += "\n"

    # Word Limits
    word_limits = journal_data.get('word_limits', {})
    if word_limits:
        md += "## Word Limits\n\n"

        total_limit = word_limits.get('total', 0)
        md += f"**Total manuscript**: {format_word_limit(total_limit)}\n\n"

        md += "### Section-Specific Limits:\n\n"
        for section, limits in word_limits.items():
            if section == 'total':
                continue
            section_display = section.replace('_', ' ').title()
            md += f"- **{section_display}**: {format_word_limit(limits)}\n"

        md += "\n"

    # Formatting Requirements
    formatting = journal_data.get('formatting', {})
    if formatting:
        md += "## Formatting Requirements\n\n"

        citation_style = formatting.get('citation_style', 'Not specified')
        md += f"- **Citation style**: {citation_style}\n"

        ref_limit = formatting.get('reference_limit', 0)
        if ref_limit > 0:
            md += f"- **Reference limit**: {ref_limit} references maximum\n"
        else:
            md += f"- **Reference limit**: No formal limit\n"

        fig_limit = formatting.get('figure_limit', 0)
        if fig_limit > 0:
            md += f"- **Figure limit**: {fig_limit} figures maximum\n"

        table_limit = formatting.get('table_limit', 0)
        if table_limit > 0:
            md += f"- **Table limit**: {table_limit} tables maximum\n"

        if formatting.get('line_spacing'):
            md += f"- **Line spacing**: {formatting['line_spacing']}\n"

        if formatting.get('font'):
            md += f"- **Font**: {formatting['font']}\n"

        md += "\n"

    # Special Requirements
    special_reqs = journal_data.get('special_requirements', [])
    if special_reqs:
        md += "## Special Requirements\n\n"
        for req in special_reqs:
            md += f"- {req}\n"
        md += "\n"

    # Section-Specific Citation Rules
    citation_rules = journal_data.get('citation_rules', {})
    if citation_rules:
        md += "## Section-Specific Citation Guidelines\n\n"
        for section, rule in citation_rules.items():
            section_display = section.replace('_', ' ').title()
            md += f"**{section_display}**: {rule}\n\n"

    # Compliance Checklist
    md += "## Pre-Submission Compliance Checklist\n\n"
    md += "Before submitting your manuscript, verify the following:\n\n"

    # General checks
    md += "### Structure and Format:\n"
    md += f"- [ ] All required sections present and in correct order\n"

    total_limit = word_limits.get('total', 0)
    if total_limit > 0:
        md += f"- [ ] Total word count ≤ {total_limit} words\n"

    for section, limits in word_limits.items():
        if section == 'total':
            continue
        section_display = section.replace('_', ' ').title()
        if isinstance(limits, dict):
            min_val = limits.get('min', 0)
            max_val = limits.get('max', 0)
            if max_val > 0:
                md += f"- [ ] {section_display}: {min_val}-{max_val} words\n"

    md += "\n### Citations and References:\n"
    md += f"- [ ] Citations formatted in {formatting.get('citation_style', 'required')} style\n"

    if formatting.get('reference_limit', 0) > 0:
        md += f"- [ ] References ≤ {formatting['reference_limit']}\n"

    md += "\n### Figures and Tables:\n"
    if formatting.get('figure_limit', 0) > 0:
        md += f"- [ ] Figures ≤ {formatting['figure_limit']}\n"
    if formatting.get('table_limit', 0) > 0:
        md += f"- [ ] Tables ≤ {formatting['table_limit']}\n"
    md += "- [ ] All figures and tables referenced in text\n"
    md += "- [ ] Figures referenced in numerical order\n"

    md += "\n### Journal-Specific Requirements:\n"
    for req in special_reqs[:10]:  # Limit to top 10 for checklist
        md += f"- [ ] {req}\n"

    md += f"\n### Additional Resources:\n\n"
    md += f"For complete submission guidelines, visit:\n{journal_data.get('author_guidelines_url', 'N/A')}\n"

    return md


def main():
    parser = argparse.ArgumentParser(
        description='Fetch and format journal author guidelines',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --journal bioinformatics --guidelines templates/journal_guidelines.yaml --output author_guidelines.md
  %(prog)s --journal "Nature Methods" --guidelines guidelines.yaml --output guidelines.md
        """
    )
    parser.add_argument('--journal', required=True, help='Journal name (e.g., bioinformatics, "Nature Methods")')
    parser.add_argument('--guidelines', required=True, help='Path to journal_guidelines.yaml')
    parser.add_argument('--output', required=True, help='Output markdown file path')
    args = parser.parse_args()

    # Validate guidelines file
    guidelines_path = Path(args.guidelines)
    if not guidelines_path.exists():
        print(f"Error: Guidelines file not found: {args.guidelines}", file=sys.stderr)
        return 1

    # Fetch and format guidelines
    try:
        guidelines_md = fetch_guidelines(args.journal, args.guidelines)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1

    # Write output
    try:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(guidelines_md)
        print(f"✓ Author guidelines written to: {args.output}")
        return 0
    except Exception as e:
        print(f"Error writing output: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
