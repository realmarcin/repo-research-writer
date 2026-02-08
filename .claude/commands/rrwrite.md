# RRWrite: Research Repository to Manuscript

**Complete pipeline for generating academic manuscripts from research repositories**

This command orchestrates the full RRWrite workflow from repository analysis through manuscript drafting and critique.

## Overview

RRWrite transforms research code repositories into publication-ready manuscripts by:
1. Analyzing repository structure and code
2. Planning manuscript outline based on findings
3. **Assessing journal fit and fetching author guidelines** ← NEW STEP
4. Conducting targeted literature research
5. Drafting sections with proper citations
6. **Assembling complete manuscript from sections** ← NEW STEP
7. Critiquing for quality and guideline compliance

## Workflow Pipeline (9 Steps)

###  Step 1: Repository Analysis

Analyze the source repository to extract key information about the research.

```bash
python scripts/rrwrite-analyze-repo.py --repo-path <path> --output-dir <target_dir>
```

**Outputs:**
- `<target_dir>/repository_analysis.md` - Repository structure, code analysis, key findings

### Step 2: Version Management

Automatically increment version number for new manuscript iterations.

**Convention:** `<repo_name>_v<N>` (e.g., `my_repo_v1`, `my_repo_v2`)

### Step 3: Planning

Generate manuscript outline based on repository analysis and target journal.

```bash
/rrwrite-plan-manuscript --target-dir <target_dir> --journal <journal>
```

**Inputs:**
- Repository analysis from Step 1
- Target journal selection (default: bioinformatics)

**Outputs:**
- `<target_dir>/outline.md` - Structured manuscript outline
- `<target_dir>/.rrwrite/state.json` - Workflow state initialized

**Available journals:**
- `bioinformatics` - Oxford Academic Bioinformatics
- `nature_methods` - Nature Methods
- `plos_computational_biology` - PLOS Computational Biology
- `bmc_bioinformatics` - BMC Bioinformatics
- `genome_biology` - Genome Biology
- `cell_systems` - Cell Systems
- `nucleic_acids_research` - Nucleic Acids Research

### Step 4: Journal Assessment ← **NEW STEP**

Analyze outline suitability for target journal, recommend alternatives if needed, and fetch comprehensive author guidelines.

```bash
/rrwrite-assess-journal --target-dir <target_dir> --initial-journal <journal>
```

**What this step does:**
1. **Compatibility Analysis**
   - Extracts keywords from outline
   - Scores compatibility with initial journal (0.0-1.0)
   - Analyzes structural alignment with journal requirements
   - Identifies missing required sections

2. **Journal Recommendations** (if score < 0.7)
   - Scores outline against all available journals
   - Ranks top 3 alternative journals with explanations
   - Provides detailed reasoning for each recommendation

3. **User Confirmation**
   - Prompts user to confirm initial journal or switch to alternative
   - Explains implications of journal choice
   - Respects user decision even if score is low

4. **Guidelines Fetching**
   - Retrieves comprehensive author guidelines for confirmed journal
   - Includes: scope, structure, word limits, citation rules, special requirements
   - Generates compliance checklist

5. **Assessment Report**
   - Creates detailed report with compatibility analysis
   - Documents journal selection rationale
   - Lists required adjustments (if any)

**Outputs:**
- `<target_dir>/journal_assessment.md` - Compatibility analysis and recommendations
- `<target_dir>/author_guidelines.md` - Comprehensive journal guidelines with checklist
- Updated `<target_dir>/.rrwrite/state.json` - Assessment stage completed

**When to run:**
- **REQUIRED** after planning and before literature research
- Ensures manuscript development aligns with journal requirements from the start
- Prevents wasted effort on incompatible journal targets

**Example scoring:**
- **≥ 0.75**: Excellent match, proceed with confidence
- **0.60-0.74**: Good match, minor adjustments recommended
- **0.45-0.59**: Moderate match, consider alternatives or revise outline
- **< 0.45**: Poor match, strongly recommend alternative journal

### Step 5: Literature Research

