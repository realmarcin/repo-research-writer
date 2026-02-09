#!/bin/bash
# Installation script for Repo Research Writer (RRWrite)

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "========================================"
echo "RRWrite Installation"
echo "========================================"
echo ""

# Install globally (only option now - RRWrite stays in its own repo)
echo "Installing skills globally to ~/.claude/skills/"
echo ""

# Create global skills directory
mkdir -p ~/.claude/skills

# Create symlinks for skills
for skill in rrwrite-plan-manuscript rrwrite-draft-section \
             rrwrite-critique-manuscript rrwrite-research-literature; do
    target=~/.claude/skills/$skill
    if [ -L "$target" ] || [ -e "$target" ]; then
        echo "  ⚠️  Removing existing $skill"
        rm -rf "$target"
    fi
    echo "  ✓ Linking $skill"
    ln -s "$SCRIPT_DIR/.claude/skills/$skill" "$target"
done

echo ""
echo "✅ Installation complete!"
echo ""
echo "════════════════════════════════════════"
echo "Usage"
echo "════════════════════════════════════════"
echo ""
echo "RRWrite now works with external repositories. You provide a"
echo "GitHub URL or local path, and RRWrite generates manuscripts"
echo "in versioned output directories."
echo ""
echo "Examples:"
echo ""
echo "  # Analyze GitHub repository"
echo "  /rrwrite https://github.com/user/research-project"
echo ""
echo "  # Use local repository"
echo "  /rrwrite /path/to/local/repo --journal bioinformatics"
echo ""
echo "  # Analyze current directory"
echo "  /rrwrite . --journal nature"
echo ""
echo "  # Create new version (after addressing critique)"
echo "  /rrwrite . --version v2"
echo ""
echo "════════════════════════════════════════"
echo "Output Structure"
echo "════════════════════════════════════════"
echo ""
echo "All manuscripts are generated in versioned directories:"
echo ""
echo "  manuscript/"
echo "  ├── repo-name_v1/     # First iteration"
echo "  │   ├── outline.md"
echo "  │   ├── abstract.md"
echo "  │   ├── introduction.md"
echo "  │   ├── methods.md"
echo "  │   ├── results.md"
echo "  │   ├── discussion.md"
echo "  │   ├── literature.md"
echo "  │   ├── literature_citations.bib"
echo "  │   └── .rrwrite/state.json"
echo "  └── repo-name_v2/     # After critique & revision"
echo ""
echo "Individual skills can also be used with --target-dir:"
echo "  /rrwrite-plan-manuscript --target-dir manuscript/repo_v1"
echo "  /rrwrite-draft-section abstract --target-dir manuscript/repo_v1"
echo ""
