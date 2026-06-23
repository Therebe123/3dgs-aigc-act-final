# 组员 C：题目二 ACT 跨环境泛化

基于 LeRobot `ACTPolicy`，在 CALVIN-LeRobot 数据集上比较单环境训练与多环境联合训练的 zero-shot 泛化能力。

## 实验

| 模型 | 训练数据 | 测试数据 |
|---|---|---|
| ACT-A | `splitA` | `splitD` |
| ACT-ABC | `splitA + splitB + splitC` | `splitD` |

## 主要结果（全量 splitD）

| 模型 | 训练 episode | splitD Action L1 ↓ | splitD Action MSE ↓ |
|---|---:|---:|---:|
| ACT-A | 6089 | 0.158918 | 0.090742 |
| ACT-ABC | 17870 | 0.156221 | 0.090205 |

ACT-ABC 相比 ACT-A：Action L1 相对降低约 **1.70%**，Action MSE 相对降低约 **0.59%**。

## 环境

```bash
cd task2_lerobot_act/member_C
python3 -m venv .venv
.venv/bin/pip install -U pip setuptools wheel
.venv/bin/pip install --no-deps lerobot==0.3.3
.venv/bin/pip install -r requirements.txt
export PYTHONPATH="$PWD/src"
```

或：`conda env create -f environment.yml && conda activate act-calvin`

## 数据

- [xiaoma26/calvin-lerobot](https://huggingface.co/datasets/xiaoma26/calvin-lerobot/tree/main)
- 镜像：[hf-mirror](https://hf-mirror.com/datasets/xiaoma26/calvin-lerobot/tree/main)

```bash
cd task2_lerobot_act/member_C
export PYTHONPATH="$PWD/src"
bash scripts/download_full.sh
```

数据目录：`data/calvin_lerobot/`（约 66 GB）。规模见 `artifacts/dataset_summary.json`。

## 训练与评估

```bash
cd task2_lerobot_act/member_C
export PYTHONPATH="$PWD/src"

CUDA_VISIBLE_DEVICES=0 bash scripts/train_final_full.sh
CUDA_VISIBLE_DEVICES=0 bash scripts/eval_final_full.sh
python compile_final_full_results.py
```

## 模型权重

见 [Google Drive](https://drive.google.com/drive/folders/1zq4sE9CjMhWjk5RhR1OpKe3YlPzJxqpP?usp=drive_link)（`题目二`）或 [`docs/cloud_storage.md`](../../../docs/cloud_storage.md)。

| 文件 | 说明 |
|---|---|
| `act_splitA_full_best.pt` | ACT-A 最优权重 |
| `act_jointABC_full_best.pt` | ACT-ABC 最优权重 |

下载后放入 `weights/`。

## 报告引用

| 内容 | 路径 |
|---|---|
| 数据集概览 | `artifacts/dataset_summary.json` |
| 对比曲线 | `artifacts/final_full_action_l1_compare.png` |
| 训练曲线 | `outputs/final_act_*/loss_curve.png` |
| splitD 评估 | `outputs/final_act_*/eval_splitD.json` |
| 结果汇总 | `artifacts/final_full_results.json` |
| 报告段落 | `docs/final_report_section.md` |

## 超参数

| 项目 | 设置 |
|---|---|
| Policy | LeRobot ACT (`lerobot==0.3.3`) |
| Image size | 64 × 64 |
| Chunk size | 8 |
| Backbone | ResNet-18 |
| Optimizer | AdamW, lr=1e-5 |
| Batch size | 8 |
| Max steps | 15000 |

完整配置：`configs/final_splitA_full.yaml`、`configs/final_jointABC_full.yaml`。
