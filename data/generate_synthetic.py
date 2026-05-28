#!/usr/bin/env python3
"""Generate a reproducible unit-vector biometric identification benchmark."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np


def _unit(x: np.ndarray) -> np.ndarray:
    return x / np.linalg.norm(x, axis=1, keepdims=True)


def generate(
    out: Path,
    identities: int = 2000,
    dim: int = 512,
    genuine_queries: int = 2000,
    impostor_queries: int = 2000,
    noise: float = 0.82,
    seed: int = 20260712,
) -> None:
    rng = np.random.default_rng(seed)
    centers = _unit(rng.normal(size=(identities, dim)).astype(np.float32))
    gallery = _unit(centers + 0.10 * rng.normal(size=(identities, dim)).astype(np.float32))

    query_labels = rng.integers(0, identities, size=genuine_queries, endpoint=False)
    genuine = _unit(centers[query_labels] + noise * rng.normal(size=(genuine_queries, dim)).astype(np.float32))
    impostors = _unit(rng.normal(size=(impostor_queries, dim)).astype(np.float32))

    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        out,
        gallery=gallery.astype(np.float32),
        gallery_labels=np.arange(identities, dtype=np.int64),
        genuine_queries=genuine.astype(np.float32),
        genuine_labels=query_labels.astype(np.int64),
        impostor_queries=impostors.astype(np.float32),
        impostor_labels=np.full(impostor_queries, -1, dtype=np.int64),
        seed=np.array(seed, dtype=np.int64),
        noise=np.array(noise, dtype=np.float32),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("data/synthetic_embeddings.npz"))
    parser.add_argument("--identities", type=int, default=2000)
    parser.add_argument("--dim", type=int, default=512)
    parser.add_argument("--genuine-queries", type=int, default=2000)
    parser.add_argument("--impostor-queries", type=int, default=2000)
    parser.add_argument("--noise", type=float, default=0.82)
    parser.add_argument("--seed", type=int, default=20260712)
    args = parser.parse_args()
    generate(args.out, args.identities, args.dim, args.genuine_queries, args.impostor_queries, args.noise, args.seed)


if __name__ == "__main__":
    main()
