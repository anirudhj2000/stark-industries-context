---
name: summarize-answers
description: Generate AI summary of question responses from QA tracker artifact, write summary.md to summaries/ directory. Supports both org and project contexts via context_type.
disable-model-invocation: true
---

# Summarize Question Answers

You are about to analyze responses to a question and generate a comprehensive summary.

## Arguments

This command receives two file path arguments:
- **First argument**: Path to manifest JSON file (contains organization info)
- **Second argument**: Path to payload JSON file (contains project_id, question_id, agent_sdk_ref_id, context_type)

## Your Task

1. **Read the manifest and payload** from the file paths provided as arguments

2. **Resolve artifact path from context_type** (CRITICAL - DO THIS FIRST):
   ```python
   context_type = payload.get("context_type", "org")
   project_id = payload.get("project_id")

   if context_type == "project" and project_id:
       artifact_dir = f"project_workspaces/project_{project_id}/artifacts/art_qa_tracker_{project_id}"
   else:
       artifact_dir = f"artifacts/art_qa_tracker_{project_id}"
   ```

3. **Read the question artifact** from:
   ```
   {artifact_dir}/questions/{agent_sdk_ref_id}.yaml
   ```

4. **Use the summarize-answers skill** to:
   - Extract thread[] responses from the question artifact
   - Analyze responses for key points, consensus, and conflicts
   - Generate structured summary

5. **MANDATORY: Write files using tools**
   - **Write** `{artifact_dir}/summaries/{agent_sdk_ref_id}_summary.md` using Write tool
   - **Update** `{artifact_dir}/questions/{agent_sdk_ref_id}.yaml` with summary_cursor using Write tool

6. **Return structured JSON** with `files_written` and `commit_message`

**DO NOT run git add, git commit, or git push.** The task runner handles all git operations.

## Critical Requirements

```
┌─────────────────────────────────────────────────────────────┐
│  YOU MUST WRITE FILES BEFORE RETURNING JSON                 │
│  Returning JSON without writing files = COMPLETE FAILURE    │
└─────────────────────────────────────────────────────────────┘
```

**Required tool usage:**
- ✅ Resolve `{artifact_dir}` from `context_type` FIRST
- ✅ Use **Write tool** to create `{artifact_dir}/summaries/{ref_id}_summary.md`
- ✅ Use **Write tool** to update `{artifact_dir}/questions/{ref_id}.yaml`
- ✅ Return structured JSON with `files_written` and `commit_message`

**DO NOT run git add, git commit, or git push.** The task runner handles all git operations.

## Success Criteria

- [ ] Artifact path resolved from context_type
- [ ] Question artifact read from `{artifact_dir}/questions/{ref_id}.yaml`
- [ ] Summary.md written to `{artifact_dir}/summaries/{ref_id}_summary.md`
- [ ] Question YAML updated with `summary_cursor`
- [ ] `files_written` array returned with all created files
- [ ] `commit_message` returned for task runner
- [ ] Valid JSON returned matching output schema
