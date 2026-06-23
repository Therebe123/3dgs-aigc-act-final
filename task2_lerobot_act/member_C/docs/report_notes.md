# 题目二report_notes

## 任务背景

本实验关注视觉-动作策略在跨环境场景中的泛化能力。CALVIN 数据集包含多个具有不同视觉外观和物体布局的环境划分，本实验将环境 A 作为单环境训练集，将环境 A、B、C 作为多环境联合训练集，并统一在未见过的环境 D 上进行 zero-shot 测试。对比目标是判断多环境训练是否能缓解视觉分布偏移，并提升 ACT 策略在新环境中的动作预测稳定性。

## 数据集描述

实验使用助教提供的 `xiaoma26/calvin-lerobot` 数据集。该数据集采用 LeRobot v2.1 格式，每个 episode 以 Parquet 文件存储，主要字段包括：

| 字段 | 含义 | 形状 |
|---|---|---|
| `image` | 主视角 RGB 图像 | 200 x 200 x 3 |
| `wrist_image` | 腕部相机 RGB 图像 | 84 x 84 x 3 |
| `state` | 机器人状态 | 15 |
| `actions` | 末端控制动作 | 7 |
| `task_index` | 任务编号 | 1 |

各 split 的规模和用途如下：

| Split | 环境 | Episodes | Frames | 用途 |
|---|---|---:|---:|---|
| `splitA` | A | 6089 | 366693 | 基础 ACT 训练；联合训练 |
| `splitB` | B | 6115 | 367096 | 多环境联合训练 |
| `splitC` | C | 5666 | 337954 | 多环境联合训练 |
| `splitD` | D | 5124 | 308918 | zero-shot 测试 |

## 方法

本实验基于 LeRobot 中的 Action Chunking Transformer。ACT 不直接预测单步动作，而是在每个观测时刻预测未来一段动作序列。设当前观测为 $o_t$，策略输出为：

$$
\hat{a}_{t:t+H-1} = \pi_{\theta}(o_t)
$$

其中 $H$ 为 action chunk 长度。本实验设置 $H=8$。训练时使用未来 8 步动作作为监督信号，对 padding 位置进行 mask，并以 Action L1 Loss 作为主要训练指标：

$$
\mathcal{L}_{L1}=\frac{1}{N}\sum ||a_{t:t+H-1}-\hat{a}_{t:t+H-1}||_1
$$

默认配置中使用主视角图像、腕部图像和机器人状态作为输入。两路图像统一 resize 后输入 ResNet-18 backbone；状态向量经过线性层投影后与图像 token、latent token 一起进入 Transformer。ACT 的 VAE 分支在训练阶段对动作 chunk 进行编码，损失包含动作重建误差和 KL 正则项。

本次运行采用 CALVIN-LeRobot 本地全量数据。基础模型 ACT-A 使用 `splitA` 的 6089 个 episode 训练；联合模型 ACT-ABC 使用 `splitA + splitB + splitC` 共 17870 个 episode 训练。两个模型均在完整 `splitD` 的 5124 个 episode 上进行 zero-shot 动作误差评估，并保持完全相同的网络结构与超参数。

## 实验设计

实验包含两个模型：

| 模型 | 训练数据 | 测试数据 | 目的 |
|---|---|---|---|
| ACT-A | `splitA` | `splitD` | 检验单环境训练的 zero-shot 泛化 |
| ACT-ABC | `splitA + splitB + splitC` | `splitD` | 检验多环境联合训练的 zero-shot 泛化 |

两个模型使用相同网络结构、优化器和训练超参数，仅改变训练数据来源。这样可以尽量将差异归因于训练环境多样性。

## 超参数设置

| 超参数 | 数值 |
|---|---|
| Policy | LeRobot ACT |
| Image size | 64 x 64 |
| State dim | 15 |
| Action dim | 7 |
| Chunk size | 8 |
| Vision backbone | ResNet-18 |
| Transformer hidden dim | 128 |
| Attention heads | 4 |
| Encoder layers | 1 |
| Decoder layers | 1 |
| VAE encoder layers | 1 |
| Latent dim | 32 |
| Optimizer | AdamW |
| Learning rate | 1e-5 |
| Weight decay | 1e-4 |
| Batch size | 8 |
| Max steps | 15000 |
| Main train metric | Action L1 Loss |
| Zero-shot metric | Action L1 / MSE on splitD |

## 结果记录

测试指标来自：

```text
outputs/final_act_splitA_full/eval_splitD.json
outputs/final_act_jointABC_full/eval_splitD.json
```

结果表如下：

| 模型 | 训练环境 | 训练 episode | splitD 测试 episode | splitD Action L1 ↓ | splitD Action MSE ↓ |
|---|---|---:|---:|---:|---:|
| ACT-A | A | 6089 | 5124 | 0.158918 | 0.090742 |
| ACT-ABC | A+B+C | 17870 | 5124 | 0.156221 | 0.090205 |

从结果看，ACT-ABC 在未见环境 D 上的 Action L1 和 MSE 均低于 ACT-A，说明多环境联合训练不仅降低了平均绝对动作偏差，也减少了平方误差意义下的大偏差。整体上，多环境训练带来了更好的跨环境鲁棒性。

## 现象分析口径

ACT-ABC 在 splitD 上的 Action L1 更低，可以说明多环境联合训练提升了视觉外观和任务布局变化下的鲁棒性。环境 A、B、C 提供了更多背景、物体位置和视觉纹理变化，使策略更不容易依赖单一环境中的偶然视觉线索。相比之下，ACT-A 只见过环境 A，容易在环境 D 中出现状态估计偏差，从而导致动作 chunk 中连续多步动作同时偏离。

联合训练集包含多个环境，视觉分布更宽，优化初期的样本方差更大，因此训练中局部验证指标不一定始终优于单环境模型。但完整 splitD 评估显示 ACT-ABC 的动作误差更低，说明模型牺牲了一部分单环境拟合速度，换来了更好的跨环境泛化能力。

ACT 的 Action Chunking 机制在跨环境视觉偏移下具有两面性。一方面，chunk 预测可以利用短时动作序列的结构，使输出更平滑，减少单步误差积累；另一方面，如果当前视觉观测被错误解释，整个 chunk 都可能受到影响。因此在多环境训练下，ACT 的优势更容易体现，因为模型见过更丰富的视觉变化，输出动作序列更稳定。

## 代码复现命令

```bash
cd task2_lerobot_act/member_C
export PYTHONPATH="$PWD/src"

bash scripts/download_full.sh
CUDA_VISIBLE_DEVICES=0 bash scripts/train_final_full.sh
CUDA_VISIBLE_DEVICES=0 bash scripts/eval_final_full.sh
python compile_final_full_results.py
```
