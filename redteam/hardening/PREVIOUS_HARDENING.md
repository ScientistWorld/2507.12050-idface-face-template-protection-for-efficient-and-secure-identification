# Hardening report (iteration 11)

**Verdict.** Better results now score higher and worse ones lower, by more than the test's noise on paired comparisons. Every major shortcut in `REDTEAM.md` now either fails (worst value on every metric) or ties the reference without gain. The test has headroom: the reference is at the bound of none of its 12 scored metrics, and a better variant at the same encrypted cost beats it on every test draw. One shortcut remains open: an encoder deliberately reading the hidden evaluator at test time (see "Left open").

All "after" numbers come from job `0e38311d-a0a`, which ran `scripts/reproduce.sh` and then `redteam/hardening/audit.py`; the job ran the no-argument hidden test with every case installed as a method directory. Raw files are in `redteam/hardening/results/` (`summary.md`, `summary.json`, `rank_bootstrap.json`, per-run score files). "Before" numbers are the red team's (`REDTEAM.md`, `redteam/summary.json`).

Rank deltas use the gym rule: Σ over experiments of weight × Σ over metrics of |coefficient| × direction × (row − reference) / SD. "Complete" scales are the SDs over all 19 rows of the hidden-draw audit run, "calibration" scales the SDs over the honest rows only. Absolute rank values depend on the cohort's spread. The comparisons below are paired: the same probes, gallery and impostors for every method.

## What was wrong and what changed

| Problem in `REDTEAM.md` | Fix |
|---|---|
| Labels, gallery identities, query counts, scores, costs and the protection flag all came from the method's artifact | A method is now a per-template **encoder** (`encoder.json`). The evaluator runs it on unlabeled templates, gallery and probes in separate calls with genuine and impostor probes shuffled together, and computes every score (cosine of the returned integer codes, i.e. the decrypted additive-HE inner product) and every metric from its own labels. Method-written scores, labels and metadata are never read. |
| Test answers visible (`data/synthetic_embeddings.npz` held all test labels; the test was the odd rows of the same file) | The hidden test benchmark is generated in memory by `eval/test/evaluate.py` from a seed that exists only there. It is a fresh draw of the same distribution, so its templates, identities and labels are never on disk. The visible file is now a development split only. |
| Resource counts and protection were self-reported; forged counts strictly improved the rank; a failing matcher outranked the reference through impossible metadata | Cost is computed from the codes: ciphertext additions = 2 × (‖q‖₁ − 1), and templates per 50-bit slot = largest m with (B+1)^m ≤ 2^50, where B = min(max‖g‖₁·max\|q\|, max‖q‖₁·max\|g\|) is the decoded-digit bound. Cost is enforced as a **fixed budget per experiment**, taken from the paper's two operating points, rather than scored, so lowering cost earns nothing by itself and a method that fails the task cannot buy rank with resources. Integer codes on an additive-HE database are protected by construction, so the self-reported protection flag is gone. |
| Score scale (margin) was rewarded | The margin metric was removed. Scores are cosines of codes, so scale is irrelevant, and scaled codes blow the cost budget. |
| Ties: constant rankings got MRR = 1; constant impostors gave realized FPIR 1 | Ties never count as correct (strict top-1, pessimistic rank). Thresholds accept on `>` against the k-th largest impostor score, so the realized FPIR is at most the nominal FPIR. |
| Failed or malformed runs crashed the test (stale score file) or produced empty rows | Every failure mode (no encoder, crash, timeout, NaN/float/wrong-shape/oversized codes, codes that change between calls, budget exceeded) is a failed run with value 0 on all six metrics of that experiment. The test itself never aborts on a method error. |
| `evaluate_test.sh` scored only the methods listed in the mutable train manifest | The test discovers every method directory under `method/outputs`, `baseline/outputs` and `checkpoints` on its own. Train scores are never read. |
| Brute-force unprotected cosine solved the test and outranked the reference | Full-precision codes need ~148k additions per probe and cannot pack 5 per slot, so they fail both budgets. |
| Synthetic data exaggerated the β trade-off 35× (27.1 points vs 0.76 at (341,63)) and the main reference was near saturation (TPIR .989, top-1 1.0) | The data generator is redesigned (details below). Gallery 10k identities, 10k genuine and 20k impostor probes per split, against 2k / 1k / 1k before. |
| Paillier smoke row reported per-block algorithmic counts as its actual counts | It is no longer a scored row. It is a method-side correctness check (`method/smoke/paillier_small`) that reports its measured counts (1,008 additions and 16 decryptions per query over 8 blocks) next to the per-block algorithmic counts. |

