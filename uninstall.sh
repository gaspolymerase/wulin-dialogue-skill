#!/usr/bin/env bash
# Remove the wulin-dialogue skill from ~/.claude/skills/.
set -euo pipefail

DEST="${CLAUDE_HOME:-$HOME/.claude}/skills/wulin-dialogue"

if [ -L "$DEST" ] || [ -e "$DEST" ]; then
  rm -rf "$DEST"
  echo "removed: $DEST"
else
  echo "nothing to remove at $DEST"
fi
