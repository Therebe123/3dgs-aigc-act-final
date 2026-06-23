from __future__ import annotations

import math

import numpy as np
import torch
from torch.utils.data import Dataset


def estimate_stats(dataset: Dataset, max_samples: int = 1000) -> dict[str, dict[str, torch.Tensor]]:
    n = min(len(dataset), int(max_samples))
    if n <= 0:
        raise ValueError("Cannot estimate stats from an empty dataset")
    indices = np.linspace(0, len(dataset) - 1, n, dtype=np.int64)
    sums: dict[str, torch.Tensor] = {}
    sums_sq: dict[str, torch.Tensor] = {}
    counts: dict[str, int] = {}

    def add(key: str, values: torch.Tensor) -> None:
        flat = values.detach().float()
        if key.startswith("observation.images."):
            flat = flat.view(3, -1).mean(dim=1)
            sq = flat.square()
            cnt = 1
        else:
            flat = flat.reshape(-1, flat.shape[-1])
            sq = flat.square()
            cnt = flat.shape[0]
            flat = flat.sum(dim=0)
            sq = sq.sum(dim=0)
        sums[key] = sums.get(key, torch.zeros_like(flat)) + flat
        sums_sq[key] = sums_sq.get(key, torch.zeros_like(sq)) + sq
        counts[key] = counts.get(key, 0) + cnt

    for idx in indices:
        item = dataset[int(idx)]
        add("observation.state", item["observation.state"])
        mask = ~item["action_is_pad"]
        add("action", item["action"][mask])
        for key, value in item.items():
            if key.startswith("observation.images."):
                add(key, value)

    stats: dict[str, dict[str, torch.Tensor]] = {}
    for key in sums:
        mean = sums[key] / max(counts[key], 1)
        var = sums_sq[key] / max(counts[key], 1) - mean.square()
        std = torch.sqrt(torch.clamp(var, min=1e-6))
        if key.startswith("observation.images."):
            mean = mean.view(3, 1, 1)
            std = std.view(3, 1, 1)
        stats[key] = {"mean": mean.float(), "std": std.float()}
    for key, value in list(stats.items()):
        if torch.isnan(value["mean"]).any() or torch.isnan(value["std"]).any():
            raise FloatingPointError(f"Invalid stats for {key}")
        if math.isclose(float(value["std"].mean()), 0.0):
            value["std"] = value["std"] + 1e-3
    return stats
