#!/bin/bash
# PreToolUse hook: BLOCKS creation of subdirectories in entities/organization/
# Exit code 0 = allow, Exit code 2 = block with message

# The tool input is passed via stdin as JSON
INPUT=$(cat)

# Extract the file_path or command from the input
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)

# Check Write tool - block if writing to entities/organization/*/
if [ -n "$FILE_PATH" ]; then
  if echo "$FILE_PATH" | grep -qE 'entities/organization/[^/]+/'; then
    echo "❌ BLOCKED: Cannot create files in subdirectories of entities/organization/"
    echo "   Attempted path: $FILE_PATH"
    echo ""
    echo "   → Store previous employers in: person.background.previous_companies"
    echo "   → Store competitors in: entities/competitor/{id}/context.yaml"
    exit 2
  fi
fi

# Check Bash tool - block mkdir in entities/organization/
if [ -n "$COMMAND" ]; then
  if echo "$COMMAND" | grep -qE 'mkdir.*entities/organization/[^/]+'; then
    echo "❌ BLOCKED: Cannot create subdirectories in entities/organization/"
    echo "   Attempted command: $COMMAND"
    echo ""
    echo "   → Store previous employers in: person.background.previous_companies"
    echo "   → Store competitors in: entities/competitor/{id}/context.yaml"
    exit 2
  fi
fi

# Allow the operation
exit 0
