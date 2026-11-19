#!/usr/bin/env bash
# Fetch every pre-existing artifact of the gym from public sources.
#
# Estimated download size: ~590 MB.
#   * LFW, XQLFW (cross-quality LFW) and CPLFW (cross-pose LFW) as aligned
#     112x112 face crops in webdataset shards (Hugging Face datasets
#     LSIbabnikz/lfw, LSIbabnikz/xqlfw, LSIbabnikz/cplfw), ~330 MB;
#   * the paper's feature extractor, AdaFace IR-101 trained on WebFace12M
#     (CVLFace, Hugging Face model minchul/cvlface_adaface_ir101_webface12m), 261 MB.
#
# The 512-D embeddings derived from them are committed (data/face_embeddings_dev.npz,
# eval/test/face_embeddings_test.npz). To regenerate them from these downloads:
#     bash scripts/download.sh --with-extraction-deps   # also installs torch for Python 3.11 into .pylib/
#     bash scripts/prepare_data.sh                      # GPU job recommended; CPU works (slow)
set -euo pipefail

cd "$(dirname "$0")/.."
DL=data/downloads
HF=https://huggingface.co
mkdir -p "$DL/lfw" "$DL/xqlfw" "$DL/cplfw" "$DL/adaface_ir101_webface12m"

fetch() {  # url dest
  if [ -s "$2" ]; then return 0; fi
  echo "fetch $1"
  curl -fL --retry 5 --retry-delay 5 -o "$2.part" "$1"
  mv "$2.part" "$2"
}

for ds in lfw xqlfw cplfw; do
  for i in 0 1 2 3; do
    fetch "$HF/datasets/LSIbabnikz/$ds/resolve/main/shard-00000$i.tar" "$DL/$ds/shard-00000$i.tar"
  done
done
fetch "$HF/minchul/cvlface_adaface_ir101_webface12m/resolve/main/model.safetensors" \
      "$DL/adaface_ir101_webface12m/model.safetensors"
fetch "$HF/minchul/cvlface_adaface_ir101_webface12m/resolve/main/README.md" \
      "$DL/adaface_ir101_webface12m/README.md"

( cd "$DL" && sha256sum lfw/*.tar xqlfw/*.tar cplfw/*.tar adaface_ir101_webface12m/model.safetensors > SHA256SUMS.local )
if [ -f data/SHA256SUMS ]; then
  ( cd "$DL" && sha256sum -c ../SHA256SUMS ) || { echo "checksum mismatch against data/SHA256SUMS" >&2; exit 1; }
fi

if [ "${1:-}" = "--with-extraction-deps" ]; then
  # Embedding extraction needs torch, which the evaluation container does not ship.
  # Install a CUDA build for the container's Python 3.11 into .pylib/ (gitignored).
  uv pip install --target .pylib --python-version 3.11 --python-platform x86_64-manylinux_2_28 \
     --index-url https://download.pytorch.org/whl/cu121 --extra-index-url https://pypi.org/simple \
     "torch==2.5.1" safetensors pillow
fi
echo "downloads complete in $DL"
