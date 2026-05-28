# Data

This gym uses a reproducible synthetic biometric-embedding benchmark because the paper's main face benchmarks and WebFace12M-trained AdaFace feature pipeline are large and not fully portable for a small research gym.

The generated data keeps the paper's problem structure: unit-norm biometric templates, a gallery of enrolled identities, genuine identification queries, and impostor queries used to set false-positive thresholds.
