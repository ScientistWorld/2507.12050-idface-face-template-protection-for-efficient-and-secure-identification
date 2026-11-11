# Hardening audit summary

checks: {"evaluate_test_exit_code": 0, "forged_scores_overwritten": true, "methods_scored_with_empty_train_manifest": ["hv_alpha277", "hv_full_sign_512", "hv_multilevel_gallery", "hv_weaker_127", "idface", "random_codes", "sc_batch_center", "sc_cached_predictions", "sc_constant_codes", "sc_empty_codes", "sc_forged_metadata", "sc_nan_codes", "sc_scaled_codes", "sc_stateful_gallery_fold", "sc_stateful_query_lookup", "sc_unprotected_float", "sc_visible_lookup", "sc_zero_codes", "sign_random_subset"]}

| method | status full | status compressed | TPIR@1e-2 full | TPIR@1e-2 compr. | rank Δ complete | rank Δ calibration |
|---|---|---|---:|---:|---:|---:|
| hv_alpha277 | failed | failed | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| hv_full_sign_512 | failed | failed | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| hv_multilevel_gallery | failed | failed | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| hv_weaker_127 | failed | failed | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| idface | failed | failed | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| random_codes | failed | failed | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| sc_batch_center | failed | failed | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| sc_cached_predictions | failed | failed | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| sc_constant_codes | failed | failed | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| sc_empty_codes | failed | failed | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| sc_forged_metadata | failed | failed | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| sc_nan_codes | failed | failed | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| sc_scaled_codes | failed | failed | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| sc_stateful_gallery_fold | failed | failed | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| sc_stateful_query_lookup | failed | failed | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| sc_unprotected_float | failed | failed | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| sc_visible_lookup | failed | failed | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| sc_zero_codes | failed | failed | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| sign_random_subset | failed | failed | 0.0000 | 0.0000 | +0.0000 | +0.0000 |

