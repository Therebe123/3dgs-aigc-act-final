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

Current checked-in work focuses on **Task 1 / member B**: text-to-3D Object B, single-image-to-3D Object C, representation conversion, and Gaussian scene fusion.

## Environment

```bash
conda env create -f environment.yml
conda activate spatial-final
pip install -r requirements.txt
```

The final environment may be split by task if 3DGS, threestudio, Zero123, and LeRobot require incompatible dependencies. Member B's actual training was run on the server environment documented in `task1_3dgs_aigc/member_B/docs/runbook.md`:

- Python/conda env: `/opt/conda/envs/hw3_3d_train`
- External framework: `threestudio`
- Object B diffusion model: `Manojb/stable-diffusion-2-1-base`
- Object C checkpoint: `stabilityai/stable-zero123`
- Fusion preview tool: Blender `4.5.1 LTS`

## Data

### Task 1

Suggested local data layout:

```text
task1_3dgs_aigc/data/object_a/      # multi-view images or video
task1_3dgs_aigc/data/object_c/      # single input image
task1_3dgs_aigc/data/background/    # open-source background scene
```

Member B's prepared inputs, scripts, outputs, and method notes are under:

```text
task1_3dgs_aigc/member_B/
|-- scripts/       Runnable training, conversion, and fusion scripts.
|-- assets/        Lightweight preview inputs and images.
|-- outputs/       Compressed fused Gaussian scenes and preview figures.
`-- docs/          Runbook, method notes, manifests, and report text.
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

### Task 1 / Member B Train

```bash
bash task1_3dgs_aigc/scripts/generate_object_b_text_to_3d.sh
bash task1_3dgs_aigc/scripts/generate_object_c_image_to_3d.sh
```

### Task 1 / Member B Test And Fusion

```bash
bash task1_3dgs_aigc/scripts/render_fused_scene.sh
gzip -d -k task1_3dgs_aigc/member_B/outputs/renders/fused_scene_gaussian_clean_candidate_guitar_floor_v3.ply.gz
```

Open the decompressed `fused_scene_gaussian_clean_candidate_guitar_floor_v3.ply` in SuperSplat or another 3DGS-compatible viewer for visual inspection. See `task1_3dgs_aigc/member_B/outputs/README.md` and `task1_3dgs_aigc/member_B/docs/fusion_deliverables.md` for the final deliverable list.

Task 1 Object A and background reconstruction are provided by the teammate responsible for real 3DGS reconstruction; member B consumes their Gaussian PLY assets for fusion.

## Expected Outputs

- Task 1 / member B: generated B/C assets, Gaussian conversion scripts, final compressed fused scene, placement checks, rendered preview images, and method notes.
- Task 2: ACT checkpoints, training curves, zero-shot metrics on `splitD`, and comparison tables.
- Final report: method descriptions, visualizations, hyperparameters, metrics, GitHub link, and weight download links.
