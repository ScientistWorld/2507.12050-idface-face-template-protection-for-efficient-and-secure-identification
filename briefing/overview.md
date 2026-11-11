# Overview

IDFace is a biometric template protection method for face identification. It transforms unit face embeddings into sparse ternary templates and packs multiple protected templates so encrypted database matching can be performed with additions instead of expensive encrypted multiplications.

This gym scores a template representation for additively homomorphic identification: the evaluator runs a method's per-template encoder on enrolled and probe templates of a synthetic face-embedding benchmark (a hidden fresh draw at test time), computes the decrypted match scores and the encrypted cost (ciphertext additions per probe, templates packed per plaintext slot) from the integer codes, and measures open-set identification accuracy within two fixed cost budgets taken from the paper's operating points, (341, 341) and the compressed (341, 63).
