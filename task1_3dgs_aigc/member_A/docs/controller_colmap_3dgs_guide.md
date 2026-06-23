# 题目一：手柄真实数据采集、COLMAP 与 3DGS 重建指南

本文档面向成员 A，目标是从手机拍摄一个真实手柄开始，完成 COLMAP 相机位姿估计和 3D Gaussian Splatting（3DGS）重建，并整理可用于报告的过程材料与结果。

推荐对象：游戏手柄、VR 手柄、遥控器等小型物体。本文以 `object_A_controller` 为例。

## 1. 总体流程

```text
手机拍摄手柄
  -> 整理原始照片或视频
  -> 筛选/抽帧/去模糊
  -> COLMAP 估计相机参数和稀疏点云
  -> 转换为 3DGS 所需数据格式
  -> 训练 3DGS
  -> 渲染检查
  -> 导出图片、视频、点云和实验记录
```

建议仓库路径：

```text
3dgs-aigc-act-final/
|-- data/
|   `-- object_A_controller/
|       |-- raw_images/       # 手机原始照片
|       |-- raw_video/        # 手机原始视频
|       `-- input/            # 最终送入 COLMAP/3DGS 的图片
|-- outputs/
|   `-- object_A_controller/  # COLMAP、3DGS、渲染结果
|-- external_repos/
|   `-- gaussian-splatting/   # 官方 3DGS 代码，建议放这里
`-- docs/
    `-- task1_controller_colmap_3dgs_guide.md
```

## 2. 手机拍摄前准备

### 2.1 场地和光照

手柄这类物体常见问题是黑色塑料、反光表面、纹理不足。拍摄时优先让 COLMAP 能稳定匹配特征点。

建议：

- 使用明亮、均匀、稳定的光照。优先选择白天窗边散射光，或两盏台灯从左右两侧打光。
- 不要使用强烈单点光源，避免手柄表面出现大片高光。
- 不要使用闪光灯。
- 桌面和背景不要纯白、纯黑、纯色。可以铺一张带纹理的布、报纸、海报纸、鼠标垫，帮助 COLMAP 找特征。
- 手柄下面不要用会反光的玻璃、金属桌面。
- 如果手柄是黑色或亮面，可以在周围放一些固定的、有纹理的小物件作为辅助特征，但不要遮挡手柄。

不建议：

- 手持手柄在空中转动拍摄。这样背景和物体相对关系会变化，COLMAP 容易失败。
- 把手柄放在纯色桌面上绕拍。纹理不足时特征匹配会很差。
- 在室内自动灯光频闪或曝光剧烈变化的环境下拍。

### 2.2 手机设置

优先使用手机原生相机或可以锁定参数的相机 App。

建议设置：

- 使用后置主摄，不要用超广角镜头。超广角畸变大，不利于重建。
- 关闭美颜、HDR、夜景、人像模式、滤镜、水印。
- 尽量锁定曝光和焦点。iPhone 可长按画面进行 AE/AF Lock；安卓相机通常也支持长按锁定。
- 分辨率不需要极高。照片长边 1600-3000 像素已经足够；太大会拖慢 COLMAP。
- 拍照时尽量保持同一焦距，不要一会儿 1x、一会儿 2x、一会儿数字变焦。
- 不要中途切换横竖屏。建议全程横屏。
- 镜头擦干净。

## 3. 拍摄方案

推荐“固定物体，移动相机”的方式：手柄放在桌面上不动，人拿手机围绕它拍摄。

### 3.1 最小可用方案

适合快速跑通流程：

- 拍摄 60-100 张照片。
- 围绕手柄水平一圈，每隔约 10-15 度拍一张。
- 再从略高角度绕一圈。
- 再补拍顶部、正面、背面、左右侧细节。

### 3.2 更稳妥的课程项目方案

推荐用于最终提交：

- 总照片数：100-180 张。
- 第一圈：低角度，接近桌面，高度略低于手柄中心，拍 30-40 张。
- 第二圈：中角度，与手柄中心齐平，拍 30-50 张。
- 第三圈：高角度，俯视 30-45 度，拍 30-50 张。
- 顶部补拍：围绕摇杆、按键、扳机区域补拍 20-40 张。
- 每张照片与前后照片保持 60%-80% 画面重叠。

