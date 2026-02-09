---
name: rrwrite
description: Generate manuscript from GitHub repo or local path
---

# RRWrite: Repository-to-Manuscript Workflow

Generate a complete academic manuscript from a research repository (GitHub URL or local path) with automated literature review, citation management, and journal-specific formatting.

## Usage

```bash
/rrwrite <github-url-or-local-path> [--journal JOURNAL] [--version VERSION]
```

## Arguments

- `<repo>`: GitHub URL (e.g., `https://github.com/user/repo`) or local path (e.g., `/path/to/repo` or `.`)
- `--journal`: Target journal format (default: `bioinformatics`)
  - `bioinformatics` - Bioinformatics/Oxford Academic format
  - `nature` - Nature journal format
  - `plos` - PLOS ONE format
- `--version`: Version number for output directory (default: auto-increment)
  - `v1`, `v2`, `v3`, etc. - Specific version
  - `auto` - Auto-increment from existing versions (default)

## Examples

```bash
# Analyze GitHub repository and generate manuscript
/rrwrite https://github.com/user/research-project

# Use local repository with Nature format
/rrwrite /path/to/my-research --journal nature

# Create specific version (e.g., after addressing critique)
/rrwrite . --version v2

# Analyze current directory for Bioinformatics journal
/rrwrite . --journal bioinformatics
```

## Workflow Overview

The `/rrwrite` command orchestrates the complete manuscript generation workflow:

1. **Repository Analysis**: Analyze repository structure, identify key files, extract research context
2. **Version Management**: Determine output directory (`manuscript/<repo-name>_v{N}/`)
3. **Planning**: Generate detailed manuscript outline based on journal guidelines
4. **Literature Research**: Conduct deep literature review with citations
5. **Drafting**: Generate all manuscript sections (abstract, intro, methods, results, discussion)
6. **Critique**: Review manuscript against journal standards
7. **Progress Report**: Display status and next steps

## Output Structure

All manuscript files are generated in a versioned directory:

```
manuscript/
├── <repo-name>_v1/
│   ├── outline.md                      # Manuscript structure
│   ├── abstract.md                     # Abstract section
│   ├── introduction.md                 # Introduction section
│   ├── methods.md                      # Methods section
│   ├── results.md                      # Results section
│   ├── discussion.md                   # Discussion section
│   ├── literature.md                   # Literature review summary
│   ├── literature_citations.bib        # BibTeX citations
│   ├── literature_evidence.csv         # Citation evidence tracker
│   ├── critique_manuscript_v1.md       # Quality critique
│   └── .rrwrite/
│       └── state.json                  # Progress tracking
├── <repo-name>_v2/                     # After addressing critique
│   └── ...
```

## Implementation Protocol

### Step 1: Parse Arguments

Extract repository input, journal, and version from user command:

```python
import re
import sys

# Parse command arguments
args = sys.argv[1:]  # Get arguments after /rrwrite

# Required: repository input (first positional arg)
repo_input = args[0] if args else None
if not repo_input:
    print("Error: Repository URL or path required")
    print("Usage: /rrwrite <github-url-or-local-path> [--journal JOURNAL] [--version VERSION]")
    exit(1)

# Optional: journal (default: bioinformatics)
journal = "bioinformatics"
if "--journal" in args:
    idx = args.index("--journal")
    if idx + 1 < len(args):
        journal = args[idx + 1]

# Optional: version (default: auto)
version = "auto"
if "--version" in args:
    idx = args.index("--version")
    if idx + 1 < len(args):
        version = args[idx + 1]
```

### Step 2: Analyze Repository

Run repository analyzer to extract structure and context:

```bash
python scripts/rrwrite-analyze-repo.py <repo_input> --output analysis.md
```

This generates a detailed analysis prompt that will be used for planning.

### Step 3: Normalize Repository Name

Get clean directory name from URL or path:

```bash
repo_name=$(python scripts/rrwrite-normalize-repo-name.py <repo_input>)
```

### Step 4: Determine Version Number

Check for existing manuscript directories and determine next version:

```python
import os
import re
from pathlib import Path

def get_next_version(repo_name: str, specified_version: str = "auto") -> int:
    """
    Determine version number for output directory.

    Args:
        repo_name: Normalized repository name
        specified_version: User-specified version or "auto"

    Returns:
        Version number (integer)
    """
    if specified_version != "auto":
        # Extract number from version string (v1 -> 1)
        match = re.match(r'v?(\d+)', specified_version)
        if match:
            return int(match.group(1))
        else:
            print(f"Warning: Invalid version format '{specified_version}', using auto-increment")

    # Auto-increment: scan for existing versions
    manuscript_dir = Path("manuscript")
    if not manuscript_dir.exists():
        return 1

    existing = list(manuscript_dir.glob(f"{repo_name}_v*"))
    versions = []

    for d in existing:
        match = re.match(rf"{repo_name}_v(\d+)", d.name)
        if match:
            versions.append(int(match.group(1)))

    return max(versions, default=0) + 1

version_num = get_next_version(repo_name, version)
target_dir = f"manuscript/{repo_name}_v{version_num}"
```

### Step 5: Create Output Directory

Set up directory structure for manuscript:

