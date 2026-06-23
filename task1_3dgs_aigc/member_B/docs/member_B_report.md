# 题目一：组员 B 生成资产与场景融合报告

## 1. 任务目标

组员 B 负责题目一中的 AIGC 资产生成与多源资产融合渲染。具体包括：使用文本到 3D 方法生成物体 B，使用单图到 3D 方法生成物体 C，将组员 A 提供的真实物体 A、背景场景与 AIGC 资产统一到同一种可渲染表达，并在同一 3D 场景中调整尺度、位置和朝向，最终输出多视角渲染图与漫游视频。

本部分采用两级融合方案。首先，为了与组员 A 的 3DGS 背景保持一致，将物体 B/C 的 OBJ Mesh 表面采样并转换为 3DGS-compatible Gaussian PLY，再与物体 A 和背景的原生 Gaussian PLY 做代码级拼接，得到统一高斯场景 `outputs/renders/fused_scene_gaussian_clean_candidate_guitar_floor_v3.ply.gz`。其次，为了在普通环境中快速检查布局，额外提供 Blender 预览版：A/背景高斯被采样成彩色点云 Mesh，B/C 以 OBJ Mesh 导入并渲染 `flythrough_clear.mp4`。Blender 预览不等价于真实 3DGS viewer 渲染。

## 2. 物体 B：文本到 3D 生成

### 2.1 Prompt 设计

物体 B 最终选择家居/装饰场景中常见的小型青花瓷花瓶。前期曾尝试陶瓷狐狸，但结果出现多余耳朵等局部结构错误，因此最终改用几何更简单、轮廓更稳定的单体花瓶。

Prompt：

```text
a single small blue and white porcelain vase, one smooth rounded body, one narrow circular opening, glossy ceramic surface, cobalt floral pattern, centered object, symmetrical, studio lighting, high quality 3D asset
```

负向 Prompt：

```text
animal, face, ears, horns, legs, tail, handles, extra openings, duplicated parts, extra limbs, broken geometry, floating parts, blurry texture, noisy surface, low quality
```

该 Prompt 强调单个物体、圆润瓶身、单个窄口、蓝白陶瓷纹样和对称构图，同时用负向 Prompt 抑制动物特征、把手、多开口、重复结构和漂浮碎片。

### 2.2 生成流程与模型

使用 threestudio 的 Stable DreamFusion/SDS 路线完成文本到 3D 生成，扩散模型采用公开 SD2.1 base 镜像：

```text
Manojb/stable-diffusion-2-1-base
```

训练设置：

| 参数 | 值 |
|---|---|
| 配置 | `configs/dreamfusion-sd.yaml` |
| 训练步数 | `10000` |
| GPU | `CUDA_VISIBLE_DEVICES=7` |
| 图像分辨率 | `64 x 64` |
| batch size | `1` |
| validation interval | `200` |

关键结果文件：

| 交付项 | 路径 |
|---|---|
| 训练日志 | `task1_3dgs_aigc/member_B/logs/object_B_train_v3_vase_sd21.log` |
| 最终预览图 | `task1_3dgs_aigc/member_B/assets/object_B/object_B_preview.png` |
| 转台视频 | `task1_3dgs_aigc/member_B/assets/object_B/object_B_turntable.mp4` |
| 导出 OBJ | `task1_3dgs_aigc/member_B/assets/object_B/object_B.obj` |
| checkpoint | `task1_3dgs_aigc/member_B/results/object_B_threestudio/object_B_porcelain_vase_sd21/a_single_small_blue_and_white_porcelain_vase,_one_smooth_rounded_body,_one_narrow_circular_opening,_glossy_ceramic_surface,_cobalt_floral_pattern,_centered_object,_symmetrical,_studio_lighting,_high_quality_3D_asset@20260621-155553/ckpts/last.ckpt` |
| 完整输出目录 | `task1_3dgs_aigc/member_B/results/object_B_threestudio/object_B_porcelain_vase_sd21/a_single_small_blue_and_white_porcelain_vase,_one_smooth_rounded_body,_one_narrow_circular_opening,_glossy_ceramic_surface,_cobalt_floral_pattern,_centered_object,_symmetrical,_studio_lighting,_high_quality_3D_asset@20260621-155553` |

日志显示训练正常达到 `max_steps=10000`，并完成 120 帧 test 视角渲染。导出阶段使用 mesh exporter 生成 `model.obj`，随后复制到稳定交付路径 `assets/object_B/object_B.obj`。

### 2.3 结果观察

与狐狸这类包含耳朵、腿和面部细节的物体相比，花瓶的整体轮廓更简单，SDS 优化时更容易保持单体结构。当前结果可作为题目一中“文本生成 3D 资产”的物体 B 交付；其不足是纹理与几何细节仍依赖扩散先验，多视角一致性和表面质量不如真实多视角重建，需要在最终融合前通过 Blender 预览检查尺度、底部接触和可见面的纹理质量。

## 3. 物体 C：单图到 3D 生成

### 3.1 输入图准备

