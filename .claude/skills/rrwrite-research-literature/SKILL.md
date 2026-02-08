---
name: rrwrite-research-literature
description: Performs deep literature research on manuscript topics and generates a comprehensive one-page summary of background and related work with citations.
arguments:
  - name: target_dir
    description: Output directory for manuscript files (e.g., manuscript/repo_v1)
    default: manuscript
allowed-tools:
context: fork
---
# Literature Research Protocol

## Purpose
Conduct comprehensive literature research on the manuscript topic and generate a structured summary of:
- Background context and foundations
- Related work and competing approaches
- Recent advances and state-of-the-art
- Gaps that the manuscript addresses

## Prerequisites
**Best if you have:**
- `manuscript_plan.md` (outline with research questions)
- Draft manuscript sections (especially Introduction/Methods)
- `references.bib` (existing citations to build upon)

**Minimum requirement:**
- PROJECT.md with clear research topic and key findings

## Workflow

### Phase 1: Topic Extraction
1. **Read Context Documents:**
   - Read `PROJECT.md` to understand the research domain
   - Read `manuscript_plan.md` if available (for detailed topics)
   - Read `{target_dir}/introduction.md` or `{target_dir}/abstract.md` if available
   - Read `references.bib` to see what's already cited

2. **Extract Key Research Topics:**
   - Primary methodology (e.g., "transformer-based protein structure prediction")
   - Domain area (e.g., "computational biology", "deep learning")
   - Specific techniques (e.g., "attention mechanisms", "MSA features")
   - Comparison methods (e.g., "AlphaFold2", "RoseTTAFold")

3. **Formulate Search Queries:**
   Create 3-5 targeted search queries combining:
   - Core method + domain
   - Technique + application
   - "Recent advances in [topic]"
   - "State of the art [domain]"
   - Each competing method mentioned

### Phase 2: Literature Search

**Use API-based search tools for reliable results:**

**2.1 Run Combined API Search**

Use the integrated literature search script with caching:

```bash
python3 scripts/rrwrite-search-literature.py \
  "[your search query]" \
  --max-results 20 \
  --cache-dir {target_dir}/.cache \
  --output {target_dir}/.cache/search_results.json
```

This searches:
- **Semantic Scholar API**: All domains, citation counts, recent papers
- **PubMed E-utilities**: Biomedical focus (if applicable)
- **24-hour cache**: Instant results for repeat searches

**2.2 Search Strategy**

Run 3-5 targeted searches:

1. **Foundational Papers** (core concepts)
   - Query: "[core method] review" OR "[domain] fundamentals"
   - API automatically prioritizes highly-cited papers (>100 citations)

2. **Recent Advances** (last 2 years, 2024-2026)
   - Query: "[method] 2024" OR "[method] recent advances"
   - API returns papers sorted by year + citations

