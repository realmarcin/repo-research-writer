# ClueWrite 📝

**Transform your research code into publication-ready manuscripts automatically.**

ClueWrite is an AI-powered system that reads your research repository—code, data, and notebooks—and generates scientifically accurate manuscripts with verified facts, proper citations, and journal-specific formatting.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 What ClueWrite Does

Instead of manually translating your computational research into text:

```
Your Research Repo          ClueWrite              Publication
├── data/results.csv    ──────────────────>    ┌─────────────────┐
├── scripts/analyze.py  ──────────────────>    │ Abstract        │
├── figures/fig1.png    ──────────────────>    │ Introduction    │
└── notebooks/          ──────────────────>    │ Methods         │
                                                │ Results         │
                                                │ Discussion      │
                                                └─────────────────┘
```

ClueWrite:
- ✅ **Extracts findings** from your data files
- ✅ **Verifies all numbers** against source CSVs
- ✅ **Describes methods** by reading your code
- ✅ **Formats for journals** (Nature, PLOS, Bioinformatics)
- ✅ **Maintains evidence chains** from data to claims

## 🚀 Quick Example

See a real example: [example/](example/) - A complete protein structure prediction project

```bash
# In your research project directory
cd my-research-project

# Step 1: Tell ClueWrite about your project
# Edit PROJECT.md with your findings and data sources

# Step 2: Plan the manuscript
"Use plan-manuscript to create an outline for Bioinformatics journal"

# Step 3: Draft sections
"Use draft-section to write the Methods section"
"Use draft-section to write the Results section"

# Step 4: Review for compliance
"Use review-manuscript to check the draft"
```

**Result**: A complete manuscript draft where every claim is traced back to your source data.

## 📊 Real-World Example

The `example/` directory contains a complete demonstration:

**Input**: Protein prediction project with:
- CSV data: `benchmark_results.csv` (model accuracies)
- Python scripts: `train_model.py`, `evaluate.py`
- Figures: `accuracy_comparison.png`
- BibTeX: `references.bib`

**ClueWrite Output**:
- Detailed manuscript plan mapping data→sections
- Methods section describing the code implementation
- Results section with verified statistics
- Proper figure captions derived from plotting code
- Journal-compliant formatting for Bioinformatics

[→ View Full Example](example/)

## 🔧 Installation

### Global Installation (Use Across All Projects)

```bash
# 1. Clone ClueWrite
git clone https://github.com/realmarcin/cluewrite.git ~/cluewrite

# 2. Install globally
cd ~/cluewrite
./install.sh global

# 3. Setup any research project
cd /path/to/your/research/project
~/cluewrite/install.sh setup-project
```

### What This Does

- Creates `~/.claude/skills/` with symbolic links to ClueWrite skills
- Skills become available in all your AI agent sessions
- Each project gets:
  - `PROJECT.md` template for documenting your findings
  - `scripts/` with verification tools
  - `drafts/` for manuscript sections

## 📖 How It Works

### 1. Repository Ingestion

ClueWrite reads your project structure:
```
your-project/
├── data/processed/results.csv    → Numerical evidence
├── scripts/analyze.py             → Methodology
├── figures/fig1.png              → Visual results
└── PROJECT.md                    → Key findings summary
```

### 2. Planning

The `plan-manuscript` skill creates a detailed outline:
- Maps each section to specific files
- Links claims to data sources
- Applies journal-specific structure

### 3. Drafting with Verification

The `draft-section` skill:
- Reads relevant code/data files
- Generates academic prose
- **Verifies every number** using `verify_stats.py`
- Cites from your `references.bib`

Example fact-checking:
```bash
# Agent writes: "The model achieved 87% accuracy"
# Behind the scenes:
python scripts/verify_stats.py --file data/results.csv --col accuracy --op mean
# Returns: 0.87 ✓
```

### 4. Review

The `review-manuscript` skill acts as "Reviewer #2":
- Checks journal-specific requirements
- Verifies citation integrity
- Flags missing figures or data availability statements

## 🎓 Skills Included

### `plan-manuscript`
Maps your repository to a manuscript outline for your target journal.

**Supports**:
- Nature Methods
- PLOS Computational Biology
- Bioinformatics

### `draft-section`
Writes individual sections with fact-checking.

