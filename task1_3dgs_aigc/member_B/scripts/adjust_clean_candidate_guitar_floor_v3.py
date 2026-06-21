#!/usr/bin/env python3
"""Move the guitar off the tabletop and down to the cabinet/floor side.

Input is the clean fused candidate ordered as:
background -> controller -> bottle/vase -> guitar.

Only the guitar chunk is transformed. The background, controller and bottle
chunks stay unchanged.
"""

from __future__ import annotations

import gzip
import math
from pathlib import Path

import numpy as np

PROPS = [
    "x", "y", "z", "nx", "ny", "nz", "f_dc_0", "f_dc_1", "f_dc_2",
    *[f"f_rest_{i}" for i in range(45)],
    "opacity", "scale_0", "scale_1", "scale_2", "rot_0", "rot_1", "rot_2", "rot_3",
]

SEGMENTS = {
    "background": (0, 413_019),
    "controller": (413_019, 441_058),
    "bottle": (441_058, 535_058),
    "guitar": (535_058, 625_058),
}

INPUT = Path("task1_3dgs_aigc/member_B/outputs/renders/fused_scene_gaussian_clean_candidate.ply.gz")
OUTPUT_PLY = Path("task1_3dgs_aigc/member_B/outputs/renders/fused_scene_gaussian_clean_candidate_guitar_floor_v3.ply")
OUTPUT_GZ = Path("task1_3dgs_aigc/member_B/outputs/renders/fused_scene_gaussian_clean_candidate_guitar_floor_v3.ply.gz")
OUTPUT_STATS = Path("task1_3dgs_aigc/member_B/outputs/renders/guitar_floor_v3_stats.csv")
OUTPUT_TOPDOWN = Path("task1_3dgs_aigc/member_B/outputs/renders/guitar_floor_v3_topdown.png")

# Put guitar on the floor/cabinet-front side, not on the tabletop.
GUITAR_TARGET_XY = np.asarray([-0.72, -0.34], dtype=np.float32)
GUITAR_SUPPORT_Z = -1.10
GUITAR_SCALE = 0.88
GUITAR_ROT_X_DEG = -8.0
GUITAR_ROT_Y_DEG = -16.0
GUITAR_ROT_Z_DEG = -12.0


def opener(path: Path, mode: str):
    return gzip.open(path, mode) if path.suffix == ".gz" else path.open(mode)


def read_gaussian_ply(path: Path) -> np.ndarray:
    with opener(path, "rb") as f:
        props: list[str] = []
        vertex_count = None
        while True:
            raw = f.readline()
            if not raw:
                raise ValueError(f"Invalid PLY header: {path}")
            text = raw.decode("ascii", errors="replace").strip()
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
            raise ValueError(f"Unexpected schema in {path}")
        return np.frombuffer(f.read(vertex_count * len(PROPS) * 4), dtype="<f4").reshape(vertex_count, len(PROPS)).copy()


def write_gaussian_ply(path: Path, data: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with opener(path, "wb") as f:
        f.write(b"ply\n")
        f.write(b"format binary_little_endian 1.0\n")
        f.write(b"comment Clean fused Gaussian scene with guitar floor-side v3 placement\n")
        f.write(b"comment Only guitar moved lower/front; background/controller/bottle unchanged\n")
        f.write(f"element vertex {len(data)}\n".encode("ascii"))
        for prop in PROPS:
            f.write(f"property float {prop}\n".encode("ascii"))
        f.write(b"end_header\n")
        f.write(data.astype("<f4", copy=False).tobytes())


def robust_bounds(xyz: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return np.percentile(xyz, 1, axis=0).astype(np.float32), np.percentile(xyz, 99, axis=0).astype(np.float32)


def rotation_matrix(rx_deg: float, ry_deg: float, rz_deg: float) -> np.ndarray:
    rx, ry, rz = map(math.radians, [rx_deg, ry_deg, rz_deg])
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    rxm = np.asarray([[1, 0, 0], [0, cx, -sx], [0, sx, cx]], dtype=np.float32)
    rym = np.asarray([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]], dtype=np.float32)
    rzm = np.asarray([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]], dtype=np.float32)
    return rzm @ rym @ rxm


