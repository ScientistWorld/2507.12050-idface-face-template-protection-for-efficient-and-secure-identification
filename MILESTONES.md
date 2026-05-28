# Reproduction Milestones

**Current: core_claim_plus**

## Progress Log

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
