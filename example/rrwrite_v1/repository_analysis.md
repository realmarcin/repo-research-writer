# Research Repository Analysis for Manuscript Generation

**Repository**: /Users/marcin/Documents/VIMSS/ontology/repo-research-writer
**Name**: repo-research-writer
**Analysis Date**: 2026-02-09 20:01:19

---

## Repository Structure

```
repo-research-writer/
├── .claude
│   ├── commands
│   │   ├── rrwrite-workflow.md
│   │   └── rrwrite.md
│   ├── skills
│   │   ├── rrwrite-analyze-repository
│   │   │   └── SKILL.md
│   │   ├── rrwrite-assemble
│   │   │   └── SKILL.md
│   │   ├── rrwrite-assemble-manuscript
│   │   │   └── SKILL.md
│   │   ├── rrwrite-assess-journal
│   │   │   └── SKILL.md
│   │   ├── rrwrite-critique-manuscript
│   │   │   └── SKILL.md
│   │   ├── rrwrite-draft-section
│   │   │   └── SKILL.md
│   │   ├── rrwrite-plan-manuscript
│   │   │   └── SKILL.md
│   │   ├── rrwrite-research-literature
│   │   │   └── SKILL.md
│   │   └── rrwrite-workflow
│   │       └── SKILL.md
│   └── settings.local.json
├── data
│   └── gemini_deepresearch_cluewrite_concept.md
├── docs
│   ├── git-hooks
│   │   └── pre-commit-manuscript
│   ├── 2-5-minute-rule.md
│   ├── API_IMPLEMENTATION_SUMMARY.md
│   ├── API_LITERATURE_SEARCH.md
│   ├── ASSEMBLY_SUMMARY.md
│   ├── ASSESSMENT_QUICKSTART.md
│   ├── EVIDENCE_ENHANCEMENTS_COMPLETE.md
│   ├── EVIDENCE_MARKDOWN_MIGRATION.md
│   ├── EVIDENCE_TRACKING.md
│   ├── GIT_ARCHITECTURE.md
│   ├── GUIDELINES_INTEGRATION.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── LITERATURE_AGENT_COMPARISON.md
│   ├── TABLE_GENERATION.md
│   ├── VERSIONING_IMPLEMENTATION_PLAN.md
│   ├── VERSION_REUSE.md
│   ├── cascading-literature-search.md
│   ├── citation-rules-by-section.md
│   ├── power-user-workflow.md
│   ├── rationalization-table.md
│   ├── remaining-implementation-notes.md
│   └── skill-optimization-guide.md
├── example
│   ├── data
│   │   └── benchmark_results.csv
│   ├── drafts
│   ├── figures
│   ├── notebooks
│   ├── repo_research_writer_v2
│   │   ├── .rrwrite
│   │   │   └── state.json
│   │   ├── README.md
│   │   ├── abstract.md
│   │   ├── availability.md
│   │   ├── critique_manuscript_v1.md
│   │   ├── discussion.md
│   │   ├── introduction.md
│   │   ├── literature.md
│   │   ├── literature_citations.bib
│   │   ├── literature_evidence.csv
│   │   ├── methods.md
│   │   ├── outline.md
│   │   └── results.md
│   ├── rrwrite_v1
│   │   └── .rrwrite
│   ├── scripts
│   │   ├── evaluate.py
│   │   └── train_model.py
│   ├── PROJECT.md
│   ├── README.md
│   ├── literature_evidence.csv
│   ├── manuscript_plan.md
│   └── references.bib
├── manuscript
│   ├── MicroGrowAgents_v4
│   │   ├── .rrwrite
│   │   │   └── state.json
│   │   ├── data_tables
│   │   │   ├── file_inventory.tsv
│   │   │   ├── repository_statistics.tsv
│   │   │   ├── research_indicators.tsv
│   │   │   └── size_distribution.tsv
│   │   ├── .gitignore
│   │   ├── LITERATURE_RESEARCH_SUMMARY.md
│   │   ├── abstract.md
│   │   ├── availability.md
│   │   ├── critique_content_v1.md
│   │   ├── critique_format_v1.md
│   │   ├── discussion.md
│   │   ├── introduction.md
│   │   ├── literature.md
... (truncated)
```

---

## Key Files Identified

### Documentation Files
**File**: `README.md`

# RRWrite: Research Repository to Manuscript

**Transform your research code repository into a publication-ready scientific manuscript.**

RRWrite is an AI-powered tool that analyzes software repositories, extracts evidence, conducts literature review, and generates structured academic manuscripts tailored to specific journal requirements.

---

## Features

- 🔍 **Repository Analysis**: Deep analysis of code structure, documentation, and git history
- 📚 **Literature Research**: Automated literature search via PubMed and Semantic Scholar
- ✍️ **Manuscript Drafting**: Generate publication-ready sections with citations
- 🎯 **Journal Targeting**: Match manuscripts to appropriate journals and fetch author guidelines
- 🔬 **Evidence-Based**: All claims verified against repository evidence
- 📝 **Citation Management**: Automatic citation formatting and bibliography generation
- 🔄 **Version Control**: Safe Git integration for manuscript tracking (separate from tool repo)
- ⚡ **Iterative Refinement**: Adversarial critique and revision workflow