物体 C 使用单张真实图片作为输入，主体为吉他。原始图片位于：

```text
task1_3dgs_aigc/member_B/assets/object_C/input.png
```

为避免沙发、抱枕和室内背景影响单图生成，先将原图复制为交付输入图，再使用手动去背景结果作为主体图。用户手动清理后的图片为 `image.png`，随后将其转换为真正带 alpha 通道的透明 PNG，用作 Stable-Zero123 训练输入：

```text
task1_3dgs_aigc/member_B/assets/object_C/input.png
task1_3dgs_aigc/member_B/assets/object_C/image.png
task1_3dgs_aigc/member_B/assets/object_C/input_rgba.png
```

其中 `input_rgba.png` 是实际传入 `data.image_path` 的图片，保留吉他主体并使用透明背景，图像模式为 RGBA。

### 3.2 生成流程与模型

物体 C 采用 threestudio 中的 Stable-Zero123 单图到 3D 流程。生成模型使用公开权重：

```text
stabilityai/stable-zero123
```

本地 checkpoint 路径：

```text
task1_3dgs_aigc/member_B/repos/threestudio/load/zero123/stable_zero123.ckpt
```

训练设置：

| 参数 | 值 |
|---|---|
| 配置 | `configs/stable-zero123.yaml` |
| 输入图 | `task1_3dgs_aigc/member_B/assets/object_C/input_rgba.png` |
| 训练步数 | `600` |
| GPU | `CUDA_VISIBLE_DEVICES=7` |
| validation interval | `100` |
| 输出名称 | `object_C_guitar_stable_zero123` |

关键结果文件：

| 交付项 | 路径 |
|---|---|
| 原始输入图 | `task1_3dgs_aigc/member_B/assets/object_C/input.png` |
| 去背景图 | `task1_3dgs_aigc/member_B/assets/object_C/input_rgba.png` |
| 训练日志 | `task1_3dgs_aigc/member_B/logs/object_C_zero123_train.log` |
| 最终预览图 | `task1_3dgs_aigc/member_B/assets/object_C/object_C_preview.png` |
| 多视角转台视频 | `task1_3dgs_aigc/member_B/assets/object_C/object_C_turntable.mp4` |
| validation 视频 | `task1_3dgs_aigc/member_B/assets/object_C/object_C_final_val.mp4` |
| checkpoint | `task1_3dgs_aigc/member_B/results/object_C_zero123/object_C_guitar_stable_zero123/[64, 128, 256]_input_rgba.png@20260621-171641/ckpts/epoch=0-step=600.ckpt` |
| 完整输出目录 | `task1_3dgs_aigc/member_B/results/object_C_zero123/object_C_guitar_stable_zero123/[64, 128, 256]_input_rgba.png@20260621-171641` |

日志显示训练正常达到 `max_steps=600`，并完成 120 帧 test 视角渲染。最终的 `it600-test.mp4` 已复制为稳定交付路径 `assets/object_C/object_C_turntable.mp4`，并从中抽取一帧作为 `object_C_preview.png`。

### 3.3 结果观察

单图生成能较好保留输入图中吉他的主体类别、颜色和正面轮廓；相比直接从文本生成，输入图对主体身份约束更强。但由于只有一张图片，侧面和背面仍由模型先验补全，可能出现不可见区域纹理不稳定、厚度估计不准确或轮廓局部拉伸等问题。当前结果可作为题目一中“使用 Zero123 生成物体 C”的交付，包括输入图、去背景图、生成模型、结果图和训练日志。当前已在此 checkpoint 基础上执行 mesh export，并整理为 `task1_3dgs_aigc/member_B/assets/object_C/object_C.obj`，用于最终融合场景。

## 4. 资产格式统一

题目说明中提到，threestudio 生成资产通常是隐式场或 Mesh，而背景是显式高斯球 3DGS，因此需要说明如何统一表示。本实验采用“高斯统一 + Blender 预览”两套输出。

| 资产 | 原始来源 | 原始表达 | 统一高斯格式 | 处理方式 |
|---|---|---|---|---|
| 背景场景 | 组员 A 提供 | 3DGS/Gaussian PLY | `assets/background/counter.ply` | 保持原生高斯，融合时保留全部 413019 个点 |
| 物体 A | 组员 A 提供 | 3DGS/Gaussian PLY | `assets/object_A/controller2.ply` | 保持原生高斯，28039 个点 |
| 物体 B | threestudio Stable DreamFusion + SD2.1 | OBJ Mesh | Gaussian PLY | 最终融合中使用 94000 个高斯点 |
| 物体 C | 单图 + Stable-Zero123 | OBJ Mesh | Gaussian PLY | 最终融合中使用 90000 个高斯点 |

最终代码级拼接结果为 `outputs/renders/fused_scene_gaussian_clean_candidate_guitar_floor_v3.ply.gz`，解压后共 625058 个高斯点。该文件应使用 3DGS/Nerfstudio/SIBR/gsplat viewer 之类支持 Gaussian Splatting 的工具查看。普通 Blender 不能原生解释 `opacity/scale/rot/SH` 等高斯参数，因此只能作为近似预览。

