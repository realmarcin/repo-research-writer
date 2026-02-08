---
name: rrwrite-plan-manuscript
description: Generates manuscript outline from repository analysis for target journal
arguments:
  - name: target_dir
    description: Directory containing repository analysis and output location
    default: manuscript
  - name: journal
    description: Target journal for manuscript
    default: bioinformatics
allowed-tools:
---

# Manuscript Planning Protocol

Generates a structured manuscript outline from repository analysis.
Tailors outline to target journal requirements and research domain.

## Overview

This skill bridges repository analysis (Step 1) and journal assessment (Step 4).
It creates a manuscript outline that:
- Reflects the repository's research contributions
- Follows academic manuscript structure
- Aligns with target journal expectations
- Provides foundation for literature research and section drafting

---

## Phase 1: Load Repository Analysis

### 1.1 Verify Analysis Exists

```bash
ANALYSIS_FILE="{target_dir}/repository_analysis.md"

if [ ! -f "$ANALYSIS_FILE" ]; then
  echo "❌ Error: Repository analysis not found at $ANALYSIS_FILE"
  echo "   Run: python scripts/rrwrite-analyze-repo.py --repo-path <path> --output-dir {target_dir}"
  exit 1
fi

echo "✓ Repository analysis found"
```

### 1.2 Load Analysis Data

```python
import json
from pathlib import Path

# Load JSON analysis data
analysis_json = Path("{target_dir}") / "repository_analysis.json"

if not analysis_json.exists():
    print("❌ Error: repository_analysis.json not found")
    exit(1)

with open(analysis_json) as f:
    analysis = json.load(f)

print("✓ Analysis data loaded")
print(f"  Repository: {analysis['repository_name']}")
print(f"  Primary domain: {analysis['research_domain']['primary_domain']}")
print(f"  Contribution type: {analysis['contributions']['type']}")
```

### 1.3 Extract Key Information

```python
# Extract key data for outline generation
repo_name = analysis['repository_name']
primary_domain = analysis['research_domain']['primary_domain']
contrib_type = analysis['contributions']['type']
description = analysis['documentation'].get('description', '')
artifacts = analysis['contributions'].get('artifacts', [])
primary_language = analysis['languages'].get('primary_language', 'Unknown')

print("\nKey Information:")
print(f"  Name: {repo_name}")
print(f"  Domain: {primary_domain}")
print(f"  Type: {contrib_type}")
print(f"  Language: {primary_language}")
print(f"  Artifacts: {len(artifacts)}")
```

---

## Phase 2: Determine Manuscript Structure

### 2.1 Select Outline Template

Different contribution types require different outline structures:

```python
# Determine outline template based on contribution type
outline_templates = {
    "tool": "software_tool",
    "database": "database_resource",
    "schema": "schema_ontology",
    "algorithm": "algorithm_method",
    "framework": "software_framework",
    "analysis": "data_analysis"
}

template_type = outline_templates.get(contrib_type.lower(), "software_tool")

print(f"\nSelected outline template: {template_type}")
```

**Template Types**:

1. **software_tool**: General computational tool/application
   - Sections: Abstract, Introduction, Implementation, Results (benchmarks), Discussion, Availability

2. **database_resource**: Database or data repository
   - Sections: Abstract, Introduction, Database Content, Utility & Applications, Discussion, Data Availability

3. **schema_ontology**: Schema, ontology, or data model
   - Sections: Abstract, Introduction, Schema Design, Implementation, Use Cases, Discussion, Availability

4. **algorithm_method**: Novel algorithm or computational method
   - Sections: Abstract, Introduction, Methods (Algorithm), Results (Validation), Discussion, Availability

5. **software_framework**: Framework or library
   - Sections: Abstract, Introduction, Architecture, Features, Use Cases, Discussion, Availability

6. **data_analysis**: Analysis study or investigation
   - Sections: Abstract, Introduction, Methods, Results, Discussion, Conclusions, Data Availability

### 2.2 Determine Section Titles

Map template sections to journal-appropriate titles:

