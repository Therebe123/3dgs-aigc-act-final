#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

exec bash task1_3dgs_aigc/member_B/scripts/run_object_B_train_v3_vase_sd21.sh
