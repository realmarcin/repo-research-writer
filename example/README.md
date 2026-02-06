# Example: Protein Structure Prediction Project

This example demonstrates how to use RRW skills to generate a manuscript from a computational biology research project.

## Project Overview

This fictional project analyzes protein structure prediction accuracy using a novel deep learning approach.

## Directory Structure

```
example/
├── data/
│   ├── predictions.csv          # Model predictions
│   └── benchmark_results.csv    # Comparison with existing methods
├── scripts/
│   ├── train_model.py          # Training pipeline
│   └── evaluate.py             # Evaluation metrics
├── figures/
│   ├── accuracy_comparison.png # Figure 1
│   └── training_curve.png      # Figure 2
├── notebooks/
│   └── exploratory_analysis.ipynb
├── CLUEWRITE.md                   # Project context for ClueWrite
└── references.bib              # Citations

```

## Workflow Demonstration

### Step 1: Initialize Project Context

See `CLUEWRITE.md` for the project context that guides the AI agent.

### Step 2: Plan the Manuscript

```
User: "Use /rrw-plan-manuscript to create an outline for Bioinformatics journal"

Agent: [Reads CLUEWRITE.md, scans data/ and scripts/]
       [Creates manuscript_plan.md with sections mapped to files]
```

Output: `manuscript_plan.md`

### Step 3: Draft Individual Sections

```
User: "Use /rrw-draft-section to write the Methods section"

Agent: [Reads scripts/train_model.py and scripts/evaluate.py]
       [References data files to understand pipeline]
       [Generates rrw-drafts/methods.md]
```

Output: `rrw-drafts/methods.md`

```
User: "Use /rrw-draft-section to write the Results section"

Agent: [Reads data/benchmark_results.csv]
       [Verifies numbers using rrw-verify-stats.py]
       [References figures/accuracy_comparison.png]
       [Generates rrw-drafts/results.md]
```

Output: `rrw-drafts/results.md`

### Step 4: Review for Compliance

```
User: "Use /rrw-review-manuscript to check the draft"

Agent: [Reads all rrw-drafts/*]
       [Checks Bioinformatics journal requirements]
       [Verifies citation integrity]
       [Generates review_round_1.md]
```

Output: `review_round_1.md` with actionable feedback

## Expected Outputs

After running the full workflow:

```
example/
├── manuscript_plan.md          # Detailed outline
├── rrw-drafts/
│   ├── abstract.md
│   ├── introduction.md
│   ├── methods.md
│   ├── results.md
│   └── discussion.md
└── review_round_1.md          # Review feedback
```

## Key Features Demonstrated

1. **Repository Awareness**: Agent reads actual code and data files
2. **Fact Checking**: Numbers verified against source CSV files
3. **Journal Compliance**: Follows Bioinformatics formatting rules
4. **Citation Management**: Extracts from references.bib
5. **Figure Integration**: Describes figures based on generating scripts

## Try It Yourself

1. Copy this example directory
2. Install RRW skills globally
3. Navigate to the example directory
4. Start your AI agent
5. Follow the workflow above
