# 组员 B 实验命令记录

本文件记录组员 B 需要运行或保留到最终报告中的关键命令。实际路径可根据本机环境调整。

已创建训练环境：

```bash
conda activate hw3_3d_train
python --version
```

当前环境路径：

```text
/opt/conda/envs/hw3_3d_train
```

## 1. threestudio 生成物体 B

### 1.1 环境准备

```bash
cd /pfs/siqingyi/code/token_credit/homework/member_B/repos/threestudio
conda activate hw3_3d_train
```

### 1.2 文本到 3D 训练：SD2.1 青花瓷花瓶

最终采用的物体 B prompt：

```text
a single small blue and white porcelain vase, one smooth rounded body, one narrow circular opening, glossy ceramic surface, cobalt floral pattern, centered object, symmetrical, studio lighting, high quality 3D asset
```

负向 Prompt：

```text
animal, face, ears, horns, legs, tail, handles, extra openings, duplicated parts, extra limbs, broken geometry, floating parts, blurry texture, noisy surface, low quality
```

复现实验命令：

```bash
CUDA_VISIBLE_DEVICES=7 /opt/conda/envs/hw3_3d_train/bin/python launch.py \
  --config configs/dreamfusion-sd.yaml \
  --train \
  --gpu 0 \
  system.prompt_processor.prompt="a single small blue and white porcelain vase, one smooth rounded body, one narrow circular opening, glossy ceramic surface, cobalt floral pattern, centered object, symmetrical, studio lighting, high quality 3D asset" \
  system.prompt_processor.negative_prompt="animal, face, ears, horns, legs, tail, handles, extra openings, duplicated parts, extra limbs, broken geometry, floating parts, blurry texture, noisy surface, low quality" \
  system.prompt_processor.pretrained_model_name_or_path="Manojb/stable-diffusion-2-1-base" \
  system.guidance.pretrained_model_name_or_path="Manojb/stable-diffusion-2-1-base" \
  name=object_B_porcelain_vase_sd21 \
  exp_root_dir="/pfs/siqingyi/code/token_credit/homework/member_B/results/object_B_threestudio" \
  trainer.max_steps=10000 \
  trainer.val_check_interval=200 \
  data.batch_size=1 \
  data.width=64 \
  data.height=64 \
  2>&1 | tee "/pfs/siqingyi/code/token_credit/homework/member_B/logs/object_B_train_v3_vase_sd21.log"
```

也可以直接运行脚本：

```bash
homework/member_B/scripts/run_object_B_train_v3_vase_sd21.sh
```

### 1.3 导出 Mesh

训练完成后导出 OBJ：

```bash
CUDA_VISIBLE_DEVICES=7 TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1 \
  homework/member_B/scripts/export_object_B_mesh.sh \
  "/pfs/siqingyi/code/token_credit/homework/member_B/results/object_B_threestudio/object_B_porcelain_vase_sd21/a_single_small_blue_and_white_porcelain_vase,_one_smooth_rounded_body,_one_narrow_circular_opening,_glossy_ceramic_surface,_cobalt_floral_pattern,_centered_object,_symmetrical,_studio_lighting,_high_quality_3D_asset@20260621-155553"
```

当前已整理出的稳定交付路径：

```text
homework/member_B/assets/object_B/object_B.obj
homework/member_B/assets/object_B/object_B_preview.png
homework/member_B/assets/object_B/object_B_turntable.mp4
homework/member_B/logs/object_B_train_v3_vase_sd21.log
```

旧的狐狸训练和中断的 v2 花瓶训练仅作为尝试记录，不作为最终物体 B 交付。

## 2. Stable-Zero123 生成物体 C

### 2.1 输入图去背景

本次物体 C 使用吉他图片。原图复制到：

```text
homework/member_B/assets/object_C/input.png
```

用户手动去除了背景、抱枕和沙发，只保留吉他，得到：

```text
homework/member_B/assets/object_C/image.png
```

`image.png` 是 RGB 图。为了让 threestudio/Stable-Zero123 正确识别透明背景，将其转换为带 alpha 通道的实际训练输入：

```text
homework/member_B/assets/object_C/input_rgba.png
```

### 2.2 下载 Stable-Zero123 权重

权重来自公开 Hugging Face 仓库 `stabilityai/stable-zero123`。最终权重路径：

```text
homework/member_B/repos/threestudio/load/zero123/stable_zero123.ckpt
```

下载命令记录：

```bash
cd /pfs/siqingyi/code/token_credit/homework/member_B/repos/threestudio/load/zero123
/opt/conda/envs/hw3_3d_train/bin/python -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='stabilityai/stable-zero123', filename='stable_zero123.ckpt', local_dir='.', local_dir_use_symlinks=False, resume_download=True)"
```

### 2.3 单图到 3D 训练

复现实验命令：

