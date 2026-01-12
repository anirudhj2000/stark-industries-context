---
name: harvest-answers
description: Harvest a Q&A answer into an entity after summarize-answers has run - reads existing summary, updates entity field, tracks harvest via cursor
---

# Harvest Question Answers to Entity

You are about to harvest a question's summary and integrate the answer into the relevant entity.

## Arguments

This command receives two file path arguments:
- **First argument**: Path to manifest JSON file (contains organization info)
- **Second argument**: Path to payload JSON file (contains project_id, question_id, agent_sdk_ref_id)

**REQUIRED BACKGROUND:** You MUST run `summarize-answers` first. This command reads the existing summary.md - it does NOT create it.

## Your Task

1. **Read the manifest and payload** from the file paths provided as arguments

2. **Read the question artifact** from:
   ```
   artifacts/art_qa_tracker_{project_id}/questions/{agent_sdk_ref_id}.yaml
   ```

3. **Read the existing summary** from:
   ```
   artifacts/art_qa_tracker_{project_id}/summaries/{agent_sdk_ref_id}_summary.md
   ```

4. **Verify summary is current** - Check that `summary_cursor` covers all thread responses

5. **Use the harvest-answers skill** to:
   - Extract the answer from summary.md
   - Update the entity that had the gap (using source info from question artifact)
   - Update question YAML with `harvest_cursor`

6. **Return structured JSON** with `files_written` and `commit_message`

**DO NOT run git add, git commit, or git push.** The task runner handles all git operations.

## Critical Requirements

```
┌─────────────────────────────────────────────────────────────┐
│  THIS COMMAND READS SUMMARY - IT DOES NOT CREATE IT         │
│  If summary.md doesn't exist, FAIL and ask for summarize    │
└─────────────────────────────────────────────────────────────┘
```

**Required actions:**
- ✅ Read existing `summaries/{ref_id}_summary.md` (do NOT create)
- ✅ Use **Write tool** to update entity in `entities/{type}/{id}/context.yaml`
- ✅ Use **Write tool** to update `questions/{ref_id}.yaml` with harvest_cursor
- ✅ Return structured JSON with `files_written` and `commit_message`

**DO NOT run git add, git commit, or git push.** The task runner handles all git operations.

## Failure Conditions

- ❌ Summary.md not found → FAIL (run summarize-answers first)
- ❌ Summary is stale (new responses since last summary) → FAIL (run summarize-answers first)

## Success Criteria

- [ ] Summary.md read from `summaries/{ref_id}_summary.md`
- [ ] Entity updated with answer from summary
- [ ] Question YAML updated with `harvest_cursor`
- [ ] `files_written` array returned with all created files
- [ ] `commit_message` returned for task runner
- [ ] Valid JSON returned matching output schema
