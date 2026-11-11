#!/usr/bin/env python3
"""Better-variant check: multi-level enrolled templates at the reference's encrypted cost.

Probe codes are exactly T_beta (ternary, beta non-zeros), so ciphertext
additions per probe are unchanged. Enrolled codes keep the same top-alpha
support but quantize magnitudes to three levels by rank within the support
(top 1/6 -> 3, next 1/3 -> 2, rest -> 1). Every decoded digit stays below
min(||g||_1, beta * 3) <= 1023, so a 50-bit slot still packs 5 templates at
(alpha, beta) = (341, 341): the extra precision uses digit capacity the
ternary code leaves unused. With --levels 1 the encoder is plain T_alpha.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np


def ternary(x: np.ndarray, k: int) -> np.ndarray:
    idx = np.argpartition(np.abs(x), -k, axis=1)[:, -k:]
    z = np.zeros(x.shape, dtype=np.int8)
    rows = np.arange(len(x))[:, None]
    z[rows, idx] = np.where(x[rows, idx] >= 0, 1, -1)
    return z


def multilevel(x: np.ndarray, k: int) -> np.ndarray:
    order = np.argsort(-np.abs(x), axis=1, kind="stable")[:, :k]
    levels = np.ones(k, dtype=np.int8)
    levels[: k // 6] = 3
    levels[k // 6 : k // 6 + k // 3] = 2
    z = np.zeros(x.shape, dtype=np.int8)
    rows = np.arange(len(x))[:, None]
    z[rows, order] = np.where(x[rows, order] >= 0, 1, -1).astype(np.int8) * levels[None, :]
    return z


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--alpha", type=int, default=341)
    parser.add_argument("--beta", type=int, default=341)
    parser.add_argument("--levels", type=int, choices=(1, 3), default=3)
    parser.add_argument("--role", choices=("gallery", "query"), required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with np.load(args.input, allow_pickle=False) as payload:
        x = payload["templates"]
    if args.role == "query":
        codes = ternary(x, args.beta)
    elif args.levels == 3:
        codes = multilevel(x, args.alpha)
    else:
        codes = ternary(x, args.alpha)
    np.savez(args.output, codes=codes)


if __name__ == "__main__":
    main()
