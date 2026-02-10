# Manuscript Outline: RRWrite

**Target Journal**: Bioinformatics
**Manuscript Type**: Application Note
**Total Word Limit**: 6,000 words (targeting 4,250 words for conciseness)
**Created**: 2026-02-09

---

## Target Journal Structure: Bioinformatics

Bioinformatics Application Notes follow the structure: **Abstract → Introduction → Methods (Implementation) → Results → Discussion → Availability**

This structure emphasizes:
- **Software utility**: Solving a specific bioinformatics problem
- **Implementation details**: Technical architecture and design
- **Performance/validation**: Benchmarks and use cases
- **Availability**: Open-source access and documentation

---

## Abstract

**Word Count**: 200 words (strict Bioinformatics limit)
**Word Range**: 150-250 words

### Purpose
Concise summary of the motivation, implementation, key features, and availability.

### Key Points to Cover
1. **Motivation**: Academic manuscript generation is labor-intensive, requiring repository analysis, literature review, and journal-specific formatting
2. **What RRWrite Does**: AI-powered tool that transforms research repositories into publication-ready manuscripts
3. **Key Features**:
   - Repository analysis (code, data, documentation extraction)
   - Automated literature search with cascading year strategy (recent → foundational)
   - Multi-phase workflow (analysis → planning → research → drafting → critique)
   - Defense-in-depth citation validation (4 layers)
   - Journal-specific formatting (Nature, Bioinformatics, PLOS)
4. **Implementation**: Python-based CLI with Claude AI integration, Git-safe version control, LinkML schema validation
5. **Results**: Successfully generated manuscripts from diverse repositories (9 skills, 20 scripts, 157 files analyzed)
6. **Availability**: Open-source on GitHub with MIT license

### Evidence Files
- `README.md` - Tool overview and features
- `.claude/skills/*/SKILL.md` - 9 workflow skills
- `scripts/rrwrite*.py` - 20 implementation scripts
- `docs/` - 18 documentation files

---

## Introduction

**Word Count**: 500 words (target), 400-800 words (range)
**Word Range**: 400-800 words

### Purpose
Establish the manuscript generation challenge, current limitations, and position RRWrite as a practical solution for computational researchers.

### Key Points to Cover

#### The Manuscript Generation Challenge (150 words)
1. **Problem**: Converting research code into publishable manuscripts is time-consuming and error-prone
2. **Barriers**:
   - Repository analysis: Manual extraction of methods, results from code/data
   - Literature review: Time-intensive search, citation management
   - Journal formatting: Different structures (Nature vs. PLOS vs. Bioinformatics)
   - Citation integrity: Ensuring all claims have evidence, no orphaned references
3. **Existing approaches**: General writing assistants (Grammarly, Overleaf) lack domain knowledge; LaTeX editors handle formatting but not content generation

#### Current Gaps (150 words)
1. **No automated repository-to-manuscript tools**: Researchers manually translate code into prose
2. **Limited AI integration**: ChatGPT/Claude can draft text but lack structured workflow, validation, version control
3. **Citation chaos**: Manual bibliography management leads to 15-40% citation errors [needs citation]
4. **No journal-aware generation**: Manuscripts written generically, then reformatted (wasted effort)

#### RRWrite Solution (200 words)
1. **Innovation**: First tool integrating repository analysis + literature search + multi-phase drafting + validation
2. **Architecture**:
   - 9 specialized skills (analyze, plan, research, draft, critique)
   - 20 Python scripts for evidence extraction, citation validation, state management
   - Defense-in-depth validation (4 layers: entry, business logic, assembly, audit)
   - Cascading literature search (prioritize recent, expand to foundational)
3. **Workflow**: 7 phases with verification gates at each stage
4. **Journal targeting**: Templates for Nature, Bioinformatics, PLOS with word limits, structure requirements

### Evidence Files
- `README.md` - Overview of features
- `.claude/skills/rrwrite-workflow/SKILL.md` - Complete workflow documentation
- `docs/cascading-literature-search.md` - Literature search strategy
- `docs/citation-rules-by-section.md` - Validation rules
- `scripts/rrwrite_citation_validator.py` - Multi-layer validation code

---

## Methods (Implementation)

