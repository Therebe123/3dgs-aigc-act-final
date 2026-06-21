# 组员 B 交付包：题目一生成与融合线

本目录整理题目一中组员 B 负责的 AIGC 资产生成、资产格式统一、场景融合渲染和结果对比材料。当前已完成物体 B、物体 C、A/背景资产接入、Blender 融合场景、多视角渲染图和最终漫游视频。

## 当前物体 B 最终版

采用 SD2.1 生成的青花瓷花瓶作为物体 B，旧狐狸与中断的 v2 花瓶仅作为尝试记录，不进入最终清单。

| 交付项 | 路径/内容 |
|---|---|
| Prompt | `a single small blue and white porcelain vase, one smooth rounded body, one narrow circular opening, glossy ceramic surface, cobalt floral pattern, centered object, symmetrical, studio lighting, high quality 3D asset` |
| Negative prompt | `animal, face, ears, horns, legs, tail, handles, extra openings, duplicated parts, extra limbs, broken geometry, floating parts, blurry texture, noisy surface, low quality` |
| 生成模型 | `Manojb/stable-diffusion-2-1-base` |
| 训练日志 | `logs/object_B_train_v3_vase_sd21.log` |
| 结果图 | `assets/object_B/object_B_preview.png` |
| 转台视频 | `assets/object_B/object_B_turntable.mp4` |
| 导出 Mesh | `assets/object_B/object_B.obj` |
| 完整训练目录 | `results/object_B_threestudio/object_B_porcelain_vase_sd21/a_single_small_blue_and_white_porcelain_vase,_one_smooth_rounded_body,_one_narrow_circular_opening,_glossy_ceramic_surface,_cobalt_floral_pattern,_centered_object,_symmetrical,_studio_lighting,_high_quality_3D_asset@20260621-155553` |

## 当前物体 C 最终版

采用 Stable-Zero123 生成吉他物体 C。用户提供去除背景后的 `assets/object_C/image.png`，实际训练输入为带透明通道的 `assets/object_C/input_rgba.png`。

| 交付项 | 路径/内容 |
|---|---|
| 原始输入图 | `assets/object_C/input.png` |
| 去背景图 | `assets/object_C/input_rgba.png` |
| 生成模型 | `stabilityai/stable-zero123` |
| 训练日志 | `logs/object_C_zero123_train.log` |
| 结果图 | `assets/object_C/object_C_preview.png` |
| 转台视频 | `assets/object_C/object_C_turntable.mp4` |
| 导出 Mesh | `assets/object_C/object_C.obj` |
| 完整训练目录 | `results/object_C_zero123/object_C_guitar_stable_zero123/[64, 128, 256]_input_rgba.png@20260621-171641` |

## 场景融合最终版

| 交付项 | 路径 |
|---|---|
| 资产格式说明 | `asset_format_summary.md` |
| 资产位置/尺度/朝向表 | `asset_manifest_clear.csv` |
| Blender 融合脚本 | `scripts/fuse_scene_blender.py` |
| Blender 场景文件 | `renders/fusion_scene_clear/fusion_scene.blend` |
| 多视角渲染图 | `renders/fusion_scene_clear/view_000.png` 至 `view_035.png` |
| 多视角总览图 | `renders/fusion_overview_clear.png` |
| 最终漫游视频 | `renders/flythrough_clear.mp4` |
| 融合渲染日志 | `logs/fusion_clear_render.log` |
| B/C 方法对比表 | `comparison_table.csv` |

## 目录结构

| 路径 | 用途 |
|---|---|
| `member_B_report.md` | 可直接合入最终实验报告的组员 B 章节 |
| `runbook.md` | threestudio、Zero123、Blender 融合渲染的命令记录 |
| `comparison_table.csv` | 三种 3D 资产生成方式的对比表，A 行按分工留空，只填写 B/C |
| `asset_manifest_clear.csv` | 清晰版资产路径、尺度、位置、朝向登记表 |
| `asset_format_summary.md` | Mesh/点云/高斯球等格式说明 |
| `fusion_deliverables.md` | 融合场景、多视角图、漫游视频交付清单 |
| `scripts/fuse_scene_blender.py` | Blender 中导入 A/B/C 与背景资产并批量渲染的脚本 |
| `assets/` | 放置物体 A/B/C 与背景资产 |
| `renders/` | 放置融合渲染图片和漫游视频 |
| `results/` | 放置训练输出、checkpoint、测试视频等结果材料 |