**Features**:
- Reads code to describe methods
- Verifies numbers against data files
- Generates LaTeX equations from code
- Maintains variable name consistency

### `review-manuscript`
Reviews drafts for compliance and accuracy.

**Checks**:
- Word counts
- Citation integrity
- Figure references
- Data availability statements

## 📁 Project Structure

Your research project should have:

```
your-research-project/
├── .claude/skills/        # ClueWrite skills (symlinked)
├── PROJECT.md            # Your project context
├── data/
│   └── processed/        # Data files with results
├── scripts/              # Analysis code
├── figures/              # Generated plots
├── references.bib        # Citations
└── drafts/              # Generated manuscript sections
```

## 🛠️ Verification Tools

ClueWrite includes Python tools to ensure accuracy:

### `verify_stats.py`
Verifies numerical claims against source data:
```bash
python scripts/verify_stats.py \
  --file data/results.csv \
  --col accuracy \
  --op mean
# Output: 0.8734
```

### `clean_ipynb.py`
Converts Jupyter notebooks to clean markdown:
```bash
python scripts/clean_ipynb.py notebook.ipynb -o clean.md
# Removes base64 images, keeps code and markdown
```

## 🔄 Workflow

```mermaid
graph LR
    A[Research Code] --> B[plan-manuscript]
    B --> C[manuscript_plan.md]
    C --> D[draft-section]
    D --> E[drafts/*.md]
    E --> F[review-manuscript]
    F --> G[review_report.md]
    G --> H[Revise & Compile]
    H --> I[Final Manuscript]
```

## 💡 Key Features

### ✅ Fact-Checking
Every numerical claim is verified against source data files.

### ✅ Code→Text Consistency
Variable names in the code match those in the manuscript.

### ✅ Evidence Chains
Each claim links to specific files/line numbers.

### ✅ Journal Compliance
Automatic formatting for target journals.

### ✅ Reproducibility
Complete provenance from data to publication.

## 📚 Example Outputs

### From PROJECT.md:
```markdown
## Key Finding
Our model achieves 87% accuracy on the benchmark.

Evidence: data/results.csv (line 45), figures/accuracy.png
```

### Generated Methods Section:
```markdown
## Methods

The model was trained using AdamW optimizer (learning rate 1e-4,
weight decay 0.01) for 100 epochs on 4× NVIDIA A100 GPUs. The loss
function combined RMSD and TM-score as implemented in
`scripts/train_model.py:87-89`.
```

### With Verification:
```python
# The agent reads train_model.py and finds:
optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=1e-4,          # ← Extracted
    weight_decay=0.01  # ← Extracted
)
```

## 🤝 Contributing

We welcome contributions! To add:
- **New journal templates**: Add to skills/plan-manuscript
- **New verification tools**: Add to scripts/
- **Documentation improvements**: Update README or USAGE_GUIDE

1. Fork this repository
2. Create your feature branch
3. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE)

## 🙏 Citation

If ClueWrite helps your research, please cite:

```bibtex
@software{cluewrite2026,
  title={ClueWrite: Repository-Driven Scientific Manuscript Generation},
  author={ClueWrite Contributors},
  year={2026},
  url={https://github.com/realmarcin/cluewrite}
}
```

## 🔗 Resources

- **[Full Example](example/)**: Complete protein prediction project
- **[Usage Guide](USAGE_GUIDE.md)**: Detailed integration instructions
- **[Technical Spec](data/deepresearch.md)**: Architecture details

## ❓ FAQ

**Q: Does this work with non-Python projects?**
A: Yes! The skills read any text files. Verification tools are Python, but you can write your own for other languages.

**Q: Can I customize for my specific journal?**
A: Yes! Edit the skill files to add new journal templates.

**Q: How does it handle figures?**
A: ClueWrite reads the scripts that generate figures to write accurate captions.

**Q: Does it hallucinate numbers?**
A: No! The verification loop ensures every number comes from your data files.

## 🎯 Next Steps

1. **Try the example**: `cd example/` and explore
2. **Install globally**: `./install.sh global`
3. **Setup your project**: Use `setup-project` in your research directory
4. **Start writing**: Use the skills with your AI agent

---

**Made with ❤️ for researchers who code**
