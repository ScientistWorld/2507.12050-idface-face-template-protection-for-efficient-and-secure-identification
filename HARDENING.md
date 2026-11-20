# Hardening: real face identification

The final test rewards the demonstrated improvement and penalizes the weaker encoder. Multi-level gallery quantization raises full-budget TPIR@1% from **0.904561 to 0.911104** (+0.654 percentage points, **9.4 paired standard errors**) and normalized overall rank by **0.021405 ± 0.006682 SE** (3.2 SE). The weaker sparsity variant loses **0.196865 ± 0.061158 SE** overall. All repaired attack-only submissions receive zero in every metric of both experiments. Honest reference codes with forged metadata tie only because they perform exactly the reference computation; the metadata earns nothing.

Evidence: [paired summary](redteam/hardening/review_results/summary.json), [all audit rows and failure reasons](redteam/hardening/review_results/test_all.json), and [isolated reference run](redteam/hardening/review_results/reference_scores_test.json). Job `1094e3a6-544` exited 0 after one combined, serial CPU run: reference and baselines end to end, all changed attacks and honest variants through the no-argument hidden entry point, 300 paired bootstrap resamples, and validation. All fixes were selected from the reports and paper before that job. No experiments ran between patches.

## What changed, including REVIEW.md

The review correctly rejected isotropic synthetic vectors as evidence about real face representations. The final banks contain frozen **AdaFace IR-101 / WebFace12M** embeddings from public aligned LFW, XQLFW and CPLFW captures. Development has 2,881 people / 18,932 captures; test has 2,882 different people / 19,186 captures. The partition is by person across all sources. Neither the enrollment image nor a degraded copy with the same image key is a genuine probe. Enrollment prefers LFW; probes include quality and pose variation. Extraction uses the published backbone in inference mode, with no training or seed-dependent backbone fitting.

Each split averages **16 fixed, paired draws**, each enrolling 1,200 people and retaining up to eight probes per person. Test draws contain 4,848–5,080 genuine and 6,861–7,017 impostor probes; totals are 78,782 and 111,387 probe appearances, respectively. These appearances reuse people, not independent test subjects. A secret orthogonal basis per draw preserves real cosine geometry and prevents direct public-vector lookup. The partition builder, hidden bank, seeds, labels and any raw hidden audit outcomes stay only under `eval/test/`. The evaluator never trains.

Additional changes:

- **Unreadable answers and isolated calls.** A Linux Landlock launcher confines each encoder to its own inputs/scratch, installed libraries, development bank, and permitted code/model assets. Hidden data and evaluator code, raw downloads, score files and other call directories are unreadable. Writes outside the call are denied. Restrictions survive exec and failure to establish them fails closed. This closes the previous hardening report's open hidden-file reading and persistent-state attacks. It imposes no whitelist of encoder algorithms or reference settings.
- **Complete failure rows.** Any failed draw or experiment gives all six metrics the worst value, zero, in both experiments, including experiments not reached. Missing specs, empty directories, absent experiment entries, malformed codes, forbidden reads, budget violations and failed task feasibility all follow this rule. Every method directory is discovered independently of train manifests; colliding names are retained with suffixes.
- **Evaluator-owned comparisons.** The evaluator derives similarities, strict ties, thresholds, costs and all six metrics from integer codes against its own inputs and labels. It ignores submitted labels, predictions, counters, flags and verdicts. Minimum feasibility is top-1 >=0.10 and TPIR@1% >=0.05 in every draw. Costs are fixed gates, never compensating rewards.
- **Load independence.** Removed the inherited ten-minute encoder timeout. No method-path value or success gate depends on elapsed time. Shared embeddings, inputs and random seeds are frozen. The stored reference comes from serial reproduction before audit encoders were installed, with no concurrent task. Its metrics reproduced exactly during the audit.
- **Paper arithmetic restored.** Reference encoding remains the paper's top-magnitude ternary transformation at (341,341) and (341,63). The actual Paillier check now uses a 2048-bit key and the first-ciphertext accumulator schedule, without an extra zero addition or scalar power. On eight real development enrollments and eight probes it measures exactly 124 additions, zero scalar multiplications and two decryptions per query (one packed block), with maximum plaintext/decrypted score error zero. This check is unranked.
- **Packaging and source results.** Derived banks are committed for offline runs. Download scripts fetch all public image shards and the backbone with real curl commands and SHA256 verification. The container builds from `environment/`. Differently scaled paper results remain unchanged under `_paper_reported` in `scoring/reference.json`; scored reference rows now contain final measured values. Briefing and scoring documents describe the real protocol. Historical builder notes and obsolete synthetic audit evidence are archived.

