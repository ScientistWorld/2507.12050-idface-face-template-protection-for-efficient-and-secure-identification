# Problem Definition

The task is privacy-preserving biometric identification over unit-norm templates.

Given an enrolled gallery of identity templates and a query template, the system must return the closest identity when the query matches an enrolled subject and reject non-enrolled impostor queries. Templates are real-valued unit vectors, matching is based on inner product or cosine similarity, and the benchmark fixes a gallery, genuine queries with labels, and impostor queries.

The problem is method-agnostic: any method may transform or protect templates, but it must produce a score matrix for genuine queries and impostor queries against the fixed gallery so the evaluator can compute identification metrics at fixed false-positive identification rates.

## Portable Dataset

The original paper evaluates on LFW, CFP-FP, AgeDB, and IJB-C with AdaFace embeddings. IJB-C distribution has been discontinued and AgeDB requires an email/password flow, so this gym includes a reproducible synthetic unit-vector benchmark in `data/generate_synthetic.py`. The substitute preserves the relevant structure: 512-dimensional unit embeddings, enrolled identities, noisy genuine queries, and random impostor queries.
