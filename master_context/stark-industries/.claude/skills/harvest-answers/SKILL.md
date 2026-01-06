---
name: harvest-answers
description: Use when harvesting a Q&A answer into an entity after summarize-answers has run - reads existing summary, updates entity field that had the gap, tracks harvest provenance via cursor
---

# Harvest Answers

## Overview

Takes a question's existing summary.md and integrates the answer into the relevant entity. Returns structured JSON - the handler sends the webhook.

**REQUIRED BACKGROUND:** You MUST run `summarize-answers` first to create the summary.md file.

## When to Use

**Use when:**
- Q&A thread has been summarized (summary.md exists in `summaries/`)
- Project owner clicks "Harvest" in Playbook UI
- Need to fill an entity gap with the Q&A answer

**Don't use when:**
- Summary.md doesn't exist yet → run `summarize-answers` first
- Summary is stale (new responses since summarization) → re-run `summarize-answers`

## Quick Reference

| Step | Action | File |
|------|--------|------|
| 1 | Read manifest + payload | From argument paths (do NOT use hardcoded names) |
| 2 | Read question YAML | `questions/{ref_id}.yaml` |
| 3 | Read summary.md | `summaries/{ref_id}_summary.md` |
| 4 | Verify summary_cursor | Check covers all responses |
| 5 | Update entity | `entities/{type}/{id}/context.yaml` |
| 6 | Update harvest_cursor | `questions/{ref_id}.yaml` |
| 7 | Git commit | All changed files |
| 8 | Return JSON | Structured output for handler |

---

## Workflow

### Phase 1: Load Configuration

**Read manifest, payload, and QnA artifact from temp files (written by Agent SDK):**

```python
import json
import os
import sys
import yaml

# Read manifest and payload from the file paths provided as arguments
# IMPORTANT: Do NOT use hardcoded paths - use the arguments passed to the command
# First argument = manifest path, Second argument = payload path
manifest_path = sys.argv[1]  # Path from first argument
payload_path = sys.argv[2]   # Path from second argument

with open(manifest_path, 'r') as f:
    manifest = json.load(f)

with open(payload_path, 'r') as f:
    payload = json.load(f)

# Extract key information (manifest v2.0 uses 'org' not 'organization')
org_id = manifest['org']['id']
project_id = payload['project_id']
question_id = payload['question_id']
agent_sdk_ref_id = payload['agent_sdk_ref_id']  # e.g., "qna_20251207_abc12"
harvest_count = payload.get('harvest_count', 0)
topic_id = payload.get('topic_id')
context_type = payload.get('context_type', 'project')

# Optional: User prompt provides additional context when invoked from chat
user_prompt = payload.get('user_prompt', '')

# Resolve artifact_dir based on context_type (all projects use project workspace)
if context_type == 'project':
    artifact_dir = f"project_workspaces/project_{project_id}/artifacts/art_qa_tracker_{project_id}"
else:
    artifact_dir = f"artifacts/art_qa_tracker_{project_id}"

question_path = f"{artifact_dir}/questions/{agent_sdk_ref_id}.yaml"

if not os.path.exists(question_path):
    raise FileNotFoundError(f"Question artifact not found: {question_path}")

with open(question_path, 'r') as f:
    qna_artifact = yaml.safe_load(f)

question_text = qna_artifact['text']
thread = qna_artifact.get('thread', [])
```

---

### Phase 2: Read Existing Summary

**Summary.md is created by summarize-answers skill in the summaries/ directory:**

```python
# Directory structure (artifact_dir resolved from context_type):
# {artifact_dir}/
# ├── type.meta.json
# ├── questions/
# │   └── qna_20251207_abc12.yaml        # Question artifact
# └── summaries/
#     └── qna_20251207_abc12_summary.md  # Summary (created by summarize-answers)

summary_path = f"{artifact_dir}/summaries/{agent_sdk_ref_id}_summary.md"

if not os.path.exists(summary_path):
    raise FileNotFoundError(
        f"Summary not found: {summary_path}. "
        "Run summarize-answers first."
    )

with open(summary_path, 'r') as f:
    summary_content = f.read()

# Extract the Answer section from the summary markdown
# Format: ## Answer\n\n{answer text}\n\n## Consensus Points...
def extract_answer_section(content):
    """Extract text between ## Answer and next ## header."""
    import re
    match = re.search(r'## Answer\s*\n\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
    return match.group(1).strip() if match else content

answer_text = extract_answer_section(summary_content)
```

