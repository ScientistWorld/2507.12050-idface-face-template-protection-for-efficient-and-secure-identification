# Overview

IDFace is a biometric template protection method for face identification. It transforms unit face embeddings into sparse ternary templates and packs multiple protected templates so encrypted database matching can be performed with additions instead of expensive encrypted multiplications.

This reproduction implements the core IDFace computation and evaluates whether transformed protected templates preserve identification accuracy on a portable synthetic embedding benchmark. It also includes a small Paillier-backed encrypted run that verifies packed templates can be searched through additive homomorphic operations and decode to the same scores.

---

# Problem Definition

The task is privacy-preserving biometric identification over unit-norm templates.

Given an enrolled gallery of identity templates and a query template, the system must identify the matching enrolled subject when the query is genuine and reject non-enrolled impostor queries. Templates are fixed 512-dimensional real-valued unit vectors, matching quality is judged from gallery-query scores, and the benchmark fixes:

- one enrolled gallery template per identity,
- genuine query templates with identity labels,
- impostor query templates that should be rejected at calibrated thresholds.

The problem is method-agnostic. Any submitted method may use any protected representation or matching procedure, provided it writes gallery-query score matrices in the required artifact format and does not store enrolled gallery templates as raw reusable unit vectors when claiming protected-template performance.

## Portable Dataset

The gym uses a reproducible synthetic unit-vector benchmark in `data/generate_synthetic.py`. The generated data preserves the relevant identification structure: high-dimensional normalized templates, same-identity query variation, many enrolled identities, and impostor queries used to set false-positive identification thresholds.

---

# Method

IDFace protects biometric templates for large-scale identification by adapting the template representation to additive homomorphic encrypted database search.

The implementation follows the paper's algorithmic steps:

1. Apply `T_alpha` to every enrolled unit vector: keep the `alpha` largest absolute components, replace them by their signs, and set all other components to zero.
2. Split each ternary vector into positive and negative binary parts.
3. Pack `m` transformed templates into one vector using base-`p` encoding.
4. For a query, apply `T_beta`, split signs, and compute four binary inner products between enrolled/query sign parts.
5. Homomorphically add those four products into two packed accumulators: same-sign counts and opposite-sign counts.
6. Decode packed accumulators and subtract opposite-sign counts from same-sign counts to recover transformed-template scores.

The paper instantiates the additive database with Paillier or CKKS. This gym uses two execution modes:

- The main benchmark uses deterministic packed integer arrays to reproduce the IDFace arithmetic at useful synthetic-benchmark scale and records the corresponding encrypted operation counts.
- A smaller `idface_paillier_small` smoke test uses a pure-Python randomized Paillier implementation for actual encrypted template storage, homomorphic additions/scalar multiplications, decryption, and decode. It checks that decrypted encrypted scores exactly match the packed IDFace arithmetic.

The default reproduction runs the paper's high-accuracy setting `alpha=341,beta=341` and the compressed setting `alpha=341,beta=63`. The compressed setting uses the paper's smaller packing base `p=min(alpha,beta)+1`, so a 50-bit CKKS-style slot packs 8 templates at `beta=63` instead of 5 templates at `beta=341`.

## Deviations

- Uses synthetic 512-D unit embeddings instead of AdaFace embeddings on gated/discontinued face benchmarks.
- Uses a small pure-Python Paillier smoke test rather than optimized IPCL/HEAAN ciphertext libraries for the portable encrypted check.
- Does not reproduce wall-clock speed; the evaluator uses machine-independent operation counts.

---

# Evaluation

The evaluator reads prediction artifacts from submitted method or baseline output directories. It does not rerun the method or import method code.

Each artifact directory must contain `predictions.npz` with:

- `genuine_scores`: score matrix shaped `[num_genuine_queries, num_gallery]`
- `impostor_scores`: score matrix shaped `[num_impostor_queries, num_gallery]`
- `genuine_labels`: identity label for each genuine query
- `gallery_labels`: identity label for each gallery template

