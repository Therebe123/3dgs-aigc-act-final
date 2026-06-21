# Gaussian Fusion Fix Notes

## 问题

初版 `renders/fused_scene_gaussian.ply` 将背景和物体 A 也做了归一化缩放，这会破坏原生 3DGS 的空间坐标和高斯 `scale_0..2` 参数。因此在 3DGS viewer 中打开时，背景可能会被压缩、变形或尺度不合理。

## 修正

已将旧版备份为：

```text
homework/member_B/renders/fused_scene_gaussian_normalized_old.ply
```

新的 `homework/member_B/renders/fused_scene_gaussian.ply` 已重新生成，策略如下：

- 背景 `counter.ply`：保留原生 3DGS 坐标和高斯尺度，不归一化。
- 物体 A `controller2.ply`：保留原生 3DGS 坐标和高斯尺度，不归一化。
- 物体 B/C：从 OBJ 采样转换为 3DGS-compatible Gaussian PLY 后，放入背景原生坐标系中。

当前融合文件统计：

| 资产 | 高斯数量 | 坐标/尺度处理 |
|---|---:|---|
| 背景 | 413019 | 保留原生坐标和 scale |
| 物体 A | 28039 | 保留原生坐标和 scale |
| 物体 B | 70000 | 插入背景坐标系 |
| 物体 C | 50000 | 插入背景坐标系 |
| 合计 | 561058 | 统一 62 字段 Gaussian PLY |

新文件 bounding box 与原始背景一致：

```text
min [-13.702231, -10.314659, -11.484602]
max [25.529058, 23.799545, 5.519185]
```

这说明背景没有再被错误缩放。该文件仍需使用支持 3DGS 的 viewer 打开，普通 Blender 不能正确解释高斯球渲染参数。

## B/C 轮廓问题修正

初版 OBJ -> Gaussian 转换只写入了一个固定颜色，因此在 SuperSplat 中 B/C 会像纯色剪影。当前版本已改为读取 OBJ 顶点行中的 RGB 值，并在三角面采样时按重心坐标插值到每个 Gaussian 点。

颜色验证结果：

| 资产 | RGB 均值 | RGB 标准差 | 说明 |
|---|---|---|---|
| 物体 B | [0.1281, 0.1200, 0.6829] | [0.3032, 0.2999, 0.3878] | 保留青花瓷蓝白纹理，不再是单色轮廓 |
| 物体 C | [0.6128, 0.5576, 0.4614] | [0.3594, 0.3762, 0.3450] | 保留吉他输入图颜色，不再是单色轮廓 |

GitHub 中的可打开文件为：

```text
task1_3dgs_aigc/member_B/outputs/renders/fused_scene_gaussian.ply.gz
```

解压后用 SuperSplat 或其他 3DGS viewer 打开。不要打开旧的 `fused_scene_gaussian_normalized_old.ply`，那是保留给错误对比的旧文件。
