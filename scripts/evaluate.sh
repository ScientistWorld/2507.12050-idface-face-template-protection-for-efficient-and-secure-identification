#!/usr/bin/env bash
set -euo pipefail
bash scripts/evaluate_train.sh "$@"
cp scoring/scores_train.json scoring/scores.json