Extract topics from outline and conduct journal-scope-aware literature review.

```bash
/rrwrite-research-literature --target-dir <target_dir>
```

**Inputs:**
- Outline from Step 3
- **Author guidelines from Step 4** (if available) ← NEW
  - Filters papers by journal scope
  - Prioritizes papers published in target journal
  - Excludes out-of-scope research areas

**Outputs:**
- `<target_dir>/literature.md` - Comprehensive literature review with citations
- Citation index for downstream drafting

**Enhancements with assessment:**
- Research focuses on journal-relevant topics
- Papers are pre-filtered for scope compatibility
- Literature matches journal's typical citation style

### Step 6: Section Drafting

Draft individual manuscript sections with fact-checking and guideline compliance.

```bash
/rrwrite-draft-section <section> --target-dir <target_dir>
```

**Available sections:**
- `introduction`
- `methods` (or `algorithm`, `implementation` depending on journal)
- `results`
- `discussion`
- `availability` (or `data_availability`)
- `abstract` (draft last, after all sections complete)

**Inputs:**
- Outline from Step 3
- Literature review from Step 5
- Repository analysis from Step 1
- **Author guidelines from Step 4** ← NEW
  - Section-specific word limits enforced
  - Citation rules applied per section
  - Special formatting requirements followed
  - Journal-specific terminology used

**Guidelines Integration:**

Before drafting ANY section, the skill automatically:
1. Loads author guidelines from `<target_dir>/author_guidelines.md`
2. Extracts section-specific requirements:
   - Word count limits (min-max range)
   - Citation rules for this section
   - Special requirements (e.g., "Methods at end" for Nature Methods)
3. Applies guidelines during drafting:
   - Adheres to word limits
   - Follows citation style (numbered vs. author-year)
   - Implements journal-specific formatting
   - Respects section positioning rules

**Example guideline applications:**
- **Bioinformatics**: Methods section includes algorithm details, cites specific tools/datasets used
- **Nature Methods**: Methods section is brief in main text, extensive details in Online Methods
- **PLOS Computational Biology**: Includes Author Summary (non-technical), emphasizes biological insight

**Outputs:**
- `<target_dir>/<section>.md` - Drafted section with citations
- Updated state tracking section completion

### Step 6.5: Manuscript Assembly ← **NEW STEP**

Assemble complete manuscript from individual section files into a single reproducible document.

```bash
/rrwrite-assemble-manuscript --target-dir <target_dir> --validate
```

**What this step does:**
1. **Load Journal Guidelines**
   - Reads author guidelines from assessment step
   - Determines correct section order for target journal
   - Gets word limit requirements

2. **Find Section Files**
   - Locates all drafted section files
   - Handles common naming variations (e.g., methods vs. materials_and_methods)
   - Identifies missing required sections

3. **Concatenate in Correct Order**
   - Orders sections per journal requirements
   - Adds section markers for reproducibility
   - Handles journal-specific ordering (e.g., Nature Methods: Methods at END)

4. **Add Metadata Header**
   - Title and authors
   - Target journal
   - Assembly timestamp
   - Total word count

5. **Calculate Statistics**
   - Word count per section
   - Total word count
   - Sections included vs. missing

6. **Validate Against Limits**
   - Checks total word count against journal limit
   - Validates section word counts
   - Flags violations (exceeds maximum) and warnings (below minimum)

7. **Generate Assembly Manifest**
   - JSON manifest with complete assembly metadata
   - Tracks sections included, word counts, warnings
   - Enables reproducibility

**Inputs:**
- All drafted section files from Step 6
- Author guidelines from Step 4 (for section order and word limits)
- Workflow state for journal and metadata

**Outputs:**
- `<target_dir>/manuscript.md` - Complete assembled manuscript
- `<target_dir>/assembly_manifest.json` - Assembly metadata and statistics
- Updated state tracking assembly completion

