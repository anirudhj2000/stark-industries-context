---
name: frd-brainstorm
description: Create a Functional Requirements Document through collaborative dialogue. Checks for PRD first. Use when user tags @frd.
---

# FRD Brainstorm Command

Read the skill: `.claude/skills/frd-brainstorm/SKILL.md`

## Quick Reference

| Item | Value |
|------|-------|
| Input | `project_id`, `project_name`, `prompt` from payload file |
| Output | Plain text during dialogue, JSON at completion |
| Artifact | `project_workspaces/project_{project_id}/artifacts/art_frd_*/content.md` |
| Prerequisite | Checks for existing PRD (soft redirect if missing) |
