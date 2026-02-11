#!/usr/bin/env python3
"""
RRWrite Revision Context Manager

Provides context for section revisers:
- Citation lookup from literature_evidence.csv
- Software version extraction from repository_analysis.md
- Journal guidelines
- Repository metadata
"""

import csv
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import logging


@dataclass
class Citation:
    """Represents a literature citation."""
    doi: str
    citation_key: str  # e.g., "author2024"
    evidence: str  # Quoted text supporting the claim

    def __str__(self):
        return f"[{self.citation_key}]"


class RevisionContext:
    """Provides context data for section revisers."""

    def __init__(self, manuscript_dir: Path):
        """Initialize revision context.

        Args:
            manuscript_dir: Path to manuscript directory
        """
        self.manuscript_dir = Path(manuscript_dir)
        self.logger = logging.getLogger(__name__)

        # Load context data
        self.citations = self._load_citations()
        self.guidelines = self._load_guidelines()
        self.repo_analysis = self._load_repo_analysis()
        self.software_versions = self._extract_software_versions()

    def _load_citations(self) -> List[Citation]:
        """Load citations from literature_evidence.csv.

        Returns:
            List of Citation objects
        """
        citations = []
        evidence_file = self.manuscript_dir / "literature_evidence.csv"

        if not evidence_file.exists():
            self.logger.warning(f"Literature evidence file not found: {evidence_file}")
            return citations

        try:
            with open(evidence_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    citation = Citation(
                        doi=row.get('doi', ''),
                        citation_key=row.get('citation_key', ''),
                        evidence=row.get('evidence', '')
                    )
                    citations.append(citation)

            self.logger.info(f"Loaded {len(citations)} citations from {evidence_file.name}")

        except Exception as e:
            self.logger.error(f"Failed to load citations: {e}")

        return citations

    def _load_guidelines(self) -> Optional[str]:
        """Load journal author guidelines.

        Returns:
            Guidelines content or None
        """
        # Look for author_guidelines.md
        guidelines_file = self.manuscript_dir / "author_guidelines.md"

        if not guidelines_file.exists():
            self.logger.warning(f"Author guidelines not found: {guidelines_file}")
            return None

        try:
            with open(guidelines_file, 'r', encoding='utf-8') as f:
                content = f.read()
            self.logger.info(f"Loaded guidelines from {guidelines_file.name}")
            return content

        except Exception as e:
            self.logger.error(f"Failed to load guidelines: {e}")
            return None

    def _load_repo_analysis(self) -> Optional[str]:
        """Load repository analysis.

        Returns:
            Repository analysis content or None
        """
        analysis_file = self.manuscript_dir / "repository_analysis.md"

        if not analysis_file.exists():
            self.logger.warning(f"Repository analysis not found: {analysis_file}")
            return None

        try:
            with open(analysis_file, 'r', encoding='utf-8') as f:
                content = f.read()
            self.logger.info(f"Loaded repository analysis from {analysis_file.name}")
            return content

        except Exception as e:
            self.logger.error(f"Failed to load repository analysis: {e}")
            return None

    def _extract_software_versions(self) -> Dict[str, str]:
        """Extract software versions from repository analysis.

        Returns:
            Dict mapping software names to versions
        """
        versions = {}

        if not self.repo_analysis:
            return versions

        # Pattern: "Software v1.2.3" or "Package (version 1.2.3)"
        patterns = [
            r'(\w+)\s+v?([\d.]+)',  # "Software v1.2.3" or "Software 1.2.3"
            r'(\w+)\s+\(version\s+([\d.]+)\)',  # "Package (version 1.2.3)"
        ]

        for pattern in patterns:
            matches = re.findall(pattern, self.repo_analysis, re.IGNORECASE)
            for name, version in matches:
                # Only keep if looks like a reasonable version (has digit)
                if re.search(r'\d', version):
                    versions[name.lower()] = version

        self.logger.info(f"Extracted {len(versions)} software versions")
        return versions

    def find_relevant_citations(self, query: str, max_results: int = 3) -> List[Citation]:
        """Find citations relevant to a query.

        Args:
            query: Search query (topic, claim, keyword)
            max_results: Maximum number of results to return

        Returns:
            List of Citation objects ranked by relevance
        """
        # Simple keyword matching (can be improved with embeddings)
        query_lower = query.lower()
        scored_citations = []

        for citation in self.citations:
            score = 0

            # Search in evidence text
            evidence_lower = citation.evidence.lower()

            # Count matching words
            query_words = set(re.findall(r'\w+', query_lower))
            evidence_words = set(re.findall(r'\w+', evidence_lower))
            matching_words = query_words & evidence_words

            score = len(matching_words)

            if score > 0:
                scored_citations.append((score, citation))

        # Sort by score (descending) and return top results
        scored_citations.sort(reverse=True, key=lambda x: x[0])
        return [cit for _, cit in scored_citations[:max_results]]

    def get_software_version(self, software_name: str) -> Optional[str]:
        """Get version for a specific software package.

        Args:
            software_name: Software package name

        Returns:
            Version string or None
        """
        return self.software_versions.get(software_name.lower())

    def get_all_software_versions(self) -> Dict[str, str]:
        """Get all extracted software versions.

        Returns:
            Dict mapping software names to versions
        """
        return self.software_versions.copy()

    def get_word_limit(self, section: str) -> Optional[int]:
        """Get word count limit for a section from guidelines.

        Args:
            section: Section name (e.g., 'abstract', 'introduction')

        Returns:
            Word limit or None
        """
        if not self.guidelines:
            return None

        # Search for word limits in guidelines
        # Pattern: "Abstract: 150 words" or "Abstract (max 150 words)"
        patterns = [
            rf'{section}[:\s]+(\d+)\s+words?',
            rf'{section}[:\s]+\(max[:\s]+(\d+)\s+words?\)',
            rf'{section}[:\s]+maximum[:\s]+(\d+)\s+words?',
        ]

        for pattern in patterns:
            match = re.search(pattern, self.guidelines, re.IGNORECASE)
            if match:
                return int(match.group(1))

        return None

    def get_citation_by_key(self, citation_key: str) -> Optional[Citation]:
        """Get citation by citation key.

        Args:
            citation_key: Citation key (e.g., "author2024")

        Returns:
            Citation object or None
        """
        for citation in self.citations:
            if citation.citation_key == citation_key:
                return citation
        return None

    def validate_citation_exists(self, citation_key: str) -> bool:
        """Check if a citation exists in literature_evidence.csv.

        Args:
            citation_key: Citation key (e.g., "author2024")

        Returns:
            True if citation exists
        """
        return self.get_citation_by_key(citation_key) is not None

    def extract_citations_from_text(self, text: str) -> List[str]:
        """Extract all citation keys from text.

        Args:
            text: Text containing citations in [author2024] format

        Returns:
            List of citation keys
        """
        # Pattern: [author2024] or [author2024,other2023]
        pattern = r'\[([a-zA-Z]+\d{4}(?:,[a-zA-Z]+\d{4})*)\]'
        matches = re.findall(pattern, text)

        # Split comma-separated citations
        citation_keys = []
        for match in matches:
            keys = [k.strip() for k in match.split(',')]
            citation_keys.extend(keys)

        return list(set(citation_keys))  # Remove duplicates

    def get_repository_path(self) -> Optional[str]:
        """Extract repository path from repository analysis.

        Returns:
            Repository path or None
        """
        if not self.repo_analysis:
            return None

        # Pattern: "**Repository**: /path/to/repo"
        match = re.search(r'\*\*Repository\*\*:\s+(.+?)(?:\n|$)', self.repo_analysis)
        if match:
            return match.group(1).strip()

        return None

    def get_data_tables(self) -> List[str]:
        """Extract data table file paths from repository analysis.

        Returns:
            List of data table file paths
        """
        tables = []

        if not self.repo_analysis:
            return tables

        # Look for markdown table or list of data files
        # Pattern: "- data/table_name.csv" or similar
        pattern = r'(?:data|tables?)/[\w/.-]+\.(?:csv|tsv|xlsx)'
        matches = re.findall(pattern, self.repo_analysis)

        return list(set(matches))  # Remove duplicates


def main():
    """CLI for testing revision context."""
    import argparse

    parser = argparse.ArgumentParser(description="Test RRWrite revision context")
    parser.add_argument("--manuscript-dir", required=True, help="Manuscript directory")
    parser.add_argument("--query", help="Search for citations matching query")
    parser.add_argument("--software", help="Get version for software package")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(levelname)s: %(message)s'
    )

    # Load context
    context = RevisionContext(args.manuscript_dir)

    print(f"\nRevision Context Summary:")
    print(f"  Citations loaded: {len(context.citations)}")
    print(f"  Guidelines loaded: {context.guidelines is not None}")
    print(f"  Repository analysis loaded: {context.repo_analysis is not None}")
    print(f"  Software versions found: {len(context.software_versions)}")

    # Query citations
    if args.query:
        print(f"\nSearching for citations matching: '{args.query}'")
        results = context.find_relevant_citations(args.query, max_results=5)
        print(f"Found {len(results)} relevant citations:")
        for cit in results:
            print(f"  - {cit}")
            if args.verbose:
                print(f"    Evidence: {cit.evidence[:100]}...")

    # Get software version
    if args.software:
        version = context.get_software_version(args.software)
        if version:
            print(f"\n{args.software}: v{version}")
        else:
            print(f"\nNo version found for: {args.software}")

    # Show all software versions
    if args.verbose and context.software_versions:
        print("\nAll software versions:")
        for name, version in sorted(context.software_versions.items()):
            print(f"  - {name}: {version}")


if __name__ == "__main__":
    main()
