# 题目二报告段落

## 基于 LeRobot ACT 的跨环境泛化实验

本实验使用助教提供的 `xiaoma26/calvin-lerobot` 数据集，比较单环境训练和多环境联合训练对 ACT 策略 zero-shot 泛化能力的影响。数据集包含 `splitA`、`splitB`、`splitC`、`splitD` 四个环境划分，其中 A/B/C 用于训练，D 作为完全未见环境用于测试。

本次运行使用本地全量 CALVIN-LeRobot 数据。基础模型 ACT-A 使用 `splitA` 的 6089 个 episode 训练；联合模型 ACT-ABC 使用 `splitA + splitB + splitC` 共 17870 个 episode 训练。两个模型均在完整 `splitD` 的 5124 个 episode、308918 帧上进行 zero-shot 动作误差评估。

方法上，我们直接调用 LeRobot 中的 `ACTPolicy`。模型输入包括主视角图像、腕部图像和 15 维机器人状态，输出为 7 维动作序列。ACT 采用 action chunking 机制，在每个观测时刻预测未来连续 8 步动作，以 Action L1 Loss 作为主要监督信号。两个模型使用相同网络结构和超参数：ResNet-18 视觉 backbone、Transformer hidden dimension 128、4 个 attention heads、1 层 encoder、1 层 decoder、AdamW 优化器、学习率 `1e-5`、batch size 8，均训练 15000 step。为避免较长训练中的数值发散，训练时关闭 AMP 并使用梯度裁剪。

实验结果如下：

| 模型 | 训练数据 | 训练 episode | Final train Action L1 ↓ | Best val Action L1 ↓ | splitD Action L1 ↓ | splitD Action MSE ↓ |
|---|---|---:|---:|---:|---:|---:|
| ACT-A | splitA | 6089 | 0.671962 | 0.154819 | 0.158918 | 0.090742 |
| ACT-ABC | splitA+B+C | 17870 | 0.465014 | 0.157630 | 0.156221 | 0.090205 |

可以看到，多环境联合训练模型 ACT-ABC 在未见环境 `splitD` 上取得了更低的动作误差。相比只在环境 A 上训练的 ACT-A，ACT-ABC 的 splitD Action L1 从 0.158918 降至 0.156221，Action MSE 从 0.090742 降至 0.090205。该结果说明，在相同模型结构和训练步数下，引入 B/C 环境能够扩展训练视觉分布，使策略在新环境中对外观、背景和物体布局变化更加鲁棒。

ACT 的 action chunking 机制对跨环境泛化有双重影响。一方面，连续动作块预测利用了短时动作序列的平滑性和结构性，相比单步动作预测更不容易产生高频抖动；另一方面，如果视觉编码在新环境中发生偏差，整个动作 chunk 都可能受到影响。因此，多环境训练对 ACT 尤其重要：它让视觉 backbone 和 Transformer 在训练阶段见过更多环境变化，从而降低视觉分布偏移对动作块预测的影响。

对应输出文件包括 `artifacts/final_full_action_l1_compare.png`、`outputs/final_act_splitA_full/loss_curve.png`、`outputs/final_act_jointABC_full/loss_curve.png`，模型权重为 `weights/act_splitA_full_best.pt` 和 `weights/act_jointABC_full_best.pt`。
