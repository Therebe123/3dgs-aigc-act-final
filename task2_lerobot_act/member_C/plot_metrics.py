from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DEFAULT_COLUMNS = [
    "step",
    "epoch",
    "loss",
    "l1_loss",
    "kld_loss",
    "lr",
    "seconds",
    "val_action_l1",
    "val_action_mse",
    "val_num_action_values",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def read_metrics(path: str | Path) -> pd.DataFrame:
    with Path(path).open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    if not rows:
        return pd.DataFrame()
    header = rows[0]
    width = max([len(header), len(DEFAULT_COLUMNS)] + [len(r) for r in rows[1:]])
    columns = list(header)
    for name in DEFAULT_COLUMNS:
        if len(columns) >= width:
            break
        if name not in columns:
            columns.append(name)
    while len(columns) < width:
        columns.append(f"extra_{len(columns)}")
    normalized = [r + [""] * (width - len(r)) for r in rows[1:]]
    df = pd.DataFrame(normalized, columns=columns)
    for col in df.columns:
        converted = pd.to_numeric(df[col], errors="coerce")
        if converted.notna().any():
            df[col] = converted
    return df


def main() -> None:
    args = parse_args()
    df = read_metrics(args.metrics)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(1, 1, figsize=(8, 4.5))
    ax.plot(df["step"], df["loss"], label="train total loss", linewidth=1.6)
    if "l1_loss" in df:
        ax.plot(df["step"], df["l1_loss"], label="train Action L1", linewidth=1.6)
    if "val_action_l1" in df and df["val_action_l1"].notna().any():
        ax.plot(df["step"], df["val_action_l1"], label="splitD Action L1", marker="o", linewidth=1.6)
    ax.set_xlabel("Training step")
    ax.set_ylabel("Loss / error")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    print(out)


if __name__ == "__main__":
    main()
