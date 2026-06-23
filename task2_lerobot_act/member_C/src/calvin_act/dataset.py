from __future__ import annotations

import io
import json
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from PIL import Image
from torch.utils.data import Dataset


@dataclass(frozen=True)
class EpisodeRef:
    split: str
    episode_index: int
    length: int
    path: Path


def read_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def episode_path(split_dir: Path, episode_index: int, chunks_size: int = 1000) -> Path:
    chunk = episode_index // chunks_size
    return split_dir / "data" / f"chunk-{chunk:03d}" / f"episode_{episode_index:06d}.parquet"


def decode_image(value, image_size: int) -> torch.Tensor:
    if isinstance(value, dict):
        if value.get("bytes") is not None:
            img = Image.open(io.BytesIO(value["bytes"]))
        elif value.get("path") is not None:
            img = Image.open(value["path"])
        else:
            raise ValueError("Unsupported image dictionary")
    elif isinstance(value, Image.Image):
        img = value
    elif isinstance(value, np.ndarray):
        img = Image.fromarray(value)
    else:
        raise TypeError(f"Unsupported image value: {type(value)}")

    img = img.convert("RGB").resize((image_size, image_size), Image.BILINEAR)
    arr = np.asarray(img, dtype=np.float32) / 255.0
    return torch.from_numpy(arr).permute(2, 0, 1).contiguous()


class CalvinActDataset(Dataset):
    def __init__(
        self,
        data_root: str | Path,
        splits: list[str],
        chunk_size: int,
        image_size: int = 96,
        use_wrist_image: bool = True,
        max_episodes_per_split: int | None = None,
        max_frames: int | None = None,
        sample_stride: int = 1,
        cache_size: int = 64,
    ) -> None:
        self.data_root = Path(data_root)
        self.splits = list(splits)
        self.chunk_size = int(chunk_size)
        self.image_size = int(image_size)
        self.use_wrist_image = bool(use_wrist_image)
        self.cache_size = int(cache_size)
        self.cache: OrderedDict[Path, pd.DataFrame] = OrderedDict()
        self.episodes = self._load_episodes(max_episodes_per_split)
        self.samples = self._build_samples(sample_stride, max_frames)
        if not self.samples:
            raise ValueError("No frames found. Check data_root and split names.")

    def _load_episodes(self, max_episodes_per_split: int | None) -> list[EpisodeRef]:
        out: list[EpisodeRef] = []
        missing: list[str] = []
        for split in self.splits:
            split_dir = self.data_root / split
            info_path = split_dir / "meta" / "info.json"
            episodes_path = split_dir / "meta" / "episodes.jsonl"
            if not info_path.exists() or not episodes_path.exists():
                raise FileNotFoundError(f"Missing metadata for {split}: {split_dir}")
            info = json.loads(info_path.read_text(encoding="utf-8"))
            chunks_size = int(info.get("chunks_size", 1000))
            rows = read_jsonl(episodes_path)
            if max_episodes_per_split is not None:
                rows = rows[: int(max_episodes_per_split)]
            found = 0
            for row in rows:
                idx = int(row["episode_index"])
                path = episode_path(split_dir, idx, chunks_size)
                if path.exists():
                    out.append(EpisodeRef(split, idx, int(row["length"]), path))
                    found += 1
            if found == 0:
                missing.append(split)
        if missing:
            raise FileNotFoundError(f"No local episode parquet files found for: {', '.join(missing)}")
        return out

    def _build_samples(self, sample_stride: int, max_frames: int | None) -> list[tuple[int, int]]:
        samples: list[tuple[int, int]] = []
        stride = max(1, int(sample_stride))
        for ep_i, ep in enumerate(self.episodes):
            for frame_i in range(0, ep.length, stride):
                samples.append((ep_i, frame_i))
                if max_frames is not None and len(samples) >= int(max_frames):
                    return samples
        return samples

    def _read_episode(self, path: Path) -> pd.DataFrame:
        if path in self.cache:
            df = self.cache.pop(path)
            self.cache[path] = df
            return df
        df = pd.read_parquet(path)
        self.cache[path] = df
        while len(self.cache) > self.cache_size:
            self.cache.popitem(last=False)
        return df

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        ep_i, frame_i = self.samples[index]
        ep = self.episodes[ep_i]
        df = self._read_episode(ep.path)
        frame_i = min(frame_i, len(df) - 1)
        row = df.iloc[frame_i]
        actions = np.zeros((self.chunk_size, 7), dtype=np.float32)
        action_is_pad = np.ones((self.chunk_size,), dtype=bool)
        end = min(frame_i + self.chunk_size, len(df))
        if end > frame_i:
            future = np.stack(df["actions"].iloc[frame_i:end].to_numpy()).astype(np.float32)
            actions[: len(future)] = future
            action_is_pad[: len(future)] = False

        item = {
            "observation.images.primary": decode_image(row["image"], self.image_size),
            "observation.state": torch.tensor(np.asarray(row["state"], dtype=np.float32)),
            "action": torch.tensor(actions, dtype=torch.float32),
            "action_is_pad": torch.tensor(action_is_pad, dtype=torch.bool),
            "episode_index": torch.tensor(ep.episode_index, dtype=torch.long),
            "frame_index": torch.tensor(int(row["frame_index"]), dtype=torch.long),
        }
        if self.use_wrist_image:
            item["observation.images.wrist"] = decode_image(row["wrist_image"], self.image_size)
        return item


def describe_local_splits(data_root: str | Path, splits: list[str]) -> list[dict]:
    root = Path(data_root)
    rows = []
    for split in splits:
        split_dir = root / split
        info_path = split_dir / "meta" / "info.json"
        if not info_path.exists():
            rows.append({"split": split, "available": False})
            continue
        info = json.loads(info_path.read_text(encoding="utf-8"))
        parquet_count = len(list((split_dir / "data").rglob("*.parquet")))
        rows.append(
            {
                "split": split,
                "available": True,
                "scene": info.get("scene"),
                "episodes_meta": info.get("total_episodes"),
                "frames_meta": info.get("total_frames"),
                "local_parquet_files": parquet_count,
                "fps": info.get("fps"),
            }
        )
    return rows
