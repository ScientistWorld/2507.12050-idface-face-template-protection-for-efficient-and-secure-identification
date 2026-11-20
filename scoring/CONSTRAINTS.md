# Constraints

- Register a command and both experiment entries in `encoder.json` under `method/outputs/`, `baseline/outputs/` or `checkpoints/`. Every directory is discovered, including empty or malformed ones.
- Encode each unit 512-D template independently into an integer vector of dimension 1..512, absolute coordinate at most 2^20. Gallery and query dimensions must agree. The role may change the procedure; other rows, prior calls and benchmark identities may not.
- Learn representations on development data before evaluation. Keep code and learned assets in `method/` or `checkpoints/`. Hidden evaluation never trains. Do not train an identity classifier for benchmark identities.
- During encoding, the launcher permits reading installed libraries, method/baseline/checkpoint assets, scripts, audit encoder code and the visible development bank. It permits writing only the current call's output and scratch directory. Evaluation data and code, raw downloads, other calls and score files are unreadable. Linux Landlock is required and failure to establish it fails closed. Do not read evaluation answers or contact the network.
- Every draw must satisfy mean additions <=680 and packing >=5 in `face_identification`; <=124 and >=8 in `face_identification_compressed`, with 50-bit slots. The evaluator computes additions as `2*max(||q||_1-1,0)` and digit bound as `min(max||g||_1*max|q|,max||q||_1*max|g|)`. No method-written counters are trusted.
- Re-encoding random subsets must yield identical codes. No state can be persisted between calls. There is no method-path wall-clock timeout and no runtime metric.
- Do not change data, evaluation, comparison models, operating points, thresholds or budgets. Any failed draw or experiment assigns zeros to all metrics in both experiments.
