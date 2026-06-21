# Gaussian Fusion Notes

## 为什么普通 Blender 打开背景会不对

组员 A 提供的背景 `assets/background/counter.ply` 和物体 A `assets/object_A/controller2.ply` 不是普通 Mesh PLY，而是 3D Gaussian Splatting PLY。文件中每个 vertex 实际表示一个高斯球，包含：

- 位置：`x, y, z`
- 法线/方向辅助字段：`nx, ny, nz`
- 球谐颜色：`f_dc_0..2`, `f_rest_0..44`
- 透明度：`opacity`
- 高斯尺度：`scale_0..2`
- 高斯旋转：`rot_0..3`

因此，Blender 直接导入时不会按 3DGS 的高斯 splatting 方式渲染，只能看到点云/近似几何，背景效果一定不等同于真实 3DGS viewer 中的结果。

## 本次统一格式方案

题目说明允许两种路线：

1. 将 AIGC 资产导出为 Mesh 后，在 Blender 中进行融合渲染。
2. 将生成资产采样为点云/高斯球，和 3DGS 背景做代码级拼接。

为了和组员 A 的 3DGS 背景保持一致，本次补充了第 2 条路线：将物体 B/C 的 OBJ Mesh 表面采样并转换为 3DGS-compatible Gaussian PLY，再与物体 A 和背景拼接为统一高斯场景。

## 生成文件

| 交付项 | 路径 | 说明 |
|---|---|---|
| B 的高斯版 | `assets/object_B/object_B_gaussian.ply` | 从 `object_B.obj` 表面采样 70000 个高斯点 |
| C 的高斯版 | `assets/object_C/object_C_gaussian.ply` | 从 `object_C.obj` 表面采样 50000 个高斯点 |
| 高斯融合 manifest | `asset_manifest_gaussian_native.csv` | A/B/C/背景的高斯资产路径、位置、缩放和朝向 |
| 统一高斯场景 | `renders/fused_scene_gaussian.ply` | A + B + C + 背景拼接后的 3DGS-compatible PLY，总计 561058 个高斯；背景和 A 保持原生坐标/尺度 |
| Mesh 预览视频 | `renders/flythrough_clear.mp4` | Blender 近似预览，不代表原生 3DGS 渲染效果 |

## 复现命令

```bash
python homework/member_B/scripts/mesh_to_gaussian_ply.py   --input homework/member_B/assets/object_B/object_B.obj   --output homework/member_B/assets/object_B/object_B_gaussian.ply   --samples 70000 --color 0.86 0.92 1.0 --target-extent 0.9

python homework/member_B/scripts/mesh_to_gaussian_ply.py   --input homework/member_B/assets/object_C/object_C.obj   --output homework/member_B/assets/object_C/object_C_gaussian.ply   --samples 50000 --color 0.76 0.43 0.16 --target-extent 0.9

python homework/member_B/scripts/fuse_gaussian_scene.py   --manifest homework/member_B/asset_manifest_gaussian_native.csv   --output homework/member_B/renders/fused_scene_gaussian.ply   --max-background 413019 --max-object-a 28039
```

## 注意

B/C 的高斯版是由生成 Mesh 采样得到的格式统一结果，适合进行代码级拼接和 3DGS viewer 预览；它不是重新从多视角图像训练得到的高质量 3DGS。若要获得更真实的 B/C 高斯外观，需要对 B/C 生成多视角图，再用 3DGS/gsplat/Nerfstudio 重新优化高斯参数。