```bash
cd /pfs/siqingyi/code/token_credit/homework/member_B/repos/threestudio
CUDA_VISIBLE_DEVICES=7 TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1 \
  /opt/conda/envs/hw3_3d_train/bin/python launch.py \
  --config configs/stable-zero123.yaml \
  --train \
  --gpu 0 \
  data.image_path="/pfs/siqingyi/code/token_credit/homework/member_B/assets/object_C/input_rgba.png" \
  name=object_C_guitar_stable_zero123 \
  exp_root_dir="/pfs/siqingyi/code/token_credit/homework/member_B/results/object_C_zero123" \
  trainer.max_steps=600 \
  trainer.val_check_interval=100 \
  2>&1 | tee "/pfs/siqingyi/code/token_credit/homework/member_B/logs/object_C_zero123_train.log"
```

也可以直接运行脚本：

```bash
homework/member_B/scripts/run_object_C_stable_zero123.sh
```

### 2.4 当前稳定交付路径

```text
homework/member_B/assets/object_C/input.png
homework/member_B/assets/object_C/input_rgba.png
homework/member_B/assets/object_C/object_C_preview.png
homework/member_B/assets/object_C/object_C_turntable.mp4
homework/member_B/assets/object_C/object_C_final_val.mp4
homework/member_B/logs/object_C_zero123_train.log
homework/member_B/object_C_final_deliverables.md
```

完整输出目录：

```text
homework/member_B/results/object_C_zero123/object_C_guitar_stable_zero123/[64, 128, 256]_input_rgba.png@20260621-171641
```

当前结果满足“输入图、去背景图、生成模型、结果图、训练日志”的作业行要求，并已从 checkpoint 导出 `assets/object_C/object_C.obj` 用于最终融合。

## 3. 组员 A 资产接收

本次已接入组员 A 提供的 3DGS/Gaussian PLY：

```text
homework/assets/controller2.ply
homework/assets/counter.ply
homework/member_B/assets/object_A/controller2.ply
homework/member_B/assets/background/counter.ply
```

`controller2.ply` 作为物体 A，`counter.ply` 作为背景。二者是带 SH 颜色、opacity、scale、rotation 字段的 Gaussian PLY，融合脚本会采样 Gaussian 中心并转成彩色小点云 Mesh 进行 Blender 渲染。

## 4. Blender 融合渲染

### 4.1 Blender 环境

已下载便携版 Blender：

```text
homework/member_B/tools/blender/blender
Blender 4.5.1 LTS
```

运行时使用训练环境中的动态库：

```bash
export LD_LIBRARY_PATH=/opt/conda/envs/hw3_3d_train/lib:/pfs/siqingyi/code/token_credit/homework/member_B/tools/blender/lib:/pfs/siqingyi/code/token_credit/homework/member_B/tools/blender/lib/mesa:$LD_LIBRARY_PATH
```

### 4.2 打开 Blender 脚本渲染

```bash
LD_LIBRARY_PATH=/opt/conda/envs/hw3_3d_train/lib:/pfs/siqingyi/code/token_credit/homework/member_B/tools/blender/lib:/pfs/siqingyi/code/token_credit/homework/member_B/tools/blender/lib/mesa:$LD_LIBRARY_PATH \
  /pfs/siqingyi/code/token_credit/homework/member_B/tools/blender/blender \
  --background \
  --python homework/member_B/scripts/fuse_scene_blender.py \
  -- \
  --manifest homework/member_B/asset_manifest_clear.csv \
  --output-dir homework/member_B/renders/fusion_scene_clear \
  --resolution 1280 720 \
  --views 36 \
  --max-gaussian-points 8000 \
  --camera-radius 2.2 \
  --camera-height 0.9 \
  --target-height 0.12 \
  2>&1 | tee homework/member_B/logs/fusion_clear_render.log
```

### 4.3 合成漫游视频

```bash
ffmpeg -y -framerate 12 \
  -i homework/member_B/renders/fusion_scene_clear/view_%03d.png \
  -c:v libx264 -pix_fmt yuv420p \
  homework/member_B/renders/flythrough_clear.mp4
```

## 5. 结果文件检查

最终提交前检查：

```bash
find homework/member_B/assets -maxdepth 2 -type f
find homework/member_B/results -maxdepth 2 -type f
find homework/member_B/renders/fusion_scene -maxdepth 1 -type f
```

当前最终融合产物：

```text
homework/member_B/renders/fusion_scene_clear/fusion_scene.blend
homework/member_B/renders/fusion_scene_clear/view_000.png ... view_035.png
homework/member_B/renders/fusion_overview_clear.png
homework/member_B/renders/flythrough_clear.mp4
homework/member_B/logs/fusion_clear_render.log
```

需要保留的截图包括：

- 物体 B 的多视角预览图。
- 物体 C 的输入图、去背景图、多视角生成结果。
- Blender 融合场景截图。
- 多视角渲染图和漫游视频封面。
