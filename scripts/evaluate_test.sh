#!/usr/bin/env bash
# Score every method directory on disk on the hidden test benchmark.
set -euo pipefail

python eval/test/evaluate.py "$@" --out scoring/scores_test.json
