#!/usr/bin/env bash
# Job: extract AdaFace IR-101 embeddings of LFW / XQLFW / CPLFW (data preparation).
set -euo pipefail
cd /home/user
export PYTHONPATH="$PWD/.pylib${PYTHONPATH:+:$PYTHONPATH}"
nvidia-smi || true
python -c "import torch; print('cuda', torch.cuda.is_available(), torch.__version__)"
python data/extract_embeddings.py
ls -la data/downloads/embeddings