**Word Count**: 1,500 words (target), 800-1,600 words (range)
**Word Range**: 800-1600 words

### Purpose
Detailed implementation of RRWrite's architecture, algorithms, and workflows to enable reproduction and extension.

### Section M1: System Architecture (300 words)

#### Components
1. **Repository Analyzer**:
   - File tree generation (`tree -L 2`)
   - Pattern-based file classification (data: `*.csv/*.xlsx`, scripts: `*.py/*.R`, figures: `*.png/*.pdf`)
   - README/docs extraction and summarization
   - Research topic inference from file names and content
2. **Literature Research Agent**:
   - Cascading year search strategy (Tier 1: 2024-2026 → Tier 2: 2020-2023 → Tier 3: 2016-2019)
   - PubMed and Semantic Scholar API integration
   - DOI extraction and validation
   - Evidence quote extraction (1-2 sentence support per citation)
3. **Manuscript Drafting Engine**:
   - Section-specific templates (abstract, intro, methods, results, discussion)
   - Word count enforcement (±20% variance allowed)
   - Citation integration with in-text verification
4. **Validation Framework**:
   - Defense-in-depth (4 layers): Entry → Business Logic → Assembly → Audit
   - LinkML schema validation for structure
   - Citation completeness checking (text ↔ bibliography sync)
5. **State Manager**:
   - Git-safe version control (separate from tool repo)
   - Workflow phase tracking (analysis → plan → research → draft → critique)
   - Resume capability for interrupted workflows

#### Evidence Files
- `scripts/rrwrite-analyze-repo.py` - Repository analyzer implementation
- `scripts/rrwrite-research-literature.py` - Literature search logic
- `scripts/rrwrite-draft-section.py` - Drafting engine
- `scripts/rrwrite_citation_validator.py` - Multi-layer validation
- `scripts/rrwrite_state_manager.py` - State tracking and Git integration

### Section M2: Cascading Literature Search Algorithm (400 words)

#### Algorithm Design
**Goal**: Prioritize recent work (2024-2026) while ensuring comprehensive coverage through intelligent fallback.

**Input**:
- Research topics extracted from outline/README
- Target paper count: 15-20

**Tier 1: Recent Work (2024-2026)**
```
for topic in research_topics:
    query = f"{topic} 2024 OR {topic} 2025 OR {topic} 2026"
    papers_t1 = search(PubMed + SemanticScholar, query)

if len(papers_t1) >= 15:
    return papers_t1
else:
    proceed_to_tier_2()
```

**Tier 2: Medium Recent (2020-2023)**
```
for topic in research_topics:
    query = f"{topic} 2020..2023"
    papers_t2 = search(PubMed + SemanticScholar, query)

total = papers_t1 + papers_t2
if len(total) >= 15:
    return total
else:
    proceed_to_tier_3()
```

**Tier 3: Foundational Work (2016-2019)**
```
for topic in research_topics:
    query = f"{topic} review OR {topic} survey"
    papers_t3 = search(PubMed + SemanticScholar, query, filter_citations > 500)

total = papers_t1 + papers_t2 + papers_t3
return total  # Accept 10+ for niche topics, document gaps
```

**Rationale**:
- Tier 1: Demonstrates currency and state-of-the-art awareness
- Tier 2: Captures method evolution and major breakthroughs
- Tier 3: Establishes foundational context and seminal papers
- Fallback: Adapts to publication patterns (active vs. niche fields)

#### Evidence Files
- `docs/cascading-literature-search.md` - Complete algorithm specification
- `.claude/skills/rrwrite-research-literature/SKILL.md` - Implementation in workflow

### Section M3: Defense-in-Depth Citation Validation (400 words)

#### Four Validation Layers

**Layer 1: Entry Validation (Fast-Fail at Draft Time)**
```python
class CitationEntryValidator:
    def validate_at_entry(citation_key: str, evidence_csv: Path):
        if citation_key not in load_evidence_keys(evidence_csv):
            raise CitationNotFoundError(
                f"Citation [{citation_key}] not in literature_evidence.csv. "
                f"Run rrwrite-research-literature first."
            )
```
- **Purpose**: Reject invalid citations immediately during section drafting
- **Benefit**: Prevents propagation of errors to later stages

