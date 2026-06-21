#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

bash task1_3dgs_aigc/member_B/scripts/prepare_object_C_input.sh
exec bash task1_3dgs_aigc/member_B/scripts/run_object_C_stable_zero123.sh
