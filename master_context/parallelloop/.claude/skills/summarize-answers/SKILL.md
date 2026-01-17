---
name: summarize-answers
description: Use when question thread has new responses to summarize - supports both org-level and project-level contexts via context_type field. Reads thread[] from QA tracker artifact, writes summary.md to summaries/ directory, updates summary_cursor, commits to git, returns structured JSON.
disable-model-invocation: true
---

# Summarize Answers Skill

Generate summary of Q&A thread responses, write to artifact, return structured JSON.

**Supports both org-level and project-level contexts** - artifact path determined by `context_type` field.

**Trigger:** Agent SDK calls when new response received (5 min after last response).

---

## Output Path Resolution (CRITICAL)

**Read `context_type` from payload to determine artifact path:**

| context_type | project_id | Artifact Base Path |
|--------------|------------|-------------------|
| `"project"` | Present | `project_workspaces/project_{project_id}/artifacts/art_qa_tracker_{project_id}/` |
| `"org"` or missing | N/A | `artifacts/art_qa_tracker_{project_id}/` |

**Example:**
```python
# From payload
context_type = payload.get("context_type", "org")
project_id = payload.get("project_id")

if context_type == "project" and project_id:
    artifact_dir = f"project_workspaces/project_{project_id}/artifacts/art_qa_tracker_{project_id}"
else:
    artifact_dir = f"artifacts/art_qa_tracker_{project_id}"
```

---

## CRITICAL: YOU MUST WRITE FILES FIRST

```
┌─────────────────────────────────────────────────────────────┐
│  RETURNING JSON WITHOUT WRITING FILES = COMPLETE FAILURE    │
│  Use Write tool BEFORE returning JSON                       │
└─────────────────────────────────────────────────────────────┘
```

**Required tool calls (in order):**
1. **Read** the manifest and payload files from the paths provided as arguments (do NOT use hardcoded paths)
2. **Resolve artifact_dir** from `context_type` and `project_id`
3. **Read** `{artifact_dir}/questions/{ref_id}.yaml`
4. **Write** `{artifact_dir}/summaries/{ref_id}_summary.md`
5. **Write** updated question YAML with `summary_cursor`
6. **Return** structured JSON with `files_written` and `commit_message`

**DO NOT run git add, git commit, or git push.** The task runner handles all git operations.

---

## Quick Reference

| Step | Tool | Path |
|------|------|------|
| Read manifest | Read | First argument path (do NOT use hardcoded names) |
| Read payload | Read | Second argument path (do NOT use hardcoded names) |
| Resolve path | - | Use `context_type` to determine `{artifact_dir}` |
| Read question | Read | `{artifact_dir}/questions/{ref_id}.yaml` |
| Write summary | **Write** | `{artifact_dir}/summaries/{ref_id}_summary.md` |
| Update cursor | **Write** | `{artifact_dir}/questions/{ref_id}.yaml` |
| Return JSON | - | Include `files_written` and `commit_message` |

---

## Workflow

### 0. Resolve Artifact Path (FIRST)

```python
# From payload
context_type = payload.get("context_type", "org")
project_id = payload.get("project_id")

if context_type == "project" and project_id:
    artifact_dir = f"project_workspaces/project_{project_id}/artifacts/art_qa_tracker_{project_id}"
else:
    artifact_dir = f"artifacts/art_qa_tracker_{project_id}"
```

**Use `{artifact_dir}` for all file paths below.**

### 1. Load Configuration

```python
# From payload
project_id = payload['project_id']
question_id = payload['question_id']
agent_sdk_ref_id = payload['agent_sdk_ref_id']  # e.g., "qna_20251207_abc12"
```

### 2. Read Question Artifact

```python
question_path = f"{artifact_dir}/questions/{agent_sdk_ref_id}.yaml"

# Extract from YAML
question_text = question_artifact['text']
thread = question_artifact.get('thread', [])  # List of responses
summary_cursor = question_artifact.get('summary_cursor')  # Last summarized index
```

### 3. Check if Summary Needed

```python
if not thread:
    return {"question_id": question_id, "summary": "", "skipped": True, "reason": "No responses"}

if summary_cursor is not None and summary_cursor >= len(thread) - 1:
    return {"question_id": question_id, "summary": "", "skipped": True, "reason": "Already current"}
```

### 4. Analyze & Write Summary

**Analyze thread for:** consensus points, key insights, contradictions, gaps.

**Write to:** `{artifact_dir}/summaries/{agent_sdk_ref_id}_summary.md`

```markdown
# Summary: {question_text}

**Ref ID:** {agent_sdk_ref_id}
**Summarized:** {timestamp}
**Responses:** {len(thread)}

## Answer
{synthesized_answer}

## Consensus Points
- {point} (agreed by N responders)

## Key Insights
- From {responder}: {insight}

## Open Items
- [ ] {gap_or_conflict}
```

### 5. Update Question YAML

```python
question_artifact['summary_cursor'] = len(thread) - 1
# Write back to question_path
```

### 6. Return JSON

**DO NOT run git add, git commit, or git push.** The task runner handles all git operations.

```json
{
  "question_id": "uuid",
  "summary": "All four products launched on March 28th, 2019. The responder confirmed this date applies to all products.",
  "summary_file_path": "{artifact_dir}/summaries/{ref_id}_summary.md",
  "files_written": [
    "{artifact_dir}/summaries/{ref_id}_summary.md",
    "{artifact_dir}/questions/{ref_id}.yaml"
  ],
  "commit_message": "summarize: {ref_id}",
  "key_points": ["point1", "point2"],
  "consensus_points": ["consensus1"],
  "open_items": [{"type": "gap", "description": "..."}],
  "metadata": {
    "total_responses": 4,
    "summarized_at": "2025-12-07T18:00:00Z",
    "summary_cursor": 3,
    "agent_sdk_ref_id": "qna_20251207_abc12",
    "context_type": "org"
  }
}
```

**Note:** `summary` field is plain text (the synthesized answer), NOT markdown with headers. The full structured markdown goes in the `summary.md` file.

**Required fields:** `question_id`, `summary`

---

## Red Flags - STOP If You See These

Before returning JSON, verify you have:
- ✅ Resolved `{artifact_dir}` from `context_type` and `project_id`
- ✅ Used **Write tool** to create `{artifact_dir}/summaries/{ref_id}_summary.md`
- ✅ Used **Write tool** to update `{artifact_dir}/questions/{ref_id}.yaml`
- ✅ Included `files_written` and `commit_message` in JSON output

If ANY are missing: **STOP. Do the file operations first.**

**DO NOT run git add, git commit, or git push.** The task runner handles all git operations.

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Returning JSON without writing files | Write files FIRST using Write tool |
| Running git add/commit/push | **NEVER** - task runner handles all git operations |
| Not resolving context_type first | ALWAYS resolve `{artifact_dir}` from `context_type` before any file operations |
| Using hardcoded org-level path | Use `{artifact_dir}` which handles both org and project contexts |
| Reading responses from payload | Read from `{artifact_dir}/questions/{ref_id}.yaml` thread[] |
| Wrong summary location | `{artifact_dir}/summaries/{ref_id}_summary.md` not `questions/` |
| Forgetting summary_cursor | Update YAML before returning |
| Summary without structure | Must have ## Answer, ## Consensus Points sections |

---

## Error Response

```json
{
  "question_id": "uuid",
  "summary": "",
  "error": "Summarization failed: {specific error}"
}
```