**Layer 2: Business Logic Validation (Section Appropriateness)**
```python
SECTION_RULES = {
    'methods': {
        'allowed_types': ['tool', 'protocol', 'dataset'],
        'forbidden_types': ['review']  # Explanations belong in intro/discussion
    },
    'results': {
        'allowed_types': ['recent', 'benchmark'],
        'forbidden_types': ['review']  # No explanations, only observations
    }
}
```
- **Purpose**: Ensure citations appropriate for section context
- **Benefit**: Methods cite tools used, Results cite data analyzed (no explanatory citations)

**Layer 3: Assembly Validation (Manuscript-Wide Completeness)**
```python
def validate_citation_completeness(manuscript: Path, bib: Path):
    text_cites = extract_citations_from_text(manuscript)
    bib_cites = extract_citations_from_bib(bib)

    orphaned_text = text_cites - bib_cites  # In text, not in bib
    orphaned_bib = bib_cites - text_cites   # In bib, not cited

    if orphaned_text or orphaned_bib:
        raise CitationMismatchError(...)
```
- **Purpose**: Synchronize in-text citations with bibliography
- **Benefit**: Eliminates orphaned references and missing entries

**Layer 4: Audit Trail (Forensics and Debugging)**
```python
class CitationAuditor:
    def log_citation_usage(section: str, citation: str, context: str):
        audit_log.append({
            'timestamp': now(),
            'section': section,
            'citation': citation,
            'context': context[:100],
            'doi_verified': verify_doi(citation)
        })
```
- **Purpose**: Record when/where/why citations used
- **Benefit**: Root cause tracing for validation failures

#### Evidence Files
- `scripts/rrwrite_citation_validator.py` - All 4 layers implemented (600 lines)
- `scripts/rrwrite_citation_tracer.py` - 5-level root cause analysis
- `docs/citation-rules-by-section.md` - Section-specific rules

### Section M4: Verification Gates and Task Decomposition (400 words)

#### Iron Law of Academic Drafting
**NO SECTION MARKED COMPLETE WITHOUT PASSING VERIFICATION GATE**

**5-Step Verification Checklist** (mandatory for each section):
```bash
# Step 1: Identify proof of completeness
validator_command="python scripts/rrwrite-validate-manuscript.py --file {section}.md --type section"

# Step 2: Run validation fresh (no caching)
$validator_command

# Step 3: Read complete validation output
validation_output=$(cat)

# Step 4: Verify all checks pass
word_count_ok && citations_ok && structure_ok && no_orphans

# Step 5: ONLY THEN update state
python scripts/rrwrite_state_manager.py --mark-section-complete {section}
```

**Task Decomposition (2-5 Minute Rule)**:
Break section drafting into verifiable micro-tasks:

*Example: Drafting Methods Section (800 words)*
- **Task 1** (2 min): Write data collection paragraph (150 words) → Verify citations in evidence file
- **Task 2** (3 min): Write analysis methods paragraph (200 words) → Verify tools cited (not principles)
- **Task 3** (2 min): Write validation paragraph (150 words) → Verify word count ±20%
- **Task 4** (3 min): Write implementation details (300 words) → Verify no orphaned refs
- **Task 5** (1 min): Run validation → Checkpoint: Exit code 0 required

**Benefits**:
- Verifiable: Each task has clear done condition
- Resumable: Can stop/resume at any checkpoint
- Debuggable: Errors isolated to one micro-task
- Motivating: Frequent completion signals

#### Evidence Files
- `.claude/skills/rrwrite-draft-section/SKILL.md` - Verification gate protocol
- `docs/2-5-minute-rule.md` - Task decomposition patterns
- `docs/rationalization-table.md` - Common rationalizations countered

---

## Results

**Word Count**: 1,000 words (target), 600-1,200 words (range)
**Word Range**: 600-1200 words

### Purpose
Demonstrate RRWrite's capabilities through quantitative metrics, example outputs, and validation results.

### Section R1: Repository Analysis Performance (250 words)

#### Metrics from repo-research-writer Analysis
- **Total files analyzed**: 157 files
- **Data files identified**: 20 (CSV, JSON, TSV formats)
- **Scripts detected**: 20 (Python analysis scripts)
- **Documentation files**: 85 (Markdown, text files)
- **Research topics inferred**: 9 topics from file names and content
  - Bioinformatics, Data Analysis, Machine Learning, Workflow, Visualization, etc.
