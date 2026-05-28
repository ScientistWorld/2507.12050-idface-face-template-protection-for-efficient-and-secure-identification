#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("data/synthetic_embeddings.npz"))
    parser.add_argument("--out", type=Path, default=Path("baseline/outputs/plain_synthetic"))
    args = parser.parse_args()
    data = np.load(args.data)
    gallery = data["gallery"]
    genuine_scores = data["genuine_queries"] @ gallery.T
    impostor_scores = data["impostor_queries"] @ gallery.T
    args.out.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        args.out / "predictions.npz",
        genuine_scores=genuine_scores.astype(np.float32),
        impostor_scores=impostor_scores.astype(np.float32),
        genuine_labels=data["genuine_labels"],
        gallery_labels=data["gallery_labels"],
    )
    (args.out / "metadata.json").write_text(json.dumps({"method": "plain"}, indent=2) + "\n")


if __name__ == "__main__":
    main()
