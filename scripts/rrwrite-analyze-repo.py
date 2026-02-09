#!/usr/bin/env python3
"""
RRWrite Repository Analyzer

Analyzes a GitHub repository or local directory to extract information
for manuscript generation. Populates a template with repository structure,
key files, and inferred research context.

Usage:
    python rrwrite-analyze-repo.py <github-url-or-local-path> [--output FILE]

Examples:
    python rrwrite-analyze-repo.py https://github.com/user/research-repo
    python rrwrite-analyze-repo.py /path/to/local/repo --output analysis.md
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from rrwrite_table_generator import TableGenerator


class RepoAnalyzer:
    """Analyzes repository structure and content for manuscript generation."""

    # File patterns for different categories
    DATA_PATTERNS = ['*.csv', '*.tsv', '*.xlsx', '*.xls', '*.json', '*.xml', '*.h5', '*.hdf5', '*.parquet']
    SCRIPT_PATTERNS = ['*.py', '*.ipynb', '*.r', '*.R', '*.jl', '*.m', '*.sh']
    FIGURE_PATTERNS = ['*.png', '*.jpg', '*.jpeg', '*.pdf', '*.svg', '*.eps']
    CONFIG_PATTERNS = ['requirements.txt', 'environment.yml', 'setup.py', 'pyproject.toml', 'Pipfile', 'package.json']
    DOC_PATTERNS = ['README.md', 'README.txt', 'README.rst', 'README', 'DOCUMENTATION.md', 'NOTES.md']

    # Directories to skip
    SKIP_DIRS = {'.git', '__pycache__', '.ipynb_checkpoints', 'node_modules', '.venv', 'venv',
                 'env', '.env', 'dist', 'build', '.pytest_cache', '.mypy_cache', '.tox'}

    def __init__(self, repo_input: str, max_depth: int = 5):
        """
        Initialize analyzer.

        Args:
            repo_input: GitHub URL or local path
            max_depth: Maximum directory depth to scan
        """
        self.repo_input = repo_input
        self.max_depth = max_depth
        self.temp_dir: Optional[Path] = None
        self.repo_path: Optional[Path] = None
        self.repo_name: str = ""

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup temp directory."""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def is_github_url(self, input_str: str) -> bool:
        """Check if input is a GitHub URL."""
        return input_str.startswith('http://') or input_str.startswith('https://')

    def clone_repo(self, url: str) -> Path:
        """
        Clone GitHub repository to temporary directory.

        Args:
            url: GitHub repository URL

        Returns:
            Path to cloned repository
        """
        self.temp_dir = Path(tempfile.mkdtemp(prefix='rrwrite_'))

        try:
            print(f"Cloning repository: {url}", file=sys.stderr)
            result = subprocess.run(
                ['git', 'clone', '--depth', '1', url, str(self.temp_dir / 'repo')],
                capture_output=True,
                text=True,
                check=True
            )
            return self.temp_dir / 'repo'
        except subprocess.CalledProcessError as e:
            print(f"Error cloning repository: {e.stderr}", file=sys.stderr)
            raise

    def setup_repo_path(self) -> Tuple[Path, str]:
        """
        Setup repository path and extract repository name.

        Returns:
            Tuple of (repo_path, repo_name)
        """
        if self.is_github_url(self.repo_input):
            # Extract repo name from URL: https://github.com/user/repo -> repo
            match = re.search(r'github\.com/[^/]+/([^/\.]+)', self.repo_input)
            repo_name = match.group(1) if match else 'unknown-repo'
            repo_path = self.clone_repo(self.repo_input)
        else:
            # Local path
            repo_path = Path(self.repo_input).resolve()
            if not repo_path.exists():
                raise FileNotFoundError(f"Path does not exist: {repo_path}")
            repo_name = repo_path.name

        return repo_path, repo_name

    def scan_directory_tree(self, max_lines: int = 100) -> str:
        """
        Generate directory tree structure.

        Args:
            max_lines: Maximum number of lines to include

        Returns:
            Tree structure as string
        """
        lines = []

        def walk_tree(path: Path, prefix: str = "", depth: int = 0):
            if depth > self.max_depth or len(lines) >= max_lines:
                return

            try:
                items = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name))
            except PermissionError:
                return

            # Filter out skip directories
            items = [item for item in items if item.name not in self.SKIP_DIRS]

            for i, item in enumerate(items):
                if len(lines) >= max_lines:
                    break

                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                lines.append(f"{prefix}{current_prefix}{item.name}")

                if item.is_dir():
                    extension = "    " if is_last else "│   "
                    walk_tree(item, prefix + extension, depth + 1)

        lines.append(self.repo_name + "/")
        walk_tree(self.repo_path)

        if len(lines) >= max_lines:
            lines.append("... (truncated)")

        return "\n".join(lines)

    def find_files_by_pattern(self, patterns: List[str]) -> List[Path]:
        """
        Find files matching given patterns.

        Args:
            patterns: List of glob patterns

        Returns:
            List of matching file paths
        """
        files = []
        for pattern in patterns:
            files.extend(self.repo_path.rglob(pattern))

        # Filter out files in skip directories
        files = [f for f in files if not any(skip in f.parts for skip in self.SKIP_DIRS)]
        return sorted(files)

    def format_file_list(self, files: List[Path], max_files: int = 20) -> str:
        """
        Format file list for display.

        Args:
            files: List of file paths
            max_files: Maximum number of files to display

        Returns:
            Formatted string
        """
        if not files:
            return "No files found."

        lines = []
        for i, f in enumerate(files[:max_files]):
            rel_path = f.relative_to(self.repo_path)
            size = f.stat().st_size
            size_str = self._format_size(size)
            lines.append(f"- `{rel_path}` ({size_str})")

        if len(files) > max_files:
            lines.append(f"- ... and {len(files) - max_files} more files")

        return "\n".join(lines)

    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def extract_readme_summary(self, max_chars: int = 2000) -> str:
        """
        Extract summary from README file.

        Args:
            max_chars: Maximum characters to extract

        Returns:
            README summary or message if not found
        """
        readme_files = self.find_files_by_pattern(self.DOC_PATTERNS)

        if not readme_files:
            return "No README file found."

        # Prefer README.md
        readme = readme_files[0]
        for f in readme_files:
            if f.name.lower() == 'readme.md':
                readme = f
                break

        try:
            content = readme.read_text(encoding='utf-8', errors='ignore')
            if len(content) > max_chars:
                content = content[:max_chars] + "\n\n... (truncated)"
            return f"**File**: `{readme.name}`\n\n{content}"
        except Exception as e:
            return f"Error reading README: {e}"

    def infer_research_topics(self) -> str:
        """
        Infer research topics from repository content.

        Returns:
            Inferred topics as formatted string
        """
        topics = set()

        # Extract from README
        readme_files = self.find_files_by_pattern(self.DOC_PATTERNS)
        if readme_files:
            try:
                content = readme_files[0].read_text(encoding='utf-8', errors='ignore')
                # Look for common research keywords
                keywords = ['machine learning', 'deep learning', 'neural network', 'classification',
                           'regression', 'clustering', 'bioinformatics', 'genomics', 'proteomics',
                           'RNA-seq', 'single-cell', 'phylogenetics', 'evolution', 'statistics',
                           'data analysis', 'visualization', 'pipeline', 'workflow', 'algorithm']

                for keyword in keywords:
                    if keyword.lower() in content.lower():
                        topics.add(keyword.title())
            except Exception:
                pass

        # Extract from directory names
        for path in self.repo_path.rglob('*'):
            if path.is_dir() and path.name not in self.SKIP_DIRS:
                name = path.name.lower().replace('_', ' ').replace('-', ' ')
                if any(kw in name for kw in ['analysis', 'model', 'data', 'result', 'figure']):
                    topics.add(path.name.replace('_', ' ').title())

        # Extract from script files
        script_files = self.find_files_by_pattern(['*.py'])[:10]  # Check first 10
        for script in script_files:
            try:
                content = script.read_text(encoding='utf-8', errors='ignore')[:1000]
                # Look for import statements that indicate research domain
                if 'sklearn' in content or 'tensorflow' in content or 'torch' in content:
                    topics.add('Machine Learning')
                if 'pandas' in content or 'numpy' in content:
                    topics.add('Data Analysis')
                if 'matplotlib' in content or 'seaborn' in content or 'plotly' in content:
                    topics.add('Data Visualization')
                if 'biopython' in content or 'pysam' in content:
                    topics.add('Bioinformatics')
            except Exception:
                pass

        if not topics:
            return "Unable to infer specific research topics from repository content."

        return "**Detected Topics**:\n" + "\n".join(f"- {topic}" for topic in sorted(topics))

    def suggest_sections(self) -> str:
        """
        Suggest manuscript sections based on repository content.

        Returns:
            Suggested sections as formatted string
        """
        sections = []

        # Check for data files
        data_files = self.find_files_by_pattern(self.DATA_PATTERNS)
        if data_files:
            sections.append("**Data Description**: Repository contains data files that should be described in Methods")

        # Check for analysis scripts
        script_files = self.find_files_by_pattern(self.SCRIPT_PATTERNS)
        if script_files:
            sections.append("**Analysis Methods**: Repository contains analysis scripts/notebooks")

        # Check for figures
        figure_files = self.find_files_by_pattern(self.FIGURE_PATTERNS)
        if figure_files:
            sections.append("**Results**: Repository contains figure files suggesting visualized results")

        # Check for notebooks
        notebooks = self.find_files_by_pattern(['*.ipynb'])
        if notebooks:
            sections.append("**Computational Workflow**: Jupyter notebooks suggest step-by-step analysis")

        if not sections:
            sections.append("Standard manuscript structure recommended: Abstract, Introduction, Methods, Results, Discussion")

        return "\n".join(f"{i+1}. {s}" for i, s in enumerate(sections))

    def analyze(self) -> Dict[str, str]:
        """
        Perform complete repository analysis.

        Returns:
            Dictionary with analysis results
        """
        self.repo_path, self.repo_name = self.setup_repo_path()

        print(f"Analyzing repository: {self.repo_name}", file=sys.stderr)
        print(f"Path: {self.repo_path}", file=sys.stderr)

        # Gather all information
        results = {
            'repo_url': self.repo_input,
            'repo_name': self.repo_name,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'directory_tree': self.scan_directory_tree(),
            'readme_summary': self.extract_readme_summary(),
            'data_files_list': self.format_file_list(self.find_files_by_pattern(self.DATA_PATTERNS)),
            'script_files_list': self.format_file_list(self.find_files_by_pattern(self.SCRIPT_PATTERNS)),
            'figure_files_list': self.format_file_list(self.find_files_by_pattern(self.FIGURE_PATTERNS)),
            'config_files_list': self.format_file_list(self.find_files_by_pattern(self.CONFIG_PATTERNS)),
            'inferred_topics': self.infer_research_topics(),
            'suggested_sections': self.suggest_sections(),
            'additional_notes': self._generate_additional_notes()
        }

        # Generate data tables if output_file is provided
        if hasattr(self, '_output_file') and self._output_file:
            table_results = self._generate_data_tables(self._output_file)
            results.update(table_results)

        return results

    def _generate_additional_notes(self) -> str:
        """Generate additional notes about the repository."""
        notes = []

        # Count total files
        all_files = list(self.repo_path.rglob('*'))
        all_files = [f for f in all_files if f.is_file() and not any(skip in f.parts for skip in self.SKIP_DIRS)]
        notes.append(f"- Total files analyzed: {len(all_files)}")

        # Check for tests
        test_files = self.find_files_by_pattern(['test_*.py', '*_test.py', 'test*.py'])
        if test_files:
            notes.append(f"- Contains {len(test_files)} test file(s)")

        # Check for documentation
        doc_files = self.find_files_by_pattern(['*.md', '*.rst', '*.txt'])
        if doc_files:
            notes.append(f"- Contains {len(doc_files)} documentation file(s)")

        return "\n".join(notes) if notes else "No additional notes."

    def _generate_data_tables(self, output_file: str) -> Dict[str, str]:
        """
        Generate TSV data tables from repository analysis.

        Args:
            output_file: Path to output markdown file (used to determine output directory)

        Returns:
            Dict with keys: data_tables_generated, data_tables_dir
        """
        # Create output directory for tables
        output_path = Path(output_file)
        output_dir = output_path.parent / 'data_tables'
        output_dir.mkdir(exist_ok=True)

        print(f"Generating data tables in: {output_dir}", file=sys.stderr)

        # Collect categorized files
        categorized_files = {
            'data': self.find_files_by_pattern(self.DATA_PATTERNS),
            'script': self.find_files_by_pattern(self.SCRIPT_PATTERNS),
            'figure': self.find_files_by_pattern(self.FIGURE_PATTERNS),
            'config': self.find_files_by_pattern(self.CONFIG_PATTERNS),
            'doc': self.find_files_by_pattern(['*.md', '*.rst', '*.txt', '*.pdf'])
        }

        # Generate TSV tables
        try:
            table_paths = TableGenerator.generate_repo_tables(
                repo_path=self.repo_path,
                categorized_files=categorized_files,
                output_dir=output_dir
            )

            print(f"Generated {len(table_paths)} data tables", file=sys.stderr)

            # Return relative path from output file directory
            rel_dir = output_dir.relative_to(output_path.parent)

            return {
                'data_tables_generated': str(len(table_paths)),
                'data_tables_dir': str(rel_dir)
            }
        except Exception as e:
            print(f"Warning: Failed to generate data tables: {e}", file=sys.stderr)
            return {
                'data_tables_generated': '0',
                'data_tables_dir': 'N/A'
            }

    def populate_template(self, template_path: Path, results: Dict[str, str]) -> str:
        """
        Populate template with analysis results.

        Args:
            template_path: Path to template file
            results: Analysis results dictionary

        Returns:
            Populated template as string
        """
        template = template_path.read_text(encoding='utf-8')

        # Replace placeholders
        for key, value in results.items():
            placeholder = '{' + key + '}'
            template = template.replace(placeholder, value)

        return template


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Analyze repository for manuscript generation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        'repo',
        help='GitHub URL or local repository path'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file (default: stdout)',
        default=None
    )
    parser.add_argument(
        '--template',
        help='Template file to use',
        default=None
    )
    parser.add_argument(
        '--max-depth',
        help='Maximum directory depth to scan',
        type=int,
        default=5
    )

    args = parser.parse_args()

    # Determine template path
    if args.template:
        template_path = Path(args.template)
    else:
        # Default template path relative to script location
        script_dir = Path(__file__).parent
        template_path = script_dir.parent / 'templates' / 'repo_analysis_prompt.md'

    if not template_path.exists():
        print(f"Error: Template not found: {template_path}", file=sys.stderr)
        return 1

    try:
        with RepoAnalyzer(args.repo, max_depth=args.max_depth) as analyzer:
            # Store output file path for table generation
            if args.output:
                analyzer._output_file = args.output

            results = analyzer.analyze()
            output = analyzer.populate_template(template_path, results)

            if args.output:
                output_path = Path(args.output)
                output_path.write_text(output, encoding='utf-8')
                print(f"Analysis written to: {output_path}", file=sys.stderr)
            else:
                print(output)

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
