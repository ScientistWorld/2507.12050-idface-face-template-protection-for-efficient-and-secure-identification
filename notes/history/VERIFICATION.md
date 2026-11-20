# Verification Report

## Initial Assessment

The inherited workspace claimed `core_claim_plus`. The claim is justified: the method code implements the paper's protected-template computation, integer packing, additive packed matching, decoding, and a small randomized encrypted smoke path. The evaluator reads prediction artifacts instead of importing `method/`, and the reproduced scores support the protected-identification claim on the portable synthetic benchmark.

## Issues Found

- Minor, fixed: `briefing/problem.md`, `briefing/evaluation.md`, and scoring guidance still contained more paper-specific wording than from-scratch mode needs.
- Minor, fixed: `scripts/evaluate.sh` only scored fixed default paths unless extra methods were passed manually, making it less reusable for future methods.
- Cosmetic, handled locally: system-managed tracked files (`README.md`, `manifest.json`, and `trajectory/*.jsonl`) were busy/read-only in this runtime and could not be restored normally; they were marked skip-worktree after confirming they are not gym deliverables.
- Residual limitation: the reusable benchmark is synthetic and smaller than the original face benchmark setting because the original datasets/full embedding pipeline are not bundled.

## Fixes Applied

- Tightened method-agnostic documentation in `briefing/` and `scoring/` while preserving the problem definition and constraints.
- Updated `eval/evaluate.py` and `scripts/evaluate.sh` to discover arbitrary `*/predictions.npz` artifacts under `baseline/outputs`, `method/outputs`, and `checkpoints`, matching the train/test evaluator behavior.
- Adjusted one nonzero metric description in `scoring/reference.json` to describe the scientific quantity directly rather than the paper's implementation.
- Re-ran `uv run --with numpy bash scripts/evaluate.sh`, `uv run --with numpy bash scripts/evaluate_train.sh`, `uv run --with numpy bash scripts/evaluate_test.sh`, `uv run --with numpy python validate.py --compare`, `uv run --with numpy python validate.py --post-reproducer`, and `uv run --with numpy python validate.py`; all passed.

## Final Judgment

The workspace is ready to serve as a gym. Improve-mode agents can modify the packaged method and be scored through artifact-based evaluation. From-scratch agents can use the method-agnostic problem, data, and eval interfaces without being told the paper's implementation details.

- Milestone: core_claim_plus
- Ready for gym use: yes
- Confidence: high
- Key limitation: synthetic benchmark and small encrypted smoke test instead of the original restricted/discontinued face datasets and large optimized HE backend
