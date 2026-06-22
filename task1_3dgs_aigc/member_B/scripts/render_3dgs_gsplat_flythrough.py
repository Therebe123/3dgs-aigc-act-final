#!/usr/bin/env python3
"""Render a 3DGS binary PLY flythrough with gsplat CUDA rasterization."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import cv2
try:
    import imageio.v2 as imageio
except ModuleNotFoundError:
    import imageio
import numpy as np
import torch
from gsplat import rasterization

PROPS = [
    "x", "y", "z", "nx", "ny", "nz", "f_dc_0", "f_dc_1", "f_dc_2",
    *[f"f_rest_{i}" for i in range(45)],
    "opacity", "scale_0", "scale_1", "scale_2", "rot_0", "rot_1", "rot_2", "rot_3",
]
SH_C0 = 0.28209479177387814


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        default="homework/member_B/outputs/renders/fused_scene_gaussian_clean_candidate_guitar_floor_v3.ply",
        help="Input 3DGS binary PLY.",
    )
    parser.add_argument(
        "--output-dir",
        default="homework/member_B/outputs/renders/3dgs_flythrough_gsplat",
        help="Directory for frames, MP4, and metadata.",
    )
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--frames", type=int, default=72)
    parser.add_argument("--fps", type=int, default=18)
    parser.add_argument("--fov-deg", type=float, default=66.0)
    parser.add_argument("--radius", type=float, default=2.35)
    parser.add_argument("--height-offset", type=float, default=1.05)
    parser.add_argument("--yaw-start-deg", type=float, default=-65.0)
    parser.add_argument("--yaw-end-deg", type=float, default=65.0)
    parser.add_argument("--target", type=float, nargs=3, default=(-0.18, 0.20, -0.54))
    parser.add_argument("--near", type=float, default=0.02)
    parser.add_argument("--far", type=float, default=20.0)
    parser.add_argument("--eps2d", type=float, default=0.3)
    parser.add_argument("--radius-clip", type=float, default=0.0)
    parser.add_argument("--exposure", type=float, default=1.0)
    parser.add_argument("--crop-min", type=float, nargs=3, default=(-3.0, -3.0, -2.0))
    parser.add_argument("--crop-max", type=float, nargs=3, default=(3.0, 3.2, 1.4))
    parser.add_argument("--no-crop", action="store_true")
    parser.add_argument("--max-points", type=int, default=0, help="Optional random cap after crop; 0 keeps all selected gaussians.")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--topdown", action="store_true")
    parser.add_argument("--rasterize-mode", choices=["classic", "antialiased"], default="antialiased")
    return parser.parse_args()


def read_gaussian_ply(path: Path) -> tuple[list[str], np.memmap]:
    props: list[str] = []
    vertex_count = None
    offset = 0
    with path.open("rb") as f:
        while True:
            line = f.readline()
            if not line:
                raise ValueError(f"Invalid PLY header: {path}")
            offset += len(line)
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
        raise ValueError(f"Unexpected 3DGS schema in {path}: {props}")
    data = np.memmap(path, dtype="<f4", mode="r", offset=offset, shape=(vertex_count, len(PROPS)))
    return props, data


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30.0, 30.0)))


def normalize_np(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    return v / max(n, 1e-8)


def camera_viewmat(eye: np.ndarray, target: np.ndarray) -> np.ndarray:
    forward = normalize_np(target - eye)
    world_up = np.array([0.0, 0.0, 1.0], dtype=np.float32)
    right = normalize_np(np.cross(forward, world_up))
    if np.linalg.norm(right) < 1e-6:
        right = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    up = normalize_np(np.cross(right, forward))

    # gsplat uses OpenCV-style camera coordinates: +x right, +y down, +z forward.
    rot = np.stack([right, -up, forward], axis=0).astype(np.float32)
    trans = -(rot @ eye.astype(np.float32))
    view = np.eye(4, dtype=np.float32)
    view[:3, :3] = rot
    view[:3, 3] = trans
    return view


def intrinsic_matrix(width: int, height: int, fov_deg: float) -> np.ndarray:
    f = 0.5 * width / math.tan(math.radians(fov_deg) * 0.5)
    return np.array([[f, 0.0, width * 0.5], [0.0, f, height * 0.5], [0.0, 0.0, 1.0]], dtype=np.float32)


def camera_path(args: argparse.Namespace, i: int) -> tuple[np.ndarray, np.ndarray]:
    target = np.asarray(args.target, dtype=np.float32)
    t = 0.0 if args.frames == 1 else i / (args.frames - 1)
    smooth = 0.5 - 0.5 * math.cos(math.pi * t)
    yaw = math.radians(args.yaw_start_deg + (args.yaw_end_deg - args.yaw_start_deg) * smooth)
    radius = args.radius * (1.0 + 0.04 * math.sin(2.0 * math.pi * t))
    eye = target + np.array(
        [
            radius * math.sin(yaw),
            -radius * math.cos(yaw),
            args.height_offset + 0.08 * math.sin(2.0 * math.pi * t + 0.4),
        ],
        dtype=np.float32,
    )
    look = target + np.array([0.08 * math.sin(2.0 * math.pi * t), 0.06 * math.cos(2.0 * math.pi * t), 0.0], dtype=np.float32)
    return eye, look


def select_indices(data: np.ndarray, args: argparse.Namespace) -> np.ndarray:
    xyz = np.asarray(data[:, 0:3], dtype=np.float32)
    mask = np.ones(len(data), dtype=bool)
    if not args.no_crop:
        crop_min = np.asarray(args.crop_min, dtype=np.float32)
        crop_max = np.asarray(args.crop_max, dtype=np.float32)
        mask &= np.all((xyz >= crop_min) & (xyz <= crop_max), axis=1)
    idx = np.flatnonzero(mask)
    if args.max_points and len(idx) > args.max_points:
        rng = np.random.default_rng(args.seed)
        idx = np.sort(rng.choice(idx, size=args.max_points, replace=False))
    return idx


def load_tensors(data: np.ndarray, idx: np.ndarray, device: torch.device) -> dict[str, torch.Tensor]:
    selected = np.asarray(data[idx], dtype=np.float32)
    means = torch.from_numpy(selected[:, 0:3]).to(device=device, dtype=torch.float32)
    colors_np = np.clip(0.5 + SH_C0 * selected[:, 6:9], 0.0, 1.0).astype(np.float32)
    colors = torch.from_numpy(colors_np).to(device=device, dtype=torch.float32)
    opacities = torch.from_numpy(sigmoid(selected[:, 54]).astype(np.float32)).to(device=device, dtype=torch.float32)
    scales_np = np.exp(np.clip(selected[:, 55:58], -12.0, 4.0)).astype(np.float32)
    scales = torch.from_numpy(scales_np).to(device=device, dtype=torch.float32)
    quats_np = selected[:, 58:62].astype(np.float32)
    norms = np.linalg.norm(quats_np, axis=1, keepdims=True)
    quats_np = quats_np / np.maximum(norms, 1e-8)
    quats = torch.from_numpy(quats_np).to(device=device, dtype=torch.float32)
    return {"means": means, "colors": colors, "opacities": opacities, "scales": scales, "quats": quats}


def render_one(
    tensors: dict[str, torch.Tensor],
    viewmat_np: np.ndarray,
    K_np: np.ndarray,
    args: argparse.Namespace,
    device: torch.device,
) -> np.ndarray:
    viewmats = torch.from_numpy(viewmat_np[None]).to(device=device, dtype=torch.float32)
    Ks = torch.from_numpy(K_np[None]).to(device=device, dtype=torch.float32)
    with torch.no_grad():
        colors, alphas, _ = rasterization(
            means=tensors["means"],
            quats=tensors["quats"],
            scales=tensors["scales"],
            opacities=tensors["opacities"],
            colors=tensors["colors"],
            viewmats=viewmats,
            Ks=Ks,
            width=args.width,
            height=args.height,
            near_plane=args.near,
            far_plane=args.far,
            radius_clip=args.radius_clip,
            eps2d=args.eps2d,
            packed=True,
            render_mode="RGB",
            rasterize_mode=args.rasterize_mode,
        )
    img = colors[0].detach().clamp(0.0, 1.0).cpu().numpy()
    if args.exposure != 1.0:
        img = np.clip(img * args.exposure, 0.0, 1.0)
    return (img * 255.0 + 0.5).astype(np.uint8)


def write_video(frame_paths: list[Path], output: Path, fps: int) -> None:
    frames = [imageio.imread(path) for path in frame_paths]
    imageio.mimwrite(output, frames, fps=fps, quality=8, macro_block_size=1)


def render_topdown(tensors: dict[str, torch.Tensor], args: argparse.Namespace, K_np: np.ndarray, out: Path, device: torch.device) -> None:
    target = np.asarray(args.target, dtype=np.float32)
    eye = target + np.array([0.0, 0.0, 4.2], dtype=np.float32)
    look = target + np.array([0.0, 0.001, 0.0], dtype=np.float32)
    frame = render_one(tensors, camera_viewmat(eye, look), K_np, args, device)
    imageio.imwrite(out, frame)


def main() -> None:
    args = parse_args()
    input_path = Path(args.input).resolve()
    output_dir = Path(args.output_dir).resolve()
    frames_dir = output_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    device = torch.device(args.device if torch.cuda.is_available() else "cpu")
    if device.type != "cuda":
        raise RuntimeError("gsplat rendering requires CUDA in this workflow")

    _, data = read_gaussian_ply(input_path)
    idx = select_indices(data, args)
    tensors = load_tensors(data, idx, device)
    K_np = intrinsic_matrix(args.width, args.height, args.fov_deg)
    xyz = np.asarray(data[idx, 0:3], dtype=np.float32)
    print(f"loaded {input_path}")
    print(f"selected {len(idx)} / {len(data)} gaussians on {device}")
    print(f"bounds min {xyz.min(axis=0)} max {xyz.max(axis=0)}")

    frame_paths: list[Path] = []
    for i in range(args.frames):
        eye, look = camera_path(args, i)
        frame = render_one(tensors, camera_viewmat(eye, look), K_np, args, device)
        out = frames_dir / f"frame_{i:04d}.png"
        imageio.imwrite(out, frame)
        frame_paths.append(out)
        print(f"frame {i + 1:03d}/{args.frames}: {out}", flush=True)

    video_path = output_dir / "fused_scene_gaussian_clean_candidate_guitar_floor_v3_gsplat_flythrough.mp4"
    write_video(frame_paths, video_path, args.fps)
    topdown_path = output_dir / "topdown_check.png"
    if args.topdown:
        render_topdown(tensors, args, K_np, topdown_path, device)

    metadata = {
        "input": str(input_path),
        "video": str(video_path),
        "frames_dir": str(frames_dir),
        "topdown_check": str(topdown_path) if args.topdown else None,
        "renderer": "gsplat 1.5.3 CUDA rasterization, DC color from 3DGS SH coefficients",
        "selected_gaussians": int(len(idx)),
        "total_gaussians": int(len(data)),
        "camera": {
            "target": list(args.target),
            "radius": args.radius,
            "height_offset": args.height_offset,
            "yaw_start_deg": args.yaw_start_deg,
            "yaw_end_deg": args.yaw_end_deg,
            "fov_deg": args.fov_deg,
            "near": args.near,
            "far": args.far,
        },
        "output": {"width": args.width, "height": args.height, "frames": args.frames, "fps": args.fps},
        "crop": None if args.no_crop else {"min": list(args.crop_min), "max": list(args.crop_max)},
    }
    with (output_dir / "render_metadata.json").open("w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"wrote video: {video_path}")
    print(f"wrote metadata: {output_dir / 'render_metadata.json'}")
    if args.topdown:
        print(f"wrote topdown check: {topdown_path}")


if __name__ == "__main__":
    main()
