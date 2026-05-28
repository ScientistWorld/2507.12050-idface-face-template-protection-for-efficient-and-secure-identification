# Reproduction Milestones

**Current: core_claim_plus**

## Progress Log

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