```python
# Journal-specific section naming
journal_section_mapping = {
    "bioinformatics": {
        "implementation": "Implementation",
        "results": "Results",
        "availability": "Data and Code Availability"
    },
    "nature_methods": {
        "implementation": "Implementation",
        "results": "Results",
        "availability": "Data Availability"
    },
    "plos_computational_biology": {
        "implementation": "Methods",
        "results": "Results",
        "availability": "Data Availability"
    }
}

# Get journal-specific titles (default to generic)
journal_key = "{journal}".lower().replace(' ', '_')
section_titles = journal_section_mapping.get(journal_key, {})

print(f"\nJournal: {journal}")
print(f"Section customization: {len(section_titles)} titles")
```

---

## Phase 3: Generate Outline

### 3.1 Create Abstract Section

```markdown
## Abstract

**Purpose**: Concise summary of the work (150-250 words for most journals)

**Content to include**:
- Background (1-2 sentences): Context and motivation
- Objective (1 sentence): What problem does this address?
- Methods (2-3 sentences): What was created/developed?
- Results (2-3 sentences): Key features and capabilities
- Availability (1 sentence): Where to access the tool/resource

**Outline**:
1. State the problem or need in [primary_domain]
2. Introduce [repo_name] as the solution
3. Describe key features: [list main artifacts]
4. Highlight main technical approach: [mention primary_language, frameworks]
5. State availability and license
```

### 3.2 Create Introduction Section

```markdown
## Introduction

**Purpose**: Establish context, motivation, and contributions (600-1200 words)

**Content structure**:

### Background (2-3 paragraphs)
- Current state of [primary_domain]
- Existing tools/resources and their limitations
- Specific need that motivated this work

### Motivation (1-2 paragraphs)
- Why existing solutions are insufficient
- What gap this work fills
- Who will benefit from this contribution

### Contributions (1 paragraph)
This work presents [repo_name], which provides:
1. [Artifact 1 from analysis]
2. [Artifact 2 from analysis]
3. [Artifact 3 from analysis]
...

### Organization (1 paragraph)
The remainder of this paper is organized as follows: Section 2 describes...
```

### 3.3 Create Methods/Implementation Section

```markdown
## Implementation (or Methods/Algorithm)

**Purpose**: Describe technical approach and implementation details

**Content structure**:

### Design Principles
- Key design decisions
- Architecture overview
- Technology choices: [primary_language], [frameworks]

### Core Components
[For each major component identified in repository structure]
- Component purpose
- Implementation approach
- Key algorithms or data structures

### Data Model (if applicable)
- Schema structure
- Entity relationships
- Validation approach

### Software Engineering
- Development practices
- Testing strategy
- Documentation approach
- Continuous integration (if applicable)
```

### 3.4 Create Results Section

```markdown
## Results (or Use Cases/Utility)

**Purpose**: Demonstrate capabilities and validation

**Content structure**:

### Features and Capabilities
[Based on key_features from README analysis]
- Feature 1: Description and significance
- Feature 2: Description and significance
...

### Use Cases (if examples/ directory exists)
- Use case 1: [From examples directory]
- Use case 2: [From examples directory]
...

### Performance (if applicable)
- Runtime benchmarks
- Scalability tests
- Comparison with similar tools

### Validation
- Testing results
- Quality metrics
- User feedback (if applicable)
```

### 3.5 Create Discussion Section

```markdown
## Discussion

**Purpose**: Interpret results, compare with related work, discuss limitations

**Content structure**:

### Comparison with Related Work
- How does [repo_name] compare to existing solutions?
- What advantages does it provide?
- What trade-offs were made?

### Impact and Applications
- Who is using or will use this tool?
- What research questions does it enable?
- What domains can benefit?

### Limitations and Future Work
- Current limitations
- Planned enhancements
- Community contributions (if open source)

### Conclusions
- Recap main contributions
- Broader impact statement
```

### 3.6 Create Availability Section

```markdown
## Data and Code Availability

**Purpose**: Provide access information (mandatory for most journals)

**Content**:
- **Source code**: [GitHub URL from git analysis]
- **License**: [From LICENSE file if detected]
- **Documentation**: [Docs URL if available]
- **Installation**: [Link to installation instructions]
- **Version**: [Current commit hash from analysis]
- **Dependencies**: [Major dependencies from analysis]
- **Operating System**: [Inferred from README or code]
```

---

## Phase 4: Write Outline File