No weights changed: both experiments remain 0.5; TPIR coefficients remain 1 / 0.6 / 0.3, top-1 0.3, AUC 0.25, MRR 0.15. Both the paper's ordinary representation quality and its compressed operating point matter. Rank uses each coefficient's magnitude and metric direction, divided by that metric's population SD over the ranked cohort, then sums weighted improvements over the reference. Only official experiment `results` are ranked. Failure rows cannot outrank a feasible method through costs or missing metrics.

## Reference and scientific direction, before and after

| Reference metric | Previous hardened synthetic full / compressed | Final real-face full / compressed |
|---|---:|---:|
| TPIR@1% FPIR | 0.9694 / 0.9510 | **0.904561 / 0.865212** |
| Top-1 | 0.9755 / 0.9677 | **0.944403 / 0.926205** |
| TPIR@0.1% FPIR | 0.9665 / 0.9393 | **0.432033 / 0.423196** |
| AUC | 0.9757 / 0.9683 | **0.943201 / 0.927022** |
| MRR | 0.9774 / 0.9704 | **0.950382 / 0.935617** |

The original REDTEAM reference was 0.989 / 0.718 TPIR@1%, with full-budget top-1=1. These are different data and protocols, not a regression comparison or a target for matching paper percentages. The final reference's normalized rank improvement over itself is zero.

The paper's direction is reproduced: full-budget magnitude selection gives TPIR 0.904561 versus **0.878610** for the full-sign ablation on identical inputs. Compressed asymmetric encoding gives **0.865212** versus **0.782808** for the paper's sparse-both-sides (63,63) alternative. The equal-cost random-coordinate sign baseline gives **0.833933 / 0.292586** and ranks below reference by **1.614896**; sparse-63 ranks below by **0.410230**. Random codes fail the task and receive zeros everywhere.

Unprotected cosine is a fixed, unranked comparison at TPIR **0.919833**, so protection loses 1.53 and 5.46 percentage points here. These are not the paper's IJB-C losses (0.47 and 1.23). Real capture tails are much harder than the previous isotropic impostors: strict-FPIR TPIR now falls substantially, rather than nearly equaling TPIR@1%. We did not tune the data to match the paper's percentages.

Development/reference TPIR is **0.892244 / 0.851485**, versus test **0.904561 / 0.865212**; top-1 is **0.937228 / 0.918805** versus **0.944403 / 0.926205**. Both sides use the same task, size, budgets and difficulty protocol with independent implementations and different identities. The stricter 0.1%-FPIR metric is less stable across identity splits: **0.342412 / 0.333196** on development versus **0.432033 / 0.423196** on test. Fixed paired inputs, rather than cross-split comparisons, determine improvement.

## Honest variants and headroom

Before values below are the archived previous hardening's synthetic complete-cohort rank differences. After values use the final audit cohort. These normalized scales are cohort-dependent and are not directly comparable. The original REDTEAM alpha=beta=255 variant had inconsistent paired improvements (+0.043 / +0.021 / -0.078); it was not reliable headroom. The new evidence concerns richer representations on real faces at unchanged budgets.

| Encoder | Before rank delta | Final full / compressed TPIR@1% | Final rank delta ± paired SE | Finding |
|---|---:|---:|---:|---|
| Reference | 0 | .904561 / .865212 | 0 | Baseline |
| Multi-level gallery, unchanged queries | +.0065 | .911104 / .865212 | **+.021405 ± .006682** | Overall win, 3.2 SE; primary gain .006543 ± .000696 (9.4 SE) |
| Four-level gallery | Not previously run | .911399 / .865212 | +.014631 ± .007486 | Primary improvement; overall only 2.0 SE |
| Rounded gallery within digit budget | Not previously run | .912964 / .865212 | +.015800 ± .008608 | Primary improvement; overall only 1.8 SE |
| Alpha=277 alternative | +.0044, inconclusive hidden win | .905434 / .867689 | +.031122 ± .019498 | 1.6 SE: still inconclusive overall |
| Weaker (127,127) / (63,63) | -.331 | .883222 / .782808 | **-.196865 ± .061158** | Overall worse, 3.2 SE |

