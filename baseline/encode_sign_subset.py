#!/usr/bin/env python3
"""Sign-of-fixed-coordinates baseline encoder.

A simple data-independent binarization: gallery templates keep the signs of a
fixed random set of ``alpha`` coordinates, probes keep the signs of a fixed
random subset of ``beta`` of those coordinates. It has the same code sparsity,
ciphertext-addition count and packing as a ternary code with the same
(alpha, beta), but chooses coordinates without looking at their magnitudes.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

COORDINATE_SEED = 12345


def coordinate_sets(dim: int, alpha: int, beta: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(COORDINATE_SEED)
    gallery_coords = np.sort(rng.choice(dim, size=alpha, replace=False))
    probe_coords = np.sort(rng.choice(gallery_coords, size=min(beta, alpha), replace=False))
    return gallery_coords, probe_coords


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--alpha", type=int, default=341)
    parser.add_argument("--beta", type=int, default=341)
    parser.add_argument("--role", choices=("gallery", "query"), required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    with np.load(args.input, allow_pickle=False) as payload:
        templates = payload["templates"]
    gallery_coords, probe_coords = coordinate_sets(templates.shape[1], args.alpha, args.beta)
    coords = gallery_coords if args.role == "gallery" else probe_coords
    codes = np.zeros(templates.shape, dtype=np.int8)
    codes[:, coords] = np.where(templates[:, coords] >= 0, 1, -1)
    np.savez(args.output, codes=codes)


if __name__ == "__main__":
    main()