3. **Direct Competitors** (methods you're comparing against)
   - Query: exact names of competing methods
   - Semantic Scholar finds original papers + citations

4. **Application Domain** (specific to your problem)
   - Query: "[your application] + [your method type]"
   - Example: "dataset documentation standards LinkML"

**2.3 Extract Paper Metadata**

The API automatically provides:
- **Authors**: Formatted string (e.g., "Smith J, Jones A, et al.")
- **Title**: Full paper title
- **Venue**: Journal/conference name
- **Year**: Publication year
- **DOI**: Digital Object Identifier (for citing)
- **PMID**: PubMed ID (for biomedical papers)
- **Abstract**: Full abstract text
- **Citations**: Citation count (from Semantic Scholar)
- **URL**: Direct link to paper

**For each relevant paper:**
- **Citation key**: Generate from first author + year (e.g., smith2024)
- **Direct quote**: Extract 1-2 sentences from abstract representing key finding

### Phase 3: Synthesis

Generate a structured summary in `{target_dir}/literature.md`:

```markdown
# Literature Review: [Manuscript Topic]

**Generated:** [Date]
**Based on:** [manuscript_plan.md / PROJECT.md]

## 1. Background & Foundations (200-300 words)

### Core Concepts
- [Topic 1]: Foundational work by [Author et al., Year]. Key insight: ...
- [Topic 2]: Established by [Author et al., Year]. Approach: ...

### Historical Context
- Evolution from [old method] to [current method]
- Major breakthrough: [cite landmark paper]

## 2. Related Work (300-400 words)

### Approach A: [Method Name]
- **Key Papers**: [Author1, Year], [Author2, Year]
- **Methodology**: [Brief description]
- **Strengths**: ...
- **Limitations**: ...

### Approach B: [Method Name]
- **Key Papers**: [Author3, Year], [Author4, Year]
- **Methodology**: [Brief description]
- **Strengths**: ...
- **Limitations**: ...

### Approach C: [Method Name]
- **Key Papers**: [Author5, Year]
- **Methodology**: [Brief description]
- **Strengths**: ...
- **Limitations**: ...

## 3. Recent Advances (200-300 words)

### State-of-the-Art
- [Recent Paper 1, 2024/2025]: Achieved [result]. Method: ...
- [Recent Paper 2, 2024/2025]: Novel approach using ...

### Current Trends
- Trend 1: [Description]
- Trend 2: [Description]

## 4. Research Gaps (100-150 words)

**Identified Gaps:**
1. [Gap 1 that your work addresses]
2. [Gap 2 that your work addresses]
3. [Gap 3 that your work addresses]

**How Our Work Fits:**
[Brief statement of how your manuscript fills these gaps]

## 5. Key Citations to Add

**Essential references to cite in manuscript:**

### Background (Introduction)
- [author2020]: Foundational work on [topic]
- [author2021]: Comprehensive review of [domain]

### Related Work (Methods/Discussion)
- [author2023]: Competing approach [Method A]
- [author2024]: Recent improvement to [Method B]
- [author2025]: State-of-the-art baseline

### Recent Comparisons (Results/Discussion)
- [author2024a]: Benchmark dataset
- [author2024b]: Performance comparison

## 6. Citation Integration Guide

**Where to cite what:**

**Introduction:**
- Cite [author2020, author2021] when introducing the problem
- Cite [author2023] when discussing prior approaches

**Methods:**
- Cite [author2022] when describing your architecture basis
- Cite [author2023] when contrasting with existing methods

**Results:**
- Cite [author2024a, author2024b] when presenting comparisons

**Discussion:**
- Cite [author2025] when positioning your work

---

## References to Add to references.bib

[Provide properly formatted BibTeX entries for all cited works]

```

### Phase 4: Citation File Generation

Create or update `bib_additions.bib` with BibTeX entries for all newly found papers:

```bibtex
@article{author2024,
  title={Title of Paper},
  author={Author, First and Author, Second},
  journal={Journal/Conference},
  year={2024},
  doi={10.1234/journal.2024.12345},
  url={https://doi.org/10.1234/journal.2024.12345}
}
```

**CRITICAL**: Always include DOI when available. DOIs are permanent identifiers and essential for verification.

### Phase 5: Evidence Documentation

Create `{target_dir}/literature_evidence.md` in markdown format:

```markdown
# Literature Evidence

**Generated**: [Date]
**Purpose**: Verbatim quotes supporting cited claims

---

## [citation_key]: [Paper Title]

**Authors**: [Author list]
**Venue**: [Journal/Conference, Year]
**DOI**: [DOI or arXiv]
**URL**: [Direct link]

**Evidence Quote**:
> "[Verbatim quote from abstract or paper capturing key finding/contribution]"

**Key Findings**:
- [Specific result, metric, or claim]
- [Novel method or approach]
- [Quantitative improvement if applicable]

---

## Example:

## gebru2021: Datasheets for Datasets

**Authors**: Gebru T, Morgenstern J, Vecchione B, et al.
**Venue**: Communications of the ACM, 2021
**DOI**: 10.1145/3458723
**URL**: https://doi.org/10.1145/3458723

**Evidence Quote**:
> "Currently there is no standard way to identify how a dataset was created, and what characteristics, motivations, and potential skews it represents. To address this gap, we propose datasheets for datasets."

**Key Findings**:
- Proposes structured documentation framework for datasets
- Covers motivation, composition, collection, preprocessing, uses, distribution, maintenance
- Analogous to datasheets in electronics manufacturing
- Addresses transparency and accountability in AI/ML

---
```

**Requirements for evidence quotes:**
- Extract 1-2 sentences that capture the KEY finding or contribution
- Use direct quotes (verbatim from the paper abstract or full text)
- Focus on quantitative results or novel methodological claims
- Include enough context to verify the claim independently
- Ensure quote is self-contained and understandable
- Include page number in comment if possible

## Output Files

Generate **three files** in the `{target_dir}/` directory (per schema: schemas/manuscript.yaml):

1. **`{target_dir}/literature.md`**
   - One-page structured summary (800-1000 words)
   - Organized by themes, not chronologically
   - Includes citation keys in [author2024] format
   - **Each citation includes DOI**: e.g., [jumper2021, DOI:10.1038/...]
   - Required sections: Background, Related Work, Recent Advances, Research Gaps

2. **`{target_dir}/literature_citations.bib`**
   - BibTeX entries for all newly found references
   - **Must include DOI field** for each entry
   - Ready to append to existing references.bib

3. **`{target_dir}/literature_evidence.csv`**
   - **Three columns**: doi, citation_key, evidence
   - Direct quotes from each cited paper
   - Enables verification and evidence chains
   - Can be used to check claims against original sources

## Validation

After generating files, validate the literature review:
```bash
python scripts/rrwrite-validate-manuscript.py --file {target_dir}/literature.md --type literature
```

## State Update

After successful validation, update workflow state:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path('scripts').resolve()))
from rrwrite_state_manager import StateManager

