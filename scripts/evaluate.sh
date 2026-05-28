#!/usr/bin/env bash
set -euo pipefail

python eval/evaluate.py \
  --plain baseline/outputs/plain_synthetic \
  --random baseline/outputs/random_synthetic \
  --idface method/outputs/idface_synthetic \
  --idface-compressed method/outputs/idface_synthetic_beta63 \
  --out scoring/scores.json
