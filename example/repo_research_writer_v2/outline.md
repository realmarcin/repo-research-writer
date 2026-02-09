# Manuscript Outline: RRWrite - Repository Research Writer

**Target Journal**: Bioinformatics (Oxford Academic)
**Total Word Limit**: 6000 words
**Date**: 2026-02-06
**Version**: 2

---

## Overview

This manuscript describes RRWrite, a novel AI-powered system for automatically generating publication-ready manuscripts from computational research repositories. RRWrite addresses the critical gap between research code execution and manuscript preparation by providing automated fact verification, citation management, and journal-specific formatting.

**Key Innovation**: Integration of repository analysis, automated fact-checking via data verification, literature synthesis, and iterative critique workflow with configurable word limits and versioned output management.

---

## Section 1: Abstract

**Word Limits**: Min: 150, Target: 200, Max: 250

**Purpose**: Structured abstract presenting motivation, implementation, results, and availability.

**Key Points**:
1. Problem: Manual manuscript writing from computational research is error-prone and time-consuming
2. Solution: RRWrite automates manuscript generation with fact verification
3. Implementation: AI skills integrated with Claude Code, Python verification scripts, versioned workflow
4. Results: Successfully generates 6000-word manuscripts with 15-25 verified citations, demonstrated via self-documentation
5. Availability: Open source (MIT license), available at GitHub

**Evidence Files**:
- `README.md` - Project description
- `scripts/rrwrite-config-manager.py` - Word limit configuration
- `examples/repo-research-writer_v1/` - Reference implementation

---

## Section 2: Introduction

**Word Limits**: Min: 400, Target: 500, Max: 800

**Purpose**: Establish the problem of manuscript generation from computational research and position RRWrite's contribution.

**Key Points**:
1. **Background**: Computational research produces code, data, and notebooks but manuscript writing remains manual
2. **Challenge**: Maintaining accuracy between code outputs and manuscript claims requires tedious verification
3. **Existing Approaches**: Literature review tools exist but lack integration with fact-checking and repository analysis
4. **Gap**: No automated system connects repository artifacts → verified manuscript with journal formatting
5. **Contribution**: RRWrite provides end-to-end workflow from repository analysis to critique-ready manuscript

**Evidence Files**:
- `.claude/skills/` - Four integrated skills (plan, research, draft, critique)
- `templates/manuscript_config.yaml` - Journal-specific configurations
- `scripts/rrwrite-analyze-repo.py` - Repository analysis implementation

**Literature Context**:
- Related work on literature review automation
- Academic writing assistance tools
- Reproducibility in computational science
- Citation management systems

---

## Section 3: Methods

**Word Limits**: Min: 800, Target: 1500, Max: 1600

**Purpose**: Describe RRWrite architecture, skills, verification mechanisms, and workflow management.

### 3.1 System Architecture

**Key Points**:
- External repository model: RRWrite stays in dedicated repo, analyzes target repos via URL or path
- Versioned output: `manuscript/<repo-name>_vN/` structure for iterative refinement
- State tracking: JSON-based workflow progress with `.rrwrite/state.json`
- Template system: Configurable word limits per journal (Bioinformatics: 6000, Nature: 3000, PLOS: unlimited)

**Evidence Files**:
- `scripts/rrwrite-state-manager.py` - State management implementation
- `scripts/rrwrite-analyze-repo.py` - Repository analyzer (300+ lines)
- `scripts/rrwrite-normalize-repo-name.py` - Name normalization
- `templates/manuscript_config.yaml` - Configuration schema

### 3.2 Four Core Skills

**Key Points**:
1. **Planning** (`rrwrite-plan-manuscript`): Generates outline with evidence mapping
2. **Research** (`rrwrite-research-literature`): Conducts literature review with DOI verification and evidence quotes
3. **Drafting** (`rrwrite-draft-section`): Writes sections with fact-checking against data files
4. **Critique** (`rrwrite-critique-manuscript`): Reviews against journal standards

