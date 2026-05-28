# Targets

Primary target: maximize `tpir_at_fpir_0.01` in `synthetic_identification` while preserving IDFace's additive-only encrypted database matching.

Secondary targets:

- Keep `ciphertext_multiplications_per_query = 0`.
- Keep `ciphertext_rotations_per_query = 0`.
- Improve identification accuracy without increasing embedding dimension or using additional training data.
