#!/usr/bin/env python3
"""
RRWrite Manuscript Assembler

Assembles complete manuscript from individual section files.
Concatenates sections in journal-specified order, adds metadata,
and generates statistics.

Usage:
    rrwrite-assemble-manuscript.py --target-dir DIR [--journal JOURNAL] [--output FILE]

Output:
    Complete manuscript.md with all sections in correct order
"""

import argparse
import json
import re
import sys
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class ManuscriptAssembler:
    """Assembles manuscript from component sections."""

    def __init__(self, target_dir: str, journal: Optional[str] = None):
        """Initialize assembler.

        Args:
            target_dir: Directory containing manuscript sections
            journal: Target journal name (loads from state if not provided)
        """
        self.target_dir = Path(target_dir).resolve()
        self.journal = journal

        # Load workflow state
        self.state = self._load_state()

        # Determine journal
        if not self.journal:
            self.journal = self.state.get("target_journal")

        # Load journal guidelines if available
        self.guidelines = self._load_guidelines()

        # Track assembly manifest
        self.manifest = {
            "assembled_at": datetime.now().isoformat(),
            "target_journal": self.journal,
            "sections_included": [],
            "sections_missing": [],
            "total_word_count": 0,
            "section_word_counts": {},
            "validation_warnings": []
        }

    def _load_state(self) -> Dict:
        """Load workflow state."""
        state_file = self.target_dir / ".rrwrite" / "state.json"

        if not state_file.exists():
            return {}

        with open(state_file, 'r') as f:
            return json.load(f)

    def _load_guidelines(self) -> Optional[Dict]:
        """Load journal guidelines if available."""
        guidelines_file = self.target_dir / "author_guidelines.md"

        if not guidelines_file.exists():
            return None

        # Also try to load YAML for section order
        yaml_file = Path(__file__).parent.parent / "templates" / "journal_guidelines.yaml"

        if yaml_file.exists() and self.journal:
            try:
                with open(yaml_file, 'r') as f:
                    all_guidelines = yaml.safe_load(f)

                journal_key = self.journal.lower().replace(' ', '_')
                if journal_key in all_guidelines.get('journals', {}):
                    return all_guidelines['journals'][journal_key]
            except Exception as e:
                print(f"Warning: Could not load journal guidelines from YAML: {e}", file=sys.stderr)

        return None

    def get_section_order(self) -> List[str]:
        """Get section order for manuscript assembly.

        Returns:
            List of section names in correct order
        """
        # Try to get from guidelines
        if self.guidelines and 'structure' in self.guidelines:
            order = self.guidelines['structure'].get('section_order', [])
            if order:
                # Normalize section names (lowercase, replace spaces with underscores)
                return [s.lower().replace(' ', '_') for s in order]

        # Default order if no guidelines available
        default_order = [
            'abstract',
            'introduction',
            'methods',
            'results',
            'discussion',
            'conclusion',
            'data_availability',
            'code_availability',
            'acknowledgements',
            'funding',
            'references'
        ]

        return default_order

    def find_section_file(self, section_name: str) -> Optional[Path]:
        """Find file for a section.

        Args:
            section_name: Name of section to find

        Returns:
            Path to section file if found, None otherwise
        """
        # Try exact match
        candidates = [
            self.target_dir / f"{section_name}.md",
            self.target_dir / f"{section_name.replace('_', '-')}.md",
            self.target_dir / f"{section_name.replace('_', ' ')}.md"
        ]

        # Also try common variations
        variations = {
            'methods': ['methods', 'materials_and_methods', 'experimental_procedures'],
            'data_availability': ['data_availability', 'availability', 'availability_and_requirements'],
            'code_availability': ['code_availability', 'software_availability'],
            'acknowledgements': ['acknowledgements', 'acknowledgments'],
            'references': ['references', 'bibliography']
        }

        if section_name in variations:
            for variant in variations[section_name]:
                candidates.append(self.target_dir / f"{variant}.md")

        for candidate in candidates:
            if candidate.exists():
                return candidate

        return None

    def read_section(self, section_file: Path) -> Tuple[str, int]:
        """Read section content and count words.

        Args:
            section_file: Path to section file

        Returns:
            Tuple of (content, word_count)
        """
        content = section_file.read_text()

        # Count words (exclude markdown headers, citations)
        text_only = re.sub(r'#+\s+', '', content)  # Remove headers
        text_only = re.sub(r'\[.*?\]', '', text_only)  # Remove citations
        text_only = re.sub(r'\*\*|\*|__|_', '', text_only)  # Remove formatting

        words = text_only.split()
        word_count = len(words)

        return content, word_count

    def generate_header(self) -> str:
        """Generate manuscript header with metadata.

        Returns:
            Header markdown string
        """
        header_lines = []

        # Title (from state or default)
        title = self.state.get('manuscript_title', 'Manuscript Title')
        header_lines.append(f"# {title}\n")

        # Authors (from state or placeholder)
        authors = self.state.get('authors', ['Author Name'])
        if isinstance(authors, list):
            header_lines.append(", ".join(authors) + "\n")
        else:
            header_lines.append(str(authors) + "\n")

        # Metadata
        header_lines.append(f"\n**Target Journal**: {self.journal or 'Not specified'}")
        header_lines.append(f"**Assembled**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        header_lines.append(f"**Total Word Count**: (calculated after assembly)\n")

        # Separator
        header_lines.append("\n---\n\n")

        return "\n".join(header_lines)

    def assemble(self, output_file: Optional[str] = None) -> str:
        """Assemble complete manuscript.

        Args:
            output_file: Optional path to save manuscript (default: {target_dir}/manuscript.md)

        Returns:
            Complete manuscript content
        """
        if not output_file:
            output_file = self.target_dir / "manuscript.md"
        else:
            output_file = Path(output_file)

        print(f"Assembling manuscript for: {self.journal or 'default format'}")
        print(f"Target directory: {self.target_dir}")

        # Get section order
        section_order = self.get_section_order()
        print(f"\nSection order ({len(section_order)} sections):")
        for i, section in enumerate(section_order, 1):
            print(f"  {i}. {section}")

        # Assemble content
        manuscript_parts = []

        # Add header
        header = self.generate_header()
        manuscript_parts.append(header)

        # Add sections in order
        total_words = 0

        for section_name in section_order:
            section_file = self.find_section_file(section_name)

            if section_file:
                print(f"\n✓ Found: {section_name} ({section_file.name})")

                content, word_count = self.read_section(section_file)

                # Add section separator
                manuscript_parts.append(f"\n\n<!-- Section: {section_name} -->\n\n")

                # Add content
                manuscript_parts.append(content)

                # Track in manifest
                self.manifest['sections_included'].append({
                    'name': section_name,
                    'file': str(section_file.name),
                    'word_count': word_count
                })
                self.manifest['section_word_counts'][section_name] = word_count
                total_words += word_count

                print(f"  Word count: {word_count}")

            else:
                print(f"\n⚠ Missing: {section_name}")
                self.manifest['sections_missing'].append(section_name)

                # Check if this is a required section
                if self.guidelines:
                    required = self.guidelines.get('structure', {}).get('required_sections', [])
                    required_normalized = [s.lower().replace(' ', '_') for s in required]

                    if section_name in required_normalized:
                        warning = f"Required section missing: {section_name}"
                        self.manifest['validation_warnings'].append(warning)
                        print(f"  ❌ REQUIRED by {self.journal}")

        # Update total word count
        self.manifest['total_word_count'] = total_words

        # Update header with actual word count
        complete_manuscript = "".join(manuscript_parts)
        complete_manuscript = complete_manuscript.replace(
            "**Total Word Count**: (calculated after assembly)",
            f"**Total Word Count**: {total_words:,} words"
        )

        # Add assembly manifest as comment at end
        manifest_comment = "\n\n<!-- Assembly Manifest\n"
        manifest_comment += json.dumps(self.manifest, indent=2)
        manifest_comment += "\n-->\n"
        complete_manuscript += manifest_comment

        # Write to file
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(complete_manuscript)

        print(f"\n{'='*60}")
        print(f"✓ Manuscript assembled successfully!")
        print(f"{'='*60}")
        print(f"\nOutput: {output_file}")
        print(f"Total word count: {total_words:,} words")
        print(f"Sections included: {len(self.manifest['sections_included'])}")
        print(f"Sections missing: {len(self.manifest['sections_missing'])}")

        if self.manifest['validation_warnings']:
            print(f"\n⚠ Warnings: {len(self.manifest['validation_warnings'])}")
            for warning in self.manifest['validation_warnings']:
                print(f"  - {warning}")

        # Save manifest separately
        manifest_file = output_file.parent / "assembly_manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(self.manifest, f, indent=2)
        print(f"\nManifest saved: {manifest_file}")

        return complete_manuscript

    def validate_word_limits(self) -> List[str]:
        """Validate word counts against journal limits.

        Returns:
            List of validation messages
        """
        messages = []

        if not self.guidelines or 'word_limits' not in self.guidelines:
            return ["No word limit guidelines available"]

        word_limits = self.guidelines['word_limits']

        # Check total word count
        if 'total' in word_limits:
            limit = word_limits['total']
            actual = self.manifest['total_word_count']

            if isinstance(limit, dict):
                min_words = limit.get('min', 0)
                max_words = limit.get('max', float('inf'))

                if actual < min_words:
                    messages.append(f"⚠ Total word count below minimum: {actual} < {min_words}")
                elif actual > max_words:
                    messages.append(f"❌ Total word count exceeds maximum: {actual} > {max_words}")
                else:
                    messages.append(f"✓ Total word count within limits: {actual} words ({min_words}-{max_words})")
            elif isinstance(limit, int) and limit > 0:
                if actual > limit:
                    messages.append(f"❌ Total word count exceeds limit: {actual} > {limit}")
                else:
                    messages.append(f"✓ Total word count within limit: {actual}/{limit}")

        # Check section word counts
        for section_name, count in self.manifest['section_word_counts'].items():
            if section_name in word_limits:
                limit = word_limits[section_name]

                if isinstance(limit, dict):
                    min_words = limit.get('min', 0)
                    max_words = limit.get('max', float('inf'))

                    if count < min_words:
                        messages.append(f"⚠ {section_name}: {count} words < {min_words} (minimum)")
                    elif count > max_words:
                        messages.append(f"❌ {section_name}: {count} words > {max_words} (maximum)")
                    else:
                        messages.append(f"✓ {section_name}: {count} words (within {min_words}-{max_words})")

        return messages


def main():
    """CLI interface for manuscript assembler."""
    parser = argparse.ArgumentParser(
        description="Assemble complete manuscript from component sections",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --target-dir manuscript/repo_v1
  %(prog)s --target-dir manuscript/repo_v1 --journal bioinformatics
  %(prog)s --target-dir manuscript/repo_v1 --output final_manuscript.md
  %(prog)s --target-dir manuscript/repo_v1 --validate
        """
    )
    parser.add_argument(
        "--target-dir",
        required=True,
        help="Directory containing manuscript sections"
    )
    parser.add_argument(
        "--journal",
        help="Target journal name (uses state if not provided)"
    )
    parser.add_argument(
        "--output",
        help="Output file path (default: {target_dir}/manuscript.md)"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate word counts against journal limits"
    )

    args = parser.parse_args()

    try:
        # Create assembler
        assembler = ManuscriptAssembler(
            target_dir=args.target_dir,
            journal=args.journal
        )

        # Assemble manuscript
        assembler.assemble(output_file=args.output)

        # Validate if requested
        if args.validate:
            print(f"\n{'='*60}")
            print("Word Count Validation")
            print(f"{'='*60}\n")

            validation_messages = assembler.validate_word_limits()
            for message in validation_messages:
                print(message)

        sys.exit(0)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
