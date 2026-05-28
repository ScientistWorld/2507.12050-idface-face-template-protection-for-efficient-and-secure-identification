#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def _load_predictions(path: Path) -> dict[str, np.ndarray]:
    pred_file = path / "predictions.npz"
    if not pred_file.exists():
        raise FileNotFoundError(f"missing predictions file: {pred_file}")
    return dict(np.load(pred_file))


def _threshold_at_fpir(impostor_scores: np.ndarray, fpir: float) -> float:
    max_impostor = np.max(impostor_scores, axis=1)
    return float(np.quantile(max_impostor, 1.0 - fpir, method="higher"))


def identification_metrics(pred: dict[str, np.ndarray]) -> dict[str, float]:
    genuine_scores = pred["genuine_scores"]
    impostor_scores = pred["impostor_scores"]
    genuine_labels = pred["genuine_labels"]
    gallery_labels = pred["gallery_labels"]

    top_idx = np.argmax(genuine_scores, axis=1)
    top_scores = genuine_scores[np.arange(len(genuine_scores)), top_idx]
    top_labels = gallery_labels[top_idx]
    correct_top1 = top_labels == genuine_labels

    metrics = {"top1_identification": float(np.mean(correct_top1))}
    for fpir in (1e-1, 1e-2):
        threshold = _threshold_at_fpir(impostor_scores, fpir)
        accepted_correct = correct_top1 & (top_scores >= threshold)
        metrics[f"tpir_at_fpir_{fpir:g}"] = float(np.mean(accepted_correct))
        metrics[f"threshold_at_fpir_{fpir:g}"] = threshold
    return metrics


def evaluate_method(name: str, path: Path) -> dict[str, float]:
    metrics = identification_metrics(_load_predictions(path))
    metadata_file = path / "metadata.json"
    if metadata_file.exists():
        metadata = json.loads(metadata_file.read_text())
        counts = metadata.get("operation_counts", {})
        for key in (
            "ciphertext_additions_per_query",
            "ciphertext_multiplications_per_query",
            "ciphertext_rotations_per_query",
            "decryptions_per_query",
            "pack",
        ):
            if key in counts:
                metrics[key] = float(counts[key])
        if name == "plain":
            metrics.update(
                {
                    "ciphertext_additions_per_query": 0.0,
                    "ciphertext_multiplications_per_query": 0.0,
                    "ciphertext_rotations_per_query": 0.0,
                    "decryptions_per_query": 0.0,
                    "pack": 1.0,
                }
            )
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plain", type=Path, default=Path("baseline/outputs/plain_synthetic"))
    parser.add_argument("--random", type=Path, default=Path("baseline/outputs/random_synthetic"))
    parser.add_argument("--idface", type=Path, default=Path("method/outputs/idface_synthetic"))
    parser.add_argument("--out", type=Path, default=Path("scoring/scores.json"))
    args = parser.parse_args()

    results = {}
    for name, path in [("plain", args.plain), ("random", args.random), ("idface_341_341", args.idface)]:
        if (path / "predictions.npz").exists():
            results[name] = evaluate_method("plain" if name == "plain" else name, path)

    output = {"experiments": {"synthetic_identification": {"results": results}}}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
