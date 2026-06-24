# 3DGS-AIGC-ACT Final Project

**Deep Learning and Spatial Intelligence** — 期末小组项目。

| 链接 | URL |
|---|---|
| GitHub | https://github.com/Therebe123/3dgs-aigc-act-final |
| Google Drive | https://drive.google.com/drive/folders/1zq4sE9CjMhWjk5RhR1OpKe3YlPzJxqpP?usp=drive_link |

## 组员分工

| 组员 | 姓名 | 学号 | 职责 | 目录 |
|:---:|---|---:|---|---|
| A | 邓捷比 | 25210980029 | 题目一真实重建 | [`task1_3dgs_aigc/member_A/`](task1_3dgs_aigc/member_A/README.md) |
| B | 谢佳杭 | 25210980118 | 题目一 AIGC 与融合 | [`task1_3dgs_aigc/member_B/`](task1_3dgs_aigc/member_B/README.md) |
| C | 李浩然 | 25210980063 | 题目二 ACT 实验 | [`task2_lerobot_act/member_C/`](task2_lerobot_act/member_C/README.md) |

实验报告：[`reports/final_report.pdf`](reports/final_report.pdf)。

## 快速开始

```bash
git clone https://github.com/Therebe123/3dgs-aigc-act-final.git
cd 3dgs-aigc-act-final
```

1. 从 [Google Drive](https://drive.google.com/drive/folders/1zq4sE9CjMhWjk5RhR1OpKe3YlPzJxqpP?usp=drive_link) 下载大文件（`题目一`：PLY/checkpoint；`题目二`：ACT 权重）。
2. 按任务进入对应 member 目录配置环境（见下方「环境说明」）。
3. 题目一：[`task1_3dgs_aigc/README.md`](task1_3dgs_aigc/README.md)；题目二：[`task2_lerobot_act/README.md`](task2_lerobot_act/README.md)。

## 仓库结构

```text
.
├── task1_3dgs_aigc/
│   ├── member_A/          # 真实重建
│   ├── member_B/          # AIGC 与融合
│   └── scripts/
├── task2_lerobot_act/
│   ├── member_C/          # ACT 实验
│   └── scripts/
├── reports/
└── external_repos/        # threestudio 等第三方源码
```

Member A 训练脚本默认将 checkpoint 写入仓库根目录 `outputs/`。

## 复现命令

### 题目一 / Member A

```bash
task1_3dgs_aigc/member_A/scripts/train_object_A_splatfacto_windows.bat   # Windows
bash task1_3dgs_aigc/member_A/scripts/train_object_A_splatfacto_linux.sh
bash task1_3dgs_aigc/member_A/scripts/train_background_counter_splatfacto_linux.sh
```

Runbook：[`member_A/docs/runbook.md`](task1_3dgs_aigc/member_A/docs/runbook.md)

### 题目一 / Member B

```bash
bash task1_3dgs_aigc/scripts/generate_object_b_text_to_3d.sh
bash task1_3dgs_aigc/scripts/generate_object_c_image_to_3d.sh
bash task1_3dgs_aigc/scripts/render_fused_scene.sh
```

融合交付：[`member_B/docs/fusion_deliverables.md`](task1_3dgs_aigc/member_B/docs/fusion_deliverables.md)

```bash
gzip -d -k task1_3dgs_aigc/member_B/outputs/renders/fused_scene_gaussian_clean_candidate_guitar_floor_v3.ply.gz
```

### 题目二 / Member C

```bash
bash task2_lerobot_act/scripts/download_data.sh
bash task2_lerobot_act/scripts/train_act.sh
bash task2_lerobot_act/scripts/eval_act.sh
```

评估前从 Drive `题目二` 下载权重至 `task2_lerobot_act/member_C/weights/`。详见 [`member_C/README.md`](task2_lerobot_act/member_C/README.md)。

## 环境说明

| 组员 | 环境 | 文档 |
|---|---|---|
| A | `nerfstudio_gs` | [`member_A/docs/environment.md`](task1_3dgs_aigc/member_A/docs/environment.md) |
| B | `hw3_3d_train` + threestudio | [`member_B/docs/runbook.md`](task1_3dgs_aigc/member_B/docs/runbook.md) |
| C | venv / conda | [`member_C/README.md`](task2_lerobot_act/member_C/README.md) |
