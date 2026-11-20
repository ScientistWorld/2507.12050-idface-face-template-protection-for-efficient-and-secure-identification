# Targets

Maximize `tpir_at_fpir_0.01` in both `face_identification` and `face_identification_compressed` while satisfying their fixed encrypted-cost budgets in every draw. Secondary quantities are stricter-FPIR TPIR, looser-FPIR TPIR, top-1, open-set AUC and MRR with coefficients listed in `reference.json`.

The reference baseline is the measured `idface` row in `scores_test.json`, reproduced serially from the final code. [RESULTS.md](RESULTS.md) reports its utility and the development/test comparison. The accuracy gap left by integer representation on mixed-quality real captures is the target for improvement; cost accounting and method-written metadata earn no credit.

An improvement must preserve the per-template interface and feasibility. The paired headroom audit compares each encoder on identical hidden inputs and estimates uncertainty by resampling people across all draws.
