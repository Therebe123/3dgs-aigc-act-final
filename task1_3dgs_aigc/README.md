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

## Members

| Member | Folder | Responsibility |
|---|---|---|
| A | `member_A/` | Real capture, COLMAP, Splatfacto reconstruction |
| B | `member_B/` | AIGC Object B/C, format unification, scene fusion |

Member A exports `controller2.ply` and `counter.ply` for Member B fusion. Large files: [Google Drive](https://drive.google.com/drive/folders/1zq4sE9CjMhWjk5RhR1OpKe3YlPzJxqpP?usp=drive_link) (`题目一`) — see [`docs/cloud_storage.md`](../docs/cloud_storage.md).

## Scripts

Task-level scripts under `scripts/` wrap member B training and fusion entry points.
