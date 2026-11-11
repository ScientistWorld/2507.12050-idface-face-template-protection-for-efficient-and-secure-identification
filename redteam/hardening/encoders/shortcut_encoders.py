#!/usr/bin/env python3
"""Shortcut encoders used to check the hardened evaluator (audit only, not methods).

Each --kind reproduces, through the new encoder interface, the strongest
available form of a shortcut from REDTEAM.md, or a new attack on the new
interface:

visible_lookup   exact-match lookup of templates in the visible development
                 file; matched templates get identity-revealing 2-hot codes,
                 matched impostors get zero codes, unmatched get honest codes
constant         every template gets the same code
float_quantized  near-lossless integer codes round(4096 * x) (unprotected-quality
                 matching that the additive-HE budget cannot afford)
scaled           honest ternary codes multiplied by 1000 (score-scale inflation)
nan_float        float codes containing NaN (impossible values)
empty            zero rows (task shrinking)
zero             all-zero codes (no work, no information)
stateful_query   gallery calls stash templates; query calls look up the nearest
                 stashed gallery template and copy its code (query side reads the
                 enrolled database in the clear)
stateful_gallery query calls stash probes; gallery calls fold nearby stashed probes
                 into each enrolled template before coding (test-time transduction)
batch_center     codes computed after subtracting the batch mean (batch-dependent)
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

STATE = Path(__file__).resolve().parents[1] / "state"
WORKSPACE = Path(__file__).resolve().parents[3]


def ternary(x: np.ndarray, k: int) -> np.ndarray:
    idx = np.argpartition(np.abs(x), -k, axis=1)[:, -k:]
    z = np.zeros(x.shape, dtype=np.int64)
    rows = np.arange(len(x))[:, None]
    z[rows, idx] = np.where(x[rows, idx] >= 0, 1, -1)
    return z


def two_hot(identity: int, dim: int) -> np.ndarray:
    j = identity % dim
    k = (j + 1 + identity // dim) % dim
    code = np.zeros(dim, dtype=np.int64)
    code[j] = 1
    code[k] = 1
    return code


def visible_lookup(x: np.ndarray, role: str, k: int) -> np.ndarray:
    data = np.load(WORKSPACE / "data" / "synthetic_embeddings.npz")
    table: dict[bytes, int] = {}
    for i, row in enumerate(data["gallery"]):
        table[row.tobytes()] = int(i)
    for row, label in zip(data["genuine_queries"], data["genuine_labels"]):
        table[row.tobytes()] = int(label)
    for row in data["impostor_queries"]:
        table[row.tobytes()] = -1
    codes = ternary(x, k)
    hits = 0
    for i, row in enumerate(x.astype(np.float32)):
        identity = table.get(row.tobytes())
        if identity is None:
            continue
        hits += 1
        codes[i] = 0 if identity < 0 else two_hot(identity, x.shape[1])
    print(f"visible_lookup matched {hits}/{len(x)} {role} templates")
    return codes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", required=True)
    parser.add_argument("--alpha", type=int, default=341)
    parser.add_argument("--beta", type=int, default=341)
    parser.add_argument("--role", choices=("gallery", "query"), required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with np.load(args.input, allow_pickle=False) as payload:
        x = payload["templates"].astype(np.float32)
    k = args.alpha if args.role == "gallery" else args.beta
    STATE.mkdir(parents=True, exist_ok=True)

    if args.kind == "visible_lookup":
        codes = visible_lookup(x, args.role, k)
    elif args.kind == "constant":
        codes = np.zeros(x.shape, dtype=np.int64)
        codes[:, 0] = 1
    elif args.kind == "float_quantized":
        codes = np.rint(4096 * x).astype(np.int64)
    elif args.kind == "scaled":
        codes = 1000 * ternary(x, k)
    elif args.kind == "nan_float":
        codes = ternary(x, k).astype(np.float64)
        codes[0, 0] = np.nan
    elif args.kind == "empty":
        codes = np.zeros((0, x.shape[1]), dtype=np.int64)
    elif args.kind == "zero":
        codes = np.zeros(x.shape, dtype=np.int64)
    elif args.kind == "stateful_query":
        stash = STATE / f"gallery_{args.alpha}_{args.beta}.npy"
        if args.role == "gallery":
            np.save(stash, x)
            codes = ternary(x, args.alpha)
        else:
            codes = ternary(x, args.beta)
            if stash.is_file():
                gallery = np.load(stash)
                sims = x @ gallery.T
                best = sims.argmax(axis=1)
                confident = sims[np.arange(len(x)), best] > 0.3
                codes[confident] = ternary(gallery[best[confident]], args.beta)
    elif args.kind == "stateful_gallery":
        stash = STATE / f"probes_{args.alpha}_{args.beta}.npy"
        if args.role == "query":
            np.save(stash, x)
            codes = ternary(x, args.beta)
        else:
            folded = x.copy()
            if stash.is_file():
                probes = np.load(stash)
                for start in range(0, len(x), 2048):
                    sims = x[start : start + 2048] @ probes.T
                    folded[start : start + 2048] += (np.where(sims > 0.35, sims, 0.0) @ probes).astype(np.float32)
            codes = ternary(folded, args.alpha)
    elif args.kind == "batch_center":
        codes = ternary(x - x.mean(axis=0, keepdims=True), k)
    else:
        raise SystemExit(f"unknown kind {args.kind}")
    np.savez(args.output, codes=codes)


if __name__ == "__main__":
    main()
