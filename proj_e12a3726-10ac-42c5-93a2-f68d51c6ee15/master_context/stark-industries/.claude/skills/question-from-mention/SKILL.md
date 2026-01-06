---
name: question-from-mention
description: Use when team members are @-mentioned in chat. Help user brainstorm and refine questions, then create tracked Q&A questions when confirmed. Conversational multi-turn skill.
---

# Question from Mention Skill

## STOP - READ THIS FIRST

**After creating questions, your ONLY output should be ONE sentence like:**
- "Done! Created 3 questions for John."
- "Questions sent to pl@pl.ai!"

**FORBIDDEN outputs after question creation:**
- ❌ Tables listing questions
- ❌ Question IDs (UUIDs)
- ❌ Question text/content
- ❌ Status, type, assignee details
- ❌ Markdown formatting of results

The UI automatically shows artifact cards. Any verbose output from you is redundant and clutters the chat.

---

## CRITICAL: This Skill is DIFFERENT from Other Q&A Skills

**DO NOT write YAML files.** This skill creates questions via Playbook API, NOT by writing files to `art_qa_tracker_*` directories.

- **DO NOT** use `Write` tool to create question files
- **DO NOT** write to `artifacts/art_qa_tracker_*/questions/`
- **DO NOT** commit question YAML files
- **MUST** use the Python script `create_question_from_chat.py` which calls Playbook API

If you write a YAML file instead of calling the script, the question will NOT be tracked in Playbook and the user will NOT be notified.

---

Help users formulate questions when they @-mention team members. This is a **conversational** skill - engage in dialogue to understand intent before creating questions.

## When This Triggers

You'll receive a `<question_context>` block in the prompt with all the metadata you need:

```yaml
<question_context>
organization_id: org_abc123
project_id: proj_xyz789
conversation_id: conv_12345
mentioned_by_user_id: user_sender456

tagged_users:
  - name: John Doe
    id: user_john123
    email: john@example.com
    function: Engineering
    expertise: authentication, security
</question_context>
```

Use these values when calling the script (don't hardcode or guess - use exactly what's provided).

## Your Approach

### 1. Assess Intent

**If NOT a question** (thanks, FYI, acknowledgment):
- Respond naturally: "Got it, I'll note that for John."
- Don't offer to create a question

**If it IS or MIGHT BE a question**:
- First try to answer it yourself from the context repository
- Then offer to create a tracked question for clarifications

### 2. Answer First, Then Clarify

**IMPORTANT**: Don't immediately ask 4 follow-up questions. Instead:

1. **Search the repository** for relevant information (entities, sources, artifacts)
2. **Provide what you know** from the repo
3. **Then offer** to ask the tagged person for what's missing or unclear

Example flow:

```
User: "@john.doe how does our auth flow work?"

You: "Based on the repository, here's what I found about auth:

[Summary of auth-related information from entities/sources]
- OAuth providers configured: Google, GitHub
- Token refresh happens via /api/auth/refresh
- Session timeout is 24 hours

If you need John to clarify something specific - like the recent OAuth
library change or the redirect handling - I can create a tracked question
for him. What would you like to ask?"

User: "Yes, ask about the redirect issue"

You: "Got it. I'll create this question for John:

> 'The OAuth redirect is failing after we switched libraries. Can you
investigate the callback handling?'

Ready to send this to John?"
```

### 3. When You Don't Have Information

If the repo doesn't have relevant info, be honest:

```
User: "@john.doe why did we choose Postgres over MongoDB?"

You: "I don't see documentation about that decision in the repository.
Would you like me to ask John directly? I can create a question like:

> 'What was the reasoning behind choosing Postgres over MongoDB for our
database?'

Should I create this for John?"
```

### 4. Create the Question

When user confirms, invoke the script using values from `<question_context>`:

```bash
python3 .claude/skills/question-from-mention/scripts/create_question_from_chat.py \
  --organization-id "org_abc123" \
  --project-id "proj_xyz789" \
  --assignee-ids "user_john123" \
  --question-text "The refined question text" \
  --question-type "clarification" \
  --mentioned-by "user_sender456" \
  --conversation-id "conv_12345"
```

**Important**: Use the exact IDs from `<question_context>` - don't hardcode or guess values.

**After script succeeds**: Say ONE sentence only (e.g., "Done! Question sent to John."). See "STOP - READ THIS FIRST" section at top of this skill.

### 5. Continue Naturally

After creating a question, stay in conversation. User might:
- Ask to also create a question for another person
- Move on to a different topic
- Ask follow-up questions

## Multiple Tagged Users

When multiple people are tagged:
- Help determine who's best suited for the question
- Consider their `expertise_tags` and `function`
- Can create one question with multiple assignees (comma-separated IDs)
- Or suggest separate questions for different aspects

## Response Style

- **Short**: 2-4 sentences typical
- **Use names**: "John" not "user-uuid-123"
- **Quote drafts**: So user sees exactly what will be created
- **Be helpful, not pushy**: If they don't want a question, that's fine

## Script Output

The script returns JSON:
```json
{"success": true, "question_id": "q-123", "assignees": ["John Doe"]}
```

If it fails:
```json
{"success": false, "error": "Error message"}
```

Handle errors naturally: "I ran into an issue creating that - [error]. Want me to try again?"

## Common Mistakes

**Don't:**
- Create questions without user confirmation
- Assume every @-mention needs a question
- Expose UUIDs to the user
- End conversation artificially

**Do:**
- Understand the problem first
- Help pick the right assignee
- Let user refine wording
- Confirm before creating
