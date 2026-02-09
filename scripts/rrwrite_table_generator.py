#!/usr/bin/env python3
"""
Table generation and formatting utilities for RRWrite manuscript pipeline.

This module provides tools for:
1. Exporting repository analysis data to TSV files
2. Formatting DataFrames as markdown tables
3. Selecting appropriate tables for manuscript sections
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd


class TableGenerator:
    """Generate and format tables for manuscript sections."""

    @staticmethod
    def save_tsv(
        df: pd.DataFrame,
        output_path: Path,
        metadata: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Save DataFrame to TSV file with optional metadata header.

        Args:
            df: DataFrame to save
            output_path: Path to output TSV file
            metadata: Optional dict of metadata to include as comments
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            # Write metadata as comments
            if metadata:
                for key, value in metadata.items():
                    f.write(f"# {key}: {value}\n")
                f.write("#\n")

            # Write DataFrame as TSV
            df.to_csv(f, sep='\t', index=False)

    @staticmethod
    def load_tsv_with_metadata(tsv_path: Path) -> Tuple[pd.DataFrame, Dict[str, str]]:
        """
        Load TSV file and extract metadata from comment lines.

        Args:
            tsv_path: Path to TSV file

        Returns:
            Tuple of (DataFrame, metadata_dict)
        """
        metadata = {}

        with open(tsv_path, 'r') as f:
            lines = f.readlines()

        # Extract metadata from comment lines
        data_start = 0
        for i, line in enumerate(lines):
            if line.startswith('#'):
                # Parse metadata: # key: value
                match = re.match(r'#\s*(\w+):\s*(.+)', line)
                if match:
                    metadata[match.group(1)] = match.group(2).strip()
                data_start = i + 1
            else:
                break

        # Load DataFrame from remaining lines
        df = pd.read_csv(tsv_path, sep='\t', skiprows=data_start)

        return df, metadata

    @staticmethod
    def format_markdown_table(
        df: pd.DataFrame,
        alignment: Optional[Dict[str, str]] = None,
        max_col_width: int = 50,
        caption: Optional[str] = None
    ) -> str:
        """
        Convert DataFrame to markdown table with pipe format.

        Args:
            df: DataFrame to convert
            alignment: Dict mapping column names to alignment ('left', 'right', 'center')
            max_col_width: Maximum column width in characters (truncate longer values)
            caption: Optional caption to add before table

        Returns:
            Markdown formatted table string
        """
        if df.empty:
            return ""

        # Default alignment: left for text, right for numbers
        if alignment is None:
            alignment = {}

        for col in df.columns:
            if col not in alignment:
                if pd.api.types.is_numeric_dtype(df[col]):
                    alignment[col] = 'right'
                else:
                    alignment[col] = 'left'

        # Truncate long values
        df_display = df.copy()
        for col in df_display.columns:
            if df_display[col].dtype == 'object':
                df_display[col] = df_display[col].apply(
                    lambda x: str(x)[:max_col_width] + '...' if len(str(x)) > max_col_width else str(x)
                )

        # Build markdown table
        lines = []

        # Add caption if provided
        if caption:
            lines.append(caption)
            lines.append("")

        # Header row
        header = "| " + " | ".join(df_display.columns) + " |"
        lines.append(header)

        # Alignment row
        alignment_symbols = []
        for col in df_display.columns:
            align = alignment.get(col, 'left')
            if align == 'left':
                alignment_symbols.append(':---')
            elif align == 'right':
                alignment_symbols.append('---:')
            elif align == 'center':
                alignment_symbols.append(':---:')
            else:
                alignment_symbols.append('---')

        alignment_row = "| " + " | ".join(alignment_symbols) + " |"
        lines.append(alignment_row)

        # Data rows
        for _, row in df_display.iterrows():
            row_str = "| " + " | ".join(str(val) for val in row) + " |"
            lines.append(row_str)

        return "\n".join(lines)

    @staticmethod
    def generate_repo_tables(
        repo_path: Path,
        categorized_files: Dict[str, List[Path]],
        output_dir: Path
    ) -> Dict[str, Path]:
        """
        Generate all repository analysis tables and save as TSV files.

        Creates 4 tables:
        1. file_inventory.tsv - Complete file listing with metadata
        2. repository_statistics.tsv - Summary metrics by category
        3. size_distribution.tsv - File size distribution quartiles
        4. research_indicators.tsv - Detected research topics

        Args:
            repo_path: Path to repository root
            categorized_files: Dict mapping category names to file lists
            output_dir: Directory to save TSV files

        Returns:
            Dict mapping table names to their file paths
        """
        repo_path = Path(repo_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        table_paths = {}

        # Table 1: File Inventory
        file_inventory = TableGenerator._generate_file_inventory(
            repo_path, categorized_files
        )
        inventory_path = output_dir / "file_inventory.tsv"
        TableGenerator.save_tsv(
            file_inventory,
            inventory_path,
            metadata={
                'generated_by': 'rrwrite-analyze-repo',
                'description': 'Complete file listing with metadata',
                'total_files': str(len(file_inventory))
            }
        )
        table_paths['file_inventory'] = inventory_path

        # Table 2: Repository Statistics
        repo_stats = TableGenerator._generate_repository_statistics(
            categorized_files, file_inventory
        )
        stats_path = output_dir / "repository_statistics.tsv"
        TableGenerator.save_tsv(
            repo_stats,
            stats_path,
            metadata={
                'generated_by': 'rrwrite-analyze-repo',
                'description': 'Summary metrics by file category'
            }
        )
        table_paths['repository_statistics'] = stats_path

        # Table 3: Size Distribution
        size_dist = TableGenerator._generate_size_distribution(
            categorized_files, file_inventory
        )
        size_path = output_dir / "size_distribution.tsv"
        TableGenerator.save_tsv(
            size_dist,
            size_path,
            metadata={
                'generated_by': 'rrwrite-analyze-repo',
                'description': 'File size distribution quartiles by category'
            }
        )
        table_paths['size_distribution'] = size_path

        # Table 4: Research Indicators
        research_ind = TableGenerator._generate_research_indicators(
            categorized_files
        )
        research_path = output_dir / "research_indicators.tsv"
        TableGenerator.save_tsv(
            research_ind,
            research_path,
            metadata={
                'generated_by': 'rrwrite-analyze-repo',
                'description': 'Detected research topics with evidence'
            }
        )
        table_paths['research_indicators'] = research_path

        return table_paths

    @staticmethod
    def _generate_file_inventory(
        repo_path: Path,
        categorized_files: Dict[str, List[Path]]
    ) -> pd.DataFrame:
        """Generate file inventory table with metadata."""
        # Get git tracked files (single call for efficiency)
        git_tracked = TableGenerator._get_git_tracked_files(repo_path)

        inventory_data = []

        for category, files in categorized_files.items():
            for file_path in files:
                file_path = Path(file_path)

                # Skip if file doesn't exist
                if not file_path.exists():
                    continue

                try:
                    stat = file_path.stat()
                    rel_path = file_path.relative_to(repo_path)

                    inventory_data.append({
                        'path': str(rel_path),
                        'type': category,
                        'size_bytes': stat.st_size,
                        'last_modified': pd.Timestamp(stat.st_mtime, unit='s').isoformat(),
                        'git_tracked': str(rel_path) in git_tracked
                    })
                except (OSError, ValueError):
                    # Skip files that can't be accessed or aren't in repo
                    continue

        # Sort by size descending and limit to 1000 largest files if needed
        df = pd.DataFrame(inventory_data)
        if len(df) > 1000:
            df = df.nlargest(1000, 'size_bytes')

        return df.sort_values('size_bytes', ascending=False).reset_index(drop=True)

    @staticmethod
    def _generate_repository_statistics(
        categorized_files: Dict[str, List[Path]],
        file_inventory: pd.DataFrame
    ) -> pd.DataFrame:
        """Generate repository statistics table."""
        stats_data = []

        for category in file_inventory['type'].unique():
            category_files = file_inventory[file_inventory['type'] == category]

            # Count test and doc files
            test_count = category_files['path'].str.contains(
                'test', case=False, na=False
            ).sum()
            doc_count = category_files['path'].str.contains(
                r'readme|doc|documentation', case=False, na=False
            ).sum()

            stats_data.append({
                'category': category,
                'file_count': len(category_files),
                'total_size_mb': category_files['size_bytes'].sum() / (1024 * 1024),
                'avg_size_kb': category_files['size_bytes'].mean() / 1024,
                'test_files': test_count,
                'doc_files': doc_count
            })

        df = pd.DataFrame(stats_data)

        # Round numeric columns
        df['total_size_mb'] = df['total_size_mb'].round(2)
        df['avg_size_kb'] = df['avg_size_kb'].round(2)

        return df.sort_values('file_count', ascending=False).reset_index(drop=True)

    @staticmethod
    def _generate_size_distribution(
        categorized_files: Dict[str, List[Path]],
        file_inventory: pd.DataFrame
    ) -> pd.DataFrame:
        """Generate size distribution table with quartiles."""
        dist_data = []

        for category in file_inventory['type'].unique():
            category_files = file_inventory[file_inventory['type'] == category]
            sizes_kb = category_files['size_bytes'] / 1024

            dist_data.append({
                'category': category,
                'percentile_25_kb': sizes_kb.quantile(0.25),
                'percentile_50_kb': sizes_kb.quantile(0.50),
                'percentile_75_kb': sizes_kb.quantile(0.75),
                'min_kb': sizes_kb.min(),
                'max_kb': sizes_kb.max()
            })

        df = pd.DataFrame(dist_data)

        # Round all numeric columns
        numeric_cols = df.select_dtypes(include=['float64']).columns
        df[numeric_cols] = df[numeric_cols].round(2)

        return df

    @staticmethod
    def _generate_research_indicators(
        categorized_files: Dict[str, List[Path]]
    ) -> pd.DataFrame:
        """Generate research indicators table by detecting topics from filenames."""
        # Common research keywords to detect
        research_keywords = {
            'machine_learning': ['ml', 'model', 'train', 'predict', 'neural', 'learning'],
            'data_analysis': ['analysis', 'statistics', 'statistical', 'analyze'],
            'visualization': ['plot', 'chart', 'graph', 'visual', 'figure'],
            'bioinformatics': ['sequence', 'genome', 'protein', 'gene', 'bio'],
            'pipeline': ['pipeline', 'workflow', 'snakemake', 'nextflow'],
            'database': ['database', 'db', 'sql', 'schema', 'query'],
            'api': ['api', 'rest', 'endpoint', 'service'],
            'testing': ['test', 'spec', 'mock', 'fixture']
        }

        indicators = []

        for topic, keywords in research_keywords.items():
            matching_files = []

            # Search through all categorized files
            for category, files in categorized_files.items():
                for file_path in files:
                    file_str = str(file_path).lower()
                    if any(kw in file_str for kw in keywords):
                        matching_files.append(file_path)

            if matching_files:
                # Determine confidence based on evidence count
                count = len(matching_files)
                if count >= 5:
                    confidence = 'high'
                elif count >= 2:
                    confidence = 'medium'
                else:
                    confidence = 'low'

                # Get example files (max 3)
                examples = [str(Path(f).name) for f in matching_files[:3]]

                indicators.append({
                    'topic': topic.replace('_', ' ').title(),
                    'confidence': confidence,
                    'evidence_count': count,
                    'example_files': ', '.join(examples)
                })

        df = pd.DataFrame(indicators)
        return df.sort_values('evidence_count', ascending=False).reset_index(drop=True)

    @staticmethod
    def _get_git_tracked_files(repo_path: Path) -> set:
        """
        Get set of git-tracked files efficiently.

        Args:
            repo_path: Path to repository root

        Returns:
            Set of relative paths for git-tracked files
        """
        import subprocess

        try:
            result = subprocess.run(
                ['git', 'ls-files'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return set(result.stdout.strip().split('\n'))
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return set()


class TableSelector:
    """Select appropriate tables for manuscript sections."""

    # Mapping of section names to relevant table files
    SECTION_TABLE_MAP = {
        'methods': [
            'repository_statistics.tsv',
            'research_indicators.tsv'
        ],
        'results': [
            'repository_statistics.tsv',
            'size_distribution.tsv',
            'file_inventory.tsv'
        ],
        'introduction': [
            'research_indicators.tsv'
        ],
        'discussion': [
            'repository_statistics.tsv'
        ]
    }

    @staticmethod
    def get_tables_for_section(
        section_name: str,
        data_tables_dir: Path
    ) -> List[Dict[str, any]]:
        """
        Get list of available tables relevant to a manuscript section.

        Args:
            section_name: Name of manuscript section (e.g., 'methods', 'results')
            data_tables_dir: Directory containing TSV table files

        Returns:
            List of dicts with keys: name, path, exists
        """
        data_tables_dir = Path(data_tables_dir)
        section_lower = section_name.lower()

        # Get relevant table names for this section
        table_names = TableSelector.SECTION_TABLE_MAP.get(section_lower, [])

        # Check which tables exist
        available_tables = []
        for table_name in table_names:
            table_path = data_tables_dir / table_name
            available_tables.append({
                'name': table_name,
                'path': table_path,
                'exists': table_path.exists()
            })

        return available_tables

    @staticmethod
    def get_all_tables(data_tables_dir: Path) -> List[Path]:
        """
        Get all TSV table files in directory.

        Args:
            data_tables_dir: Directory containing TSV files

        Returns:
            List of paths to TSV files
        """
        data_tables_dir = Path(data_tables_dir)

        if not data_tables_dir.exists():
            return []

        return sorted(data_tables_dir.glob("*.tsv"))
