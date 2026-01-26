---
name: github-repository-sync
description: Sync (clone or pull) GitHub repositories using GitHub App installation tokens. Supports org and project contexts.
---

# GitHub Repository Sync Command

Sync a GitHub repository (clone new or pull existing) using installation tokens and analyze its codebase structure.

Read the full skill file for detailed workflow:
`.claude/skills/github-repository-sync/SKILL.md`

## Quick Reference

1. **Read payload** - Extract installation_id, repo_url, source_id, context_type, project_id, operation
2. **Generate token** - Use GitHub App credentials from environment
3. **Sync repository** - Clone if new, pull if exists
4. **Analyze codebase** - File count, tech stack detection
5. **Create structured.md** - Structured findings
6. **Git commit** - Commit repository and analysis
7. **Return JSON** - Output commit_sha, operation, and metadata

## Environment Requirements

- `GITHUB_APP_ID` - GitHub App ID (set in Agent SDK)
- `GITHUB_APP_PRIVATE_KEY` - GitHub App private key (set in Agent SDK)

## Output

Returns structured JSON with:
- `commit_sha` - Git commit SHA
- `operation` - "clone" or "pull"
- `repo_path` - Path to repository
- `metadata` - File count, tech stack, etc.
