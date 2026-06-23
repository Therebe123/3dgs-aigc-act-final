#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 /path/to/input_image" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MEMBER_B_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON="${PYTHON:-python}"

INPUT="$1"
OUT_DIR="$MEMBER_B_ROOT/assets/object_C"
mkdir -p "$OUT_DIR"
cp "$INPUT" "$OUT_DIR/input.png"
"$PYTHON" -m rembg i "$OUT_DIR/input.png" "$OUT_DIR/input_rgba.png"
echo "Saved: $OUT_DIR/input.png"
echo "Saved: $OUT_DIR/input_rgba.png"
