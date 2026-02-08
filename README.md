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

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/rrwrite.git
cd rrwrite

# Install tool repository protection (recommended)
python scripts/rrwrite_state_manager.py --install-tool-protection

# Install dependencies (if any)
# pip install -r requirements.txt  # Add if you create one
```

### Basic Usage

```bash
# Generate a manuscript from your research repository
python scripts/rrwrite.py --repo /path/to/your/research-repo

# Or use the Claude Code skill
/rrwrite --repo /path/to/your/research-repo
```

### What Happens

1. **Analysis**: RRWrite analyzes your repository structure, code, and documentation
2. **Planning**: Generates a manuscript outline
3. **Assessment**: Recommends target journals and fetches guidelines
4. **Research**: Conducts literature review on relevant topics
5. **Drafting**: Writes individual sections (Abstract, Introduction, Methods, Results, Discussion)
6. **Assembly**: Combines sections into complete manuscript
7. **Critique**: Performs adversarial review and suggests improvements

**Output:** Complete manuscript in `manuscript/yourrepo_v1/manuscript.md` with:
- All sections in journal-specific order
- Bibliography with formatted citations
- Evidence links to repository
- Git version control for tracking changes

---

## Directory Structure

```
rrwrite/                          # Tool repository (clone this)
├── .git/                         # Tool's git repository
├── .gitignore                    # Ignores manuscript/ workspace
├── .claude/                      # Claude Code skills
│   └── skills/
│       ├── rrwrite.md
│       ├── rrwrite-plan-manuscript.md
│       ├── rrwrite-draft-section.md
│       └── ...
├── scripts/                      # Python tools
│   ├── rrwrite_state_manager.py  # Workflow state management
│   ├── rrwrite_git.py            # Git version control manager
│   ├── rrwrite-analyze-repo.py
│   ├── rrwrite-search-literature.py
│   └── ...
├── templates/                    # Configuration templates
│   └── journal_guidelines.yaml
├── docs/                         # Documentation
│   └── GIT_ARCHITECTURE.md       # Git architecture explained
├── example/                      # Example manuscripts (for reference)
│   └── data_sheets_schema_v1/
└── manuscript/                   # Your workspace (auto-created, gitignored)
    └── yourrepo_v1/              # Your manuscript project
        ├── .git/                 # Separate git repo for your manuscript
        ├── .rrwrite/
        │   └── state.json        # Workflow state
        ├── sections/
        │   ├── abstract.md
        │   ├── introduction.md
        │   └── ...
        └── manuscript.md         # Final assembled manuscript
```

---

## Git Architecture

RRWrite uses **separate Git repositories** for tool and manuscripts to prevent pollution.

### Key Concepts

- **Tool Repository** (`rrwrite/.git/`): The RRWrite tool itself (this repo)
- **Manuscript Repositories** (`manuscript/project_v1/.git/`): Your manuscripts (separate repos)
- **Safety:** Four layers of protection prevent accidental commits to tool repo

### Workflow

```bash
# 1. Clone rrwrite tool (once)
git clone https://github.com/user/rrwrite.git
cd rrwrite

# 2. Run rrwrite (creates manuscript with own .git/)
python scripts/rrwrite.py --repo /path/to/research

# 3. Manuscript has independent git history
cd manuscript/research_v1
git log  # Shows only manuscript commits

# 4. Push manuscript to your own repo
git remote add origin https://github.com/you/my-manuscript.git
git push -u origin main

