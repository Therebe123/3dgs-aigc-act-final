# 组员 A 实验命令记录

本文件记录组员 A 需要运行或保留到最终报告中的关键命令。所有路径默认从仓库根目录 `3dgs-aigc-act-final/` 出发。可直接运行 `scripts/` 下脚本，或复制下方命令。

实际训练框架：**Nerfstudio Splatfacto**（conda 环境 `nerfstudio_gs`）。

## 1. 环境准备

```powershell
conda activate nerfstudio_gs
cd <path-to>/3dgs-aigc-act-final
python -c "import nerfstudio, gsplat, torch; print('nerfstudio ok'); print(torch.__version__, torch.cuda.is_available())"
```

Linux 服务器参考 `docs/environment.md`。

## 2. COLMAP：物体 A 位姿估计

### 2.1 GUI 方式（已使用）

见 `docs/capture_notes.md`。COLMAP 工程路径（仓库内）：

- Database: `outputs/object_A_controller/colmap/database.db`
- Images: `data/object_A_controller/images/`
- Sparse export: `outputs/object_A_controller/colmap/sparse/0`

### 2.2 CLI 方式（可复现）

```powershell
mkdir -Force outputs/object_A_controller/colmap/sparse

colmap feature_extractor `
    --database_path outputs/object_A_controller/colmap/database.db `
    --image_path data/object_A_controller/images `
    --ImageReader.camera_model SIMPLE_RADIAL `
    --SiftExtraction.use_gpu 1

colmap exhaustive_matcher `
    --database_path outputs/object_A_controller/colmap/database.db `
    --SiftMatching.use_gpu 1

colmap mapper `
    --database_path outputs/object_A_controller/colmap/database.db `
    --image_path data/object_A_controller/images `
    --output_path outputs/object_A_controller/colmap/sparse

colmap model_converter `
    --input_path outputs/object_A_controller/colmap/sparse/0 `
    --output_path outputs/object_A_controller/colmap/sparse_points.ply `
    --output_type PLY
```

### 2.3 整理为 Splatfacto 输入

Nerfstudio `colmap` dataparser 期望：

```text
data/object_A_controller/
├── images/          # 或 input/
└── sparse/0/
    ├── cameras.bin
    ├── images.bin
    └── points3D.bin
```

若 COLMAP 输出在其他目录，复制到仓库内布局：

```powershell
mkdir -Force data/object_A_controller/images, data/object_A_controller/sparse/0
Copy-Item <your-colmap-images>\* data/object_A_controller/images/
Copy-Item <your-colmap-sparse-0>\* data/object_A_controller/sparse/0/
```

或从 Google Drive `题目一` 下载 `member_A_training_data.zip` 解压到 `data/object_A_controller/`。

## 3. Splatfacto 训练：物体 A（controller）

正式训练：**30000 iterations**。

脚本：`scripts/train_object_A_splatfacto_windows.bat`（Windows）或 `scripts/train_object_A_splatfacto_linux.sh`（Linux）。

### 3.1 Windows

```powershell
conda activate nerfstudio_gs
cd <path-to>/3dgs-aigc-act-final

ns-train splatfacto `
  --max-num-iterations 30000 `
  --output-dir outputs/object_A_controller/nerfstudio_splatfacto `
  --experiment-name controller `
  --vis viewer `
  colmap `
  --data data/object_A_controller `
  --images-path images `
  --colmap-path sparse/0 `
  --downscale-factor 1
```

### 3.2 Linux

```bash
conda activate nerfstudio_gs
cd <path-to>/3dgs-aigc-act-final

ns-train splatfacto \
  --max-num-iterations 30000 \
  --output-dir outputs/object_A_controller/nerfstudio_splatfacto \
  --experiment-name controller \
  --vis viewer \
  colmap \
  --data data/object_A_controller \
  --images-path images \
  --colmap-path sparse/0 \
  --downscale-factor 1
```

训练完成后 config 位于：

```text
outputs/object_A_controller/nerfstudio_splatfacto/controller/splatfacto/<timestamp>/config.yml
```

参考配置：`member_A/outputs/configs/splatfacto_controller_2026-06-19/`。

## 4. Splatfacto 训练：背景 counter

数据目录：`data/background_scene/mipnerf360/counter`（Mip-NeRF 360 counter，自带 COLMAP）。

脚本：`scripts/train_background_counter_splatfacto_linux.sh`。

```bash
conda activate nerfstudio_gs
cd <path-to>/3dgs-aigc-act-final

ns-train splatfacto \
  --max-num-iterations 30000 \
  --output-dir outputs/background_scene/counter_splatfacto \
  --experiment-name counter \
  --vis viewer \
  colmap \
  --data data/background_scene/mipnerf360/counter \
  --images-path images \
  --colmap-path sparse/0 \
  --downscale-factor 1
```

下载与数据准备见 `docs/background_counter_3dgs_guide.md`。

## 5. 导出 Gaussian PLY

将 `<timestamp>` 替换为训练输出目录中的实际时间戳。

脚本：`scripts/export_gaussian_splat_windows.bat` 或 `scripts/export_gaussian_splat.sh`（通过 `LOAD_CONFIG` 和 `OUTPUT_DIR` 环境变量指定路径）。

### 5.1 物体 A → controller2.ply

```powershell
conda activate nerfstudio_gs
cd <path-to>/3dgs-aigc-act-final

ns-export gaussian-splat `
  --load-config outputs/object_A_controller/nerfstudio_splatfacto/controller/splatfacto/<timestamp>/config.yml `
  --output-dir outputs/object_A_controller/exports/controller_gaussian_splat
```

导出文件通常命名为 `splat.ply`，交付前重命名为 `controller2.ply`。

### 5.2 背景 → counter.ply

```powershell
ns-export gaussian-splat `
  --load-config outputs/background_scene/counter_splatfacto/counter/splatfacto/<timestamp>/config.yml `
  --output-dir outputs/background_scene/exports/counter_gaussian_splat
```

交付前重命名为 `counter.ply`。

## 6. 交付给组员 B

将导出的 PLY 复制到组员 B 资产目录：

```powershell
mkdir -Force task1_3dgs_aigc/member_B/assets/object_A, task1_3dgs_aigc/member_B/assets/background
Copy-Item outputs/object_A_controller/exports/controller_gaussian_splat/controller2.ply task1_3dgs_aigc/member_B/assets/object_A/
Copy-Item outputs/background_scene/exports/counter_gaussian_splat/counter.ply task1_3dgs_aigc/member_B/assets/background/
```

或在网盘上传后，由组员 B 按 `docs/asset_manifest.csv` 下载。

## 7. 查看融合结果

解压后的融合场景由组员 B 提供，可用 SuperSplat 打开：

```bash
gzip -d -k task1_3dgs_aigc/member_B/outputs/renders/fused_scene_gaussian_clean_candidate_guitar_floor_v3.ply.gz
```
