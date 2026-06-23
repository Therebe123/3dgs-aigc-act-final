from __future__ import annotations

import torch
from torch.utils.data import DataLoader

from calvin_act.modeling import move_batch


@torch.no_grad()
def action_error(policy, dataloader: DataLoader, device: torch.device, max_batches: int | None = None) -> dict:
    policy.eval()
    l1_total = 0.0
    mse_total = 0.0
    count = 0
    for batch_i, batch in enumerate(dataloader):
        if max_batches is not None and batch_i >= max_batches:
            break
        batch = move_batch(batch, device)
        pred = policy.predict_action_chunk(batch)
        target = batch["action"]
        mask = ~batch["action_is_pad"]
        if mask.sum().item() == 0:
            continue
        diff = pred[mask] - target[mask]
        l1_total += diff.abs().sum().item()
        mse_total += diff.square().sum().item()
        count += diff.numel()
    if count == 0:
        return {"action_l1": float("nan"), "action_mse": float("nan"), "num_action_values": 0}
    return {
        "action_l1": l1_total / count,
        "action_mse": mse_total / count,
        "num_action_values": count,
    }
