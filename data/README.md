# Real face templates

The frozen feature extractor is [CVLFace AdaFace IR-101 / WebFace12M](https://huggingface.co/minchul/cvlface_adaface_ir101_webface12m), matching the paper's backbone. [CVLFace](https://github.com/mk-minchul/CVLface) supplies the IR-101 architecture and RGB input convention. `extract_embeddings.py` loads the published safetensors strictly, normalizes RGB crops to [-1,1], and saves 512-D outputs in inference mode. No backbone is trained in this gym.

Public aligned-image shards are [LFW](https://huggingface.co/datasets/LSIbabnikz/lfw), [XQLFW](https://huggingface.co/datasets/LSIbabnikz/xqlfw) and [CPLFW](https://huggingface.co/datasets/LSIbabnikz/cplfw). `scripts/download.sh` fetches all 12 shards and the model using curl and verifies `data/SHA256SUMS`. These are public source artifacts, not scored answers.

The derived banks are committed for offline evaluation: `data/face_embeddings_dev.npz` and the hidden bank inside `eval/test/`. They contain normalized `embeddings`, source `identities`, image `keys` and `sources`. The partition builder and its seed live only inside `eval/test/`, and split by person across all three sources. Hidden draw construction and basis seeds also stay there; development contains no test people. Per-draw gallery/probe assignments and thresholds are never method artifacts.

To regenerate from public sources, run `bash scripts/download.sh --with-extraction-deps`, then `bash scripts/prepare_data.sh` in a GPU job (CPU extraction also works). Extraction dependencies install into `.pylib/` for Python 3.11. Normal reproduction and hidden evaluation need only NumPy and the committed banks. `prepare_smoke.py` derives a tiny visible input for the real-Paillier arithmetic check.

`generate_synthetic.py` and old synthetic audit records are historical and are not used by the real-face benchmark.
