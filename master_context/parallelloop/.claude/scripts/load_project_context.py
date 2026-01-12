#!/usr/bin/env python3
"""
Project Context Loader for Image Generation.

Loads BOTH:
1. Organizational entities from entities/ directory
2. Project sources from project_workspaces/project_{id}/sources/*/structured.md

Usage:
    python load_project_context.py --project-id test123
    python load_project_context.py --project-id test123 --pretty
    python load_project_context.py --project-id test123 --base-dir /path/to/context
"""

import argparse
import json
import os
import re
import sys
import yaml
from pathlib import Path
from typing import Optional


# Directories to exclude when discovering entity types
EXCLUDED_DIRS = {"schemas", "organization"}


def discover_entity_types(entities_root: Path) -> list:
    """Dynamically discover entity types from the entities/ directory structure."""
    if not entities_root or not entities_root.exists():
        return []

    entity_types = []
    for item in entities_root.iterdir():
        if item.is_dir() and item.name not in EXCLUDED_DIRS:
            entity_types.append(item.name)

    return sorted(entity_types)


def load_yaml_file(filepath: str) -> dict:
    """Load a YAML file, handling encoding issues gracefully."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            clean_content = ''.join(char for char in content if char.isprintable() or char in '\n\r\t')
            return yaml.safe_load(clean_content) or {}
    except Exception as e:
        print(f"Warning: Could not load {filepath}: {e}", file=sys.stderr)
        return {}


def load_markdown_file(filepath: str) -> dict:
    """Load a structured.md file and extract metadata and content."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        result = {
            "file": str(filepath),
            "content": content,
            "metadata": {}
        }

        # Extract metadata from header (lines like **Key**: Value)
        metadata_pattern = r'\*\*([^*]+)\*\*:\s*(.+)'
        for match in re.finditer(metadata_pattern, content[:500]):
            key = match.group(1).strip().lower().replace(' ', '_')
            value = match.group(2).strip()
            result["metadata"][key] = value

        # Get title from first heading
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            result["title"] = title_match.group(1).strip()

        # Word count
        words = len(content.split())
        result["word_count"] = words

        return result
    except Exception as e:
        print(f"Warning: Could not load {filepath}: {e}", file=sys.stderr)
        return {}


def find_context_root(base_dir: Optional[str] = None) -> Optional[Path]:
    """Find the context repository root (containing entities/ and project_workspaces/)."""
    if base_dir:
        return Path(base_dir)

    current = Path.cwd()

    # Check current and parents for entities/ or project_workspaces/
    for path in [current] + list(current.parents):
        if (path / "entities").exists() or (path / "project_workspaces").exists():
            return path

    return current


def load_organization_context(context_root: Path) -> dict:
    """Load organization overview from entities/."""
    entities_root = context_root / "entities"
    org_dir = entities_root / "organization"

    context = {
        "name": None,
        "summary": None,
        "industry": None,
        "mission": None,
    }

    if not entities_root.exists():
        return {}

    # Try overview.yaml
    overview_file = org_dir / "overview.yaml"
    if overview_file.exists():
        overview = load_yaml_file(str(overview_file))
        context["name"] = overview.get("name")
        context["summary"] = overview.get("summary")
        profile = overview.get("profile", {})
        context["industry"] = profile.get("industry")
        context["mission"] = profile.get("mission")

    # Check for context.yaml in org subdirs
    if org_dir.exists():
        for item_dir in org_dir.iterdir():
            if item_dir.is_dir():
                context_file = item_dir / "context.yaml"
                if context_file.exists():
                    data = load_yaml_file(str(context_file))
                    if data.get("name") and not context["name"]:
                        context["name"] = data.get("name")

    return {k: v for k, v in context.items() if v is not None}


def load_entities_of_type(entities_root: Path, entity_type: str) -> list:
    """Load all entities of a given type."""
    entities = []
    entity_dir = entities_root / entity_type

    if not entity_dir.exists():
        return entities

    for item_dir in entity_dir.iterdir():
        if item_dir.is_dir():
            context_file = item_dir / "context.yaml"
            if context_file.exists():
                data = load_yaml_file(str(context_file))
                if data:
                    if "id" not in data:
                        data["id"] = item_dir.name
                    data["_source"] = f"entities/{entity_type}/{item_dir.name}"
                    entities.append(data)

    return entities


def load_all_entities(context_root: Path) -> dict:
    """Load all org entities."""
    entities_root = context_root / "entities"

    if not entities_root.exists():
        return {"entities": {}, "counts": {}, "total": 0}

    entities = {}
    counts = {}

    # Dynamically discover entity types from directory structure
    entity_types = discover_entity_types(entities_root)

    for entity_type in entity_types:
        loaded = load_entities_of_type(entities_root, entity_type)
        entities[entity_type] = loaded
        counts[entity_type] = len(loaded)

    return {
        "entities": entities,
        "counts": counts,
        "total": sum(counts.values())
    }


def load_project_sources(context_root: Path, project_id: str) -> list:
    """Load all structured.md files from project sources."""
    sources = []
    project_dir = context_root / "project_workspaces" / f"project_{project_id}" / "sources"

    if not project_dir.exists():
        return sources

    for source_dir in project_dir.iterdir():
        if source_dir.is_dir():
            structured_file = source_dir / "structured.md"
            if structured_file.exists():
                source_data = load_markdown_file(str(structured_file))
                if source_data:
                    source_data["source_id"] = source_dir.name
                    source_data["_source"] = f"project_workspaces/project_{project_id}/sources/{source_dir.name}"
                    sources.append(source_data)

    return sources


def main():
    parser = argparse.ArgumentParser(description="Load project context for image generation")
    parser.add_argument("--project-id", required=True, help="Project ID (e.g., test123)")
    parser.add_argument("--base-dir", help="Base directory containing entities/ and project_workspaces/")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    parser.add_argument("--sources-only", action="store_true", help="Only load project sources, skip org entities")
    parser.add_argument("--entities-only", action="store_true", help="Only load org entities, skip project sources")
    args = parser.parse_args()

    context_root = find_context_root(args.base_dir)

    if not context_root:
        result = {
            "success": False,
            "error": "NO_CONTEXT_ROOT",
            "error_message": "Could not find context repository root",
            "searched_from": str(Path.cwd())
        }
        print(json.dumps(result, indent=2 if args.pretty else None))
        sys.exit(1)

    result = {
        "success": True,
        "project_id": args.project_id,
        "context_root": str(context_root),
    }

    # Load org context
    if not args.sources_only:
        result["organization"] = load_organization_context(context_root)
        entity_data = load_all_entities(context_root)
        result["entities"] = entity_data["entities"]
        result["entity_counts"] = entity_data["counts"]
        result["total_entities"] = entity_data["total"]

    # Load project sources
    if not args.entities_only:
        sources = load_project_sources(context_root, args.project_id)
        result["project_sources"] = sources
        result["source_count"] = len(sources)

    print(json.dumps(result, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
