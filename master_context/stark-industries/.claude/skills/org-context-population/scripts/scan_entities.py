#!/usr/bin/env python3
"""
Scan entities/ directory and return structured index of existing files.

Returns file paths only (not content) for routing decisions:
- What files can be updated
- Where to route new entities (triage files)
- What list files exist for appending

Usage:
    python scan_entities.py                          # Scan ./entities
    python scan_entities.py /path/to/entities        # Scan specific path
    python scan_entities.py --pretty                 # Pretty-print output
"""

import argparse
import json
import sys
from pathlib import Path


# Common list file names (files that contain arrays of entities)
LIST_FILE_PATTERNS = {
    "vendors", "competitors", "systems", "tools", "products",
    "services", "partners", "clients", "projects", "teams"
}


def scan_entities(entities_path: str = "entities") -> dict:
    """
    Scan entities/ and return structured index of existing files.

    Returns:
        dict with:
        - entity_files: Individual entity files (overview.yaml, context.yaml, etc.)
        - list_files: Files containing arrays (vendors.yaml, competitors.yaml)
        - triage_files: _triage.yaml files for routing new entities
        - directories: Existing directories (for understanding structure)
    """
    path = Path(entities_path)

    if not path.exists():
        return {
            "success": False,
            "error": "PATH_NOT_FOUND",
            "error_message": f"Path '{entities_path}' does not exist",
            "entity_files": [],
            "list_files": [],
            "triage_files": [],
            "directories": []
        }

    result = {
        "success": True,
        "entities_root": str(path.resolve()),
        "entity_files": [],
        "list_files": [],
        "triage_files": [],
        "directories": []
    }

    # Scan all YAML files
    for yaml_file in sorted(path.rglob("*.yaml")):
        rel_path = str(yaml_file.relative_to(path))
        stem = yaml_file.stem.lower()

        if yaml_file.name == "_triage.yaml":
            result["triage_files"].append(rel_path)
        elif stem in LIST_FILE_PATTERNS:
            result["list_files"].append(rel_path)
        else:
            result["entity_files"].append(rel_path)

    # Also scan .yml files
    for yml_file in sorted(path.rglob("*.yml")):
        rel_path = str(yml_file.relative_to(path))
        stem = yml_file.stem.lower()

        if yml_file.name == "_triage.yml":
            result["triage_files"].append(rel_path)
        elif stem in LIST_FILE_PATTERNS:
            result["list_files"].append(rel_path)
        else:
            result["entity_files"].append(rel_path)

    # Scan directories
    for directory in sorted(path.rglob("*")):
        if directory.is_dir():
            result["directories"].append(str(directory.relative_to(path)))

    # Add counts
    result["counts"] = {
        "entity_files": len(result["entity_files"]),
        "list_files": len(result["list_files"]),
        "triage_files": len(result["triage_files"]),
        "directories": len(result["directories"])
    }

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Scan entities/ directory for existing files"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="entities",
        help="Path to entities/ directory (default: ./entities)"
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output"
    )
    args = parser.parse_args()

    result = scan_entities(args.path)
    print(json.dumps(result, indent=2 if args.pretty else None))

    # Exit with error code if scan failed
    if not result.get("success"):
        sys.exit(1)


if __name__ == "__main__":
    main()
