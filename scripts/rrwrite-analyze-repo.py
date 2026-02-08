#!/usr/bin/env python3
"""
RRWrite Repository Analyzer

Analyzes a research software repository to extract key information for manuscript generation.
Examines repository structure, documentation, code, and generates a comprehensive analysis.

Usage:
    rrwrite-analyze-repo.py --repo-path PATH --output-dir DIR [--branch BRANCH]

Output:
    {output_dir}/repository_analysis.md - Comprehensive repository analysis
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from collections import Counter


class RepositoryAnalyzer:
    """Analyzes research software repositories."""

    def __init__(self, repo_path: str, output_dir: str, branch: str = "main"):
        """Initialize analyzer.

        Args:
            repo_path: Path to repository
            output_dir: Directory for output files
            branch: Git branch to analyze (default: main)
        """
        self.repo_path = Path(repo_path).resolve()
        self.output_dir = Path(output_dir).resolve()
        self.branch = branch

        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")

        self.analysis = {
            "repository_path": str(self.repo_path),
            "repository_name": self.repo_path.name,
            "analyzed_at": datetime.now().isoformat(),
            "branch": branch
        }

    def run_git_command(self, *args) -> Optional[str]:
        """Run a git command and return output.

        Args:
            *args: Git command arguments

        Returns:
            Command output or None if failed
        """
        try:
            result = subprocess.run(
                ["git", "-C", str(self.repo_path)] + list(args),
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    def analyze_git_info(self):
        """Extract git repository information."""
        git_info = {}

        # Get remote URL
        remote_url = self.run_git_command("config", "--get", "remote.origin.url")
        if remote_url:
            git_info["remote_url"] = remote_url

        # Get current commit
        commit = self.run_git_command("rev-parse", "HEAD")
        if commit:
            git_info["commit_hash"] = commit[:8]

        # Get commit count
        commit_count = self.run_git_command("rev-list", "--count", "HEAD")
        if commit_count:
            git_info["total_commits"] = int(commit_count)

        # Get contributors
        contributors = self.run_git_command("shortlog", "-sn", "--all")
        if contributors:
            git_info["contributors_count"] = len(contributors.split('\n'))

        self.analysis["git_info"] = git_info

    def analyze_structure(self):
        """Analyze repository directory structure."""
        structure = {
            "total_files": 0,
            "total_directories": 0,
            "key_directories": [],
            "documentation_files": [],
            "configuration_files": []
        }

        # Common important directories
        important_dirs = {
            "src", "source", "lib", "tests", "test", "docs", "documentation",
            "examples", "scripts", "data", "notebooks", "schemas", "models",
            "project", "tools", "utils", "bin"
        }

        # Documentation files
        doc_patterns = ["README*", "CONTRIBUTING*", "LICENSE*", "CHANGELOG*", "*.md"]

        # Configuration files
        config_patterns = [
            "pyproject.toml", "setup.py", "setup.cfg", "requirements*.txt",
            "Makefile", "CMakeLists.txt", "package.json", "pom.xml",
            "Dockerfile", "docker-compose.yml", "*.yaml", "*.yml", "*.json"
        ]

        for item in self.repo_path.rglob("*"):
            # Skip hidden and common ignore patterns
            if any(part.startswith('.') for part in item.parts):
                if not any(part in ['.github', '.gitlab'] for part in item.parts):
                    continue

            relative_path = item.relative_to(self.repo_path)

            if item.is_dir():
                structure["total_directories"] += 1
                if item.name in important_dirs:
                    structure["key_directories"].append(str(relative_path))
            else:
                structure["total_files"] += 1

                # Check for documentation
                if any(item.match(pattern) for pattern in doc_patterns):
                    structure["documentation_files"].append(str(relative_path))

                # Check for configuration
                if any(item.match(pattern) for pattern in config_patterns):
                    if len(structure["configuration_files"]) < 20:  # Limit list
                        structure["configuration_files"].append(str(relative_path))

        self.analysis["structure"] = structure

    def analyze_programming_languages(self):
        """Detect programming languages used."""
        language_extensions = {
            '.py': 'Python',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.h': 'C/C++ Header',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.r': 'R',
            '.R': 'R',
            '.sh': 'Shell',
            '.bash': 'Bash',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.json': 'JSON',
            '.xml': 'XML',
            '.sql': 'SQL',
            '.go': 'Go',
            '.rs': 'Rust',
            '.jl': 'Julia',
            '.scala': 'Scala'
        }

        language_counts = Counter()
        total_lines = Counter()

        for item in self.repo_path.rglob("*"):
            if item.is_file() and item.suffix in language_extensions:
                # Skip hidden files and common ignore directories
                if any(part.startswith('.') for part in item.parts):
                    continue
                if any(part in ['venv', 'node_modules', '__pycache__', 'build', 'dist'] for part in item.parts):
                    continue

                lang = language_extensions[item.suffix]
                language_counts[lang] += 1

                # Count lines (for major languages)
                if lang in ['Python', 'Java', 'C++', 'C', 'JavaScript', 'R']:
                    try:
                        lines = len(item.read_text(errors='ignore').split('\n'))
                        total_lines[lang] += lines
                    except:
                        pass

        languages = {
            "file_counts": dict(language_counts.most_common()),
            "line_counts": dict(total_lines.most_common()),
            "primary_language": language_counts.most_common(1)[0][0] if language_counts else None
        }

        self.analysis["languages"] = languages

    def extract_readme_content(self) -> Optional[str]:
        """Extract and return README content."""
        readme_files = list(self.repo_path.glob("README*"))
        if readme_files:
            try:
                return readme_files[0].read_text(errors='ignore')
            except:
                pass
        return None

    def analyze_documentation(self):
        """Analyze repository documentation."""
        doc_info = {
            "has_readme": False,
            "readme_sections": [],
            "description": None,
            "key_features": [],
            "installation_instructions": False,
            "usage_examples": False,
            "has_docs_directory": False
        }

        # Check for README
        readme_content = self.extract_readme_content()
        if readme_content:
            doc_info["has_readme"] = True

            # Extract title/description (first paragraph)
            lines = readme_content.split('\n')
            for i, line in enumerate(lines[:20]):
                if line.strip() and not line.startswith('#'):
                    doc_info["description"] = line.strip()
                    break

            # Extract section headers
            sections = re.findall(r'^#+\s+(.+)$', readme_content, re.MULTILINE)
            doc_info["readme_sections"] = sections[:10]  # First 10 sections

            # Check for installation
            if re.search(r'(?i)(install|setup|getting started)', readme_content):
                doc_info["installation_instructions"] = True

            # Check for usage examples
            if re.search(r'(?i)(usage|example|tutorial|quick\s*start)', readme_content):
                doc_info["usage_examples"] = True

            # Extract bullet points that might be features
            features = re.findall(r'^\s*[\*\-]\s+(.+)$', readme_content, re.MULTILINE)
            doc_info["key_features"] = [f.strip() for f in features[:10]]  # First 10

        # Check for docs directory
        docs_dirs = ['docs', 'documentation', 'doc']
        for dirname in docs_dirs:
            if (self.repo_path / dirname).is_dir():
                doc_info["has_docs_directory"] = True
                break

        self.analysis["documentation"] = doc_info

    def detect_research_domain(self):
        """Detect research domain from repository content."""
        readme_content = self.extract_readme_content() or ""

        # Domain keywords
        domain_keywords = {
            "bioinformatics": [
                "genomics", "proteomics", "sequence", "genome", "gene",
                "protein", "biological", "bioinformatics", "computational biology"
            ],
            "machine_learning": [
                "machine learning", "deep learning", "neural network",
                "ai", "artificial intelligence", "model training", "classification"
            ],
            "data_science": [
                "data analysis", "data science", "statistics", "visualization",
                "pandas", "numpy", "data processing"
            ],
            "systems_biology": [
                "systems biology", "pathway", "network", "metabolic",
                "cellular", "signaling"
            ],
            "medical_informatics": [
                "medical", "clinical", "patient", "healthcare", "disease",
                "diagnosis", "treatment"
            ],
            "database_schema": [
                "schema", "database", "data model", "metadata",
                "ontology", "vocabulary", "linkml", "rdf"
            ]
        }

        domain_scores = {}
        content_lower = readme_content.lower()

        for domain, keywords in domain_keywords.items():
            score = sum(1 for kw in keywords if kw in content_lower)
            if score > 0:
                domain_scores[domain] = score

        # Sort by score
        sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)

        self.analysis["research_domain"] = {
            "detected_domains": [d[0] for d in sorted_domains[:3]],
            "primary_domain": sorted_domains[0][0] if sorted_domains else "unknown",
            "domain_scores": dict(sorted_domains)
        }

    def detect_tools_and_frameworks(self):
        """Detect tools, frameworks, and technologies used."""
        tools = {
            "python_packages": [],
            "r_packages": [],
            "frameworks": [],
            "databases": [],
            "schemas": []
        }

        # Check Python requirements/setup files
        requirements_files = [
            "requirements.txt", "requirements-dev.txt",
            "setup.py", "pyproject.toml", "poetry.lock"
        ]

        for req_file in requirements_files:
            req_path = self.repo_path / req_file
            if req_path.exists():
                try:
                    content = req_path.read_text(errors='ignore')

                    # Extract package names
                    if req_file.endswith('.txt'):
                        packages = re.findall(r'^([a-zA-Z0-9\-_]+)', content, re.MULTILINE)
                        tools["python_packages"].extend(packages[:20])
                    elif req_file == 'pyproject.toml':
                        packages = re.findall(r'"([a-zA-Z0-9\-_]+)[>=<]', content)
                        tools["python_packages"].extend(packages[:20])
                except:
                    pass

        # Look for schema files
        schema_patterns = ["*.yaml", "*.json", "*.linkml", "*.owl", "*.ttl"]
        for pattern in schema_patterns:
            schemas = list(self.repo_path.glob(f"**/{pattern}"))[:10]
            if schemas and pattern in ["*.linkml", "*.owl", "*.ttl"]:
                tools["schemas"].extend([s.name for s in schemas])

        # Detect frameworks from README
        readme_content = self.extract_readme_content() or ""
        framework_keywords = {
            "LinkML", "OWL", "RDF", "SPARQL", "SQLAlchemy", "FastAPI",
            "Flask", "Django", "React", "Vue", "Docker", "Kubernetes",
            "Apache Spark", "Airflow", "Snakemake"
        }

        for framework in framework_keywords:
            if framework in readme_content:
                tools["frameworks"].append(framework)

        self.analysis["tools"] = tools

    def identify_key_contributions(self):
        """Identify key research contributions."""
        contributions = {
            "type": None,
            "artifacts": [],
            "novelty_claims": [],
            "applications": []
        }

        readme_content = self.extract_readme_content() or ""

        # Determine contribution type
        type_indicators = {
            "database": ["database", "data repository", "data collection"],
            "schema": ["schema", "data model", "ontology", "vocabulary"],
            "tool": ["tool", "software", "application", "pipeline"],
            "algorithm": ["algorithm", "method", "approach"],
            "framework": ["framework", "library", "package"],
            "analysis": ["analysis", "study", "investigation"]
        }

        type_scores = {}
        content_lower = readme_content.lower()

        for contrib_type, indicators in type_indicators.items():
            score = sum(1 for ind in indicators if ind in content_lower)
            if score > 0:
                type_scores[contrib_type] = score

        if type_scores:
            contributions["type"] = max(type_scores, key=type_scores.get)

        # Identify artifacts (schemas, tools, datasets)
        structure = self.analysis.get("structure", {})
        key_dirs = structure.get("key_directories", [])

        if any("schema" in d for d in key_dirs):
            contributions["artifacts"].append("Schema definitions")
        if any("data" in d for d in key_dirs):
            contributions["artifacts"].append("Dataset or data collection")
        if any("src" in d or "source" in d for d in key_dirs):
            contributions["artifacts"].append("Source code implementation")
        if any("examples" in d for d in key_dirs):
            contributions["artifacts"].append("Usage examples")

        # Extract novelty claims (sentences with "first", "novel", "new")
        novelty_patterns = [
            r'(?i)(first|novel|new|innovative|unique).{0,100}',
            r'(?i)we (present|introduce|propose|develop).{0,100}'
        ]

        for pattern in novelty_patterns:
            matches = re.findall(pattern, readme_content)
            contributions["novelty_claims"].extend(matches[:3])

        self.analysis["contributions"] = contributions

    def generate_markdown_report(self) -> str:
        """Generate markdown analysis report.

        Returns:
            Markdown formatted analysis
        """
        md = []

        # Header
        md.append(f"# Repository Analysis: {self.analysis['repository_name']}")
        md.append(f"\n**Analyzed**: {self.analysis['analyzed_at']}")
        md.append(f"**Repository Path**: `{self.analysis['repository_path']}`\n")

        # Git Info
        if "git_info" in self.analysis:
            git = self.analysis["git_info"]
            md.append("## Git Repository Information\n")
            if "remote_url" in git:
                md.append(f"- **Remote URL**: {git['remote_url']}")
            if "commit_hash" in git:
                md.append(f"- **Current Commit**: `{git['commit_hash']}`")
            if "total_commits" in git:
                md.append(f"- **Total Commits**: {git['total_commits']}")
            if "contributors_count" in git:
                md.append(f"- **Contributors**: {git['contributors_count']}")
            md.append("")

        # Research Domain
        if "research_domain" in self.analysis:
            domain = self.analysis["research_domain"]
            md.append("## Research Domain\n")
            md.append(f"**Primary Domain**: {domain['primary_domain'].replace('_', ' ').title()}\n")
            if domain.get("detected_domains"):
                md.append("**Related Domains**:")
                for d in domain["detected_domains"]:
                    score = domain["domain_scores"].get(d, 0)
                    md.append(f"- {d.replace('_', ' ').title()} (confidence: {score})")
                md.append("")

        # Description
        if "documentation" in self.analysis:
            doc = self.analysis["documentation"]
            if doc.get("description"):
                md.append("## Project Description\n")
                md.append(doc["description"])
                md.append("")

        # Key Contributions
        if "contributions" in self.analysis:
            contrib = self.analysis["contributions"]
            md.append("## Key Contributions\n")
            if contrib.get("type"):
                md.append(f"**Contribution Type**: {contrib['type'].title()}\n")
            if contrib.get("artifacts"):
                md.append("**Artifacts**:")
                for artifact in contrib["artifacts"]:
                    md.append(f"- {artifact}")
                md.append("")

        # Repository Structure
        if "structure" in self.analysis:
            struct = self.analysis["structure"]
            md.append("## Repository Structure\n")
            md.append(f"- **Total Files**: {struct['total_files']}")
            md.append(f"- **Total Directories**: {struct['total_directories']}\n")

            if struct.get("key_directories"):
                md.append("**Key Directories**:")
                for directory in struct["key_directories"][:15]:
                    md.append(f"- `{directory}/`")
                md.append("")

        # Programming Languages
        if "languages" in self.analysis:
            langs = self.analysis["languages"]
            md.append("## Programming Languages\n")
            if langs.get("primary_language"):
                md.append(f"**Primary Language**: {langs['primary_language']}\n")

            if langs.get("file_counts"):
                md.append("**Language Distribution**:")
                for lang, count in list(langs["file_counts"].items())[:10]:
                    md.append(f"- {lang}: {count} files")
                md.append("")

            if langs.get("line_counts"):
                md.append("**Lines of Code**:")
                for lang, lines in list(langs["line_counts"].items())[:5]:
                    md.append(f"- {lang}: {lines:,} lines")
                md.append("")

        # Tools and Technologies
        if "tools" in self.analysis:
            tools = self.analysis["tools"]
            md.append("## Tools and Technologies\n")

            if tools.get("frameworks"):
                md.append("**Frameworks/Technologies**:")
                for fw in tools["frameworks"][:10]:
                    md.append(f"- {fw}")
                md.append("")

            if tools.get("python_packages"):
                packages = list(set(tools["python_packages"]))  # Remove duplicates
                md.append(f"**Python Dependencies**: {len(packages)} packages")
                if packages:
                    md.append(f"- Key packages: {', '.join(packages[:10])}")
                md.append("")

            if tools.get("schemas"):
                md.append("**Schema Files**:")
                for schema in tools["schemas"][:10]:
                    md.append(f"- `{schema}`")
                md.append("")

        # Documentation
        if "documentation" in self.analysis:
            doc = self.analysis["documentation"]
            md.append("## Documentation\n")
            md.append(f"- **README Present**: {'✓ Yes' if doc['has_readme'] else '✗ No'}")
            md.append(f"- **Installation Instructions**: {'✓ Yes' if doc['installation_instructions'] else '✗ No'}")
            md.append(f"- **Usage Examples**: {'✓ Yes' if doc['usage_examples'] else '✗ No'}")
            md.append(f"- **Documentation Directory**: {'✓ Yes' if doc['has_docs_directory'] else '✗ No'}\n")

            if doc.get("readme_sections"):
                md.append("**README Sections**:")
                for section in doc["readme_sections"][:10]:
                    md.append(f"- {section}")
                md.append("")

            if doc.get("key_features"):
                md.append("**Key Features** (from README):")
                for feature in doc["key_features"][:10]:
                    if len(feature) > 100:
                        feature = feature[:97] + "..."
                    md.append(f"- {feature}")
                md.append("")

        # Analysis Summary
        md.append("## Analysis Summary\n")
        md.append("This repository analysis provides foundational information for manuscript generation.")
        md.append("The detected research domain, key contributions, and technical details will inform")
        md.append("the manuscript outline and content development.\n")

        md.append("---")
        md.append(f"\n*Analysis generated by RRWrite Repository Analyzer on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

        return "\n".join(md)

    def analyze(self) -> str:
        """Run complete repository analysis.

        Returns:
            Path to generated analysis file
        """
        print(f"Analyzing repository: {self.repo_path}")
        print(f"Output directory: {self.output_dir}")

        # Run all analysis steps
        print("\n1. Analyzing git information...")
        self.analyze_git_info()

        print("2. Analyzing repository structure...")
        self.analyze_structure()

        print("3. Detecting programming languages...")
        self.analyze_programming_languages()

        print("4. Analyzing documentation...")
        self.analyze_documentation()

        print("5. Detecting research domain...")
        self.detect_research_domain()

        print("6. Detecting tools and frameworks...")
        self.detect_tools_and_frameworks()

        print("7. Identifying key contributions...")
        self.identify_key_contributions()

        # Generate report
        print("\n8. Generating analysis report...")
        report = self.generate_markdown_report()

        # Save report
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_file = self.output_dir / "repository_analysis.md"
        output_file.write_text(report)

        # Save JSON data
        json_file = self.output_dir / "repository_analysis.json"
        with open(json_file, 'w') as f:
            json.dump(self.analysis, f, indent=2)

        print(f"\n✓ Analysis complete!")
        print(f"  Markdown report: {output_file}")
        print(f"  JSON data: {json_file}")

        return str(output_file)


def main():
    """CLI interface for repository analyzer."""
    parser = argparse.ArgumentParser(
        description="Analyze research software repository for manuscript generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --repo-path /path/to/repo --output-dir manuscript/repo_v1
  %(prog)s --repo-path ../my-tool --output-dir output --branch develop
        """
    )
    parser.add_argument(
        "--repo-path",
        required=True,
        help="Path to repository to analyze"
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Output directory for analysis files"
    )
    parser.add_argument(
        "--branch",
        default="main",
        help="Git branch to analyze (default: main)"
    )

    args = parser.parse_args()

    try:
        analyzer = RepositoryAnalyzer(
            repo_path=args.repo_path,
            output_dir=args.output_dir,
            branch=args.branch
        )

        analyzer.analyze()
        sys.exit(0)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
