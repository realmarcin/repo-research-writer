# RRW File Naming Conventions

All RRW files use `rrw-` prefix or `CLUEWRITE` name to avoid conflicts.

## Core Files

- **`CLUEWRITE.md`** - Project context (replaces PROJECT.md)
- **`rrw-drafts/`** - Generated sections directory (deprecated, use `manuscript/` instead)
- **`manuscript/`** - All manuscript outputs (schema-validated)
- **`scripts/rrw-*.py`** - Verification tools

## Generated Files (Legacy - deprecated)

- `rrw-manuscript-plan.md`
- `rrw-literature-review.md`
- `rrw-literature-evidence.csv`
- `rrw-bib-additions.bib`
- `rrw-review-*.md`

## New Schema-Based Structure

All new manuscript outputs go in `manuscript/` directory:
- `manuscript/outline.md`
- `manuscript/literature.md`
- `manuscript/literature_citations.bib`
- `manuscript/literature_evidence.csv`
- `manuscript/abstract.md`, `manuscript/introduction.md`, etc.
- `manuscript/review_TYPE_vN.md`

## Why?

**Prevents conflicts** with existing project files like PROJECT.md, drafts/, README.md

**Clear ownership:** `ls rrw-*` shows all RRW files

**Safe removal:** `rm -rf rrw-*` won't touch your research files

**Schema validation:** `manuscript/` directory follows LinkML schema for consistency
