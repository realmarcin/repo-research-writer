---
name: rrwrite-draft-section
description: Drafts a specific manuscript section using repository data and citation indices. Enforces fact-checking via Python tools.
arguments:
  - name: target_dir
    description: Output directory for manuscript files (e.g., manuscript/repo_v1)
    default: manuscript
allowed-tools:
context: fork
---
# Section Drafting Protocol

## Inputs
*   **Section Name:** (e.g., "Methods", "Results", "Introduction") provided by the user or plan.
*   **Target Directory:** Output directory for manuscript files (e.g., manuscript/repo_v1), default: manuscript
*   **Context Files:** The list of code/data files identified in `{target_dir}/outline.md`.

## Workflow
1.  **Read Outline:** Read `{target_dir}/outline.md` to understand section requirements and evidence files.
2.  **Load Word Limits:** Check section-specific word limits:
    ```bash
    python scripts/rrwrite-config-manager.py --section {section_name}
    ```
    This ensures the draft meets the target word count (±20% variance allowed).
3.  **Load Context:** Read the specified code/data files. DO NOT read unrelated files to save tokens.
4.  **Load Citations:** Read `references.bib` or `{target_dir}/literature_citations.bib` to find relevant citation keys.
5.  **Drafting:** Write the text in Markdown, adhering to word limits from step 2.
    *   Use **LaTeX** for math (e.g., `$x^2$`).
    *   Use **[Key]** format for citations (e.g., `[smith2020]`).
    *   **Style:** Formal academic prose. Passive voice for Methods; Active voice for Results.

## Fact-Checking Requirement
**CRITICAL:** You must verify all numerical claims.
*   Before finalizing a sentence containing a number, locate that number in the source file (`*.csv` or `*.log`).
*   If the number involves a calculation (e.g., mean, p-value), generate a temporary Python script to compute it from the raw data and verify your claim.
*   **Command:** `python scripts/rrwrite-verify-stats.py --file <PATH> --col [NAME] --op [mean/max/min]`

## Evidence Tracking

**IMPORTANT:** Track all repository-based claims for verification.

When drafting sections, automatically track factual claims about the repository by appending to `{target_dir}/repo_evidence.md`. This enables reviewers to verify all claims.

**What to track:**
- Numerical claims (line counts, file counts, commit counts, contributor counts)
- Version requirements (Python 3.9+, etc.)
- Feature capabilities (100% validation, etc.)
- Repository statistics (classes, functions, tests)

**How to track:**

After drafting a section with repository claims, append evidence stubs to repo_evidence.md:

```bash
# Extract claims from the just-drafted section
python3 scripts/rrwrite-extract-repo-evidence.py \
  --repo-path <REPO_PATH> \
  --manuscript {target_dir}/SECTIONNAME.md \
  --output {target_dir}/SECTIONNAME_evidence.md

# Append to main evidence file (create if doesn't exist)
if [ -f "{target_dir}/repo_evidence.md" ]; then
  # Skip header and append new claims
  tail -n +8 {target_dir}/SECTIONNAME_evidence.md >> {target_dir}/repo_evidence.md
else
  # First section - copy entire file
  cp {target_dir}/SECTIONNAME_evidence.md {target_dir}/repo_evidence.md
fi

# Clean up temporary file
rm {target_dir}/SECTIONNAME_evidence.md
```

**Evidence stub format** (auto-generated):
```markdown
## Claim: "372 commits"

**Section**: [Section Name]
**Evidence Source**: Git repository metadata

**Verification**:
```bash
git rev-list --all --count
```

**Output**:
```
[Actual count from repository]
```

**Status**: ⚠ Approximate
```

**Why this matters:**
- Enables fact-checking during critique
- Provides verification commands for reviewers
- Tracks claim accuracy across manuscript versions
- Supports reproducibility requirements

## Figure referencing
*   Ensure every Figure mentioned is referenced as "Figure X" (capitalized).
*   Describe the figure content based on the generating script's logic (e.g., "Figure 1 visualizes the t-SNE projection...").

## Section-Specific Guidelines

### Methods Section Citations

When drafting Methods sections, cite ONLY specific tools, datasets, and methodologies that were actually used:

**✅ Appropriate citations:**
- Specific software tools used (e.g., [LinkML2024] for schema validation)
- Datasets accessed (e.g., [GTDB2024] for taxonomic data)
- Published algorithms implemented (e.g., [Smith2020] for MaxPro design)
- Computational methods applied (e.g., [Jones2019] for embedding generation)
- Analysis frameworks employed (e.g., [pandas2023] for data processing)