**Example Output:**
```
Assembling manuscript for: Bioinformatics
Target directory: manuscript/repo_v1

Section order (10 sections):
  1. abstract
  2. introduction
  3. methods
  4. results
  5. discussion
  6. data_availability
  ...

✓ Found: abstract (abstract.md) - 247 words
✓ Found: introduction (introduction.md) - 1,423 words
✓ Found: methods (methods.md) - 2,156 words
✓ Found: results (results.md) - 1,876 words
✓ Found: discussion (discussion.md) - 1,102 words
✓ Found: data_availability (availability.md) - 127 words
⚠ Missing: references

============================================================
✓ Manuscript assembled successfully!
============================================================

Output: manuscript/repo_v1/manuscript.md
Total word count: 6,931 words
Sections included: 6
Sections missing: 1

Word Count Validation:
✓ Total word count within limits: 6,931 words (3000-7000)
✓ abstract: 247 words (within 150-250)
✓ introduction: 1,423 words (within 500-1500)
❌ methods: 2,156 words > 2000 (maximum)
✓ results: 1,876 words (within 1000-2000)
✓ discussion: 1,102 words (within 500-1500)
✓ data_availability: 127 words (within 50-150)
```

**When to run:**
- **REQUIRED** after all (or most) sections are drafted
- **BEFORE** critique (critique validates the complete manuscript)
- **Can be rerun** after editing sections (idempotent and reproducible)

**Why it matters:**
1. **Single Source of Truth**: One complete manuscript.md file instead of scattered sections
2. **Correct Ordering**: Sections arranged per journal requirements automatically
3. **Word Count Validation**: Catches length issues before submission
4. **Reproducibility**: Manifest tracks exactly what was assembled and when
5. **Critique Input**: Critique validates the complete assembled manuscript

**Handling Warnings:**
- **Missing sections**: Re-run after drafting missing sections
- **Word count violations**: Edit section files, then reassemble
- **Order issues**: Handled automatically based on journal guidelines

### Step 7.5: Manuscript Critique

Perform adversarial critique against journal requirements and quality standards.

```bash
/rrwrite-critique-manuscript --target-dir <target_dir>
```

**Critique Categories:**

1. **Factual Accuracy** - Verify claims against repository code/data
2. **Citation Quality** - Check citation appropriateness and completeness
3. **Logical Flow** - Assess narrative coherence
4. **Technical Depth** - Evaluate methodological detail
5. **Clarity** - Check readability and terminology
6. **Completeness** - Verify all required content present
7. **Author Guidelines Compliance** ← NEW
   - Section order matches journal requirements
   - Special sections present (e.g., Author Summary for PLOS)
   - Word limits respected (total + per-section)
   - Citation style correct (numbered vs. author-year)
   - Reference count within limit
   - Journal-specific requirements met
   - Figures/tables within limits

**Guidelines Compliance Checks:**

The critique automatically validates:
- ✓ All required sections present and in correct order
- ✓ Section-specific word counts within limits
- ✓ Total manuscript length complies with journal limits
- ✓ Citations formatted correctly (numbered vs. author-year)
- ✓ Reference count ≤ journal limit
- ✓ Section-specific citation rules followed
- ✓ Special requirements met (e.g., Data Availability statement)
- ✓ Figures and tables within limits
- ✓ Journal-specific formatting applied

**Example violations flagged:**
- ❌ "PLOS Computational Biology requires 'Author Summary' section (non-technical) - MISSING"
- ❌ "Methods section exceeds word limit: 2800 words (limit: 2500)"
- ❌ "Nature Methods: Methods section should be at END, currently at position 2"
- ❌ "Reference count (65) exceeds limit (50) for Bioinformatics"

**Inputs:**
- All drafted sections
- Outline for structure validation
- Repository analysis for factual verification
- **Author guidelines for compliance checking** ← NEW

**Outputs:**
- `<target_dir>/critique.md` - Detailed critique with issues categorized by severity
- Issue counts (major/minor) in workflow state

### Step 8.5: Progress Report

Display current workflow status with all stages.

```bash
python scripts/rrwrite-status.py --output-dir <target_dir> [--verbose]
```

