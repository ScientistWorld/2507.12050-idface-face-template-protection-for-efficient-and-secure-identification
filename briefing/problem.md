# Problem

Build a protected template representation for open-set face identification. A database holds one enrollment capture per person. Each probe must either identify its enrolled person or be rejected as unenrolled. Inputs are fixed, normalized 512-dimensional face embeddings; the representation must preserve their useful identity information while fitting an encrypted computation budget.

The method supplies two per-template encoders: one for enrollment (gallery) and one for probes (query). Each returns an integer vector of dimension at most 512. Gallery codes can be stored under additive homomorphic encryption. Matching sums encrypted gallery coordinates according to the query code. After decryption the evaluator computes the cosine of the integer codes. Signed coordinates use separate same-sign and opposite-sign accumulators; multiple gallery codes occupy base-p digits of a plaintext slot.

| Experiment | Mean ciphertext additions per probe per packed block | Minimum templates per 50-bit slot |
|---|---:|---:|
| `face_identification` | 680 | 5 |
| `face_identification_compressed` | 124 | 8 |

The goal is higher identification accuracy within both budgets. The compressed experiment tests the accuracy lost when encrypted computation and storage are more constrained. Costs are constraints, so saving unused computation alone earns no reward.

Inputs come from real, fixed AdaFace IR-101 / WebFace12M embeddings of public LFW, cross-quality XQLFW and cross-pose CPLFW images. Development and hidden test contain disjoint identities. Each side averages 16 fixed draws with 1,200 enrolled identities, up to eight genuine probes per enrolled identity and up to eight impostor probes per unenrolled identity. Enrollment prefers LFW; probes mix the three sources. Another version of the enrollment image cannot be a genuine probe. The actual probe counts are evaluator-owned and recorded in each score file.

Each draw applies a dense orthogonal change of basis to all its embeddings. This preserves all pairwise cosine similarities and prevents direct public-vector lookup. Codes must be functions of an individual template and its role; they cannot depend on other rows, prior calls or benchmark identities. Encoders may be learned on the development bank before evaluation. See [evaluation.md](evaluation.md) for the interface.
