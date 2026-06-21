# Asset Format Summary

本阶段同时保留两种融合表达：

1. **统一高斯版本（推荐作为格式统一交付）**：A、背景为组员 A 原生 3DGS PLY；B、C 从 OBJ Mesh 表面采样并转换为 3DGS-compatible Gaussian PLY；最终拼接为 `renders/fused_scene_gaussian.ply`。
2. **Blender 预览版本**：A、背景高斯 PLY 被采样成彩色点云 Mesh，B/C 以 OBJ Mesh 导入，用于快速生成 `flythrough_clear.mp4` 预览。该预览不等价于真实 3DGS viewer 渲染。

| 资产 | 原始路径 | 原始格式 | 统一高斯路径 | 说明 |
|---|---|---|---|---|
| 背景 | `assets/background/counter.ply` | 3DGS/Gaussian PLY | `assets/background/counter.ply` | 原生高斯，413019 个点；融合时保留全部 413019 个点 |
| 物体 A | `assets/object_A/controller2.ply` | 3DGS/Gaussian PLY | `assets/object_A/controller2.ply` | 原生高斯，28039 个点 |
| 物体 B | `assets/object_B/object_B.obj` | OBJ Mesh | `assets/object_B/object_B_gaussian.ply` | 从 Mesh 表面采样 70000 个 3DGS-compatible 高斯点 |
| 物体 C | `assets/object_C/object_C.obj` | OBJ Mesh | `assets/object_C/object_C_gaussian.ply` | 从 Mesh 表面采样 50000 个 3DGS-compatible 高斯点 |

统一后的高斯场景：`renders/fused_scene_gaussian.ply`，总计 561058 个高斯点。

相关脚本：

- `scripts/mesh_to_gaussian_ply.py`：OBJ Mesh -> 3DGS-compatible Gaussian PLY。
- `scripts/fuse_gaussian_scene.py`：多个 Gaussian PLY 按 manifest 归一化、变换并拼接。
- `scripts/fuse_scene_blender.py`：Blender 预览渲染脚本。
