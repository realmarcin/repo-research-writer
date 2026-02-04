# Usage Guide: Integrating with Existing Research Projects

## Scenario 1: You Have an Existing Local Git Repo

Let's say you have a research project at `/Users/yourname/research/my-awesome-project/`

### Step 1: Install the Skills Globally (Do Once)

```bash
# Clone this repo to a permanent location
cd ~
git clone <this-repo-url> claude-scientific-writer

# Create global skills directory
mkdir -p ~/.claude/skills

# Create symlinks
ln -s ~/claude-scientific-writer/.claude/skills/plan-manuscript ~/.claude/skills/
ln -s ~/claude-scientific-writer/.claude/skills/draft-section ~/.claude/skills/
ln -s ~/claude-scientific-writer/.claude/skills/review-manuscript ~/.claude/skills/
```

**Benefits**: Skills are available to ALL your projects. Update once, use everywhere.

### Step 2: Prepare Your Research Project

```bash
# Navigate to your project
cd /Users/yourname/research/my-awesome-project

# Create required directories
mkdir -p drafts scripts

# Copy CLAUDE.md template
cp ~/claude-scientific-writer/CLAUDE.md.template ./CLAUDE.md

# Edit CLAUDE.md with your project details
nano CLAUDE.md  # or use your preferred editor
```

### Step 3: Add Supporting Scripts (Optional but Recommended)

```bash
# Copy verification scripts to your project
cp ~/claude-scientific-writer/scripts/verify_stats.py ./scripts/
cp ~/claude-scientific-writer/scripts/clean_ipynb.py ./scripts/

# Make them executable
chmod +x scripts/*.py
```

### Step 4: Start Using the Skills

```bash
# Start Claude Code in your project directory
cd /Users/yourname/research/my-awesome-project
claude
```

In Claude, invoke the skills:

```
"Use the plan-manuscript skill to create an outline targeting Nature Methods"

"Use the draft-section skill to write the Methods section"

"Use the review-manuscript skill to check the draft"
```

## Scenario 2: Installing Per-Project (No Global Installation)

If you prefer project-specific skills:

```bash
cd /Users/yourname/research/my-awesome-project

# Option A: Direct copy
git clone <this-repo-url> temp-skills
mkdir -p .claude/skills
cp -r temp-skills/.claude/skills/* .claude/skills/
rm -rf temp-skills

# Option B: Git submodule (easier to update)
git submodule add <this-repo-url> .claude/scientific-writer
mkdir -p .claude/skills
ln -s ../scientific-writer/.claude/skills/* .claude/skills/
```

## Scenario 3: Multiple Projects Workflow

When you have multiple research projects that all need these skills:

```bash
# Project structure
~/research/
├── project-a/
├── project-b/
└── project-c/

# ONE TIME: Install skills globally
cd ~
git clone <this-repo-url> claude-scientific-writer
mkdir -p ~/.claude/skills
ln -s ~/claude-scientific-writer/.claude/skills/* ~/.claude/skills/

# For each project, just add the necessary structure
for proj in project-a project-b project-c; do
  cd ~/research/$proj
  mkdir -p drafts scripts
  cp ~/claude-scientific-writer/CLAUDE.md.template ./CLAUDE.md
  cp ~/claude-scientific-writer/scripts/*.py ./scripts/
done
```

## Example: Complete Workflow

### Starting from a typical research repo:

```
my-project/
├── data/
│   ├── experiment1.csv
│   └── experiment2.csv
├── notebooks/
│   ├── exploration.ipynb
│   └── analysis.ipynb
├── src/
│   └── analysis.py
├── README.md
└── requirements.txt
```

### After setup:

```bash
cd my-project

# Create structure
mkdir -p drafts scripts figures

# Initialize CLAUDE.md
cat > CLAUDE.md << 'EOF'
# My Awesome Research Project

## Project Overview
Investigating the effect of X on Y using computational methods.

## Target Journal
PLOS Computational Biology

## Key Findings
1. Finding from experiment1.csv: X shows significant correlation
2. Finding from experiment2.csv: Y demonstrates novel behavior

## Repository Map
- data/experiment1.csv: Experimental data (n=1000 samples)
- notebooks/analysis.ipynb: Statistical analysis
- src/analysis.py: Core computational pipeline
EOF

# Copy verification script
cp ~/claude-scientific-writer/scripts/verify_stats.py ./scripts/

# Start Claude Code
claude
```

### In Claude session:

```
User: "Use plan-manuscript to outline a paper for PLOS Comp Bio"

Claude: [Analyzes repo, creates manuscript_plan.md]

User: "Use draft-section to write the Results section"

Claude: [Reads relevant data files, generates drafts/results.md]

User: "Use review-manuscript to check it"

Claude: [Reviews for PLOS compliance, generates review_round_1.md]
```

## Checking Skill Installation

To verify skills are properly installed:

```bash
# Check global skills
ls -la ~/.claude/skills/

# Check project skills
ls -la .claude/skills/

# In Claude Code session, list skills
claude  # start session
# Then: "What skills are available?"
```

## Updating Skills

### If using global symlinks:

```bash
cd ~/claude-scientific-writer
git pull origin main
# All projects automatically get updates
```

### If using git submodules per project:

```bash
cd /path/to/project
git submodule update --remote
```

### If using direct copies:

```bash
# Re-copy the updated skills
cd /path/to/project
rm -rf .claude/skills/plan-manuscript
rm -rf .claude/skills/draft-section
rm -rf .claude/skills/review-manuscript

git clone <this-repo-url> temp-skills
cp -r temp-skills/.claude/skills/* .claude/skills/
rm -rf temp-skills
```

## Troubleshooting

**Skills not found?**
- Check symlinks: `ls -la ~/.claude/skills/`
- Verify SKILL.md exists: `cat ~/.claude/skills/plan-manuscript/SKILL.md`

**Verification scripts failing?**
- Ensure scripts are executable: `chmod +x scripts/*.py`
- Check Python environment: `python3 --version`
- Install pandas: `pip install pandas openpyxl`

**Skills not activating?**
- Ensure YAML frontmatter is valid in SKILL.md files
- Check Claude Code can find the skills directory
- Try restarting Claude Code session