Primary retrieval metrics:

- `top1_identification`: fraction of genuine queries whose highest-scoring gallery identity is correct.
- `tpir_at_fpir_0.1`: true-positive identification rate when the threshold is set from impostor queries at FPIR 0.1.
- `tpir_at_fpir_0.01`: true-positive identification rate at FPIR 0.01.
- `mean_reciprocal_rank`, `mean_genuine_rank_margin`, and `open_set_score_auc`: ranking, margin, and threshold-independent separation checks.
- `tpir_at_fpir_0.001`: stricter tail operating point.

Resource and protection metrics are read from artifact metadata. They report machine-independent operation counts, compactness, and whether enrolled templates are stored in a protected representation instead of raw reusable unit vectors. Wall-clock runtime is not scored.

`scripts/evaluate.sh` writes `scoring/scores.json`.

---

# Reproduction Log

### Iteration 1: gpt-5.5
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 14m | **GPU**: 0.0h
- **Jobs**: 3 total (2 completed, 1 failed)

<details>
<summary>Progress Log</summary>

### [2026-05-28 00:00] - none
- Started reproduction work.
- Retrieved the missing arXiv paper and source archive for IDFace.

### [2026-05-28 00:20] - none
- Implemented IDFace, plain, and random pipelines.
- Packaged evaluator, reference numbers, briefing files, and container scripts.
- Submitting CPU smoke job to test the containerized reproduction end to end.

### [2026-05-28 00:35] - none
- Fixed environment build portability failure by replacing the GHCR uv image with Docker Hub `python:3.11-slim-bookworm`.
- Resubmitting the same CPU smoke job.

### [2026-05-28 19:25] - none
- CPU smoke job ran the pipeline but failed score-schema validation.
- Fixed metric declarations and a synthetic-data noise bug that made the plain baseline random-level.
- Resubmitting CPU smoke job.

### [2026-05-28 19:35] - core_claim
- CPU smoke job completed and passed validation.
- Reproduced IDFace on the portable synthetic benchmark: `tpir_at_fpir_0.01 = 0.986`, top-1 `0.9995`, with zero ciphertext multiplications and rotations.
- Added the paper's compressed `beta=63` setting for the next job.

### [2026-05-28 19:45] - core_claim_plus
- Compressed `alpha=341,beta=63` setting completed and passed validation.
- Reproduced the expected accuracy/efficiency trade-off: top-1 `0.936`, `tpir_at_fpir_0.01 = 0.714`, zero ciphertext multiplications/rotations, and additive operations reduced from `680` to `124`.
- Final packaged environment is ready for reuse.

</details>

### Iteration 2: gpt-5.5
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 3m | **GPU**: 0.0h
- **Jobs**: 4 total (3 completed, 1 failed)

<details>
<summary>Progress Log</summary>

### [2026-05-28 23:26] - core_claim_plus
- Implemented IDFace's top-alpha/top-beta ternary transform, positive/negative base-p packing, additive-only score computation, and decoding.
- Ran the portable synthetic identification benchmark with plain, random, IDFace `(alpha=341,beta=341)`, and compressed IDFace `(alpha=341,beta=63)` outputs.
- `python validate.py --compare` passes; IDFace reaches `tpir_at_fpir_0.01 = 0.986` in the high-accuracy setting and `0.714` in the compressed setting with zero ciphertext multiplications and rotations.

### [2026-05-28 23:30] - core_claim_plus
- CPU test job `6313c13f-d71` verified the standalone evaluator in the packaged container.
- `scripts/evaluate.sh` and `python validate.py --compare` completed with exit code 0 after adding `scoring/EXPERIMENTS.md` and making compressed-output evaluation explicit.

</details>

### Iteration 3: gpt-5.5
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 27m | **GPU**: 0.0h
- **Jobs**: 4 total (3 completed, 1 failed)

<details>
<summary>Progress Log</summary>

