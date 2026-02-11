#!/usr/bin/env python3
"""
Integration tests for RRWrite revision workflow.

Tests the full revision loop on sample data.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from rrwrite_revision_parser import CritiqueParser
from rrwrite_revision_context import RevisionContext
from rrwrite_state_manager import StateManager


class TestRevisionIntegration(unittest.TestCase):
    """Integration tests for revision workflow."""

    def setUp(self):
        """Create temporary directory with sample files."""
        self.test_dir = Path(tempfile.mkdtemp())

        # Create sample critique files
        self._create_sample_critique_content()
        self._create_sample_critique_format()
        self._create_sample_literature_evidence()
        self._create_sample_section_files()

    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir)

    def _create_sample_critique_content(self):
        """Create sample content critique."""
        content = """# Content Review Report (Stage 1)

## Summary Assessment

Found 5 major content issues requiring revision. 2 minor issues.

## Major Issues (Content)

1. **Evidence:** Strong claim without evidence: "The system achieves 100% precision"
   - **Impact:** Unsupported claims undermine credibility
   - **Action:** Add citation or data reference to support claim

2. **Reproducibility:** Methods missing reproducibility elements
   - **Impact:** Work cannot be reproduced by others
   - **Action:** Add software versions, parameters, data sources

3. **Evidence:** Strong claim without evidence: "AI-powered integration accelerates discovery"
   - **Impact:** Unsupported claims undermine credibility
   - **Action:** Add citation or data reference to support claim

4. **Evidence:** Strong claim without evidence: "Results demonstrate effectiveness"
   - **Impact:** Unsupported claims undermine credibility
   - **Action:** Add citation or data reference to support claim

5. **Evidence:** Strong claim without evidence: "Analysis confirms validity"
   - **Impact:** Unsupported claims undermine credibility
   - **Action:** Add citation or data reference to support claim

## Minor Issues (Content)

1. **Coherence:** Section 2 lacks transitional references
   - **Action:** Add transitional phrases

2. **Coherence:** Section 3 lacks transitional references
   - **Action:** Add transitional phrases
"""

        file_path = self.test_dir / "critique_content_v1.md"
        file_path.write_text(content)

    def _create_sample_critique_format(self):
        """Create sample format critique."""
        content = """# Format Review Report (Stage 2)

## Summary Assessment

Found 2 formatting issues.

## Formatting Issues

1. **Citation Format:** Malformed citation: [1]
   - **Action:** Use [author2024] format for citations

2. **Word Count:** Abstract has 151 words, exceeds Nature limit of 150
   - **Action:** Reduce abstract to 150 words or fewer
"""

        file_path = self.test_dir / "critique_format_v1.md"
        file_path.write_text(content)

    def _create_sample_literature_evidence(self):
        """Create sample literature evidence CSV."""
        content = """doi,citation_key,evidence
10.1038/s41579-020-00458-8,lewis2021,"The growing interest in efficient cultivation strategies has led to many rapid methodological advances."
10.1093/nsr/nwaa280,jiao2021,"More than 99% of bacterial species have not been obtained in pure culture."
10.1073/pnas.1910499117,seif2020,"We develop an algorithm using comparative genomics coupled with metabolic modeling to predict auxotrophies."
"""

        file_path = self.test_dir / "literature_evidence.csv"
        file_path.write_text(content)

    def _create_sample_section_files(self):
        """Create sample section markdown files."""
        # Abstract
        abstract = """# Abstract

The system achieves 100% precision in organism extraction. This work demonstrates effectiveness.

Word count: 151 words (including some filler text to reach the limit and test word count reduction functionality for the automated revision system).
"""
        (self.test_dir / "abstract.md").write_text(abstract)

        # Introduction
        intro = """# Introduction

AI-powered integration accelerates discovery. Analysis confirms validity.

## Background

Previous work has shown various approaches.
"""
        (self.test_dir / "introduction.md").write_text(intro)

        # Methods
        methods = """# Methods

We developed a novel algorithm for processing data.

## Implementation

The implementation uses Python and various libraries.
"""
        (self.test_dir / "methods.md").write_text(methods)

        # Results
        results = """# Results

Results demonstrate effectiveness of the approach.

## Performance

The system performed well across all metrics.
"""
        (self.test_dir / "results.md").write_text(results)

        # Discussion
        discussion = """# Discussion

Our findings support the hypothesis.

## Implications