**Displays:**
- Overall progress (percentage, current stage)
- Status of each workflow stage:
  - Repository Analysis
  - Planning
  - **Journal Assessment** ← NEW
    - Initial vs. confirmed journal
    - Compatibility score
    - Guidelines availability
    - Required adjustments count
  - Literature Research
  - Drafting (with section-by-section progress)
  - **Assembly** ← NEW
    - Manuscript file created
    - Sections included/missing
    - Total word count
    - Validation warnings
  - Critique
- Generated files list
- Manuscript statistics (word count, citations, figures, tables)

**Assessment Stage Display:**
```
✓ Journal Assessment: COMPLETED
   Initial Journal: bioinformatics
   Confirmed Journal: bioinformatics
   Compatibility: ✓ 85% (0.85/1.00)
   ✓ Guidelines: manuscript/repo_v1/author_guidelines.md
```

or if journal was switched:

```
✓ Journal Assessment: COMPLETED
   Initial Journal: bioinformatics
   Confirmed Journal: plos_computational_biology
   Compatibility: ✓ 92% (0.92/1.00)
   ⚠ Journal switched (better match recommended)
   ✓ Guidelines: manuscript/repo_v1/author_guidelines.md
```

## Complete Usage Example

```bash
# Step 1: Analyze repository
python scripts/rrwrite-analyze-repo.py --repo-path ./my-research-repo --output-dir manuscript/my_repo_v1

# Step 2: Version is auto-determined (my_repo_v1)

# Step 3: Generate outline
/rrwrite-plan-manuscript --target-dir manuscript/my_repo_v1 --journal bioinformatics

# Step 4: Assess journal fit and fetch guidelines ← NEW STEP
/rrwrite-assess-journal --target-dir manuscript/my_repo_v1 --initial-journal bioinformatics
# → Analyzes compatibility, may recommend alternatives
# → User confirms journal (or switches)
# → Fetches comprehensive guidelines

# Step 5: Conduct literature research (now journal-aware)
/rrwrite-research-literature --target-dir manuscript/my_repo_v1

# Step 6: Draft sections (now guideline-aware)
/rrwrite-draft-section introduction --target-dir manuscript/my_repo_v1
/rrwrite-draft-section methods --target-dir manuscript/my_repo_v1
/rrwrite-draft-section results --target-dir manuscript/my_repo_v1
/rrwrite-draft-section discussion --target-dir manuscript/my_repo_v1
/rrwrite-draft-section availability --target-dir manuscript/my_repo_v1
/rrwrite-draft-section abstract --target-dir manuscript/my_repo_v1

# Step 6.5: Assemble complete manuscript ← NEW STEP
/rrwrite-assemble-manuscript --target-dir manuscript/my_repo_v1 --validate
# → Concatenates sections in correct order
# → Validates word counts against journal limits
# → Creates manuscript.md + assembly_manifest.json

# Step 7.5: Critique manuscript (now includes guideline compliance)
/rrwrite-critique-manuscript --target-dir manuscript/my_repo_v1

# Step 8.5: Check status
python scripts/rrwrite-status.py --output-dir manuscript/my_repo_v1 --verbose
```

## When to Use Journal Assessment

**ALWAYS run assessment** after planning and before any other steps:
- ✅ **Before literature research** - Ensures papers match journal scope
- ✅ **Before drafting** - Applies correct guidelines from the start
- ✅ **After major outline changes** - Re-verify compatibility

**Benefits:**
1. **Prevents mismatch** - Catches incompatible journal choices early
2. **Saves time** - Avoids rewriting entire manuscript for different journal
3. **Improves quality** - Guidelines applied consistently throughout
4. **Increases acceptance odds** - Manuscript follows journal requirements exactly

## Pipeline Integration Points

The assessment step integrates at multiple points:

```
Planning → ASSESSMENT → Research → Drafting → Critique
    ↓          ↓            ↓          ↓         ↓
  outline  guidelines   filter by  apply     validate
  created   fetched     journal    rules     compliance
                        scope
```

## Output Files Summary

After complete pipeline execution:

