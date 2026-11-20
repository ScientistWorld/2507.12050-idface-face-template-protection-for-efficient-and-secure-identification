#!/usr/bin/env bash
# Reproduce the reference and baselines end to end from committed real-face banks.
set -euo pipefail
cd "$(dirname "$0")/.."
bash scripts/reproduce.sh
