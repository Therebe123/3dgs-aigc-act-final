from __future__ import annotations

import json
import shutil
from pathlib import Path

import matplotlib.pyplot as plt

from plot_metrics import read_metrics


ROOT = Path(__file__).resolve().parent
RUNS = {
    "ACT-A": ROOT / "outputs" / "final_act_splitA_full",
    "ACT-ABC": ROOT / "outputs" / "final_act_jointABC_full",
}


def last_valid(series):
    valid = series.dropna()
    return None if valid.empty else float(valid.iloc[-1])


def split_episode_count(split: str) -> int:
    return len(list((ROOT / "data" / "calvin_lerobot" / split / "data").glob("chunk-*/*.parquet")))


def main() -> None:
    rows = []
    for name, run_dir in RUNS.items():
        metrics = read_metrics(run_dir / "train_metrics.csv")
        eval_data = json.loads((run_dir / "eval_splitD.json").read_text(encoding="utf-8"))
        train_episodes = split_episode_count("splitA")
        train_split = "splitA"
        if name == "ACT-ABC":
            train_episodes = sum(split_episode_count(s) for s in ["splitA", "splitB", "splitC"])
            train_split = "splitA+splitB+splitC"
        rows.append(
            {
                "model": name,
                "train_split": train_split,
                "train_episodes": train_episodes,
                "test_episodes": eval_data["episodes"],
                "final_train_loss": last_valid(metrics["loss"]),
                "final_train_l1": last_valid(metrics["l1_loss"]),
                "best_val_l1": float(metrics["val_action_l1"].dropna().min()),
                "splitD_action_l1": eval_data["action_l1"],
                "splitD_action_mse": eval_data["action_mse"],
                "splitD_frames": eval_data["frames"],
                "splitD_episodes": eval_data["episodes"],
                "checkpoint": str(run_dir / "checkpoints" / "best.pt"),
            }
        )

    artifacts = ROOT / "artifacts"
    artifacts.mkdir(exist_ok=True)
    (artifacts / "final_full_results.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    fig, ax = plt.subplots(1, 1, figsize=(8.4, 4.8))
    for name, run_dir in RUNS.items():
        metrics = read_metrics(run_dir / "train_metrics.csv")
        ax.plot(metrics["step"], metrics["l1_loss"], label=f"{name} train Action L1", linewidth=1.1, alpha=0.75)
        val = metrics.dropna(subset=["val_action_l1"])
        ax.plot(val["step"], val["val_action_l1"], marker="o", linewidth=1.5, label=f"{name} splitD Action L1")
    ax.set_xlabel("Training step")
    ax.set_ylabel("Action L1")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(artifacts / "final_full_action_l1_compare.png", dpi=220)

    weights = ROOT / "weights"
    weights.mkdir(exist_ok=True)
    shutil.copy2(RUNS["ACT-A"] / "checkpoints" / "best.pt", weights / "act_splitA_full_best.pt")
    shutil.copy2(RUNS["ACT-ABC"] / "checkpoints" / "best.pt", weights / "act_jointABC_full_best.pt")

    md = [
        "# Final ACT Results - Full Dataset",
        "",
        "实验采用 CALVIN-LeRobot 四个 split 的本地全量数据。两个模型使用相同网络结构和超参数，只改变训练 split。",
        "",
        "| 模型 | 训练数据 | 训练 episode | splitD 测试 episode | Final train Action L1 ↓ | Best val Action L1 ↓ | splitD Action L1 ↓ | splitD Action MSE ↓ |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        md.append(
            f"| {row['model']} | {row['train_split']} | {row['train_episodes']} | {row['test_episodes']} | "
            f"{row['final_train_l1']:.6f} | {row['best_val_l1']:.6f} | "
            f"{row['splitD_action_l1']:.6f} | {row['splitD_action_mse']:.6f} |"
        )
    md.extend(
        [
            "",
            "相关文件：",
            "",
            "- `artifacts/final_full_action_l1_compare.png`",
            "- `weights/act_splitA_full_best.pt`",
            "- `weights/act_jointABC_full_best.pt`",
            "- `outputs/final_act_splitA_full/eval_splitD.json`",
            "- `outputs/final_act_jointABC_full/eval_splitD.json`",
        ]
    )
    (ROOT / "docs" / "final_full_results.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
