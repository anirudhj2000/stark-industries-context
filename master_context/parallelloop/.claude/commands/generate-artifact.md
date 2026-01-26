---
name: generate-artifact
description: Generate documents and artifacts from conversation. Use when user says "create a doc", "save this", "make a PRD/TDD/FRD". Creates immediately without dialogue.
---

# Generate Artifact Command

Invokes the generate-artifact skill to create documents from conversation context.

## Usage

This command is triggered when users say things like:
- "create a PRD"
- "create a doc"
- "save this as meeting notes"
- "generate a TDD"

## Workflow

1. Read the skill at `.claude/skills/generate-artifact/SKILL.md`
2. Follow the skill instructions to:
   - Detect artifact type from user request and conversation context
   - Find and use template if available
   - Generate content from conversation
   - Write artifact to appropriate output path
3. Respond naturally describing what was created

## See Also

For dialogue-based document creation (asking questions first), use:
- `@prd` - PRD brainstorm with guided questions
- `@tdd` - TDD brainstorm with guided questions
- `@frd` - FRD brainstorm with guided questions
