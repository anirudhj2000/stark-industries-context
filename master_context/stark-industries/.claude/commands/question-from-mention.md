---
description: Help user create a tracked Q&A question for @-mentioned team members. Conversational - brainstorm and refine before creating.
---

# Question from Mention

**CRITICAL: DO NOT write YAML files. Use the Python script to create questions via Playbook API.**

Help the user formulate a question for the @-mentioned team members.

Read the skill for full instructions: `.claude/skills/question-from-mention/SKILL.md`

## Quick Reference

The prompt includes a `<question_context>` block with all required metadata:
- `organization_id`, `project_id`, `conversation_id` - for the script
- `mentioned_by_user_id` - the user who sent the message
- `tagged_users` - list of @-mentioned team members with IDs, names, expertise

## Workflow

1. Assess if the user's message contains a question or request
2. If not a question (thanks, FYI), acknowledge naturally
3. If it is a question, help refine it through conversation
4. When user confirms, create via script using values from `<question_context>`:

```bash
python3 .claude/skills/question-from-mention/scripts/create_question_from_chat.py \
  --organization-id "{organization_id from context}" \
  --project-id "{project_id from context}" \
  --assignee-ids "{user id from tagged_users}" \
  --question-text "the refined question" \
  --question-type "clarification" \
  --mentioned-by "{mentioned_by_user_id from context}" \
  --conversation-id "{conversation_id from context}"
```

**Important**: Use exact IDs from `<question_context>` - never hardcode or guess.
