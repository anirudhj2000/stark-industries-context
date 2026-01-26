---
name: github-repository-sync
description: Sync GitHub repositories (clone or pull) and analyze codebase structure, tech stack, and metrics using GitHub App installation tokens. Supports both org-level and project-level contexts via context_type field.
---

# GitHub Repository Sync Skill

## Purpose

Sync GitHub repositories into the workspace using GitHub App installation tokens (clone new repos, pull existing ones) and perform analysis to extract insights about tech stack, file counts, and repository structure. Transform raw repositories into actionable organizational knowledge.

**Supports both org-level and project-level contexts** - output path determined by `context_type` field.

## When to Use

- Command: `github-repository-sync`
- Processing sources with type GITHUB_REPOSITORY
- Initial clone of repositories for analysis, auditing, or project setup
- Updating existing cloned repositories with latest changes
- Both org-level (`context_type: "org"`) and project-level (`context_type: "project"`) processing

## Output Path Resolution (CRITICAL)

**Read `context_type` from payload to determine output path:**

| context_type | project_id | Output Base Path |
|--------------|------------|------------------|
| `"project"` | Present | `project_workspaces/project_{project_id}/sources/{source_id}/` |
| `"org"` or missing | N/A | `sources/{source_id}/` |

**Example:**
```python
# From payload
context_type = payload.get("context_type", "org")
project_id = payload.get("project_id")
source_id = payload.get("source_id")

if context_type == "project" and project_id:
    output_base = f"project_workspaces/project_{project_id}/sources/{source_id}"
else:
    output_base = f"sources/{source_id}"
```

## What Agent SDK Already Did

Before you run, Agent SDK has:
- Downloaded and parsed markdown instruction file from S3 (if applicable)
- Extracted `installation_id`, `repo_url`, `branch`, and other metadata
- Validated manifest
- Sent "running" webhook to Playbook

## What You Need to Do

1. **Resolve output path** from `context_type` and `project_id`
2. **Determine operation** - Check if `{output_base}/repository/.git` exists (pull) or not (clone)
3. Generate GitHub App installation access token
4. Sync repository (clone if new, pull if exists)
5. Analyze codebase (file count, tech stack)
6. Create/update structured.md with findings
7. Commit to git
8. Return structured JSON with commit SHA and operation type

## Output Files

| File | Purpose |
|------|---------|
| `repository/` | Synced GitHub repository (full git history) |
| `structured.md` | Analysis results with tech stack, metrics, and insights |

---

## Workflow

### Step 0: Resolve Output Path and Determine Operation (FIRST)

```python
# Read from payload (passed as argument)
context_type = payload.get("context_type", "org")
project_id = payload.get("project_id")
source_id = payload.get("source_id")

if context_type == "project" and project_id:
    output_base = f"project_workspaces/project_{project_id}/sources/{source_id}"
else:
    output_base = f"sources/{source_id}"

# Determine operation
repo_path = f"{output_base}/repository"
if os.path.exists(f"{repo_path}/.git"):
    operation = "pull"
else:
    operation = "clone"
```

**Use `{output_base}` for all file paths below.**

### Step 1: Extract Payload Data

