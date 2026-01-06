"""
Generate Questions - Utility Functions

This file provides utility functions for the generate-questions skill.
The actual gap analysis and question generation is done by Claude (AI-driven).

SKILL.md guides Claude on how to analyze entities and generate questions.
This file provides the tools to scan, load, write, and commit.
"""

import os
import json
import yaml
import random
import string
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


# =============================================================================
# Entity Scanning & Loading
# =============================================================================

def scan_all_entity_files(entities_dir: str) -> List[str]:
    """
    Scan entities directory for all entity YAML files.

    Structure: entities/{type}/{id}/context.yaml

    Returns list of file paths.
    """
    entity_files = []

    if not os.path.exists(entities_dir):
        return entity_files

    for type_dir in os.listdir(entities_dir):
        type_path = os.path.join(entities_dir, type_dir)
        if not os.path.isdir(type_path) or type_dir in ('schemas', 'organization'):
            continue

        for entity_id in os.listdir(type_path):
            entity_path = os.path.join(type_path, entity_id)
            if not os.path.isdir(entity_path):
                continue

            context_file = os.path.join(entity_path, 'context.yaml')
            if os.path.exists(context_file):
                entity_files.append(context_file)

    return entity_files


def load_entity(entity_file: str) -> Dict:
    """Load a single entity from its context.yaml file."""
    with open(entity_file, 'r') as f:
        return yaml.safe_load(f)


def get_entity_summary(entity: Dict) -> str:
    """
    Get a brief summary of an entity for AI analysis.

    Returns a formatted string with key entity info.
    """
    entity_type = entity.get('type', 'unknown')
    entity_id = entity.get('id', 'unknown')
    name = entity.get('name', entity_id)

    summary_lines = [
        f"Type: {entity_type}",
        f"ID: {entity_id}",
        f"Name: {name}",
    ]

    # Add status if present
    if 'status' in entity:
        summary_lines.append(f"Status: {entity['status']}")

    # Add completeness if present
    completeness = entity.get('metadata', {}).get('completeness')
    if completeness:
        summary_lines.append(f"Completeness: {completeness}")

    return "\n".join(summary_lines)


# =============================================================================
# Conflict Extraction (Hints for AI)
# =============================================================================

def find_conflict_markers(obj: Any, path: str = "") -> List[Tuple[str, Dict]]:
    """Recursively find all _conflict keys in nested structure."""
    markers = []

    if isinstance(obj, dict):
        if '_conflict' in obj:
            markers.append((path, obj['_conflict']))

        for key, value in obj.items():
            if key != '_conflict':
                new_path = f"{path}.{key}" if path else key
                markers.extend(find_conflict_markers(value, new_path))

    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            new_path = f"{path}[{i}]"
            markers.extend(find_conflict_markers(item, new_path))

    return markers


def extract_conflicts(entity: Dict) -> List[Dict]:
    """
    Extract conflict markers from an entity.

    Returns list of conflicts as hints for AI analysis.
    """
    conflicts = []

    for field_path, conflict_marker in find_conflict_markers(entity):
        conflicts.append({
            "field": conflict_marker.get('field', field_path),
            "existing_value": conflict_marker.get('existing_value'),
            "new_value": conflict_marker.get('new_value'),
            "source_id": conflict_marker.get('source_id'),
            "severity": conflict_marker.get('severity', 'medium'),
            "reason": conflict_marker.get('reason')
        })

    return conflicts


# =============================================================================
# Deduplication
# =============================================================================

def load_existing_questions(artifacts_dir: str, project_id: str) -> Dict[Tuple, Dict]:
    """
    Load existing QnA artifacts and build dedup index.

    Returns dict keyed by (entity_id, entity_type, field_path) for O(1) lookup.
    """
    existing = {}
    qa_tracker_dir = os.path.join(artifacts_dir, f'art_qa_tracker_{project_id}')
    questions_dir = os.path.join(qa_tracker_dir, 'questions')

    if not os.path.exists(questions_dir):
        return existing

    for filename in os.listdir(questions_dir):
        if not filename.endswith('.yaml'):
            continue

        artifact_path = os.path.join(questions_dir, filename)
        with open(artifact_path, 'r') as f:
            artifact = yaml.safe_load(f)

        source = artifact.get('source', {})
        key = (
            source.get('entity_id'),
            source.get('entity_type'),
            source.get('field_path')
        )
        existing[key] = artifact

    return existing


def is_duplicate(entity_id: str, entity_type: str, field_path: str,
                 existing_questions: Dict) -> bool:
    """Check if question already exists for this entity+field."""
    key = (entity_id, entity_type, field_path)
    return key in existing_questions


def generate_question_ref_id() -> str:
    """Generate unique agent_sdk_ref_id: qna_YYYYMMDD_xxxxx"""
    date_part = datetime.now().strftime('%Y%m%d')
    random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    return f"qna_{date_part}_{random_part}"


# =============================================================================
# Configuration Loading
# =============================================================================

