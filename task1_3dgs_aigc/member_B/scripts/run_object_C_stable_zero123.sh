#!/usr/bin/env bash
set -euo pipefail

ROOT="/pfs/siqingyi/code/token_credit"
THREESTUDIO="$ROOT/homework/member_B/repos/threestudio"
LOG_DIR="$ROOT/homework/member_B/logs"
INPUT_IMAGE="$ROOT/homework/member_B/assets/object_C/input_rgba.png"
EXP_ROOT="$ROOT/homework/member_B/results/object_C_zero123"

mkdir -p "$LOG_DIR" "$EXP_ROOT"
cd "$THREESTUDIO"

CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-7}" TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1 /opt/conda/envs/hw3_3d_train/bin/python launch.py   --config configs/stable-zero123.yaml   --train   --gpu 0   data.image_path="$INPUT_IMAGE"   name=object_C_guitar_stable_zero123   exp_root_dir="$EXP_ROOT"   trainer.max_steps=600   trainer.val_check_interval=100   2>&1 | tee "$LOG_DIR/object_C_zero123_train.log"
