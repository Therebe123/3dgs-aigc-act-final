#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD/src"
.venv/bin/python download_data_mirror.py --splits splitA splitB splitC splitD --full --workers 32 --output-dir data/calvin_lerobot
