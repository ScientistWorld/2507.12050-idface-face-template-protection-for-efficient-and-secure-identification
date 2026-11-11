# Method

IDFace protects biometric templates for large-scale identification by adapting the template representation to additively homomorphic encrypted database search.

The paper's algorithmic steps:

1. Apply `T_alpha` to every enrolled unit vector: keep the `alpha` largest absolute components, replace them by their signs, and set all other components to zero.
2. Split each ternary vector into positive and negative binary parts.
3. Pack `m` transformed templates into one vector using base-`p` encoding, `p = min(alpha, beta) + 1`, `m = floor(n / log2 p)` for an `n`-bit plaintext slot (50 bits for CKKS).
4. For a query, apply `T_beta`, split signs, and compute four binary inner products between enrolled/query sign parts.
5. Homomorphically add those four products into two packed accumulators (same-sign and opposite-sign counts): `2(beta - 1)` ciphertext additions, no multiplications or rotations, 2 decryptions.
6. Decode the packed accumulators and subtract opposite-sign from same-sign counts to recover the transformed-template scores.

In this gym the reference method is the encoder `method/encode_idface.py` (steps 1 and 4), registered in `method/outputs/idface/encoder.json`. The evaluator computes exactly the decoded result of steps 2–6 (the integer inner products of the codes) and the cost of steps 3 and 5 from the codes. The reference runs the paper's operating points: `alpha=beta=341` (680 additions, 5 templates per slot) for `synthetic_identification` and `alpha=341, beta=63` (124 additions, 8 templates per slot) for `synthetic_identification_compressed`.

`method/idface.py` also implements the packed encode/decode database; `method/self_check.py` verifies that its packed computation equals the code inner products the evaluator scores, and `method/run_encrypted_idface.py` runs a small real-Paillier database (64 identities, 256-bit key) whose decrypted scores must equal the plaintext packed arithmetic.

## Deviations

- Synthetic 512-D templates with face-embedding-like coordinate statistics replace AdaFace embeddings of IJB-C and the verification benchmarks.
- Encrypted search is evaluated through its exact decrypted result and machine-independent operation counts; no wall-clock HE timing (IPCL/HEaaN) is reproduced.
- The gallery is 10,000 identities, not the paper's 1M-identity efficiency setting (the per-probe cost is per packed block and does not depend on gallery size).
