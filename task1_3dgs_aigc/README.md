# Task 1: 3DGS and AIGC Scene Fusion

## Goal

Generate and reconstruct three 3D assets with different technical routes, reconstruct one real background scene, and fuse all assets into one 3D scene for multi-view rendering.

## Components

| Asset | Method | Expected Output |
|---|---|---|
| Object A | Multi-view capture + COLMAP + 3DGS | 3DGS model, rendered views |
| Object B | Text prompt + threestudio | Generated 3D asset |
| Object C | Single image + Zero123 | Generated 3D asset |
| Background | Open-source scene + 3DGS | 3DGS background model |

## Directory Usage

```text
configs/   Configuration files.
data/      Local data paths or data preparation notes.
scripts/   Runnable scripts for reconstruction, generation, fusion, and rendering.
assets/    Exported 3D assets such as mesh, point cloud, or gaussian files.
outputs/   Rendered images, videos, logs, and visualizations.
docs/      Notes for methods, parameters, and experiment records.
```

## Key Results to Record

- Geometry quality.
- Texture quality.
- Runtime and hardware usage.
- Asset representation and fusion method.
- Final multi-view rendering video.