拍摄时画面中手柄最好占 50%-75%，不要让物体太小，也不要裁掉边缘。

### 3.3 视频抽帧方案

如果不想手动拍很多照片，可以录视频后抽帧。

建议：

- 录制 4K 或 1080p，30fps 即可。
- 绕物体慢慢走，速度要稳定。
- 视频时长 1-2 分钟。
- 后续每隔 10-20 帧抽一张，最终保留 100-200 张。

抽帧命令示例：

```powershell
ffmpeg -i data/object_A_controller/raw_video/controller.mp4 -vf "fps=2,scale=1920:-1" data/object_A_controller/input/frame_%04d.jpg
```

如果视频很晃、拖影明显，不如直接拍照片。

## 4. 数据整理

### 4.1 放置原始数据

照片方案：

```text
data/object_A_controller/raw_images/
```

视频方案：

```text
data/object_A_controller/raw_video/
```

最终用于 COLMAP/3DGS 的图片统一放：

```text
data/object_A_controller/input/
```

### 4.2 筛选图片

删除以下图片：

- 明显模糊、拖影、失焦。
- 手柄被手、影子、其他物体严重遮挡。
- 曝光突然过亮或过暗。
- 与前后视角几乎完全重复。
- 中途变焦、换镜头、换焦距的照片。
- 只拍到局部细节，无法与其他照片建立连续匹配的孤立照片。

保留原则：

- 视角连续。
- 覆盖完整。
- 光照一致。
- 物体和背景都尽量清晰。

## 5. 安装与准备 COLMAP

COLMAP 可以通过 GUI 或命令行使用。第一次建议先用 GUI 理解流程，再用命令行保证可复现。

### 5.1 Windows 安装

1. 下载 COLMAP Windows 版本。
2. 解压到稳定路径，例如：

```text
<colmap-install-dir>/
```

3. 启动脚本通常为 `COLMAP.bat`（CUDA 版）或 `colmap.exe`。

可以将安装目录加入系统 Path，或在命令中使用完整路径。
4. 在 PowerShell 检查：

```powershell
colmap -h
```

如果提示找不到命令，使用安装目录下的启动脚本，例如：

```powershell
& "<colmap-install-dir>/COLMAP.bat" -h
```

### 5.2 GPU 注意事项

如果电脑有 NVIDIA GPU，COLMAP 特征提取和匹配会快很多。没有 GPU 也能跑，只是更慢。

常用原则：

- 有 CUDA：使用默认 GPU 设置。
- 没有 CUDA 或报 GPU 错误：在命令中加入 `--SiftExtraction.use_gpu 0 --SiftMatching.use_gpu 0`。

## 6. 用 COLMAP GUI 跑通一次

GUI 流程适合第一次理解 COLMAP。

1. 打开 COLMAP。
2. 点击 `File -> New project`。
3. 新建数据库：

```text
outputs/object_A_controller/colmap/database.db
```

4. 选择图片目录：

```text
data/object_A_controller/input/
```

5. 点击 `Processing -> Feature extraction`。
6. 相机模型可先用 `SIMPLE_RADIAL`。
7. 点击 `Processing -> Feature matching`，选择 `Exhaustive matching`。
8. 点击 `Reconstruction -> Start reconstruction`。
9. 如果窗口里出现相机位姿和稀疏点云，说明 COLMAP 成功。
10. 保存 sparse model 到：

```text
outputs/object_A_controller/colmap/sparse/0/
```

GUI 成功后，再用命令行复现同样流程。

## 7. 用 COLMAP 命令行重建

以下命令从仓库根目录执行：

```powershell
cd <repo-root>
```

创建输出目录：

```powershell
mkdir outputs/object_A_controller/colmap
mkdir outputs/object_A_controller/colmap/sparse
```

### 7.1 特征提取

```powershell
colmap feature_extractor `
    --database_path outputs/object_A_controller/colmap/database.db `
    --image_path data/object_A_controller/input `
    --ImageReader.camera_model SIMPLE_RADIAL `
    --SiftExtraction.use_gpu 1
```

如果没有 NVIDIA GPU：

```powershell
colmap feature_extractor `
    --database_path outputs/object_A_controller/colmap/database.db `
    --image_path data/object_A_controller/input `
    --ImageReader.camera_model SIMPLE_RADIAL `
    --SiftExtraction.use_gpu 0
```