manager = StateManager(output_dir="{target_dir}")
# Count papers from literature_citations.bib
import re
with open('{target_dir}/literature_citations.bib', 'r') as f:
    papers_found = len(re.findall(r'^@\w+{', f.read(), re.MULTILINE))

manager.update_workflow_stage("research", status="completed",
                              file_path="{target_dir}/literature.md",
                              papers_found=papers_found)
```

Display updated progress:
```bash
python scripts/rrwrite-status.py --output-dir {target_dir}
```

If validation passes, confirm completion and show progress. If it fails, fix issues and re-validate.

## Quality Criteria

**Ensure the literature review:**
- ✅ Covers foundational work (pre-2020)
- ✅ Includes recent advances (2024-2026)
- ✅ Identifies all major competing approaches
- ✅ Explains relationships between methods
- ✅ Highlights gaps your work addresses
- ✅ Provides actionable integration guidance
- ✅ All citations are real and verifiable
- ✅ BibTeX entries are properly formatted
- ✅ **DOIs included for all papers** (when available)
- ✅ **Evidence quotes captured** for verification
- ✅ **literature_evidence.csv created** with direct quotes

## Search Strategy Notes

**Coverage targets:**
- 15-25 papers total
- 3-5 foundational/review papers
- 5-8 directly related work papers
- 4-6 recent advances (last 2 years)
- 2-4 competing method papers

**Quality indicators for papers:**
- Published in top-tier venues (Nature, Science, NeurIPS, ICML, ICLR)
- High citation count (>50 for recent, >500 for foundational)
- Relevant to your specific approach and domain
- Provides reproducible benchmarks or datasets

**Verification:**
- Cross-check papers exist via multiple sources
- **Prioritize papers with DOIs** (permanent identifiers)
- Accept arXiv IDs for preprints (format: arXiv:YYMM.NNNNN)
- Verify author names and publication years
- Confirm venue/journal names are correct
- **Extract direct quote from abstract or key results section**
- Record quote in evidence file for later verification

## Integration with Drafting

After generating the literature review:

1. **Update Introduction:**
   - Integrate background citations from Section 1
   - Add related work references from Section 2

2. **Update Methods:**
   - Add citations justifying methodological choices
   - Reference papers you're building upon or modifying

3. **Update Discussion:**
   - Compare your results to recent state-of-the-art
   - Position your work in context of current trends

4. **Inform Future Work:**
   - Cite papers suggesting future directions
   - Reference emerging techniques to try

## Example Usage

```
User: "Use /rrwrite-research-literature to research the background for my protein structure prediction paper"

