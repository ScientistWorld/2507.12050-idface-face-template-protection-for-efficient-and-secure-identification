#!/usr/bin/env bash
# Baselines are encoders run by the evaluator; their specs live in
# baseline/outputs/<name>/encoder.json. Nothing is precomputed.
set -euo pipefail

test -f baseline/outputs/sign_random_subset/encoder.json
test -f baseline/outputs/random_codes/encoder.json
test -f baseline/outputs/sparse_63/encoder.json
echo "baseline encoders: sign_random_subset, random_codes, sparse_63"
