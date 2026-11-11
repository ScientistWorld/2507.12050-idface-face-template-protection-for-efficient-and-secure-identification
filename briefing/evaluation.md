# Evaluation

The evaluator runs each method's encoder itself and computes every scored number from the codes it returns. Nothing a method writes besides its codes (scores, labels, costs, flags, metadata) is read.

## Method interface

A method is a directory under `method/outputs/`, `baseline/outputs/` or `checkpoints/` containing `encoder.json`:

```json
{
  "command": ["python", "method/my_encoder.py"],
  "experiments": {
    "synthetic_identification": {"args": ["--my-option", "1"]},
    "synthetic_identification_compressed": {"args": ["--my-option", "2"]}
  }
}
```

For each experiment the evaluator runs, from the workspace root,
`command + args + ["--role", "gallery"|"query", "--input", IN.npz, "--output", OUT.npz]`.
`IN.npz` holds `templates`, a float32 array `[n, 512]` of unit vectors; the encoder must write `OUT.npz` with `codes`, an integer array `[n, D]`, `1 ≤ D ≤ 512`, the same `D` for both roles, `|code| ≤ 2^20`. Probe batches mix genuine and impostor probes in random order without labels.

Each experiment calls the encoder four times: a random 10% of the gallery; all probes (shuffled); the whole gallery (shuffled); a random 10% of the probes. Codes of the same template must be identical across calls, so an encoder must be a per-template function that keeps no state between calls and does not use other templates in the batch.

A directory without a usable `encoder.json` entry for an experiment, an encoder that crashes, times out (10 min per call), or writes malformed, non-integer or wrongly shaped codes, codes that change between calls, or codes over the experiment's budget is a **failed run** for that experiment and receives the worst value (0) of every scored metric.

## Scores and costs

- Match score = cosine of the integer codes (0 for an all-zero code), i.e. the decrypted additive-HE inner product normalized by code norms.
- Ciphertext additions per probe = 2 × (‖q‖₁ − 1), averaged over all probes.
- Templates per 50-bit slot = largest m with (B + 1)^m ≤ 2^50, B = min(max‖g‖₁·max|q|, max‖q‖₁·max|g|) over all codes of the run.

Budgets: `synthetic_identification` ≤ 680 additions and ≥ 5 templates per slot; `synthetic_identification_compressed` ≤ 124 additions and ≥ 8 templates per slot.

## Metrics (per experiment, all higher is better)

- `tpir_at_fpir_0.01` (primary): fraction of genuine probes whose true identity is the strict unique top match and whose score exceeds the threshold at which 1% of impostor probes are accepted (threshold from the benchmark's own impostor probes, accept on `>`).
- `tpir_at_fpir_0.001`, `tpir_at_fpir_0.1`: the same at 0.1% and 10% FPIR.
- `top1_identification`: closed-set rank-1 rate; a tie with a wrong identity is an error.
- `mean_reciprocal_rank`: tied wrong identities rank ahead of the true one.
- `open_set_score_auc`: probability that a genuine probe's true-identity score exceeds an impostor probe's highest score (ties ½).

Each experiment's output also records `_diagnostics` (status, failure reason, additions, packing, code dimension per method) and `_context` (accuracy of unprotected float cosine matching on the same split, an unreachable upper reference). These are not scored.

## Scripts

- `scripts/evaluate_train.sh` scores every method directory on the visible development split and writes `scoring/scores_train.json`.
- `scripts/evaluate_test.sh` (no arguments) scores every method directory on the hidden test split and writes `scoring/scores_test.json`.
- `scripts/evaluate.sh` writes the development scores to `scoring/scores.json`.
