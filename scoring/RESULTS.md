# Results

Reference runs (from `scripts/reproduce.sh`, job `0e38311d-a0a`). Scores are in `scoring/scores_test.json` (hidden test draw) and `scoring/scores_train.json` (visible development split). Every number is computed by the evaluator from the codes returned by each method's encoder.

## Hidden test split

| Row | Experiment | TPIR@1e-2 | TPIR@1e-3 | TPIR@1e-1 | Top-1 | AUC | MRR |
|---|---|---:|---:|---:|---:|---:|---:|
| `idface` (341, 341) | `synthetic_identification` | 0.9694 | 0.9665 | 0.9727 | 0.9755 | 0.9757 | 0.9774 |
| `sign_random_subset` | `synthetic_identification` | 0.9084 | 0.8680 | 0.9351 | 0.9486 | 0.9516 | 0.9556 |
| `random_codes` | `synthetic_identification` | 0.0000 | 0.0000 | 0.0000 | 0.0002 | 0.0003 | 0.0011 |
| `idface` (341, 63) | `synthetic_identification_compressed` | 0.9510 | 0.9393 | 0.9622 | 0.9677 | 0.9683 | 0.9704 |
| `sign_random_subset` | `synthetic_identification_compressed` | 0.0868 | 0.0321 | 0.1731 | 0.2812 | 0.3191 | 0.3570 |
| `random_codes` | `synthetic_identification_compressed` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0007 |
| unprotected float cosine (context) | same split | 0.9764 | 0.9734 | 0.9790 | 0.9813 | 0.9817 | 0.9830 |

Encrypted cost computed from the reference codes: 680 ciphertext additions per probe, digit bound 341, 5 templates per 50-bit slot at (341, 341); 124 additions, digit bound 63, 8 templates per slot at (341, 63); no multiplications or rotations, 2 decryptions per packed block, matching the paper's Table 1.

Development split (visible): `idface` 0.9720 / 0.9530 TPIR@1e-2 (full / compressed), unprotected context 0.9785, so train and test are of comparable difficulty.

## Paper claims, in the paper's direction

- Protected codes nearly preserve identification: (341, 341) loses 0.70 TPIR@1e-2 points against unprotected cosine (paper, IJB-C with AdaFace: 0.47).
- Smaller query sparsity trades accuracy for cost: (341, 63) loses 2.5 points (paper: 1.2) for 5.5× fewer additions and 1.6× denser packing.
- Magnitude-based selection matters: signs of fixed random coordinates at the same cost lose 6.1 points at (341, 341) and collapse at (341, 63); with full-sign enrolled codes, (512, 63) reaches 0.907 against 0.951 for (341, 63), and (512, 512) does not fit the 680-addition budget.
- Seed noise is small: the reference's TPIR@1e-2 over four independent test draws is 0.9694–0.9700 (full) and 0.9494–0.9513 (compressed).

Deviation: very sparse codes on both sides are penalized more here than in the paper ((127, 127)/(63, 63) rows in `redteam/hardening/results/summary.md`: (63, 63) at the compressed budget loses 15 points; the paper's (63, 63) loses 3.6 on IJB-C).

A real-Paillier smoke run (`method/smoke/paillier_small`, 64 identities, 256-bit key) decrypts to exactly the packed plaintext scores (max error 0).
