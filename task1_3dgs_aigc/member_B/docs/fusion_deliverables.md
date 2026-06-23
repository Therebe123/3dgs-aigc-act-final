# Fusion Deliverables

| 交付项 | 路径 |
|---|---|
| 资产格式说明 | `task1_3dgs_aigc/member_B/docs/asset_format_summary.md` |
| 高斯融合 manifest | `task1_3dgs_aigc/member_B/docs/asset_manifest_gaussian_native.csv` |
| 最终融合高斯场景（压缩） | `task1_3dgs_aigc/member_B/outputs/renders/fused_scene_gaussian_clean_candidate_guitar_floor_v3.ply.gz` |
| 最终俯视位置检查图 | `task1_3dgs_aigc/member_B/outputs/renders/guitar_floor_v3_topdown.png` |
| 最终位置统计 | `task1_3dgs_aigc/member_B/outputs/renders/guitar_floor_v3_stats.csv` |
| clean-candidate 复现输入 | `task1_3dgs_aigc/member_B/outputs/renders/fused_scene_gaussian_clean_candidate.ply.gz` |
| 资产位置/尺度/朝向表 | `task1_3dgs_aigc/member_B/docs/asset_manifest_clear.csv` |
| 融合脚本 | `task1_3dgs_aigc/member_B/scripts/fuse_scene_blender.py` |
| 多视角总览图 | `task1_3dgs_aigc/member_B/outputs/renders/fusion_overview_clear.png` |
| B/C 方法对比表 | `task1_3dgs_aigc/member_B/docs/comparison_table.csv` |

当前高斯融合布局（`asset_manifest_gaussian_native.csv`）：

| 资产 | 位置 `(x, y, z)` | 旋转 `(rx, ry, rz)` | 缩放 | 坐标处理 |
|---|---:|---:|---:|---|
| 背景 | `(0, 0, 0)` | `(0, 0, 0)` | `1.0` | 保留原生 3DGS 坐标和 scale |
| 物体 A | `(0, 0, 0)` | `(0, 0, 0)` | `1.0` | 保留原生 3DGS 坐标和 scale |
| 物体 B | `(-0.55, -0.70, -0.20)` | `(0, 0, -8)` | `0.55` | 插入背景原生坐标系 |
| 物体 C | `(0.45, -0.70, -0.20)` | `(0, 0, 12)` | `0.55` | 插入背景原生坐标系 |

Blender 预览布局另见 `asset_manifest_clear.csv`；该预览仅用于报告截图/视频，不代表原生 3DGS 渲染。

当前推荐提交统一高斯场景 `fused_scene_gaussian_clean_candidate_guitar_floor_v3.ply.gz` 作为格式统一结果。`fused_scene_gaussian_clean_candidate.ply.gz` 仅保留为生成最终 v3 的复现输入。

## Final Clean Gaussian Candidate

After visual placement review, the recommended final 3DGS deliverable is:

| 交付项 | 路径 |
|---|---|
| 最终融合高斯场景（压缩） | `task1_3dgs_aigc/member_B/outputs/renders/fused_scene_gaussian_clean_candidate_guitar_floor_v3.ply.gz` |
| 最终俯视位置检查图 | `task1_3dgs_aigc/member_B/outputs/renders/guitar_floor_v3_topdown.png` |
| 最终位置统计 | `task1_3dgs_aigc/member_B/outputs/renders/guitar_floor_v3_stats.csv` |
| 三个前景资产 transform 表 | `task1_3dgs_aigc/member_B/docs/transforms_clean_candidate.csv` |
| 吉他最终微调脚本 | `task1_3dgs_aigc/member_B/scripts/adjust_clean_candidate_guitar_floor_v3.py` |

该版本先分别调整 controller / bottle / guitar 的 translation、rotation、scale，再与未移动的 `counter.ply` 背景合并。经 SuperSplat 复查后，保留 controller 和 bottle 的 clean-candidate 位置，并将 guitar 单独下移到柜体/地面侧。`counter.ply` 的高斯记录保持在融合文件前缀中，未做整体移动或归一化。
