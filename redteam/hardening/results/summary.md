# Hardening audit summary

checks: {"evaluate_test_exit_code": 0, "forged_scores_overwritten": true, "methods_scored_with_empty_train_manifest": ["hv_alpha277", "hv_full_sign_512", "hv_multilevel_gallery", "hv_weaker_127", "idface", "random_codes", "sc_batch_center", "sc_cached_predictions", "sc_constant_codes", "sc_empty_codes", "sc_forged_metadata", "sc_nan_codes", "sc_scaled_codes", "sc_stateful_gallery_fold", "sc_stateful_query_lookup", "sc_unprotected_float", "sc_visible_lookup", "sc_zero_codes", "sign_random_subset"]}

| method | status full | status compressed | TPIR@1e-2 full | TPIR@1e-2 compr. | rank Δ complete | rank Δ calibration |
|---|---|---|---:|---:|---:|---:|
| hv_alpha277 | ok | ok | 0.9696 | 0.9537 | +0.0044 | +0.0048 |
| hv_full_sign_512 | failed | ok | 0.0000 | 0.9071 | -2.8318 | -3.6382 |
| hv_multilevel_gallery | ok | ok | 0.9718 | 0.9510 | +0.0065 | +0.0085 |
| hv_weaker_127 | ok | ok | 0.9623 | 0.8239 | -0.3309 | -0.3592 |
| idface | ok | ok | 0.9694 | 0.9510 | +0.0000 | +0.0000 |
| random_codes | ok | ok | 0.0000 | 0.0000 | -5.5112 | -6.5629 |
| sc_batch_center | failed | failed | 0.0000 | 0.0000 | -5.5116 | -6.5635 |
| sc_cached_predictions | failed | failed | 0.0000 | 0.0000 | -5.5116 | -6.5635 |
| sc_constant_codes | ok | ok | 0.0000 | 0.0000 | -5.2314 | -6.2296 |
| sc_empty_codes | failed | failed | 0.0000 | 0.0000 | -5.5116 | -6.5635 |
| sc_forged_metadata | ok | ok | 0.9694 | 0.9510 | +0.0000 | +0.0000 |
| sc_nan_codes | failed | failed | 0.0000 | 0.0000 | -5.5116 | -6.5635 |
| sc_scaled_codes | failed | failed | 0.0000 | 0.0000 | -5.5116 | -6.5635 |
| sc_stateful_gallery_fold | failed | failed | 0.0000 | 0.0000 | -5.5116 | -6.5635 |
| sc_stateful_query_lookup | failed | failed | 0.0000 | 0.0000 | -5.5116 | -6.5635 |
| sc_unprotected_float | failed | failed | 0.0000 | 0.0000 | -5.5116 | -6.5635 |
| sc_visible_lookup | ok | ok | 0.9694 | 0.9510 | +0.0000 | +0.0000 |
| sc_zero_codes | ok | ok | 0.0000 | 0.0000 | -5.2314 | -6.2296 |
| sign_random_subset | ok | ok | 0.9084 | 0.0868 | -2.5260 | -2.7744 |

## Failure reasons
- synthetic_identification / hv_full_sign_512: budget exceeded: 1022.0 ciphertext additions per query > 680
- synthetic_identification / sc_batch_center: gallery codes changed between calls (depend on batch or on previously seen probes)
- synthetic_identification / sc_cached_predictions: no encoder.json: the method provides no encoder the evaluator can run
- synthetic_identification / sc_empty_codes: gallery codes have shape (0, 512), expected (1000, D)
- synthetic_identification / sc_nan_codes: gallery codes must be integers, got dtype float64
- synthetic_identification / sc_scaled_codes: budget exceeded: 681998.0 ciphertext additions per query > 680
- synthetic_identification / sc_stateful_gallery_fold: gallery codes changed between calls (depend on batch or on previously seen probes)
- synthetic_identification / sc_stateful_query_lookup: query codes changed between calls (depend on batch or on previously seen gallery)
- synthetic_identification / sc_unprotected_float: budget exceeded: 147966.5 ciphertext additions per query > 680
- synthetic_identification_compressed / sc_batch_center: gallery codes changed between calls (depend on batch or on previously seen probes)
- synthetic_identification_compressed / sc_cached_predictions: no encoder.json: the method provides no encoder the evaluator can run
- synthetic_identification_compressed / sc_empty_codes: gallery codes have shape (0, 512), expected (1000, D)
- synthetic_identification_compressed / sc_nan_codes: gallery codes must be integers, got dtype float64
- synthetic_identification_compressed / sc_scaled_codes: budget exceeded: 125998.0 ciphertext additions per query > 124
- synthetic_identification_compressed / sc_stateful_gallery_fold: gallery codes changed between calls (depend on batch or on previously seen probes)
- synthetic_identification_compressed / sc_stateful_query_lookup: query codes changed between calls (depend on batch or on previously seen gallery)
- synthetic_identification_compressed / sc_unprotected_float: budget exceeded: 147966.5 ciphertext additions per query > 124

