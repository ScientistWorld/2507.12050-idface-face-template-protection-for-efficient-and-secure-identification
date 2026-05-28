# Reproduction Milestones

**Current: none**

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
