# Task 2: LeRobot ACT Cross-Environment Generalization

Train and evaluate ACT policies on the CALVIN-LeRobot dataset to compare single-environment and multi-environment training under zero-shot generalization.

**Deliverables:** `member_C/`

## Dataset

- Hugging Face: https://huggingface.co/datasets/xiaoma26/calvin-lerobot/tree/main
- Mirror: https://hf-mirror.com/datasets/xiaoma26/calvin-lerobot/tree/main

| Split | Usage |
|---|---|
| splitA | Environment A, baseline training |
| splitB | Environment B, joint training |
| splitC | Environment C, joint training |
| splitD | Unseen environment D, zero-shot evaluation |

## Experiments

| Experiment | Training Data | Evaluation Data |
|---|---|---|
| ACT-A (baseline) | splitA | splitD |
| ACT-ABC (joint) | splitA + splitB + splitC | splitD |

## Results (full splitD)

| Model | splitD Action L1 ↓ | splitD Action MSE ↓ |
|---|---:|---:|
| ACT-A | 0.158918 | 0.090742 |
| ACT-ABC | 0.156221 | 0.090205 |

Details: `member_C/docs/final_full_results.md`, `member_C/artifacts/final_full_action_l1_compare.png`

## Model Weights

See [`docs/cloud_storage.md`](../docs/cloud_storage.md) and `member_C/docs/asset_manifest.csv`.

## Quick Start

```bash
cd task2_lerobot_act/member_C
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
export PYTHONPATH="$PWD/src"

bash task2_lerobot_act/scripts/download_data.sh
bash task2_lerobot_act/scripts/train_act.sh
bash task2_lerobot_act/scripts/eval_act.sh
```

Full documentation: `member_C/README.md`