## Seeds (rank Δ vs same-draw reference, calibration scales)
- secret: hv_alpha277=+0.0048, hv_multilevel_gallery=+0.0085, hv_weaker_127=-0.3592, idface=+0.0000, sign_random_subset=-2.7744
- 101: hv_alpha277=+0.0160, hv_multilevel_gallery=+0.0101, hv_weaker_127=-0.2946, idface=+0.0000, sign_random_subset=-2.7731
- 202: hv_alpha277=+0.0167, hv_multilevel_gallery=+0.0110, hv_weaker_127=-0.3457, idface=+0.0000, sign_random_subset=-2.7516
- 303: hv_alpha277=+0.0015, hv_multilevel_gallery=+0.0101, hv_weaker_127=-0.3106, idface=+0.0000, sign_random_subset=-2.7699
- reference TPIR@1e-2 by draw: {'secret': 0.9694, '101': 0.9696, '202': 0.97, '303': 0.9695}
- reference rank vs secret-draw reference: {'secret': 0.0, '101': -0.006114796986918033, '202': -0.0061447042856246584, '303': -0.0050617676959809794}

## Paired TPIR differences vs reference (bootstrap SE)
- synthetic_identification:hv_multilevel_gallery:tpir@0.01: secret +0.0024±0.0006, 101 +0.0033±0.0006, 202 +0.0036±0.0006, 303 +0.0025±0.0006
- synthetic_identification:hv_multilevel_gallery:tpir@0.001: secret +0.0027±0.0007, 101 +0.0019±0.0005, 202 +0.0037±0.0007, 303 +0.0039±0.0008
- synthetic_identification:hv_alpha277:tpir@0.01: secret +0.0002±0.0007, 101 +0.0008±0.0006, 202 +0.0010±0.0007, 303 +0.0004±0.0006
- synthetic_identification:hv_alpha277:tpir@0.001: secret -0.0003±0.0006, 101 +0.0001±0.0007, 202 +0.0002±0.0008, 303 +0.0009±0.0009
- synthetic_identification:hv_weaker_127:tpir@0.01: secret -0.0071±0.0012, 101 -0.0068±0.0014, 202 -0.0070±0.0010, 303 -0.0083±0.0013
- synthetic_identification:hv_weaker_127:tpir@0.001: secret -0.0111±0.0012, 101 -0.0141±0.0017, 202 -0.0090±0.0023, 303 -0.0091±0.0021
- synthetic_identification:sign_random_subset:tpir@0.01: secret -0.0610±0.0023, 101 -0.0577±0.0024, 202 -0.0610±0.0024, 303 -0.0645±0.0025
- synthetic_identification:sign_random_subset:tpir@0.001: secret -0.0985±0.0058, 101 -0.1125±0.0073, 202 -0.0982±0.0053, 303 -0.1024±0.0079
- synthetic_identification_compressed:hv_multilevel_gallery:tpir@0.01: secret +0.0000±0.0000, 101 +0.0000±0.0000, 202 +0.0000±0.0000, 303 +0.0000±0.0000
- synthetic_identification_compressed:hv_multilevel_gallery:tpir@0.001: secret +0.0000±0.0000, 101 +0.0000±0.0000, 202 +0.0000±0.0000, 303 +0.0000±0.0000
- synthetic_identification_compressed:hv_alpha277:tpir@0.01: secret +0.0027±0.0010, 101 +0.0032±0.0009, 202 +0.0036±0.0009, 303 +0.0037±0.0011
- synthetic_identification_compressed:hv_alpha277:tpir@0.001: secret +0.0015±0.0042, 101 +0.0100±0.0049, 202 +0.0118±0.0056, 303 -0.0068±0.0066
- synthetic_identification_compressed:hv_weaker_127:tpir@0.01: secret -0.1271±0.0180, 101 -0.0830±0.0205, 202 -0.1286±0.0181, 303 -0.0874±0.0086
- synthetic_identification_compressed:hv_weaker_127:tpir@0.001: secret -0.1648±0.0083, 101 -0.1545±0.0249, 202 -0.1555±0.0062, 303 -0.1665±0.0069
- synthetic_identification_compressed:sign_random_subset:tpir@0.01: secret -0.8642±0.0034, 101 -0.8642±0.0031, 202 -0.8679±0.0035, 303 -0.8665±0.0034
- synthetic_identification_compressed:sign_random_subset:tpir@0.001: secret -0.9072±0.0105, 101 -0.9007±0.0101, 202 -0.8770±0.0122, 303 -0.8868±0.0066
