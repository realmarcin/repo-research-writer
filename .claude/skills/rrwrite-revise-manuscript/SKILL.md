---
name: rrwrite-revise-manuscript
description: Automatically revise manuscript based on critique reports using iterative refinement with convergence detection
arguments:
  - name: manuscript_dir
    description: Manuscript directory containing critique reports
    default: manuscript
  - name: max_iterations
    description: Maximum number of revision iterations
    default: 2
  - name: min_improvement
    description: Minimum improvement rate to continue (0.05 = 5%)
    default: 0.05
  - name: dry_run
    description: Show planned revisions without saving changes
    default: false
allowed-tools:
context: fork
---
# Automated Manuscript Revision Protocol

## Purpose
Iteratively revise manuscript sections based on critique reports to address major and minor issues with automated convergence detection.

## Prerequisites

**Required files in {manuscript_dir}:**
- `critique_content_v1.md` - Content critique report
- `critique_format_v1.md` - Format critique report
- `literature_evidence.csv` - Citation database
- `repository_analysis.md` - Repository metadata
- Section files: `abstract.md`, `introduction.md`, `methods.md`, `results.md`, `discussion.md`

**Required state:**
- Critique must be completed first
- At least one major or minor issue present

## How It Works

The revision system uses a **modular orchestrator** architecture:

1. **Parse critique reports** → Extract structured issues with severity/category
2. **Map issues to sections** → Infer which section each issue belongs to
3. **Revise sections** → Apply specialized revisers (rule-based + LLM)
4. **Re-assemble manuscript** → Combine revised sections
5. **Re-run critique** → Generate new critique report
6. **Check convergence** → Stop if major issues resolved or stalled
7. **Iterate** → Repeat until convergence or max iterations

## Convergence Criteria

Revision stops when ANY of these conditions are met:

1. **Major issues resolved**: All major issues fixed ✓ (Primary goal)
2. **Max iterations reached**: Hit iteration limit
3. **Stalled**: < 5% improvement in last iteration
4. **Worsened**: More issues than before (rare)

## Revision Strategies

### Evidence Issues
- **Strategy**: Search `literature_evidence.csv` for relevant citations
- **Action**: Insert citations near claims lacking evidence
- **Example**: "Strong claim" → "Strong claim [author2024]"

### Word Count Issues
- **Strategy**: LLM-based condensation
- **Action**: Preserve key points while reducing words
- **Example**: Abstract 151 words → 150 words

### Reproducibility Issues
- **Strategy**: Extract from `repository_analysis.md`
- **Action**: Add software versions, parameters, data sources
- **Example**: Add "Software: Python 3.9, pandas 1.5.0"

### Citation Format Issues
- **Strategy**: Rule-based regex correction
- **Action**: Convert malformed citations to [Author2024] format
- **Example**: "[1]" → "[smith2024]" (if detectable)

### Interpretation Issues (Results section)
- **Strategy**: Flag for manual review
- **Action**: Warn about interpretation statements in Results
- **Example**: Flag "this suggests that..." for Discussion move

## Workflow

### Phase 1: Check Prerequisites

1. **Verify critique exists:**
   ```bash
   cd {manuscript_dir}

   if [ ! -f "critique_content_v1.md" ]; then
       echo "Error: No critique found. Run /rrwrite-critique-manuscript first"
       exit 1
   fi
   ```

2. **Check issue count:**
   ```python
   from rrwrite_revision_parser import CritiqueParser

   parser = CritiqueParser("{manuscript_dir}")
   issues = parser.parse_critique_reports(version=1)
   metrics = parser.count_issues(issues)

   print(f"Major issues: {metrics['major']}")
   print(f"Minor issues: {metrics['minor']}")

   if metrics['major'] == 0:
       print("No major issues to revise")
       exit(0)
   ```

### Phase 2: Run Revision Loop

1. **Standard revision (2 iterations):**
   ```bash
   python scripts/rrwrite-revise-manuscript.py \
       --manuscript-dir {manuscript_dir} \
       --max-iterations {max_iterations}
   ```

2. **Custom improvement threshold:**
   ```bash
   python scripts/rrwrite-revise-manuscript.py \
       --manuscript-dir {manuscript_dir} \
       --max-iterations {max_iterations} \
       --min-improvement {min_improvement}
   ```

3. **Dry run (preview changes):**
   ```bash
   python scripts/rrwrite-revise-manuscript.py \
       --manuscript-dir {manuscript_dir} \
       --dry-run
   ```

### Phase 3: Review Results

