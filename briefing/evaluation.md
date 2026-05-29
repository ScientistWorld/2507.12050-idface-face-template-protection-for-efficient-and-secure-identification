# Evaluation

The evaluator reads prediction artifacts from submitted method or baseline output directories. It does not rerun the method or import method code.

Each artifact directory must contain `predictions.npz` with:

- `genuine_scores`: score matrix shaped `[num_genuine_queries, num_gallery]`
- `impostor_scores`: score matrix shaped `[num_impostor_queries, num_gallery]`
- `genuine_labels`: identity label for each genuine query
- `gallery_labels`: identity label for each gallery template

Primary retrieval metrics:

- `top1_identification`: fraction of genuine queries whose highest-scoring gallery identity is correct.
- `tpir_at_fpir_0.1`: true-positive identification rate when the threshold is set from impostor queries at FPIR 0.1.
- `tpir_at_fpir_0.01`: true-positive identification rate at FPIR 0.01.
- `mean_reciprocal_rank`, `mean_genuine_rank_margin`, and `open_set_score_auc`: ranking, margin, and threshold-independent separation checks.
- `tpir_at_fpir_0.001`: stricter tail operating point.

Resource and protection metrics are read from artifact metadata. They report machine-independent operation counts, compactness, and whether enrolled templates are stored in a protected representation instead of raw reusable unit vectors. Wall-clock runtime is not scored.

`scripts/evaluate.sh` writes `scoring/scores.json`.
