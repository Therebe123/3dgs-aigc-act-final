# Final ACT Results - Full Dataset

实验采用 CALVIN-LeRobot 四个 split 的本地全量数据。两个模型使用相同网络结构和超参数，只改变训练 split。

| 模型 | 训练数据 | 训练 episode | splitD 测试 episode | Final train Action L1 ↓ | Best val Action L1 ↓ | splitD Action L1 ↓ | splitD Action MSE ↓ |
|---|---|---:|---:|---:|---:|---:|---:|
| ACT-A | splitA | 6089 | 5124 | 0.671962 | 0.154819 | 0.158918 | 0.090742 |
| ACT-ABC | splitA+splitB+splitC | 17870 | 5124 | 0.465014 | 0.157630 | 0.156221 | 0.090205 |

相关文件：

- `artifacts/final_full_action_l1_compare.png`
- `weights/act_splitA_full_best.pt`
- `weights/act_jointABC_full_best.pt`
- `outputs/final_act_splitA_full/eval_splitD.json`
- `outputs/final_act_jointABC_full/eval_splitD.json`