```
manuscript/my_repo_v1/
├── .rrwrite/
│   └── state.json                    # Workflow state tracking
├── repository_analysis.md             # Step 1: Repo analysis
├── outline.md                         # Step 3: Manuscript outline
├── journal_assessment.md              # Step 4: ← NEW Assessment report
├── author_guidelines.md               # Step 4: ← NEW Comprehensive guidelines
├── literature.md                      # Step 5: Literature review
├── introduction.md                    # Step 6: Drafted sections
├── methods.md
├── results.md
├── discussion.md
├── availability.md
├── abstract.md
└── critique.md                        # Step 7: Critique report
```

## Troubleshooting

### Assessment Issues

**Problem:** "Compatibility score too low (< 0.7)"
**Solution:**
- Review recommended alternative journals
- Consider revising outline to better match journal scope
- User can proceed anyway if confident in choice

**Problem:** "Missing required sections in outline"
**Solution:**
- Add missing sections to outline before proceeding
- Or acknowledge sections will be added during drafting

**Problem:** "Journal not found in database"
**Solution:**
- Check available journals with `--journal` flag
- Use one of the 7 supported journals
- Or add new journal to `templates/journal_guidelines.yaml`

### Guideline Application Issues

**Problem:** "Guidelines not applied during drafting"
**Solution:**
- Verify `author_guidelines.md` exists in target_dir
- Re-run assessment step if guidelines file missing
- Check skill is reading guidelines (check skill logs)

**Problem:** "Word count violations in critique"
**Solution:**
- Review word limits in author_guidelines.md
- Edit sections to comply with limits
- Some journals have strict limits (e.g., Nature Methods: 3000 words total)

## Advanced Usage

### Re-assessing After Outline Changes

If outline is significantly revised:

```bash
# Re-run assessment to verify still compatible
/rrwrite-assess-journal --target-dir manuscript/my_repo_v1 --initial-journal bioinformatics

# Guidelines will be refreshed
# New compatibility score computed
```

### Switching Journals Mid-Pipeline

If you need to switch journals after drafting has started:

```bash
# 1. Re-run assessment with new journal
/rrwrite-assess-journal --target-dir manuscript/my_repo_v1 --initial-journal nature_methods

# 2. Review guideline differences carefully
diff manuscript/my_repo_v1/author_guidelines.md.backup manuscript/my_repo_v1/author_guidelines.md

# 3. Re-draft sections that don't comply with new guidelines
/rrwrite-draft-section methods --target-dir manuscript/my_repo_v1  # Re-draft

# 4. Re-critique with new guidelines
/rrwrite-critique-manuscript --target-dir manuscript/my_repo_v1
```

### Viewing Guidelines Only

To view guidelines for a journal without running full assessment:

```bash
python scripts/rrwrite-fetch-guidelines.py \
  --journal bioinformatics \
  --guidelines templates/journal_guidelines.yaml \
  --output guidelines_preview.md
```

### Comparing Journals

To compare compatibility across all journals:

```bash
python scripts/rrwrite-recommend-journal.py \
  --outline manuscript/my_repo_v1/outline.md \
  --guidelines templates/journal_guidelines.yaml \
  --top 7 \
  --show-scores
```

## Notes

- **Assessment is recommended but not mandatory** - Pipeline can skip to research if user prefers
- **User always has final say** - Assessment recommends but respects user choice
- **Guidelines are advisory** - Critique flags violations but drafting continues
- **State is persisted** - Progress tracked across sessions in `.rrwrite/state.json`
- **Modular execution** - Can run steps individually or as full pipeline
- **Version control friendly** - All outputs are markdown files suitable for git tracking

## See Also

- `/rrwrite-plan-manuscript` - Detailed planning skill documentation
- `/rrwrite-assess-journal` - Detailed assessment skill documentation
- `/rrwrite-draft-section` - Detailed drafting skill documentation
- `/rrwrite-critique-manuscript` - Detailed critique skill documentation
- `templates/journal_guidelines.yaml` - Journal guidelines database
- `scripts/rrwrite-status.py` - Status dashboard documentation
