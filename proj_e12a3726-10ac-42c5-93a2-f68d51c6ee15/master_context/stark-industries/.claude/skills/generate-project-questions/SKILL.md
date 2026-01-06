---
name: project-generate-questions
description: Use when analyzing PROJECT sources to identify knowledge gaps. Three dimensions - (1) source-internal gaps (TBD, missing owners), (2) conflicts with org context, (3) capability gaps (current vs required state). Output is YAML files with qna_YYYYMMDD_xxxxx IDs.
---

# Project Generate Questions

Analyze project sources to generate questions. Output is **YAML** files (not JSON).

## CRITICAL Rules

1. **Use the script first** - Run `load_project_context.py` before analyzing
2. **Question files are YAML** - `{ref_id}.yaml`, NOT `.json`
3. **ID format**: `qna_YYYYMMDD_xxxxx` (e.g., `qna_20251211_a1b2c`)
4. **Include analysis_type** - Every question must have `source_internal`, `cross_reference`, or `capability_gap`

## Quick Reference

| Item | Value |
|------|-------|
| Required param | `project_id` |
| Output path | `project_workspaces/project_{id}/artifacts/art_qa_tracker_{project_id}/questions/` |
| File format | **YAML** (`{ref_id}.yaml`) |
| Script | `.claude/skills/project-generate-questions/scripts/load_project_context.py` |

## Three Analysis Dimensions

### 1. Source-Internal Gaps (`analysis_type: source_internal`)
TBD values, missing deadlines/owners, vague statements.

### 2. Cross-Reference Issues (`analysis_type: cross_reference`)
Conflicts with org entities, new entities not in org, opportunities to fill gaps.

### 3. Capability Gaps (`analysis_type: capability_gap`)
Current state vs new requirements - what's missing to bridge the gap?

**Capability gap questions MUST suggest options:**
- "Need real-time sync but no message queue. Use Redis, RabbitMQ, or Kafka?"
- "Handle 100 orders/day but need 1000. Scale team, automate, or outsource?"

## Workflow

### Step 1: Load Context (REQUIRED)

```bash
python3 .claude/skills/project-generate-questions/scripts/load_project_context.py --project-id {project_id} --base-dir {context_root} --pretty
```

### Step 2: Analyze All Three Dimensions

For each source, identify gaps in all three dimensions. Don't skip capability gaps.

### Step 3: Write Question Files (YAML)

Path: `project_workspaces/project_{project_id}/artifacts/art_qa_tracker_{project_id}/questions/{ref_id}.yaml`

```yaml
id: qna_20251211_abc12
text: "What is the exact budget for Phase 2?"
question_type: clarification
priority: high
source:
  source_id: src_001
  context: "Source mentions 'approximately $50k'"
  analysis_type: source_internal  # REQUIRED field
generated_at: "2025-12-11T10:00:00Z"
thread: []
```

### Step 4: Return Output

**DO NOT run git add, git commit, or git push.** The task runner handles all git operations.

Return JSON:
```json
{
  "questions": [{"id": "qna_20251211_abc12", "text": "...", "analysis_type": "source_internal"}],
  "files_written": ["project_workspaces/project_{project_id}/artifacts/art_qa_tracker_{project_id}/questions/qna_20251211_abc12.yaml"],
  "commit_message": "qna: generate questions for project {project_id}",
  "metadata": {
    "sources_analyzed": ["src_001", "src_002"],
    "source_internal_gaps": 5,
    "cross_reference_issues": 3,
    "capability_gaps": 2,
    "questions_generated": 10
  }
}
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Creating `.json` question files | Question files are **YAML**: `{ref_id}.yaml` |
| Using `q001`, `q002` IDs | Use `qna_YYYYMMDD_xxxxx` format |
| Missing `analysis_type` field | Every question needs `source_internal`, `cross_reference`, or `capability_gap` |
| Skipping capability gaps | Always compare current state vs requirements |
| Capability gaps without options | Suggest 2-3 alternatives for bridging gaps |
| Not using the script | Run `.claude/skills/project-generate-questions/scripts/load_project_context.py` first |
