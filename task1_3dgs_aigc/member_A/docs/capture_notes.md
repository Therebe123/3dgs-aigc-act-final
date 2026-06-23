# Capture and COLMAP Notes — Object A (Controller)

## Capture

| Field | Value |
|---|---|
| Object | Game controller (物体 A) |
| Image path (in repo) | `data/object_A_controller/images/` |
| Raw archive | Google Drive `题目一` (see `cloud_storage.md`) |
| Selected image count | 120 |
| Phone/camera | Xiaomi 15 |
| Lighting | 室内灯光 |
| Background | 房间 |

拍摄建议见 `controller_colmap_3dgs_guide.md` §2–§4：环绕物体、光照均匀、避免运动模糊、覆盖多高度角。

## COLMAP

| Field | Value |
|---|---|
| Method | COLMAP GUI（Feature extraction → Matching → Reconstruction → Export） |
| Database path (repo) | `outputs/object_A_controller/colmap/database.db` |
| Sparse output (repo) | `outputs/object_A_controller/colmap/sparse/0` |
| Camera model | SIMPLE_RADIAL |
| Matching method | exhaustive_matcher |
| Registered images | 118 |
| Notes | 导出后应含 `cameras.bin`、`images.bin`、`points3D.bin` |

CLI 复现命令见 `runbook.md` §2。

整理为 Splatfacto 输入后使用：

```text
data/object_A_controller/
├── images/
└── sparse/0/
```

## 3DGS / Splatfacto

| Field | Value |
|---|---|
| Framework | Nerfstudio Splatfacto |
| Source data path | `data/object_A_controller/` |
| Output dir | `outputs/object_A_controller/nerfstudio_splatfacto/` |
| Target iterations | 30000 |
| GPU | NVIDIA A100 80GB |
| Training time | 21 分 37 秒 |
| Export PLY | `controller2.ply`（28039 Gaussians，交付组员 B） |
| Notes | Config：`member_A/outputs/configs/splatfacto_controller_2026-06-19/` |

## Background (counter)

| Field | Value |
|---|---|
| Dataset | Mip-NeRF 360 counter |
| Data path | `data/background_scene/mipnerf360/counter` |
| Output dir | `outputs/background_scene/counter_splatfacto` |
| GPU | NVIDIA A10 80GB |
| Training time | 35 分 27 秒 |
| Export PLY | `counter.ply`（413019 Gaussians，交付组员 B） |
| Guide | `background_counter_3dgs_guide.md` |
