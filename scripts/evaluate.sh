#!/usr/bin/env bash
set -euo pipefail

python eval/evaluate.py \
  --plain baseline/outputs/plain_synthetic \
  --random baseline/outputs/random_synthetic \
  --idface method/outputs/idface_synthetic \
  --out scoring/scores.json
