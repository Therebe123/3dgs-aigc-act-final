#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../member_C"
export PYTHONPATH="$PWD/src"
bash scripts/eval_final_full.sh
python compile_final_full_results.py
