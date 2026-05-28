#!/usr/bin/env bash
set -euo pipefail

python data/generate_synthetic.py --out data/synthetic_embeddings.npz
python baseline/run_plain.py --data data/synthetic_embeddings.npz --out baseline/outputs/plain_synthetic
python baseline/run_random.py --data data/synthetic_embeddings.npz --out baseline/outputs/random_synthetic
python method/run_idface.py --data data/synthetic_embeddings.npz --out method/outputs/idface_synthetic --alpha 341 --beta 341
scripts/evaluate.sh
python validate.py --compare
