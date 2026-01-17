---
name: complete-action
description: Mark an action as completed and update its status in the action tracker
---

# Complete Action

You are about to mark an action as completed and update its status in the action tracker artifact.

## Arguments

This command receives two file path arguments:
- **First argument**: Path to manifest JSON file (contains organization info, context paths)
- **Second argument**: Path to payload JSON file (contains action_id, completion_notes, effort_hours)

## Payload Structure

```json
{
  "action_id": "act_20251206_xxxxx",
  "agent_sdk_ref_id": "act_20251206_xxxxx",
  "project_id": "proj_xxx",
  "completion_notes": "Completed the budget review with stakeholder approval",
  "effort_hours": 4.5,
  "resolution_type": "completed",
  "deliverables": [
    {
      "type": "artifact",
      "artifact_id": "art_xxx",
      "description": "Budget review document"
    }
  ]
}
```

## Your Task

1. **Read the manifest and payload** from the file paths provided as arguments

2. **Locate the action YAML file** at:
   `artifacts/art_action_list_{project_id}/actions/{agent_sdk_ref_id}.yaml`

3. **Update the action status**:
   - Set `status: completed`
   - Add `completed_at: {current_timestamp}`
   - Add `completion_notes` from payload
   - Add `actual_effort_hours` from payload
   - Link any deliverables

4. **MANDATORY: Write updated YAML:**
   - Update the action YAML file using Write tool

5. **Return structured output** with `files_written` and `commit_message`

**DO NOT run git add, git commit, or git push.** The task runner handles all git operations.

## Updated Action YAML Structure

```yaml
action_id: act_YYYYMMDD_xxxxx
title: "Short action title"
text: "Full action description"
priority: normal
status: completed  # Updated
completed_at: "2025-01-08T16:30:00Z"  # Added
completion_notes: "Completed with stakeholder approval"  # Added
actual_effort_hours: 4.5  # Added
deliverables:  # Added
  - type: artifact
    artifact_id: art_xxx
    description: "Budget review document"
source_reference:
  source_id: src_xxx
  excerpt: "Relevant quote"
suggested_assignees:
  - email: john@example.com
context:
  meeting_date: "2025-01-08"
created_at: ISO8601
```

## Structured Output

**Your final response MUST be valid JSON with this structure:**

```json
{
  "status": "success",
  "action_id": "act_20251206_xxxxx",
  "agent_sdk_ref_id": "act_20251206_xxxxx",
  "resolution_type": "completed",
  "completed_at": "2025-01-08T16:30:00Z",
  "effort_hours": 4.5,
  "deliverables_linked": 1,
  "files_written": [
    "artifacts/art_action_list_xxx/actions/act_20251206_xxxxx.yaml"
  ],
  "commit_message": "actions: complete action act_20251206_xxxxx"
}
```

## Resolution Types

Valid resolution types map to Question model status choices:
- **completed**: Action finished successfully (status: `completed`)
- **cancelled**: Action cancelled, no longer needed (status: `cancelled`)
- **blocked**: Action blocked by another action (status: `blocked`)
- **archived**: Action archived without completion (status: `archived`)

## CRITICAL: Execution Order

**YOU MUST EXECUTE IN THIS ORDER:**
1. Read manifest and payload
2. Read existing action YAML
3. Update action data (in memory)
4. **WRITE UPDATED YAML TO DISK** using Write tool
5. Return JSON output with `files_written` and `commit_message`

**If you skip step 4, the skill has FAILED.**

**DO NOT run git add, git commit, or git push.** The task runner handles all git operations.

## Error Handling

If action YAML not found:
```json
{
  "status": "error",
  "error_type": "action_not_found",
  "message": "Action YAML not found at expected path",
  "searched_path": "artifacts/art_action_list_xxx/actions/act_xxx.yaml"
}
```

If action already completed:
```json
{
  "status": "error",
  "error_type": "already_completed",
  "message": "Action was already completed",
  "completed_at": "2025-01-07T10:00:00Z"
}
```

## DO NOT:
- Skip updating the YAML file on disk
- Run git add, git commit, or git push (task runner handles this)
- Complete an action without verifying it exists
- Make HTTP requests or API calls
- Modify other action files

**The Agent SDK automatically extracts your structured output and sends webhook to Playbook. The task runner handles git operations using `files_written` and `commit_message`.**

## Success Criteria

- Action YAML found and updated
- Status changed to completed/cancelled/blocked/archived
- Completion metadata added
- `files_written` array returned with updated file
- `commit_message` returned for task runner
- Valid JSON output returned
