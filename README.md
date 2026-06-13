# 3DGS-AIGC-ACT Final Project

Final project for **Deep Learning and Spatial Intelligence**.

This repository contains two tasks:

- **Task 1:** 3DGS and AIGC based 3D asset generation, reconstruction, fusion, and rendering.
- **Task 2:** LeRobot ACT policy training and zero-shot cross-environment evaluation.

## Main Folders

```text
.
|-- README.md              Project overview and runnable entry points.
|-- requirements.txt       Python package requirements.
|-- environment.yml        Conda environment template.
|-- task1_3dgs_aigc/       Task 1: 3DGS reconstruction, AIGC assets, and scene fusion.
|-- task2_lerobot_act/     Task 2: LeRobot ACT training and evaluation.
|-- reports/               Final report materials and exported figures.
`-- external_repos/        Optional external source repositories, such as 3DGS or LeRobot.
```

Large datasets, checkpoints, rendered videos, and logs should not be committed directly. Put download links or preparation notes in the corresponding task folder.

## Environment

```bash
conda env create -f environment.yml
conda activate spatial-final
pip install -r requirements.txt
```

The final environment may be split by task if 3DGS, threestudio, Zero123, and LeRobot require incompatible dependencies.

## Data

### Task 1

Suggested local data layout:

```text
task1_3dgs_aigc/data/object_a/      # multi-view images or video
task1_3dgs_aigc/data/object_c/      # single input image
task1_3dgs_aigc/data/background/    # open-source background scene
```

### Task 2

Use the provided CALVIN-LeRobot dataset:

https://huggingface.co/datasets/xiaoma26/calvin-lerobot/tree/main

Suggested local data layout:

```text
task2_lerobot_act/data/splitA/
task2_lerobot_act/data/splitB/
task2_lerobot_act/data/splitC/
task2_lerobot_act/data/splitD/
```

## Commands

These commands are placeholders and should be replaced by the final runnable scripts.

### Task 1

```bash
bash task1_3dgs_aigc/scripts/train_object_a_3dgs.sh
bash task1_3dgs_aigc/scripts/train_background_3dgs.sh
bash task1_3dgs_aigc/scripts/generate_object_b_text_to_3d.sh
bash task1_3dgs_aigc/scripts/generate_object_c_image_to_3d.sh
bash task1_3dgs_aigc/scripts/render_fused_scene.sh
```

### Task 2

```bash
bash task2_lerobot_act/scripts/train_act_splitA.sh
bash task2_lerobot_act/scripts/train_act_splitABC.sh
bash task2_lerobot_act/scripts/eval_act_splitD.sh
```

## Expected Outputs

- Task 1: reconstructed/generated 3D assets, fused scene, rendered images, and demo video.
- Task 2: ACT checkpoints, training curves, zero-shot metrics on `splitD`, and comparison tables.
- Final report: method descriptions, visualizations, hyperparameters, metrics, GitHub link, and weight download links.
