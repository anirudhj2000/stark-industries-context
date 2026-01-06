---
name: prd-brainstorm
description: Create a Product Requirements Document through collaborative dialogue. Use when user tags @prd.
---

# PRD Brainstorm Command

Read the skill: `.claude/skills/prd-brainstorm/SKILL.md`

## Quick Reference

| Item | Value |
|------|-------|
| Input | `project_id`, `project_name`, `prompt` from payload file |
| Output | Plain text during dialogue, JSON at completion |
| Artifact | `project_workspaces/project_{project_id}/artifacts/art_prd_*/content.md` |