### 4.1 Generate Complete Outline

```python
from pathlib import Path
from datetime import datetime

# Generate outline markdown
outline_content = f"""# Manuscript Outline: {repo_name}

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Target Journal**: {journal}
**Repository**: {analysis['repository_path']}
**Primary Domain**: {primary_domain}
**Contribution Type**: {contrib_type}

---

## Abstract

**Target Length**: 150-250 words

**Key Points**:
- Background: {primary_domain} research requires [specific need]
- Objective: Present {repo_name}, a {contrib_type} for [purpose]
- Methods: Implemented using {primary_language}, providing {', '.join(artifacts[:3])}
- Results: Key features include [feature 1], [feature 2], [feature 3]
- Availability: Open source at [GitHub URL], license: [license]

---

## Introduction

**Target Length**: 600-1200 words

### Background
- Current landscape of {primary_domain}
- Existing tools and their limitations
- Need for improved solutions

### Motivation
- Specific problems addressed by {repo_name}
- Gap in current tools/resources
- Target users and use cases

### Contributions
This paper presents {repo_name}, contributing:
{chr(10).join(f'- {artifact}' for artifact in artifacts)}

### Organization
Brief roadmap of paper sections

---

## Implementation

**Target Length**: 1000-2000 words

### Design and Architecture
- Overall design philosophy
- Component architecture
- Technology stack: {primary_language}, [frameworks]

### Core Components
[List main components from repository structure analysis]

### Data Model / Schema (if applicable)
- Schema design
- Entities and relationships
- Validation approach

### Software Engineering Practices
- Development workflow
- Testing: {analysis['structure']['total_directories']} test files detected
- Documentation: README, docs/ directory
- Version control: Git with {analysis['git_info']['total_commits']} commits

---

## Results

**Target Length**: 1000-2000 words

### Features and Capabilities
[Extract from README key_features]

### Use Cases
[Reference examples/ directory if present]

### Performance and Validation
- Test coverage
- Performance benchmarks (if applicable)
- Real-world applications

---

## Discussion

**Target Length**: 600-1200 words

### Comparison with Related Work
- Existing tools in {primary_domain}
- Advantages of {repo_name}
- Trade-offs and design choices

### Impact and Applications
- Current adoption
- Potential research applications
- Future directions

### Limitations
- Current limitations
- Areas for improvement

### Conclusions
- Summary of contributions
- Broader impact

---

## Data and Code Availability

**Target Length**: 50-150 words

- **Repository**: {analysis['git_info'].get('remote_url', 'GitHub URL')}
- **Version**: {analysis['git_info'].get('commit_hash', 'current')}
- **License**: [Extract from LICENSE file]
- **Documentation**: [URL]
- **Installation**: [Instructions URL]
- **Requirements**: [Key dependencies]

---

*Outline generated by RRWrite Planning Skill*
*Ready for Step 4: Journal Assessment*
"""

# Write outline file
outline_file = Path("{target_dir}") / "outline.md"
outline_file.write_text(outline_content)

print(f"\n✓ Outline written to: {outline_file}")
```

---

## Phase 5: Initialize Workflow State

### 5.1 Create State Manager

```python
import sys
sys.path.insert(0, 'scripts')
from rrwrite_state_manager import StateManager

# Initialize state manager
manager = StateManager(output_dir="{target_dir}")

print("\n✓ Workflow state initialized")
print(f"  State file: {manager.state_file}")
```

### 5.2 Update Planning Stage

```python
# Update plan stage
manager.update_workflow_stage(
    "plan",
    status="completed",
    file=str(outline_file),
    target_journal="{journal}"
)

# Set repository path and target journal in main state
manager.state["repository_path"] = analysis["repository_path"]
manager.state["target_journal"] = "{journal}"
manager.state["manuscript_title"] = f"{repo_name}: A {contrib_type.title()} for {primary_domain.replace('_', ' ').title()}"

# Update files tracking
manager.state["files"]["outline"] = str(outline_file)
manager.state["files"]["repository_analysis"] = str(analysis_json.parent / "repository_analysis.md")

manager._save_state()

print("✓ Planning stage marked complete")
print(f"  Target journal: {journal}")
print(f"  Manuscript title: {manager.state['manuscript_title']}")
```

