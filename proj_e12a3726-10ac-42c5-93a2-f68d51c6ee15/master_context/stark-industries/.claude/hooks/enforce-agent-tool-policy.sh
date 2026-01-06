#!/bin/bash
# enforce-agent-tool-policy.sh
#
# Validates tool calls against agent-specific tool policies
# Called by PreToolUse hook before ANY tool execution
#
# Input: JSON via stdin with tool information
# Output: Exit 0 (allow) or Exit 2 (block)

set -euo pipefail

# Read input from stdin
INPUT=$(cat)

# DEBUG: Log what we're receiving
echo "[DEBUG] Hook input: $INPUT" >> /tmp/enforce-agent-tool-policy.log 2>&1

# Extract agent name and tool name from input
AGENT_NAME=$(echo "$INPUT" | jq -r '.agent_name // "unknown"' 2>/dev/null || echo "unknown")
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null || echo "")

# DEBUG: Log extracted values
echo "[DEBUG] Agent: $AGENT_NAME, Tool: $TOOL_NAME" >> /tmp/enforce-agent-tool-policy.log 2>&1

# Handle MCP-namespaced tools (e.g., mcp__ide__executeCode)
TOOL_NAME=$(echo "$TOOL_NAME" | sed 's/^[a-z_]*__//')

if [[ -z "$TOOL_NAME" ]]; then
  # No tool name provided, allow to continue
  exit 0
fi

# Resolve policy file location relative to this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
POLICY_FILE="$SCRIPT_DIR/../config/tool-policies.json"

# Check if policy file exists
if [[ ! -f "$POLICY_FILE" ]]; then
  # No policy file found, allow tool usage (graceful degradation)
  exit 0
fi

# Get blocked tools for this agent from the policy file
BLOCKED_TOOLS=$(jq -r ".agents[\"$AGENT_NAME\"].blocked_tools[]? // empty" "$POLICY_FILE" 2>/dev/null || echo "")

# Check if current tool is in the blocked list
while IFS= read -r blocked_tool; do
  [[ -z "$blocked_tool" ]] && continue

  if [[ "$TOOL_NAME" == "$blocked_tool" ]]; then
    # Tool is blocked for this agent
    ALLOWED_TOOLS=$(jq -r ".agents[\"$AGENT_NAME\"].allowed_tools[]?" "$POLICY_FILE" 2>/dev/null | paste -sd ',' - || echo "none")
    RATIONALE=$(jq -r ".agents[\"$AGENT_NAME\"].rationale[]?" "$POLICY_FILE" 2>/dev/null | sed 's/^/  • /' || echo "  • Policy enforcement")

    cat >&2 <<EOF
╭─────────────────────────────────────────────────────────────────╮
│ ❌ TOOL BLOCKED BY AGENT POLICY                                 │
├─────────────────────────────────────────────────────────────────┤
│ Agent:       $AGENT_NAME
│ Tool:        $TOOL_NAME
│ Status:      DENIED
├─────────────────────────────────────────────────────────────────┤
│ Allowed tools for this agent:
│   $ALLOWED_TOOLS
├─────────────────────────────────────────────────────────────────┤
│ Why this tool is blocked:
$RATIONALE
├─────────────────────────────────────────────────────────────────┤
│ Policy:      .claude/config/tool-policies.json
│ Enforced by: .claude/hooks/enforce-agent-tool-policy.sh
╰─────────────────────────────────────────────────────────────────╯
EOF
    exit 2  # Exit code 2 = block the tool call
  fi
done <<< "$BLOCKED_TOOLS"

# Tool is allowed, proceed with execution
echo "[DEBUG] Tool $TOOL_NAME allowed for agent $AGENT_NAME" >> /tmp/enforce-agent-tool-policy.log 2>&1
exit 0
