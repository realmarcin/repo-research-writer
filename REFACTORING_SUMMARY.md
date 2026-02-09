# Refactoring Summary

This document summarizes all the major refactorings applied to this repository.

## Repository Rename

**Old name:** `research-writer`  
**New name:** `repo-research-writer`

All repository references, clone URLs, and file paths have been updated to reflect the new name.

**Note:** The schema namespace URL `https://w3id.org/research-writer/` was intentionally preserved for backward compatibility.

---

## Refactoring 1: cluewrite- → rrw- → rrwrite-

### Phase 1: cluewrite- → rrw-
- **Commit:** `45eaba6` - Refactor: cluewrite- → rrw-, research-writer → repo-research-writer
- All skill names changed from `cluewrite-*` to `rrw-*`
- All Python scripts renamed from `cluewrite-*.py` to `rrw-*.py`
- Fixed 5 critical double-prefix bugs (`cluewrite-cluewrite-` → `rrw-`)
- Updated 200+ content references

### Phase 2: rrw- → rrwrite-
- **Commit:** `34890ac` - Refactor: rrw- → rrwrite- for improved clarity
- All skill names changed from `rrw-*` to `rrwrite-*`
- All Python scripts renamed from `rrw-*.py` to `rrwrite-*.py`
- Branding updated: `RRW` → `RRWrite`

**Breaking Changes:**
- `/cluewrite-plan-manuscript` → `/rrwrite-plan-manuscript`
- `/cluewrite-draft-section` → `/rrwrite-draft-section`
- `/cluewrite-research-literature` → `/rrwrite-research-literature`
- `/cluewrite-review-manuscript` → `/rrwrite-review-manuscript` (later changed to critique)

---

## Refactoring 2: review → critique

**Commit:** `c24cbbe` - Refactor: review → critique for manuscript analysis skill

Changed the manuscript analysis skill from "review" to "critique" terminology.

### Changes:
- Skill name: `rrwrite-review-manuscript` → `rrwrite-critique-manuscript`
- File outputs: `review_*.md` → `critique_*.md`
- Process terminology: "review" → "critique" (for the skill process)
- Schema classes: `Review*` → `Critique*`

### Preserved:
- "literature review" (standard academic term)
- "peer review" (standard academic term)
- Academic context uses of "review"

**Breaking Changes:**
- `/rrwrite-review-manuscript` → `/rrwrite-critique-manuscript`
- `review_manuscript_v1.md` → `critique_manuscript_v1.md`
- `review_outline_v1.md` → `critique_outline_v1.md`
- `review_literature_v1.md` → `critique_literature_v1.md`
- `review_section_v1.md` → `critique_section_v1.md`
- Validation type: `--type review` → `--type critique`

---

## Current State

### Repository Name
`repo-research-writer`

### Skills (all with `rrwrite-` prefix)
1. `/rrwrite-plan-manuscript` - Creates manuscript outline
2. `/rrwrite-draft-section` - Drafts manuscript sections
3. `/rrwrite-research-literature` - Performs literature research
4. `/rrwrite-critique-manuscript` - Critiques manuscripts/outlines/sections

### Python Scripts (all with `rrwrite-` prefix)
1. `rrwrite-verify-stats.py` - Verifies numerical claims
2. `rrwrite-clean-ipynb.py` - Cleans Jupyter notebooks
3. `rrwrite-validate-manuscript.py` - Validates manuscript outputs
4. `rrwrite-assemble-manuscript.py` - Assembles full manuscript

### Output Files
- Manuscript sections: `manuscript/*.md`
- Outlines: `manuscript_plan.md`
- Literature research: `manuscript/literature.md`
- Critiques: `critique_*.md` (e.g., `critique_manuscript_v1.md`)

### Branding
**Full name:** Repo Research Writer (RRWrite)  
**Short name:** RRWrite

---

## Migration Guide

If you have existing projects using the old naming:

### Update Skill Invocations
```bash
# Old → New
/cluewrite-plan-manuscript → /rrwrite-plan-manuscript
/cluewrite-draft-section → /rrwrite-draft-section
/cluewrite-research-literature → /rrwrite-research-literature
/cluewrite-review-manuscript → /rrwrite-critique-manuscript
```

### Update File References
```bash
# Old → New
cluewrite-drafts/ → rrwrite-drafts/ or manuscript/
review_*.md → critique_*.md
cluewrite-verify-stats.py → rrwrite-verify-stats.py
```

### Update Repository References
```bash
# Old → New
git clone https://github.com/user/research-writer.git
git clone https://github.com/user/repo-research-writer.git
```

### Re-install Skills
```bash
cd ~/repo-research-writer
git pull origin main
./install.sh global  # Updates global symlinks
```

---

## Verification

All refactorings have been verified:
- ✅ 0 old prefix references remaining
- ✅ All Python scripts pass syntax validation
- ✅ All shell scripts pass syntax validation
- ✅ All symlinks working correctly
- ✅ Schema URL preserved for backward compatibility
- ✅ Standard academic terms preserved

Last updated: 2026-02-05