### 7.2 特征匹配

小物体数据集通常图片数量不大，使用 exhaustive matching 即可：

```powershell
colmap exhaustive_matcher `
    --database_path outputs/object_A_controller/colmap/database.db `
    --SiftMatching.use_gpu 1
```

无 GPU：

```powershell
colmap exhaustive_matcher `
    --database_path outputs/object_A_controller/colmap/database.db `
    --SiftMatching.use_gpu 0
```

### 7.3 稀疏重建

```powershell
colmap mapper `
    --database_path outputs/object_A_controller/colmap/database.db `
    --image_path data/object_A_controller/input `
    --output_path outputs/object_A_controller/colmap/sparse
```

成功后通常会生成：

```text
outputs/object_A_controller/colmap/sparse/0/
|-- cameras.bin
|-- images.bin
`-- points3D.bin
```

### 7.4 导出可查看点云

可导出 PLY 点云用于 Meshlab 或 CloudCompare 检查：

```powershell
colmap model_converter `
    --input_path outputs/object_A_controller/colmap/sparse/0 `
    --output_path outputs/object_A_controller/colmap/sparse_points.ply `
    --output_type PLY
```

检查重点：

- 相机是否围绕手柄形成一圈或多圈。
- 稀疏点云是否集中在手柄和桌面区域。
- 是否有大量漂浮点。
- 注册图片数量是否足够。最终建议至少 70% 以上图片被成功注册。

## 8. 转换为 3DGS 数据格式

官方 3DGS 通常使用 `convert.py` 调用 COLMAP，并要求数据目录中有 `input/` 或 `images/` 图片目录。

建议先把官方仓库克隆到：

```text
external_repos/gaussian-splatting/
```

如果你已经用上面的 COLMAP 命令生成了 sparse，可以按以下结构整理：

```text
data/object_A_controller/
|-- input/
`-- sparse/
    `-- 0/
        |-- cameras.bin
        |-- images.bin
        `-- points3D.bin
```

可以把 COLMAP 输出复制过去：

```powershell
Copy-Item -Recurse outputs/object_A_controller/colmap/sparse data/object_A_controller/sparse
```

更推荐使用官方 3DGS 的 `convert.py` 一步处理：

```powershell
cd external_repos/gaussian-splatting
python convert.py -s ../../data/object_A_controller
```

`convert.py` 会完成 COLMAP 和图像 undistortion，生成 3DGS 训练所需结构。若之前已经跑过 COLMAP，也可以保留原始记录，并用 `convert.py` 再生成一份标准输入。

## 9. 训练 3D Gaussian Splatting

从 3DGS 仓库执行：

```powershell
cd <repo-root>\external_repos\gaussian-splatting
```

训练命令：

```powershell
python train.py `
    -s ../../data/object_A_controller `
    -m ../../outputs/object_A_controller/3dgs
```

常用训练迭代：

- 快速测试：`--iterations 7000`
- 较稳定结果：`--iterations 30000`

示例：

```powershell
python train.py `
    -s ../../data/object_A_controller `
    -m ../../outputs/object_A_controller/3dgs `
    --iterations 30000
```

训练结果通常包括：

```text
outputs/object_A_controller/3dgs/
|-- point_cloud/
|-- cameras.json
|-- cfg_args
`-- input.ply
```

如果显存不足：

- 减少图片分辨率，例如长边压到 1200-1600。
- 降低训练迭代先跑通。
- 关闭其他占用 GPU 的程序。
- 检查是否误用了超高分辨率原图。

## 10. 渲染和检查结果

渲染训练视角：

```powershell
python render.py `
    -m ../../outputs/object_A_controller/3dgs
```

如果需要计算指标：

```powershell
python metrics.py `
    -m ../../outputs/object_A_controller/3dgs
```

建议保存以下材料用于报告：

```text
outputs/object_A_controller/
|-- colmap/
|   |-- sparse_points.ply
|   `-- reconstruction_screenshot.png
|-- 3dgs/
|-- renders/
|-- videos/
`-- notes.md
```

报告中建议放：

- 拍摄对象照片。
- 拍摄环绕示意图。
- COLMAP sparse reconstruction 截图。
- 3DGS 渲染结果。
- 失败案例或调参说明。
- 数据量：照片数、注册照片数、训练迭代数、训练时长、GPU 型号。

