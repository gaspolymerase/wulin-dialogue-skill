#!/usr/bin/env bash
# Build wulin-dialogue.zip — the upload format for Claude Desktop / Claude.ai web.
# Output goes to ./dist/wulin-dialogue.zip.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$REPO_DIR/wulin-dialogue"
OUT_DIR="$REPO_DIR/dist"
OUT="$OUT_DIR/wulin-dialogue.zip"

if [ ! -d "$SRC" ]; then
  echo "error: $SRC not found" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"
rm -f "$OUT"

# Zip from REPO_DIR so the archive contains a top-level wulin-dialogue/ folder,
# which is what Claude Desktop / Claude.ai expects.
( cd "$REPO_DIR" && zip -qr "$OUT" wulin-dialogue \
    -x 'wulin-dialogue/.DS_Store' \
    -x 'wulin-dialogue/**/__pycache__/*' \
    -x 'wulin-dialogue/**/.DS_Store' )

echo "built: $OUT"
echo "size:  $(du -h "$OUT" | cut -f1)"
echo
echo "Upload via:  Claude Desktop / Claude.ai → Settings → Customize → Skills → '+'"
