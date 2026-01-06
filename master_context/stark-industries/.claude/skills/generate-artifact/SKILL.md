---
name: generate-artifact
description: Generate project artifacts using templates and project context
version: 1.0.0
author: GSD Team
---

# Generate Artifact Skill

This skill generates project artifacts (PRD, TDD, FRD, etc.) using templates and accumulated project context.

## Input Parameters

The skill receives these parameters via structured output:

- `artifact_type`: Type of artifact to generate (PRD, TDD, FRD, etc.)
- `template_path`: Path to template file in workspace (e.g., `.claude/templates/prd.md`)
- `project_id`: Project identifier
- `project_context_path`: Path to project workspace (e.g., `project_workspaces/project_123/`)
- `custom_prompt`: Optional custom instructions for generation
- `output_path`: Where to write the generated artifact

## Workflow

1. **Load Template**: Read the template file from `template_path`
2. **Gather Context**:
   - Read PROJECT_BRIEF from project workspace
   - Read QA_TRACKER for answered questions and insights
   - Read any existing artifacts in the phase
   - Read sources summaries if available
3. **Generate Content**: Use Claude to fill in template with project context
4. **Write Output**: Save generated artifact to `output_path`
5. **Return structured output** (task runner handles git)

**DO NOT run git add, git commit, or git push.** The task runner handles all git operations.

## Output Schema

```json
{
  "type": "object",
  "properties": {
    "status": {"type": "string", "enum": ["success", "error"]},
    "artifact_type": {"type": "string"},
    "output_path": {"type": "string"},
    "files_written": {"type": "array", "items": {"type": "string"}},
    "commit_message": {"type": "string"},
    "sections_generated": {"type": "array", "items": {"type": "string"}},
    "context_sources_used": {"type": "array", "items": {"type": "string"}},
    "error": {"type": "string"}
  },
  "required": ["status", "artifact_type", "files_written", "commit_message"]
}
```

## Execution

When invoked:

1. Parse input parameters from payload
2. Validate template exists at `template_path`
3. Load project context from project workspace:
   - `{project_context_path}/artifacts/project_brief/structured.md`
   - `{project_context_path}/artifacts/qa_tracker/state.json`
   - `{project_context_path}/sources/*/structured.md`
4. Read template and identify sections to populate
5. Generate content for each section using accumulated context
6. Write generated content to `output_path`
7. Return structured output with `files_written` and `commit_message`

**DO NOT run git add, git commit, or git push.** The task runner handles all git operations.

## Error Handling

- If template not found: Return error with suggestion to sync templates
- If project context insufficient: Return partial generation with warnings