### [2026-05-28 23:38] - core_claim
- Audited the inherited workspace and confirmed prior packaged CPU jobs reproduced the core IDFace claim on the synthetic identification benchmark.
- Found and fixed a compressed-packing issue: IDFace's packing base must be tied to `min(alpha, beta) + 1`, not `max(alpha, beta) + 1`, so the `alpha=341,beta=63` setting can pack 8 templates under the 50-bit plaintext model.
- Added `method/self_check.py` to verify top-alpha sparsity, encode/decode arithmetic, direct transformed-score equivalence, and compressed packing before future benchmark runs.
- A post-fix CPU test job is queued through `action.yaml`; milestone remains `core_claim` until the updated scores are produced by the packaged run.

### [2026-05-28 23:39] - core_claim
- Rechecked the workspace and found no new post-fix job directory; `scoring/scores.json` still reflects the old `idface_341_63` packing factor of `5`.
- Refreshed `action.yaml` to resubmit the packaged CPU reproduction so the corrected implementation can produce updated scores.

### [2026-05-28 23:42] - core_claim_plus
- Ran the deterministic IDFace self-check and refreshed the compressed `alpha=341,beta=63` method output after the packing fix.
- Re-ran the independent evaluator; `scoring/scores.json` now reports `idface_341_63.pack = 8`, `top1_identification = 0.936`, and `tpir_at_fpir_0.01 = 0.714`.
- Verified `python validate.py --compare` and `python validate.py --post-reproducer`; both passed.

### [2026-05-28 23:57] - core_claim_plus
- Continuing-agent audit reviewed `method/`, `eval/`, `baseline/`, `data/`, scripts, scoring files, briefing files, and environment files.
- Confirmed the implementation is the IDFace algorithmic computation rather than a surrogate: top-alpha ternary transform, positive/negative splitting, base-`p` packing, additive packed inner products, and decoding are all present.
- Verified the evaluator reads prediction artifacts independently from `method/`; `uv run --with numpy bash scripts/evaluate.sh`, `python validate.py --compare`, `python validate.py --post-reproducer`, and `uv run --with numpy python method/self_check.py` all passed.
- Restored the reset milestone to `core_claim_plus`.

</details>

### Iteration 4: gpt-5.5 (designer_stage_1)
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 4m | **GPU**: 0.0h
- **Jobs**: 4 total (3 completed, 1 failed)

<details>
<summary>Progress Log</summary>

### [2026-05-28 23:38] - core_claim
- Audited the inherited workspace and confirmed prior packaged CPU jobs reproduced the core IDFace claim on the synthetic identification benchmark.
- Found and fixed a compressed-packing issue: IDFace's packing base must be tied to `min(alpha, beta) + 1`, not `max(alpha, beta) + 1`, so the `alpha=341,beta=63` setting can pack 8 templates under the 50-bit plaintext model.
- Added `method/self_check.py` to verify top-alpha sparsity, encode/decode arithmetic, direct transformed-score equivalence, and compressed packing before future benchmark runs.
- A post-fix CPU test job is queued through `action.yaml`; milestone remains `core_claim` until the updated scores are produced by the packaged run.

### [2026-05-28 23:39] - core_claim
- Rechecked the workspace and found no new post-fix job directory; `scoring/scores.json` still reflects the old `idface_341_63` packing factor of `5`.
- Refreshed `action.yaml` to resubmit the packaged CPU reproduction so the corrected implementation can produce updated scores.

### [2026-05-28 23:42] - core_claim_plus
- Ran the deterministic IDFace self-check and refreshed the compressed `alpha=341,beta=63` method output after the packing fix.
- Re-ran the independent evaluator; `scoring/scores.json` now reports `idface_341_63.pack = 8`, `top1_identification = 0.936`, and `tpir_at_fpir_0.01 = 0.714`.
- Verified `python validate.py --compare` and `python validate.py --post-reproducer`; both passed.

