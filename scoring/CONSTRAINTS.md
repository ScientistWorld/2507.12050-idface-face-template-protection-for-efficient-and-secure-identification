# Constraints

- Use the same generated benchmark from `data/generate_synthetic.py`.
- Keep embedding dimension fixed at 512.
- Do not train a classifier or surrogate model to map queries to identities.
- Evaluation must consume prediction artifacts written by `method/` or `baseline/`.
- Submitted protected methods must not store enrolled gallery templates as raw reusable unit vectors.
- Protected methods must report machine-independent operation metadata used by the evaluator.
- Encrypted variants must recover scores only after computation over protected stored templates followed by the appropriate reveal/decode step.
