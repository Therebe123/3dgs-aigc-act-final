# 3DGS-AIGC-ACT Final Project

This repository contains the final project for Deep Learning and Spatial Intelligence.

The project includes two tasks:

- **Task 1:** Multi-source 3D asset generation and real-scene fusion based on 3DGS and AIGC.
- **Task 2:** Cross-environment generalization of ACT policies based on LeRobot.

## Repository Structure

```text
3dgs-aigc-act-final/
├── README.md
├── requirements.txt
├── environment.yml
├── task1_3dgs_aigc/
│   ├── README.md
│   ├── configs/
│   ├── data/
│   ├── scripts/
│   ├── assets/
│   ├── outputs/
│   └── docs/
├── task2_lerobot_act/
│   ├── README.md
│   ├── configs/
│   ├── data/
│   ├── scripts/
│   ├── checkpoints/
│   ├── outputs/
│   └── docs/
├── reports/
└── third_party/
```

## Environment Setup

The full environment will be finalized after implementation.

```bash
conda env create -f environment.yml
conda activate spatial-final
pip install -r requirements.txt
```

## Data Preparation

### Task 1

Prepare the following data:

- Multi-view images or video for object A.
- One input image for object C.
- One open-source background scene, such as a Mip-NeRF 360 scene.

Suggested local paths:

```text
task1_3dgs_aigc/data/object_a/
task1_3dgs_aigc/data/object_c/
task1_3dgs_aigc/data/background/
```

### Task 2

Use the provided CALVIN-LeRobot dataset:

https://huggingface.co/datasets/xiaoma26/calvin-lerobot/tree/main

Suggested local paths:

```text
task2_lerobot_act/data/splitA/
task2_lerobot_act/data/splitB/
task2_lerobot_act/data/splitC/
task2_lerobot_act/data/splitD/
```

## Train and Test Commands

Final commands will be updated after the codebase is completed.

### Task 1

```bash
# Reconstruct object A with 3DGS
bash task1_3dgs_aigc/scripts/train_object_a_3dgs.sh

# Reconstruct background scene with 3DGS
bash task1_3dgs_aigc/scripts/train_background_3dgs.sh

# Generate object B from text
bash task1_3dgs_aigc/scripts/generate_object_b_text_to_3d.sh

# Generate object C from a single image
bash task1_3dgs_aigc/scripts/generate_object_c_image_to_3d.sh

# Fuse assets and render video
bash task1_3dgs_aigc/scripts/render_fused_scene.sh
```

### Task 2

```bash
# Train ACT on environment A
bash task2_lerobot_act/scripts/train_act_splitA.sh

# Train ACT on environments A, B, and C
bash task2_lerobot_act/scripts/train_act_splitABC.sh

# Evaluate both models on unseen environment D
bash task2_lerobot_act/scripts/eval_act_splitD.sh
```

## Expected Deliverables

- Rendered images and video for Task 1.
- Training curves and evaluation metrics for Task 2.
- Model checkpoints or external download links.
- Final PDF report with method, results, analysis, repository link, and weight links.