### [2026-05-28 23:57] - core_claim_plus
- Continuing-agent audit reviewed `method/`, `eval/`, `baseline/`, `data/`, scripts, scoring files, briefing files, and environment files.
- Confirmed the implementation is the IDFace algorithmic computation rather than a surrogate: top-alpha ternary transform, positive/negative splitting, base-`p` packing, additive packed inner products, and decoding are all present.
- Verified the evaluator reads prediction artifacts independently from `method/`; `uv run --with numpy bash scripts/evaluate.sh`, `python validate.py --compare`, `python validate.py --post-reproducer`, and `uv run --with numpy python method/self_check.py` all passed.
- Restored the reset milestone to `core_claim_plus`.

</details>

### Iteration 5: gpt-5.5 (designer_stage_2)
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 5m | **GPU**: 0.0h
- **Jobs**: 4 total (3 completed, 1 failed)

<details>
<summary>Progress Log</summary>

### [2026-05-28 23:38] - core_claim
- Audited the inherited workspace and confirmed prior packaged CPU jobs reproduced the core IDFace claim on the synthetic identification benchmark.
- Found and fixed a compressed-packing issue: IDFace's packing base must be tied to `min(alpha, beta) + 1`, not `max(alpha, beta) + 1`, so the `alpha=341,beta=63` setting can pack 8 templates under the 50-bit plaintext model.
- Added `method/self_check.py` to verify top-alpha sparsity, encode/decode arithmetic, direct transformed-score equivalence, and compressed packing before future benchmark runs.
- A post-fix CPU test job is queued through `action.yaml`; milestone remains `core_claim` until the updated scores are produced by the packaged run.

### [2026-05-28 23:39] - core_claim
- Rechecked the workspace and found no new post-fix job directory; `scoring/scores.json` still reflects the old `idface_341_63` packing factor of `5`.
- Refreshed `action.yaml` to resubmit the packaged CPU reproduction so the corrected implementation can produce updated scores.

### [2026-05-28 23:42] - core_claim_plus
- Ran the deterministic IDFace self-check and refreshed the compressed `alpha=341,beta=63` method output after the packing fix.
- Re-ran the independent evaluator; `scoring/scores.json` now reports `idface_341_63.pack = 8`, `top1_identification = 0.936`, and `tpir_at_fpir_0.01 = 0.714`.
- Verified `python validate.py --compare` and `python validate.py --post-reproducer`; both passed.

### [2026-05-28 23:57] - core_claim_plus
- Continuing-agent audit reviewed `method/`, `eval/`, `baseline/`, `data/`, scripts, scoring files, briefing files, and environment files.
- Confirmed the implementation is the IDFace algorithmic computation rather than a surrogate: top-alpha ternary transform, positive/negative splitting, base-`p` packing, additive packed inner products, and decoding are all present.
- Verified the evaluator reads prediction artifacts independently from `method/`; `uv run --with numpy bash scripts/evaluate.sh`, `python validate.py --compare`, `python validate.py --post-reproducer`, and `uv run --with numpy python method/self_check.py` all passed.
- Restored the reset milestone to `core_claim_plus`.

</details>

### Iteration 6: gpt-5.5 (designer_stage_3)
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 3m | **GPU**: 0.0h
- **Jobs**: 5 total (4 completed, 1 failed)

<details>
<summary>Progress Log</summary>

### [2026-05-28 23:38] - core_claim
- Audited the inherited workspace and confirmed prior packaged CPU jobs reproduced the core IDFace claim on the synthetic identification benchmark.
- Found and fixed a compressed-packing issue: IDFace's packing base must be tied to `min(alpha, beta) + 1`, not `max(alpha, beta) + 1`, so the `alpha=341,beta=63` setting can pack 8 templates under the 50-bit plaintext model.
- Added `method/self_check.py` to verify top-alpha sparsity, encode/decode arithmetic, direct transformed-score equivalence, and compressed packing before future benchmark runs.
- A post-fix CPU test job is queued through `action.yaml`; milestone remains `core_claim` until the updated scores are produced by the packaged run.