- **Processing time**: <5 seconds for 157-file repository
- **Directory depth**: 6 levels traversed

#### File Classification Accuracy
- **Data files**: 100% precision (all `.csv`, `.tsv`, `.xlsx` correctly identified)
- **Scripts**: 100% precision (all `.py`, `.R`, `.sh` correctly identified)
- **Figures**: N/A (no figure files in this repository)
- **Documentation**: 98% recall (missed 2 edge-case markdown files in ATTIC/)

#### Evidence Files
- `example/rrwrite_v1/repository_analysis.md` - Complete analysis output
- `example/rrwrite_v1/data_tables/file_inventory.tsv` - 157 files cataloged
- `example/rrwrite_v1/data_tables/repository_statistics.tsv` - Summary metrics
- `example/rrwrite_v1/data_tables/research_indicators.tsv` - Topic detection results

### Section R2: Literature Search Validation (250 words)

#### Cascading Strategy Performance (Test Case: MicroGrowAgents)

**Tier 1 Search Results (2024-2026)**:
- Query: "AI microbial cultivation 2024", "agentic AI science 2025", "autonomous labs 2026"
- Papers found: 10 papers (3 Nature, 2 Scientific Reports, 2 npj, 3 arXiv)
- DOI resolution: 90% (9/10 valid DOIs, 1 arXiv preprint)

**Tier 2 Expansion (2020-2023)**:
- Query: "genome-scale metabolic modeling 2020..2023", "knowledge graphs biology 2021"
- Additional papers: 7 papers (2 Nature Communications, 3 PLOS, 2 Bioinformatics)
- Total: 17 papers (exceeded 15-paper target)
- **Decision**: Stopped before Tier 3, sufficient coverage

**Tier 3 Not Triggered**: Target met in Tier 2

**Version Reuse Performance**:
- Imported from v3: 20 papers (validated DOIs, no broken links)
- Extended with v4 search: 10 new papers (2024-2026)
- Total merged: 30 papers with no duplicates
- Processing time: Import (2 sec) + Validation (18 sec) + New search (45 sec) = 65 sec total

#### Evidence Files
- `manuscript/MicroGrowAgents_v4/literature_evidence.csv` - 30 validated papers
- `manuscript/MicroGrowAgents_v4/LITERATURE_RESEARCH_SUMMARY.md` - Search results
- `docs/cascading-literature-search.md` - Strategy documentation with examples

### Section R3: Citation Validation Results (250 words)

#### Defense-in-Depth Effectiveness (MicroGrowAgents v4 Case Study)

**Layer 1: Entry Validation**
- Total citations drafted: 37 citation instances across 6 sections
- Invalid citations caught: 0 (all citations pre-validated in literature_evidence.csv)
- False positives: 2 (`[oxidized]`, `[reduced]` - chemical notation in Nernst equation, not citations)

**Layer 2: Business Logic Validation**
- Sections validated: 6 (abstract, introduction, methods, results, discussion, availability)
- Inappropriate citations flagged: 0 violations
  - Methods: 6 citations (all tools: Bakta, GTDB, ChEBI, KEGG, MaxPro, LHS) ✓
  - Results: 10 citations (all data sources or benchmarks) ✓
  - Availability: 0 citations (factual only, no methodology papers) ✓

**Layer 3: Assembly Validation**
- Text citations extracted: 20 unique citations
- Bibliography entries: 22 entries (2 extra: `[oxidized]`, `[reduced]`)
- Orphaned text citations: 0
- Orphaned bibliography entries: 2 (false positives from chemical notation)
- **Outcome**: 100% citation-bib sync (excluding false positives)

**Layer 4: Audit Trail**
- Citation usage events logged: 37 events
- Forensic traces available: 37 JSON entries with timestamp, section, context, DOI status

#### Evidence Files
- `scripts/rrwrite_citation_validator.py` - Validator implementation (600 lines)
- `manuscript/MicroGrowAgents_v4/critique_content_v1.md` - Validation report
- `manuscript/MicroGrowAgents_v4/critique_format_v1.md` - Format compliance

### Section R4: Example Manuscript Generation (250 words)

