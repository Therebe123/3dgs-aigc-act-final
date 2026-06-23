# 实验结果表

## 数据集概况

| Split | Scene | Episodes | Frames | 用途 |
|---|---|---:|---:|---|
| splitA | A | 6089 | 366693 | 基础训练；联合训练 |
| splitB | B | 6115 | 367096 | 联合训练 |
| splitC | C | 5666 | 337954 | 联合训练 |
| splitD | D | 5124 | 308918 | zero-shot 测试 |

## 训练设置

| 项目 | ACT-A | ACT-ABC |
|---|---:|---:|
| 训练 split | A | A+B+C |
| 训练 episode | 6089 | 17870 |
| 测试 episode | 5124 | 5124 |
| Batch size | 8 | 8 |
| Learning rate | 1e-5 | 1e-5 |
| Optimizer | AdamW | AdamW |
| Weight decay | 1e-4 | 1e-4 |
| Chunk size | 8 | 8 |
| Image size | 64 | 64 |
| Max steps | 15000 | 15000 |

## 训练结果

| 模型 | Final train loss ↓ | Final train Action L1 ↓ | Best splitD Action L1 ↓ |
|---|---:|---:|---:|
| ACT-A | 0.672136 | 0.671962 | 0.154819 |
| ACT-ABC | 0.465278 | 0.465014 | 0.157630 |

## Zero-shot 测试结果

| 模型 | 测试 split | Action L1 ↓ | Action MSE ↓ | Action values |
|---|---|---:|---:|---:|
| ACT-A | splitD | 0.158918 | 0.090742 | 16295104 |
| ACT-ABC | splitD | 0.156221 | 0.090205 | 16295104 |

## 输出文件检查

| 文件 | 状态 |
|---|---|
| `outputs/final_act_splitA_full/checkpoints/best.pt` | 存在 |
| `outputs/final_act_jointABC_full/checkpoints/best.pt` | 存在 |
| `outputs/final_act_splitA_full/train_metrics.csv` | 存在 |
| `outputs/final_act_jointABC_full/train_metrics.csv` | 存在 |
| `outputs/final_act_splitA_full/eval_splitD.json` | 存在 |
| `outputs/final_act_jointABC_full/eval_splitD.json` | 存在 |
| `outputs/final_act_splitA_full/loss_curve.png` | 存在 |
| `outputs/final_act_jointABC_full/loss_curve.png` | 存在 |
| `artifacts/final_full_action_l1_compare.png` | 存在 |

模型权重：

```text
act_splitA_full_best.pt
act_jointABC_full_best.pt
```
