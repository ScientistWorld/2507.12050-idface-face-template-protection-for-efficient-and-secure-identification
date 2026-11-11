# Gym scoring audit

Each case has a standalone `run.sh`. It constructs its artifact in
`method/outputs/audit_<case>`, runs the visible training evaluation, then runs
`bash scripts/evaluate_test.sh` **with no arguments**, in a fresh subprocess.
The hidden evaluator and Python environment are never modified. Inputs to the
builders are limited to the future agent's visible data, method, baseline, and
training artifacts. `summarize.py` is post-run analysis, not a submitted method.

Run every case with `python redteam/audit.py all` inside the gym container.
The harness restores both scoring files after each case and deletes its
installed candidate output. Each folder retains `run.log`, `status.json`,
`scores_train.json`, `scores_test.json`, and metadata. A nonzero test exit means
that folder's score file is stale, as marked in `status.json`; it is never
counted as a successful scored method.

`reference_seed_*` regenerates the same generator with three independent data
seeds, since IDFace itself has no training or randomized matching. Three
`reference_repeat_*` cases also rerun the original deterministic method on the
fixed benchmark. `variant_255_*` changes only alpha/beta to 255; `variant_512_*`
removes magnitude-based sparsity. The exhaustive cosine baseline is explicitly
unprotected and is not claimed as a valid privacy-preserving improvement.

Rank uses direction, absolute coefficients, experiment weights and population
standard deviations over the documented attempt cohort. There is no fixed
scalar rank in the gym: future attempts change those standard deviations.
`summary.json` records both the complete finite audit cohort and an honest
cohort without shortcuts. Comparisons that dominate the reference on every
scored metric are independent of the cohort. Missing rows receive zero under
the stated skip-missing rule; nonfinite values and failed tests receive no
invented numeric rank.
