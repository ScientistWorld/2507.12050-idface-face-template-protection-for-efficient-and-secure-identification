#!/usr/bin/env bash
# Regenerate the committed embedding files from the artifacts fetched by
# scripts/download.sh (run it with --with-extraction-deps first: extraction
# needs torch, installed into .pylib/ for the container's Python 3.11).
#   1. data/extract_embeddings.py: AdaFace IR-101 (WebFace12M) embeddings of
#      LFW, XQLFW and CPLFW -> data/downloads/embeddings/ (raw, float32);
#   2. data/build_splits.py: identity-disjoint development / hidden-test pools
#      -> data/face_embeddings_dev.npz and eval/test/face_embeddings_test.npz.
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD/.pylib${PYTHONPATH:+:$PYTHONPATH}"
python data/extract_embeddings.py "$@"
python data/build_splits.py
