#!/usr/bin/env python3
"""
Unit tests for RRWrite revision parser.

Tests parsing of critique reports and issue extraction.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from rrwrite_revision_parser import CritiqueParser, Issue


class TestCritiqueParser(unittest.TestCase):
    """Test critique report parsing."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir)

    def test_parse_content_critique(self):
        """Test parsing of content critique file."""
        # Create sample critique file
        critique_content = """# Content Review Report (Stage 1)

**Reviewed:** 2026-02-09 18:53
**Manuscript:** manuscript/test/manuscript_full.md
**Focus:** Scientific validity, argument strength, evidence quality

## Summary Assessment

Found 3 major content issues requiring revision. 1 minor issue could improve clarity.

## Major Issues (Content)

1. **Evidence:** Strong claim without evidence: "Validation through the MP_plus v10 system demonstrates 100% precision"
   - **Impact:** Unsupported claims undermine credibility
   - **Action:** Add citation or data reference to support claim

2. **Reproducibility:** Methods missing reproducibility elements: software versions, parameters, data sources, code availability
   - **Impact:** Work cannot be reproduced by others
   - **Action:** Add missing elements: software versions, parameters, data sources, code availability

3. **Evidence:** Strong claim without evidence: "MicroGrowAgents demonstrates that AI-powered integration"
   - **Impact:** Unsupported claims undermine credibility
   - **Action:** Add citation or data reference to support claim

## Minor Issues (Content)

1. **Coherence:** Section 3 lacks transitional references
   - **Action:** Add transitional phrases linking to previous/next sections
"""

        critique_file = self.test_dir / "critique_content_v1.md"
        critique_file.write_text(critique_content)

        # Parse
        parser = CritiqueParser(self.test_dir)
        issues = parser.parse_content_critique(critique_file)

        # Verify
        self.assertEqual(len(issues), 4)

        # Check major issues
        major_issues = [i for i in issues if i.severity == "major"]
        self.assertEqual(len(major_issues), 3)

        # Check first issue
        self.assertEqual(major_issues[0].category, "Evidence")
        self.assertIn("Validation through", major_issues[0].description)
        self.assertEqual(major_issues[0].action, "Add citation or data reference to support claim")

        # Check minor issues
        minor_issues = [i for i in issues if i.severity == "minor"]
        self.assertEqual(len(minor_issues), 1)
        self.assertEqual(minor_issues[0].category, "Coherence")

    def test_parse_format_critique(self):
        """Test parsing of format critique file."""
        # Create sample critique file
        critique_content = """# Format Review Report (Stage 2)

**Reviewed:** 2026-02-09 18:53
**Manuscript:** manuscript/test/manuscript_full.md
**Target Journal:** Nature
**Focus:** Citations, structure, journal requirements

## Summary Assessment

Found 2 formatting issues requiring correction. No warnings.

## Formatting Issues

1. **Citation Format:** Malformed citation: [References will be generated from literature_citat...]
   - **Action:** Use [author2024] format for citations

2. **Word Count:** Abstract has 151 words, exceeds Nature limit of 150
   - **Action:** Reduce abstract to 150 words or fewer
"""

        critique_file = self.test_dir / "critique_format_v1.md"
        critique_file.write_text(critique_content)

        # Parse
        parser = CritiqueParser(self.test_dir)
        issues = parser.parse_format_critique(critique_file)

        # Verify
        self.assertEqual(len(issues), 2)

        # All should be major (formatting issues)
        for issue in issues:
            self.assertEqual(issue.severity, "major")

        # Check issue categories
        categories = [i.category for i in issues]
        self.assertIn("Citation Format", categories)
        self.assertIn("Word Count", categories)

    def test_count_issues(self):
        """Test issue counting."""
        issues = [
            Issue(severity="major", category="Evidence", description="Test 1", action="Fix 1"),
            Issue(severity="major", category="Evidence", description="Test 2", action="Fix 2"),
            Issue(severity="minor", category="Coherence", description="Test 3", action="Fix 3"),
        ]

        parser = CritiqueParser(self.test_dir)
        counts = parser.count_issues(issues)

        self.assertEqual(counts["major"], 2)
        self.assertEqual(counts["minor"], 1)

    def test_group_by_section(self):
        """Test grouping issues by section."""
        issues = [
            Issue(severity="major", category="Evidence", description="Test 1", action="Fix 1", section="introduction"),
            Issue(severity="major", category="Evidence", description="Test 2", action="Fix 2", section="methods"),
            Issue(severity="minor", category="Coherence", description="Test 3", action="Fix 3", section="introduction"),
        ]

        parser = CritiqueParser(self.test_dir)
        grouped = parser.group_by_section(issues)

        self.assertEqual(len(grouped), 2)
        self.assertEqual(len(grouped["introduction"]), 2)
        self.assertEqual(len(grouped["methods"]), 1)

    def test_infer_section_from_word_count(self):
        """Test section inference from word count description."""
        parser = CritiqueParser(self.test_dir)

        # Abstract word count
        issue = Issue(
            severity="major",
            category="Word Count",
            description="Abstract has 151 words, exceeds Nature limit of 150",
            action="Reduce to 150 words"
        )
        section = parser._extract_section_from_word_count(issue.description)
        self.assertEqual(section, "abstract")

        # Introduction word count
        issue = Issue(
            severity="major",
            category="Word Count",
            description="Introduction exceeds limit",
            action="Reduce word count"
        )
        section = parser._extract_section_from_word_count(issue.description)
        self.assertEqual(section, "introduction")

    def test_category_to_section_mapping(self):
        """Test category-based section inference."""
        parser = CritiqueParser(self.test_dir)

        # Reproducibility -> methods
        issue = Issue(
            severity="major",
            category="Reproducibility",
            description="Missing software versions",
            action="Add versions"
        )
        section = parser.infer_section_from_issue(issue)
        self.assertEqual(section, "methods")

        # Evidence -> manuscript_full (needs context)
        issue = Issue(
            severity="major",
            category="Evidence",
            description="Strong claim without evidence",
            action="Add citation"
        )
        section = parser.infer_section_from_issue(issue)
        self.assertEqual(section, "manuscript_full")


class TestIssueDataclass(unittest.TestCase):
    """Test Issue dataclass."""

    def test_issue_creation(self):
        """Test creating an Issue object."""
        issue = Issue(
            severity="major",
            category="Evidence",
            description="Test description",
            action="Test action",
            section="introduction"
        )

        self.assertEqual(issue.severity, "major")
        self.assertEqual(issue.category, "Evidence")
        self.assertEqual(issue.description, "Test description")
        self.assertEqual(issue.action, "Test action")
        self.assertEqual(issue.section, "introduction")

    def test_issue_string_representation(self):
        """Test Issue string representation."""
        issue = Issue(
            severity="major",
            category="Evidence",
            description="This is a very long description that should be truncated in the string representation",
            action="Fix it",
            section="introduction"
        )

        issue_str = str(issue)
        self.assertIn("MAJOR", issue_str)
        self.assertIn("Evidence", issue_str)
        # Should be truncated
        self.assertLess(len(issue_str), 100)


if __name__ == '__main__':
    unittest.main()
