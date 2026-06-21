#!/usr/bin/env python3
"""Convert simple OBJ meshes to 3DGS-compatible Gaussian PLY files.

This is a format-unification utility for the homework package. It samples mesh
surfaces and writes the same 62 float properties used by the provided 3DGS PLY
files: xyz, normals, SH DC/rest color, opacity, scales, quaternion rotation.
"""

from __future__ import annotations

import argparse
import math
import struct
from pathlib import Path

import numpy as np

PROPS = [
    "x", "y", "z", "nx", "ny", "nz", "f_dc_0", "f_dc_1", "f_dc_2",
    *[f"f_rest_{i}" for i in range(45)],
    "opacity", "scale_0", "scale_1", "scale_2", "rot_0", "rot_1", "rot_2", "rot_3",
]
SH_C0 = 0.2820947918


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--samples", type=int, default=60000)
    parser.add_argument("--color", nargs=3, type=float, default=(0.8, 0.8, 0.8), help="RGB in 0..1")
    parser.add_argument("--location", nargs=3, type=float, default=(0.0, 0.0, 0.0))
    parser.add_argument("--rotation-z-deg", type=float, default=0.0)
    parser.add_argument("--scale", type=float, default=1.0)
    parser.add_argument("--target-extent", type=float, default=0.9)
    parser.add_argument("--opacity", type=float, default=4.0, help="Raw 3DGS opacity logit")
    parser.add_argument("--splat-scale", type=float, default=0.012, help="Raw log scale before object scaling")
    parser.add_argument("--seed", type=int, default=1234)
    return parser.parse_args()


def parse_obj(path: Path) -> tuple[np.ndarray, np.ndarray]:
    vertices: list[list[float]] = []
    faces: list[list[int]] = []
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("v "):
                parts = line.split()
                if len(parts) >= 4:
                    vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])
            elif line.startswith("f "):
                ids = []
                for token in line.split()[1:]:
                    raw = token.split("/")[0]
                    if not raw:
                        continue
                    idx = int(raw)
                    ids.append(idx - 1 if idx > 0 else len(vertices) + idx)
                if len(ids) >= 3:
                    for i in range(1, len(ids) - 1):
                        faces.append([ids[0], ids[i], ids[i + 1]])
    if not vertices or not faces:
        raise ValueError(f"OBJ has no vertices/faces: {path}")
    return np.asarray(vertices, dtype=np.float32), np.asarray(faces, dtype=np.int64)


def normalize_vertices(vertices: np.ndarray, target_extent: float) -> np.ndarray:
    mins = vertices.min(axis=0)
    maxs = vertices.max(axis=0)
    center = (mins + maxs) * 0.5
    extent = float((maxs - mins).max())
    if extent <= 0:
        raise ValueError("Invalid mesh extent")
    return (vertices - center) * (target_extent / extent)


def transform_vertices(vertices: np.ndarray, scale: float, rotation_z_deg: float, location: tuple[float, float, float]) -> np.ndarray:
    theta = math.radians(rotation_z_deg)
    c, s = math.cos(theta), math.sin(theta)
    rot = np.asarray([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]], dtype=np.float32)
    out = vertices @ rot.T
    out = out * scale
    out = out + np.asarray(location, dtype=np.float32)
    return out


def sample_surface(vertices: np.ndarray, faces: np.ndarray, n_samples: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    tri = vertices[faces]
    v0, v1, v2 = tri[:, 0], tri[:, 1], tri[:, 2]
    cross = np.cross(v1 - v0, v2 - v0)
    areas = np.linalg.norm(cross, axis=1) * 0.5
    valid = areas > 1e-12
    tri = tri[valid]
    cross = cross[valid]
    areas = areas[valid]
    if len(areas) == 0:
        raise ValueError("Mesh has no valid triangle area")
    probs = areas / areas.sum()
    rng = np.random.default_rng(seed)
    choice = rng.choice(len(tri), size=n_samples, replace=True, p=probs)
    chosen = tri[choice]
    r1 = rng.random(n_samples, dtype=np.float32)
    r2 = rng.random(n_samples, dtype=np.float32)
    sqrt_r1 = np.sqrt(r1)
    a = 1.0 - sqrt_r1
    b = sqrt_r1 * (1.0 - r2)
    c = sqrt_r1 * r2
    points = chosen[:, 0] * a[:, None] + chosen[:, 1] * b[:, None] + chosen[:, 2] * c[:, None]
    normals = cross[choice]
    normals = normals / np.maximum(np.linalg.norm(normals, axis=1, keepdims=True), 1e-8)
    return points.astype(np.float32), normals.astype(np.float32)


def write_gaussian_ply(path: Path, points: np.ndarray, normals: np.ndarray, color: tuple[float, float, float], opacity: float, splat_scale: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rgb = np.clip(np.asarray(color, dtype=np.float32), 0.0, 1.0)
    f_dc = (rgb - 0.5) / SH_C0
    n = points.shape[0]
    rest = np.zeros((n, 45), dtype=np.float32)
    scales = np.full((n, 3), math.log(max(splat_scale, 1e-6)), dtype=np.float32)
    rots = np.zeros((n, 4), dtype=np.float32)
    rots[:, 0] = 1.0
    data = np.concatenate([
        points.astype(np.float32),
        normals.astype(np.float32),
        np.tile(f_dc, (n, 1)).astype(np.float32),
        rest,
        np.full((n, 1), opacity, dtype=np.float32),
        scales,
        rots,
    ], axis=1)
    if data.shape[1] != len(PROPS):
        raise AssertionError((data.shape, len(PROPS)))
    with path.open("wb") as f:
        f.write(b"ply\n")
        f.write(b"format binary_little_endian 1.0\n")
        f.write(b"comment Converted from OBJ mesh for homework asset-format unification\n")
        f.write(f"element vertex {n}\n".encode("ascii"))
        for prop in PROPS:
            f.write(f"property float {prop}\n".encode("ascii"))
        f.write(b"end_header\n")
        f.write(data.astype("<f4", copy=False).tobytes())


def main() -> None:
    args = parse_args()
    vertices, faces = parse_obj(Path(args.input))
    vertices = normalize_vertices(vertices, args.target_extent)
    vertices = transform_vertices(vertices, args.scale, args.rotation_z_deg, tuple(args.location))
    points, normals = sample_surface(vertices, faces, args.samples, args.seed)
    write_gaussian_ply(Path(args.output), points, normals, tuple(args.color), args.opacity, args.splat_scale)
    print(f"wrote {args.output}: {points.shape[0]} gaussian points")


if __name__ == "__main__":
    main()