```bash
mkdir -p <target_dir>/.rrwrite
```

### Step 6: Initialize State Tracking

Create state.json for progress tracking:

```bash
python scripts/rrwrite-state-manager.py init \
    --project-name <repo_name> \
    --output-dir <target_dir>
```

### Step 7: Run Planning Phase

Generate manuscript outline using repository analysis:

```bash
/rrwrite-plan-manuscript --target-dir <target_dir> --journal <journal>
```

**Pass the analysis.md content** to the planning skill as context for understanding the repository.

Output: `<target_dir>/outline.md`

### Step 8: Run Literature Research

Extract topics from outline and conduct literature review:

```bash
/rrwrite-research-literature --target-dir <target_dir>
```

Output: `<target_dir>/literature.md`, `literature_citations.bib`, `literature_evidence.csv`

### Step 9: Draft All Sections

For each section in the manuscript outline, generate content:

```bash
/rrwrite-draft-section abstract --target-dir <target_dir>
/rrwrite-draft-section introduction --target-dir <target_dir>
/rrwrite-draft-section methods --target-dir <target_dir>
/rrwrite-draft-section results --target-dir <target_dir>
/rrwrite-draft-section discussion --target-dir <target_dir>
```

**Note**: The draft skill should be called once per section. Each call generates one section file.

### Step 10: Run Critique

Review the complete manuscript against journal standards:

```bash
/rrwrite-critique-manuscript --target-dir <target_dir>
```

Output: `<target_dir>/critique_manuscript_v1.md`

### Step 11: Display Progress Summary

Show status dashboard with completed and remaining tasks:

```bash
python scripts/rrwrite-status.py --output-dir <target_dir>
```

### Step 12: Present Next Steps

Inform user of options for proceeding:

```markdown
## Manuscript Generation Complete! ✓

**Output location**: `<target_dir>/`

### Generated Files:
- ✓ outline.md - Manuscript structure
- ✓ abstract.md - Abstract section
- ✓ introduction.md - Introduction
- ✓ methods.md - Methods
- ✓ results.md - Results
- ✓ discussion.md - Discussion
- ✓ literature.md - Literature review
- ✓ literature_citations.bib - Citations (BibTeX)
- ✓ critique_manuscript_v1.md - Quality review

### Next Steps:

1. **Review Critique**: Read `critique_manuscript_v1.md` for improvement suggestions

2. **Revise Manuscript**: Address critique points by re-running individual sections:
   ```bash
   /rrwrite-draft-section introduction --target-dir <target_dir>
   /rrwrite-draft-section methods --target-dir <target_dir>
   ```

3. **Generate New Version**: Create a revised version incorporating feedback:
   ```bash
   /rrwrite <repo_input> --journal <journal> --version v<N+1>
   ```

4. **Assemble Full Document**: Combine all sections into single manuscript:
   ```bash
   python scripts/rrwrite-assemble-manuscript.py --output-dir <target_dir>
   ```

5. **Compare Versions**: Review changes between versions:
   ```bash
   python scripts/rrwrite-compare-runs.py <target_dir> manuscript/<repo_name>_v<N+1>
   ```
```

## Error Handling

### Repository Not Found
If the repository cannot be accessed:

```
Error: Unable to access repository: <repo_input>

Please check:
- GitHub URL is correct and repository is public
- Local path exists and is readable
- You have necessary permissions
```

### Version Already Exists
If specified version already exists:

```
Warning: Directory already exists: <target_dir>

Options:
1. Use auto-increment: /rrwrite <repo> --version auto
2. Specify different version: /rrwrite <repo> --version v<N>
3. Archive existing version:
   python scripts/rrwrite-archive-run.py --source-dir <target_dir>
```

### Invalid Journal Format
If journal is not recognized:

```
Error: Invalid journal format: <journal>

Supported journals:
- bioinformatics (Bioinformatics/Oxford Academic)
- nature (Nature journal)
- plos (PLOS ONE)
```

## Exit Points

The workflow can be interrupted at any stage. Use individual skills to resume or modify specific parts:

- **Re-plan**: `/rrwrite-plan-manuscript --target-dir <target_dir>`
- **Re-research**: `/rrwrite-research-literature --target-dir <target_dir>`
- **Re-draft section**: `/rrwrite-draft-section <section> --target-dir <target_dir>`
- **Re-critique**: `/rrwrite-critique-manuscript --target-dir <target_dir>`

State tracking in `.rrwrite/state.json` allows resuming from any point.

## Technical Notes

### Repository Analysis
The analyzer extracts:
- Directory structure (tree view)
- Key files by type (data, scripts, figures, docs)
- README summary
- Inferred research topics
- Suggested manuscript sections

### Version Management
- Versions are integers (v1, v2, v3, ...)
- Auto-increment scans `manuscript/<repo-name>_v*` directories
- Manual versions can skip numbers (v1 → v5 is valid)
- Each version is completely independent

### State Tracking
The `.rrwrite/state.json` file tracks:
- Completed phases (planning, research, drafting, critique)
- Section statuses
- File locations
- Timestamps

This allows:
- Resuming interrupted workflows
- Skipping completed steps
- Progress reporting
