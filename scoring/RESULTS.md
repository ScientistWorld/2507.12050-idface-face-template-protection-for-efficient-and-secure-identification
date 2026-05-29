# Results

Final reproduced results are in `scoring/scores.json`. The compressed `alpha=341,beta=63` setting uses packing base `min(alpha,beta)+1` and reports packing factor `8`.

On the portable synthetic identification benchmark:

- Plain baseline: top-1 `1.0`, `tpir_at_fpir_0.01 = 1.0`.
- Random baseline: top-1 `0.0`, `tpir_at_fpir_0.01 = 0.0`.
- IDFace `alpha=341,beta=341`: top-1 `0.9995`, `tpir_at_fpir_0.01 = 0.986`, zero ciphertext multiplications and rotations.
- IDFace `alpha=341,beta=63`: top-1 `0.936`, `tpir_at_fpir_0.01 = 0.714`, zero ciphertext multiplications and rotations, with additive operations reduced from `680` to `124`.
- Paillier encrypted IDFace small subset: top-1 `1.0`, `tpir_at_fpir_0.01 = 0.9375`, zero score error versus plaintext packed IDFace arithmetic, and randomized encrypted storage for 8,192 packed template components.

The scored synthetic benchmark now includes `protected_template_storage`, so unprotected raw-vector nearest-neighbor artifacts do not receive full credit solely by matching retrieval accuracy. This supports the core paper claim that IDFace can preserve identification utility using an additive-only encrypted matching computation, and the additional compressed setting shows the expected accuracy/efficiency trade-off.
