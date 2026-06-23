# 组员 A 环境说明

Member A 使用 Nerfstudio Splatfacto 进行物体 A 与背景 counter 的 3DGS 重建。训练 conda 环境为 **`nerfstudio_gs`**。

## 环境配置

| 组件 | 推荐 |
|---|---|
| Python | 3.10 |
| CUDA toolkit | 11.8 |
| PyTorch | cu118 构建 |

```bash
conda create -n nerfstudio_gs python=3.10 -y
conda activate nerfstudio_gs
conda install -y cuda-toolkit=11.8 -c nvidia
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install nerfstudio gsplat ninja opencv-python matplotlib numpy
```

## 与组员 B 环境的关系

组员 B 的 threestudio / Zero123 在独立远程 conda 环境中训练，与 Member A 的 Splatfacto 环境分离。融合阶段仅交换 Gaussian PLY。

## 第三方源码（可选）

- 官方 3DGS：`external_repos/gaussian-splatting/`（按需 clone）
- COLMAP：系统安装（按需 clone `external_repos/COLMAP/`）

Member A 主路径不依赖克隆官方 gaussian-splatting 仓库。
