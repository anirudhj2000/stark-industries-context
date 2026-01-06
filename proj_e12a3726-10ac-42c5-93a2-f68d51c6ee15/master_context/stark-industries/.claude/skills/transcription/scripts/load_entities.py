#!/usr/bin/env python3
"""
Entity Loader Script for Image Generation.

Loads all organizational entities from entities/ directory and outputs
structured JSON for Claude to analyze and craft image generation prompts.

Usage:
    python load_entities.py                    # JSON output to stdout
    python load_entities.py --pretty           # Pretty-printed JSON
    python load_entities.py --entities-root /path/to/entities
"""

import argparse
import json
import os
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


def find_entities_root() -> Optional[Path]:
    """Find the entities/ directory."""
    current = Path.cwd()

    # Check current and parent
    for pattern in [current / "entities", current.parent / "entities"]:
        if pattern.exists():
            return pattern

    # Walk up the tree
    for parent in current.parents:
        entities_path = parent / "entities"
        if entities_path.exists():
            return entities_path

    return None


def load_organization_context(entities_root: Path) -> dict:
    """Load organization overview."""
    org_dir = entities_root / "organization"
    context = {
        "name": None,
        "summary": None,
        "industry": None,
        "mission": None,
    }

    # Try overview.yaml
    overview_file = org_dir / "overview.yaml"
    if overview_file.exists():
        overview = load_yaml_file(str(overview_file))
        context["name"] = overview.get("name")
        context["summary"] = overview.get("summary")
        profile = overview.get("profile", {})
        context["industry"] = profile.get("industry")
        context["mission"] = profile.get("mission")

    # Also check for context.yaml in org subdirs
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
                    # Add the directory name as id if not present
                    if "id" not in data:
                        data["id"] = item_dir.name
                    # Add source path for reference
                    data["_source"] = f"entities/{entity_type}/{item_dir.name}"
                    entities.append(data)

    return entities


def main():
    parser = argparse.ArgumentParser(description="Load organizational entities for image generation")
    parser.add_argument("--entities-root", help="Path to entities/ directory")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    parser.add_argument("--type", help="Load only specific entity type")
    args = parser.parse_args()

    # Find entities root
    entities_root = Path(args.entities_root) if args.entities_root else find_entities_root()

    if not entities_root or not entities_root.exists():
        result = {
            "success": False,
            "error": "NO_ENTITIES_DIR",
            "error_message": "Could not find entities/ directory",
            "searched_from": str(Path.cwd())
        }
        print(json.dumps(result, indent=2 if args.pretty else None))
        sys.exit(1)

    # Discover available entity types from directory structure
    available_types = discover_entity_types(entities_root)

    # Load organization context
    organization = load_organization_context(entities_root)

    # Load entities
    entities = {}
    counts = {}

    types_to_load = [args.type] if args.type else available_types

    for entity_type in types_to_load:
        loaded = load_entities_of_type(entities_root, entity_type)
        entities[entity_type] = loaded
        counts[entity_type] = len(loaded)

    # Calculate total
    total_entities = sum(counts.values())

    result = {
        "success": True,
        "entities_root": str(entities_root),
        "available_types": available_types,
        "organization": organization,
        "entities": entities,
        "counts": counts,
        "total_entities": total_entities
    }

    print(json.dumps(result, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
