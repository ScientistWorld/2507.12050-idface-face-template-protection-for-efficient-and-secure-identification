# Design Notes

## Checks Performed

- Read `eval/train/evaluate.py`, `eval/test/evaluate.py`, `scripts/evaluate_train.sh`, `scripts/evaluate_test.sh`, and `scoring/reference.json` side by side.
- Confirmed the train script calls `eval/train/evaluate.py` and writes `scoring/scores_train.json`.
- Confirmed the test script calls `eval/test/evaluate.py` and writes `scoring/scores_test.json`.
- Confirmed both split evaluators read method-produced `predictions.npz` artifacts instead of regenerating the experiment inline.
- Confirmed method discovery is directory based and supports `--method NAME=PATH`; there is no hardcoded single method default.
- Grepped for train/test cross-imports and paper-agreement metric names.
- Ran `bash -n` on both train/test shell scripts.
- Confirmed `scoring/scores_train.json` and `scoring/scores_test.json` do not exist.

## Changes Made

- Added train/test metrics that triangulate the same prediction artifacts from additional angles:
  - `mean_reciprocal_rank` for ranking quality beyond exact top-1 success.
  - `tpir_at_fpir_0.001` for a stricter impostor-tail threshold than the visible primary metric.
  - `open_set_score_auc` for threshold-independent genuine-vs-impostor separation.
- Kept the existing train/test row split style, but strengthened it with metric-level triangulation so a method tuned only to `top1_identification` or `tpir_at_fpir_0.01` is more likely to show a held-out gap.
- Closed a metadata shortcut: non-baseline methods that omit operation counts now receive conservative operation-count penalties instead of silently avoiding efficiency penalties. The known `plain` and `random` baselines still receive explicit baseline operation metadata.
- Updated `scoring/reference.json` so the scored benchmark surface is the portable artifact-backed `synthetic_identification` experiment with weight `1.0`.
- Marked the paper-table-only experiments as context-only with weight `0.0` and coefficient `0.0`, preserving their reported result values while preventing unavailable paper benchmarks and hardware-dependent timing from affecting the local gym score.
- Added required `higher_is_better`, `coefficient`, and `description` fields to every metric entry.

## Problems Fixed

- Context-only paper metrics were previously weighted even though the train/test evaluators do not compute them. This could make future score files incomplete or force scoring against unavailable benchmarks rather than the local scientific quantity.
- `identify_seconds` was previously a nonzero scoring metric in `reference.json`; wall-clock speed is hardware-dependent and is no longer part of the metric definitions.
- Missing operation metadata previously let a custom method avoid efficiency penalties. The split now penalizes absent non-baseline operation metadata.

## Runtime Concerns For Next Iteration

- I did not run the Python evaluators or produce scores, per this iteration's constraints.
- The `tpir_at_fpir_0.001` metric uses about 1000 impostor rows per split after the 50/50 row split, so it is intentionally stricter but may be higher variance than `tpir_at_fpir_0.01`.
- The train/test split re-scores existing `predictions.npz` outputs rather than running fresh inference. This keeps test lightweight, but it means the next runner should verify that future methods consistently emit full genuine and impostor score matrices for all rows.
- The legacy `scripts/evaluate.sh` and `eval/evaluate.py` are outside this train/test iteration's editable scope and still represent the original unsplit evaluator; train/test scoring should use `scripts/evaluate_train.sh` and `scripts/evaluate_test.sh`.
