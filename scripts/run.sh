#!/usr/bin/env bash
set -euo pipefail

bash scripts/reproduce.sh
bash scripts/evaluate_train.sh /home/user/checkpoints
bash scripts/evaluate_test.sh /home/user/checkpoints
