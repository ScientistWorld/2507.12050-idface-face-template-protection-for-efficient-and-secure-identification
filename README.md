# Overview

IDFace is a biometric template protection method for face identification. It transforms unit face embeddings into sparse ternary templates and packs multiple protected templates so encrypted database matching can be performed with additions instead of expensive encrypted multiplications.

This reproduction implements the core IDFace computation and evaluates whether transformed protected templates preserve identification accuracy on a portable synthetic embedding benchmark. It also records operation counts showing the method remains addition-only.

---

# Problem Definition

The task is privacy-preserving biometric identification over unit-norm templates.

Given an enrolled gallery of identity templates and a query template, the system must return the closest identity when the query matches an enrolled subject and reject non-enrolled impostor queries. Templates are real-valued unit vectors, matching is based on inner product or cosine similarity, and the benchmark fixes a gallery, genuine queries with labels, and impostor queries.

The problem is method-agnostic: any method may transform or protect templates, but it must produce a score matrix for genuine queries and impostor queries against the fixed gallery so the evaluator can compute identification metrics at fixed false-positive identification rates.

## Portable Dataset

The original paper evaluates on LFW, CFP-FP, AgeDB, and IJB-C with AdaFace embeddings. IJB-C distribution has been discontinued and AgeDB requires an email/password flow, so this gym includes a reproducible synthetic unit-vector benchmark in `data/generate_synthetic.py`. The substitute preserves the relevant structure: 512-dimensional unit embeddings, enrolled identities, noisy genuine queries, and random impostor queries.

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

The paper instantiates the additive database with Paillier or CKKS. This gym uses a deterministic additive ciphertext mock for portability: the stored packed arrays stand in for ciphertext payloads, and method metadata records the corresponding encrypted operation counts. This preserves the computation being reproduced while avoiding unavailable HE libraries and heavy build requirements.

The default reproduction runs the paper's high-accuracy setting `alpha=341,beta=341` and the compressed setting `alpha=341,beta=63`. The compressed setting uses the paper's smaller packing base `p=min(alpha,beta)+1`, so a 50-bit CKKS-style slot packs 8 templates at `beta=63` instead of 5 templates at `beta=341`.

## Deviations

- Uses synthetic 512-D unit embeddings instead of AdaFace embeddings on gated/discontinued face benchmarks.
- Uses an additive HE mock instead of IPCL/HEAAN ciphertext objects.
- Does not reproduce wall-clock speed; the evaluator uses machine-independent operation counts.

---

# Evaluation

The evaluator reads prediction artifacts from method or baseline output directories. It does not rerun the method.

Each artifact directory must contain `predictions.npz` with:

- `genuine_scores`: score matrix shaped `[num_genuine_queries, num_gallery]`
- `impostor_scores`: score matrix shaped `[num_impostor_queries, num_gallery]`
- `genuine_labels`: identity label for each genuine query
- `gallery_labels`: identity label for each gallery template

Metrics:

- `top1_identification`: fraction of genuine queries whose highest-scoring gallery identity is correct.
- `tpir_at_fpir_0.1`: true-positive identification rate when the threshold is set from impostor queries at FPIR 0.1.
- `tpir_at_fpir_0.01`: true-positive identification rate at FPIR 0.01.
- Operation-count metrics report whether a protected method keeps encrypted matching addition-only.

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


---

# Reproduction Milestones

**Current: core_claim_plus**
