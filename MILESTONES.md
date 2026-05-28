# Reproduction Milestones

**Current: core_claim_plus**

## Progress Log

### [2026-05-28 23:26] - core_claim_plus
- Implemented IDFace's top-alpha/top-beta ternary transform, positive/negative base-p packing, additive-only score computation, and decoding.
- Ran the portable synthetic identification benchmark with plain, random, IDFace `(alpha=341,beta=341)`, and compressed IDFace `(alpha=341,beta=63)` outputs.
- `python validate.py --compare` passes; IDFace reaches `tpir_at_fpir_0.01 = 0.986` in the high-accuracy setting and `0.714` in the compressed setting with zero ciphertext multiplications and rotations.

### [2026-05-28 23:30] - core_claim_plus
- CPU test job `6313c13f-d71` verified the standalone evaluator in the packaged container.
- `scripts/evaluate.sh` and `python validate.py --compare` completed with exit code 0 after adding `scoring/EXPERIMENTS.md` and making compressed-output evaluation explicit.

## Stop Justification
- Completed at milestone `core_claim_plus`.