This work has broad implications for the field.
"""
        (self.test_dir / "discussion.md").write_text(discussion)

    def test_parse_critique_reports(self):
        """Test parsing both critique reports."""
        parser = CritiqueParser(self.test_dir)
        issues = parser.parse_critique_reports(version=1)

        # Should parse both content and format critiques
        self.assertGreater(len(issues), 0)

        # Count by severity
        counts = parser.count_issues(issues)
        self.assertEqual(counts["major"], 7)  # 5 content + 2 format
        self.assertEqual(counts["minor"], 2)

    def test_load_revision_context(self):
        """Test loading revision context."""
        context = RevisionContext(self.test_dir)

        # Should load citations
        self.assertGreater(len(context.citations), 0)
        self.assertEqual(len(context.citations), 3)

        # Test citation lookup
        citations = context.find_relevant_citations("cultivation", max_results=2)
        self.assertGreater(len(citations), 0)

    def test_state_manager_revision_tracking(self):
        """Test state manager revision methods."""
        manager = StateManager(output_dir=str(self.test_dir), enable_git=False)

        # Start revision
        manager.start_revision(max_revisions=2)

        state = manager.state["workflow_status"]["revision"]
        self.assertEqual(state["status"], "in_progress")
        self.assertEqual(state["max_revisions"], 2)

        # Update iteration
        metrics_before = {"major": 7, "minor": 2}
        metrics_after = {"major": 3, "minor": 1}

        manager.update_revision_iteration(
            iteration=1,
            sections_revised=["introduction", "methods"],
            metrics_before=metrics_before,
            metrics_after=metrics_after
        )

        # Check iteration recorded
        iterations = manager.state["workflow_status"]["revision"]["iterations"]
        self.assertEqual(len(iterations), 1)
        self.assertEqual(iterations[0]["iteration"], 1)
        self.assertEqual(iterations[0]["issues_before"]["major"], 7)
        self.assertEqual(iterations[0]["issues_after"]["major"], 3)

        # Test convergence check
        should_stop, reason = manager.check_revision_convergence(
            metrics_after={"major": 0, "minor": 0},
            iteration=1,
            max_revisions=2,
            improvement_rate=1.0
        )
        self.assertTrue(should_stop)
        self.assertEqual(reason, "major_issues_resolved")

        # Test convergence - max iterations
        should_stop, reason = manager.check_revision_convergence(
            metrics_after={"major": 3, "minor": 1},
            iteration=2,
            max_revisions=2,
            improvement_rate=0.5
        )
        self.assertTrue(should_stop)
        self.assertEqual(reason, "max_iterations_reached")

        # Test convergence - stalled
        should_stop, reason = manager.check_revision_convergence(
            metrics_after={"major": 3, "minor": 1},
            iteration=1,
            max_revisions=5,
            improvement_rate=0.02  # Less than 5% improvement
        )
        self.assertTrue(should_stop)
        self.assertEqual(reason, "stalled_no_improvement")

    def test_revision_summary(self):
        """Test getting revision summary."""
        manager = StateManager(output_dir=str(self.test_dir), enable_git=False)

        # Before revision starts
        summary = manager.get_revision_summary()
        self.assertEqual(summary["status"], "not_started")

        # After starting revision
        manager.start_revision(max_revisions=2)

        # Add iterations
        manager.update_revision_iteration(
            iteration=1,
            sections_revised=["introduction"],
            metrics_before={"major": 7, "minor": 2},
            metrics_after={"major": 3, "minor": 1}
        )

        manager.update_revision_iteration(
            iteration=2,
            sections_revised=["methods", "results"],
            metrics_before={"major": 3, "minor": 1},
            metrics_after={"major": 0, "minor": 0}
        )

        # Complete revision
        manager.complete_revision("converged", "major_issues_resolved")

        # Get summary
        summary = manager.get_revision_summary()

        self.assertEqual(summary["status"], "completed")
        self.assertEqual(summary["iterations"], 2)
        self.assertEqual(summary["issues_initial"]["major"], 7)
        self.assertEqual(summary["issues_final"]["major"], 0)
        self.assertEqual(summary["total_major_resolved"], 7)
        self.assertEqual(summary["convergence_reason"], "major_issues_resolved")

    def test_section_inference(self):
        """Test inferring sections from issues."""
        parser = CritiqueParser(self.test_dir)
        issues = parser.parse_critique_reports(version=1)
        issues = parser.infer_all_sections(issues)

        # Group by section
        grouped = parser.group_by_section(issues)

        # Should have manuscript_full for Evidence issues (no context)
        # and abstract for Word Count issue
        self.assertIn("manuscript_full", grouped)
        self.assertIn("abstract", grouped)

        # Word count issue should be in abstract
        word_count_issues = [
            i for i in grouped.get("abstract", [])
            if i.category == "Word Count"
        ]
        self.assertEqual(len(word_count_issues), 1)


class TestRevisionWorkflow(unittest.TestCase):
    """Test complete revision workflow."""

    def setUp(self):
        """Create test environment."""
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.test_dir)

    def test_convergence_logic(self):
        """Test convergence detection logic."""
        manager = StateManager(output_dir=str(self.test_dir), enable_git=False)

        # Scenario 1: Major issues resolved
        should_stop, reason = manager.check_revision_convergence(
            metrics_after={"major": 0, "minor": 5},
            iteration=1,
            max_revisions=3,
            improvement_rate=1.0
        )
        self.assertTrue(should_stop)
        self.assertEqual(reason, "major_issues_resolved")

        # Scenario 2: Max iterations
        should_stop, reason = manager.check_revision_convergence(
            metrics_after={"major": 5, "minor": 2},
            iteration=3,
            max_revisions=3,
            improvement_rate=0.5
        )
        self.assertTrue(should_stop)
        self.assertEqual(reason, "max_iterations_reached")

        # Scenario 3: Stalled
        should_stop, reason = manager.check_revision_convergence(
            metrics_after={"major": 10, "minor": 2},
            iteration=1,
            max_revisions=5,
            improvement_rate=0.03  # 3% improvement
        )
        self.assertTrue(should_stop)
        self.assertEqual(reason, "stalled_no_improvement")

        # Scenario 4: Continue iterating
        should_stop, reason = manager.check_revision_convergence(
            metrics_after={"major": 5, "minor": 2},
            iteration=1,
            max_revisions=3,
            improvement_rate=0.5  # 50% improvement
        )
        self.assertFalse(should_stop)
        self.assertIsNone(reason)


if __name__ == '__main__':
    unittest.main()