**❌ Inappropriate citations:**
- Abstract principles (FAIR data sharing, reproducibility frameworks)
- General best practices papers
- Related tools NOT used in this work
- Methodological reviews unless specific method was implemented
- Workflow standards not explicitly followed

**Rationale:** Methods describes what YOU did, not general principles. Abstract concepts belong in Introduction (motivation) or Discussion (broader context).

**Example (correct):**
```markdown
Schema validation was performed using LinkML specifications [LinkML2024].
```

**Example (incorrect):**
```markdown
All data followed FAIR principles [Wilkinson2016].
```

### Data and Code Availability Section
When drafting the Availability (or "Data and Code Availability") section:

**Should include:**
- Repository URL (GitHub, GitLab, etc.)
- License information (MIT, Apache, GPL, etc.)
- Installation instructions or reference to installation docs
- Documentation locations
- Data repository locations (Zenodo, Figshare, Dryad, etc.)
- Software version or DOI if available
- System requirements (Python version, dependencies)

**Should NOT include:**
- General methodology citations (FAIR principles, reproducibility papers)
- Citations unless specifically about tools/platforms (e.g., [zenodo2023] for Zenodo DOI, [docker2024] for containerization)
- Research methodology or background information
- Discussion of data analysis approaches

**Format:** Concise, factual statements. 50-150 words typical.

**Example (correct):**
```markdown
# Data and Code Availability

Source code is available at https://github.com/user/project under the MIT license.
Installation requires Python 3.10+ and can be completed via `pip install project`.
Complete documentation is hosted at https://project.readthedocs.io.
All experimental data are deposited in Zenodo (DOI: 10.5281/zenodo.1234567).
```

**Example (incorrect - has inappropriate citations):**
```markdown
... complete documentation following FAIR principles [Wilkinson2016].
```

### Results Section Citations

When drafting Results sections, cite ONLY to report what was observed or measured, not to explain concepts or provide justification:

**✅ Appropriate citations:**
- Papers/datasets that were analyzed or benchmarked against (e.g., [Smith2020] for comparison dataset)
- Examples of findings from your analysis (e.g., "identified 29 papers including [ExamplePaper2024]")
- Tools whose performance was measured (e.g., [Tool2024] achieved 85% accuracy in our tests)
- Specific data sources that were processed (e.g., analyzed sequences from [GTDB2024])

**❌ Inappropriate citations:**
- Explaining what concepts mean (e.g., "establishing provenance chains [citations]")
- Justifying why you did something (e.g., "addressing concerns about hallucination [citations]")
- Discussing future possibilities (e.g., "for future integration with standards [citations]")
- Providing background context or motivation

**Rationale:** Results reports OBSERVATIONS and MEASUREMENTS from your work. Explanations, justifications, and contextual citations belong in Introduction (motivation/background) or Discussion (interpretation/implications).

**Example (correct):**
```markdown
The literature search identified 29 papers spanning reproducible research [Wilkinson2016, Barker2022], computational notebooks [Pimentel2023], and AI-assisted writing [CHI2024, Ros2025].
```
(These are examples of papers found - actual results being reported)

**Example (incorrect):**
```markdown
Literature evidence tracking established provenance chains between claims and sources [Himmelstein2019, CliVER2024].
```
(This explains what provenance chains are/do, not reporting a measurement)

**Example (incorrect):**
```markdown
This evidence chain addresses concerns about hallucination in AI writing [CliVER2024].
```
(This justifies WHY we did something - belongs in Introduction or Discussion)

## Output and Naming (per schema: schemas/manuscript.yaml)

Write the section to `{target_dir}/SECTIONNAME.md` where SECTIONNAME is:
- `abstract.md` for Abstract
- `introduction.md` for Introduction
- `methods.md` for Methods
- `results.md` for Results
- `discussion.md` for Discussion
- `conclusion.md` for Conclusion
- `availability.md` for Data and Code Availability

## Validation

After drafting, validate the section:
```bash
python scripts/rrwrite-validate-manuscript.py --file {target_dir}/SECTIONNAME.md --type section
```

## State Update

After successful validation, update workflow state:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path('scripts').resolve()))
from rrwrite_state_manager import StateManager

manager = StateManager(output_dir="{target_dir}")
manager.add_section_completed("SECTIONNAME")  # e.g., "methods", "results"
```

Display updated progress:
```bash
python scripts/rrwrite-status.py --output-dir {target_dir}
```

Report validation status and updated workflow progress. If validation fails, fix issues and re-validate.
