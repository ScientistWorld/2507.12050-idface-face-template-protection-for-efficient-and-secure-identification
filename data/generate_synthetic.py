#!/usr/bin/env python3
"""Generate the visible (development) synthetic face-template identification benchmark.

Templates are 512-dimensional unit vectors. Every identity has a center drawn
uniformly on the sphere; every sample of that identity is a unit vector whose
cosine to the center is a per-sample quality value rho:

    sample = normalize(rho * center + sqrt(1 - rho^2) * u),  u ⟂ center, |u| = 1.

Quality is heterogeneous, as in mixed-media face benchmarks:

* enrolled gallery templates are good captures, rho ~ U(0.75, 0.95);
* probes (genuine and impostor alike) are usable captures with probability
  0.95, rho ~ U(0.5, 0.9), and degraded captures otherwise, rho ~ U(0.05, 0.5).

Genuine probes belong to enrolled identities; impostor probes belong to
identities that are never enrolled. This file only produces the visible
development split. The hidden test split is produced independently at test
time by the test evaluator with its own seed.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

DIM = 512
GALLERY_RHO = (0.75, 0.95)
PROBE_GOOD_RHO = (0.5, 0.9)
PROBE_DEGRADED_RHO = (0.05, 0.5)
PROBE_DEGRADED_FRACTION = 0.05


def _unit(x: np.ndarray) -> np.ndarray:
    return x / np.linalg.norm(x, axis=1, keepdims=True)


def _around(centers: np.ndarray, rho: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    noise = rng.standard_normal(centers.shape)
    noise -= np.sum(noise * centers, axis=1, keepdims=True) * centers
    noise = _unit(noise)
    rho = rho[:, None]
    return _unit(rho * centers + np.sqrt(1.0 - rho**2) * noise)


def _probe_quality(n: int, rng: np.random.Generator) -> np.ndarray:
    degraded = rng.random(n) < PROBE_DEGRADED_FRACTION
    good = rng.uniform(*PROBE_GOOD_RHO, size=n)
    bad = rng.uniform(*PROBE_DEGRADED_RHO, size=n)
    return np.where(degraded, bad, good)


def generate_arrays(
    seed: int,
    identities: int = 10_000,
    genuine_queries: int = 10_000,
    impostor_queries: int = 20_000,
    dim: int = DIM,
) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    centers = _unit(rng.standard_normal((identities, dim)))
    gallery = _around(centers, rng.uniform(*GALLERY_RHO, size=identities), rng)
    genuine_labels = rng.integers(0, identities, size=genuine_queries)
    genuine = _around(centers[genuine_labels], _probe_quality(genuine_queries, rng), rng)
    impostor_centers = _unit(rng.standard_normal((impostor_queries, dim)))
    impostor = _around(impostor_centers, _probe_quality(impostor_queries, rng), rng)
    return {
        "gallery": gallery.astype(np.float32),
        "gallery_labels": np.arange(identities, dtype=np.int64),
        "genuine_queries": genuine.astype(np.float32),
        "genuine_labels": genuine_labels.astype(np.int64),
        "impostor_queries": impostor.astype(np.float32),
        "impostor_labels": np.full(impostor_queries, -1, dtype=np.int64),
    }


def generate(out: Path, seed: int, identities: int, genuine_queries: int, impostor_queries: int, dim: int) -> None:
    arrays = generate_arrays(seed, identities, genuine_queries, impostor_queries, dim)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out, seed=np.array(seed, dtype=np.int64), **arrays)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("data/synthetic_embeddings.npz"))
    parser.add_argument("--identities", type=int, default=10_000)
    parser.add_argument("--genuine-queries", type=int, default=10_000)
    parser.add_argument("--impostor-queries", type=int, default=20_000)
    parser.add_argument("--dim", type=int, default=DIM)
    parser.add_argument("--seed", type=int, default=20260712)
    args = parser.parse_args()
    generate(args.out, args.seed, args.identities, args.genuine_queries, args.impostor_queries, args.dim)


if __name__ == "__main__":
    main()