1. **Check revision summary:**

   The script outputs:
   ```
   REVISION SUMMARY
   ----------------
   Total iterations: 2
   Issues resolved: 21 → 8 → 0 (major)
   Convergence: major_issues_resolved

   ✓ All major issues resolved!
   ```

2. **Review state tracking:**
   ```python
   from rrwrite_state_manager import StateManager

   manager = StateManager(output_dir="{manuscript_dir}")
   summary = manager.get_revision_summary()

   print(f"Status: {summary['status']}")
   print(f"Iterations: {summary['iterations']}")
   print(f"Major resolved: {summary['total_major_resolved']}")
   print(f"Convergence: {summary['convergence_reason']}")
   ```

3. **Review critique reports:**

   Each iteration generates new critique files:
   - `critique_content_v2.md`
   - `critique_format_v2.md`
   - `critique_content_v3.md` (if 3+ iterations)

   Compare versions to track progress.

### Phase 4: Manual Review (If Needed)

If revision stalled or issues remain:

1. **Review remaining issues:**
   ```bash
   cat {manuscript_dir}/critique_content_v*.md | grep "## Major Issues"
   ```

2. **Identify problematic sections:**
   ```python
   from rrwrite_revision_parser import CritiqueParser

   parser = CritiqueParser("{manuscript_dir}")

   # Get latest version
   import re
   files = list(Path("{manuscript_dir}").glob("critique_content_v*.md"))
   latest_version = max([int(re.search(r'v(\d+)', f.name).group(1)) for f in files])

   issues = parser.parse_critique_reports(version=latest_version)
   issues = parser.infer_all_sections(issues)

   grouped = parser.group_by_section(issues)
   for section, section_issues in grouped.items():
       major = sum(1 for i in section_issues if i.severity == "major")
       if major > 0:
           print(f"{section}: {major} major issues")
   ```

3. **Manually revise problematic sections:**
   - Edit section files directly
   - Re-run assembly and critique
   - Run another revision iteration if needed

## Section-Specific Revision Logic

### Abstract
- **Focus**: Word count reduction
- **Preserve**: Key results, conclusions, citations
- **Strategy**: LLM condensation with strict word target

### Introduction
- **Focus**: Adding citations for claims
- **Preserve**: Narrative flow, background context
- **Strategy**: Citation search + LLM insertion

### Methods
- **Focus**: Reproducibility elements
- **Add**: Software versions, parameters, data sources, code availability
- **Strategy**: Extract from repository_analysis.md

### Results
- **Focus**: Move interpretation to Discussion
- **Add**: Figure/table references if missing
- **Strategy**: Flag interpretation keywords for manual review

### Discussion
- **Focus**: Strengthen arguments with citations
- **Add**: Citations for claims, comparisons to prior work
- **Strategy**: Citation search + LLM insertion

## Validation After Revision

Each revised section is validated:

1. **Citation existence**: All [author2024] keys exist in literature_evidence.csv
2. **Citation format**: No numeric citations ([1], [2])
3. **Word count**: Within journal limits (if specified)

**If validation fails:**
- Section is not saved
- Error is logged
- Revision continues with other sections

## State Tracking

Revision state is tracked in `.rrwrite/state.json`:

```json
{
  "workflow_status": {
    "revision": {
      "status": "completed",
      "max_revisions": 2,
      "current_iteration": 2,
      "iterations": [
        {
          "iteration": 1,
          "sections_revised": ["introduction", "methods"],
          "issues_before": {"major": 21, "minor": 4},
          "issues_after": {"major": 8, "minor": 2},
          "convergence_metrics": {
            "major_resolved": 13,
            "minor_resolved": 2,
            "improvement_rate": 0.62
          },
          "git_commit": "abc123d"
        }
      ],
      "convergence_status": "converged",
      "convergence_reason": "major_issues_resolved"
    }
  }
}
```

## Git Integration

Each iteration is committed automatically:

```
Commit message: "Revision iteration 1: Resolved 13 major, 2 minor issues"
Files: *.md, .rrwrite/state.json
```

View revision history:
```bash
cd {manuscript_dir}
git log --oneline --grep="Revision iteration"
```

## Troubleshooting

### No issues found
**Symptom**: "No critique reports found"
**Solution**: Run critique first: `/rrwrite-critique-manuscript`

### Revision stalled
**Symptom**: "Convergence: stalled_no_improvement"
**Causes**:
- Issues are cross-cutting (affect multiple sections)
- Issues require manual judgment
- LLM unable to find appropriate citations

