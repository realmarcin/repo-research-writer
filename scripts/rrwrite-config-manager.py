#!/usr/bin/env python3
"""
RRWrite Configuration Manager

Manages word limits and other configuration settings for manuscript generation.

Usage:
    python scripts/rrwrite-config-manager.py --journal bioinformatics
    python scripts/rrwrite-config-manager.py --show
    python scripts/rrwrite-config-manager.py --section abstract
"""

import argparse
import sys
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Manages RRWrite configuration settings."""

    def __init__(self, config_file: Optional[str] = None, journal: Optional[str] = None):
        """
        Initialize configuration manager.

        Args:
            config_file: Path to custom config file (optional)
            journal: Target journal to apply preset (optional)
        """
        # Default config path
        script_dir = Path(__file__).parent
        default_config = script_dir.parent / 'templates' / 'manuscript_config.yaml'

        # Load configuration
        if config_file and Path(config_file).exists():
            self.config_path = Path(config_file)
        else:
            self.config_path = default_config

        self.config = self._load_config()

        # Apply journal preset if specified
        if journal:
            self.apply_journal_preset(journal)

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}", file=sys.stderr)
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Return minimal default configuration."""
        return {
            'manuscript': {
                'total_word_limit': 6000,
                'target_journal': 'bioinformatics'
            },
            'sections': {
                'abstract': {'min_words': 150, 'target_words': 200, 'max_words': 250},
                'introduction': {'min_words': 400, 'target_words': 600, 'max_words': 800},
                'methods': {'min_words': 800, 'target_words': 1200, 'max_words': 1600},
                'results': {'min_words': 600, 'target_words': 900, 'max_words': 1200},
                'discussion': {'min_words': 400, 'target_words': 700, 'max_words': 1000},
            }
        }

    def apply_journal_preset(self, journal: str) -> None:
        """Apply journal-specific preset configuration.

        Args:
            journal: Journal name (bioinformatics, nature, plos)
        """
        presets = self.config.get('journal_presets', {})

        if journal not in presets:
            print(f"Warning: No preset for journal '{journal}', using defaults", file=sys.stderr)
            return

        preset = presets[journal]

        # Merge manuscript settings
        if 'manuscript' in preset:
            self.config['manuscript'].update(preset['manuscript'])

        # Merge section settings
        if 'sections' in preset:
            for section, settings in preset['sections'].items():
                if section in self.config['sections']:
                    self.config['sections'][section].update(settings)

        # Update target journal
        self.config['manuscript']['target_journal'] = journal

    def get_total_word_limit(self) -> int:
        """Get total manuscript word limit."""
        return self.config['manuscript'].get('total_word_limit', 6000)

    def get_section_limits(self, section: str) -> Dict[str, int]:
        """Get word limits for a specific section.

        Args:
            section: Section name (abstract, introduction, etc.)

        Returns:
            Dictionary with min_words, target_words, max_words
        """
        sections = self.config.get('sections', {})

        if section not in sections:
            # Return defaults for unknown sections
            return {
                'min_words': 200,
                'target_words': 500,
                'max_words': 800
            }

        return sections[section]

    def get_section_target(self, section: str) -> int:
        """Get target word count for a section.

        Args:
            section: Section name

        Returns:
            Target word count
        """
        limits = self.get_section_limits(section)
        return limits.get('target_words', 500)

    def get_all_sections(self) -> Dict[str, Dict[str, Any]]:
        """Get all section configurations."""
        return self.config.get('sections', {})

    def get_literature_limits(self) -> Dict[str, int]:
        """Get literature review limits."""
        return self.config.get('literature', {
            'max_papers': 25,
            'min_papers': 15,
            'target_summary_words': 1000
        })

    def get_citation_settings(self) -> Dict[str, Any]:
        """Get citation requirements."""
        return self.config.get('citations', {
            'min_citations': 15,
            'max_citations': 50,
            'require_doi': True
        })

    def display_config(self) -> None:
        """Display current configuration."""
        print("=" * 60)
        print("RRWrite Configuration")
        print("=" * 60)
        print()

        # Manuscript settings
        manuscript = self.config.get('manuscript', {})
        print(f"Total Word Limit: {manuscript.get('total_word_limit', 'No limit')}")
        print(f"Target Journal: {manuscript.get('target_journal', 'Not specified')}")
        print()

        # Section limits
        print("Section Word Limits:")
        print("-" * 60)
        sections = self.config.get('sections', {})
        for section, limits in sections.items():
            required = limits.get('required', False)
            req_str = " (required)" if required else " (optional)"
            print(f"\n  {section.title()}{req_str}:")
            print(f"    Min: {limits.get('min_words', 'N/A')}")
            print(f"    Target: {limits.get('target_words', 'N/A')}")
            print(f"    Max: {limits.get('max_words', 'N/A')}")
            if 'notes' in limits:
                print(f"    Notes: {limits['notes']}")

        print()

        # Literature settings
        lit = self.get_literature_limits()
        print("Literature Review:")
        print("-" * 60)
        print(f"  Papers: {lit.get('min_papers')}-{lit.get('max_papers')}")
        print(f"  Summary words: {lit.get('target_summary_words')}")
        print()

    def export_for_skill(self, section: Optional[str] = None) -> str:
        """Export configuration as formatted text for skill consumption.

        Args:
            section: Specific section to export (optional)

        Returns:
            Formatted configuration text
        """
        output = []

        # Overall limits
        output.append("## Manuscript Configuration")
        output.append(f"- Total word limit: {self.get_total_word_limit()}")
        output.append(f"- Target journal: {self.config['manuscript'].get('target_journal')}")
        output.append("")

        # Section limits
        if section:
            limits = self.get_section_limits(section)
            output.append(f"## Word Limits for {section.title()}")
            output.append(f"- Minimum: {limits['min_words']} words")
            output.append(f"- Target: {limits['target_words']} words")
            output.append(f"- Maximum: {limits['max_words']} words")
            if 'notes' in limits:
                output.append(f"- Notes: {limits['notes']}")
        else:
            output.append("## Section Word Limits")
            for sec, limits in self.get_all_sections().items():
                output.append(f"- {sec.title()}: {limits['target_words']} words (range: {limits['min_words']}-{limits['max_words']})")

        return "\n".join(output)


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Manage RRWrite configuration settings"
    )
    parser.add_argument(
        '--config',
        help='Path to custom config file (default: templates/manuscript_config.yaml)'
    )
    parser.add_argument(
        '--journal',
        choices=['bioinformatics', 'nature', 'plos'],
        help='Apply journal-specific preset'
    )
    parser.add_argument(
        '--show',
        action='store_true',
        help='Display current configuration'
    )
    parser.add_argument(
        '--section',
        help='Show limits for specific section'
    )
    parser.add_argument(
        '--export',
        action='store_true',
        help='Export configuration for skill consumption'
    )

    args = parser.parse_args()

    # Create manager
    manager = ConfigManager(config_file=args.config, journal=args.journal)

    if args.show:
        manager.display_config()
    elif args.export:
        print(manager.export_for_skill(section=args.section))
    elif args.section:
        limits = manager.get_section_limits(args.section)
        print(f"Word limits for {args.section}:")
        print(f"  Minimum: {limits['min_words']}")
        print(f"  Target: {limits['target_words']}")
        print(f"  Maximum: {limits['max_words']}")
    else:
        # Default: show summary
        total = manager.get_total_word_limit()
        journal = manager.config['manuscript'].get('target_journal', 'Not set')
        print(f"Total word limit: {total}")
        print(f"Target journal: {journal}")
        print("\nUse --show for full configuration")

    return 0


if __name__ == '__main__':
    sys.exit(main())
