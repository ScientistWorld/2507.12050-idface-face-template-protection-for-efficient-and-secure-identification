# Hardening evidence

`review_audit.py` is the current real-face audit. It saves the isolated reference scores, installs honest variants and repaired shortcuts as normal method directories, plants a forged test score and an empty train manifest, and runs `bash scripts/evaluate_test.sh` with no arguments. It then measures paired rank uncertainty by resampling identity clusters jointly across all 16 draws, including recalculating impostor thresholds. Official score files are restored from the isolated reproduction and audit methods removed in `finally`.

Aggregate evidence is in `review_results/`. Raw per-probe outcomes stay inside `eval/test/review_outcomes/` and are not committed. `hv_*` are honest variants; `sc_*` are attacks. The three gallery-precision variants keep the compressed reference procedure; the alpha277 and weaker127 variants also change query sparsity.

The older `audit.py`, `rank_bootstrap.py`, `results/` and `PREVIOUS_HARDENING.md` document the retired synthetic protocol. They are retained as before evidence and are not runnable against the current interface without adaptation. The new job does not replay unrelated old attacks.
