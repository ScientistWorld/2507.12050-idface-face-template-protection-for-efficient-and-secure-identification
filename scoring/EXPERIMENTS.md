# Experiments

Both scored experiments measure open-set identification accuracy of a protected template representation on the same benchmark, at two fixed encrypted-cost budgets. A method is a directory with `encoder.json` (see `briefing/evaluation.md`); the evaluator runs its encoder on templates only, computes match scores as the cosine of the returned integer codes (the decrypted result of additively homomorphic matching), computes the encrypted cost from the codes, and computes every metric from its own labels.

Benchmark (each split): 10,000 enrolled identities with one template each, 10,000 genuine probes, 20,000 impostor probes from never-enrolled identities; 512-D unit templates with face-embedding-like isotropic coordinates and mixed probe quality (95% usable captures, 5% degraded). The development split is `data/synthetic_embeddings.npz` (`data/generate_synthetic.py`); the hidden test split is an independent draw made by the test evaluator.

## `synthetic_identification` (weight 0.5)

Budget: mean ciphertext additions per probe ≤ 680 (= 2 × (‖q‖₁ − 1)), at least 5 gallery templates per 50-bit plaintext slot, code dimension ≤ 512. This is the encrypted cost of the high-accuracy operating point studied in the source paper.

## `synthetic_identification_compressed` (weight 0.5)

Budget: mean ciphertext additions per probe ≤ 124, at least 8 templates per 50-bit slot, code dimension ≤ 512, i.e. roughly 5.5× fewer additions and 1.6× denser packing. This is the paper's fastest operating point, where protected identification loses the most accuracy.

## Metrics (both experiments)

Primary `tpir_at_fpir_0.01` (coefficient 1.0); `tpir_at_fpir_0.001` (0.6); `tpir_at_fpir_0.1` (0.3); `top1_identification` (0.3); `open_set_score_auc` (0.25); `mean_reciprocal_rank` (0.15). Thresholds are set from the benchmark's impostor probes; ties never count as correct. A failed run (missing/crashing encoder, malformed or state-dependent codes, budget exceeded) gets 0 on every metric of that experiment.

## Rows

- `idface`: reproduced reference method (`method/outputs/idface`).
- `sign_random_subset`: signs of fixed random coordinates with the same sparsity and cost as the reference (no magnitude information); a simple baseline.
- `random_codes`: codes carrying no template information; chance-level sanity check.
- `_context.unprotected_float_cosine` (in each score file): accuracy of plain float cosine matching on the same split, which no budget-feasible code can match exactly; an upper reference, not a ranked row.

`scoring/reference.json` keeps the source paper's own reported numbers under `_paper_reported` (face benchmarks, 1M-identity timings) and the paper's IJB-C identification TPIR in the `idface`/`plain` rows for orientation; the synthetic benchmark is not IJB-C.
