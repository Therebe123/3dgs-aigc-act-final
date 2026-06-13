# Task 2: LeRobot ACT Cross-Environment Generalization

## Goal

Train and evaluate ACT policies on the CALVIN-LeRobot dataset to compare single-environment training and multi-environment training under zero-shot generalization.

## Dataset

Dataset: https://huggingface.co/datasets/xiaoma26/calvin-lerobot/tree/main

| Split | Usage |
|---|---|
| splitA | Environment A, baseline training |
| splitB | Environment B, joint training |
| splitC | Environment C, joint training |
| splitD | Unseen environment D, zero-shot evaluation |

## Experiments

| Experiment | Training Data | Evaluation Data |
|---|---|---|
| Baseline ACT | splitA | splitD |
| Joint ACT | splitA + splitB + splitC | splitD |

## Directory Usage

```text
configs/      ACT training and evaluation configs.
data/         Local dataset links or preparation notes.
scripts/      Runnable train and test scripts.
checkpoints/  Local model checkpoints or checkpoint notes.
outputs/      Logs, curves, metrics, and evaluation results.
docs/         Experiment notes and analysis drafts.
```

## Key Results to Record

- Action L1 Loss curves.
- Validation metrics if available.
- Success Rate or action error on splitD.
- Comparison between baseline and joint training.
- Analysis of Action Chunking under visual distribution shift.

