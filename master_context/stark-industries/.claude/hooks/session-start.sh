#!/usr/bin/env bash
# SessionStart hook - minimal version (using-superpowers injection disabled)

set -euo pipefail

# Output empty context - no skill injection
cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": ""
  }
}
EOF

exit 0