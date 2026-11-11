# Targets

Primary target: maximize `tpir_at_fpir_0.01` in both `synthetic_identification` and `synthetic_identification_compressed` while staying within each experiment's encrypted-cost budget.

Secondary targets, in order of weight: `tpir_at_fpir_0.001`, `tpir_at_fpir_0.1` and `top1_identification`, `open_set_score_auc`, `mean_reciprocal_rank`.

Reference points on the hidden test split (reproduced, see `scoring/RESULTS.md`): the reference representation reaches 0.969 TPIR@1%FPIR at the 680-addition budget and 0.951 at the 124-addition budget, while unprotected float cosine matching on the same split reaches 0.976. The gap to that unprotected context, largest at the compressed budget, is the available headroom; a code that only rearranges the reference's cost (same additions, same packing) without using it better does not gain.

Non-targets: anything that changes cost accounting rather than representation quality earns nothing, because cost is computed from the codes and only enforced as a budget. Scores, labels and metadata written by a method are ignored.
