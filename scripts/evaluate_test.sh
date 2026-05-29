#!/usr/bin/env bash
set -euo pipefail

python eval/test/evaluate.py "$@" \
  --train-scores scoring/scores_train.json \
  --out scoring/scores_test.json