## Failure reasons
- synthetic_identification / hv_alpha277: query encoder exited 1:   File "/usr/local/lib/python3.11/zipfile.py", line 2030, in _fpclose |     fp.close() | OSError: [Errno 28] No space left on device
- synthetic_identification / hv_full_sign_512: query encoder exited 1:   File "/usr/local/lib/python3.11/zipfile.py", line 2030, in _fpclose |     fp.close() | OSError: [Errno 28] No space left on device
- synthetic_identification / hv_multilevel_gallery: query encoder exited 1:   File "/usr/local/lib/python3.11/zipfile.py", line 2030, in _fpclose |     fp.close() | OSError: [Errno 28] No space left on device
- synthetic_identification / hv_weaker_127: query encoder exited 1:   File "/usr/local/lib/python3.11/zipfile.py", line 2030, in _fpclose |     fp.close() | OSError: [Errno 28] No space left on device
- synthetic_identification / idface: query encoder exited 1:   File "/usr/local/lib/python3.11/zipfile.py", line 2030, in _fpclose |     fp.close() | OSError: [Errno 28] No space left on device
- synthetic_identification / random_codes: query encoder exited 1:   File "/usr/local/lib/python3.11/zipfile.py", line 2030, in _fpclose |     fp.close() | OSError: [Errno 28] No space left on device
- synthetic_identification / sc_batch_center: query encoder exited 1:   File "/usr/local/lib/python3.11/zipfile.py", line 2030, in _fpclose |     fp.close() | OSError: [Errno 28] No space left on device
- synthetic_identification / sc_cached_predictions: no encoder.json: the method provides no encoder the evaluator can run
- synthetic_identification / sc_constant_codes: query encoder exited 1:   File "/usr/local/lib/python3.11/zipfile.py", line 2030, in _fpclose |     fp.close() | OSError: [Errno 28] No space left on device
- synthetic_identification / sc_empty_codes: gallery codes have shape (0, 512), expected (1000, D)
- synthetic_identification / sc_forged_metadata: query encoder exited 1:   File "/usr/local/lib/python3.11/zipfile.py", line 2030, in _fpclose |     fp.close() | OSError: [Errno 28] No space left on device
- synthetic_identification / sc_nan_codes: gallery codes must be integers, got dtype float64
- synthetic_identification / sc_scaled_codes: query encoder exited 1:   File "/usr/local/lib/python3.11/zipfile.py", line 2030, in _fpclose |     fp.close() | OSError: [Errno 28] No space left on device
- synthetic_identification / sc_stateful_gallery_fold: query encoder exited 1:   File "/usr/local/lib/python3.11/zipfile.py", line 2030, in _fpclose |     fp.close() | OSError: [Errno 28] No space left on device
- synthetic_identification / sc_stateful_query_lookup: query encoder exited 1:   File "/usr/local/lib/python3.11/zipfile.py", line 2030, in _fpclose |     fp.close() | OSError: [Errno 28] No space left on device
- synthetic_identification / sc_unprotected_float: query encoder exited 1:   File "/usr/local/lib/python3.11/zipfile.py", line 2030, in _fpclose |     fp.close() | OSError: [Errno 28] No space left on device
- synthetic_identification / sc_visible_lookup: query encoder exited 1:   File "/usr/local/lib/python3.11/zipfile.py", line 2030, in _fpclose |     fp.close() | OSError: [Errno 28] No space left on device
- synthetic_identification / sc_zero_codes: query encoder exited 1:   File "/usr/local/lib/python3.11/zipfile.py", line 2030, in _fpclose |     fp.close() | OSError: [Errno 28] No space left on device
- synthetic_identification / sign_random_subset: query encoder exited 1:   File "/usr/local/lib/python3.11/zipfile.py", line 2030, in _fpclose |     fp.close() | OSError: [Errno 28] No space left on device
- synthetic_identification_compressed / hv_alpha277: query encoder exited 1:   File "/usr/local/lib/python3.11/zipfile.py", line 2030, in _fpclose |     fp.close() | OSError: [Errno 28] No space left on device
- synthetic_identification_compressed / hv_full_sign_512: query encoder exited 1:   File "/usr/local/lib/python3.11/zipfile.py", line 2030, in _fpclose |     fp.close() | OSError: [Errno 28] No space left on device
- synthetic_identification_compressed / hv_multilevel_gallery: query encoder exited 1:   File "/usr/local/lib/python3.11/zipfile.py", line 2030, in _fpclose |     fp.close() | OSError: [Errno 28] No space left on device
- synthetic_identification_compressed / hv_weaker_127: query encoder exited 1:   File "/usr/local/lib/python3.11/zipfile.py", line 2030, in _fpclose |     fp.close() | OSError: [Errno 28] No space left on device
- synthetic_identification_compressed / idface: query encoder exited 1:   File "/usr/local/lib/python3.11/zipfile.py", line 2030, in _fpclose |     fp.close() | OSError: [Errno 28] No space left on device
- synthetic_identification_compressed / random_codes: query encoder exited 1:   File "/usr/local/lib/python3.11/zipfile.py", line 2030, in _fpclose |     fp.close() | OSError: [Errno 28] No space left on device
- synthetic_identification_compressed / sc_batch_center: query encoder exited 1:   File "/usr/local/lib/python3.11/zipfile.py", line 2030, in _fpclose |     fp.close() | OSError: [Errno 28] No space left on device
- synthetic_identification_compressed / sc_cached_predictions: no encoder.json: the method provides no encoder the evaluator can run
- synthetic_identification_compressed / sc_constant_codes: query encoder exited 1:   File "/usr/local/lib/python3.11/zipfile.py", line 2030, in _fpclose |     fp.close() | OSError: [Errno 28] No space left on device
- synthetic_identification_compressed / sc_empty_codes: gallery codes have shape (0, 512), expected (1000, D)
- synthetic_identification_compressed / sc_forged_metadata: query encoder exited 1:   File "/usr/local/lib/python3.11/zipfile.py", line 2030, in _fpclose |     fp.close() | OSError: [Errno 28] No space left on device
- synthetic_identification_compressed / sc_nan_codes: gallery codes must be integers, got dtype float64
- synthetic_identification_compressed / sc_scaled_codes: query encoder exited 1:   File "/usr/local/lib/python3.11/zipfile.py", line 2030, in _fpclose |     fp.close() | OSError: [Errno 28] No space left on device
- synthetic_identification_compressed / sc_stateful_gallery_fold: query encoder exited 1:   File "/usr/local/lib/python3.11/zipfile.py", line 2030, in _fpclose |     fp.close() | OSError: [Errno 28] No space left on device
- synthetic_identification_compressed / sc_stateful_query_lookup: query encoder exited 1:   File "/usr/local/lib/python3.11/zipfile.py", line 2030, in _fpclose |     fp.close() | OSError: [Errno 28] No space left on device
- synthetic_identification_compressed / sc_unprotected_float: query encoder exited 1:   File "/usr/local/lib/python3.11/zipfile.py", line 2030, in _fpclose |     fp.close() | OSError: [Errno 28] No space left on device
- synthetic_identification_compressed / sc_visible_lookup: query encoder exited 1:   File "/usr/local/lib/python3.11/zipfile.py", line 2030, in _fpclose |     fp.close() | OSError: [Errno 28] No space left on device
- synthetic_identification_compressed / sc_zero_codes: query encoder exited 1:   File "/usr/local/lib/python3.11/zipfile.py", line 2030, in _fpclose |     fp.close() | OSError: [Errno 28] No space left on device
- synthetic_identification_compressed / sign_random_subset: query encoder exited 1:   File "/usr/local/lib/python3.11/zipfile.py", line 2030, in _fpclose |     fp.close() | OSError: [Errno 28] No space left on device

## Seeds (rank Δ vs same-draw reference, calibration scales)
- secret: hv_alpha277=+0.0000, hv_multilevel_gallery=+0.0000, hv_weaker_127=+0.0000, idface=+0.0000, sign_random_subset=+0.0000
- 101: hv_alpha277=+0.0000, hv_multilevel_gallery=+0.0000, hv_weaker_127=+0.0000, idface=+0.0000, sign_random_subset=+0.0000
- 202: hv_alpha277=+0.0000, hv_multilevel_gallery=+0.0000, hv_weaker_127=+0.0000, idface=+0.0000, sign_random_subset=+0.0000
- 303: hv_alpha277=+0.0000, hv_multilevel_gallery=+0.0000, hv_weaker_127=+0.0000, idface=+0.0000, sign_random_subset=+0.0000
- reference TPIR@1e-2 by draw: {'secret': 0.0, '101': 0.0, '202': 0.0, '303': 0.0}
- reference rank vs secret-draw reference: {'secret': 0.0, '101': 0.0, '202': 0.0, '303': 0.0}

## Paired TPIR differences vs reference (bootstrap SE)
