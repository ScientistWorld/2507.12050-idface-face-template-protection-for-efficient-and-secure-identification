# Direction

Work within biometric template protection for large-scale identification under additively homomorphic encryption: find template representations whose encrypted inner products preserve identification accuracy at a fixed encrypted cost.

Valid improvements include better per-template integer encodings for the gallery or the probes, better use of the plaintext digit capacity (packing), learned or data-independent transforms applied before encoding, and representations that move the accuracy/cost frontier at either budget, especially the compressed one.

Invalid improvements include matching with unprotected full-precision templates, encoders that look at other templates, labels or evaluation files, encoders that keep state between calls, training an identity classifier on the benchmark identities, and changing the benchmark, the evaluators or the budgets.
