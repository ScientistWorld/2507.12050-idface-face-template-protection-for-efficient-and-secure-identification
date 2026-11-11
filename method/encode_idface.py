#!/usr/bin/env python3
"""IDFace template encoder (the method's side of the evaluation interface).

Enrolled gallery templates are mapped by T_alpha and probe templates by T_beta:
keep the alpha (resp. beta) largest-magnitude coordinates, replace them by
their signs, zero the rest. The evaluator encrypts nothing itself; it computes
exactly what the additively homomorphic, sign-split, base-p packed database of
the paper returns after decryption and decoding: the integer inner products of
these ternary codes. Each template is encoded independently of every other.

Usage (called by the evaluator):
    python method/encode_idface.py --alpha 341 --beta 63 --role query \
        --input templates.npz --output codes.npz
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from idface import transform  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--alpha", type=int, default=341, help="non-zeros kept in enrolled (gallery) templates")
    parser.add_argument("--beta", type=int, default=341, help="non-zeros kept in probe (query) templates")
    parser.add_argument("--role", choices=("gallery", "query"), required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    with np.load(args.input, allow_pickle=False) as payload:
        templates = payload["templates"]
    sparsity = args.alpha if args.role == "gallery" else args.beta
    codes = transform(templates, sparsity).astype(np.int8)
    np.savez(args.output, codes=codes)


if __name__ == "__main__":
    main()
