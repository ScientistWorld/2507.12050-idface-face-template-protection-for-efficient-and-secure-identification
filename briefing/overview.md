# Overview

This gym measures open-set face identification using integer template representations that fit fixed additive homomorphic encryption budgets. Encoders receive real face embeddings and return codes; the evaluator owns the gallery, labels, matching, cost accounting and thresholds.

The two experiments balance identification quality against constrained encrypted computation and packing. They use fixed AdaFace embeddings from LFW, XQLFW and CPLFW, with disjoint development and hidden identities and 16 paired draws. See [problem.md](problem.md), [evaluation.md](evaluation.md) and [../scoring/EXPERIMENTS.md](../scoring/EXPERIMENTS.md).
