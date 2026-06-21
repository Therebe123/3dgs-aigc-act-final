#!/usr/bin/env bash
set -euo pipefail

ROOT="/pfs/siqingyi/code/token_credit"
THREESTUDIO="$ROOT/homework/member_B/repos/threestudio"
LOG_DIR="$ROOT/homework/member_B/logs"
MODEL_NAME="${MODEL_NAME:-Manojb/stable-diffusion-2-1-base}"

mkdir -p "$LOG_DIR"
cd "$THREESTUDIO"

CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-7}" \
/opt/conda/envs/hw3_3d_train/bin/python launch.py \
  --config configs/dreamfusion-sd.yaml \
  --train \
  --gpu 0 \
  system.prompt_processor.prompt="a single small blue and white porcelain vase, one smooth rounded body, one narrow circular opening, glossy ceramic surface, cobalt floral pattern, centered object, symmetrical, studio lighting, high quality 3D asset" \
  system.prompt_processor.negative_prompt="animal, face, ears, horns, legs, tail, handles, extra openings, duplicated parts, extra limbs, broken geometry, floating parts, blurry texture, noisy surface, low quality" \
  system.prompt_processor.pretrained_model_name_or_path="$MODEL_NAME" \
  system.guidance.pretrained_model_name_or_path="$MODEL_NAME" \
  name=object_B_porcelain_vase_sd21 \
  exp_root_dir="$ROOT/homework/member_B/results/object_B_threestudio" \
  trainer.max_steps=10000 \
  trainer.val_check_interval=200 \
  data.batch_size=1 \
  data.width=64 \
  data.height=64 \
  2>&1 | tee "$LOG_DIR/object_B_train_v3_vase_sd21.log"
