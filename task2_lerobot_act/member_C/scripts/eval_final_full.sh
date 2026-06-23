#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD/src"

CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-5}" .venv/bin/python eval_action_error.py \
  --checkpoint outputs/final_act_splitA_full/checkpoints/best.pt \
  --data-root data/calvin_lerobot \
  --splits splitD \
  --output outputs/final_act_splitA_full/eval_splitD.json \
  --batch-size 8 \
  --num-workers 2 \
  --device cuda

CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-5}" .venv/bin/python eval_action_error.py \
  --checkpoint outputs/final_act_jointABC_full/checkpoints/best.pt \
  --data-root data/calvin_lerobot \
  --splits splitD \
  --output outputs/final_act_jointABC_full/eval_splitD.json \
  --batch-size 8 \
  --num-workers 2 \
  --device cuda

.venv/bin/python plot_metrics.py --metrics outputs/final_act_splitA_full/train_metrics.csv --output outputs/final_act_splitA_full/loss_curve.png
.venv/bin/python plot_metrics.py --metrics outputs/final_act_jointABC_full/train_metrics.csv --output outputs/final_act_jointABC_full/loss_curve.png