#### MicroGrowAgents Nature Manuscript (v4)

**Input**: Repository with 2,877 files (Python codebase, data files, Jupyter notebooks)

**Processing Phases**:
1. Repository analysis: 157 files analyzed in 4 seconds
2. Outline generation: 432-word outline with 6 sections in 8 seconds
3. Literature research: 30 papers (20 imported + 10 new) in 65 seconds
4. Section drafting: 6 sections (2,954 words total) in 12 minutes
5. Assembly: Combined manuscript in 2 seconds
6. Two-stage critique: Content + format review in 15 seconds

**Output Statistics**:
- Total word count: 2,954 words (98.5% of 3,000-word Nature target)
- Sections: Abstract (151w), Introduction (437w), Results (888w), Discussion (780w), Methods (656w), Availability (100w)
- Citations: 20 unique citations (all with verified DOIs)
- Validation: 2 format issues (1-word abstract overflow, placeholder text)
- Content issues: 21 major (missing data file references for quantitative claims)

**Files Generated**: 15 files (outline, 6 sections, literature review, citations, critiques, state tracking)

#### Evidence Files
- `manuscript/MicroGrowAgents_v4/` - Complete example manuscript directory
- `manuscript/MicroGrowAgents_v4/manuscript_full.md` - Assembled 2,954-word manuscript
- `manuscript/MicroGrowAgents_v4/critique_content_v1.md` - 21 content issues identified
- `manuscript/MicroGrowAgents_v4/critique_format_v1.md` - 2 format issues identified

---

## Discussion

**Word Count**: 800 words (target), 400-1,000 words (range)
**Word Range**: 400-1000 words

### Purpose
Interpret results, compare to existing tools, discuss limitations, and outline future directions.

### Section D1: Comparison to Existing Approaches (250 words)

#### vs. General Writing Assistants (Grammarly, ChatGPT)
**Advantages**:
- Repository integration: RRWrite analyzes code/data directly; general assistants require manual input
- Structured workflow: 7-phase process with validation gates vs. freeform text generation
- Citation integrity: 4-layer validation vs. no citation checking
- Journal targeting: Format-aware from start vs. generic output

**Limitations**:
- Requires repository structure (code, data, docs); general assistants work with any text
- Domain-specific (scientific manuscripts); general assistants handle any genre

#### vs. LaTeX Editors (Overleaf, TeXShop)
**Advantages**:
- Content generation: RRWrite drafts text; LaTeX only formats
- Literature automation: Cascading search + DOI validation vs. manual BibTeX entry
- Evidence extraction: Repository analysis vs. manual methods documentation

**Limitations**:
- Output format: Markdown (requires conversion to LaTeX); LaTeX editors native
- Equation rendering: Limited to LaTeX syntax in Markdown; LaTeX has full support

#### vs. Reference Managers (Zotero, Mendeley)
**Advantages**:
- Literature search: Automated PubMed/SemanticScholar queries vs. manual import
- Evidence tracking: Quotes extracted automatically vs. manual note-taking
- Validation: Citation-text sync checking vs. passive bibliography management

**Limitations**:
- PDF management: No PDF storage; reference managers excel at library organization
- Manual entry: RRWrite requires PubMed/SemanticScholar hits; reference managers accept any source

### Section D2: Limitations and Future Directions (300 words)

#### Current Limitations

**1. Manuscript Quality**
- AI-generated text requires human review and refinement
- Domain expertise still needed for scientific accuracy
- Generated content may lack nuance or over-generalize

**2. Repository Requirements**
- Assumes structured repository (code, data, docs in conventional locations)
- Poor performance on unorganized repositories or pure documentation repos
- No support for non-code repositories (wet lab protocols, field notes)

**3. Citation Coverage**
- Cascading search may miss niche journals not indexed in PubMed/SemanticScholar
- No support for books, conference proceedings, or preprints (except arXiv)
- DOI validation requires internet; offline mode limited

**4. Journal Support**
- Currently supports 3 journals (Nature, Bioinformatics, PLOS)
- No support for domain-specific journals with unique requirements
- Supplementary materials generation not automated

#### Future Directions

