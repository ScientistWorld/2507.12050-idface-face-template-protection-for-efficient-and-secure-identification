# Evaluation

The evaluator runs every encoder directory under `method/outputs/`, `baseline/outputs/` and `checkpoints/`. It computes scores, costs, thresholds and metrics itself from returned codes and its own fixed benchmark. It ignores submitted predictions, labels, sample counts, metadata, costs and verdicts. Train manifests do not determine discovery.

## Encoder interface

Register an encoder in a method directory's `encoder.json`:

```json
{
  "command": ["python", "method/my_encoder.py"],
  "experiments": {
    "face_identification": {"args": ["--setting", "1"]},
    "face_identification_compressed": {"args": ["--setting", "2"]}
  }
}
```

For each draw and experiment, the command is run from the workspace root with the experiment arguments and `--role gallery|query --input IN.npz --output OUT.npz`. The input contains `templates`, float32 unit vectors with shape `[n,512]`. Write `codes`, an integer array `[n,D]`, to the output npz: `1 <= D <= 512`, the same D for both roles, absolute coordinate at most 2^20. Queries mix genuine and impostor probes in a shuffled, unlabeled batch.

Four calls encode a random 10% gallery subset, all queries shuffled, the full gallery shuffled, and a random 10% query subset. Repeated templates must produce exactly identical codes. Each call has its own scratch directory and Linux Landlock filesystem restriction. The encoder can read its input, installed libraries, `method/`, `baseline/`, `checkpoints/`, `.pylib/`, `scripts/`, audit encoder code, and `data/face_embeddings_dev.npz`. It can write only in its call directory (including `TMPDIR`). Put learned assets in `method/` or `checkpoints/`. Other calls, evaluation code, hidden templates, labels, downloads and score files are unreadable. There is no wall-clock timeout in the encoder or method path. There is no training during evaluation.

## Costs and failure

The evaluator computes encrypted additions as `2*max(||q||_1-1,0)`, averaged over all probes of each draw. The digit bound is `B = min(max||g||_1 * max|q|, max||q||_1 * max|g|)`. Packing is the largest m with `(B+1)^m <= 2^50`. Budgets are fixed at 680 additions / 5 packed templates and 124 / 8, respectively, and must hold in every draw. Costs are per packed SIMD block, not timings or a claim about total runtime at a million identities.

Missing or malformed specs, absent experiment entries, crashes, forbidden reads, invalid codes, inconsistent codes, exceeded budgets and nonfinite or impossible metrics fail the run. Minimum task feasibility is top-1 >= 0.10 and TPIR@1% >= 0.05 in every draw. A failure anywhere assigns **zero to all six metrics in both experiments**, including experiments not run. No empty result is emitted. The evaluator continues with other methods and atomically replaces its score file.

## Scientific measurements

All six metrics are higher-is-better, bounded by [0,1], averaged equally over 16 fixed draws. Every method sees the same gallery, probes, bases and orders.

- `tpir_at_fpir_0.01` (primary, coefficient 1): fraction of genuine probes correctly identified as the strict unique top match and accepted at 1% false positive identification rate.
- `tpir_at_fpir_0.001` (0.6) and `tpir_at_fpir_0.1` (0.3): the same at 0.1% and 10% FPIR.
- `top1_identification` (0.3): closed-set strict rank-one accuracy; ties are errors.
- `open_set_score_auc` (0.25): probability the true-person genuine score exceeds an impostor's maximum gallery score, ties worth one half.
- `mean_reciprocal_rank` (0.15): tied wrong identities rank ahead of the true person.

Each FPIR threshold is the `floor(FPIR*n)`-indexed score among descending impostor maxima. Acceptance requires strict `>`, so ties cannot inflate false accepts. Similarities are cosine values, with zero vectors scoring zero. Thresholds, impostors and labels belong to the evaluator.

Both experiments have weight 0.5. Rank improvement is the sum of `weight * abs(coefficient) * direction * (candidate-reference) / population_SD`, where direction follows `higher_is_better` and SD is over the attempts being ranked. A zero-variance metric contributes zero. Only numbers under each experiment's `results` in the official score file are ranked; diagnostics and audit summaries are not.

`bash scripts/evaluate_train.sh` writes `scoring/scores_train.json`. `bash scripts/evaluate_test.sh` takes no required arguments and writes `scoring/scores_test.json`. Both discover every directory independently. `scripts/evaluate.sh` also copies train results to `scoring/scores.json`. Development and test use independent implementations and identity banks with the same protocol and difficulty. Test inputs, labels, partition and draw construction stay in `eval/test/`.
