# Cloud Storage

Large files are hosted on Google Drive (not in Git).

**Drive:** [3DGS_AIGC_ACT](https://drive.google.com/drive/folders/1zq4sE9CjMhWjk5RhR1OpKe3YlPzJxqpP?usp=drive_link)

**GitHub:** https://github.com/Therebe123/3dgs-aigc-act-final

| Drive 文件夹 | 内容 |
|---|---|
| `题目一` | 3DGS 资产、COLMAP、checkpoint、融合用 PLY |
| `题目二` | ACT 权重与可选训练日志 |

## 题目一 — Member A

CSV：[`member_A/docs/cloud_storage_manifest.csv`](../task1_3dgs_aigc/member_A/docs/cloud_storage_manifest.csv)、[`member_A/docs/asset_manifest.csv`](../task1_3dgs_aigc/member_A/docs/asset_manifest.csv)

| 建议文件名 | 说明 | 本地路径（相对仓库根） |
|---|---|---|
| `member_A_object_A_raw_images.zip` | 物体 A 原始照片 | `data/object_A_controller/images/` |
| `member_A_colmap_sparse_0.zip` | COLMAP sparse/0 | `outputs/object_A_controller/colmap/sparse/0/` |
| `member_A_training_data.zip` | Splatfacto 训练数据 | `data/object_A_controller/` |
| `member_A_controller_step-000029999.ckpt` | 物体 A checkpoint | `outputs/object_A_controller/nerfstudio_splatfacto/.../` |
| `controller2.ply` | 物体 A Gaussian PLY | `task1_3dgs_aigc/member_B/assets/object_A/controller2.ply` |
| `counter.ply` | 背景 Gaussian PLY | `task1_3dgs_aigc/member_B/assets/background/counter.ply` |
| `member_A_counter_step-000029999.ckpt` | 背景 checkpoint | `outputs/background_scene/.../` |
| `member_A_object_A_background_assets.zip` | A+背景打包 | 按需解压 |
| `mipnerf360_counter.zip` | counter 背景数据集 | `data/background_scene/mipnerf360/counter/` |

## 题目一 — Member B

融合场景与统计见 [`member_B/docs/fusion_deliverables.md`](../task1_3dgs_aigc/member_B/docs/fusion_deliverables.md)。

| 文件 | 路径 |
|---|---|
| 最终融合高斯场景 | `task1_3dgs_aigc/member_B/outputs/renders/fused_scene_gaussian_clean_candidate_guitar_floor_v3.ply.gz` |
| 位置统计 | `task1_3dgs_aigc/member_B/outputs/renders/guitar_floor_v3_stats.csv` |

## 题目二 — Member C

CSV：[`member_C/docs/asset_manifest.csv`](../task2_lerobot_act/member_C/docs/asset_manifest.csv)

| 文件名 | 本地路径 |
|---|---|
| `act_splitA_full_best.pt` | `task2_lerobot_act/member_C/weights/act_splitA_full_best.pt` |
| `act_jointABC_full_best.pt` | `task2_lerobot_act/member_C/weights/act_jointABC_full_best.pt` |
| `train_metrics_splitA.csv`（可选） | `member_C/outputs/final_act_splitA_full/train_metrics.csv` |
| `train_metrics_jointABC.csv`（可选） | `member_C/outputs/final_act_jointABC_full/train_metrics.csv` |

数据集（~66 GB）从 Hugging Face 下载，见 `member_C/scripts/download_full.sh`。
