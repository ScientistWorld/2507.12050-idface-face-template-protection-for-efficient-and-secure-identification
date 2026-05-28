# Experiments

## `synthetic_identification`

Portable benchmark for the core IDFace claim. The fixed data generator creates 512-dimensional unit-vector biometric templates, one enrolled gallery template per identity, genuine noisy queries with identity labels, and impostor queries that should be rejected at fixed FPIR thresholds.

Run path:

- `scripts/baseline.sh` writes plain and random baseline artifacts.
- `scripts/method.sh` writes IDFace artifacts for `(alpha=341,beta=341)` and `(alpha=341,beta=63)`.
- `scripts/evaluate.sh` reads those artifacts and writes `scoring/scores.json`.

Primary metric: `tpir_at_fpir_0.01`.

Expected interpretation:

- `plain` is the unprotected cosine-search upper bound.
- `random` verifies that the evaluator does not grant credit to arbitrary scores.
- `idface_341_341` tests the high-accuracy protected setting.
- `idface_341_63` tests the compressed protected setting and its accuracy/operation-count trade-off.

## Paper-Reported Reference Groups

`face_benchmark_accuracy` and `efficiency_1m` in `scoring/reference.json` record the paper's reported numbers from Tables 2 and 3. They are included for context and target setting alignment. The portable reproduction does not score these groups because the exact face benchmarks and HE backend setup are not part of the reusable local gym.
