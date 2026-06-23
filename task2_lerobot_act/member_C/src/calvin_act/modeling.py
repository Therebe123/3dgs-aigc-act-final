from __future__ import annotations

import random
from dataclasses import asdict, dataclass

import numpy as np
import torch

from lerobot.configs.types import FeatureType, PolicyFeature
from lerobot.policies.act.configuration_act import ACTConfig
from lerobot.policies.act.modeling_act import ACTPolicy


@dataclass
class ActModelConfig:
    image_size: int = 96
    state_dim: int = 15
    action_dim: int = 7
    chunk_size: int = 16
    n_action_steps: int = 16
    use_wrist_image: bool = True
    vision_backbone: str = "resnet18"
    pretrained_backbone_weights: str | None = None
    dim_model: int = 256
    n_heads: int = 8
    dim_feedforward: int = 1024
    n_encoder_layers: int = 2
    n_decoder_layers: int = 1
    use_vae: bool = True
    latent_dim: int = 32
    n_vae_encoder_layers: int = 2
    kl_weight: float = 10.0
    dropout: float = 0.1
    optimizer_lr: float = 1e-5
    optimizer_lr_backbone: float = 1e-5
    optimizer_weight_decay: float = 1e-4
    device: str = "cuda"
    use_amp: bool = False


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def build_config(cfg: ActModelConfig) -> ACTConfig:
    img_shape = (3, cfg.image_size, cfg.image_size)
    input_features = {
        "observation.images.primary": PolicyFeature(type=FeatureType.VISUAL, shape=img_shape),
        "observation.state": PolicyFeature(type=FeatureType.STATE, shape=(cfg.state_dim,)),
    }
    if cfg.use_wrist_image:
        input_features["observation.images.wrist"] = PolicyFeature(type=FeatureType.VISUAL, shape=img_shape)
    return ACTConfig(
        input_features=input_features,
        output_features={"action": PolicyFeature(type=FeatureType.ACTION, shape=(cfg.action_dim,))},
        chunk_size=cfg.chunk_size,
        n_action_steps=cfg.n_action_steps,
        vision_backbone=cfg.vision_backbone,
        pretrained_backbone_weights=cfg.pretrained_backbone_weights,
        dim_model=cfg.dim_model,
        n_heads=cfg.n_heads,
        dim_feedforward=cfg.dim_feedforward,
        n_encoder_layers=cfg.n_encoder_layers,
        n_decoder_layers=cfg.n_decoder_layers,
        use_vae=cfg.use_vae,
        latent_dim=cfg.latent_dim,
        n_vae_encoder_layers=cfg.n_vae_encoder_layers,
        kl_weight=cfg.kl_weight,
        dropout=cfg.dropout,
        optimizer_lr=cfg.optimizer_lr,
        optimizer_lr_backbone=cfg.optimizer_lr_backbone,
        optimizer_weight_decay=cfg.optimizer_weight_decay,
        device=cfg.device,
        use_amp=cfg.use_amp,
        push_to_hub=False,
    )


def build_policy(cfg: ActModelConfig, stats: dict[str, dict[str, torch.Tensor]]) -> ACTPolicy:
    return ACTPolicy(build_config(cfg), dataset_stats=stats)


def config_to_dict(cfg: ActModelConfig) -> dict:
    return asdict(cfg)


def config_from_dict(data: dict) -> ActModelConfig:
    valid = {f.name for f in ActModelConfig.__dataclass_fields__.values()}
    return ActModelConfig(**{k: v for k, v in data.items() if k in valid})


def move_batch(batch: dict, device: torch.device) -> dict:
    return {k: v.to(device, non_blocking=True) if torch.is_tensor(v) else v for k, v in batch.items()}
