# Evaluation

The evaluator reads prediction artifacts from method or baseline output directories. It does not rerun the method.

Each artifact directory must contain `predictions.npz` with:

- `genuine_scores`: score matrix shaped `[num_genuine_queries, num_gallery]`
- `impostor_scores`: score matrix shaped `[num_impostor_queries, num_gallery]`
- `genuine_labels`: identity label for each genuine query
- `gallery_labels`: identity label for each gallery template

Metrics:

- `top1_identification`: fraction of genuine queries whose highest-scoring gallery identity is correct.
- `tpir_at_fpir_0.1`: true-positive identification rate when the threshold is set from impostor queries at FPIR 0.1.
- `tpir_at_fpir_0.01`: true-positive identification rate at FPIR 0.01.
- Operation-count metrics report whether a protected method keeps encrypted matching addition-only.

`scripts/evaluate.sh` writes `scoring/scores.json`.
