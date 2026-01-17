---
name: extract-meeting-actions
description: Extract actionable items from meeting transcripts and create action list entries
---

# Extract Actions from Meeting Transcripts

You are about to analyze meeting transcripts or source documents and extract actionable items that can be assigned to team members.

## Arguments

This command receives two file path arguments:
- **First argument**: Path to manifest JSON file (contains organization info, context paths, team members)
- **Second argument**: Path to payload JSON file (contains source_id, meeting_context, participants)

## Your Task

1. **Read the manifest and payload** from the file paths provided as arguments to this command

2. **Read the source content** from the structured.json or structured.md files in the source directory

3. **Extract actionable items** by:
   - Identifying explicit action items ("John will review...", "Action: Complete...")
   - Detecting implicit commitments ("I'll handle that", "Let me follow up")
   - Recognizing deadlines and priorities mentioned
   - Mapping actions to participants/assignees when possible

4. **MANDATORY: Write artifacts BEFORE returning JSON:**
   - Create directory: `artifacts/art_action_list_{project_id}/actions/`
   - Write `type.meta.json` with artifact metadata
   - Write individual action YAMLs to `actions/{ref_id}.yaml`

5. **Return structured output** with `files_written` and `commit_message`

**DO NOT run git add, git commit, or git push.** The task runner handles all git operations.

## CRITICAL: Execution Order

**YOU MUST EXECUTE IN THIS ORDER:**
1. Read source content
2. Extract actions (in memory)
3. **WRITE FILES TO DISK** using Write tool
4. Return JSON output with `files_written` and `commit_message`

**If you skip step 3, the skill has FAILED even if actions are extracted.**

**DO NOT run git add, git commit, or git push.** The task runner handles all git operations.

## Action YAML Structure

Each action file should follow this structure:

```yaml
action_id: act_YYYYMMDD_xxxxx
title: "Short action title"
text: "Full action description"
priority: normal  # urgent, high, normal, low
status: assigned
source_reference:
  source_id: src_xxx
  excerpt: "Relevant quote from meeting"
  timestamp: "00:15:30"  # if available
suggested_assignees:
  - email: john@example.com
    reason: "Mentioned by name"
deadline: "2025-01-15"  # if mentioned
context:
  meeting_date: "2025-01-08"
  meeting_title: "Weekly Standup"
is_actionable_by_ai: false
ai_execution_config: null
created_at: ISO8601
```

## Structured Output

**Your final response MUST be valid JSON with this structure:**

```json
{
  "actions": [
    {
      "title": "Review Q4 budget",
      "text": "John needs to review the Q4 budget and provide feedback by Friday",
      "question_type": "action_item",
      "priority": "high",
      "agent_sdk_ref_id": "act_20251206_xxxxx",
      "context": {
        "source_excerpt": "John, can you review the Q4 budget?",
        "deadline_mentioned": "Friday"
      },
      "suggested_assignees": ["john@example.com"],
      "is_actionable_by_ai": false
    }
  ],
  "files_written": [
    "artifacts/art_action_list_{project_id}/type.meta.json",
    "artifacts/art_action_list_{project_id}/actions/act_20251206_xxxxx.yaml"
  ],
  "commit_message": "actions: extract meeting actions from source {source_id}",
  "metadata": {
    "job_id": "...",
    "source_id": "...",
    "generated_at": "...",
    "actions_extracted": 5,
    "with_assignees": 3,
    "with_deadlines": 2,
    "ai_actionable": 0
  }
}
```

## Action Type Classification

Classify extracted actions into these types (stored in question_type field):
- **action_item**: Explicit task to complete
- **follow_up**: Follow-up conversation or check-in needed
- **decision**: Decision to be made
- **review**: Document or artifact to review
- **research**: Investigation or research needed

## Priority Detection

Detect priority from context:
- **urgent**: "ASAP", "immediately", "critical", "blocking"
- **high**: "important", "priority", "by tomorrow", "this week"
- **normal**: Default for most actions
- **low**: "when you have time", "nice to have", "eventually"

## AI-Actionable Actions

Some actions can be flagged for AI execution:
- Research tasks that can be automated
- Document generation tasks
- Data gathering tasks

For these, set:
```json
{
  "is_actionable_by_ai": true,
  "ai_execution_config": {
    "skill_name": "research-topic",
    "params": { "topic": "..." },
    "constraints": { "max_sources": 5 }
  }
}
```

## DO NOT:
- Skip writing artifacts to disk (this is MANDATORY)
- Return JSON without first writing files
- Run git add, git commit, or git push (task runner handles this)
- Make any HTTP requests or API calls
- POST to any Playbook endpoint
- Invent actions not present in the source content
- Assign actions without evidence from the transcript

**The Agent SDK automatically extracts your structured output and POSTs to Playbook. The task runner handles git operations using `files_written` and `commit_message`.**

## Success Criteria

- Actions extracted with valid JSON structure
- Each action has unique `agent_sdk_ref_id` (format: act_YYYYMMDD_xxxxx)
- Action list structure created at `artifacts/art_action_list_{project_id}/`
- type.meta.json created with artifact metadata
- Individual action YAMLs written to `actions/` subdirectory
- `files_written` array returned with all created files
- `commit_message` returned for task runner
- Final response is valid structured output JSON
