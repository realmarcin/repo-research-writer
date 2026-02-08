# RRWrite Example Manuscripts

This directory contains reference example manuscripts demonstrating RRWrite's capabilities.

## Generating a Self-Referential Example

To create an example manuscript about the RRWrite tool itself:

```bash
# From the rrwrite directory
/rrwrite --repo /path/to/rrwrite --output-dir example/rrwrite_v1
```

This will generate a complete manuscript that:
- Documents the RRWrite tool's functionality
- Demonstrates all manuscript sections
- Shows evidence tracking in action
- Includes literature citations
- Provides a reference for users

## Purpose

Examples in this directory:
- **Are tracked in git** (part of the tool repository)
- Serve as reference implementations
- Demonstrate RRWrite's output format
- Help new users understand the workflow

## User Manuscripts

User-generated manuscripts should go in `manuscript/` directory (gitignored) where each will have its own separate git repository.

See [Git Architecture](../docs/GIT_ARCHITECTURE.md) for details on the separation between tool and manuscript repositories.
