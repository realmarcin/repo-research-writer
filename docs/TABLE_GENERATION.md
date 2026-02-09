# Table Generation and TSV Data Export

## Overview

RRWrite now automatically generates structured data tables during repository analysis and provides utilities for including them in manuscript sections.

## Features

### 1. Automatic TSV Generation

During repository analysis (`rrwrite-analyze-repo`), four TSV tables are automatically created:

| Table File | Description | Use Case |
|------------|-------------|----------|
| `file_inventory.tsv` | Complete file listing with metadata (path, type, size, date, git status) | Detailed results section |
| `repository_statistics.tsv` | Summary metrics by file category | Methods/Results overview |
| `size_distribution.tsv` | File size quartiles by category | Distribution analysis |
| `research_indicators.tsv` | Detected research topics with confidence scores | Introduction/Methods context |

**Location:** Tables are saved in `{manuscript_dir}/data_tables/`

### 2. Markdown Table Formatting

Convert pandas DataFrames to formatted markdown tables with:
- Custom column alignment (left, right, center)
- Optional captions
- Automatic type-based alignment (numbers right-aligned)
- Column width limits

### 3. Section-Specific Table Selection

`TableSelector` automatically recommends relevant tables for each section:
- **Methods:** `repository_statistics.tsv`, `research_indicators.tsv`
- **Results:** All tables (filtered as needed)
- **Introduction:** `research_indicators.tsv`

### 4. Validation and Tracking

- Automatic detection of markdown tables in sections
- Table reference counting (e.g., "Table 1", "Table 2")
- Journal-specific table limit warnings
- State management tracks table generation and usage

## Usage

### During Repository Analysis

Tables are generated automatically when using `--output` flag:

```bash
python scripts/rrwrite-analyze-repo.py /path/to/repo --output manuscript/analysis.md
# Creates: manuscript/data_tables/*.tsv
```

### In Section Drafting

The `rrwrite-draft-section` skill now includes table discovery and formatting:

```python
from pathlib import Path
import pandas as pd
from rrwrite_table_generator import TableGenerator, TableSelector

# Discover available tables
data_tables_dir = Path("manuscript/data_tables")
available_tables = TableSelector.get_tables_for_section(
    section_name="results",
    data_tables_dir=data_tables_dir
)

# Load and format a table
df = pd.read_csv("manuscript/data_tables/repository_statistics.tsv", sep='\t')
table_md = TableGenerator.format_markdown_table(
    df,
    caption="**Table 1: Repository composition by file type**",
    alignment={'file_count': 'right', 'total_size_mb': 'right'}
)

# Include in manuscript
print(f"""
The repository structure (Table 1) shows clear organization...

{table_md}

As shown in Table 1, data files comprise...
""")
```

### Validation

```bash
python scripts/rrwrite-validate-manuscript.py --file manuscript/results.md --type section
```

Output includes:
- `✓ Contains N markdown table(s)` - Count of tables detected
- `✓ References N table(s)` - Count of table references
- Warnings if references don't match table count
- Warnings if table count exceeds journal limits

## Journal Table Limits

The validator checks against common journal limits:
- **Bioinformatics:** 5 tables
- **Nature:** 4 tables
- **PLOS:** 10 tables
- **BMC:** 10 tables

Exceeding limits triggers a warning to move tables to supplementary materials.

## Implementation Files

### New Files
- `scripts/rrwrite_table_generator.py` - Core utilities (TableGenerator, TableSelector)
- `docs/TABLE_GENERATION.md` - This documentation

### Modified Files
- `scripts/rrwrite-analyze-repo.py` - Calls table generation after analysis
- `scripts/rrwrite_state_manager.py` - Tracks table metadata in state.json
- `scripts/rrwrite-validate-manuscript.py` - Detects and validates tables
- `.claude/skills/rrwrite-draft-section/SKILL.md` - Table inclusion guidelines

## State Tracking

State file (`manuscript/.rrwrite/state.json`) now includes:

```json
{
  "workflow_status": {
    "repository_analysis": {
      "data_tables": {
        "file_inventory": "data_tables/file_inventory.tsv",
        "repository_statistics": "data_tables/repository_statistics.tsv",
        ...
      }
    },
    "drafting": {
      "sections": {
        "results": {
          "table_count": 2
        }
      }
    }
  },
  "metadata": {
    "tables_count": 3,
    "data_tables_generated": true
  }
}
```

## Best Practices

### When to Include Tables
1. Data is clearer in tabular format than prose
2. Comparing 3+ items or showing multiple metrics
3. Within journal table limits

### Table Formatting
- Use descriptive captions: "Table 1: Repository composition by file type"
- Align numbers to the right, text to the left
- Keep tables focused (limit to 10-15 rows for main text)
- Move large tables to supplementary materials

### Table Referencing
- First mention: "Table 1: Repository composition" (full caption)
- Subsequent: "Table 1" or "(Table 1)"
- Sequential numbering across manuscript

## Examples

### Example 1: Simple Table

```python
df = pd.DataFrame({
    'Category': ['Data', 'Scripts', 'Figures'],
    'Count': [25, 12, 8]
})

table_md = TableGenerator.format_markdown_table(df)
```

Output:
```markdown
| Category | Count |
| :--- | ---: |
| Data | 25 |
| Scripts | 12 |
| Figures | 8 |
```

### Example 2: Table with Caption

```python
table_md = TableGenerator.format_markdown_table(
    df,
    caption="**Table 1: File distribution by category**",
    alignment={'Count': 'right'}
)
```

### Example 3: Loading TSV with Metadata

```python
df, metadata = TableGenerator.load_tsv_with_metadata(
    "manuscript/data_tables/file_inventory.tsv"
)
print(f"Generated by: {metadata['generated_by']}")
print(f"Total files: {metadata['total_files']}")
```

## Troubleshooting

### Tables Not Generated
- Ensure `--output` flag is used with `rrwrite-analyze-repo.py`
- Check for errors in stderr output
- Verify pandas is installed

### Tables Not Found in Drafting
- Confirm `data_tables/` directory exists in manuscript directory
- Check file paths are correct
- Use `TableSelector.get_all_tables()` to list available tables

### Validation Warnings
- **"Table reference count doesn't match"**: Check table numbering in text
- **"Exceeds journal limit"**: Move tables to supplementary materials
- **"No tables found"**: Normal if section doesn't require tables

## API Reference

### TableGenerator Methods

- `save_tsv(df, output_path, metadata)` - Save DataFrame with metadata header
- `load_tsv_with_metadata(tsv_path)` - Load TSV and extract metadata
- `format_markdown_table(df, alignment, max_col_width, caption)` - Format as markdown
- `generate_repo_tables(repo_path, categorized_files, output_dir)` - Generate all 4 tables

### TableSelector Methods

- `get_tables_for_section(section_name, data_tables_dir)` - Get relevant tables for section
- `get_all_tables(data_tables_dir)` - List all available TSV tables
- `SECTION_TABLE_MAP` - Dict mapping sections to recommended tables
