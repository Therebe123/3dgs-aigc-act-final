#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD/src"
CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-5}" .venv/bin/python train_act.py --config configs/final_splitA_full.yaml
CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-5}" .venv/bin/python train_act.py --config configs/final_jointABC_full.yaml