**Evidence Files**:
- `.claude/skills/rrwrite-plan-manuscript/SKILL.md` - Planning protocol
- `.claude/skills/rrwrite-research-literature/SKILL.md` - Research protocol with evidence.csv generation
- `.claude/skills/rrwrite-draft-section/SKILL.md` - Drafting with verification
- `.claude/skills/rrwrite-critique-manuscript/SKILL.md` - Quality assessment

### 3.3 Verification Mechanisms

**Key Points**:
- Statistical verification: `rrwrite-verify-stats.py` validates numerical claims against CSV data
- Citation evidence tracking: `literature_evidence.csv` stores DOI + direct quotes for each citation
- Schema validation: `manuscript.yaml` defines required structure and fields
- State validation: Progress tracking ensures workflow completeness

**Evidence Files**:
- `scripts/rrwrite-verify-stats.py` - Statistical verification tool
- `scripts/rrwrite-validate-manuscript.py` - Schema validator
- `schemas/manuscript.yaml` - Manuscript schema definition

### 3.4 Workflow Orchestration

**Key Points**:
- Main command: `/rrwrite <url-or-path> [--journal JOURNAL] [--version VERSION]`
- Auto-version increment: Scans existing `manuscript/<repo>_v*` directories
- Resumable execution: State tracking allows interruption and continuation
- Individual skill invocation: Each phase can be re-run independently with `--target-dir`

**Evidence Files**:
- `.claude/commands/rrwrite.md` - Main workflow orchestrator
- `scripts/rrwrite-status.py` - Progress reporting
- `scripts/rrwrite-assemble-manuscript.py` - Section assembly

---

## Section 4: Results

**Word Limits**: Min: 600, Target: 1000, Max: 1200

**Purpose**: Demonstrate RRWrite capabilities through self-documentation and key metrics.

### 4.1 Self-Documentation Demonstration

**Key Points**:
- RRWrite successfully generated its own manuscript (examples/repo-research-writer_v1/)
- Output: 6000-word manuscript with 20+ citations, all with DOIs
- Sections: Abstract, Introduction, Methods, Results, Discussion, Availability
- Critique identified 3 major issues, 5 minor issues → addressed in v2

**Evidence Files**:
- `examples/repo-research-writer_v1/outline.md` - Generated outline
- `examples/repo-research-writer_v1/abstract.md` - Generated abstract (200 words)
- `examples/repo-research-writer_v1/methods.md` - Generated methods (1500 words)
- `examples/repo-research-writer_v1/critique_manuscript_v1.md` - Quality assessment

### 4.2 Fact Verification Performance

**Key Points**:
- All numerical claims in v1 manuscript traced to source files
- Literature evidence CSV contains 20 entries with direct quotes
- 100% of citations include DOIs for permanent identification
- Statistical verification scripts validated mean/max/count operations

**Evidence Files**:
- `examples/repo-research-writer_v1/literature_evidence.csv` - Citation evidence (20 papers)
- `examples/repo-research-writer_v1/literature_citations.bib` - BibTeX entries with DOIs

### 4.3 Word Limit Compliance

**Key Points**:
- V1 manuscript total: ~6000 words (within Bioinformatics limit)
- Abstract: 200 words (target)
- Introduction: 600 words (within 400-800 range)
- Methods: 1500 words (target)
- Results: 900 words (within 600-1200 range)
- Discussion: 700 words (within 400-1000 range)

**Evidence Files**:
- `templates/manuscript_config.yaml` - Word limit definitions
- `scripts/rrwrite-config-manager.py` - Configuration management

### 4.4 Workflow Efficiency

**Key Points**:
- Planning phase: Generates outline with evidence mapping
- Research phase: Finds 15-25 papers with evidence quotes
- Drafting phase: Produces 5 sections adhering to word limits
- Critique phase: Identifies issues with actionable feedback
- Version management: Auto-increment enables iterative refinement

**Evidence Files**:
- `scripts/rrwrite-state-manager.py` - Workflow tracking (get_next_version method at line 506)
- `.claude/commands/rrwrite.md` - Complete workflow protocol

---