---

### Phase 2.5: Check Summary is Current

**Verify summary is up-to-date before harvesting:**

```python
def is_summary_current(qna_artifact):
    """Check if summary.md covers all thread replies."""
    thread = qna_artifact.get('thread', [])
    summary_cursor = qna_artifact.get('summary_cursor')

    if not thread:
        return False  # No responses to harvest

    if summary_cursor is None:
        return False  # Never summarized

    return summary_cursor >= len(thread) - 1

if not is_summary_current(qna_artifact):
    raise ValueError(
        "Summary is stale - new responses exist since last summary. "
        "Run summarize-answers first."
    )
```

---

### Phase 3: Update Entity with Answer

**Use the answer from summary to update the entity that had the gap:**

```python
# Get source info from QnA artifact (which entity/field had the gap)
source_info = qna_artifact.get('source', {})
entity_id = source_info.get('entity_id')
entity_type = source_info.get('entity_type')
field_path = source_info.get('field_path')
entity_file = None

if entity_id and entity_type and field_path:
    entity_file = f"entities/{entity_type}/{entity_id}/context.yaml"

    if os.path.exists(entity_file):
        with open(entity_file, 'r') as f:
            entity = yaml.safe_load(f)

        # Update the field that had the gap
        def set_nested_field(obj, path, value):
            """Set a nested field like 'profile.joined_date'."""
            keys = path.split('.')
            for key in keys[:-1]:
                obj = obj.setdefault(key, {})
            obj[keys[-1]] = value

        set_nested_field(entity, field_path, answer_text)

        # Add citation
        if 'citations' not in entity:
            entity['citations'] = []
        entity['citations'].append({
            'source_id': f"qa_{question_id}",
            'source_type': 'qa_harvest',
            'note': f"From Q&A: {question_text[:50]}...",
            'harvested_at': datetime.utcnow().isoformat() + 'Z'
        })

        with open(entity_file, 'w') as f:
            yaml.safe_dump(entity, f, allow_unicode=True, sort_keys=False)
```

---

### Phase 4: Update Harvest Cursor

**Mark the question as harvested via harvest_cursor:**

```python
from datetime import datetime

# Update harvest cursor in the question YAML
qna_artifact['harvest_cursor'] = len(thread) - 1
qna_artifact['last_harvested_at'] = datetime.utcnow().isoformat() + 'Z'
qna_artifact['harvest_count'] = harvest_count + 1

with open(question_path, 'w') as f:
    yaml.safe_dump(qna_artifact, f, allow_unicode=True, sort_keys=False)

# Track files written for the task runner
files_written = [question_path]
if entity_file and os.path.exists(entity_file):
    files_written.append(entity_file)
```

**DO NOT run git add, git commit, or git push.** The task runner handles all git operations.

---

### Phase 5: Return Structured Output (CRITICAL)

**The handler sends the webhook. Return valid JSON matching this schema:**

```json
{
  "question_id": "uuid-from-payload",
  "harvested": true,
  "summary_file_path": "{artifact_dir}/summaries/qna_20251207_abc12_summary.md",
  "files_written": ["{artifact_dir}/questions/qna_20251207_abc12.yaml", "entities/person/vivek_gupta/context.yaml"],
  "commit_message": "harvest: qna_20251207_abc12",
  "entity_updated": true,
  "metadata": {
    "harvest_count": 1,
    "harvested_at": "2025-12-08T10:30:00Z",
    "project_id": "project-uuid",
    "topic_id": "topic-uuid-or-null",
    "agent_sdk_ref_id": "qna_20251207_abc12",
    "entity_id": "vivek_gupta",
    "entity_type": "person",
    "field_path": "profile.joined_date"
  }
}
```

