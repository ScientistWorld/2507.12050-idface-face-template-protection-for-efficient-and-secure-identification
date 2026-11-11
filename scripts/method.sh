#!/usr/bin/env bash
# Reference method (IDFace). The evaluator runs the encoder named in
# method/outputs/idface/encoder.json on the benchmark's templates; this script
# only runs the method's own correctness checks.
set -euo pipefail

test -f method/outputs/idface/encoder.json
python method/self_check.py
[ -f data/synthetic_embeddings.npz ] || python data/generate_synthetic.py --out data/synthetic_embeddings.npz
# Small real-Paillier run: decrypted packed scores must equal the plaintext packed arithmetic.
python method/run_encrypted_idface.py --data data/synthetic_embeddings.npz --out method/smoke/paillier_small
