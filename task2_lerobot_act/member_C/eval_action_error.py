from __future__ import annotations

import argparse
from pathlib import Path

import torch
from torch.utils.data import DataLoader

from calvin_act.dataset import CalvinActDataset
from calvin_act.evaluate import action_error
from calvin_act.io import write_json
from calvin_act.modeling import build_policy, config_from_dict


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--data-root", required=True)
    parser.add_argument("--splits", nargs="+", default=["splitD"])
    parser.add_argument("--output", required=True)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--num-workers", type=int, default=2)
    parser.add_argument("--max-episodes-per-split", type=int)
    parser.add_argument("--max-frames", type=int)
    parser.add_argument("--sample-stride", type=int, default=1)
    parser.add_argument("--max-batches", type=int)
    parser.add_argument("--device", default="cuda")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ckpt = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    cfg = config_from_dict(ckpt["model_config"])
    device = torch.device(args.device if args.device == "cpu" or torch.cuda.is_available() else "cpu")
    cfg.device = str(device)
    ds = CalvinActDataset(
        args.data_root,
        args.splits,
        chunk_size=cfg.chunk_size,
        image_size=cfg.image_size,
        use_wrist_image=cfg.use_wrist_image,
        max_episodes_per_split=args.max_episodes_per_split,
        max_frames=args.max_frames,
        sample_stride=args.sample_stride,
    )
    loader = DataLoader(
        ds,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=torch.cuda.is_available(),
        drop_last=False,
    )
    policy = build_policy(cfg, ckpt["stats"]).to(device)
    policy.load_state_dict(ckpt["policy"], strict=True)
    metrics = action_error(policy, loader, device, args.max_batches)
    metrics.update(
        {
            "checkpoint": str(Path(args.checkpoint).resolve()),
            "splits": args.splits,
            "frames": len(ds),
            "episodes": len(ds.episodes),
        }
    )
    write_json(args.output, metrics)
    print(metrics)


if __name__ == "__main__":
    main()
