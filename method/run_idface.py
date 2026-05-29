#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from idface import IDFaceDatabase


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("data/synthetic_embeddings.npz"))
    parser.add_argument("--out", type=Path, default=Path("method/outputs/idface_synthetic"))
    parser.add_argument("--alpha", type=int, default=341)
    parser.add_argument("--beta", type=int, default=341)
    parser.add_argument("--plaintext-bits", type=int, default=50)
    args = parser.parse_args()

    data = np.load(args.data)
    gallery = data["gallery"]
    gallery_labels = data["gallery_labels"]
    genuine = data["genuine_queries"]
    impostor = data["impostor_queries"]

    db = IDFaceDatabase.enroll(gallery, gallery_labels, args.alpha, args.beta, args.plaintext_bits)
    genuine_scores = db.batch_scores(genuine)
    impostor_scores = db.batch_scores(impostor)

    args.out.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        args.out / "predictions.npz",
        genuine_scores=genuine_scores.astype(np.float32),
        impostor_scores=impostor_scores.astype(np.float32),
        genuine_labels=data["genuine_labels"],
        gallery_labels=gallery_labels,
    )
    metadata = {
        "method": "idface",
        "alpha": args.alpha,
        "beta": args.beta,
        "plaintext_bits": args.plaintext_bits,
        "operation_counts": db.operation_counts(),
    }
    metadata["operation_counts"]["protected_template_storage"] = 1.0
    (args.out / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")


if __name__ == "__main__":
    main()