Every comparison is paired on the same people, enrollments, probes, bases and ordering. The 300 bootstrap replicates resample **identities jointly across all draws and both methods**, then recompute all metrics, including each impostor threshold. They do not count repeated images or 16 bases as independent people. Rank SD denominators are fixed from the complete audited cohort. The multi-level variant has positive overall rank in every bootstrap replicate; the weaker variant in none. These are uncertainty estimates, not new ranked metrics. Exact repeated-reference metrics were identical.

The improved encoder changes the representation, not labels or search effort: gallery rank bands receive magnitudes 3/2/1, with L1=566, query codes stay at 341 ternary entries. It uses **680 additions and five packed templates**, exactly the full reference budget, and leaves the compressed procedure unchanged. It is a valid quantizer improvement allowed by the paper's suggested precision extensions. The other encoders also stay within fixed budgets; the larger apparent alpha277 rank gain does not establish superiority beyond noise.

**Bounds:** the reference is at the bound of **none of the 12 scored quantities**. Full-budget values range from .432033 to .950382 and compressed from .423196 to .935617; all upper bounds are one. No tried honest variant reaches a scored bound. Existing full and compressed experiments now both expose real representation loss; the real-face replacement and paired 16-draw protocol were added rather than a third experiment. A better encoder demonstrably raises the overall score, so this is more than unsaturated numerical room. The simple baselines remain clearly worse.

**Brute force:** the paper searches all gallery identities too; its benefit is cheaper encrypted score computation. Enumerating raw cosine comparisons is not a valid protected representation. The private-search version of that shortcut cannot persist gallery/probe state between encoder calls, read other calls, or alter evaluator-owned matching. Returning round(4096*x) to make the evaluator do unprotected matching fails at **147,967.2 additions/query >680**, also exceeding the compressed budget. Increasing only sample size would not make an unprotected output valid. This revision enforces representation and encrypted-work budgets directly.

## Major shortcuts: before, fix, and measured after

Before numbers are from REDTEAM unless labelled previous hardening. All after failures have **six zeros in both experiments**, TPIR=0 and overall audit rank delta **-5.536582**. This includes experiments never reached, so missing values cannot escape ranking. `test_all.json` records each reason.

| Shortcut | Before: TPIR / rank delta or outcome | Fix and final measured result |
|---|---|---|
| Visible labels / constant self-labels | 1.000 / +.116116 | Test-only people and labels; encoder sees shuffled unlabeled templates. Development-only lookup and constant codes both fail; **0 / -5.536582**. The constant submission exceeds the cost budget; even feasible constant ties fail task feasibility. |
| Cached predictions | .989 / 0 (paying tie) | Fresh hidden inputs require an encoder, not a predictions artifact. No-encoder cached submission **fails, 0 / -5.536582**. |
| Forged costs / protection flags | .989 / +3.36e-10 (+.407629 on calibration scales) | Resource metadata is ignored; all costs are recomputed. Honest codes plus impossible metadata give **.904561 / .865212, delta 0**, exactly equal to the honest reference. No metadata-derived gain or computation bypass remains. |
| Unprotected artifact / exhaustive cosine | 1.000 / +.114693 | Raw-code and per-instance cost validation; call isolation removes query-to-gallery adaptation. Rounded raw floats **fail budget, 0 / -5.536582**. |
| Scale-margin | .989 / +1.538583 | Removed margin reward; cosine is scale invariant. Reference codes x1000 **fail at 681,998 additions >680, 0 / -5.536582**. |
| Impostor threshold manipulation | 1.000 / +.116105 | Genuine/impostor labels hidden, query batch mixed; evaluator derives its own impostor maxima and strict threshold. No submitted threshold or score field is consumed. Old-form cached-score submission fails as above; no separate new threshold attack was needed. |
| Shrink task / replace benchmark | 1.000 / +.116107 or +.116113 | Evaluator fixes the full real inputs, gallery, counts and labels. Shortened output **fails shape, 0 / -5.536582**. |
| Failed matcher with impossible metadata / constant truth | .003 / +5.028108; tied constant truth .003 / -8.963632 | No resource rewards; strict ties, pessimistic ranks and task gate. Zero-code matcher **fails, 0 / -5.536582**, in every metric, rather than receiving AUC/MRR credit. |
| Direct score write | Overwritten; remaining cached artifact tied | Audit planted a billion-valued forged row. No-argument test **overwrites it**, and cached artifact fails. Only evaluator-written official results count. |
| Empty train manifest / omitted experiment | No row, zero contribution (tie) | Discovery ignores train JSON. Audit empties it and still scores all **24** directories. Empty directory and missing experiment each **fail, 0 / -5.536582**. |
| Null/NaN metadata, NaN codes, empty predictions | Crash/stale score or accepted NaN | Metadata unused; malformed/non-integer/empty codes get complete failure rows. NaN and wrong-shape attacks **fail, 0 / -5.536582**, while evaluation exits successfully. |
| Read hidden evaluator/data | Previous hardening explicitly open, not measured | Landlock denies hidden bank access with PermissionError. **0 / -5.536582**. Same restriction protects code and seeds. |
| Read public raw embedding cache | Direct lookup risk identified in review | Raw downloads unreadable and hidden basis changes coordinates. Attempted cache read gets PermissionError, **0 / -5.536582**. |
| Persist gallery/probes for private nearest-neighbor lookup | Naive state caught before; selective state remained open | Writes to persistent method state denied with PermissionError. **0 / -5.536582**. No cross-call data is readable. |
| Batch-dependent encoding | Previous hardening caught naive version | Re-encoding shuffled subsets detects changed gallery codes. **0 / -5.536582**. |

