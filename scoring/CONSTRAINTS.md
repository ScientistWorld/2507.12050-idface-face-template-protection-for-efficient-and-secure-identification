# Constraints

- A method is a directory under `method/outputs/`, `baseline/outputs/` or `checkpoints/` with an `encoder.json` that names an encoder command and per-experiment arguments.
- The encoder maps each 512-D unit template to an integer code of dimension `D ≤ 512` (same `D` for gallery and probes), independently of every other template: no state carried between calls, no use of other rows of the batch, no use of files written during evaluation. The evaluator checks this by re-encoding random subsets in a different order and fails the run on any difference.
- The encoder must not read evaluation data or labels other than the templates it is given (in particular nothing under `eval/`), and must not contact the network.
- Codes are integers with `|value| ≤ 2^20`. Match scores are the cosine of the codes; the evaluator computes them.
- Budgets: `synthetic_identification` mean ciphertext additions per probe ≤ 680 and ≥ 5 templates per 50-bit slot; `synthetic_identification_compressed` ≤ 124 and ≥ 8. Additions are 2 × (‖q‖₁ − 1); packing uses the digit bound B = min(max‖g‖₁·max|q|, max‖q‖₁·max|g|).
- An encoder call may take at most 10 minutes.
- Do not train a classifier that maps templates to the benchmark's identities; methods may learn a representation from the development split.
- Do not change the benchmark data, its generator, the evaluators or the budgets.
