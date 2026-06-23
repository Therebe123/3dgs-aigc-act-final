# 组员 B：题目一 AIGC 与融合

AIGC 资产生成、格式统一、场景融合与结果对比。

## 物体 B（SD2.1 青花瓷花瓶）

| 项 | 内容 |
|---|---|
| Prompt | `a single small blue and white porcelain vase, one smooth rounded body, one narrow circular opening, glossy ceramic surface, cobalt floral pattern, centered object, symmetrical, studio lighting, high quality 3D asset` |
| Negative | `animal, face, ears, horns, legs, tail, handles, extra openings, duplicated parts, extra limbs, broken geometry, floating parts, blurry texture, noisy surface, low quality` |
| 模型 | `Manojb/stable-diffusion-2-1-base` |
| 输出 | `assets/object_B/`、`results/object_B_threestudio/` |

## 物体 C（Stable-Zero123 吉他）

| 项 | 内容 |
|---|---|
| 输入 | `assets/object_C/input.png` → `input_rgba.png` |
| 模型 | `stabilityai/stable-zero123` |
| 输出 | `assets/object_C/`、`results/object_C_zero123/` |

## 场景融合

| 交付项 | 路径 |
|---|---|
| 资产格式说明 | `docs/asset_format_summary.md` |
| 位置/尺度/朝向表 | `docs/asset_manifest_clear.csv` |
| 融合脚本 | `scripts/fuse_scene_blender.py` |
| 最终融合场景 | `outputs/renders/fused_scene_gaussian_clean_candidate_guitar_floor_v3.ply.gz` |
| 交付清单 | `docs/fusion_deliverables.md` |
| B/C 对比表 | `docs/comparison_table.csv` |
| 报告段落 | `docs/member_B_report.md` |

## 运行

```bash
bash task1_3dgs_aigc/scripts/generate_object_b_text_to_3d.sh
bash task1_3dgs_aigc/scripts/generate_object_c_image_to_3d.sh
bash task1_3dgs_aigc/scripts/render_fused_scene.sh
```

环境：`hw3_3d_train` + threestudio（克隆至 `external_repos/threestudio`），见 `docs/runbook.md`。
