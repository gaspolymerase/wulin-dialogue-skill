#!/usr/bin/env bash
# Install the wulin-dialogue skill into ~/.claude/skills/.
# Creates a symlink so edits in this repo are immediately picked up.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$REPO_DIR/wulin-dialogue"
DEST_DIR="${CLAUDE_HOME:-$HOME/.claude}/skills"
DEST="$DEST_DIR/wulin-dialogue"

if [ ! -d "$SRC" ]; then
  echo "error: $SRC not found" >&2
  exit 1
fi

mkdir -p "$DEST_DIR"

if [ -L "$DEST" ] || [ -e "$DEST" ]; then
  echo "removing existing $DEST"
  rm -rf "$DEST"
fi

ln -s "$SRC" "$DEST"
echo "installed: $DEST -> $SRC"
echo
echo "Try it in Claude Code with:  /wulin-dialogue"
echo "Or just say:                  '我想和佟湘玉聊天' / 'let's play 对台词'"