An original visible-lookup attack with an honest fallback can still execute that fallback and tie, because it performs the complete honest computation on all test inputs; there are no test lookup hits. The audit's pure lookup fails. Likewise, ignoring metadata around a real reference encoder is an honest computation, not the former free resource gain. Cached predictions without executing an encoder no longer tie.

## Remaining limitations and shortcuts left to the grader

- Deliberate identity lookup using downloaded public images disguised as learned assets, network exfiltration, filesystem/sandbox exploitation, or an adversarial batch rule engineered to evade the finite subset check remain forbidden and subject to the separate shortcut grader. Landlock blocks the measured file/state routes, not all possible hostile computation or network access. No claim of a complete security sandbox is made. Ordinary per-template quantizers, learned encoders and fixed transforms remain expressible.
- Copying an honest encoder necessarily ties its output. It still runs on unseen inputs and incurs the same representation constraints; rejecting identical algorithms would not create scientific headroom. A legitimate encoder with indistinguishable utility is also a headroom question, not a loophole.
- This is real mixed-quality face identification, but **not IJB-C**, verification, multiple backbones, or million-identity encrypted timing/storage reproduction. Hidden scoring uses exact decrypted code scores and machine-independent work budgets. The real Paillier smoke check establishes arithmetic correctness at small scale, not production HE performance or end-to-end cryptographic security.
- Very strict FPIR depends strongly on a few impostor identities. Cross-split strict-FPIR scores differ and overall rank uncertainty remains larger than primary-TPIR uncertainty. Alpha277, four-level and rounded-gallery overall wins are not established at three SE; only the multi-level overall win is. Failed controls increase cohort SDs; future cohort scales will differ.
- `python validate.py` passes. Its three soft "looks detached" warnings are heuristic: the two evaluators explicitly run arbitrary encoder commands and consume returned codes, and the hidden bank builder prepares inputs. They never substitute the reference algorithm for a candidate.
- `README.md` and `manifest.json` are pre-existing `/dev/null` device mounts and cannot be replaced in the working filesystem. The README was repaired directly in the Git index so a fresh clone has current results and valid documentation links. Harness-generated manifest history is left unchanged. The missing read-only runtime `trajectory/session.json` is also outside editable packaging. These runtime limitations do not affect the committed banks or reproduction scripts.

## Final package

`scoring/scores_test.json`, `scores_train.json` and `scores.json` contain **only the isolated reference and baseline runs**, not audit variants or shortcuts. Source-paper numeric results are unchanged. The audit restores the exact official bytes in `finally` and removes temporary method directories. The final `scripts/run.sh` runs reference reproduction end to end; [review_audit.py](redteam/hardening/review_audit.py) preserves the separate audit procedure. Generated banks and aggregate evidence are committed. No additional model/evaluator/data change was made after the successful job.
