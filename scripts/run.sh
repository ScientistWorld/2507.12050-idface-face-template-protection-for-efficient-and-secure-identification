#!/usr/bin/env bash
set -euo pipefail

bash scripts/reproduce.sh
bash scripts/evaluate_train.sh checkpoints
bash scripts/evaluate_test.sh checkpoints
