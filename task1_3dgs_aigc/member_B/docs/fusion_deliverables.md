# Fusion Deliverables

| 交付项 | 路径 |
|---|---|
| 资产格式说明 | `homework/member_B/asset_format_summary.md` |
| B 高斯资产 | `homework/member_B/assets/object_B/object_B_gaussian.ply` |
| C 高斯资产 | `homework/member_B/assets/object_C/object_C_gaussian.ply` |
| 高斯融合 manifest | `homework/member_B/asset_manifest_gaussian_native.csv` |
| 统一高斯融合场景 | `homework/member_B/renders/fused_scene_gaussian.ply` |
| 高斯融合说明 | `homework/member_B/gaussian_fusion_notes.md` |
| 资产位置/尺度/朝向表 | `homework/member_B/asset_manifest_clear.csv` |
| 融合脚本 | `homework/member_B/scripts/fuse_scene_blender.py` |
| Blender 场景文件 | `homework/member_B/renders/fusion_scene_clear/fusion_scene.blend` |
| 多视角渲染图 | `homework/member_B/renders/fusion_scene_clear/view_000.png` 至 `view_035.png` |
| 多视角总览图 | `homework/member_B/renders/fusion_overview_clear.png` |
| 最终漫游视频 | `homework/member_B/renders/flythrough_clear.mp4` |
| 融合渲染日志 | `homework/member_B/logs/fusion_clear_render.log` |
| B/C 方法对比表 | `homework/member_B/comparison_table.csv` |

当前高斯融合布局（`asset_manifest_gaussian_native.csv`）：

| 资产 | 位置 `(x, y, z)` | 旋转 `(rx, ry, rz)` | 缩放 | 坐标处理 |
|---|---:|---:|---:|---|
| 背景 | `(0, 0, 0)` | `(0, 0, 0)` | `1.0` | 保留原生 3DGS 坐标和 scale |
| 物体 A | `(0, 0, 0)` | `(0, 0, 0)` | `1.0` | 保留原生 3DGS 坐标和 scale |
| 物体 B | `(-0.55, -0.70, -0.20)` | `(0, 0, -8)` | `0.55` | 插入背景原生坐标系 |
| 物体 C | `(0.45, -0.70, -0.20)` | `(0, 0, 12)` | `0.55` | 插入背景原生坐标系 |

Blender 预览布局另见 `asset_manifest_clear.csv`；该预览仅用于报告截图/视频，不代表原生 3DGS 渲染。

渲染参数：Blender `4.5.1 LTS`，CPU Cycles，`1280 x 720`，36 个环绕视角，`12 fps` 合成 MP4。当前推荐提交统一高斯场景 `fused_scene_gaussian.ply` 作为格式统一结果；`flythrough_clear.mp4` 是 Blender 近似预览，B/C 被放大并置于前景。
