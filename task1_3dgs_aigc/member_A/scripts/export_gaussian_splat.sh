#!/usr/bin/env bash
# Member A: Export trained Splatfacto checkpoint to Gaussian PLY.
# Usage (from repository root):
#   LOAD_CONFIG=outputs/object_A_controller/nerfstudio_splatfacto/controller/splatfacto/<timestamp>/config.yml \
#   OUTPUT_DIR=outputs/object_A_controller/exports/controller_gaussian_splat \
#   bash task1_3dgs_aigc/member_A/scripts/export_gaussian_splat.sh
#
# Background example:
#   LOAD_CONFIG=outputs/background_scene/counter_splatfacto/counter/splatfacto/<timestamp>/config.yml \
#   OUTPUT_DIR=outputs/background_scene/exports/counter_gaussian_splat \
#   bash task1_3dgs_aigc/member_A/scripts/export_gaussian_splat.sh

set -euo pipefail

cd "$(dirname "$0")/../../../"
conda activate nerfstudio_gs

: "${LOAD_CONFIG:?Set LOAD_CONFIG to the splatfacto config.yml path}"
: "${OUTPUT_DIR:?Set OUTPUT_DIR to the export directory}"

ns-export gaussian-splat \
  --load-config "${LOAD_CONFIG}" \
  --output-dir "${OUTPUT_DIR}"
