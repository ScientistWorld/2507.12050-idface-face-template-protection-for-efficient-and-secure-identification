# Experiments

Two equally weighted experiments measure open-set identification from protected integer template codes. Both use real, fixed 512-D face embeddings from LFW, XQLFW and CPLFW. Development and hidden test identities are disjoint. Each split uses 16 fixed draws, 1,200 enrolled people per draw, at most eight genuine probes per enrolled person and at most eight impostor probes per unenrolled person. Enrollment prefers LFW; genuine probes exclude the enrollment image across quality versions. A shared orthogonal basis per draw preserves face cosine geometry and blocks direct vector lookup. Counts are fixed by the evaluator and recorded in `_protocol`.

| Experiment | Weight | Maximum mean encrypted additions per probe | Minimum templates per 50-bit slot |
|---|---:|---:|---:|
| `face_identification` | 0.5 | 680 | 5 |
| `face_identification_compressed` | 0.5 | 124 | 8 |

The compressed experiment tests representation quality where tighter computation and storage lose identity information. These budgets apply per packed block and every draw; integer code dimension is at most 512. They are feasibility gates, not scored resource quantities.

Both experiments score TPIR@1% FPIR (primary, coefficient 1), TPIR@0.1% (0.6), TPIR@10% (0.3), strict top-1 (0.3), open-set score AUC (0.25) and pessimistic MRR (0.15). All are higher-is-better, bounded by [0,1], and averaged over draws. The evaluator runs encoders, derives cosine scores and costs from raw codes, and fixes labels and strict impostor-derived thresholds. A failed run gets zero for every metric in both experiments. See [../briefing/evaluation.md](../briefing/evaluation.md) for exact definitions and the interface.

The rank adds each experiment weight times the absolute metric coefficient times the improvement in its better direction over the measured reference, divided by that metric's population standard deviation over the attempts later ranked. Diagnostics, context rows, saved predictions and separately written ranks are unranked.

Official reference-only rows are `idface`, `sign_random_subset` (a simple equal-cost baseline), `sparse_63` (a lower-accuracy sparse baseline) and `random_codes` (a failed-task control). `_context` holds float-cosine matching and full-sign matching on identical inputs for scientific comparison; these ignore the encrypted budgets and are not ranked.

The source paper's results remain under `_paper_reported` in `reference.json`. Its scored experiment rows hold measured results on this scaled real-face setup, not source-paper numbers from a different protocol. [RESULTS.md](RESULTS.md) reports reproduction and limitations.