## 11. 常见问题与处理

### 11.1 COLMAP 注册图片很少

可能原因：

- 图片太模糊。
- 视角跨度太大，前后图片重叠不足。
- 背景和物体纹理太少。
- 手柄表面反光导致特征不稳定。
- 中途变焦或换镜头。

处理：

- 删除模糊照片。
- 增加中间视角照片。
- 换成有纹理的桌面或背景。
- 使用更均匀的光照。
- 全程固定焦距和曝光。

### 11.2 点云主要重建了桌面，手柄很少

可能原因：

- 手柄纹理太少，桌面纹理更多。
- 手柄在画面中太小。
- 手柄黑色反光严重。

处理：

- 让手柄占画面更大。
- 增加按键、摇杆、边缘细节视角。
- 使用哑光光照，减少高光。
- 可以在手柄旁边放固定纹理参照物，但最终展示时说明这是辅助 COLMAP 的背景特征。

### 11.3 3DGS 出现漂浮点或背景很乱

可能原因：

- COLMAP 位姿不准。
- 图片里有移动物体、手、影子。
- 背景过复杂，且目标物体占比不够。

处理：

- 先修 COLMAP，不要直接硬训。
- 删除异常图片后重新跑 COLMAP。
- 训练前裁剪或重新拍摄更干净的数据。
- 让手柄占更大画面。

### 11.4 3DGS 手柄表面发糊

可能原因：

- 输入图片失焦或压缩严重。
- 训练迭代不够。
- 拍摄视角没有覆盖细节区域。
- 黑色/反光表面本身较难重建。

处理：

- 使用更清晰的照片。
- 增加局部细节视角。
- 提高训练迭代。
- 重拍时锁定焦点，慢慢移动手机。

## 12. 推荐执行清单

### 拍摄当天

- [ ] 清洁手机镜头。
- [ ] 手柄固定在有纹理桌面上。
- [ ] 光照均匀，无强高光。
- [ ] 手机使用后置主摄，关闭滤镜和水印。
- [ ] 锁定曝光和焦点。
- [ ] 拍摄 100-180 张照片，覆盖低/中/高三圈。
- [ ] 检查照片是否清晰、连续、无遮挡。

### COLMAP 阶段

- [ ] 将最终图片放入 `data/object_A_controller/input/`。
- [ ] 跑 `feature_extractor`。
- [ ] 跑 `exhaustive_matcher`。
- [ ] 跑 `mapper`。
- [ ] 检查注册图片数量和 sparse 点云。
- [ ] 导出 `sparse_points.ply`。

### 3DGS 阶段

- [ ] 使用官方 `convert.py` 生成标准数据。
- [ ] 先用 7000 iterations 跑通。
- [ ] 确认渲染正常后跑 30000 iterations。
- [ ] 保存渲染图和视频。
- [ ] 记录训练环境、数据量、参数和问题。

## 13. 建议记录模板

可以在 `outputs/object_A_controller/notes.md` 中记录：

```markdown
# Object A Controller Reconstruction Notes

## Capture

- Date:
- Phone:
- Camera mode:
- Number of raw photos:
- Number of selected input photos:
- Lighting:
- Background:

## COLMAP

- Camera model:
- Feature extraction GPU:
- Matching type:
- Registered images:
- Main issues:

## 3DGS

- 3DGS repository commit:
- GPU:
- Iterations:
- Training time:
- Output path:
- Observations:

## Report Figures

- Original object photo:
- COLMAP sparse reconstruction:
- 3DGS render:
- Failure/ablation figure:
```

## 14. 最推荐的第一轮实践

为了降低第一次上手成本，建议按这个顺序：

1. 先拍 80 张清晰照片，不追求完美。
2. 放入 `data/object_A_controller/input/`。
3. 用 COLMAP GUI 跑一遍，确认能看到相机和点云。
4. 用命令行复现 COLMAP。
5. 用 3DGS 跑 `7000` iterations。
6. 看渲染效果后决定是否重拍。
7. 最终重拍一版 120-180 张照片，跑 `30000` iterations。

第一次的目标不是一次成功出大片，而是尽快判断拍摄数据是否可用。只要 COLMAP 的相机位姿是稳定环绕的，3DGS 后续才有意义。
