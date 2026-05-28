# Progress

## What Works

- Paper files were missing from the workspace, so arXiv 2507.12050 was fetched into `paper/`.
- The source archive confirms the core method: top-alpha ternary transformation, positive/negative encoding, additive homomorphic-style database inner products, and decoding.
- Implemented a reusable IDFace pipeline in `method/` and baselines in `baseline/`.
- Implemented an evaluator that reads prediction artifacts and writes `scoring/scores.json`.
- `python validate.py` passes for `scoring/reference.json`.

## Results Achieved

- No reproduction run has completed yet.

## What Remains

- Run the method and evaluator through a submitted job.
- Inspect scores and decide whether the synthetic benchmark supports the core claim.

## Issues Encountered

- The paper was not present at the provided local path initially; it was fetched from arXiv.
- The login environment does not currently have `numpy`, so full smoke testing is deferred to the containerized CPU job.
- First container build failed because `ghcr.io/astral-sh/uv:python3.11-bookworm-slim` is not an accepted portable Docker Hub base. The container now uses `python:3.11-slim-bookworm`, and `setup.sh` falls back to `python -m pip install numpy` if `uv` is unavailable.

## Deviations from Paper

- Exact face datasets are not used in the portable benchmark: IJB-C distribution is discontinued, AgeDB requires an email/password flow, and the full AdaFace/WebFace12M pipeline is heavyweight for this gym.
- The implementation uses a deterministic additive HE mock instead of IPCL/HEAAN ciphertext objects. It preserves IDFace's transform/packing/additive-inner-product/decode computation and records machine-independent operation counts.
