#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MEMBER_B_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$MEMBER_B_ROOT/../.." && pwd)"

THREESTUDIO="${THREESTUDIO:-$REPO_ROOT/external_repos/threestudio}"
LOG_DIR="${LOG_DIR:-$MEMBER_B_ROOT/logs}"
PYTHON="${PYTHON:-python}"
INPUT_IMAGE="${INPUT_IMAGE:-$MEMBER_B_ROOT/assets/object_C/input_rgba.png}"
EXP_ROOT="${EXP_ROOT:-$MEMBER_B_ROOT/results/object_C_zero123}"

if [[ ! -d "$THREESTUDIO" ]]; then
  echo "threestudio not found at $THREESTUDIO" >&2
  echo "Clone threestudio to external_repos/threestudio or set THREESTUDIO." >&2
  exit 1
fi

mkdir -p "$LOG_DIR" "$EXP_ROOT"
cd "$THREESTUDIO"

CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}" TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1 \
"$PYTHON" launch.py \
  --config configs/stable-zero123.yaml \
  --train \
  --gpu 0 \
  data.image_path="$INPUT_IMAGE" \
  name=object_C_guitar_stable_zero123 \
  exp_root_dir="$EXP_ROOT" \
  trainer.max_steps=600 \
  trainer.val_check_interval=100 \
  2>&1 | tee "$LOG_DIR/object_C_zero123_train.log"
