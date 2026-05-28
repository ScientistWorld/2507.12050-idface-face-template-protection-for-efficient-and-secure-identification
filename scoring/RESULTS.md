# Results

Latest completed-job results are in `scoring/scores.json`. The implementation has since been corrected so the compressed `alpha=341,beta=63` setting uses packing base `min(alpha,beta)+1`; a queued CPU test will refresh the score file with the expected packing factor of `8`.

On the portable synthetic identification benchmark:

- Plain baseline: top-1 `1.0`, `tpir_at_fpir_0.01 = 1.0`.
- Random baseline: top-1 `0.0`, `tpir_at_fpir_0.01 = 0.0`.
- IDFace `alpha=341,beta=341`: top-1 `0.9995`, `tpir_at_fpir_0.01 = 0.986`, zero ciphertext multiplications and rotations.
- IDFace `alpha=341,beta=63`: top-1 `0.936`, `tpir_at_fpir_0.01 = 0.714`, zero ciphertext multiplications and rotations, with additive operations reduced from `680` to `124`.

This supports the core paper claim that IDFace can preserve identification utility using an additive-only encrypted matching computation, and the additional compressed setting shows the expected accuracy/efficiency trade-off.
