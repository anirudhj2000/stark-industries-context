#!/usr/bin/env python3
"""
Structured Metadata Generator

Creates organization-aware structured.json files for transcriptions.
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def load_organization_schema(org_slug: str) -> dict:
    """Load organization-specific schema requirements"""
    schema_path = Path('.claude/skills/transcription/references/organization_schemas.json')

    if not schema_path.exists():
        # Return default schema
        return {
            "required_fields": ["title", "source_type", "metadata"],
            "optional_fields": ["department", "project", "tags"]
        }

    with open(schema_path) as f:
        schemas = json.load(f)
        return schemas.get(org_slug, schemas.get('default', {}))


def create_structured_metadata(
    source_id: str,
    transcript_data: dict,
    organization: str,
    transcript_path: str
) -> dict:
    """Create structured metadata following organization schema"""

    schema = load_organization_schema(organization)

    # Base structure
    structured = {
        "source_id": source_id,
        "title": f"Source {source_id} Transcription",
        "source_type": "AUDIO",  # or VIDEO
        "ingested_at": datetime.utcnow().isoformat() + 'Z',
        "transcript_path": transcript_path,
        "summary_markdown": None,  # Generated later by context-analysis skill
        "metadata": {
            "transcription_engine": transcript_data.get('engine'),
            "language": transcript_data.get('language'),
            "duration_seconds": transcript_data.get('duration'),
            "word_count": transcript_data.get('words'),
            "confidence": transcript_data.get('raw_response', {}).get('confidence', 0.95)
        },
        "links": {
            "artifacts": [],
            "questions": []
        }
    }

    # Add organization-specific fields
    if "department" in schema.get("optional_fields", []):
        structured["department"] = None  # To be filled from prompt context

    if "project" in schema.get("optional_fields", []):
        structured["project"] = None

    if "tags" in schema.get("optional_fields", []):
        structured["tags"] = []

    return structured


def main():
    parser = argparse.ArgumentParser(description='Create structured metadata')
    parser.add_argument('--source-id', required=True)
    parser.add_argument('--transcript', required=True, help='Path to transcript JSON')
    parser.add_argument('--organization', required=True)
    parser.add_argument('--output', required=True, help='Output structured.json path')

    args = parser.parse_args()

    transcript_path = Path(args.transcript)
    if not transcript_path.exists():
        print(f"ERROR: Transcript file not found: {transcript_path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(transcript_path) as f:
            transcript_data = json.load(f)

        structured = create_structured_metadata(
            source_id=args.source_id,
            transcript_data=transcript_data,
            organization=args.organization,
            transcript_path=args.output.replace('structured.json', 'transcript.txt')
        )

        with open(args.output, 'w') as f:
            json.dump(structured, f, indent=2)

        print(f"SUCCESS: Structured metadata created at {args.output}")

    except Exception as e:
        print(f"ERROR: Failed to create structured metadata: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
