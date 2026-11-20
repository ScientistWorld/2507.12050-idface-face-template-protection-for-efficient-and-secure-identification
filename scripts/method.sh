#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
test -f method/outputs/idface/encoder.json
python method/self_check.py
# Real encryption correctness check at the paper's 2048-bit Paillier setting.
# Eight templates fit one packed block. Timing is never scored.
python method/run_encrypted_idface.py --data data/paillier_dev.npz --out method/smoke/paillier_small \
  --identities 8 --genuine-queries 4 --impostor-queries 4 --key-bits 2048 --plaintext-bits 50