### [2026-05-28 23:39] - core_claim
- Rechecked the workspace and found no new post-fix job directory; `scoring/scores.json` still reflects the old `idface_341_63` packing factor of `5`.
- Refreshed `action.yaml` to resubmit the packaged CPU reproduction so the corrected implementation can produce updated scores.

### [2026-05-28 23:42] - core_claim_plus
- Ran the deterministic IDFace self-check and refreshed the compressed `alpha=341,beta=63` method output after the packing fix.
- Re-ran the independent evaluator; `scoring/scores.json` now reports `idface_341_63.pack = 8`, `top1_identification = 0.936`, and `tpir_at_fpir_0.01 = 0.714`.
- Verified `python validate.py --compare` and `python validate.py --post-reproducer`; both passed.

### [2026-05-28 23:57] - core_claim_plus
- Continuing-agent audit reviewed `method/`, `eval/`, `baseline/`, `data/`, scripts, scoring files, briefing files, and environment files.
- Confirmed the implementation is the IDFace algorithmic computation rather than a surrogate: top-alpha ternary transform, positive/negative splitting, base-`p` packing, additive packed inner products, and decoding are all present.
- Verified the evaluator reads prediction artifacts independently from `method/`; `uv run --with numpy bash scripts/evaluate.sh`, `python validate.py --compare`, `python validate.py --post-reproducer`, and `uv run --with numpy python method/self_check.py` all passed.
- Restored the reset milestone to `core_claim_plus`.

</details>

### Iteration 7: gpt-5.5 (packager)
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 1m | **GPU**: 0.0h
- **Jobs**: 5 total (4 completed, 1 failed)

<details>
<summary>Progress Log</summary>

### [2026-05-28 23:38] - core_claim
- Audited the inherited workspace and confirmed prior packaged CPU jobs reproduced the core IDFace claim on the synthetic identification benchmark.
- Found and fixed a compressed-packing issue: IDFace's packing base must be tied to `min(alpha, beta) + 1`, not `max(alpha, beta) + 1`, so the `alpha=341,beta=63` setting can pack 8 templates under the 50-bit plaintext model.
- Added `method/self_check.py` to verify top-alpha sparsity, encode/decode arithmetic, direct transformed-score equivalence, and compressed packing before future benchmark runs.
- A post-fix CPU test job is queued through `action.yaml`; milestone remains `core_claim` until the updated scores are produced by the packaged run.

### [2026-05-28 23:39] - core_claim
- Rechecked the workspace and found no new post-fix job directory; `scoring/scores.json` still reflects the old `idface_341_63` packing factor of `5`.
- Refreshed `action.yaml` to resubmit the packaged CPU reproduction so the corrected implementation can produce updated scores.

### [2026-05-28 23:42] - core_claim_plus
- Ran the deterministic IDFace self-check and refreshed the compressed `alpha=341,beta=63` method output after the packing fix.
- Re-ran the independent evaluator; `scoring/scores.json` now reports `idface_341_63.pack = 8`, `top1_identification = 0.936`, and `tpir_at_fpir_0.01 = 0.714`.
- Verified `python validate.py --compare` and `python validate.py --post-reproducer`; both passed.

### [2026-05-28 23:57] - core_claim_plus
- Continuing-agent audit reviewed `method/`, `eval/`, `baseline/`, `data/`, scripts, scoring files, briefing files, and environment files.
- Confirmed the implementation is the IDFace algorithmic computation rather than a surrogate: top-alpha ternary transform, positive/negative splitting, base-`p` packing, additive packed inner products, and decoding are all present.
- Verified the evaluator reads prediction artifacts independently from `method/`; `uv run --with numpy bash scripts/evaluate.sh`, `python validate.py --compare`, `python validate.py --post-reproducer`, and `uv run --with numpy python method/self_check.py` all passed.
- Restored the reset milestone to `core_claim_plus`.

</details>

### Iteration 8: gpt-5.5 (verifier)
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 12m | **GPU**: 0.0h
- **Jobs**: 5 total (4 completed, 1 failed)

