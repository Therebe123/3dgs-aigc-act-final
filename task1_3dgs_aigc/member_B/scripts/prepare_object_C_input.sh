#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 /path/to/input_image" >&2
  exit 1
fi

ROOT="/pfs/siqingyi/code/token_credit"
INPUT="$1"
OUT_DIR="$ROOT/homework/member_B/assets/object_C"
mkdir -p "$OUT_DIR"
cp "$INPUT" "$OUT_DIR/input.png"
/opt/conda/envs/hw3_3d_train/bin/rembg i "$OUT_DIR/input.png" "$OUT_DIR/input_rgba.png"
echo "Saved: $OUT_DIR/input.png"
echo "Saved: $OUT_DIR/input_rgba.png"