def move_guitar(data: np.ndarray) -> np.ndarray:
    out = data.copy()
    start, end = SEGMENTS["guitar"]
    chunk = out[start:end]
    xyz = chunk[:, 0:3]
    lo, hi = robust_bounds(xyz)

    # Pivot around the bottom center so the guitar stays grounded after tilting.
    pivot = np.asarray([(lo[0] + hi[0]) * 0.5, (lo[1] + hi[1]) * 0.5, lo[2]], dtype=np.float32)
    rot = rotation_matrix(GUITAR_ROT_X_DEG, GUITAR_ROT_Y_DEG, GUITAR_ROT_Z_DEG)
    target = np.asarray([GUITAR_TARGET_XY[0], GUITAR_TARGET_XY[1], GUITAR_SUPPORT_Z], dtype=np.float32)

    moved = (xyz - pivot) * GUITAR_SCALE
    moved = moved @ rot.T
    moved = moved + target

    # Re-ground after rotation using robust bottom, because the tilt can move
    # a few points below the intended support plane.
    bottom = np.percentile(moved[:, 2], 1)
    moved[:, 2] += GUITAR_SUPPORT_Z - bottom
    chunk[:, 0:3] = moved

    normals = chunk[:, 3:6] @ rot.T
    norms = np.maximum(np.linalg.norm(normals, axis=1, keepdims=True), 1e-8)
    chunk[:, 3:6] = normals / norms
    chunk[:, 55:58] += math.log(max(GUITAR_SCALE, 1e-8))
    out[start:end] = chunk
    return out


def write_stats(path: Path, data: np.ndarray) -> None:
    lines = ["name,count,p01_x,p01_y,p01_z,p99_x,p99_y,p99_z,mean_x,mean_y,mean_z"]
    for name, (start, end) in SEGMENTS.items():
        xyz = data[start:end, 0:3]
        lo, hi = robust_bounds(xyz)
        mean = xyz.mean(axis=0)
        lines.append(
            f"{name},{end-start},"
            f"{lo[0]:.5f},{lo[1]:.5f},{lo[2]:.5f},"
            f"{hi[0]:.5f},{hi[1]:.5f},{hi[2]:.5f},"
            f"{mean[0]:.5f},{mean[1]:.5f},{mean[2]:.5f}"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_topdown(path: Path, data: np.ndarray) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rng = np.random.default_rng(33)
    colors = {
        "background": "#b8b4ac",
        "controller": "#ef4444",
        "bottle": "#60a5fa",
        "guitar": "#d69b32",
    }
    fig, ax = plt.subplots(figsize=(7, 7), dpi=180)
    fig.patch.set_facecolor("#f7f5ef")
    ax.set_facecolor("#fffdf8")
    for name, (start, end) in SEGMENTS.items():
        xyz = data[start:end, 0:3]
        idx = np.arange(len(xyz))
        limit = 20_000 if name == "background" else 16_000
        if len(idx) > limit:
            idx = rng.choice(idx, size=limit, replace=False)
        ax.scatter(
            xyz[idx, 0],
            xyz[idx, 1],
            s=0.08 if name == "background" else 0.35,
            c=colors[name],
            alpha=0.06 if name == "background" else 0.5,
            linewidths=0,
            label=name,
        )
        lo, hi = robust_bounds(xyz)
        ax.add_patch(plt.Rectangle((lo[0], lo[1]), hi[0] - lo[0], hi[1] - lo[1], fill=False, color=colors[name], linewidth=1.4))
        ax.text((lo[0] + hi[0]) / 2, hi[1], name, color=colors[name], ha="center", va="bottom")
    ax.set_xlim(-1.2, 0.35)
    ax.set_ylim(-0.75, 0.75)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, color="#d8d3c7", linewidth=0.6)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("guitar floor-side v3 top-down placement")
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    data = read_gaussian_ply(INPUT)
    if len(data) != SEGMENTS["guitar"][1]:
        raise ValueError(f"Expected {SEGMENTS['guitar'][1]} gaussians, got {len(data)}")
    adjusted = move_guitar(data)
    write_gaussian_ply(OUTPUT_PLY, adjusted)
    write_gaussian_ply(OUTPUT_GZ, adjusted)
    write_stats(OUTPUT_STATS, adjusted)
    write_topdown(OUTPUT_TOPDOWN, adjusted)
    print(f"wrote {OUTPUT_PLY}")
    print(f"wrote {OUTPUT_GZ}")
    print(f"wrote {OUTPUT_STATS}")
    print(f"wrote {OUTPUT_TOPDOWN}")


if __name__ == "__main__":
    main()
