#!/usr/bin/env bash
set -euo pipefail

python data/generate_synthetic.py --out data/synthetic_embeddings.npz
python method/run_idface.py --data data/synthetic_embeddings.npz --out method/outputs/idface_synthetic --alpha 341 --beta 341
python method/run_idface.py --data data/synthetic_embeddings.npz --out method/outputs/idface_synthetic_beta63 --alpha 341 --beta 63
python method/run_encrypted_idface.py --data data/synthetic_embeddings.npz --out method/outputs/idface_paillier_small
scripts/evaluate.sh
