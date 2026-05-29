# Method

IDFace protects biometric templates for large-scale identification by adapting the template representation to additive homomorphic encrypted database search.

The implementation follows the paper's algorithmic steps:

1. Apply `T_alpha` to every enrolled unit vector: keep the `alpha` largest absolute components, replace them by their signs, and set all other components to zero.
2. Split each ternary vector into positive and negative binary parts.
3. Pack `m` transformed templates into one vector using base-`p` encoding.
4. For a query, apply `T_beta`, split signs, and compute four binary inner products between enrolled/query sign parts.
5. Homomorphically add those four products into two packed accumulators: same-sign counts and opposite-sign counts.
6. Decode packed accumulators and subtract opposite-sign counts from same-sign counts to recover transformed-template scores.

The paper instantiates the additive database with Paillier or CKKS. This gym uses two execution modes:

- The main benchmark uses deterministic packed integer arrays to reproduce the IDFace arithmetic at useful synthetic-benchmark scale and records the corresponding encrypted operation counts.
- A smaller `idface_paillier_small` smoke test uses a pure-Python randomized Paillier implementation for actual encrypted template storage, homomorphic additions/scalar multiplications, decryption, and decode. It checks that decrypted encrypted scores exactly match the packed IDFace arithmetic.

The default reproduction runs the paper's high-accuracy setting `alpha=341,beta=341` and the compressed setting `alpha=341,beta=63`. The compressed setting uses the paper's smaller packing base `p=min(alpha,beta)+1`, so a 50-bit CKKS-style slot packs 8 templates at `beta=63` instead of 5 templates at `beta=341`.

## Deviations

- Uses synthetic 512-D unit embeddings instead of AdaFace embeddings on gated/discontinued face benchmarks.
- Uses a small pure-Python Paillier smoke test rather than optimized IPCL/HEAAN ciphertext libraries for the portable encrypted check.
- Does not reproduce wall-clock speed; the evaluator uses machine-independent operation counts.