# 5. Update tool without affecting manuscripts
cd ../..
git pull  # Updates rrwrite tool only
```

**See [docs/GIT_ARCHITECTURE.md](docs/GIT_ARCHITECTURE.md) for detailed explanation.**

### Safety Features

1. ✅ **Remote URL validation** - Prevents commits to tool repo
2. ✅ **Pre-commit hooks** - Rejects manuscript files in tool commits
3. ✅ **Explicit --git-dir** - All git commands specify exact repository
4. ✅ **Warning messages** - Loud alerts when safety checks fail

---

## Workflow Stages

### 1. Repository Analysis

```bash
python scripts/rrwrite-analyze-repo.py --repo-path /path/to/repo
```

Analyzes:
- Code structure and architecture
- Documentation (README, docstrings, comments)
- Git history (commits, contributors)
- Dependencies and technologies
- Test coverage and examples

**Output:** `repository_analysis.md`

### 2. Manuscript Planning

```bash
/rrwrite-plan-manuscript
```

Generates structured outline:
- Title and abstract outline
- Section structure tailored to research type
- Key points for each section
- Suggested figures and tables

**Output:** `outline.md`

### 3. Journal Assessment

```bash
/rrwrite-assess-journal
```

Recommends target journals based on:
- Research scope and methodology
- Manuscript outline content
- Journal impact and fit

Fetches author guidelines for selected journal.

**Output:** `journal_assessment.md`, `journal_guidelines.md`

### 4. Literature Research

```bash
python scripts/rrwrite-search-literature.py --topics "topic1,topic2,topic3"
```

Conducts literature review:
- Searches PubMed and Semantic Scholar
- Ranks papers by relevance
- Generates citation indices
- Creates evidence database

**Output:** `literature.md`, `literature_evidence.csv`, `literature_citations.bib`

### 5. Section Drafting

```bash
/rrwrite-draft-section --section introduction
```

Writes individual sections:
- Uses repository evidence
- Incorporates citations from literature
- Follows journal guidelines
- Fact-checks claims against evidence

**Output:** `sections/introduction.md`, `sections/methods.md`, etc.

### 6. Manuscript Assembly

```bash
python scripts/rrwrite-assemble-manuscript.py
```

Combines sections in journal-specified order:
- Merges section files
- Formats citations
- Validates completeness
- Generates metadata

**Output:** `manuscript.md`, `assembly_manifest.json`

### 7. Manuscript Critique

```bash
/rrwrite-critique-manuscript
```

Adversarial review:
- Checks clarity and coherence
- Validates citations
- Identifies weak arguments
- Suggests improvements

**Output:** `critique_manuscript_v1.md`

---

## Command Reference

### Core Scripts

| Script | Purpose |
|--------|---------|
| `rrwrite-analyze-repo.py` | Analyze repository structure and content |
| `rrwrite-search-literature.py` | Search PubMed and Semantic Scholar |
| `rrwrite-extract-repo-evidence.py` | Extract evidence from repository |
| `rrwrite-verify-evidence.py` | Verify manuscript claims against evidence |
| `rrwrite-assemble-manuscript.py` | Assemble final manuscript from sections |
| `rrwrite-match-journal-scope.py` | Match manuscript to journal scopes |
| `rrwrite-recommend-journal.py` | Recommend suitable journals |
| `rrwrite-fetch-guidelines.py` | Fetch author guidelines for journal |

### Claude Code Skills

| Skill | Purpose |
|-------|---------|
| `/rrwrite` | Full end-to-end manuscript generation |
| `/rrwrite-plan-manuscript` | Generate manuscript outline |
| `/rrwrite-assess-journal` | Journal recommendation and guidelines |
| `/rrwrite-research-literature` | Deep literature research |
| `/rrwrite-draft-section` | Draft individual manuscript section |
| `/rrwrite-critique-manuscript` | Adversarial critique of manuscript |

### State Management

```bash
# View workflow status
python scripts/rrwrite-status.py --output-dir manuscript/yourrepo_v1

# View state summary
python scripts/rrwrite_state_manager.py --output-dir manuscript/yourrepo_v1 --summary

# Export state as JSON
python scripts/rrwrite_state_manager.py --output-dir manuscript/yourrepo_v1 --export
```

---

## Configuration

### Journal Guidelines Template

Edit `templates/journal_guidelines.yaml` to customize journal-specific formatting:

```yaml
journal: "Nature Methods"
sections_order:
  - abstract
  - introduction
  - results
  - discussion
  - methods
  - availability
citation_style: "nature"
word_limits:
  abstract: 200
  main_text: 3000
