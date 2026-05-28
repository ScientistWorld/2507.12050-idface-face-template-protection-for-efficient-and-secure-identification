# Method

IDFace protects biometric templates for large-scale identification by adapting the template representation to additive homomorphic encrypted database search.

The implementation follows the paper's algorithmic steps:

1. Apply `T_alpha` to every enrolled unit vector: keep the `alpha` largest absolute components, replace them by their signs, and set all other components to zero.
2. Split each ternary vector into positive and negative binary parts.
3. Pack `m` transformed templates into one vector using base-`p` encoding.
4. For a query, apply `T_beta`, split signs, and compute two additive database inner products: same-sign counts and opposite-sign counts.
5. Decode packed accumulators and subtract opposite-sign counts from same-sign counts to recover transformed-template scores.

The paper instantiates the additive database with Paillier or CKKS. This gym uses a deterministic additive ciphertext mock for portability: the stored packed arrays stand in for ciphertext payloads, and method metadata records the corresponding encrypted operation counts. This preserves the computation being reproduced while avoiding unavailable HE libraries and heavy build requirements.

The default reproduction runs the paper's high-accuracy setting `alpha=341,beta=341` and the compressed setting `alpha=341,beta=63`.

## Deviations

- Uses synthetic 512-D unit embeddings instead of AdaFace embeddings on gated/discontinued face benchmarks.
- Uses an additive HE mock instead of IPCL/HEAAN ciphertext objects.
- Does not reproduce wall-clock speed; the evaluator uses machine-independent operation counts.
