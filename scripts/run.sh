#!/usr/bin/env bash
# One combined verification job. All method runs are serial.
set -euo pipefail
cd /home/user
export OPENBLAS_NUM_THREADS=4 OMP_NUM_THREADS=4 MKL_NUM_THREADS=4
# Public AdaFace extraction was completed in the preceding preparation job.
# Build banks once; the partition builder is kept on the hidden side.
if [ ! -s data/face_embeddings_dev.npz ] || [ ! -s eval/test/face_embeddings_test.npz ]; then
  python eval/test/prepare_data.py
fi
bash scripts/reproduce.sh
python redteam/hardening/review_audit.py
python validate.py
