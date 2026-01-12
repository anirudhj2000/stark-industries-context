#!/usr/bin/env python3
"""
Helper script for artifact generation.

This script handles deterministic operations like file reading/writing
that Claude invokes via Bash tool.
"""

import argparse
import json
import sys
from pathlib import Path


def load_template(template_path: str) -> dict:
    """Load and parse template file."""
    path = Path(template_path)
    if not path.exists():
        return {"error": f"Template not found: {template_path}"}

    content = path.read_text()

    # Parse sections from markdown template
    sections = []
    current_section = None

    for line in content.split('\n'):
        if line.startswith('## '):
            if current_section:
                sections.append(current_section)
            current_section = {
                "title": line[3:].strip(),
                "content": "",
                "placeholder": True
            }
        elif current_section:
            current_section["content"] += line + "\n"

    if current_section:
        sections.append(current_section)

    return {
        "template_path": template_path,
        "raw_content": content,
        "sections": sections
    }


def gather_project_context(project_context_path: str) -> dict:
    """Gather all relevant project context."""
    context = {
        "project_brief": None,
        "qa_tracker": None,
        "sources": [],
        "existing_artifacts": []
    }

    base_path = Path(project_context_path)

    # Load project brief
    brief_path = base_path / "artifacts" / "project_brief" / "structured.md"
    if brief_path.exists():
        context["project_brief"] = brief_path.read_text()

    # Load QA tracker
    qa_path = base_path / "artifacts" / "qa_tracker" / "state.json"
    if qa_path.exists():
        try:
            context["qa_tracker"] = json.loads(qa_path.read_text())
        except json.JSONDecodeError:
            pass

    # Load source summaries
    sources_dir = base_path / "sources"
    if sources_dir.exists():
        for source_dir in sources_dir.iterdir():
            if source_dir.is_dir():
                summary_path = source_dir / "structured.md"
                if summary_path.exists():
                    context["sources"].append({
                        "source_id": source_dir.name,
                        "summary": summary_path.read_text()
                    })

    return context


def main():
    parser = argparse.ArgumentParser(description="Artifact generation helper")
    parser.add_argument("--action", required=True,
                        choices=["load-template", "gather-context", "write-artifact"])
    parser.add_argument("--template-path", help="Path to template file")
    parser.add_argument("--project-context-path", help="Path to project workspace")
    parser.add_argument("--output-path", help="Path to write generated artifact")
    parser.add_argument("--content", help="Content to write (for write-artifact)")

    args = parser.parse_args()

    if args.action == "load-template":
        if not args.template_path:
            print(json.dumps({"error": "template-path required"}))
            sys.exit(1)
        result = load_template(args.template_path)
        print(json.dumps(result, indent=2))

    elif args.action == "gather-context":
        if not args.project_context_path:
            print(json.dumps({"error": "project-context-path required"}))
            sys.exit(1)
        result = gather_project_context(args.project_context_path)
        print(json.dumps(result, indent=2))

    elif args.action == "write-artifact":
        if not args.output_path or not args.content:
            print(json.dumps({"error": "output-path and content required"}))
            sys.exit(1)

        output_path = Path(args.output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(args.content)
        print(json.dumps({"status": "written", "path": str(output_path)}))


if __name__ == "__main__":
    main()
