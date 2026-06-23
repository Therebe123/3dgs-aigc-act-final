#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MEMBER_B_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$MEMBER_B_ROOT/../.." && pwd)"

THREESTUDIO="${THREESTUDIO:-$REPO_ROOT/external_repos/threestudio}"
LOG_DIR="${LOG_DIR:-$MEMBER_B_ROOT/logs}"
PYTHON="${PYTHON:-python}"
MODEL_NAME="${MODEL_NAME:-Manojb/stable-diffusion-2-1-base}"

if [[ ! -d "$THREESTUDIO" ]]; then
  echo "threestudio not found at $THREESTUDIO" >&2
  echo "Clone threestudio to external_repos/threestudio or set THREESTUDIO." >&2
  exit 1
fi

mkdir -p "$LOG_DIR" "$MEMBER_B_ROOT/results/object_B_threestudio"
cd "$THREESTUDIO"

CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}" \
"$PYTHON" launch.py \
  --config configs/dreamfusion-sd.yaml \
  --train \
  --gpu 0 \
  system.prompt_processor.prompt="a single small blue and white porcelain vase, one smooth rounded body, one narrow circular opening, glossy ceramic surface, cobalt floral pattern, centered object, symmetrical, studio lighting, high quality 3D asset" \
  system.prompt_processor.negative_prompt="animal, face, ears, horns, legs, tail, handles, extra openings, duplicated parts, extra limbs, broken geometry, floating parts, blurry texture, noisy surface, low quality" \
  system.prompt_processor.pretrained_model_name_or_path="$MODEL_NAME" \
  system.guidance.pretrained_model_name_or_path="$MODEL_NAME" \
  name=object_B_porcelain_vase_sd21 \
  exp_root_dir="$MEMBER_B_ROOT/results/object_B_threestudio" \
  trainer.max_steps=10000 \
  trainer.val_check_interval=200 \
  data.batch_size=1 \
  data.width=64 \
  data.height=64 \
  2>&1 | tee "$LOG_DIR/object_B_train_v3_vase_sd21.log"
