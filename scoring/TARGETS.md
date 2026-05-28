# Targets

Primary target: maximize `tpir_at_fpir_0.01` in `synthetic_identification` while preserving IDFace's additive-only encrypted database matching.

Secondary targets:

- Keep `ciphertext_multiplications_per_query = 0`.
- Keep `ciphertext_rotations_per_query = 0`.
- Report additive count, decryptions, and packing factor for IDFace-style methods.
- Cover both `idface_341_341` and the compressed `idface_341_63` setting.
- Improve identification accuracy without increasing embedding dimension or using additional training data.