Agent:
1. Reads PROJECT.md and manuscript_plan.md
2. Extracts topics: "transformer architecture", "protein folding", "AlphaFold2", "attention mechanisms"
3. Searches for:
   - "protein structure prediction review 2024"
   - "transformer protein folding"
   - "AlphaFold2 improvements 2024"
   - "attention mechanisms structural biology"
4. Finds 20 relevant papers with DOIs
5. Extracts direct quotes from each paper
6. Generates:
   - literature_review.md (structured summary, 950 words)
   - bib_additions.bib (20 BibTeX entries with DOIs)
   - literature_evidence.csv (20 rows with DOIs and quotes)
   - literature_integration_notes.md
7. Provides integration guidance

Output: "✓ Literature review complete. Found 20 relevant papers (5 foundational, 8 related work, 7 recent). Generated manuscript/literature.md (950 words), manuscript/literature_citations.bib (20 entries with DOIs), and manuscript/literature_evidence.csv (20 evidence quotes)."
```

## Evidence File Example

`literature_evidence.csv`:
```csv
doi,citation_key,evidence
10.1038/s41586-021-03819-2,jumper2021,"We developed AlphaFold, a deep learning system that predicts protein structures with atomic accuracy even in cases in which no similar structure is known. AlphaFold achieved a median accuracy of 92.4 GDT on CASP14 targets."
10.1126/science.abj8754,baek2021,"RoseTTAFold can generate accurate models of protein structures and complexes using as input only a protein sequence. The method achieves accuracy comparable to AlphaFold while being more computationally efficient."
10.1038/s41467-024-12345-6,yang2024,"We demonstrate that pre-trained protein language models can reduce MSA requirements by 80% while maintaining prediction accuracy above 85% on CASP15 targets."
arXiv:2401.12345,zhang2025,"Our efficient transformer architecture achieves real-time protein structure prediction (< 1 second per protein) with only 5% accuracy loss compared to AlphaFold2."
```

**Using the evidence file:**
- Cross-reference claims in your manuscript with direct quotes
- Verify that your interpretation aligns with original sources
- Provide evidence for peer reviewers if challenged
- Enable reproducible claim verification

## Limitations & Handling

**If no manuscript outline exists:**
- Use PROJECT.md "Key Findings" to infer topics
- Focus on broader domain literature
- Request user clarification on specific sub-topics

**If references.bib already extensive:**
- Compare found papers with existing citations
- Flag papers that should be added
- Suggest papers that might be outdated or less relevant

**If topic is very niche:**
- Expand search to broader domain
- Include methodological foundations even if not domain-specific
- Flag if insufficient literature found (suggest broadening)

## Notes

- **DO NOT hallucinate papers** - Only cite papers found via WebSearch or in references.bib
- **Verify all citations** - Double-check author names, years, venues
- **Always capture DOIs** - Essential for permanent identification and verification
- **Extract exact quotes** - Copy verbatim from paper abstract or results, no paraphrasing
- **Be selective** - Quality over quantity; cite only the most relevant papers
- **Stay current** - Prioritize papers from last 2-3 years for "Recent Advances"
- **Cross-reference** - If a paper cites another relevant paper, follow the trail
- **Use WebFetch if needed** - To read paper abstracts and extract accurate quotes
- **Format evidence properly** - Ensure CSV is properly escaped (quotes within quotes)
