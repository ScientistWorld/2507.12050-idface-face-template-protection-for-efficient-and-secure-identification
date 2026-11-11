#!/usr/bin/env bash
# Convenience view: development-benchmark scores of every method, written to scoring/scores.json.
set -euo pipefail

[ -f data/synthetic_embeddings.npz ] || python data/generate_synthetic.py --out data/synthetic_embeddings.npz
python eval/train/evaluate.py "$@" --out scoring/scores.json