```

### Custom Output Location

```bash
# Output to directory outside rrwrite/
python scripts/rrwrite.py \
    --repo /path/to/research \
    --output-dir ~/my-manuscripts/project_v1
```

### Disable Git Version Control

```bash
python scripts/rrwrite.py --repo /path/to/research --no-git
```

---

## Examples

See `example/data_sheets_schema_v1/` for a complete example manuscript generated by RRWrite.

---

## Troubleshooting

### "SAFETY VIOLATION: RRWRITE TOOL REPOSITORY DETECTED"

**Cause:** Trying to initialize git in tool directory
**Fix:** Use `manuscript/` subdirectory or `--output-dir`

```bash
# Correct:
python scripts/rrwrite.py --repo /path/to/research --output-dir manuscript/myproject

# Wrong:
python scripts/rrwrite.py --repo /path/to/research --output-dir .
```

### "Commit rejected: manuscript/ files detected"

**Cause:** Pre-commit hook detected manuscript files in tool repo
**Fix:** Commit from manuscript directory instead

```bash
git reset HEAD manuscript/
cd manuscript/myproject
git commit -m "Your manuscript changes"
```

### "Git repository not initialized"

**Cause:** Git initialization failed or disabled
**Fix:** Manually initialize

```bash
cd manuscript/yourproject
python ../../scripts/rrwrite_git.py --manuscript-dir . --initialize
```

### API Rate Limits

**PubMed:** No authentication required, but rate limited to 3 requests/second
**Semantic Scholar:** Rate limited to 100 requests/5 minutes

**Fix:** If you hit limits, wait and retry, or register for API keys

---

## Development

### Adding New Skills

1. Create skill file in `.claude/skills/`
2. Define metadata, prompts, and tools
3. Test with `/skill-name`

### Adding New Scripts

1. Create Python script in `scripts/`
2. Follow naming convention: `rrwrite-action-name.py`
3. Add CLI argparse interface
4. Document in README

### Running Tests

```bash
# Verify safety features
python scripts/rrwrite_git.py --install-tool-hook
git add manuscript/  # Should fail with hook

# Test manuscript creation
python scripts/rrwrite.py --repo /path/to/test-repo --output-dir /tmp/test-manuscript
```

---

## Architecture

### Workflow State Machine

```
not_started → in_progress → completed
```

Stages tracked:
1. repository_analysis
2. plan
3. assessment
4. research
5. drafting (with sub-stages for each section)
6. assembly
7. critique

State stored in: `{manuscript_dir}/.rrwrite/state.json`

### Evidence Chain

```
Repository → Evidence Extraction → Citation Index → Manuscript → Verification
```

1. Extract facts from repo (code, docs, commits)
2. Create evidence database (CSV)
3. Draft manuscript sections referencing evidence
4. Verify all claims link back to evidence

### Git Integration

```
StateManager → GitManager → Manuscript .git/
```

- `StateManager`: Initializes git for new manuscripts
- `GitManager`: Handles all git operations with safety checks
- Each manuscript gets independent `.git/` repository

---

## Contributing

Contributions welcome! Please:

1. Fork this repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

**Note:** Examples should go in `example/`, not `manuscript/`

---

## License

[Specify your license here]

---

## Citation

If you use RRWrite in your research, please cite:

```bibtex
@software{rrwrite2025,
  title={RRWrite: Research Repository to Manuscript Generator},
  author={Your Name},
  year={2025},
  url={https://github.com/YOUR_USERNAME/rrwrite}
}
```

---

## Support

- **Documentation:** See `docs/` directory
- **Issues:** Report bugs on GitHub Issues
- **Questions:** Open a GitHub Discussion

---

## Acknowledgments

Built with [Claude Code](https://claude.com/code) using Claude AI models.

---

## Learn More

- [Git Architecture](docs/GIT_ARCHITECTURE.md) - Detailed explanation of version control system
- [Example Manuscript](example/data_sheets_schema_v1/) - See RRWrite output
- [Journal Guidelines](templates/journal_guidelines.yaml) - Customize formatting

---

**RRWrite**: From code to publication, powered by AI.
