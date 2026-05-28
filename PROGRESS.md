# Progress

## What Works

- Paper files were missing from the workspace, so arXiv 2507.12050 was fetched into `paper/`.
- The source archive confirms the core method: top-alpha ternary transformation, positive/negative encoding, additive homomorphic-style database inner products, and decoding.
- Implemented a reusable IDFace pipeline in `method/` and baselines in `baseline/`.
- Implemented an evaluator that reads prediction artifacts and writes `scoring/scores.json`.
- `python validate.py` passes for `scoring/reference.json`.
- Continuing audit on 2026-05-28 verified that the implementation is the paper's actual IDFace computation rather than a surrogate, and that `eval/` reads artifacts without importing or rerunning `method/`.

## Results Achieved

- CPU smoke job `369146f1-281` executed the pipeline but failed final validation because `scores.json` emitted undeclared metrics and the random baseline was missing from `reference.json`.
- The same job exposed a synthetic-data bug: unscaled Gaussian noise made both gallery and query embeddings effectively random, so the plain baseline top-1 score was only 0.002.
- CPU smoke job `5ede7b09-dba` completed successfully. On `synthetic_identification`, plain achieved top-1 `1.0` and `tpir_at_fpir_0.01 = 1.0`; random achieved `0.0`; IDFace `alpha=341,beta=341` achieved top-1 `0.9995` and `tpir_at_fpir_0.01 = 0.986` with zero ciphertext multiplications/rotations.
- CPU smoke job `58a94f2d-fe7` completed successfully with the compressed setting. IDFace `alpha=341,beta=63` achieved top-1 `0.936`, `tpir_at_fpir_0.1 = 0.8535`, and `tpir_at_fpir_0.01 = 0.714`, while reducing additive operations per query from `680` to `124` and keeping zero ciphertext multiplications/rotations.
- Continuing audit ran `python validate.py --compare` successfully and added `scoring/EXPERIMENTS.md` plus an explicit compressed-output argument in `scripts/evaluate.sh`. Direct `scripts/evaluate.sh` execution on the login Python failed because `numpy` is only installed by `environment/setup.sh`; a CPU test job was submitted to verify the script in the packaged environment.
- CPU test job `6313c13f-d71` completed successfully after the audit changes. It ran `scripts/evaluate.sh` inside the packaged container and `python validate.py --compare`; all scoring and structure checks passed.
- Continuing audit found that the compressed packing implementation used `max(alpha,beta)+1` as the packing base. The paper's decoded digit bound is `min(alpha,beta)`, so this has been fixed to `min(alpha,beta)+1` and a deterministic method self-check was added. The old `scores.json` still reflects the pre-fix run until the queued CPU test completes.

## What Remains

- Rerun `scripts/reproduce.sh` in the packaged environment after the compressed-packing fix and update `scoring/scores.json`; the expected `idface_341_63` packing factor is `8`.
- If that run passes, restore the milestone to `core_claim_plus`.
- Higher milestones would require acquiring the original AdaFace/WebFace12M embedding pipeline and restricted/discontinued face benchmarks, which is beyond the reusable synthetic gym packaged here.

## Issues Encountered

- The paper was not present at the provided local path initially; it was fetched from arXiv.
- The login environment does not currently have `numpy`, so full smoke testing is deferred to the containerized CPU job.
- First container build failed because `ghcr.io/astral-sh/uv:python3.11-bookworm-slim` is not an accepted portable Docker Hub base. The container now uses `python:3.11-slim-bookworm`, and `setup.sh` falls back to `python -m pip install numpy` if `uv` is unavailable.
- Fixed the synthetic generator to scale Gaussian noise by `sqrt(dim)`, and aligned emitted evaluation metrics with `scoring/reference.json`.
- Corrected the compressed IDFace packing base from `max(alpha,beta)+1` to `min(alpha,beta)+1`; this affects the reported packing factor for the `alpha=341,beta=63` setting but not the transformed score arithmetic.

## Deviations from Paper

- Exact face datasets are not used in the portable benchmark: IJB-C distribution is discontinued, AgeDB requires an email/password flow, and the full AdaFace/WebFace12M pipeline is heavyweight for this gym.
- The implementation uses a deterministic additive HE mock instead of IPCL/HEAAN ciphertext objects. It preserves IDFace's transform/packing/additive-inner-product/decode computation and records machine-independent operation counts.