<details>
<summary>Progress Log</summary>

### [2026-05-28 23:38] - core_claim
- Audited the inherited workspace and confirmed prior packaged CPU jobs reproduced the core IDFace claim on the synthetic identification benchmark.
- Found and fixed a compressed-packing issue: IDFace's packing base must be tied to `min(alpha, beta) + 1`, not `max(alpha, beta) + 1`, so the `alpha=341,beta=63` setting can pack 8 templates under the 50-bit plaintext model.
- Added `method/self_check.py` to verify top-alpha sparsity, encode/decode arithmetic, direct transformed-score equivalence, and compressed packing before future benchmark runs.
- A post-fix CPU test job is queued through `action.yaml`; milestone remains `core_claim` until the updated scores are produced by the packaged run.

### [2026-05-28 23:39] - core_claim
- Rechecked the workspace and found no new post-fix job directory; `scoring/scores.json` still reflects the old `idface_341_63` packing factor of `5`.
- Refreshed `action.yaml` to resubmit the packaged CPU reproduction so the corrected implementation can produce updated scores.

### [2026-05-28 23:42] - core_claim_plus
- Ran the deterministic IDFace self-check and refreshed the compressed `alpha=341,beta=63` method output after the packing fix.
- Re-ran the independent evaluator; `scoring/scores.json` now reports `idface_341_63.pack = 8`, `top1_identification = 0.936`, and `tpir_at_fpir_0.01 = 0.714`.
- Verified `python validate.py --compare` and `python validate.py --post-reproducer`; both passed.

### [2026-05-28 23:57] - core_claim_plus
- Continuing-agent audit reviewed `method/`, `eval/`, `baseline/`, `data/`, scripts, scoring files, briefing files, and environment files.
- Confirmed the implementation is the IDFace algorithmic computation rather than a surrogate: top-alpha ternary transform, positive/negative splitting, base-`p` packing, additive packed inner products, and decoding are all present.
- Verified the evaluator reads prediction artifacts independently from `method/`; `uv run --with numpy bash scripts/evaluate.sh`, `python validate.py --compare`, `python validate.py --post-reproducer`, and `uv run --with numpy python method/self_check.py` all passed.
- Restored the reset milestone to `core_claim_plus`.

### [2026-05-29 00:30] - core_claim_plus
- Added a pure-Python Paillier-backed IDFace smoke test to exercise actual randomized encrypted template storage and additive homomorphic matching on a small subset.
- Updated the main evaluator to emit every declared synthetic metric and score the Paillier artifact.
- Local `uv run --with numpy bash scripts/reproduce.sh` regenerated `scoring/scores.json`; `python validate.py --compare` and `python validate.py --post-reproducer` passed.

### [2026-05-29 01:05] - core_claim_plus
- Final verification preserved `core_claim_plus` after auditing folder structure, method/problem separation, reusable evaluation, scoring coefficients, and train/test evaluation artifacts.
- Rewrote method-agnostic scoring guidance to remove implementation details and added `protected_template_storage` as a scored constraint so unprotected raw-template search cannot dominate the gym.
- Re-ran `scripts/reproduce.sh`, `scripts/evaluate_train.sh`, `scripts/evaluate_test.sh`, `python validate.py --compare`, and `python validate.py --post-reproducer`; all passed.

</details>

### Iteration 9: gpt-5.5 (verifier)
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 6m | **GPU**: 0.0h
- **Jobs**: 5 total (4 completed, 1 failed)

<details>
<summary>Progress Log</summary>

### [2026-05-28 23:38] - core_claim
- Audited the inherited workspace and confirmed prior packaged CPU jobs reproduced the core IDFace claim on the synthetic identification benchmark.
- Found and fixed a compressed-packing issue: IDFace's packing base must be tied to `min(alpha, beta) + 1`, not `max(alpha, beta) + 1`, so the `alpha=341,beta=63` setting can pack 8 templates under the 50-bit plaintext model.
- Added `method/self_check.py` to verify top-alpha sparsity, encode/decode arithmetic, direct transformed-score equivalence, and compressed packing before future benchmark runs.
- A post-fix CPU test job is queued through `action.yaml`; milestone remains `core_claim` until the updated scores are produced by the packaged run.

