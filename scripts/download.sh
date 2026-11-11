#!/usr/bin/env bash
set -euo pipefail

# Estimated download size: 0 bytes. The benchmark is generated: the visible
# development split by data/generate_synthetic.py and the hidden test split by
# the test evaluator at test time. No pre-existing artifacts are required.

mkdir -p data/downloads
echo "No external downloads required for the IDFace gym."
