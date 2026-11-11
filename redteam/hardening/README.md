# Hardening audit (iteration 11)

`audit.py` installs every case in `CASES` as a method directory under
`checkpoints/`, plants a forged `scoring/scores_test.json` and an empty
`scoring/scores_train.json`, runs `bash scripts/evaluate_test.sh` with no
arguments, runs the train evaluator, reruns the reference and the honest
variants on three further test draws (`--data-seed 101/202/303`) with
per-probe dumps for paired bootstrap statistics, then removes the cases and
restores the scoring files. Results: `results/summary.md`, `results/summary.json`,
and the raw score files in `results/`.

Cases: `hv_*` are honest variants (better: multi-level enrolled codes at the
same encrypted cost; alternative: alpha=277; weaker: (127,127)/(63,63); paper
ablation: (512,512)/(512,63)). `sc_*` are shortcuts from `REDTEAM.md`
re-expressed through the encoder interface, plus attacks on the interface
itself (stateful and batch-dependent encoders). Encoders live in `encoders/`.

Rank deltas use the gym rule: sum over experiments of weight × sum over
metrics of |coefficient| × direction × (row − reference) / cohort SD.
