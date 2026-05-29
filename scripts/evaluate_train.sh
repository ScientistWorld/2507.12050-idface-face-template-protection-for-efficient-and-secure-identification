#!/usr/bin/env bash
set -euo pipefail

python eval/train/evaluate.py "$@" \
  --out scoring/scores_train.json
