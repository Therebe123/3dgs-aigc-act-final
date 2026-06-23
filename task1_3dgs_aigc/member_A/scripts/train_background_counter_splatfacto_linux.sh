#!/usr/bin/env bash
# Member A: Train counter background with Nerfstudio Splatfacto on Linux.
# Run from repository root, or let this script cd there automatically.
# See: task1_3dgs_aigc/member_A/docs/runbook.md

set -euo pipefail

cd "$(dirname "$0")/../../../"
conda activate nerfstudio_gs

ns-train splatfacto \
  --max-num-iterations 30000 \
  --output-dir outputs/background_scene/counter_splatfacto \
  --experiment-name counter \
  --vis viewer \
  colmap \
  --data data/background_scene/mipnerf360/counter \
  --images-path images \
  --colmap-path sparse/0 \
  --downscale-factor 1