**Solutions**:
1. Review remaining issues manually
2. Edit sections directly
3. Lower `--min-improvement` threshold
4. Increase `--max-iterations`

### Validation failures
**Symptom**: "Validation failed: Citation not found"
**Causes**:
- LLM hallucinated citation key
- Citation missing from literature_evidence.csv

**Solutions**:
1. Check literature_evidence.csv completeness
2. Re-run literature research to add missing papers
3. Manually correct citation keys in section files

### Max iterations reached
**Symptom**: "Convergence: max_iterations_reached" with issues remaining
**Solutions**:
1. Increase `--max-iterations`
2. Review remaining issues for manual fixes
3. Check if issues are actionable by automated revisers

## Performance

**Typical performance:**
- Parsing: < 1 second
- Section revision: 10-30 seconds per section (LLM calls)
- Re-assembly: < 5 seconds
- Re-critique: 20-40 seconds (LLM calls)
- **Total per iteration**: 1-3 minutes

**For {max_iterations} iterations:**
- Expected time: {max_iterations} × 2 minutes = ~{max_iterations * 2} minutes

## Example Output

```
==============================================================
REVISION ITERATION 1/2
==============================================================

Parsing critique reports (version 1)...
Found 21 major issues, 4 minor issues

Mapping issues to sections...
  - introduction: 5 major, 1 minor
  - methods: 10 major, 0 minor
  - results: 6 major, 3 minor

Revising sections...
  Revising introduction... ✓ (3 changes)
    - Added evidence: Strong claim without evidence: "Validation through..."
    - Added evidence: Strong claim without evidence: "The system's validation..."
    - Added evidence: Strong claim without evidence: "MicroGrowAgents demonstrates..."
  Revising methods... ✓ (2 changes)
    - Added reproducibility: Methods missing reproducibility elements
    - Added reproducibility: Code availability statement
  Revising results... ✓ (1 changes)
    - Added evidence: Strong claim without evidence: "Histogram analysis confirms..."

Re-assembling manuscript...
  ✓ Manuscript assembled

Re-running critique (version 2)...
  ✓ Critique complete

After revision:
  Major issues: 21 → 8 (13 resolved)
  Minor issues: 4 → 2
  Improvement rate: 61.9%

==============================================================
REVISION ITERATION 2/2
==============================================================
...

==============================================================
Revision converged: major_issues_resolved
==============================================================

REVISION SUMMARY
----------------
Total iterations: 2
Issues resolved: 21 → 8 → 0 (major)
Convergence: major_issues_resolved

✓ All major issues resolved!
==============================================================
```

## Next Steps After Revision

1. **Review final manuscript:**
   ```bash
   cat {manuscript_dir}/manuscript_full.md
   ```

2. **Check final critique:**
   ```bash
   cat {manuscript_dir}/critique_content_v*.md
   ```

3. **Validate final output:**
   ```bash
   python scripts/rrwrite-validate-manuscript.py \
       --file {manuscript_dir}/manuscript_full.md \
       --type manuscript
   ```

4. **Check workflow status:**
   ```bash
   python scripts/rrwrite-status.py --output-dir {manuscript_dir}
   ```

5. **Export for submission:**
   ```bash
   # Convert to .docx
   pandoc {manuscript_dir}/manuscript_full.md \
       -o {manuscript_dir}/manuscript_full.docx \
       -f markdown -t docx --standalone

   # Or use existing conversion script
   python scripts/rrwrite-convert-to-docx.py \
       --input {manuscript_dir}/manuscript_full.md
   ```

## Integration with Full Workflow

The revision step is now integrated into the assembly workflow:

```bash
# Assemble with automatic critique and 2 revision iterations
python scripts/rrwrite-assemble-manuscript.py \
    --output-dir {manuscript_dir} \
    --max-revisions 2

# Or use the skill directly
/rrwrite-assemble --target_dir {manuscript_dir} --max_revisions 2
```

## Limitations

**Current limitations:**
1. **Citation format fixes**: Can only fix obvious patterns, not all malformed citations
2. **Interpretation detection**: Flags keywords, doesn't move content automatically
3. **Cross-cutting issues**: Issues affecting entire manuscript may not be addressable
4. **LLM limitations**: May occasionally hallucinate citations or miss context
5. **Manual judgment required**: Some issues need human decision-making

**Future improvements:**
- Interactive mode for user confirmation
- More sophisticated citation extraction/mapping
- Automated content movement (Results → Discussion)
- Section-specific word count targets
- Better handling of cross-cutting issues