---

## Phase 6: Display Planning Summary

### 6.1 Generate Summary

```bash
echo "\n{'='*60}"
echo "Manuscript Planning Complete"
echo "{'='*60}\n"

echo "Repository: {repo_name}"
echo "Domain: {primary_domain}"
echo "Type: {contrib_type}"
echo "Target Journal: {journal}"
echo "\nOutline: {target_dir}/outline.md"
echo "State: {target_dir}/.rrwrite/state.json"

echo "\nNext Steps:"
echo "  1. Review outline: cat {target_dir}/outline.md"
echo "  2. Run journal assessment: /rrwrite-assess-journal --target-dir {target_dir} --initial-journal {journal}"
echo "  3. Check status: python scripts/rrwrite-status.py --output-dir {target_dir}"
```

---

## Output Files

### Generated Files

1. **`{target_dir}/outline.md`**
   - Complete manuscript outline
   - Section-by-section content guidelines
   - Target word counts
   - Key points to address

2. **`{target_dir}/.rrwrite/state.json`**
   - Workflow state initialized
   - Planning stage marked complete
   - Target journal set
   - Repository path recorded

---

## Validation

### Validate Outline Structure

```bash
# Check outline has required sections
grep -q "## Abstract" "{target_dir}/outline.md" && echo "✓ Has Abstract"
grep -q "## Introduction" "{target_dir}/outline.md" && echo "✓ Has Introduction"
grep -q "## Implementation" "{target_dir}/outline.md" && echo "✓ Has Implementation"
grep -q "## Results" "{target_dir}/outline.md" && echo "✓ Has Results"
grep -q "## Discussion" "{target_dir}/outline.md" && echo "✓ Has Discussion"
grep -q "## Availability" "{target_dir}/outline.md" && echo "✓ Has Availability"
```

### Validate State

```bash
# Check state file
test -f "{target_dir}/.rrwrite/state.json" && echo "✓ State file created"

# Check state content
python -c "
import json
with open('{target_dir}/.rrwrite/state.json') as f:
    state = json.load(f)
    assert state['workflow_status']['plan']['status'] == 'completed'
    assert state['target_journal'] == '{journal}'
    print('✓ State validation passed')
"
```

---

## Error Handling

### Common Errors

**Error: "Repository analysis not found"**
- **Cause**: Planning run before repository analysis
- **Solution**: Run `python scripts/rrwrite-analyze-repo.py --repo-path <path> --output-dir {target_dir}` first

**Error: "Cannot determine outline template"**
- **Cause**: Unrecognized contribution type in analysis
- **Solution**: Manually specify type or use default "tool" template

**Error: "State file already exists"**
- **Cause**: Planning run multiple times
- **Solution**: Either delete existing state or use a new version directory

---

## Customization

### Adjust Outline for Different Journals

Different journals have different preferences:

**Bioinformatics**:
- Emphasize algorithm/implementation details
- Include performance benchmarks
- Data and Code Availability is mandatory

**Nature Methods**:
- Focus on novelty and broad applicability
- Include comparison with state-of-the-art
- Methods section goes at END

**PLOS Computational Biology**:
- Add Author Summary (non-technical)
- Emphasize biological insight
- Comprehensive methods section

The outline template can be customized based on `{journal}` parameter.

---

## Success Criteria

Planning is successful when:

1. ✅ Repository analysis loaded successfully
2. ✅ Appropriate outline template selected
3. ✅ Complete outline.md generated with all sections
4. ✅ Workflow state initialized
5. ✅ Planning stage marked complete
6. ✅ Target journal set
7. ✅ Ready for journal assessment (Step 4)

---

## Notes

- **Automated**: Uses repository analysis to generate context-appropriate outline
- **Flexible**: Adapts outline structure to contribution type
- **Journal-aware**: Considers target journal expectations
- **Foundation**: Provides structure for all downstream steps
- **Iterative**: Outline can be manually refined before proceeding

---

## See Also

- `scripts/rrwrite-analyze-repo.py` - Repository analysis script
- `scripts/rrwrite_state_manager.py` - State management
- `.claude/skills/rrwrite-assess-journal/` - Next step: Journal assessment
- `.claude/commands/rrwrite.md` - Full pipeline documentation
