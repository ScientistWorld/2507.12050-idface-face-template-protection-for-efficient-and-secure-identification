# Targets

Primary target: maximize `tpir_at_fpir_0.01` in `synthetic_identification` while preserving protected enrolled-template storage.

Secondary targets:

- Keep expensive protected-computation operation counts low.
- Report operation counts, reveal/decode counts, compactness, and protected-storage status for protected methods.
- Preserve ranking quality beyond top-1 through MRR, margin, and open-set AUC.
- Keep any submitted secure-computation check consistent with the same scores produced by the protected representation.
- Improve identification accuracy without increasing embedding dimension or using additional training data.
