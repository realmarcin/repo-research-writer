---
name: cluewrite-research-literature
description: Performs deep literature research on manuscript topics and generates a comprehensive one-page summary of background and related work with citations.
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
   - Read `drafts/introduction.md` or `drafts/abstract.md` if available
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

**Use WebSearch tool to find:**
1. **Foundational Papers** (highly cited, >1000 citations)
   - Query: "[core method] review" OR "[domain] survey"
   - Focus on papers from last 5 years for reviews, last 10 for foundations

2. **Recent Advances** (last 2 years, 2024-2026)
   - Query: "[method] 2024" OR "[method] 2025" OR "[method] 2026"
   - Look for: NeurIPS, ICLR, ICML, Nature, Science papers

3. **Direct Competitors** (methods you're comparing against)
   - Query: exact names of competing methods
   - Find their original papers and recent improvements

4. **Application Domain** (specific to your problem)
   - Query: "[your application] + [your method type]"
   - Example: "protein structure prediction transformers"

**For each relevant paper found:**
- Extract: Authors, Title, Venue, Year
- Note: Key contribution, methodology, results
- Record: Citation key format (e.g., author2024)

### Phase 3: Synthesis

Generate a structured summary in `drafts/literature_review.md`:

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
  url={https://...}
}
```

## Output Files

Generate three files:

1. **`drafts/literature_review.md`**
   - One-page structured summary (800-1000 words)
   - Organized by themes, not chronologically
   - Includes citation keys in [author2024] format

2. **`bib_additions.bib`**
   - BibTeX entries for all newly found references
   - Ready to append to existing references.bib

3. **`literature_integration_notes.md`**
   - Suggestions for where to integrate citations into existing draft
   - Gaps in current draft that literature addresses
   - Potential rewrites to strengthen positioning

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
- Prefer papers with DOIs or arXiv IDs
- Verify author names and publication years
- Confirm venue/journal names are correct

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
User: "Use cluewrite-research-literature to research the background for my protein structure prediction paper"

Agent:
1. Reads PROJECT.md and manuscript_plan.md
2. Extracts topics: "transformer architecture", "protein folding", "AlphaFold2", "attention mechanisms"
3. Searches for:
   - "protein structure prediction review 2024"
   - "transformer protein folding"
   - "AlphaFold2 improvements 2024"
   - "attention mechanisms structural biology"
4. Finds 20 relevant papers
5. Generates literature_review.md with structured summary
6. Creates bib_additions.bib with BibTeX entries
7. Provides integration guidance

Output: "✓ Literature review complete. Found 20 relevant papers (5 foundational, 8 related work, 7 recent). Generated drafts/literature_review.md (950 words) and bib_additions.bib (20 entries)."
```

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
- **Be selective** - Quality over quantity; cite only the most relevant papers
- **Stay current** - Prioritize papers from last 2-3 years for "Recent Advances"
- **Cross-reference** - If a paper cites another relevant paper, follow the trail