### [2026-05-28 23:39] - core_claim
- Rechecked the workspace and found no new post-fix job directory; `scoring/scores.json` still reflects the old `idface_341_63` packing factor of `5`.
- Refreshed `action.yaml` to resubmit the packaged CPU reproduction so the corrected implementation can produce updated scores.

### [2026-05-28 23:42] - core_claim_plus
- Ran the deterministic IDFace self-check and refreshed the compressed `alpha=341,beta=63` method output after the packing fix.
- Re-ran the independent evaluator; `scoring/scores.json` now reports `idface_341_63.pack = 8`, `top1_identification = 0.936`, and `tpir_at_fpir_0.01 = 0.714`.
- Verified `python validate.py --compare` and `python validate.py --post-reproducer`; both passed.

### [2026-05-28 23:57] - core_claim_plus
- Continuing-agent audit reviewed `method/`, `eval/`, `baseline/`, `data/`, scripts, scoring files, briefing files, and environment files.
- Confirmed the implementation is the IDFace algorithmic computation rather than a surrogate: top-alpha ternary transform, positive/negative splitting, base-`p` packing, additive packed inner products, and decoding are all present.
- Verified the evaluator reads prediction artifacts independently from `method/`; `uv run --with numpy bash scripts/evaluate.sh`, `python validate.py --compare`, `python validate.py --post-reproducer`, and `uv run --with numpy python method/self_check.py` all passed.
- Restored the reset milestone to `core_claim_plus`.

### [2026-05-29 00:30] - core_claim_plus
- Added a pure-Python Paillier-backed IDFace smoke test to exercise actual randomized encrypted template storage and additive homomorphic matching on a small subset.
- Updated the main evaluator to emit every declared synthetic metric and score the Paillier artifact.
- Local `uv run --with numpy bash scripts/reproduce.sh` regenerated `scoring/scores.json`; `python validate.py --compare` and `python validate.py --post-reproducer` passed.

### [2026-05-29 01:05] - core_claim_plus
- Final verification preserved `core_claim_plus` after auditing folder structure, method/problem separation, reusable evaluation, scoring coefficients, and train/test evaluation artifacts.
- Rewrote method-agnostic scoring guidance to remove implementation details and added `protected_template_storage` as a scored constraint so unprotected raw-template search cannot dominate the gym.
- Re-ran `scripts/reproduce.sh`, `scripts/evaluate_train.sh`, `scripts/evaluate_test.sh`, `python validate.py --compare`, and `python validate.py --post-reproducer`; all passed.

### [2026-05-29 00:33] - core_claim_plus
- Final verifier preserved `core_claim_plus` after checking folder structure, download portability, problem/solution separation, scoring coefficients, train/test artifacts, and reusable evaluation.
- Tightened method-agnostic guidance in `briefing/` and `scoring/` and made `scripts/evaluate.sh` discover arbitrary `*/predictions.npz` method artifacts under standard output roots.
- Re-ran `uv run --with numpy bash scripts/evaluate.sh`, `uv run --with numpy bash scripts/evaluate_train.sh`, `uv run --with numpy bash scripts/evaluate_test.sh`, `uv run --with numpy python validate.py --compare`, `uv run --with numpy python validate.py --post-reproducer`, and `uv run --with numpy python validate.py`; all passed.

</details>

### Iteration 10: gpt-6.1-sol (redteam)
- **Milestone**: `core_claim_plus` | **Status**: done
- **Working time**: 11m | **GPU**: 0.0h

<details>
<summary>Progress Log</summary>

