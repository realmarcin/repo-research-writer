#!/usr/bin/env python3
"""
RRWrite Repository Name Normalizer

Converts GitHub URLs or local paths to normalized directory names
suitable for manuscript output directories.

Usage:
    python rrwrite-normalize-repo-name.py <github-url-or-local-path>

Examples:
    python rrwrite-normalize-repo-name.py https://github.com/user/my-repo
    # Output: my-repo

    python rrwrite-normalize-repo-name.py /path/to/my research/project
    # Output: project

    python rrwrite-normalize-repo-name.py https://github.com/user/repo.git
    # Output: repo
"""

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


def normalize_repo_name(repo_input: str) -> str:
    """
    Normalize repository name from URL or path.

    Args:
        repo_input: GitHub URL or local path

    Returns:
        Normalized repository name suitable for directory naming
    """
    # Check if input is a URL
    if repo_input.startswith('http://') or repo_input.startswith('https://'):
        # Parse URL
        parsed = urlparse(repo_input)

        # Extract path component
        path = parsed.path.strip('/')

        # For GitHub URLs: github.com/user/repo or github.com/user/repo.git
        if 'github.com' in parsed.netloc:
            parts = path.split('/')
            if len(parts) >= 2:
                # Take the repo name (last part)
                repo_name = parts[-1]
            else:
                # Fallback to full path
                repo_name = path.replace('/', '-')
        else:
            # Other URLs: use last path component
            repo_name = Path(path).name

        # Remove .git suffix if present
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]

    else:
        # Local path: use directory name
        repo_name = Path(repo_input).resolve().name

    # Normalize the name:
    # 1. Convert to lowercase
    repo_name = repo_name.lower()

    # 2. Replace spaces and problematic characters with underscores
    repo_name = re.sub(r'[\s/\\:*?"<>|]+', '_', repo_name)

    # 3. Replace multiple underscores/hyphens with single ones
    repo_name = re.sub(r'[_-]+', '_', repo_name)

    # 4. Remove leading/trailing underscores or hyphens
    repo_name = repo_name.strip('_-')

    # 5. If empty after normalization, use default
    if not repo_name:
        repo_name = 'unknown_repo'

    return repo_name


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Normalize repository name for directory naming',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        'repo',
        help='GitHub URL or local repository path'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress error messages'
    )

    args = parser.parse_args()

    try:
        normalized = normalize_repo_name(args.repo)
        print(normalized)
        return 0
    except Exception as e:
        if not args.quiet:
            print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
