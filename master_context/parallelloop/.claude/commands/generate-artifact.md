---
name: generate-artifact
description: Generate project artifacts (PRD, Technical Spec, User Stories, API Spec, Database Schema). Routes to appropriate skill based on artifact_type parameter.
disable-model-invocation: true
---

# Generate Artifact Command

This command dispatches to the appropriate artifact generator skill based on the `artifact_type` parameter.

## Routing

Read `artifact_type` from the payload and invoke the corresponding skill:

| artifact_type | Skill |
|---------------|-------|
| `PRD` | `.claude/skills/prd-generator/SKILL.md` |
| `TECHNICAL_SPEC` | `.claude/skills/tech-spec-generator/SKILL.md` |
| `USER_STORIES` | `.claude/skills/user-story-generator/SKILL.md` |
| `API_SPEC` | `.claude/skills/api-spec-generator/SKILL.md` |
| `DATABASE_SCHEMA` | `.claude/skills/database-schema-generator/SKILL.md` |

## Workflow

1. Parse `artifact_type` from payload params
2. Read the corresponding skill file
3. Follow the skill instructions exactly
4. Return the structured output as specified by the skill

**DO NOT run git add, git commit, or git push.** The task runner handles all git operations. Each skill returns `files_written` and `commit_message` in its output.

## Example Payload

```json
{
  "command": "generate-artifact",
  "params": {
    "project_id": "uuid-here",
    "artifact_type": "PRD",
    "phase_artifact_id": "uuid-here",
    "custom_prompt": "Optional custom instructions"
  },
  "context": {
    "project_name": "My Project",
    "phase_name": "Discovery"
  }
}
```

## Error Handling

If `artifact_type` is not recognized:
```json
{
  "status": "error",
  "error": "Unknown artifact type: {artifact_type}. Supported: PRD, TECHNICAL_SPEC, USER_STORIES, API_SPEC, DATABASE_SCHEMA"
}
```