**1. Enhanced Content Quality**
- Integration with theorem provers for mathematical claims
- Fact-checking against external databases (UniProt, PDB, KEGG)
- Multi-agent review system (separate agents for methods, results, discussion)

**2. Expanded Repository Support**
- Non-code repositories: Wet lab protocols, clinical trials, field studies
- Multi-repository manuscripts: Comparing multiple tools/datasets
- Historical repository analysis: Git history mining for methodology evolution

**3. Broader Journal Coverage**
- Templates for 20+ journals (Cell, Science, PNAS, PLOS Biology, BMC Bioinformatics)
- Automatic journal recommendation based on manuscript content and scope
- Supplementary materials generation (figures, extended methods, datasets)

**4. Collaborative Features**
- Multi-user editing with conflict resolution
- Reviewer response generation from critique feedback
- Revision tracking across manuscript versions

**5. Quality Assurance**
- Statistical validation of results claims
- Reproducibility checking (code execution, environment capture)
- Plagiarism detection integration

### Section D3: Broader Impact (250 words)

#### Democratizing Scientific Publishing

**Reducing Barriers**:
- Early-career researchers: Generate first drafts without extensive writing experience
- Non-native English speakers: Structured templates reduce language barriers
- Under-resourced labs: Free, open-source alternative to expensive writing services

**Accelerating Publication**:
- Manuscript generation: Days instead of weeks for initial drafts
- Iteration speed: Automated critique enables faster refinement cycles
- Multi-version workflows: Easy comparison between revisions

#### Improving Research Quality

**Reproducibility**:
- Repository integration ensures code/data linkage to claims
- Validation gates prevent incomplete or unsupported statements
- Audit trail provides provenance for all citations

**Citation Integrity**:
- 4-layer validation structurally prevents citation errors
- Automated DOI checking eliminates broken references
- Evidence tracking ensures claims backed by quotes

#### Ethical Considerations

**Authorship**:
- AI-assisted writing requires clear disclosure in manuscript
- Human authors retain responsibility for scientific content
- Tool is assistant, not author (analogous to Grammarly, not ghost-writer)

**Bias Mitigation**:
- Cascading literature search reduces recency bias while maintaining currency
- Multi-tier approach balances recent and foundational work
- Transparent algorithm enables bias detection and correction

#### Community Impact

**Open Science**:
- Open-source code enables community contributions
- Transparent validation rules foster reproducible writing practices
- Example manuscripts demonstrate best practices

---

## Availability

**Word Count**: 100 words (target), 50-150 words (range)
**Word Range**: 50-150 words

### Purpose
Provide access information for source code, documentation, and example outputs.

### Content

**Source Code**: Available at https://github.com/realmarcin/repo-research-writer under MIT License

**Installation**: Python 3.8+ required. Dependencies specified in repository documentation. No external databases required (uses PubMed and Semantic Scholar APIs via web requests).

**Documentation**: Complete workflow documentation, skill descriptions, and implementation guides in `docs/` directory. Example manuscripts in `example/` and `manuscript/` directories.

**Skills**: 9 Claude Code CLI skills (analyze, plan, research, draft, assemble, critique) in `.claude/skills/` directory.

**Scripts**: 20 Python implementation scripts in `scripts/` directory for validation, state management, table generation, and Git integration.

**Tutorial**: Quickstart guide and example workflows in README.md

### Evidence Files
- `README.md` - Installation and usage instructions
- `.claude/skills/*/SKILL.md` - 9 skill documentation files
- `scripts/` - 20 Python scripts
- `docs/` - 18 documentation files
- `example/` - Example manuscript outputs

---

## Figures (Suggested)

### Figure 1: RRWrite Workflow Architecture
- 7-phase workflow diagram: Analysis → Planning → Research → Drafting → Assembly → Critique → Revision
- Data flow between phases (repository → analysis → outline → literature → sections → manuscript → critique)
- Verification gates at each phase transition

**Source**: System architecture diagram (to be created from workflow documentation)

### Figure 2: Cascading Literature Search Strategy
- Flowchart showing tier-based search (Tier 1 → Tier 2 → Tier 3)
- Decision points (paper count thresholds)
- Example results for different research areas (active vs. niche)

**Source**: `docs/cascading-literature-search.md` algorithm description

