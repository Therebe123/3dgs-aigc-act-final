from __future__ import annotations

import argparse
import time
from pathlib import Path

import torch
from torch.utils.data import DataLoader

from calvin_act.dataset import CalvinActDataset, describe_local_splits
from calvin_act.evaluate import action_error
from calvin_act.io import append_csv, load_yaml, save_checkpoint, write_json
from calvin_act.modeling import ActModelConfig, build_policy, config_from_dict, config_to_dict, move_batch, set_seed
from calvin_act.stats import estimate_stats


def parse_args() -> argparse.Namespace:
    base = argparse.ArgumentParser(add_help=False)
    base.add_argument("--config")
    known, _ = base.parse_known_args()
    defaults = load_yaml(known.config)
    parser = argparse.ArgumentParser()
    parser.add_argument("--config")
    parser.add_argument("--run-name")
    parser.add_argument("--data-root")
    parser.add_argument("--splits", nargs="+")
    parser.add_argument("--val-splits", nargs="+")
    parser.add_argument("--output-dir")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--batch-size", type=int)
    parser.add_argument("--num-workers", type=int)
    parser.add_argument("--epochs", type=int)
    parser.add_argument("--max-steps", type=int)
    parser.add_argument("--max-episodes-per-split", type=int)
    parser.add_argument("--max-frames", type=int)
    parser.add_argument("--sample-stride", type=int)
    parser.add_argument("--stats-samples", type=int)
    parser.add_argument("--eval-every", type=int)
    parser.add_argument("--eval-batches", type=int)
    parser.add_argument("--save-every", type=int)
    parser.add_argument("--device")
    parser.add_argument("--use-amp", action="store_true")
    parser.add_argument("--image-size", type=int)
    parser.add_argument("--chunk-size", type=int)
    parser.add_argument("--use-wrist-image", action="store_true")
    parser.add_argument("--no-wrist-image", action="store_true")
    parser.add_argument("--dim-model", type=int)
    parser.add_argument("--n-heads", type=int)
    parser.add_argument("--dim-feedforward", type=int)
    parser.add_argument("--n-encoder-layers", type=int)
    parser.add_argument("--n-decoder-layers", type=int)
    parser.add_argument("--n-vae-encoder-layers", type=int)
    parser.add_argument("--learning-rate", type=float)
    parser.add_argument("--weight-decay", type=float)
    parser.add_argument("--grad-clip-norm", type=float)
    parser.add_argument("--pretrained-backbone-weights")
    parser.set_defaults(**defaults)
    args = parser.parse_args()
    if args.no_wrist_image:
        args.use_wrist_image = False
    return args


def model_cfg_from_args(args: argparse.Namespace) -> ActModelConfig:
    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    return ActModelConfig(
        image_size=args.image_size,
        chunk_size=args.chunk_size,
        n_action_steps=args.chunk_size,
        use_wrist_image=args.use_wrist_image,
        dim_model=args.dim_model,
        n_heads=args.n_heads,
        dim_feedforward=args.dim_feedforward,
        n_encoder_layers=args.n_encoder_layers,
        n_decoder_layers=args.n_decoder_layers,
        n_vae_encoder_layers=args.n_vae_encoder_layers,
        optimizer_lr=args.learning_rate,
        optimizer_lr_backbone=args.learning_rate,
        optimizer_weight_decay=args.weight_decay,
        pretrained_backbone_weights=args.pretrained_backbone_weights,
        device=device,
        use_amp=args.use_amp,
    )