### [2026-05-28 23:38] - core_claim
- Audited the inherited workspace and confirmed prior packaged CPU jobs reproduced the core IDFace claim on the synthetic identification benchmark.
- Found and fixed a compressed-packing issue: IDFace's packing base must be tied to `min(alpha, beta) + 1`, not `max(alpha, beta) + 1`, so the `alpha=341,beta=63` setting can pack 8 templates under the 50-bit plaintext model.
- Added `method/self_check.py` to verify top-alpha sparsity, encode/decode arithmetic, direct transformed-score equivalence, and compressed packing before future benchmark runs.
- A post-fix CPU test job is queued through `action.yaml`; milestone remains `core_claim` until the updated scores are produced by the packaged run.

### [2026-05-28 23:39] - core_claim
- Rechecked the workspace and found no new post-fix job directory; `scoring/scores.json` still reflects the old `idface_341_63` packing factor of `5`.
- Refreshed `action.yaml` to resubmit the packaged CPU reproduction so the corrected implementation can produce updated scores.

### [2026-05-28 23:42] - core_claim_plus
- Ran the deterministic IDFace self-check and refreshed the compressed `alpha=341,beta=63` method output after the packing fix.
- Re-ran the independent evaluator; `scoring/scores.json` now reports `idface_341_63.pack = 8`, `top1_identification = 0.936`, and `tpir_at_fpir_0.01 = 0.714`.
- Verified `python validate.py --compare` and `python validate.py --post-reproducer`; both passed.

### [2026-05-28 23:57] - core_claim_plus
- Continuing-agent audit reviewed `method/`, `eval/`, `baseline/`, `data/`, scripts, scoring files, briefing files, and environment files.
- Confirmed the implementation is the IDFace algorithmic computation rather than a surrogate: top-alpha ternary transform, positive/negative splitting, base-`p` packing, additive packed inner products, and decoding are all present.
- Verified the evaluator reads prediction artifacts independently from `method/`; `uv run --with numpy bash scripts/evaluate.sh`, `python validate.py --compare`, `python validate.py --post-reproducer`, and `uv run --with numpy python method/self_check.py` all passed.
- Restored the reset milestone to `core_claim_plus`.

### [2026-05-29 00:30] - core_claim_plus
- Added a pure-Python Paillier-backed IDFace smoke test to exercise actual randomized encrypted template storage and additive homomorphic matching on a small subset.
- Updated the main evaluator to emit every declared synthetic metric and score the Paillier artifact.
- Local `uv run --with numpy bash scripts/reproduce.sh` regenerated `scoring/scores.json`; `python validate.py --compare` and `python validate.py --post-reproducer` passed.

### [2026-05-29 01:05] - core_claim_plus
- Final verification preserved `core_claim_plus` after auditing folder structure, method/problem separation, reusable evaluation, scoring coefficients, and train/test evaluation artifacts.
- Rewrote method-agnostic scoring guidance to remove implementation details and added `protected_template_storage` as a scored constraint so unprotected raw-template search cannot dominate the gym.
- Re-ran `scripts/reproduce.sh`, `scripts/evaluate_train.sh`, `scripts/evaluate_test.sh`, `python validate.py --compare`, and `python validate.py --post-reproducer`; all passed.

### [2026-05-29 00:33] - core_claim_plus
- Final verifier preserved `core_claim_plus` after checking folder structure, download portability, problem/solution separation, scoring coefficients, train/test artifacts, and reusable evaluation.
- Tightened method-agnostic guidance in `briefing/` and `scoring/` and made `scripts/evaluate.sh` discover arbitrary `*/predictions.npz` method artifacts under standard output roots.
- Re-ran `uv run --with numpy bash scripts/evaluate.sh`, `uv run --with numpy bash scripts/evaluate_train.sh`, `uv run --with numpy bash scripts/evaluate_test.sh`, `uv run --with numpy python validate.py --compare`, `uv run --with numpy python validate.py --post-reproducer`, and `uv run --with numpy python validate.py`; all passed.

</details>


---

# Reproduction Milestones

**Current: core_claim_plus**