### Figure 3: Defense-in-Depth Citation Validation
- 4-layer validation architecture (Entry → Business Logic → Assembly → Audit)
- Error interception at each layer
- Example validation failure and resolution

**Source**: `scripts/rrwrite_citation_validator.py` implementation

### Figure 4: Example Manuscript Generation Performance
- Timeline showing processing time for each phase (MicroGrowAgents case study)
- Word count distribution across sections
- Citation validation results

**Source**: `manuscript/MicroGrowAgents_v4/` metrics and timing data

---

## Tables (Suggested)

### Table 1: RRWrite Implementation Statistics
- Number of skills, scripts, documentation files
- Lines of code per component
- Test coverage (if applicable)

**Source**: Repository analysis of repo-research-writer itself

### Table 2: Cascading Literature Search Performance
- Tier 1, 2, 3 paper counts for different test cases
- Processing time per tier
- DOI validation success rate

**Source**: Literature search logs from MicroGrowAgents and other test repositories

### Table 3: Citation Validation Effectiveness
- Errors caught per validation layer (Entry, Business Logic, Assembly, Audit)
- False positive rate
- Time to validate (per section and full manuscript)

**Source**: `manuscript/MicroGrowAgents_v4/critique_*.md` validation reports

---

## Word Count Summary

| Section | Target | Min | Max | Evidence Files |
|---------|--------|-----|-----|----------------|
| Abstract | 200 | 150 | 250 | README.md, skills/ |
| Introduction | 500 | 400 | 800 | README.md, docs/, workflow docs |
| Methods | 1500 | 800 | 1600 | scripts/, .claude/skills/, docs/ |
| Results | 1000 | 600 | 1200 | example/, manuscript/, data_tables/ |
| Discussion | 800 | 400 | 1000 | Comparative analysis, limitations |
| Availability | 100 | 50 | 150 | README.md, repository metadata |
| **TOTAL** | **4100** | **2400** | **5000** | **All repository files** |

**Note**: Bioinformatics target is 6,000 words maximum. This outline targets 4,100 words for conciseness, leaving room for figures, tables, and references.

---

## Key Evidence Files by Section

### Abstract & Introduction
- `README.md` - Tool overview, features, installation
- `.claude/skills/rrwrite-workflow/SKILL.md` - Complete workflow
- `docs/cascading-literature-search.md` - Literature strategy

### Methods
- `scripts/rrwrite-analyze-repo.py` - Repository analyzer
- `scripts/rrwrite-research-literature.py` - Literature search
- `scripts/rrwrite_citation_validator.py` - 4-layer validation (600 lines)
- `scripts/rrwrite_state_manager.py` - State and Git management
- `.claude/skills/*/SKILL.md` - 9 skill implementations
- `docs/2-5-minute-rule.md` - Task decomposition
- `docs/citation-rules-by-section.md` - Validation rules

### Results
- `example/rrwrite_v1/repository_analysis.md` - Analysis output
- `example/rrwrite_v1/data_tables/` - Metrics and statistics
- `manuscript/MicroGrowAgents_v4/` - Example manuscript
- `manuscript/MicroGrowAgents_v4/critique_*.md` - Validation reports

### Discussion
- Comparative analysis with existing tools
- Limitation documentation
- Future directions from development notes

### Availability
- `README.md` - Installation and usage
- Repository structure

---

## Manuscript Focus: Software Utility for Bioinformatics

This outline emphasizes:

1. **Practical Application**: Solving the manuscript generation problem for computational researchers
2. **Technical Implementation**: Detailed architecture, algorithms, validation framework
3. **Performance Validation**: Quantitative metrics from real repository analyses
4. **Open Science**: Open-source availability, transparent algorithms, reproducible workflows
5. **Bioinformatics Relevance**: Repository analysis, literature mining, citation management for computational biology

---

## Next Steps

After outline approval:

1. **Literature Research**: Generate `literature.md` with citations for:
   - Scientific writing tools and assistants
   - AI-powered content generation
   - Citation management systems
   - Bioinformatics workflow automation
   - Validation and quality control in scientific writing

2. **Section Drafting**: Generate each section using evidence files specified above

3. **Figure/Table Creation**: Generate publication-quality figures from workflow diagrams and performance data

4. **Validation**: Verify word counts, citation completeness, schema compliance