def main() -> None:
    args = parse_args()
    set_seed(args.seed)
    output_dir = Path(args.output_dir) / args.run_name
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "run_config.json", vars(args))
    write_json(output_dir / "data_summary.json", {"splits": describe_local_splits(args.data_root, args.splits)})

    train_ds = CalvinActDataset(
        args.data_root,
        args.splits,
        chunk_size=args.chunk_size,
        image_size=args.image_size,
        use_wrist_image=args.use_wrist_image,
        max_episodes_per_split=args.max_episodes_per_split,
        max_frames=args.max_frames,
        sample_stride=args.sample_stride,
    )
    train_loader = DataLoader(
        train_ds,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.num_workers,
        pin_memory=torch.cuda.is_available(),
        drop_last=True,
    )
    val_loader = None
    if args.val_splits:
        val_ds = CalvinActDataset(
            args.data_root,
            args.val_splits,
            chunk_size=args.chunk_size,
            image_size=args.image_size,
            use_wrist_image=args.use_wrist_image,
            max_episodes_per_split=args.max_episodes_per_split,
            max_frames=args.max_frames,
            sample_stride=args.sample_stride,
        )
        val_loader = DataLoader(
            val_ds,
            batch_size=args.batch_size,
            shuffle=False,
            num_workers=args.num_workers,
            pin_memory=torch.cuda.is_available(),
            drop_last=False,
        )

    model_cfg = model_cfg_from_args(args)
    stats = estimate_stats(train_ds, args.stats_samples)
    device = torch.device(model_cfg.device if model_cfg.device == "cpu" or torch.cuda.is_available() else "cpu")
    model_cfg.device = str(device)
    policy = build_policy(model_cfg, stats).to(device)
    optimizer = torch.optim.AdamW(policy.get_optim_params(), lr=args.learning_rate, weight_decay=args.weight_decay)
    scaler = torch.amp.GradScaler("cuda", enabled=bool(args.use_amp and device.type == "cuda"))

    metrics_path = output_dir / "train_metrics.csv"
    best_val = float("inf")
    step = 0
    start = time.time()

    for epoch in range(args.epochs):
        policy.train()
        for batch in train_loader:
            step += 1
            batch = move_batch(batch, device)
            optimizer.zero_grad(set_to_none=True)
            with torch.amp.autocast("cuda", enabled=bool(args.use_amp and device.type == "cuda")):
                loss, loss_dict = policy(batch)
            if not torch.isfinite(loss):
                raise FloatingPointError(f"Non-finite loss at step {step}: {loss_dict}")
            scaler.scale(loss).backward()
            if args.grad_clip_norm:
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(policy.parameters(), args.grad_clip_norm)
            scaler.step(optimizer)
            scaler.update()

            row = {
                "step": step,
                "epoch": epoch,
                "loss": float(loss.item()),
                "l1_loss": float(loss_dict.get("l1_loss", 0.0)),
                "kld_loss": float(loss_dict.get("kld_loss", 0.0)),
                "lr": optimizer.param_groups[0]["lr"],
                "seconds": round(time.time() - start, 3),
                "val_action_l1": None,
                "val_action_mse": None,
                "val_num_action_values": None,
            }
            if val_loader is not None and args.eval_every and step % args.eval_every == 0:
                val = action_error(policy, val_loader, device, args.eval_batches)
                row.update({f"val_{k}": v for k, v in val.items()})
                if val["action_l1"] < best_val:
                    best_val = val["action_l1"]
                    save_checkpoint(
                        output_dir / "checkpoints" / "best.pt",
                        {
                            "policy": policy.state_dict(),
                            "stats": stats,
                            "model_config": config_to_dict(model_cfg),
                            "args": vars(args),
                            "step": step,
                            "best_val_action_l1": best_val,
                        },
                    )
                policy.train()
            append_csv(metrics_path, row)

            if args.save_every and step % args.save_every == 0:
                save_checkpoint(
                    output_dir / "checkpoints" / f"step_{step:07d}.pt",
                    {
                        "policy": policy.state_dict(),
                        "optimizer": optimizer.state_dict(),
                        "stats": stats,
                        "model_config": config_to_dict(model_cfg),
                        "args": vars(args),
                        "step": step,
                    },
                )
            if args.max_steps and step >= args.max_steps:
                break
        if args.max_steps and step >= args.max_steps:
            break

    save_checkpoint(
        output_dir / "checkpoints" / "last.pt",
        {
            "policy": policy.state_dict(),
            "optimizer": optimizer.state_dict(),
            "stats": stats,
            "model_config": config_to_dict(model_cfg),
            "args": vars(args),
            "step": step,
            "best_val_action_l1": best_val,
        },
    )
    if not (output_dir / "checkpoints" / "best.pt").exists():
        save_checkpoint(
            output_dir / "checkpoints" / "best.pt",
            {
                "policy": policy.state_dict(),
                "stats": stats,
                "model_config": config_to_dict(model_cfg),
                "args": vars(args),
                "step": step,
                "best_val_action_l1": best_val,
            },
        )


if __name__ == "__main__":
    main()
