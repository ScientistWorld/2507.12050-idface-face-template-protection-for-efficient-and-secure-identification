#!/usr/bin/env bash
# No arguments scores every method directory on disk.
set -euo pipefail
cd "$(dirname "$0")/.."
export OPENBLAS_NUM_THREADS=4 OMP_NUM_THREADS=4 MKL_NUM_THREADS=4
python eval/test/evaluate.py "$@" --out scoring/scores_test.json
