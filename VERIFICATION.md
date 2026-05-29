# Verification Report

## Initial Assessment

The inherited workspace claimed `core_claim_plus`. That claim was mostly justified: the method code implements the IDFace-style top-k transform, integer packing, additive packed matching, decoding, and a small Paillier encrypted smoke path; the evaluator reads method artifacts instead of importing `method/`; and prior scores supported the protected-identification claim on the portable synthetic benchmark.

## Issues Found

- Critical, fixed: strict method-agnostic guidance in `scoring/EXPERIMENTS.md` and related scoring docs exposed implementation-specific details that would compromise from-scratch mode.
- Critical, fixed: the scored synthetic benchmark could over-reward unprotected raw-vector search because accuracy metrics alone gave the plain baseline perfect retrieval utility.
- Minor, fixed: `briefing/evaluation.md` and result documentation did not clearly describe all scored metrics and the distinction between paper context rows and local synthetic benchmark reference rows.
- Residual limitation: the reusable benchmark is synthetic and smaller than the original face benchmark setting because the original datasets/full embedding pipeline are not bundled.

## Fixes Applied

- Rewrote `scoring/EXPERIMENTS.md`, `scoring/TARGETS.md`, `scoring/CONSTRAINTS.md`, and `scoring/DIRECTION.md` to describe the problem and allowed research direction without leaking the paper's concrete implementation.
- Added a scored `protected_template_storage` metric and method-output metadata so protected-template methods receive credit for the core privacy constraint while unprotected baselines remain visible but cannot win on retrieval accuracy alone.
- Updated `eval/`, `eval/train/`, `eval/test/`, and method artifact writers so `scores.json`, `scores_train.json`, and `scores_test.json` all include the new metric.
- Regenerated scores with `scripts/reproduce.sh`, verified train/test scripts, and ran both validation modes successfully.

## Final Judgment

The workspace is ready to serve as a gym. Improve-mode agents can modify the packaged method and be scored through artifact-based evaluation. From-scratch agents can use the method-agnostic problem, data, and eval interfaces without being told the paper's implementation details.

- Milestone: core_claim_plus
- Ready for gym use: yes
- Confidence: medium
- Key limitation: synthetic benchmark and small encrypted smoke test instead of the original restricted/discontinued face datasets and large optimized HE backend
