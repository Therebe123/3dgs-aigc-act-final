#!/usr/bin/env python3
"""Fuse Gaussian PLY assets into one 3DGS-compatible Gaussian PLY.

The provided Object A/background are native 3DGS PLYs. Object B/C can be the
Gaussian PLYs generated from mesh sampling. This script normalizes each asset to
a target extent, applies scene placement transforms, adjusts Gaussian log-scales,
and concatenates all records with the same 62-property schema.
"""

from __future__ import annotations

import argparse
import csv
import math
import struct
from pathlib import Path

import numpy as np

PROPS = [
    "x", "y", "z", "nx", "ny", "nz", "f_dc_0", "f_dc_1", "f_dc_2",
    *[f"f_rest_{i}" for i in range(45)],
    "opacity", "scale_0", "scale_1", "scale_2", "rot_0", "rot_1", "rot_2", "rot_3",
]

TARGET_EXTENT = {
    "background": 2.6,
    "object_A": 0.85,
    "object_B": 0.9,
    "object_C": 0.9,
}


def preserve_native_for(row: dict[str, str]) -> bool:
    value = row.get("preserve_native", "").strip().lower()
    return value in {"1", "true", "yes", "y"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-background", type=int, default=220000)
    parser.add_argument("--max-object-a", type=int, default=28039)
    return parser.parse_args()


def read_gaussian_ply(path: Path) -> tuple[list[str], np.ndarray]:
    with path.open("rb") as f:
        props = []
        vertex_count = None
        while True:
            line = f.readline()
            if not line:
                raise ValueError(f"Invalid PLY header: {path}")
            text = line.decode("ascii", errors="replace").strip()
            parts = text.split()
            if parts[:2] == ["element", "vertex"]:
                vertex_count = int(parts[2])
            elif len(parts) == 3 and parts[0] == "property":
                props.append(parts[2])
            elif text == "end_header":
                break
        if vertex_count is None:
            raise ValueError(f"Missing vertex count: {path}")
        if props != PROPS:
            raise ValueError(f"Unexpected schema in {path}: {props}")
        data = np.frombuffer(f.read(vertex_count * len(PROPS) * 4), dtype="<f4").reshape(vertex_count, len(PROPS)).copy()
    return props, data


def write_gaussian_ply(path: Path, data: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        f.write(b"ply\n")
        f.write(b"format binary_little_endian 1.0\n")
        f.write(b"comment Fused Gaussian scene for homework task1\n")
        f.write(b"comment Assets: background + object_A + object_B + object_C\n")
        f.write(f"element vertex {len(data)}\n".encode("ascii"))
        for prop in PROPS:
            f.write(f"property float {prop}\n".encode("ascii"))
        f.write(b"end_header\n")
        f.write(data.astype("<f4", copy=False).tobytes())


def target_extent_for(name: str) -> float:
    return TARGET_EXTENT.get(name, 0.9)


def transform_data(data: np.ndarray, row: dict[str, str]) -> np.ndarray:
    out = data.copy()
    if preserve_native_for(row):
        return out

    xyz = out[:, 0:3]
    mins = xyz.min(axis=0)
    maxs = xyz.max(axis=0)
    center = (mins + maxs) * 0.5
    extent = float((maxs - mins).max())
    if extent <= 0:
        raise ValueError(f"Bad extent for {row['name']}")
    normalize_scale = target_extent_for(row["name"]) / extent
    manifest_scale = float(row["scale"])
    total_scale = normalize_scale * manifest_scale

    theta = math.radians(float(row["rotation_z_deg"]))
    c, s = math.cos(theta), math.sin(theta)
    rot = np.asarray([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]], dtype=np.float32)
    loc = np.asarray([float(row["location_x"]), float(row["location_y"]), float(row["location_z"])], dtype=np.float32)

    xyz = (xyz - center) * normalize_scale
    xyz = xyz @ rot.T
    xyz = xyz * manifest_scale + loc
    out[:, 0:3] = xyz

    normals = out[:, 3:6]
    normals = normals @ rot.T
    norms = np.maximum(np.linalg.norm(normals, axis=1, keepdims=True), 1e-8)
    out[:, 3:6] = normals / norms

    # 3DGS stores scale as log radii. When coordinates are rescaled, add log(scale).
    out[:, 55:58] += math.log(max(total_scale, 1e-8))
    return out


def maybe_downsample(name: str, data: np.ndarray, max_background: int, max_object_a: int) -> np.ndarray:
    limit = None
    if name == "background":
        limit = max_background
    elif name == "object_A":
        limit = max_object_a
    if limit is None or len(data) <= limit:
        return data
    step = max(1, len(data) // limit)
    return data[::step][:limit]


def main() -> None:
    args = parse_args()
    manifest = Path(args.manifest).resolve()
    root = manifest.parent
    chunks = []
    total = 0
    with manifest.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            path = (root / row["path"]).resolve()
            _, data = read_gaussian_ply(path)
            data = maybe_downsample(row["name"], data, args.max_background, args.max_object_a)
            data = transform_data(data, row)
            chunks.append(data)
            total += len(data)
            print(f"{row['name']}: {path} -> {len(data)} gaussians")
    fused = np.concatenate(chunks, axis=0)
    write_gaussian_ply(Path(args.output), fused)
    print(f"wrote {args.output}: {total} gaussians, {fused.nbytes / 1024 / 1024:.1f} MiB raw")


if __name__ == "__main__":
    main()
