#!/usr/bin/env bash
# Score every method directory on disk on the visible development benchmark.
set -euo pipefail

[ -f data/synthetic_embeddings.npz ] || python data/generate_synthetic.py --out data/synthetic_embeddings.npz
python eval/train/evaluate.py "$@" --out scoring/scores_train.json