New attack surface created by running the method at test time, and how it is handled: each experiment calls the encoder four times: (1) a random 10% of the gallery before any probe has been seen, (2) all probes, (3) the whole gallery, (4) a random 10% of the probes. Codes from (1) must equal the same rows of (3), and codes from (4) the same rows of (2). This catches encoders that use other rows of the batch, stash the gallery to match probes in the clear, or stash probes to fold them into enrolled templates. Encoder I/O is staged on the workspace filesystem, each call has a 10-minute limit, and `TMPDIR` is fresh per call.

### Data

`data/generate_synthetic.py` (visible) and the copy in `eval/test/` draw identity centers uniformly on S^511. Each sample is normalize(ρ·center + √(1−ρ²)·u), u ⟂ center, with a per-sample quality ρ:
- enrolled templates ~ U(0.75, 0.95);
- probes: 95% usable, ~ U(0.5, 0.9); 5% degraded, ~ U(0.05, 0.5).

The old data had every probe at the same low quality, so a small loss of SNR moved the whole genuine distribution across the threshold. The mixed-quality probe set (as in IJB-C's mixed media) gives a broad genuine-score distribution, so representation loss shows up the way the paper reports it.

Before choosing synthetic data I checked public real 512-D face embeddings (FaceNet on LFW, `lajota13/lfw_facenet_embeddings`). Their coordinates are Gaussian-like: the top-63 coordinates hold 0.487 of the energy, against 0.49 for a Gaussian, and per-coordinate variance spans only 1.6×. That supports the isotropic model. That embedding model is too weak to be a benchmark (plain TPIR@1e-2 of 0.31 in an LFW open-set protocol, with a noisy, non-monotone ordering of (α, β) settings), and public real embeddings would also expose test labels, so they are not used.

The data regime was chosen so the *unprotected* context lands in the paper's high-accuracy regime (0.976 here vs 0.964 for the paper's plain model); the protected rows were not tuned. Resulting gaps to unprotected cosine at TPIR@1e-2, test draw:

| Setting | Here | Paper (IJB-C) |
|---|---:|---:|
| (341, 341) | −0.70 | −0.47 |
| (127, 127) | −1.41 | −1.10 |
| (341, 63) | −2.54 | −1.23 |
| (63, 63) | −15.3 | −3.55 |

(512, 512) does not fit the 680-addition budget. On the development prototype it lost 1.7 points against 1.3 in the paper, with (341, 341) ahead of (512, 512) as the paper finds. At the compressed budget, full-sign enrolled codes (512, 63) score 0.907 against 0.951 for (341, 63).

### Experiments and weights

`synthetic_identification` (≤ 680 additions, ≥ 5 templates/slot: the paper's (341,341) cost) and `synthetic_identification_compressed` (≤ 124, ≥ 8: the paper's (341,63) cost) have weight 0.5 each. The paper's accuracy table centres on (341,341) and its efficiency headline (126 ms per 1M identities, ~2× plain) on (341,63), so neither dominates.

Metric coefficients are identical in both experiments:

