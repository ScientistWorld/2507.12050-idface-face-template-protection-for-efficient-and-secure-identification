# Experiments

## `synthetic_identification`

Portable benchmark for privacy-preserving biometric identification. The fixed data generator creates 512-dimensional unit-vector biometric templates, one enrolled gallery template per identity, genuine noisy queries with identity labels, and impostor queries that should be rejected at fixed FPIR thresholds.

Run path:

- `scripts/baseline.sh` writes reference baseline artifacts.
- `scripts/method.sh` writes reproduced protected-method artifacts.
- `scripts/evaluate.sh` reads prediction artifacts and writes `scoring/scores.json`.

Primary metric: `tpir_at_fpir_0.01`.

Expected interpretation:

- `plain` is the unprotected cosine-search upper bound.
- `random` verifies that the evaluator does not grant credit to arbitrary scores.
- Protected-method rows test whether a submitted representation preserves identification utility while storing enrolled templates in a protected form and reporting machine-independent operation costs.
- Optional secure-computation smoke rows can be included when a method provides an additional artifact showing that protected stored templates are actually searched through the claimed protected computation path.

## Paper-Reported Reference Groups

`face_benchmark_accuracy` and `efficiency_1m` in `scoring/reference.json` record published reference numbers for context and target alignment. They are not present in `scoring/scores.json`, so the portable gym does not rank future methods on those groups.
