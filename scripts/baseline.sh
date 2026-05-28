#!/usr/bin/env bash
set -euo pipefail

python data/generate_synthetic.py --out data/synthetic_embeddings.npz
python baseline/run_plain.py --data data/synthetic_embeddings.npz --out baseline/outputs/plain_synthetic
python baseline/run_random.py --data data/synthetic_embeddings.npz --out baseline/outputs/random_synthetic
scripts/evaluate.sh
