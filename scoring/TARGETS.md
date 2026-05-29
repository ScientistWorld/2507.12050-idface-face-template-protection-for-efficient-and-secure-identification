# Targets

Primary target: maximize `tpir_at_fpir_0.01` in `synthetic_identification` while preserving protected enrolled-template storage.

Secondary targets:

- Keep expensive encrypted-operation counts low.
- Report additive count, decryptions, compactness/packing factor, and protected-storage status for protected methods.
- Preserve ranking quality beyond top-1 through MRR, margin, and open-set AUC.
- Keep the small encrypted-computation check passing with no score drift from the submitted protected representation.
- Improve identification accuracy without increasing embedding dimension or using additional training data.
