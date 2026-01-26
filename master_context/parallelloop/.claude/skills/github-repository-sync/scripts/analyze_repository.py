#!/usr/bin/env python3
"""
Repository Analysis Script

Analyzes a synced repository to extract metrics, tech stack, and structure insights.
Simplified version: only file count and root-level tech stack detection.
"""
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Set


# Tech stack detection patterns (root-level files only)
TECH_STACK_PATTERNS = {
    "Python": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile", "conda.yml", "environment.yml"],
    "JavaScript": ["package.json", "package-lock.json"],
    "TypeScript": ["tsconfig.json"],
    "Java": ["pom.xml", "build.gradle", "build.gradle.kts"],
    "Go": ["go.mod", "go.sum"],
    "Ruby": ["Gemfile", "Gemfile.lock", ".ruby-version"],
    "Rust": ["Cargo.toml", "Cargo.lock"],
    "PHP": ["composer.json", "composer.lock"],
    ".NET": ["*.csproj", "*.sln"],
    "Dart": ["pubspec.yaml", "pubspec.lock"],
    "Docker": ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"],
    "Terraform": ["main.tf", "variables.tf"],
}

# Framework detection (requires examining package files)
FRAMEWORK_INDICATORS = {
    "Django": ["django", "Django"],
    "Flask": ["flask", "Flask"],
    "FastAPI": ["fastapi", "FastAPI"],
    "React": ["react", "React"],
    "Vue": ["vue", "Vue"],
    "Angular": ["@angular", "angular"],
    "Next.js": ["next", "Next"],
    "Express": ["express", "Express"],
    "Spring": ["spring-boot", "springframework"],
    "Laravel": ["laravel/framework"],
    "Rails": ["rails", "Rails"],
}


def count_files(repo_path: Path, exclude_patterns: Set[str] = None) -> int:
    """
    Count total number of files in repository, excluding .git and other patterns.

    Args:
        repo_path: Path to repository
        exclude_patterns: Set of directory names to exclude

    Returns:
        Total file count
    """
    if exclude_patterns is None:
        exclude_patterns = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'build', 'dist', 'target'}

    count = 0
    for root, dirs, files in os.walk(repo_path):
        # Remove excluded directories from traversal
        dirs[:] = [d for d in dirs if d not in exclude_patterns]
        count += len(files)

    return count


def detect_tech_stack(repo_path: Path) -> List[str]:
    """
    Detect technology stack based on root-level project files only.
    Simplified for performance - only checks repository root.

    Args:
        repo_path: Path to repository

    Returns:
        List of detected technologies
    """
    detected = set()

    # Check for tech stack indicator files at root level only
    for tech, patterns in TECH_STACK_PATTERNS.items():
        for pattern in patterns:
            if '*' in pattern:
                # Handle wildcards - check root level only
                ext = pattern.replace('*', '')
                for item in repo_path.iterdir():
                    if item.is_file() and item.name.endswith(ext):
                        detected.add(tech)
                        break
            else:
                # Check for exact file match at root
                if (repo_path / pattern).exists():
                    detected.add(tech)
                    break

    # Check for frameworks in package files
    detected_frameworks = detect_frameworks(repo_path)
    detected.update(detected_frameworks)

    return sorted(list(detected))


def detect_frameworks(repo_path: Path) -> List[str]:
    """
    Detect frameworks by examining dependency files at root level.

    Args:
        repo_path: Path to repository

    Returns:
        List of detected frameworks
    """
    detected = []

    # Check Python requirements
    requirements_files = ['requirements.txt', 'pyproject.toml', 'setup.py', 'Pipfile']
    for req_file in requirements_files:
        req_path = repo_path / req_file
        if req_path.exists():
            try:
                content = req_path.read_text().lower()
                for framework, indicators in FRAMEWORK_INDICATORS.items():
                    if any(indicator.lower() in content for indicator in indicators):
                        detected.append(framework)
            except Exception:
                pass

    # Check package.json for JavaScript frameworks
    package_json = repo_path / 'package.json'
    if package_json.exists():
        try:
            content = package_json.read_text().lower()
            for framework, indicators in FRAMEWORK_INDICATORS.items():
                if any(indicator.lower() in content for indicator in indicators):
                    detected.append(framework)
        except Exception:
            pass

    return detected


def analyze_structure(repo_path: Path) -> Dict:
    """
    Analyze repository structure (top-level directories).

    Args:
        repo_path: Path to repository

    Returns:
        Dictionary with structure information
    """
    structure = {
        "top_level_dirs": [],
        "has_tests": False,
        "has_docs": False,
        "has_ci": False
    }

    try:
        for item in repo_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                structure["top_level_dirs"].append(item.name)

                # Check for common directory patterns
                if item.name.lower() in ['test', 'tests', '__tests__', 'spec']:
                    structure["has_tests"] = True
                elif item.name.lower() in ['docs', 'doc', 'documentation']:
                    structure["has_docs"] = True

        # Check for CI/CD configuration
        ci_files = ['.github', '.gitlab-ci.yml', '.travis.yml', 'Jenkinsfile', '.circleci']
        for ci_file in ci_files:
            if (repo_path / ci_file).exists():
                structure["has_ci"] = True
                break

    except Exception as e:
        print(f"Warning: Could not fully analyze structure: {e}", file=sys.stderr)

    return structure


def analyze_repository(repo_path: str, user_instructions: str = None) -> Dict:
    """
    Perform repository analysis.

    Args:
        repo_path: Path to repository
        user_instructions: Optional custom analysis instructions

    Returns:
        Analysis results dictionary
    """
    repo_path_obj = Path(repo_path)

    if not repo_path_obj.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

    if not repo_path_obj.is_dir():
        raise NotADirectoryError(f"Repository path is not a directory: {repo_path}")

    print("Analyzing repository...", file=sys.stderr)

    # Perform analysis
    file_count = count_files(repo_path_obj)
    print(f"Counted {file_count} files", file=sys.stderr)

    tech_stack = detect_tech_stack(repo_path_obj)
    print(f"Detected tech stack: {', '.join(tech_stack) if tech_stack else 'None detected'}", file=sys.stderr)

    structure = analyze_structure(repo_path_obj)
    print(f"Analyzed structure", file=sys.stderr)

    return {
        "file_count": file_count,
        "tech_stack": tech_stack,
        "structure": structure,
        "user_instructions": user_instructions or "No custom instructions provided"
    }


def main():
    parser = argparse.ArgumentParser(
        description="Analyze GitHub repository structure and tech stack"
    )
    parser.add_argument(
        "--repo-path",
        required=True,
        help="Path to repository"
    )
    parser.add_argument(
        "--instructions",
        help="Optional custom analysis instructions from user"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output file path for analysis result JSON"
    )

    args = parser.parse_args()

    try:
        # Analyze repository
        analysis_result = analyze_repository(
            repo_path=args.repo_path,
            user_instructions=args.instructions
        )

        # Write to output file
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(analysis_result, f, indent=2)

        print(f"Analysis complete", file=sys.stderr)
        print(f"Results written to: {args.output}", file=sys.stderr)

        # Also output to stdout for piping
        print(json.dumps(analysis_result))

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
