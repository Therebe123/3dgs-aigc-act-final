# 组员 A：题目一真实重建

真实数据采集、COLMAP 位姿估计、Nerfstudio Splatfacto 3DGS 重建，以及交付给组员 B 的 Gaussian PLY。

## 交付清单

| 任务 | 交付物 | 位置 |
|---|---|---|
| 拍摄物体 A | 原始数据、拍摄说明 | `docs/capture_notes.md`；原始图见网盘 `题目一` |
| COLMAP 位姿 | COLMAP 输出、处理记录 | `docs/capture_notes.md`、`docs/runbook.md` §2 |
| 3DGS 重建物体 A | 模型、训练记录 | `outputs/configs/`；PLY 见网盘 |
| 背景 counter | 数据说明与训练 | `docs/background_counter_3dgs_guide.md`、`docs/runbook.md` §4 |
| 参数与资产清单 | 参数表、manifest | `docs/dataset_manifest.csv`、`docs/asset_manifest.csv` |

## 最终资产

| 资产 | 格式 | 高斯点数 | Member B 路径 |
|---|---|---:|---|
| 物体 A（controller） | 3DGS Gaussian PLY | 28039 | `task1_3dgs_aigc/member_B/assets/object_A/controller2.ply` |
| 背景（counter） | 3DGS Gaussian PLY | 413019 | `task1_3dgs_aigc/member_B/assets/background/counter.ply` |

技术路线：Nerfstudio Splatfacto，conda 环境 `nerfstudio_gs`，30000 iterations。

## 预览图

- `assets/object_A_preview.png` — 物体 A
- `assets/counter_preview.png` — counter 背景

## 网盘

大文件见 [Google Drive](https://drive.google.com/drive/folders/1zq4sE9CjMhWjk5RhR1OpKe3YlPzJxqpP?usp=drive_link)（`题目一`），资产清单见 `docs/asset_manifest.csv`。

## 复现

1. 环境：`docs/environment.md`
2. 命令：`docs/runbook.md`
3. 脚本：`scripts/`
4. 指南：`docs/controller_colmap_3dgs_guide.md`、`docs/background_counter_3dgs_guide.md`

```bash
task1_3dgs_aigc\member_A\scripts\train_object_A_splatfacto_windows.bat
bash task1_3dgs_aigc/member_A/scripts/train_object_A_splatfacto_linux.sh
bash task1_3dgs_aigc/member_A/scripts/train_background_counter_splatfacto_linux.sh
bash task1_3dgs_aigc/member_A/scripts/export_gaussian_splat.sh
```
