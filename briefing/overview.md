# Overview

IDFace is a biometric template protection method for face identification. It transforms unit face embeddings into sparse ternary templates and packs multiple protected templates so encrypted database matching can be performed with additions instead of expensive encrypted multiplications.

This reproduction implements the core IDFace computation and evaluates whether transformed protected templates preserve identification accuracy on a portable synthetic embedding benchmark. It also records operation counts showing the method remains addition-only.
