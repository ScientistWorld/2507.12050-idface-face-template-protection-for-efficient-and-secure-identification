#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("data/synthetic_embeddings.npz"))
    parser.add_argument("--out", type=Path, default=Path("baseline/outputs/random_synthetic"))
    parser.add_argument("--seed", type=int, default=123)
    args = parser.parse_args()
    data = np.load(args.data)
    rng = np.random.default_rng(args.seed)
    n_gallery = len(data["gallery_labels"])
    n_genuine = len(data["genuine_labels"])
    n_impostor = len(data["impostor_labels"])
    args.out.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        args.out / "predictions.npz",
        genuine_scores=rng.normal(size=(n_genuine, n_gallery)).astype(np.float32),
        impostor_scores=rng.normal(size=(n_impostor, n_gallery)).astype(np.float32),
        genuine_labels=data["genuine_labels"],
        gallery_labels=data["gallery_labels"],
    )
    (args.out / "metadata.json").write_text(json.dumps({"method": "random"}, indent=2) + "\n")


if __name__ == "__main__":
    main()