From the payload, extract:
- `installation_id` - GitHub App installation ID
- `repo_url` - Repository URL (e.g., https://github.com/owner/repo)
- `branch` - (Optional) Specific branch to sync
- `instruction` - (Optional) User's custom analysis instructions

### Step 2: Generate GitHub App Installation Token

**IMPORTANT:** This requires `GITHUB_APP_ID` and `GITHUB_APP_PRIVATE_KEY` environment variables to be set in Agent SDK.

```bash
python .claude/skills/github-repository-sync/scripts/generate_github_token.py \
  --installation-id "{installation_id}" \
  --output /tmp/github_token.json
```

**Output:** JSON file with:
```json
{
  "token": "ghs_xxx",
  "expires_at": "2025-12-30T12:00:00Z"
}
```

### Step 3: Sync Repository

Read the token from the previous step and sync the repository:

```bash
# Extract token from JSON
TOKEN=$(cat /tmp/github_token.json | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")

# Sync repository (clone or pull based on operation)
python .claude/skills/github-repository-sync/scripts/sync_repository.py \
  --repo-url "{repo_url}" \
  --access-token "$TOKEN" \
  --sync-path "{output_base}/repository" \
  --operation "{operation}" \
  --branch "{branch}" \
  --output /tmp/sync_result.json
```

**If branch is not specified in payload, omit the `--branch` flag.**

**Output:** JSON file with:
```json
{
  "sync_path": "/path/to/repo",
  "commit_sha": "abc123...",
  "branch": "main",
  "owner": "owner",
  "repo_name": "repo",
  "operation": "clone",
  "commits_pulled": 0
}
```

For pull operations, `commits_pulled` will show how many commits were fetched.

### Step 4: Analyze Repository

```bash
python .claude/skills/github-repository-sync/scripts/analyze_repository.py \
  --repo-path "{output_base}/repository" \
  --instructions "{instruction}" \
  --output /tmp/analysis_result.json
```

**If instruction is not in payload, omit the `--instructions` flag.**

**Output:** JSON file with:
```json
{
  "file_count": 150,
  "tech_stack": ["Python", "Django", "Docker"],
  "structure": {
    "top_level_dirs": ["src", "tests", "docs"],
    "has_tests": true,
    "has_docs": true,
    "has_ci": true
  },
  "user_instructions": "..."
}
```

### Step 5: Create Analysis Markdown

Read the results from Step 3 and Step 4, then create `{output_base}/structured.md`:

**Use the Write tool to create the file with the following structure:**

```markdown
# Repository Analysis: {repo_name}

## Repository Information
- **Owner**: {owner}
- **Repository**: {repo_name}
- **URL**: {repo_url}
- **Branch**: {branch}
- **Commit**: {commit_sha}
- **Last Sync**: {current_timestamp}
- **Operation**: {clone or pull}

## Code Metrics
- **Total Files**: {file_count}
- **Top-Level Directories**: {top_level_dirs_count}

## Technology Stack

{list_each_tech_stack_item}

## Repository Structure

### Top-Level Directories
{list_top_level_dirs}

### Project Organization
- **Has Tests**: {yes/no}
- **Has Documentation**: {yes/no}
- **Has CI/CD**: {yes/no}

## Analysis Notes

{user_instructions_or_standard_analysis}

---

*Analysis generated on {timestamp}*
```

**Example formatting:**
```markdown
## Technology Stack

- Python
- Django
- Docker
- PostgreSQL
```

### Step 6: Commit to Git

**IMPORTANT:** Commit both the synced repository and the analysis file.

```bash
git add {output_base}/repository {output_base}/structured.md

git commit -m "$(cat <<'EOF'
feat(sources): Sync GitHub repository {repo_name}

- Repository: {owner}/{repo_name}
- Operation: {clone/pull}
- Branch: {branch}
- Commit: {commit_sha_short}
- Files: {file_count}
- Tech Stack: {tech_stack_summary}
- Sync completed for source {source_id}

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

git rev-parse HEAD
```

**Note:** Replace placeholders with actual values from the JSON results.

### Step 7: Return Structured Output

**CRITICAL:** Return this exact JSON structure to Agent SDK:

```json
{
  "success": true,
  "operation": "{clone or pull}",
  "commit_sha": "{git_commit_sha_from_step_6}",
  "repo_path": "{output_base}/repository",
  "structured_path": "{output_base}/structured.md",
  "file_count": {file_count},
  "tech_stack": [{tech_stack_array}],
  "repo_name": "{owner}/{repo_name}",
  "branch": "{branch}",
  "repo_commit_sha": "{latest_commit_sha_in_repo}",
  "commits_pulled": {number_or_0}
}
```

**Use the exact field names shown above.** Agent SDK expects this structure.

---

## Error Handling

| Condition | Action |
|-----------|--------|
| GITHUB_APP_ID not set | `echo "ERROR: GITHUB_APP_ID environment variable not set"` -> exit 1 |
| GITHUB_APP_PRIVATE_KEY not set | `echo "ERROR: GITHUB_APP_PRIVATE_KEY environment variable not set"` -> exit 1 |
| Token generation fails | `echo "ERROR: Failed to generate GitHub token: {error}"` -> exit 1 |
| Invalid installation_id | `echo "ERROR: Invalid installation ID or app not installed"` -> exit 1 |
| Clone fails (auth) | `echo "ERROR: Authentication failed. Check token permissions."` -> exit 1 |
| Clone fails (not found) | `echo "ERROR: Repository not found or not accessible"` -> exit 1 |
| Pull fails (conflicts) | `echo "ERROR: Pull failed - merge conflicts detected"` -> exit 1 |
| Analysis fails | `echo "WARNING: Analysis incomplete: {error}"` -> continue with partial data |
| Git commit fails | `echo "ERROR: Git commit failed: {error}"` -> exit 1 |

Agent SDK catches errors and sends error webhooks to Playbook.

---

## Success Criteria

- [ ] Output path resolved correctly based on context_type
- [ ] Operation determined correctly (clone vs pull)
- [ ] GitHub App installation token generated successfully
- [ ] Repository synced to workspace
- [ ] Repository contains .git directory (full clone, not shallow)
- [ ] Codebase analyzed (file count, tech stack detected)
- [ ] structured.md created with proper formatting
- [ ] Both repository and structured.md committed to git
- [ ] Commit SHA returned in structured JSON
- [ ] Operation field returned correctly
- [ ] Metadata includes all required fields

---

## Environment Requirements

**CRITICAL:** The following environment variables MUST be set in Agent SDK:

```bash
GITHUB_APP_ID=123456
GITHUB_APP_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----
...
-----END RSA PRIVATE KEY-----"
```

**Without these variables, the skill will fail at token generation.**

---

## What Happens Next

After you complete:
1. Return commit SHA, operation, and metadata to Agent SDK
2. Agent SDK sends "completed" webhook to Playbook
3. Playbook updates source status and stores metadata

**You do NOT send webhooks** - Agent SDK handles that.

---

## Notes

- **Full clone**: Includes complete git history (not shallow)
- **Pull operation**: Uses `git fetch --all && git pull` to update existing repo
- **Token expiry**: Installation tokens are valid for 1 hour
- **Read-only operation**: Never modifies the repository content (only syncs)
- **Tech stack detection**: Pattern-based detection from root-level project files (requirements.txt, package.json, etc.)
- **Metrics exclude**: .git, node_modules, __pycache__, build artifacts
- **Large repositories**: Clone timeout is 5 minutes; may fail for very large repos

---

## Quick Reference

| Script | Purpose | Required Args |
|--------|---------|---------------|
| `generate_github_token.py` | Generate installation access token | `--installation-id`, `--output` |
| `sync_repository.py` | Sync repository (clone or pull) | `--repo-url`, `--access-token`, `--sync-path`, `--operation`, `--output` |
| `analyze_repository.py` | Analyze codebase metrics | `--repo-path`, `--output` |

**Optional Args:**
- `sync_repository.py`: `--branch` (specific branch)
- `analyze_repository.py`: `--instructions` (custom analysis instructions)

---

## Troubleshooting

**Token generation fails with 401:**
- Check `GITHUB_APP_ID` is correct
- Check `GITHUB_APP_PRIVATE_KEY` is valid PEM format
- Ensure private key matches the GitHub App

**Token generation fails with 404:**
- Check `installation_id` is correct
- Ensure GitHub App is installed for the target organization/repository

**Clone/Pull fails with 401/403:**
- Token may have expired (unlikely with fresh token)
- Repository may not be accessible by the GitHub App
- Check App permissions include "Contents: Read"

**Clone/Pull fails with 404:**
- Repository URL may be incorrect
- Repository may be deleted or renamed
- GitHub App may not have access to the repository

**Pull fails with conflicts:**
- Local changes may have been made to the repository
- May need to reset or stash local changes

**No tech stack detected:**
- Repository may use unconventional structure
- Check for project files in root directory
- Tech stack detection is best-effort, not exhaustive
