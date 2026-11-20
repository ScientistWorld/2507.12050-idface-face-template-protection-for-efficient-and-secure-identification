#!/usr/bin/env bash
# Reference reproduction, serial and without wall-clock limits.
set -euo pipefail
cd "$(dirname "$0")/.."
export OPENBLAS_NUM_THREADS=4 OMP_NUM_THREADS=4 MKL_NUM_THREADS=4
# Committed derived banks make offline evaluation independent of torch.
test -s data/face_embeddings_dev.npz
test -s eval/test/face_embeddings_test.npz
python data/prepare_smoke.py
bash scripts/method.sh
bash scripts/baseline.sh
bash scripts/evaluate_train.sh
bash scripts/evaluate_test.sh
cp scoring/scores_train.json scoring/scores.json
python scripts/record_reference.py
python validate.py
