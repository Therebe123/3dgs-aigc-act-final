#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../member_C"
export PYTHONPATH="$PWD/src"
bash scripts/train_final_full.sh