def load_configuration(manifest_path: str, payload_path: str) -> Tuple[Dict, Dict]:
    """
    Load manifest and payload from temp files.

    Returns (manifest, payload) tuple.
    """
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    with open(payload_path, 'r') as f:
        payload = json.load(f)

    return manifest, payload


def extract_config(manifest: Dict, payload: Dict) -> Dict:
    """Extract key configuration from manifest and payload."""
    return {
        'org_id': manifest['org']['id'],
        'org_slug': manifest['org']['slug'],
        'job_id': payload['job_id'],
        'project_id': payload.get('project_id', 'default'),
        'question_types': payload.get('question_types', ['gap_analysis', 'conflict_resolution']),
        'team_members': manifest.get('team_members', [])
    }


# =============================================================================
# Artifact Writing
# =============================================================================

def ensure_qa_tracker_structure(artifacts_dir: str, project_id: str,
                                 org_id: str) -> Tuple[Path, Path]:
    """
    Ensure QA tracker artifact directory structure exists.

    Creates:
        artifacts/art_qa_tracker_{project_id}/
        ├── type.meta.json
        └── questions/
    """
    qa_tracker_dir = Path(artifacts_dir) / f'art_qa_tracker_{project_id}'
    questions_dir = qa_tracker_dir / 'questions'

    questions_dir.mkdir(parents=True, exist_ok=True)

    meta_path = qa_tracker_dir / 'type.meta.json'
    if not meta_path.exists():
        meta_content = {
            "artifact_type": "QA_TRACKER",
            "artifact_id": f"art_qa_tracker_{project_id}",
            "project_id": project_id,
            "org_id": org_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "version": "1.0"
        }
        with open(meta_path, 'w') as f:
            json.dump(meta_content, f, indent=2)

    return qa_tracker_dir, questions_dir


def create_question_artifact(
    text: str,
    entity_id: str,
    entity_type: str,
    question_type: str,
    job_id: str,
    priority: str = "normal",
    field_path: str = "",
    gap_type: str = "ai_identified",
    additional_context: Dict = None
) -> Dict:
    """
    Create a question artifact dict.

    Args:
        text: The question text
        entity_id: ID of the entity this question is about
        entity_type: Type of the entity
        question_type: "gap_analysis" or "conflict_resolution"
        job_id: The job ID that generated this question
        priority: "normal" or "high"
        field_path: Optional field path if question is about a specific field
        gap_type: Type of gap identified
        additional_context: Any additional context to include

    Returns:
        Question artifact dict ready to write.
    """
    ref_id = generate_question_ref_id()

    artifact = {
        "id": ref_id,
        "text": text,
        "question_type": question_type,
        "priority": priority,
        "source": {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "field_path": field_path,
            "gap_type": gap_type,
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by_job": job_id,
        "thread": [],
        "harvest_cursor": None
    }

    if additional_context:
        artifact["source"].update(additional_context)

    return artifact


def write_question_artifact(artifact: Dict, project_id: str, org_id: str) -> str:
    """
    Write a single question artifact to the QA tracker.

    Returns the path to the written file.
    """
    qa_tracker_dir, questions_dir = ensure_qa_tracker_structure(
        'artifacts', project_id, org_id
    )

    ref_id = artifact['id']
    artifact_path = questions_dir / f"{ref_id}.yaml"

    with open(artifact_path, 'w') as f:
        yaml.safe_dump(artifact, f, allow_unicode=True, sort_keys=False)

    return str(artifact_path)


def write_qna_artifacts(artifacts: List[Dict], project_id: str,
                        org_id: str) -> List[str]:
    """
    Write multiple QnA artifacts to git.

    Creates individual YAML files:
        artifacts/art_qa_tracker_{project_id}/questions/{ref_id}.yaml

    Returns list of created file paths.
    """
    qa_tracker_dir, questions_dir = ensure_qa_tracker_structure(
        'artifacts', project_id, org_id
    )

    created_paths = []

    for artifact in artifacts:
        ref_id = artifact['id']
        artifact_path = questions_dir / f"{ref_id}.yaml"

        with open(artifact_path, 'w') as f:
            yaml.safe_dump(artifact, f, allow_unicode=True, sort_keys=False)

        created_paths.append(str(artifact_path))

    # Include type.meta.json
    meta_path = qa_tracker_dir / 'type.meta.json'
    if meta_path.exists() and str(meta_path) not in created_paths:
        created_paths.append(str(meta_path))

    return created_paths


def commit_artifacts(artifact_paths: List[str], project_id: str) -> Optional[str]:
    """
    Git add and commit artifacts.

    Returns commit SHA or None if nothing to commit.
    """
    if not artifact_paths:
        return None

    subprocess.run(['git', 'add'] + artifact_paths, check=True)
    subprocess.run(
        ['git', 'commit', '-m',
         f'qna: generate {len(artifact_paths)} questions for project {project_id}'],
        check=True
    )

    result = subprocess.run(
        ['git', 'rev-parse', 'HEAD'],
        capture_output=True, text=True, check=True
    )
    return result.stdout.strip()