## Section 5: Discussion

**Word Limits**: Min: 400, Target: 800, Max: 1000

**Purpose**: Interpret results, compare with existing tools, discuss limitations, and future directions.

### 5.1 Key Contributions

**Key Points**:
1. **Integrated workflow**: First system to combine repository analysis + fact verification + citation management + journal formatting
2. **Evidence chains**: Maintains traceability from data files to manuscript claims via verification scripts
3. **Versioned iteration**: Supports critique → revision → v2 workflow with clean separation
4. **Configurable limits**: Journal-specific word targets prevent manuscript bloat

### 5.2 Comparison to Existing Tools

**Key Points**:
- Literature review tools (Semantic Scholar, ConnectedPapers): Focus on discovery, not manuscript generation
- Writing assistants (Grammarly, Overleaf): Fix prose, don't generate from code
- Reproducibility tools (Jupyter, Quarto): Execute code but don't write manuscripts
- RRWrite uniqueness: End-to-end automation with verification

### 5.3 Limitations

**Key Points**:
1. Requires Claude Code integration (not standalone)
2. Best for computational research with code/data artifacts
3. Generated text requires human review for scientific judgment
4. Literature research depends on web search availability
5. Version 2 addresses v1 critique issues but may introduce new ones

### 5.4 Future Directions

**Key Points**:
1. Multi-journal simultaneous generation (Bioinformatics + Nature + PLOS)
2. Figure caption auto-generation from plotting scripts
3. Supplementary material generation
4. Integration with citation managers (Zotero, Mendeley)
5. Collaborative manuscript tracking across research teams

**Evidence Files**:
- `REFACTORING_SUMMARY.md` - Architecture evolution
- `examples/repo-research-writer_v1/critique_manuscript_v1.md` - Areas for improvement

---

## Section 6: Data and Code Availability

**Word Limits**: Min: 50, Target: 100, Max: 150

**Key Points**:
- Source code: https://github.com/realmarcin/repo-research-writer
- License: MIT (open source)
- Examples: Complete v1 manuscript in `examples/repo-research-writer_v1/`
- Installation: `./install.sh` for global skill installation
- Documentation: README.md, INSTALL.md, USAGE_GUIDE.md

**Evidence Files**:
- `LICENSE` - MIT license text
- `README.md` - Installation and usage instructions
- `install.sh` - Simplified global installation script

---

## Manuscript Statistics

**Estimated Total**: ~6000 words
- Abstract: 200 words
- Introduction: 500 words
- Methods: 1500 words
- Results: 1000 words
- Discussion: 800 words
- Availability: 100 words
- **Buffer**: 900 words for transitions, subsection headers, and adjustments

**Citation Target**: 15-25 papers with DOIs and evidence quotes

**Figures**:
- Figure 1: RRWrite architecture diagram (workflow: analyze → plan → research → draft → critique)
- Figure 2: Version management structure (examples/ vs manuscript/ directories)
- Figure 3: Word limit compliance comparison (v1 vs targets)

---

## Notes for Drafting

1. **Fact verification**: Every numerical claim must reference source file (e.g., "methods.md contains 1500 words" → verify via `wc`)
2. **Evidence files**: Link each section to specific files/lines for traceability
3. **Word discipline**: Adhere strictly to target word counts; use ±20% tolerance
4. **Citation strategy**: Focus on reproducibility, manuscript automation, and computational biology papers
5. **Self-referential**: This manuscript demonstrates RRWrite's capabilities by documenting itself

---

## Revision Strategy (v1 → v2)

Based on `examples/repo-research-writer_v1/critique_manuscript_v1.md`:

**Major Issues Addressed**:
1. Word limit configuration now explicit (6000 words for Bioinformatics)
2. Version management clarified (examples/ vs manuscript/ separation)
3. External repository model fully implemented (no PROJECT.md required)

**Minor Issues Addressed**:
1. Template system documented (`templates/` directory)
2. Configuration management explained (`manuscript_config.yaml`)
3. Installation simplified (single `install.sh` command)

---

**End of Outline**
