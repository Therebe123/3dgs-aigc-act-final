# 题目一：Mip-NeRF 360 背景场景数据获取与 3DGS 重建指南

本文档面向**背景场景重建**任务：从 Mip-NeRF 360 开源数据集中选一个场景（如 `garden`、`bicycle`、`counter`），用 **3D Gaussian Splatting（3DGS）** 重建为统一环境背景，供后续与物体 A/B/C 融合。

> **重要说明**：[google-research/multinerf](https://github.com/google-research/multinerf) 是 Mip-NeRF 360 / Ref-NeRF / RawNeRF 的 **JAX 版 NeRF 训练代码**，作业要求的背景重建用的是 **3DGS**，**不需要安装或运行 multinerf**。multinerf 仓库的价值在于：说明了数据集格式、COLMAP 目录结构，以及「自带位姿的数据如何组织」——Mip-NeRF 360 官方包已经跑好 COLMAP，可直接喂给 3DGS。

## 1. 总体流程

```text
下载 Mip-NeRF 360 数据集（360_v2.zip）
  -> 解压并选择一个场景（garden / bicycle / counter 等）
  -> 确认 images + sparse/0 已就绪（无需再跑 COLMAP）
  -> 用官方 3DGS 训练该场景
  -> 渲染检查 / 导出视频
  -> 将背景模型交给融合同学（组员 B）
```

建议仓库路径：

```text
3dgs-aigc-act-final/
|-- data/
|   `-- mipnerf360/
|       `-- 360_v2/
|           |-- garden/
|           |-- bicycle/
|           |-- counter/
|           `-- ...
|-- outputs/
|   `-- background_garden/    # 以 garden 为例
|       `-- 3dgs/
|-- external_repos/
|   `-- gaussian-splatting/
`-- docs/
    `-- task1_background_mipnerf360_3dgs_guide.md
```

## 2. 数据集来源与 multinerf 的关系

### 2.1 官方下载地址

| 资源 | 链接 |
|------|------|
| 项目主页 | https://jonbarron.info/mipnerf360/ |
| **标准 7 场景压缩包** | http://storage.googleapis.com/gresearch/refraw360/360_v2.zip |
| 额外场景（可选） | https://storage.googleapis.com/gresearch/refraw360/360_extra_scenes.zip |

`360_v2.zip` 解压后得到 `360_v2/` 目录，内含作业提到的场景：

| 场景 | 类型 | 说明 |
|------|------|------|
| `garden` | 室外 | 花园，细节丰富，推荐作背景 |
| `bicycle` | 室外 | 自行车场景，较大 |
| `stump` | 室外 | 树桩 |
| `room` | 室内 | 房间 |
| `counter` | 室内 | 厨房台面，作业示例之一 |
| `kitchen` | 室内 | 厨房 |
| `bonsai` | 室内 | 盆景 |

> 数据集体积约 **12 GB**（压缩包），解压后更大。请预留至少 **30 GB** 磁盘空间。

### 2.2 multinerf 仓库做什么、不做什么

[multinerf README](https://github.com/google-research/multinerf) 中：

- **做**：用 gin 配置训练 **Mip-NeRF 360（NeRF）**；若自己拍照片，可用 `scripts/local_colmap_and_resize.sh` 跑 COLMAP。
- **不做**：不提供 3DGS 训练；也不托管数据集下载（需从上面 Google Storage 链接获取）。

Mip-NeRF 360 官方包的数据布局与 multinerf 要求的 COLMAP 格式一致：

```text
360_v2/garden/
|-- images/          # 原始分辨率图像
|-- images_2/        # 1/2 分辨率（室内场景训练常用）
|-- images_4/        # 1/4 分辨率（室外场景训练常用）
|-- images_8/        # 1/8 分辨率（可选）
|-- sparse/
|   `-- 0/
|       |-- cameras.bin
|       |-- images.bin
|       `-- points3D.bin
`-- poses_bounds.npy   # LLFF 格式（NeRF 用；3DGS 主要读 sparse/0）
```

**结论**：背景任务只需下载 `360_v2.zip`，**不必 clone multinerf**，也**不必再跑 COLMAP**。

## 3. 下载与解压（Windows PowerShell）

在仓库根目录执行：

```powershell
cd <repo-root>
mkdir data\mipnerf360
cd data\mipnerf360
```

### 3.1 方式 A：curl 下载（推荐）

```powershell
curl -L -o 360_v2.zip http://storage.googleapis.com/gresearch/refraw360/360_v2.zip
```

### 3.2 方式 B：浏览器

打开 https://jonbarron.info/mipnerf360/ ，按页面说明下载 `360_v2.zip`，放到 `data/mipnerf360/`。

### 3.3 解压

```powershell
Expand-Archive -Path 360_v2.zip -DestinationPath .
```

解压后应存在：

```text
data/mipnerf360/360_v2/garden/images/
data/mipnerf360/360_v2/garden/sparse/0/cameras.bin
```

### 3.4 只练一个场景时（省空间）

若磁盘紧张，可只保留一个场景文件夹，例如只留 `garden/`，删除其余场景目录。

## 4. 场景选择建议

| 场景 | 优点 | 缺点 | 作业推荐度 |
|------|------|------|------------|
| **garden** | 室外、层次好、融合物体效果好 | 显存占用大、训练慢 | ⭐⭐⭐ 首选 |
| **counter** | 室内、规模适中、训练较快 | 空间较封闭 | ⭐⭐⭐ 室内首选 |
| **bonsai** | 室内、最小、适合先跑通 | 场景偏小 | ⭐⭐ 练手 |
| **bicycle** | 经典 benchmark | 室外大图，显存要求高 | ⭐⭐ |
| **kitchen / room** | 室内大场景 | 训练时间较长 | ⭐⭐ |

**建议策略**：

1. 先用 `bonsai` 或 `counter` 跑通 7000 iter，确认环境 OK。
2. 再训练最终提交用的 `garden` 或 `counter`（30000 iter）。

## 5. 3DGS 环境准备

项目已克隆官方仓库：

```text
external_repos/gaussian-splatting/
```

### 5.1 Conda 环境

```powershell
cd <repo-root>/external_repos/gaussian-splatting
conda env create --file environment.yml
conda activate gaussian_splatting
```

若 PyTorch/CUDA 版本需与本机显卡匹配，可参考 [3DGS README](https://github.com/graphdeco-inria/gaussian-splatting) 的 Modifications 一节。

### 5.2 编译 CUDA 扩展

```powershell
pip install submodules/diff-gaussian-rasterization
pip install submodules/simple-knn
```

Windows 若报 `cl.exe: File not found`，需安装 Visual Studio 的「使用 C++ 的桌面开发」工作负载。

## 6. 训练背景场景

官方 `full_eval.py` 对 Mip-NeRF 360 的约定（与论文一致）：

- **室外**（`bicycle`, `garden`, `stump`, `flowers`, `treehill`）：`-i images_4`（1/4 分辨率）
- **室内**（`room`, `counter`, `kitchen`, `bonsai`）：`-i images_2`（1/2 分辨率）

### 6.1 室外示例：garden

```powershell
cd <repo-root>/external_repos/gaussian-splatting

python train.py `
    -s ../../data/mipnerf360/360_v2/garden `
    -i images_4 `
    -m ../../outputs/background_garden/3dgs `
    --iterations 30000
```

### 6.2 室内示例：counter

```powershell
python train.py `
    -s ../../data/mipnerf360/360_v2/counter `
    -i images_2 `
    -m ../../outputs/background_counter/3dgs `
    --iterations 30000
```

### 6.3 快速冒烟测试（7000 iter）

```powershell
python train.py `
    -s ../../data/mipnerf360/360_v2/bonsai `
    -i images_2 `
    -m ../../outputs/background_bonsai/3dgs_test `
    --iterations 7000
```

### 6.4 显存不足时

按优先级尝试：

1. 使用更低分辨率子目录：室外可试 `-i images_8`，室内保持 `images_2`。
2. 加 `--data_device cpu`（减显存、略变慢）。
3. 减少 `--iterations` 先验证流程。
4. 换更小场景（`bonsai` / `counter`）。
5. 使用云 GPU（AutoDL 等，作业允许）。

官方建议训练到论文质量约需 **24 GB VRAM**；`images_4` / `images_2` 是为控制分辨率设计的。

### 6.5 带 train/test 划分的评估（可选）

若需与论文对比 PSNR，加 `--eval`（Mip-NeRF 360 风格：每 8 张图留 1 张做测试）：

```powershell
python train.py `
    -s ../../data/mipnerf360/360_v2/garden `
    -i images_4 `
    -m ../../outputs/background_garden/3dgs_eval `
    --eval `
    --iterations 30000
```

作业若只要求「可漫游的背景」，**不必加 `--eval`**，用全部图像训练通常观感更好。

## 7. 渲染与检查

### 7.1 渲染训练视角

```powershell
python render.py -m ../../outputs/background_garden/3dgs
```

### 7.2 计算指标（仅在使用了 `--eval` 时有意义）

```powershell
python metrics.py -m ../../outputs/background_garden/3dgs
```

### 7.3 用 SIBR 实时查看（可选）

编译 SIBR_viewers 后：

```powershell
.\SIBR_viewers\bin\SIBR_gaussianViewer_app.exe -m ../../outputs/background_garden/3dgs
```

### 7.4 建议保存的交付物

```text
outputs/background_garden/
|-- 3dgs/
|   |-- point_cloud/iteration_30000/point_cloud.ply
|   |-- cameras.json
|   `-- cfg_args
|-- renders/
`-- notes.md
```

报告中建议包含：场景名、分辨率档位（`images_2`/`images_4`）、迭代数、GPU 型号、训练时长、渲染截图或短视频。

## 8. 与物体 A/B/C 融合的对接说明

背景 3DGS 训练完成后，将以下内容交给组员 B：

| 交付项 | 路径示例 |
|--------|----------|
| 高斯点云 | `outputs/background_garden/3dgs/point_cloud/iteration_30000/point_cloud.ply` |
| 相机参数 | `outputs/background_garden/3dgs/cameras.json` |
| 场景尺度参考 | 记录训练时 `cameras.json` 中的场景范围，便于放置物体 A/B/C |

融合时注意：

- 物体 A（3DGS）、物体 B/C（Mesh 或点云）与背景的**坐标系、尺度**需统一（常在 Blender 或自定义脚本中对齐）。
- 背景场景选 **garden（室外）** 或 **counter（室内）** 时，需与 AIGC 物体风格协调（例如室外花园放自行车/花盆比放厨房用品更自然）。

## 9. 常见问题

### 9.1 要不要运行 multinerf 或 convert.py？

- **不要**对 Mip-NeRF 360 官方包再跑 `convert.py`：数据已含 `sparse/0` 和多档 `images_*`。
- `convert.py` 仅用于**自己拍摄**、只有 `input/` 原图、还没有 COLMAP 结果的数据（见 `task1_controller_colmap_3dgs_guide.md`）。

### 9.2 训练报找不到 sparse 或 images

检查 `-s` 是否指向**场景根目录**（含 `sparse/` 和 `images_4` 的那一层），例如：

```text
.../360_v2/garden   # 正确
.../360_v2           # 错误（少一层场景名）
```

### 9.3 CUDA OOM

见 6.4 节；室外 `garden`/`bicycle` 最常见。

### 9.4 下载很慢或中断

- 使用下载工具支持断点续传。
- 或在 Linux 云主机上用 `wget` 下载后，只拷贝单个场景文件夹到本机。

## 10. 推荐执行清单

### 数据准备

- [ ] 下载 `360_v2.zip` 到 `data/mipnerf360/`
- [ ] 解压并确认目标场景含 `images/`、`images_2` 或 `images_4`、`sparse/0/`
- [ ] 选定场景并记录选择理由（室内/室外、规模）

### 训练

- [ ] `conda activate gaussian_splatting`
- [ ] 小场景 `bonsai` 7000 iter 冒烟测试
- [ ] 目标场景 30000 iter 正式训练
- [ ] `render.py` 检查无明显空洞、漂浮点

### 交付

- [ ] 导出 `point_cloud.ply` 与 `cameras.json`
- [ ] 填写 `notes.md`（参数、耗时、GPU）
- [ ] 与组员 B 对齐融合用的坐标与尺度

## 11. 参考链接

- Mip-NeRF 360 数据主页：https://jonbarron.info/mipnerf360/
- MultiNeRF 代码（NeRF，非 3DGS）：https://github.com/google-research/multinerf
- 3D Gaussian Splatting：https://github.com/graphdeco-inria/gaussian-splatting
- 本仓库手柄重建流程：`docs/task1_controller_colmap_3dgs_guide.md`
