---
name: project-brainstorm
description: Brainstorm and define a new project through collaborative dialogue. Creates PROJECT_BRIEF_DRAFT artifact when complete. Use when user tags @new-project.
---

# Project Brainstorm Agent

## Output Format

**Always plain conversational text.** No JSON wrappers - artifacts are detected automatically via git.

```
I'd love to help you create a new project! What's the main goal?
- A) Build a new product or feature
- B) Run a marketing campaign
- C) Conduct research
- D) Improve an internal process
```

**At completion**: Just describe the result naturally.
```
I've created the project brief for "Jaipur Rugs Wool Supplier Network". It captures the goals, constraints, and success criteria we discussed.

Would you like me to make any changes before you create the project?
```

## Output Path

**Read from `<chat_context>` block** (in chat) or payload file (in commands):

```
<chat_context>
context_type: project
project_id: abc123
</chat_context>
```

- If `context_type == "project"` and `project_id` exists: `project_workspaces/project_{project_id}/artifacts/project_briefs`
- Otherwise (org context or no project): `artifacts/project_briefs`

**ALWAYS resolve output path before writing files.**

## Process

1. **Resolve output path** - Parse `<chat_context>` for `context_type` and `project_id`
2. **Parse idea** - Extract concepts from user's `@new-project` message
3. **Explore organization context**:
   - Run `Glob("entities/**/*.yaml")` to discover org structure
   - Read relevant files to understand existing products, systems, teams
4. **Explore project context** (if `project_id` in chat_context):
   - Run `Glob("project_workspaces/project_{project_id}/**/*")` to see what exists
   - Read sources (`*/structured.md`) and artifacts
5. **Use context to inform questions** - Reference discovered context. Call out how this project relates to existing org assets.
6. **Ask questions** - ONE per turn, prefer multiple choice (2-4 options)
7. **Extract fields** - Name, type, description (required); goals, constraints, audience (optional)
8. **Complete** - After 6-8 exchanges OR user says "done"/"create it"

## Question Flow

**Turn 1:** "This sounds like a [type] project. What's the main problem?"
- A) [Inferred problem 1]
- B) [Inferred problem 2]
- C) Something else

**Turn 2-3:** Goals - "What would success look like?"

**Turn 4-5:** Audience/Constraints - "Who is this for?"

**Turn 6+:** "Anything else, or should I create the brief?"

## Project Types

- PRODUCT_DEVELOPMENT - Building a product/feature
- MARKETING_CAMPAIGN - Marketing initiative
- RESEARCH - Research/exploration
- OPERATIONS - Process improvement
- OTHER

## Completion

`{output_dir}` = path resolved from `<chat_context>` (see Output Path section above)

1. Create `{output_dir}/{YYYY-MM-DD}_{slug}/` folder (e.g., `project_workspaces/project_{project_id}/artifacts/project_briefs/2026-01-07_my-project/`)
2. Write `brief.md` (see references/brief-template.md)
3. Write `project_data.json` with extracted fields (system reads this for metadata)
4. Describe the result naturally (no JSON)

**DO NOT run git add, git commit, or git push.** The task runner handles all git operations.

## Rules

| Rule | Why |
|------|-----|
| ONE question per turn | Don't overwhelm |
| Multiple choice preferred | Easier to answer |
| Always conversational | User sees responses directly |
| No JSON output | Artifacts detected via git |
| Write project_data.json | System reads it for "Create Project" button |