| Metric | Coefficient |
|---|---:|
| TPIR@1e-2 (primary, the paper's main identification metric) | 1.0 |
| TPIR@1e-3 (paper also reports it) | 0.6 |
| TPIR@1e-1 | 0.3 |
| Top-1 | 0.3 |
| Open-set AUC | 0.25 |
| MRR | 0.15 |

The paper's own Table 2/3 numbers are kept unchanged in `scoring/reference.json` under `_paper_reported`. The `idface` / `plain` rows of each scored experiment carry the paper's IJB-C TPIR for orientation only. The packing capacity was restored to the paper's floor(n / log₂ p) (base-p packing), which gives the same packs (5 / 7 / 8) at the paper's operating points.

## Do better results score higher?

**Before** (`REDTEAM.md`): the best honest change against the main reference, (255,255), gained +.043 / −.086 / −.146 rank over three seeds, i.e. no reliable improvement, within the reference's own .107 seed range. Only a change between two compressed settings (β 63 → 127) was detectable (+1.70 / +1.72 / +1.53).

**After**, rank delta against the same-draw reference (calibration scales, paired bootstrap SE over probes, `rank_bootstrap.json`):

| Variant (same encrypted cost unless noted) | Hidden draw | Draw 101 | Draw 202 | Draw 303 | Reading |
|---|---:|---:|---:|---:|---|
| `hv_multilevel_gallery`: enrolled codes with 3 magnitude levels on the top-341 support, probes T₃₄₁; same 680 additions, digit bound 568 → still 5/slot (compressed: = reference) | **+.0085 ± .0013** | +.0101 ± .0012 | +.0110 ± .0014 | +.0101 ± .0013 | **Better, 6–8 SE on every draw**; TPIR@1e-2 +0.24 to +0.36 points (±0.06) |
| `hv_alpha277`: (277,277) / (277,63) | +.0048 ± .0037 | +.0160 ± .0041 | +.0167 ± .0047 | +.0015 ± .0051 | Honest alternative, not reliably different on the hidden draw. Compressed TPIR@1e-2 +0.27 to +0.37 points (~3 SE) on every draw |
| `hv_weaker_127`: (127,127) / (63,63) | −.359 ± .024 | −.295 ± .034 | −.346 ± .023 | −.311 ± .014 | **Worse, far beyond noise** |
| `hv_full_sign_512`: (512,512) / (512,63), the paper's no-magnitude-selection ablation | full: fails budget (1,022 additions) | | | | compressed: .907 vs .951 TPIR@1e-2 |
| `sign_random_subset` baseline | −2.774 | −2.773 | −2.752 | −2.770 | Clearly below |

Hidden-draw values on the complete scales: multi-level gallery +.0065, α=277 +.0044, weaker −.331, sign baseline −2.526, random codes −5.511.

Seed noise (unpaired): the reference's TPIR@1e-2 over the four draws is 0.9694 / 0.9696 / 0.9700 / 0.9695 (full) and 0.9510 / 0.9510 / 0.9513 / 0.9494 (compressed). Its rank relative to the hidden-draw reference spans 0 to −.0061. The paper's effect (magnitude selection vs random coordinates: −6.1 TPIR points full, −86 compressed; (341,341) vs (127,127)/(63,63)) is hundreds of times this. The multi-level gain is larger than the unpaired seed spread and 6.5 SE on the paired comparison, which is how the hidden test compares methods: every method sees the same fixed draw.

Train/test comparability: the reference scores .972 / .953 on the development split against .969 / .951 on test, with the unprotected context at .979 against .976.

## Shortcuts: before and after

| Shortcut (REDTEAM.md) | Before: TPIR / rank Δ | After (new-interface form) | After: result |
|---|---|---|---|
| visible_labels | 1.000 / **+.116** | `sc_visible_lookup`: look up each template in the visible file, emit identity-revealing 2-hot codes and zero codes for impostors, honest codes otherwise | Test: no template matches; **ties the reference exactly (Δ 0)**. Train: 1.000 everywhere, an obvious train/test gap. Train is never ranked. |
| constant_self_labels | 1.000 / **+.116** | `sc_constant_codes` | TPIR 0; Δ −5.23 |
| cached_predictions | .989 / 0 (tie) | `sc_cached_predictions`: old-style `predictions.npz` + metadata, no encoder | **failed** (no encoder.json); Δ −5.51 |
| forged_costs | .989 / +3e−10 (+.41 calib.) | `sc_forged_metadata`: honest encoder + metadata claiming 0 additions and pack 10¹² | Metadata ignored; ties the reference (Δ 0, no gain) |
| unprotected_artifact, bruteforce_cosine | 1.000 / **+.115** | `sc_unprotected_float`: round(4096·x) codes | **failed**: 147,967 additions > 680 / 124; Δ −5.51 |
| scale_margin | .989 / **+1.54** | `sc_scaled_codes`: honest codes × 1000 | **failed**: 681,998 additions > 680; Δ −5.51 (margin metric removed; cosine is scale-free) |
| impostor_threshold | 1.000 / **+.116** | not expressible: probes arrive unlabeled and mixed, and the evaluator computes impostor scores | closed by design |
| shrink_task, replace_benchmark | 1.000 / **+.116** | `sc_empty_codes`: return fewer rows; the evaluator owns the benchmark | **failed** (shape); Δ −5.51 |
| failed_task_impossible_metadata | .003 / **+5.03** | `sc_zero_codes` (zero cost, no information); `sc_nan_codes` | zero codes: TPIR 0, Δ −5.23 (cost is not scored, so no credit); NaN codes: **failed** (dtype); Δ −5.51 |
| constant_truth | .003 / −8.96 | `sc_zero_codes` | TPIR 0, MRR 0.0001 (ties pessimistic) |
| direct_scores | test overwrote it | audit wrote a fake `sc_direct_write` row into `scores_test.json` before the test | overwritten (`forged_scores_overwritten: true`) |
| empty_manifest | tie (no row) | audit emptied `scores_train.json` before the test | test still scored all 19 method directories |
| null/nan metadata, empty_predictions | test crashed / NaN accepted | metadata unused; malformed codes → failed row | test exit 0; failed rows get 0 |
| *new:* stateful query-side lookup | — | `sc_stateful_query_lookup`: gallery calls stash templates, probe calls copy the nearest stashed template's code | **failed** (query codes changed between calls) |
| *new:* stateful gallery folding | — | `sc_stateful_gallery_fold`: probe calls stash probes, gallery calls fold nearby probes into enrolled templates | **failed** (gallery codes changed between calls) |
| *new:* batch-dependent encoding | — | `sc_batch_center`: subtract the batch mean | **failed** (codes changed between calls) |

Reference score: before, TPIR@1e-2 .989 (main) and .718 (compressed), top-1 1.000 and .944, on the old 1k-probe test half. After, .9694 and .9510, top-1 .9755 and .9677, on the new hidden draw. The two are not directly comparable: the benchmark, test size and protocol all changed.

## Shortcuts left open

1. **Reading the hidden evaluator at test time.** The encoder runs inside the test container, so a method could open `eval/test/evaluate.py`, recover the seed and generator, regenerate the benchmark with labels, and emit identity-revealing codes. No honest method reads `eval/`. It is forbidden in `scoring/CONSTRAINTS.md`, and the shortcut grader can see it in the code. Closing it would need sandboxing the encoder process, which is out of scope. Not run.
2. **A stateful encoder that defeats the consistency check selectively.** It would remember which rows it saw in the first 10% gallery call and leak information only into the other rows. The call-order check catches naive stashing (shown above), not this. It needs deliberate state files, which are forbidden in `CONSTRAINTS.md` and visible to the grader. Not run.
3. **Copying the reference encoder.** This ties the reference: no gain, no loss. It is inherent to improve mode and not a scoring defect.
4. **Lookup in the visible development file.** This ties on test with no gain. It scores 1.0 on train, which is not ranked.

## Headroom

- **Bounds:** the reference sits at the bound of none of the 12 scored metrics: TPIR .9665–.9727 (full) and .9393–.9622 (compressed), top-1 .9755 / .9677, AUC .9757 / .9683, MRR .9774 / .9704. Unprotected float cosine on the same draw reaches .9764 TPIR@1e-2, 0.7 points above the reference at the full budget and 2.5 at the compressed one.
- **Better variants exist:** a simple variant at identical cost beats the reference in the full experiment on every draw (above) without reaching the bound: it closes 0.24 of the 0.70-point gap. At the compressed budget, α=277 gains about 0.3 TPIR points (~3 SE).
- **Baselines and brute force:** the simple baseline is far below, and brute-force unprotected matching is infeasible under the budgets.
- No extra experiment was needed. The compressed experiment is where the paper's method falls short most (both in the paper and here) and carries half the weight.

## Not fixed / limitations, stated plainly

- The benchmark is synthetic: no face images, no AdaFace backbone, no IJB-C. Very sparse codes on both sides lose much more here than in the paper: (63,63) loses 15 points against 3.6. Strict-FPIR TPIR is close to the 1e-2 value (.9665 vs .9694), because isotropic impostors have a thin tail; in IJB-C, TPIR@1e-3 is 11 points below TPIR@1e-2.
- Encrypted search is scored through its exact decrypted result and machine-independent operation counts. No CKKS/Paillier timing at 1M identities is reproduced. The Paillier smoke check uses a 256-bit key and 64 identities.
- Genuine improvements move the rank by about .01 on the audit cohort's scales, because random codes and failures dominate those SDs. Against a cohort of attempts close to the reference, the same gains are larger relative to the spread; the paired SE scales the same way.
- `validate.py` passes. It prints one soft heuristic warning per evaluator ("looks detached"), because eval runs encoders named in `encoder.json` rather than reading prediction files.
- The iteration-10 cases under `redteam/shortcut_*`, `variant_*` and `reference_*` target the retired artifact interface and are kept only as the "before" record. `redteam/hardening/` holds the current audit.
- `README.md` and `manifest.json` are device mounts in this runtime and were not touched.
