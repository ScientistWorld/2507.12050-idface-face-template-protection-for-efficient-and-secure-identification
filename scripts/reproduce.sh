#!/usr/bin/env bash
# End-to-end reproduction: data, reference method checks, baselines, train/test scoring, validation.
set -euo pipefail

python data/generate_synthetic.py --out data/synthetic_embeddings.npz
bash scripts/method.sh
bash scripts/baseline.sh
bash scripts/evaluate_train.sh
bash scripts/evaluate_test.sh
cp scoring/scores_train.json scoring/scores.json
python validate.py --post-design
