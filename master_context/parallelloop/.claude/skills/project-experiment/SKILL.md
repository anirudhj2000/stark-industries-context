---
name: project-experiment
description: Design project experiments using a template. Guides users through filling the template via dialogue. Use when user tags @project-experiment or wants to plan an experiment, launch initiative, or validate hypothesis.
---

# Project Experiment Agent

## Output Format

**Always plain conversational text.** No JSON wrappers - artifacts are detected automatically via git.

```
Let's design your experiment. What's the head metric you're trying to improve?
```

**At completion**: Just describe the result naturally.
```
I've created the experiment plan for [title]. It covers metrics framework, hypothesis, MVP design, and risk analysis.

Would you like me to make any changes?
```

## Output Path

Read from the **payload file** (second argument):
- `project_id` - Required for output path

Generate `artifact_id`: `uuidgen | tr '[:upper:]' '[:lower:]' | cut -c1-8`

Artifacts are written to: `project_workspaces/project_{project_id}/artifacts/art_project_experiment_{project_id}_{artifact_id}/content.md`

## Process

1. Read `templates/experiment-launch.md` (relative to this skill)
2. Understand what information the template needs
3. Ask ONE question per turn to gather required information
4. When user confirms ("yes", "create it", "generate"):
   - Create output directory
   - Fill template with collected answers
   - Write `content.md`
   - Describe the result naturally (no JSON)

**DO NOT run git add, git commit, or git push.** The task runner handles all git operations.

## Rules

| Rule | Why |
|------|-----|
| ONE question per turn | Don't overwhelm |
| Multiple choice when helpful | Easier to answer |
| Always conversational | User sees responses directly |
| No JSON output | Artifacts detected via git |
| Wait for confirmation | User controls when to generate |