Note: `{artifact_dir}` is resolved from `context_type` (e.g., `project_workspaces/project_{project_id}/artifacts/art_qa_tracker_{project_id}`).

**Important:**
- The handler receives this JSON via structured output
- The handler sends the webhook to Playbook with proper format
- You do NOT need to send any webhook yourself

---

## Error Handling

**If harvest fails, return an error response:**

```json
{
  "question_id": "uuid-from-payload",
  "harvested": false,
  "error": "Harvest failed: specific error message"
}
```

**Common errors:**
- Summary not found (run summarize-answers first)
- Summary is stale (new responses since last summary)
- Entity file not found
- Git commit failed

---

## Output Schema

```json
{
  "type": "object",
  "properties": {
    "question_id": {
      "type": "string",
      "description": "UUID of the question being harvested"
    },
    "harvested": {
      "type": "boolean",
      "description": "Whether the harvest was successful"
    },
    "summary_file_path": {
      "type": "string",
      "description": "Path to the summary.md file that was read"
    },
    "files_written": {
      "type": "array",
      "items": {"type": "string"},
      "description": "List of files modified by this skill"
    },
    "commit_message": {
      "type": "string",
      "description": "Commit message for the task runner"
    },
    "entity_updated": {
      "type": "boolean",
      "description": "Whether an entity was updated with the answer"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "harvest_count": {"type": "integer"},
        "harvested_at": {"type": "string"},
        "project_id": {"type": "string"},
        "topic_id": {"type": "string"},
        "agent_sdk_ref_id": {"type": "string"},
        "entity_id": {"type": "string"},
        "entity_type": {"type": "string"},
        "field_path": {"type": "string"}
      }
    }
  },
  "required": ["question_id", "harvested", "files_written", "commit_message"]
}
```

---

## Re-Harvest Behavior

When a question is harvested multiple times (harvest_count > 0):

1. **Re-read summary.md** (may have been updated by summarize-answers)
2. **Update entity again** with latest answer
3. **Increment harvest_count** in question YAML
4. **Track version history** via git commits

```python
# Re-harvest uses same flow - reads latest summary.md
# harvest_count is incremented automatically in Phase 4
```

---

## MANDATORY EXECUTION ORDER

**You MUST execute these steps IN ORDER:**

1. **READ** manifest + payload from the file paths passed as arguments (do NOT use hardcoded names)
2. **RESOLVE** `artifact_dir` from `context_type` and `project_id` in payload
3. **READ** question artifact YAML from `{artifact_dir}/questions/{ref_id}.yaml`
4. **READ** summary.md from `{artifact_dir}/summaries/{ref_id}_summary.md`
5. **VERIFY** summary is current (summary_cursor covers all responses)
6. **UPDATE** entity with answer (if source info available)
7. **UPDATE** question YAML with harvest_cursor
8. **RETURN** structured JSON with `files_written` and `commit_message`

**DO NOT run git add, git commit, or git push.** The task runner handles all git operations.

**FAILURE CONDITIONS:**
- Summary.md not found = FAIL (run summarize-answers first)
- Summary is stale = FAIL (run summarize-answers first)

---

## Quality Criteria

A good harvest should:

1. **Read Existing Summary**: Never regenerate - use summary.md from summarize-answers
2. **Update Entities**: Fill the gap in the entity that triggered the question
3. **Track Provenance**: Add citation linking back to Q&A source
4. **Support Re-harvest**: Multiple harvests update entity with latest answer
5. **Maintain Cursors**: Update harvest_cursor to mark what's been harvested

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Creating summary.md instead of reading it | Read from `summaries/{ref_id}_summary.md` - summarize-answers creates it |
| Harvesting without checking summary_cursor | Verify summary is current before harvesting |
| Not updating entity | Extract answer and update the entity field that had the gap |
| Forgetting to update harvest_cursor | Update question YAML with harvest_cursor |
| Running git add/commit/push | **NEVER** - task runner handles all git operations |
| Making HTTP calls | Never - return JSON, handler does HTTP |
