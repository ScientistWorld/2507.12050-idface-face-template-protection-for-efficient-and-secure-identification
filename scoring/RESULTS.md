# Final real-face results

The final serial reproduction completed successfully in job `1094e3a6-544` on
2026-11-20. The official score files contain only the reference and three
baselines from that isolated run. Audit methods and shortcuts are recorded
separately in [../HARDENING.md](../HARDENING.md). All values below are fractions,
not percentages, and are means over 16 fixed draws.

## Reference on development and hidden test

| Budget | Metric | Development | Hidden test |
|---|---|---:|---:|
| Full | TPIR at 1% FPIR | 0.892244 | 0.904561 |
| Full | TPIR at 0.1% FPIR | 0.342412 | 0.432033 |
| Full | TPIR at 10% FPIR | 0.922381 | 0.930225 |
| Full | Top-1 | 0.937228 | 0.944403 |
| Full | Open-set AUC | 0.936134 | 0.943201 |
| Full | MRR | 0.944003 | 0.950382 |
| Compressed | TPIR at 1% FPIR | 0.851485 | 0.865212 |
| Compressed | TPIR at 0.1% FPIR | 0.333196 | 0.423196 |
| Compressed | TPIR at 10% FPIR | 0.895114 | 0.903662 |
| Compressed | Top-1 | 0.918805 | 0.926205 |
| Compressed | Open-set AUC | 0.919266 | 0.927022 |
| Compressed | MRR | 0.928502 | 0.935617 |

Full and compressed reference costs are exactly 680 / 124 additions per probe,
with 5 / 8 templates per 50-bit slot, in every draw. Costs are feasibility gates,
not scored rewards. No elapsed-time metric or method-path timeout is used.
The unchanged reference produced exactly the same metrics during the later
audit. The shared backbone is frozen, and each method sees identical paired
inputs, bases and orders.

Development has 2,881 identities / 18,932 captures, and test has 2,882 disjoint
identities / 19,186 captures, from LFW, XQLFW and CPLFW. Both use 1,200 enrolled
identities per draw and up to eight probes per person. Test draws have
4,848–5,080 genuine and 6,861–7,017 impostor probes. Repeated appearances across
draws are not independent people. Exact counts are in each score file's
`_protocol`; bank hashes are confined to `eval/test/data_provenance.json`.

The ordinary operating point has a 1.23 percentage-point development/test TPIR
difference; the compressed point has a 1.37-point difference. Strict 0.1%-FPIR
TPIR varies more across the identity splits because a few hard impostor people
control the threshold. Improvement is assessed on paired hidden inputs, not by
comparing development and test percentages.

## Baselines and scientific direction

| Method | Full TPIR@1% | Compressed TPIR@1% | Full top-1 | Compressed top-1 |
|---|---:|---:|---:|---:|
| `idface` | 0.904561 | 0.865212 | 0.944403 | 0.926205 |
| `sign_random_subset` | 0.833933 | 0.292586 | 0.908699 | 0.511376 |
| `sparse_63` | 0.782808 | 0.782808 | 0.883722 | 0.883722 |
| `random_codes` | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

Random codes fail task feasibility and receive zero in all metrics of both
experiments. The simple equal-cost baseline and sparse-both-sides baseline
remain below the reference on the primary metric and overall rank.

Unranked, evaluator-owned comparisons on identical inputs give TPIR@1% of
**0.919833** for unprotected float cosine and **0.878610** for full-sign codes.
The reference improves over the full-sign ablation by 2.60 percentage points;
compressed asymmetric encoding improves over sparse-both-sides by 8.24 points.
These reproduce the paper's qualitative magnitude-selection and asymmetric
representation advantages. The loss relative to unprotected cosine is 1.53
points at the full budget and 5.46 points compressed.

This protocol uses the paper's publicly released AdaFace IR-101 / WebFace12M
backbone on real mixed-quality/pose captures, but is not the paper's IJB-C
protocol. The paper's percentages and runtime/storage values remain unchanged
under `_paper_reported` in `reference.json`; they are not targets for these
scaled scored experiments. Data and operating points were not chosen to fit
paper percentages.

## Paired headroom check

Multi-level gallery quantization at the unchanged full budget raises TPIR to
**0.911104**, a difference of **0.006543 ± 0.000696 SE** (9.4 SE), and raises
complete-cohort normalized overall rank by **0.021405 ± 0.006682 SE** (3.2 SE).
Its compressed procedure stays at the reference. A weaker sparsity variant
scores **0.883222 / 0.782808** TPIR and loses **0.196865 ± 0.061158 SE** overall.
Uncertainty comes from 300 paired identity-cluster bootstrap resamples shared
across all 16 draws, with impostor thresholds recomputed in each resample.
The reference and all tried honest variants are below every scored upper bound.

Four-level and rounded-gallery alternatives improve primary TPIR further, but
their overall gains are only 2.0 and 1.8 SE. Alpha277's overall gain is also
inconclusive (1.6 SE). These are not counted as proven overall improvements.
Rank scales depend on the attempts being ranked; the paired overall figures
use the complete audited cohort. The [audit summary](../redteam/hardening/review_results/summary.json)
is evidence, not an additional ranked score.

## Scope and verification

The real Paillier arithmetic check uses a 2048-bit key, eight enrollments and
eight probes, and reports zero plaintext/decrypted score error. It measures
124 homomorphic additions, zero scalar multiplications and two decryptions per
probe over one packed block. It is not a scored experiment. Hidden evaluation
uses exact decrypted-code scores and fixed encrypted-work gates; it does not
retrain or reproduce million-identity HE timings, verification, or cryptographic
security claims.

The no-argument hidden evaluator scored all 24 audit directories despite an
empty train manifest, overwrote a forged score, and gave every failed submission
zeros in both experiments. Official score files were restored byte-for-byte
from isolated reproduction. `python validate.py` passed, with only three soft
heuristic warnings about dynamic encoder invocation / hidden input construction.
The final `scripts/run.sh` reproduces reference and baselines end to end.
