---
name: tdd-brainstorm
description: Create a Technical Design Document through collaborative dialogue. Checks for PRD and FRD first. Use when user tags @tdd.
---

# TDD Brainstorm Command

Read the skill: `.claude/skills/tdd-brainstorm/SKILL.md`

## Quick Reference

| Item | Value |
|------|-------|
| Input | `project_id`, `project_name`, `prompt` from payload file |
| Output | Plain text during dialogue, JSON at completion |
| Artifact | `project_workspaces/project_{project_id}/artifacts/art_tdd_*/content.md` |
| Prerequisites | Checks for existing PRD and FRD (soft redirect if missing) |
