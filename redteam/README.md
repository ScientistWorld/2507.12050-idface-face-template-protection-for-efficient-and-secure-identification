# Gym scoring audit

Each case has a standalone `run.sh`. It constructs its artifact in
`method/outputs/audit_<case>`, runs the visible training evaluation, then runs
`bash scripts/evaluate_test.sh` **with no arguments**, in a fresh subprocess.
The evaluator and Python environment are never modified. Method builders use
only the future agent's visible data, method, baseline, and training artifacts.
`summarize.py` and `REDTEAM.md` are post-run analysis, not submitted methods.
No test script changes are needed when the gym restores its evaluator.

Run every case with `python redteam/audit.py all` inside the gym container.
The harness restores both scoring files after each case and deletes its
installed candidate output. Each folder retains `run.log`, `status.json`,
`scores_train.json`, `scores_test.json`, and metadata. A nonzero test exit means
that folder's score file is stale, as marked in `status.json`; it is never
counted as a successful scored method. `remaining` resumes unfinished cases.
All 36 cases completed in two CPU jobs; two deliberately malformed artifacts
made the hidden evaluator fail, as recorded in their status files.

`reference_seed_*` regenerates the same generator with three independent data
seeds, since IDFace itself has no training or randomized matching. Three
`reference_repeat_*` cases also rerun the original deterministic method on the
fixed benchmark. `variant_255_*` changes alpha/beta to 255; `variant_512_*`
removes magnitude-based sparsity. `variant_beta127_*` increases query components
relative to `variant_beta63_*`, retaining the same protected representation.
The exhaustive search shortcut `shortcut_bruteforce_cosine` is unprotected and
not a valid privacy-preserving improvement. Its original run records retain
its historical name; see that folder's PROVENANCE.md.

Rank uses direction, absolute coefficients, experiment weights and population
standard deviations over the documented attempt cohort. It is reported as a
difference from the reproduced main method in original_scores_test.json.
There is no fixed scalar rank: future attempts change standard deviations.
`summary.json` records the complete finite audit cohort (38 rows: five shipped
methods and 33 finite successful cases, including one empty result) and a
calibration cohort (25 rows: shipped methods, honest variants/repeats, and the
explicitly unprotected exhaustive baseline control). The latter retains the
historical key `honest_attempts`. Comparisons that dominate the reference on
every scored metric are independent of the finite cohort. Missing rows receive
zero contribution under the stated skip-missing rule; nonfinite values and
failed tests receive no invented numeric rank. Empty results do not prove that
an external scheduler will accept a method with no result row.

Small JSON artifacts, original score files, logs and the complete summary are
committed. Large prediction arrays and generated data are recreated by run.sh;
local caches are ignored. Summary computation itself uses only Python's
standard library and can run outside the gym container.
