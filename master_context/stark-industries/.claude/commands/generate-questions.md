---
name: generate-questions
description: Generate intelligent questions from organizational context to identify gaps and ambiguities
---

# Generate Questions from Context

You are about to analyze the entire organizational context repository and generate intelligent questions to identify knowledge gaps, ambiguities, contradictions, and undefined requirements.

## Arguments

This command receives two file path arguments:
- **First argument**: Path to manifest JSON file (contains organization info, context paths, team members)
- **Second argument**: Path to payload JSON file (contains job_id, question_types, focus_areas, constraints)

## Your Task

1. **Read the manifest and payload** from the file paths provided as arguments to this command

2. **Use the generate-questions skill** to:
   - Analyze entities directory for gaps and conflicts
   - Identify missing required fields, TBD values, and conflicts
   - Generate targeted questions with unique ref_ids

3. **MANDATORY: Write artifacts BEFORE returning JSON:**
   - Create directory: `artifacts/art_qa_tracker_{project_id}/questions/`
   - Write `type.meta.json` with artifact metadata
   - Write individual question YAMLs to `questions/{ref_id}.yaml`

4. **Return structured output** with `files_written` and `commit_message`

**DO NOT run git add, git commit, or git push.** The task runner handles all git operations.

## CRITICAL: Execution Order

**YOU MUST EXECUTE IN THIS ORDER:**
1. Generate questions (in memory)
2. **WRITE FILES TO DISK** using Write tool
3. Return JSON output with `files_written` and `commit_message`

**If you skip step 2, the skill has FAILED even if questions are generated.**

**DO NOT run git add, git commit, or git push.** The task runner handles all git operations.

## Structured Output

**Your final response MUST be valid JSON with this structure:**

```json
{
  "questions": [
    {
      "text": "Question text here",
      "question_type": "gap_analysis",
      "priority": "normal",
      "agent_sdk_ref_id": "qna_20251206_xxxxx",
      "context": {},
      "suggested_assignees": [],
      "min_responses": 1
    }
  ],
  "files_written": [
    "artifacts/art_qa_tracker_{project_id}/type.meta.json",
    "artifacts/art_qa_tracker_{project_id}/questions/qna_20251206_xxxxx.yaml"
  ],
  "commit_message": "qna: create question artifacts for project {project_id}",
  "metadata": {
    "job_id": "...",
    "generated_at": "...",
    "gaps_found": 0,
    "conflicts_found": 0,
    "questions_generated": 0,
    "focus_areas": [],
    "question_types": []
  }
}
```

**DO NOT:**
- Skip writing artifacts to disk (this is MANDATORY)
- Return JSON without first writing files
- Run git add, git commit, or git push (task runner handles this)
- Write to `questions_to_post.json` (deprecated)
- Make any HTTP requests or API calls
- POST to any Playbook endpoint

**The Agent SDK automatically extracts your structured output and POSTs to Playbook. The task runner handles git operations using `files_written` and `commit_message`.**

## Success Criteria

- Questions generated with valid JSON structure
- Each question has unique `agent_sdk_ref_id`
- QA tracker structure created at `artifacts/art_qa_tracker_{project_id}/`
- type.meta.json created with artifact metadata
- Individual question YAMLs written to `questions/` subdirectory
- `files_written` array returned with all created files
- `commit_message` returned for task runner
- Final response is valid structured output JSON