相关脚本：`scripts/mesh_to_gaussian_ply.py` 用于 B/C Mesh 到高斯 PLY 转换，`scripts/fuse_gaussian_scene.py` 用于拼接 A/B/C/背景高斯资产。详细格式说明见 `asset_format_summary.md`，最终融合文件清单见 `fusion_deliverables.md`。

## 5. 融合场景设计

融合时将背景场景作为主体坐标系，三个物体放置在可见且不遮挡主要背景结构的位置。当前布局如下：

| 资产 | 位置 `(x, y, z)` | 旋转 `(rx, ry, rz)` | 缩放 | 说明 |
|---|---:|---:|---:|---|
| 背景 | `(0, 0, -0.12)` | `(0, 0, 0)` | `0.75` | counter 背景 3DGS PLY |
| 物体 A | `(-0.95, 0.15, 0.02)` | `(0, 0, 8)` | `0.34` | controller2 真实重建 Gaussian PLY |
| 物体 B | `(-0.32, -0.52, 0.12)` | `(0, 0, -8)` | `0.78` | 青花瓷花瓶，展示文本生成资产 |
| 物体 C | `(0.48, -0.50, 0.12)` | `(0, 0, 12)` | `0.72` | 吉他，展示单图生成资产 |

高斯统一版本使用 `scripts/fuse_gaussian_scene.py` 将 A/B/C/背景拼接为高斯场景，再用 `scripts/adjust_clean_candidate_guitar_floor_v3.py` 对吉他位置做最终微调。Blender 预览版本使用 `scripts/fuse_scene_blender.py` 自动导入资产、设置相机轨迹并输出多视角渲染图，再用 ffmpeg 合成为 `renders/flythrough_clear.mp4`。

## 6. 多视角渲染与漫游视频

最终输出包括：

- `outputs/renders/fused_scene_gaussian_clean_candidate_guitar_floor_v3.ply.gz`：A/B/C/背景统一为 3DGS-compatible Gaussian PLY 后的最终代码级拼接结果。
- `renders/fusion_scene_clear/view_000.png` 至 `renders/fusion_scene_clear/view_035.png`：36 张 Blender 近似预览图。该版本将 B/C 放大并置于前景，便于明确看到花瓶和吉他。
- `outputs/renders/fusion_overview_clear.png`：6 个代表视角拼图，便于报告中快速展示。
- `renders/flythrough_clear.mp4`：围绕融合资产的 Blender 近似预览漫游视频。
- `renders/fusion_scene_clear/fusion_scene.blend`：融合后的 Blender 场景文件。
- `logs/fusion_clear_render.log`：融合渲染日志。

渲染设置：

| 参数 | 值 |
|---|---|
| Blender | `4.5.1 LTS` |
| 分辨率 | `1280 x 720` |
| 渲染引擎 | CPU Cycles |
| 多视角数量 | `36` |
| 视频帧率 | `12 fps` |
| 输出格式 | PNG 序列 + MP4 |

## 7. 资产生成方式对比（B/C）

物体 A（真实多视角重建）的方法对比见最终实验报告正文。本节仅记录组员 B 负责的物体 B 和物体 C。

| 方法 | 输入 | 几何准确度 | 纹理细节 | 计算耗时 | 优点 | 局限 |
|---|---|---|---|---:|---|---|
| 物体 B：文本 + threestudio Stable DreamFusion/SD2.1 | 文本 Prompt | 中，花瓶整体轮廓较稳定但表面仍可能有 SDS 伪影 | 中，青花瓷风格可见但纹理细节需检查 | 约 32 分钟 | 不需要真实物体，创作自由度高 | 多视角一致性和几何稳定性弱于真实重建 |
| 物体 C：单图 + Stable-Zero123 | 单张去背景吉他图片 | 中高，正面形状较准，背面依赖补全 | 中高，正面纹理保留较好，侧背面可能拉伸 | 约 3 分钟，权重下载另计 | 输入成本低，贴近真实图片 | 不可见区域容易出现纹理拉伸或语义错误 |

从 B/C 对比看，文本到 3D 更适合生成不存在或难以采集的创意资产，但形状和纹理稳定性依赖 prompt 与扩散先验；单图到 3D 对输入主体身份约束更强，但背面与侧面仍需要模型补全。融合渲染时，两类资产都需要在 Blender 中统一尺度、坐标系、材质亮度和底部接触关系。

## 8. 小结

组员 B 完成了题目一中 AIGC 生成与融合渲染部分的实验设计和可复现流程。通过将 threestudio 生成的物体 B、Stable-Zero123 生成的物体 C，以及组员 A 提供的 3DGS/Gaussian PLY 资产统一到 Blender 可渲染表达，可以完成尺度对齐、场景摆放、多视角渲染和漫游视频生成。该流程兼顾了真实重建的高保真、文本生成的灵活性和单图生成的低输入成本，满足题目一对多源 3D 资产融合展示与方法对比的要求。