---

## Installation

### Prerequisites

- **Python 3.8+** (check with `python3 --version`)
- **Git** (check with `git --version`)
- **Claude Code CLI** (optional, for `/rrwrite` skills) - [Install here](https://claude.com/code)
- **Internet connection** (for PubMed and Semantic Scholar API access)

### Step 1: Clone RRWrite Repository

```bash
# Clone from GitHub (replace YOUR_USERNAME with actual repository location)
git clone https://github.com/YOUR_USERNAME/rrwrite.git

# Navigate into the repository
cd rrwrite

# Verify you're in the correct directory
pwd
# Should show: /path/to/rrwrite
```

**Expected result:**
```
Cloning into 'rrwrite'...
remote: Enumerating objects: 60, done.
remote: Counting objects: 100% (60/60), done.
Receiving objects: 100% (60/60), done.
```

### Step 2: Install Git Safety Hooks (Recommended)

```bash
# Install pre-commit hook to protect tool repository
python3 scripts/rrwrite_state_manager.py --install-to

... (truncated)

### Data Files
- `.claude/settings.local.json` (3.3 KB)
- `example/data/benchmark_results.csv` (559.0 B)
- `example/literature_evidence.csv` (1.2 KB)
- `example/repo_research_writer_v2/.rrwrite/state.json` (1.7 KB)
- `example/repo_research_writer_v2/literature_evidence.csv` (6.1 KB)
- `manuscript/MicroGrowAgents_v4/.rrwrite/state.json` (7.0 KB)
- `manuscript/MicroGrowAgents_v4/data_tables/file_inventory.tsv` (103.5 KB)
- `manuscript/MicroGrowAgents_v4/data_tables/repository_statistics.tsv` (268.0 B)
- `manuscript/MicroGrowAgents_v4/data_tables/research_indicators.tsv` (996.0 B)
- `manuscript/MicroGrowAgents_v4/data_tables/size_distribution.tsv` (330.0 B)
- `manuscript/MicroGrowAgents_v4/literature_evidence.csv` (9.7 KB)
- `manuscript/MicroGrowAgents_v4/literature_evidence_imported.csv` (6.3 KB)
- `manuscript/MicroGrowAgents_v4/literature_evidence_new.csv` (3.4 KB)
- `manuscript/MicroGrowAgents_v4/manifest.json` (777.0 B)
- `manuscript/microgrowagents_v3/.rrwrite/state.json` (4.3 KB)
- `manuscript/microgrowagents_v3/data_tables/file_inventory.tsv` (103.5 KB)
- `manuscript/microgrowagents_v3/data_tables/repository_statistics.tsv` (268.0 B)
- `manuscript/microgrowagents_v3/data_tables/research_indicators.tsv` (996.0 B)
- `manuscript/microgrowagents_v3/data_tables/size_distribution.tsv` (330.0 B)
- `manuscript/microgrowagents_v3/literature_evidence.csv` (6.3 KB)
- ... and 1 more files

### Analysis Scripts
- `example/scripts/evaluate.py` (4.2 KB)
- `example/scripts/train_model.py` (3.6 KB)
- `install.sh` (2.8 KB)
- `scripts/__init__.py` (61.0 B)
- `scripts/rrwrite-analyze-repo.py` (18.5 KB)
- `scripts/rrwrite-api-pubmed.py` (8.6 KB)
- `scripts/rrwrite-api-semanticscholar.py` (7.3 KB)
- `scripts/rrwrite-archive-run.py` (7.0 KB)
- `scripts/rrwrite-assemble-manuscript.py` (4.7 KB)
- `scripts/rrwrite-clean-ipynb.py` (2.7 KB)
- `scripts/rrwrite-compare-runs.py` (8.1 KB)
- `scripts/rrwrite-config-manager.py` (9.4 KB)
- `scripts/rrwrite-convert-evidence-to-md.py` (4.4 KB)
- `scripts/rrwrite-critique-content.py` (13.0 KB)
- `scripts/rrwrite-critique-format.py` (14.8 KB)
- `scripts/rrwrite-extract-repo-evidence.py` (11.5 KB)
- `scripts/rrwrite-fetch-guidelines.py` (9.1 KB)
- `scripts/rrwrite-match-journal-scope.py` (9.6 KB)
- `scripts/rrwrite-migrate-v1.py` (8.4 KB)
- `scripts/rrwrite-normalize-repo-name.py` (3.1 KB)
- ... and 15 more files

### Figures and Visualizations
No files found.

### Configuration and Dependencies
- `requirements.txt` (218.0 B)

---

## Inferred Research Context

**Detected Topics**:
- Bioinformatics
- Data
- Data Analysis
- Data Tables
- Data Visualization
- Figures
- Machine Learning
- Visualization
- Workflow

---

## Suggested Manuscript Sections

Based on the repository contents, the following sections are recommended:

1. **Data Description**: Repository contains data files that should be described in Methods
2. **Analysis Methods**: Repository contains analysis scripts/notebooks

---

## Additional Notes

- Total files analyzed: 157
- Contains 2 test file(s)
- Contains 85 documentation file(s)
