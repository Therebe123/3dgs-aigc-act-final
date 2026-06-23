# Cloud Storage — Member C

Checkpoint 位于 Drive `题目二`：[3DGS_AIGC_ACT](https://drive.google.com/drive/folders/1zq4sE9CjMhWjk5RhR1OpKe3YlPzJxqpP?usp=drive_link)

总清单：[`docs/cloud_storage.md`](../../../docs/cloud_storage.md)

| 文件 | 下载后路径 |
|---|---|
| `act_splitA_full_best.pt` | `weights/act_splitA_full_best.pt` |
| `act_jointABC_full_best.pt` | `weights/act_jointABC_full_best.pt` |
| `train_metrics_splitA.csv`（可选） | `outputs/final_act_splitA_full/train_metrics.csv` |
| `train_metrics_jointABC.csv`（可选） | `outputs/final_act_jointABC_full/train_metrics.csv` |

数据集（~66 GB）从 Hugging Face 下载，见 `scripts/download_full.sh`。

评估 JSON、loss 曲线等轻量结果在 `artifacts/` 与 `outputs/`。
